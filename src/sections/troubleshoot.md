# Troubleshoot

**Troubleshoot**, in the side bar: a packet from one address to another
followed across the hosts and their vnet jails, and what stops it on
the way. Nothing is sent to find it out: each place says what it would
do with the packet, from its addresses, its routes, its ARP and NDP
entries, its sysctls and its firewall's ruleset as the kernel has them
now.

![A packet's way, and where it is stopped](../img/tour-troubleshoot.png)

## Packet path

Give the source and the destination, the protocol (TCP, UDP, ICMP, or
any IP) and the port, and where to look: the hosts, and their running
vnet jails that route as routers do. None ticked, every host is asked.

Where the packet comes in is the place whose address the source is, or
the one on the source's network, coming in on that interface. There it
is asked:

- **does the firewall take it in**: ipfw's ruleset walked for the
  packet, coming in on that interface;
- **does the place forward at all**: `net.inet.ip.forwarding`;
- **is there a route to send it by**, the *send route*: in the FIB of
  the interface it came in on, or the one the firewall's `setfib` gives
  it; a blackhole or reject route is said as one;
- **does the next hop answer**: its ARP or NDP entry;
- **does the firewall let it out** by that interface;
- **does the reply find its way back**, the *receive route*: the route
  back to the source from where the reply comes in, by the same
  interface (symmetric) or another; and does the firewall let the reply
  in and out.

The send route names the next hop (or the firewall's `fwd` another), and
the place that has that address is asked next, the packet coming in on
the interface that has it, until the destination is reached, the next
hop is no place of the console's (it leaves them there), something
stops it, or it comes back to a place it passed (a loop).

The reply is followed the same way, from the destination back, as a
reply: a TCP segment of the connection (not a SYN), an echo reply, from
the service's port. A place it passes that the request did not has no
state of the request: a stateful firewall there (`check-state`,
`keep-state`) drops it, and uRPF (`verrevpath`) on a place the request
came in on by another interface drops the request itself. When the
request and the reply go by different places, that is said as the
asymmetry it is.

What is wrong is said first, worst first, each with its place: the
firewall dropping it (and by which rule), no send route, no receive
route, forwarding off, a next hop that does not answer, an asymmetric
way back. Below, the way there and the way back, place by place: where
it comes in, each firewall's verdict with its rule (the rule's text when
hovered), the route, the next hop, and each place's own check. The
whole can be exported as JSON or YAML.

<div class="freebsd">

**FreeBSD:** the ruleset is the kernel's, as `ipfw list` and `ipfw table
all list` print it, and the walk follows `ip_fw2.c`: `count` and
`setfib` go on, `skipto` jumps forward, `check-state` and the first
`keep-state` look the flow up, `verrevpath`, `versrcreach` and
`antispoof` by the routes, `me` by the place's addresses, a table by its
longest entry, `tablearg` by the entry's value. A rule the walk cannot
judge for a packet that was never sent (a socket's `uid`, a `tag`, a MAC
address) is named as uncertain, never guessed. The routes are netlink's
`RTM_GETROUTE` per FIB, the neighbours `RTM_GETNEIGH`; a vnet jail's
are read from inside it. The walk is tested against the kernel: packets
sent at a ruleset in a vnet jail move the counter of the rule it names.

</div>

The agent's `path-check` answers for one place: `arcanactl
[-j jail] path-check [-r] [-F fib] [-i interface] [-p proto] [-P port]
src dst`.
