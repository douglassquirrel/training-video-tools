"""A scene's choreography from the script: the Cast table, the Moves list and the two panel
sections, read into plain data (PLAN.md item 15, "The choreography format").

`parse_sections` is called by `script.parse` with the raw lines of each section; it reports
every malformed line as a problem naming it. What a row or move *means* (an element the library
has, a cue the scene has, a label in On screen) is checked later, against the library.
Standard library only; runs on Python 3.9.
"""

import os
import re
import shlex

NAME = r"[A-Za-z0-9][A-Za-z0-9-]*"
DOTTED = r"[a-z][a-z0-9-]*(?:\.\d+)*"            # a parameter or anchor name, maybe indexed: highlight.3
QUALIFIERS = ("where", "first", "columns")        # rows.where, .first, .columns: part of a data file, in that order
TEXT_QUALIFIERS = ("skip", "first")               # text.skip, .first: some of a text's lines, in that order
NOT_COUNTED = "tab"                               # an index of tabs (tab.N, tab-box.N) is not one of rows or lines
ROTATE = "rotate"                                 # on any member: degrees clockwise about its box's centre
OWN_COLOUR = "colour."                            # colour.<role>=<name>: a member's own colour for an element's role
NUM = r"-?\d+(?:\.\d+)?"
REGIONS = ("left", "right", "centre", "top-left", "top-right", "bottom-left", "bottom-right", "full")
CAST_COLUMNS = ("Name", "Element", "Where", "Size", "Parameters")
PIECES = ("pill", "callout", "text", "badge", "hand", "arrow")   # video-tools' own cast members
DEFAULT_SPAN = 0.6                                               # seconds a move takes when no time is given

_NAME_RE = re.compile(f"^{NAME}$")
_PIXELS_RE = re.compile(rf"^({NUM}) ({NUM})$")
_ANCHOR_RE = re.compile(rf"^({NAME})\.({DOTTED})(?: \+ ({NUM}) ({NUM}))?$")
_SIZE_RE = re.compile(rf"^({NUM})(?:x({NUM}))?$")
_TIME = rf"end(?:[+-]{NUM})?|{NUM}%|{NUM}"       # seconds from the cue's start or its end, or a share of its length
_SPAN_RE = re.compile(rf"^(?P<a>{_TIME})(?P<as>\s*s)?(?:\s*[–-]\s*(?P<b>{_TIME})(?P<bs>\s*s)?)?$")
_ACROSS_RE = re.compile(rf"^(?P<a>{_TIME})(?P<as>\s*s)?\s*[–-]\s*"
                        rf"(?:cue (?P<cue>\d+),\s*(?P<b>{_TIME})(?P<bs>\s*s)?|(?P<scene>end of scene))$")
_SCENE_MOVE_RE = re.compile(r"^cue (\d+)(?:, ([^:]+))?: (.+)$")
_PANEL_MOVE_RE = re.compile(r"^(?:([^:]+): )?(.+)$")
_VALUE = r'"[^"]*"|\S+'
_SHOW_RE = re.compile(rf"^(show|hide|keep) ({NAME}(?:, {NAME})*)$")
_DIM_RE = re.compile(rf"^dim ({NAME}(?:, {NAME})*) to ({NUM})$")
_FLASH_RE = re.compile(rf"^flash ({NAME}(?:, {NAME})*)((?: \S+)*)$")
_MOVE_RE = re.compile(rf"^move ({NAME}) to (.+)$")
_ANIMATE_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE}) (?:→|->) ({_VALUE})$")
_SET_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE})$")
_STATE_RE = re.compile(rf"^({NAME}) ([a-z][a-z0-9-]*) (?:→|->) ([a-z][a-z0-9-]*)$")
_LIST_RE = re.compile(r"^-\s+(.+)$")
# a parameter's name: the element's own, maybe indexed; colour.<role>; or a qualifier of a data file or a text:
# <rows parameter>.where / .first / .columns, <text parameter>.skip / .first
_PARAM_NAME_RE = re.compile(rf"^(?:{DOTTED}|colour\.[a-z][a-z0-9-]*|[a-z][a-z0-9-]*\.(?:where|first|columns|skip))$")

WHERE_HELP = ("is not X Y in area pixels, a region ({}) or a member's anchor like sample.row.3 + 40 -12"
              .format(", ".join(REGIONS)))
ACTION_HELP = ("is not show NAME, hide NAME, keep NAME, dim NAME to LEVEL, flash NAME, move NAME to WHERE, "
               "NAME.PARAM A → B, NAME.PARAM VALUE or NAME STATE → STATE")
FLASH = {"rate": 1.4, "phase": 0.0, "low": 0.0}  # a flash's options and their defaults: flashes a second (9 radians a
MAX_FLASH_RATE = 3.0                             # second is 1.43), a fraction of a beat, the lowest opacity


def parse_where(text):
    """{'kind': 'pixels', x, y} | {'kind': 'region', name} | {'kind': 'anchor', member, anchor, dx, dy};
    None when the text is none of them."""
    m = _PIXELS_RE.match(text)
    if m:
        return {"kind": "pixels", "x": float(m.group(1)), "y": float(m.group(2))}
    if text in REGIONS:
        return {"kind": "region", "name": text}
    m = _ANCHOR_RE.match(text)
    if m:
        return {"kind": "anchor", "member": m.group(1), "anchor": m.group(2),
                "dx": float(m.group(3) or 0), "dy": float(m.group(4) or 0)}
    return None


def parse_points(text):
    """The two control points of an arrow's `via`, 'P; P', each a Where's pixels or anchor
    ({'kind': 'pixels' | 'anchor', …}); None when the text is not two such places."""
    places = [parse_where(part.strip()) for part in text.split(";")]
    if len(places) != 2 or any(w is None or w["kind"] == "region" for w in places):
        return None
    return places


def parse_dash(text):
    """[on, off] from 'ON OFF', two numbers above 0; None otherwise."""
    parts = text.split()
    if len(parts) != 2 or not all(re.match(f"^{NUM}$", v) and float(v) > 0 for v in parts):
        return None
    return [float(v) for v in parts]


def _column(text, header, what):
    """(index from 0, None) for a column written as its header's name or its number from 1; or
    (None, a problem)."""
    text = text.strip()
    if text.isdigit():
        n, count = int(text), f"{len(header)} column{'' if len(header) == 1 else 's'}"
        return (n - 1, None) if 1 <= n <= len(header) else (None, f"'{what}': no column {n} (there are {count})")
    if text in header:
        return header.index(text), None
    return None, f"'{what}': no column '{text}' (the columns are {', '.join(header)})"


def select_rows(rows, params, name):
    """(rows, [problems]) for a data file's rows as a cast row chooses them beside the parameter
    `name`: `name.where` ("COLUMN = VALUE" or "COLUMN != VALUE") keeps the data rows that match,
    `name.first` then the first N of them, `name.columns` ("A, B") then those columns in that
    order. A column is its header's name or its number from 1; the first row is the header and
    is always kept. With a problem, that choice is left unmade."""
    where, first, columns = (params.get(f"{name}.{q}") for q in QUALIFIERS)
    if where is None and first is None and columns is None:
        return rows, []
    if not rows:
        q = next(q for q in QUALIFIERS if f"{name}.{q}" in params)
        return rows, [f"'{name}.{q}': the file has no rows"]
    header, data, problems = rows[0], rows[1:], []
    if where is not None:
        m = re.match(r"^(.+?)\s*(!=|=)\s*(.*)$", where)
        if not m:
            problems.append(f"'{name}.where' should be COLUMN = VALUE or COLUMN != VALUE, not '{where}'")
        else:
            col, problem = _column(m.group(1), header, f"{name}.where")
            value, equal = m.group(3).strip(), m.group(2) == "="
            if problem:
                problems.append(problem)
            else:
                kept = [r for r in data if ((r[col].strip() if col < len(r) else "") == value) == equal]
                if equal and not kept:
                    problems.append(f"'{name}.where': no row has '{value}' in column '{header[col]}'")
                else:
                    data = kept
    if first is not None:
        if not first.isdigit() or int(first) < 1:
            problems.append(f"'{name}.first' should be a whole number above 0, not '{first}'")
        else:
            data = data[:int(first)]
    if columns is not None:
        wanted = [c for c in columns.split(",") if c.strip()]
        found = [_column(c, header, f"{name}.columns") for c in wanted]
        if not wanted:
            problems.append(f"'{name}.columns' names no column")
        elif any(problem for _i, problem in found):
            problems += [problem for _i, problem in found if problem]
        else:
            picked = [i for i, _problem in found]
            header, data = [header[i] for i in picked], [[r[i] if i < len(r) else "" for i in picked] for r in data]
    return [header] + data, problems


def lines_of(text):
    """A text's lines, the blank ones left out, each as written."""
    return [line for line in text.splitlines() if line.strip()]


def select_lines(text, params, name):
    """(text, [problems]) for a text as a cast row chooses its lines beside the parameter `name`:
    `name.skip` drops the first N lines, `name.first` then keeps the first N of the rest, lines
    counted without the blank ones. With either, the result is the chosen lines alone, a line a
    line; with neither, the text exactly as it is. With a problem, that choice is left unmade."""
    skip, first = (params.get(f"{name}.{q}") for q in TEXT_QUALIFIERS)
    if skip is None and first is None:
        return text, []
    lines, problems = lines_of(text), []
    for q, value in (("skip", skip), ("first", first)):
        if value is None:
            continue
        if not value.isdigit() or int(value) < 1:
            problems.append(f"'{name}.{q}' should be a whole number above 0, not '{value}'")
        elif q == "first":
            lines = lines[:int(value)]
        elif int(value) >= len(lines):
            problems.append(f"'{name}.skip': the text has only {len(lines)} line{'' if len(lines) == 1 else 's'}")
        else:
            lines = lines[int(value):]
    return "\n".join(lines), problems


def parse_size(text):
    """(ok, None | {'w', 'h'}): blank is the element's own size; W or WxH in pixels."""
    if not text:
        return True, None
    m = _SIZE_RE.match(text)
    if not m:
        return False, None
    return True, {"w": float(m.group(1)), "h": float(m.group(2)) if m.group(2) else None}


def parse_params(text):
    """({name: value}, [problems]) from `name=value` pairs, values with spaces in double quotes."""
    out, problems = {}, []
    try:
        tokens = shlex.split(text)
    except ValueError as e:
        return out, [f"Parameters: {e}"]
    for token in tokens:
        name, eq, value = token.partition("=")
        if not eq or not _PARAM_NAME_RE.match(name):
            problems.append(f"Parameters: '{token}' is not name=value")
            continue
        out[name] = value
    return out, problems


def _value(s):
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] == '"' else s


def parse_action(text):
    """The action of a move as plain data, or (None, problem)."""
    m = _SHOW_RE.match(text)
    if m:
        return {"kind": m.group(1), "names": [n.strip() for n in m.group(2).split(",")]}, None
    m = _DIM_RE.match(text)
    if m:
        return {"kind": "dim", "names": [n.strip() for n in m.group(1).split(",")], "level": float(m.group(2))}, None
    m = _FLASH_RE.match(text)
    if m:
        act = dict({"kind": "flash", "names": [n.strip() for n in m.group(1).split(",")]}, **FLASH)
        for token in m.group(2).split():
            option, eq, value = token.partition("=")
            if option not in FLASH or not re.match(f"^{NUM}$", value):
                return None, (f"'{text}': a flash's options are {', '.join(list(FLASH)[:-1])} and {list(FLASH)[-1]}, "
                              f"each a number, not '{token}'")
            act[option] = float(value)
        return act, None
    m = _MOVE_RE.match(text)
    if m:
        where = parse_where(m.group(2))
        if where is None:
            return None, f"Where '{m.group(2)}' {WHERE_HELP}"
        return {"kind": "move", "name": m.group(1), "to": where}, None
    m = _ANIMATE_RE.match(text)
    if m:
        return {"kind": "param", "name": m.group(1), "param": m.group(2), "from": _value(m.group(3)),
                "to": _value(m.group(4))}, None
    m = _SET_RE.match(text)
    if m:
        return {"kind": "set", "name": m.group(1), "param": m.group(2), "value": _value(m.group(3))}, None
    m = _STATE_RE.match(text)
    if m:
        return {"kind": "state", "name": m.group(1), "from": m.group(2), "to": m.group(3)}, None
    return None, f"'{text}' {ACTION_HELP}"


def _time(s):
    """A written time as data, and whether it is written with ' s': ('start' | 'end', offset
    seconds) from '0.4', '-0.3', 'end-1.2' (True: seconds), or from a bare 'end' (None: either
    way); ('fraction', share of the cue's length) from '74%' (False: never)."""
    if s == "end":
        return ("end", 0.0), None
    if s.startswith("end"):
        return ("end", float(s[3:])), True
    if s.endswith("%"):
        return ("fraction", float(s[:-1]) / 100), False
    return ("start", float(s)), True


def parse_span(text):
    """(start, end, end cue) from a move's written time: 'A s', 'A–B s', 'over the cue', a time as
    'P%' (that share of the cue's length), 'A s – cue M, B s' (ending in a later cue: its number
    is the third value, else None) or 'A s – end of scene'. A time is ('start' | 'end', seconds
    from there), ('fraction', share) or ('scene', 0.0), the scene's end; a lone 'P%' ends
    ('fraction', share, 0.6), the usual 0.6 s later. `text` None is the default, the first 0.6 s.
    (None, None, None) when not understood: seconds are written with ' s' (once, at the end,
    for 'A–B s'), a percentage without, a bare 'end' either way."""
    if text is None:
        return ("start", 0.0), ("start", DEFAULT_SPAN), None
    text = text.strip()
    if text == "over the cue":
        return ("start", 0.0), ("end", 0.0), None
    across = _ACROSS_RE.match(text)
    m = across or _SPAN_RE.match(text)
    if not m:
        return None, None, None

    def written_right(needs, has):
        return needs is None or needs == bool(has)

    a, a_needs = _time(m.group("a"))
    has_b = bool(m.group("b"))
    b, b_needs = _time(m.group("b")) if has_b else (None, None)
    if has_b and not written_right(b_needs, m.group("bs")):
        return None, None, None                 # '0.5–50% s', or seconds without their ' s'
    shared = has_b and not across and bool(m.group("bs"))     # 'A–B s': the one ' s' is for both
    if a_needs is False and m.group("as"):
        return None, None, None                 # '74% s'
    if a_needs and not m.group("as") and not shared:
        return None, None, None                 # seconds without their ' s'
    if across and across.group("scene"):
        return a, ("scene", 0.0), None
    if not has_b:
        return a, ((a[0], a[1] + DEFAULT_SPAN) if a[0] != "fraction" else ("fraction", a[1], DEFAULT_SPAN)), None
    return a, b, (int(across.group("cue")) if across else None)


CUELESS = {"panel": "a panel's moves have no 'cue N': times count from the panel's rise",
           "scene": "the scene has no cues, so its moves have no 'cue N': times count from the scene's start"}


MOVE_HELP = ("is not cue N[, TIME][, linear]: ACTION (TIME: A s, A–B s, over the cue, P%–Q%, A s – cue M, B s, "
             "or A s – end of scene)")


def parse_move(text, cueless=None):
    """({cue, start, end, action}, problem) for the text of one move list item. `cueless` is
    'panel' or 'scene' where moves are written without a cue (a panel; a scene that has none).
    The move also has `linear: True` when its time ends ', linear': a steady rate, not eased."""
    if cueless:
        if text.startswith("cue "):
            return None, CUELESS[cueless]
        m = _PANEL_MOVE_RE.match(text)
        cue, span, action = None, m.group(1), m.group(2)
    else:
        m = _SCENE_MOVE_RE.match(text)
        if not m:
            if ":" in text and not text.startswith("cue "):
                return None, ("a scene's move starts 'cue N' (a panel's moves and those of a scene with no cues "
                              "have none)")
            return None, f"'{text}' {MOVE_HELP}"
        cue, span, action = int(m.group(1)), m.group(2), m.group(3)
    linear = False
    if span is not None:
        parts = [part.strip() for part in span.split(",")]
        if parts[-1] == "linear":
            linear, span = True, ", ".join(parts[:-1]) or None
    start, end, end_cue = parse_span(span)
    if start is None or (end_cue and cueless):
        return None, f"'{text}' {MOVE_HELP}"
    act, problem = parse_action(action.strip())
    if problem:
        return None, problem
    move = {"cue": cue, "start": start, "end": end, "action": act}
    if end_cue:
        move["end_cue"] = end_cue
    if linear:
        move["linear"] = True
    return move, None


def window(move, tl, panel=False):
    """(from, to) in scene seconds for a move against a Timeline: each time from its own cue's
    start, end or length (the span's later cue for its end, when it has one); with no cue, the
    mistake cue's in a panel (times count from the panel's rise) or the scene's own."""
    def frame_of(cue):
        if cue is not None:
            return tl.start(cue), tl.length(cue)
        if not panel:
            return 0.0, tl.total
        return (tl.start(tl.mistake), tl.length(tl.mistake)) if tl.mistake else (0.0, 0.0)

    def at(when, cue):
        base, length = frame_of(cue)
        if when[0] == "scene":
            return tl.total
        if when[0] == "fraction":
            return base + length * when[1] + (when[2] if len(when) > 2 else 0.0)
        return base + when[1] + (length if when[0] == "end" else 0.0)
    return at(move["start"], move["cue"]), at(move["end"], move.get("end_cue", move["cue"]))


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_rule(cells):
    return all(set(c) <= set("-: ") for c in cells)


def parse_cast_rows(lines, where, problems):
    """The cast rows of a table given as [(line number, text)]; problems appended with `where`.
    A row's `where` is None for an arrow whose Where is blank."""
    cast, seen, header_seen = [], {}, False
    for n, line in lines:
        cells = _cells(line)
        if _is_rule(cells):
            continue
        if not header_seen:
            header_seen = True
            if tuple(cells[:5]) != CAST_COLUMNS:
                problems.append(f"line {n}: {where}: the table's columns are {' | '.join(CAST_COLUMNS)} | Notes, "
                                f"not {' | '.join(cells)}; its rows are not read")
                return cast
            continue
        if len(cells) < 5:
            problems.append(f"line {n}: {where}: a row needs five cells ({' | '.join(CAST_COLUMNS)}), "
                            f"this one has {len(cells)}")
            continue
        name, element, where_text, size_text, params_text = cells[:5]
        ok = True
        if not _NAME_RE.match(name):
            problems.append(f"line {n}: {where}: '{name}' is not a name (letters, digits and hyphens)")
            ok = False
        elif name in seen:
            problems.append(f"line {n}: {where}: '{name}' is already in the cast (line {seen[name]})")
            ok = False
        pos = parse_where(where_text)
        placed_by_its_ends = element == "arrow" and not where_text      # its from and to place it
        if pos is None and not placed_by_its_ends:
            problems.append(f"line {n}: {where}: Where '{where_text}' {WHERE_HELP}")
            ok = False
        size_ok, size = parse_size(size_text)
        if not size_ok:
            problems.append(f"line {n}: {where}: Size '{size_text}' is not W or WxH in pixels, or blank")
            ok = False
        params, param_problems = parse_params(params_text)
        for p in param_problems:
            problems.append(f"line {n}: {where}: {p}")
        if param_problems:
            ok = False
        if ok:
            seen[name] = n
            cast.append({"name": name, "element": element, "where": pos, "size": size, "params": params, "line": n})
    return cast


def parse_moves(lines, where, cueless, problems):
    moves = []
    for n, line in lines:
        m = _LIST_RE.match(line.strip())
        if not m:
            problems.append(f"line {n}: {where}: not a move (a list item '- cue N[, TIME]: ACTION'): {line.strip()}")
            continue
        move, problem = parse_move(m.group(1).strip(), cueless)
        if problem:
            problems.append(f"line {n}: {where}: {problem}")
            continue
        move["line"] = n
        moves.append(move)
    return moves


def parse_sections(scene, sections, problems):
    """Fill `scene['cast']`, `scene['moves']` and `scene['panels']` from the raw lines of its
    `### Cast`, `### Moves`, `### Mistake` and `### Right way` sections
    ({name: {"line": heading line, "lines": [(n, line)]}})."""
    key = scene["key"]
    if "cast" in sections:
        scene["cast"] = parse_cast_rows(_tables_only(sections["cast"]["lines"], f"scene {key}, cast", problems),
                                        f"scene {key}, cast", problems)
    if "moves" in sections:
        scene["moves"] = parse_moves([(n, ln) for n, ln in sections["moves"]["lines"] if ln.strip()],
                                     f"scene {key}, moves", None if scene["cues"] else "scene", problems)
    for panel in ("mistake", "right way"):
        if panel not in sections:
            continue
        where = f"scene {key}, {panel}"
        table, moves = [], []
        for n, ln in sections[panel]["lines"]:
            s = ln.strip()
            if not s:
                continue
            (table if s.startswith("|") else moves if s.startswith("-") else _reject(problems, n, where, s)).append(
                (n, ln))
        scene["panels"][panel] = {"line": sections[panel]["line"], "cast": parse_cast_rows(table, where, problems),
                                 "moves": parse_moves(moves, where, "panel", problems)}


def _reject(problems, n, where, s):
    problems.append(f"line {n}: {where}: not a cast row or a move: {s}")
    return []


def _tables_only(lines, where, problems):
    out = []
    for n, ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("|"):
            out.append((n, ln))
        else:
            problems.append(f"line {n}: {where}: not a cast row: {s}")
    return out


# ---------------------------------------------------------------- what a row or a move means

BOX_ANCHORS = ("top-left", "top-right", "bottom-left", "bottom-right", "centre")   # every member has these
PANELS = ("mistake", "right way")
# The pieces' parameters by name and kind: label (the words the piece is for: not empty, and checked
# against On screen), caption (optional words: checked against On screen unless empty, which is none),
# number, unit (a number from 0 to 1), colour (a name frame.colour resolves), align (left, centre, right),
# yesno, anchor (a member's anchor, a.centre, with an optional offset), points (two places separated by
# ';', each X Y or an anchor), dash (two numbers above 0), text.
PIECE_PARAMS = {
    "pill": {"text": "label", "size": "number", "fill": "colour", "colour": "colour", "anchor": "align"},
    "callout": {"text": "label", "target": "anchor", "size": "number", "fill": "colour", "colour": "colour",
                "anchor": "align", "leader": "colour"},
    "text": {"text": "label", "size": "number", "role": "text", "colour": "colour", "anchor": "align"},
    "badge": {"ok": "yesno", "r": "number"},
    "hand": {"angle": "number", "scale": "number", "mirror": "yesno", "label": "caption"},
    "arrow": {"from": "anchor", "to": "anchor", "colour": "colour", "width": "number", "progress": "unit",
              "head": "yesno", "via": "points", "dash": "dash"},
}
PIECE_REQUIRED = {"pill": ("text",), "callout": ("text", "target"), "text": ("text",), "badge": ("ok",),
                  "hand": ("angle", "scale"), "arrow": ("from", "to")}
ESTIMATE_NOTE = " (estimated at 2.6 words a second; run narrate for the measured length)"


def _a(noun):
    return ("an " if noun[0] in "aeiou" else "a ") + noun


def _secs(t):
    return f"{round(t, 3):g}"


def check(scene, tl, lib, folder, colours=None):
    """Every problem with what a scene's choreography means: the elements (the pieces, and the
    library's when `lib` is given), the anchors members are placed by, the parameters by name,
    kind and range, labels against On screen, cues and times against `tl` (a Timeline), members
    shown twice or never. `folder` is the video's, for data files; `colours` the names
    `frame.colour` knows (the script's Colours and the brand's roles), for a member's own
    colours, or None when they are not known. [] when all is well."""
    key = scene["key"]
    problems = []
    has_mistake = any("mistake" in c for c in scene["cues"])
    for panel in PANELS:
        if panel in scene["panels"] and not has_mistake:
            problems.append(f"line {scene['panels'][panel]['line']}: scene {key}: a {panel.capitalize()} section, "
                            f"but no cue has a 'mistake:'")
    labels = [it["text"] for it in scene["screen"]]
    problems += _check_part(scene, scene["cast"], scene["moves"], f"scene {key}, cast", f"scene {key}, moves",
                            tl, lib, labels, folder, panel=False, colours=colours)
    for panel in PANELS:
        if panel in scene["panels"]:
            p = scene["panels"][panel]
            where = f"scene {key}, {panel}"
            problems += _check_part(scene, p["cast"], p["moves"], where, where, tl, lib, labels, folder, panel=True,
                                    colours=colours)
    return problems


def warnings(scene, lib):
    """What is allowed but probably not meant, by line: a library member with a blank Size whose
    element is code with a nominal size (what it draws depends on its data or text) and does not
    offer its natural size (its `fit` is not `natural`), so it is fitted into the nominal one.
    [] without a library."""
    if lib is None:
        return []
    key, out = scene["key"], []
    parts = [(f"scene {key}, cast", scene["cast"])]
    parts += [(f"scene {key}, {panel}", scene["panels"][panel]["cast"]) for panel in PANELS if panel in scene["panels"]]
    for where, cast in parts:
        for m in cast:
            if m["size"] is not None or _element_kind(m["element"], lib) != "library":
                continue
            el = lib.element(m["element"])
            if el["kind"] == "code" and el.get("fit") != "natural" and _size_is_nominal(el):
                w, h = el["size"]
                out.append(f"line {m['line']}: {where}: '{m['name']}': Size is blank and {_a(el['name'])}'s own size "
                           f"({w:g} × {h:g}) is nominal, so it will not be drawn at the size its data or text "
                           f"needs; give it a Size")
    return out


def _size_is_nominal(el):
    """True when the Notes cell of the `size` row in the element's ELEMENT.md begins 'nominal': the
    description the library returns does not carry it (PLAN.md item 17, 3; "Open questions" 1)."""
    path = os.path.join(el.get("folder") or "", "ELEMENT.md")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8") as f:
        for line in f:
            cells = _cells(line) if line.lstrip().startswith("|") else []
            if len(cells) >= 3 and cells[0] == "size":
                return cells[2].lower().startswith("nominal")
    return False


def _check_part(scene, cast, moves, cast_where, moves_where, tl, lib, labels, folder, panel, colours=None):
    members = {m["name"]: m for m in cast}
    rows_of = {m["name"]: _rows_file(m, lib, folder) for m in cast}   # name -> (file, row count) or None
    ctx = {"members": members, "lib": lib, "labels": labels, "folder": folder, "rows_of": rows_of, "colours": colours,
           "order": {m["name"]: i for i, m in enumerate(cast)}}
    problems = []
    for m in cast:
        at = f"line {m['line']}: {cast_where}: "
        kind = _element_kind(m["element"], lib)
        if kind is None:
            problems.append(f"{at}'{m['name']}': no element '{m['element']}': not one of video-tools' pieces "
                            f"({', '.join(PIECES)}) and not in the library ({', '.join(lib.names())})")
        if m["where"] and m["where"]["kind"] == "anchor":      # no Where: an arrow, placed by its ends
            problem = _anchor_problem(ctx, m["where"], m["name"])
            if problem:
                problems.append(f"{at}'{m['name']}' is placed by {problem}")
        if kind == "piece":
            problems += [at + p for p in _piece_params(m, ctx)]
        elif kind == "library":
            problems += [at + p for p in _library_params(m, ctx)]
    shown_problems, move_problems = _check_moves(scene, ctx, moves, moves_where, tl, panel)
    for m in cast:
        if not panel and m["name"] in shown_problems:
            problems.append(f"line {m['line']}: {cast_where}: '{m['name']}' is never shown")
    return problems + move_problems


def _element_kind(element, lib):
    """'piece', 'library', or None for an element nobody has; 'unknown' when there is no library
    to ask (check-script says why)."""
    if element in PIECES:
        return "piece"
    if lib is None:
        return "unknown"
    try:
        lib.element(element)
    except Exception:
        return None
    return "library"


def _anchor_names(member, lib):
    """The anchors a member can be placed by, or None when the library is not here to say."""
    if member["element"] in PIECES:
        return list(BOX_ANCHORS)
    if lib is None:
        return None
    try:
        return list(lib.element(member["element"])["anchors"]) + list(BOX_ANCHORS)
    except Exception:
        return None


def _anchor_matches(name, pattern):
    """'row.3' matches 'row.*'; 'cell.3.2' matches 'cell.*.*'; a plain name matches itself."""
    a, b = name.split("."), pattern.split(".")
    return len(a) == len(b) and all(x == y or (y == "*" and x.isdigit()) for x, y in zip(a, b))


def _is_computed(member, anchor, lib):
    """True when a library element's anchor is worked out by its draw (the description says
    `computed`, or it is indexed), so a member placed by it must come later in the cast."""
    if member["element"] in PIECES or anchor in BOX_ANCHORS or lib is None:
        return False
    for name, value in lib.element(member["element"])["anchors"].items():
        if _anchor_matches(anchor, name):
            return value == "computed"
    return False


def _anchor_problem(ctx, where, self_name=None, placed=None):
    """None, or the rest of a sentence: 'X', which is not in the cast (…) / 'X'.'y', but ….
    `placed` is the member being placed (`self_name` when it is placed by its Where), for the
    rule that a computed anchor's member must come earlier in the cast."""
    members, target, anchor = ctx["members"], where["member"], where["anchor"]
    placed = placed or self_name
    if target == self_name:
        return "itself"
    if target not in members:
        return f"'{target}', which is not in the cast ({', '.join(members)})"
    names = _anchor_names(members[target], ctx["lib"])
    if names is None:
        return None
    if any(_anchor_matches(anchor, n) for n in names):
        rows = ctx["rows_of"].get(target)
        index = _first_index(anchor)
        if index == 0:
            return f"'{target}'.'{anchor}', but rows count from 1"
        if rows and index is not None and index > rows[1] and not anchor.startswith(NOT_COUNTED):
            return f"'{target}'.'{anchor}', but {_counted(rows)}"
        order = ctx.get("order", {})
        if (placed in order and _is_computed(members[target], anchor, ctx["lib"])
                and order[target] >= order[placed]):
            return (f"'{target}'.'{anchor}', which is computed when '{target}' is drawn, so '{placed}' must come "
                    f"after '{target}' in the cast")
        return None
    element = members[target]["element"]
    listed = ", ".join(names[:-1]) + " and " + names[-1]
    return f"'{target}'.'{anchor}', but {_a(element)}'s anchors are {listed}"


def _first_index(name):
    """The first index in a dotted name ('highlight.3' -> 3, 'cell.3.2' -> 3), or None."""
    parts = name.split(".")
    return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None


def is_qualifier(name):
    """True for `<parameter>.where`, `.first`, `.columns` or `.skip`: a choice of a data file's
    rows or columns, or of a text's lines."""
    base, dot, last = name.rpartition(".")
    return bool(dot) and last in QUALIFIERS + TEXT_QUALIFIERS


def text_file(folder, value):
    """The path of the file a text parameter's value names under the video's folder, or None when
    the value is the text itself."""
    if folder is None or "\n" in value:
        return None
    path = os.path.join(folder, value)
    return path if os.path.isfile(path) else None


def _counted(c):
    """'FILE has N rows as chosen', from what `_rows_file` found."""
    return f"{c[0]} has {c[1]} {c[4]}{'' if c[1] == 1 else 's'}{c[2]}"


def _rows_file(m, lib, folder):
    """What a library member's indices are counted against, or None: (the file as written, how
    many, a note, [problems of the choosing], 'row' | 'line', the parameter). Its `rows`
    parameter when that names a readable CSV under the video's folder: the rows its qualifiers
    choose. Else its one text parameter that names a file or has a qualifier: the lines chosen,
    blank ones not counted (labelled 'the text' when the value is the text itself)."""
    if m["element"] in PIECES or lib is None:
        return None
    if "rows" in m["params"]:
        path = os.path.join(folder, m["params"]["rows"]) if folder is not None else None
        if path is None or not os.path.isfile(path):
            return None
        import csv
        with open(path, encoding="utf-8", newline="") as f:
            rows, problems = select_rows(list(csv.reader(f)), m["params"], "rows")
        chosen = any(f"rows.{q}" in m["params"] for q in QUALIFIERS)
        return m["params"]["rows"], len(rows), " as chosen" if chosen else "", problems, "row", "rows"
    try:
        described = lib.element(m["element"])["params"]
    except Exception:
        return None
    texts = [n for n, d in described.items() if d["type"] == "text" and n in m["params"]
             and (text_file(folder, m["params"][n]) or any(f"{n}.{q}" in m["params"] for q in TEXT_QUALIFIERS))]
    if len(texts) != 1:
        return None
    name, value = texts[0], m["params"][texts[0]]
    path = text_file(folder, value)
    if path:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    else:
        text = value
    chosen, problems = select_lines(text, m["params"], name)
    note = " as chosen" if any(f"{name}.{q}" in m["params"] for q in TEXT_QUALIFIERS) else ""
    return (value if path else "the text"), len(lines_of(chosen)), note, problems, "line", name


def _param_match(name, params):
    """The description of the parameter `name` names ('highlight.3' matches 'highlight.*'), or None."""
    for pattern, desc in params.items():
        if _anchor_matches(name, pattern):
            return desc
    return None


def _library_value_problem(desc, name, value, ctx):
    """The problem with a value for a library element's parameter, or None."""
    kind = desc["type"]
    if kind in ("number", "integer"):
        if not re.match(f"^{NUM}$" if kind == "number" else r"^-?\d+$", value):
            noun = "a number" if kind == "number" else "a whole number"
            return f"'{name}' should be {noun}, not '{value}'"
        if not desc["min"] <= float(value) <= desc["max"]:
            return f"'{name}' is {desc['min']:g} to {desc['max']:g}, not '{value}'"
    elif kind == "colour":
        if not value:
            return f"'{name}' needs a colour name"
    elif kind == "boolean":
        if value not in ("yes", "no", "true", "false"):
            return f"'{name}' is yes or no (true or false), not '{value}'"
    elif kind == "label":
        if value and value not in ctx["labels"]:        # an empty label is none: nothing drawn, nothing to check
            return f"draws '{value}', which is not in the script's On screen list ({', '.join(ctx['labels'])})"
    elif kind == "rows":
        if ctx["folder"] is not None and not os.path.isfile(os.path.join(ctx["folder"], value)):
            return f"'{name}' names {value}, which is not under {ctx['folder']}"
    elif kind == "text":                        # a file's name, or the text itself: a name with no file is a slip
        looks_like_a_file = re.match(r"^\S+\.(?:txt|md)$", value)
        if ctx["folder"] is not None and looks_like_a_file and not text_file(ctx["folder"], value):
            return f"'{name}' names {value}, which is not under {ctx['folder']}"
    return None


def _index_problem(name, rows):
    index = _first_index(name)
    if index == 0:
        return f"'{name}' counts from 1"
    if rows and index is not None and index > rows[1] and not name.startswith(NOT_COUNTED):
        return f"'{name}': {_counted(rows)}"
    return None


def _state_problem(el, state):
    if not el["states"]:
        return f"{_a(el['name'])} has no states"
    if state not in el["states"]:
        return f"{_a(el['name'])} has no state '{state}' (its states are {', '.join(el['states'])})"
    return None


def _rotate_problem(value):
    """The problem with a value for `rotate`, which any member takes, or None."""
    return None if re.match(f"^{NUM}$", value) else f"'{ROTATE}' should be a number, not '{value}'"


def _own_colour_problem(el, name, value, colours):
    """The problem with `colour.<role>=<name>` on a member of `el`, or None: the role is one of the
    element's, and the name a colour the video knows (when `colours` says which those are)."""
    role = name[len(OWN_COLOUR):]
    if role not in el["colours"]:
        roles = ", ".join(el["colours"]) or "none"
        return f"{_a(el['name'])} has no colour role '{role}' (its colour roles are {roles})"
    if colours is not None and value not in colours:
        return (f"'{name}' names '{value}', which is not in the script's Colours or the brand's roles "
                f"({', '.join(sorted(colours))})")
    return None


def _library_params(m, ctx):
    el = ctx["lib"].element(m["element"])
    params, out = el["params"], []
    for name, desc in params.items():
        if desc["type"] == "rows" and name not in m["params"]:
            out.append(f"'{m['name']}': {_a(el['name'])} needs '{name}'")
    for name, value in m["params"].items():
        if is_qualifier(name):
            base, _dot, q = name.rpartition(".")
            kind = params.get(base, {}).get("type")
            problem = (f"'{name}' qualifies '{base}', which is a data file: it takes where, first and columns"
                       if kind == "rows" and q not in QUALIFIERS
                       else f"'{name}' qualifies '{base}', which is text: it takes skip and first"
                       if kind == "text" and q not in TEXT_QUALIFIERS
                       else f"'{name}' qualifies '{base}', which {_a(el['name'])} does not take as "
                            f"{'text' if q == 'skip' else 'a data file'}" if kind not in ("rows", "text")
                       else f"'{name}' qualifies '{base}', which is not given" if base not in m["params"] else None)
        elif name.startswith(OWN_COLOUR):
            problem = _own_colour_problem(el, name, value, ctx["colours"])
        elif name == ROTATE:
            problem = _rotate_problem(value)
        elif name == "state":
            problem = _state_problem(el, value)
        else:
            desc = _param_match(name, params)
            if desc is None:
                out.append(f"'{m['name']}': {_a(el['name'])} has no parameter '{name}' "
                           f"(its parameters are {', '.join(params)})")
                continue
            problem = (_index_problem(name, ctx["rows_of"].get(m["name"]))
                       or _library_value_problem(desc, name, value, ctx))
        if problem:
            out.append(f"'{m['name']}'" + (" " if problem.startswith("draws") else ": ") + problem)
        counted = ctx["rows_of"].get(m["name"])
        if counted and name == counted[5]:      # the problems of choosing its rows or lines, where it is given
            out += [f"'{m['name']}': {p}" for p in counted[3]]
    return out


def _value_problem(kind, name, value, ctx, self_name):
    """The problem with a piece's parameter value of `kind`, or None."""
    labels = ctx["labels"]
    if kind in ("number", "unit"):
        if not re.match(f"^{NUM}$", value):
            return f"'{name}' should be a number, not '{value}'"
        if kind == "unit" and not 0 <= float(value) <= 1:
            return f"'{name}' is 0 to 1, not '{value}'"
    elif kind == "align":
        if value not in ("left", "centre", "right"):
            return f"'{name}' is left, centre or right, not '{value}'"
    elif kind == "yesno":
        if value not in ("yes", "no"):
            return f"'{name}' is yes or no, not '{value}'"
    elif kind in ("label", "caption"):
        if not value:
            return f"'{name}' is empty, so there is nothing to draw" if kind == "label" else None
        if value not in labels:
            return f"draws '{value}', which is not in the script's On screen list ({', '.join(labels)})"
    elif kind == "anchor":
        where = parse_where(value)
        if not where or where["kind"] != "anchor":
            return f"'{name}' should be a member's anchor like a.centre, not '{value}'"
        problem = _anchor_problem(ctx, where, placed=self_name)
        if problem:
            return f"'{name}' is {problem}"
    elif kind == "points":
        places = parse_points(value)
        if places is None:
            return (f"'{name}' should be two points separated by ';', each X Y or a member's anchor like "
                    f"a.centre + 10 0, not '{value}'")
        for where in places:
            problem = _anchor_problem(ctx, where, placed=self_name) if where["kind"] == "anchor" else None
            if problem:
                return f"'{name}' is {problem}"
    elif kind == "dash":
        if parse_dash(value) is None:
            return f"'{name}' should be two numbers above 0, the dash and the gap, not '{value}'"
    return None


def _piece_params(m, ctx):
    piece, params = m["element"], PIECE_PARAMS[m["element"]]
    out = []
    for name in PIECE_REQUIRED[piece]:
        if name not in m["params"]:
            out.append(f"'{m['name']}': {_a(piece)} needs '{name}'")
    for name, value in m["params"].items():
        if name == ROTATE:
            if _rotate_problem(value):
                out.append(f"'{m['name']}': {_rotate_problem(value)}")
            continue
        if name not in params:
            out.append(f"'{m['name']}': {_a(piece)} has no parameter '{name}' "
                       f"(its parameters are {', '.join(params)})")
            continue
        problem = _value_problem(params[name], name, value, ctx, m["name"])
        own = params[name] == "anchor" and m["where"] is None and not problem
        if own and parse_where(value)["member"] == m["name"]:
            problem = f"'{name}' is its own anchor, but with a blank Where its two ends are what place it"
        if problem:
            out.append(f"'{m['name']}'" + (" " if problem.startswith("draws") else ": ") + problem)
    return out


def _resolve(tl, cue, when):
    """Seconds into its cue for a written time (None for the scene's end, which is in no cue)."""
    if when[0] == "scene":
        return None
    if when[0] == "fraction":
        return tl.length(cue) * when[1] + (when[2] if len(when) > 2 else 0.0)
    return when[1] if when[0] == "start" else tl.length(cue) + when[1]


def _check_moves(scene, ctx, moves, where, tl, panel):
    """([members never shown], [problems]) for a cast's moves."""
    members, lib = ctx["members"], ctx["lib"]
    problems, events, flashes = [], [], {}
    for mv in moves:
        at = f"line {mv['line']}: {where}: "
        cue, act = mv["cue"], mv["action"]
        if cue is None and not panel:           # a scene with no cues: times from its start, `end` its end
            for t in window(mv, tl):
                if t > tl.total + 1e-9:
                    problems.append(f"{at}{_secs(t)} s is past the end of the scene, which is {tl.total:.1f} s long")
                    break
        elif not panel:
            if not 1 <= cue <= len(scene["cues"]):
                problems.append(f"{at}cue {cue}: the scene has {len(scene['cues'])} cues")
                continue
            later = mv.get("end_cue", cue)
            if not 1 <= later <= len(scene["cues"]):
                problems.append(f"{at}cue {later}: the scene has {len(scene['cues'])} cues")
                continue
            if later < cue or (later == cue and "end_cue" in mv):
                problems.append(f"{at}the span ends at cue {later}, which is not after cue {cue}")
                continue
            for when, its_cue in ((mv["start"], cue), (mv["end"], later)):
                t, length = _resolve(tl, its_cue, when), tl.length(its_cue)
                if t is not None and t > length + 1e-9:
                    note = ESTIMATE_NOTE if its_cue in tl.estimated else ""
                    problems.append(f"{at}{_secs(t)} s is past the end of cue {its_cue}, which is {length:.1f} s "
                                    f"long{note}")
                    break
        names = act.get("names", [act.get("name")])
        missing = [n for n in names if n not in members]
        for n in missing:
            problems.append(f"{at}'{n}' is not in the cast ({', '.join(members)})")
        if missing:
            continue
        if act["kind"] == "keep":           # names the members, so the curtain leaves them; nothing else
            continue
        if act["kind"] == "flash":          # multiplies the opacity over its span; one at a time for a member
            if not 0 < act["rate"] <= MAX_FLASH_RATE:
                problems.append(f"{at}a flash's rate is above 0 and at most {MAX_FLASH_RATE:g} a second, not "
                                f"'{act['rate']:g}'")
            if not 0 <= act["low"] < 1:
                problems.append(f"{at}a flash's low is from 0 to below 1, not '{act['low']:g}'")
            a, b = window(mv, tl, panel)
            for n in names:
                clash = next((line for a2, b2, line in flashes.get(n, []) if a < b2 and a2 < b), None)
                if clash:
                    problems.append(f"{at}'{n}' is already flashing then (line {clash})")
                flashes.setdefault(n, []).append((a, b, mv["line"]))
            continue
        if act["kind"] == "dim" and not 0 <= act["level"] <= 1:
            problems.append(f"{at}a level is 0 to 1, not '{act['level']:g}'")
        if act["kind"] in ("show", "hide", "dim"):
            t = window(mv, tl, panel)[0]
            for n in names:
                events.append((t, mv["line"], act["kind"], n, cue))
        elif act["kind"] == "move":
            if act["to"]["kind"] == "anchor":
                problem = _anchor_problem(ctx, act["to"], placed=act["name"])
                if problem:
                    problems.append(f"{at}'{act['name']}' moves to {problem}")
        elif act["kind"] == "state":
            member = members[act["name"]]
            if member["element"] in PIECES:
                problems.append(f"{at}'{act['name']}' is {_a(member['element'])}, and the pieces have no states")
            elif _element_kind(member["element"], lib) == "library":
                el = lib.element(member["element"])
                problem = _state_problem(el, act["from"]) or _state_problem(el, act["to"])
                if problem:
                    problems.append(f"{at}'{act['name']}': {problem}")
        else:                                   # param (animate) or set
            member = members[act["name"]]
            values = [act["value"]] if act["kind"] == "set" else [act["from"], act["to"]]
            if act["param"] == ROTATE:          # any member turns
                problem = next((p for p in map(_rotate_problem, values) if p), None)
                if problem:
                    problems.append(f"{at}'{act['name']}': {problem}")
                continue
            if _element_kind(member["element"], lib) == "library":
                el = lib.element(member["element"])
                desc = _param_match(act["param"], el["params"])
                if desc is None:
                    problems.append(f"{at}'{act['name']}': {_a(el['name'])} has no parameter '{act['param']}' "
                                    f"(its parameters are {', '.join(el['params'])})")
                    continue
                problem = _index_problem(act["param"], ctx["rows_of"].get(act["name"]))
                for v in values:
                    problem = problem or _library_value_problem(desc, act["param"], v, ctx)
                if problem:
                    sep = " " if problem.startswith("draws") else ": "
                    problems.append(f"{at}'{act['name']}'{sep}{problem}")
            elif member["element"] in PIECES:
                params = PIECE_PARAMS[member["element"]]
                if act["param"] not in params:
                    problems.append(f"{at}'{act['name']}': {_a(member['element'])} has no parameter "
                                    f"'{act['param']}' (its parameters are {', '.join(params)})")
                    continue
                for v in values:
                    problem = _value_problem(params[act["param"]], act["param"], v, ctx, act["name"])
                    if problem:
                        sep = " " if problem.startswith("draws") else ": "
                        problems.append(f"{at}'{act['name']}'{sep}{problem}")
                        break
    shown = {n: None for n in members}           # name -> the line that showed it, or None
    if panel:
        for n in members:
            if not any(e[3] == n and e[2] == "show" for e in events):
                shown[n] = 0                     # shown from the start
    never, dimmed = set(members), set()
    for _t, line, kind, n, cue in sorted(events, key=lambda e: (e[0], e[1])):
        at = f"line {line}: {where}: "
        when = "" if cue is None else f" at cue {cue}"
        if kind == "show":
            never.discard(n)
            if shown[n] is not None and n not in dimmed:    # never 0: a member with a show is not shown from the start
                problems.append(f"{at}'{n}' is shown again{when} while still shown (shown at line {shown[n]}, "
                                "not hidden since)")
            shown[n] = line
            dimmed.discard(n)
        elif kind == "dim":
            if shown[n] is None:
                problems.append(f"{at}'{n}' is dimmed{when} but is not shown")
            else:
                dimmed.add(n)
        else:
            if shown[n] is None:
                problems.append(f"{at}'{n}' is hidden{when} but was not shown")
            shown[n] = None
            dimmed.discard(n)
    return never, sorted(problems, key=lambda p: int(p.split(":")[0].split()[1]))
