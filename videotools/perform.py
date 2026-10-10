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
        if self._under_curtain(name, shows):
            value *= self.tl.before_curtain(self.t)
        return value

    def _under_curtain(self, name, shows):
        """The curtain for free (PLAN.md item 15): a scene member first shown before the mistake
        cue and not named in any move at or after the cue that follows it belongs to the picture
        before the mistake, and fades while the panels cover it."""
        if self.panel or self.tl.mistake is None:
            return False
        first_show = next((a for (a, _b), mv in shows if mv["action"]["kind"] == "show"), None)
        if first_show is None or first_show >= self.tl.start(self.tl.mistake):
            return False
        for mv in self.moves:
            act = mv["action"]
            if mv["cue"] > self.tl.mistake and name in act.get("names", [act.get("name")]):
                return False
        return True

    def anchors_of(self, name, anchor):
        """A member's anchor in frame pixels: what its draw returned once it is drawn (a library
        element's anchors; a piece's real box); else a box anchor from its rect, or a library
        element's fixed anchor scaled into the rect as the element is fitted (uniformly,
        centred). A computed anchor (a row, a cell) exists only once the member is drawn."""
        drawn = self._anchors.get(name, {})
        if anchor in drawn:
            return drawn[anchor]
        rect = self.rect(name)
        if anchor in choreography.BOX_ANCHORS:
            return box_anchors(rect)[anchor]
        element = self.cast[name]["element"]
        if element not in choreography.PIECES:
            el = self.lib.element(element)
            for pattern, value in el["anchors"].items():
                if choreography._anchor_matches(anchor, pattern) and value != "computed":
                    x, y, w, h = rect
                    w0, h0 = el["size"]
                    scale = min(w / w0, h / h0) if w0 and h0 else 1.0
                    return (x + (w - w0 * scale) / 2 + value[0] * scale, y + (h - h0 * scale) / 2 + value[1] * scale)
        raise cli.Failure(f"'{anchor}' of '{name}' is computed when it is drawn, so a member placed by it must "
                          f"come after '{name}' in the cast")

    def rect(self, name):
        if name in self._rects:
            return self._rects[name]
        if name in self._busy:
            raise cli.Failure(f"'{name}' is placed by a member placed by it, round in a circle")
        self._busy.add(name)
        member = self.cast[name]
        if member["where"] is None:             # an arrow with a blank Where: the box its two ends span
            p, _state = self.params(member)
            (x0, y0), (x1, y1) = self._point(p["from"]), self._point(p["to"])
            x, y, w, h = min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)
        else:
            x, y, w, h = base_rect(member, self.area, self.lib, self.anchors_of)
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

    def _kind(self, member, name):
        """The type of a parameter: the library description's, or the piece's (number or a word)."""
        if member["element"] in choreography.PIECES:
            return "number" if choreography.PIECE_PARAMS[member["element"]][name] in ("number", "unit") else "text"
        return choreography._param_match(name, self.lib.element(member["element"])["params"])["type"]

    def _convert(self, kind, value):
        if kind == "rows":
            with open(os.path.join(self.folder, value), encoding="utf-8", newline="") as f:
                return [row for row in csv.reader(f)]
        if kind == "number":
            return float(value)
        if kind == "integer":
            return int(value)
        if kind == "boolean":
            return value in YES
        return value

    def params(self, member):
        """The member's parameters at t: the cast row's, converted by the element's description
        (a data file read into rows; numbers, booleans), then its moves in time order: a number
        animated or set eases over the span (an integer stays whole), a word is set at the
        span's start, a state change is the name after, or (from, to, progress) part-way.
        Returns (params, state) with `state` taken out of the parameters."""
        name = member["name"]
        out, state = {}, None
        for pname, value in member["params"].items():
            if pname == "state":
                state = value
            else:
                out[pname] = self._convert(self._kind(member, pname), value)
        if state is None and member["element"] not in choreography.PIECES:
            state = self.lib.element(member["element"]).get("default-state")
        for (a, b), mv in self._moves_of(name, ("param", "set", "state")):
            if self.t < a:
                break
            p, act = timeline.ep(self.t, a, b), mv["action"]
            if act["kind"] == "state":
                state = act["to"] if p >= 1 else (act["from"], act["to"], p) if p > 0 else state
                continue
            kind = self._kind(member, act["param"])
            if kind in ("number", "integer"):
                start = float(act["from"]) if act["kind"] == "param" else float(out.get(act["param"], act["value"]))
                end = float(act["to"] if act["kind"] == "param" else act["value"])
                value = timeline.lerp(start, end, p)
                out[act["param"]] = int(round(value)) if kind == "integer" else value
            else:
                out[act["param"]] = act["to"] if act["kind"] == "param" else act["value"]
        return out, state

    def draw(self, frame):
        for name, member in self.cast.items():
            alpha = self.alpha(name)
            if alpha <= 0:
                continue
            x, y, w, h = self.rect(name)
            element = member["element"]
            p, state = self.params(member)
            if element == "pill":
                box = frame.tag(p["text"], x, y, size=float(p.get("size", 22)), fill=p.get("fill", "ink"),
                                colour=p.get("colour", "on-accent"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha)
                self._anchors[name] = box_anchors(box)
            elif element == "text":
                size, align = float(p.get("size", 22)), ALIGN[p.get("anchor", "left")]
                width = frame.text(p["text"], x, y, size, role=p.get("role", "body"), colour=p.get("colour", "ink"),
                                   anchor=align, alpha=alpha, check=True)
                left = x if align == "l" else x - width / 2 if align == "c" else x - width
                scaled = frame._size(size)                      # the baseline is at y; the box is the type size
                self._anchors[name] = box_anchors((left, y - scaled * 0.75, width, scaled))
            elif element == "badge":
                r = float(p.get("r", 24))
                frame.badge(x, y, p["ok"] in YES, r=r, alpha=alpha)
                self._anchors[name] = box_anchors((x - r, y - r, 2 * r, 2 * r))
            elif element == "hand":
                frame.hand(x, y, float(p["angle"]), float(p["scale"]), alpha=alpha, mirror=p.get("mirror") in YES,
                           label=p.get("label"))
            elif element == "callout":
                target = self._point(p["target"])
                frame.callout(p["text"], target, (x, y), size=float(p.get("size", 22)), fill=p.get("fill", "surface"),
                              colour=p.get("colour", "ink"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha)
            elif element == "arrow":
                from videotools import draw
                headless = {} if p.get("head", "yes") in YES else {"head": 0}     # draw.arrow's head is its size
                draw.arrow(frame.ctx, [self._point(p["from"]), self._point(p["to"])],
                           frame.colour(p.get("colour", "ink")), lw=float(p.get("width", 6)),
                           progress=float(p.get("progress", 1)), alpha=alpha, **headless)
            else:
                el = self.lib.element(element)
                try:
                    self._anchors[name] = el.draw(frame, (x, y, w, h), state=state, params=p, alpha=alpha)
                except Exception as e:      # the library refuses in words (its Failure) or fails: one line, exit 3
                    raise cli.Failure(f"scene {frame.scene['key']}: the library could not draw '{name}' ({element}): "
                                      f"{e}") from e

    def _point(self, text):
        """A point written as a member's anchor with an optional offset (an arrow's ends, a callout's target)."""
        where = choreography.parse_where(text)
        x, y = self.anchors_of(where["member"], where["anchor"])
        return (x + where["dx"], y + where["dy"])


def draw_scene(frame, video, scene, tl, t):
    """The scene's described cast at t, before the module's draw (if any)."""
    Performance(scene["cast"], scene["moves"], frame.area, tl, t, video.library, folder=video.folder).draw(frame)


def draw_panel(frame, video, scene, panel, rect, tl, t):
    """A described panel's cast, in the panel body's pixels, timed from the panel's rise."""
    p = scene["panels"][panel]
    Performance(p["cast"], p["moves"], rect, tl, t, video.library, panel_start=tl.start(tl.mistake),
                folder=video.folder).draw(frame)
