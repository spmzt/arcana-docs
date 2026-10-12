# The book of Arcana

The manual of [Arcana](https://github.com/spmzt/arcana), the FreeBSD
fleet manager, written as a book with [mdBook](https://rust-lang.github.io/mdBook/)
and published at <https://spmzt.github.io/arcana-docs/>.

It is kept apart from Arcana's tree so that the screenshots and the
book's history do not weigh on the code's. The book reads Arcana
itself: its workflow checks out `spmzt/arcana` beside it, the chapters
include real files from there (`{{#include ../../arcana/…}}`), and
every page names the Arcana commit it was built from.

## Building it

```sh
git clone https://github.com/spmzt/arcana-docs.git
git clone --depth 1 https://github.com/spmzt/arcana.git arcana-docs/arcana
cd arcana-docs
mdbook serve            # http://localhost:3000
```

A checkout of Arcana elsewhere works as well: `ln -s ../arcana arcana`.

## When it is published

`.github/workflows/pages.yml` builds the book, checks its links with
lychee, and deploys it to GitHub Pages:

- on every push to `main`;
- once a day, so that it follows Arcana's `main`;
- by hand, from the Actions tab.

A pull request builds it and keeps the result as an artifact, without
deploying.

## Layout

| Path | Is |
|---|---|
| `book.toml` | mdBook's configuration |
| `src/SUMMARY.md` | the parts and chapters |
| `src/` | the chapters, one Markdown file each |
| `src/img/` | screenshots, taken by Arcana's browser test on the lab VM |
| `theme/` | what the book adds to mdBook's look: the footer naming Arcana's commit |
| `PLAN.md` | the plan of the book and its tasks |

Text under the BSD-2-Clause licence, as Arcana.
