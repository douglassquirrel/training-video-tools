"""render: each scene to a video segment through ffmpeg.

`render SCRIPT.md [--scenes KEY,…] [--frames A-B] [--replace] [--dry-run]`: every frame of a
scene drawn with cairo and piped as raw BGRA to ffmpeg (libx264, the script's quality as CRF,
veryfast, yuv420p, the script's fps) into `work/segments/<scene>_<first frame>.mp4`. Refuses
without complete timings, and an existing segment unless --replace. ffmpeg's exit status is
checked and the segment's frames counted; a failure names the partial file and leaves it.
Needs pycairo and ffmpeg.
"""

import argparse
import os
import subprocess
import time

import cairo

from videotools import cli, ffmpeg, frame, script

PROG = "render"


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Render each scene of a video to a segment in "
                                "work/segments/, frame by frame through ffmpeg.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--scenes", metavar="KEY,...", help="only these scenes (default: all, in script order)")
    p.add_argument("--frames", metavar="A-B", help="only frames A to B (B excluded) of the one scene in --scenes")
    p.add_argument("--replace", action="store_true", help="write over existing segments, listing them first")
    p.add_argument("--dry-run", action="store_true",
                   help="list the scenes, their lengths, frame counts and segments; write nothing")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def segment_name(scene, first):
    return f"{scene['key']}_{first:05d}.mp4"


def encode(video, scene, tl, first, last, path):
    """Draw frames first..last-1 of the scene into ffmpeg; returns (frames, seconds taken)."""
    st, lay = video.settings, video.layout
    args = [ffmpeg.require("ffmpeg")] + ffmpeg.QUIET + [
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{lay.width}x{lay.height}", "-r", str(st["fps"]), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(st["quality"]), "-pix_fmt", "yuv420p",
        "-r", str(st["fps"]), path]
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, lay.width, lay.height)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    started = time.time()
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    died = False
    for f in range(first, last):
        frame.draw_frame(ctx, video, scene, tl, f / st["fps"])
        surface.flush()
        try:
            p.stdin.write(bytes(surface.get_data()))
        except BrokenPipeError:
            died = True
            break
    try:
        p.stdin.close()
    except BrokenPipeError:
        died = True
    stderr = p.stderr.read()
    p.wait()
    if p.returncode != 0 or died:
        raise cli.Failure(f"ffmpeg failed (exit {p.returncode}) encoding scene {scene['key']}; its output follows, "
                          f"and {path} may be partial\n" + stderr.decode(errors="replace").strip(), cli.EXTERNAL)
    return last - first, time.time() - started


def _run(args):
    video = frame.Video(args.SCRIPT)
    scenes = script.select(video.data, args.scenes)
    folder = os.path.join(video.folder, "work", "segments")
    jobs = []
    for scene in scenes:
        tl = video.timeline(scene)
        first, last = 0, tl.frames
        if args.frames:
            if len(scenes) != 1:
                raise cli.Failure("--frames needs exactly one scene in --scenes", cli.USAGE)
            try:
                first, last = (int(v) for v in args.frames.split("-"))
            except ValueError:
                raise cli.Failure(f"--frames should be A-B, not '{args.frames}'", cli.USAGE) from None
            if not 0 <= first < last <= tl.frames:
                raise cli.Failure(f"--frames {args.frames} is outside scene {scene['key']}'s {tl.frames} frames",
                                  cli.USAGE)
        jobs.append((scene, tl, first, last, os.path.join(folder, segment_name(scene, first))))
    if args.dry_run:
        for scene, tl, first, last, path in jobs:
            print(f"{scene['key']}  {tl.total:.3f} s  {tl.frames} frames  -> {path}"
                  + (f"  (frames {first}-{last})" if (first, last) != (0, tl.frames) else ""))
        print(f"{len(jobs)} scenes, {sum(tl.total for _, tl, _, _, _ in jobs):.3f} s, "
              f"{sum(tl.frames for _, tl, _, _, _ in jobs)} frames; nothing written (dry run).")
        return cli.OK
    existing = [path for _, _, _, _, path in jobs if os.path.lexists(path)]
    if existing and not args.replace:
        raise cli.Failure("these would be written over; delete them, or run with --replace:\n"
                          + "\n".join("  " + p for p in existing))
    ffmpeg.require("ffmpeg")
    ffmpeg.require("ffprobe")
    if existing:
        print("Replacing:\n" + "\n".join("  " + p for p in existing))
    os.makedirs(folder, exist_ok=True)
    for scene, tl, first, last, path in jobs:
        print(f"{scene['key']}  {tl.total:.3f} s  {tl.frames} frames", flush=True)
        n, seconds = encode(video, scene, tl, first, last, path)
        counted = ffmpeg.count_frames(path)
        if counted != n:
            raise cli.Failure(f"{path} holds {counted} frames, not the {n} rendered; it is left for inspection",
                              cli.EXTERNAL)
        rate = n / max(seconds, 1e-6)
        print(f"Rendered {scene['key']}: {n} frames in {seconds:.1f} s ({rate:.1f} frames/s) -> {path}", flush=True)
    return cli.OK
