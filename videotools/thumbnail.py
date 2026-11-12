"""thumbnail: a branded 1280x720 PNG for a video, from its script, brand kit and one frame (PLAN.md item 32).

`thumbnail SCRIPT.md [--at SCENE:SECONDS] [--out FILE.png] [--replace] [--dry-run]`: the title (or
`thumbnail-title`), the eyebrow, the short rule and the mark on the left, on the kit's background; on
the right a card holding the frame at that moment, drawn as `stills` draws it (the animation area
of a step scene, the whole frame of a title or end card). Needs pycairo and Pillow.
"""

import argparse
import hashlib
import io
import os
import sys
import tempfile

from videotools import brand, cli, elements, script

PROG = "thumbnail"
SIZE = (1280, 720)
MARGIN = 64
PICTURE = (560, 322)    # the frame's picture inside the card, near the animation area's shape (1422 x 818)
CARD_PAD = 10           # the card's surface around the picture
CARD_RADIUS = 12
BORDER = 2              # the card's `rule` border
GUTTER = 48             # between the left block and the card
MARK_R, MARK_SIZE = 24, 25            # the roundel's radius; the wordmark at 25 px x the kit's font scale (28 px)
EYEBROW_SIZE, EYEBROW_TRACK, EYEBROW_GAP = 20, 3, 28
LEADING = 1.1           # title lines this many times the size apart
RULE_GAP, RULE_LENGTH = 32, 160       # the short rule: this far under the last baseline, this long;
#                                       twice the kit's title-rule height
LIMIT = 2_000_000       # bytes

LARGEST = 96            # px: the title's largest size
MIN_CAP = 40            # px: no size whose capitals are shorter than this (10 px at 320x180)
MAX_LINES = 3


def parse_at(text):
    """(scene key, seconds) from SCENE:SECONDS; a negative time is kept, to count back from the end."""
    m = script.MOMENT.match(text)
    if not m:
        raise cli.Failure(f"'{text.strip()}' is not SCENE:SECONDS", cli.USAGE)
    return m.group(1), float(m.group(2))


def default_out(script_path, output):
    """Beside the script's `output`, its extension replaced by ' thumbnail.png'."""
    return os.path.join(script.folder(script_path), os.path.splitext(output)[0] + " thumbnail.png")


def _wrap(title, width, measure, size):
    lines, current = [], ""
    for word in title.split():
        trial = (current + " " + word).strip()
        if not current or measure(trial, size) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    return lines + ([current] if current else [])


def fit_title(title, width, measure, cap, largest=LARGEST, min_cap=MIN_CAP, max_lines=MAX_LINES):
    """(size, lines) for the largest size, from `largest` down a pixel at a time, at which the title
    wraps to at most `max_lines` lines none wider than `width`; None when no size whose capital height
    (`cap(size)`) is at least `min_cap` will do. `measure(text, size)` is a line's width."""
    size = largest
    while size > 0 and cap(size) >= min_cap:
        lines = _wrap(title, width, measure, size)
        if len(lines) <= max_lines and all(measure(line, size) <= width for line in lines):
            return size, lines
        size -= 1
    return None


def cover_box(src_w, src_h, dst_w, dst_h):
    """The middle part of a src_w x src_h picture with the shape of dst_w x dst_h: (left, top, right, bottom)."""
    if src_w * dst_h > dst_w * src_h:                  # wider than the card: trim the sides
        w = src_h * dst_w / dst_h
        return ((src_w - w) / 2, 0.0, (src_w + w) / 2, float(src_h))
    h = src_w * dst_h / dst_w
    return (0.0, (src_h - h) / 2, float(src_w), (src_h + h) / 2)


def fade_warning(key, t, total, fade):
    """Words for a moment inside the scene's fade-in or fade-out, else None."""
    fade_in, fade_out = fade
    if t < fade_in:
        return f"scene {key} at {t:.3f} s is inside its fade-in (the first {fade_in:g} s): the picture is partly faded"
    if t > total - fade_out:
        return f"scene {key} at {t:.3f} s is inside its fade-out (the last {fade_out:g} s): the picture is partly faded"
    return None


def size_problem(nbytes):
    """Words for a PNG over the limit, else None."""
    if nbytes > LIMIT:
        return f"the thumbnail would be {nbytes:,} bytes, over the {LIMIT:,}-byte limit; nothing written"
    return None


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Draw a branded 1280x720 PNG thumbnail for a video: its "
                                "title, eyebrow and mark in the brand kit's style beside one frame of the video, "
                                "drawn as stills draws it.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--at", metavar="SCENE:SECONDS", help="the frame to show (default: the script's thumbnail-at "
                   "setting); a negative time counts back from the scene's end")
    p.add_argument("--out", metavar="FILE.png", help="where to write it (default: beside the script's output, "
                   "named after it with ' thumbnail.png')")
    p.add_argument("--replace", action="store_true", help="replace the file if it exists")
    p.add_argument("--dry-run", action="store_true",
                   help="check everything and print what would be drawn; write nothing")
    elements.add_arguments(p)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, brand.BrandError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def _layout():
    """The card's outer box (x, y, w, h) and the left block's width."""
    w, h = PICTURE[0] + 2 * CARD_PAD, PICTURE[1] + 2 * CARD_PAD
    x, y = SIZE[0] - MARGIN - w, (SIZE[1] - h) // 2
    return (x, y, w, h), x - GUTTER - MARGIN


def _measurer(family):
    import cairo

    from videotools import draw
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1))

    def measure(s, size):
        return draw.text_width(ctx, s, family, size)

    def cap(size):
        draw.font(ctx, family, size)
        return -ctx.text_extents("H").y_bearing
    return measure, cap


def _run(args):
    data = script.read(args.SCRIPT)
    st = script.settings(data)
    moment = args.at or st["thumbnail-at"]
    if not moment:
        raise cli.Failure("give --at SCENE:SECONDS, or set thumbnail-at in the script's Settings", cli.USAGE)
    key, t = parse_at(moment)
    out = args.out or default_out(args.SCRIPT, st["output"])
    folder = os.path.dirname(os.path.abspath(out))
    if not os.path.isdir(folder):
        raise cli.Failure(f"no folder {folder}; make it, or give --out")
    if os.path.lexists(out) and not args.replace:
        raise cli.Failure(f"{out} already exists; give --replace to replace it, or another --out")
    cli.need("cairo")
    cli.need("PIL")
    from videotools import frame
    video = frame.Video(args.SCRIPT, *elements.from_args(args))
    scene = video.scene(key)
    tl = video.timeline(scene, estimate=True)
    if tl.estimated:
        cues = ", ".join(str(n) for n in tl.estimated)
        sys.stderr.write(f"{PROG}: scene {key} has no narration clips (cues {cues}); "
                         "times are estimated at 2.6 words a second\n")
    spec = moment.strip()
    if t < 0:
        t = tl.total + t
        if t < 0:
            raise cli.Failure(f"{spec} is past the start of scene {key} ({tl.total:.3f} s)", cli.USAGE)
    if t > tl.total:
        raise cli.Failure(f"{spec} is past the end of scene {key} ({tl.total:.3f} s)", cli.USAGE)
    warning = fade_warning(key, t, tl.total, st["fade"])
    if warning:
        sys.stderr.write(f"{PROG}: {warning}\n")
    label = "thumbnail-title" if st["thumbnail-title"] else "title"
    title = st[label]
    family = video.brand["fonts"]["display"]
    measure, cap = _measurer(family)
    card, width = _layout()
    fitted = fit_title(title, width, measure, cap)
    if fitted is None:
        raise cli.Failure(f"the {label} '{title}' does not fit in three lines with capitals at least {MIN_CAP} px "
                          "tall; set a shorter thumbnail-title in the script's Settings")
    size, lines = fitted
    print(f"Title: {len(lines)} line{'s' if len(lines) > 1 else ''} at {size} px (capitals {round(cap(size))} px): "
          + " / ".join(lines))
    print(f"Eyebrow: {st['eyebrow'] or 'none'}")
    print(f"Picture: scene {key} at {t:.3f} s (of {tl.total:.3f} s)")
    if args.dry_run:
        print(f"Would write: {out} (--dry-run: nothing written)")
        return cli.OK
    png = _draw(video, scene, tl, t, st["eyebrow"], size, lines, cap, card)
    problem = size_problem(len(png))
    if problem:
        raise cli.Failure(problem)
    _write(out, png)
    print(f"Wrote {out}: {len(png)} bytes, SHA-256 {hashlib.sha256(png).hexdigest()}")
    return cli.OK


def _picture(video, scene, tl, t):
    """The frame as stills draws it: a step scene's animation area, a card's whole frame; cropped to the
    picture's shape and scaled into it."""
    import cairo
    from PIL import Image

    from videotools import frame, stills
    lay = video.layout
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
    frame.draw_frame(cairo.Context(surface), video, scene, tl, t)
    surface.flush()
    im = stills.to_image(surface)
    if script.kind(scene) == "step":
        ax, ay, aw, ah = lay.area
        im = im.crop((ax, ay, ax + aw, ay + ah))
    return im.resize(PICTURE, Image.LANCZOS, box=cover_box(im.width, im.height, *PICTURE))


def _draw(video, scene, tl, t, eyebrow, size, lines, cap, card):
    """The thumbnail's PNG bytes."""
    import cairo

    from videotools import draw, frame, stills
    kit = video.brand
    family = kit["fonts"]["display"]
    picture = _picture(video, scene, tl, t)              # first: it draws on its own surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *SIZE)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(*kit["colours"]["background"])
    ctx.paint()
    frame.mark(ctx, video, MARGIN + MARK_R, MARGIN + MARK_R, MARK_R, MARK_SIZE)
    # The left block, centred on the frame: eyebrow, title, rule.
    rule_role, rule_h = kit["settings"]["title-rule"]
    rule_h *= 2
    eyebrow_cap = cap(EYEBROW_SIZE)
    title_cap = cap(size)
    height = title_cap + (len(lines) - 1) * LEADING * size + RULE_GAP + rule_h
    if eyebrow:
        height += eyebrow_cap + EYEBROW_GAP
    y = (SIZE[1] - height) / 2
    if eyebrow:
        draw.text(ctx, eyebrow, MARGIN, y + eyebrow_cap, family, EYEBROW_SIZE,
                  brand.text_colour(kit, "accent", EYEBROW_SIZE), track=EYEBROW_TRACK)
        y += eyebrow_cap + EYEBROW_GAP
    baseline = y + title_cap
    for i, line in enumerate(lines):
        draw.text(ctx, line, MARGIN, baseline + i * LEADING * size, family, size, kit["colours"]["ink"])
    ctx.rectangle(MARGIN, baseline + (len(lines) - 1) * LEADING * size + RULE_GAP, RULE_LENGTH, rule_h)
    ctx.set_source_rgb(*brand.colour(kit, rule_role))
    ctx.fill()
    x, y, w, h = card
    draw.fill_rrect(ctx, x, y, w, h, CARD_RADIUS, kit["colours"]["surface"], stroke=kit["colours"]["rule"], lw=BORDER)
    surface.flush()
    im = stills.to_image(surface)
    im.paste(picture, (x + CARD_PAD, y + CARD_PAD))
    buffer = io.BytesIO()
    im.save(buffer, "PNG")
    return buffer.getvalue()


def _write(out, png):
    """`png` at `out` through a temporary file in the same folder and a rename: a failure leaves no
    file with the final name and no temporary file."""
    folder = os.path.dirname(os.path.abspath(out))
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=folder, prefix="." + os.path.basename(out) + ".", suffix=".part")
        with os.fdopen(fd, "wb") as f:
            f.write(png)
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(tmp, 0o666 & ~umask)
        os.replace(tmp, out)
    except OSError as e:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
        raise cli.Failure(f"cannot write {out}: {e.strerror}") from e
