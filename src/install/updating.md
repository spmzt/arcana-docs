# Updating

The console asks GitHub's release feed every six hours and shows a
banner when a newer version is out (`update_check = false` in
`web.conf` turns that off). The box that opens from the banner, and
from **Update** on **Devices** and **Update console** in **Settings**,
lists what is new: the release notes, or the commit messages where
there are none. **Settings**, **Update** gathers both: the console's
update and the agents'.

## The console

The console runs unprivileged and does not replace itself:

- **natively**, update with `pkg upgrade arcana` or `make install` from
  a newer tree, then `service arcana_console restart`;
- **in a container**, `podman auto-update` pulls the newer image;
- **from its repository**: with `agent_source` set in **Settings**,
  **Settings**, **Update** has **Update console**. The agent on the
  console's own host builds all of Arcana as `nobody`, installs it as
  root, and restarts the console and then itself. The page reconnects
  by itself, still signed in.

The page and the installed app take a newer version by themselves the
next time they come into view.

## The agents

The console marks every host whose agent is not the build it has, on
**Devices**: **Update** in its row, or **Update N agents** at the top
(also on the fleet's page and in **Settings**, **Update**), sends it. Builds are told apart by their SHA-256, so a rebuild
of the same version counts as another. Each host

1. checks the program against the SHA-256 sent with it,
2. runs it once with `-V`, so a program built for another machine or
   FreeBSD version is dropped rather than installed,
3. puts it in place of the old one, kept as `arcana-agent.old`, and
   restarts its service.

A host can also **Build** (its row on **Devices**) from the repository
named in **Settings**, and the console then sends that build to the
others.
Hosts that differ from the console's machine (another architecture or
FreeBSD version) are updated with `pkg upgrade arcana` instead, which
their Packages tab can do.

The program travels compressed (gzip) to an agent of 0.235.0 or later,
whose hello says `gzip-update`, and is inflated there before the checks
above; an older agent is sent it as it is, which it takes up to 6 MiB.
So a host whose agent is older than 0.235.0 is updated to a release
small enough for that first; the console says so when one is too big.

If an update goes wrong on a host, put `arcana-agent.old` back and
restart the service.

## Versions

The agent and the console each have a version, and every change to one
bumps it. A host's header shows its agent's version; the console's is
beside its name at the top of the panel.

Update the agents before the console when a console's release says it
needs them newer; until they are, what needs them stops with the
agent's refusal, nothing else changed. So far:

| Console | Needs agents | For |
|---|---|---|
| 0.317.0 | 0.211.0 | SD-WAN: a zone's URL filtering, middlebox or malware scanning (the proxy's lists, a file each) |
| 0.330.0 | 0.232.0 | jobs, storage, services, jails and packages through YANG: an older agent answers hello and takes agent-update, the rest waits for its update |
