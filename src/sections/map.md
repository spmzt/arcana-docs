# The network map

**Network**, in the tree, shows the fleet as a map. Nothing is
configured for it: the console reads each host's interfaces every few
seconds and works the links out. Its second tab, **Nexthop groups**, has
every host's routes of several next hops with what each next hop sent
and what its gateway received, as a host's [Nexthops](network.md#nexthops-and-their-groups)
draws them; its third, **Traceroute**, is below.

![The map: three hosts, a shared network, a private link and a tunnel](../img/demo-map.png)

## Links

A link is drawn only between hosts of this console: a tunnel whose far
end is an address of another host, a point-to-point address whose peer
is one, or two hosts with addresses in the same network. Three or more
hosts in one network join a node of its own. A link carries its
traffic: its width and the dots that run along it follow the rate of
the interface behind it. On a tunnel or a point-to-point link, each
end's interface is written at its own end, and what it carries in the
middle.

Routing is drawn too, from what each host's BIRD says: a BGP session or
an OSPF adjacency between two hosts as a link of its own kind, and a
neighbour that is not a host of this console as a small node beside the
host that speaks to it, with its AS or router ID; picking one opens
that host's BIRD. **Peers** hides them.

A running vnet jail is a node of its own, drawn with a dashed edge
under its host: it has its interfaces and their traffic, its tunnels,
its BGP and OSPF sessions, as a host has. **Its network** opens its
host's Network tab with the jail picked. **VNet jails** hides them all,
and **Jails** hangs each host's running jails under it.

## Moving around

A host is dragged to where it should be, and stays there in that
browser; the map is dragged to move it, the wheel zooms, and on a
phone two fingers do. **Fit** shows every host, **Arrange** puts them
back on a circle and straightens every line. Once the map was moved or
zoomed it is not fitted again unasked, so nothing shifts under the
hand. A line is dragged to bend it away from the lines beside it.

**Labels** has the switches of what is written: **Names** and **Rates**
apart, and one for each kind of line. Until a kind is switched, a kind
with more than six lines has its labels left out, and a line shows its
own when the pointer is on it or it is picked. The **legend** names the
kinds of lines, and each is picked to take that kind out of the map and
put it back.

A host or a link is picked for its details beside the map: the host's
interfaces with their addresses and a chart of each one's traffic; a
link's two ends. With nothing picked, what the whole fleet receives and
sends over time, its busiest interfaces, and every WireGuard session.

## Drawing a tunnel

Drag the dot on a host's edge onto another host. The console offers the
outer addresses the two reach each other by and a free pair of inner
ones, asks for the kind (gif, gre, WireGuard, vxlan), and creates an
interface on each host, the two ends of one tunnel. For WireGuard each
host makes its own key; once both have one, each is given the other as
its peer, by its public key, at its outer address. Each end is made in
safe mode, and kept in `rc.conf` unless told otherwise. A tunnel picked
on the map is destroyed with one button, both ends.

## Look up the route

Asks each host on the way which route it takes to an address, follows
the gateway to the host that has its address, and draws the way over
the map hop by hop, until the address is reached, the way leaves the
hosts of this console, or it comes back to where it was. Beside each
hop are the routes that would be taken in its place when the best one
goes, drawn dashed.

## Traceroute

The way the packets take in fact, as `mtr` shows it: from a host of this
console to an address or another host, a round of `traceroute` every
second, a probe a hop, each hop with what it lost and its last,
average, best and worst times and their deviation. A hop that answers
differently over the rounds says how many more answered. Where a hop is
a host of this console it is named, with the interface the probe came
in by; and of each of ours on the way, the interface it sends on, by
which gateway, and that interface's MTU: the smallest of them is as
large as the path's MTU can be.

From a shell: `arcanactl traceroute address`.

<div class="freebsd">

**FreeBSD:** the links are worked out from each host's `getifaddrs(3)`;
a route is looked up among the routes the kernel gives through
`netlink(4)`, the most specific first; traceroute is `traceroute(8)` and `traceroute6(8)`.

</div>
