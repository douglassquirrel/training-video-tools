"""Scene B2: the strip below the triangle folds up, near side then far; a custom side panel."""

from videotools import draw as d

from _sheet import centre, label, sheet


def draw(frame):
    cx, cy = centre(frame)
    w, h = 700, 250
    x, y = cx - w / 2, cy - h / 2
    tl, t = frame.timeline, frame.t
    sheet(frame, x, y, w, h)
    d.poly(frame.ctx, [(x, y), (x + w, y), (cx, y + h - 60)], fill=frame.colours["paper-back"],
              stroke=frame.colours["paper-edge"], lw=3)
    p = tl.p(t, 1, 0.4, 1.6)
    strip_h = 60 * (1 - p) + 60 * p
    d.fill_rrect(frame.ctx, x, y + h - 60 - 60 * p, w, strip_h, 4, frame.colours["paper"],
                 stroke=frame.colours["paper-edge"], lw=3)
    label(frame, "fold the strip up", cx, y + h + 60, alpha=tl.p(t, 1, 0.3, 0.8))
    label(frame, "both sides", cx, y - 50, alpha=tl.p(t, 1, 2.0, 2.5))


def panel(frame, rect):
    x, y, w, h = rect
    kit = frame.brand
    d.fill_rrect(frame.ctx, x, y, w, 150, 12, kit["colours"]["surface"], stroke=kit["colours"]["rule"], lw=2)
    d.line(frame.ctx, [(x + 30, y + 100), (x + w - 30, y + 100)], frame.colours["paper-edge"], 6)
    d.line(frame.ctx, [(x + 30, y + 100), (x + 30, y + 40), (x + w - 30, y + 40), (x + w - 30, y + 100)],
              frame.colours["paper-edge"], 6, dash=[10, 8])
    d.arrow(frame.ctx, [(x + w / 2, y + 130), (x + w / 2, y + 60)], kit["colours"]["accent"], 4, head=14)
