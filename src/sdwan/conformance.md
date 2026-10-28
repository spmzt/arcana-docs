# Conformance: SASE

How Arcana stands against the current SASE documents, attribute by
attribute and requirement by requirement. These are **Mplify 117.1**
(SASE Service Attributes and Service Framework, June 2025), **MEF 138**
(Security Functions for IP Services, July 2024) and **MEF 118.1** (Zero
Trust Framework for MEF Services, July 2024). Each row is in one of two
lists: what Arcana does (**yes**, or **partly**, saying what is
missing), and what it does not (**no**). **n/a** marks what does not
apply to how Arcana is built.

The documents moved on while Arcana was being built. Mplify 117.1
replaces MEF 117 and takes its Security Functions from MEF 138, which
replaces MEF 88. MEF 118.1 replaces MEF 118. Arcana's security policies
were first written to MEF 88's criteria; since console 0.317.0 they are
MEF 138's model: Security Function Policies, each one function's Block,
Allow and Quarantine lists with its No-match and Duration, put together
by the security policies that MEF 70.2's AF-SECURITY criteria name.

The connectivity under it, MEF 70.2 and Mplify 119, has a chapter of
its own ([Mplify 119](mplify.md)).

## Mplify 117.1: Service Attributes (§8)

| § | Service Attribute | Status | In Arcana |
|---|---|---|---|
| 8.1 | List of SASE Edges | partly | The document's `edges`, each a server, a service's end points on two or more. A SASE Agent (software on a device, §9.1.1) is not an edge here: a remote identity is a WireGuard peer of an edge. |
| 8.2 | List of SASE Network Termination Points | partly | A UNI (`uni.id`) or a remote end point (its wg interface) is where an Actor's access connection ends; there is no NTP identifier of its own. |
| 8.3 | SASE Policy End Point Identifier | partly | Each edge is a Policy End Point, named by its server; there is no identifier of its own. |
| 8.4 | List of Identity Providers | partly | One, the console: an identity is known by its WireGuard key. No external IdP (OAuth, SAML). |
| 8.5 | List of SASE Application Flow Specifications | yes | The service's `flows`, ordered, first match wins: SAV4, DAV4, PROTV4, SAV6, DAV6, NEXTHEADV6, DSCP, SPORT, DPORT, APPID, ANY, and Table 8's ETHERTYPE, SDAV4, SDAV6, SDPORT. |
| 8.6 | List of SASE Session State Values | no | No session states (Initial, Operational, Re-Evaluate, Terminal). A session is a WireGuard handshake and its traffic. |
| 8.7 | List of SASE Identity Policies | partly | A remote end point's identities with their zones and re-authorisation interval; not as named Identity Policies. |
| 8.8 | List of SASE Actor Access Connection Policies | partly | The access connection is WireGuard; there is no policy list of its own. |
| 8.9 | List of SASE Supported TLS Versions | no | An Actor's access connection is WireGuard, not TLS. |
| 8.10 | List of SASE Supported Cipher Suites | no | WireGuard has one suite (Noise IK, ChaCha20-Poly1305), not a list. |
| 8.11 | List of SASE Supported IPSEC Security Options | partly | IKEv2 proposals are agreed for tunnels between edges, not for an Actor's access connection. |
| 8.12 | List of SASE Context Policies | no | No temporal criteria (time, day, duration); location is the zone alone. |
| 8.13 | List of SASE Security Policies | yes | The service's `security_policies`, by name, each made of MEF 138 Security Function Policies (`security_function_policies`), see below. |
| 8.14 | List of SASE Security Functions | partly | Of the eight [R15] asks for, seven: MBSF, IPPF, DNF, URLF, MD+R, DPF and PDNS, each as function policies; DLP is not. |
| 8.15 | List of SASE Session Forwarding Policies | yes | MEF 70.2's policies: ENCRYPTION, PUBLIC-PRIVATE, BILLING-METHOD, BUSINESS-IMPORTANCE, PERFORMANCE, BANDWIDTH. |
| 8.16 | List of SASE Monitoring Policies | partly | The probes and the TCA of each service, and the re-authorisation interval; not as named Monitoring Policies. |
| 8.17 | List of SASE Notification Policies, Recipients | partly | The events, Web Push to the console's devices and the workflows; no SAAN or SSEN as 117.1 shapes them (see below). |
| 8.18 | SASE Composite Policy Levels | n/a | Arcana's policies are not composite. |
| 8.19 | List of SASE Rate Limiters | yes | `rate_limiters`, each a name, commit and limit, shared at an end point. |
| 8.20 | List of SASE Session Business Importance Levels | partly | `importance.levels`, highest first; per Application Flow, not per Actor pair. |
| 8.21 | List of SASE SA-IdAM Application Flow Specifications | no | No SA-IdAM. |
| 8.22 | List of SASE Data Integrity Actions | no | No Data Integrity. |
| 8.23 | List of SASE RBI Actors | no | No Remote Browser Isolation. |
| 8.24 | SASE Performance Time Intervals | yes | `intervals`: eval, arrival, ir. |
| 8.25 | SASE Service Performance Objectives Reporting Periods | no | The paths' delay, jitter and loss are shown, not reported against objectives by period. |
| 8.26 | SASE Policy Execution Order Parameter Range | n/a | No composite policies, no order between them. |
| 8.27 | UCS Identifier, UCS Type, UCS Billing Method | yes | `ucs`: id, type (Public, Private), billing (Flat-rate, Usage-based, Other). |
| 8.28 | UCS UNI Identifier | partly | A UCS end point's id on an edge. |

### Requirements without an attribute

| Requirements | Status | In Arcana |
|---|---|---|
| R1–R3 One-way delay, delay variation, loss | partly | Delay is half the round trip of each tunnel's probes, not one-way. |
| R26–R34 A SASE Edge's UNIs, UCSs, IdAM, NTP, Policy End Point | partly | An edge has UNIs and UCSs and is a Policy End Point; its IdAM is the console's. |
| R40–R50 Identity and Access Management | partly | Every remote Actor is authenticated (its key) and authorised (its zone); a UNI's hosts are authorised by their zone, not authenticated one by one ([R43]). |
| R61, R62 A packet to the first Session Specification it matches, else dropped | yes | Classification by `flows`; no zone or no policy, dropped. |
| R63 Encrypted connectivity between any two Edges | partly | Where the policy says ENCRYPTION or the tunnel is WireGuard or IPsec; a plain GRE or GENEVE tunnel is not. |
| R64–R89 Session forwarding criteria | yes | MEF 70.2's, already conformant (see [Mplify 119](mplify.md)). |
| R90, R91 Re-Evaluate on a change | partly | An identity's re-authorisation and revocation take effect at the next apply; there is no session state. |
| R92–R95 The eight MEF 138 Security Functions | partly | Seven of eight, as function policies; no DLP. See the MEF 138 table. |
| R107–R110 SAAN on a denied access or a Blocked session | partly | The record (each deny, with its rule, policy and edge) and the audit trail; no SAAN ID or format as Table 11 has it. |
| R111–R114 SSEN on what a Security Function Blocks | partly | Suricata's alerts and ClamAV's detections are events; no SSEN ID; domains and URLs are not neutralised ([R114]). |
| R115–R151 SASE Policy as a Composite Policy of six | no | Arcana's policies are MEF 70.2's, with MEF 138's Security Function Policies put together by a security policy; not Mplify 117.1's composite of six. |
| CR3–CR18 With SD-WAN under the service | n/a | Arcana's SASE is the SD-WAN service itself, not a SASE service over one. |

## MEF 138: Security Functions

| Requirements | Status | In Arcana |
|---|---|---|
| R117–R120 Security Policy Identifier, Policy ID | yes | A security policy's `name` and a function policy's `id`, each one in its service. |
| R1–R6 Block List, kept by the provider, added to by the Subscriber | partly | Inline entries and named lists (feeds or pasted). No threat entries of the provider's own that the Subscriber may not remove ([R4]): the feeds are the Subscriber's choice. |
| R7–R10 Allow and Quarantine Lists | yes | `allow` and `quarantine`, inline and by named lists; Quarantine blocks. |
| R14 An entry on one list at most | partly | Refused for inline entries; between named lists, the first of Block, Quarantine, Allow wins. |
| §6.1.6 The more specific entry overrules | partly | IPPF, DPF and URLF order their entries most specific first; DNF and PDNS by unbound's longest match; a named list's prefixes by the table's longest match. Between a function's inline entries and its named lists, the inline ones are tried first; a URLF's named Allow before its named Block. |
| R11–R19 Supported and Unsupported Lists (MBSF, PDNS) | partly | Kept by Arcana: TLS 1.2 and 1.3 are opened; PDNS takes unencrypted DNS and DNS over TLS, southbound and northbound, not DNS over HTTPS (the base system's unbound is built without it). Not lists of the document's. |
| R20–R23 Notification modifier, Block and Quarantine by default | partly | `notify` per list, Block and Quarantine where it says nothing; the record for IPPF and DPF, unbound's log for DNF and PDNS, Squid's access log for URLF. |
| R24–R30 SEN | yes | A SEN for each deny the edges' rules logged and each Suricata alert, with Table 3's items: issuer, UTC time, a UUID, the function and its policy, IOC or OTHER, the event, source, details, action and the UNI where known ([D2]); domains and URLs neutralised with `[.]` ([R28], [D3]); kept by the console alone ([R26]), read by `GET /api/sdwan/sen` (and `.csv`), shown on the Security tab, sent to the recipients Settings names ([R30]: mail, Telegram). |
| R31–R36 SAN | yes | A SAN for each function policy whose values a kept document changes ([R31]), with Table 4's: who, from where, when, the values that changed alone, a Block's and Quarantine's names neutralised ([R34]); kept by the console alone ([R32]), `GET /api/sdwan/san`, the Security tab, its recipients ([R36]). The audit trail keeps the whole document's changes beside. |
| MBSF, Middlebox (§7, Table 9) | partly | Squid's bump with a CA of the edge's own; Block and Allow of TLS versions, No-match, `invalid-server-certificate`, `unencrypted`, `trusted-cas` (the edge's own). TLS alone ([R45]): no IPsec middlebox; Squid asks for no client certificate. |
| IPPF (§8.1, Table 10) | yes | ipfw on each flow: Table 5's eight criteria, Block, Allow, Quarantine, named lists of prefixes, No-match, Duration. |
| DNF (§8.2, Table 11) | yes | unbound, a view a zone; a name or `*.` and one, each with the names beneath it. A `*` for a whole label inside a name ([R71], `host.*.tld`) on a Block or Quarantine is ended by the zone's Squid at the TLS name and refused by the request's host, since unbound has no such match; on an Allow it is refused. |
| URLF (§8.3, Table 12) | yes | Squid by zone: hosts at the TLS name or the request, paths in the request, where TLS is opened (MBSF) or the request is cleartext. |
| MD+R (§8.4, Table 13) | partly | ClamAV through c-icap: signature scan, the object not passed on (block the subset); the lists are hashes (MD5, SHA-1, SHA-256, with the size where known), each edge's written as ClamAV's hash signatures (`.hdb`, `.hsb`; an Allow's as its false positives, `.fp`, `.sfp`) before c-icap starts. No behaviour analysis; No-match Allow alone. |
| DLP (§8.5, Table 14) | no | FreeBSD has no engine for it. |
| DPF (§8.6.1, Table 15) | partly | ipfw on the flow's DNS (53, and 853 for DNS over TLS): addresses, Block answered at once (port unreachable, [R100]); `message-type` `any`, `query` (to the port) and `response` (from it); an update or another kind is inside the message, which ipfw does not read. `redirect` is Arcana's Alter, of queries. |
| PDNS (§8.6.2, Table 16) | partly | unbound by zone: A and AAAA answers by their addresses (`respip`), CNAME and NS entries by a response policy zone of the zone's own (a QNAME trigger on the alias's chain; `rpz-nsdname`, `rpz-nsip`) ([R104]: SOA, MX, SRV and PTR not limited, unbound's RPZ having no trigger on their values); DNS over TLS southbound (port 853, a certificate of the instance's own) and northbound (`forward-tls-upstream`) ([D20]–[D22]); not DNS over HTTPS ([D19]), the base system's unbound lacking it. |
| R116 Performance impact stated | partly | The book says where each function runs; no measured figures. |

Arcana has two of its own that no Security Function is: `ids`
(Suricata, detect or prevent) and `rate-limit` (dummynet).

## MEF 118.1: Zero Trust Framework

| Requirements | Status | In Arcana |
|---|---|---|
| R1 Service Attributes encrypted at rest and in transit | partly | In transit, yes (TLS between the console and the agents). At rest, the console's document is plain JSON, readable by the console's user alone. |
| R2–R11 Identity Provider: IdPID, OAuth 2.0 (R6), OpenID Connect, SAML | no | The console is the only IdP, without OAuth or SAML. |
| R12 MFA for Authentication | partly | The console's users sign in with security keys (WebAuthn); a remote identity has one factor, its key. |
| R13–R15 Authentication requests logged | no | A WireGuard handshake is not logged as a request. |
| R20, R38 At least one Role | yes | An identity's zone. |
| R21, R33–R37 A unique Actor ID | partly | An identity's name, unique at its remote end point. |
| R41–R43 System Administrator alone changes Policies | yes | The console's users, and the write API tokens they make, audited by name; a read token reads only. |
| R44–R60 Device and Application Actors | no | Only User Actors (identities) and a UNI's hosts by zone. |
| R61–R63 PIP, PDP, PEP | yes | The console (information and decision), the edges (enforcement). |
| R64 Allow or Block | yes | The policy map, Block where no Policy is. |
| R65 An Audit Event for each Policy Action | partly | The audit trail for what the console does, the record for what the edges deny; an Allowed session is not audited one by one. |
| R66 The Audit Event tamper-proof | partly | The console's trail is HMAC-chained under a key of its own; the edges' record is not. |
| R67, R68 A Policy End Point for each Actor | yes | The edge of its UNI or remote end point. |
| R69–R98 PBAC, MAC, DAC, ABAC, RBAC | partly | Roles (zones) and Policies; no attributes, labels or constraints of their own. |
| R99–R101 Delegation | no | |
| R102–R111 Non-programmatic User-to-User | n/a | |
| R112–R118 Risk Score | no | |
| R119–R121 Continuous Monitoring by time | yes | A remote end point's re-authorisation interval, the same for every identity there (not per session, [R121]). |
| R122–R124 By event | no | Events are kept and sent, but none takes a Policy Action. |
