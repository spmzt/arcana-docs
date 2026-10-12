# The plugins

A plugin is what works through a program that has to be installed, not
the base system's:

| Tab | Program | Package |
|---|---|---|
| **WireGuard** | `wg(8)` (the interface itself, `if_wg(4)`, is the base system's, among the interfaces) | `wireguard-tools`; from FreeBSD 15 `wg` is in the base system |
| **BIRD** | `birdc(8)` | `bird3` |
| **IPsec** | strongSwan's `swanctl(8)` (an `ipsec(4)` interface is the base system's) | `strongswan` |

Each has a tab of its own, after the others and marked ◆, on every
host. Where the plugin is not installed (on the host, or in the jail
picked, each marked so in the picker), the tab says which program it
works through and which package has it, with a button that installs it
there with `pkg install`, a job of its own; the tab comes alive once it
is done. Nothing is installed but when that is pressed. **From a
template… → A plugin's package installed** does the same as a workflow.

A jail's programs are looked for as the jail sees them: the agent
attaches to the jail to look, so a link inside the jail leads where it
does there. The picker at the left of the toolbar names the host and
each running vnet jail, and the tab is then of that jail.

## WireGuard

The `wg` interfaces with their peers: endpoint, allowed addresses, last
handshake, traffic.

![WireGuard: an interface and its peers](../img/sec-wireguard.png)

- **Make its key** has the host make the interface's private key, which
  stays on the host: the console is told, and shows, public keys only,
  and what `wg` prints with keys in it is kept out of the trace.
- **+ peer** adds a peer by its public key; the cross removes one.
- **+ interface** opens the interface form with wg chosen.

Kept for a boot, an interface is written with its key, addresses and
peers to `/usr/local/etc/wireguard/<if>.conf` for `wg-quick`, readable
by root alone, and named in `wireguard_interfaces`: that needs the
`wireguard-tools` package.

## IPsec

strongSwan, IKEv2 only: every connection Arcana writes says `version =
2`.

![IPsec: connections, their children and SAs](../img/sec-ipsec.png)

### Keys and certificates

**Make its key** has the host make a key of its own, ECDSA P-256, whose
private half stays on the host; the tab shows the public half, which is
what a peer is given: two hosts know each other by their keys, no CA
between them. Where there are certificates, the tab reads them from
swanctl's `x509` and `x509ca` and lists them with each one's subject,
names and expiry, so that a peer is known one of three ways: by its
public key, pasted; by its certificate, picked from `x509`; or by a CA
that signed its certificate, with the peer's identity saying which.
This host can use a certificate of its own from `x509` too.

**At boot** keeps strongSwan started with the host
(`strongswan_enable`), and **Start** starts it when it is not running.

### Connections and children

**+ connection** joins this host to another between two addresses,
with one child in **tunnel** mode or in **transport** mode, where what
is sent between the two addresses is protected as it is: a gre, gif or
WireGuard tunnel between them, the traffic named as `192.0.2.1[gre]`.

A connection is the IKE side, the two addresses and how each is known;
its children are what it carries, each in its own mode between its own
traffic selectors. **+ child** adds one, the cross on a child takes it
away. With a **reqid** a child serves the `ipsec` interface made with
that reqid: tunnel mode, the interface's routes deciding what goes
through it.

A connection is written as `swanctl/conf.d/arcana-<name>.conf`, with the
peer's key in `pubkey` when it is known by its key, and strongSwan reads
them all again; if it refuses, the files are put back as they were. The
table has each connection with its children, its SA's state and
algorithm, and its traffic; **Up**, **Down**, and the cross, which takes
it away, its SAs ended first.

### In a jail

In a vnet jail, strongSwan is the jail's own, installed in it: its key,
its `swanctl/conf.d` and its `strongswan_enable` are beneath the jail's
root, and `swanctl` and the rc.d script run in it. The kernel's IPsec is
the host's: built in, or `ipsec.ko` loaded on the host, since a jail
cannot load a module; the tab says so when it is not there.

From a shell: `arcanactl ipsec init | start | conn | child | unchild |
unconn | up | down`.

## BIRD

The routing daemon drawn in the middle, and around it its BGP
neighbours (their AS and address), its OSPF neighbours and its RPKI
caches, each coloured by its state. Under the protocols, the **BFD
sessions**: each neighbour that asked for BFD, on which interface, and
whether it still answers.

![BIRD and its neighbours](../img/sec-bird.png)

A neighbour picked opens in a box: what the daemon says of it (session,
timers, each channel's table, its import and export filters, how many
routes came and went), **restart**, **reload**, **disable** and
**enable**, and the part of the configuration that makes it, to be
changed there. Each channel's import and export filter is chosen from a
list of the filters the file has, with `all` and `none`.

### The configuration

Under it, what the configuration is made of, read from the host:

- **filters and functions**, what BGP and OSPF take in and give out,
  each edited as it is written;
- **communities and sets**, the named lists filters test against, one
  entry a line, a community as `(AS, value)` and a large one as `(AS,
  a, b)`;
- **RPKI**, the caches with their state and the ROA tables, and **+
  cache**, which adds the tables, the protocol and a function
  `rpki_invalid()` for filters to ask;
- the protocols and the rest, with **+ BGP neighbour** and **+ OSPF**
  to start one from an outline.

**Configuration** edits the whole file; a configuration in several
files has a list to pick from. A change is put back as the whole file
with that part changed. The host has `bird -p` parse the whole
configuration first: what it refuses does not stay, the box says what
bird said, and what was typed is kept. Then BIRD is told to read it. The
file as it was is kept beside it as `<file>.arcana-old`.

### BIRD's own safe mode

A change is made in safe mode unless that is turned off beside
**Configuration**: BIRD is told to take the new configuration back by
itself (`configure timeout`, for the host's rollback timer), and a few
seconds later the page says that it stays (`configure confirm`), which
it can only do if the console still reaches the host. If it cannot,
BIRD goes back to what it ran when the time is up, and the host puts
the file back as it was. While a change waits, another is not taken.

A BIRD that does not take a configuration leaves the file as it was.
One that stops answering while it is told is not undone: the file
parses, and stays for BIRD to read when it is started again; the host
starts nothing by itself.

### Routes

**Routes** shows what BIRD's tables hold: for a prefix, or for an
address the route that covers it; those learned from a neighbour or
sent to it; those of one table; and what they carry, a BGP route's path
and communities. More than 2000 routes are not fetched, and the count
is said instead.

From a shell: `arcanactl bird routes …`, `arcanactl -s bird config -w
file`, `arcanactl bird confirm`.
