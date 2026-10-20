# Mail: OpenSMTPD

**Mail**, beside BIRD and IPsec among a host's plugin tabs, is
OpenSMTPD, the port `mail/opensmtpd`: on the host itself, or in a jail
of it (a jail with the host's network or one of its own; the tab says
which). Until it is installed anywhere the tab shows how. FreeBSD
itself comes with `sendmail(8)` and `dma(8)` for the host's own mail;
OpenSMTPD serves a domain's. Each change is a task; the tab reads the
host again when it ends.

**FreeBSD:** which program `sendmail(8)` is on a host is
`mailer.conf(5)`'s choice (the tab says what it is); OpenSMTPD's is
`/usr/local/sbin/smtpctl`. Its queue is `/var/spool/smtpd`, its log
`/var/log/maillog` (the Log tab).

## State and queue

The chips say whether it is enabled at boot and running, and, running,
whether each of its parts (the delivery agent, the transfer agent, the
SMTP server) runs or is **paused** (`smtpctl pause`, `resume`).
**Enable and start** enables `smtpd` in `rc.conf` and starts it;
**Stop and disable** asks first.

The **queue** is each envelope waiting (`smtpctl show queue`): who it
is from and to, its state, how often it was tried and what the last
try said. **Try now** schedules one (`smtpctl schedule`), **Remove**
takes it out, never delivered and the sender not told (asked first);
the same for all of them. The **counters** are `smtpctl show stats`.

## Configuration

**Configuration** opens the form `smtpd.conf(5)` is made of. The form
goes to the host as it is; the agent renders the file there, checks it
with `smtpd -n` before it is put in place, and starts smtpd again
where it runs: what runs is what was checked. The form is kept on the
host beside the file, so the tab fills it from there.

- **Listeners**, one a line: where it listens (an interface, `localhost`,
  `all` or an address), then `port N`; `tls`, `tls-require` or `smtps`
  with `pki arcana` (this host's own certificate, the one Arcana's CA
  gave the agent) or a `pki` of the own lines; `auth` (the credentials
  table); `hostname NAME`; `filter A,B`.
- **Local mail**: the domains delivered here; `maildir`, `mbox` or
  `lmtp` with its path; the aliases and virtual users tables.
- **Mail out**: by MX, or by a smart host with its port and protocol
  (`smtp+tls`, `smtps`, `smtp`, `smtp+notls`, `lmtp`), signing in with
  the secrets table's `relay` label; the sender's domain mail goes out
  as.
- **Policy**: the largest message, recipients a message, when the
  sender is warned, reverse DNS checks (`filter check-rdns`,
  `check-fcrdns`), queue compression.
- **Filters**: the filter ports installed (`opensmtpd-filter-rspamd`,
  `-dkimsign`, `-senderscore`), one a line with its arguments.
- **Own lines**: `smtpd.conf(5)` lines the form has not, appended as
  they are; what the form owns (`listen`, `table`, `pki`, `action`,
  `match`, `filter`, `include`) they may not set.

## Tables

Each table is a file of the agent's, read again by smtpd at once
(`smtpctl update table`): **aliases**, **virtuals**, **domains**,
**senders**, and two kept root's alone: **credentials** (a user and a
password a line: the host hashes each with OpenSMTPD's `encrypt` and
keeps the clear one nowhere; the tab shows the users' names) and
**secrets** (the smart host's sign-in, `relay user:password`; the tab
shows the labels).

## Your own smtpd.conf

An smtpd.conf that Arcana's form did not write is yours, and the tab
works with it as it is: **Configuration** shows it as text, **Check**
has the host read it with `smtpd -n`, and **Save and restart smtpd**
puts it in place once smtpd takes it, keeping the one before as
`smtpd.conf.arcana-old`. The form is there on asking, with a warning:
it writes the whole file. The agent refuses to let the form replace a
file it did not write unless that is asked for.

The **Tables** are those your smtpd.conf declares (`table NAME
[BACKEND:]PATH`), at their own paths: `file:` tables by their first
word (an alias without its colon), `passwd:` tables by the name before
the first colon. A user given a password gets it hashed by OpenSMTPD's
`encrypt`, written as the other lines are (a `{SHA512-CRYPT}` scheme
kept), the rest of their line (uid, gid, home, shell) untouched; a new
user gets the fields every other line has alike, or empty ones. Tables
a listener signs users in by, and a relay's sign-in, show names alone.
`db:` tables are made the admin's way (`makemap`) and are not written
here.


every other entry is kept). **Add or change** puts lines in by their
first word: a user there already gets the new password, an alias the
new address, a new one is added, and nothing else is touched. Writing
the whole table at once is folded away under **Replace the whole
table**, since an entry not written there is gone.

```
arcanactl smtpd
arcanactl smtpd conf form.json
arcanactl smtpd table credentials users.txt
arcanactl smtpd entry credentials carol.txt
arcanactl smtpd unentry credentials bob
arcanactl smtpd enable yes
arcanactl smtpd pause mta
arcanactl smtpd remove all
```
