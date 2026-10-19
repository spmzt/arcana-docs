# System and host security

Two tabs of a host, **System** and **Security**, and what the Storage,
Log, Sysctl and IPsec tabs show beside their own: the system's own
configuration, FreeBSD's files and daemons. A file is written whole
by a task (`sysfile`), one of a fixed table and no other path, and the
daemon that reads it is told; the rest is changed by the task that owns
it (`ntp`, `kmod`, `sysctl`, `service-action`, `service-config`,
`geom`). `arcanactl system` reads it all; `arcanactl sysfile FILE PATH`
writes a file.

## System

- **Time (NTP)**: the servers `ntpd(8)` keeps time by (`ntp.conf`,
  eight at most; ntpd enabled and restarted), and its peers
  (`ntpq -pn`).
- **Linux compatibility**: `linux(4)`, `linux_enable` and its modules
  (linux, linux64, linprocfs, linsysfs, fdescfs). The Linux userland is
  a package or a jail of its own; Arcana installs none.
- **Service jails**: `rc(8)` runs a service in a jail of its own
  (`NAME_svcj`, FreeBSD 15), with the options that give it the network
  (`net_basic`, `net_all`), NFS, routing, SysV IPC and the others.
- **periodic(8)**: each script of the daily, weekly, monthly and
  security runs on or off, its default beside (`periodic.conf`, by
  `sysrc -f`), and `periodic.conf` itself.
- **devd(8)**: rules of its own beside the system's
  (`/usr/local/etc/devd/arcana.conf`), devd restarted.
- **Resource limits (rctl)**: `rctl(8)`'s rules, a jail's, a user's, a
  login class's or a process's, by a form or `rctl.conf` itself; what
  is limited now below it. rctl needs `kern.racct.enable=1`, a tunable
  of the boot: where it is off, a button writes it to
  `/boot/loader.conf.d/arcana.conf` for the next boot.

## Security

- **Audit**: `auditd(8)` on or off; `audit_control` (what is recorded
  of everyone) and `audit_user` (of a user, more or less). The records
  are BSM, in `/var/audit`, read by `praudit(1)`.
- **Kerberos**: `krb5.conf`, the realms and their KDCs.
- **MAC policies**: `mac(4)`'s modules, each loaded or unloaded and
  kept in `kld_list` for the next boot: `mac_bsdextended` (`ugidfw`),
  `mac_portacl`, `mac_seeotheruids`, `mac_partition`, `mac_ifoff`,
  `mac_ntpd`, `mac_do` (`mdo(1)`). MLS, Biba and LOMAC are loaded at
  boot alone, from `loader.conf`.
- **securelevel**: now, and at boot (`kern_securelevel_enable`,
  `kern_securelevel`); raised now too where asked, never lowered while
  the host runs (`security(7)`).

## Beside the other tabs

- **Storage: GEOM**: each class loaded and its providers (`geom CLASS
  status`), the tree (`geom -t`), and a class's command by a form:
  mirror, stripe, concat, raid3, label, nop, multipath, shsec, virstor,
  cache, journal, eli or union, its subcommand one of the class's own
  (`gmirror label`, `gstripe create`, `geli init`...). **GELI**: its
  providers (`geli list`), and the same form, a passphrase given to geli
  by a file of the task's own on the host, never on a command line.
  **devfs**: `devfs.rules`, what each rule set shows of `/dev` (a
  jail's by its `devfs_ruleset`).
- **Log: Configuration**: `syslog.conf` and `newsyslog.conf`, and a
  line that sends the logs to another host (`*.* @host`).
- **Sysctl: Hardening**: the sysctls `security(7)` and hardening guides
  set (users seeing their own processes, no hard links to others'
  files, ASLR, no W^X memory, blackholes for closed ports, no ICMP
  redirects or source routing...), as this kernel has them: now, what
  hardened is, why; each applied, or all that differ, kept in
  `sysctl.conf`.
- **IPsec: setkey**: `ipsec.conf`, `setkey(8)`'s policies and manual
  keys (root's alone), the policies now (`setkey -DP`); IKE
  (strongSwan) makes them for those it knows.
