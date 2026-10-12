# cblink in a page

The console and the agents speak **cblink**: a small protocol of
requests, replies and notifications, written for Arcana and kept in a
repository of its own (`spmzt/cblink`), a submodule of Arcana's tree.

- **Transports**: TCP, SCTP or a local (`AF_UNIX`) socket; on the
  network always TLS 1.3 with a certificate on both sides.
- **Messages**: CBOR, each a map of numbered attributes. A family's
  operations and attributes are described once, in YAML
  (`share/arcana/arcana.yaml` for Arcana's), from which `cblink-gen`
  writes both sides' C: structures, the checks of every attribute's
  type and length, client calls and server glue.
- **Requests** carry a number and are answered in any order; several
  may be in flight on one connection. Over SCTP each goes on a stream
  of its own, so a slow answer holds up no other.
- **Streams**: an answer too large for one message (the routes of a
  full BGP table, the kernel's state) comes in parts, flow-controlled:
  the agent sends a part only while the reader has room for it.
- **Notifications**: a client subscribes, and the agent tells it of
  events as they happen; the console's workflows and the page's live
  views are made of them.

The activity bar shows each request as cblink sent it, and beside it
the operation's **CBOR schema**: its request and reply in CDDL, from
the same YAML. The whole of it is [the agent's
protocol](../reference/schema.md).
