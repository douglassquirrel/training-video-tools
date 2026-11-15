"""thumbnail (PLAN.md item 32): a branded 1280x720 PNG from the script, its brand kit and one frame."""

import hashlib
import os
import re
import subprocess
import sys

import pytest
from PIL import Image, ImageChops

from tests.tier2.conftest import REPO, clean_env, cropped, narrated, run, run_program

TITLE = "Title: 2 lines at 96 px (capitals {cap} px): Folding a / Paper Boat"
PICTURE = (646, 199, 646 + 560, 199 + 322)       # the picture inside the card: 10 px in from (636, 189)
LEFT = (0, 150, 588, 720)                        # the left block, below the mark
BACKGROUND = (0xF7, 0xF3, 0xEA)
ACCENT_DARK = (0x15, 0x50, 0x6A)


@pytest.fixture
def prepared(example):
    cropped(example)
    narrated(example)
    os.makedirs(os.path.join(os.path.dirname(example), "out"))
    return example


def default_path(example):
    return os.path.join(os.path.dirname(example), "out", "Folding a Paper Boat thumbnail.png")


def edit(example, old, new):
    text = open(example, encoding="utf-8").read()
    assert old in text
    open(example, "w", encoding="utf-8").write(text.replace(old, new, 1))


def setting(example, row):
    edit(example, "| scene-code | scenes/ | |\n", f"| scene-code | scenes/ | |\n{row}\n")


def capitals(out):
    m = re.match(r"Title: \d+ lines? at \d+ px \(capitals (\d+) px\)", out)
    assert m, out
    return int(m.group(1))


def test_help_shows_every_flag():
    code, out, err = run_program("thumbnail", "--help")
    assert code == 0 and " ".join(out.split()).startswith(
        "usage: thumbnail [-h] [--at SCENE:SECONDS] [--out FILE.png] [--replace] [--dry-run] [--elements DIR] "
        "[--renderer PATH] SCRIPT")


def test_it_writes_a_1280x720_rgb_png_beside_the_output_and_prints_what_it_drew(prepared):
    code, out, err = run_program("thumbnail", prepared, "--at", "A:1.5")
    assert (code, err) == (0, "")
    path = default_path(prepared)
    data = open(path, "rb").read()
    im = Image.open(path)
    assert (im.format, im.size, im.mode) == ("PNG", (1280, 720), "RGB")
    assert len(data) < 2_000_000
    assert capitals(out) >= 40
    assert out.splitlines() == [TITLE.format(cap=capitals(out)), "Eyebrow: THE PAPERBOAT METHOD",
                                "Picture: scene A at 1.500 s (of 8.700 s)",
                                f"Wrote {path}: {len(data)} bytes, SHA-256 {hashlib.sha256(data).hexdigest()}"]
    assert im.getpixel((20, 700)) == BACKGROUND                        # the kit's background, plain
    assert im.getpixel((636 + 5, 189 + 5)) == (255, 255, 255)          # the card's surface, inside its border


def test_the_same_inputs_give_the_same_bytes(prepared, tmp_path):
    for name in ("one.png", "two.png"):
        code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--out", tmp_path / name)
        assert code == 0, err
    assert (tmp_path / "one.png").read_bytes() == (tmp_path / "two.png").read_bytes()


FRAME_ALONE = """
import sys
sys.path.insert(0, {repo!r})
import cairo
from PIL import Image
from videotools import frame, stills, thumbnail
video = frame.Video({script!r})
scene = video.scene({key!r})
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
frame.draw_frame(cairo.Context(surface), video, scene, video.timeline(scene), {t!r})
surface.flush()
im = stills.to_image(surface).crop({area!r})
im.resize((560, 322), Image.LANCZOS, box=thumbnail.cover_box(im.width, im.height, 560, 322)).save({out!r})
"""


@pytest.mark.parametrize("key, t, area", [("A", 1.5, (40, 118, 40 + 1422, 118 + 818)),     # a step: its animation area
                                          ("title", 3.0, (0, 0, 1920, 1080))])             # a card: the whole frame
def test_the_picture_is_stills_frame_cut_scaled_and_cropped_into_the_card(prepared, tmp_path, key, t, area):
    path = tmp_path / "thumb.png"
    code, out, err = run("thumbnail", prepared, "--at", f"{key}:{t}", "--out", path)
    assert code == 0, err
    # Drawn alone in a fresh process, as test_stills does (fontconfig fixes a process's fonts at its first text call).
    alone = tmp_path / "alone.png"
    program = FRAME_ALONE.format(repo=REPO, script=prepared, key=key, t=t, area=area, out=str(alone))
    subprocess.run([sys.executable, "-c", program], check=True, capture_output=True,
                   env=clean_env(PYTHONDONTWRITEBYTECODE="1"))
    card = Image.open(path).convert("RGB").crop(PICTURE)
    assert ImageChops.difference(card, Image.open(alone).convert("RGB")).getbbox() is None


def test_the_script_setting_gives_the_moment_and_at_wins_over_it(prepared, tmp_path):
    setting(prepared, "| thumbnail-at | B:3.5 | |")
    code, out, err = run("thumbnail", prepared, "--out", tmp_path / "one.png")
    assert code == 0 and out.splitlines()[2] == "Picture: scene B at 3.500 s (of 7.900 s)"
    code, out, err = run("thumbnail", prepared, "--at", "C:-1", "--out", tmp_path / "two.png")
    assert code == 0 and out.splitlines()[2] == "Picture: scene C at 7.900 s (of 8.900 s)"


def test_no_moment_a_malformed_one_an_unknown_scene_and_a_time_outside_the_scene_are_refused(prepared):
    for args, message in [((), "give --at SCENE:SECONDS, or set thumbnail-at in the script's Settings"),
                          (("--at", "A"), "'A' is not SCENE:SECONDS"),
                          (("--at", "Z:1"), "no scene 'Z' in the script (scenes: title, A, B, B2, C, R, end)"),
                          (("--at", "A:9.0"), "A:9.0 is past the end of scene A (8.700 s)"),
                          (("--at", "A:-9.0"), "A:-9.0 is past the start of scene A (8.700 s)")]:
        code, out, err = run("thumbnail", prepared, *args)
        assert (code, out, err) == (2, "", f"thumbnail: {message}\n"), args
    assert os.listdir(os.path.dirname(default_path(prepared))) == []


def test_a_bad_thumbnail_at_in_the_script_is_refused_as_a_problem_with_the_script(prepared):
    setting(prepared, "| thumbnail-at | Z:1 | |")
    code, out, err = run("thumbnail", prepared)
    assert (code, out) == (3, "")
    assert re.fullmatch(f"thumbnail: {re.escape(prepared)}: 1 problem:\n  - line \\d+: Settings: 'thumbnail-at' names "
                        "no scene 'Z' \\(scenes: title, A, B, B2, C, R, end\\)\n", err), err


def test_a_title_too_long_for_three_readable_lines_is_refused_and_thumbnail_title_then_works(prepared):
    long = "Folding a Paper Boat from One Sheet of Paper, with Every Mistake You Could Make Along the Way"
    edit(prepared, "| title | Folding a Paper Boat | |", f"| title | {long} | |")
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5")
    assert (code, out) == (3, "")
    assert err == (f"thumbnail: the title '{long}' does not fit in three lines with capitals at least 40 px tall; "
                   "set a shorter thumbnail-title in the script's Settings\n")
    setting(prepared, "| thumbnail-title | “Café” Boats, Folded | |")
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--out", os.path.join(os.path.dirname(prepared), "t.png"))
    assert code == 0, err
    assert re.match(r"Title: \d lines? at \d+ px \(capitals \d+ px\): “Café”", out), out


def ink_box(path):
    """The box of everything but the background in the left block, below the mark."""
    im = Image.open(path).convert("RGB").crop(LEFT)
    return ImageChops.difference(im, Image.new("RGB", im.size, BACKGROUND)).getbbox()


def accent_dark_pixels(path):
    im = Image.open(path).convert("RGB").crop(LEFT)
    return dict((c, n) for n, c in im.getcolors(1 << 20)).get(ACCENT_DARK, 0)


def test_the_eyebrow_is_accent_dark_and_without_it_the_block_is_still_centred(prepared, tmp_path):
    with_it = tmp_path / "with.png"
    assert run("thumbnail", prepared, "--at", "A:1.5", "--out", with_it)[0] == 0
    edit(prepared, "| eyebrow | THE PAPERBOAT METHOD | |\n", "")
    without = tmp_path / "without.png"
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--out", without)
    assert code == 0 and out.splitlines()[1] == "Eyebrow: none"
    assert accent_dark_pixels(with_it) > 0 and accent_dark_pixels(without) == 0   # 20 px: under 24, accent-dark
    for path in (with_it, without):
        top, bottom = ink_box(path)[1] + LEFT[1], ink_box(path)[3] + LEFT[1]
        assert abs((top + bottom) / 2 - 360) <= 12, (path, top, bottom)
    assert ink_box(without)[1] > ink_box(with_it)[1]               # the title's block starts lower: nothing left blank


def test_a_moment_inside_a_fade_is_drawn_with_a_warning(prepared, tmp_path):
    code, out, err = run("thumbnail", prepared, "--at", "A:0.2", "--out", tmp_path / "t.png")
    assert code == 0
    assert err == "thumbnail: scene A at 0.200 s is inside its fade-in (the first 0.45 s): the picture is partly faded\n"


def test_without_narration_the_times_are_estimated_with_stills_warning(example, tmp_path):
    cropped(example)
    code, out, err = run("thumbnail", example, "--at", "A:1.5", "--out", tmp_path / "t.png")
    assert code == 0
    assert err == "thumbnail: scene A has no narration clips (cues 1, 2); times are estimated at 2.6 words a second\n"


def test_an_existing_file_is_refused_untouched_and_replace_replaces_it(prepared):
    path = default_path(prepared)
    open(path, "w").write("keep")
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5")
    assert (code, out) == (3, "")
    assert err == f"thumbnail: {path} already exists; give --replace to replace it, or another --out\n"
    assert open(path).read() == "keep"
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--replace")
    assert code == 0, err
    assert Image.open(path).size == (1280, 720)
    assert sorted(os.listdir(os.path.dirname(path))) == ["Folding a Paper Boat thumbnail.png"]


def test_dry_run_checks_everything_prints_the_plan_and_writes_nothing(prepared):
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--dry-run")
    assert (code, err) == (0, "")
    assert out.splitlines() == [TITLE.format(cap=capitals(out)), "Eyebrow: THE PAPERBOAT METHOD",
                                "Picture: scene A at 1.500 s (of 8.700 s)",
                                f"Would write: {default_path(prepared)} (--dry-run: nothing written)"]
    assert os.listdir(os.path.dirname(default_path(prepared))) == []
    code, out, err = run("thumbnail", prepared, "--at", "Z:1", "--dry-run")
    assert code == 2                                                      # and it still refuses


def test_a_missing_folder_is_refused(example, tmp_path):
    cropped(example)
    code, out, err = run("thumbnail", example, "--at", "A:1.5")
    folder = os.path.dirname(default_path(example))
    assert (code, out, err) == (3, "", f"thumbnail: no folder {folder}; make it, or give --out\n")


def test_a_folder_it_cannot_write_in_is_a_useful_error_and_leaves_nothing(prepared, tmp_path):
    folder = tmp_path / "locked"
    folder.mkdir()
    folder.chmod(0o555)
    try:
        code, out, err = run("thumbnail", prepared, "--at", "A:1.5", "--out", folder / "t.png")
        assert code == 3                         # stdout has the lines it checked; the failure is on stderr
        assert err == f"thumbnail: cannot write {folder / 't.png'}: Permission denied\n"
        assert os.listdir(folder) == []
    finally:
        folder.chmod(0o755)


def test_a_brand_kit_missing_a_colour_is_refused_naming_it(prepared):
    kit = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(prepared))), "brands", "paperboat", "BRAND.md")
    text = open(kit, encoding="utf-8").read()
    open(kit, "w", encoding="utf-8").write(text.replace("| surface |", "| x-surface |", 1))
    code, out, err = run("thumbnail", prepared, "--at", "A:1.5")
    assert (code, out) == (3, "")
    assert err == f"thumbnail: {os.path.dirname(kit)}: Colours: 'surface' is missing\n"
    assert os.listdir(os.path.dirname(default_path(prepared))) == []
