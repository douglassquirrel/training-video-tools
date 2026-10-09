"""A whole frame: the video's files loaded once, then the chrome around the scene's drawing.

`Video` reads the script, the brand kit, the config-free things a frame needs (fonts registered,
insets from `work/insets/`, `timing.json` if there is one) and the scene modules. `draw_frame`
paints one frame at time t of a scene: background and dot grid, header with roundel, titles and
tracker, the reference column (inset, side panel, brand mark), the scene code's drawing clipped
to the animation area, the mistake panels on the mistake cue, the caption band, and the fades.
Title and end cards are drawn by the chrome from the script and the brand. Needs pycairo.
"""

import json
import math
import os

import cairo

from videotools import brand as brand_
from videotools import chrome, cli, draw, fonts, scenes, script, timeline

HEADING_HEIGHT = 38      # what a side-panel heading adds above a steps or checklist panel


class Video:
    """Everything a frame needs, loaded once."""

    def __init__(self, script_path):
        self.script_path = script_path
        self.folder = script.folder(script_path)
        self.data = script.read(script_path)
        self.settings = script.settings(self.data)
        self.layout = chrome.Layout(self.settings["size"])
        kit_folder = brand_.folder_for(script_path, self.settings["brand"])
        self.brand = brand_.read(kit_folder)
        self.scale = self.brand["settings"]["font-size-scale"]
        fonts.load(self.brand, os.path.join(self.folder, "work"))
        self.colours = {k: draw.rgb(v) for k, v in self.data["colours"].items()}
        self.insets = self._insets()
        self.timing = self._timing()
        self._scenes = {s["key"]: s for s in self.data["scenes"]}
        self._modules = {}
        self._background = None
        self._end_card = None

    def _insets(self):
        folder = os.path.join(self.folder, "work", "insets")
        surfaces = {}
        for key in self.data["insets"]:
            path = os.path.join(folder, f"{key}.png")
            if not os.path.isfile(path):
                raise cli.Failure(f"no {path} (inset '{key}'); run crop-insets first")
            surfaces[key] = cairo.ImageSurface.create_from_png(path)
        page = os.path.join(folder, "title-page.png")
        if any(script.kind(s) == "title" for s in self.data["scenes"]) and self.settings["source-image"]:
            if not os.path.isfile(page):
                raise cli.Failure(f"no {page} (the title card's page); run crop-insets first")
            surfaces["title-page"] = cairo.ImageSurface.create_from_png(page)
        return surfaces

    def _timing(self):
        path = os.path.join(self.folder, "work", "narration", "timing.json")
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def scene(self, key):
        if key not in self._scenes:
            raise cli.Failure(f"no scene '{key}' in the script (scenes: {', '.join(self._scenes)})", cli.USAGE)
        return self._scenes[key]

    def timeline(self, scene, estimate=False):
        return timeline.build(self.settings, scene, timeline.clips_for(self.timing, scene), estimate)

    def module(self, scene):
        if scene["key"] not in self._modules:
            folder = os.path.join(self.folder, self.settings["scene-code"])
            self._modules[scene["key"]] = scenes.load(folder, scene)
        return self._modules[scene["key"]]

    # ---- cached surfaces
    def background(self):
        if self._background is None:
            lay, kit = self.layout, self.brand
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
            c = cairo.Context(surface)
            c.set_source_rgb(*kit["colours"]["background"])
            c.paint()
            grid = kit["settings"]["background-grid"]
            if grid:
                _, spacing, size, opacity = grid
                ax, ay, aw, ah = lay.area
                for x in range(ax + spacing // 2, ax + aw, spacing):
                    for y in range(ay + spacing // 2, ay + ah + 4, spacing):
                        c.rectangle(x - size / 2, y - size / 2, size, size)
                c.set_source_rgba(*kit["colours"]["grid"], opacity)
                c.fill()
            self._background = surface
        return self._background

    def end_card_image(self):
        if self._end_card is None:
            self._end_card = cairo.ImageSurface.create_from_png(self.brand["illustration"]["end-card"])
        return self._end_card


# ---------------------------------------------------------------- pieces
def _font(video, role):
    return video.brand["fonts"][role]


def _colour(video, role, size=None):
    kit = video.brand
    return brand_.text_colour(kit, role, size) if size is not None else kit["colours"][role]


def _text(ctx, video, s, x, y, role, size, colour_role, anchor="l", alpha=1.0, track=0):
    size = chrome.px(video.scale, size)
    return draw.text(ctx, s, x, y, _font(video, role), size, _colour(video, colour_role, size), anchor, alpha, track)


def mark(ctx, video, x, y, r, size, alpha=1.0):
    """The brand mark: the roundel with its letter, and the wordmark to its right."""
    kit, m = video.brand, video.brand["mark"]
    draw.circle(ctx, x, y, r, fill=brand_.colour(kit, m.get("fill", "accent")), alpha=alpha)
    draw.text(ctx, m["letter"], x, y + r * 0.5, _font(video, m.get("letter-font", "display")), r * 1.2,
              brand_.colour(kit, m.get("letter-colour", "on-accent")), anchor="c", alpha=alpha)
    return _text(ctx, video, m["wordmark"], x + r + 14, y + size * 0.36, "display", size, "ink", alpha=alpha)


def header(ctx, video, scene):
    kit, lay = video.brand, video.layout
    x = 60
    letter = scene["props"].get("letter")
    if letter:
        draw.circle(ctx, 92, 62, 37, fill=kit["colours"]["accent"])
        draw.text(ctx, letter, 92, 79, _font(video, "display"), chrome.px(video.scale, 46), kit["colours"]["on-accent"],
                  anchor="c")
        x = 150
    _text(ctx, video, scene["props"].get("eyebrow", ""), x, 50, "display", 18, "accent", track=3)
    _text(ctx, video, scene["props"].get("title", ""), x, 93, "display", 46, "ink")
    done, now = chrome.tracker_done_now(video.data, scene)
    xx = lay.width - 58
    places = chrome.tracker(video.data)
    for i in range(len(places) - 1, -1, -1):
        _, label, _ = places[i]
        is_letter = len(label) == 1
        size = chrome.px(video.scale, 24 if is_letter else 21)
        w = 40 if is_letter else draw.text_width(ctx, label, _font(video, "display-medium"), size) + 28
        bx, cx = xx - w, xx - w / 2
        if i == now:
            draw.fill_rrect(ctx, bx, 42, w, 40, 20, kit["colours"]["accent"])
            fg = kit["colours"]["on-accent"]
        elif i in done:
            draw.fill_rrect(ctx, bx, 42, w, 40, 20, kit["colours"]["ink"])
            fg = kit["colours"]["on-accent"]
        else:
            draw.rrect(ctx, bx + 1, 43, w - 2, 38, 19)
            ctx.set_source_rgba(*kit["colours"]["muted"], 0.6)
            ctx.set_line_width(2)
            ctx.stroke()
            fg = kit["colours"]["muted"]
        draw.text(ctx, label, cx, 70, _font(video, "display" if is_letter else "display-medium"), size, fg, anchor="c")
        xx = bx - 10
    draw.line(ctx, [(56, lay.header_rule), (lay.width - 56, lay.header_rule)], kit["colours"]["rule"], 2)


def reference_column(ctx, video, scene, tl, t, frame):
    kit, lay = video.brand, video.layout
    cx, cy, cw, ch = lay.column
    mark(ctx, video, cx + 20, cy + ch - 30, 19, 25)
    y = cy + 22
    inset = scene["props"].get("inset")
    if inset:
        img = video.insets[inset]
        _text(ctx, video, video.settings["source-label"], cx, y + 10, "display", 16, "muted", track=2)
        iw, ih = img.get_width(), img.get_height()
        ix, iy = cx + (cw - iw) / 2, y + 24
        draw.fill_rrect(ctx, ix - 6, iy - 6, iw + 12, ih + 12, 6, kit["colours"]["surface"],
                        stroke=kit["colours"]["rule"], lw=1.5)
        ctx.set_source_surface(img, ix, iy)
        ctx.paint()
        y = iy + ih + 34
    kind, _, cue = script.side_panel(scene)
    heading = scene["props"].get("side-panel-heading")
    if heading and kind in ("steps", "checklist"):
        # The heading in KEY POINTS' style above the rows, which move down to make room for it.
        _text(ctx, video, heading, cx, y + 6, "display", 16, "muted", track=2)
        y += HEADING_HEIGHT
    if kind == "custom":
        alpha = tl.p(t, cue, 0.0, 0.5)
        if alpha > 0:
            ctx.save()
            ctx.push_group()
            video.module(scene).panel(frame, (cx, y, cw, cy + ch - 60 - y))
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(alpha)
            ctx.restore()
    elif kind == "steps":
        now, done = chrome.current_step(scene, tl, t), chrome.steps_done(scene, tl, t)
        for i, item in enumerate(scene["side"], 1):
            yy = y + 18 + (i - 1) * 52
            role = "accent" if i == now else "ink" if i in done else "rule"
            colour = kit["colours"][role]
            draw.circle(ctx, cx + 20, yy, 18, fill=colour)
            fg = kit["colours"]["on-accent"] if (i == now or i in done) else kit["colours"]["muted"]
            draw.text(ctx, str(i), cx + 20, yy + 9, _font(video, "display"), chrome.px(video.scale, 24), fg, anchor="c")
            _text(ctx, video, item["text"], cx + 52, yy + 8, "display" if i == now else "body-medium", 22,
                  "ink" if (i == now or i in done) else "muted")
    elif kind == "checklist":
        progress = chrome.checklist_progress(tl, cue, len(scene["side"]), t)
        for i, (item, p) in enumerate(zip(scene["side"], progress)):
            yy = y + 30 + i * 60
            draw.badge(ctx, cx + 22, yy, True, kit["colours"]["correct"], kit["colours"]["on-accent"], 18, p)
            _text(ctx, video, item["text"], cx + 54, yy + 8, "body-medium", 24, "ink", alpha=0.35 + 0.65 * p)
    elif kind == "key-points":
        _text(ctx, video, heading or "KEY POINTS", cx, y + 6, "display", 16, "muted", track=2)
        for i, item in enumerate(scene["side"]):
            yy = y + 44 + i * 44
            ctx.rectangle(cx, yy - 13, 12, 12)
            ctx.set_source_rgb(*kit["colours"]["accent"])
            ctx.fill()
            _text(ctx, video, item["text"], cx + 24, yy, "body-medium", 22, "ink")


def caption(ctx, video, scene, tl, t):
    kit, lay = video.brand, video.layout
    if not scene["cues"]:
        return
    n = tl.cue(t)
    cue = scene["cues"][max(n, 1) - 1]
    bx, by, bw, bh = lay.caption
    ctx.rectangle(bx, by, bw, bh)
    ctx.set_source_rgb(*brand_.colour(kit, kit["settings"]["caption-band"]))
    ctx.fill()
    rule_role, rule_h = kit["settings"]["caption-rule"]
    ctx.rectangle(bx, by, bw, rule_h)
    ctx.set_source_rgb(*brand_.colour(kit, rule_role))
    ctx.fill()
    if n == 0:
        return
    alpha = tl.p(t, n, -0.05, 0.2) if n > 1 else timeline.ep(t, 0.0, 0.4)
    cx, max_w = lay.width / 2, lay.width - 280
    if "mistake" in cue:
        draw.tag(ctx, "COMMON MISTAKE", 60, by + 66, _font(video, "display"), chrome.px(video.scale, 22),
                 fill=kit["colours"]["mistake"], colour=kit["colours"]["on-accent"])
        cx, max_w = lay.width / 2 + 150, lay.width - 480
    size = chrome.px(video.scale, 36)
    lines = draw.wrap(ctx, cue["text"], _font(video, "body-medium"), size, max_w)
    y0 = by + 66 - (len(lines) - 1) * 23 + 12
    for k, line in enumerate(lines):
        draw.text(ctx, line, cx, y0 + k * 46, _font(video, "body-medium"), size, kit["colours"]["on-accent"],
                  anchor="c", alpha=alpha)


def mistake_panels(ctx, video, scene, tl, t, frame):
    kit, lay = video.brand, video.layout
    cue = next((c for c in scene["cues"] if "mistake" in c), None)
    if not cue:
        return
    n = cue["n"]
    if t < tl.start(n) - 0.1:
        return
    p = tl.p(t, n, 0.0, 0.5)
    if n < len(scene["cues"]):
        p *= 1 - tl.p(t, n + 1, -0.4, 0.1)
    if p <= 0:
        return
    wrong, right = script.mistake(cue)
    ax, ay, aw, ah = lay.area
    ctx.push_group()
    ctx.rectangle(ax - 10, ay, aw + 20, ah + 6)
    ctx.set_source_rgba(*kit["colours"]["background"], 0.96)
    ctx.fill()
    module = video.module(scene)
    for side, (x, body) in enumerate(((52, module.mistake), (764, module.right_way))):
        y, w, h = 134, 690, 790
        draw.fill_rrect(ctx, x, y, w, h, 16, kit["colours"]["surface"], stroke=kit["colours"]["rule"], lw=2)
        head = kit["colours"]["mistake"] if side == 0 else kit["colours"]["correct"]
        ctx.save()
        draw.rrect(ctx, x, y, w, h, 16)
        ctx.clip()
        ctx.rectangle(x, y, w, 62)
        ctx.set_source_rgb(*head)
        ctx.fill()
        ctx.restore()
        draw.badge(ctx, x + 36, y + 31, side == 1, kit["colours"]["on-accent"], head, 17)
        draw.text(ctx, "MISTAKE" if side == 0 else "RIGHT WAY", x + 64, y + 42, _font(video, "display"),
                  chrome.px(video.scale, 32), kit["colours"]["on-accent"])
        draw.text(ctx, wrong if side == 0 else right, x + w - 24, y + 40, _font(video, "body-medium"),
                  chrome.px(video.scale, 22), kit["colours"]["on-accent"], anchor="r")
        ctx.save()
        ctx.rectangle(x + 2, y + 62, w - 4, h - 64)
        ctx.clip()
        body(frame, (x, y + 62, w, h - 62))
        ctx.restore()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(p)


def title_card(ctx, video, scene, tl, t):
    kit, st, _lay = video.brand, video.settings, video.layout
    a = timeline.ep(t, 0.1, 1.0)
    mark(ctx, video, 152, 150, 30, 36, alpha=a)
    _text(ctx, video, st["eyebrow"], 120, 318, "display", 22, "accent", alpha=a, track=4)
    _text(ctx, video, st["title"], 112, 440, "display", 118, "ink", alpha=a)
    _text(ctx, video, st["subtitle"], 120, 510, "italic", 36, "muted", alpha=timeline.ep(t, 0.5, 1.4))
    rule_role, rule_h = kit["settings"]["title-rule"]
    ctx.rectangle(120, 556, 230 * timeline.ep(t, 0.8, 1.8), rule_h)
    ctx.set_source_rgb(*brand_.colour(kit, rule_role))
    ctx.fill()
    steps = chrome.title_steps(video.data)
    cue = 2 if len(scene["cues"]) >= 2 else 1 if scene["cues"] else None
    for i, (letter, title) in enumerate(steps):
        p = tl.p(t, cue, 0.2 + i * 0.25, 0.7 + i * 0.25) if cue else 1.0
        col, row = i % 3, i // 3
        x, y = 120 + col * 320, 650 + row * 78
        draw.circle(ctx, x + 24, y - 8, 24, fill=kit["colours"]["accent"], alpha=p)
        draw.text(ctx, letter, x + 24, y + 3, _font(video, "display"), chrome.px(video.scale, 28),
                  kit["colours"]["on-accent"], anchor="c", alpha=p)
        _text(ctx, video, title, x + 62, y + 2, "body-medium", 28, "ink", alpha=p)
    page = video.insets.get("title-page")
    if page:
        iw, ih = page.get_width(), page.get_height()
        x, y = 1250, 112
        pa = timeline.ep(t, 0.4, 1.4)
        ctx.save()
        ctx.translate(x + iw / 2, y + ih / 2)
        ctx.rotate(math.radians(2.2))
        ctx.translate(-iw / 2, -ih / 2)
        draw.fill_rrect(ctx, 8, 12, iw, ih, 4, kit["colours"]["ink"], alpha=0.16 * pa)
        ctx.set_source_surface(page, 0, 0)
        ctx.paint_with_alpha(pa)
        ctx.rectangle(0, 0, iw, ih)
        ctx.set_source_rgba(*kit["colours"]["ink"], 0.25 * pa)
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.restore()
        _text(ctx, video, st["title-image-caption"], x + iw / 2, y + ih + 44, "italic", 22, "muted", anchor="c",
              alpha=pa)


def end_card(ctx, video, scene, tl, t):
    kit, st, lay = video.brand, video.settings, video.layout
    a = timeline.ep(t, 0.2, 1.2)
    img = video.end_card_image()
    iw = img.get_width()
    ctx.set_source_surface(img, (lay.width - iw) / 2, 110 + (1 - a) * 14)
    ctx.paint_with_alpha(a)
    b = timeline.ep(t, 0.7, 1.6)
    size = chrome.px(video.scale, 64)
    w = draw.text_width(ctx, kit["mark"]["wordmark"], _font(video, "display"), size)
    mark(ctx, video, lay.width / 2 - (w + 60 + 18) / 2 + 40, 640, 40, 64, alpha=b)
    rule_role, rule_h = kit["settings"]["title-rule"]
    ctx.rectangle(lay.width / 2 - 115, 705, 230 * b, rule_h)
    ctx.set_source_rgb(*brand_.colour(kit, rule_role))
    ctx.fill()
    _text(ctx, video, kit["identity"]["website"], lay.width / 2, 770, "italic", 34, "muted", anchor="c", alpha=b)
    c = timeline.ep(t, 1.2, 2.0)
    y = 860
    for line in (st["credit"], kit["identity"].get("illustration-credit", "")):
        if line:
            _text(ctx, video, line, lay.width / 2, y, "body", 22, "muted", anchor="c", alpha=c)
            y += 36


def draw_frame(ctx, video, scene, tl, t):
    """One frame of `scene` at `t` seconds, on a 1920x1080 context."""
    kit, lay = video.brand, video.layout
    kind = script.kind(scene)
    ctx.set_source_surface(video.background(), 0, 0)
    ctx.paint()
    frame = scenes.Frame(ctx, t, tl, scene, video.colours, kit, lay.area)
    if kind == "title":
        ctx.save()
        ctx.rectangle(*lay.card)
        ctx.clip()
        title_card(ctx, video, scene, tl, t)
        if video.module(scene):
            video.module(scene).draw(frame)
        ctx.restore()
        caption(ctx, video, scene, tl, t)
    elif kind == "end":
        ctx.save()
        ctx.rectangle(0, 0, lay.width, lay.height)
        ctx.clip()
        end_card(ctx, video, scene, tl, t)
        if video.module(scene):
            video.module(scene).draw(frame)
        ctx.restore()
    else:
        header(ctx, video, scene)
        ax, ay, aw, ah = lay.area
        ctx.save()
        ctx.rectangle(ax - 20, ay, aw + 40, ah + 10)
        ctx.clip()
        video.module(scene).draw(frame)
        mistake_panels(ctx, video, scene, tl, t, frame)
        ctx.restore()
        reference_column(ctx, video, scene, tl, t, frame)
        caption(ctx, video, scene, tl, t)
    fade_in, fade_out = video.settings["fade"]
    fade = max(1 - timeline.ep(t, 0.0, fade_in), timeline.ep(t, tl.total - fade_out, tl.total))
    if fade > 0:
        ctx.set_source_rgba(*kit["colours"]["background"], fade)
        ctx.paint()
