# Security

**Security**, in the side bar: the plugins that guard a host by
themselves, apart from SD-WAN, a tab each. Choose the host at the top;
each tab says what runs there and what it was given. The plugins are
the host's own: Arcana installs none of them by itself. A tab whose
plugin the host lacks says so, with a button that installs it when you
press it (`pkg install squid`; `c-icap c-icap-modules clamav`;
`clamav`; `suricata`; `snort3`).

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

## Malware

c-icap with ClamAV's module scans what a URL filter fetches before the
client has it, and an object that holds malware is refused. Each filter
that scans has a c-icap of its own on the loopback, started before its
Squid; tick **Scan what it fetches for malware** in the filter's form,
or **Stop scanning** here.

## Signatures

ClamAV knows what its signatures know: freshclam fetches them from
ClamAV's mirrors into `/var/db/clamav`. The tab lists each database
(main, daily, bytecode) with its version, how many signatures, and when
it was built, as the head of its file says; and whether freshclam runs.
**Start freshclam**, or **Look now** while it runs, is the service
`clamav_freshclam` started or restarted: it looks for new signatures as
it starts. Enable it on the Services tab to have it at boot.

## IDS/IPS

Suricata watching interfaces: its alerts are counted in the table and
the latest shown under it, and each is an event in the host's log.

- **Interfaces**: what it watches, by pcap(3).
- **The networks it guards**: the rules' `HOME_NET`; empty, the private
  ranges (RFC 1918).
- **The ruleset suricata-update keeps**: run `suricata-update` on the
  host to fetch it (`/var/lib/suricata/rules/suricata.rules`).
- **Rules of its own**: a rule a line, as Suricata writes them.

Its configuration is checked with `suricata -T` first.

**Prevent, not only detect › Divert port**: Suricata then takes the
packets an ipfw divert rule sends to that port (divert(4)) and drops
what its rules say to drop. Add the rule on the Firewall tab, for
instance `divert 8600 ip from any to any via em0`. While it is stopped,
what is diverted goes nowhere, so the host raises a Critical fault: a
filter that prevents is only as available as Suricata.

## Snort

Snort 3, a host's own IDS/IPS. The snort3 package has no rc.d script,
so Arcana's package brings one, `arcana_snort`: **Start**, **Stop**
and **Restart** at the top are `service arcana_snort`, and the warnings
under them say what keeps Snort from doing what it was told (enabled
but stopped, an interface the host has not, no rules yet, inline with
no ipfw rule diverting to its port).

- **Alerts**: the newest of `alert_json.txt` first, sorted and
  filtered: the rule (gid:sid), its message and class, the addresses
  and ports. **Turn off** turns that rule off.
- **Rules**: **Update** fetches an archive of rules files (or a
  `.rules` file) and takes in every `*.rules` in it: Snort's community
  rules unless another address is given (http, https or `file:///`),
  then the last one. Each rule's chip turns it on or off; that is kept
  by gid:sid and holds across updates, and **As shipped** gives it back
  to the file's own choice. `local.rules`' rules are listed too, as
  that file has them.
- **Settings**: started at boot; **Detects** (watching the interfaces,
  a packet thread each) or **Prevents** (inline: what an ipfw rule
  diverts to its port, for instance `divert 8000 ip from any to any via
  em0` on the Firewall tab, passed back unless a rule drops it); and
  `HOME_NET`, the networks the rules call home. Snort takes rc.conf's
  settings when it starts: restart it after a change.
- **local.rules** and **snort.lua**: your own rules, and Snort's
  configuration, written as typed.

Every change is checked by `snort -T` first: what Snort refuses is not
written, and its own words say why. A running Snort is then told to
read its rules and configuration again (SIGHUP).

<div class="freebsd">

**FreeBSD:** Snort runs by `rc(8)`, its settings `rc.conf`'s
(`arcana_snort_enable`, `_mode`, `_interfaces`, `_divert_port`), set
with `sysrc(8)`; watching is by `bpf(4)` through libpcap, preventing by
`divert(4)`, which `ipfw(8)`'s `divert` rule feeds and the rc.d script
loads (`ipdivert.ko`). The rules are fetched by `libfetch(3)`, the
library `fetch(1)` is made of.

</div>

## By the API

`POST /api/servers/<id>/security` with `{"what": "proxy" or "ids",
"instances": [...]}`, the whole list of the kind, each instance as the
form has it; `[]` stops them all. What runs, and the forms as saved,
are in `GET /api/servers/<id>/sdwan` (`proxy`, `ids`, `security_proxy`,
`security_ids`, `clamav`).

Snort is read by `GET /api/servers/<id>/snort` (`?rules=1` for every
rule), and changed by jobs of kind `snort`: `set`, `conf`, `update` and
`rule`, as in `arcanactl snort`.
