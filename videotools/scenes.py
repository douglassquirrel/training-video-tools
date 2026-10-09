"""A video's own drawing code: one module per scene, and the frame object it draws with.

The script's `scene-code` folder holds one Python module per scene, named by the scene's
`code` property. A module defines `draw(frame)`; `mistake(frame, rect)` and `right_way(frame,
rect)` when the scene has a mistake cue; `panel(frame, rect)` when its side panel is custom.
Standard library only.
"""

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


_loaded = {}


def load(folder, scene):
    """The scene's module from `folder`, checked for the functions the scene needs."""
    code = scene["props"].get("code")
    if not code:
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
    needed = [("draw", "(frame)", "")]
    mistake_cue = next((cue for cue in scene["cues"] if "mistake" in cue), None)
    if mistake_cue:
        why = f", and cue {mistake_cue['n']} is a mistake"
        needed += [("mistake", "(frame, rect)", why), ("right_way", "(frame, rect)", why)]
    if script.side_panel(scene)[0] == "custom":
        needed.append(("panel", "(frame, rect)", f", and its side-panel is '{scene['props']['side-panel']}'"))
    for name, signature, why in needed:
        if not callable(getattr(module, name, None)):
            raise cli.Failure(f"scene {scene['key']}: {path} has no {name}{signature} function{why}")
    return module
