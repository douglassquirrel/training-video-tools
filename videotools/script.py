"""Read a video's script.md (the training-video project's format) into plain data.

The format is `videos/SCRIPT-FORMAT.md` in the training-video project: one `# title`, tables
under `## Settings`, `## Colours` and `## Insets`, then `## Scene <key>: <name>` sections each
with a property table and `### Narration`, `### Side panel`, `### On screen` lists. Anything
else is prose for people and is skipped. Standard library only; runs on Python 3.9.
"""

import os
import re

# The Settings table: key -> required?
SETTINGS = {"title": True, "subtitle": False, "eyebrow": False, "brand": True, "voice": True,
            "speed": True, "language": True, "speech-model": True, "size": True, "fps": True,
            "quality": False, "lead": False, "cue-gap": False, "tail": False, "fade": False,
            "source": True, "source-image": False, "source-label": False,
            "title-image-caption": False, "credit": False, "output": True, "scene-code": True}
NUMBER_SETTINGS = ("speed", "fps", "quality", "lead", "cue-gap", "tail")
FILE_SETTINGS = ("source", "source-image")
SCENE_KEYS = {"kind", "letter", "tracker-label", "eyebrow", "title", "inset", "source",
              "side-panel", "code", "extra"}
CUE_KEYS = {"say", "min", "mistake", "step", "added"}
KINDS = ("title", "step", "end")
SIDE_PANEL = re.compile(r"^(key-points|steps|none)$|^checklist (\d+)$|^custom ([a-z0-9-]+) (\d+)$")
COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
INSET = re.compile(r"^\d+ \d+ \d+ \d+$")
NUMBER = re.compile(r"^\d+(\.\d+)?$")
SIZE = re.compile(r"^\d+x\d+$")

SCENE_HEADING = re.compile(r"^## Scene ([A-Za-z0-9-]+): (.+)$")
TABLE_SECTIONS = {"Settings": "settings", "Colours": "colours", "Insets": "insets"}
LIST_ITEM = re.compile(r"^(?:-|\d+\.)\s+(.+)$")
CUE_ITEM = re.compile(r"^(\d+)\.\s+(.+)$")
SUB_BULLET = re.compile(r"^\s+-\s+([a-z-]+):\s*(.*)$")


def _table_row(line):
    """The (key, value) of a Markdown table row, or None for the header, the rule or junk."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 2 or cells[0].lower() == "key" or set(cells[0]) <= set("-: "):
        return None
    return cells[0], cells[1]


def _new_scene(key, name, line):
    return {"key": key, "name": name, "line": line, "props": {}, "cues": [], "side": [], "screen": []}


def parse(text):
    """Return (data, problems) for the text of a script.

    data: {"title", "settings", "colours", "insets", "scenes"}; each scene {"key", "name",
    "line", "props", "cues", "side", "screen"}; each cue {"n", "text", "line"} plus any
    sub-bullets by name; each side-panel or on-screen item {"text", "line"} plus "added".
    problems: structural faults found while reading, each naming its line.
    """
    problems = []
    data = {"title": None, "settings": {}, "colours": {}, "insets": {}, "scenes": [], "lines": {}}
    section = None      # "settings" | "colours" | "insets" | "scene" | "notes" | None
    sub = None          # the current ### heading inside a scene, lower-cased
    scene = None
    item = None         # the cue or list item that sub-bullets attach to
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("# ") and data["title"] is None:
            data["title"] = line[2:].strip()
            continue
        if line.startswith("## "):
            head = line[3:].strip()
            sub, item, scene = None, None, None
            m = SCENE_HEADING.match(line)
            if m:
                scene = _new_scene(m.group(1), m.group(2).strip(), n)
                data["scenes"].append(scene)
                section = "scene"
            else:
                section = TABLE_SECTIONS.get(head, "notes")
            continue
        if line.startswith("### "):
            sub, item = line[4:].strip().lower(), None
            if section != "scene":
                problems.append("line %d: '%s' outside a scene" % (n, line.strip()))
            continue
        if section in ("settings", "colours", "insets"):
            if line.startswith("|"):
                row = _table_row(line)
                if row:
                    data[section][row[0]] = row[1]
                    data["lines"][(section, row[0])] = n
            continue
        if section != "scene":
            continue
        if sub is None:
            if line.startswith("|"):
                row = _table_row(line)
                if row:
                    scene["props"][row[0]] = row[1]
                    data["lines"][(scene["key"], row[0])] = n
            continue
        if sub == "narration":
            m = CUE_ITEM.match(line)
            if m:
                item = {"n": int(m.group(1)), "text": m.group(2).strip(), "line": n}
                scene["cues"].append(item)
                continue
            m = SUB_BULLET.match(line)
            if m and item is not None:
                item[m.group(1)] = m.group(2).strip()
                continue
            if line.strip():
                problems.append("line %d: scene %s: not a cue or a cue's sub-bullet: %s"
                                % (n, scene["key"], line.strip()[:60]))
            continue
        if sub in ("side panel", "on screen"):
            dest = scene["side"] if sub == "side panel" else scene["screen"]
            m = LIST_ITEM.match(line)
            if m:
                item = {"text": m.group(1).strip(), "line": n}
                dest.append(item)
                continue
            m = SUB_BULLET.match(line)
            if m and item is not None and m.group(1) == "added":
                item["added"] = m.group(2).strip()
                continue
            if line.strip():
                problems.append("line %d: scene %s, %s: not a list item: %s"
                                % (n, scene["key"], sub, line.strip()[:60]))
    return data, problems


def _at(data, section, key):
    """'line N: ' for a table row the parser saw, or '' when there is no line to name."""
    n = data["lines"].get((section, key))
    return "line %d: " % n if n else ""


def brands_root(script_path):
    """The first folder, from the script's folder upwards, that holds `brands/`; or None."""
    folder = os.path.dirname(os.path.abspath(script_path))
    while True:
        if os.path.isdir(os.path.join(folder, "brands")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def check(data, script_path):
    """Every problem with parsed script data, against the format; [] when it is well formed."""
    problems = []
    if not data["title"]:
        problems.append("no '# title' line at the top")
    st = data["settings"]
    for key, required in SETTINGS.items():
        if required and not st.get(key):
            problems.append("Settings: '%s' is missing" % key)
    for key, value in st.items():
        where = _at(data, "settings", key)
        if key not in SETTINGS and not key.startswith("x-"):
            problems.append("%sSettings: unknown key '%s'" % (where, key))
        elif key in NUMBER_SETTINGS and value and not NUMBER.match(value):
            problems.append("%sSettings: '%s' should be a number, not '%s'" % (where, key, value))
        elif key == "size" and value and not SIZE.match(value):
            problems.append("%sSettings: 'size' should look like 1920x1080, not '%s'" % (where, value))
    folder = os.path.dirname(os.path.abspath(script_path))
    for key in FILE_SETTINGS:
        if st.get(key) and not os.path.isfile(os.path.join(folder, st[key])):
            problems.append("%sSettings: '%s' file not found: %s" % (_at(data, "settings", key), key, st[key]))
    brand = st.get("brand")
    if brand:
        root = brands_root(script_path)
        where = _at(data, "settings", "brand")
        if root is None:
            problems.append("%sSettings: brand '%s': no 'brands/' folder in or above %s" % (where, brand, folder))
        elif not os.path.isfile(os.path.join(root, "brands", brand, "BRAND.md")):
            problems.append("%sSettings: brand '%s' has no brands/%s/BRAND.md under %s" % (where, brand, brand, root))
    for key, value in data["colours"].items():
        if not COLOUR.match(value):
            problems.append("%sColours: '%s' is not #RRGGBB: %s" % (_at(data, "colours", key), key, value))
    for key, value in data["insets"].items():
        if not INSET.match(value):
            problems.append("%sInsets: '%s' should be four whole numbers x0 y0 x1 y1: %s"
                            % (_at(data, "insets", key), key, value))
    seen = {}
    for scene in data["scenes"]:
        problems += _check_scene(data, scene, seen)
    return problems


def _side_panel_text(scene):
    """The scene's side-panel setting as written, with the format's default."""
    return scene["props"].get("side-panel", "key-points" if scene["side"] else "none")


def _check_scene(data, scene, seen):
    problems = []
    key, props, where = scene["key"], scene["props"], "line %d: scene %s" % (scene["line"], scene["key"])
    if key in seen:
        problems.append("%s: key used twice (first at line %d)" % (where, seen[key]))
    seen.setdefault(key, scene["line"])

    def at(prop):
        return "line %d: scene %s" % (data["lines"][(key, prop)], key)

    for prop, value in props.items():
        if prop not in SCENE_KEYS and not prop.startswith("x-"):
            problems.append("%s: unknown property '%s'" % (at(prop), prop))
    kind = props.get("kind", "step")
    if kind not in KINDS:
        problems.append("%s: kind must be title, step or end, not '%s'" % (at("kind"), kind))
    if kind == "step" and props.get("letter") and not props.get("source"):
        problems.append("%s: a lettered step needs a 'source'" % where)
    if props.get("inset") and props["inset"] not in data["insets"]:
        problems.append("%s: inset '%s' is not in Insets" % (at("inset"), props["inset"]))
    if "extra" in props and not NUMBER.match(props["extra"]):
        problems.append("%s: extra should be a number of seconds, not '%s'" % (at("extra"), props["extra"]))
    panel = _side_panel_text(scene)
    panel_where = at("side-panel") if "side-panel" in props else where
    m = SIDE_PANEL.match(panel)
    if not m:
        problems.append("%s: side-panel '%s' not understood" % (panel_where, panel))
    elif (panel in ("key-points", "steps") or panel.startswith("checklist")) and not scene["side"]:
        problems.append("%s: side-panel '%s' but no Side panel list" % (panel_where, panel))
    if m and (m.group(2) or m.group(4)):
        cue_n = int(m.group(2) or m.group(4))
        if not 1 <= cue_n <= len(scene["cues"]):
            problems.append("%s: side-panel refers to cue %d, which doesn't exist" % (panel_where, cue_n))
    if kind != "end" and not scene["cues"] and not props.get("extra"):
        problems.append("%s: no narration and no 'extra'" % where)
    mistakes = 0
    for i, cue in enumerate(scene["cues"], 1):
        cue_where = "line %d: scene %s cue %d" % (cue["line"], key, i)
        if cue["n"] != i:
            problems.append("line %d: scene %s: cue numbered %d where %d was expected" % (cue["line"], key, cue["n"], i))
        for sub in cue:
            if sub not in ("n", "text", "line") and sub not in CUE_KEYS:
                problems.append("%s: unknown sub-bullet '%s'" % (cue_where, sub))
        if "min" in cue and not NUMBER.match(cue["min"]):
            problems.append("%s: min should be a number of seconds, not '%s'" % (cue_where, cue["min"]))
        if "mistake" in cue:
            mistakes += 1
            if " / " not in cue["mistake"]:
                problems.append("%s: mistake needs '<wrong> / <right>'" % cue_where)
        if "step" in cue:
            if panel != "steps":
                problems.append("%s: step %s needs 'side-panel: steps'" % (cue_where, cue["step"]))
            elif not cue["step"].isdigit() or not 1 <= int(cue["step"]) <= len(scene["side"]):
                problems.append("%s: step %s is not in the Side panel list (%d item%s)"
                                % (cue_where, cue["step"], len(scene["side"]), "" if len(scene["side"]) == 1 else "s"))
        if "added" in cue and not cue["added"]:
            problems.append("%s: 'added:' must say where it comes from" % cue_where)
    if mistakes > 1:
        problems.append("%s: %d mistakes; one per scene" % (where, mistakes))
    for name, items in (("side panel", scene["side"]), ("on screen", scene["screen"])):
        for item in items:
            if "added" in item and not item["added"]:
                problems.append("line %d: scene %s, %s: 'added:' must say where it comes from" % (item["line"], key, name))
    return problems


class ScriptError(Exception):
    """A script that cannot be used, with every problem found."""

    def __init__(self, path, problems):
        self.path, self.problems = path, list(problems)
        n = len(self.problems)
        super().__init__("%s: %d problem%s:\n%s" % (path, n, "" if n == 1 else "s",
                                                   "\n".join("  - " + p for p in self.problems)))


def read(path):
    """The data of the script at `path`, or ScriptError with every problem."""
    if not os.path.isfile(path):
        raise ScriptError(path, ["no such file: %s" % path])
    with open(path, encoding="utf-8") as f:
        data, problems = parse(f.read())
    problems += check(data, path)
    if problems:
        raise ScriptError(path, problems)
    return data


def folder(path):
    """The video's folder: the script's own."""
    return os.path.dirname(os.path.abspath(path))


DEFAULTS = {"quality": "18", "lead": "0.7", "cue-gap": "0.55", "tail": "1.0", "fade": "0.45 0.4"}
TEXT_SETTINGS = ("title", "subtitle", "eyebrow", "brand", "voice", "language", "speech-model",
                 "source", "source-image", "source-label", "title-image-caption", "credit",
                 "output", "scene-code")


def settings(data):
    """The Settings table with the format's defaults filled in and values typed.

    Text settings are strings ('' when absent); `speed`, `lead`, `cue-gap`, `tail` floats;
    `fps`, `quality` ints; `size` (width, height); `fade` (in, out) seconds.
    """
    st = dict(DEFAULTS)
    st.update({k: v for k, v in data["settings"].items() if v})
    out = {k: st.get(k, "") for k in TEXT_SETTINGS}
    out["speed"] = float(st["speed"])
    out["fps"] = int(st["fps"])
    out["quality"] = int(st["quality"])
    for k in ("lead", "cue-gap", "tail"):
        out[k] = float(st[k])
    w, h = st["size"].split("x")
    out["size"] = (int(w), int(h))
    fade_in, fade_out = st["fade"].split()
    out["fade"] = (float(fade_in), float(fade_out))
    return out


def kind(scene):
    """'title', 'step' or 'end'."""
    return scene["props"].get("kind", "step")


def extra(scene):
    """Seconds the scene holds after its last cue (or, with no cues, its whole length)."""
    return float(scene["props"].get("extra", "0"))


def side_panel(scene):
    """(kind, name, cue): kind is key-points, steps, checklist, custom or none; name only for
    custom; cue only for checklist and custom."""
    m = SIDE_PANEL.match(_side_panel_text(scene))
    if m.group(1):
        return m.group(1), None, None
    if m.group(2):
        return "checklist", None, int(m.group(2))
    return "custom", m.group(3), int(m.group(4))


def spoken(cue):
    """What the voice says: `say:` if given, else the caption."""
    return cue.get("say") or cue["text"]


def minimum(cue):
    """The cue's `min:` in seconds, 0 when none."""
    return float(cue.get("min", "0"))


def mistake(cue):
    """(wrong, right) for the scene's mistake cue, or None."""
    if "mistake" not in cue:
        return None
    wrong, right = cue["mistake"].split(" / ", 1)
    return wrong.strip(), right.strip()


def select(data, keys):
    """The scenes named in a comma-separated list of keys, in that order; all when keys is
    empty or None. An unknown key is a usage error naming the scenes there are."""
    if not keys:
        return list(data["scenes"])
    by_key = {s["key"]: s for s in data["scenes"]}
    wanted = [k.strip() for k in keys.split(",") if k.strip()]
    for k in wanted:
        if k not in by_key:
            from videotools import cli
            raise cli.Failure(f"no scene '{k}' in the script (scenes: {', '.join(by_key)})", cli.USAGE)
    return [by_key[k] for k in wanted]
