"""assemble: segments joined, narration laid at cue times, refusals, the report."""

import hashlib
import os

import numpy as np
import pytest
import soundfile

from tests.tier2.conftest import EXAMPLE_FRAMES, fake_media, ff_calls, narrated, rendered, run

TOTAL_FRAMES = sum(EXAMPLE_FRAMES.values())     # 1587 frames, 52.9 s


def video(example):
    return os.path.dirname(example)


@pytest.fixture
def ready(example, ffstub):
    narrated(example)
    rendered(example)
    return example


def test_help_and_usage():
    code, out, err = run("assemble", "--help")
    assert code == 0 and out.startswith("usage: assemble [-h] [--out FILE] [--replace] SCRIPT")
    code, out, err = run("assemble")
    assert code == 2 and "usage: assemble" in err


def test_the_segments_are_joined_in_script_order_and_muxed_with_the_narration(ready, ffstub):
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, err) == (0, "")
    work = os.path.join(video(ready), "work", "assemble")
    out_file = os.path.join(video(ready), "out", "Folding a Paper Boat.mp4")
    assert open(os.path.join(work, "segments.txt")).read() == "".join(
        f"file '{os.path.join(video(ready), 'work', 'segments', k + '_00000.mp4')}'\n" for k in EXAMPLE_FRAMES)
    calls = ff_calls(ffstub)
    concat = [c["ffmpeg"] for c in calls if "ffmpeg" in c and "concat" in c["ffmpeg"]][0]
    assert concat == ["-hide_banner", "-loglevel", "error", "-nostdin", "-f", "concat", "-safe", "0", "-i",
                      os.path.join(work, "segments.txt"), "-c", "copy", os.path.join(work, "video-only.mp4")]
    mux = [c["ffmpeg"] for c in calls if "ffmpeg" in c and "aac" in c["ffmpeg"]][0]
    assert mux == ["-hide_banner", "-loglevel", "error", "-nostdin", "-i", os.path.join(work, "video-only.mp4"), "-i",
                   os.path.join(work, "narration.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                   "-movflags", "+faststart", "-shortest", out_file]
    assert "-y" not in concat and "-y" not in mux
    fake = dict(line.split("=", 1) for line in open(out_file).read().splitlines())
    assert (fake["frames"], fake["joined"], fake["audio"]) == (str(TOTAL_FRAMES), "7", "narration.wav")
    size = os.path.getsize(out_file)
    sha = hashlib.sha256(open(out_file, "rb").read()).hexdigest()
    assert out.splitlines()[-3:] == [f"Wrote {out_file}", f"length 52.900 s ({TOTAL_FRAMES} frames), size {size} bytes",
                                     f"sha256 {sha}"]


def test_each_clip_is_laid_at_its_scenes_start_plus_its_cues_start_plus_50_ms_at_48_khz(ready, ffstub):
    run("assemble", ready, env=ffstub)
    mix, rate = soundfile.read(os.path.join(video(ready), "work", "assemble", "narration.wav"), dtype="float32")
    assert rate == 48000 and mix.ndim == 1
    assert len(mix) == round(TOTAL_FRAMES / 30 * 48000)
    loud = np.flatnonzero(np.abs(mix) > 1e-4)
    # title cue 1 starts at lead 0.7 s; + 0.05 s = 0.75 s = sample 36000, a 1 s clip to 84000
    assert loud[0] == 36000
    assert loud[loud < 100000][-1] == 84000 - 1
    # title cue 2 at 0.7 + 3.0 + 0.05 = 3.75 s; A cue 1 at 8.3 + 0.7 + 0.05 = 9.05 s
    assert np.abs(mix[int(3.75 * 48000) + 10]) > 1e-4 and np.abs(mix[int(3.75 * 48000) - 10]) < 1e-4
    assert np.abs(mix[int(9.05 * 48000) + 10]) > 1e-4 and np.abs(mix[int(9.05 * 48000) - 10]) < 1e-4


def test_the_mix_is_peak_normalised_to_0_89(ready, ffstub):
    run("assemble", ready, env=ffstub)
    mix, _ = soundfile.read(os.path.join(video(ready), "work", "assemble", "narration.wav"), dtype="float32")
    assert float(np.abs(mix).max()) == pytest.approx(0.89, abs=0.001)


def test_a_clip_at_another_sample_rate_is_resampled_to_its_true_length(example, ffstub):
    narrated(example, rate=22050, seconds=0.5)
    rendered(example)
    run("assemble", example, env=ffstub)
    mix, _ = soundfile.read(os.path.join(video(example), "work", "assemble", "narration.wav"), dtype="float32")
    loud = np.flatnonzero(np.abs(mix) > 1e-4)
    assert loud[0] == 36000 and loud[loud < 100000][-1] == 36000 + 24000 - 1


def test_out_overrides_the_scripts_output(ready, ffstub, tmp_path):
    code, out, err = run("assemble", ready, "--out", tmp_path / "else.mp4", env=ffstub)
    assert (code, err) == (0, "")
    assert os.path.exists(tmp_path / "else.mp4")
    assert not os.path.exists(os.path.join(video(ready), "out"))


def test_missing_segments_or_clips_are_refused_by_name_and_nothing_is_written(ready, ffstub):
    os.remove(os.path.join(video(ready), "work", "segments", "B2_00000.mp4"))
    os.remove(os.path.join(video(ready), "work", "narration", "C_02.wav"))
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == (f"assemble: scene B2 has no segment in {os.path.join(video(ready), 'work', 'segments')}\n"
                   f"assemble: scene C cue 2 has no clip: {os.path.join(video(ready), 'work', 'narration', 'C_02.wav')}\n")
    assert not os.path.exists(os.path.join(video(ready), "work", "assemble"))
    assert ff_calls(ffstub) == []


def test_missing_timings_are_refused(ready, ffstub):
    os.remove(os.path.join(video(ready), "work", "narration", "timing.json"))
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"assemble: no {os.path.join(video(ready), 'work', 'narration', 'timing.json')}; run narrate first\n"


def test_segments_whose_frames_do_not_add_up_are_refused(ready, ffstub):
    seg = os.path.join(video(ready), "work", "segments")
    fake_media(os.path.join(seg, "A_00000.mp4"), frames=100, duration="3.333333")
    fake_media(os.path.join(seg, "A_00100.mp4"), frames=160, duration="5.333333")
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == "assemble: scene A: its segments hold 260 frames, the script's timing gives 261\n"


def test_segments_that_do_not_chain_from_frame_0_are_refused(ready, ffstub):
    seg = os.path.join(video(ready), "work", "segments")
    fake_media(os.path.join(seg, "A_00000.mp4"), frames=100, duration="3.333333")
    fake_media(os.path.join(seg, "A_00110.mp4"), frames=161, duration="5.366667")
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, out) == (3, "")
    assert err == "assemble: scene A: segment A_00110.mp4 starts at frame 110 but the segments before it end at 100\n"


def test_a_scene_in_several_segments_is_joined_in_frame_order(ready, ffstub):
    seg = os.path.join(video(ready), "work", "segments")
    os.remove(os.path.join(seg, "A_00000.mp4"))
    fake_media(os.path.join(seg, "A_00100.mp4"), frames=161, duration="5.366667")
    fake_media(os.path.join(seg, "A_00000.mp4"), frames=100, duration="3.333333")
    code, out, err = run("assemble", ready, env=ffstub)
    assert (code, err) == (0, "")
    lst = open(os.path.join(video(ready), "work", "assemble", "segments.txt")).read().splitlines()
    assert lst[1:3] == [f"file '{os.path.join(seg, 'A_00000.mp4')}'", f"file '{os.path.join(seg, 'A_00100.mp4')}'"]


def test_an_existing_output_is_refused_and_never_replaced(ready, ffstub):
    out_dir = os.path.join(video(ready), "out")
    os.makedirs(out_dir)
    open(os.path.join(out_dir, "Folding a Paper Boat.mp4"), "w").write("keep")
    code, out, err = run("assemble", ready, "--replace", env=ffstub)
    assert (code, out) == (3, "")
    assert err == f"assemble: {os.path.join(out_dir, 'Folding a Paper Boat.mp4')} already exists; give a new name\n"
    assert open(os.path.join(out_dir, "Folding a Paper Boat.mp4")).read() == "keep"


def test_existing_intermediates_are_refused_unless_replace(ready, ffstub, tmp_path):
    run("assemble", ready, env=ffstub)
    first_calls = [c for c in ff_calls(ffstub) if "ffmpeg" in c]
    work = os.path.join(video(ready), "work", "assemble")
    code, out, err = run("assemble", ready, "--out", tmp_path / "two.mp4", env=ffstub)
    assert (code, out) == (3, "")
    assert err == ("assemble: these would be written over; delete them, or run with --replace:\n"
                   + "".join(f"  {os.path.join(work, f)}\n" for f in ("narration.wav", "segments.txt", "video-only.mp4")))
    assert [c for c in ff_calls(ffstub) if "ffmpeg" in c] == first_calls   # refused before ffmpeg ran
    code, out, err = run("assemble", ready, "--out", tmp_path / "two.mp4", "--replace", env=ffstub)
    assert (code, err) == (0, "")
    assert out.startswith("Replacing:\n")
    assert os.path.exists(tmp_path / "two.mp4")
    concat, mux = [c["ffmpeg"] for c in ff_calls(ffstub)[len(first_calls):] if "ffmpeg" in c][-2:]
    assert "-y" in concat and "-nostdin" in concat            # the listed intermediate may be written over
    assert "-y" not in mux and "-nostdin" in mux              # the finished video never


def test_a_failed_concat_names_the_partial_file_and_exits_4(ready, ffstub):
    code, out, err = run("assemble", ready, env=dict(ffstub, FFSTUB_FAIL="concat"))
    work = os.path.join(video(ready), "work", "assemble")
    assert code == 4 and out.startswith("Narration mixed")      # progress so far stays on stdout
    assert err == (f"assemble: ffmpeg failed (exit 1) joining the segments; its output follows, and "
                   f"{os.path.join(work, 'video-only.mp4')} may be partial\nstub ffmpeg: concat failed on purpose\n")
    assert os.path.exists(os.path.join(work, "video-only.mp4"))
    assert not os.path.exists(os.path.join(video(ready), "out"))


def test_a_failed_mux_names_the_partial_output_and_exits_4(ready, ffstub):
    code, out, err = run("assemble", ready, env=dict(ffstub, FFSTUB_FAIL="mux"))
    out_file = os.path.join(video(ready), "out", "Folding a Paper Boat.mp4")
    assert code == 4 and out.endswith(f"Segments joined to {os.path.join(video(ready), 'work', 'assemble', 'video-only.mp4')}\n")
    assert err == (f"assemble: ffmpeg failed (exit 1) muxing the narration; its output follows, and "
                   f"{out_file} may be partial\nstub ffmpeg: mux failed on purpose\n")


def test_ffmpeg_missing_from_path_is_a_useful_error(ready, tmp_path):
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    code, out, err = run("assemble", ready, env={"PATH": str(empty)})
    assert (code, out) == (4, "")
    assert err == "assemble: ffprobe is not on PATH; install ffmpeg as the README says\n"


def test_the_segments_clips_and_script_are_never_modified(ready, ffstub):
    folder = video(ready)
    paths = [ready] + sorted(os.path.join(d, f) for d in (os.path.join(folder, "work", "segments"),
                                                            os.path.join(folder, "work", "narration"))
                             for f in os.listdir(d))
    before = [open(p, "rb").read() for p in paths]
    run("assemble", ready, env=ffstub)
    assert [open(p, "rb").read() for p in paths] == before
