# Security

**Security**, in the side bar: the plugins that guard a host by
themselves, apart from SD-WAN, a tab each. Choose the host at the top;
each tab says what runs there and what it was given. The plugins are
the host's own: Arcana installs none of them by itself. A tab whose
plugin the host lacks says so, with a button that installs it when you
press it (`pkg install squid`; `c-icap c-icap-modules clamav`;
`clamav`; `suricata`).

SD-WAN's security policies use the same plugins at its edges
([Security policies](../sdwan/security.md)); what this page makes is
kept apart from them: its instances are named `sec-…`, and saving one
list never stops the other's.

## URL filter

Squid as a proxy the clients are told of, in their browsers or by WPAD
(an *explicit* proxy, not one the firewall sends traffic to). For each
filter:

- **Listens on** and **Port**: the host's addresses the clients use,
  3128 unless said.
- **Who may use it**: the networks it serves; the rest are refused.
- **TLS**: *its name looked at* (sni) reads the name a client asks for
  as TLS begins (Squid's `ssl_bump peek`), ends the connection when the
  name is denied, and leaves the rest unopened (`splice`). *Opened*
  (inspect) decrypts it (`bump`) with a CA of the filter's own, made
  once by openssl(1) and kept on the host: the clients must trust it,
  and the row shows its certificate to copy.
- **Denied**: a domain a line; the names beneath it are denied too.
- **Scan what it fetches for malware**: see Malware below.
- **More options › Routing table**: the FIB it reaches the web by,
  setfib(1).

Squid's configuration is checked with `squid -k parse` before it is
used; a running filter is told to reconfigure, one not running yet is
started. Its logs are `/var/log/squid/<name>-access.log` and
`-cache.log`.

## Antivirus

ClamAV, in one tab: what it scans, and below it the signatures it knows.

### Scanning

c-icap with ClamAV's module scans what a URL filter fetches before the
client has it, and an object that holds malware is refused. Each filter
that scans has a c-icap of its own on the loopback, started before its
Squid; tick **Scan what it fetches for malware** in the filter's form,
or **Stop scanning** here.

### Signatures

ClamAV knows what its signatures know: freshclam fetches them from
ClamAV's mirrors into `/var/db/clamav`. The tab lists each database
(main, daily, bytecode) with its version, how many signatures, and when
it was built, as the head of its file says; and whether freshclam runs.
**Start freshclam**, or **Look now** while it runs, is the service
`clamav_freshclam` enabled and started or restarted: it looks for new
signatures as it starts.

**Mirrors** are freshclam.conf's `DatabaseMirror` lines, a line each in
the order freshclam tries them: a host name, or an http or https URL.
Saving them writes those lines in place of the ones there were, and
restarts a running freshclam so that it reads them. Where freshclam.conf
is missing, or is still the port's sample with the `Example` line that
keeps freshclam from running, saving the mirrors, or starting freshclam,
makes it from the sample without that line. The mirrors offered by
default are ClamAV's own, `database.clamav.net`, and Microsoft's,
`https://packages.microsoft.com/clam`, which carries the same
databases. `arcanactl clamav mirrors` does the same.

## IDS/IPS

Suricata watching interfaces: its alerts are counted in the table and
the latest shown under it, and each is an event in the host's log.

- **Interfaces**: what it watches, by pcap(3).
- **The networks it guards**: the rules' `HOME_NET`; empty, the private
  ranges (RFC 1918); `any`, alone, every address, and `EXTERNAL_NET`
  then `any` too. **And the networks of a list** adds the prefixes of
  one or several of the console's prefix lists (pick several with Ctrl
  or ⌘).
- **The ruleset suricata-update keeps**: Emerging Threats Open, fetched
  by **Fetch the ruleset** above the table, which runs
  `suricata-update` on the host (to `/var/lib/suricata/rules`) and then
  applies the instances again, so that one started without it takes
  it and those reading it read their rules again (`SIGUSR2`). The line
  under the buttons says when it was fetched. Until it is, an instance
  that adds it runs on its own rules, and its job says so.
  `arcanactl suricata update` does the same.

An instance's form has Suricata's settings, folded, each Suricata's
default unless given:

- **Logging**: what `eve.json` has besides alerts (HTTP, DNS, TLS,
  SSH, flows and the other event types), an alert's packet and payload,
  and the statistics every so many seconds (10 unless told; 0 none),
  which the graphs read; and the packets of its alerts kept
  (`pcap-log`, conditional on alerts), a ring of files of so many
  megabytes in its log directory, listed under its statistics, for
  Wireshark or a replay.
- **Capture**: by `pcap(3)`, watching (the default), or by
  `netmap(4)`, taking the NIC's rings, a thread a ring as the NIC's RSS
  fills them. With netmap it also prevents at L2: each pair of
  interfaces (`em0:em1`) is a bump in the wire, what one receives
  passed to the other by Suricata, dropping what its rules say
  (`copy-mode: ips`, the `workers` runmode); `em0:em0^` puts it between
  em0 and its host stack. Divert, below, is the L3 way, behind `ipfw(8)`.
  **Its interfaces' offloading off** turns checksum, TSO and LRO
  offloading off by `ifconfig(8)` as it starts, so Suricata sees
  packets as they are on the wire; while it is on, the instance's row
  says so (`SIOCGIFCAP`).
- **Performance**: a preset for a host of its size (small, medium,
  large: the runmode, detect profile, memcaps and packets pending the
  fields below do not say), the host's CPUs and memory domains
  (`hw.ncpu`, `vm.ndomains`), the runmode (`workers`: one thread does all of a
  packet), the pattern matcher (Hyperscan where it is built in), the
  detect profile, the CPUs of its management and worker threads
  (`cpu-affinity`, as `cpuset(1)` numbers them) and the packets pending.
- **Memory**: the memcaps of flows, the stream, reassembly, fragments,
  hosts and HTTP (`64mb`, `512kb`, `1gb`).
- **Stream and HTTP**: the stream inspected before it passes where it
  prevents (`stream.inline`), how deep each is reassembled, streams
  picked up midway, how much of an HTTP request's and response's body is
  inspected, and what is done past a limit (`exception-policy`).
- **Plugins**: Suricata's plugins (a capture or an eve output), shared
  objects under `/usr/local/lib` the admin installed; the host loads
  none that is not root's and written by root alone.
- **Its own YAML**: keys the form does not set, checked by
  `suricata -T` with the rest; the keys the form owns (`plugins`,
  `run-as`, `unix-command`, the outputs and the rule files) it may not
  set again.

The form goes to the host as it is: the agent renders Suricata's YAML
from it and checks it there, so what runs is what was checked.

**Stop** stops an instance on the host and keeps its configuration,
shown *stopped*, and **Start** runs it again as it was; **Remove**
stops it and takes its files away. One that prevents passes nothing
while it is stopped, and the host says so, a Critical fault.

### Sources

**Sources** is where `suricata-update` fetches the ruleset from: the
sources of its index (**Fetch the list of sources** runs
`suricata-update update-sources`), each with its vendor, license and
what it is, and whether it is enabled here. With none enabled it
fetches Emerging Threats Open. **Enable** a commercial one (ET Pro,
Secureworks) asks for its secret code; the agent writes
`suricata-update`'s own file of the source,
`/var/lib/suricata/update/sources/NAME.yaml`, root's alone, so the code
is on no command line, in no task's title and in no trace. **Disable**
keeps it, **Remove** takes it away, and **Add by address** adds a
`.rules` file or an archive of them by `https`, `http` or `file:///`. A
change takes effect when the ruleset is fetched again. `arcanactl
suricata sources`, `source-enable name=et/pro secret-code=...`,
`source-disable`, `source-remove` and `source-add name=... url=...` do
the same.

### Statistics

**Statistics** on an instance's row is what Suricata's stats records in
`eve.json` say (every 10 s unless its form says otherwise), the agent
keeping the last hour of them: packets a second and those the kernel
dropped before Suricata saw them, throughput, alerts a second, memory in
use (flows, TCP, reassembly, HTTP) and TCP sessions and flows a second,
as graphs; its flows by protocol; and of its latest alerts the
signatures, sources and destinations seen most. Drops above a percent
or so are Suricata falling behind: see its settings (the `workers`
runmode, its threads' CPUs, larger memcaps).

Below them, **Ask Suricata** asks the instance's Suricata itself, by
its unix command socket (`unix-command`, a socket of each instance's
own): its memcaps, its rules loaded, skipped and failed (and which
failed), and each interface's packets, drops and invalid checksums.
**What to look at** is worked out of all that: drops above a percent,
invalid packets of offloading still on, memory near its memcaps, rules
that failed to load, alerts so many a second that their signatures want
a threshold. The line above them says what its Suricata is built with
(`suricata --build-info`): netmap, ipfw, Hyperscan, Lua, plugins and
rule profiling. **Rule profiling** (`ruleset-profile`, which rules
take the time) needs Suricata built with `--enable-profiling-rules`; the
port does not, and the page says how poudriere builds it so. `arcanactl
suricata rules instance=NAME command=memcap-list` asks the same.

**Replay a capture**, under its statistics, runs a capture the host has
(a `.pcap`, `.pcapng` or `.cap` by its whole path, a link not followed)
through the instance's configuration and rules, offline (`suricata
-r`, in a directory of its own, its running self untouched): a task,
whose alerts the page then shows. `arcanactl suricata pcap
instance=NAME file=PATH` does the same.

### Rules of its own, thresholds and suppression

**Own rules** on an instance's row shows its rules besides the
ruleset's as a table: each added or changed by its parts (action,
protocol, from and to with their ports, the way, the message, the sid,
the rev and its other options) or the whole as text, disabled (kept in
its rules file, commented out) or deleted. A new rule takes the next
local sid (1000000 and above). Every change applies the instance
again, so `suricata -T` checks it before it replaces what runs.

Below them, **Lua scripts** are the instance's own (Suricata 8 has Lua
built in): a rule runs one by its `lua:NAME.lua;` keyword, and one
marked an output is run on what it asks for (Suricata's Lua output).
The agent writes them to a directory of the instance's, which its
configuration names (`default-rule-path`), and Lua rules are allowed
only where it has scripts (`security.lua.allow-rules`).

Below them, **Thresholds and suppression** is the instance's
`threshold.config` (Suricata's `threshold-file`): a rule's alerts
suppressed, for every address or by source or destination; told at
most so many times in so long (`threshold`, `event_filter`); or past a
rate, its action changed for a while (`rate_filter`, a drop where it
prevents). **Suppress** beside an alert adds a suppression of that
rule from that source address.

### Rules

**Rules**, beside **Instances**, is the ruleset `suricata-update`
fetched, rule by rule: some 70000 for Emerging Threats Open, so the
host searches them and sends a page at a time. A search is any text of
the rule (a message, `ET SCAN`, a CVE), a class (`trojan-activity`),
and which rules: every one, those enabled, those disabled, or those set
here. A rule's sid shows its text.

Each rule can be enabled, disabled, made a **Drop** (on, and where an
instance prevents, what it matches does not pass), or put back **as it
ships**. The agent keeps what is set by sid and gives it to
`suricata-update` every time it runs (`--enable-conf`,
`--disable-conf`, `--drop-conf`, files of the agent's own beside its
other kept files), so a choice holds when the ruleset is fetched again;
a change makes the ruleset again from what was fetched (`--offline`)
and the instances read it. suricata-update's own `enable.conf`,
`disable.conf` and `drop.conf` in `/usr/local/etc/suricata` are not
read. `arcanactl suricata rules q=... only=...` and
`arcanactl suricata rule on=sid,...` do the same.

Each configuration is checked by `suricata -T` before it is run, and
what Suricata refuses is said with its own reason. One exception: the
rules of the ruleset that do not parse with these networks (with
`HOME_NET` `any`, the few that negate it, since `!any` is nothing) are
left out, as Suricata itself does when it runs, and the job counts
them; a rule of the instance's own that does not parse is refused. Its
`classification.config` and `reference.config` are the ones in
`/usr/local/etc/suricata`, or the package's `.sample` of each where a
fresh install has nothing else.
- **Rules of its own**: a rule a line, as Suricata writes them.

Its configuration is checked with `suricata -T` first.

**Prevent, not only detect › Divert port**: Suricata then takes the
packets an ipfw divert rule sends to that port (divert(4)) and drops
what its rules say to drop. Add the rule on the Firewall tab, for
instance `divert 8600 ip from any to any via em0`. While it is stopped,
what is diverted goes nowhere, so the host raises a Critical fault: a
filter that prevents is only as available as Suricata. Until a rule of
ipfw's diverts to its port, nothing is held up and the fault is a
Warning; the host reads ipfw again every ten seconds while the
instance is down. ipfw's divert sockets come with `ipdivert.ko`: the
agent loads it (`kldload ipdivert`) before it starts an instance that
prevents.

A start counts once Suricata's log says its engine started, not when
its pid file appears: Suricata writes that file first, then loads its
rules and opens its capture or divert port, and may still stop there.
If it does, the job fails with the first and the last error it
logged; the ruleset's rules it left out are not counted as why.

## By the API

`POST /api/servers/<id>/security` with `{"what": "proxy" or "ids",
"instances": [...]}`, the whole list of the kind, each instance as the
form has it; `[]` stops them all. What runs, and the forms as saved,
are in `GET /api/servers/<id>/sdwan` (`proxy`, `ids`, `security_proxy`,
`security_ids`, `clamav`).

## Sandboxed programs

FreeBSD's capsicum(4) is a sandbox a process enters for good: from
then on it keeps the descriptors it holds and can name nothing else
on the system. Arcana's programs enter it where their work allows:

- **arcanactl** once the agent is connected: the agent's answers are
  decoded and printed in the sandbox; files named on the command line
  are opened for it by Casper's fileargs service.
- **arcana-enrol** once the console has answered: the answer is
  parsed and the certificate, key and CA are written in the sandbox.
- **jailconf** once `jail.conf` and its includes are read: the edit,
  its check and the write happen in the sandbox.

The agent and the console cannot enter it: their work is running
programs and opening files by name. The agent's helpers for a jail's
network exist to do exactly that inside the jail.
