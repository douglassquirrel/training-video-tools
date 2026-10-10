"""Which characters a font file has: its `cmap` table, read with the standard library.

cairo's simple text API draws a character the font lacks as the font's missing-glyph box and
reports the same width for every such character, so the only way to know is to ask the font.
`characters(path)` reads a TrueType/OpenType file's cmap (formats 4 and 12, the Unicode
subtables) once; `fonts.load` registers each of a kit's files by family name, and `draw.text`
asks `has(family, ch)`. Python 3.9; also used by `check-script`.
"""

import struct

from videotools import cli

_by_path = {}      # font file -> set of code points
_by_family = {}    # family name -> font file


def characters(path):
    """The set of code points the font file maps to a glyph."""
    if path not in _by_path:
        try:
            with open(path, "rb") as f:
                data = f.read()
            _by_path[path] = _read_cmap(data)
        except (OSError, struct.error, IndexError, ValueError):
            raise cli.Failure(f"{path} is not a TrueType or OpenType font with a character map (cmap)") from None
    return _by_path[path]


def register(family, path):
    """Make `has(family, ch)` answer from this file."""
    _by_family[family] = path


def has(family, ch):
    """Whether the family's file has a glyph for `ch`; a family never registered is assumed to
    have everything (fallback fonts, plain drawing in the tests)."""
    if family not in _by_family:
        return True
    return ord(ch) in characters(_by_family[family])


def _read_cmap(data):
    tag = data[:4]
    if tag == b"ttcf":                      # a collection: its first font
        offset = struct.unpack(">I", data[12:16])[0]
    elif tag in (b"\0\1\0\0", b"true", b"OTTO"):
        offset = 0
    else:
        raise ValueError("not a font")
    num_tables = struct.unpack(">H", data[offset + 4:offset + 6])[0]
    cmap = None
    for i in range(num_tables):
        rec = offset + 12 + 16 * i
        if data[rec:rec + 4] == b"cmap":
            cmap = struct.unpack(">I", data[rec + 8:rec + 12])[0]
    if cmap is None:
        raise ValueError("no cmap")
    n = struct.unpack(">H", data[cmap + 2:cmap + 4])[0]
    found = set()
    seen = False
    for i in range(n):
        platform, encoding, sub = struct.unpack(">HHI", data[cmap + 4 + 8 * i:cmap + 12 + 8 * i])
        if (platform, encoding) not in ((0, 3), (0, 4), (0, 6), (3, 1), (3, 10)):   # the Unicode subtables
            continue
        fmt = struct.unpack(">H", data[cmap + sub:cmap + sub + 2])[0]
        if fmt == 4:
            found |= _format4(data, cmap + sub)
            seen = True
        elif fmt == 12:
            found |= _format12(data, cmap + sub)
            seen = True
    if not seen:
        raise ValueError("no unicode cmap subtable")
    return found


def _format4(data, at):
    seg_x2 = struct.unpack(">H", data[at + 6:at + 8])[0]
    segs = seg_x2 // 2
    ends = struct.unpack(f">{segs}H", data[at + 14:at + 14 + seg_x2])
    starts_at = at + 16 + seg_x2
    starts = struct.unpack(f">{segs}H", data[starts_at:starts_at + seg_x2])
    deltas = struct.unpack(f">{segs}h", data[starts_at + seg_x2:starts_at + 2 * seg_x2])
    offsets_at = starts_at + 2 * seg_x2
    offsets = struct.unpack(f">{segs}H", data[offsets_at:offsets_at + seg_x2])
    found = set()
    for i in range(segs):
        if starts[i] == 0xFFFF:
            continue
        for cp in range(starts[i], ends[i] + 1):
            if offsets[i] == 0:
                glyph = (cp + deltas[i]) & 0xFFFF
            else:
                g_at = offsets_at + 2 * i + offsets[i] + 2 * (cp - starts[i])
                glyph = struct.unpack(">H", data[g_at:g_at + 2])[0]
                if glyph:
                    glyph = (glyph + deltas[i]) & 0xFFFF
            if glyph:
                found.add(cp)
    return found


def _format12(data, at):
    groups = struct.unpack(">I", data[at + 12:at + 16])[0]
    found = set()
    for i in range(groups):
        start, end, glyph = struct.unpack(">III", data[at + 16 + 12 * i:at + 28 + 12 * i])
        for cp in range(start, end + 1):
            if glyph + (cp - start):
                found.add(cp)
    return found
