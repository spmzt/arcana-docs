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
  then `any` too.
- **The ruleset suricata-update keeps**: Emerging Threats Open, fetched
  by **Fetch the ruleset** above the table, which runs
  `suricata-update` on the host (to `/var/lib/suricata/rules`) and then
  applies the instances again, so that one started without it takes
  it and those reading it read their rules again (`SIGUSR2`). The line
  under the buttons says when it was fetched. Until it is, an instance
  that adds it runs on its own rules, and its job says so.
  `arcanactl suricata update` does the same.

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
filter that prevents is only as available as Suricata.

## By the API

`POST /api/servers/<id>/security` with `{"what": "proxy" or "ids",
"instances": [...]}`, the whole list of the kind, each instance as the
form has it; `[]` stops them all. What runs, and the forms as saved,
are in `GET /api/servers/<id>/sdwan` (`proxy`, `ids`, `security_proxy`,
`security_ids`, `clamav`).
