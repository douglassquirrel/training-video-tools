"""The cells and the one table of a finished video's out/OUT.md (PLAN.md item 31).

Standard library only; runs on Python 3.9.
"""

import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from videotools import cli

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
COMMIT = re.compile(r"[0-9a-fA-F]{4,40}")
SEPARATOR = re.compile(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?")


def size_text(size):
    """A size in bytes with comma thousands separators: 19630414 -> '19,630,414'."""
    return f"{size:,}"


def made_text(mtime, zone):
    """A file time as 'D Month YYYY, HH:MM' in the IANA zone `zone`, or the machine's own when None."""
    if zone is None:
        when = datetime.fromtimestamp(mtime).astimezone()
    else:
        try:
            when = datetime.fromtimestamp(mtime, ZoneInfo(zone))
        except (ZoneInfoNotFoundError, ValueError) as e:
            raise cli.Failure(f"TIME_ZONE '{zone}' is not a time zone this machine knows; give a name such as "
                              "Europe/London (or remove the setting to use the machine's own)") from e
    return f"{when.day} {MONTHS[when.month - 1]} {when.year}, {when:%H:%M}"


def text_cell(text, flag):
    """TEXT for a cell: `|` written `\\|`; a line break refused, naming the flag it came from."""
    if "\n" in text or "\r" in text:
        raise cli.Failure(f"the {flag} text has a line break; a table cell is one line: give it on one line")
    return text.replace("|", "\\|")


def commit(value, flag):
    """A commit given on the command line: 4 to 40 hexadecimal digits, else refused naming the flag."""
    if not COMMIT.fullmatch(value):
        raise cli.Failure(f"{flag} {value!r} is not a commit id (4 to 40 hexadecimal digits)")
    return value


def made_with(tools, elements):
    """The Made-with cell: the tools commit, and the library's in brackets when there is one."""
    return f"`{tools}`" + (f" (video-elements `{elements}`)" if elements else "")


def row(name, made, made_with_cell, size, sha, state):
    """One table row for the file `name`, every cell given as written but the name, size and hash."""
    if "`" in name or "\n" in name or "\r" in name:
        raise cli.Failure(f"the file name {name!r} has a backtick or a line break, which a table cell cannot hold; "
                          "rename the copy you record")
    cells = ["`" + name.replace("|", "\\|") + "`", made, made_with_cell, size_text(size), f"`{sha}`", state]
    return "|" + "|".join(f" {c} " if c else " " for c in cells) + "|"



def _bars(content):
    """The positions of the `|`s in a line that are not written `\\|`."""
    return [i for i, c in enumerate(content) if c == "|" and (i == 0 or content[i - 1] != "\\")]


def _cells(content):
    """A table line's cells, stripped: what lies between its bars (it starts with one; the closing one
    is optional)."""
    edges = _bars(content)
    if not content.rstrip().endswith("|"):
        edges.append(len(content))
    return [content[a + 1:b].strip() for a, b in zip(edges, edges[1:])]


def _content(line):
    """A line without its line ending."""
    return line.rstrip("\r\n")


def _table(lines, path):
    """(first, last): the indices of the one table's header and its last row; refused unless the
    file has exactly one table (a run of lines starting `|`, its second a separator row) of six columns."""
    tables, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            j = i
            while j + 1 < len(lines) and lines[j + 1].lstrip().startswith("|"):
                j += 1
            if j > i and SEPARATOR.fullmatch(_content(lines[i + 1]).strip()):
                tables.append((i, j))
            i = j + 1
        else:
            i += 1
    if not tables:
        raise cli.Failure(f"{path} has no table; record-output changes nothing in it")
    if len(tables) > 1:
        raise cli.Failure(f"{path} has {len(tables)} tables; it should have one; record-output changes nothing in it")
    first, last = tables[0]
    columns = len(_cells(_content(lines[first])))
    if columns != 6:
        raise cli.Failure(f"{path} has a table of {columns} columns; it should have six (file, made, made with, size, "
                          "SHA-256, state); record-output changes nothing in it")
    return first, last


def _row_of(lines, first, last, name):
    """The index of `name`'s row in the table, or None; names compared in Unicode NFC."""
    want = unicodedata.normalize("NFC", "`" + name.replace("|", "\\|") + "`")
    for k in range(first + 2, last + 1):
        cells = _cells(_content(lines[k]))
        if cells and unicodedata.normalize("NFC", cells[0]) == want:
            return k
    return None


def append(text, row_line, name, path):
    """`text` with `row_line` after its table's last row; refused if the table has a row for `name`."""
    lines = text.splitlines(keepends=True)
    first, last = _table(lines, path)
    if _row_of(lines, first, last, name) is not None:
        raise cli.Failure(f"{path} already has a row for {name}; to add to its state, use --add-state")
    ending = lines[last][len(_content(lines[last])):] or ("\r\n" if lines[first].endswith("\r\n") else "\n")
    lines[last] = _content(lines[last]) + ending
    lines.insert(last + 1, row_line + ending)
    return "".join(lines)


def add_state(text, name, addition, path):
    """(the new text, the row as it now reads) with `addition` added, after a space, to `name`'s
    State cell (alone in an empty one); every other byte unchanged."""
    lines = text.splitlines(keepends=True)
    first, last = _table(lines, path)
    k = _row_of(lines, first, last, name)
    if k is None:
        raise cli.Failure(f"{path} has no row for {name}; add one first (record-output without --add-state)")
    content = _content(lines[k])
    cells = _cells(content)
    if len(cells) != 6:
        raise cli.Failure(f"{path}: the row for {name} has {len(cells)} cells, not six; record-output changes "
                          "nothing in it")
    bars = _bars(content)
    closed = content.rstrip().endswith("|")
    start, end = (bars[-2], bars[-1]) if closed else (bars[-1], len(content))
    old = content[start + 1:end].strip()
    new = f"{old} {addition}" if old else addition
    line = content[:start + 1] + f" {new} " + content[end:]
    lines[k] = line + lines[k][len(content):]
    return "".join(lines), line


def new_file(title, row_line):
    """A new OUT.md holding one row."""
    return (f"# out/ — {title}: finished files\n"
            "\n"
            "*Each version, newest last. Finished files are never written over or renamed.*\n"
            "\n"
            "| File | Made | Made with | Size (bytes) | SHA-256 | State |\n"
            "|---|---|---|---|---|---|\n"
            f"{row_line}\n")
