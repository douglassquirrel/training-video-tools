"""Scene R: the boat on water, slowly zooming in."""

from videotools import draw as d

from _sheet import centre, label


def draw(frame):
    cx, cy = centre(frame)
    tl, t = frame.timeline, frame.t
    c = frame.colours
    z = 1.0 + 0.15 * (t / max(tl.total, 1))
    d.fill_rrect(frame.ctx, cx - 600, cy + 150, 1200, 200, 20, c["water"])
    hull = [(cx - 320 * z, cy + 60), (cx + 320 * z, cy + 60), (cx + 220 * z, cy + 170), (cx - 220 * z, cy + 170)]
    d.poly(frame.ctx, hull, fill=c["paper"], stroke=c["paper-edge"], lw=3)
    d.poly(frame.ctx, [(cx - 150 * z, cy + 60), (cx + 150 * z, cy + 60), (cx, cy - 120 * z)], fill=c["paper-back"],
              stroke=c["paper-edge"], lw=3)
    label(frame, "CHECK BEFORE YOU LAUNCH IT", cx, cy - 220, alpha=tl.p(t, 2, 0.0, 0.5))
