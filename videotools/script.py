"""Read a video's script.md (the training-video project's format) into plain data.

The format is `videos/SCRIPT-FORMAT.md` in the training-video project: one `# title`, tables
under `## Settings`, `## Colours` and `## Insets`, then `## Scene <key>: <name>` sections each
with a property table and `### Narration`, `### Side panel`, `### On screen` lists. Anything
else is prose for people and is skipped. Standard library only; runs on Python 3.9.
"""

import re

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
    data = {"title": None, "settings": {}, "colours": {}, "insets": {}, "scenes": []}
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
            continue
        if section != "scene":
            continue
        if sub is None:
            if line.startswith("|"):
                row = _table_row(line)
                if row:
                    scene["props"][row[0]] = row[1]
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
