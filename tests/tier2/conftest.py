"""Tier 2: whole commands, called in the test's own process by run() (a few started as programs by
run_program()), against stubs and copies of the example."""

import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLES = os.path.join(REPO, "examples")
STUBS = os.path.join(REPO, "tests", "stubs")
STUB = os.path.join(STUBS, "stub.sh")      # the one stand-in launcher, linked in under each program's name


# Settings the user's shell may export (the README tells device-shell users to export
# TRAINING_VIDEO_TOOLS_PYTHON, and before the rename VIDEO_TOOLS_PYTHON) that would change what a
# command under test does: a test sets them on purpose or not at all. FONTCONFIG_FILE: set in-process
# by fonts.load on Linux; a child must set its own.
USER_SETTINGS = ("TRAINING_VIDEO_TOOLS_PYTHON", "TRAINING_VIDEO_TOOLS_CONF", "VIDEO_TOOLS_PYTHON", "VIDEO_TOOLS_CONF",
                 "FONTCONFIG_FILE")


@pytest.fixture(autouse=True, scope="session")
def _stand_in_unchanged():
    """At the end of the run, check that no test wrote over the shared stand-in launcher."""
    with open(STUB, "rb") as f:
        before = f.read()
    yield
    with open(STUB, "rb") as f:
        assert f.read() == before, f"a test wrote over {STUB}: restore it with git checkout"
    assert os.access(STUB, os.X_OK), f"{STUB} is no longer executable"


def clean_env(**overrides):
    """A copy of the environment without the user's own training-video-tools settings, plus `overrides`."""
    env = {k: v for k, v in os.environ.items() if k not in USER_SETTINGS}
    env.update(overrides)
    return env


def command_env(env=None, program=False):
    """The environment a command runs with: the clean one, the stand-ins' settings, then `env` (None in it
    unsets a variable). A program also gets coverage's hook (pyproject.toml: parallel = true)."""
    full_env = clean_env()
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if program:
        full_env.setdefault("COVERAGE_PROCESS_START", os.path.join(REPO, "pyproject.toml"))
    full_env.update(TVT_STUBS=STUBS, TVT_STUB_PYTHON=sys.executable)    # what tests/stubs/stub.sh runs
    full_env.update(env or {})
    return {k: v for k, v in full_env.items() if v is not None}


def run_program(command, *args, cwd=None, env=None):
    """Start a top-level command script as a program, with the venv's Python, as a user runs it; (exit code,
    stdout, stderr). For the few tests of each command that prove the file runs; most use run()."""
    p = subprocess.run([sys.executable, os.path.join(REPO, command)] + [str(a) for a in args],
                       capture_output=True, text=True, cwd=cwd or REPO, env=command_env(env, program=True))
    return p.returncode, p.stdout, p.stderr


def catch_output(call):
    """Call `call()` with stdout and stderr caught at the file level, so that what child programs (the
    stand-ins) print is caught with what Python prints, in order; (stdout, stderr) as text."""
    import io
    import tempfile
    sys.stdout.flush()
    sys.stderr.flush()
    streams, fds = (sys.stdout, sys.stderr), (os.dup(1), os.dup(2))
    files = (tempfile.TemporaryFile(), tempfile.TemporaryFile())
    try:
        os.dup2(files[0].fileno(), 1)
        os.dup2(files[1].fileno(), 2)
        sys.stdout, sys.stderr = (io.TextIOWrapper(io.FileIO(fd, "w", closefd=False), encoding="utf-8",
                                                   write_through=True) for fd in (1, 2))
        call()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = streams
        for fd, saved in zip((1, 2), fds):
            os.dup2(saved, fd)
            os.close(saved)
    texts = []
    for f in files:
        f.seek(0)
        with io.TextIOWrapper(f, encoding="utf-8", newline=None) as text:   # as text=True reads a program's
            texts.append(text.read())
    return tuple(texts)


def _exit_code(value):
    """The exit code sys.exit(value) gives a program: None 0, a number itself, anything else printed, 1."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    sys.stderr.write(f"{value}\n")
    return 1


def _set_aside(folders):
    """Take out of sys.modules every module a folder on PYTHONPATH would shadow (the stand-in speech model
    over the installed one); returns them, to put back after the call."""
    names = set()
    for folder in folders:
        if os.path.isdir(folder):
            names.update(n[:-3] if n.endswith(".py") else n for n in os.listdir(folder))
    aside = {m: mod for m, mod in sys.modules.items() if m.split(".")[0] in names}
    for m in aside:
        del sys.modules[m]
    return aside


def _forget_new(before):
    """Drop the modules a call imported from outside this Python and the commands' package (a stand-in, a
    video-elements library, a scene module), so the next call imports them afresh, as a new program would."""
    kept = [os.path.realpath(p) + os.sep for p in (sys.prefix, sys.base_prefix, os.path.join(REPO, "videotools"))]
    for name in set(sys.modules) - before:
        path = getattr(sys.modules[name], "__file__", None)
        if path and not any(os.path.realpath(path).startswith(k) for k in kept):
            del sys.modules[name]


def run(command, *args, cwd=None, env=None):
    """Call a command's main inside this process, as its program would run (bernstein's rule, Settled 66):
    argv, the environment run_program would give it, the working folder, PYTHONPATH's folders first on the
    import path, stdout and stderr caught at the file level; all put back after. An uncaught exception is a
    traceback on stderr and exit 1, as a program's. (exit code, stdout, stderr)."""
    import importlib
    import traceback
    full_env = command_env(env)
    argv = [str(a) for a in args]
    module = importlib.import_module("videotools." + command.replace("-", "_"))
    saved = dict(os.environ), os.getcwd(), list(sys.argv), list(sys.path), sys.dont_write_bytecode
    extra = [p for p in full_env.get("PYTHONPATH", "").split(os.pathsep) if p]
    code = []

    def call():
        try:
            code.append(_exit_code(module.main(argv)))
        except SystemExit as e:
            code.append(_exit_code(e.code))
        except Exception:
            traceback.print_exc()
            code.append(1)

    aside = _set_aside(extra)
    before = set(sys.modules)
    try:
        os.environ.clear()
        os.environ.update(full_env)
        os.chdir(cwd or REPO)
        sys.argv = [os.path.join(REPO, command)] + argv
        sys.path[:0] = extra
        sys.dont_write_bytecode = True
        out, err = catch_output(call)
    finally:
        os.environ.clear()
        os.environ.update(saved[0])
        os.chdir(saved[1])
        sys.argv, sys.path[:], sys.dont_write_bytecode = saved[2], saved[3], saved[4]
        _forget_new(before)
        sys.modules.update(aside)
    return code[0], out, err


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
        os.symlink(STUB, bin_dir / name)
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
    os.symlink(STUB, bin_dir / "git")
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


_PRISTINE = {}       # "video": the pristine example's video folder, cropped once a run (cropped())


@pytest.fixture(autouse=True, scope="session")
def _pristine_folder(tmp_path_factory):
    """Where cropped() keeps its one cropped copy of the example, under pytest's own temporary folders."""
    _PRISTINE["base"] = tmp_path_factory.mktemp("pristine-cropped")
    yield
    _PRISTINE.clear()


def _same_tree(a, b):
    """True when folders a and b hold the same files with the same bytes, leaving out work/."""
    import filecmp
    names_a = sorted(n for n in os.listdir(a) if n != "work")
    names_b = sorted(n for n in os.listdir(b) if n != "work")
    if names_a != names_b:
        return False
    for name in names_a:
        pa, pb = os.path.join(a, name), os.path.join(b, name)
        if os.path.isdir(pa) != os.path.isdir(pb):
            return False
        if os.path.isdir(pa):
            if not _same_tree(pa, pb):
                return False
        elif not filecmp.cmp(pa, pb, shallow=False):
            return False
    return True


def cropped(example):
    """The example copy with its insets cut (crop-insets run through the clean environment). crop-insets runs
    once a test run, on a pristine copy, and its work/insets/ is copied into each example after that;
    an example that differs from the pristine one, or has a work/ already, is cropped for real."""
    video = os.path.dirname(example)
    if "video" not in _PRISTINE:
        pristine = os.path.join(str(_PRISTINE["base"]), "examples")
        shutil.copytree(EXAMPLES, pristine)
        script = os.path.join(pristine, "videos", "paper-boat", "script.md")
        code, out, err = run("crop-insets", script)
        assert code == 0, err
        _PRISTINE["video"] = os.path.dirname(script)
    if os.path.exists(os.path.join(video, "work")) or not _same_tree(video, _PRISTINE["video"]):
        code, out, err = run("crop-insets", example)
        assert code == 0, err
        return example
    shutil.copytree(os.path.join(_PRISTINE["video"], "work"), os.path.join(video, "work"))
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
