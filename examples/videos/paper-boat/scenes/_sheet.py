"""Shared drawing for the paper-boat scenes: the sheet, folds and labels."""

from videotools import draw as d


def sheet(frame, x, y, w, h, alpha=1.0, back=False):
    c = frame.colours
    d.fill_rrect(frame.ctx, x, y, w, h, 6, c["paper-back"] if back else c["paper"], alpha,
                    stroke=c["paper-edge"], lw=3)


def crease(frame, p0, p1, alpha=1.0):
    d.line(frame.ctx, [p0, p1], frame.colours["paper-edge"], 2.5, alpha, dash=[12, 8])


def label(frame, text, x, y, alpha=1.0, anchor="c"):
    kit = frame.brand
    d.tag(frame.ctx, frame.label(text), x, y, kit["fonts"]["display"], 24 * kit["settings"]["font-size-scale"],
             fill=kit["colours"]["accent"], colour=kit["colours"]["on-accent"], anchor=anchor, alpha=alpha)


def centre(frame):
    x, y, w, h = frame.area
    return x + w / 2, y + h / 2
