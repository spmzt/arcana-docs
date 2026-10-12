# Breakout, bandwidth and egress

What a policy says beyond the tunnels: whether a flow may reach the
Internet and where it leaves, how much of a link it may take and how
it ranks against the others, and what may not leave by a UNI.

## Beyond the tunnels

**Beyond the tunnels**, a flow with a policy may reach the hosts of
the edge's own UNIs of the service whose zone it is allowed, and the
Internet where its policy says `internet-breakout: enabled`
(R53–R57): what is not a prefix of the service's UNIs (the table
`sw<fib>_known`) is the Internet. Where it leaves is the edge's own
UCS end point marked `breakout` (local: the service's default route
by its `gateway`, reached by its interface, in the service's table),
else the first edge of the document that has one and a tunnel to it
(remote: the default route by the tunnel). Leaving locally, IPv4 is
translated by an ipfw nat instance (`3000 + fib`) to the first host
of the `nat.public_prefix` of the edge's end point that has one, else
the interface's address, with `nat.exceptions` left as they are; what
comes back in by that interface to the translated address or to the
service's prefixes is forwarded by the service's table (`setfib`),
and when no flow at the edge's UNIs breaks out, what comes in from
the Internet for the service's prefixes is dropped (R56). The nat
instance's output does not go through the kept rules. A flow's
packets that none of this lets through are dropped by the flow's own
last rule, so a later flow never sees them (R96); a policy without
`internet-breakout` drops the flow's Internet traffic (R57).

## Bandwidth

**Bandwidth** (`bandwidth` in a policy: a rate limiter's name, shared
by every flow naming it, or the policy's own `commit` and `limit`,
R77–R83): each limiter is a dummynet pipe of its `limit` (none: no
limit), each flow in it a queue of that pipe weighted 1 to 100, half
by its commit's share of the pipe's commits and half by its
`business-importance` among the service's `importance.levels`, the
first level the highest (D4). The queue meters the flow after the
policy says it is forwarded (R79): on the way out by the service's
tunnels, and in the flow's rule for its own UNIs' hosts and for
breakout. The pipes and queues are numbered from 3000 and are made
and deleted with the rules; `dummynet` and `ipfw_nat` are loaded as
needed. A packet out of a pipe leaves the firewall (ipfw's one_pass).
**Egress** (`egress` in an end point's policy map, R85, R86): a flow
of the zone whose egress policy says `egress-block: discard` is
dropped leaving by that end point's UNI. Backup and billing are in
the steering above (R63, R64); a rooted-multipoint topology gives a
leaf its roots only, so no edge forwards for another (R50, R51).
