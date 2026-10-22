# Several uplinks, several tunnels: the mesh

What a service needs when its edges have more than one way to each
other, and more than one way out: tunnels of several kinds between the
same two edges, uplinks that are metered, behind NAT or reached through
a relay, an edge that is a host with jails rather than a router of its
own, loopbacks the routing rides on, one edge standing in for another
when every direct path is down, and destinations picked by what BGP
says of them. Every attribute here is Arcana's own beside MEF 70.2 and
Mplify 119, named in [The document](document.md)'s terms, and each is
checked by **Check** with the message quoted.

## The tunnels' MTU

A UCS's `tunnel` takes `mtu`: `auto`, or 1280 to 9000 bytes. `auto`
is 1500 less the tunnel's overhead (the kind's, IPsec's under it, an
IPv6 underlay's), and the smallest over a pair of edges is set on
every tunnel of that pair, each end, so the two ends agree. The MSS
clamp (`mss`) follows from it. With GRE and the like
([gre(4)](https://man.freebsd.org/gre/4)), the interface's MTU is
what the host fragments by; set too high, large packets vanish where
ICMP is filtered, and set by hand on one end only, TCP stalls one way.

## Several kinds of tunnel between two edges

Two edges may be joined by tunnels of several kinds at once, each a
transport the far side may block or not: one public UCS per kind
(`inet-gre` with IPsec, `inet-wg`, `inet-gif`, `inet-geneve`, say),
and on each edge a UCS End Point per UCS, all on the same interface.
Two public UCSs join only when their tunnels are of the same kind with
the same IPsec setting, so K transports give K tunnels per pair, not
K². ([gre(4)](https://man.freebsd.org/gre/4) and
[gif(4)](https://man.freebsd.org/gif/4) refuse a second interface over
the same outer address pair, so plain GRE and GRE under IPsec cannot
share one; that is one UCS, not two.)

A UCS End Point's `preference` (0 to 65535, the higher first) orders
the edge's uplinks where a policy names none (`ucs-end-point-list`
orders them for one policy), and picks the breakout taken first when
the edge has several. A UCS's `billing` `usage-based` marks a metered
link; with a low preference it carries traffic only when the others
cannot.

## WireGuard behind NAT, through a relay, in a table of its own

A UCS End Point on a WireGuard underlay takes:

- `nat: true` when it sits behind NAT (CGNAT, a home connection): the
  far peers get no `endpoint` for it, this end keeps the session alive
  (`persistent-keepalive`), and it is the one that calls.
- `relay`, a list of `{to, endpoint, port}`: toward the edge `to`, the
  wg peer's endpoint is `endpoint` (host:port, a process on this host
  such as a forward-error-correction or obfuscation relay listening
  there) instead of the far underlay address, and the relay itself
  reaches the far edge's underlay at `port`; the relay's own UDP is
  sent by the end point's `vrf` (an ipfw `setfib` rule in the service's
  set, before the zones). The relay process is yours: Arcana installs
  nothing.
- `vrf`: as for any uplink, the table the underlay is in; a wg tunnel
  over such an end point gets that table as its `tunnelfib` too, so
  its outer packets leave by the uplink's table and never by the
  service's. (With a relay the socket must reach the relay in table 0,
  so there is no tunnelfib then.)

Both are plain
[wg(8)](https://man.freebsd.org/wg/8) peers and `ifconfig tunnelfib`
on the host; nothing else is added.

## Equal-cost paths

With more than one tunnel between two edges, the far prefixes' kernel
routes are multipath: every tunnel that is no `backup`, as one route
with as many next hops ([route(8)](https://man.freebsd.org/route/8)'s
weighted ECMP, not persisted, since
[rc.conf(5)](https://man.freebsd.org/rc.conf/5) cannot keep one). A
service with BIRD gets `merge paths on` in its kernel protocols, so
the paths iBGP learns by each tunnel (each with `next hop self`) go to
the kernel as one route too. The steering still picks one path per
policy by the probes; ECMP is what the kernel does when the steering
says nothing.

## An edge that is a host with jails: its own table

An edge with `own_table: true` keeps the services' overlay in the
host's own routing table, FIB 0, instead of a table of the service's
(`swvcs[].fib` stays the number the objects are named by). The
uplinks go to tables of their own (`vrf`), the host's default route
stays the host's, and the host's jails, bridges and daemons see the
service's routes without moving anywhere. On such an edge
`net.add_addr_allfibs` is set to 1 when its uplinks have a `vrf`, so
the uplinks' connected routes are in table 0 too; a service breaking
out here needs its `domains.breakout.fib`, since the host's default
route is not the service's to write.

With `host_bird: true` the host runs a BIRD of its own in table 0,
and no service that needs one here (BFD, routing at a UNI) may use
the edge: Check says which. A UNI with `host_addressed: true` has its
addresses already (a bridge the jails hang off): the apply adds and
takes away none, and `ipv4.prefix` is the aggregate the far ends
route. On an own-table edge the service's BIRD writes its routes into
FIB 0, beside what the host has there.

## iBGP between loopbacks, transit by the others

A service with `ibgp: "loopback"` (the default, `"tunnel"`, is one
session by each tunnel) gives each edge a loopback address of the
service's reserved prefixes on a cloned
[lo(4)](https://man.freebsd.org/lo/4) of its own in the edge's table,
and one multihop iBGP session with each other edge, loopback to
loopback. Each edge's BIRD has a static route to every far loopback
over every tunnel to it, each path watched by BFD (`bfd` on the next
hop; the service needs `bfd`), backups in a static of lower
preference; the session rides whichever paths are up and moves with
them without ever dropping. The UNIs' prefixes are the edge's own
statics (`orig*`), kept out of the kernel's table (the UNI is
connected there) and advertised to the others; no far prefix is
written into the kernel by the console, iBGP does.

Edges with `transit: true` (the default) are route reflectors (RFC
4456, `rr client` on their sessions): a route one edge advertises
reaches the others through them, and so does a loopback. BGP's
preference (100) is below the statics' (200), so a route through a
third edge is taken only when every direct path to the far loopback
is withdrawn by BFD. `transit: false` on an edge keeps it out of
that: it reflects nothing and is never a remote breakout for the
others, which is what a metered or a home uplink wants. It is one or
the other with `control_plane` (Mplify 119's reflector host).

## BIRD on an edge that is a jail

A vnet jail edge (`server/jail`) takes BFD and routing at a UNI like
a host: the service's BIRD runs in the jail
([jexec(8)](https://man.freebsd.org/jexec/8), `setfib`), its
configuration, socket and pid under the jail's `/var/run`, named
`sw<fib>-<jail>`, and the agent keeps and restarts it with the
host's. The host's BIRD, if any, is untouched.

## Breakout failover

An edge with several `breakout` uplinks routes each one's gateway by
its interface in the breakout table, writes the default by the most
preferred (`preference`), and probes each uplink's `beacon` (an
address of the Internet reached by that uplink alone; without one, the
gateway). The agent's steering takes the first uplink whose beacon
answers and puts it in the default route's place
([route(8)](https://man.freebsd.org/route/8), in the service's or the
breakout's table), and back when the preferred answers again; the
Paths tab shows each beacon beside the tunnels. The kernel's weighted
ECMP shares a load but does not fail over, and BFD to an ISP's
gateway does not exist, which is why a probe does it.

## NAT64 and CLAT

A service with `nat64` (`prefix`, an IPv6 /96, `64:ff9b::/96` as a
rule; `pool`, an IPv4 prefix of the edge's; `edge`, the one that
translates) lets its IPv6-only hosts reach the IPv4 Internet: on that
edge an ipfw `nat64lsn` instance (RFC 6146, stateful,
[ipfw(8)](https://man.freebsd.org/ipfw/8), `ipfw_nat64` loaded and
kept) translates what comes in for the prefix before the zones, the
pool is among the known prefixes so the breakout's NAT takes it out
like a UNI's, and what comes back for the pool is translated after
the NAT. A UNI with `clat` (`prefix`, an IPv6 /96 of its own) gives
its IPv4 hosts a CLAT (RFC 6877, `nat64clat`) with the service's
NAT64 as its PLAT: their IPv4 goes out as IPv6 and is routed to the
NAT64 edge like the UNI's subnet; a CLAT needs the service's `nat64`.
Neither is MEF 70.2 §10.5's NAT.

## Destinations by what BGP says: sets

A service's `bgp_sets` are destination sets learned from BGP rather
than written as prefixes: each a `name`, `as_path` (a list of AS
numbers; a route whose path holds any of them is in the set) and
`communities` (`[as, value]` pairs; a route carrying any is in it).
An edge's `breakout_sets` (`{set, via}`) sends each set out by one of
its own breakout uplinks, `via` the UCS End Point's id: the edge's
BIRD exports the matching routes to the kernel with that uplink's
gateway as their next hop (`gw` in the kernel protocol's export
filter), the gateway routed by its interface in the service's table,
so those destinations leave by that uplink whatever the default says.
`bgp_import` on an edge says what else BGP writes: `all`, every route
(the default), or `sets`, the matched routes alone, the kernel keeping
its own default route for the rest, which an own-table edge with a
default of its own wants. The routes come from an edge that leaks them
into the service's BIRD (a border edge with eBGP of its own, by hand);
iBGP keeps the AS path, so a set matches on every edge. ipfw's `fwd`
is not used for this: a set may be a hundred thousand prefixes, which
are the kernel's routing table's to hold, not a rule's.

## Neighbours at a UNI, by family

A UNI's `routing` takes `bgp` and `ospf` as one entry or a list of
them, so a UNI may have an OSPF area per family and several BGP
neighbours, each of its own AS. A `bgp` entry adds to §11.6's
attributes:

- `bfd: true`, the session watched by BFD, and the UNI's interface
  joined to the service's BFD;
- `source`, an address of this edge's the session is from (the
  loopback of the section above, say): the session is then multihop;
- `multihop: true` for a neighbour outside the UNI's prefixes;
- an `as` equal to the service's own: iBGP, with `next hop self`.

An `ospf` entry takes `bfd: true` on its interface too. A router that
never gets an agent, a wireless controller or a modem router, stays a
neighbour of the service this way for good; what it advertises
reaches every edge, and what the edges hold reaches it.

## The apply, in safe mode

Every job the apply sends is in safe mode where the host can undo it
(a tunnel, a route, an address, a sysctl, a BIRD configuration, a
WireGuard or IPsec change), and the console's next successful read of
the job, over a fresh connection, confirms it: a step that cut the
host off from the console is taken back by the host itself after
`safe_wait`. The apply keeps the list of what it made, and on the
first failure unmakes all of it, last phase first, so an edge is
never left half made (`rolled back`, naming the step, in the apply's
history). The Deploy dialog says this as it is, and the `sdwan-*`
operations (steering, probes) are swaps, not jobs.
