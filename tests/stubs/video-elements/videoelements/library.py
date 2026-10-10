"""A stub of `videoelements.library`: reads ELEMENT.md, PROVENANCE.md and licenses/SOURCES.md
in the settled rows into the plain data the real reader exposes. Checks little."""

import builtins
import os

from videoelements.cli import Failure

DRAWN_HERE = "Drawn here"


def _tables(path):
    """{heading: {key: value}} for every `| Key | Value |` table under a `##` heading."""
    out, heading = {}, None
    with builtins.open(path, encoding="utf-8") as f:   # `open` below is the library's
        for raw in f:
            line = raw.strip()
            if line.startswith("## "):
                heading = line[3:].strip()
                out.setdefault(heading, {})
            elif line.startswith("|") and heading:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 2 and cells[0].lower() != "key" and not set(cells[0]) <= set("-: "):
                    out[heading][cells[0]] = cells[1]
    return out


def _param(value):
    kind, _, rest = value.partition(" ")
    if kind in ("number", "integer"):
        lo, hi, default = rest.split()
        conv = float if kind == "number" else int
        return {"type": kind, "min": conv(lo), "max": conv(hi), "default": conv(default)}
    if kind == "colour":
        return {"type": "colour", "default": rest}
    if kind == "boolean":
        return {"type": "boolean", "default": rest == "true"}
    if kind in ("text", "label"):
        return {"type": kind, "default": rest}
    if kind == "rows":
        return {"type": "rows"}
    raise Failure(f"stub library: unknown parameter type '{kind}'")


def _anchor(value):
    return "computed" if value == "computed" else tuple(float(v) for v in value.split())


def _element(folder):
    t = _tables(os.path.join(folder, "ELEMENT.md"))
    ident = t["Identity"]
    w, h = ident["size"].split()
    states = dict(t.get("States", {}))
    return {"name": ident["name"], "kind": ident["kind"], "size": (float(w), float(h)),
            "description": ident.get("description", ""),
            "default-state": ident.get("default-state", next(iter(states), None)),
            "anchors": {k: _anchor(v) for k, v in t.get("Anchors", {}).items()},
            "states": states,
            "params": {k: _param(v) for k, v in t.get("Parameters", {}).items()},
            "colours": dict(t.get("Colours", {})),
            "provenance": _provenance(folder), "folder": folder}


def _provenance(folder):
    out = []
    for heading, table in _tables(os.path.join(folder, "PROVENANCE.md")).items():
        out.append({"source": heading, "licence": table.get("licence", ""), "line": 0})
    return out


def _register(path):
    out = {}
    with builtins.open(path, encoding="utf-8") as f:   # `open` below is the library's
        for raw in f:
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if len(cells) >= 5 and cells[0] not in ("Source", "") and not set(cells[0]) <= set("-: "):
                out[cells[0]] = {"licence": cells[1], "credit": cells[3], "category": cells[4]}
    return out


class Element(dict):
    def __init__(self, data, library):
        super().__init__(data)
        self.library = library

    def draw(self, frame, rect, state=None, params=None, alpha=1.0):
        """The stub's drawing: the rect filled with the brand's accent at `alpha` (a cross-fade
        part-way draws the same); the call recorded in `library.draws`; anchors returned in frame
        pixels: fixed ones scaled into the rect, `row.N` down the right edge and `cell.N.M` across
        the rows for a `rows` parameter, any other computed one at the rect's top-left."""
        params = dict(params or {})
        if params.get("explode"):
            raise Failure(f"element '{self['name']}': its draw failed: Failure: no font role 'mono' in the brand kit")
        x, y, w, h = rect
        self.library.draws.append({"name": self["name"], "rect": tuple(float(v) for v in rect), "state": state,
                                   "params": params, "alpha": alpha})
        if alpha > 0:
            frame.ctx.save()
            frame.ctx.rectangle(x, y, w, h)
            frame.ctx.set_source_rgba(*frame.colour("accent"), alpha)
            frame.ctx.fill()
            frame.ctx.restore()
        w0, h0 = self["size"]
        anchors = {}
        for name, value in self["anchors"].items():
            if value == "computed":
                anchors[name] = (x, y)
            else:
                anchors[name] = (x + value[0] * w / w0, y + value[1] * h / h0)
        rows = params.get("rows") or []
        for i in range(1, len(rows) + 1):
            anchors[f"row.{i}"] = (x + w, y + h * i / (len(rows) + 1))
            for j in range(1, len(rows[i - 1]) + 1):
                anchors[f"cell.{i}.{j}"] = (x + w * j / (len(rows[i - 1]) + 1), y + h * i / (len(rows) + 1))
        return anchors


class Library:
    def __init__(self, path, renderer, register, elements):
        self.path, self.renderer, self.register = path, renderer, register
        self._elements = {n: Element(d, self) for n, d in elements.items()}
        self.draws = []                      # every draw call, for the tests

    def names(self):
        return sorted(self._elements)

    def element(self, name):
        if name not in self._elements:
            raise Failure(f"no element '{name}' in {os.path.join(self.path, 'elements')} ({', '.join(self.names())})")
        return self._elements[name]

    def credits(self, names):
        seen = {e["source"] for n in names for e in self.element(n)["provenance"] if e["source"] != DRAWN_HERE}
        lines = [{"category": self.register[s]["category"], "credit": self.register[s]["credit"],
                  "licence": self.register[s]["licence"]} for s in seen]
        return sorted(lines, key=lambda c: (c["category"], c["credit"]))


def open(path, renderer="rsvg-convert"):
    path = os.fspath(path)
    if not os.path.isdir(path):
        raise Failure(f"{path}: library folder not found")
    elements_dir, register_path = os.path.join(path, "elements"), os.path.join(path, "licenses", "SOURCES.md")
    problems = [f"{p}: {what} not found" for p, what in ((elements_dir, "folder"), (register_path, "file"))
                if not os.path.exists(p)]
    if problems:
        raise Failure(problems)
    elements = {name: _element(os.path.join(elements_dir, name)) for name in sorted(os.listdir(elements_dir))
                if os.path.isfile(os.path.join(elements_dir, name, "ELEMENT.md"))}
    return Library(path, renderer, _register(register_path), elements)
