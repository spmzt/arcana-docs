# The programs

Arcana is a handful of programs, each doing one thing.

```text
 browser (the panel)        console host                       each host
┌──────────────┐ HTTPS  ┌─────────────────────────┐ cblink  ┌──────────────────┐
│ C → wasm,    │──────▶ │ kore + arcana-console.so│───────▶ │ arcana-agent     │
│ installable  │ JSON   │ WebAuthn, sessions,     │ mTLS,   │ the only part    │
│ as an app    │◀────── │ the fleet's state       │◀─────── │ running as root  │
└──────────────┘        └─────────────────────────┘  CBOR   └──────────────────┘
                                                arcanactl ──▶ (the same, from a shell)
```

| Program | Runs on | Does |
|---|---|---|
| `arcana-agent(8)` | every host, as root | Reads the host and changes it, as jobs; the only privileged part. |
| `arcana-console(8)` | the console host, unprivileged | A module of the Kore web server: serves the panel and its JSON API, signs you in with WebAuthn, talks to every agent. |
| the panel | your browser | The console's pages, written in C and compiled to WebAssembly; installable as an app on a phone or a desktop. |
| `arcana-enrol(8)` | a host, once | Joins the host to the console with a one-time token: gets it a certificate from the console's CA and starts its agent. |
| `arcanactl(8)` | anywhere | Talks to an agent from a shell, for scripts and for administrators. |
| `jailconf(8)` | anywhere | Changes one value of a jail's parameter in `jail.conf` in place, as `sysrc(8)` does for `rc.conf`. |

## How they talk

The console and the agents speak *cblink*, a small RPC protocol over
TCP, SCTP or a local socket, with mutual TLS 1.3 on the network: the
console proves who it is with a client certificate, the agent with a
server certificate, both signed by the console's own CA unless you
bring yours. The messages are CBOR, and their shape is one file in
Arcana's tree, `share/arcana/arcana.yaml`, from which both sides' code
is generated.

When the console runs on a host that has its own agent, it reaches it
through a local socket instead, and the console itself stays
unprivileged.

## Where things are kept

| What | Where |
|---|---|
| The console's settings | `/usr/local/etc/arcana/web.conf`, `kore.conf` |
| The console's data (keys, hosts, workflows, SD-WAN) | `/var/db/arcana` |
| An agent's certificates | `/usr/local/etc/arcana` on the host |
| An agent's local socket | `/var/run/arcana-agent.sock` |
| Changes kept for a boot | where FreeBSD keeps them: `rc.conf`, `jail.conf`, `/etc/fstab`, the plugins' own files |
