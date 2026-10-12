# Probes, rules and steering

Once the tunnels are up, each edge measures them, the firewall sorts
the subscribers' packets into flows, and each flow is sent by the
tunnel its policy prefers: chosen by the edge itself when a tunnel
goes down, and by the console's manager when a tunnel's delay, its
variation or its loss crosses the policy's thresholds.

## Paths

![Paths: each tunnel as its probes see it](../img/sd-paths-error.png)

(The picture is of a test run whose agent is not root, so its probes
could not run; see [Troubleshooting](faults.md#troubleshooting).)

**Paths** shows what each edge's probes see of each tunnel. After the
tunnels and their far ends, an apply tells each edge the tunnels to
measure (`sdwan-probes`): the far inner address of each, pinged (ICMP
echo, a raw socket, so the agent must be root) through the service's
table, as Mplify 119 §11.4 has an edge measure its tunnels. Of each
eval interval the agent keeps a sample: the one-way delay, half the
mean round trip (MEF 105); the delay variation, the mean difference
between one round trip and the next; the loss; the least and the
most. So many misses in a row and the tunnel is down, so many answers
and it is up again, each an event (`sdwan-tunnel`) the Faults list
shows. The service's `probe` sets how: `interval` (ms, 100), `size`
(bytes, 64), `count` (0 for without end), `dscp`, `down` and `up` (3
and 3), `timeout` (ms, 1000), `history` (samples kept, 3600) and
`report`; `intervals.eval` is the sample's length. The targets are
kept beside `history.conf` for the agent's next start; `arcanactl
sdwan` reads what they saw, `arcanactl sdwan probes json` sets them.
Under each tunnel's table, its **monitor**: three charts over the last
5, 15 or 60 minutes (the buttons at the top), the delay (each end's
mean a line, its least to most a band), the variation and the loss,
both ends each in a colour, the service's `tca` threshold a dashed
line where set, and the tunnel's faults (tunnel, bfd, tca) as bands of
the time they were open; a column hovered gives its figures. The page
asks each edge only for the samples after the last it gave (`after`)
and keeps the earlier ones, as many as the agent does.

## The rules

**The rules** (after the probes, before the routes and UNIs): the
console compiles each edge's services into one ipfw ruleset of their
own, in set 30, rules 10 to 99, kept apart from the kept rules and
loaded again at the agent's start (`sdwan-rules`). What comes in at a
UNI goes by its source to its zone's block (`skipto tablearg` by the
zone table; no zone, dropped, R23; a packet with source routing
dropped, D1); the block has the flows in order, each with the ingress
policy the end point's map or the zone gives it (R109–R112): a flow
with none, or Block, is dropped; one with a policy is forwarded by the
policy's table (`fwd tablearg`), which maps each far prefix to the
inner address of the tunnel chosen for it, and what is not in the
table goes on; a packet no flow matches is dropped (R96). A flow's
criteria are said as ipfw says them (addresses, protocols, ports,
DSCP, `appid` by a small catalog: dns, http, https, ssh, sip, ntp,
smtp, imap, pop3, ldap, rdp, snmp, syslog, ike, bgp, quic, dhcp,
icmp); `ethertype` cannot be, and a flow with IPv4 and IPv6 criteria
both matches nothing.

## The steering

**The steering** (`sdwan-steer`): for each policy's table, each far
prefix the policy may reach (its virtual topology, R47–R51; its
allowed destination zones, R58–R62, Self alone by default) with the
tunnels that fit the policy (encryption, public or private, billing,
backup only when enabled, R63) in order: no backup first, private
before public. The edge takes the first whose far end its probes do
not say is down, fills a second table beside the one in use and swaps
it in, and chooses again the moment a probe's state changes: the local
failover, with no console. Where a policy has `performance`, the
console's manager reads every edge's probes every five seconds and
orders the tunnels by it (R69, R70): those that meet every threshold
first, by the primary metric, and the one in use stays first while it
meets them and is under the ceiling (R73); an order that changed is
sent to the edge. `GET /api/sdwan/steer` says what was sent last;
Paths shows each edge's prefixes, by which tunnel each goes now and
the others' states.
