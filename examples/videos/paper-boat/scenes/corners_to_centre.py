"""Scene B: a dashed centre line, then each top corner folds down to it."""

from videotools import draw as d

from _sheet import centre, label, sheet


def draw(frame):
    cx, cy = centre(frame)
    w, h = 700, 250
    x, y = cx - w / 2, cy - h / 2
    tl, t = frame.timeline, frame.t
    sheet(frame, x, y, w, h)
    d.line(frame.ctx, [(cx, y - 30), (cx, y + h + 30)], frame.brand["colours"]["accent"], 3,
              tl.p(t, 1, 0.5, 1.2), dash=[14, 10])
    label(frame, "centre", cx, y - 60, alpha=tl.p(t, 1, 1.0, 1.5))
    for side, start in ((-1, 0.4), (1, 1.6)):
        p = tl.p(t, 2, start, start + 1.0)
        corner_x = cx + side * w / 2
        tip = (corner_x + (cx - corner_x) * p, y + h * p)
        d.poly(frame.ctx, [(corner_x, y), (cx, y), tip], fill=frame.colours["paper-back"],
                  stroke=frame.colours["paper-edge"], lw=3, alpha=min(1.0, p * 4))
    label(frame, "corner to the centre line", cx, y + h + 60, alpha=tl.p(t, 2, 1.0, 1.5))
