"""check-video: length, levels, silences and a frame sheet, compared with the script.

Reads the script and `work/narration/timing.json` to know what the file should be: its length
within one frame of the scenes' total (ffprobe); its peak below 0 dBFS (volumedetect);
silences of 2 s or more (silencedetect, -40 dB) only outside the cues' windows, and narration
heard in every one; with --sheet, one frame from the middle of each scene pasted on a
1920x1080 sheet. Lists every problem; exit 1 if any. Needs ffmpeg and ffprobe, and Pillow for
the sheet.
"""

import argparse
import json
import math
import os
import tempfile

from videotools import cli, ffmpeg, script, timeline

PROG = "check-video"
NOISE_DB, MIN_SILENCE = -40, 2.0
CLIP_LEAD = 0.05        # assemble lays each clip this long after its cue's start
SLACK = 0.1             # silencedetect's boundaries are trusted to this
SHEET_SIZE = (1920, 1080)


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Check a finished video against its script: length, "
                                "levels, silences, and (with --sheet) a frame from each scene.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("VIDEO", nargs="?", help="the file to check (default: the script's output setting)")
    p.add_argument("--sheet", metavar="OUT.png", help="write a sheet of one frame per scene (never over a file)")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def windows(data, settings, timing):
    """[(scene key, cue number, start, end)] of every cue's speech in the whole video, and
    [(scene key, start, end, has cues)] of every scene."""
    cues, scenes, offset = [], [], 0.0
    for scene in data["scenes"]:
        tl = timeline.build(settings, scene, timeline.clips_for(timing, scene))
        clips = timeline.clips_for(timing, scene) or []
        for cue, clip in zip(scene["cues"], clips):
            start = offset + tl.start(cue["n"]) + CLIP_LEAD
            cues.append((scene["key"], cue["n"], start, start + clip))
        scenes.append((scene["key"], offset, offset + tl.total, bool(scene["cues"])))
        offset += tl.total
    return cues, scenes


def describe_silence(a, b, cues, scenes):
    """Where a silence falls: inside a cue (overlapping it by more than the slack), between
    cues, or in a scene with no cues."""
    for key, n, s, e in cues:
        if min(b, e) - max(a, s) > SLACK:
            return f"scene {key} cue {n}, {s:.3f}-{e:.3f}", (key, n, s, e)
    for key, s, e, has_cues in scenes:
        if a < e and b > s and not has_cues:
            return f"scene {key}, no cues", None
    return "between cues", None


def sheet(path, scenes, video_file):
    """One frame from the middle of each scene, pasted in a grid on a 1920x1080 sheet."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as e:
        raise cli.Failure(f"Pillow is not installed in this Python ({e}); install it into the venv as the README says",
                          cli.EXTERNAL)
    n = len(scenes)
    columns = min(n, 4)
    rows = math.ceil(n / columns)
    cell = (SHEET_SIZE[0] // columns, SHEET_SIZE[1] // rows)
    im = Image.new("RGB", SHEET_SIZE, "white")
    draw = ImageDraw.Draw(im)
    with tempfile.TemporaryDirectory() as tmp:
        for i, (key, start, end, _) in enumerate(scenes):
            t = (start + end) / 2
            frame = os.path.join(tmp, f"{i}.png")
            ffmpeg.run("ffmpeg", ffmpeg.QUIET + ["-ss", f"{t:.3f}", "-i", video_file, "-frames:v", "1", frame],
                       f"taking a frame at {t:.3f} s", partial=frame)
            img = Image.open(frame).convert("RGB")
            img = img.resize((cell[0], round(img.height * cell[0] / img.width))) if img.width else img
            x, y = (i % columns) * cell[0], (i // columns) * cell[1]
            im.paste(img, (x, y))
            draw.text((x + 8, y + 6), f"{key} @ {t:.1f} s", fill=(0, 0, 0))
    im.save(path)


def _run(args):
    data = script.read(args.SCRIPT)
    settings = script.settings(data)
    video = script.folder(args.SCRIPT)
    video_file = args.VIDEO or os.path.join(video, settings["output"])
    if args.sheet:
        cli.refuse_existing(args.sheet)
    if not os.path.isfile(video_file):
        raise cli.Failure(f"no such file: {video_file}")
    timing_path = os.path.join(video, "work", "narration", "timing.json")
    if not os.path.isfile(timing_path):
        raise cli.Failure(f"no {timing_path}; run narrate first")
    with open(timing_path, encoding="utf-8") as f:
        timing = json.load(f)
    cues, scenes = windows(data, settings, timing)
    expected = scenes[-1][2] if scenes else 0.0
    problems = []
    print(video_file)
    info = ffmpeg.probe(video_file)
    fps = info["fps"] or settings["fps"]
    off = abs(info["duration"] - expected) * fps
    verdict = "OK" if off <= 1.0 + 1e-6 else f"{off:.1f} frames off, more than one"
    print(f"length {info['duration']:.3f} s; the script's scenes give {expected:.3f} s: {verdict}")
    if verdict != "OK":
        problems.append(f"length {info['duration']:.3f} s; the script's scenes give {expected:.3f} s: {verdict}")
    mean, peak = ffmpeg.levels(video_file)
    verdict = "OK" if peak < 0 else "at or above 0 dBFS, clipping"
    print(f"peak {peak:.1f} dBFS, mean {mean:.1f} dBFS: {verdict}")
    if verdict != "OK":
        problems.append(f"peak {peak:.1f} dBFS: {verdict}")
    found = ffmpeg.silences(video_file, NOISE_DB, MIN_SILENCE)
    described, silent_cues, inside = [], [], 0
    for a, b in found:
        where, cue = describe_silence(a, b, cues, scenes)
        described.append(f"{a:.3f}-{b:.3f} ({where})")
        if cue:
            inside += 1
            key, n, s, e = cue
            problems.append(f"silence at {a:.3f}-{b:.3f} overlaps scene {key} cue {n} ({s:.3f}-{e:.3f})")
            if a <= s + SLACK and b >= e - SLACK and cue not in silent_cues:
                silent_cues.append(cue)
    verdict = "OK" if not inside else f"{inside} inside a cue"
    print(f"silences of {MIN_SILENCE:g} s or more: {len(found)}, at {', '.join(described) or 'none'}: {verdict}"
          if found else f"silences of {MIN_SILENCE:g} s or more: none: OK")
    if silent_cues:
        print("narration in every cue's window: " + ", ".join(
            f"scene {key} cue {n} ({s:.3f}-{e:.3f}) is silent" for key, n, s, e in silent_cues))
        problems += [f"no narration heard in scene {key} cue {n} ({s:.3f}-{e:.3f})" for key, n, s, e in silent_cues]
    else:
        print("narration in every cue's window: OK")
    if args.sheet:
        sheet(args.sheet, scenes, video_file)
        print(f"sheet of {len(scenes)} frames written to {args.sheet}")
    if problems:
        print(f"{len(problems)} problem{'' if len(problems) == 1 else 's'}:")
        for p in problems:
            print("  - " + p)
        return cli.PROBLEMS
    print("No problems found.")
    return cli.OK
