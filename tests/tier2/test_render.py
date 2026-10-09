"""render: every frame of a scene piped to (stub) ffmpeg as raw BGRA; checks; refusals."""

import os
import subprocess
import sys

import pytest

from tests.tier2.conftest import EXAMPLE_FRAMES, REPO, fake_media, ff_calls, narrated, run

FRAME_BYTES = 1920 * 1080 * 4


@pytest.fixture
def prepared(example, ffstub):
    subprocess.run([sys.executable, os.path.join(REPO, "crop-insets"), example], check=True, capture_output=True)
    narrated(example)
    return example


def segments(example):
    return os.path.join(os.path.dirname(example), "work", "segments")


def fake(path):
    return dict(line.split("=", 1) for line in open(path).read().splitlines())


def test_help_and_usage():
    code, out, err = run("render", "--help")
    assert code == 0 and " ".join(out.split()).startswith("usage: render [-h] [--scenes KEY,...] [--frames A-B] [--replace] [--dry-run] SCRIPT")
    code, out, err = run("render")
    assert code == 2 and "usage: render" in err


def test_dry_run_lists_scenes_lengths_frames_and_segments_and_writes_nothing(prepared, ffstub):
    code, out, err = run("render", prepared, "--dry-run", env=ffstub)
    assert (code, err) == (0, "")
    seg = segments(prepared)
    assert out.splitlines()[0] == f"title  8.300 s  249 frames  -> {os.path.join(seg, 'title_00000.mp4')}"
    assert out.splitlines()[6] == f"end  5.700 s  171 frames  -> {os.path.join(seg, 'end_00000.mp4')}"
    assert out.splitlines()[-1] == "7 scenes, 52.900 s, 1587 frames; nothing written (dry run)."
    assert not os.path.exists(seg) and ff_calls(ffstub) == []


def test_a_scene_is_piped_frame_by_frame_to_ffmpeg_with_the_scripts_settings(prepared, ffstub):
    code, out, err = run("render", prepared, "--scenes", "B2", env=ffstub)
    assert (code, err) == (0, "")
    path = os.path.join(segments(prepared), "B2_00000.mp4")
    assert fake(path)["frames"] == "159" and fake(path)["bytes"] == str(159 * FRAME_BYTES)
    calls = ff_calls(ffstub)
    assert calls[0]["ffmpeg"] == ["-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1920x1080",
                                  "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                  "-pix_fmt", "yuv420p", "-r", "30", path]
    assert "-y" not in calls[0]["ffmpeg"]
    assert "nb_read_frames" in " ".join(calls[1]["ffprobe"])
    lines = out.splitlines()
    assert lines[0] == "B2  5.300 s  159 frames"
    assert lines[-1].startswith("Rendered B2: 159 frames in ") and " frames/s) -> " in lines[-1]


def test_the_quality_setting_is_the_crf(prepared, ffstub):
    text = open(prepared, encoding="utf-8").read().replace("| quality | 18 | |", "| quality | 20 | |")
    open(prepared, "w", encoding="utf-8").write(text)
    run("render", prepared, "--scenes", "end", env=ffstub)
    args = ff_calls(ffstub)[0]["ffmpeg"]
    assert args[args.index("-crf") + 1] == "20"


def test_a_frame_range_renders_part_of_one_scene_named_by_its_first_frame(prepared, ffstub):
    code, out, err = run("render", prepared, "--scenes", "A", "--frames", "100-130", env=ffstub)
    assert (code, err) == (0, "")
    path = os.path.join(segments(prepared), "A_00100.mp4")
    assert fake(path)["frames"] == "30"
    code, out, err = run("render", prepared, "--frames", "0-10", env=ffstub)
    assert code == 2 and err == "render: --frames needs exactly one scene in --scenes\n"
    code, out, err = run("render", prepared, "--scenes", "A", "--frames", "100-300", env=ffstub)
    assert code == 2 and err == "render: --frames 100-300 is outside scene A's 261 frames\n"


def test_every_scene_by_default_in_script_order(prepared, ffstub):
    code, out, err = run("render", prepared, env=ffstub)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(segments(prepared))) == sorted(f"{k}_00000.mp4" for k in EXAMPLE_FRAMES)
    assert all(fake(os.path.join(segments(prepared), f"{k}_00000.mp4"))["frames"] == str(n) for k, n in EXAMPLE_FRAMES.items())


def test_missing_timings_are_refused_never_estimated(prepared, ffstub):
    os.remove(os.path.join(os.path.dirname(prepared), "work", "narration", "timing.json"))
    code, out, err = run("render", prepared, "--scenes", "A", env=ffstub)
    assert (code, out) == (3, "")
    assert err == "render: scene A has no narration clips; run narrate first\n"
    narrated(prepared)
    import json
    tp = os.path.join(os.path.dirname(prepared), "work", "narration", "timing.json")
    timing = json.load(open(tp))
    timing["scenes"]["A"] = [1.0]
    json.dump(timing, open(tp, "w"))
    code, out, err = run("render", prepared, "--scenes", "A", env=ffstub)
    assert code == 3 and err == "render: scene A cue 2 has no narration clip; run narrate first\n"


def test_an_existing_segment_is_refused_unless_replace(prepared, ffstub):
    run("render", prepared, "--scenes", "end", env=ffstub)
    path = os.path.join(segments(prepared), "end_00000.mp4")
    before = open(path).read()
    code, out, err = run("render", prepared, "--scenes", "end,title", env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"render: these would be written over; delete them, or run with --replace:\n  {path}\n"
    assert open(path).read() == before and not os.path.exists(os.path.join(segments(prepared), "title_00000.mp4"))
    code, out, err = run("render", prepared, "--scenes", "end", "--replace", env=ffstub)
    assert code == 0 and out.startswith(f"Replacing:\n  {path}\n")


def test_ffmpeg_failing_names_the_partial_segment_and_exits_4(prepared, ffstub):
    code, out, err = run("render", prepared, "--scenes", "end", env=dict(ffstub, FFSTUB_FAIL="render"))
    path = os.path.join(segments(prepared), "end_00000.mp4")
    assert code == 4
    assert err.startswith(f"render: ffmpeg failed (exit 1) encoding scene end; its output follows, and {path} may be partial\n")
    assert os.path.exists(path)


def test_ffmpeg_dying_part_way_is_reported_not_hidden(prepared, ffstub):
    code, out, err = run("render", prepared, "--scenes", "end", env=dict(ffstub, FFSTUB_DIE="render"))
    assert code == 4
    assert "render: ffmpeg failed (exit 1) encoding scene end" in err


def test_a_segment_with_the_wrong_frame_count_is_reported(prepared, ffstub, tmp_path):
    # the stub counts the bytes it was sent; make ffprobe disagree by faking the file afterwards
    # is not possible mid-run, so pin the check through a stub that drops a frame: FFSTUB_DROP
    code, out, err = run("render", prepared, "--scenes", "end", env=dict(ffstub, FFSTUB_DROP="1"))
    path = os.path.join(segments(prepared), "end_00000.mp4")
    assert code == 4
    assert err == f"render: {path} holds 170 frames, not the 171 rendered; it is left for inspection\n"


def test_the_script_and_narration_are_never_modified(prepared, ffstub):
    folder = os.path.dirname(prepared)
    paths = [prepared] + sorted(os.path.join(folder, "work", "narration", f) for f in os.listdir(os.path.join(folder, "work", "narration")))
    before = [open(p, "rb").read() for p in paths]
    run("render", prepared, "--scenes", "end", env=ffstub)
    assert [open(p, "rb").read() for p in paths] == before
