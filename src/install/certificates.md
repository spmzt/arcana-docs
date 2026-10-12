# Certificates of your own

The console and the agents authenticate each other with TLS 1.3 client
and server certificates. By default the console runs a CA of its own:
at its first start it writes `ca.pem`, `ca.key`, `console.pem` and
`console.key` into its data directory, and hosts get their
certificates from it by enrolling. Nothing else is needed.

To use a CA of your own instead, name its certificate and the
console's client certificate in `web.conf`'s `tls { }` block, and add
`ca_key` if the console is still to enrol hosts. With the base system's
`openssl(1)`:

```sh
cd /usr/local/etc/arcana
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
    -keyout ca.key -out ca.pem -days 3650 -subj "/CN=arcana CA" \
    -addext basicConstraints=critical,CA:TRUE

# One per host, named as the console reaches it.
openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
    -keyout host1.key -out host1.csr -subj "/CN=host1.example"
printf 'subjectAltName=DNS:host1.example\nextendedKeyUsage=serverAuth\n' \
    > host1.ext
openssl x509 -req -in host1.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
    -days 825 -extfile host1.ext -out host1.pem

# The console's client certificate the same way, with
# extendedKeyUsage=clientAuth, as client.pem and client.key.
```

```text
tls {
	ca = "/usr/local/etc/arcana/ca.pem";
	ca_key = "/usr/local/etc/arcana/ca.key";
	cert = "/usr/local/etc/arcana/client.pem";
	key = "/usr/local/etc/arcana/client.key";
}
```

Keep `ca.key` off the hosts.
