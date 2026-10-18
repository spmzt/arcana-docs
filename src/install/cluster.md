# A cluster of consoles

One console is one point of failure: when its host stops, the fleet has
no panel. A **cluster** is several consoles that are one, active on
every node. Each serves the browsers that come to it from its own copy
of the console's documents (the hosts, the users and their keys, the
workflows, the SD-WAN services…), and a change made on any is every
one's.

## How it works

The nodes talk to each other over cblink, the transport the console
already speaks to the agents, in a family of their own, `arcana-cluster`
(`share/arcana/cluster.yaml`), by TLS with certificates of the console's
CA. They elect a **leader** with Raft:

- A node that hears no leader for a second and a half or so asks the
  others for their votes; a node votes once a term, and only for one
  that holds every change it holds. A majority makes a leader, which
  says so every 400 ms.
- Every change is a whole document (each of the console's stores is
  written whole). The leader numbers it, sends it to the others, and
  makes it once a **majority** holds it: then every node writes it into
  its data directory. A change made on a follower goes to the leader
  first, and the follower answers the browser once it is made.
- A node that was away is sent what it missed; one too far behind is
  sent every document whole.
- The workflow scheduler, the SD-WAN manager and mail run on the leader
  alone, and move with it.

So three nodes go on when one stops, five when two do. A node cut off
from the majority still shows what it has, and refuses changes, saying
the cluster has no majority there.

## Setting one up

1. Install the console on each node as usual ([The console](console.md)).
2. The first node is the **seed**: if a console already runs, it is
   that one, and its documents become the cluster's. Copy its `ca.pem`
   and `ca.key` (in `/var/db/arcana`) into each other node's data
   directory before that node first starts, so that they are one
   console to the agents and to each other.
3. Give every node the same `cluster` block in `web.conf`, but `self`:

   ```
   rp_id = "console.example";
   origin = "https://a.console.example";

   cluster {
   	self = "a";
   	listen = "tcp://[::]:4311";
   	nodes {
   		a { uri = "tcp://a.console.example:4311";
   		    origin = "https://a.console.example"; }
   		b { uri = "tcp://b.console.example:4311";
   		    origin = "https://b.console.example"; }
   		c { uri = "tcp://c.console.example:4311";
   		    origin = "https://c.console.example"; }
   	}
   }
   ```

   `rp_id` is a name every node's origin is under: a security key
   registered on one node then signs in on every one, and a browser
   signed in on one is signed in on all.
4. Start the nodes. Each makes its own certificate of the CA,
   `cluster/node.pem`, which says `urn:arcana:role:console` and its host
   name; the nodes take each other by it.

**Settings › Cluster** shows the nodes, who leads and in which term, and
how far each holds the changes; `GET /api/cluster` says the same.

## Where it is kept

Each node keeps its term, its vote and the changes not yet in every
node's documents in `cluster/` of its data directory, written and
`fsync(2)`ed before it says anything to the others. The documents
themselves are the data directory's JSON files, as on a single console.
