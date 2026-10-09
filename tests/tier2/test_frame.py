"""videotools.frame: whole frames of the example drawn, checked by pixels and stored images.

Stored images (tests/tier2/frames/*.png) are the frames reduced to 192x108; a drawn frame must
match within a tolerance, since text rendering differs a little between platforms.
"""

import os
import subprocess
import sys

import cairo
import pytest
from PIL import Image, ImageChops, ImageStat

from tests.tier2.conftest import REPO, clean_env, cropped, narrated
from videotools import cli, frame

FRAMES = os.path.join(os.path.dirname(__file__), "frames")
TOLERANCE = 6.0          # mean absolute difference per channel, 0–255, at 192x108


@pytest.fixture
def video(example):
    """The example copy with insets cut and narration faked, loaded."""
    cropped(example)
    narrated(example)
    return frame.Video(example)


def rendered(video, key, t):
    scene = video.scene(key)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surface)
    frame.draw_frame(ctx, video, scene, video.timeline(scene), t)
    surface.flush()
    return surface


def pixel(surface, x, y):
    data, stride = surface.get_data(), surface.get_stride()
    i = y * stride + x * 4
    return data[i + 2], data[i + 1], data[i]


def as_image(surface):
    return Image.frombuffer("RGBA", (surface.get_width(), surface.get_height()), bytes(surface.get_data()),
                            "raw", "BGRA", surface.get_stride(), 1).convert("RGB")


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def test_the_video_loads_the_script_brand_fonts_insets_and_timings(video):
    assert video.data["title"] == "Folding a Paper Boat"
    assert video.brand["identity"]["name"] == "Paperboat Press"
    assert sorted(video.insets) == ["A", "B", "C", "full", "title-page"]
    assert video.timeline(video.scene("A")).estimated == []
    assert video.scene("B2")["props"]["code"] == "strip_fold"


def test_a_step_scene_has_background_header_roundel_rule_column_and_caption_band(video):
    s = rendered(video, "A", 1.0)
    assert pixel(s, 20, 20) == hex_rgb("#F7F3EA")              # background
    assert pixel(s, 60, 62) == hex_rgb("#1F6F8B")              # the step roundel, accent
    assert pixel(s, 500, 112) == hex_rgb("#DAD2C4")            # the header rule
    assert pixel(s, 100, 949) == hex_rgb("#1F6F8B")            # the caption rule
    assert pixel(s, 100, 1060) == hex_rgb("#2B2B2B")           # the caption band
    assert pixel(s, 1500, 905) == hex_rgb("#1F6F8B")           # the brand mark at the column's foot


def test_the_tracker_shows_done_now_and_to_come(video):
    s = rendered(video, "B2", 1.0)       # B2 shares B's place: A done (ink), B now (accent), C to come (outline)
    row = [pixel(s, x, 62) for x in range(1500, 1870)]
    assert hex_rgb("#2B2B2B") in row and hex_rgb("#1F6F8B") in row
    assert hex_rgb("#F7F3EA") in row[-30:] or hex_rgb("#6B6560") in row[-30:]


def test_the_caption_is_the_speaking_cue_and_the_mistake_cue_gets_its_tag(video):
    before = rendered(video, "A", 1.0)
    during = rendered(video, "A", 5.0)       # cue 2 (the mistake) starts at 3.7 s
    assert pixel(before, 80, 1014) == hex_rgb("#2B2B2B")
    assert pixel(during, 80, 1014) == hex_rgb("#A33A2E")       # the COMMON MISTAKE tag
    assert as_image(before).crop((0, 948, 1920, 1080)).tobytes() != as_image(during).crop((0, 948, 1920, 1080)).tobytes()


def test_the_mistake_panels_cover_the_area_during_the_mistake_cue_only(video):
    during = rendered(video, "A", 5.0)
    assert pixel(during, 300, 150) == hex_rgb("#A33A2E")       # left panel's heading, mistake colour
    assert pixel(during, 1100, 150) == hex_rgb("#3E7D4F")      # right panel's heading, correct colour
    before = rendered(video, "A", 1.0)
    assert pixel(before, 300, 150) != hex_rgb("#A33A2E")


def test_the_title_and_end_cards_have_no_header_or_column(video):
    title = rendered(video, "title", 2.0)
    assert pixel(title, 60, 62) != hex_rgb("#1F6F8B")
    assert pixel(title, 500, 112) == hex_rgb("#F7F3EA")
    assert pixel(title, 100, 1060) == hex_rgb("#2B2B2B")       # the title card still has captions
    end = rendered(video, "end", 1.0)
    assert pixel(end, 100, 1060) == hex_rgb("#F7F3EA")         # the end card has no caption band


def test_every_scene_fades_in_from_the_background_and_out_to_it(video):
    assert pixel(rendered(video, "A", 0.0), 100, 1060) == hex_rgb("#F7F3EA")
    tl = video.timeline(video.scene("A"))
    assert pixel(rendered(video, "A", tl.total), 100, 1060) == hex_rgb("#F7F3EA")


def test_a_label_the_script_does_not_list_stops_the_frame(video, tmp_path):
    path = os.path.join(os.path.dirname(video.script_path), "scenes", "fold_in_half.py")
    text = open(path).read().replace('"crease"', '"creese"')
    open(path, "w").write(text)
    with pytest.raises(cli.Failure) as e:
        rendered(video, "A", 1.0)
    assert "'creese', which is not in the script's On screen list" in str(e.value)


def test_missing_insets_are_a_useful_error(example):
    narrated(example)
    with pytest.raises(cli.Failure) as e:
        frame.Video(example)
    assert str(e.value) == (f"no {os.path.join(os.path.dirname(example), 'work', 'insets', 'A.png')} "
                            "(inset 'A'); run crop-insets first")


@pytest.mark.parametrize("key,t", [("title", 2.0), ("A", 1.5), ("A", 5.0), ("B", 3.5), ("B2", 3.0), ("C", 6.0), ("R", 5.0), ("end", 1.5)])
def test_frames_match_the_stored_images_within_the_tolerance(video, key, t):
    drawn = as_image(rendered(video, key, t)).resize((192, 108), Image.LANCZOS)
    path = os.path.join(FRAMES, f"{key}_{t:.1f}.png")
    assert os.path.exists(path), f"no stored image {path}; see tests/tier2/frames/README.md"
    stored = Image.open(path).convert("RGB")
    diff = ImageStat.Stat(ImageChops.difference(drawn, stored)).mean
    assert max(diff) < TOLERANCE, f"{key} at {t} s differs from the stored image by {diff}"


FRESH_FRAME = """
import sys
sys.path.insert(0, {repo!r})
import cairo
from PIL import Image
from videotools import fonts, frame
if {without_fonts!r}:
    fonts.load = lambda kit, work, platform=None: []       # the brand's fonts never reach cairo
video = frame.Video({script!r})
scene = video.scene("A")
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
frame.draw_frame(cairo.Context(s), video, scene, video.timeline(scene), 5.0)
s.flush()
Image.frombuffer("RGBA", (1920, 1080), bytes(s.get_data()), "raw", "BGRA", s.get_stride(), 1).convert("RGB").save({out!r})
"""


def fresh_frame(example, out, without_fonts):
    """Frame A at 5.0 s drawn in a new process, as a command draws it, with or without the fonts."""
    code = FRESH_FRAME.format(repo=REPO, script=example, out=str(out), without_fonts=without_fonts)
    # clean_env: without the FONTCONFIG_FILE an earlier in-process frame set (Linux), or the child
    # "without fonts" would find the brand's fonts through it (request 5, item 1).
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True,
                   env=clean_env(PYTHONDONTWRITEBYTECODE="1"))
    return Image.open(out).convert("RGB")


def test_a_frame_drawn_in_a_fresh_process_uses_the_brands_fonts(example, tmp_path):
    """The stored-image tolerance above does not see fonts (with fallback fonts, six of the eight
    frames differ by under 2 of 6: DIARY.md, request 3 item 3), so this pins them: the text in a
    frame changes when the brand's fonts are not loaded, in a process that drew nothing before."""
    cropped(example)
    narrated(example)
    with_fonts = fresh_frame(example, tmp_path / "with.png", without_fonts=False)
    without = fresh_frame(example, tmp_path / "without.png", without_fonts=True)
    changed = ImageChops.difference(with_fonts, without).convert("L").point(lambda v: 255 if v else 0)
    pixels = changed.histogram()[255]
    print(f"pixels changed without the brand's fonts: {pixels}")
    assert pixels > 20_000, f"only {pixels} pixels change without the brand's fonts"   # 58,956 on macOS: text all over
    # And a second fresh process with the fonts draws the same frame exactly: the route is deterministic.
    again = fresh_frame(example, tmp_path / "again.png", without_fonts=False)
    assert ImageChops.difference(with_fonts, again).getbbox() is None


def with_heading(example, key, heading):
    """The example copy with a side-panel-heading on scene `key`."""
    text = open(example, encoding="utf-8").read()
    marker = f"## Scene {key}:"
    head, sep, rest = text.partition(marker)
    rest = rest.replace("| code |", f"| side-panel-heading | {heading} |\n| code |", 1)
    open(example, "w", encoding="utf-8").write(head + sep + rest)


def first_row_of(surface, colour, x, y0=130, y1=900):
    return next((y for y in range(y0, y1) if pixel(surface, x, y) == hex_rgb(colour)), None)


def test_a_side_panel_heading_sits_above_a_checklist_and_moves_its_rows_down(video):
    cx = video.layout.column[0]
    plain = rendered(video, "R", 5.0)                               # R: checklist 2, both ticks shown by 5 s
    with_heading(video.script_path, "R", "CHECK BEFORE YOU LEAVE IT")
    headed = rendered(frame.Video(video.script_path), "R", 5.0)
    badge_x = cx + 22
    before, after = first_row_of(plain, "#3E7D4F", badge_x), first_row_of(headed, "#3E7D4F", badge_x)
    assert before is not None and after == before + 38                # the ticks move down for the heading
    assert first_row_of(headed, "#6B6560", cx + 2, before - 60, before) is not None   # muted heading text above


def test_a_side_panel_heading_replaces_key_points_without_moving_the_list(video):
    cx = video.layout.column[0]
    plain = rendered(video, "A", 1.0)                               # A: key-points by default
    with_heading(video.script_path, "A", "TIPS")
    headed = rendered(frame.Video(video.script_path), "A", 1.0)
    square_x = cx + 6
    assert first_row_of(plain, "#1F6F8B", square_x, 300) == first_row_of(headed, "#1F6F8B", square_x, 300)
    assert as_image(plain).tobytes() != as_image(headed).tobytes()   # KEY POINTS became TIPS
