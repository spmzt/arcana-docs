# A host: summary, jails, services

A host's page has a header and a row of tabs. The header says what the
host is (FreeBSD's version and machine, CPUs, memory, uptime, whether
the agent runs as root, the agent's version) and carries **Update
agent** when the host runs another build than the console's.

## Summary

Usage gauges with their recent history, counts of jails, services,
packages and jobs, the ZFS pools, and the host's jails as a graph; a
jail picked in the graph opens in a box over the page.

![A host's summary](../img/tour-host.png)

### How it is reached

At the foot of the summary: the agent's listeners and the connections
open to the agent now, each with its transport, where it comes from and
the name in its certificate, read again every few seconds. A green
light is before the way the console itself gets in, the one it knows to
work; another the agent listens on has an empty one until it is tried.
The agent's local socket is listed only when it is the console's way.

The console keeps its connection to an agent open and sends the next
request over it; several requests at once have one each. An agent that
listens on TCP listens on SCTP as well, at the same address and port,
where the kernel has SCTP. It never loads the module itself: where it
is missing the listener is shown as down with the reason, and once
`sctp` is loaded from the Kernel tab, **Try SCTP again** has the agent
start it.

**Switch to SCTP** has the console ask the agent over SCTP first, and
only when it answers is the host reached that way from then on; when it
does not, nothing is changed. **Go back to TCP** does the same the
other way, and is also offered when a host reached over SCTP stops
answering. From a shell: `arcanactl transport [retry]`.

Over SCTP, the requests the console makes of a host at once all go over
one association, each waiting for its own answer: the agent sees one
session where over TCP it would see one for each. What comes in parts
(the kernel's state, the routes, connections and sockets) is a cblink
stream over that association, flow-controlled by itself: the host sends
a part only while the page has room for it, so a slow page holds its
own stream and nothing else.

<div class="freebsd">

**FreeBSD:** SCTP is the kernel's own `sctp(4)`, a module the agent
uses when it is loaded and never loads by itself; the association
carries many streams, each request on its own, so one slow answer holds
up no other.

</div>

### Rollback timer

Below it, the host's **rollback timer**: how long a change made in safe
mode waits there for the console to be heard from again before the
agent undoes it, 10 to 3600 seconds, or empty for the agent's own
(`arcana-agent -w`, a minute unless set). See [Safe
mode](network.md#safe-mode).

## Jails

Each jail with its state (running, stopped, dying; starting, stopping,
restarting while something happens to it; unknown when the host does
not answer), with **Start**, **Stop**, **Restart** and **Kill**. Those
running come first; **Sort** orders by running or by name.

### A jail's page

Each jail has a page of its own: its actions; its addresses, changed
live (with `jail_setv(3)` and the interface's alias), in its
`jail.conf` block (with a diff to preview), or both; its configuration
as `jail(8)` reads it; and its history.

![A jail's page](../img/tour-jail.png)

A jail with a network of its own (vnet) has **Open it in the Network
tab**: see [A jail's own network](network.md#a-jails-own-network).

## Services

The `rc.d` scripts, enabled or not, running or not, with **Start**,
**Stop**, **Restart**, **Reload**, **Enable** and **Disable**. Those
running come first, then those enabled; **Sort** orders by running,
enabled or name, and the other way round when pressed again. A
service's drawer edits its `rc.conf` variables through `sysrc(8)`, in
safe mode.

![The Services tab](../img/tour-services.png)

<div class="freebsd">

**FreeBSD:** running jails are read with `libjail(3)`, configured ones
from `jail.conf(5)` by Arcana's `libjailconf`, and acted on with
`jail(8)`; services are `service(8)` and `rc.conf(5)`, written with
`sysrc(8)`, for a jail in its own root (`sysrc -R`).

</div>
