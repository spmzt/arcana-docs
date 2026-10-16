# Check, plan and apply

A document is kept only once the console has checked it against MEF
70.2, and is made on the edges only when you ask: the **Edges** tab
shows what the services would make on each edge, and **Deploy** makes
it, step by step, in the order Mplify 119 sets out.

## Dashboard

![The Dashboard](../img/sd-overview.png)

**Dashboard** counts what there is, each number naming the FreeBSD
piece that does the work (routing tables by setfib, tunnels by gre,
gif, geneve, wg and uswe, IPsec by strongSwan or keyed by the agents,
the rules in an ipfw set),
draws the edges with the tunnels between them as their probes see them
(green up, red down, dashed a backup, a lock encrypted, the delay and
loss on each) or as planned before an apply, and lists the underlays,
the edges and the services in tables, with forms: **+ underlay** (its
type, billing, the tunnel kind over it and IPsec under it), **+ edge**
(a host the console has), **+ WAN link** on an edge (the underlay, the
interface picked from the host's own list with the address it has, the
gateway, bandwidth, breakout and backup), each changed with the pencil
or taken away with the cross, the document kept at each step and
checked as a whole; **Services** has the same for a service and its
parts: **+ service** (id, routing table, reserved prefixes, underlays,
provider AS, evaluation interval, BFD), **+ end point** (an edge, its
interface from the host's list, a VLAN tag, the IPv4 and IPv6 subnets
with the edge's address in each, a NAT prefix), **+ zone** (name and
prefixes, or the Default), **+ flow** (applications from the catalog,
DSCP, protocol, ports, prefixes, or everything), **+ policy** (the
tunnel criteria, breakout, the destination zones, performance by a
metric with threshold, ceiling and remediation, bandwidth by a limiter
or a commit and limit, importance; for egress, the block), and **+
rule** on an end point (zone, flow or group, ingress and egress policy)
or on a zone (flow and policy). What a form does not ask for, as
virtual topologies, rate limiters, secondary subnets or BGP at a UNI,
stays as it is and the Document tab writes. It shows one service's
end points, zones, flows (in the
order they are matched), policies, topologies and rate limiters;
**Document** the whole of it as JSON. **Check** asks the console
whether it is one the standard allows and **Keep** keeps it; what the
console says no to names where, and the requirement:

```text
swvc office, policy realtime: performance: the ceiling is the
threshold or above it (R72)
```

A change is made from the version it was read at; one made from an
older version is refused, so two pages do not undo each other. **Start
from an example** writes one with two of the console's hosts as its
edges.

## What an edge changes on its host

Making a host an edge, and giving it its WAN links, changes the host
only as follows, and only once a plan is applied (**Deploy**, which says
first what it will make):

- **IP forwarding** turned on for IPv4 and IPv6
  (`net.inet.ip.forwarding`, `net.inet6.ip6.forwarding`), kept in
  `/etc/sysctl.conf`.
- **NTP**, when the edge names servers: `ntpd(8)` set to them.
- **A WAN link's interface is not touched** while it is left
  **Static** with no routing table of its own, which is how a link is
  made: its addresses and routes stay as the host has them, and the
  link only says which interface and address the tunnels start from.
  Only a link you set to **DHCP** gets `dhclient(8)`, to **SLAAC**
  `rtsol(8)` (`ifconfig_<if>="DHCP"` or `inet6 accept_rtadv`, kept in
  rc.conf), and only a link given a **routing table (VRF)** is put in
  it (`ifconfig <if> fib N`). Undone, each goes back to static and
  table 0.
- **The link the console reaches the host through** is said in its
  form: DHCP or SLAAC may give it another address, and a table of its
  own sends its replies by that table, so either can lose the host to
  the console. The form refuses to give that link either unless you
  tick that you reach the host another way too, or that its address
  and routes stay.
- Once a service uses the edge: more routing tables (`net.fibs`), the
  service's tunnels in its table, its routes, ipfw rules in set 30, and
  BIRD, strongSwan, local-unbound, Squid or Suricata as it asks, each
  listed below.

## Edges

![The Edges tab, before an apply](../img/sd-edges-plan.png)

**Edges** shows what the kept services make on the edges, and makes
it: **Deploy** says first what it will make, make again and take away
and asks, then runs it, each edge's steps done so far shown on its
line while it runs; the table lists each edge's objects by step in
the order they are made, the changes alone until **Show all**; **Past
applies** lists the last fifty, when, how each went and what it did.
Each edge is to have, for each service on it:

- `net.fibs` raised to the highest service FIB on it, and one (never
  lowered). It is per vnet: a fresh vnet has 1. `net.add_addr_allfibs`
  must be 0, the default: at 1 an interface's addresses are routed in
  every table and no service can have one of its own, so the step
  fails and says so.
- strongSwan's key and daemon, when one of its tunnels wants IPsec.
- Its end of each tunnel (a Tunnel Virtual Connection, §7.10): one
  between each two edges of a service, over each two of their UCS End
  Points that a tunnel can join (the same underlay, or two public
  ones), each End Point with its outer `address`. The tunnel is the
  underlay's `tunnel`: gre, gif or geneve, under IPsec IKEv2 in
  transport mode when it says `ipsec` (a public underlay does unless it
  says otherwise; and every tunnel of a service does when one of its
  policies says `encryption` `required-always`, R39, which an underlay
  that says no IPsec cannot meet), or wg. One IKEv2 connection serves
  every tunnel of a kind between the same two outer addresses: in
  transport mode it protects all of them, and two would conflict. It is in the service's FIB, its outer packets
  in FIB 0, its inner addresses a /31 and a /127 of the service's
  reserved prefixes; each end has its own unit (`gre100`, `gre101`),
  since two ends may be one host. The far end is told once both ends
  have a key: the wg peer, or the IKEv2 connection with the far host's
  key, protecting only the tunnel's own packets (GRE, IP-in-IP, or
  UDP for geneve).
- Routes in the service's FIB: each far end point's prefixes by a
  tunnel to its edge, one that is no backup first and a private one
  before a public one; and each UNI's static routes. A prefix no tunnel
  can carry (an IPv6 one with no IPv6 reserved prefix for the tunnels'
  inner addresses, say) is left out, and the plan says so in a note.
- The UNIs, last: the interface, or a VLAN on it, in the service's FIB,
  with the provider's addresses.

Each is a row with the jobs that make it, and whether it is to be
made, made again (its jobs changed), taken away, or is as it is.
**Apply** takes away what goes, last made first, and then makes what
comes in the order of Mplify 119's activity flow (§12.1, steps 1 to
13), each step on every edge before the next; a step that fails takes
away what it made and stops the apply. The Edges tab names each row's
step:

| Step (§12.1) | What Arcana makes |
|---|---|
| 1 VRFs | the services' tables, the domains' and the underlays' (net.fibs raised, setfib); forwarding on |
| 2 Synchronization | ntpd by the edge's servers |
| 3 UCS UNIs | the WAN links' interfaces: their table, addressing, routing with the underlay |
| 4 Control plane | the control tunnels (CTVC), their key pairs and SAs; the iBGP to the host, by BIRD |
| 5 UTVCs | the data tunnels: gre, gif, geneve, wg or uswe, IKEv2 under them or the agents' keys; no GRE with MPLS labels (not supported) |
| 6 SD-WAN UNIs | the UNI interfaces and VLANs, their addresses, router advertisements and DHCP |
| 7 Subscriber routing | the routes written, and BIRD at the UNIs (static, BGP, OSPF) |
| 8 Application flows, 9 Zones | the ipfw tables and rules in set 30 |
| 10 Policy map | the steering: each far prefix by its policy's tunnels in order |
| 11 Fault management | BFD on the tunnels in BIRD; the agents' faults (§11.3) |
| 12 Performance monitoring | the probes, their thresholds |
| 13 Enable SD-WAN UNI | the UNIs come up last (R169) |

What was made is
kept in `sdwan-state.json` with the jobs that take it away again, and
the tunnels' units and addresses, so that one added moves none of the
others. **Make all again** takes everything made away first.

A wg tunnel's FIB is set, but not kept across a reboot: wg-quick(8),
which brings wg up at boot, gives its addresses before any table can
be set. gre, gif and geneve keep theirs in `rc.conf`.
