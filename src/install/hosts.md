# Adding hosts

Every host runs `arcana-agent`. The console's own host joins by itself
(see [The console](console.md)); every other host joins by
*enrolling*.

## Enrolling a host

1. Install the host's programs on it (the port without `CONSOLE`, or
   `make install WITHOUT_CONSOLE=yes`).
2. In the console, press **Enrol a host** at the top of the tree. Give
   the host a name and the name or address the console reaches it by.
3. The console shows a one-time command. Run it on the host as root:

```sh
arcana-enrol -s https://console.example 3f1c…
```

`arcana-enrol(8)` makes a key on the host, has the console's CA sign a
certificate for it, writes both and the CA's certificate to
`/usr/local/etc/arcana`, and, with `-s`, enables and starts the agent
on port 4310. The console adds the host at the same moment. The token
works once, for an hour.

Without `-s` it prints the `rc.conf` lines to add instead:

```sh
sysrc arcana_agent_enable=YES
sysrc arcana_agent_listen="tcp://0.0.0.0:4310 tcp://[::]:4310"
service arcana_agent start
```

## What the agent listens on

The agent always listens on its local socket,
`/var/run/arcana-agent.sock`, which `arcanactl` on the host uses.
`arcana_agent_listen` adds network listeners. Its certificates are
`ca.pem`, `host.pem` and `host.key` in `/usr/local/etc/arcana` unless
`arcana_agent_ca`, `arcana_agent_cert` or `arcana_agent_key` say
otherwise; `arcana_agent_flags` adds options of `arcana-agent(8)`.

Check it from the host:

```sh
arcanactl hello
arcanactl list
```

## A host with certificates of your own

A host whose certificate comes from your own CA (see [Certificates of
your own](certificates.md)) needs no enrolment: add it with **Add a
server**, by a name and a URI such as `tcp://host1.example:4310`.
