# The part of YAML Arcana's own files are written in: block maps and
# lists by indentation, "|" and ">" blocks, quoted and plain scalars,
# and [a, b] lists on one line.  Python's own library only, so the book
# builds with nothing installed.

def _scalar(s):
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        return [_scalar(x) for x in inner.split(',')] if inner else []
    if len(s) >= 2 and s[0] == s[-1] and s[0] in '"\'':
        return s[1:-1]
    if s in ('true', 'false'):
        return s == 'true'
    if s in ('null', '~', ''):
        return None
    try:
        return int(s)
    except ValueError:
        return s


def _strip_comment(s):
    q = None
    for i, c in enumerate(s):
        if q:
            if c == q:
                q = None
        elif c in '"\'':
            q = c
        elif c == '#' and (i == 0 or s[i - 1] in ' \t'):
            return s[:i].rstrip()
    return s.rstrip()


def load(text):
    lines = []
    for raw in text.split('\n'):
        if raw.strip() in ('---', '...'):
            continue
        lines.append(raw.rstrip('\n'))
    pos = [0]

    def indent(l):
        return len(l) - len(l.lstrip(' '))

    def skip():
        while pos[0] < len(lines):
            l = lines[pos[0]]
            if l.strip() == '' or l.lstrip().startswith('#'):
                pos[0] += 1
            else:
                return
        return

    def block(ind, folded):
        out = []
        while pos[0] < len(lines):
            l = lines[pos[0]]
            if l.strip() and indent(l) < ind:
                break
            out.append(l[ind:] if l.strip() else '')
            pos[0] += 1
        while out and out[-1] == '':
            out.pop()
        return (' '.join(out) if folded else '\n'.join(out)) + '\n'

    def value_after(rest, ind):
        rest = _strip_comment(rest).strip()
        if rest in ('|', '|-', '>', '>-'):
            skip()
            if pos[0] >= len(lines):
                return ''
            return block(indent(lines[pos[0]]), rest.startswith('>'))
        if rest == '':
            skip()
            if pos[0] < len(lines) and indent(lines[pos[0]]) > ind or \
               (pos[0] < len(lines) and indent(lines[pos[0]]) == ind and
                    lines[pos[0]].lstrip().startswith('- ')):
                return node(indent(lines[pos[0]]))
            return None
        return _scalar(rest)

    def node(ind):
        skip()
        if pos[0] >= len(lines):
            return None
        if lines[pos[0]].lstrip().startswith('- ') or \
           lines[pos[0]].strip() == '-':
            return seq(ind)
        return mapping(ind)

    def mapping(ind, first=None):
        m = {}
        if first is not None:
            k, rest = first
            m[k] = value_after(rest, ind)
        while True:
            skip()
            if pos[0] >= len(lines):
                return m
            l = lines[pos[0]]
            if indent(l) != ind or l.lstrip().startswith('- '):
                return m
            s = l.strip()
            k, _, rest = s.partition(':')
            pos[0] += 1
            m[k.strip()] = value_after(rest, ind)

    def seq(ind):
        a = []
        while True:
            skip()
            if pos[0] >= len(lines):
                return a
            l = lines[pos[0]]
            if indent(l) != ind or not (l.lstrip().startswith('- ') or
                                        l.strip() == '-'):
                return a
            item = l.strip()[2:] if l.strip() != '-' else ''
            pos[0] += 1
            iind = ind + 2
            s = _strip_comment(item)
            if ':' in s and not s.startswith(('"', "'", '[')) and \
               (s.split(':', 1)[1] == '' or s.split(':', 1)[1][0] == ' '):
                k, _, rest = s.partition(':')
                a.append(mapping(iind, (k.strip(), rest)))
            elif s == '':
                a.append(node(iind))
            else:
                a.append(_scalar(s))

    return node(0)
