"""Tier 2: whole commands run as subprocesses, against stubs and copies of the example."""

import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLES = os.path.join(REPO, "examples")


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
def example(tmp_path):
    """A copy of examples/ in a temporary folder; returns the copied video's script path."""
    shutil.copytree(EXAMPLES, tmp_path / "examples")
    return str(tmp_path / "examples" / "videos" / "paper-boat" / "script.md")
