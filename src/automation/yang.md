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
answers with their ids.

## Configuration: running and the candidate

The models are also configuration, in RFC 8342's datastores:
`running`, what is in use (read from the kernel and from what rc(8)
reads, without what DHCP, SLAAC or the kernel made), and `candidate`,
the configuration being made, one for every session. Running changes
by a confirmed commit of the candidate alone (RFC 6241 section 8.4):
the host undoes it at its timeout unless a second commit confirms it.

```
arcanactl get -d running routing > routing.json
# ... routing.json edited: a static route added ...
arcanactl edit routing @routing.json
arcanactl get -d candidate routing
arcanactl commit -c 120
confirm within 120 seconds: arcanactl commit -i 3f9a0c2e8b71d465
arcanactl commit -i 3f9a0c2e8b71d465
```

A commit is checked first against the model (types, keys, mandatory
nodes, `when` and `must`) and the host's access rules, then made all or
nothing. So far it changes the static routes of each FIB; interfaces
made and destroyed, and an interface's description, state, MTU,
addresses, FIB, router advertisements (every capability of
rtadvd.conf(5), `arcana-ra` on RFC 8349's) and the vnet
jail it is moved into (`bind-lne-name`, RFC 8530); the network
instances, a FIB each (`net.fibs` raised for the next boot when one
more is asked for); syslog.conf(5) and newsyslog.conf(5) from
ietf-syslog; sysctl.conf(5) (`arcana-sysctl`, each value set in the
kernel too, a tunable refused with loader.conf(5) named); `kld_list`
(`arcana-kernel`); each service's `<name>_enable` and its own rc.conf
variables (`arcana-services`); and the access rules themselves. A vnet jail's own
network is read through its logical network element's `root`, served
by a helper of the agent's attached to the jail. Anything else is
refused as not supported yet, and jobs do the rest.

A read says how defaults are reported with `-w` (RFC 6243: `explicit`,
`report-all`, `trim`, `report-all-tagged`), and with `-o` where each
configuration node of the operational state came from (RFC 8342's
origin), as RFC 7952 annotations in the JSON:

```
arcanactl get -o interfaces
{"ietf-interfaces:interfaces":{"@":{"ietf-origin:origin":"ietf-origin:intended"},
 "interface":[{"name":"em0", ... "ietf-ip:ipv6":{"address":[
  {"@":{"ietf-origin:origin":"ietf-origin:learned"},"ip":"2001:db8:1::5c","origin":"link-layer", ...},
  {"@":{"ietf-origin:origin":"ietf-origin:system"},"ip":"fe80::5054:ff:fe12:3456","origin":"link-layer", ...}]}}]}}
```

`intended` is what running has, `learned` what DHCP, SLAAC or a
temporary address gave or a neighbour the host found, `system` what the
kernel made, `default` a default in use, and `unknown` what was set by
hand since; a node says it only where it is not its parent's.

The console turns the two reads into a host's **Configuration drift**,
on its Summary: running against the configuration part of the
operational state (RFC 8342's intended against operational), a row a
node with its api-path: configured but not in effect, differing, or
beyond running with where it came from (set by hand, learned, the
kernel's own). `GET /api/servers/<id>/drift` gives the rows.

What a commit keeps of rc.conf(5) goes into a file of Arcana's own,
`/usr/local/etc/rc.conf.d/arcana`, which `rc_conf_files` in
`/etc/rc.conf` names so that rc(8) reads it after yours. Your files are
left as they are but for what you accept with `-a`: naming the file in
`rc_conf_files`, once (`rc-conf-files`), and a variable Arcana writes
that your files set too, commented out in yours (`rc-conf-conflict`):
the line stays where it was, under a `#`, with `# taken by Arcana`
after it, so you can see what was yours and put it back. Nothing of
yours is deleted. A refusal says which it waits for:

```
arcanactl: commit: your files set what Arcana would write: static_routes (/etc/rc.conf line 2); accept rc-conf-conflict to keep them in Arcana's file, commented out in yours (go on with -a rc-conf-conflict)
```

A host that was configured by hand can be moved under Arcana in one
go, service by service, with arcana-services' `convert` action: each
named service's `<name>_enable` and `<name>_*` variables, as rc(8)
reads them from your files, are written to Arcana's file and commented
out in yours; no name, every rc script the host has. `-n` says what
would be taken, writing nothing; a variable whose value is an
expansion, or on a line sh(1) may or may not run, is left where it is
and the row says why. It is a change like a commit's: the same warnings
apply, and failing, every file is put back.

```
arcanactl services convert -n sshd ntpd
SERVICE  VARIABLE       VALUE  WHERE
sshd     sshd_enable    YES    /etc/rc.conf:4
ntpd     ntpd_enable    YES    /etc/rc.conf:7
ntpd     ntpd_sync_on_start  YES  /etc/rc.conf.d/ntpd:1
arcanactl services convert -a rc-conf-conflict sshd ntpd
```

Where the kernel refuses a change, the files are put back and the
commit fails. An undo the host cannot do (a commit not confirmed in
time) stops there and leaves the rest as committed: a Critical alarm,
an alert by mail or Telegram, and on the host's Log (its events) a
report of the failure alone, not of your configuration, with a link
that opens an issue of Arcana's with it for you to file if you choose.
Arcana files nothing.

The console does the same over RESTCONF (RFC 8527's datastores): a
node put in `/restconf/ds/ietf-datastores:candidate/arcana-fleet:fleet/host=<id>/...`,
then `ietf-netconf:commit` POSTed under the host's entry with `persist`
(the console's connection to a host is every user's). The access rules
are edited on a host's Security tab in just that way.

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

A subscription the agent keeps by configuration (RFC 8639 section 2.5)
has the console as its receiver over HTTPS-notif
(draft-ietf-netconf-https-notif): `GET /api/servers/<id>/subscription`
gives the document to put into the host's candidate and commit, after
which the agent calls the console's `/api/notif/<host>/relay-notification`
with its own certificate for every record, replays what the console
missed while it was away (from the last record it kept), and the
console keeps them (`GET /api/servers/<id>/notifications`) across its
own restarts.

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
trim, report-all-tagged) are taken, and of the operational datastore
(`/restconf/ds/ietf-datastores:operational/...`) `with-origin`.
`/.well-known/host-meta` says where the root is; `/restconf/data`
holds the fleet's hosts, `restconf-state`'s capabilities, the console's
`yang-library` and `schema-mounts` (each host's entry an inline mount;
inside an agent, each network instance's `vrf-root` a shared-schema
mount of its FIB's routing, with its own YANG library). An
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
