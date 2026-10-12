# The console

The console is a module of the Kore web server, `arcana-console.so`,
and runs as an unprivileged user. It serves the panel and its JSON API,
keeps the fleet's state in a data directory, and talks to the agents.

## Set it up

```sh
pw useradd arcana -d /var/db/arcana -s /usr/sbin/nologin
install -d -o arcana -m 0700 /var/db/arcana
cd /usr/local/etc/arcana
cp kore.conf.sample kore.conf          # the name, certificate, address
cp web.conf.sample web.conf            # rp_id, origin
sysrc arcana_console_enable=YES
service arcana_console start
```

The console's HTTPS certificate must be **RSA**: Kore keeps the private
key out of its worker in a key manager, which signs with nothing else.

## kore.conf

How the web server listens and which certificate it shows. Change the
domain, the certificate's paths and, if need be, the addresses it binds
to:

```text
{{#include ../../arcana/www/arcana-console/conf/kore.conf.sample}}
```

## web.conf

The console's own settings, in UCL. At the least, `rp_id` and `origin`
must be the name and the exact address your browser uses: a security
key signs for that name and no other.

```text
{{#include ../../arcana/www/arcana-console/conf/web.conf.sample}}
```

## The console's own host

Arcana installs the agent beside the console. Start it, and the console
adds that host by itself, over the agent's local socket, under the
host's name:

```sh
sysrc arcana_agent_enable=YES
service arcana_agent start
```

The agent's rc script lets the group `arcana`, the console's, use its
socket when that group exists. The console stays unprivileged; only the
agent runs as root.

<div class="freebsd">

**FreeBSD:** both are ordinary `rc.d` services, enabled in `rc.conf`
with `sysrc(8)` and run with `service(8)`; the local socket is an
`AF_UNIX` socket whose group decides who may open it.

</div>
