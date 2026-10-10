"""frame-hashes: the MD5 of every frame a scene draws, written to a file or compared with one.

`frame-hashes SCRIPT.md (--out HASHES.json [--merge] | --compare HASHES.json) [--scenes KEY,…]
[--step N]`: every N-th frame of each scene drawn as `render` draws it (cairo, no ffmpeg) and
the MD5 of its pixels recorded by scene and frame number, `{"<scene>": {"<frame>": "<md5>"}}`.
--out refuses an existing file unless --merge (the other scenes kept); --compare lists, per
scene, the frames whose pixels differ from the file's, exit 1 if any. Needs complete timings,
as `render` does, and pycairo.
"""

import argparse
import hashlib
import json
import os
import time

from videotools import brand, cli, elements, script

PROG = "frame-hashes"
SHOWN = 12            # differing frame numbers listed before an ellipsis


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Record the MD5 of every frame each scene draws, or compare "
                                "the frames drawn now with such a record, to show what a change changed.")
    p.add_argument("SCRIPT", help="the video's script.md")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--out", metavar="HASHES.json", help="write the hashes here (never over a file, unless --merge)")
    g.add_argument("--compare", metavar="HASHES.json", help="compare with the hashes in this file")
    p.add_argument("--merge", action="store_true", help="with --out: add these scenes to an existing file, "
                   "keeping its other scenes")
    p.add_argument("--scenes", metavar="KEY,...", help="only these scenes (default: all, in script order)")
    p.add_argument("--step", metavar="N", type=int, default=1, help="hash every N-th frame of a scene (default 1)")
    elements.add_arguments(p)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, brand.BrandError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def compare(hashes, reference):
    """(the frame numbers whose hash differs from the reference's or is not there, in order;
    those not there at all)."""
    bad = sorted(int(n) for n, h in hashes.items() if reference.get(n) != h)
    missing = sorted(int(n) for n in hashes if n not in reference)
    return bad, missing


def describe(bad, missing):
    if not bad:
        return "all match"
    shown = ", ".join(str(n) for n in bad[:SHOWN]) + (", …" if len(bad) > SHOWN else "")
    note = f", {len(missing)} not in the reference" if missing else ""
    return f"{len(bad)} differ (frames {shown}){note}"


def hash_scene(video, scene, tl, step):
    """{frame number as text: md5 of its pixels} for frames 0, step, 2·step, … of the scene."""
    import cairo

    from videotools import frame
    lay = video.layout
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    hashes = {}
    for n in range(0, tl.frames, step):
        frame.draw_frame(ctx, video, scene, tl, n / tl.fps)
        surface.flush()
        hashes[str(n)] = hashlib.md5(bytes(surface.get_data())).hexdigest()
    return hashes


def _load(path):
    if not os.path.isfile(path):
        raise cli.Failure(f"no such file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _run(args):
    if args.step < 1:
        raise cli.Failure("--step must be 1 or more", cli.USAGE)
    reference, result = {}, {}
    if args.compare:
        reference = _load(args.compare)
    elif os.path.lexists(args.out):
        if not args.merge:
            raise cli.Failure(f"{args.out} already exists; give a new name, or --merge to add scenes to it")
        result = _load(args.out)
    cli.need("cairo")
    from videotools import frame
    video = frame.Video(args.SCRIPT)
    scenes = script.select(video.data, args.scenes)
    timelines = [(scene, video.timeline(scene)) for scene in scenes]   # every scene's timing checked first
    differ = 0
    for scene, tl in timelines:
        started = time.time()
        hashes = hash_scene(video, scene, tl, args.step)
        took = time.time() - started
        key = scene["key"]
        if args.compare:
            bad, missing = compare(hashes, reference.get(key, {}))
            differ += len(bad)
            print(f"{key:8} {len(hashes):5} frames in {took:5.1f} s: {describe(bad, missing)}", flush=True)
        else:
            result[key] = hashes
            print(f"{key:8} {len(hashes):5} frames in {took:5.1f} s", flush=True)
    if args.compare:
        print("All frames match." if not differ else f"{differ} frames differ.")
        return cli.PROBLEMS if differ else cli.OK
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=0)
    frames = sum(len(v) for v in result.values())
    print(f"Wrote {args.out}: {frames} frames, {len(result)} scene{'s' if len(result) != 1 else ''}")
    return cli.OK
