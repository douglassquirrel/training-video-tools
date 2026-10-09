"""The command wrappers run under the repository's .venv when it exists, whatever python3 ran them."""

import os
import shutil
import subprocess
import sys

from tests.tier2.conftest import REPO

COMMANDS = ["check-script", "narrate"]


def copy_with_fake_venv(tmp_path):
    """A copy of the wrappers and the package beside a fake .venv whose python records that it
    was used, then runs the real one."""
    for name in COMMANDS:
        shutil.copy(os.path.join(REPO, name), tmp_path / name)
    shutil.copytree(os.path.join(REPO, "videotools"), tmp_path / "videotools")
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    fake = tmp_path / ".venv" / "bin" / "python"
    # The shim marks itself as the venv (a real venv is known by sys.prefix instead).
    fake.write_text("#!/bin/sh\necho used-the-venv >> '%s'\nVIDEO_TOOLS_VENV='%s' exec '%s' \"$@\"\n"
                    % (tmp_path / "venv.log", fake, sys.executable))
    fake.chmod(0o755)
    return tmp_path


def test_a_wrapper_run_by_another_python_re_runs_itself_under_the_venv(tmp_path):
    folder = copy_with_fake_venv(tmp_path)
    p = subprocess.run([sys.executable, str(folder / "check-script"), "--help"], capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout.startswith("usage: check-script")
    assert (folder / "venv.log").read_text() == "used-the-venv\n"


def test_a_wrapper_already_under_the_venv_does_not_re_run(tmp_path):
    folder = copy_with_fake_venv(tmp_path)
    p = subprocess.run([str(folder / ".venv" / "bin" / "python"), str(folder / "narrate"), "--help"],
                       capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout.startswith("usage: narrate")
    assert (folder / "venv.log").read_text() == "used-the-venv\n"


def test_without_a_venv_the_wrapper_runs_as_it_is(tmp_path):
    folder = copy_with_fake_venv(tmp_path)
    shutil.rmtree(folder / ".venv")
    p = subprocess.run([sys.executable, str(folder / "check-script"), "--help"], capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout.startswith("usage: check-script")
