# The console

The console, `arcana-console`, is its own web server, built on
libwebsockets, and serves as an unprivileged user. It serves the panel
and its JSON API, keeps the fleet's state in a data directory, and
talks to the agents.

## Set it up

```sh
pw useradd arcana -d /var/db/arcana -s /usr/sbin/nologin
install -d -o arcana -m 0700 /var/db/arcana
cd /usr/local/etc/arcana
cp web.conf.sample web.conf            # address, certificate; rp_id, origin
sysrc arcana_console_enable=YES
service arcana_console start
```

It is three processes. The supervisor, root, listens on the addresses
and starts the worker, which serves as `arcana`, again if it ever dies;
the worker serves on the supervisor's sockets, so a restart of it
refuses no one. The certificate may be RSA or EC (browsers then get
HTTP/2, others HTTP/1.1), and its key is never in the worker: a key
manager, forked by the worker while it is still root, reads the key,
becomes `arcana`, and signs each handshake's digest for the worker.

<div class="freebsd">

**FreeBSD:** the key manager runs in capability mode, `capsicum(4)`:
after `cap_enter(2)` it can open nothing, connect nowhere, and only read
and write the one socket it shares with the worker
(`cap_rights_limit(2)`). A flaw that lets an attacker read the worker's
memory finds no key there.

</div>

## web.conf

The console's settings, in UCL. Its `server` block says where it
listens and which certificate it shows; the rest is the console's own.
At the least, `rp_id` and `origin` must be the name and the exact
address your browser uses: a security key signs for that name and no
other.

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
