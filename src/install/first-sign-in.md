# The first sign-in

Arcana has no passwords. You sign in with a **security key** (a
hardware key) or a **passkey** (kept by a phone, a computer or a
password manager), through WebAuthn.

## The first key

With no key registered yet, the console writes a one-time token to
`/var/db/arcana/setup-token` and says so in its log. Open the console
in the browser, paste the token, and touch your key. That registers the
key and signs you in, and the token is gone.

Register a second key straight away, from **Keys**, so that losing one
does not lock you out.

## A phone's passkey

A phone works as a second key. Open the console on the phone, sign in
once with the security key (Chrome can use it over USB or NFC, or the
passkey of another device nearby), and register from **Keys**. From
then on **Use a passkey** on the sign-in page uses it, on the phone or,
through the phone, on any browser.

Opened on a phone or a tablet, the console offers to install itself as
an app: with the browser's own prompt on Android, and by saying where
to tap in Safari on iOS and in Firefox.

## When a key is refused

A key signs for the name it was registered under and no other.
`rp_id` in `web.conf` must be the name in the browser's address bar (or
a parent domain of it), `origin` the exact origin, and the page served
over HTTPS unless it is on `localhost`. Anywhere else the browser
refuses with "SecurityError" ("The operation is insecure" in Firefox),
and the sign-in page says which address the console is set up for.

After changing `rp_id`, the keys registered under the old name no
longer work: remove `/var/db/arcana/credentials.json`, restart the
console, and register again with the new setup token.
