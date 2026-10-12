# Workflows

A workflow is a chain of steps the console keeps and runs on several
hosts at once, by hand, at an interval, or on an event.

![A workflow in the editor](../img/sec-workflow-edit.png)

## Steps

A step is one of three things:

- **A job** of any kind, its fields those `share/arcana/jobs.yaml` says
  the kind needs (marked) and uses, with a choice where a field is one
  of a few. The build checks that file against `arcana.yaml`'s kinds of
  job and their attributes, and stops where they differ.
- **A read** of the host (hello, jails, services, stats, events,
  history, packages) whose answer a later step looks at.
- **One of Arcana's own**, from the repository the console builds from
  (`agent_source`):
  - **is its repository newer** asks the step's host for the commit at
    its head (`git ls-remote`, nothing cloned) and answers
    `new_agents`, `new_console` and `new`, each true when the head is
    not what the agents, or the console, were last updated to;
  - **build the agent** has the host build `arcana-agent`, kept by the
    console;
  - **update every host's agent** sends it to every host, each
    restarted with it;
  - **update the console** builds and installs all of Arcana on the
    console's own host, the console restarting once the step has
    ended.

Steps are put in another order by dragging them by their number, or one
earlier with ↑.

## Conditions, failures and values

**Only when…** puts a condition before a step: a read made then, or
what an earlier step answered, a path in it (`jails[name=web].state`,
`host.hostname`) and a test (eq, ne, contains, gt, lt, exists,
missing). A step whose condition fails is skipped.

**When it fails**, the host's run stops, goes on, or goes on at a later
step, those between not run.

A value may be:

| Value | Is |
|---|---|
| `${param.NAME}` | asked for when it runs, its default offered |
| `${host.id}`, `${host.name}` | the host the step runs on |
| `${step.ID.PATH}` | what an earlier step answered |
| `${event.PATH}` | of the event that began the run |

## When it runs

- **By hand**: **Run**, on the hosts picked.
- **Every** so many seconds, a minute to a week. The interval counts
  from when the workflow last ran by it, kept in `every.json` across
  restarts of the console.
- **On** events: those the console sees itself (a host that stopped
  answering, `host-down`; that answers again, `host-up`; a jail whose
  state changed, `jail-state`) and those the host tells (`threshold`,
  `kmsg`, `link` and the rest), each with what it must match
  (`what=mem`). An event's run is on the host it happened on.

The console subscribes to the events of each host a workflow waits on,
so a run begins as soon as the host tells, and a host that goes is
`host-down` at once; what a host said while it was not heard is read
when it answers again. A workflow that runs by itself may hold a step
that destroys (a dataset, an interface, a partition table) only when
**It may destroy, by itself** says so.

## Runs

Each run is listed with what began it and how each host's went. A run
is drawn as its chain, a row for each host, each step coloured by how
it went; a failure that goes on at a later step is drawn as an arrow
under the row from the one to the other, bright when the run took it.
A step picked shows its trace.

![A run, its chain for each host](../img/tour-workflow-run.png)

## Templates

What waits in the queue becomes a workflow with **As a workflow**, and
**From a template…** starts one made already, to be looked over and
saved:

- **Arcana kept up to date** from its repository: every hour the check,
  then the agent built, sent to every host, and the console updated,
  each only when the head is newer;
- **a jail started again** when it stops;
- **packages upgraded** every week;
- **a service restarted** when its host answers again;
- **a plugin's package installed**, the package a parameter.

The console keeps the workflows in `workflows.json`, the last 30 runs
in `runs.json` with each run's traces in a file of its own under
`runs/`; what runs by itself is started by one worker of the console's,
the one holding `workflows.lock`.
