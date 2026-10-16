# SSH

The **SSH** tab is the base system's `sshd(8)` on a host, or in one of
its running jails, picked at its left. It shows five things:

- what sshd is set to, as `sshd -T` reports it;
- its banner;
- the CA keys whose user certificates it takes;
- its host keys and their certificates;
- who may sign in, and with which keys.

![sshd's settings](../img/sec-ssh.png)

**FreeBSD:** every change goes into `/etc/ssh/sshd_config` the same
way. `sshd -t` reads the new file first; what it refuses is not put in
place, and its message is shown. The file as it was is kept beside it
(`sshd_config.arcana-before`), and then `service sshd onereload` runs
(`reload` alone does nothing for an sshd not enabled in `rc.conf`).
Through the API or `arcanactl -s`, a change can be made in safe mode:
unless it is confirmed, the file before it is put back.

## Settings

Each setting shows its value; **✎** changes it:

- `PermitRootLogin`, `PasswordAuthentication`,
  `KbdInteractiveAuthentication`, `PubkeyAuthentication` and
  `X11Forwarding`, chosen from the values sshd takes;
- `MaxAuthTries` and `Port`, numbers (several ports, a space between
  them);
- `AllowUsers`, `AllowGroups`, `DenyUsers` and `DenyGroups`, names or
  patterns (`user@host` too). Leaving them empty takes the line away.

The line goes before the first `Match` block, so it holds for everyone.
The `Match` blocks themselves are left as they are. If `sshd -T` cannot
run (for example without host keys), the page shows what the file says
instead, and says so.

## Banner

The banner is what a client sees before it signs in. It is kept as
`/etc/ssh/banner` and named by `Banner`. Saving it empty sets
`Banner none`.

## User certificates

A user can sign in with a certificate instead of a key listed for them:
`ssh-keygen -s ca -I id -n name user.pub` signs their public key with
your certificate authority's key, and the certificate's principals are
the names they may sign in as. The table lists the CA public keys sshd
trusts for that (type, size, fingerprint and comment). The box below it
holds them, one a line, comments with `#`. Saving it writes
`/etc/ssh/trusted_user_ca_keys` and names it by `TrustedUserCAKeys`.
Saving it empty takes the line away, and no certificate is taken.
Only public keys go there: a certificate or a line with options is
refused, and so is a private key, which never leaves the page.

## Host keys

![Host keys, a certificate, and who signs in](../img/sec-ssh-keys.png)

Each host key shows its type, size and fingerprint (`SHA256:`, as
`ssh-keygen -l` prints it). The agent reads keys and certificates
itself; it does not run ssh-keygen to read them. A host key that has a
certificate shows:

- the fingerprint of the CA key that signed it;
- the names it is valid for;
- the day it ends;
- *not used*, if no `HostCertificate` line names it.

**Sign with a CA key…** signs every host key with your certificate
authority's private key, `ssh-keygen -s … -h` for 52 weeks, for the
principals you give: the names clients reach the host by, one at least,
since a host certificate for no name is good for any. Each
certificate is written beside its key and named by `HostCertificate`.
Clients then trust the host through a `@cert-authority` line in their
`known_hosts`, instead of each host's key.

### Where the CA's private key is, and is not

**Arcana keeps the CA's private key nowhere.** It is given each time
you sign, and its way is this:

1. **The page.** You paste it into the box; it is sent once, in the
   body of one HTTPS request, and the box is closed. A browser cannot
   be made to forget a string at once: close the tab when you are done
   on a machine you share.
2. **The console.** The request is read into memory (Kore keeps bodies
   in memory, `http_body_disk_offload` off), parsed, and put into a
   job for the host. The raw body, Kore's copy of it, the parsed JSON's
   copy and the job's are each overwritten with zeros
   (`explicit_bzero(3)`) as soon as they are no longer needed. It is
   not in the console's log, its audit trail (which records *ssh sign*
   and who did it) or its store.
3. **To the host.** Over the console's mutual-TLS connection to the
   agent, as every job.
4. **The agent.** The job runs on the host itself, never in a jail,
   whose root could read it there. The key is never written to a file:
   on ZFS a block written over is a new block, and the old one stays
   until it is freed, or for good in a snapshot. Instead the agent
   starts an `ssh-agent(1)` of its own, its socket in a directory of
   `/tmp` that only root can enter, gives it the key through
   `ssh-add -`'s standard input (a pipe), and signs with
   `ssh-keygen -s ca.pub -U`, which asks that agent to sign: only the
   CA's public key is in the directory. The agent holds the key for two
   minutes at most (`ssh-agent -t 120`) and is ended as soon as the
   keys are signed; the job's copy of the key is overwritten when the
   job ends, and the job's trace never had it. For a jail, only its
   public host keys come out and only their certificates go in.

What is left to trust: root on the host while it signs (it could read
any process's memory), and the console's host while the request passes.
A CA key you care for is best kept offline or in a hardware token; sign
with it from a host you trust, or sign the host keys yourself with
`ssh-keygen -s` and give the console only the certificates.

## Who signs in

The users who may sign in are root and the people (uid 1000 and up)
whose shell lets them in. For each one the tab shows their keys file
(`AuthorizedKeysFile`) and its keys: type, fingerprint, comment and
options.

- **+ key** adds one line of `authorized_keys`, options first if it has
  any. The `.ssh` directory and the file are made if missing, belong to
  the user, and are theirs alone (0700 and 0600). A key they have
  already is refused.
- **×** takes a key out, by its fingerprint.

The directory is opened beneath the user's home and never through a
link, so a `.ssh` that is a link to somewhere else is refused.

From the command line: `arcanactl [-s] [-j jail] sshd [list] | banner
file | set Setting [value ...] | authorize user keyfile | unauthorize
user fingerprint | sign ca-key-file [principal ...] | user-cas file`
(`-` for none).
