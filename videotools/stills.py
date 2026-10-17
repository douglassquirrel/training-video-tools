"""stills: frames at chosen times on labelled sheets, for looking before rendering.

`stills SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]`: each frame drawn at full
size, scaled into a cell of a 1920x1080 sheet with its scene, time and cue in a strip under it
(never over it); a negative time counts back from the scene's end. Works on estimated timings,
with a warning.

`stills SCRIPT.md --cue-changes [--scenes KEY,…] --out SHEET.png [--grid CxR]`: the frames at
−0.3, 0 and +0.3 s around every cue start (and +0.6 s for the cue after a mistake, when the
panels have gone), on as many sheets as needed (`SHEET-1.png`, `SHEET-2.png`, …), with a warning
for a picture that vanishes as the mistake panels lift (PLAN.md item 14). Needs pycairo and
Pillow.
"""

import argparse
import sys

from videotools import brand, cli, elements, script
from videotools import sheet as sheet_
from videotools.sheet import SHEET

PROG = "stills"
AROUND = (-0.3, 0.0, 0.3)          # seconds around a cue start, with --cue-changes
AFTER_CURTAIN = 0.6                # and this much after the cue that follows a mistake
LIFT_FROM, LIFT_TO = -0.4, 0.1     # the panels lift over this span around the next cue's start (timeline.curtain)
VANISHED_SHARE = 0.002             # of the animation area's pixels: more than this vanishing as the panels lift warns
NEAR = 8                           # a pixel within this of the background, per channel, counts as background


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Draw frames of a video's scenes at the given times "
                                "onto one sheet, each labelled, so the layout can be checked before rendering; "
                                "or, with --cue-changes, the frames around every cue start.")
    p.add_argument("SCRIPT", metavar="SCRIPT|VIDEO",
                   help="the video's script.md, or a video file (any name not ending .md): then --at, --every or "
                        "--changes choose the frames, --out is the folder for the stills and --sheet the sheet")
    p.add_argument("FRAMES", nargs="?", help="SCENE:SECONDS, comma-separated; a negative time counts back from the "
                   "scene's end (not with --cue-changes)")
    p.add_argument("--cue-changes", action="store_true",
                   help="the frames at -0.3, 0 and +0.3 s around every cue start (+0.6 s after a mistake), "
                        "on numbered sheets, with a warning for a picture that vanishes as the mistake panels lift")
    p.add_argument("--scenes", metavar="KEY,...", help="with --cue-changes: only these scenes (default: all)")
    p.add_argument("--out", metavar="SHEET.png|FOLDER", required=True,
                   help="the sheet to write, or for a video file the folder for the stills (never over a file)")
    p.add_argument("--grid", metavar="CxR", default=None,
                   help="columns x rows of a sheet (default 2x2; for a video file, chosen to fit)")
    p.add_argument("--at", metavar="T,T,...", help="video file: frames at these times, in seconds")
    p.add_argument("--every", metavar="SECONDS", type=float, help="video file: a frame every so many seconds from 0")
    p.add_argument("--changes", action="store_true",
                   help="video file: the first frame and every frame where the picture changes (ffmpeg's scene "
                        "detection)")
    p.add_argument("--threshold", metavar="N",
                   help="with --changes: how big a change counts, 0 to 1 (default 0.3)")
    p.add_argument("--sheet", metavar="SHEET.png", help="video file: also a contact sheet of the stills, labelled")
    elements.add_arguments(p)
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


def cue_change_times(tl):
    """The times to look at for a scene: around every cue start, and after the panels have gone
    for the cue that follows a mistake; clipped to the scene."""
    times = []
    for n in range(1, len(tl._starts) + 1):
        offsets = AROUND + ((AFTER_CURTAIN,) if tl.mistake is not None and n == tl.mistake + 1 else ())
        for d in offsets:
            t = tl.start(n) + d
            if 0 <= t <= tl.total and (not times or abs(t - times[-1]) > 1e-9):
                times.append(round(t, 3))
    return times


def vanished_as_the_curtain_lifts(video, scene, tl):
    """How many pixels of the animation area the scene code draws (without the panels) at the
    moment the panels start to lift that are background by the moment they have gone: the glimpse."""
    import cairo
    from PIL import ImageChops

    from videotools import frame
    lay = video.layout
    area = (lay.area[0], lay.area[1], lay.area[0] + lay.area[2], lay.area[1] + lay.area[3])
    background = to_image(video.background()).crop(area)
    looks = []
    for t in (tl.start(tl.mistake + 1) + LIFT_FROM, tl.start(tl.mistake + 1) + LIFT_TO):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
        frame.draw_frame(cairo.Context(surface), video, scene, tl, t, curtain=False)
        surface.flush()
        looks.append(ImageChops.difference(to_image(surface).crop(area), background).convert("L"))
    drawn_then = looks[0].point(lambda v: 255 if v > NEAR else 0)
    gone_after = looks[1].point(lambda v: 255 if v <= NEAR else 0)
    return ImageChops.multiply(drawn_then, gone_after).histogram()[255]


def _run(args):
    if not args.SCRIPT.lower().endswith(".md"):
        for given, flag in ((args.FRAMES, "SCENE:SECONDS"), (args.cue_changes, "--cue-changes"),
                            (args.scenes, "--scenes"), (args.elements, "--elements"), (args.renderer, "--renderer")):
            if given:
                raise cli.Failure(f"{flag} goes with a script, not a video file", cli.USAGE)
        from videotools import video_stills
        return video_stills.run(args)
    for given, flag in ((args.at, "--at"), (args.every, "--every"), (args.changes, "--changes"),
                        (args.threshold, "--threshold"), (args.sheet, "--sheet")):
        if given is not None and given is not False:
            raise cli.Failure(f"{flag} goes with a video file, not a script", cli.USAGE)
    args.grid = args.grid or "2x2"
    if args.cue_changes and args.FRAMES:
        raise cli.Failure("--cue-changes takes no SCENE:SECONDS (it chooses the times itself)", cli.USAGE)
    if not args.cue_changes and not args.FRAMES:
        raise cli.Failure("give SCENE:SECONDS, or --cue-changes", cli.USAGE)
    wanted = parse_frames(args.FRAMES) if args.FRAMES else []
    from videotools import video_stills
    columns, rows = video_stills.parse_grid(args.grid)
    if wanted and len(wanted) > columns * rows:
        raise cli.Failure(f"{len(wanted)} frames do not fit a {columns}x{rows} grid; give a bigger --grid", cli.USAGE)
    cli.refuse_existing(args.out)
    cli.need("cairo")
    cli.need("PIL")
    from videotools import frame
    video = frame.Video(args.SCRIPT, *elements.from_args(args))
    timelines, warned, jobs = {}, set(), []

    def timeline_for(scene):
        key = scene["key"]
        if key not in timelines:
            timelines[key] = video.timeline(scene, estimate=True)
            tl = timelines[key]
            if tl.estimated and key not in warned:
                warned.add(key)
                cues = ", ".join(str(n) for n in tl.estimated)
                sys.stderr.write(f"{PROG}: scene {key} has no narration clips (cues {cues}); "
                                 "times are estimated at 2.6 words a second\n")
        return timelines[key]

    if args.cue_changes:
        for scene in script.select(video.data, args.scenes):
            tl = timeline_for(scene)
            jobs += [(scene, tl, t) for t in cue_change_times(tl)]
    else:
        for key, t, spec in wanted:
            scene = video.scene(key)
            tl = timeline_for(scene)
            if t < 0:
                t = tl.total + t
            if t > tl.total or t < 0:
                raise cli.Failure(f"{spec} is past the end of scene {key} ({tl.total:.3f} s)", cli.USAGE)
            jobs.append((scene, tl, t))
    per_sheet = columns * rows
    chunks = [jobs[i:i + per_sheet] for i in range(0, len(jobs), per_sheet)] or [[]]
    names = sheet_.names(args.out, len(chunks))
    for name in names:
        cli.refuse_existing(name)
    for name, chunk in zip(names, chunks):
        draw_sheet(video, chunk, name, columns, rows)
    if args.cue_changes:
        for scene in script.select(video.data, args.scenes):
            tl = timelines[scene["key"]]
            if tl.mistake is None or tl.mistake >= len(tl._starts):
                continue
            count = vanished_as_the_curtain_lifts(video, scene, tl)
            if count > VANISHED_SHARE * video.layout.area[2] * video.layout.area[3]:
                sys.stderr.write(f"{PROG}: scene {scene['key']}: something drawn under the panel at cue {tl.mistake} "
                                 f"vanishes as it lifts for cue {tl.mistake + 1} ({count} pixels); fade it out while "
                                 "covered: frame.timeline.before_curtain\n")
    return cli.OK


def draw_sheet(video, jobs, out, columns, rows):
    """The frames of `jobs` (scene, timeline, seconds) on one sheet at `out`, each labelled under it."""
    import cairo
    from PIL import Image, ImageDraw, ImageFont

    from videotools import frame
    from videotools import sheet as sheet_
    sheet = Image.new("RGB", SHEET, "white")
    draw = ImageDraw.Draw(sheet)
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
        sheet_.paste(sheet, draw, to_image(surface), x, y, cell, label, font)   # the label under the frame
        print(f"{scene['key']} at {t:.3f} s (of {tl.total:.3f} s, {f'cue {cue}' if cue else 'no cue'})")
    sheet.save(out)
    print(f"Wrote {out}: {len(jobs)} frames, {columns}x{rows}")
