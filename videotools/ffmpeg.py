"""Running ffmpeg and ffprobe: found on PATH, every exit status checked, output parsed.

The formats parsed here were recorded from ffmpeg 9.0.2 (PLAN.md, "Things checked" 6).
Standard library only.
"""

import json
import re
import shutil
import subprocess

from videotools import cli

QUIET = ["-hide_banner", "-loglevel", "error", "-nostdin"]   # -nostdin: never stop to ask about a file


def require(name):
    """The program's path, or Failure (exit 4) saying how to install it."""
    path = shutil.which(name)
    if not path:
        raise cli.Failure(f"{name} is not on PATH; install ffmpeg as the README says", cli.EXTERNAL)
    return path


def run(name, args, doing, partial=None, stdin=None):
    """Run ffmpeg or ffprobe with `args`; returns its stdout. A non-zero exit is a Failure
    (exit 4) saying what it was doing, with the program's own output and the file that may be
    partial. Nothing is deleted."""
    program = require(name)
    p = subprocess.run([program] + args, capture_output=True, text=True, stdin=stdin)
    if p.returncode != 0:
        tail = f", and {partial} may be partial" if partial else ""
        raise cli.Failure(f"{name} failed (exit {p.returncode}) {doing}; its output follows{tail}\n"
                          + p.stderr.strip(), cli.EXTERNAL)
    return p.stdout


def count_frames(path):
    """The number of video frames in a file, decoded and counted."""
    out = run("ffprobe", ["-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "json", path], f"counting the frames of {path}")
    return int(json.loads(out)["streams"][0]["nb_read_frames"])


def probe(path):
    """{"duration": seconds, "size": bytes, "fps": float, "width", "height", "frames", "sample_rate",
    "channels"} of a media file, from ffprobe's JSON."""
    out = run("ffprobe", ["-v", "error", "-show_entries", "format=duration,size:stream=index,codec_type,"
                          "nb_frames,r_frame_rate,width,height,sample_rate,channels", "-of", "json", path],
              f"reading {path}")
    data = json.loads(out)
    info = {"duration": float(data["format"]["duration"]), "size": int(data["format"]["size"]),
            "fps": None, "width": None, "height": None, "frames": None, "sample_rate": None, "channels": None}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and info["fps"] is None:
            num, den = stream.get("r_frame_rate", "0/1").split("/")
            info["fps"] = float(num) / float(den) if float(den) else None
            info["width"], info["height"] = stream.get("width"), stream.get("height")
            info["frames"] = int(stream["nb_frames"]) if stream.get("nb_frames") else None
        elif stream.get("codec_type") == "audio" and info["sample_rate"] is None:
            info["sample_rate"] = int(stream["sample_rate"]) if stream.get("sample_rate") else None
            info["channels"] = stream.get("channels")
    return info


def levels(path):
    """(mean dB, peak dB) of a file's audio, from the volumedetect filter's last report."""
    program = require("ffmpeg")
    p = subprocess.run([program, "-hide_banner", "-i", path, "-map", "0:a", "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise cli.Failure(f"ffmpeg failed (exit {p.returncode}) measuring the levels of {path}; its output follows\n"
                          + p.stderr.strip(), cli.EXTERNAL)
    mean = re.findall(r"mean_volume: (-?[\d.]+) dB", p.stderr)
    peak = re.findall(r"max_volume: (-?[\d.]+) dB", p.stderr)
    if not mean or not peak:
        raise cli.Failure(f"ffmpeg's volumedetect gave no levels for {path}; its output follows\n" + p.stderr.strip(),
                          cli.EXTERNAL)
    return float(mean[-1]), float(peak[-1])


def silences(path, noise_db=-40, min_seconds=2.0):
    """[(start, end)] of the silences the silencedetect filter finds."""
    program = require("ffmpeg")
    p = subprocess.run([program, "-hide_banner", "-i", path, "-map", "0:a", "-af",
                        f"silencedetect=n={noise_db}dB:d={min_seconds}", "-f", "null", "-"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise cli.Failure(f"ffmpeg failed (exit {p.returncode}) finding silences in {path}; its output follows\n"
                          + p.stderr.strip(), cli.EXTERNAL)
    starts = [float(v) for v in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(v) for v in re.findall(r"silence_end: (-?[\d.]+)", p.stderr)]
    return list(zip(starts, ends))
