# The service as L3NM, SAP and VN

The panel speaks MEF 70.2 and Mplify 119: underlays, edges, SWVCs, UNIs,
zones, flows, policies. What the console **stores** is the IETF's
network model of a layer 3 VPN, **L3NM** (RFC 9182, over RFC 9181's
`ietf-vpn-common`), with Arcana's module `arcana-l3nm` adding what an
SD-WAN service has that L3NM has no node for, in MEF's terms. The MEF
70.2 document the **Document** tab shows is made from it at each read,
and kept into it at each **Keep**: one service, one source of truth,
two vocabularies.

Beside it, two views the console makes and does not store: the
**SAP** network (RFC 9408), where on the fleet a service can be
attached, and the **VN** (RFC 9731), the service as its customer sees
it, end to end, with its paths' bounds.

```text
                 the page (MEF 70.2's terms)
                          │  Keep / Document
                          ▼
  arcana-console:sdwan/document ── import / export ──┐
                                                    ▼
  /restconf/data/ietf-l3vpn-ntw:l3vpn-ntw   ◀── stored (L3NM + arcana-l3nm)
        │                     │                     │
        ▼ planner             ▼ read                ▼ read
  plan, ledger, apply   ietf-network:networks   ietf-vn:virtual-network
  (the edges' commits)  (SAPs, from the agents)  (VN, its members' tunnels)
```

## Where each MEF term is kept

| MEF 70.2, Mplify 119 | L3NM (RFC 9182) | `arcana-l3nm` |
|---|---|---|
| **UCS** (§12), its tunnel kind and IPsec | — | `l3vpn-ntw/sdwan/ucs` |
| **SD-WAN Edge** (§7.8) | a `vpn-node` of each service it has end points of: `vpn-node-id` the edge, `ne-id` its host | `l3vpn-ntw/sdwan/edge`, its NTP, own table, transit |
| **UCS End Point** (§12.3) | — | `edge/ucs-end-point`: interface, address, gateway, bandwidth, breakout, backup, addressing, VRF, routing |
| **SWVC** (§9) | a `vpn-service`, `vpn-id` its id | `vpn-service/sdwan`: the FIB, its UCSs, reserved prefixes |
| **Routing domains** (Mplify 119 §7.3: service, breakout, subscriber) | `vpn-instance-profiles`: RD and route targets L3NM's (an `ASN:n` written `0:ASN:n`), `local-as` the provider AS | each profile's `domain`, `fib`, `label`, `prefix`; a profile `subscriber` always |
| **SWVC End Point** at its **UNI** (§10, §11) | a `vpn-network-access` at the edge's `vpn-node`: `interface-id` the UNI's interface, a VLAN its `dot1q` `cvlan-id`, the first provider address and the subnet's length `local-address` and `prefix-length`; static routes, BGP and OSPF its `routing-protocols`; a BGP password the explicit key | the access's `sdwan`: UNI id, policy map, NAT, CLAT, remote access (WireGuard identities and groups); each family's `mode`, `provider`, `reserved`, `dns`, `lease`, `secondary` |
| **Zones** (§9.5), **Application Flows** and groups (§9.14), **Policies** (§9.12) with their steering criteria, **virtual topologies** (§9.6), **rate limiters**, **importance**, intervals (§9.7) | — | `vpn-service/sdwan` |
| **Security function policies** and **security policies** (MEF 138) | — | `vpn-service/sdwan` |
| BFD, TCA thresholds, probes | — | `vpn-service/sdwan` |
| Named lists | — | `l3vpn-ntw/sdwan/named-list` |
| **TVC** (§7.10) | — | none: the planner makes the tunnels, the VN shows them |
| The document's version | — | none: the datastore's change count, its entity tag |

Each `arcana-l3nm` node's description names the MEF requirement it
carries. A `vpn-service` without `arcana-l3nm`'s `sdwan` is an L3VPN of
L3NM's but no SWVC: it is kept, planned for nothing and left out of the
document.

The example's service, as it is stored (shortened):

```json
{"ietf-l3vpn-ntw:l3vpn-ntw": {
  "arcana-l3nm:sdwan": {
    "ucs": [{"id": "internet", "type": "public", "billing": "flat-rate",
             "tunnel": {"kind": "gre", "ipsec": true}}],
    "edge": [{"server": "a", "ucs-end-point": [
               {"id": "hq-inet", "ucs": "internet", "interface": "vtnet0",
                "address": "192.0.2.10", "gateway": "192.0.2.1", "breakout": true}]},
             {"server": "b", "ucs-end-point": [
               {"id": "br-inet", "ucs": "internet", "interface": "vtnet0",
                "address": "198.51.100.20"}]}]},
  "vpn-services": {"vpn-service": [{
    "vpn-id": "office",
    "vpn-instance-profiles": {"vpn-instance-profile": [
      {"profile-id": "subscriber", "local-as": 64600, "rd": "0:64600:3",
       "arcana-l3nm:domain": "subscriber", "arcana-l3nm:fib": 1}]},
    "vpn-nodes": {"vpn-node": [{
      "vpn-node-id": "a", "ne-id": "a",
      "active-vpn-instance-profiles": {"vpn-instance-profile": [{"profile-id": "subscriber"}]},
      "vpn-network-accesses": {"vpn-network-access": [{
        "id": "hq", "interface-id": "vtnet2",
        "vpn-network-access-type": "ietf-vpn-common:multipoint",
        "vpn-instance-profile": "subscriber",
        "ip-connection": {"ipv4": {
          "local-address": "10.1.0.1", "prefix-length": 24,
          "address-allocation-type": "ietf-l3vpn-ntw:static-address",
          "arcana-l3nm:mode": "static", "arcana-l3nm:provider": ["10.1.0.1"]}},
        "arcana-l3nm:sdwan": {"uni-id": "uni-hq"}}]}}]},
    "arcana-l3nm:sdwan": {
      "fib": 1, "ucs": ["internet"], "reserved-prefix": ["100.64.0.0/24"],
      "zone": [{"name": "office", "prefix": ["10.1.0.0/16"]}],
      "application-flow": [{"name": "web", "criteria": {"protv4": ["tcp"], "dport": [80, "https"]}}],
      "policy": [{"name": "fast", "direction": "ingress",
                  "criteria": {"encryption": "required-public-only"}}]}}]}}}
```

### What does not come back the same

The document and the L3NM say the same service, but not every way of
writing it survives the round trip: a value that may be an object or a
list of one comes back as one of them; `null` and absent, `false` and
absent (BGP multihop, a UNI's routing), an empty object and none are
alike; a prefix comes back in inet_ntop(3)'s form; an OSPF area of none
is the backbone; a service's end points come back by edge, and a UNI's
static routes by family. A member the models do not have is no longer
kept.

## Reading and changing it

The L3NM is the console's own datastore, at
`/restconf/data/ietf-l3vpn-ntw:l3vpn-ntw`, operators' and owners':
GET, POST, PUT, PATCH, YANG Patch and DELETE, each change checked first
as RFC 7950 says (types, keys, mandatory nodes, leafrefs, `when`,
`must`), then as MEF 70.2 says (the same checks **Check** makes), all or
nothing. It is kept in the console's `l3nm.json`, through the cluster
where there is one.

```
curl -H "Authorization: Bearer $TOKEN" \
    https://console.example/restconf/data/ietf-l3vpn-ntw:l3vpn-ntw/vpn-services/vpn-service=office
```

The document is `arcana-console:sdwan/document`, written whole (its
`version` the L3NM's change count): a change by either way changes the
other, and a page holding an older version is refused, as two pages
are ([Check, plan and apply](apply.md)). See
[The API: RESTCONF](../automation/restconf.md) for the rest of
`arcana-console:sdwan`.

<div class="freebsd">

**FreeBSD:** nothing of L3NM is a FreeBSD notion, and none needs to
be: a VPN instance profile's `fib` is a routing table of `setfib(1)`,
a `vpn-node` a host or a vnet jail with `arcana-agent(8)`, a
`vpn-network-access` an interface or a `vlan(4)` in that table. The
console turns one into the other in its planner; the agents only ever
see their own models (`ietf-interfaces`, `ietf-routing`,
`ietf-network-instance`).

</div>

## The SAP view: where a service can attach

Each agent serves its host as a node of RFC 9408's SAP network, at
`H/ietf-network:networks/network=arcana-sap`: a termination point for
each interface (its vnet jails' too), and a **SAP** for each one a
service can be attached to, a UNI candidate, with its kind:

| Interface | SAP |
|---|---|
| Ethernet (the hardware's) | `phy`, `untagged-int`, child SAPs allowed |
| a cloned one, `epair(4)`, `tap(4)`, `vxlan(4)` | `logical`, `untagged-int`, child SAPs allowed |
| `lagg(4)` | `lag`, `lag-int`, child SAPs allowed |
| `vlan(4)` | `logical`, `dot1q` (`qinq` with a second tag), its parent named |
| `bridge(4)` | `irb` with an address, else `local-bridge` |
| a lagg's port, a bridge's member, the loopbacks, the tunnels (`gif`, `gre`, `wg`, `ipsec`), `pflog`, `pfsync`, `enc` | none |

A SAP's `sap-status` is its interface's state (up `op-up`, down
`op-down`); an `epair(4)`'s two ends name each other as peers, across
vnets too. The agent tells a change as it happens (YANG-Push on-change).

The console merges them at `/restconf/data/ietf-network:networks`, the
hosts you may read: `arcana-physical`, each host a node and each epair a
link, and over it `arcana-sap`, the same nodes with their SAPs. A SAP's
`service-status` is the console's, from the L3NM: the access that
names its interface at the `vpn-node` whose `ne-id` is the host, its
admin status the access's (else its node's, its service's), its
operational status up where the last apply made that UNI and the SAP
is up. `arcana-l3nm` adds to each SAP its `attachment` (service,
access, node, made), whether it is `free` (a UNI candidate, up, named
by no access, with no anomaly), and its `anomaly`, RFC 9408 §5's rules
as checks:

- `sap-down-service-up`: a service admin-up at a SAP that is down;
- `service-down-oper-up`: a service admin-down where its UNI is made
  and the SAP is up.

**Attach** (RFC 9408 Appendix D) makes an end point of a free SAP:
`arcana-console:sdwan/attach` with the service, the edge's node, a SAP
(or none: the first free one fit for the access, one allowing child
SAPs for a VLAN) and the access; it reads the host's SAPs through the
fleet mount, takes the SAP, and adds the access to the L3NM (the node
too, where the service has none there), as a PATCH of it would. The
next plan makes the UNI as of any access. A SAP not free, none free,
or an access of that id at the node is 409.

<div class="freebsd">

**FreeBSD:** the agent finds the SAPs as `ifconfig(8)` does: the
interfaces by `getifaddrs(3)`, their kind by their cloner's group
(`epair`, `tap`, `vxlan`), `vlan(4)`'s tag and parent, `lagg(4)`'s
ports, `bridge(4)`'s members; a vnet jail's through a helper attached
to it with `jail_attach(2)`.

</div>

## The VN view: the service as its customer sees it

RFC 9731's `ietf-vn` is the customer's side: **access points** where
the service is reached, the service's **virtual network**, and its
**members**, each a path between two access points. The console makes
it of the L3NM at each read, at `/restconf/data/ietf-vn:access-point`
and `/restconf/data/ietf-vn:virtual-network`, read alone (a change is
405, naming the L3NM as where to make it), with the L3NM's entity tag:

| ietf-vn | Is |
|---|---|
| a VN | each `vpn-service`, its id the `vpn-id`; admin-down where the service is |
| an AP | each place a host attaches accesses, the SAP: `<ne-id>:<interface-id>` |
| a VNAP | each access there, `<vpn-id>:<access-id>` |
| a VN member | each pair of a service's accesses on two nodes, `<node>:<access>~<node>:<access>`: the tunnels between their edges; none between two spokes |
| `path-metric-bounds` | the service's TCA thresholds: delay as `path-metric-delay-average` (µs), and `arcana-sdwan-underlay`'s `path-metric-loss` (millionths) and `path-metric-delay-variation` (µs), which RFC 8776 has not |
| a member's `underlay` (`arcana-sdwan-underlay`) | the tunnels the plan makes between its two edges: UCS, encapsulation, FIB, VNI, IPsec, backup, the probes' DSCP, BFD, each end's UCS End Point, outer address and FIB, interface and inner addresses; and, from each edge's steering, the far end's state and whether it is in use |
| `oper-status` | a member up where one of its tunnels is up, down where all are, else unknown; the VN the same of its members |

**vn-compute** (`POST /restconf/operations/ietf-vn:vn-compute`) is
the Check of a path, nothing made: for each member asked for, its
access points, the plan's tunnels between its edges, and its bounds
(its own, else the input's) against the last samples each edge's
steering has of each tunnel, the worse of the two ends. A tunnel within
every bound is `up`, one unmeasured `unknown`, else `down` with
`error-info` and RFC 9731's reason: `vn-computation-ap-unknown`,
`-path-not-found` (two VNs, no member, no tunnel) or `-no-resource`
(the bounds no tunnel meets, each excess named). Bandwidth, class of
service, optimizations and disjointness are not checked: no edge
measures them.

```
curl -X POST -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/yang-data+json' \
    -d '{"ietf-vn:input":{"vn-member-list":[{"id":"1","src":{"ap":"a:vtnet2"},"dest":{"ap":"b:vtnet2"},
         "path-constraints":{"path-metric-bounds":{"path-metric-bound":[
           {"metric-type":"ietf-te-types:path-metric-delay-average","upper-bound":"30000"}]}}}]}}' \
    https://console.example/restconf/operations/ietf-vn:vn-compute
```

<div class="freebsd">

**FreeBSD:** the samples are each edge's probes, ICMP echo to the far
inner address of each tunnel on a raw socket in the service's table
(`setfib(2)`), and the steering's choice is the edge's own
([Probes, rules and steering](steering.md)): the VN reads both through
the fleet mount (`arcana-steer:steering/state`).

</div>

## The planner's ledger

The planner reads the L3NM: each service's VPN instance profiles
resolved for each node (RFC 9182 §7.6.1: the node's active profile,
then the node's own `local-as` and `router-id` over the service's; its
RD as written, a suffix to its router id, or allocated for `rd-auto`),
and the augments in MEF 70.2's terms, checked as MEF 70.2 says before
anything is planned.

What it allocates, it keeps in the **ledger**, the apply's
`sdwan-state.json`: `fib:<service>` (the lowest table no service,
domain or entry has, for a service whose profiles name none),
`fib:<service>/<node>` its table on each node, `rd:<service>/<node>`,
the tunnels' units, VNIs and inner address pairs, the loopbacks', the
identities' addresses; and the ipfw tables named by the service's
table (`sw<fib>_…`). An entry stays while its owner is there, so a plan
after a plan allocates nothing new and a tunnel added moves no other.
`arcana-console:sdwan/ledger` shows it with each node's resolved
profile.

<div class="freebsd">

**FreeBSD:** a FIB is a number below `net.fibs`, raised as needed and
never lowered; a tunnel's unit is its interface's (`gre100`,
`gif101`); the inner pairs are a /31 and a /127 of the service's
reserved prefixes, and the ipfw tables live in set 30.

</div>

How the plan becomes each edge's commits, and the warnings an apply
accepts, is [Check, plan and apply](apply.md#how-an-edge-is-changed).
