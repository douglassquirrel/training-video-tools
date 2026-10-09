"""frame-hashes: the MD5 of every frame a scene draws, written to a file or compared with one."""

import json
import os
import re

import pytest

from tests.tier2.conftest import cropped, narrated, run

HEX32 = re.compile(r"^[0-9a-f]{32}$")


@pytest.fixture
def prepared(example):
    cropped(example)
    narrated(example)
    return example


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def change_water(script_path):
    """The example copy's `water` colour changed: only scene R draws it."""
    with open(script_path, encoding="utf-8") as f:
        text = f.read()
    assert "| water | #BFD9E6 |" in text
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(text.replace("| water | #BFD9E6 |", "| water | #FF0000 |"))


def test_help_and_usage():
    code, out, err = run("frame-hashes", "--help")
    assert code == 0 and " ".join(out.split()).startswith(
        "usage: frame-hashes [-h] (--out HASHES.json | --compare HASHES.json) [--merge] [--scenes KEY,...] [--step N] SCRIPT")
    code, out, err = run("frame-hashes")
    assert code == 2 and "usage: frame-hashes" in err
    code, out, err = run("frame-hashes", "x.md")
    assert code == 2 and "one of the arguments --out --compare is required" in err


def test_out_writes_the_md5_of_every_frame_by_scene_and_frame_number_and_the_same_twice(prepared, tmp_path):
    first, second = str(tmp_path / "one.json"), str(tmp_path / "two.json")
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--out", first)
    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert re.match(r"^B2 +159 frames in +\d+\.\d s$", lines[0]), lines[0]
    assert lines[1] == f"Wrote {first}: 159 frames, 1 scene"
    hashes = load(first)
    assert list(hashes) == ["B2"] and len(hashes["B2"]) == 159
    assert list(hashes["B2"])[:3] == ["0", "1", "2"] and list(hashes["B2"])[-1] == "158"
    assert all(HEX32.match(h) for h in hashes["B2"].values())
    assert hashes["B2"]["0"] != hashes["B2"]["100"]
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--out", second)
    assert code == 0 and load(second) == hashes


def test_step_hashes_every_nth_frame_from_0_and_scenes_limits_which(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    code, out, err = run("frame-hashes", prepared, "--scenes", "R,B2", "--step", "50", "--out", path)
    assert (code, err) == (0, "")
    hashes = load(path)
    assert list(hashes) == ["R", "B2"]
    assert list(hashes["R"]) == ["0", "50", "100", "150", "200"] and list(hashes["B2"]) == ["0", "50", "100", "150"]
    assert out.splitlines()[-1] == f"Wrote {path}: 9 frames, 2 scenes"


def test_out_refuses_an_existing_file_unless_merge_which_keeps_the_other_scenes(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    assert run("frame-hashes", prepared, "--scenes", "B2", "--step", "50", "--out", path)[0] == 0
    before = load(path)
    code, out, err = run("frame-hashes", prepared, "--scenes", "R", "--step", "50", "--out", path)
    assert (code, out) == (3, "")
    assert err == f"frame-hashes: {path} already exists; give a new name, or --merge to add scenes to it\n"
    assert load(path) == before
    code, out, err = run("frame-hashes", prepared, "--scenes", "R", "--step", "50", "--out", path, "--merge")
    assert (code, err) == (0, "")
    assert out.splitlines()[-1] == f"Wrote {path}: 9 frames, 2 scenes"
    merged = load(path)
    assert merged["B2"] == before["B2"] and list(merged["R"]) == ["0", "50", "100", "150", "200"]
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--step", "100", "--out", path, "--merge")
    assert code == 0 and list(load(path)["B2"]) == ["0", "100"] and load(path)["R"] == merged["R"]


def test_compare_says_all_match_and_exits_0_when_nothing_changed(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    assert run("frame-hashes", prepared, "--scenes", "B2", "--step", "50", "--out", path)[0] == 0
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--step", "50", "--compare", path)
    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert re.match(r"^B2 +4 frames in +\d+\.\d s: all match$", lines[0]), lines[0]
    assert lines[1] == "All frames match."


def test_compare_lists_the_frames_that_differ_per_scene_and_exits_1(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    assert run("frame-hashes", prepared, "--scenes", "R,B2", "--step", "50", "--out", path)[0] == 0
    change_water(prepared)
    code, out, err = run("frame-hashes", prepared, "--scenes", "R,B2", "--step", "50", "--compare", path)
    assert (code, err) == (1, "")
    lines = out.splitlines()
    assert re.match(r"^R +5 frames in +\d+\.\d s: 4 differ \(frames 50, 100, 150, 200\)$", lines[0]), lines[0]
    assert re.match(r"^B2 +4 frames in +\d+\.\d s: all match$", lines[1]), lines[1]
    assert lines[2] == "4 frames differ."


def test_compare_counts_frames_the_reference_does_not_have_as_differing(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    assert run("frame-hashes", prepared, "--scenes", "B2", "--step", "50", "--out", path)[0] == 0
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--step", "25", "--compare", path)
    assert (code, err) == (1, "")
    line = out.splitlines()[0]
    assert re.match(r"^B2 +7 frames in +\d+\.\d s: 3 differ \(frames 25, 75, 125\), 3 not in the reference$", line), line
    assert out.splitlines()[1] == "3 frames differ."


def test_compare_shows_the_first_twelve_differing_frames_then_an_ellipsis(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    assert run("frame-hashes", prepared, "--scenes", "R", "--step", "10", "--out", path)[0] == 0
    change_water(prepared)
    code, out, err = run("frame-hashes", prepared, "--scenes", "R", "--step", "10", "--compare", path)
    assert code == 1
    line = out.splitlines()[0]
    assert line.endswith(": 24 differ (frames 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, …)"), line


def test_compare_with_a_missing_reference_file_is_refused_exit_3(prepared, tmp_path):
    code, out, err = run("frame-hashes", prepared, "--scenes", "B2", "--compare", str(tmp_path / "none.json"))
    assert (code, out) == (3, "")
    assert err == f"frame-hashes: no such file: {tmp_path / 'none.json'}\n"


def test_missing_timings_are_refused_as_render_refuses_them_and_nothing_is_written(prepared, tmp_path):
    os.remove(os.path.join(os.path.dirname(prepared), "work", "narration", "timing.json"))
    path = str(tmp_path / "h.json")
    code, out, err = run("frame-hashes", prepared, "--scenes", "A", "--out", path)
    assert (code, out) == (3, "")
    assert err == "frame-hashes: scene A has no narration clips; run narrate first\n"
    assert not os.path.exists(path)


def test_an_unknown_scene_is_a_usage_error(prepared, tmp_path):
    code, out, err = run("frame-hashes", prepared, "--scenes", "Z", "--out", str(tmp_path / "h.json"))
    assert code == 2 and "no scene 'Z'" in err


def test_a_bad_step_is_a_usage_error(prepared, tmp_path):
    code, out, err = run("frame-hashes", prepared, "--step", "0", "--out", str(tmp_path / "h.json"))
    assert code == 2 and "--step must be 1 or more" in err


def test_the_script_and_the_reference_are_never_modified(prepared, tmp_path):
    path = str(tmp_path / "h.json")
    before_script = open(prepared, encoding="utf-8").read()
    assert run("frame-hashes", prepared, "--scenes", "B2", "--step", "50", "--out", path)[0] == 0
    before_ref = open(path, encoding="utf-8").read()
    assert run("frame-hashes", prepared, "--scenes", "B2", "--step", "25", "--compare", path)[0] == 1
    assert open(prepared, encoding="utf-8").read() == before_script
    assert open(path, encoding="utf-8").read() == before_ref
    assert sorted(os.listdir(tmp_path)) == ["examples", "h.json"]
