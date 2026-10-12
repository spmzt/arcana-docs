# Running a console

## Backups

Everything the console knows is in its data directory,
`/var/db/arcana` (`datadir` in `web.conf`), readable by the console's
user alone:

| File | Holds |
|---|---|
| `ca.pem`, `ca.key`, `console.pem`, `console.key` | the console's own CA and its client certificate, when it runs one |
| `credentials.json` | the security keys and passkeys that may sign in |
| `servers.json` | the hosts, where each is reached, each host's rollback timer |
| `settings.json` | what Settings changed over `web.conf` |
| `tokens.json` | the read-only API tokens, as their SHA-256 |
| `push.json`, `vapid.pem` | the devices told of what ends, and the key the console signs with |
| `workflows.json`, `runs.json`, `runs/`, `every.json` | the workflows, their last runs and traces, when each last ran by its interval |
| `sdwan.json`, `sdwan-state.json`, `sdwan-lists.json` | the SD-WAN services, what was made on the edges, the lists and feeds |
| `transfers.json` | the snapshots sent between hosts |
| `arcana-source.json` | what was last built and updated from the repository |
| `agent/` | the agent a host built, which the console sends |

Back it up whole, with the console stopped or from a ZFS snapshot of
the dataset it is on:

```sh
zfs snapshot zroot/var/db/arcana@$(date +%Y%m%d)
```

The agents keep their own state on their hosts (their certificates in
`/usr/local/etc/arcana`, the samples and probes beside them, the jobs in
memory): a console restored from a backup finds them as they are.

## Moving a console

1. Stop the console, and copy the data directory and
   `/usr/local/etc/arcana` to the new host, keeping their owners and
   modes.
2. Give the new host the console's name. Security keys are bound to
   `rp_id`, so the name in the address bar must stay the same; with a
   new name, remove `credentials.json` and register again with the new
   setup token.
3. Start it. The agents need nothing: they authenticate the console by
   its client certificate, which moved with it.

## A host that cannot be reached

The tree marks it, and its page says why: the connection refused, the
certificate refused, nothing answering. Look, in order, at:

- whether `arcana_agent` runs on the host (`service arcana_agent
  status`, its log in `/var/log/messages`);
- whether it listens where the console calls it (`arcanactl hello` on
  the host, `sockstat -l | grep 4310`);
- the firewall between them, and the host's own;
- the clocks: TLS refuses a certificate not yet valid;
- for a host reached over SCTP, **Go back to TCP** on its summary.

A change made in safe mode that cut the host off is undone by the host
within its rollback timer; wait that long before anything else.

## Reading a trace

Every task in the activity bar has its trace: the API call, the session
check, the cblink request, then each step the agent made, nested as
they were made. A step's kind says what it was (a library call, a
system call, a program, the agent's own work), its time how long it
took, and its colour how it ended. A program's step has its arguments,
exit status and output; **Raw output** has them verbatim. What failed
is the first red step from the top; what it said is in its detail.

## Known limits

What is known not to work, or has never been run for real, is kept in
Arcana's [docs/TODO.md](https://github.com/spmzt/arcana/blob/main/docs/TODO.md),
under *Not yet verified* and *Known limits*.
