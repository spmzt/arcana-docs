#!/bin/sh
#
# A fleet made for the book's pictures, on the lab VM: three vnet jails
# (hq, branch-a, branch-b), each running its own arcana-agent, numbered
# from the documentation ranges only (192.0.2.0/24, 198.51.100.0/24,
# 2001:db8::/32) and private 10/8 LANs, so no picture shows a real
# address.  Everything is made under /tmp/ad and taken away by "down";
# nothing of the host is changed but the interfaces and jails it makes.
#
# As root:	fleet.sh up ARCANA-TREE	|	fleet.sh down

set -eu
D=/tmp/ad
HOSTS="hq branch-a branch-b"

up() {
	tree=$(cd "${1:?usage: fleet.sh up arcana-tree}" && pwd)
	agent="$tree/obj/usr.sbin/arcana-agent/arcana-agent"
	[ -x "$agent" ] || { echo "fleet.sh: build Arcana first: $agent" >&2; exit 1; }
	for h in $HOSTS; do
		jls -j "ad-$h" >/dev/null 2>&1 &&
		    { echo "fleet.sh: ad-$h is there: fleet.sh down" >&2; exit 1; }
	done
	mkdir -p "$D"
	chmod 755 "$D"
	kldload -nq if_bridge if_epair if_gif 2>/dev/null || true

	# The Internet: a bridge on the host, each edge an epair on it.
	bridge=$(ifconfig bridge create)
	echo "$bridge" > "$D/bridge"
	ifconfig "$bridge" inet 192.0.2.1/24 up
	n=10
	for h in $HOSTS; do
		mkdir -p "$D/$h/jail.conf.d"
		jail -c name="ad-$h" host.hostname="$h.example.org" vnet persist \
		    path=/ allow.raw_sockets
		e=$(ifconfig epair create)
		echo "${e%a}" >> "$D/epairs"
		ifconfig "$bridge" addm "$e" && ifconfig "$e" up
		ifconfig "${e%a}b" vnet "ad-$h"
		jexec "ad-$h" ifconfig "${e%a}b" name vtnet0
		jexec "ad-$h" ifconfig vtnet0 inet "192.0.2.$n/24" up
		# Its LAN: the far end of a pair left on the host, down.
		l=$(ifconfig epair create)
		echo "${l%a}" >> "$D/epairs"
		ifconfig "${l%a}b" vnet "ad-$h"
		jexec "ad-$h" ifconfig "${l%a}b" name vtnet2
		jexec "ad-$h" ifconfig vtnet2 inet "10.$n.0.1/24" up
		jexec "ad-$h" ifconfig vtnet2 inet6 "2001:db8:$n::1/64" up
		jexec "ad-$h" ifconfig lo0 up
		jexec "ad-$h" route -q add default 192.0.2.1 || true
		n=$((n + 10))
	done
	# A private circuit between hq and branch-a.
	p=$(ifconfig epair create)
	echo "${p%a}" >> "$D/epairs"
	ifconfig "$p" vnet ad-hq
	ifconfig "${p%a}b" vnet ad-branch-a
	jexec ad-hq ifconfig "$p" name vtnet1
	jexec ad-branch-a ifconfig "${p%a}b" name vtnet1
	jexec ad-hq ifconfig vtnet1 inet 198.51.100.1/30 up
	jexec ad-branch-a ifconfig vtnet1 inet 198.51.100.2/30 up
	# A tunnel from hq to branch-b over the Internet.
	jexec ad-hq ifconfig gif0 create
	jexec ad-hq ifconfig gif0 tunnel 192.0.2.10 192.0.2.30
	jexec ad-hq ifconfig gif0 inet 10.255.0.0 10.255.0.1 netmask 255.255.255.254 up
	jexec ad-branch-b ifconfig gif0 create
	jexec ad-branch-b ifconfig gif0 tunnel 192.0.2.30 192.0.2.10
	jexec ad-branch-b ifconfig gif0 inet 10.255.0.1 10.255.0.0 netmask 255.255.255.254 up

	# A CA of the fleet's own: a certificate for each agent, by its
	# address, and the console's client certificate, as a fleet with a
	# CA of its own has them (web.conf's tls block).
	openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
	    -keyout "$D/ca.key" -out "$D/ca.pem" -days 2 -subj "/CN=demo CA" \
	    -addext basicConstraints=critical,CA:TRUE 2>/dev/null
	cert() {	# name, extended key usage, subjectAltName
		openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
		    -keyout "$D/$1.key" -out "$D/$1.csr" -subj "/CN=$1" 2>/dev/null
		printf 'extendedKeyUsage=%s\nsubjectAltName=%s\n' "$2" "$3" \
		    > "$D/$1.ext"
		openssl x509 -req -in "$D/$1.csr" -CA "$D/ca.pem" -CAkey \
		    "$D/ca.key" -CAcreateserial -days 2 -extfile "$D/$1.ext" \
		    -out "$D/$1.pem" 2>/dev/null
	}
	cert client clientAuth DNS:console.example.org
	chown pouria "$D/client.key" "$D/client.pem"
	n=10
	for h in $HOSTS; do
		cert "$h" serverAuth "IP:192.0.2.$n,DNS:$h.example.org"
		n=$((n + 10))
	done

	# Each edge's agent, in its jail, with a jail.conf of its own.
	for h in $HOSTS; do
		case $h in
		hq) jails="web db mail"; o=10 ;;
		branch-a) jails="cache files"; o=20 ;;
		*) jails="proxy"; o=30 ;;
		esac
		: > "$D/$h/jail.conf"
		i=2
		for j in $jails; do
			printf '%s {\n\tpath = "/jails/%s";\n\thost.hostname = "%s.%s.example.org";\n\tip4.addr = "vtnet2|10.%s.0.%d/24";\n\tpersist;\n}\n' \
			    "$j" "$j" "$j" "$h" "$o" "$i" \
			    >> "$D/$h/jail.conf"
			i=$((i + 1))
		done
		jexec "ad-$h" /usr/sbin/sshd -o PidFile="$D/$h/sshd.pid" || true
		ip=$(jexec "ad-$h" ifconfig vtnet0 inet | awk '/inet /{print $2}')
		jexec "ad-$h" "$agent" -F -l "unix:$D/$h.sock" \
		    -l "tcp://$ip:4310" -A "$D/ca.pem" -C "$D/$h.pem" \
		    -K "$D/$h.key" -g pouria \
		    -f "$D/$h/jail.conf" -D "$D/$h/jail.conf.d" \
		    -1 "$D/$h/history.conf" -p "$D/$h/agent.pid" \
		    > "$D/$h/agent.out" 2>&1 &
	done
	for h in $HOSTS; do
		i=0
		while [ ! -S "$D/$h.sock" ] && [ $i -lt 100 ]; do
			sleep 0.1; i=$((i + 1))
		done
		[ -S "$D/$h.sock" ] || { cat "$D/$h/agent.out"; exit 1; }
	done
	echo "fleet.sh: up: $(for h in $HOSTS; do printf 'unix:%s/%s.sock ' "$D" "$h"; done)"
}

down() {
	for h in $HOSTS; do
		[ -f "$D/$h/agent.pid" ] && kill "$(cat "$D/$h/agent.pid")" 2>/dev/null
		jls -j "ad-$h" >/dev/null 2>&1 || continue
		# Every interface out of the jail before it goes: a vnet torn
		# down with addresses on its interfaces panics a debug kernel.
		jexec "ad-$h" ifconfig gif0 destroy 2>/dev/null || true
		jexec "ad-$h" pkill -f sshd 2>/dev/null || true
	done
	[ -f "$D/epairs" ] && while read -r e; do
		ifconfig "${e}a" destroy 2>/dev/null || true
	done < "$D/epairs"
	[ -f "$D/bridge" ] && ifconfig "$(cat "$D/bridge")" destroy 2>/dev/null
	for h in $HOSTS; do
		jail -r "ad-$h" 2>/dev/null || true
	done
	rm -rf "$D"
	echo "fleet.sh: down"
}

case "${1:-}" in
up) up "${2:-}" ;;
down) down ;;
*) echo "usage: fleet.sh up arcana-tree | down" >&2; exit 2 ;;
esac
