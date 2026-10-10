"""compare-frames: the frame drawn now beside an old video's frame at the same moment.

`compare-frames SCRIPT.md OLD.mp4 SCENE:SECONDS[,…] --out SHEET.png [--offset SCENE=SECONDS …]`:
for each time (as `stills` reads them), the frame drawn from the script and its scene code
beside the old video's frame at the scene's start (the sum of the earlier scenes' lengths from
timing.json, plus any --offset) plus the time; new left, old right, one pair a row, each
labelled under the frame with the mean absolute RGB difference (0-255), printed too. Needs
complete timings as `render` does; pycairo, numpy, Pillow and ffmpeg.
"""

import argparse
import os

from videotools import brand, cli, elements, ffmpeg, script
from videotools.stills import parse_frames, to_image

PROG = "compare-frames"
FRAME_WIDTH = 950         # on the sheet: two frames a row, a gap between


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Draw frames of the video's scenes at the given times and "
                                "put each beside the earlier video's frame at the same moment, with a number for "
                                "how different they are.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("OLD", help="the earlier video (an .mp4)")
    p.add_argument("FRAMES", help="SCENE:SECONDS, comma-separated; a negative time counts back from the scene's end")
    p.add_argument("--out", metavar="SHEET.png", required=True, help="the sheet to write (never over a file)")
    p.add_argument("--offset", metavar="SCENE=SECONDS", action="append", default=[],
                   help="move one scene's start in the old video by so many seconds (repeatable)")
    elements.add_arguments(p)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, brand.BrandError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def parse_offsets(items, video):
    offsets = {}
    for item in items:
        key, sep, seconds = item.partition("=")
        try:
            offsets[key] = float(seconds)
        except ValueError:
            raise cli.Failure(f"--offset should be SCENE=SECONDS, not '{item}'", cli.USAGE) from None
        if not sep or not key:
            raise cli.Failure(f"--offset should be SCENE=SECONDS, not '{item}'", cli.USAGE)
        video.scene(key)                      # an unknown scene is a usage error naming the scenes
    return offsets


def _run(args):
    wanted = parse_frames(args.FRAMES)
    cli.refuse_existing(args.out)
    cairo = cli.need("cairo")
    np = cli.need("numpy")
    cli.need("PIL")
    if not os.path.isfile(args.OLD):
        raise cli.Failure(f"no such file: {args.OLD}")
    ffmpeg.require("ffmpeg")
    ffmpeg.require("ffprobe")
    from PIL import Image, ImageDraw, ImageFont

    from videotools import frame
    from videotools import sheet as sheet_
    video = frame.Video(args.SCRIPT)
    offsets = parse_offsets(args.offset, video)
    starts, at = {}, 0.0
    for scene in video.data["scenes"]:        # every scene's timing, so the starts are exact
        starts[scene["key"]] = at
        at += video.timeline(scene).total
    old_length = ffmpeg.probe(args.OLD)["duration"]
    jobs = []
    for key, t, spec in wanted:
        scene = video.scene(key)
        tl = video.timeline(scene)
        if t < 0:
            t = tl.total + t
        if t > tl.total or t < 0:
            raise cli.Failure(f"{spec} is past the end of scene {key} ({tl.total:.3f} s)", cli.USAGE)
        moment = starts[key] + offsets.get(key, 0.0) + t
        if moment > old_length:
            raise cli.Failure(f"{args.OLD} is {old_length:.3f} s long; scene {key} at {t:.3f} s would be at "
                              f"{moment:.3f} s in it")
        jobs.append((scene, tl, t, moment))
    lay = video.layout
    cell = (FRAME_WIDTH, FRAME_WIDTH * lay.height // lay.width + sheet_.STRIP)
    gap = sheet_.SHEET[0] - 2 * FRAME_WIDTH
    out = Image.new("RGB", (sheet_.SHEET[0], cell[1] * len(jobs)), sheet_.STRIP_FILL)
    draw = ImageDraw.Draw(out)
    font = ImageFont.truetype(video.brand["font_files"]["display"], sheet_.LABEL_SIZE)
    for row, (scene, tl, t, moment) in enumerate(jobs):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
        frame.draw_frame(cairo.Context(surface), video, scene, tl, t)
        surface.flush()
        new = to_image(surface)
        old = Image.frombytes("RGB", (lay.width, lay.height), ffmpeg.frame_at(args.OLD, moment, lay.width, lay.height))
        diff = float(np.abs(np.asarray(new, dtype=np.int16) - np.asarray(old, dtype=np.int16)).mean())
        y = row * cell[1]
        sheet_.paste(out, draw, new, 0, y, cell, f"NEW  {scene['key']} @ {t:.2f} s", font)
        sheet_.paste(out, draw, old, FRAME_WIDTH + gap, y, cell,
                     f"OLD  {moment:.2f} s   mean difference {diff:.1f}", font)
        print(f"{scene['key']:8} {t:7.2f} s  old {moment:7.2f} s  mean difference {diff:5.1f}", flush=True)
    out.save(args.out)
    print(f"Wrote {args.out}: {len(jobs)} pairs")
    return cli.OK
