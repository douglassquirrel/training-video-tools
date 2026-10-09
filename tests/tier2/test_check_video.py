"""check-video: the finished file against the script; the stub supplies the measurements."""

import os

import pytest
from PIL import Image

from tests.tier2.conftest import EXAMPLE_FRAMES, fake_media, ff_calls, narrated, run

TOTAL = sum(EXAMPLE_FRAMES.values()) / 30          # 52.9 s
END_SCENE_START = TOTAL - EXAMPLE_FRAMES["end"] / 30  # 47.2 s: the silent end card


def video(example):
    return os.path.dirname(example)


def finished(example, **fields):
    defaults = {"frames": sum(EXAMPLE_FRAMES.values()), "duration": f"{TOTAL:.6f}", "max_volume": "-1.0",
                "mean_volume": "-20.0", "silences": f"{END_SCENE_START:.3f}-{TOTAL:.3f}"}
    defaults.update(fields)
    return fake_media(os.path.join(video(example), "out", "Folding a Paper Boat.mp4"), **defaults)


@pytest.fixture
def ready(example, ffstub):
    narrated(example)
    finished(example)
    return example


def test_help_and_usage():
    code, out, err = run("check-video", "--help")
    assert code == 0 and out.startswith("usage: check-video [-h] [--sheet OUT.png] SCRIPT [VIDEO]")
    code, out, err = run("check-video")
    assert code == 2 and "usage: check-video" in err


def test_a_clean_file_passes_with_a_report(ready, ffstub):
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, err) == (0, "")
    assert out == (f"{os.path.join(video(ready), 'out', 'Folding a Paper Boat.mp4')}\n"
                   "length 52.900 s; the script's scenes give 52.900 s: OK\n"
                   "peak -1.0 dBFS, mean -20.0 dBFS: OK\n"
                   "silences of 2 s or more: 1, at 47.200-52.900 (scene end, no cues): OK\n"
                   "narration in every cue's window: OK\n"
                   "No problems found.\n")
    calls = ff_calls(ffstub)
    assert [list(c)[0] for c in calls] == ["ffprobe", "ffmpeg", "ffmpeg"]
    assert "silencedetect=n=-40dB:d=2.0" in calls[2]["ffmpeg"]


def test_a_length_more_than_one_frame_off_is_a_problem(ready, ffstub):
    finished(ready, duration=f"{TOTAL + 2 / 30:.6f}")
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, err) == (1, "")
    assert "length 52.967 s; the script's scenes give 52.900 s: 2.0 frames off, more than one\n" in out
    assert out.endswith("1 problem:\n  - length 52.967 s; the script's scenes give 52.900 s: 2.0 frames off, more than one\n")


def test_a_length_within_one_frame_passes(ready, ffstub):
    finished(ready, duration=f"{TOTAL + 1 / 30:.6f}")
    code, out, err = run("check-video", ready, env=ffstub)
    assert code == 0 and "give 52.900 s: OK" in out


def test_a_peak_at_or_above_0_dbfs_is_a_problem(ready, ffstub):
    finished(ready, max_volume="0.0")
    code, out, err = run("check-video", ready, env=ffstub)
    assert code == 1 and "peak 0.0 dBFS, mean -20.0 dBFS: at or above 0 dBFS, clipping\n" in out


def test_a_silence_covering_a_cues_window_means_it_was_not_heard(ready, ffstub):
    # title cue 1's clip plays from 0.75 s (cue start 0.7 + the 50 ms lead) for 1.0 s; a silence
    # from 0.5 to 3.5 covers all of it: two problems, the overlap and the unheard cue
    finished(ready, silences=f"0.5-3.5,{END_SCENE_START:.3f}-{TOTAL:.3f}")
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, err) == (1, "")
    assert "silences of 2 s or more: 2, at 0.500-3.500 (scene title cue 1, 0.750-1.750), 47.200-52.900 (scene end, no cues): 1 inside a cue\n" in out
    assert "narration in every cue's window: scene title cue 1 (0.750-1.750) is silent\n" in out
    assert out.endswith("2 problems:\n  - silence at 0.500-3.500 overlaps scene title cue 1 (0.750-1.750)\n"
                        "  - no narration heard in scene title cue 1 (0.750-1.750)\n")


def test_a_silence_overlapping_part_of_a_cue_is_one_problem(ready, ffstub):
    finished(ready, silences=f"1.0-3.5,{END_SCENE_START:.3f}-{TOTAL:.3f}")
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, err) == (1, "")
    assert "narration in every cue's window: OK\n" in out
    assert out.endswith("1 problem:\n  - silence at 1.000-3.500 overlaps scene title cue 1 (0.750-1.750)\n")


def test_a_silence_between_cues_or_scenes_is_fine(ready, ffstub):
    # title cue 1's clip ends at 1.75 s and cue 2's starts at 3.75 s: a silence 1.700-3.700
    # overlaps each by 50 ms, within the 0.1 s the boundaries are trusted to
    finished(ready, silences=f"1.700-3.700,{END_SCENE_START:.3f}-{TOTAL:.3f}")
    code, out, err = run("check-video", ready, env=ffstub)
    assert code == 0 and "silences of 2 s or more: 2, at 1.700-3.700 (between cues), 47.200-52.900 (scene end, no cues): OK" in out


def test_the_video_argument_names_another_file(ready, ffstub, tmp_path):
    other = fake_media(str(tmp_path / "other.mp4"), frames=10, duration="0.333333", max_volume="-3.0", mean_volume="-20.0")
    code, out, err = run("check-video", ready, other, env=ffstub)
    assert code == 1 and out.startswith(f"{other}\nlength 0.333 s; the script's scenes give 52.900 s: 1577.0 frames off")


def test_a_missing_video_or_timing_is_refused(ready, ffstub):
    os.remove(os.path.join(video(ready), "out", "Folding a Paper Boat.mp4"))
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"check-video: no such file: {os.path.join(video(ready), 'out', 'Folding a Paper Boat.mp4')}\n"
    finished(ready)
    os.remove(os.path.join(video(ready), "work", "narration", "timing.json"))
    code, out, err = run("check-video", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"check-video: no {os.path.join(video(ready), 'work', 'narration', 'timing.json')}; run narrate first\n"


def test_sheet_pastes_one_frame_from_the_middle_of_each_scene(ready, ffstub, tmp_path):
    sheet = tmp_path / "sheet.png"
    code, out, err = run("check-video", ready, "--sheet", sheet, env=ffstub)
    assert (code, err) == (0, "")
    assert f"sheet of 7 frames written to {sheet}\n" in out
    im = Image.open(sheet)
    assert im.size == (1920, 1080)
    # 7 frames in a 3 x 3 grid of 640 x 360 cells, each frame filling its cell; stub frames are red
    assert im.getpixel((320, 300))[:3] == (200, 40, 40)
    assert im.getpixel((320 + 640 * 2, 300))[:3] == (200, 40, 40)
    assert im.getpixel((320, 360 * 2 + 300))[:3] == (200, 40, 40)             # the seventh, bottom left
    assert im.getpixel((320 + 640, 360 * 2 + 300))[:3] != (200, 40, 40)       # the empty eighth cell
    frames = [c["ffmpeg"] for c in ff_calls(ffstub) if "ffmpeg" in c and "-frames:v" in c["ffmpeg"]]
    assert len(frames) == 7
    assert frames[0][:5] == ["-hide_banner", "-loglevel", "error", "-nostdin", "-ss"] and float(frames[0][5]) == pytest.approx(249 / 30 / 2, abs=0.001)
    assert float(frames[1][5]) == pytest.approx(249 / 30 + 261 / 30 / 2, abs=0.001)


def test_an_existing_sheet_is_refused_before_any_check(ready, ffstub, tmp_path):
    sheet = tmp_path / "sheet.png"
    sheet.write_text("keep")
    code, out, err = run("check-video", ready, "--sheet", sheet, env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"check-video: {sheet} already exists; give a new name\n"
    assert sheet.read_text() == "keep" and ff_calls(ffstub) == []


def test_ffmpeg_failing_is_exit_4_with_its_output(ready, ffstub):
    code, out, err = run("check-video", ready, env=dict(ffstub, FFSTUB_FAIL="volume"))
    assert code == 4
    assert err.startswith("check-video: ffmpeg failed (exit 1) measuring the levels of ")
    assert err.endswith("stub ffmpeg: volume failed on purpose\n")


def test_the_video_is_never_modified(ready, ffstub, tmp_path):
    path = os.path.join(video(ready), "out", "Folding a Paper Boat.mp4")
    before = open(path, "rb").read()
    run("check-video", ready, "--sheet", tmp_path / "s.png", env=ffstub)
    assert open(path, "rb").read() == before


def test_the_sheets_label_sits_in_a_strip_under_each_frame_and_covers_no_pixel_of_it(ready, ffstub, tmp_path):
    sheet = tmp_path / "sheet.png"
    code, out, err = run("check-video", ready, "--sheet", sheet, env=ffstub)
    assert (code, err) == (0, "")
    im = Image.open(sheet).convert("RGB")
    # A 640 x 360 cell holds a 36 px strip, so the stub's square frame is scaled to 324 x 324 at the
    # cell's top left; beside it the sheet's white, under it the strip.
    assert im.getpixel((0, 0)) == (200, 40, 40) and im.getpixel((323, 323)) == (200, 40, 40)
    assert im.getpixel((330, 100)) == (255, 255, 255)
    assert im.getpixel((4, 328)) == (0x55, 0x55, 0x55)                        # the strip's fill
    strip = im.crop((0, 324, 324, 360))
    assert any(c == (255, 255, 255) for _, c in strip.getcolors(10000))       # its white text
    assert all(im.getpixel((x, y)) == (200, 40, 40) for x in range(0, 324, 27) for y in range(0, 324, 27))
