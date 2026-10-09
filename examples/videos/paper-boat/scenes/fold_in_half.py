"""Scene A: the sheet folds in half, top edge to bottom edge; the mistake is a diagonal fold."""

from videotools import draw as d

from _sheet import centre, crease, label, sheet


def draw(frame):
    cx, cy = centre(frame)
    w, h = 700, 500
    x, y = cx - w / 2, cy - h / 2
    tl, t = frame.timeline, frame.t
    p = tl.p(t, 1, 0.6, 2.4)            # the top half comes down during cue 1
    sheet(frame, x, y, w, h)
    crease(frame, (x, cy), (x + w, cy), alpha=tl.p(t, 1, 0.2, 0.6))
    top_h = h / 2 * (1 - p)
    sheet(frame, x, cy - top_h, w, top_h + h / 2 * p, back=True, alpha=1.0)
    label(frame, "top edge to bottom edge", x - 20, y - 20, alpha=tl.p(t, 1, 0.3, 0.8), anchor="r")
    label(frame, "crease", x + w + 90, cy, alpha=tl.p(t, 1, 2.4, 2.9))
    d.hand(frame.ctx, cx, cy - top_h, angle=1.5708, scale=0.8, skin=frame.colours["paper-edge"],
              outline=frame.brand["colours"]["ink"], sleeve=frame.brand["colours"]["muted"], alpha=tl.p(t, 1, 0.4, 0.8))


def _panel_sheet(frame, rect, diagonal):
    x, y, w, h = rect
    sx, sy, sw, sh = x + 100, y + 120, w - 200, h - 280
    sheet(frame, sx, sy, sw, sh)
    if diagonal:
        d.poly(frame.ctx, [(sx, sy), (sx + sw, sy), (sx, sy + sh)], fill=frame.colours["paper-back"],
                  stroke=frame.colours["paper-edge"], lw=3)
    else:
        sheet(frame, sx, sy, sw, sh / 2, back=True)
    return sx + sw / 2, sy + sh + 60


def mistake(frame, rect):
    cx, ly = _panel_sheet(frame, rect, diagonal=True)
    d.badge(frame.ctx, cx - 180, ly, False, frame.brand["colours"]["mistake"], frame.brand["colours"]["on-accent"])
    label(frame, "diagonal fold", cx + 20, ly)


def right_way(frame, rect):
    cx, ly = _panel_sheet(frame, rect, diagonal=False)
    d.badge(frame.ctx, cx - 180, ly, True, frame.brand["colours"]["correct"], frame.brand["colours"]["on-accent"])
    label(frame, "edge fold", cx + 20, ly)
