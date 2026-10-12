# Plan: the book, on GitHub Pages

Written 2026-10-11, in Arcana's tree; moved here 2026-10-12, when B-1 began. Confirmed: arcana-docs, built daily from arcana's main.

## What it is

A manual that reads as a book, kept in its own repository,
https://github.com/spmzt/arcana-docs, and published at
https://spmzt.github.io/arcana-docs/ by GitHub Actions. The panel
tutorial is its heart; the reference chapters, the SD-WAN part, the
architecture and the developer's pages are around it. It says,
chapter by chapter, which FreeBSD piece does the work.

Revised 2026-10-12: the book and its screenshots go in arcana-docs,
not in this repository, so that Arcana's own history stays light.

## The tool

mdBook: one binary, chapters in Markdown, a sidebar of parts and
chapters, search, light and dark themes, a print view, `{{#include}}`
of files so a chapter can carry a real configuration or a man page
section without copying it. Alternatives weighed: MkDocs Material
(Python, heavier, more a site than a book), Docusaurus (Node, a site).
mdBook is what "a complete book" asks for and the lightest to run in
CI; nothing of it is needed on the VM or a host to build Arcana.

## Where it lives

- **arcana-docs** (cloned at ~/code/arcana-docs): `book.toml`,
  `src/SUMMARY.md`, the chapters under `src/`, the screenshots under
  `src/img/`, the generators under `tools/`, and
  `.github/workflows/pages.yml`. This plan moves there as its
  README's companion once B-1 begins.
- **arcana** keeps what a developer of Arcana reads beside the code:
  README.md (short, linking to the book), TODO.md, the plans,
  ARCHITECTURE.md, NAMING.md, TOOLS.md, UPDATING.md. USING.md's
  content moves into the book's tour and sections and USING.md is
  then a pointer to the book. Nothing heavy is added here.
- **How the book reads Arcana**: its workflow checks out
  spmzt/arcana (public) at main beside the book, and the chapters
  include from that checkout (a real configuration, the man page,
  the developer's pages) instead of copies. The footer of every page
  names the Arcana commit it was built from.
- **Screenshots**: the browser test already takes them on the VM
  (pwa_test with the `shots` variable). `tools/shots.sh` in
  arcana-docs, run on the VM, copies a named list from that
  directory into `src/img/`, shrunk losslessly, and they are
  committed in arcana-docs. CI runs on GitHub's Linux runners and
  cannot drive the FreeBSD lab. A chapter never shows a picture the
  test did not take.
- **Generated chapters**: the HTTP API from `docs/openapi.yaml`, the
  arcanactl reference from `usr.sbin/arcanactl/arcanactl.8` (mandoc
  to Markdown), the schema from `share/arcana/arcana.yaml`, made by
  `tools/gen.sh` in the book's workflow from the checkout, at every
  build: they cannot drift from the code, and nothing generated is
  committed.
- **When it is built**: on a push to arcana-docs, by hand (workflow
  dispatch), and once a day from arcana's main, so that the generated
  chapters follow the code without a token between the two
  repositories. (A push to arcana could trigger it at once instead,
  with a repository_dispatch and a token kept as arcana's secret: only
  if you want that.) A pull request builds the book and keeps it as
  an artifact without deploying. The link check (lychee, over the built pages)
  runs on every build.
- Once, by hand, on arcana-docs: Settings, Pages, source "GitHub
  Actions".

## The parts and chapters

1. **Welcome.** What Arcana is; why FreeBSD, and what of it the book
   meets (jails and vnet, FIBs, ipfw and dummynet, netgraph, ZFS, the
   base system's IPsec, WireGuard, Unbound); what the console, the
   agent and arcanactl are; a screenshot of the fleet.
2. **Install.** The package and the port; the console on a host; the
   first sign-in with a passkey; enrolling an agent, by the console or
   by hand; updating (from UPDATING.md); what runs as root and what
   does not.
3. **The first hour: a tour.** The panel chapter by chapter as a
   first user meets it: the fleet and a host; its summary; jails, one
   made and started; services; the network tabs; the firewall's kept
   rules and a change in safe mode; packages; storage; the log; jobs,
   the queue and a workflow; the phone. Every step a screenshot and the
   job it sends.
4. **The sections, one by one.** The reference of each tab of a host
   (from USING.md, re-cut with pictures): what is shown, what each
   button sends, what is kept where on the host; the plugins
   (WireGuard, IPsec, BIRD); the network map; Utilization; Workflows;
   Settings.
5. **SD-WAN.** MEF 70.2 in a page; the document (underlays, edges,
   services, zones, flows, policies); a tutorial with two edges from
   the example to a working service; steering and the probes;
   breakout, bandwidth, egress; routing at the UNI; what each FreeBSD
   piece does in it (setfib, ipfw sets and tables, dummynet, gre and
   the rest, strongSwan, BIRD); the Paths and Dashboard pages;
   troubleshooting; what Mplify 119 and SASE will add (from the plan).
6. **Automation.** Jobs and what a job is; the queue; workflows and
   their runs; API tokens; the HTTP API (the generated reference);
   arcanactl (the generated reference); cblink in a page.
7. **Under the hood.** Architecture (ARCHITECTURE.md); the agent's
   archives and naming (NAMING.md); how a change is made, kept and
   taken back; events and the activity bar; security: passkeys, the
   origin, tokens, what the agent refuses.
8. **Operations.** Backups of the console's data; moving a console;
   a host that cannot be reached; reading traces; known limits
   (TODO.md's verified-for-real list).
9. **Development.** Building; the tests and the lab (TOOLS.md, the
   VM, make check); contributing; the plans (PLAN-119-SASE.md).
10. **Appendix.** The schema; the glossary of MEF and FreeBSD terms;
    the licence and the acknowledgement.

## The tasks

- **B-1 The skeleton and the first deploy.** (Done 2026-10-12.) In arcana-docs:
  book.toml, SUMMARY.md, parts 1 and 2 written, the workflow with the
  checkout of arcana, the daily build and the link check (lychee); the Pages
  setting. In arcana: README pointing to the book. Done when the URL
  serves the two parts.
- **B-2 The tour.** (Done 2026-10-12.) `tools/shots.sh` with the named list; part 3
  written from the browser test's path through the panel, a picture
  a step. Done when every step shows its picture.
- **B-3 The sections.** (Done 2026-10-12.) Part 4 from USING.md, re-cut per tab with
  pictures; USING.md in arcana made a pointer to the book.
- **B-4 SD-WAN.** (Done 2026-10-12.) Part 5, with the lab's own screenshots and the
  example document walked through.
- **B-5 The generated references.** (Done 2026-10-12.) `tools/gen.sh` for the API, the
  CLI and the schema, run at every build from arcana's checkout;
  part 6.
- **B-6 Under the hood, operations, development.** Parts 7 to 9 from
  the existing docs, re-cut.
- **B-7 Polish.** A landing page; the book's theme matched to the
  console's Graphite; the phone screenshots beside the desktop ones;
  a printable PDF of the whole (mdbook-pdf) attached to releases.

B-1 is a day; B-2 to B-4 are the bulk, each a few days with the
screenshots; B-5 to B-7 a few days together. It goes after, or
beside, the SD-WAN and UX tasks as you say.

## What to confirm

- The book in spmzt/arcana-docs, at https://spmzt.github.io/arcana-docs/,
  deployed by its own Actions; screenshots committed there.
- Built daily from arcana's main (no token), or at once on every push
  to arcana (a token as arcana's secret).
- USING.md's content moved to the book; the developer's pages stay in
  arcana and are included by the book from its checkout.
- The Pages setting on arcana-docs, and the site public.
