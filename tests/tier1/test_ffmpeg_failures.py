"""ffmpeg's answers that the commands cannot use are failures in words, exit 4: a short frame, no
levels, a failed silence scan. subprocess.run is replaced; no ffmpeg is run."""

import subprocess

import pytest

from videotools import cli, ffmpeg


@pytest.fixture
def answers(monkeypatch):
    """Make ffmpeg answer with the given exit code, stdout and stderr."""
    def set_answer(returncode=0, stdout="", stderr=""):
        monkeypatch.setattr(ffmpeg, "require", lambda name: "/fake/" + name)
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, returncode, stdout, stderr))
    return set_answer


def test_a_frame_of_the_wrong_size_is_refused_saying_the_file_may_be_shorter(answers):
    answers(stdout=b"\0" * 5)
    with pytest.raises(cli.Failure) as e:
        ffmpeg.frame_at("in.mp4", 9.5, 2, 1)
    assert (str(e.value), e.value.code) == ("ffmpeg gave 5 bytes for the frame of in.mp4 at 9.500 s, not the 6 of a "
                                            "2x1 frame; is the file that long?", cli.EXTERNAL)


def test_levels_without_a_volumedetect_report_are_refused_with_ffmpegs_output(answers):
    answers(stderr="Output #0, null\n  no audio here\n")
    with pytest.raises(cli.Failure) as e:
        ffmpeg.levels("in.mp4")
    assert (str(e.value), e.value.code) == ("ffmpeg's volumedetect gave no levels for in.mp4; its output follows\n"
                                            "Output #0, null\n  no audio here", cli.EXTERNAL)


def test_a_failed_silence_scan_is_refused_with_its_exit_code_and_output(answers):
    answers(returncode=1, stderr="in.mp4: Invalid data found\n")
    with pytest.raises(cli.Failure) as e:
        ffmpeg.silences("in.mp4")
    assert (str(e.value), e.value.code) == ("ffmpeg failed (exit 1) finding silences in in.mp4; its output follows\n"
                                            "in.mp4: Invalid data found", cli.EXTERNAL)
