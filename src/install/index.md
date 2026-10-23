# Before you begin

Setting Arcana up takes four steps, each a chapter of this part:

1. **Build or install** Arcana: the whole of it on the host that will
   run the console, and the host's programs alone on every other host.
2. **Start the console** on its host, natively or in a container.
3. **Sign in** the first time, with a one-time token and a security
   key or a passkey.
4. **Add the hosts**: the console's own host joins by itself, and every
   other host joins with a one-time command the console gives you.

## What you need

- **FreeBSD 16.0 or later** on every host: 16-CURRENT until 16.0 is
  released. FreeBSD 15 and older are not supported.
- **A name for the console** that your browser reaches over HTTPS with
  a certificate it trusts, such as one from Let's Encrypt. Security
  keys and passkeys (WebAuthn) work only on such a page, or on
  `localhost`.
- **A security key or a passkey**: a hardware key such as a YubiKey, or
  the passkey of a phone or a computer. Arcana has no passwords.
- **The network between them**: the console reaches each agent on TCP
  port 4310 (or SCTP, once switched). A host reaches the console only
  once, over HTTPS, when it enrols; after that the console calls the
  agents and never the other way round.
