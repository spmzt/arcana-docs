#!/usr/bin/env python3
# share/arcana/arcana.yaml, the agent's protocol, as the book's appendix:
# its operations, each with what it takes and answers, and its
# attribute sets, each attribute with its type and what it is.
#
#	schema2md.py arcana/share/arcana/arcana.yaml > src/reference/schema.md

import sys
import miniyaml


def esc(s):
    return str(s or '').replace('&', '&amp;').replace('<', '&lt;').replace(
        '>', '&gt;')


def cell(s):
    return ' '.join(esc(s).split()).replace('|', '\\|')


def main():
    doc = miniyaml.load(open(sys.argv[1]).read())
    out = ['# The agent\'s protocol', '',
           '*Generated from `share/arcana/arcana.yaml` at every build of '
           'the book: what each side of a cblink session with '
           '`arcana-agent` may send, attribute by attribute.*', '']
    if doc.get('doc'):
        out += [esc(doc['doc'].strip()), '']
    sets = {s['name']: s for s in doc.get('attribute-sets') or []}
    out += ['## Operations', '']
    for op in doc.get('operations') or []:
        # A retired one keeps its command number, nothing more.
        if op.get('retired'):
            continue
        out += ['#### %s' % op['name'], '']
        if op.get('doc'):
            out += [esc(op['doc'].strip()), '']
        for way in ('do', 'dump'):
            d = op.get(way) or {}
            for part in ('request', 'reply'):
                p = d.get(part) or {}
                names = p.get('attributes') or []
                if names:
                    req = set(p.get('required') or [])
                    out.append('- **%s%s**: %s' % (
                        part, ' (dump)' if way == 'dump' else '',
                        ', '.join('[`%s`](#%s-%s)%s' % (
                            n, op.get('attribute-set', 'arcana'), n,
                            ' (required)' if n in req else '')
                            for n in names)))
        out.append('')
    out += ['## Attribute sets', '']
    for name, s in sets.items():
        out += ['### %s' % name, '',
                '| Attribute | Type | Is |', '|---|---|---|']
        for a in s.get('attributes') or []:
            t = a.get('type', '')
            if a.get('enum'):
                t += ' (%s)' % a['enum']
            if a.get('nested-attributes'):
                t += ' of %s' % a['nested-attributes']
            if a.get('multi-attr'):
                t += ', many'
            out.append('| <span id="%s-%s"></span>`%s` | %s | %s |' % (
                name, a['name'], a['name'], cell(t), cell(a.get('doc'))))
        out.append('')
    defs = [d for d in doc.get('definitions') or []
            if d.get('type') == 'enum']
    if defs:
        out += ['## Enumerations', '']
        for d in defs:
            out += ['#### %s' % d['name'], '']
            for e in d.get('entries') or []:
                if isinstance(e, dict):
                    out.append('- `%s`%s' % (e.get('name'), (': ' + cell(
                        e.get('doc'))) if e.get('doc') else ''))
                else:
                    out.append('- `%s`' % e)
            out.append('')
    sys.stdout.write('\n'.join(out) + '\n')


main()
