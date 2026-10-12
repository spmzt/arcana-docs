# Jobs and the queue

Everything that changes a host is a **job**. A job is asked of the
host's agent, which queues it, runs it in its own time, keeps its
outcome and its trace, and answers for it later to whoever asks: the
console, `arcanactl`, a workflow. Reads (a list of jails, the routes,
the processes) are not jobs: they are answered at once.

## What a job is

A job has a **kind** (`jail-action`, `if-address`, `route`, `zfs`,
`pkg-install`, and some thirty more) and the fields its kind needs,
which `share/arcana/jobs.yaml` in Arcana's tree lists: what each kind
needs and may use, the values some fields take, and which kinds
destroy. The agent

1. checks the job against its kind before it is queued, refusing what
   is malformed or unsafe (a name that is not a name, a path out of a
   jail, a pool the system lives on);
2. runs the jobs one after another, in the order given, whether or not
   the client stays connected;
3. for a change made in **safe mode**, waits to hear from the client
   again, and undoes the change itself if it does not, within the
   host's rollback timer;
4. keeps the last 64 jobs, each with its trace: every library call,
   system call and program, with what each said.

## From the panel

A button sends a job and the activity bar shows it as it goes. With
**Queue** on, a change waits in the activity bar instead, until **Run**
sends what waits to each host as one batch; **As a workflow** keeps it
to run again. A host's **Jobs** tab lists what it was asked. See [The
panel](../sections/panel.md#the-activity-bar).

## From the API

```sh
curl -s -b cookie -H 'Content-Type: application/json' \
    -d '{"jobs":[{"kind":"if-address","interface":"lo0",
         "address":"10.9.0.6/24","safe":true}]}' \
    https://console.example/api/servers/<id>/jobs
```

answers with each job's id; `GET /api/servers/<id>/jobs/<n>` is its
state and trace, and reading it is what confirms a safe change. Changes
need a signed-in session; a read-only **API token** (Settings → API
tokens, sent as `Authorization: Bearer arcr_…`) reads everything the
API tells and changes nothing. See [The HTTP API](../reference/api.md).

## From a shell

`arcanactl` speaks to an agent directly, over its local socket on the
host or over the network with a certificate:

```sh
arcanactl list                                  # jails, now
arcanactl -s interface lo0 add 10.9.0.6/24      # a job in safe mode, waited for
arcanactl -q route add 10.77.0.0/16 10.0.0.1    # queued, not waited for
arcanactl jobs                                  # what the host was asked
arcanactl job 2                                 # one, with its trace
arcanactl --libxo json hello                    # any answer as JSON
```

See [arcanactl](../reference/arcanactl.md) for every command.

<div class="freebsd">

**FreeBSD:** a job does what the base system's own tools do, by the
same tools: `ifconfig(8)`, `route(8)`, `jail(8)`, `sysrc(8)`,
`service(8)`, `zfs(8)`, `pkg(8)`; the trace says which, with their
arguments, exit status and output.

</div>
