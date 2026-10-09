"""Scene C: the triangle opens from below and flattens; its corners pull apart into the boat."""

from videotools import draw as d

from _sheet import centre, label


def draw(frame):
    cx, cy = centre(frame)
    tl, t = frame.timeline, frame.t
    c = frame.colours
    p1 = tl.p(t, 1, 0.5, 2.5)
    p2 = tl.p(t, 2, 0.5, 2.5)
    half = 250 * (1 - p2) + 350 * p2
    top = cy - 220 + 80 * p1
    hull = [(cx - half, cy + 60), (cx + half, cy + 60), (cx + half - 80, cy + 180), (cx - half + 80, cy + 180)]
    d.poly(frame.ctx, hull, fill=c["paper"], stroke=c["paper-edge"], lw=3, alpha=p1)
    sail_w = 200 * (1 - p1) + 120 * p1
    d.poly(frame.ctx, [(cx - sail_w, cy + 60), (cx + sail_w, cy + 60), (cx, top)], fill=c["paper-back"],
              stroke=c["paper-edge"], lw=3)
    label(frame, "open", cx - 300, cy - 100, alpha=tl.p(t, 1, 0.3, 0.8))
    label(frame, "flatten into a square", cx, cy + 250, alpha=tl.p(t, 1, 2.2, 2.7))
    label(frame, "pull apart", cx + 320, cy - 100, alpha=tl.p(t, 2, 0.3, 0.8))
    for side in (-1, 1):
        d.arrow(frame.ctx, [(cx + side * 100, cy + 100), (cx + side * (half + 40), cy + 100)],
                   frame.brand["colours"]["accent"], 6, progress=p2, head=18, alpha=min(1.0, p2 * 3))
