# Built on standards

Where the IETF, the IEEE or MEF has already said how a thing is to be
modelled or spoken, Arcana does it their way. A host's interfaces are
`ietf-interfaces`, its routes `ietf-routing`, its FIBs network
instances, its faults alarms; what goes on the wire is YANG data in
CBOR, keyed by SIDs; the configuration lives in NMDA's datastores and
changes by NETCONF's confirmed commit; who may do what is NACM's
rules; an SD-WAN service is MEF 70.2's. Arcana's own models are kept
for what no standard covers, and each says which FreeBSD facility it
reads. Underneath, every one of them is the base system's own:
netlink(4), ipfw(8), rc.conf(5), sctp(4) ([FreeBSD
underneath](freebsd.md)).

This page maps each function to the document and the rule it follows,
and says honestly how far it goes:

- **full**: the rule as written, for what the row names;
- **partial**: what is done and, after it, what is not yet;
- **own**: Arcana's own, where it deliberately departs or no standard
  exists.

The YANG side is told at length in [The models: YANG](../automation/yang.md),
the SD-WAN side in [Conformance: SASE](../sdwan/conformance.md) and
[Mplify 119](../sdwan/mplify.md).

## The wire and its encoding

What the console and the agents say to each other: cblink's YANG
family ([cblink in a page](../automation/cblink.md)).

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Data on the wire | [RFC 9254](https://www.rfc-editor.org/rfc/rfc9254) YANG-CBOR | §3.2 SID deltas; §6 the types, §6.13.1 instance-identifier | One CBOR map per frame body, children keyed by their delta from the parent's SID, YANG-CBOR's tags 43–47 alone | full |
| CBOR itself | [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) | a strict profile | Definite lengths only, integers and keys in their shortest form, every other tag and simple value refused before a program sees it | full |
| Item numbers | [RFC 9595](https://www.rfc-editor.org/rfc/rfc9595) SIDs | Appendix B numbering; §6.4.2 experimental range | IANA's ranges where IANA gives one (`ietf-interfaces` 1500, `ietf-ip` 1600, `ietf-netconf-acm` 1250, `iana-if-type` 1800), the experimental range 60 000–99 999 for the rest; a SID never reused; `GET-SID` sends each module's `.sid` file as `ietf-sid-file` | partial: no registered block yet, so no interoperation is claimed for the experimental SIDs (an IANA mega-range or [RFC 9997](https://www.rfc-editor.org/rfc/rfc9997)'s PEN ranges later) |
| Operations | [draft-ietf-core-comi](https://datatracker.ietf.org/doc/draft-ietf-core-comi/) (CORECONF) | §3: FETCH, iPATCH, POST | GET, EDIT, RPC and actions (the target an instance-identifier), NOTIFY, GET-SID, SUBSCRIBE, each in CORECONF's shape | partial: CORECONF's shape over cblink's frames, not CoAP; a GET's target is a top-level node, not yet a list entry |
| Modules | [RFC 7950](https://www.rfc-editor.org/rfc/rfc7950) YANG 1.1 | §6.4 XPath, §7.5.3 `must`, §7.21.5 `when` | cblink-gen compiles them with libyang 3; every EDIT and rpc input validated (types, mandatory nodes, keys, `unique`, `must`, `when`, leafrefs) before a handler sees it | partial: XPath within XPath-lite; anyxml content not validated |
| Framework items | [RFC 8791](https://www.rfc-editor.org/rfc/rfc8791) structures | `sx:structure` | Errors, credit, hello, close, the user and datastore of a request: structures of the `cblink` module, at SIDs like any data | full |
| Errors | [RFC 8040](https://www.rfc-editor.org/rfc/rfc8040), [RFC 6241](https://www.rfc-editor.org/rfc/rfc6241) | RFC 8040 §7 error-tag; RFC 6241's warnings | Each refusal an `error-tag` identity, an `error-app-tag` and an `error-path`, FreeBSD's errno beside them; warnings as errors of severity warning | full |
| Metadata | [RFC 7952](https://www.rfc-editor.org/rfc/rfc7952) annotations | [draft-ietf-core-yang-metadata](https://datatracker.ietf.org/doc/draft-ietf-core-yang-metadata/)'s CBOR | Tag 109 on an annotated value | partial: tag 109 is not IANA's yet, held as provisional |
| JSON | [RFC 7951](https://www.rfc-editor.org/rfc/rfc7951) | §4 member names; §6 the values | `arcanactl get` and the console speak it: `module:name` where the module changes, 64-bit numbers and decimals as strings, `[null]` for empty, identities `module:name`; JSON read back into YANG data for `arcanactl edit` | full |
| Model trees | [RFC 8340](https://www.rfc-editor.org/rfc/rfc8340) tree diagrams | the notation | The console's { } Schema panel shows an operation's YANG tree beside its CBOR | full |

## Datastores and configuration safety

What the configuration is, and how it changes without cutting the
console off.

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Datastores | [RFC 8342](https://www.rfc-editor.org/rfc/rfc8342) NMDA | §5.1.2 candidate, §5.1.3 running, §5.3 operational | A GET or an EDIT names its datastore; `running` is what rc(8) reads (without what DHCP, SLAAC or the kernel made), `candidate` one shared configuration being made, `operational` (the default) what is | partial: no `startup` or `intended` |
| Where configuration came from | RFC 8342; [RFC 8527](https://www.rfc-editor.org/rfc/rfc8527) | §5.3.4 the `origin` annotation; RFC 8527 §3.2.2 `with-origin` | A read of the operational datastore with `with-origin` (`arcanactl get -o`, RESTCONF's `?with-origin`) annotates each configuration node where its origin is not its parent's: `intended` where running has it, `default` for a default in use, `learned` for what DHCP, SLAAC or a temporary address gave and a neighbour the host found, `system` for what the kernel made (an interface, a link-local address); `unknown` for what was set by hand since | partial: no `dynamic` (no dynamic datastore) |
| Validation where it belongs | RFC 8342 | §5.3: operational state is not validated | Edits and rpc input in full; what the agent reads back, never | full |
| Candidate and commit | [RFC 6241](https://www.rfc-editor.org/rfc/rfc6241) | §8.3 `:candidate`: commit, discard-changes | `arcanactl edit` changes the candidate, checked against the model and NACM at once; `commit` puts it in use, every node or none; `discard` forgets it | partial: no lock or unlock; NETCONF's session operations (get-config, edit-config, copy-config) are refused, a cblink peer has no use for them |
| Confirmed commit | RFC 6241 | §8.4 `:confirmed-commit`: `confirm-timeout` (600 s by default), `persist`, `persist-id`, cancel-commit | Undone at its timeout, by `cancel-commit`, or when its session goes without `persist`; confirmed by a second commit of its session or one that gives the persist-id (`arcanactl commit -c 120`, `-i <persist-id>`) | full |
| All or nothing | RFC 6241 | §7.2 `rollback-on-error` | An EDIT and a commit each: if one node fails, those already changed are undone; the files put back as they were | full |
| Writing rc.conf | [rc.conf(5)](https://man.freebsd.org/cgi/man.cgi?query=rc.conf&sektion=5) | `rc_conf_files` | One file of Arcana's, `/usr/local/etc/rc.conf.d/arcana`, named once in `rc_conf_files` so every rc script reads it; a variable the admin's files set too is a warning to accept first | own |
| What EDIT changes so far | [RFC 8349](https://www.rfc-editor.org/rfc/rfc8349), [RFC 8343](https://www.rfc-editor.org/rfc/rfc8343), [RFC 8529](https://www.rfc-editor.org/rfc/rfc8529) | the `static` control-plane protocol; interfaces; network instances | Static routes of each FIB, written as rc.d/routing reads them (`static_routes`, `route_<name>`, `defaultrouter`, the IPv6 ones and their `_fibN` forms), then made the kernel's by netlink(4), tried again once, the files put back if it still fails; interfaces made and destroyed (`cloned_interfaces`), their description, state, MTU, addresses (a point-to-point one with its peer), FIB (`bind-ni-name`) and router advertisements (rtadvd.conf(5)); a network instance a FIB, `net.fibs` raised for the next boot (loader.conf.d) when one more is asked for, and accepted; syslog.conf and newsyslog.conf from ietf-syslog; sysctl.conf and `kld_list`; a service's rc.conf variables; NACM's own rules | partial: every other node refuses a commit for now |
| An undo that fails | — | beyond RFC 6241 | The undo stops there, a Critical alarm `undo` and an `undo-failed` event carry a report of the failure (never the host's configuration) for the admin to file if they choose | own |
| Safe mode for jobs | — | before the datastores | A job made in safe mode is undone unless confirmed within the rollback timer: the confirmed commit's forerunner, still how jobs change the host | own |

## Access control

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Who may do what | [RFC 8341](https://www.rfc-editor.org/rfc/rfc8341) NACM | groups, rule-lists in order, the first matching rule decides | The agent serves `ietf-netconf-acm:nacm` and cblink checks every request against it; the rules are kept in their own file (`--nacm`), changed by a commit; edited on a host's Security tab, saved by a confirmed commit the page confirms as you, so that rules that would refuse you are undone by the host | full |
| Defaults | RFC 8341 | §3.3.4 `enable-nacm`, `read-default` permit, `write-default` deny, `exec-default` permit | As written; with no rules file, group `admin` (users `admin` and `console`) has one rule-list permitting everything, anyone else RFC 8341's defaults | full |
| Sensitive nodes | RFC 8341 | `nacm:default-deny-all`, `nacm:default-deny-write` | The tables' flags; the `nacm` container itself is deny-all, so only a rule lets anyone change the rules; every command of the agent's own family that changes the host, or gives out a capture, a dataset or its configuration, is deny-all too | full |
| Enforcement points | RFC 8341 | §3.4.4 rpcs, §3.4.5 data nodes, §3.4.6 notifications | An rpc's or action's exec; a read (what is denied left out); an EDIT and a commit (each node created, changed or deleted, all or nothing); each notification, and each record of a subscription | full |
| Recovery session | RFC 8341 | §3.3.3 emergency recovery session | root, or the agent's own user, on the agent's unix socket: nothing holds it back, so it can always write the rules anew | full |
| Counters | RFC 8341 | `denied-operations`, `denied-data-writes`, `denied-notifications` | Counted by cblink, read in the `nacm` container | full |
| The user of a request | RFC 8341 | the NACM user name | The console says, per request, which of its users it acts for; its own requests (a poll, a schedule) are user `console`; a local user on the unix socket is their login name; another host's certificate is refused | partial: groups come from the rules alone, no external groups |

## Notifications and subscriptions

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Events | [RFC 8639](https://www.rfc-editor.org/rfc/rfc8639) | the `NETCONF` stream | Every event the host tells (netlink(4)'s routes, links, addresses and neighbours, a jail's state by `EVFILT_JAIL`, a job's end) is an `arcana-events:event` notification | full |
| Dynamic subscriptions | RFC 8639 | establish, modify, delete, kill; replay; suspension and resumption | `arcanactl subscribe`, each subscription a flow-controlled stream of its own; an XPath filter; replay from a start time; one that falls behind suspended and resumed with all its data again | partial: subtree filters not yet |
| Configured subscriptions | RFC 8639 §2.5; [draft-ietf-netconf-https-notif](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) | receivers, the state machine's notifications (started, modified, terminated, completed), replay on reconnect | Kept in the agent's running (`subscriptions`, written by a commit, loaded at start), each receiver reached by the agent as an HTTPS-notif publisher (its certificate from the console's PKI, `capabilities` then `relay-notification`), backoff while it is away, replay from the last record's second; the console the receiver, judging the agent by its certificate, keeping the records | partial: a receiver's `reset` and the `suspended` state untested; `receiver-identity` off |
| YANG-Push | [RFC 8641](https://www.rfc-editor.org/rfc/rfc8641) | periodic and on-change of the operational datastore | Periodic from an anchor time; on-change as a [RFC 8072](https://www.rfc-editor.org/rfc/rfc8072) YANG Patch per change, the events, alarms and jobs told as they change | partial: interfaces, addresses, routes and jails are compared each dampening period (a second at least), as the kernel announces some of their changes on no socket |
| RESTCONF streams | [RFC 8040](https://www.rfc-editor.org/rfc/rfc8040), [RFC 8650](https://www.rfc-editor.org/rfc/rfc8650) | RFC 8040 §6 streams as Server-Sent Events; RFC 8650 establish-subscription over RESTCONF | Each host's events, and the whole fleet's, as `text/event-stream`, `Last-Event-ID` honoured; a subscription of one's own by POST | full |

## The console's northbound: RESTCONF

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Discovery | RFC 8040, [RFC 6415](https://www.rfc-editor.org/rfc/rfc6415) | §3.1 `/.well-known/host-meta` | An XRD naming `/restconf` | full |
| Reads | RFC 8040 | §3.3 the root, §3.5.3 api-path, §4.8.1 `content`, §4.8.2 `depth`, §4.8.3 `fields`, §9.1 `restconf-state` | A path under a host made an XPath filter of its agent's GET, answered as `application/yang-data+json` | full; no ETag |
| Datastores | [RFC 8527](https://www.rfc-editor.org/rfc/rfc8527) | §3.1 `{+restconf}/ds/<datastore>` | `/restconf/ds/ietf-datastores:running`, `candidate` and `operational`, each host's below its entry | full for those three |
| Changes | RFC 8040 | §4.5 PUT, §4.7 DELETE | A host's top-level node put or deleted in its candidate; a PUT or DELETE under `/restconf/data` (running) is refused with how to make the change | partial: a top-level node whole; no POST of data, PATCH or YANG Patch |
| Commit | RFC 6241 §8.3, §8.4; RFC 8528 §3.3 | `commit`, `cancel-commit`, `discard-changes` as the mount's actions | POSTed under a host's entry; a confirmed commit through the console names `persist` (its connection is every user's), and the commit that confirms runs over a connection of its own, the proof that a new one reaches the host | Arcana's own: the `arcana-accept` query parameter carries the warnings a change goes on despite |
| Defaults | [RFC 6243](https://www.rfc-editor.org/rfc/rfc6243) | report-all, trim, explicit, report-all-tagged | RESTCONF's `with-defaults` (§4.8.9), tagged ones by RFC 7952's `@` member; the agent's own reads too (`arcanactl get -w`), report-all-tagged with [draft-ietf-netconf-default-attribute](https://datatracker.ietf.org/doc/draft-ietf-netconf-default-attribute/)'s `ietf-defaults:default` | full |
| The fleet | [RFC 8528](https://www.rfc-editor.org/rfc/rfc8528) schema mount | inline and shared-schema mount points; §3 `schema-mounts` | `arcana-fleet:fleet/host`, each host an inline mount of the models its agent serves; a mounted host's notification nested in its entry; inside an agent, each network instance's `vrf-root` (RFC 8529) a shared-schema mount of its FIB's routing, the host's interfaces its `parent-reference`, its YANG library inside it; each running vnet jail an [RFC 8530](https://www.rfc-editor.org/rfc/rfc8530) logical network element whose `root` is an inline mount served by a helper the agent runs attached to the jail (jail_attach(2), cblink over a socketpair): the jail's interfaces, routing, network instances with their own `vrf-root`s and its YANG library; `bind-lne-name` on an interface moves it into the jail by a commit (ifconfig vnet, jail.conf `vnet.interface`); all said in `schema-mounts` | full for reads; a jail's own configuration is read-only through its root |
| What it implements | [RFC 8525](https://www.rfc-editor.org/rfc/rfc8525) YANG library | module sets, features, `content-id`, datastores | The console's own library, and each agent's: every module with its revision and the features on, those imported only, the running, candidate and operational datastores | full |

## Data models: interfaces and layer 2

All read by the agent from the kernel; changed by jobs, and some of
it by a confirmed commit (the table above says what).

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Interfaces | [RFC 8343](https://www.rfc-editor.org/rfc/rfc8343) | `ietf-interfaces`, IANA's `iana-if-type` | getifaddrs(3) and `struct if_data`, the ioctls ifconfig(8) uses; layers as lower- and higher-layer-if | partial: broadcast counters left out (FreeBSD counts them with multicast); a commit changes an interface's description and `enabled`, kept in `ifconfig_<if>` |
| Addresses, neighbours | [RFC 8344](https://www.rfc-editor.org/rfc/rfc8344) | `ietf-ip` | Each address with its origin and IPv6 status (SIOCGIFAFLAG_IN6), ARP and NDP by netlink(4) | partial: a deviation (`arcana-ip-deviations`): forwarding, DAD and temporary addresses are the host's sysctls, one MTU for both families, IPv4 cannot be turned off on one interface; a commit changes the static addresses (`ifconfig_<if>_alias<n>`) and the IPv4 MTU |
| Interface extensions | [draft-ietf-netmod-intf-ext-yang](https://datatracker.ietf.org/doc/draft-ietf-netmod-intf-ext-yang/), [draft-ietf-netmod-sub-intf-vlan-model](https://datatracker.ietf.org/doc/draft-ietf-netmod-sub-intf-vlan-model/) | max-frame-size, parent- and peer-interface, Ethernet addresses, a VLAN's outer tag | A vlan(4)'s parent and tag (SIOCGETVLAN), an epair(4) end's other | partial: working-group drafts, at the revisions taken |
| Ethernet | [IEEE 802.3](https://www.ieee802.org/3/) | `ieee802-ethernet-interface` | Auto-negotiation, duplex and the PMD type from the media (SIOCGIFXMEDIA) | partial: read only |
| Link aggregation | [IEEE 802.1AX](https://1.ieee802.org/tsn/802-1ax-rev/) | `ieee802-dot1ax-linkagg`: aggregators, LACP state | lagg(4) by SIOCGLAGG | partial: a deviation (`arcana-ieee802-deviations`): FreeBSD's LACP keeps no administrative key, so `actor-admin-key` is not mandatory |
| Bridges | [IEEE 802.1Q](https://standards.ieee.org/ieee/802.1Q/10323/) | `ieee802-dot1q-bridge`, `ieee802-dot1q-rstp-bridge` | if_bridge(4)'s members (BRDGGIFS) and their RSTP state | partial: read only; `protocol-migration-check` not served |
| Hardware | [RFC 8348](https://www.rfc-editor.org/rfc/rfc8348) | `ietf-hardware` components | The chassis from SMBIOS (kenv(2)), a CPU each with its temperature (coretemp(4), amdtemp(4)), GEOM's disks | partial: read only |

## Data models: routing and instances

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| RIBs | [RFC 8349](https://www.rfc-editor.org/rfc/rfc8349) | `ietf-routing` with the IPv4 and IPv6 unicast modules | netlink(4) dumps, multipath routes as next-hop lists, blackhole and reject as special next hops; the `active-route` action is `route get` | partial: FreeBSD has no route preference; `last-updated` only for a route the agent saw change |
| Static routes | RFC 8349 | the `static` protocol | rc.conf's `static_routes` and the rest, read both ways, written by a commit (above) | partial: FIB 0 only so far |
| Route origin | RFC 8349, the protocols' modules | `source-protocol` | netlink(4)'s `rtm_protocol`, as `ietf-ospf`'s, `ietf-rip`'s, `ietf-isis`'s, `ietf-babel`'s or `ietf-bgp`'s identity | partial: the IETF protocol modules are imported for their identities only |
| FIBs | [RFC 8529](https://www.rfc-editor.org/rfc/rfc8529) network instances | one instance per VRF, `bind-ni-name` | Each FIB (`net.fibs`, setfib(2)) beyond the host's an instance, named in `fibs.conf`; an interface's binding its FIB | partial: read only; the `vrf-root` mount not yet |
| vnet jails | [RFC 8530](https://www.rfc-editor.org/rfc/rfc8530) logical network elements | one LNE per separate network stack | Each vnet jail, as jail_get(2) lists it | partial: read only; the `root` mount not yet |
| BGP, OSPF, BFD | [RFC 4271](https://www.rfc-editor.org/rfc/rfc4271), [RFC 2328](https://www.rfc-editor.org/rfc/rfc2328), [RFC 5880](https://www.rfc-editor.org/rfc/rfc5880) | the protocols | BIRD (`bird3`), the agent reading birdc(8) | own: the state is `arcana-bird`, not the IETF protocol models |
| Route reflection | [RFC 4456](https://www.rfc-editor.org/rfc/rfc4456) | every client of every other | An SD-WAN edge that carries transit reflects what it learns, so a site whose tunnels are down is reached through a third | full |
| Syslog | [RFC 9742](https://www.rfc-editor.org/rfc/rfc9742) `ietf-syslog`, [RFC 5424](https://www.rfc-editor.org/rfc/rfc5424) | facilities and severities | syslog.conf(5) and newsyslog.conf(5) read as the model | partial: read only |
| Alarms | [RFC 8632](https://www.rfc-editor.org/rfc/rfc8632) | the alarm list, inventory, summary, `purge-alarms`, `compress-alarms` | Each of the agent's faults an alarm, its kind an `arcana-alarms` identity, its raising and clearing its history | partial: no shelving |

## Transports

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| TCP | [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446) TLS 1.3 | mutual authentication | TLS 1.3 only, a certificate on both sides, no resumption, no renegotiation, the base system's OpenSSL | full |
| SCTP | [RFC 9260](https://www.rfc-editor.org/rfc/rfc9260), [RFC 6458](https://www.rfc-editor.org/rfc/rfc6458) | streams, multihoming | sctp(4), one-to-one sockets; requests on stream 0, each cblink stream on one of its own (64 asked), so a slow answer holds no other; several addresses by `sctp_bindx()` and `sctp_connectx()`, failing over between them | full |
| SCTP's security | [RFC 6083](https://www.rfc-editor.org/rfc/rfc6083) DTLS over SCTP, [RFC 4895](https://www.rfc-editor.org/rfc/rfc4895) SCTP-AUTH | mutual DTLS | DTLS 1.2 with forward-secret AEAD suites, OpenSSL's SCTP BIO, `net.inet.sctp.auth_enable` | partial: DTLS 1.2, as base OpenSSL has no DTLS 1.3 |
| Interleaving | [RFC 8260](https://www.rfc-editor.org/rfc/rfc8260) I-DATA | `SCTP_INTERLEAVING_SUPPORTED` | A large message on one stream interleaved with the others | partial: plaintext SCTP only; OpenSSL's SCTP BIO needs each record whole |
| Local | — | getpeereid(3) | A unix socket, its permissions the access control | full |

## The console's other doors

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| Sign-in | [W3C WebAuthn](https://www.w3.org/TR/webauthn/) | COSE algorithms EdDSA, ES256, RS256 | The console's users sign in with security keys, verified in the console | full |
| Directory sign-in | [RFC 4511](https://www.rfc-editor.org/rfc/rfc4511), [RFC 4515](https://www.rfc-editor.org/rfc/rfc4515) | §4.14 StartTLS; filters escaped | LDAP written in the console (bind, search, StartTLS), always over TLS | full |
| Notifications to devices | [RFC 8030](https://www.rfc-editor.org/rfc/rfc8030), [RFC 8291](https://www.rfc-editor.org/rfc/rfc8291), [RFC 8188](https://www.rfc-editor.org/rfc/rfc8188), [RFC 8292](https://www.rfc-editor.org/rfc/rfc8292) | Web Push, its encryption, VAPID | Each message encrypted per subscription (aes128gcm), signed by VAPID, tested against RFC 8291's example | full |
| Live pages | [RFC 8441](https://www.rfc-editor.org/rfc/rfc8441) | WebSockets over HTTP/2 | Extended CONNECT where the browser speaks HTTP/2 | full |

## SD-WAN and SASE

An SD-WAN service is MEF 70.2's in its terms, with what Mplify 119
asks of an edge; its security is MEF 138's; the SASE documents are
checked attribute by attribute in [Conformance:
SASE](../sdwan/conformance.md).

| Arcana function | Standard | Section / rule | How Arcana does it | Status |
|---|---|---|---|---|
| The service | [MEF 70.2](https://www.mplify.net/resources/mef-70-2-sd-wan-service-attributes-and-service-framework/) | UCS (§12), SWVC (§9), Zones (§9.5), Application Flows (§9.14), Policies (§9.12), the policy map | A FIB per service on each edge (setfib(1)), flows and zones as ipfw(8) rules and tables, tunnels in the service's FIB, their outer packets in the host's (`tunnelfib`) | full: the session forwarding criteria as 70.2 has them ([MEF 70.2 in a page](../sdwan/index.md)) |
| The edge | [Mplify 119](https://www.mplify.net/resources/mplify-119-universal-sd-wan-edge-implementation-agreement/) | §7.3 routing domains; §10 the uswe tunnel; §11.4 probes; §12 management plane (R89–R160) | Breakout and service domains as FIBs; ESP in tunnel mode on an ipsec(4) interface, keys derived by the agents; ICMP probes per tunnel; BFD and TCP-MD5 iBGP by BIRD | partial: no DSCP marking of the tunnels' outer packets, no RD/RT or MPLS labels, a key's activation by rotation rather than a date ([Mplify 119](../sdwan/mplify.md)) |
| Security functions | [MEF 138](https://www.mplify.net/resources/mef-138-security-functions-for-ip-services/) | §9 Security Function Policies: Block, Allow, Quarantine, No-match, Duration | IPPF and DPF by ipfw, DNF and PDNS by local-unbound(8), URLF and the middlebox by Squid, MD+R by ClamAV | partial: seven of the eight functions; no DLP |
| SASE | [Mplify 117.1](https://www.mplify.net/resources/mplify-117-1-sase-service-attributes-and-service-framework-revision/) | §8 Service Attributes | The flows, security policies, forwarding policies, rate limiters, intervals and UCSs | partial: one IdP (the console), no session states, no composite policies |
| Zero trust | [MEF 118.1](https://www.mplify.net/resources/mef-118-1-zero-trust-framework-for-mef-services/) | Policy Decision and Enforcement Points, Audit Events | The console decides, the edges enforce; an HMAC-chained audit trail | partial: no external IdP or risk score |
| Measurement | Mplify 119 | §11.4 | ICMP echo on each tunnel: delay, its variation, loss | partial: delay is half the round trip, not one-way |
| IKEv2 | [RFC 7296](https://www.rfc-editor.org/rfc/rfc7296) | IKEv2 only | strongSwan by swanctl(8), `version = 2` always, tunnel or transport mode, each host's own key | full |
| ESP | [RFC 4303](https://www.rfc-editor.org/rfc/rfc4303), [RFC 3948](https://www.rfc-editor.org/rfc/rfc3948) | ESP, ESP in UDP | ipsec(4) interfaces and the kernel's SAs; for a uswe tunnel, ESN and ESP in UDP on unless the service says otherwise | full |
| IPv6 to the IPv4 Internet | [RFC 6146](https://www.rfc-editor.org/rfc/rfc6146) NAT64, [RFC 6877](https://www.rfc-editor.org/rfc/rfc6877) 464XLAT | the translators | ipfw's `nat64lsn` at the edge that breaks out, `nat64clat` at a UNI that says so | own beside MEF 70.2 §10.5 |

## Where Arcana departs, and why

- **cblink, not CoAP.** The YANG family has CORECONF's methods and
  RFC 9254's encoding, carried in cblink's own frames (a netlink-like
  header, request numbers, flow-controlled streams) over TLS 1.3 or
  SCTP. The operations of the agent's own family are an interim YANG
  module (`arcana`), each an rpc, until each moves to its model.
- **Experimental SIDs.** Arcana's modules, and the IETF modules IANA
  has no range for, are numbered in RFC 9595's experimental range.
  RFC 9595 says such SIDs are for no operational deployment with
  another SID-keyed peer; Arcana claims none, and moves to a registered
  block before it does.
- **No direct writes to running.** An EDIT of `running` is refused:
  every change goes through the candidate and a commit, so it can be
  confirmed and taken back. There are no locks: the candidate is one,
  shared, and a confirmed commit holds it to its session or persist-id.
- **An undo that fails is told, not hidden.** RFC 6241 says what a
  confirmed commit not confirmed does; it does not say what to do when
  putting the old configuration back fails. Arcana stops, raises a
  Critical alarm and writes a report of the failure alone for the
  admin to file as a bug; it never files one by itself.
- **FreeBSD as it is.** Where FreeBSD differs from a model, a deviation
  module says so (`arcana-ip-deviations`,
  `arcana-ieee802-deviations`, `arcana-network-instance`'s FIB case
  without a VSI root) rather than the data pretending otherwise.
  carp(4) is not VRRP on the wire, so it is not called VRRP.
- **Arcana's own modules** cover what no standard models: jails,
  services, packages, ZFS and GEOM, sysctl, the kernel's modules,
  processes (in OpenConfig's `procmon` shape), ipfw(8), BIRD,
  WireGuard, netgraph(4), the probes and the SD-WAN edge. Each leaf
  names the FreeBSD facility it is read from.
- **Beside MEF 70.2 and Mplify 119**, marked as Arcana's own in the
  document: named lists of prefixes, services and ways; destination
  sets by BGP AS path or community; a host-as-subscriber edge whose
  service lives in the host's own table; iBGP between loopbacks with
  route reflection; NAT64 and CLAT; a rate limit per security policy;
  Suricata's `ids`. A rule of the documents is never renamed to a
  vendor's word.

## What comes next

The plan in Arcana's tree, `docs/PLAN-SDN-YANG.md`, takes the
standards further: commits of FIBs, interfaces made and taken away,
and the Arcana modules; RESTCONF's PATCH and YANG Patch; ACLs as RFC 8519
compiled to ipfw(8); IPsec as RFC 9061; L3NM (RFC 9182) as the stored
form of a service; STAMP (RFC 8762) in place of ICMP probes. None of
it is claimed above until it is done.
