"""Read a brand kit's BRAND.md into colours, fonts, mark, illustration and settings.

The convention is the training-video project's (BRAND.md, "How this file is read"): the tables
under Identity, Colours, Fonts, Mark, Illustration and Settings are read, first column the key,
second the value, and for Fonts the third the file; paths are relative to the kit's folder.
Standard library only; runs on Python 3.9.
"""

import os
import re

from videotools import script

TABLES = ("identity", "colours", "fonts", "mark", "illustration", "settings")
COLOUR_ROLES = ("background", "surface", "ink", "muted", "rule", "grid", "accent", "accent-dark",
                "accent-light", "mistake", "correct", "on-accent")
FONT_ROLES = ("display", "body", "italic")
FONT_FALLBACKS = {"display-medium": "display", "body-medium": "body", "bold": "display",
                  "italic-medium": "italic"}
IDENTITY_KEYS = ("name", "website")
SETTING_DEFAULTS = {"font-size-scale": "1.0", "background-grid": "dots 40 2 0.55", "caption-band": "ink",
                    "caption-rule": "accent 4", "small-text-accent": "accent-dark 24",
                    "title-rule": "accent 3", "label-shape": "pill"}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
NUMBER = re.compile(r"^\d+(\.\d+)?$")


class BrandError(Exception):
    """A brand kit that cannot be used, with every problem found."""

    def __init__(self, folder, problems):
        self.folder, self.problems = folder, list(problems)
        super().__init__("{}: {}".format(folder, "\n".join(self.problems)))


def rgb(hex_colour):
    """'#RRGGBB' as an (r, g, b) triple in 0–1."""
    h = hex_colour.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _tables(text):
    """{heading: [(key, value, third)]} for every '## Heading' with a `| Key | Value |` table under
    it. A table with any other header (the contrast table) is for people and skipped."""
    tables, heading, reading = {}, None, False
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            heading, reading = m.group(1).lower(), False
            continue
        if not line.startswith("|"):
            reading = False                           # a table ends at its first non-table line
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not reading:                               # the first line of a table is its header
            reading = heading is not None and len(cells) >= 2 and [c.lower() for c in cells[:2]] == ["key", "value"]
            if reading:
                tables.setdefault(heading, [])        # a header alone still makes the table
            continue
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        tables[heading].append((cells[0], cells[1], cells[2] if len(cells) > 2 else ""))
    return tables


def _role_and_number(value, what, name, problems):
    parts = value.split()
    if len(parts) == 2 and NUMBER.match(parts[1]):
        return parts[0], float(parts[1]) if "." in parts[1] else int(parts[1])
    problems.append(f"Settings: '{name}' should be '{what}', not '{value}'")
    return None


def _settings(rows, problems):
    raw = dict(SETTING_DEFAULTS)
    raw.update({k: v for k, v, _ in rows})
    out = {}
    v = raw["font-size-scale"]
    if NUMBER.match(v):
        out["font-size-scale"] = float(v)
    else:
        problems.append(f"Settings: 'font-size-scale' should be a number, not '{v}'")
    v = raw["background-grid"]
    parts = v.split()
    if v == "none":
        out["background-grid"] = None
    elif len(parts) == 4 and parts[0] == "dots" and all(NUMBER.match(p) for p in parts[1:]):
        out["background-grid"] = ("dots", int(parts[1]), int(parts[2]), float(parts[3]))
    else:
        problems.append(f"Settings: 'background-grid' should be 'dots SPACING SIZE OPACITY' or 'none', not '{v}'")
    out["caption-band"] = raw["caption-band"]
    for key in ("caption-rule", "title-rule"):
        out[key] = _role_and_number(raw[key], "ROLE HEIGHT", key, problems)
    out["small-text-accent"] = _role_and_number(raw["small-text-accent"], "ROLE SIZE", "small-text-accent", problems)
    out["label-shape"] = raw["label-shape"]
    return out


def read(folder):
    """The brand kit in `folder`: {"folder", "identity", "colours", "fonts", "font_files",
    "mark", "illustration", "settings"}, or BrandError with every problem."""
    folder = os.path.abspath(folder)
    path = os.path.join(folder, "BRAND.md")
    if not os.path.isfile(path):
        raise BrandError(folder, [f"no BRAND.md in {folder}"])
    with open(path, encoding="utf-8") as f:
        tables = _tables(f.read())
    problems = []
    rows = {name: tables.get(name, []) for name in TABLES}

    def present(name):
        """Whether the table is there; a missing one is a problem, reported in its place."""
        if name in tables:
            return True
        problems.append(f"no '{name.title()}' table")
        return False

    identity = {k: v for k, v, _ in rows["identity"]}
    for key in IDENTITY_KEYS:
        if present("identity") and not identity.get(key):
            problems.append(f"Identity: '{key}' is missing")
    colours = {}
    for key, value, _ in rows["colours"]:
        if HEX.match(value):
            colours[key] = rgb(value)
        else:
            problems.append(f"Colours: '{key}' is not #RRGGBB: {value}")
    for role in COLOUR_ROLES:
        if present("colours") and role not in {k for k, _, _ in rows["colours"]}:
            problems.append(f"Colours: '{role}' is missing")
    fonts, files = {}, {}
    for role, name, file in rows["fonts"]:
        fonts[role] = name
        files[role] = os.path.join(folder, file)
        if not os.path.isfile(files[role]):
            problems.append(f"Fonts: file for '{role}' not found: {files[role]}")
    for role in FONT_ROLES:
        if present("fonts") and role not in fonts:
            problems.append(f"Fonts: '{role}' is missing")
    for role, fallback in FONT_FALLBACKS.items():
        if role not in fonts and fallback in fonts:
            fonts[role] = fonts[fallback]
    mark = {k: v for k, v, _ in rows["mark"]}
    if present("mark"):
        for key in ("letter", "wordmark"):
            if not mark.get(key):
                problems.append(f"Mark: '{key}' is missing")
    illustration = {k: os.path.join(folder, v) for k, v, _ in rows["illustration"]}
    if present("illustration") and "end-card" not in illustration:
        problems.append("Illustration: 'end-card' is missing")
    for key, file in illustration.items():
        if not os.path.isfile(file):
            problems.append(f"Illustration: file for '{key}' not found: {file}")
    settings = _settings(rows["settings"], problems)
    if problems:
        raise BrandError(folder, problems)
    return {"folder": folder, "identity": identity, "colours": colours, "fonts": fonts,
            "font_files": files, "mark": mark, "illustration": illustration, "settings": settings}


def colour(kit, value):
    """The (r, g, b) of a colour role, or of a '#RRGGBB' value."""
    if value in kit["colours"]:
        return kit["colours"][value]
    if HEX.match(value):
        return rgb(value)
    raise BrandError(kit["folder"], [f"no colour role '{value}' in the brand kit (and it is not #RRGGBB)"])


def text_colour(kit, role, size):
    """The colour for text in `role` at `size` px: accent below the small-text size uses the
    darker role (BRAND.md rule 3)."""
    dark_role, limit = kit["settings"]["small-text-accent"]
    if role == "accent" and size < limit:
        role = dark_role
    return colour(kit, role)


def folder_for(script_path, name):
    """The folder of the brand `name` a script names: brands/<name> at the first folder above
    the script that has brands/."""
    root = script.brands_root(script_path)
    return None if root is None else os.path.join(root, "brands", name)
