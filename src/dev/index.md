# Building and testing

## The tree

| Path | Is |
|---|---|
| `usr.sbin/arcana-agent` | the agent, its source laid out by the seven Archives |
| `www/arcana-console` | the console, its own server on libwebsockets |
| `www/arcana-ui` | the panel, C compiled to WebAssembly |
| `usr.sbin/arcanactl`, `usr.sbin/arcana-enrol`, `usr.sbin/jailconf` | the command-line programs |
| `lib/libjailconf` | the in-place editor of `jail.conf` |
| `share/arcana/arcana.yaml` | the agent's protocol, from which both sides' code is generated |
| `share/arcana/jobs.yaml` | the kinds of job, checked against `arcana.yaml` at the build |
| `cblink/` | the protocol's library and generator, a submodule |
| `port/` | Arcana's port |
| `docs/` | the developers' pages: the architecture, the naming, the plans, what is to do |

## Building

Base `make(1)` and `bsd.*.mk`, on FreeBSD 16.0 or later; see [Building
and packages](../install/building.md) for what the console needs. In a
fresh checkout, `make obj` first, so that what is built goes under
`obj/` and not beside the sources.

```sh
git clone --recurse-submodules https://github.com/spmzt/arcana.git
cd arcana
cp config.mk.sample config.mk
make obj && make -j8
```

## The tests

```sh
make check
```

runs every suite with `kyua(1)`, side by side:

| Suite | Tests |
|---|---|
| `lib/libjailconf/tests`, `usr.sbin/jailconf/tests` | the `jail.conf` editor |
| `usr.sbin/arcana-agent/tests` | the agent against stand-ins of every program it runs; as root, `agent_root_test` drives throwaway jails, interfaces and pools of its own |
| `www/arcana-console/tests` | the console against a real agent with stand-ins (`console_test`), and the panel in Chromium driven by chromedriver (`pwa_test`) |

Nothing the tests do touches what is on the host already: a test that
needs a jail, a pool or an interface makes its own and takes it away.
`pwa_test` takes the screenshots this book shows, given a directory:

```sh
cd obj/www/arcana-console/tests
kyua -v test_suites.FreeBSD.shots=/tmp/shots test pwa_test
```

## Contributing

- Every commit to the agent or the console bumps its version
  (`ARCANA_AGENT_VERSION` in `usr.sbin/arcana-agent/agent.h`,
  `ARCW_VERSION` in `www/arcana-console/console.h`), and its subject
  names it: `agent 0.74.0, console 0.130.0: …`. The update boxes find
  what is new by those names.
- An attribute added to `arcana.yaml` goes at the end of its set.
- A kind of job added to `arcana.yaml` is added to `jobs.yaml` too; the
  build stops otherwise.
- What a user reads goes into this book, in
  [spmzt/arcana-docs](https://github.com/spmzt/arcana-docs).

## The plans

What is being built and in what order is in Arcana's `docs/`:
[PLAN-119-SASE.md](https://github.com/spmzt/arcana/blob/main/docs/PLAN-119-SASE.md)
for Mplify 119 and SASE, and
[TODO.md](https://github.com/spmzt/arcana/blob/main/docs/TODO.md) for
the rest. This book's own plan is
[PLAN.md](https://github.com/spmzt/arcana-docs/blob/main/PLAN.md).
