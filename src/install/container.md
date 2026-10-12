# The console in a container

The console is also published as a container image, built on FreeBSD:
`ghcr.io/spmzt/arcana`. It runs Kore unprivileged (uid 4310) on port
8443: HTTPS with an RSA certificate mounted as `console.pem` and
`console.key` in `/usr/local/etc/arcana`, or plain HTTP behind a
reverse proxy that does the HTTPS.

```sh
podman run -d --name arcana -p 8443:8443 \
    -e ARCANA_RP_ID=console.example \
    -v arcana:/var/db/arcana \
    ghcr.io/spmzt/arcana
podman exec arcana cat /var/db/arcana/setup-token
```

| Variable | Default | Is |
|---|---|---|
| `ARCANA_RP_ID` | none | The console's name, as the browser's address bar has it |
| `ARCANA_ORIGIN` | `https://` and the name | The exact origin the browser uses |
| `ARCANA_PORT` | `8443` | The port it listens on |

A mounted `web.conf` or `kore.conf` replaces the one the image makes.
The console's CA lives in the `arcana` volume; to use one of your own,
mount `ca.pem`, `client.pem` and `client.key` into
`/usr/local/etc/arcana`, readable by uid 4310 (see [Certificates of
your own](certificates.md)).

The image carries `io.containers.autoupdate=registry`, so `podman
auto-update` run from cron pulls a newer release and restarts it.
