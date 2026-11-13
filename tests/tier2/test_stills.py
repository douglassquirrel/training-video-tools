"""stills: frames at given times on one labelled sheet; estimates with a warning; refusals."""

import os
import subprocess
import sys

import pytest
from PIL import Image

from tests.tier2.conftest import REPO, clean_env, cropped, narrated, run


@pytest.fixture
def prepared(example):
    cropped(example)
    return example


def test_help_and_usage():
    code, out, err = run("stills", "--help")
    assert code == 0 and " ".join(out.split()).startswith(
        "usage: stills [-h] [--cue-changes] [--scenes KEY,...] --out SHEET.png [--grid CxR] [--elements DIR] "
        "[--renderer PATH] SCRIPT [FRAMES]")
    for gone in ("--at", "--every", "--changes", "--threshold", "--detect-fps", "--from", "--until", "--sheet", "SCRIPT|VIDEO", "FOLDER"):
        assert gone not in out
    code, out, err = run("stills", "x.md")
    assert code == 2 and "usage: stills" in err


def test_four_frames_make_a_2x2_sheet_each_labelled(prepared, tmp_path):
    narrated(prepared)
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "A:1.5,A:5.0,B:3.5,end:1.5", "--out", sheet)
    assert (code, err) == (0, "")
    im = Image.open(sheet)
    assert im.size == (1920, 1080)
    # Frames are 896x504 in a 960x540 cell, the label strip under each (test below).
    assert im.getpixel((960 + 16, 20))[:3] == (0xF7, 0xF3, 0xEA)        # frame 2's background, top left
    assert im.getpixel((100, 540 + 490))[:3] == (0x2B, 0x2B, 0x2B)       # frame 3's caption band, bottom left
    assert im.getpixel((100 + 960, 540 + 490))[:3] == (0xF7, 0xF3, 0xEA)  # the end card has no band
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
    assert Image.open(sheet).getpixel((100, 1030))[:3] == (0x2B, 0x2B, 0x2B)   # 1856x1044: the band is at the bottom
    assert Image.open(sheet).getpixel((1900, 500))[:3] == (255, 255, 255)        # beside the frame: the sheet's white
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


def test_a_malformed_brand_kit_is_refused_in_words_with_exit_3_not_a_traceback(prepared, tmp_path):
    kit = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(prepared))), "brands", "paperboat", "BRAND.md")
    text = open(kit, encoding="utf-8").read().replace("| website |", "| x-website |", 1)
    open(kit, "w", encoding="utf-8").write(text)
    code, out, err = run("stills", prepared, "A:1.5", "--out", tmp_path / "s.png")
    assert (code, out) == (3, "")
    assert "Traceback" not in err
    assert err == f"stills: {os.path.dirname(kit)}: Identity: 'website' is missing\n"
    assert not os.path.exists(tmp_path / "s.png")


FRAME_ALONE = """
import sys
sys.path.insert(0, {repo!r})
import cairo
from videotools import frame, stills
video = frame.Video({script!r})
scene = video.scene("A")
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
frame.draw_frame(cairo.Context(surface), video, scene, video.timeline(scene), 1.5)
surface.flush()
from PIL import Image
stills.to_image(surface).resize({size!r}, Image.LANCZOS).save({out!r})
"""


def test_the_label_sits_in_a_strip_under_the_frame_and_covers_no_pixel_of_it(prepared, tmp_path):
    from PIL import ImageChops

    from videotools import sheet as sheet_

    narrated(prepared)
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "A:1.5", "--out", sheet)
    assert (code, err) == (0, "")
    im = Image.open(sheet).convert("RGB")
    w, h = sheet_.frame_size((960, 540))
    assert (w, h) == (896, 504)                                          # 16:9 in the cell above the strip
    # The same frame drawn alone and scaled as the cell scales it: in a fresh process, as the command
    # draws it, because fontconfig (Linux) fixes its font list at a process's first text call and an
    # earlier test's text would leave this process with other fonts than the command's.
    alone_path = tmp_path / "alone.png"
    code = FRAME_ALONE.format(repo=REPO, script=prepared, size=(w, h), out=str(alone_path))
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, env=clean_env(PYTHONDONTWRITEBYTECODE="1"))
    alone = Image.open(alone_path).convert("RGB")
    assert ImageChops.difference(im.crop((0, 0, w, h)), alone).getbbox() is None
    assert im.getpixel((16, 20)) == (0xF7, 0xF3, 0xEA)                   # the header's corner is the frame's background
    strip = im.crop((0, h, w, 540))
    assert strip.getpixel((4, 4)) == (0x55, 0x55, 0x55)                  # the strip's fill, apart from the band
    assert strip.getcolors(10000) and any(c == (255, 255, 255) for _, c in strip.getcolors(10000))  # its white text


# ---- --cue-changes: frames around every cue start, several sheets, and the curtain warning

THIRD_CUE = "3. Then open it out.\n"
FAULTY = '''"""A scene that keeps its old picture until the next cue's start: the glimpse."""
from videotools import draw as d


def draw(frame):
    tl, t = frame.timeline, frame.t
    a = 1 - tl.p(t, 3, 0.0, 0.1)            # goes as the panel lifts, so it shows through the lifting panel
    d.fill_rrect(frame.ctx, 300, 300, 500, 400, 10, frame.colours["paper-edge"], alpha=a)


def mistake(frame, rect):
    pass


def right_way(frame, rect):
    pass
'''
FIXED = FAULTY.replace("a = 1 - tl.p(t, 3, 0.0, 0.1)", "a = tl.before_curtain(t)        ")


def three_cues(example, module):
    """The example copy with a third cue after scene A's mistake cue, its module replaced, and
    timings for three 1 s clips: cue starts 0.7, 3.7 (min 3.0) and 7.7 (min 4.0)."""
    import json
    narrated(example)
    text = open(example, encoding="utf-8").read()
    anchor = "   - added: the consequence (no hull) is our inference; the figure shows only the edge fold.\n"
    assert anchor in text
    open(example, "w", encoding="utf-8").write(text.replace(anchor, anchor + THIRD_CUE))
    folder = os.path.dirname(example)
    with open(os.path.join(folder, "scenes", "fold_in_half.py"), "w", encoding="utf-8") as f:
        f.write(module)
    tp = os.path.join(folder, "work", "narration", "timing.json")
    timing = json.load(open(tp))
    timing["scenes"]["A"] = [1.0, 1.0, 1.0]
    json.dump(timing, open(tp, "w"))
    return example


def test_cue_changes_draws_three_frames_around_each_cue_start_on_one_sheet_when_they_fit(prepared, tmp_path):
    narrated(prepared)
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "--cue-changes", "--scenes", "B2", "--out", sheet)
    assert (code, err) == (0, "")
    assert out.splitlines() == ["B2 at 0.400 s (of 5.300 s, no cue)", "B2 at 0.700 s (of 5.300 s, cue 1)",
                                "B2 at 1.000 s (of 5.300 s, cue 1)", f"Wrote {sheet}: 3 frames, 2x2"]
    assert Image.open(sheet).size == (1920, 1080)


def test_cue_changes_adds_a_frame_after_the_curtain_has_gone_and_spreads_over_numbered_sheets(prepared, tmp_path):
    three_cues(prepared, FIXED)
    sheet = tmp_path / "sheet.png"
    code, out, err = run("stills", prepared, "--cue-changes", "--scenes", "A", "--out", sheet)
    assert (code, err) == (0, "")
    times = [line.split(" at ")[1].split(" s")[0] for line in out.splitlines() if line.startswith("A at ")]
    assert times == ["0.400", "0.700", "1.000", "3.400", "3.700", "4.000", "7.400", "7.700", "8.000", "8.300"]
    assert [line for line in out.splitlines() if line.startswith("Wrote ")] == [     # one after each sheet's frames
        f"Wrote {tmp_path / 'sheet-1.png'}: 4 frames, 2x2",
        f"Wrote {tmp_path / 'sheet-2.png'}: 4 frames, 2x2",
        f"Wrote {tmp_path / 'sheet-3.png'}: 2 frames, 2x2"]
    assert not sheet.exists() and all((tmp_path / f"sheet-{i}.png").exists() for i in (1, 2, 3))


def test_cue_changes_with_frames_or_without_out_is_usage(prepared, tmp_path):
    code, out, err = run("stills", prepared, "A:1", "--cue-changes", "--out", tmp_path / "s.png")
    assert code == 2 and "--cue-changes takes no SCENE:SECONDS" in err
    code, out, err = run("stills", prepared, "--out", tmp_path / "s.png")
    assert code == 2 and "give SCENE:SECONDS, or --cue-changes" in err


def test_a_numbered_sheet_that_exists_is_refused_before_anything_is_drawn(prepared, tmp_path):
    three_cues(prepared, FIXED)
    (tmp_path / "sheet-2.png").write_bytes(b"keep")
    code, out, err = run("stills", prepared, "--cue-changes", "--scenes", "A", "--out", tmp_path / "sheet.png")
    assert (code, out) == (3, "")
    assert err == f"stills: {tmp_path / 'sheet-2.png'} already exists; give a new name\n"
    assert not (tmp_path / "sheet-1.png").exists() and (tmp_path / "sheet-2.png").read_bytes() == b"keep"


def test_a_picture_that_vanishes_as_the_curtain_lifts_is_a_warning_naming_the_scene_and_cues(prepared, tmp_path):
    import re
    three_cues(prepared, FAULTY)
    code, out, err = run("stills", prepared, "--cue-changes", "--scenes", "A", "--out", tmp_path / "s.png")
    assert code == 0
    assert re.fullmatch(r"stills: scene A: something drawn under the panel at cue 2 vanishes as it lifts for cue 3 "
                        r"\(\d{4,} pixels\); fade it out while covered: frame\.timeline\.before_curtain\n", err), err
    assert (tmp_path / "s-1.png").exists()


def test_a_picture_faded_out_under_the_curtain_gives_no_warning(prepared, tmp_path):
    three_cues(prepared, FIXED)
    code, out, err = run("stills", prepared, "--cue-changes", "--scenes", "A", "--out", tmp_path / "s.png")
    assert (code, err) == (0, "")


def test_a_described_scene_with_no_code_draws_its_chrome_and_panels_and_needs_no_module(prepared, tmp_path):
    from tests.tier2.test_check_script_choreography import described
    narrated(prepared)
    script = described(prepared)
    text = open(script, encoding="utf-8").read().replace("| code | fold_in_half | |\n", "")
    open(script, "w", encoding="utf-8").write(text)
    sheet = tmp_path / "sheet.png"
    from tests.tier2.test_check_script_choreography import INVENTED
    code, out, err = run("stills", script, "A:1.0,A:5.0", "--out", sheet, "--elements", INVENTED)
    assert (code, err) == (0, "")
    assert sheet.exists()


def test_a_grid_with_no_columns_or_rows_is_refused_in_words_in_the_script_form_too(prepared, tmp_path):
    for flags in (["A:1"], ["--cue-changes"]):
        code, out, err = run("stills", prepared, *flags, "--out", tmp_path / "sheet.png", "--grid", "0x3")
        assert (code, out, err) == (2, "", "stills: --grid needs at least one column and one row, not '0x3'\n")
        assert not (tmp_path / "sheet.png").exists() and not (tmp_path / "sheet-1.png").exists()


def test_a_video_file_is_refused_in_words_saying_stills_on_a_video_moved_to_video_tools(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"not really a video")
    for flags in (["--at", "1"], ["--every", "2"], ["--changes"], ["--sheet", str(tmp_path / "s.png")]):
        code, out, err = run("stills", video, *flags, "--out", tmp_path / "stills")
        assert (code, out, err) == (2, "", "stills: stills on a video file has moved to video-tools; "
                                           "here stills takes a video's script.md\n")
    assert sorted(os.listdir(tmp_path)) == ["clip.mp4"]
