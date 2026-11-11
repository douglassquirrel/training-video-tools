"""Tier 2: whole commands run as subprocesses, against stubs and copies of the example."""

import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLES = os.path.join(REPO, "examples")
STUBS = os.path.join(REPO, "tests", "stubs")


# Settings the user's shell may export (the README tells device-shell users to export
# TRAINING_VIDEO_TOOLS_PYTHON, and before the rename VIDEO_TOOLS_PYTHON) that would change what a
# command under test does: a test sets them on purpose or not at all. FONTCONFIG_FILE: set in-process
# by fonts.load on Linux; a child must set its own.
USER_SETTINGS = ("TRAINING_VIDEO_TOOLS_PYTHON", "TRAINING_VIDEO_TOOLS_CONF", "VIDEO_TOOLS_PYTHON", "VIDEO_TOOLS_CONF",
                 "FONTCONFIG_FILE")


def clean_env(**overrides):
    """A copy of the environment without the user's own training-video-tools settings, plus `overrides`."""
    env = {k: v for k, v in os.environ.items() if k not in USER_SETTINGS}
    env.update(overrides)
    return env


def run(command, *args, cwd=None, env=None):
    """Run a top-level command script with the venv's Python; (exit code, stdout, stderr)."""
    full_env = clean_env()
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Let coverage.py measure the subprocess too (pyproject.toml: parallel = true).
    full_env.setdefault("COVERAGE_PROCESS_START", os.path.join(REPO, "pyproject.toml"))
    full_env.update(env or {})
    full_env = {k: v for k, v in full_env.items() if v is not None}   # None in `env` unsets a variable
    p = subprocess.run([sys.executable, os.path.join(REPO, command)] + [str(a) for a in args],
                       capture_output=True, text=True, cwd=cwd or REPO, env=full_env)
    return p.returncode, p.stdout, p.stderr


@pytest.fixture
def speech(tmp_path):
    """A fake speech model: the stub kokoro_onnx on PYTHONPATH, an empty model folder, a config
    naming it, and a log of the stub's calls. Returns the environment to run with."""
    model = tmp_path / "models" / "kokoro"
    model.mkdir(parents=True)
    (model / "model.onnx").write_bytes(b"")
    (model / "voices.npz").write_bytes(b"")
    conf = tmp_path / "training-video-tools.conf"
    conf.write_text(f"SPEECH_MODEL_DIR={model}\nVOICE=bm_george\nSPEED=1.0\n")
    log = tmp_path / "kokoro-calls.jsonl"
    return {"PYTHONPATH": STUBS, "TRAINING_VIDEO_TOOLS_CONF": str(conf), "KOKORO_STUB_LOG": str(log),
            "SPEECH_MODEL_DIR_FOR_TESTS": str(model)}


def stub_calls(env):
    """The stub speech model's recorded calls, in order."""
    import json
    path = env["KOKORO_STUB_LOG"]
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


@pytest.fixture
def ffstub(tmp_path):
    """Stub ffmpeg and ffprobe first on PATH, logging every call. Returns the environment."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("ffmpeg", "ffprobe"):
        path = bin_dir / name
        path.write_text(f"#!/bin/sh\nFFSTUB_NAME={name} exec '{sys.executable}' '{os.path.join(STUBS, 'ffstub.py')}' \"$@\"\n")
        path.chmod(0o755)
    return {"PATH": f"{bin_dir}:{os.environ['PATH']}", "FFSTUB_LOG": str(tmp_path / "ff-calls.jsonl")}


def ff_calls(env):
    """The stub's recorded calls: [{'ffmpeg': [...]} or {'ffprobe': [...]}] in order."""
    import json
    path = env["FFSTUB_LOG"]
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]



@pytest.fixture
def gitstub(tmp_path):
    """A stub git first on PATH (tests/stubs/gitstub.py), logging every call. Returns the environment;
    set GITSTUB_HEADS, GITSTUB_DIRTY or GITSTUB_FAIL in it to choose its answers."""
    bin_dir = tmp_path / "gitbin"
    bin_dir.mkdir()
    path = bin_dir / "git"
    path.write_text(f"#!/bin/sh\nexec '{sys.executable}' '{os.path.join(STUBS, 'gitstub.py')}' \"$@\"\n")
    path.chmod(0o755)
    return {"PATH": f"{bin_dir}:{os.environ['PATH']}", "GITSTUB_LOG": str(tmp_path / "git-calls.jsonl")}


def git_calls(env):
    """The stub git's recorded argument lists, in order."""
    import json
    path = env["GITSTUB_LOG"]
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line)["args"] for line in f]

def fake_media(path, **fields):
    """A fake media file the stub understands: key=value lines."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in fields.items():
            f.write(f"{k}={v}\n")
    return path


@pytest.fixture
def example(tmp_path):
    """A copy of examples/ in a temporary folder; returns the copied video's script path."""
    shutil.copytree(EXAMPLES, tmp_path / "examples")
    return str(tmp_path / "examples" / "videos" / "paper-boat" / "script.md")


def cropped(example):
    """The example copy with its insets cut (crop-insets run through the clean environment)."""
    code, out, err = run("crop-insets", example)
    assert code == 0, err
    return example


# The example's scenes with every clip 1.0 s long: cue lengths are the minimums, so the scene
# lengths are lead + minimums + tail (+ extra), rounded to frames at 30 fps.
EXAMPLE_FRAMES = {"title": 249, "A": 261, "B": 237, "B2": 159, "C": 267, "R": 243, "end": 171}
EXAMPLE_CUES = {"title": 2, "A": 2, "B": 2, "B2": 1, "C": 2, "R": 2, "end": 0}


def narrated(example, rate=24000, seconds=1.0):
    """Write real 1 s clips (a quiet tone) and a timing.json for every cue of the example copy."""
    import json

    import numpy as np
    import soundfile
    folder = os.path.join(os.path.dirname(example), "work", "narration")
    os.makedirs(folder, exist_ok=True)
    scenes = {}
    for key, n in EXAMPLE_CUES.items():
        scenes[key] = []
        for i in range(1, n + 1):
            tone = (np.cos(np.arange(int(rate * seconds)) * 0.1) * 0.25).astype(np.float32)   # loud from sample 0
            soundfile.write(os.path.join(folder, f"{key}_{i:02d}.wav"), tone, rate)
            scenes[key].append(seconds)
    with open(os.path.join(folder, "timing.json"), "w", encoding="utf-8") as f:
        json.dump({"voice": "af_heart", "speed": 0.98, "model": "kokoro-82m", "sample_rate": rate,
                   "scenes": scenes}, f)
    return folder


def rendered(example):
    """Fake segments (one per scene, from frame 0) with the frame counts the timing gives."""
    folder = os.path.join(os.path.dirname(example), "work", "segments")
    for key, frames in EXAMPLE_FRAMES.items():
        fake_media(os.path.join(folder, f"{key}_00000.mp4"), frames=frames, duration=f"{frames / 30:.6f}")
    return folder
