#!/usr/bin/env python3
# A PNG made smaller without losing a pixel: its image data deflated
# again at the highest level, and the chunks no viewer needs dropped.
# Nothing but Python's own library, so it runs wherever the book is
# made.
#
#	shrink.py file.png ...

import struct
import sys
import zlib

KEEP = {b"IHDR", b"PLTE", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"iCCP",
        b"pHYs", b"IEND"}


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))


def shrink(path):
    with open(path, "rb") as f:
        png = f.read()
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(path + ": not a PNG")
    pos, out, idat = 8, [], []
    while pos < len(png):
        n, kind = struct.unpack(">I4s", png[pos:pos + 8])
        data = png[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IDAT":
            idat.append(data)
            continue
        if kind == b"IEND":
            raw = zlib.decompress(b"".join(idat))
            out.append(chunk(b"IDAT", zlib.compress(raw, 9)))
        if kind in KEEP:
            out.append(chunk(kind, data))
    new = png[:8] + b"".join(out)
    if len(new) < len(png):
        with open(path, "wb") as f:
            f.write(new)
    return len(png), min(len(new), len(png))


for p in sys.argv[1:]:
    old, new = shrink(p)
    print("%s: %d to %d bytes" % (p, old, new))
