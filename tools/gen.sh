#!/bin/sh
#
# The chapters made from Arcana's own tree, at every build of the book,
# never committed: the HTTP API from docs/openapi.yaml, the programs'
# manual pages, and the agent's protocol from share/arcana/arcana.yaml.
# Arcana is ./arcana: the workflow's checkout, or a link to one.
#
#	tools/gen.sh && mdbook build

set -eu

top=$(cd "$(dirname "$0")/.." && pwd)
a="$top/arcana"
out="$top/src/reference"
[ -d "$a/share/arcana" ] || { echo "gen.sh: no Arcana at $a" >&2; exit 1; }
mkdir -p "$out"

awk -f "$a/www/arcana-ui/tools/openapi.awk" "$a/docs/openapi.yaml" |
    python3 "$top/tools/openapi2md.py" > "$out/api.md"
PYTHONPATH="$top/tools" python3 "$top/tools/schema2md.py" \
    "$a/share/arcana/arcana.yaml" > "$out/schema.md"

# A manual page in Markdown, its references to the others made links.
for page in usr.sbin/arcanactl/arcanactl.8 usr.sbin/arcana-agent/arcana-agent.8 \
    usr.sbin/arcana-enrol/arcana-enrol.8 usr.sbin/jailconf/jailconf.8 \
    www/arcana-console/arcana-console.8; do
	name=$(basename "$page" .8)
	{
		printf '*Generated from `%s` at every build of the book.*\n\n' "$page"
		mandoc -T markdown "$a/$page" |
		    sed -e '1s/^\(.*\)$/# \1/' \
		    -e 's/^# \([A-Z][A-Z ]*\)$/## \1/'
	} > "$out/$name.md"
done
echo "gen.sh: $(ls "$out" | wc -l | tr -d ' ') chapters in src/reference"
