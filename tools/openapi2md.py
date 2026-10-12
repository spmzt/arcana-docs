#!/usr/bin/env python3
# The console's HTTP API, from docs/openapi.yaml as Arcana's own
# tools/openapi.awk reads it (the JSON its API page shows), grouped as
# the document groups it.
#
#	awk -f arcana/www/arcana-ui/tools/openapi.awk arcana/docs/openapi.yaml |
#	    openapi2md.py > src/reference/api.md

import json
import sys

d = json.load(sys.stdin)
out = ['# The HTTP API', '',
       '*Generated from `docs/openapi.yaml` at every build of the book. '
       'The document itself is served by the console and is one press '
       'away on its API page, for a client generator.*', '']
if d.get('about'):
    out += [d['about'].strip(), '']
groups = {}
for op in d.get('ops', []):
    groups.setdefault(op.get('tag') or 'other', []).append(op)
out += ['| Group | Routes |', '|---|---|']
for tag, ops in groups.items():
    out.append('| [%s](#%s) | %d |' % (tag, tag.lower().replace(' ', '-'),
                                        len(ops)))
out.append('')
for tag, ops in groups.items():
    out += ['## %s' % tag, '']
    for op in ops:
        out += ['#### `%s %s`' % (op['method'].upper(), op['path']), '']
        if op.get('summary'):
            out += ['**%s**%s' % (op['summary'].strip(),
                    ' (no session needed)' if op.get('open') else ''), '']
        if op.get('about'):
            out += [op['about'].strip(), '']
        if op.get('params'):
            out += ['Parameters: ' + ', '.join('`%s`' % p
                                               for p in op['params']), '']
        if op.get('codes'):
            out += ['Answers: ' + ', '.join(op['codes']), '']
sys.stdout.write('\n'.join(out) + '\n')
