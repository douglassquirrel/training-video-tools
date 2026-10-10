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
_TIME = rf"end(?:[+-]{NUM})?|{NUM}"
_SPAN_RE = re.compile(rf"^(?P<a>{_TIME})(?:\s*[–-]\s*(?P<b>{_TIME}))?\s*s$|^(?P<over>over the cue)$")
_SCENE_MOVE_RE = re.compile(r"^cue (\d+)(?:, ([^:]+))?: (.+)$")
_PANEL_MOVE_RE = re.compile(r"^(?:([^:]+): )?(.+)$")
_VALUE = r'"[^"]*"|\S+'
_SHOW_RE = re.compile(rf"^(show|hide|keep) ({NAME}(?:, {NAME})*)$")
_MOVE_RE = re.compile(rf"^move ({NAME}) to (.+)$")
_ANIMATE_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE}) (?:→|->) ({_VALUE})$")
_SET_RE = re.compile(rf"^({NAME})\.({DOTTED}) ({_VALUE})$")
_STATE_RE = re.compile(rf"^({NAME}) ([a-z][a-z0-9-]*) (?:→|->) ([a-z][a-z0-9-]*)$")
_LIST_RE = re.compile(r"^-\s+(.+)$")

WHERE_HELP = ("is not X Y in area pixels, a region ({}) or a member's anchor like sample.row.3 + 40 -12"
              .format(", ".join(REGIONS)))
ACTION_HELP = ("is not show NAME, hide NAME, keep NAME, move NAME to WHERE, NAME.PARAM A → B, NAME.PARAM VALUE "
               "or NAME STATE → STATE")


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
        if not eq or not re.match(rf"^(?:{DOTTED}|colour\.[a-z][a-z0-9-]*)$", name):
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


CUELESS = {"panel": "a panel's moves have no 'cue N': times count from the panel's rise",
           "scene": "the scene has no cues, so its moves have no 'cue N': times count from the scene's start"}


def parse_move(text, cueless=None):
    """({cue, start, end, action}, problem) for the text of one move list item. `cueless` is
    'panel' or 'scene' where moves are written without a cue (a panel; a scene that has none)."""
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
        if rows and index is not None and index > rows[1]:
            return f"'{target}'.'{anchor}', but {rows[0]} has {rows[1]} rows"
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


def _rows_file(m, lib, folder):
    """(file as written, its row count) for a library member whose `rows` parameter names a
    readable CSV under the video's folder; else None."""
    if m["element"] in PIECES or lib is None or folder is None or "rows" not in m["params"]:
        return None
    path = os.path.join(folder, m["params"]["rows"])
    if not os.path.isfile(path):
        return None
    import csv
    with open(path, encoding="utf-8", newline="") as f:
        return m["params"]["rows"], sum(1 for _ in csv.reader(f))


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
    return None


def _index_problem(name, rows):
    index = _first_index(name)
    if index == 0:
        return f"'{name}' counts from 1"
    if rows and index is not None and index > rows[1]:
        return f"'{name}': {rows[0]} has {rows[1]} rows"
    return None


def _state_problem(el, state):
    if not el["states"]:
        return f"{_a(el['name'])} has no states"
    if state not in el["states"]:
        return f"{_a(el['name'])} has no state '{state}' (its states are {', '.join(el['states'])})"
    return None


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
        if name.startswith(OWN_COLOUR):
            problem = _own_colour_problem(el, name, value, ctx["colours"])
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
    ref, offset = when
    return offset if ref == "start" else tl.length(cue) + offset


def _in_scene(tl, when):
    """Seconds into a scene with no cues for a move's time: from its start, or back from its end."""
    ref, offset = when
    return offset if ref == "start" else tl.total + offset


def _check_moves(scene, ctx, moves, where, tl, panel):
    """([members never shown], [problems]) for a cast's moves."""
    members, lib = ctx["members"], ctx["lib"]
    problems, events = [], []
    for mv in moves:
        at = f"line {mv['line']}: {where}: "
        cue, act = mv["cue"], mv["action"]
        if cue is None and not panel:           # a scene with no cues: times from its start, `end` its end
            for when in (mv["start"], mv["end"]):
                if _in_scene(tl, when) > tl.total + 1e-9:
                    problems.append(f"{at}{_secs(_in_scene(tl, when))} s is past the end of the scene, which is "
                                    f"{tl.total:.1f} s long")
                    break
        elif not panel:
            if not 1 <= cue <= len(scene["cues"]):
                problems.append(f"{at}cue {cue}: the scene has {len(scene['cues'])} cues")
                continue
            length = tl.length(cue)
            for when in (mv["start"], mv["end"]):
                t = _resolve(tl, cue, when)
                if t > length + 1e-9:
                    note = ESTIMATE_NOTE if cue in tl.estimated else ""
                    problems.append(f"{at}{_secs(t)} s is past the end of cue {cue}, which is {length:.1f} s "
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
        if act["kind"] in ("show", "hide"):
            t = (mv["start"][1] if panel else _in_scene(tl, mv["start"]) if cue is None
                 else tl.start(cue) + _resolve(tl, cue, mv["start"]))
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
    never = set(members)
    for _t, line, kind, n, cue in sorted(events, key=lambda e: (e[0], e[1])):
        at = f"line {line}: {where}: "
        if kind == "show":
            never.discard(n)
            if shown[n] is not None:        # never 0 here: a member with a show is not shown from the start
                when = "" if cue is None else f" at cue {cue}"
                problems.append(f"{at}'{n}' is shown again{when} while still shown (shown at line {shown[n]}, "
                                "not hidden since)")
            shown[n] = line
        else:
            if shown[n] is None:
                when = "" if cue is None else f" at cue {cue}"
                problems.append(f"{at}'{n}' is hidden{when} but was not shown")
            shown[n] = None
    return never, sorted(problems, key=lambda p: int(p.split(":")[0].split()[1]))
