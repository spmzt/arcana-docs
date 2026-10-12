# Packages, storage and the log

## Packages

**Packages** lists what is installed on the host, or in a jail picked
in the first button: each package's version, whether it was asked for
by hand or came as what another needs, its size and its origin in the
ports tree.

![Installed packages](../img/tour-packages.png)

**Upgrades** asks the repository what is newer and upgrades it;
**Install…** installs packages by name; **Clean** empties the package
cache. **IPv4** and **IPv6** make `pkg` use one family alone, for a
host whose other one does not reach the repository.

## Storage

**Storage** is ZFS and the disks under it: **Pools**, **Datasets**,
**Snapshots**, **Disks**, **Mounts** and **Health**.

![A pool with a device taken offline](../img/tour-storage.png)

A pool shows its use and its devices, and the actions ZFS has for it:
scrub, trim, clear errors, add devices, export; a device can be taken
offline, brought back or replaced. Snapshots can be taken, rolled back
to, and sent to another host, the console carrying the stream.

## The log

**Log** reads the host's log files as `syslogd` wrote them, newest
first, and follows them live. **Search** looks through the whole file
on the host, for files too large to send.

![The host's messages, followed live](../img/tour-log.png)

<div class="freebsd">

**FreeBSD:** packages are `pkg(8)`, with `-j` for a jail; storage is
`zpool(8)`, `zfs(8)`, `gpart(8)` and `camcontrol(8)`, a snapshot sent
with `zfs send` and received with `zfs receive`; the log is what
`syslogd(8)` writes under `/var/log`.

</div>
