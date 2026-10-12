# The panel

The panel is laid out as a tree and tabs: what you pick in the tree on
the left decides the page, a host's page has a tab for each part of the
host, and the activity bar along the foot shows every call the panel
makes. This chapter is about what stays the same wherever you are.

## The tree

The tree holds the fleet's own pages (**All hosts**, **Network**,
**Utilization**, **Workflows**, **SD-WAN**), then every host with its
jails, and **Settings** at its foot. **Enrol a host** and **Add a
server** are the two icons at its top.

A host's jails are folded away until you open them with the arrow on
the host, and the browser remembers which are open. When the jails do
not fit in the space under the hosts, each host shows what fits and a
**+N more…** row that shows the rest.

The tree, the activity bar, the list of tasks in it and the service
drawer are resized by dragging their edge; the browser keeps the sizes,
and a double click on the edge goes back to the usual one.

## The address

The address in the browser's bar names what is shown, so a link, a
bookmark, a reload or the browser's back and forward land there:

| Address | Shows |
|---|---|
| `#/` | the fleet |
| `#/hosts/<id>` | a host's summary |
| `#/hosts/<id>/<tab>` | its tab: `jails`, `services`, `network`, `firewall`, `packages`, `storage`, `kernel`, `sysctl`, `processes`, `log`, `jobs` |
| `#/hosts/<id>/jails/<name>` | a jail |
| `#/network`, `#/usage`, `#/workflows`, `#/sdwan`, `#/api` | the fleet's own pages |
| `#/settings/<tab>` | a tab of Settings |

`<id>` is the host's id in `/api/servers`. Opened at one before signing
in, the console goes there after. A host that is no longer there gives
the fleet. Each change is a new entry in the browser's history.

## The console's own host

The first host is the machine the console runs on. Arcana installs the
agent beside the console, so nothing is enrolled: start the agent and
the console adds it by itself, under the host's name, over the agent's
local socket. Until then the empty page says what it waits for: no
agent answering, or one whose socket the console's user may not use.
Taken off the list, the host is not added again; `local_agent` in
`web.conf` names another socket, or none.

That host wears a **console's host** label in the tree and on its page:
besides what every agent does, it builds `arcana-agent` from the
repository for every host (**Build agent here**), and **Update
console** builds and installs the console itself there.

## All hosts

The fleet at a glance: every host as a card with its CPU, memory and
ZFS use and how many of its jails run, and the fleet as a graph from
the console through the hosts to their jails, of what runs (a host's
own Summary has all its jails). Nodes are links; a jail picked in a
graph opens in a box over the page.

## The top bar

Three lights say whether the network, the console and the host picked
answer. The console's light opens the console's own **API**, as
`docs/openapi.yaml` documents it: every route with what it is for, what
it takes and what it answers, by group and searched, and the document
itself one press away for a client generator. **Notify** has this
device told of what ends (below), and **Log out** ends the session.

## The activity bar

Every call to a host is a task in the bar at the foot, with its
workflow as a graph: from the API call through the session check and
the cblink request to each call the agent made on the host. A box
picked in the graph shows its details in a pane beside it, which stays
in view while the graph scrolls.

![A task's graph, its CBOR schema beside it](../img/tour-jails-activity.png)

- **{ } Schema** shows the operation's **CBOR schema**: its request and
  reply as maps keyed by attribute number, in CDDL, with the attribute
  sets they nest, taken from the family's own description
  (`share/arcana/arcana.yaml`).
- **Raw output**, when a program ran, shows its argv, exit status and
  output verbatim.
- Changes are jobs the host runs on its own: the graph fills in stage
  by stage, and a change that cuts the console off still completes.
- An entry still under way has a cross. For a job, it takes the job out
  of the host's queue if it has not started; one that runs is left to
  finish, since stopping a change half way is what would not be safe.
  For a reading, it stops waiting for it.
- A reading that takes long, such as the packages, is asked for once:
  leaving its tab and coming back waits for the same answer.
- A task that **failed** has **Retry**: the same job, sent again to the
  same host.
- A workflow's run is a task too, begun by hand, by the clock or by an
  event, and ended as the run ends, with why when it failed.

**Recent tasks**, along the bottom while the bar is closed, are the
last few, each with its host, how it ended and how long it took; one
picked opens the list at it. Ended tasks are kept in the browser, and
are still there, without their traces, when the page is opened again.

### The queue

**Queue** is on unless you turn it off in that browser. A change then
waits in the activity bar until you press **Run**, and what waits is
sent to each host as one batch, run in order, whichever host is
selected then; a change is taken out of the queue with its cross, and
**As a workflow** makes the queue a workflow. With the queue off, a
change is sent at once.

## Notifications on other devices

A change asked for in one browser is told, when it ends, to every other
browser where **Notify** was allowed, whether or not the console is
open there: the phone hears of what was done at the desk.

It is Web Push. The browser subscribes with its vendor's push service
(Google's for Chrome, Mozilla's for Firefox, Apple's for Safari, where
the console must be installed to the home screen first), and the
console posts the message there, encrypted for that browser alone
(RFC 8291) and signed with the console's own key (VAPID; `vapid.pem` in
the data directory). The push service sees who sends and to whom, not
what. The console must reach those services over HTTPS, and the page
must be served over HTTPS for a browser to subscribe.
**Settings → Notifications** lists the devices, up to 16, and removes
one; a device whose browser dropped the subscription is forgotten by
itself.

## Tables

Every table sorts by the column picked (numbers as numbers, whether
they came as numbers or as text) and is narrowed by the filter above
it. A column is as wide as its border is dragged in the head; a double
click on a border fits it to what is in it again. **⤓** at the right of
a table's head saves its rows as CSV, as they are shown (filtered and
in their order), without the buttons, the file named after the heading
it is under. A box with a mark
before its name (a bridge, how a host is reached) folds when its head
is pressed, and stays as it was left.

## On a phone

The tree of hosts is a drawer that slides in from the left (☰), the top
bar is one row with the rest behind **⋮**, a dialog is a sheet from the
bottom, and a row of choices (the views of a tab, a family, a range of
time) is one line that scrolls sideways; a page's tabs too.

A table on a phone is a card for each row. Its title is the column that
names the row (a process's command, an interface's or a jail's name,
a firewall's part), each other value has its column's name beside it,
and what is done to the row is along the card's foot, behind one **⋯**
when there are more than two. The table's head stays above the cards as
a row of buttons to sort by.

The firewall's parts, a side bar elsewhere, are a strip above its
rules. On the network map the tools are one line along the top and the
legend one along the foot, and **Arrange** puts the hosts on a tall
ellipse the screen holds.

<div class="phones">

![The fleet on a phone](../img/tour-phone-fleet.png)
![The tree, a drawer from the left](../img/phone-tree.png)
![A table on a phone: a card for each row](../img/phone-identities.png)

</div>
