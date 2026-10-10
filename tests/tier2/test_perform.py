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


# ---- increment 7: parameters and states change in moves

ANIMATED = CAST.replace("- cue 1, 2.6–2.9 s: hide pot1, corner\n", """- cue 1, 2.6–2.9 s: hide pot1, corner
- cue 1, 1.0–2.0 s: sheet.rows-shown 0 → 3
- cue 1, 1.0–2.0 s: sheet.highlight.2 0 → 1
- cue 1, 1.0 s: sheet.highlight-colour.2 correct
- cue 1, 1.0–1.5 s: pot1 plain → cracked
- cue 1, 1.0–2.0 s: corner.r 40
""").replace("| sheet | table | 100 400 | 300x100 | rows=assets/sample.csv | frame rect 140 518 |",
             "| sheet | table | 100 400 | 300x100 | rows=assets/sample.csv rows-shown=0 striped=yes | frame rect 140 518 |")


@pytest.fixture
def animated(example):
    cropped(example)
    narrated(example)
    return frame.Video(describe(example, ANIMATED), INVENTED, None)


def _draw(video, name, t):
    video.library.draws.clear()
    s = rendered(video, "A", t)
    return s, next(d for d in video.library.draws if d["name"] == name)


def test_a_parameter_animates_over_its_span_eased_and_a_whole_number_stays_whole(animated):
    _s, before = _draw(animated, "table", 1.4)             # the span is 1.7–2.7 s
    assert before["params"]["rows-shown"] == 0 and "highlight.2" not in before["params"]   # the element's default
    assert before["params"]["striped"] is True
    _s, mid = _draw(animated, "table", 2.2)                # half way: eased progress 0.5
    assert mid["params"]["highlight.2"] == pytest.approx(0.5) and mid["params"]["rows-shown"] == 2
    _s, after = _draw(animated, "table", 3.0)
    assert after["params"]["highlight.2"] == 1.0 and after["params"]["rows-shown"] == 3


def test_a_set_takes_effect_at_its_start_for_words_and_eases_for_numbers(animated):
    _s, before = _draw(animated, "table", 1.4)
    assert "highlight-colour.2" not in before["params"]
    _s, after = _draw(animated, "table", 1.8)
    assert after["params"]["highlight-colour.2"] == "correct"
    s = rendered(animated, "A", 1.4)                       # corner: a badge of r 20, growing to 40 over 1.7–2.7 s
    assert pixel(s, 370 + 30, 218) != hex_rgb("#3E7D4F")
    s = rendered(animated, "A", 2.6)                       # r about 39, before pot1 starts to move at 2.7 s
    assert pixel(s, 370 + 30, 218) == hex_rgb("#3E7D4F")


def test_a_state_change_is_handed_to_the_element_part_way_as_from_to_and_progress(animated):
    assert _draw(animated, "pot", 1.4)[1]["state"] == "plain"                       # the span is 1.7–2.2 s
    assert _draw(animated, "pot", 1.95)[1]["state"] == ("plain", "cracked", pytest.approx(0.5))
    assert _draw(animated, "pot", 2.5)[1]["state"] == "cracked"


PIECES = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| pot1 | pot | centre | | | fitted into the middle of the area |
| word | text | 100 100 | | text=crease size=30 | |
| hand1 | hand | 100 300 | | angle=1.2 scale=0.8 mirror=yes label=B | |
| note | callout | 400 600 | | text="edge fold" target=pot1.centre | |
| line | arrow | 100 500 | | from=word.bottom-left to=hand1.top-left width=4 | |

### Moves

- cue 1: show pot1, word, hand1, note, line

"""


def test_the_other_pieces_draw_and_a_region_fits_the_element_inside_it(example):
    cropped(example)
    narrated(example)
    text = open(example, encoding="utf-8").read().replace("- edge fold\n", "- edge fold\n- B\n")
    open(example, "w", encoding="utf-8").write(text)
    video = frame.Video(describe(example, PIECES), INVENTED, None)
    _s, pot = _draw(video, "pot", 2.0)
    x, y, w, h = pot["rect"]                       # the centre region is 711 x 409 at 395.5, 322.5: a 24 x 24 pot fits to 409
    assert (round(w), round(h)) == (409, 409) and (round(x), round(y)) == (546, 322)


# ---- increment 8: computed anchors, fixed anchors, and the pieces' real extents

ANCHORED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| rim-mark | badge | pot1.rim + 0 -60 | | ok=yes r=20 | a fixed anchor, before its member: 12 4 of 24 24 in 200 px |
| pot1 | pot | 100 100 | 200 | | frame rect 140 218, 200 x 200: rim at 240, 251 |
| sign | pill | 400 100 | | text=crease size=22 fill=accent | at 440, 218 |
| after-sign | pot | sign.bottom-right + 10 0 | 20 | | the pill's real extent, once drawn |
| word | text | 100 100 | | text=crease size=30 | baseline at 140, 218 |
| after-word | pot | word.top-right | 20 | | the text's real extent, once drawn |
| sheet | table | 100 400 | 300x100 | rows=assets/sample.csv | frame rect 140 518: the stub's row.2 at 440, 558 |
| row-mark | badge | sheet.row.2 | | ok=yes r=20 | a computed anchor, after its member |

### Moves

- cue 1: show rim-mark, pot1, sign, after-sign, word, after-word, sheet, row-mark

"""


@pytest.fixture
def anchored(example):
    cropped(example)
    narrated(example)
    return frame.Video(describe(example, ANCHORED), INVENTED, None)


def test_a_fixed_anchor_places_a_member_before_its_element_is_drawn_and_a_computed_one_after(anchored):
    s = rendered(anchored, "A", 2.0)
    assert pixel(s, 240, 191 - 15) == hex_rgb("#3E7D4F")      # rim-mark: 60 above the pot's rim
    assert pixel(s, 440, 558 - 15) == hex_rgb("#3E7D4F")      # row-mark: at the stub's row.2


def test_a_pill_and_a_text_have_their_drawn_extent_for_the_members_placed_by_them(anchored):
    rendered(anchored, "A", 2.0)
    pots = {round(d["rect"][0]): d["rect"] for d in anchored.library.draws if d["name"] == "pot"}
    after_sign = next(r for x, r in pots.items() if 480 < x < 700)          # right of the pill, 10 px on
    assert after_sign[1] > 218                                                # at the pill's bottom edge
    after_word = next(r for x, r in pots.items() if 190 < x < 480)          # the text "crease" is wider than 50 px
    assert after_word[1] < 218                                                # at the text's top, above its baseline


# ---- increment 9: the curtain for free

def test_stills_cue_changes_is_quiet_on_a_described_scene_whose_picture_fades_under_the_panels(example, tmp_path):
    cropped(example)
    narrated(example)
    # pot1 is shown at cue 1 and never named again: it fades under the panels, so nothing vanishes as they lift
    cast = CAST.replace("- cue 1, 2.6–2.9 s: hide pot1, corner\n", "")
    script = describe(example, cast)
    code, out, err = run("stills", script, "--cue-changes", "--scenes", "A", "--out", tmp_path / "cues.png",
                         "--elements", INVENTED)
    assert (code, err) == (0, "")
