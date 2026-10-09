"""stills: frames at chosen times on one sheet, for looking before rendering.

`stills SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]`: each frame drawn at full
size, scaled into a cell of a 1920x1080 sheet with its scene, time and cue in a strip under it
(never over it); a negative
time counts back from the scene's end. Works on estimated timings, with a warning. Needs
pycairo and Pillow.
"""

import argparse
import sys

from videotools import brand, cli, script
from videotools.sheet import SHEET

PROG = "stills"


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
    cairo = cli.need("cairo")
    cli.need("PIL")
    from PIL import Image, ImageDraw, ImageFont

    from videotools import frame
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
    from videotools import sheet as sheet_
    out = Image.new("RGB", SHEET, "white")
    draw = ImageDraw.Draw(out)
    cell = (SHEET[0] // columns, SHEET[1] // rows)
    font = ImageFont.truetype(video.brand["font_files"]["display"], sheet_.LABEL_SIZE)
    lay = video.layout
    for i, (scene, tl, t) in enumerate(jobs):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
        frame.draw_frame(cairo.Context(surface), video, scene, tl, t)
        surface.flush()
        x, y = (i % columns) * cell[0], (i // columns) * cell[1]
        cue = tl.cue(t)
        label = f"{scene['key']} @ {t:.2f} s" + (f"  cue {cue}" if cue else "")
        sheet_.paste(out, draw, to_image(surface), x, y, cell, label, font)   # the label under the frame
        print(f"{scene['key']} at {t:.3f} s (of {tl.total:.3f} s, {f'cue {cue}' if cue else 'no cue'})")
    out.save(args.out)
    print(f"Wrote {args.out}: {len(jobs)} frames, {columns}x{rows}")
    return cli.OK
