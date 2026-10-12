# Routing and addresses at the UNIs

Where the subscriber's network meets the service: the routes a UNI
learns and advertises, by BIRD in the service's own routing table, and
the addresses its hosts get; and how the edges' own WAN links are
addressed and routed on the underlay.

## Routing at a UNI

**Routing at a UNI** (§11.6): besides its static `routes`, a UNI may
have `bgp` (`family` ipv4, ipv6 or both, the subscriber's `as`, its
`neighbors` at the UNI, within the UNI's prefixes, and maybe a
`password`, a `hold_time`, `communities` as `[as, value]` pairs added
to what the subscriber is sent, and a `distance`) or `ospf` (`family`,
`area`, and maybe `cost`, `hello`, `dead`, a `password` and a
`distance`); one of each, for one family or both (R139). A service
with any such UNI gets a BIRD instance of its own on each of its
edges, named `sw<fib>` and run by the agent in the service's table
(`setfib`, with a control socket and a pid file beside the agent's
kept files; `sdwan-bird`, kept and started again with the agent): the
kernel's table learned and kept, so what the console put there stays
and outranks what BGP brings; the UNIs' and the tunnels' connected
routes; iBGP with every other edge by each tunnel between them (the
service's `as`, 64512 unless said), next hop the tunnel's own address,
advertising the UNIs' routes and what they learn (not the kernel's
own, nor the reserved prefixes: a peer would resolve its next hop by
them in a circle), so what one UNI learns reaches them all; and at each UNI the protocol its entry says, the
`distance` its preference (256 less it, R140–R142). What a UNI learns
goes by the service's table and the tunnel iBGP chose, not by the
policies' tables: steering by performance is of the prefixes written
in the document. With `bfd` in a service (`interval` 100 to 300 ms,
`multiplier`, Mplify 119 §10.5 and R159), the instance watches each
tunnel interface by BFD and the edges' iBGP sessions go by it; the
agent reads the sessions every second into the `sdwan` read, a
session that goes down after it was up, or comes up again, is a fault
(`sdwan-tunnel`, by bfd, R60), and the steering takes BFD's word over the probe's where
there is a session. Paths shows BFD's state beside the probe's. With
`md5` in a service, the edges' iBGP sessions are signed with TCP MD5
(R12). With `control_plane` (`host`, an edge of the service, and maybe
a `cluster_id`), the full mesh gives way to Mplify 119's control plane
(§8.3, R9–R13): every other edge peers with that host alone, by each
tunnel to it, and the host's BIRD reflects their routes to all (RFC
4456, `rr client`, the cluster id its router id unless said); a plan
refuses a topology where an edge has no tunnel to the host. With
`ctvc`, one of the service's UCSs, the control plane gets a tunnel of
its own from each edge to the host over that underlay (the CTVC,
R5, R6: the UCS's tunnel kind, addresses from the service domain's
prefix, BFD and probes like any, steered by no policy), and the iBGP
goes by it and nothing else; without it the sessions ride the data
tunnels (the CPI as a virtual interface, R2). The service form asks
for the host, the cluster id and the control tunnel's underlay. RFC 4364's VPN routes with the
domains' route distinguishers, targets and labels (R14–R20) are not
written: they need BIRD's l3vpn protocol, which the FreeBSD port of
BIRD 3 does not build (known limits). An edge with `ntp` (its servers, in the edge form) gets them
written into its `ntp.conf` and ntpd enabled and restarted, with the
FIBs, so faults line up and keys can turn together (Mplify 119
§12.2.2); the `ntp` job does it, and `arcanactl ntp` by hand.

## The hosts' addresses at a UNI

**The hosts' addresses at a UNI** (§11.4, §11.5): with `static` the
hosts set their own and the edge only has the provider's addresses on
the interface. With `slaac` (IPv6, a /64) the base system's rtadvd
advertises the prefix on the UNI, and the `dns` servers as RDNSS: an
entry for the interface in `rtadvd.conf` between arcana's marks, the
interface on `rtadvd_interfaces`, rtadvd enabled and restarted (the
`rtadvd` job; `arcanactl rtadvd` by hand). With `dhcp` the edge gives
the addresses: the base system has no DHCP server, so dnsmasq from
packages (installed on the edge beforehand: see [Before using
SD-WAN](index.md#before-using-sd-wan)), an instance of each service on each
edge, run in the service's table by setfib like the BIRD instances,
checked by `dnsmasq --test` first, its pid and lease files beside the
agent's kept files, started again at the agent's start (`sdwan-dhcp`;
`arcanactl sdwan dhcp json`). It serves no DNS; its ranges are the
subnet's hosts less the provider's addresses and the `reserved`
prefixes (for IPv6, ::100 to ::ffff of the /64, less the reserved),
the router the provider's first address, the `dns` servers told, the
`lease` 12h unless said; for IPv6 it sends the router advertisements
that tell the hosts to ask. The apply also turns the kernel's
forwarding on, both families, kept in `sysctl.conf`. Paths lists each
edge's instances and the leases they gave, under Addresses given.

## The UCS End Points, addressed and routed

**The UCS End Points, addressed and routed** (Mplify 119 §12.2.3):
with `addressing` dhcp the apply puts the interface on DHCP (the DHCP
word of `ifconfig_<if>` in rc.conf, which dhclient's rc script reads,
and `service dhclient restart <if>`), with slaac on router
advertisements (`inet6 accept_rtadv` and rtsol once, kept in
`ifconfig_<if>_ipv6`); the `if-set` job's `addressing`, `arcanactl
interface <if> addressing` by hand. The end point's `address` may then
be left out: the plan asks the host for the interface's first global
address and uses it as the tunnels' outer one, and an end point whose
host has none yet is left without tunnels, with a note, until the
next apply. With a `vrf` the interface goes into that table and the
tunnels over it send their outer packets by it (`tunnelfib`; IPsec and
WireGuard keep the first table). With `routing` (`bgp` with the
underlay's `as` and `neighbors`, or `ospf`, as a UNI's entry) the edge
runs a BIRD instance of its own for the underlay, `ucs<vrf>`, in that
table, with the kernel's routes learned and kept and the interface's
connected ones; `sdwan-bird` keeps it with the services'.
