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
| `jails`, `services`, `packages`, `jobs`, `storage`, `sysctl`, `kernel`, `processes`, `logs`, `firewall`, `history`, `events`, `bird`, `wireguard`, `netgraph`, `host`, `agent`, `probes`, `sdwan`, `sshd`, `builder` | Arcana's own (`share/yang`) | each the operation that reads the same: jail(8) and jls, rc.d, pkg(8), the job queue, ZFS and GEOM, sysctl(3), kldstat, the process table, `/var/log`, ipfw(8), the samples, the event log, birdc, wg(8), ngctl(8), the host's facts, the transport and TLS, the probes, the SD-WAN state, sshd, poudriere |

What a plugin's program reads (BIRD, WireGuard, netgraph) is left out
where the program is not installed or does not answer: a read of
everything is not lost for one host's lack of BIRD.

## Reading it

```
arcanactl get interfaces
arcanactl get routing network-instances
arcanactl get            # everything
```

The answer is RFC 7951's JSON: a member is `module:name` where its
module changes, 64-bit numbers and decimals are strings, an identity is
`module:name`, an `empty` leaf `[null]`.

## Actions and jobs

Some of the modules' actions are served, each done as the agent's own
operation does it, what changes the host one change at a time:

| Action | On | Done as |
|---|---|---|
| `start`, `stop`, `restart`, `kill` | `jails/jail` *name* | jail(8), as the Start and Stop buttons |
| `start`, `stop`, `restart`, `reload` | `services/service` *name* | service(8) |
| `signal`, `renice` | `processes/process` *pid* | kill(2), setpriority(2), the process's start time checked |
| `cancel`, `confirm` | `jobs/job` *id* | the job queue's own |
| `refresh` | `packages` | `pkg update` |
| `read` | `logs` | the end of a log, as the Log tab reads it |
| `routes` | `bird` | `birdc show route` |

```
arcanactl action jails/jail web restart
arcanactl action processes/process 4242 signal signal=HUP
arcanactl action logs read name=messages lines=20
```

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

## From the console

`GET /api/servers/<id>/data?node=interfaces,routing` answers with the
host's YANG data under `data`, as RFC 7951's JSON, for a script or a
tool that speaks YANG rather than Arcana's own API.

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
