# Mplify 119

Mplify 119 (the Universal SD-WAN Edge) fixes how an edge of one maker
talks to a service of another: the routing domains, the tunnel format,
the keys, the faults, and the steps a manager sends. Arcana keeps the
MEF 70.2 service as it is and adds what Mplify 119 asks for, where a
service says so.

## The routing domains

**The routing domains** (Mplify 119 §7.3, R15–R26): a service's
`domains` name its tables beyond its own. With a `breakout` domain's
`fib`, the apply keeps the Internet apart from the subscriber's table:
the default route (by the local breakout gateway, or by the tunnel to
the edge that breaks out, whose far end gets a route by the tunnel
interface there) goes into the breakout table, the edge's own UNIs'
subnets and static routes are imported into it (R25, R26) once the
UNIs are up, so what comes back finds the hosts, the flows that break
out are sent to it by `setfib` before they leave, and what comes back
in at the breakout interface is set to it too; the service's own table
holds no default route then. net.fibs is raised over the domains'
tables as well. With a `service` domain's `prefix`, the tunnels' inner
addresses are taken from it rather than from the reserved prefixes,
and the edges' iBGP keeps it to themselves like them; its `fib` is
kept for the control plane interface to come. The route
distinguishers, targets and labels are checked and kept for the
tunnel format to come; nothing uses them yet.

## The uswe tunnel

**The uswe tunnel** (Mplify 119 §10): a UCS whose `tunnel` is of kind
`uswe` gets, for each pair of edges, an ipsec(4) interface at each end
whose reqid is its unit, ESP in tunnel mode keyed by the agents
themselves: the apply has each end make its X25519 pair (`ipsec-sa
key`), makes the interface with its outer ends, and then has each end
derive the SAs from the far end's public half, which the console reads
from that end's `sdwan` read and passes as `${uswe:SID:IF}` the way it
passes a wg key; `algorithms` picks AES-256-CBC with HMAC-SHA-256 or
AES-256-GCM, `esn` and `encap` (ESP in UDP) are on unless said
otherwise, and `lifetime` (seconds, a day unless said) is what the
keys are good for. No IKEv2 under it. The UCS form asks for it all
under "uswe only".

## The keys turned

**The keys turned** (Mplify 119 R110, R112): the console's manager
turns a uswe tunnel's keys at the half-life of their lifetime, both
ends in step and without a packet lost: a next pair made on each end
(`ipsec-sa key next`), its public half read from the sdwan read, the
new SAs from the two pairs put in inbound on both ends, then outbound,
each end's old outbound SA taken out as its new one goes in (`derive …
next install in | out`; the kernel would keep sending on the old one
otherwise, net.key.preferred_oldsa), then committed on both (`commit`:
the old inbound SAs taken out, the next pair made the pair). A rotation that
fails is kept with its step and why, tried again after two minutes,
and the end it failed on raises a `key-rotation` fault until one is
done. The Paths tab's Keys table shows each end's half, when it was
keyed and when it turns, and **turn the keys** does it now
(`POST /api/sdwan/rekey`); an apply waits for a rotation and a
rotation for an apply.

## Manually keyed security associations

**Manually keyed security associations** (Mplify 119 §10, R41–R50,
R55): the `ipsec-sa` job sets the two SAs of an ipsec(4) interface,
out and in, each its SPI and keys, ESP in tunnel mode on the
interface's reqid, with ESN and ESP in UDP (port 4500) where said,
AES-CBC with HMAC-SHA-1, -256 or -512, or AES-GCM-16 on its own; the
base system's setkey(8) reads them from a file the agent writes 0600
and takes out again, and neither the trace nor the job's title has the
keys. `clear` deletes every SA between the two outer addresses.
`arcanactl ipsec-sa` by hand. Rather than given, the keys are derived
(R51–R54): `key` makes an interface its X25519 pair, the private half
a PEM file 0600 beside the agent's kept files that nothing else reads,
the public half 44 characters of base64 in the `sdwan` read under
`keys`; `derive` takes the far end's public half (`peer`), the
algorithms and the flags, and computes both directions' SPIs and keys
from the agreement by HKDF-SHA256 (the two public halves in order and
an `epoch` number as the context), so the two ends, each with the
other's public half, set the same SAs mirrored; another epoch gives
other keys, for the rotation to come. Every SA gets an anti-replay
window of 1024 packets: without one, the kernel's two ends disagree
on the authenticated data of an AEAD cipher under ESN and every
packet fails its check.

## Conformance

What the document carries for each of Mplify 119's management plane
requirements (§12, R89–R160), and what is not done. The requirements
are the SD-WAN Vendor Manager's, which the console is; where the
table says a document attribute, the apply passes it to the edge as
jobs.

| Requirement | Document attribute | Done by |
|---|---|---|
| R89–R92 the VRFs of each UCS, the service, breakout and subscriber domains | `ucs_end_points[].vrf`, `swvcs[].domains.service.fib`, `domains.breakout.fib`, `swvcs[].fib` | routing tables by setfib, net.fibs raised |
| R93 NTP server addresses | `edges[].ntp` | ntp.conf, ntpd |
| R94, R95 UCS UNI and End Point interface identifiers | `ucs_end_points[].interface` | the host's interface |
| R96 MEF 10.4 Ethernet attributes (physical links, frame size, EVC EPs, C-tags, token share, envelopes) | — | not done: the interfaces are what the host has |
| R97 auto-negotiation | — | not done: ifconfig media is not written |
| R98–R101 IPv4 and IPv6 address, static or dynamic, prefix, gateway | `ucs_end_points[].address`, `gateway`, `addressing` (static, dhcp, slaac) | the interface's address, dhclient, rtsol; one address per end point, not both families |
| R102 the VRF of each UCS UNI | `ucs_end_points[].vrf` | ifconfig fib, tunnelfib |
| R103 the underlay's routing protocol | `ucs_end_points[].routing` (bgp, ospf) | a BIRD instance per underlay table |
| R104 UCS UNIs put into service | — | the apply's step 3 |
| R105, R106, R113, R115, R116 the CTVC: interface, address and prefix, its underlay interface, the far address, the service VRF | `swvcs[].control_plane.ctvc` (a UCS) | the control tunnel, step 4, in the service's table |
| R107, R110, R111 the key pair made by the edge, its public half told, a new pair at the half-life | — (the agent's) | ipsec-sa key, the sdwan read's keys, the manager's rotation |
| R108, R109, R112 authentication and privacy methods, key length and lifetime, the algorithms, the activation | `ucs[].tunnel` (`kind` uswe, `algorithms`, `esn`, `encap`, `lifetime`) | the derived SAs; the activation is the manager's rotation, in step on both ends, not a date and time |
| R114 DSCP and PCP of the CTVC | — | not done: the tunnels' outer packets are not marked |
| R117–R119 the CPI as a virtual interface | `control_plane` without `ctvc` | the iBGP by the data tunnels |
| R120 BGP router id | — | the edge's tunnel address |
| R121, R123 route distinguishers and MPLS labels per VRF | `domains.*.rd`, `rt`, `label` | kept, not used: VPN routes and MPLS in GRE are not supported (known limits) |
| R122 the BGP AS | `swvcs[].as` | BIRD |
| R124 BGP peer addresses | `control_plane.host` | the host's tunnel addresses |
| R125, R126 static routes to the control plane | — | not needed: the control plane host is an edge at the tunnel's far end |
| R127, R128 TCP MD5 on every control plane iBGP session | `swvcs[].md5` | BIRD's password, the tcp-md5 SAs in the kernel |
| R129, R130, R137, R139, R140 the UTVC: interface, address and prefix, its underlay interface, the far address, the UCS VRF | `ucs[].tunnel`, `ucs_end_points[]` | the data tunnels, step 5, in the service's table, their outer packets by the underlay's |
| R131–R136 encryption of the UTVC: keys, parameters, algorithms, rotation | `ucs[].tunnel` as the CTVC's | the uswe tunnel |
| R138 DSCP and PCP of the UTVC | — | not done |
| R141–R144 GRE of type 0x8847 and the three labels | — | not supported |
| R145, R146 the SD-WAN UNI's interface, VLAN, state, frame size | `end_points[].uni.interface`, `vlan`, `max_frame` | the interface or a vlan(4) on it, disabled until step 13 |
| R147–R150 the UNI's IPv4 and IPv6 addresses, static or dynamic | `uni.ipv4`, `uni.ipv6` (`static`, `dhcp`, `slaac`, `none`) | the provider's addresses, dnsmasq, rtadvd |
| R151 the UNI in the subscriber VRF | `swvcs[].fib` | ifconfig fib |
| R152 static routes | `uni.routes` | route(8) in the table |
| R153 BGP peers at the UNI: address, AS, MD5, password | `uni.routing.bgp` (`neighbors`, `as`, `password`) | BIRD |
| R154 application flows | `swvcs[].flows` | ipfw rules |
| R155 zones | `swvcs[].zones` | ipfw tables |
| R156 the policy map: UNI, flow, zone, the tunnels in order, breakout, allowed destinations, block | `end_points[].policy_map`, `policies` | ipfw rules and the steering |
| R157 irduration | `swvcs[].intervals.ir` | the probes |
| R158 alarm severities Warning to Critical | — | the agents' faults, all severities, in the sdwan read |
| R159 BFD 100 to 300 ms with its multiplier on every tunnel | `swvcs[].bfd` | BIRD's BFD |
| R160 faults retrieved | — | `GET /api/servers/<id>/sdwan` |

Not done, as the table says and beyond it: R96's Ethernet UNI
attributes and R97's auto-negotiation; one address per end point
where the specification allows both families; DSCP and PCP marking of
the tunnels' outer packets (R114, R138); route distinguishers,
targets and labels in the control plane's routes (R121, R123, RFC
4364's VPNv4 and VPNv6 by BIRD's l3vpn, which the FreeBSD port does
not build) and GRE with MPLS labels (R141–R144); a date and time for
a key's activation (R112, R136: the rotation is run in step on both
ends instead); more than one subscriber routing domain per service;
stateful threshold crossing alerts (the probes' are stateless, O1);
RFC 7317's hardware and virtual machine management (§12.7); and a
NETCONF, YANG or REST binding of the management plane (§7.5): the
console's own API and cblink are the management plane.
