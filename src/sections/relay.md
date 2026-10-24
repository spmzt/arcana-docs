# FEC relay: UDPspeeder

**FEC relay**, beside Mail among a host's plugin tabs, is UDPspeeder's
`speederv2`, the port `net/udpspeeder`: a relay that carries a tunnel's
UDP (WireGuard's, say) over a lossy link with forward error
correction. For every few packets it sends a few redundant ones, so
that the far end makes a lost packet again instead of waiting for it to
be sent again. A **client** takes the tunnel's plain packets at the
address it listens on and sends them, with the redundant ones, to the
far relay; the **server** there takes them and gives the tunnel back
its plain packets. It runs on the host or in a jail of it, and the
**Where** list picks which. Until it is installed there, the tab offers
**Install udpspeeder**, `pkg install` on the host or `pkg -j` in the
jail.

<div class="freebsd">

**FreeBSD:** the port's rc script runs `speederv2` under
[daemon(8)](https://man.freebsd.org/daemon/8). daemon(8) restarts it
when it exits and sends its lines to
[syslogd(8)](https://man.freebsd.org/syslogd/8) (`daemon.notice`, so
`/var/log/messages`). Its words are `rc.conf`'s `speederv2_flags`, and
`speederv2_enable` starts it at boot.

</div>

## How it is set

**Configure** opens the flags' form:

- the role;
- where it listens and where it sends, each an address and a port;
- the mode: 0 splits packets to fit the MTU and costs less bandwidth,
  1 keeps them whole and costs less latency;
- the MTU;
- the **ratios**: `x:y` sends `y` redundant packets for every `x`, and
  `1:2,2:3,8:4,20:10` sets them by the size of the group the relay
  gathers within its **timeout**;
- how often it **reports** its counters;
- a **fifo**;
- a **key**: a simple XOR, the same at both ends;
- more of speederv2's own options, such as `--jitter`, `--interval`,
  `--queue-len`, `--sock-buf`, `--out-addr` or `--log-level`.

**Write the flags** keeps them in `speederv2_flags`, and the relay is
restarted when it runs. Each word is checked on its own, because
rc.subr hands the flags to a shell: addresses and ports, numbers in
their ranges, ratios as the relay reads them, options from that list,
and no character a shell would act on. The key stays in `rc.conf`. The
tab says only whether one is set; it is never shown, never in a task's
trace (`sysrc`'s command line shows it as `<hidden>`), and kept when
the form leaves it empty.

Both ends need the same mode, key and kind of ratios. The tab sets one
end: open the far host's tab for the other.

## Changing the ratios while it runs

**Ratios**, under how it is set, changes them. A relay that runs with a
fifo is told through it (`fec x:y,...`). It takes the new ratios for
its next packets, and the tunnel stays up. Without a fifo it is
restarted. Either way the new ratios are kept in the flags for the
next start.

## What the FEC costs

With reports on, the relay logs its counters every few seconds: each
way, the packets and bytes it took in plain and those it sent with the
FEC. The tab reads its last two reports from the log and shows, each
way:

- what went in plain, and what went out with the FEC;
- the **overhead**: how much more the FEC sent than the plain traffic,
  in per cent;
- the overhead **lately**, and the plain rate, over the interval
  between the two reports.

**Redundancy by group size** is the table the relay itself logged at
its start: for each group size, the redundant packets it adds. With
`1:2`, one lone packet goes out three times (+200 %); with `20:10`, a
full group costs half again (+50 %). The overhead measured lies between
the two, depending on how many packets the traffic gathers into a
group within the timeout. Its last lines in the log are at the foot of
the tab.

## Safe mode

On the host every change is sent in safe mode. A relay often carries
the very tunnel the console reaches the host by, so a change that cuts
it is undone when the console cannot confirm it. Undoing puts back
`speederv2_flags` and `speederv2_enable` as they were, and the relay
running or stopped as it was. A jail's relay is changed without safe
mode.

From the command line: `arcanactl speeder` reads it, and `arcanactl
speeder conf role=client listen=… remote=… [mode=…] [mtu=…] [fec=…]
[timeout=…] [report=…] [fifo=…] [key=… | nokey] [extra=…]`, `speeder fec
x:y,…` and `speeder enable | disable | start | stop | restart` change
it (`-s` for safe mode, `-j` for a jail).
