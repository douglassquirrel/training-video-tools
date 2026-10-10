"""Performing a described scene (PLAN.md item 15, "How it is drawn"): where every cast member
is and how visible at a time, from its Where, its shows, hides and moves, eased over their
spans; then each member drawn in cast order, the pieces through the frame's methods and the
library's elements through `el.draw`. Needs nothing beyond what the frame carries.
"""

import csv
import os

from videotools import choreography, cli, timeline

ALIGN = {"left": "l", "centre": "c", "right": "r"}
YES = ("yes", "true")


def region_rect(name, area):
    """A region's rect in frame pixels: the halves and quarters of the area, its middle, or all of it."""
    ax, ay, aw, ah = area
    halves = {"left": (ax, ay, aw / 2, ah), "right": (ax + aw / 2, ay, aw / 2, ah),
              "top-left": (ax, ay, aw / 2, ah / 2), "top-right": (ax + aw / 2, ay, aw / 2, ah / 2),
              "bottom-left": (ax, ay + ah / 2, aw / 2, ah / 2),
              "bottom-right": (ax + aw / 2, ay + ah / 2, aw / 2, ah / 2),
              "centre": (ax + aw / 4, ay + ah / 4, aw / 2, ah / 2), "full": (ax, ay, aw, ah)}
    return halves[name]


def own_size(member, lib):
    """(w, h) the member takes from its Size column and the element's own proportions; a piece
    without a Size is a point."""
    size, element = member["size"], member["element"]
    w0, h0 = (lib.element(element)["size"] if element not in choreography.PIECES else (0.0, 0.0))
    if size is None:
        return float(w0), float(h0)
    if size["h"] is not None:
        return size["w"], size["h"]
    return size["w"], (size["w"] * h0 / w0 if w0 else 0.0)


def base_rect(member, area, lib, anchors_of):
    """The member's rect in frame pixels before any move: from its Where (pixels in the area,
    a region it is fitted into, or another member's anchor plus an offset) and its size."""
    w, h = own_size(member, lib)
    where = member["where"]
    if where["kind"] == "pixels":
        return (area[0] + where["x"], area[1] + where["y"], w, h)
    if where["kind"] == "region":
        rx, ry, rw, rh = region_rect(where["name"], area)
        if member["size"] is None and w and h:
            scale = min(rw / w, rh / h)
            w, h = w * scale, h * scale
        return (rx + (rw - w) / 2, ry + (rh - h) / 2, w, h)
    x, y = anchors_of(where["member"], where["anchor"])
    return (x + where["dx"], y + where["dy"], w, h)


def box_anchors(rect):
    x, y, w, h = rect
    return {"top-left": (x, y), "top-right": (x + w, y), "bottom-left": (x, y + h), "bottom-right": (x + w, y + h),
            "centre": (x + w / 2, y + h / 2)}


def window(move, tl, panel_start):
    """(from, to) in scene seconds for a move: its span against its cue's start and length, or
    against the panel's rise."""
    if move["cue"] is None:
        base, length = panel_start, 0.0
    else:
        base, length = tl.start(move["cue"]), tl.length(move["cue"])

    def at(when):
        ref, offset = when
        return base + (offset if ref == "start" else length + offset)
    return at(move["start"]), at(move["end"])


class Performance:
    """One cast (the scene's or a panel's) at time t: alpha and rect per member, resolved lazily
    so a member placed by another's anchor follows it."""

    def __init__(self, cast, moves, area, tl, t, lib, panel_start=None, folder=None):
        self.cast = {m["name"]: m for m in cast}
        self.moves = moves
        self.area, self.tl, self.t, self.lib, self.folder = area, tl, t, lib, folder
        self.panel = panel_start is not None
        self.panel_start = panel_start or 0.0
        self._rects, self._anchors, self._busy = {}, {}, set()

    def _moves_of(self, name, kinds):
        out = []
        for mv in self.moves:
            act = mv["action"]
            if act["kind"] in kinds and name in act.get("names", [act.get("name")]):
                out.append((window(mv, self.tl, self.panel_start), mv))
        return sorted(out, key=lambda item: item[0])

    def alpha(self, name):
        shows = self._moves_of(name, ("show", "hide"))
        value = 1.0 if self.panel and not any(mv["action"]["kind"] == "show" for _w, mv in shows) else 0.0
        for (a, b), mv in shows:
            if self.t < a:
                break
            target = 1.0 if mv["action"]["kind"] == "show" else 0.0
            value = timeline.lerp(value, target, timeline.ep(self.t, a, b))
        return value

    def anchors_of(self, name, anchor):
        """A member's anchor in frame pixels: a box anchor from its rect; a computed one from
        what its draw returned, if it has been drawn."""
        rect = self.rect(name)
        if anchor in choreography.BOX_ANCHORS:
            return box_anchors(rect)[anchor]
        drawn = self._anchors.get(name)
        if drawn is None or anchor not in drawn:
            raise cli.Failure(f"'{anchor}' of '{name}' is computed when it is drawn, so a member placed by it must "
                              f"come after '{name}' in the cast")
        return drawn[anchor]

    def rect(self, name):
        if name in self._rects:
            return self._rects[name]
        if name in self._busy:
            raise cli.Failure(f"'{name}' is placed by a member placed by it, round in a circle")
        self._busy.add(name)
        member = self.cast[name]
        rect = base_rect(member, self.area, self.lib, self.anchors_of)
        x, y, w, h = rect
        for (a, b), mv in self._moves_of(name, ("move",)):
            if self.t < a:
                break
            to = dict(member, where=mv["action"]["to"])
            tx, ty, _tw, _th = base_rect(to, self.area, self.lib, self.anchors_of)
            p = timeline.ep(self.t, a, b)
            x, y = timeline.lerp(x, tx, p), timeline.lerp(y, ty, p)
        self._busy.discard(name)
        self._rects[name] = (x, y, w, h)
        return self._rects[name]

    def params(self, member):
        """The cast row's parameters converted by the element's description (a data file read
        into rows; numbers, booleans), with `state` taken out."""
        el = self.lib.element(member["element"])
        out, state = {}, None
        for name, value in member["params"].items():
            if name == "state":
                state = value
                continue
            desc = choreography._param_match(name, el["params"])
            kind = desc["type"]
            if kind == "rows":
                with open(os.path.join(self.folder, value), encoding="utf-8", newline="") as f:
                    out[name] = [row for row in csv.reader(f)]
            elif kind == "number":
                out[name] = float(value)
            elif kind == "integer":
                out[name] = int(value)
            elif kind == "boolean":
                out[name] = value in YES
            else:
                out[name] = value
        return out, state or el.get("default-state")

    def draw(self, frame):
        for name, member in self.cast.items():
            alpha = self.alpha(name)
            if alpha <= 0:
                continue
            x, y, w, h = self.rect(name)
            element, p = member["element"], member["params"]
            if element == "pill":
                frame.tag(p["text"], x, y, size=float(p.get("size", 22)), fill=p.get("fill", "ink"),
                          colour=p.get("colour", "on-accent"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha)
            elif element == "text":
                frame.text(p["text"], x, y, float(p.get("size", 22)), role=p.get("role", "body"),
                           colour=p.get("colour", "ink"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha,
                           check=True)
            elif element == "badge":
                frame.badge(x, y, p["ok"] in YES, r=float(p.get("r", 24)), alpha=alpha)
            elif element == "hand":
                frame.hand(x, y, float(p["angle"]), float(p["scale"]), alpha=alpha, mirror=p.get("mirror") in YES,
                           label=p.get("label"))
            elif element == "callout":
                target = self._point(p["target"])
                frame.callout(p["text"], target, (x, y), size=float(p.get("size", 22)), fill=p.get("fill", "surface"),
                              colour=p.get("colour", "ink"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha)
            elif element == "arrow":
                from videotools import draw
                draw.arrow(frame.ctx, [self._point(p["from"]), self._point(p["to"])],
                           frame.colour(p.get("colour", "ink")), lw=float(p.get("width", 6)), alpha=alpha)
            else:
                params, state = self.params(member)
                el = self.lib.element(element)
                self._anchors[name] = el.draw(frame, (x, y, w, h), state=state, params=params, alpha=alpha)

    def _point(self, text):
        where = choreography.parse_where(text)
        return self.anchors_of(where["member"], where["anchor"])


def draw_scene(frame, video, scene, tl, t):
    """The scene's described cast at t, before the module's draw (if any)."""
    Performance(scene["cast"], scene["moves"], frame.area, tl, t, video.library, folder=video.folder).draw(frame)


def draw_panel(frame, video, scene, panel, rect, tl, t):
    """A described panel's cast, in the panel body's pixels, timed from the panel's rise."""
    p = scene["panels"][panel]
    Performance(p["cast"], p["moves"], rect, tl, t, video.library, panel_start=tl.start(tl.mistake),
                folder=video.folder).draw(frame)
