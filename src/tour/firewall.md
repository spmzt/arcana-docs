# The firewall

**Firewall** is the host's `ipfw` ruleset, laid out as a chain of parts
in the order a packet walks them: what goes out first, then what comes
in, before and after NAT, and so on, each part a range of rule numbers.

![The Firewall tab: the chain, part by part](../img/tour-firewall.png)

For each part the tab counts the rules that are in the kernel **now**
and those Arcana **keeps**: the ruleset written down, to be loaded at
boot and by **Apply the kept rules**. You change the kept rules, look at
**What Apply would change**, and apply them in safe mode: if the new
rules cut the console off, the agent puts the old ones back.

On the left: the dynamic states, the kept rules as text, the tables,
NAT and pipes, the packets logged, and **Follow a packet**, which traces
real packets through the rules as the kernel matches them.

<div class="freebsd">

**FreeBSD:** `ipfw(8)` with its sets (the new rules are loaded into a
set of their own and swapped in at once), its tables, `dummynet(4)`
pipes and queues, and in-kernel NAT; a packet is followed with
`dtrace(1)` and ipfw's `rule-matched` probe.

</div>
