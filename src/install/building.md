# Building and packages

Arcana builds with FreeBSD's own `make(1)` and `bsd.*.mk`. There are
two ways to get it onto a host: the port, or the source tree.

## The port

Arcana's tree carries its ports: `port/sysutils/arcana`, and
`port/www/kore` for the web server the console runs in, built with the
task threads the console needs. Neither is in the FreeBSD ports tree
yet; copy them into your ports tree, or a `poudriere` overlay, and
build as any port:

```sh
cp -R arcana/port/www/kore /usr/ports/www/kore
cp -R arcana/port/sysutils/arcana /usr/ports/sysutils/arcana
cd /usr/ports/sysutils/arcana && make install clean
```

The port's `CONSOLE` option, on by default, builds the console too.
Turned off, only what a host runs is built: `arcana-agent`,
`arcanactl`, `arcana-enrol` and `jailconf`. Hosts that only run an
agent want it off: they then need neither Kore nor Emscripten.

## From the source tree

```sh
git clone --recurse-submodules https://github.com/spmzt/arcana.git
cd arcana
pkg install libcbor                    # what cblink needs
make WITHOUT_CONSOLE=yes               # a host's programs only
make install WITHOUT_CONSOLE=yes
```

The `cblink` library and its code generator come with the tree as a
submodule and are built first, so nothing of them needs installing.

For the console as well, the build needs:

- **Kore 4.3** built with task threads (`TASKS=1`), from the port
  above;
- **Emscripten** (`pkg install emscripten`), which compiles the panel
  from C to WebAssembly;
- **libucl's sources**, which the panel compiles in: the system's
  sources under `/usr/src/contrib/libucl`, or a checkout of libucl
  0.9.4 named with `LIBUCL_SRC`;
- optionally **Chromium** (`pkg install chromium`), whose chromedriver
  drives the browser tests.

```sh
cp config.mk.sample config.mk          # where Kore is, if not /usr/local
make                                   # LIBUCL_SRC=/path without /usr/src
make check                             # the tests, with kyua(1)
make install                           # under /usr/local
```

`make check` skips the tests that need root. Run as root, they drive
throwaway jails and interfaces of their own, never what is already on
the host.
