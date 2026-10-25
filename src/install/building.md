# Building and packages

Arcana builds with FreeBSD's own `make(1)` and `bsd.*.mk`. There are
two ways to get it onto a host: the port, or the source tree.

## The port

Arcana's tree carries its port, `port/sysutils/arcana`. It is not in
the FreeBSD ports tree yet; copy it into your ports tree, or a
`poudriere` overlay, and build it as any port:

```sh
cp -R arcana/port/sysutils/arcana /usr/ports/sysutils/arcana
cd /usr/ports/sysutils/arcana && make install clean
```

The port's `CONSOLE` option, on by default, builds the console too.
Turned off, only what a host runs is built: `arcana-agent`,
`arcanactl`, `arcana-enrol` and `jailconf`. Hosts that only run an
agent want it off: they then need neither libwebsockets nor Emscripten.

## From the source tree

```sh
git clone --recurse-submodules https://github.com/spmzt/arcana.git
cd arcana
make check-deps                        # what is needed, and what is missing
make install-missing-packages          # as root: pkg install what is missing
make                                   # checks the same first
make check                             # the tests, with kyua(1)
make install                           # under /usr/local
```

`make check-deps` asks pkg(8) what is installed, and lists what is
missing as packages; `make install-missing-packages` installs them with
`pkg install` (add `WITH_TEST_TOOLS=yes` for the tests' tools too).
`make` itself checks first, and stops with that list rather than a
compiler's error. A host that runs only jails needs less: `make
WITHOUT_CONSOLE=yes` and `make install WITHOUT_CONSOLE=yes`.

The `cblink` library and its code generator come with the tree as a
submodule and are built first, so nothing of them needs installing.
What the build needs:

- **libcbor** (`devel/libcbor`), for cblink, and **libyang 3**
  (`net/libyang3`), which its code generator reads the wire's YANG
  modules with, to build only;
- for the console:
  - **libwebsockets** (`net/libwebsockets`), the console's HTTP and
    WebSocket server. A copy elsewhere is named in `config.mk`
    (`config.mk.sample` says how);
  - **Emscripten** (`devel/emscripten`), which compiles the panel from C
    to WebAssembly;
  - the sources of **libucl** and **libyaml**, which the panel compiles
    in (WebAssembly needs their sources, not a built library): the
    system's, under `/usr/src/contrib`. Without `/usr/src`, they come
    from pkgbase's `FreeBSD-src` package, which `make
    install-missing-packages` lists, or from trees named with
    `LIBUCL_SRC` and `LIBYAML_SRC` (libucl 0.9.4 and libyaml 0.2.5, the
    releases base imports, which the port fetches);
- for the tests: **git**, **curl**, **python3**, and **Chromium**,
  whose chromedriver drives the browser tests.

<div class="freebsd">

**FreeBSD:** what is installed is pkg(8)'s to say (`pkg info -e`), and
pkgbase installs the system's sources as a package like any other.

</div>

`make check` skips the tests that need root. Run as root, they drive
throwaway jails and interfaces of their own, never what is already on
the host.
