# FreeBSD underneath

Arcana is meant to show FreeBSD off, not hide it. Each feature is a
thin layer over a facility of the base system, and the panel names it.
This is the map.

| In Arcana | FreeBSD does it with |
|---|---|
| Jails, read and changed | `libjail(3)`, `jail(8)`, `jail.conf(5)`; Arcana's own `libjailconf` edits `jail.conf` in place, as `sysrc(8)` edits `rc.conf` |
| A jail's own network | VNET jails, `epair(4)`, `ifconfig -vnet` |
| Processes and resource use | `libprocstat(3)`, `sysctl(3)`, the kernel's resource accounting |
| Services | `rc.d` scripts, `service(8)`, `rc.conf(5)` through `sysrc(8)` |
| Packages | `pkg(8)`, on the host and with `-j` in a jail |
| Interfaces | `ifconfig(8)`, `getifaddrs(3)` |
| Routes and nexthops | `netlink(4)` and `route(8)`, every routing table (`setfib(1)`, FIBs) |
| Tunnels | `gif(4)`, `gre(4)`, `geneve(4)`, `vxlan(4)`, `if_wg(4)` |
| Bridges and VLANs | `if_bridge(4)`, `vlan(4)` |
| Netgraph | `netgraph(4)`, `ngctl(8)` |
| Firewall, shaping | `ipfw(8)`, its tables and sets, `dummynet(4)` |
| Packet traces | `dtrace(1)` and ipfw's `rule-matched` probe |
| The security record | `ipfw` log rules sent to the routing socket |
| IPsec | `ipsec(4)` interfaces, `setkey(8)`; IKEv2 by strongSwan (a plugin) |
| DNS filtering | `local-unbound(8)`, the base system's Unbound |
| Router advertisements | `rtadvd(8)` |
| Storage | ZFS (`zfs(8)`, `zpool(8)`), `gpart(8)`, `camcontrol(8)`, `mount(8)` |
| Kernel modules | `kldload(8)`, `kldstat(8)` |
| The console's TLS and keys | the base system's OpenSSL |
| Command-line output | `libxo(3)`, so `arcanactl --libxo json` works |

Where Arcana needs something the base system does not have, it says so
and names the package: BIRD (`bird3`) for BGP, OSPF and BFD, strongSwan
(`strongswan`) for IKEv2, `wireguard-tools` for `wg-quick(8)` to bring a
WireGuard interface back after a boot (`wg(8)` itself is the base
system's), dnsmasq (`dnsmasq`) for DHCP at
an SD-WAN UNI, Squid (`squid`) for URL filtering. Arcana installs none
of them by itself.

The standards each feature follows, section by section, are mapped in
[Built on standards](standards.md).
