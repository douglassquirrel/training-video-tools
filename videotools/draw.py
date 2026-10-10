"""Drawing primitives for scene code and the chrome, on a cairo context: text with tracking and
wrapping, polygons, lines, rounded rectangles, circles, Bézier curves, arrows that draw on,
pills, callouts, dimension lines, badges, hands. Every colour is an (r, g, b) triple in 0–1,
passed in: nothing here knows a brand. Sizes are pixels (the chrome applies the brand's
font-size-scale before calling). Needs pycairo.
"""

import math

import cairo


# ---------------------------------------------------------------- colours
def rgb(hex_colour):
    """'#RRGGBB' as an (r, g, b) triple in 0–1."""
    h = hex_colour.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def shade(colour, factor):
    """The colour darkened (factor < 1) or lightened, clamped."""
    return tuple(max(0.0, min(1.0, v * factor)) for v in colour)


def mix(a, b, p):
    """The colour p of the way from a to b."""
    return tuple(a[i] + (b[i] - a[i]) * p for i in range(3))


# ---------------------------------------------------------------- text
def font(ctx, family, size):
    ctx.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


# ✓ and ✗ a font lacks are drawn as strokes (the badge's marks without the circle), MARK_WIDTH
# of the font size wide, so a brand whose text face has no tick still gets one in every label.
MARKS = {"✓": "tick", "✗": "cross"}
MARK_WIDTH = 0.8


def _runs(s, family):
    """s split into (text, mark) runs: mark is None for text the font draws, else the mark to
    stroke in its place."""
    from videotools import glyphs
    runs, current = [], ""
    for ch in s:
        if ch in MARKS and not glyphs.has(family, ch):
            if current:
                runs.append((current, None))
                current = ""
            runs.append((ch, MARKS[ch]))
        else:
            current += ch
    if current:
        runs.append((current, None))
    return runs


def _advance(ctx, run, mark, size):
    return MARK_WIDTH * size if mark else ctx.text_extents(run).x_advance


def _mark(ctx, mark, x, y, size, colour, alpha):
    """A tick or cross stroked at the baseline point (x, y), MARK_WIDTH × size wide."""
    s = size
    lw = max(1.5, 0.11 * s)
    if mark == "tick":
        tick = [(x + 0.08 * s, y - 0.30 * s), (x + 0.32 * s, y - 0.06 * s), (x + 0.72 * s, y - 0.60 * s)]
        line(ctx, tick, colour, lw, alpha)
    else:
        line(ctx, [(x + 0.12 * s, y - 0.62 * s), (x + 0.68 * s, y - 0.06 * s)], colour, lw, alpha)
        line(ctx, [(x + 0.68 * s, y - 0.62 * s), (x + 0.12 * s, y - 0.06 * s)], colour, lw, alpha)


def text_width(ctx, s, family, size, track=0):
    font(ctx, family, size)
    if track:
        return sum(_advance(ctx, ch, mark, size) for run, mark in _runs(s, family) for ch in run) \
            + track * max(0, len(s) - 1)
    return sum(_advance(ctx, run, mark, size) for run, mark in _runs(s, family))


def text(ctx, s, x, y, family, size, colour, anchor="l", alpha=1.0, track=0):
    """Draw s with its baseline at y, anchored left ('l'), centre ('c') or right ('r') at x.
    Returns the width drawn."""
    w = text_width(ctx, s, family, size, track)
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    for run, mark in _runs(s, family):
        if mark:
            _mark(ctx, mark, x, y, size, colour, alpha)
            font(ctx, family, size)                 # line() changed the context's source and width
            x += MARK_WIDTH * size + (track if track else 0)
            continue
        ctx.set_source_rgba(*colour, alpha)
        if track:
            for ch in run:
                ctx.move_to(x, y)
                ctx.show_text(ch)
                x += ctx.text_extents(ch).x_advance + track
        else:
            ctx.move_to(x, y)
            ctx.show_text(run)
            x += ctx.text_extents(run).x_advance
    return w


def wrap(ctx, s, family, size, max_width):
    """The words of s in lines no wider than max_width (a word wider than that gets a line)."""
    lines, current = [], ""
    for word in s.split():
        trial = (current + " " + word).strip()
        if not current or text_width(ctx, trial, family, size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- shapes
def path(ctx, pts):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    ctx.close_path()


def poly(ctx, pts, fill=None, stroke=None, lw=1.5, alpha=1.0, stroke_alpha=None):
    if len(pts) < 3 or alpha <= 0:
        return
    path(ctx, pts)
    if fill is not None:
        ctx.set_source_rgba(*fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        ctx.set_source_rgba(*stroke, alpha if stroke_alpha is None else stroke_alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    ctx.new_path()


def line(ctx, pts, colour, lw=2.0, alpha=1.0, dash=None, cap=cairo.LINE_CAP_ROUND):
    if alpha <= 0 or len(pts) < 2:
        return
    ctx.new_path()
    ctx.move_to(*pts[0])
    for q in pts[1:]:
        ctx.line_to(*q)
    ctx.set_source_rgba(*colour, alpha)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash:
        ctx.set_dash(dash)
    ctx.stroke()
    ctx.set_dash([])


def rrect(ctx, x, y, w, h, r):
    """A rounded-rectangle path (not filled)."""
    r = min(r, w / 2, h / 2)
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill_rrect(ctx, x, y, w, h, r, colour, alpha=1.0, stroke=None, lw=2):
    rrect(ctx, x, y, w, h, r)
    ctx.set_source_rgba(*colour, alpha)
    if stroke:
        ctx.fill_preserve()
        ctx.set_source_rgba(*stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.fill()


def circle(ctx, x, y, r, fill=None, stroke=None, lw=2, alpha=1.0):
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    if fill:
        ctx.set_source_rgba(*fill, alpha)
        if stroke:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke:
        ctx.set_source_rgba(*stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def bezier(p0, p1, p2, p3, n=40):
    """n + 1 points along a cubic Bézier curve."""
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return out


def cut(pts, p):
    """The first fraction p (by length) of a polyline."""
    if p >= 1:
        return pts
    segments = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    wanted = sum(segments) * p
    out, done = [pts[0]], 0.0
    for i, s in enumerate(segments):
        if done + s >= wanted:
            f = (wanted - done) / s if s else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            return out
        done += s
        out.append(pts[i + 1])
    return out


def arrow(ctx, control, colour, lw=6, progress=1.0, head=20, alpha=1.0, dash=None):
    """An arrow along a straight line (two points) or a Bézier curve (four), drawn on to
    `progress` of its length, with a filled head; `dash` ([on, off]) dashes the line, not the head."""
    if progress <= 0.01 or alpha <= 0:
        return
    pts = bezier(*control) if len(control) == 4 else [control[0], control[1]]
    pts = cut(pts, progress)
    if len(pts) < 2:
        return
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - math.cos(angle) * head * 0.6, y2 - math.sin(angle) * head * 0.6
    line(ctx, pts[:-1] + [(bx, by)], colour, lw, alpha, dash=dash)
    poly(ctx, [(x2, y2),
               (x2 - math.cos(angle - 0.45) * head, y2 - math.sin(angle - 0.45) * head),
               (x2 - math.cos(angle + 0.45) * head, y2 - math.sin(angle + 0.45) * head)],
         fill=colour, alpha=alpha)


# ---------------------------------------------------------------- annotations
def badge(ctx, x, y, ok, fill, mark, r=24, alpha=1.0):
    """A ✓ (ok) or ✗ roundel."""
    if alpha <= 0:
        return
    circle(ctx, x, y, r, fill=fill, alpha=alpha)
    if ok:
        tick = [(x - r * 0.45, y + r * 0.02), (x - r * 0.1, y + r * 0.38), (x + r * 0.5, y - r * 0.35)]
        line(ctx, tick, mark, r * 0.2, alpha)
    else:
        line(ctx, [(x - r * 0.38, y - r * 0.38), (x + r * 0.38, y + r * 0.38)], mark, r * 0.2, alpha)
        line(ctx, [(x + r * 0.38, y - r * 0.38), (x - r * 0.38, y + r * 0.38)], mark, r * 0.2, alpha)


def tag(ctx, s, x, y, family, size, fill, colour, anchor="l", alpha=1.0, padx=14, pady=9, border=None):
    """A pill label; (x, y) is the left, centre or right of the pill's vertical middle.
    Returns (x, y, w, h) of the pill."""
    if alpha <= 0:
        return (x, y, 0, 0)
    w = text_width(ctx, s, family, size)
    bw, bh = w + 2 * padx, size + 2 * pady
    bx = x if anchor == "l" else x - bw / 2 if anchor == "c" else x - bw
    by = y - bh / 2
    fill_rrect(ctx, bx, by, bw, bh, bh / 2 if bh < 60 else 14, fill, alpha, stroke=border)
    text(ctx, s, bx + padx, by + pady + size * 0.80, family, size, colour, alpha=alpha)
    return (bx, by, bw, bh)


def callout(ctx, s, target, at, family, size, leader, fill, colour, anchor="l", alpha=1.0):
    """A pill label at `at` with a leader line to a dot at `target`."""
    if alpha <= 0:
        return
    line(ctx, [target, at], leader, 2.2, alpha)
    circle(ctx, target[0], target[1], 5.5, fill=leader, alpha=alpha)
    tag(ctx, s, at[0], at[1], family, size, fill=fill, colour=colour, anchor=anchor, alpha=alpha)


def dimension(ctx, p0, p1, s, family, size, colour, text_colour, alpha=1.0, side=1):
    """A dimension line between p0 and p1 with end ticks and the measurement in a pill beside it."""
    if alpha <= 0:
        return
    angle = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    nx, ny = -math.sin(angle), math.cos(angle)
    line(ctx, [p0, p1], colour, 3, alpha)
    for p in (p0, p1):
        line(ctx, [(p[0] - nx * 12, p[1] - ny * 12), (p[0] + nx * 12, p[1] + ny * 12)], colour, 3, alpha)
    mx, my = (p0[0] + p1[0]) / 2 + nx * 30 * side, (p0[1] + p1[1]) / 2 + ny * 30 * side
    tag(ctx, s, mx, my, family, size, fill=colour, colour=text_colour, anchor="c", alpha=alpha)


def hand(ctx, x, y, angle, scale, skin, outline, sleeve, alpha=1.0, mirror=False, label=None,
         label_fill=None, label_colour=None, label_font=None, label_size=28):
    """A mitten-style hand with a sleeve. (x, y) is the fingertip; angle the direction from
    wrist to fingertip; an optional letter label on a roundel at the wrist, `label_size` px
    (the roundel scales with it; pass the brand-scaled size)."""
    if alpha <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(scale, -scale if mirror else scale)
    ctx.translate(-50, 0)
    ctx.push_group()
    rrect(ctx, -150, -31, 104, 62, 12)
    ctx.set_source_rgb(*sleeve)
    ctx.fill()
    line(ctx, [(-58, -31), (-58, 31)], (1, 1, 1), 5)
    ctx.save()
    ctx.translate(-12, -27)
    ctx.rotate(-0.42)
    ctx.scale(24, 11)
    ctx.new_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*skin)
    ctx.fill_preserve()
    ctx.set_source_rgb(*outline)
    ctx.set_line_width(2.6)
    ctx.stroke()
    for (rx, ry, rw, rh, rr) in ((-52, -26, 64, 52, 20), (-6, -24, 56, 46, 17)):
        rrect(ctx, rx, ry, rw, rh, rr)
        ctx.set_source_rgb(*skin)
        ctx.fill_preserve()
        ctx.set_source_rgb(*outline)
        ctx.set_line_width(2.6)
        ctx.stroke()
    rrect(ctx, -46, -22, 40, 44, 16)      # cover the seam between palm and fingers
    ctx.set_source_rgb(*skin)
    ctx.fill()
    for yy in (-8, 7):
        line(ctx, [(22, yy), (46, yy)], outline, 2.2, 0.75)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()
    if label:
        lx = x + math.cos(angle) * (-150 * scale)
        ly = y + math.sin(angle) * (-150 * scale)
        circle(ctx, lx, ly, 21 * label_size / 28, fill=label_fill, alpha=alpha)
        text(ctx, label, lx, ly + 10 * label_size / 28, label_font, label_size, label_colour, anchor="c", alpha=alpha)
