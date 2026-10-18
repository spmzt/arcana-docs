# The document

The console keeps every SD-WAN service in one JSON document, which the
**Document** tab shows whole and the other tabs edit a part at a time.
Its names are MEF 70.2's; this chapter is its reference. For a document
to read beside it, see [A service with two edges](example.md).

**SD-WAN** in the side bar holds the SD-WAN services the console keeps,
named as MEF 70.2 (SD-WAN Service Attributes and Service Framework)
names them. It is one document with three parts, and the named lists
below them:

- `ucs`: the underlays (Underlay Connectivity Services, §12). Each has
  an `id`, a `type` (`public`, an Internet Access, or `private`), a
  `billing` (`flat-rate`, `usage-based` or `other`), and the
  `tunnel` the edges make over it: `kind` `gre`, `gif`, `geneve`, `uswe` or
  `wg`, and for the first three `ipsec`, true for IPsec IKEv2 under
  it; and `mss`, `auto` or a number of bytes, to clamp TCP's maximum
  segment size on the tunnels over it (by `ipfw tcp-setmss`, on each
  edge, IPv4 and IPv6 each; `auto` takes 1500 less the tunnel's
  overhead, IPsec's and an IPv6 underlay's). Without it, a path whose
  MTU is lower than the hosts think stalls large TCP transfers when
  ICMP is filtered somewhere.
- `edges`: the hosts that are SD-WAN Edges (§7.8). Each names its
  `server` and lists its `ucs_end_points` (§12.3): an `id`, its
  `ucs`, the `interface` it is on, and maybe an `address`, a
  `gateway`, a `bandwidth` in bits per second, `backup` (used only
  when nothing else is left), `breakout` (traffic for the Internet
  leaves here; only on a public underlay), and, Mplify 119 §12.2.3,
  its `addressing` (`static`, `dhcp` or `slaac`: by the last two the
  address is the host's own, learned when a plan is made), a `vrf`
  (a routing table of the underlay's own) and its `routing` (`bgp`,
  `ospf`, shaped as a UNI's).
  An edge may be a vnet jail on a server instead of the server itself:
  its `server` is then `server/jail` (in the form, **Jail**), and the
  jail's own network stack ([vnet(9)](https://man.freebsd.org/vnet/9))
  is the edge's. Its interfaces are made there (`ifconfig -j`), its
  routes, FIBs (`net.fibs` is per vnet) and sysctls set there (the
  jail's own `sysctl`, kept in its own `/etc/sysctl.conf`), its tunnels,
  [ipfw(8)](https://man.freebsd.org/ipfw/8) rules and steering are its
  ipfw's (by [jexec(8)](https://man.freebsd.org/jexec/8)), and its
  probes run from its network, on an ICMP socket the agent's helper
  makes in the jail. What it needs installed (strongSwan, BIRD,
  wg(8)) is looked for in the jail, as the jail sees its files. One
  server can so carry several edges, itself and its jails, as a lab on
  one host does. Not yet at a jail's edge: the services the host runs
  for a service (dnsmasq, unbound, Squid, Suricata, its BIRD), NTP,
  rtadvd, a `uswe` tunnel's manual SAs and the security record; an
  apply that needs one there stops and says so.
- `swvcs`: the services (SD-WAN Virtual Connections, §9). Each has
  an `id`, the `fib` it has on its edges (1 or more; FIB 0 is the
  underlay's), its `ucs`, `reserved_prefixes` (the provider's own
  addresses, tunnels' among them), its `domains` (Mplify 119 §7.3,
  all optional: `service`, with the `prefix` the tunnels' addresses
  come from and a `fib` kept for the control plane; `breakout`, with
  the `fib` the Internet traffic goes by; `subscriber`; each with a
  route distinguisher `rd`, route targets `rt` and an MPLS `label`,
  R15–R20, one service's each), and:
  - `zones` (§9.5): a `name` and `prefixes`, a list or `Default`, and
    `policies`, each an `app` (a flow or a group) and the ingress
    `policy` it gets in the whole zone, or `Block`;
  - `flows` (§9.14), matched in order, the first that matches: a
    `name`, `criteria` that all must match (`sav4`, `dav4`, `sdav4`,
    `sav6`, `dav6`, `sdav6`, `protv4`, `nextheadv6`, `dscp`, `sport`,
    `dport`, `sdport`, `ethertype`, `appid`, or `any` alone) and
    maybe a `group` of `groups`;
  - `policies` (§9.12): a `name`, a `direction`, `ingress` or
    `egress`, and `criteria`. Ingress: `encryption`,
    `public-private`, `internet-breakout`, `backup`,
    `virtual-topology`, `allowed-destination-zones`,
    `billing-method`, `business-importance`, `performance` (a
    `primary` metric, `delay`, `ipdv` or `loss`, with `threshold`,
    `ceiling` and `remediation`, and `secondary` ones with a
    threshold), `bandwidth` (`commit` and `limit`, or a rate
    limiter's name) and `af-security-ingress`. Egress:
    `egress-block` and `af-security-egress`;
  - `topologies` (§9.6): `multipoint-to-multipoint` with
    `end_points`, or `rooted-multipoint` with `roots` and `leaves`;
    `Swvc`, all to all, is always there;
  - `intervals` (§9.7: `eval`, `arrival`, `ir`, in milliseconds),
    `rate_limiters`, `security_policies` (§9.10, each a `name` and
    MEF 88 `criteria`: `ip-block` with `allow` and `deny` lists of
    prefixes, `dns-domain-filter` with the domains in `deny`,
    `dns-protocol-filter`, `rate-limit` in bits per second, `log`;
    a flow's policy names one by `af-security-ingress` or
    `af-security-egress`), `importance` (`levels`, high to low, and a
    `default`) and `probe`, how its tunnels are measured;
  - `end_points` (§10): an `id`, the `edge` it is on, its `uni` (§11:
    an `id`, the `interface`, a `vlan` or 0, `max_frame`, `ipv4` and
    `ipv6` addressing, `none`, `static`, `dhcp` or (IPv6) `slaac`, each
    but none with a `prefix` and the `provider`'s addresses in it,
    `ll-only` for IPv6 too; with dhcp or slaac the `reserved` prefixes
    not given out, the `dns` servers told to the hosts and a `lease`
    (§11.4, §11.5); and static `routes`), its `policy_map` (each a
    `zone` or `Internet`, an `app`, and its `ingress` and `egress`
    policies, over the zone's own) and its `nat`. In place of a `uni`,
    a `remote` (SASE-3, access by identity): a wg `interface` of the
    edge, the `prefix` the identities' addresses come from, the `port`
    it listens on (51820) and its `identities`, each a `name`, a `zone`
    of the service and a WireGuard `public_key`; the policies apply to
    an identity as to a UNI's hosts. On the edge, the apply makes the
    wg interface in the service's table with the prefix's first host
    as its address, listening on the port, and each identity a peer
    allowed its own address, the lowest free from the second, kept
    for it; the zone table sends that address to its zone's block, so
    the identity's flows get the zone's policies and the security
    policies as a UNI's host's do; the other edges route the prefix by
    their tunnels to this one. The far ends tell the prefix's zone by
    the zones' own prefixes, as they do a UNI's, so a zone the
    identities are in is best the Default one, or one whose prefixes
    hold the remote's. A remote may have `groups` of its identities,
    each a `name`, the `zone` whose policies its members get, a `pool`
    (a prefix inside the remote's, not holding the edge's own address)
    their addresses come from, and `reach`, the groups whose members
    they may reach; an identity in a `group` has the group's zone and
    needs none of its own. Members of one group reach each other;
    those of two groups neither of which names the other are kept
    apart on the edge (a table of each group's addresses, a deny rule
    each way on the wg interface before the zone table), traffic going
    both ways. An identity in no group keeps a zone of its own, takes
    an address outside every pool and reaches every other.

## Named lists

Arcana's own, beside MEF 70.2's attributes: `lists`, each a `name`
(letters, digits, `_` and `-`), a `kind` and what it holds, kept once
and named where a value would be. One list a criterion; a union is a
list of its own.

| kind | holds | named by |
|---|---|---|
| `prefixes` | `items`, IPv4 and IPv6 prefixes | a flow's `src-list`, `dst-list` and `sdst-list` (instead of `sav4`/`sav6`, `dav4`/`dav6`, `sdav4`/`sdav6`); a zone's `prefix-list` (beside its `prefixes`) |
| `services` | `protocols` and `ports` | a flow's `service-list`, instead of `protv4`, `nextheadv6`, `dport` and `appid`: they combine as PROTV4 and DPORT do in one flow |
| `ucs` | `items`, UCS ids | an ingress policy's `ucs-list`: only tunnels over these |
| `edges` | `items`, edges (their `server`) | an ingress policy's `edge-list`: only to these edges |
| `ucs-end-points` | `items`, an id or `{id, preference}` | an ingress policy's `ucs-end-point-list`: only tunnels from these, the higher `preference` first while it meets the performance |

The **Services** tab's **Lists** block makes and changes them, and the
flow, zone and policy forms pick one by name. The document keeps the
names; what a list stands for is written in where it is checked and
planned. A prefix list becomes an [ipfw(8)](https://man.freebsd.org/ipfw/8)
table of its own on each edge (`arcl_<name>`, both families), so a
long list is one table lookup, not words in each rule.

