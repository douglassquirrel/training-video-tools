"""The commands that draw, and check-script, take --elements and --renderer (PLAN.md item 15)."""

import pytest

from tests.tier2.conftest import run

COMMANDS = ("check-script", "stills", "render", "frame-hashes", "compare-frames")


@pytest.mark.parametrize("command", COMMANDS)
def test_help_names_the_elements_folder_and_the_renderer_flags(command):
    code, out, err = run(command, "--help")
    assert code == 0
    assert "--elements DIR" in out and "--renderer PATH" in out
    assert "VIDEO_ELEMENTS_DIR" in " ".join(out.split()) and "RSVG_CONVERT" in " ".join(out.split())
