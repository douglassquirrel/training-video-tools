"""assemble: the scene segments and the narration clips into the finished video.

Joins `work/segments/<scene>_<frame>.mp4` in script order (ffmpeg's concat demuxer, streams
copied), lays every clip at its scene's start plus its cue's start plus 50 ms in a 48 kHz mix
peak-normalised to 0.89 (`work/assemble/narration.wav`), and muxes the two (AAC 160 kb/s, fast
start) to the script's `output` or `--out`. Refuses, naming each, a scene with no segment,
segments whose frames do not add up or do not chain, a cue with no clip, missing timings, an
existing output; existing intermediates unless --replace. Needs numpy, soundfile and ffmpeg.
"""

import argparse
import hashlib
import json
import os
import re

from videotools import cli, ffmpeg, script, timeline

PROG = "assemble"
MIX_RATE = 48000
CLIP_LEAD = 0.05
PEAK = 0.89
SEGMENT = re.compile(r"^(.+)_(\d{5})\.mp4$")


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Join the rendered segments in script order, mix the "
                                "narration clips in at their cue times, and write the finished video.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--out", metavar="FILE", help="the finished video (default: the script's output setting)")
    p.add_argument("--replace", action="store_true",
                   help="write over existing intermediates in work/assemble/ (never the finished video)")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def segments_of(folder, key):
    """The scene's segment files in frame order: [(first frame, path)]."""
    found = []
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            m = SEGMENT.match(name)
            if m and m.group(1) == key:
                found.append((int(m.group(2)), os.path.join(folder, name)))
    return sorted(found)


def check_inputs(data, settings, video, timing):
    """Timelines, segment lists and clip paths for every scene, or Failure naming every gap."""
    problems, plan = [], []
    seg_dir = os.path.join(video, "work", "segments")
    clip_dir = os.path.join(video, "work", "narration")
    for scene in data["scenes"]:
        tl = timeline.build(settings, scene, timeline.clips_for(timing, scene))
        segs = segments_of(seg_dir, scene["key"])
        if not segs:
            problems.append(f"scene {scene['key']} has no segment in {seg_dir}")
        clips = [os.path.join(clip_dir, f"{scene['key']}_{cue['n']:02d}.wav") for cue in scene["cues"]]
        for cue, path in zip(scene["cues"], clips):
            if not os.path.isfile(path):
                problems.append(f"scene {scene['key']} cue {cue['n']} has no clip: {path}")
        plan.append((scene, tl, segs, clips))
    if problems:
        raise cli.Failure(("\n" + PROG + ": ").join(problems))
    return plan


def check_frames(plan):
    """Every scene's segments chain from frame 0 and add up to its frame count (ffprobe)."""
    for scene, tl, segs, _ in plan:
        total = 0
        for first, path in segs:
            if first != total:
                raise cli.Failure(f"scene {scene['key']}: segment {os.path.basename(path)} starts at frame {first} "
                                  f"but the segments before it end at {total}")
            total += ffmpeg.count_frames(path)
        if total != tl.frames:
            raise cli.Failure(f"scene {scene['key']}: its segments hold {total} frames, the script's timing gives {tl.frames}")


def narration(plan, out_path):
    """The mix of every clip at its time, 48 kHz mono, peak-normalised; written to out_path."""
    import numpy as np
    import soundfile
    total = sum(tl.total for _, tl, _, _ in plan)
    mix = np.zeros(round(total * MIX_RATE), dtype=np.float32)
    offset = 0.0
    for scene, tl, _, clips in plan:
        for cue, path in zip(scene["cues"], clips):
            wav, rate = soundfile.read(path, dtype="float32")
            if wav.ndim > 1:
                wav = wav.mean(axis=1)
            if rate != MIX_RATE:
                n = round(len(wav) * MIX_RATE / rate)
                wav = np.interp(np.arange(n) * rate / MIX_RATE, np.arange(len(wav)), wav).astype(np.float32)
            start = round((offset + tl.start(cue["n"]) + CLIP_LEAD) * MIX_RATE)
            end = min(start + len(wav), len(mix))
            mix[start:end] += wav[:end - start]
        offset += tl.total
    peak = float(np.max(np.abs(mix))) if len(mix) else 0.0
    if peak > 0:
        mix *= PEAK / peak
    soundfile.write(out_path, mix, MIX_RATE)
    return total


def _run(args):
    data = script.read(args.SCRIPT)
    settings = script.settings(data)
    video = script.folder(args.SCRIPT)
    timing_path = os.path.join(video, "work", "narration", "timing.json")
    if not os.path.isfile(timing_path):
        raise cli.Failure(f"no {timing_path}; run narrate first")
    with open(timing_path, encoding="utf-8") as f:
        timing = json.load(f)
    out_file = args.out or os.path.join(video, settings["output"])
    cli.refuse_existing(out_file)
    plan = check_inputs(data, settings, video, timing)
    work = os.path.join(video, "work", "assemble")
    intermediates = [os.path.join(work, name) for name in ("narration.wav", "segments.txt", "video-only.mp4")]
    existing = [p for p in intermediates if os.path.lexists(p)]
    if existing and not args.replace:
        raise cli.Failure("these would be written over; delete them, or run with --replace:\n"
                          + "\n".join("  " + p for p in existing))
    ffmpeg.require("ffprobe")
    ffmpeg.require("ffmpeg")
    check_frames(plan)
    if existing:
        print("Replacing:\n" + "\n".join("  " + p for p in existing))
    os.makedirs(work, exist_ok=True)
    narration_path, list_path, video_only = intermediates
    total = narration(plan, narration_path)
    with open(list_path, "w", encoding="utf-8") as f:
        for _, _, segs, _ in plan:
            for _, path in segs:
                f.write(f"file '{path}'\n")
    print(f"Narration mixed: {total:.3f} s to {narration_path}", flush=True)
    ffmpeg.run("ffmpeg", ffmpeg.QUIET + ["-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", video_only],
               "joining the segments", partial=video_only)
    print(f"Segments joined to {video_only}", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    ffmpeg.run("ffmpeg", ffmpeg.QUIET + ["-i", video_only, "-i", narration_path, "-c:v", "copy", "-c:a", "aac",
                                         "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out_file],
               "muxing the narration", partial=out_file)
    frames = sum(tl.frames for _, tl, _, _ in plan)
    sha = hashlib.sha256()
    with open(out_file, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha.update(chunk)
    print(f"Wrote {out_file}")
    print(f"length {total:.3f} s ({frames} frames), size {os.path.getsize(out_file)} bytes")
    print(f"sha256 {sha.hexdigest()}")
    return cli.OK
