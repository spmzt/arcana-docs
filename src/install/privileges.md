# What runs as root

Only the agent. Everything else is built to need as little as it can.

| Part | Runs as | Why |
|---|---|---|
| `arcana-agent` | root | It changes the host: jails, interfaces, routes, the firewall, packages. |
| The console (Kore and `arcana-console.so`) | `arcana` | It only talks: to your browser, and to the agents as a client. Kore's key manager keeps the HTTPS key out of the worker. |
| The panel | your browser | A web page, under the browser's own rules. |
| Builds the agent runs | `nobody` | When a host builds Arcana from its repository, `git` and `make` run as `nobody`; only installing runs as root. |

## What the agent refuses

The agent checks every request against the shape `arcana.yaml` gives
it before it does anything, and then against what is safe to do:

- over the network it accepts only a peer with a certificate the
  console's CA signed, over mutual TLS 1.3; on the host, only who may
  open its local socket (root and the socket's group);
- names that become paths or command words (a jail, an interface, a
  service, a package) are checked character by character;
- files inside a jail are opened beneath the jail's root and never
  through a link that leads out of it;
- what destroys (a dataset, an interface, a partition table) is done
  only when asked for by name, and a workflow that runs by itself may
  hold such a step only when it says so;
- secrets (private keys, IPsec keys) never appear in a trace.
