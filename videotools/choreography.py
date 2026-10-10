"""A scene's choreography from the script: the Cast table, the Moves list and the two panel
sections, read into plain data (PLAN.md item 15, "The choreography format").

`parse_sections` is called by `script.parse` with the raw lines of each section; it reports
every malformed line as a problem naming it. What a row or move *means* (an element the library
has, a cue the scene has, a label in On screen) is checked later, against the library.
Standard library only; runs on Python 3.9.
"""

import re
import shlex

NAME = r"[A-Za-z0-9][A-Za-z0-9-]*"
DOTTED = r"[a-z][a-z0-9-]*(?:\.\d+)*"            # a parameter or anchor name, maybe indexed: highlight.3
NUM = r"-?\d+(?:\.\d+)?"
REGIONS = ("left", "right", "centre", "top-left", "top-right", "bottom-left", "bottom-right", "full")
CAST_COLUMNS = ("Name", "Element", "Where", "Size", "Parameters")
PIECES = ("pill", "callout", "text", "badge", "hand", "arrow")   # video-tools' own cast members
DEFAULT_SPAN = 0.6                                               # seconds a move takes when no time is given

_NAME_RE = re.compile(f"^{NAME}$")
_PIXELS_RE = re.compile(rf"^({NUM}) ({NUM})$")
_ANCHOR_RE = re.compile(rf"^({NAME})\.({DOTTED})(?: \+ ({NUM}) ({NUM}))?$")
_SIZE_RE = re.compile(rf"^({NUM})(?:x({NUM}))?$")
_TIME = rf"end(?:[+-]{NUM})?|{NUM}"
_SPAN_RE = re.compile(rf"^(?P<a>{_TIME})(?:\s*[–-]\s*(?P<b>{_TIME}))?\s*s$|^(?P<over>over the cue)$")
_SCENE_MOVE_RE = re.compile(r"^cue (\d+)(?:, ([^:]+))?: (.+)$")
_PANEL_MOVE_RE = re.compile(r"^(?:([^:]+): )?(.+)$")
_VALUE = r'"[^"]*"|\S+'
_SHOW_RE = re.compile(rf"^(show|hide) ({NAME}(?:, {NAME})*)$")
_MOVE_RE = re.compile(rf"^move ({NAME}) to (.+)$")
_ANIMATE_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE}) (?:→|->) ({_VALUE})$")
_SET_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE})$")
_STATE_RE = re.compile(rf"^({NAME}) ([a-z][a-z0-9-]*) (?:→|->) ([a-z][a-z0-9-]*)$")
_LIST_RE = re.compile(r"^-\s+(.+)$")

WHERE_HELP = ("is not X Y in area pixels, a region ({}) or a member's anchor like sample.row.3 + 40 -12"
              .format(", ".join(REGIONS)))
ACTION_HELP = ("is not show NAME, hide NAME, move NAME to WHERE, NAME.PARAM A → B, NAME.PARAM VALUE or "
               "NAME STATE → STATE")


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
        if not eq or not re.match(f"^{DOTTED}$", name):
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
    """('start' | 'end', offset seconds) from '0.4', '-0.3', 'end', 'end-1.2'."""
    if s.startswith("end"):
        return ("end", float(s[3:] or 0))
    return ("start", float(s))


def parse_span(text):
    """(start, end) as (ref, offset) pairs from 'A s', 'A–B s' or 'over the cue'; None when
    `text` is None (the default: the first 0.6 s); (None, None) when not understood."""
    if text is None:
        return ("start", 0.0), ("start", DEFAULT_SPAN)
    m = _SPAN_RE.match(text.strip())
    if not m:
        return None, None
    if m.group("over"):
        return ("start", 0.0), ("end", 0.0)
    a = _time(m.group("a"))
    if m.group("b"):
        return a, _time(m.group("b"))
    return a, (a[0], a[1] + DEFAULT_SPAN)


def parse_move(text, in_panel):
    """({cue, start, end, action}, problem) for the text of one move list item."""
    if in_panel:
        if text.startswith("cue "):
            return None, "a panel's moves have no 'cue N': times count from the panel's rise"
        m = _PANEL_MOVE_RE.match(text)
        cue, span, action = None, m.group(1), m.group(2)
    else:
        m = _SCENE_MOVE_RE.match(text)
        if not m:
            if ":" in text and not text.startswith("cue "):
                return None, "a scene's move starts 'cue N' (a panel's moves have no cue)"
            return None, f"'{text}' is not cue N[, A s | A–B s | over the cue]: ACTION"
        cue, span, action = int(m.group(1)), m.group(2), m.group(3)
    start, end = parse_span(span)
    if start is None:
        return None, f"'{text}' is not cue N[, A s | A–B s | over the cue]: ACTION"
    act, problem = parse_action(action.strip())
    if problem:
        return None, problem
    return {"cue": cue, "start": start, "end": end, "action": act}, None


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_rule(cells):
    return all(set(c) <= set("-: ") for c in cells)


def parse_cast_rows(lines, where, problems):
    """The cast rows of a table given as [(line number, text)]; problems appended with `where`."""
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
        if pos is None:
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


def parse_moves(lines, where, in_panel, problems):
    moves = []
    for n, line in lines:
        m = _LIST_RE.match(line.strip())
        if not m:
            problems.append(f"line {n}: {where}: not a move (a list item '- cue N[, TIME]: ACTION'): {line.strip()}")
            continue
        move, problem = parse_move(m.group(1).strip(), in_panel)
        if problem:
            problems.append(f"line {n}: {where}: {problem}")
            continue
        move["line"] = n
        moves.append(move)
    return moves


def parse_sections(scene, sections, problems):
    """Fill `scene['cast']`, `scene['moves']` and `scene['panels']` from the raw lines of its
    `### Cast`, `### Moves`, `### Mistake` and `### Right way` sections ({name: [(n, line)]})."""
    key = scene["key"]
    if "cast" in sections:
        scene["cast"] = parse_cast_rows(_tables_only(sections["cast"], f"scene {key}, cast", problems),
                                        f"scene {key}, cast", problems)
    if "moves" in sections:
        scene["moves"] = parse_moves([(n, ln) for n, ln in sections["moves"] if ln.strip()],
                                     f"scene {key}, moves", False, problems)
    for panel in ("mistake", "right way"):
        if panel not in sections:
            continue
        where = f"scene {key}, {panel}"
        table, moves = [], []
        for n, ln in sections[panel]:
            s = ln.strip()
            if not s:
                continue
            (table if s.startswith("|") else moves if s.startswith("-") else _reject(problems, n, where, s)).append(
                (n, ln))
        scene["panels"][panel] = {"cast": parse_cast_rows(table, where, problems),
                                 "moves": parse_moves(moves, where, True, problems)}


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
