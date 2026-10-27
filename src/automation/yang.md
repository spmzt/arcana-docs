# The models: YANG

Besides its own protocol, the agent serves what it knows of the host as
YANG data, the way an SDN controller reads a router: the IETF's and
IEEE's standard models where there is one, Arcana's own modules for the
rest. The console reads the Network tab's interfaces this way, and
`arcanactl get` reads any of it.

## What is served

| Node | Module | Read from |
|---|---|---|
| `interfaces` | RFC 8343 `ietf-interfaces`, with RFC 8344 `ietf-ip`, `ietf-if-extensions`, IEEE 802.3, 802.1AX and 802.1Q, `arcana-interfaces` | getifaddrs(3) and the ioctls ifconfig(8) uses: `SIOCGIFFIB`, `SIOCGTUNFIB`, `SIOCGIFPSRCADDR`, `SIOCGIFXMEDIA`, `SIOCGLAGG`, `SIOCGETVLAN`, bridge(4)'s `BRDGGIFS`; nd6's state |
| `linkagg`, `bridges` | IEEE 802.1AX, 802.1Q | lagg(4)'s and bridge(4)'s parts of the same |
| `network-instances` | RFC 8529 | the FIBs, `net.fibs`, named in `fibs.conf` beside the agent's files (`fib2_name="blue"`); each interface's `bind-ni-name` its FIB's |
| `routing` | RFC 8349 with the unicast routing modules | the RIBs as netlink(4) dumps them (multipath routes as next-hop lists), rc.conf's `static_routes` as the static protocol, the last change of a route from the route events; the `active-route` action is `route get` |
| `logical-network-elements` | RFC 8530 | the vnet jails, jail_get(2) |
| `syslog` | `ietf-syslog` | syslog.conf(5) and newsyslog.conf(5) |
| `yang-library` | RFC 8525 `ietf-yang-library` | the agent's own tables: every module it implements with its revision, namespace and the features it has on, those it imports only for their identities, the operational datastore, a content-id that changes with the set |
| `alarms` | RFC 8632 `ietf-alarms`, with `arcana-alarms` | the agent's faults: each one an alarm whose resource is the fault's object and whose type is its kind (a tunnel down, a threshold crossed, a BFD or BGP or OSPF neighbour lost, BIRD not answering, an interface without link, an IDS that prevents not running, IPsec keys not rotated, storage, CPU, memory, a process's crash); its raising and clearing as its history; an inventory of the kinds and a summary by severity |
| `jails`, `services`, `packages`, `jobs`, `storage`, `sysctl`, `kernel`, `processes`, `logs`, `firewall`, `history`, `events`, `bird`, `wireguard`, `netgraph`, `host`, `agent`, `probes`, `sdwan`, `sshd`, `builder` | Arcana's own (`share/yang`) | each the operation that reads the same: jail(8) and jls, rc.d, pkg(8), the job queue, ZFS and GEOM, sysctl(3), kldstat, the process table, `/var/log`, ipfw(8), the samples, the event log, birdc, wg(8), ngctl(8), the host's facts, the transport and TLS, the probes, the SD-WAN state, sshd, poudriere |

What a plugin's program reads (BIRD, WireGuard, netgraph) is left out
where the program is not installed or does not answer: a read of
everything is not lost for one host's lack of BIRD.

## Reading it

```
arcanactl get interfaces
arcanactl get routing network-instances
arcanactl get alarms
arcanactl get yang-library
arcanactl get            # everything
```

The answer is RFC 7951's JSON: a member is `module:name` where its
module changes, 64-bit numbers and decimals are strings, an identity is
`module:name`, an `empty` leaf `[null]`.

## Actions and jobs

The modules' actions and rpcs are served, each done as the agent's own
operation does it, what changes the host one change at a time: a
jail's `start` and `stop`, a service's, a process's `signal`, a job's
`cancel` and `confirm`, the packages' `refresh` and `upgrade`, a log's
`read`, BIRD's `routes`, the firewall's `trace`, the troubleshooting
`path-check`, `traceroute` and `capture`, a dataset's `load-key`,
`unload-key` and `change-key`, `fstab`'s `replace`, the events',
history's and probes' `read`, the agent's own (`update`, `build`,
`console-update`, `config-export`, `config-apply`, the TLS `csr` and
`install`, the transport's `retry`), the kernel's `load` and a file's
`unload`, `notify`, and RFC 8632's `purge-alarms` and
`compress-alarms`. A snapshot's `send` and the storage's `receive`
carry a stream and are not served yet. An rpc is called by its name
alone:

```
arcanactl action jails/jail web restart
arcanactl action processes/process 4242 signal signal=HUP
arcanactl action logs read name=messages lines=20
arcanactl action alarms/alarm-list purge-alarms alarm-clearance-status=cleared
arcanactl action load name=if_wg
```

The agent's `update` over the network takes a program signed with the
console's CA key (its `signature`), as the console's own update does.

`arcana-jobs`' `submit` rpc takes changes as the jobs of
[Jobs and the queue](jobs.md), each checked as the agent checks a
submitted job (and refused where it would cut the console off), and
answers with their ids. Editing the configuration as YANG data (an
EDIT of `running`) is the next part of the work
(`docs/PLAN-SDN-YANG.md`): until then, changes go by jobs.

## Notifications

Every event the host tells (the Log's events) is also an
`arcana-events:event` notification on the YANG family's group:

```
arcanactl notifications
{"ietf-restconf:notification":{"eventTime":"2026-10-27T01:20:05Z","arcana-events:event":{...}}}
```

## Subscriptions

A program that wants to be told rather than ask subscribes, as RFC 8639
has it, each subscription a stream of its own on the same connection.
The `NETCONF` stream is every event the agent tells; the operational
datastore is pushed on a period (RFC 8641's YANG-Push), what an XPath
filter selects of it:

```
arcanactl subscribe -x '/arcana-events:event/job'
arcanactl subscribe -p 5 -x "/ietf-interfaces:interfaces/interface[name='em0']/statistics"
arcanactl subscribe -o 0 -x '/arcana-jobs:jobs/job/title'
arcanactl get subscriptions
```

Each record is a line of RFC 8040's JSON; a push-update carries the
data under `datastore-contents`. With `-o` the data comes whole once,
then only its changes (YANG-Push's on-change), each a YANG Patch (RFC
8072) whose edits say what was made, changed or gone and where; the
agent notices them by reading at least every second, but for the
events and the alarms, which it reads again only when one is added or
changes. A stop-time (`-s`) ends a subscription, as does closing it;
`subscriptions` lists those running with what each has sent. A
subscription that falls behind (its stream's credit used up) is
suspended, told so, and resumed with the whole of its data again;
`modify-subscription` and `resync-subscription` work on one's own.
`-r` replays the events kept since a time before the live ones:

```
arcanactl subscribe -r 2026-10-27T00:00:00Z -x '/arcana-events:event/job'
```

Subscriptions the agent keeps by configuration are not served yet.

## From the console: RESTCONF

The console is a RESTCONF server (RFC 8040) of what it reads, each host
a mount point (RFC 8528) of the `arcana-fleet` module whose data is its
agent's models:

```
curl -H "Authorization: Bearer $TOKEN" \
    https://console.example/restconf/data/arcana-fleet:fleet
curl -H "Authorization: Bearer $TOKEN" \
    "https://console.example/restconf/data/arcana-fleet:fleet/host=1a2b3c4d/ietf-interfaces:interfaces/interface=em0?content=nonconfig"
```

A path below a host's entry is RFC 8040's api-path, its first node
named with its module; the console makes it an XPath filter of the
agent's read and answers with that node alone, as
`application/yang-data+json`. Of the query parameters, `content`
(config, nonconfig, all), `depth`, `fields` (`fields=type;statistics(in-octets)`)
and `with-defaults` (explicit, the agent's data as it is; report-all,
trim, report-all-tagged) are taken. `/.well-known/host-meta`
says where the root is; `/restconf/data` holds the fleet's hosts,
`restconf-state`'s capabilities and the console's `yang-library`. An
API token that reads may read it; errors are `ietf-restconf:errors`.

Each host's events are a stream of RFC 8040's (section 6), listed in
`restconf-state/streams` by the host's id: `/restconf/streams/<id>/json`
sends every event its agent tells as Server-Sent Events, a
`data:` line of RFC 8040's notification JSON each, its `id:` the event's
time, with a comment line now and then so that proxies keep it open. A
client that comes back with `Last-Event-ID` (a browser's EventSource
does by itself) is sent what the agent kept since that time first, the
last one it had among them again, then `replay-completed`. The
stream ends, with an `error` event saying why, when the host does.

The `fleet` stream, `/restconf/streams/fleet/json`, is every host's you
may read on one connection: each notification sits in its host's entry,
`{"arcana-fleet:fleet":{"host":[{"id":"1a2b3c4d","arcana-events:event":{…}}]}}`,
as RFC 8528 nests a mounted module's notification. A host whose stream
ends is named in an `error` event while the others go on.

```
curl -N -H "Authorization: Bearer $TOKEN" \
    https://console.example/restconf/streams/1a2b3c4d/json
```

A subscription of one's own goes as RFC 8650 has it: POST
`establish-subscription` under a host's entry, of the `NETCONF` stream
(with an XPath filter, a replay start time) or of the operational
datastore (periodic, its period in centiseconds, or on-change), and the
answer's `uri` is its stream, for whoever made it to GET within a
minute:

```
curl -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/yang-data+json' \
    -d '{"ietf-subscribed-notifications:input":{"ietf-yang-push:datastore":"ietf-datastores:operational","ietf-yang-push:datastore-xpath-filter":"/ietf-interfaces:interfaces","ietf-yang-push:periodic":{"period":500}}}' \
    https://console.example/restconf/data/arcana-fleet:fleet/host=1a2b3c4d/ietf-subscribed-notifications:establish-subscription
curl -N -H "Authorization: Bearer $TOKEN" https://console.example/restconf/subscriptions/<id>
```

Writes and YANG Patch are not served yet.

`GET /api/servers/<id>/data?node=interfaces,routing` answers with the
host's YANG data under `data`, as RFC 7951's JSON, in the console's own
API.

## On the wire

The models travel over cblink's YANG family, family 1, beside the
agent's own on the same mTLS connection: a GET names the top-level nodes
by SID and gets their values back as YANG-CBOR (RFC 9254), CORECONF's
FETCH in shape (draft-ietf-core-comi); an action goes with its target,
the list entry, as an instance-identifier (RFC 9254), CORECONF's POST.
Each request runs on a thread of its own, so a slow read (ZFS, BIRD)
holds no other. As the agent's own family, another host's certificate
is refused: only the console asks.
The SIDs are in RFC 9595's experimental range for now
(`share/yang/SIDS.md`).
