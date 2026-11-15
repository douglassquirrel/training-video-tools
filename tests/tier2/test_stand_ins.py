"""The stand-in programs: one file in the repository, tests/stubs/stub.sh, linked into each test's folder
under the program's name and never written by a test."""

import os
import subprocess

from tests.tier2.conftest import STUBS

STUB = os.path.join(STUBS, "stub.sh")


def on_path(env, name):
    return os.path.join(env["PATH"].split(os.pathsep)[0], name)


def test_ffmpeg_and_ffprobe_are_links_to_the_one_stand_in_file(ffstub):
    for name in ("ffmpeg", "ffprobe"):
        path = on_path(ffstub, name)
        assert os.path.islink(path) and os.path.realpath(path) == os.path.realpath(STUB), name


def test_git_is_a_link_to_the_one_stand_in_file(gitstub):
    path = on_path(gitstub, "git")
    assert os.path.islink(path) and os.path.realpath(path) == os.path.realpath(STUB)


def test_a_name_with_no_stand_in_is_refused_in_words(tmp_path):
    link = tmp_path / "nope"
    os.symlink(STUB, link)
    p = subprocess.run([str(link), "--version"], capture_output=True, text=True)
    assert (p.returncode, p.stdout, p.stderr) == (127, "", "stub.sh: no stand-in named nope\n")
