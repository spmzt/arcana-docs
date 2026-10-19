# What Arcana is

Arcana is a fleet manager written for FreeBSD and nothing else. It does
not abstract the system away: what you see in the panel is what the
host's own programs and libraries report, and what you change is
changed the way an administrator would change it by hand, with the
same tools, in the same files.

## One user, many hosts

Arcana is built for one administrator, or a small team sharing one
console, looking after anywhere from one host to a few hundred. Each
host runs `arcana-agent`, a small daemon. The console runs on one of
them (or in a container) and talks to every agent over an encrypted,
mutually authenticated connection.

## What it does

- **Jails**: lists them as `jail(8)` and `jail.conf` have them, starts,
  stops and restarts them, changes their addresses live or in
  `jail.conf`, and opens a jail's own network when it has one (vnet).
- **Services**: every `rc.d` script of the host or a jail, started,
  stopped, enabled, and its `rc.conf` variables changed.
- **Packages**: what is installed, what can be upgraded, installed and
  upgraded on the host and in its jails.
- **Network**: interfaces, routes and nexthops of every routing table
  (FIB), sockets and connections, bridges, VLANs, tunnels, netgraph;
  changes made in *safe mode*, which the host takes back by itself if
  the change cut the console off.
- **Firewall**: the `ipfw` ruleset kept by Arcana, its tables, pipes
  and queues, and a trace of the packets it sees.
- **Storage**: disks, ZFS pools, datasets and snapshots, mounts.
- **WireGuard**: the base system's `wg(8)`, its interfaces, peers and
  clients, a view of the Network tab.
- **Plugins**: strongSwan's IPsec and BIRD, each a tab of its own when
  its package is installed.
- **Fleet-wide**: a network map of the whole fleet, utilization over
  time, workflows that run chains of jobs by hand, on a timer or on an
  event, and SD-WAN services across the hosts.

## How a change is made

Nothing in the panel changes a host directly. A button sends a *job* to
the host's agent, which does the work there and keeps it until it is
done. You can watch it, or close the browser and come back: the job's
result and its trace stay on the host. Jobs can wait in a queue for you
to look over and send together, and a queue can become a workflow.

Changes that could cut a host off (an address, a route, a firewall
rule) are made in safe mode: the agent makes the change and waits to
hear from the console again. If it does not, within the host's
rollback timer, the agent undoes the change on its own.

## What it is not

Arcana does not install anything on a host by itself. Programs that are
not part of FreeBSD's base system, such as BIRD, strongSwan or Squid,
are *plugins*: their tab says which package they need, and you install
it, with a button or by hand.
