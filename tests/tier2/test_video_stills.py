"""stills on a video file (item 24): frames at given times, every so many seconds or where the
picture changes, one PNG each at the video's own size plus stills.txt, and with --sheet a
labelled contact sheet; every refusal. ffmpeg and ffprobe are the stubs."""

import os

import pytest
from PIL import Image

from tests.tier2.conftest import fake_media, ff_calls, run


@pytest.fixture
def short(tmp_path):
    """A fake vertical Short, 480x854, 8.342 s: a colour per span, as the stub serves frames."""
    return fake_media(str(tmp_path / "clip" / "video.mp4"), duration="8.342", frames="250", width="480",
                      height="854", colours="0:10.20.30,2:40.50.60,4.04:70.80.90", scenes="2,4.04")


def test_help_names_both_forms():
    code, out, err = run("stills", "--help")
    assert code == 0 and " ".join(out.split()).startswith(
        "usage: stills [-h] [--cue-changes] [--scenes KEY,...] --out SHEET.png|FOLDER [--grid CxR] [--at T,T,...] "
        "[--every SECONDS] [--changes] [--threshold N] [--sheet SHEET.png] [--elements DIR] [--renderer PATH] "
        "SCRIPT|VIDEO [FRAMES]")
    assert "a video file (any name not ending .md)" in " ".join(out.split())


def test_at_writes_one_png_a_time_at_the_videos_own_size_and_lists_them(short, ffstub, tmp_path):
    folder = tmp_path / "stills"
    code, out, err = run("stills", short, "--at", "0,1.5,3", "--out", folder, env=ffstub)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(folder)) == ["stills.txt", "t0000.00.png", "t0001.50.png", "t0003.00.png"]
    for name, colour in [("t0000.00.png", (10, 20, 30)), ("t0001.50.png", (10, 20, 30)), ("t0003.00.png", (40, 50, 60))]:
        im = Image.open(folder / name)
        assert (im.size, im.getpixel((0, 0))[:3], im.getpixel((479, 853))[:3]) == ((480, 854), colour, colour)
    assert (folder / "stills.txt").read_text() == "0.00 t0000.00.png\n1.50 t0001.50.png\n3.00 t0003.00.png\n"
    assert out.splitlines() == ["t0000.00.png at 0.000 s", "t0001.50.png at 1.500 s", "t0003.00.png at 3.000 s",
                                f"Wrote 3 stills to {folder}"]
    calls = ff_calls(ffstub)
    assert [list(c)[0] for c in calls] == ["ffprobe", "ffmpeg", "ffmpeg", "ffmpeg"]
    for call, at in zip(calls[1:], ("0.000", "1.500", "3.000")):
        args = call["ffmpeg"]
        assert args[args.index("-ss") + 1] == at and args[args.index("-s") + 1] == "480x854" and args[-1] == "-"


def test_every_takes_a_frame_every_n_seconds_from_zero_while_less_than_the_length(short, ffstub, tmp_path):
    folder = tmp_path / "stills"
    code, out, err = run("stills", short, "--every", "2", "--out", folder, env=ffstub)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(folder)) == ["stills.txt", "t0000.00.png", "t0002.00.png", "t0004.00.png", "t0006.00.png",
                                          "t0008.00.png"]                 # 8 < 8.342; 10 would be past the end
    assert (folder / "stills.txt").read_text().splitlines()[-1] == "8.00 t0008.00.png"
    assert out.splitlines()[-1] == f"Wrote 5 stills to {folder}"
    assert [c["ffmpeg"][c["ffmpeg"].index("-ss") + 1] for c in ff_calls(ffstub)[1:]] == \
        ["0.000", "2.000", "4.000", "6.000", "8.000"]


def test_every_of_zero_or_less_is_refused_before_ffmpeg_runs(short, ffstub, tmp_path):
    for bad in ("0", "-1"):
        code, out, err = run("stills", short, "--every", bad, "--out", tmp_path / "stills", env=ffstub)
        assert (code, out, err) == (2, "", "stills: --every must be more than 0\n")
    assert ff_calls(ffstub) == [] and not (tmp_path / "stills").exists()


def test_changes_takes_the_first_frame_and_each_cut_ffmpeg_reports_with_the_threshold_as_data(short, ffstub, tmp_path):
    folder = tmp_path / "stills"
    code, out, err = run("stills", short, "--changes", "--out", folder, env=ffstub)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(folder)) == ["stills.txt", "t0000.00.png", "t0002.00.png", "t0004.04.png"]
    assert Image.open(folder / "t0004.04.png").getpixel((0, 0))[:3] == (70, 80, 90)
    assert (folder / "stills.txt").read_text() == "0.00 t0000.00.png\n2.00 t0002.00.png\n4.04 t0004.04.png\n"
    calls = ff_calls(ffstub)
    assert [list(c)[0] for c in calls] == ["ffprobe", "ffmpeg", "ffmpeg", "ffmpeg", "ffmpeg"]
    scan = calls[1]["ffmpeg"]
    assert scan[scan.index("-vf") + 1] == "select='gt(scene,0.3)',metadata=print"   # one argument, never shell text
    assert scan[scan.index("-f") + 1] == "null" and scan[-1] == "-" and "-nostdin" in scan
    assert [c["ffmpeg"][c["ffmpeg"].index("-ss") + 1] for c in calls[2:]] == ["0.000", "2.000", "4.040"]
    code, out, err = run("stills", short, "--changes", "--threshold", "0.55", "--out", tmp_path / "again", env=ffstub)
    scan = ff_calls(ffstub)[6]["ffmpeg"]
    assert code == 0 and scan[scan.index("-vf") + 1] == "select='gt(scene,0.55)',metadata=print"


@pytest.mark.parametrize("flags, message", [
    ([], "choose how to pick the frames of a video file: --at, --every or --changes"),
    (["--at", "1", "--every", "2"], "give one of --at, --every and --changes, not --at and --every"),
    (["--at", "1", "--changes"], "give one of --at, --every and --changes, not --at and --changes"),
    (["--every", "2", "--changes", "--threshold", "0.4"], "give one of --at, --every and --changes, not --every and --changes"),
    (["--at", "1", "--threshold", "0.4"], "--threshold goes with --changes"),
    (["--changes", "--threshold", "1.5"], "--threshold should be a number from 0 to 1, not '1.5'"),
    (["--at", "1", "--grid", "3"], "--grid should be COLUMNSxROWS, not '3'"),
    (["--every", "10", "--sheet", "s.png", "--grid", "0x3"], "--grid needs at least one column and one row, not '0x3'"),
    (["--at", "1", "--grid=-1x2"], "--grid needs at least one column and one row, not '-1x2'"),   # argparse: -1x2 is an option otherwise
    (["--at", "1,x"], "--at: 'x' is not a time in seconds"),
])
def test_a_bad_choice_of_frames_is_refused_before_ffmpeg_runs(short, ffstub, tmp_path, flags, message):
    code, out, err = run("stills", short, *flags, "--out", tmp_path / "stills", env=ffstub)
    assert (code, out, err) == (2, "", f"stills: {message}\n")
    assert ff_calls(ffstub) == [] and not (tmp_path / "stills").exists()


def test_a_time_past_the_end_is_refused_naming_the_length_and_nothing_is_written(short, ffstub, tmp_path):
    code, out, err = run("stills", short, "--at", "1,8.342,2", "--out", tmp_path / "stills", env=ffstub)
    assert (code, out, err) == (2, "", f"stills: 8.342 s is past the end of {short} (8.342 s)\n")
    assert [list(c)[0] for c in ff_calls(ffstub)] == ["ffprobe"] and not (tmp_path / "stills").exists()


def test_an_existing_still_or_listing_is_never_written_over_and_the_folder_is_left_as_it_was(short, ffstub, tmp_path):
    folder = tmp_path / "stills"
    folder.mkdir()
    (folder / "t0001.50.png").write_bytes(b"mine")
    (folder / "notes.md").write_text("keep\n")
    code, out, err = run("stills", short, "--at", "0,1.5", "--out", folder, env=ffstub)
    assert (code, out, err) == (3, "", f"stills: {folder / 't0001.50.png'} already exists; give a new name\n")
    assert sorted(os.listdir(folder)) == ["notes.md", "t0001.50.png"] and (folder / "t0001.50.png").read_bytes() == b"mine"
    assert [list(c)[0] for c in ff_calls(ffstub)] == ["ffprobe"]           # no frame was read
    (folder / "t0001.50.png").unlink()
    (folder / "stills.txt").write_text("mine\n")
    code, out, err = run("stills", short, "--changes", "--out", folder, env=ffstub)
    assert (code, out, err) == (3, "", f"stills: {folder / 'stills.txt'} already exists; give a new name\n")
    assert sorted(os.listdir(folder)) == ["notes.md", "stills.txt"] and (folder / "stills.txt").read_text() == "mine\n"
    assert [list(c)[0] for c in ff_calls(ffstub)] == ["ffprobe", "ffprobe"]   # refused before the scan


STRIP = (0x55, 0x55, 0x55)


def test_the_sheet_keeps_a_vertical_videos_proportions_in_360_wide_cells_with_the_label_under_each(short, ffstub, tmp_path):
    folder, sheet = tmp_path / "stills", tmp_path / "sheet.png"
    code, out, err = run("stills", short, "--at", "0,2,4.04", "--out", folder, "--sheet", sheet, env=ffstub)
    assert (code, err) == (0, "")
    im = Image.open(sheet)
    assert im.size == (720, 1354)                                    # 3 frames: 2x2 cells of 360 x (641 + 36)
    assert im.getpixel((10, 10))[:3] == (10, 20, 30)                 # frame 1, top left
    assert im.getpixel((359, 639))[:3] == (10, 20, 30)               # frame 1 fills its 360x640
    assert im.getpixel((10, 640 + 5))[:3] == STRIP                   # its label strip, under it
    assert im.getpixel((360 + 10, 10))[:3] == (40, 50, 60)           # frame 2
    assert im.getpixel((10, 677 + 10))[:3] == (70, 80, 90)           # frame 3, second row
    assert im.getpixel((360 + 10, 677 + 10))[:3] == (255, 255, 255)  # the empty fourth cell
    assert out.splitlines()[-1] == f"Wrote 3 stills to {folder} and the sheet {sheet}"
    assert sorted(os.listdir(folder)) == ["stills.txt", "t0000.00.png", "t0002.00.png", "t0004.04.png"]


def test_a_landscape_video_gets_short_cells_and_a_given_grid_spreads_over_numbered_sheets(ffstub, tmp_path):
    wide = fake_media(str(tmp_path / "wide.mp4"), duration="8.342", frames="250", width="854", height="480",
                      colours="0:10.20.30,4:40.50.60")
    folder, sheet = tmp_path / "stills", tmp_path / "s.png"
    code, out, err = run("stills", wide, "--every", "4", "--out", folder, "--sheet", sheet, "--grid", "2x1", env=ffstub)
    assert (code, err) == (0, "")
    assert not sheet.exists()
    one, two = Image.open(tmp_path / "s-1.png"), Image.open(tmp_path / "s-2.png")
    assert one.size == two.size == (720, 239)                         # 2x1 cells of 360 x (203 + 36)
    assert one.getpixel((10, 10))[:3] == (10, 20, 30) and one.getpixel((370, 10))[:3] == (40, 50, 60)   # 0 s, 4 s
    assert one.getpixel((10, 201))[:3] == (10, 20, 30) and one.getpixel((10, 202 + 5))[:3] == STRIP
    assert two.getpixel((10, 10))[:3] == (40, 50, 60) and two.getpixel((370, 10))[:3] == (255, 255, 255)   # 8 s, then empty
    assert out.splitlines()[-1] == f"Wrote 3 stills to {folder} and 2 sheets {tmp_path / 's-1.png'}, {tmp_path / 's-2.png'}"


def test_an_existing_sheet_is_refused_before_anything_is_read_or_written(short, ffstub, tmp_path):
    sheet = tmp_path / "sheet.png"
    sheet.write_bytes(b"mine")
    code, out, err = run("stills", short, "--at", "0", "--out", tmp_path / "stills", "--sheet", sheet, env=ffstub)
    assert (code, out, err) == (3, "", f"stills: {sheet} already exists; give a new name\n")
    assert ff_calls(ffstub) == [] and not (tmp_path / "stills").exists() and sheet.read_bytes() == b"mine"
    (tmp_path / "s-2.png").write_bytes(b"mine")
    code, out, err = run("stills", short, "--at", "0,1,2", "--grid", "1x1", "--out", tmp_path / "stills",
                         "--sheet", tmp_path / "s.png", env=ffstub)
    assert (code, out, err) == (3, "", f"stills: {tmp_path / 's-2.png'} already exists; give a new name\n")
    assert [list(c)[0] for c in ff_calls(ffstub)] == ["ffprobe"] and not (tmp_path / "stills").exists()


@pytest.mark.parametrize("flags, message", [
    (["A:1"], "SCENE:SECONDS goes with a script, not a video file"),
    (["--cue-changes"], "--cue-changes goes with a script, not a video file"),
    (["--at", "1", "--scenes", "A"], "--scenes goes with a script, not a video file"),
    (["--at", "1", "--elements", "x"], "--elements goes with a script, not a video file"),
    (["--at", "1", "--renderer", "x"], "--renderer goes with a script, not a video file"),
])
def test_the_script_forms_flags_are_refused_with_a_video_file(short, ffstub, tmp_path, flags, message):
    code, out, err = run("stills", short, *flags, "--out", tmp_path / "stills", env=ffstub)
    assert (code, out, err) == (2, "", f"stills: {message}\n") and ff_calls(ffstub) == []


@pytest.mark.parametrize("flags, flag", [
    (["--at", "1"], "--at"), (["--every", "2"], "--every"), (["--changes"], "--changes"),
    (["--threshold", "0.4"], "--threshold"), (["--sheet", "s.png"], "--sheet"),
])
def test_the_video_forms_flags_are_refused_with_a_script(example, tmp_path, flags, flag):
    code, out, err = run("stills", example, "A:1", *flags, "--out", tmp_path / "sheet.png")
    assert (code, out, err) == (2, "", f"stills: {flag} goes with a video file, not a script\n")


def test_without_ffmpeg_the_video_form_says_so_and_a_failing_frame_is_reported_with_what_stays(short, ffstub, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    code, out, err = run("stills", short, "--at", "0", "--out", tmp_path / "stills", env={"PATH": str(empty)})
    assert (code, out, err) == (4, "", "stills: ffmpeg is not on PATH; install ffmpeg as the README says\n")
    code, out, err = run("stills", short, "--at", "0,1", "--out", tmp_path / "stills", env={**ffstub, "FFSTUB_FAIL": "frame"})
    assert code == 4 and out == ""
    assert err.startswith(f"stills: ffmpeg failed (exit 1) reading the frame of {short} at 0.000 s; its output follows\n")
    assert os.listdir(tmp_path / "stills") == []                    # the first frame failed: nothing kept, no listing


def test_names_with_spaces_and_non_ascii_pass_through_as_data(ffstub, tmp_path):
    video = fake_media(str(tmp_path / "clips élan" / "my video 'q' $x.mp4"), duration="3", frames="90",
                       width="480", height="854", colours="0:1.2.3", scenes="1.5")
    folder = tmp_path / "stills für \"q\""
    code, out, err = run("stills", video, "--changes", "--out", folder, "--sheet", folder / "sheet ß.png", env=ffstub)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(folder)) == ["sheet ß.png", "stills.txt", "t0000.00.png", "t0001.50.png"]
    scan = ff_calls(ffstub)[1]["ffmpeg"]
    assert scan[scan.index("-i") + 1] == video                       # the path is one argument, as given
