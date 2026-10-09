"""Tier 2: whole commands run as subprocesses, against stubs and copies of the example."""

import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLES = os.path.join(REPO, "examples")
STUBS = os.path.join(REPO, "tests", "stubs")


def run(command, *args, cwd=None, env=None):
    """Run a top-level command script with the venv's Python; (exit code, stdout, stderr)."""
    full_env = dict(os.environ)
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Let coverage.py measure the subprocess too (pyproject.toml: parallel = true).
    full_env.setdefault("COVERAGE_PROCESS_START", os.path.join(REPO, "pyproject.toml"))
    full_env.update(env or {})
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
    conf = tmp_path / "video-tools.conf"
    conf.write_text("SPEECH_MODEL_DIR=%s\nVOICE=bm_george\nSPEED=1.0\n" % model)
    log = tmp_path / "kokoro-calls.jsonl"
    return {"PYTHONPATH": STUBS, "VIDEO_TOOLS_CONF": str(conf), "KOKORO_STUB_LOG": str(log),
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
def example(tmp_path):
    """A copy of examples/ in a temporary folder; returns the copied video's script path."""
    shutil.copytree(EXAMPLES, tmp_path / "examples")
    return str(tmp_path / "examples" / "videos" / "paper-boat" / "script.md")
