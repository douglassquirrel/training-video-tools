"""videotools.perform: a described scene drawn frame by frame (PLAN.md item 15): members shown,
hidden and moved over their eased spans, the pieces through the frame's methods, the library's
elements through el.draw, panels in panel pixels; and frame.Video refusing a described scene it
cannot draw."""

import os

import pytest

from tests.tier2.conftest import STUBS, cropped, narrated, run
from tests.tier2.test_frame import hex_rgb, pixel, rendered
from videotools import cli, frame

INVENTED = os.path.join(STUBS, "video-elements")
ACCENT = hex_rgb("#1F6F8B")          # the paperboat brand's accent: what the stub library fills with

# Scene A of the example, described (its code removed). Area pixels: the area is at 40, 118.
CAST = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| pot1 | pot | 100 100 | 200 | state=plain | frame rect 140 218, 200 x 200 |
| sign | pill | 400 100 | | text=crease size=22 fill=accent | |
| sheet | table | 100 400 | 300x100 | rows=assets/sample.csv | frame rect 140 518 |
| corner | badge | pot1.top-right + 30 0 | | ok=yes r=20 | follows pot1 |

### Moves

- cue 1: show pot1, corner
- cue 1, 1.0 s: show sign
- cue 1, 0.5 s: show sheet
- cue 1, 2.0–2.5 s: move pot1 to 600 100
- cue 1, 2.6–2.9 s: hide pot1, corner

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | pot | 100 100 | 100 | | panel body at 52 196: frame rect 152 296 |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| right | pill | 100 100 | | text="edge fold" fill=correct | |

"""


def describe(example, cast=CAST):
    text = open(example, encoding="utf-8").read()
    marker = "## Scene B: Corners to the centre"
    text = text.replace(marker, cast + marker).replace("| code | fold_in_half | |\n", "")
    open(example, "w", encoding="utf-8").write(text)
    assets = os.path.join(os.path.dirname(example), "assets")
    os.makedirs(assets, exist_ok=True)
    with open(os.path.join(assets, "sample.csv"), "w", encoding="utf-8") as f:
        f.write("Rep,Commission\nA,1\nB,2\nC,3\n")
    return example


@pytest.fixture
def video(example):
    cropped(example)
    narrated(example)                       # cue 1 at 0.7 s for 3.0 s (its min), cue 2 (the mistake) at 3.7 s
    return frame.Video(describe(example), INVENTED, None)


def test_a_member_is_absent_before_its_show_fades_in_over_the_span_and_is_there_after(video):
    assert pixel(rendered(video, "A", 0.3), 240, 318) != ACCENT
    assert pixel(rendered(video, "A", 1.0), 240, 318) not in (ACCENT, hex_rgb("#F7F3EA"))   # half way
    assert pixel(rendered(video, "A", 1.4), 240, 318) == ACCENT
    assert pixel(rendered(video, "A", 2.0), 290, 568) == ACCENT     # the table, 300 x 100, shown 0.5–1.1 s in


def test_a_move_glides_the_member_to_its_new_place_and_a_hide_removes_it(video):
    s = rendered(video, "A", 3.3)                                   # after the move (2.0–2.5 s into cue 1)
    assert pixel(s, 240, 318) != ACCENT and pixel(s, 740, 318) == ACCENT
    s = rendered(video, "A", 3.65)                                  # after the hide (2.6–2.9 s)
    assert pixel(s, 740, 318) != ACCENT


def test_a_member_placed_by_another_follows_it(video):
    # corner: a ✓ badge (correct, #3E7D4F in the paperboat kit) 30 px right of pot1's top-right corner
    assert pixel(rendered(video, "A", 1.4), 140 + 200 + 30, 218 - 15) == hex_rgb("#3E7D4F")   # above the ✓
    assert pixel(rendered(video, "A", 3.3), 640 + 200 + 30, 218 - 15) == hex_rgb("#3E7D4F")


def test_the_panels_casts_draw_in_panel_pixels_while_the_curtain_is_up(video):
    s = rendered(video, "A", 4.7)                                   # cue 2 + 1.0 s: covered
    assert pixel(s, 202, 346) == ACCENT                             # 'wrong' in the Mistake panel
    assert video.library.draws[-1]["name"] in ("pot", "table")


def test_the_library_is_asked_to_draw_with_the_rect_state_params_and_alpha(video):
    rendered(video, "A", 1.4)
    pot = next(d for d in video.library.draws if d["name"] == "pot" and d["rect"][0] == 140)
    assert pot["rect"] == (140.0, 218.0, 200.0, 200.0) and pot["state"] == "plain" and pot["alpha"] == 1.0
    table = next(d for d in video.library.draws if d["name"] == "table")
    assert table["params"]["rows"] == [["Rep", "Commission"], ["A", "1"], ["B", "2"], ["C", "3"]]
    assert table["rect"] == (140.0, 518.0, 300.0, 100.0)


def test_a_described_scene_that_needs_the_library_is_refused_without_one(example, monkeypatch):
    monkeypatch.setenv("VIDEO_TOOLS_CONF", "/nowhere/video-tools.conf")
    cropped(example)
    narrated(example)
    with pytest.raises(cli.Failure) as e:
        frame.Video(describe(example))
    assert str(e.value).startswith("VIDEO_ELEMENTS_DIR is not set in /nowhere/video-tools.conf and no --elements")


def test_a_described_scene_with_problems_is_refused_listing_them(example):
    cropped(example)
    narrated(example)
    bad = CAST.replace("text=crease", "text=creases").replace("- cue 1, 0.5 s: show sheet\n", "")
    with pytest.raises(cli.Failure) as e:
        frame.Video(describe(example, bad), INVENTED, None)
    assert str(e.value) == (
        "the script's choreography has 2 problems:\n"
        "  - line 128: scene A, cast: 'sign' draws 'creases', which is not in the script's On screen list "
        "(top edge to bottom edge, crease, diagonal fold, edge fold)\n"
        "  - line 129: scene A, cast: 'sheet' is never shown")           # the code line is gone: one line up
    assert e.value.code == cli.REFUSED


def test_stills_and_render_take_the_library_from_the_flag_and_refuse_without_it(example, tmp_path):
    cropped(example)
    narrated(example)
    script = describe(example)
    code, out, err = run("stills", script, "A:1.4", "--out", tmp_path / "s.png", "--elements", INVENTED)
    assert (code, err) == (0, "")
    code, out, err = run("render", script, "--scenes", "A", "--dry-run", "--elements", INVENTED)
    assert (code, err) == (0, "")
    code, out, err = run("render", script, "--scenes", "A", "--dry-run", env={"VIDEO_TOOLS_CONF": "/nowhere/c"})
    assert code == 3 and err.startswith("render: VIDEO_ELEMENTS_DIR is not set in /nowhere/c and no --elements")
