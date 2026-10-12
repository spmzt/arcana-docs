# Settings

**Settings** is a section of its own, at the foot of the tree, with a
tab for each part: **Look**, **Notifications**, **API tokens**,
**Sign-in keys**, **Console**, **web.conf** and **What's new**. It
opens with no host as well, and its head has the console's version and
the agent's it sends.

![Settings, API tokens](../img/sec-settings-tokens.png)

## Look

The themes. **Graphite**, the default everywhere, is calm: surfaces of
one hue, one blue for what can be acted on, green, amber and red for
how things are, a plain face for reading and the fixed one for what is
read character by character (addresses, keys, code). Slate, Onyx
(black, white and one red) and the light ones, Paper, the warm Sand,
the cool Mist and the green Mint, are drawn the same way in their
colours. The neon ones, Tron, Amber, Matrix and Synth, are the console
on the dark grid it began as: glow, a display face, capitals spaced
out. The one picked takes at once and is kept in that browser.
**Motion** turns the blur and the idle animations off or on.

A theme is a set of colours in `web/style.css`
(`html[data-theme="…"]`): the accent, the surfaces and the text, which
everything else is drawn from.

## Notifications

**Notify**, in the top bar, allows a notification when a task that
took more than ten seconds ends, and has this browser told of changes
made in the others; once allowed, the same button turns them off and
on again for this browser. This tab lists the devices told (see
[Notifications on other devices](panel.md#notifications-on-other-devices))
and removes one.

## API tokens

Read-only tokens for a program to look at the hosts through the API
without a passkey, sent as `Authorization: Bearer arcr_…`. One is made
with a name and its value is shown that once; the console keeps only
its SHA-256, and when it was last used. It reads whatever the API
tells (the hosts, the workflows and their runs, SD-WAN, transfers) and
nothing else: it changes nothing, and does not read the console's
settings, sign-in, push or enrolment. Deleted, it opens nothing at
once.

## Sign-in keys

The security keys and passkeys that may sign in: each can be removed,
and another registered.

## Console

The console's own settings: the name keys show, the release check and
its feed, the `arcana-agent` it sends, and the repository and branch a
host builds it from. They are kept in `settings.json` in the data
directory and take the place of `web.conf`'s; a field put back to
`web.conf`'s value follows it again.

Whoever can sign in can set the repository, and so decides what is
built and sent to every host as root.

## web.conf

The relying party, the origin, the data directory and the certificates,
shown and changed only in `web.conf`: keys are bound to the first two,
and all are read once, at the start.

## What's new

What the repository the console builds from (`agent_source`) has, read
by the host the console runs on (a bare clone without the files, kept
in its build directory) and kept five minutes: the release notes, where
the repository's tags carry messages, else the commit messages, newest
first. Above the version running is what an update brings, the
version's own commit marked; below it, what this console has. The
update boxes show the same. `GET /api/update/notes?component=console|
agent&from=VERSION[&to=VERSION]` gives it as JSON.
