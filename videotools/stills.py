"""stills: frames at chosen times on one sheet, for looking before rendering.

`stills SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]`: each frame drawn at full
size, scaled into a cell of a 1920x1080 sheet with its scene, time and cue in a strip under it
(never over it); a negative
time counts back from the scene's end. Works on estimated timings, with a warning. Needs
pycairo and Pillow.
"""

import argparse
import sys

import cairo

from videotools import brand, cli, frame, script

PROG = "stills"
SHEET = (1920, 1080)
STRIP = 36            # the label's strip under each frame, in pixels; never over the frame


def frame_size(cell, size=(1920, 1080)):
    """The largest frame of the video's proportions that fits the cell above its label strip."""
    cw, ch = cell[0], cell[1] - STRIP
    w = min(cw, ch * size[0] // size[1])
    return w, w * size[1] // size[0]


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Draw frames of a video's scenes at the given times "
                                "onto one sheet, each labelled, so the layout can be checked before rendering.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("FRAMES", help="SCENE:SECONDS, comma-separated; a negative time counts back from the scene's end")
    p.add_argument("--out", metavar="SHEET.png", required=True, help="the sheet to write (never over a file)")
    p.add_argument("--grid", metavar="CxR", default="2x2", help="columns x rows of the sheet (default 2x2)")
    return p


def parse_frames(text):
    out = []
    for part in text.split(","):
        part = part.strip()
        key, sep, seconds = part.partition(":")
        try:
            out.append((key, float(seconds), part))
        except ValueError:
            raise cli.Failure(f"'{part}' is not SCENE:SECONDS", cli.USAGE) from None
        if not sep or not key:
            raise cli.Failure(f"'{part}' is not SCENE:SECONDS", cli.USAGE)
    return out


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, brand.BrandError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def to_image(surface):
    from PIL import Image
    return Image.frombuffer("RGBA", (surface.get_width(), surface.get_height()), bytes(surface.get_data()),
                            "raw", "BGRA", surface.get_stride(), 1).convert("RGB")


def _run(args):
    wanted = parse_frames(args.FRAMES)
    try:
        columns, rows = (int(v) for v in args.grid.lower().split("x"))
    except ValueError:
        raise cli.Failure(f"--grid should be COLUMNSxROWS, not '{args.grid}'", cli.USAGE) from None
    if len(wanted) > columns * rows:
        raise cli.Failure(f"{len(wanted)} frames do not fit a {columns}x{rows} grid; give a bigger --grid", cli.USAGE)
    cli.refuse_existing(args.out)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as e:
        raise cli.Failure(f"Pillow is not installed in this Python ({e}); install it into the venv as the README says",
                          cli.EXTERNAL) from e
    video = frame.Video(args.SCRIPT)
    timelines, warned, jobs = {}, set(), []
    for key, t, spec in wanted:
        scene = video.scene(key)
        if key not in timelines:
            timelines[key] = video.timeline(scene, estimate=True)
            tl = timelines[key]
            if tl.estimated and key not in warned:
                warned.add(key)
                cues = ", ".join(str(n) for n in tl.estimated)
                sys.stderr.write(f"{PROG}: scene {key} has no narration clips (cues {cues}); "
                                 "times are estimated at 2.6 words a second\n")
        tl = timelines[key]
        if t < 0:
            t = tl.total + t
        if t > tl.total or t < 0:
            raise cli.Failure(f"{spec} is past the end of scene {key} ({tl.total:.3f} s)", cli.USAGE)
        jobs.append((scene, tl, t))
    sheet = Image.new("RGB", SHEET, "white")
    draw = ImageDraw.Draw(sheet)
    cell = (SHEET[0] // columns, SHEET[1] // rows)
    font = ImageFont.truetype(video.brand["font_files"]["display"], 22)
    lay = video.layout
    size = frame_size(cell, (lay.width, lay.height))
    for i, (scene, tl, t) in enumerate(jobs):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
        frame.draw_frame(cairo.Context(surface), video, scene, tl, t)
        surface.flush()
        img = to_image(surface).resize(size, Image.LANCZOS)
        x, y = (i % columns) * cell[0], (i // columns) * cell[1]
        sheet.paste(img, (x, y))
        cue = tl.cue(t)
        label = f"{scene['key']} @ {t:.2f} s" + (f"  cue {cue}" if cue else "")
        # The label in a strip under the frame: no pixel of the frame is covered.
        draw.rectangle([x, y + size[1], x + size[0] - 1, y + size[1] + STRIP - 1], fill=(0x55, 0x55, 0x55))
        draw.text((x + 8, y + size[1] + 4), label, font=font, fill=(255, 255, 255))
        print(f"{scene['key']} at {t:.3f} s (of {tl.total:.3f} s, {f'cue {cue}' if cue else 'no cue'})")
    sheet.save(args.out)
    print(f"Wrote {args.out}: {len(jobs)} frames, {columns}x{rows}")
    return cli.OK
