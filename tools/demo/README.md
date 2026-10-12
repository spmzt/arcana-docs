# The demo fleet

A fleet made for the book's pictures, on the lab VM, so that no picture
shows a real address: three vnet jails, `hq`, `branch-a` and
`branch-b`, each running its own `arcana-agent` over TCP with a
certificate of a CA made for them, numbered from the documentation
ranges (192.0.2.0/24, 198.51.100.0/24, 2001:db8::/32) and 10/8 LANs,
with a shared network, a private circuit, a gif tunnel and a few
configured jails; and a console of its own in `/tmp/adc`.

```sh
mdo -i sh tools/demo/fleet.sh up ../arcana      # as root: the jails, the agents
python3 tools/demo/shots.py ../arcana /tmp/demo-shots
cp /tmp/demo-shots/demo-*.png src/img/ && python3 tools/shrink.py src/img/demo-*.png
mdo -i sh tools/demo/fleet.sh down              # everything taken away
```

`shots.py` signs in with Chromium's virtual security key through
chromedriver, adds the three hosts, waits a minute for their samples,
and photographs each page by its address (`#/network`,
`#/hosts/<id>/processes`, …). Nothing of the host is changed but what
`fleet.sh` makes and takes away again.
