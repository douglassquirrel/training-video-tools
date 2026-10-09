"""A video's own drawing code: one module per scene, and the frame object it draws with.

The script's `scene-code` folder holds one Python module per scene, named by the scene's
`code` property (optional for a title or end card, which the chrome draws whole). A module
defines `draw(frame)`; `mistake(frame, rect)` and `right_way(frame, rect)` when the scene has a
mistake cue; `panel(frame, rect)` when its side panel is custom.
Standard library only.
"""

import ast
import importlib.util
import os
import sys

from videotools import cli, script


class Frame:
    """What scene code is given: the cairo context (clipped to the area), the time into the
    scene, the timeline, the scene's data, the script's colours as (r, g, b), the brand kit and
    the area's (x, y, w, h). `label(text)` checks a label against the script's On screen list."""

    def __init__(self, ctx, t, timeline, scene, colours, brand, area):
        self.ctx, self.t, self.timeline, self.scene = ctx, t, timeline, scene
        self.colours, self.brand, self.area = colours, brand, area

    def label(self, text):
        listed = [item["text"] for item in self.scene["screen"]]
        if text not in listed:
            raise cli.Failure(f"scene {self.scene['key']}: the scene code draws '{text}', which is not in the "
                              f"script's On screen list ({', '.join(listed)})")
        return text

    # ---- brand-aware drawing: thin layers over videotools.draw that fill in what the brand and
    # script already say (fonts by role, sizes scaled, colours by name, rule 3, the On screen check)

    def colour(self, name):
        """An (r, g, b) by name: the script's Colours first, then the brand's roles."""
        if name in self.colours:
            return self.colours[name]
        if name in self.brand["colours"]:
            return self.brand["colours"][name]
        raise cli.Failure(f"scene {self.scene['key']}: no colour '{name}' in the script's Colours "
                          f"({', '.join(self.colours)}) or the brand's roles ({', '.join(self.brand['colours'])})")

    def _font(self, role):
        fonts = self.brand["fonts"]
        if role not in fonts:
            raise cli.Failure(f"scene {self.scene['key']}: no font role '{role}' in the brand kit ({', '.join(fonts)})")
        return fonts[role]

    def _size(self, size):
        return size * self.brand["settings"]["font-size-scale"]

    def _colour_at(self, name, size):
        """A colour by name for text (or a pill) of `size` px: BRAND.md rule 3, accent below the
        small-text size becomes the darker role."""
        dark_role, limit = self.brand["settings"]["small-text-accent"]
        if name == "accent" and size < limit:
            name = dark_role
        return self.colour(name)

    def text(self, s, x, y, size, role="body", colour="ink", anchor="l", alpha=1.0, track=0, check=False):
        """Text in the brand's font for `role`, `size` scaled, `colour` by name with rule 3;
        `check` runs it through `label`."""
        from videotools import draw
        if check:
            s = self.label(s)
        size = self._size(size)
        draw.text(self.ctx, s, x, y, self._font(role), size, self._colour_at(colour, size), anchor, alpha, track)

    def tag(self, s, x, y, size=22, fill="ink", colour="on-accent", role="display", anchor="l", alpha=1.0,
            padx=14, pady=9, border=None):
        """A pill label, checked against the On screen list; colours by name, rule 3 on the fill."""
        from videotools import draw
        size = self._size(size)
        return draw.tag(self.ctx, self.label(s), x, y, self._font(role), size, self._colour_at(fill, size),
                        self._colour_at(colour, size), anchor, alpha, padx, pady,
                        self.colour(border) if border else None)

    def callout(self, s, target, at, size=22, leader="ink", fill="surface", colour="ink", role="display",
                anchor="l", alpha=1.0):
        """A checked pill at `at` with a leader line to a dot at `target`."""
        from videotools import draw
        size = self._size(size)
        draw.callout(self.ctx, self.label(s), target, at, self._font(role), size, self.colour(leader),
                     self._colour_at(fill, size), self._colour_at(colour, size), anchor, alpha)

    def dimension(self, p0, p1, s, size=24, colour="accent", text_colour="on-accent", role="display", side=1,
                  alpha=1.0):
        """A dimension line with its measurement (checked) in a pill beside it."""
        from videotools import draw
        size = self._size(size)
        draw.dimension(self.ctx, p0, p1, self.label(s), self._font(role), size, self._colour_at(colour, size),
                       self._colour_at(text_colour, size), alpha, side)

    def badge(self, x, y, ok, r=24, alpha=1.0):
        """A ✓ (ok) or ✗ badge in the brand's correct or mistake colour."""
        from videotools import draw
        draw.badge(self.ctx, x, y, ok, self.colour("correct" if ok else "mistake"), self.colour("on-accent"), r, alpha)

    def hand(self, x, y, angle, scale, alpha=1.0, mirror=False, label=None):
        """A mitten hand in the script's `skin`, `skin-dark` and `sleeve` colours (neutral defaults
        otherwise), its letter label on an accent roundel at the brand-scaled size."""
        from videotools import draw
        c = {name: self.colours.get(name, default) for name, default in HAND_DEFAULTS.items()}
        draw.hand(self.ctx, x, y, angle, scale, c["skin"], c["skin-dark"], c["sleeve"], alpha, mirror, label,
                  self.colour("accent"), self.colour("on-accent"), self._font("display"), self._size(28))


# The hand's colours when the script's Colours do not name them: a neutral skin, its outline, a slate sleeve.
HAND_DEFAULTS = {"skin": (0.93, 0.80, 0.66), "skin-dark": (0.45, 0.33, 0.25), "sleeve": (0.30, 0.33, 0.38)}


def needed(scene):
    """The functions a scene's module must define: [(name, signature, why)]."""
    out = [("draw", "(frame)", "")]
    mistake_cue = next((cue for cue in scene["cues"] if "mistake" in cue), None)
    if mistake_cue:
        why = f", and cue {mistake_cue['n']} is a mistake"
        out += [("mistake", "(frame, rect)", why), ("right_way", "(frame, rect)", why)]
    if script.side_panel(scene)[0] == "custom":
        out.append(("panel", "(frame, rect)", f", and its side-panel is '{scene['props']['side-panel']}'"))
    return out


def check_code(folder, data):
    """Every problem with a script's scene code, found without running any of it (check-script):
    a step scene with no `code`, a module that is missing, one that does not parse, one without a
    function the scene needs (a top-level `def`; a function made any other way is not seen).
    Standard library only."""
    if not os.path.isdir(folder):
        return [f"line {data['lines'][('settings', 'scene-code')]}: Settings: scene-code folder not found: {folder}"]
    problems = []
    for scene in data["scenes"]:
        key, code = scene["key"], scene["props"].get("code")
        if not code:
            if script.kind(scene) not in ("title", "end"):
                problems.append(f"line {scene['line']}: scene {key}: no 'code' property, so no scene code can be "
                                "found for it")
            continue
        where = f"line {data['lines'][(key, 'code')]}: scene {key}"
        path = os.path.join(folder, code + ".py")
        if not os.path.isfile(path):
            problems.append(f"{where}: no scene code {path} (the scene's 'code' is '{code}')")
            continue
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), path)
        except SyntaxError as e:
            problems.append(f"{where}: {path} could not be parsed: line {e.lineno}: {e.msg}")
            continue
        defined = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name, signature, why in needed(scene):
            if name not in defined:
                problems.append(f"{where}: {path} has no {name}{signature} function{why}")
    return problems


_loaded = {}


def load(folder, scene):
    """The scene's module from `folder`, checked for the functions the scene needs."""
    code = scene["props"].get("code")
    if not code:
        if script.kind(scene) in ("title", "end"):
            return None                     # the chrome draws the whole card; nothing to add
        raise cli.Failure(f"scene {scene['key']} has no 'code' property, so no scene code can be found for it")
    path = os.path.join(folder, code + ".py")
    if not os.path.isfile(path):
        raise cli.Failure(f"scene {scene['key']}: no scene code {path} (the scene's 'code' is '{code}')")
    if path not in _loaded:
        spec = importlib.util.spec_from_file_location(f"videotools_scene_{code}", path)
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, folder)          # so scene modules can share helpers in their folder
        try:
            spec.loader.exec_module(module)
        except Exception as e:  # the video's own code: any error is reported, none classified
            raise cli.Failure(f"scene {scene['key']}: {path} could not be loaded: {type(e).__name__}: {e}") from e
        finally:
            sys.path.remove(folder)
        _loaded[path] = module
    module = _loaded[path]
    for name, signature, why in needed(scene):
        if not callable(getattr(module, name, None)):
            raise cli.Failure(f"scene {scene['key']}: {path} has no {name}{signature} function{why}")
    return module
