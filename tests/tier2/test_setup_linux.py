"""setup-linux is retired (Settled 67): lobster-tools' prepare-venv prepares the device shell from this
checkout's prepare-venv.conf. Every form stops with the line to run instead, exit 2, and does nothing."""

import os

import pytest

from tests.tier2.conftest import run, run_program

MESSAGE = ("setup-linux: setup-linux is retired; prepare the device shell with lobster-tools' prepare-venv, which "
           "reads this checkout's prepare-venv.conf: eval \"$(python3 ~/mnt/lobster-tools/prepare-venv --project "
           "~/mnt/training-video-tools --venv DIR --model DIR --conf FILE)\" "
           "(README, \"Running from the Linux device shell\")\n")


def test_the_old_form_says_what_to_run_instead_exit_2_as_a_program(tmp_path):
    code, out, err = run_program("setup-linux", "--venv", tmp_path / "venv", "--model", tmp_path / "kokoro",
                                 "--conf", tmp_path / "x.conf")
    assert (code, out, err) == (2, "", MESSAGE)
    assert os.listdir(tmp_path) == []


@pytest.mark.parametrize("args", [[], ["--help"], ["--dry-run"]])
def test_every_other_form_says_the_same(args):
    assert run("setup-linux", *args) == (2, "", MESSAGE)
