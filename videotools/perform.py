"""Performing a described scene (PLAN.md item 15, "How it is drawn"): where every cast member
is and how visible at a time, from its Where, its shows, hides and moves, eased over their
spans; then each member drawn in cast order, the pieces through the frame's methods and the
library's elements through `el.draw`. Needs nothing beyond what the frame carries.
"""

import copy
import csv
import math
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


def own_size(member, lib, natural=None):
    """(w, h) the member takes from its Size column and the element's own proportions; a piece
    without a Size is a point, and an element without one that offers its natural size (`natural`)
    takes that."""
    size, element = member["size"], member["element"]
    w0, h0 = (lib.element(element)["size"] if element not in choreography.PIECES else (0.0, 0.0))
    if size is None:
        return natural or (float(w0), float(h0))
    if size["h"] is not None:
        return size["w"], size["h"]
    return size["w"], (size["w"] * h0 / w0 if w0 else 0.0)


def base_rect(member, area, lib, anchors_of, natural=None):
    """The member's rect in frame pixels before any move: from its Where (pixels in the area,
    a region it is fitted into, or centred in at its natural size, or another member's anchor
    plus an offset) and its size."""
    w, h = own_size(member, lib, natural)
    where = member["where"]
    if where["kind"] == "pixels":
        return (area[0] + where["x"], area[1] + where["y"], w, h)
    if where["kind"] == "region":
        rx, ry, rw, rh = region_rect(where["name"], area)
        if member["size"] is None and natural is None and w and h:
            scale = min(rw / w, rh / h)
            w, h = w * scale, h * scale
        return (rx + (rw - w) / 2, ry + (rh - h) / 2, w, h)
    x, y = anchors_of(where["member"], where["anchor"])
    return (x + where["dx"], y + where["dy"], w, h)


def box_anchors(rect):
    x, y, w, h = rect
    return {"top-left": (x, y), "top-right": (x + w, y), "bottom-left": (x, y + h), "bottom-right": (x + w, y + h),
            "centre": (x + w / 2, y + h / 2)}


def turn(point, centre, degrees):
    """`point` turned `degrees` clockwise (as the frame is seen, y downward) about `centre`."""
    a = math.radians(degrees)
    dx, dy = point[0] - centre[0], point[1] - centre[1]
    return (centre[0] + dx * math.cos(a) - dy * math.sin(a), centre[1] + dx * math.sin(a) + dy * math.cos(a))


def progress(t, a, b, move):
    """How far a move has got at t over its span a to b, 0 to 1: eased, or at a steady rate when
    the move is marked linear."""
    return (timeline.prog if move.get("linear") else timeline.ep)(t, a, b)


class Performance:
    """One cast (the scene's or a panel's) at time t: alpha and rect per member, resolved lazily
    so a member placed by another's anchor follows it."""

    def __init__(self, cast, moves, area, tl, t, lib, panel_start=None, folder=None):
        self.cast = {m["name"]: m for m in cast}
        self.moves = moves
        self.area, self.tl, self.t, self.lib, self.folder = area, tl, t, lib, folder
        self.panel = panel_start is not None       # a panel's moves count from its rise, the mistake cue's start
        self._rects, self._anchors, self._busy, self._params, self._frame = {}, {}, set(), {}, None

    def _moves_of(self, name, kinds):
        out = []
        for mv in self.moves:
            act = mv["action"]
            if act["kind"] in kinds and name in act.get("names", [act.get("name")]):
                out.append((choreography.window(mv, self.tl, self.panel), mv))
        return sorted(out, key=lambda item: item[0])

    def alpha(self, name):
        shows = self._moves_of(name, ("show", "hide", "dim"))
        value = 1.0 if self.panel and not any(mv["action"]["kind"] == "show" for _w, mv in shows) else 0.0
        for (a, b), mv in shows:
            if self.t < a:
                break
            act = mv["action"]
            target = 1.0 if act["kind"] == "show" else 0.0 if act["kind"] == "hide" else act["level"]
            value = timeline.lerp(value, target, progress(self.t, a, b, mv))
        if self._under_curtain(name, shows):
            value *= self.tl.before_curtain(self.t)
        for (a, b), mv in self._moves_of(name, ("flash",)):     # a sine between its low and 1, over its span only
            if a <= self.t < b:
                act = mv["action"]
                beat = math.sin(2 * math.pi * (act["rate"] * (self.t - a) + act["phase"]))
                value *= act["low"] + (1 - act["low"]) * (0.5 + 0.5 * beat)
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
        for mv in self.moves:               # named at the cue its span ends in; to the scene's end, at every cue
            act = mv["action"]
            last = math.inf if mv["end"][0] == "scene" else mv.get("end_cue", mv["cue"])
            if act["kind"] != "flash" and last > self.tl.mistake and name in act.get("names", [act.get("name")]):
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
            return self._turned(name, box_anchors(rect)[anchor], rect)
        element = self.cast[name]["element"]
        if element not in choreography.PIECES:
            el = self.lib.element(element)
            for pattern, value in el["anchors"].items():
                if choreography._anchor_matches(anchor, pattern) and value != "computed":
                    x, y, w, h = rect
                    w0, h0 = el["size"]
                    scale = min(w / w0, h / h0) if w0 and h0 else 1.0
                    fixed = (x + (w - w0 * scale) / 2 + value[0] * scale, y + (h - h0 * scale) / 2 + value[1] * scale)
                    return self._turned(name, fixed, rect)
        if name in self._anchors:               # drawn, and it gave no such anchor: a windowed sheet's row, say
            raise cli.Failure(f"'{name}' did not give the anchor '{anchor}' when it was drawn: a row or a cell that "
                              f"is not among those on show has none")
        raise cli.Failure(f"'{anchor}' of '{name}' is computed when it is drawn, so a member placed by it must "
                          f"come after '{name}' in the cast")

    def _turned(self, name, point, box):
        """A point of a member not yet drawn, turned as the member will be about its box's centre."""
        degrees = self.params(self.cast[name])[0].get(choreography.ROTATE, 0.0)
        return turn(point, (box[0] + box[2] / 2, box[1] + box[3] / 2), degrees) if degrees else point

    def rect(self, name):
        if name in self._rects:
            return self._rects[name]
        if name in self._busy:
            raise cli.Failure(f"'{name}' is placed by a member placed by it, round in a circle")
        self._busy.add(name)
        member, natural = self.cast[name], None
        if member["where"] is None:             # an arrow with a blank Where: the box its two ends span
            p, _state = self.params(member)
            (x0, y0), (x1, y1) = self._point(p["from"]), self._point(p["to"])
            x, y, w, h = min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)
        else:
            natural = self._natural(member)
            x, y, w, h = base_rect(member, self.area, self.lib, self.anchors_of, natural)
        for (a, b), mv in self._moves_of(name, ("move",)):
            if self.t < a:
                break
            to = dict(member, where=mv["action"]["to"])
            tx, ty, _tw, _th = base_rect(to, self.area, self.lib, self.anchors_of, natural)
            p = progress(self.t, a, b, mv)
            x, y = timeline.lerp(x, tx, p), timeline.lerp(y, ty, p)
        self._busy.discard(name)
        self._rects[name] = (x, y, w, h)
        return self._rects[name]

    def _natural(self, member):
        """(w, h) for a library member with a blank Size whose element offers its natural size
        (its `fit` is `natural`), asked with the parameters it is drawn with; else None."""
        if member["size"] is not None or member["element"] in choreography.PIECES:
            return None
        el = self.lib.element(member["element"])
        if el["fit"] != "natural":
            return None
        params = self.params(member)[0]
        params.pop(choreography.ROTATE, None)       # the turn is ours, not one of the element's parameters
        try:
            w, h = el.natural_size(self._frame, params)
        except Exception as e:              # the library refuses in words (its Failure) or fails: one line, exit 3
            raise cli.Failure(f"scene {self._frame.scene['key']}: the library could not size '{member['name']}' "
                              f"({member['element']}): {e}") from e
        return float(w), float(h)

    def _kind(self, member, name):
        """The type of a parameter: the library description's, or the piece's (number, or a word:
        never `text`, which for a library element may name a file to read)."""
        if name == choreography.ROTATE:
            return "number"
        if member["element"] in choreography.PIECES:
            return "number" if choreography.PIECE_PARAMS[member["element"]][name] in ("number", "unit") else "word"
        return choreography._param_match(name, self.lib.element(member["element"])["params"])["type"]

    def _convert(self, kind, value):
        if kind == "rows":
            with open(os.path.join(self.folder, value), encoding="utf-8", newline="") as f:
                return [row for row in csv.reader(f)]
        if kind == "text":                      # a file under the video's folder, or the text itself
            path = choreography.text_file(self.folder, value)
            if path:
                with open(path, encoding="utf-8") as f:
                    return f.read()
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
        if name not in self._params:        # once a frame: asked for the natural size, then for the draw
            self._params[name] = self._params_at_t(member)
        out, state = self._params[name]
        return dict(out), state

    def _params_at_t(self, member):
        name = member["name"]
        out, state = {}, None
        for pname, value in member["params"].items():
            if pname == "state":
                state = value
            elif not (pname.startswith(choreography.OWN_COLOUR) or choreography.is_qualifier(pname)):
                kind = self._kind(member, pname)        # its own colours and a file's qualifiers are not the element's
                out[pname] = self._convert(kind, value)
                if kind in ("rows", "text"):
                    choose = choreography.select_rows if kind == "rows" else choreography.select_lines
                    out[pname], problems = choose(out[pname], member["params"], pname)
                    if problems:
                        raise cli.Failure(f"'{name}': " + "; ".join(problems))
        if state is None and member["element"] not in choreography.PIECES:
            state = self.lib.element(member["element"]).get("default-state")
        for (a, b), mv in self._moves_of(name, ("param", "set", "state")):
            if self.t < a:
                break
            p, act = progress(self.t, a, b, mv), mv["action"]
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
        self._frame = frame
        for name, member in self.cast.items():
            alpha = self.alpha(name)
            if alpha <= 0:
                continue
            p, state = self.params(member)
            degrees = p.pop(choreography.ROTATE, 0.0)
            if not degrees:
                self._draw_member(frame, name, member, p, state, alpha)
                continue
            import cairo
            aside = copy.copy(frame)            # the member as it would be unturned, recorded, then painted turned
            recording = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
            aside.ctx = cairo.Context(recording)
            box = self._draw_member(aside, name, member, p, state, alpha)
            centre = (box[0] + box[2] / 2, box[1] + box[3] / 2)
            ctx = frame.ctx
            ctx.save()
            ctx.translate(*centre)
            ctx.rotate(math.radians(degrees))
            ctx.translate(-centre[0], -centre[1])
            ctx.set_source_surface(recording, 0, 0)
            ctx.paint()
            ctx.restore()
            anchors = dict(box_anchors(box), **self._anchors.get(name, {}))     # its anchors turn with it
            self._anchors[name] = {k: turn(pt, centre, degrees) for k, pt in anchors.items()}

    def _draw_member(self, frame, name, member, p, state, alpha):
        """Draw one member, unturned, on `frame`; keep the anchors its drawing gives; return its box."""
        x, y, w, h = self.rect(name)
        element = member["element"]
        if element == "pill":
            box = frame.tag(p["text"], x, y, size=float(p.get("size", 22)), fill=p.get("fill", "ink"),
                            colour=p.get("colour", "on-accent"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha)
            self._anchors[name] = box_anchors(box)
            return box
        if element == "text":
            size, align = float(p.get("size", 22)), ALIGN[p.get("anchor", "left")]
            width = frame.text(p["text"], x, y, size, role=p.get("role", "body"), colour=p.get("colour", "ink"),
                               anchor=align, alpha=alpha, check=True)
            left = x if align == "l" else x - width / 2 if align == "c" else x - width
            scaled = frame._size(size)                      # the baseline is at y; the box is the type size
            box = (left, y - scaled * 0.75, width, scaled)
            self._anchors[name] = box_anchors(box)
            return box
        if element == "badge":
            r = float(p.get("r", 24))
            frame.badge(x, y, p["ok"] in YES, r=r, alpha=alpha)
            box = (x - r, y - r, 2 * r, 2 * r)
            self._anchors[name] = box_anchors(box)
            return box
        if element == "hand":
            frame.hand(x, y, float(p["angle"]), float(p["scale"]), alpha=alpha, mirror=p.get("mirror") in YES,
                       label=p.get("label") or None)       # an empty label is no label
        elif element == "callout":
            target = self._point(p["target"])
            frame.callout(p["text"], target, (x, y), size=float(p.get("size", 22)), fill=p.get("fill", "surface"),
                          colour=p.get("colour", "ink"), anchor=ALIGN[p.get("anchor", "left")], alpha=alpha,
                          leader=p.get("leader", "ink"))
        elif element == "arrow":
            from videotools import draw
            headless = {} if p.get("head", "yes") in YES else {"head": 0}     # draw.arrow's head is its size
            via = [self._place(w) for w in choreography.parse_points(p["via"])] if "via" in p else []
            control = [self._point(p["from"])] + via + [self._point(p["to"])]    # two points, or a curve by four
            draw.arrow(frame.ctx, control,
                       frame.colour(p.get("colour", "ink")), lw=float(p.get("width", 6)),
                       progress=float(p.get("progress", 1)), alpha=alpha,
                       dash=choreography.parse_dash(p["dash"]) if "dash" in p else None, **headless)
        else:
            el = self.lib.element(element)
            try:
                self._anchors[name] = el.draw(self._in_its_colours(frame, member), (x, y, w, h), state=state,
                                              params=p, alpha=alpha)
            except Exception as e:      # the library refuses in words (its Failure) or fails: one line, exit 3
                raise cli.Failure(f"scene {frame.scene['key']}: the library could not draw '{name}' ({element}): "
                                  f"{e}") from e
        return (x, y, w, h)

    def _in_its_colours(self, frame, member):
        """The frame the member's element draws on: the frame itself, or a copy whose colours carry
        the member's own (`colour.<role>=<name>`) under the roles' names, which is where the library
        looks for a role's colour before the element's default."""
        own = {n[len(choreography.OWN_COLOUR):]: v for n, v in member["params"].items()
               if n.startswith(choreography.OWN_COLOUR)}
        if not own:
            return frame
        tinted = copy.copy(frame)
        tinted.colours = dict(frame.colours, **{role: frame.colour(colour) for role, colour in own.items()})
        return tinted

    def _point(self, text):
        """A point written as a member's anchor with an optional offset (an arrow's ends, a callout's target)."""
        return self._place(choreography.parse_where(text))

    def _place(self, where):
        """A parsed place in frame pixels: the cast's own pixels, or a member's anchor plus its offset."""
        if where["kind"] == "pixels":
            return (self.area[0] + where["x"], self.area[1] + where["y"])
        x, y = self.anchors_of(where["member"], where["anchor"])
        return (x + where["dx"], y + where["dy"])


def draw_scene(frame, video, scene, tl, t, area=None):
    """The scene's described cast at t, before the module's draw (if any): in the animation
    area's pixels, or in `area`'s (the whole frame, for a title or end card)."""
    Performance(scene["cast"], scene["moves"], area or frame.area, tl, t, video.library,
                folder=video.folder).draw(frame)


def draw_panel(frame, video, scene, panel, rect, tl, t):
    """A described panel's cast, in the panel body's pixels, timed from the panel's rise."""
    p = scene["panels"][panel]
    Performance(p["cast"], p["moves"], rect, tl, t, video.library, panel_start=tl.start(tl.mistake),
                folder=video.folder).draw(frame)
