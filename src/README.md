# Arcana

**The Seven Archives of FreeBSD.** Arcana manages a fleet of FreeBSD
hosts from one panel: an agent on every host, and a console in the
browser that you sign in to with a security key or a passkey.

It shows each host as it is (its jails, services, packages, network
tables, firewall, storage and resource use) and changes it. Every
change runs as a job on the host, finishes even when the console is cut
off, and comes with its trace: the library calls, system calls and
programs it used, with what they said.

This book goes through all of it:

- **Welcome** says what Arcana is and which parts of FreeBSD it is
  made of.
- **Install** sets up a console and adds the first hosts.
- **The first hour** walks through the panel as a new user meets it.
- **The sections** describe each tab, what it shows and what each
  button sends to the host.
- **SD-WAN** builds overlay services the way MEF 70.2 describes them,
  from FreeBSD's own routing tables, firewall and tunnels.
- **Automation**, **Under the hood**, **Operations** and
  **Development** are for running Arcana at scale and working on it.

Throughout, a box like this one names the FreeBSD piece that does the
work:

<div class="freebsd">

**FreeBSD:** a jail is started with `jail(8)` and read with
`libjail(3)`; a change to `rc.conf` is made as `sysrc(8)` makes it.

</div>

Arcana is open source under the BSD-2-Clause licence:
<https://github.com/spmzt/arcana>. The book is its own repository,
<https://github.com/spmzt/arcana-docs>, and each page says at its foot
which commit of Arcana it describes. Parts still being written are
greyed out in the list on the left.
