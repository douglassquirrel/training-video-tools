"""compare-frames: the frame drawn now beside an old video's frame at the same moment; the stub
serves the old video's frames as one colour."""

import os
import re

import pytest
from PIL import Image

from tests.tier2.conftest import cropped, fake_media, ff_calls, narrated, run

# The example with every clip 1 s: title 8.3 s, A 8.7, B 7.9, B2 5.3, C 8.9, R 8.1, end 5.7 (52.9 s).
A_START, B2_START, B2_TOTAL = 8.3, 24.9, 5.3


@pytest.fixture
def prepared(example, ffstub):
    cropped(example)
    narrated(example)
    return example


def old_video(tmp_path, **fields):
    defaults = {"frames": 1587, "duration": "52.900000", "colours": "0:200.40.40"}
    defaults.update(fields)
    return fake_media(str(tmp_path / "old.mp4"), **defaults)


def test_help_and_usage():
    code, out, err = run("compare-frames", "--help")
    assert code == 0 and " ".join(out.split()).startswith("usage: compare-frames [-h] --out SHEET.png [--offset SCENE=SECONDS] SCRIPT OLD FRAMES")
    code, out, err = run("compare-frames")
    assert code == 2 and "usage: compare-frames" in err


def test_each_pair_is_drawn_now_and_read_from_the_old_video_at_the_scenes_start_plus_the_time(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path), str(tmp_path / "sheet.png")
    code, out, err = run("compare-frames", prepared, old, "A:1.5,B2:-1", "--out", sheet, env=ffstub)
    assert (code, err) == (0, "")
    lines = out.splitlines()
    assert re.match(r"^A +1\.50 s  old +9\.80 s  mean difference +\d+\.\d$", lines[0]), lines[0]
    assert re.match(r"^B2 +4\.30 s  old +29\.20 s  mean difference +\d+\.\d$", lines[1]), lines[1]
    assert lines[2] == f"Wrote {sheet}: 2 pairs"
    frames = [c["ffmpeg"] for c in ff_calls(ffstub) if "ffmpeg" in c and "-frames:v" in c["ffmpeg"]]
    assert frames == [["-hide_banner", "-loglevel", "error", "-nostdin", "-ss", t, "-i", old, "-frames:v", "1",
                       "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-"] for t in ("9.800", "29.200")]
    im = Image.open(sheet).convert("RGB")
    assert im.size == (1920, 2 * 570)                    # two 949x533 frames a row, a 36 px strip under each
    assert im.getpixel((16, 10)) == (0xF7, 0xF3, 0xEA)   # the new frame's background, top left
    assert im.getpixel((1100, 100)) == (200, 40, 40)     # the old video's frame, right
    assert im.getpixel((600, 533 + 18)) == (0x55, 0x55, 0x55)   # the strip under the new frame, past its label
    assert im.getpixel((1100, 570 + 100)) == (200, 40, 40)      # the second row's old frame


def test_the_difference_is_the_mean_absolute_rgb_difference_so_a_nearer_colour_gives_a_smaller_number(prepared, tmp_path, ffstub):
    far = old_video(tmp_path, colours="0:0.0.0")
    near = fake_media(str(tmp_path / "near.mp4"), frames=1587, duration="52.900000", colours="0:240.236.226")
    code, out_far, err = run("compare-frames", prepared, far, "A:1.5", "--out", str(tmp_path / "f.png"), env=ffstub)
    assert code == 0, err
    code, out_near, err = run("compare-frames", prepared, near, "A:1.5", "--out", str(tmp_path / "n.png"), env=ffstub)
    assert code == 0, err
    diff = lambda out: float(out.splitlines()[0].rsplit(" ", 1)[1])   # noqa: E731
    assert diff(out_far) > 100 > diff(out_near) > 0   # black against the frame; a near-background colour against it


def test_offset_moves_one_scenes_start_in_the_old_video(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path), str(tmp_path / "sheet.png")
    code, out, err = run("compare-frames", prepared, old, "A:1.5,B2:0", "--out", sheet, "--offset", "B2=1.5",
                         "--offset", "A=-0.3", env=ffstub)
    assert (code, err) == (0, "")
    assert [c["ffmpeg"][5] for c in ff_calls(ffstub) if "ffmpeg" in c and "-frames:v" in c["ffmpeg"]] == ["9.500", "26.400"]
    assert out.splitlines()[1].startswith("B2          0.00 s  old   26.40 s  mean difference ")


def test_a_bad_offset_is_a_usage_error(prepared, tmp_path, ffstub):
    old = old_video(tmp_path)
    code, out, err = run("compare-frames", prepared, old, "A:1.5", "--out", str(tmp_path / "s.png"), "--offset", "A", env=ffstub)
    assert code == 2 and "--offset should be SCENE=SECONDS, not 'A'" in err
    code, out, err = run("compare-frames", prepared, old, "A:1.5", "--out", str(tmp_path / "s.png"), "--offset", "Z=1", env=ffstub)
    assert code == 2 and "no scene 'Z'" in err


def test_a_time_past_the_scenes_end_is_refused_as_stills_refuses_it(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path), str(tmp_path / "sheet.png")
    code, out, err = run("compare-frames", prepared, old, "B2:9", "--out", sheet, env=ffstub)
    assert (code, out) == (2, "")
    assert err == "compare-frames: B2:9 is past the end of scene B2 (5.300 s)\n"
    assert not os.path.exists(sheet)


def test_a_moment_past_the_old_videos_end_is_refused_by_name_before_any_frame_is_read(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path, duration="20.000000", frames=600), str(tmp_path / "sheet.png")
    code, out, err = run("compare-frames", prepared, old, "A:1.5,B2:-1", "--out", sheet, env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"compare-frames: {old} is 20.000 s long; scene B2 at 4.300 s would be at 29.200 s in it\n"
    assert not os.path.exists(sheet)
    assert not any("-frames:v" in c.get("ffmpeg", []) for c in ff_calls(ffstub))


def test_an_existing_sheet_and_a_missing_old_video_are_refused(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path), tmp_path / "sheet.png"
    sheet.write_bytes(b"keep")
    code, out, err = run("compare-frames", prepared, old, "A:1.5", "--out", str(sheet), env=ffstub)
    assert (code, out) == (3, "") and err == f"compare-frames: {sheet} already exists; give a new name\n"
    assert sheet.read_bytes() == b"keep" and ff_calls(ffstub) == []
    code, out, err = run("compare-frames", prepared, str(tmp_path / "none.mp4"), "A:1.5", "--out", str(tmp_path / "s.png"), env=ffstub)
    assert (code, out) == (3, "") and err == f"compare-frames: no such file: {tmp_path / 'none.mp4'}\n"


def test_missing_timings_are_refused_as_render_refuses_them(prepared, tmp_path, ffstub):
    os.remove(os.path.join(os.path.dirname(prepared), "work", "narration", "timing.json"))
    code, out, err = run("compare-frames", prepared, old_video(tmp_path), "A:1.5", "--out", str(tmp_path / "s.png"), env=ffstub)
    assert (code, out) == (3, "")
    assert err == "compare-frames: scene title has no narration clips; run narrate first\n"


def test_a_bad_frame_spec_is_a_usage_error(prepared, tmp_path, ffstub):
    code, out, err = run("compare-frames", prepared, old_video(tmp_path), "A", "--out", str(tmp_path / "s.png"), env=ffstub)
    assert code == 2 and err == "compare-frames: 'A' is not SCENE:SECONDS\n"


def test_only_the_sheet_is_written_and_the_inputs_are_never_modified(prepared, tmp_path, ffstub):
    old, sheet = old_video(tmp_path), str(tmp_path / "sheet.png")
    before = open(prepared, encoding="utf-8").read(), open(old, "rb").read()
    assert run("compare-frames", prepared, old, "A:1.5", "--out", sheet, env=ffstub)[0] == 0
    assert (open(prepared, encoding="utf-8").read(), open(old, "rb").read()) == before
    assert sorted(os.listdir(tmp_path)) == ["bin", "examples", "ff-calls.jsonl", "old.mp4", "sheet.png"]
