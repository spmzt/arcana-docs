#!/bin/sh
#
# The book's screenshots, from a run of Arcana's browser test.  On the
# lab VM, in Arcana's build tree:
#
#	cd obj/www/arcana-console/tests
#	kyua -v test_suites.FreeBSD.shots=/tmp/shots ... test pwa_test
#
# then, here:
#
#	tools/shots.sh /tmp/shots
#
# copies each picture tools/shots.list names into src/img/ under its
# book name, made smaller without loss.  A name the run did not take
# stops it: a chapter never shows a picture the test did not take.

set -eu

from=${1:?usage: tools/shots.sh directory-of-the-test-s-shots}
top=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$top/src/img"
grep -v '^#' "$top/tools/shots.list" | while read -r test book; do
	[ -n "$test" ] || continue
	if [ ! -f "$from/$test.png" ]; then
		echo "shots.sh: $from/$test.png: not taken" >&2
		exit 1
	fi
	cp "$from/$test.png" "$top/src/img/$book.png"
	python3 "$top/tools/shrink.py" "$top/src/img/$book.png"
done
