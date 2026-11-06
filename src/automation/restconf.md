# The API: RESTCONF

The console's API is **RESTCONF** (RFC 8040): one API for the console's
own configuration, for the SD-WAN services and for every host, each
part described by a YANG module the console lists in its YANG library.
The panel itself is a client of it. A program needs nothing of
Arcana's own to use it: any RESTCONF client, or `curl`, reads the
library, then the data, the way an SDN controller reads a router.

The old JSON API under `/api` is deprecated: every route of it has its
home in RESTCONF ([the table at the end](#from-api-to-restconf)), and
it goes away in a coming release but for what RESTCONF has no place for
([Beside RESTCONF](#beside-restconf)).

<div class="freebsd">

**FreeBSD:** the console is one program, `arcana-console(8)`, serving
HTTP/1.1 and HTTP/2 over TLS (libwebsockets). What it serves of a host it asks that host's `arcana-agent(8)`
over cblink's YANG family (YANG-CBOR, RFC 9254) on the mTLS connection
the agent keeps, and the agent reads it from the FreeBSD facility
itself: `jail_get(2)` for the jails, rc(8)'s files for the services,
netlink(4) for the routes, `ipfw(8)` for the firewall. The paths below
are the modules' names for them, not the console's.

</div>

## Finding it

```
curl https://console.example/.well-known/host-meta
<XRD xmlns='http://docs.oasis-open.org/ns/xri/xrd-1.0'>
  <Link rel='restconf' href='/restconf'/>
</XRD>
```

| Resource | Is |
|---|---|
| `/.well-known/host-meta` | where the root is (RFC 8040 §3.1, RFC 6415's XRD) |
| `/restconf` | the root: `data`, `operations`, `yang-library-version` |
| `/restconf/yang-library-version` | `2019-01-04`, RFC 8525's |
| `/restconf/data` | the console's datastore: its own modules, the fleet, `restconf-state`, `yang-library`, `schema-mounts` |
| `/restconf/data/ietf-yang-library:yang-library` | the console's modules, revisions and namespaces (RFC 8525) |
| `/restconf/data/ietf-restconf-monitoring:restconf-state` | the capabilities and the streams |
| `/restconf/operations` | the console's rpcs (`ietf-vn:vn-compute`, `arcana-console:trace-path`, `arcana-console:wireguard-keypair`) |
| `/restconf/data/arcana-fleet:fleet/host=<id>/…` | a host's data, as its agent serves it (the fleet mount) |
| `/restconf/ds/ietf-datastores:<running\|candidate\|operational>/arcana-fleet:fleet/host=<id>/…` | a host's datastore by name (RFC 8527) |
| `/restconf/streams/<id>/json`, `/restconf/streams/fleet/json` | events as Server-Sent Events |
| `/restconf/subscriptions/<n>` | a subscription's stream |

Every module, with each top-level node, rpc, action and notification
as an api-path, is in [RESTCONF paths, by module](../reference/restconf-paths.md),
made from the modules themselves at every build of this book.

## Signing in

RESTCONF has no sign-in of its own: a request carries a session or a
token.

- **A session.** The panel's sign-in (a security key or passkey by
  WebAuthn, or a password the console keeps) sets an HttpOnly,
  SameSite=Strict `arc_session` cookie. A request with it that changes
  something (POST, PUT, PATCH, DELETE) also needs the console's page as
  its `Origin`, which a browser sends by itself, or, from a client that
  sends no `Origin`, the header `X-Arcana: 1`. Another site cannot send
  either without a CORS preflight the console never answers.
- **An API token**, `Authorization: Bearer arcr_…` (reads) or
  `arcw_…` (reads and writes), made under Settings › AAA › API tokens.
  It needs no `Origin` or `X-Arcana`: a browser never sends a bearer
  token by itself. Neither kind reads or changes the console's
  settings, sign-in keys, push or enrolment, and a write token changes
  neither the tokens nor the CA.

```
TOKEN=arcr_...
curl -H "Authorization: Bearer $TOKEN" https://console.example/restconf/data/ietf-yang-library:yang-library
```

## Who may: roles and NACM

Two checks, in order. The **console's** role of the user (owner,
operator, member) and their **role on the host** (admin, operator,
viewer, a host at a time or `*`), as Settings › AAA › Roles gives them:
a host no role of theirs names is not in their `fleet`, not in their
streams and answers 404. A viewer reads; an operator changes and calls
actions; an admin also updates, builds and moves the agent. An action's
role is its kind's: `read` and the reads (`arcana-bird:bird/routes`,
`arcana-firewall:firewall/trace`, `ietf-routing`'s `active-route`, …)
a viewer's, the agent's own update and build an admin's, the rest an
operator's.

Then the **host's** own access rules: each call reaches the agent as
the user, and the agent applies its NACM (RFC 8341, `ietf-netconf-acm`)
to it. The console keeps the hosts' NACM groups in step with its users
and roles (`hosts/host=<id>/nacm-sync`), and a host's rules are
edited like any of its configuration (its Security tab does so).

<div class="freebsd">

**FreeBSD:** the agent runs as root and checks NACM itself, as the
user the console names, before it touches the system: the rules are
the agent's, so a host keeps them even against a console that asked
for more.

</div>

## Reading

`GET` a node by its api-path: the first node named with its module,
`module:name` again where the module changes, a list entry by its keys
(`interface=em0`, `vpn-service=office`), a key's own `/`, `,` or `=`
percent-encoded.

```
curl -H "Authorization: Bearer $TOKEN" \
    "https://console.example/restconf/data/arcana-fleet:fleet/host=1a2b3c4d/ietf-interfaces:interfaces/interface=em0?content=nonconfig&fields=oper-status;statistics(in-octets)"
{"ietf-interfaces:interface":[{"name":"em0","oper-status":"up","statistics":{"in-octets":"88641725"}}]}
```

The query parameters taken: `content` (config, nonconfig, all),
`depth`, `fields`, `with-defaults` (explicit, report-all, trim,
report-all-tagged) and, of the operational datastore, `with-origin`
(RFC 8527: where each configuration node came from, as RFC 7952
annotations). Any other is refused with `invalid-value`.

### JSON and YANG-CBOR

`application/yang-data+json` (RFC 7951) both ways is the default. A
host's data may also be read as **YANG-CBOR** (RFC 9254), as the
agent sent it, unchanged: an `Accept` that names
`application/yang-data+cbor; id=sid` before JSON. Its keys are the
host's SIDs, which its `.sid` files name; `content`, `depth`, `fields`
and the defaults are JSON's and refused with it. A change's body may be
YANG-CBOR too, made JSON by the console before it is checked. The
console's own modules are JSON alone.

### The fleet mount

Each host is an entry of `arcana-fleet:fleet`, and a **mount point**
(RFC 8528) of the models its agent serves: an agent of an older
release serves its own set, so each host is read by its own schema,
not the console's. `/restconf/data/ietf-yang-schema-mount:schema-mounts`
says so (an inline mount labelled `agent`), and the host's own library
is inside it:

```
curl -H "Authorization: Bearer $TOKEN" \
    https://console.example/restconf/data/arcana-fleet:fleet/host=1a2b3c4d/ietf-yang-library:yang-library
```

A path naming a node the host's modules have not is 404 ("the host's
modules have no …"). The console reads each host's library and its
`.sid` files once, and again when the agent is restarted or updated.
Inside an agent, each network instance's `vrf-root` is a mount of its
own, of that FIB's routing.

## Changing

### The console's own

The console's modules are changed in place, under `/restconf/data`,
by POST (create, 201 with `Location`), PUT (create or replace, 201 or
204), PATCH (merge, 204) and DELETE (204), each change checked as RFC
7950 says (types, keys, mandatory nodes, leafrefs, `when`, `must`) and
then by the console's own rules, all or nothing:

```
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/yang-data+json' \
    -d '{"arcana-console:hosts":{"host":[{"id":"1a2b3c4d","tenant":"lab"}]}}' \
    https://console.example/restconf/data/arcana-console:hosts
```

A secret is never read back: a token's value, an invitation's link,
the bot's token or the directory's password are written alone (a
`-set` leaf says whether there is one), or said once in an action's
output.

### A host's: the candidate and a confirmed commit

A host's configuration changes as NETCONF's does (RFC 6241 §8.3,
§8.4): the node is changed in the host's **candidate**, then
`ietf-netconf:commit` is POSTed under the host's entry, **confirmed**,
and confirmed again within its timeout, or the host itself puts running
back as it was:

```
H=https://console.example/restconf/data/arcana-fleet:fleet/host=1a2b3c4d
C=https://console.example/restconf/ds/ietf-datastores:candidate/arcana-fleet:fleet/host=1a2b3c4d
J='Content-Type: application/yang-data+json'

curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"ietf-routing:routing":{"control-plane-protocols":{"control-plane-protocol":[{"type":"ietf-routing:static","name":"static","static-routes":{"ietf-ipv4-unicast-routing:ipv4":{"route":[{"destination-prefix":"198.51.100.0/24","next-hop":{"next-hop-address":"192.0.2.1"}}]}}}]}}}' \
    "$C/ietf-routing:routing"
curl -X POST -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"ietf-netconf:input":{"confirmed":[null],"confirm-timeout":120,"persist":"route-1"}}' \
    "$H/ietf-netconf:commit"
# still reachable? then:
curl -X POST -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"ietf-netconf:input":{"persist-id":"route-1"}}' \
    "$H/ietf-netconf:commit"
```

A confirmed commit through the console names `persist`: the console's
connection to a host is every user's, and its end must not undo the
commit. `cancel-commit` puts running back at once, `discard-changes`
empties the candidate. A change under `/restconf/data` or running
directly is refused (405) and says where to make it. What is not
configuration is not changed.

<div class="freebsd">

**FreeBSD:** a commit is the agent's: it writes what rc(8) reads into
its own file, `/usr/local/etc/rc.conf.d/arcana` (named once in
`rc_conf_files`), and makes the kernel's state with the base tools,
`ifconfig(8)`, `route(8)`, `sysctl(8)`. The undo at the timeout is the
agent's too, so a commit that cuts the host off from the console comes
back by itself. See [The models: YANG](yang.md).

</div>

### Warnings accepted: `arcana-accept`

A change the host would make only with your consent (naming its file in
`rc_conf_files`, commenting out a variable of yours) is refused with
the warning as the error's `error-app-tag`. The same change with the
query parameter `arcana-accept`, the tags by commas, goes on despite
them, and those alone:

```
curl -X POST ... "$H/ietf-netconf:commit?arcana-accept=rc-conf-files,rc-conf-conflict"
```

Nothing is accepted silently: the panel asks before it sends one.

### YANG Patch

Several edits in one request, all or nothing: PATCH with
`application/yang-patch+json` (RFC 8072), its seven operations
(create, delete, insert, merge, move, replace, remove), `where` and
`point`. The reply is `ietf-yang-patch:yang-patch-status`, `ok`, or
each failed edit's errors by its `edit-id`. `OPTIONS` says
`Accept-Patch`.

```
curl -X PATCH -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/yang-patch+json' \
    -d '{"ietf-yang-patch:yang-patch":{"patch-id":"two","edit":[
          {"edit-id":"a","operation":"merge","target":"/vpn-service=office","value":{"ietf-l3vpn-ntw:vpn-service":[{"vpn-id":"office","vpn-description":"lab"}]}},
          {"edit-id":"b","operation":"remove","target":"/vpn-service=old"}]}}' \
    https://console.example/restconf/data/ietf-l3vpn-ntw:l3vpn-ntw/vpn-services
```

### Entity tags

Every read and change answers with an `ETag` and `Last-Modified`:
the console's own modules', the services', or a host's running and
candidate. `If-Match`, `If-None-Match`, `If-Modified-Since` and
`If-Unmodified-Since` are taken (412 where it changed since, 304 where
nothing did): two clients editing one thing do not undo each other.
The panel sends `If-Match` with the tag it read.

## Actions and rpcs

An **action** is POSTed on its node's path (RFC 8040 §3.6); a
**host's rpc** is POSTed under the host's entry, `H/<module>:<rpc>`;
the **console's** rpcs at `/restconf/operations/<module>:<rpc>`. The
input is `{"<module>:input": {...}}` (or none), the output
`{"<module>:output": {...}}` (200), or 204 where there is none.

```
curl -X POST -H "Authorization: Bearer $TOKEN" "$H/arcana-jails:jails/jail=web/restart"
curl -X POST -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"arcana-log:input":{"name":"messages","lines":20}}' "$H/arcana-log:logs/read"
curl -X POST -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"arcana-jobs:input":{"job":[...]}}' "$H/arcana-jobs:submit"
```

A host's warnings ride along as `arcana-fleet:warnings`. Some of the
console's own are what it works out rather than keeps: a host's
`drift` and the SD-WAN's `plan` are `anydata` read at their own path
alone (not in their parent's GET), and actions such as a host's
`move` and `agent-update` or the SD-WAN's `apply` answer with their
document in an `anydata` `result`.

Of `ietf-netconf`'s rpcs, `commit`, `cancel-commit` and
`discard-changes` are served through the mount; the others answer 405,
RESTCONF's methods doing what they do.

## Events: streams and subscriptions

Each host's events are a stream (RFC 8040 §6), listed in
`restconf-state/streams`: `GET /restconf/streams/<id>/json` sends
every event its agent tells as **Server-Sent Events**, an RFC 8040
notification's JSON on each `data:` line, its `id:` the event's time.
A client that comes back with `Last-Event-ID` (a browser's
EventSource does by itself) is sent what the agent kept since first.
`/restconf/streams/fleet/json` is every host you may read on one
connection, each notification in its host's entry.

A subscription of one's own (RFC 8639, RFC 8641's YANG-Push) is
POSTed as `ietf-subscribed-notifications:establish-subscription`
under a host's entry: of the `NETCONF` stream with an XPath filter
and a replay start, or of the operational datastore, periodic or
on-change. Its answer's `uri` is its stream, for its maker to GET:

```
curl -X POST -H "Authorization: Bearer $TOKEN" -H "$J" \
    -d '{"ietf-subscribed-notifications:input":{"ietf-yang-push:datastore":"ietf-datastores:operational","ietf-yang-push:datastore-xpath-filter":"/ietf-interfaces:interfaces","ietf-yang-push:periodic":{"period":500}}}' \
    "$H/ietf-subscribed-notifications:establish-subscription"
curl -N -H "Authorization: Bearer $TOKEN" https://console.example/restconf/subscriptions/7
```

## Errors

Every error is `ietf-restconf:errors` (RFC 8040 §7), with its
`error-type`, `error-tag` and its status (`invalid-value` 400,
`access-denied` 403, `data-missing` 404 or 409, `data-exists` 409,
`operation-not-supported` 405 or 501, `in-use` 409,
`operation-failed` 500, `malformed-message` 400, …), the node at fault
as `error-path`, why as `error-message`, and Arcana's reason, when it
has one, as `error-app-tag`:

```
{"ietf-restconf:errors":{"error":[{"error-type":"application",
  "error-tag":"operation-failed","error-app-tag":"rc-conf-files",
  "error-message":"Arcana keeps what it writes of rc.conf in /usr/local/etc/rc.conf.d/arcana, which rc(8) reads where rc_conf_files names it: accept rc-conf-files to add it to /etc/rc.conf, once"}]}}
```

## The console's own modules

| Module | Is | Where |
|---|---|---|
| `arcana-console` | the console's configuration and state: settings, users, roles, groups, tokens, enrolment, hosts, workflows and runs, templates, labels, prefix lists, threat feeds, transfers, push, CA, plugins, security keys, update, cluster; and the SD-WAN's verbs | `/restconf/data/arcana-console:…` |
| `ietf-l3vpn-ntw` (RFC 9182) with `ietf-vpn-common` (RFC 9181) and `arcana-l3nm` | the SD-WAN services, stored as L3NM: [The service as L3NM, SAP and VN](../sdwan/models.md) | `/restconf/data/ietf-l3vpn-ntw:l3vpn-ntw` |
| `ietf-network`, `ietf-network-topology` (RFC 8345), `ietf-sap-ntw` (RFC 9408) | the fleet's SAPs over its physical network, read from the agents | `/restconf/data/ietf-network:networks` |
| `ietf-vn` (RFC 9731) with `arcana-sdwan-underlay` | the services' customer view, read alone; `vn-compute` | `/restconf/data/ietf-vn:access-point`, `ietf-vn:virtual-network`; `/restconf/operations/ietf-vn:vn-compute` |
| `arcana-fleet` | the hosts, each a mount point | `/restconf/data/arcana-fleet:fleet` |
| `ietf-yang-library`, `ietf-yang-schema-mount`, `ietf-restconf-monitoring` | what is served | as above |

The SD-WAN's verbs are a container of the console's,
`arcana-console:sdwan`: `document` (the services as a MEF 70.2
document, read and written whole), `plan`, `ledger`, `apply-state`,
`steering`, `rekeys`, `lists`, `identities`, `audit`, `sen`, `san` and
`record` (`Accept: text/csv` for the CSV), and the actions `check`,
`apply`, `pin`, `rekey`, `fetch-lists`, `issue-identity`,
`revoke-identity` and `attach`.

## Beside RESTCONF

What is no YANG data stays a resource of Arcana's own, beside
`/restconf`, and needs no token:

| Resource | Is |
|---|---|
| `/api/health` | is the console up |
| `/api/auth/status`, `/api/auth/register/{begin,finish}`, `/api/auth/login/{begin,finish}`, `/api/auth/login/password`, `/api/auth/login/token`, `/api/auth/password`, `/api/auth/setup/password`, `/api/auth/logout` | the WebAuthn ceremonies, passwords, the session |
| `/api/enrol` | a host's enrolment by its one-time token (`arcana-enrol(8)`) |
| `/.well-known/assetlinks.json` | the Android app Android may let sign in |
| `/api/notif/<host>/capabilities`, `/api/notif/<host>/relay-notification` | the receiver the agents' configured subscriptions post to (HTTPS-notif, RFC 8650), by the host's certificate |
| `/api/servers/<id>/ids/pcap`, `/api/servers/<id>/ids/pcap-log` | a pcap up- and downloaded, bytes, not YANG |

They keep these paths until `/api` goes; then they move beside
`/restconf`, as this book will say.

## From /api to RESTCONF

The deprecated [/api routes](../reference/api.md), each with its home.
`C` is `/restconf/data/arcana-console:`, `H` a host's entry
`/restconf/data/arcana-fleet:fleet/host=<id>`, `O` `/restconf/operations/`.
"Edited, committed" is a PUT or PATCH of the host's candidate and its
confirmed `ietf-netconf:commit`, as above.

| /api route | Home |
|---|---|
| health; auth/*; enrol; `/.well-known/assetlinks.json` | [beside](#beside-restconf) |
| notif/&lt;host&gt;/capabilities, relay-notification | beside: the receiver the agents post to |
| servers/&lt;id&gt;/ids/pcap, ids/pcap-log | beside: bytes up and down |
| stream (WebSocket) | `/restconf/streams/<id>/json`, `/restconf/streams/fleet/json`, `establish-subscription` under `H` |
| auth/credentials, credentials/&lt;id&gt; | `C credentials` |
| servers GET POST, servers/&lt;id&gt; POST DELETE | `C hosts`, `C hosts/host=<id>` |
| servers/&lt;id&gt;/drift, watch, notifications, subscription, tls GET, transport GET, config GET | `C hosts/host=<id>/` drift, watch, notifications, subscription, tls, transport, configuration |
| servers/&lt;id&gt;/move, tls POST, transport POST, transport/switch, nacm-sync, agent-build, agent-update, console-update, config/export, config POST, capture, subscription/token | `C hosts/host=<id>/` move, renew-tls, listen, switch-transport, nacm-sync, agent-build, agent-update, console-update, export-configuration, apply-configuration, capture, subscription-token (actions) |
| update, update/notes, cluster | `C update`, `C update-notes`, `C cluster` |
| ca GET POST | `C ca` (state), `C ca/` make, request, import, discard, rollout, finish |
| plugins, plugins/&lt;id&gt;, plugins/&lt;id&gt;/store[/shared] | `C plugins`, `plugin=<id>/enabled`, `plugin=<id>/store`, `shared-store` |
| settings, settings/mail-test, telegram-test | `C settings`, `settings/mail-test`, `settings/telegram-test` |
| tokens, tokens/&lt;id&gt; | `C tokens`, `tokens/create` |
| users, users/&lt;n&gt;, users/&lt;n&gt;/invite; roles, roles/&lt;n&gt;; groups, groups/&lt;n&gt; | `C users`, `user=<n>/invite`, `C roles`, `C groups` |
| enrol/tokens | `C enrolment/create-token` |
| workflows, workflows/&lt;id&gt;, workflows/&lt;id&gt;/run | `C workflows`, `workflow=<id>/run` |
| runs, runs/&lt;n&gt;, runs/&lt;n&gt;/approve | `C runs`, `run=<n>/approve`, `run=<n>/stop`, `runs/clear` |
| templates, templates/&lt;n&gt; | `C templates` |
| labels, labels/&lt;host&gt;/&lt;if&gt; | `C labels` |
| prefix-lists, prefix-lists/&lt;n&gt; | `C prefix-lists` |
| feeds, feeds/&lt;id&gt;, /fetch, /preview | `C threat-feeds`, `feed=<id>/fetch`, `preview` |
| transfers, transfers/&lt;n&gt; | `C transfers`, `transfers/start`, `transfer=<n>/stop` |
| push, push/subscribe, unsubscribe, send | `C push`, `push/send` |
| sdwan GET PUT, sdwan/check | `C sdwan/document` (stored as `ietf-l3vpn-ntw:l3vpn-ntw`), `sdwan/check` |
| sdwan/plan, ledger, apply GET, steer GET, rekey GET, lists, identities GET, audit, sen, san, record (and .csv) | `C sdwan/` plan, ledger, apply-state, steering, rekeys, lists, identities, audit, sen, san, record (CSV by Accept) |
| sdwan/apply POST, steer POST, rekey POST, lists/fetch, identities POST DELETE, attach | `C sdwan/` apply, pin, rekey, fetch-lists, issue-identity, revoke-identity, attach |
| troubleshoot/path, wg/keypair | `O arcana-console:trace-path`, `O arcana-console:wireguard-keypair` |
| servers/&lt;id&gt;/hello, stats, certs | `H/arcana-host:host`, `host/stats`, `host/read-certificates` |
| servers/&lt;id&gt;/data | `H`, or `H/<module>:<node>` |
| servers/&lt;id&gt;/jails, jails/&lt;n&gt;/action, address, jails/files | `H/arcana-jails:jails`, `jail=<n>/{start,stop,restart,kill}` (enable: `boot` edited), `jail=<n>/arcana-network:address`, `jails/arcana-jail-files:read-files` |
| servers/&lt;id&gt;/services, services/&lt;n&gt;/action, config | `H/arcana-services:services`, `service=<n>/{start,stop,restart,reload}` (enable: `enabled` edited), `service=<n>/variable` (edited, committed) |
| servers/&lt;id&gt;/net/* | `H/arcana-network:network/<kind>`, `ietf-interfaces:interfaces`, `arcana-troubleshoot:troubleshoot/traceroute`, `arcana-netgraph:netgraph/read`, `arcana-wireguard:wireguard/read`, `arcana-bird:bird/{read,routes,ospf}`, `arcana-firewall:firewall` (state) |
| servers/&lt;id&gt;/bird/config | `H/arcana-bird:bird/configuration` (edited, committed; `bird/check`) |
| servers/&lt;id&gt;/storage/*, fstab, zfs/key | `H/arcana-storage:storage` and `storage/read`, `storage/fstab` (`fstab/replace`), `dataset=<ds>/{load-key,change-key}`, `create-encrypted` |
| servers/&lt;id&gt;/builder, builder/options | `H/arcana-builder:builder`, `builder/port-options` |
| servers/&lt;id&gt;/suricata/rules, netstore, system, smtpd, speeder, monitors, ssh | `H/arcana-suricata:suricata/read-rules`, `arcana-netstore:netstore/read`, `arcana-system:system/read`, `arcana-smtpd:smtpd/read`, `arcana-speeder:speeder/read`, `arcana-probe:probes/read`, `arcana-sshd:sshd/read` |
| servers/&lt;id&gt;/kernel, sysctl, processes, log, events | `H/arcana-kernel:kernel`, `arcana-sysctl:sysctl/read`, `arcana-processes:processes`, `arcana-log:logs/read`, `arcana-events:events/read` |
| servers/&lt;id&gt;/ipfw/rules, ipfw/trace, ipfw/path | `H/arcana-firewall:firewall/kept` (edited, committed; `firewall/check`), `firewall/trace`, `arcana-troubleshoot:troubleshoot/path-check` |
| servers/&lt;id&gt;/history | `H/arcana-history:history/read`, `history/sampling` and `limits` (edited, committed) |
| servers/&lt;id&gt;/security, sdwan | `H/arcana-sdwan:sdwan` (edited; `sdwan/apply`), `sdwan/state` with `arcana-probe:probes/state` and `arcana-steer:steering/state` |
| servers/&lt;id&gt;/packages, packages/upgrade | `H/arcana-packages:packages/{read,refresh,upgrade}` (a jail's below `jails/jail=<n>`) |
| servers/&lt;id&gt;/jobs, jobs/config, jobs/dry-run, jobs/&lt;n&gt; | `H/arcana-jobs:jobs`, `arcana-jobs:submit`, `jobs/lanes` (edited), `arcana-jobs:dry-run`, `job=<n>/read`, `job=<n>/cancel` |

## openapi.yaml

The console's page still offers `openapi.yaml`, the OpenAPI document of
`/api`: it is frozen, marked deprecated, and removed with `/api`.
RESTCONF needs none: its description is the YANG library and the
modules it lists, which any RESTCONF client reads from the console
itself.
