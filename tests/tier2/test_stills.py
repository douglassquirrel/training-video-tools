"""stills: frames at given times on one labelled sheet; estimates with a warning; refusals."""

import os
import subprocess
import sys

import pytest
from PIL import Image

from tests.tier2.conftest import REPO, narrated, run


@pytest.fixture
def prepared(example):
    subprocess.run([sys.executable, os.path.join(REPO, "crop-insets"), example], check=True, capture_output=True)
    return example


def test_help_and_usage():
    code, out, err = run("stills", "--help")
    assert code == 0 and out.startswith("usage: stills [-h] --out SHEET.png [--grid CxR] SCRIPT FRAMES")
    code, out, err = run("stills", "x.md")
    assert code == 2 and "usage: stills" in err


def test_four_frames_make_a_2x2_sheet_each_labelled(prepared, tmp_path):
    narrated(prepared)
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "A:1.5,A:5.0,B:3.5,end:1.5", "--out", sheet)
    assert (code, err) == (0, "")
    im = Image.open(sheet)
    assert im.size == (1920, 1080)
    assert im.getpixel((600 + 960, 20))[:3] == (0xF7, 0xF3, 0xEA)       # frame 2's background, top right
    assert im.getpixel((100, 540 + 530))[:3] == (0x2B, 0x2B, 0x2B)       # frame 3's caption band, bottom left
    assert im.getpixel((100 + 960, 540 + 530))[:3] == (0xF7, 0xF3, 0xEA)  # the end card has no band
    assert out.splitlines() == ["A at 1.500 s (of 8.700 s, cue 1)", "A at 5.000 s (of 8.700 s, cue 2)",
                                "B at 3.500 s (of 7.900 s, cue 2)", "end at 1.500 s (of 5.700 s, no cue)",
                                f"Wrote {sheet}: 4 frames, 2x2"]


def test_a_negative_time_counts_back_from_the_scenes_end_and_grids_can_differ(prepared, tmp_path):
    narrated(prepared)
    sheet = tmp_path / "one.png"
    code, out, err = run("stills", prepared, "A:-1.0", "--out", sheet, "--grid", "1x1")
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == "A at 7.700 s (of 8.700 s, cue 2)"
    assert Image.open(sheet).size == (1920, 1080)
    assert Image.open(sheet).getpixel((100, 1060))[:3] == (0x2B, 0x2B, 0x2B)   # full size: the band is at the bottom
    code, out, err = run("stills", prepared, "A:1,B:1,C:1,R:1,B2:1,title:1", "--out", tmp_path / "six.png", "--grid", "3x2")
    assert code == 0 and out.splitlines()[-1].endswith("6 frames, 3x2")


def test_without_narration_the_timings_are_estimated_with_a_warning(prepared, tmp_path):
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "A:1.5", "--out", sheet)
    assert code == 0
    assert err == "stills: scene A has no narration clips (cues 1, 2); times are estimated at 2.6 words a second\n"
    assert os.path.exists(sheet)


def test_a_time_past_the_scenes_end_an_unknown_scene_and_too_many_frames_are_refused(prepared, tmp_path):
    narrated(prepared)
    code, out, err = run("stills", prepared, "A:9.0", "--out", tmp_path / "s.png")
    assert (code, out) == (2, "") and err == "stills: A:9.0 is past the end of scene A (8.700 s)\n"
    code, out, err = run("stills", prepared, "Z:1.0", "--out", tmp_path / "s.png")
    assert code == 2 and err == "stills: no scene 'Z' in the script (scenes: title, A, B, B2, C, R, end)\n"
    code, out, err = run("stills", prepared, "A:1,A:2,A:3,A:4,A:5", "--out", tmp_path / "s.png")
    assert code == 2 and err == "stills: 5 frames do not fit a 2x2 grid; give a bigger --grid\n"
    code, out, err = run("stills", prepared, "A:one", "--out", tmp_path / "s.png")
    assert code == 2 and err == "stills: 'A:one' is not SCENE:SECONDS\n"
    assert not os.path.exists(tmp_path / "s.png")


def test_an_existing_sheet_is_refused_before_anything_is_drawn(prepared, tmp_path):
    sheet = tmp_path / "sheet.png"
    sheet.write_text("keep")
    code, out, err = run("stills", prepared, "A:1.5", "--out", sheet)
    assert (code, out) == (3, "") and err == f"stills: {sheet} already exists; give a new name\n"
    assert sheet.read_text() == "keep"


def test_missing_insets_are_a_useful_error(example, tmp_path):
    code, out, err = run("stills", example, "A:1.5", "--out", tmp_path / "s.png")
    assert (code, out) == (3, "")
    assert err == f"stills: no {os.path.join(os.path.dirname(example), 'work', 'insets', 'A.png')} (inset 'A'); run crop-insets first\n"
