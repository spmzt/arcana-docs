# Glossary

## Arcana's words

| Word | Is |
|---|---|
| **Agent** | `arcana-agent`, on every host; the only part that runs as root |
| **Archive** | one of the seven domains the agent's source is laid out by: Superbia, Invidia, Ira, Acedia, Avaritia, Gula, Luxuria |
| **Console** | the web server module and the panel it serves; the fleet's manager |
| **Job** | a change asked of a host, run and kept by its agent, with its trace |
| **Kept rules** | the ipfw ruleset Arcana writes down, loaded at boot and by Apply |
| **Plugin** | what works through a program that is not FreeBSD's own: BIRD, strongSwan, Squid, dnsmasq |
| **Queue** | changes waiting in the activity bar to be sent together |
| **Rollback timer** | how long a change in safe mode waits to be confirmed before the host undoes it |
| **Safe mode** | a change the host takes back by itself unless the console is heard from again |
| **Trace** | what a request did on the host: each call, system call and program, with what it said |
| **Workflow** | a chain of steps run on several hosts, by hand, at an interval or on an event |

## MEF and Mplify

| Word | Is |
|---|---|
| **AFS**, Application Flow Specification | what a flow matches: addresses, ports, DSCP, application |
| **CTVC** | a control tunnel, carrying the control plane alone (Mplify 119) |
| **Edge** | an SD-WAN Edge: a site's box, here a host with the agent |
| **Policy** | what a flow gets: encryption, links, breakout, performance, bandwidth |
| **SWVC** | an SD-WAN Virtual Connection: the service |
| **TVC** | a Tunnel Virtual Connection between two edges over one underlay |
| **UCS** | an Underlay Connectivity Service: a link the provider buys |
| **UNI** | the User Network Interface, where the subscriber's hosts meet the service |
| **USWE** | the Universal SD-WAN Edge of Mplify 119, and Arcana's `uswe` tunnel kind |
| **Zone** | the hosts a set of rules applies to, by source address |

## FreeBSD's

| Word | Is |
|---|---|
| **FIB** | a routing table; a process or packet uses one, `setfib(1)` |
| **Jail** | a confined part of the system, `jail(8)` |
| **Netgraph** | the kernel's graph of networking nodes, `netgraph(4)` |
| **rc.conf** | where the system's settings for its start are kept, `rc.conf(5)` |
| **VNET** | a jail with a network stack of its own |
| **ZFS** | the file system and volume manager, `zfs(8)`, `zpool(8)` |
