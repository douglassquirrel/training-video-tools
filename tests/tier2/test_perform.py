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

def three_cues(example):
    """The example copy with scene A given a third cue after its mistake (and a 1 s timing for it),
    so the panels lift at 7.7 s; described with pot1 shown at cue 1 and never named again."""
    import json
    cropped(example)
    narrated(example)
    text = open(example, encoding="utf-8").read().replace(
        "   - added: the consequence (no hull) is our inference; the figure shows only the edge fold.\n",
        "   - added: the consequence (no hull) is our inference; the figure shows only the edge fold.\n3. Then crease.\n")
    open(example, "w", encoding="utf-8").write(text)
    timing = os.path.join(os.path.dirname(example), "work", "narration", "timing.json")
    data = json.load(open(timing, encoding="utf-8"))
    data["scenes"]["A"].append(1.0)
    json.dump(data, open(timing, "w", encoding="utf-8"))
    return describe(example, CAST.replace("- cue 1, 2.6–2.9 s: hide pot1, corner\n", ""))


def test_a_member_not_named_after_the_mistake_is_gone_when_the_panels_lift(example):
    video = frame.Video(three_cues(example), INVENTED, None)
    assert pixel(rendered(video, "A", 3.6), 740, 318) == ACCENT          # just before cue 2: the pot, moved, is there
    assert pixel(rendered(video, "A", 7.9), 740, 318) != ACCENT          # cue 3 + 0.2 s: panels lifted, pot gone


def test_stills_cue_changes_is_quiet_on_a_described_scene_whose_picture_fades_under_the_panels(example, tmp_path):
    script = three_cues(example)
    code, out, err = run("stills", script, "--cue-changes", "--scenes", "A", "--out", tmp_path / "cues.png",
                         "--elements", INVENTED)
    assert (code, err) == (0, "")


# ---- increment 10: a panel's own moves, and a described scene equal to the same scene as a module

PANEL_MOVES = CAST.replace("| wrong | pot | 100 100 | 100 | | panel body at 52 196: frame rect 152 296 |\n",
                           "| wrong | pot | 100 100 | 100 | | panel body at 52 196: frame rect 152 296 |\n\n"
                           "- 1.0–1.4 s: show wrong\n")


def test_a_panel_move_counts_from_the_panels_rise(example):
    cropped(example)
    narrated(example)
    video = frame.Video(describe(example, PANEL_MOVES), INVENTED, None)
    assert pixel(rendered(video, "A", 4.5), 202, 346) != ACCENT          # cue 2 + 0.8 s: covered, before its show
    assert pixel(rendered(video, "A", 5.3), 202, 346) == ACCENT          # cue 2 + 1.6 s: shown


SAME_AS_MODULE = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| pot1 | pot | 100 100 | 200 | | |
| sign | pill | 400 100 | | text=crease size=22 fill=accent | |

### Moves

- cue 1: show pot1
- cue 1, 1.0 s: show sign

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | pot | 100 100 | 100 | | |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| right | pill | 100 100 | | text="edge fold" fill=correct | |

"""

MODULE = '''"""Scene A as a module, drawing exactly what the described scene draws through the stub library."""


def _pot(frame, x, y, w, h, alpha):
    if alpha <= 0:
        return
    frame.ctx.save()
    frame.ctx.rectangle(x, y, w, h)
    frame.ctx.set_source_rgba(*frame.colour("accent"), alpha)
    frame.ctx.fill()
    frame.ctx.restore()


def draw(frame):
    t, tl = frame.t, frame.timeline
    _pot(frame, 140, 218, 200, 200, tl.p(t, 1, 0.0, 0.6))
    b = tl.p(t, 1, 1.0, 1.6)
    if b > 0:
        frame.tag("crease", 440, 218, size=22, fill="accent", alpha=b)


def mistake(frame, rect):
    x, y, w, h = rect
    _pot(frame, x + 100, y + 100, 100, 100, 1.0)


def right_way(frame, rect):
    x, y, w, h = rect
    frame.tag("edge fold", x + 100, y + 100, size=22, fill="correct")
'''


def test_a_described_scene_and_the_same_scene_as_a_module_give_equal_frames(example, tmp_path):
    cropped(example)
    narrated(example)
    original = open(example, encoding="utf-8").read()
    hashes = tmp_path / "described.json"
    describe(example, SAME_AS_MODULE)
    code, out, err = run("frame-hashes", example, "--out", hashes, "--scenes", "A", "--step", "10",
                         "--elements", INVENTED)
    assert (code, err) == (0, ""), err
    open(example, "w", encoding="utf-8").write(original)                       # the coded scene instead
    with open(os.path.join(os.path.dirname(example), "scenes", "fold_in_half.py"), "w", encoding="utf-8") as f:
        f.write(MODULE)
    code, out, err = run("frame-hashes", example, "--compare", hashes, "--scenes", "A", "--step", "10")
    assert (code, err) == (0, ""), out


# ---- a library refusal at draw time is reported in words, never as a traceback

def test_a_library_refusal_while_drawing_is_one_message_in_words(example, tmp_path):
    cropped(example)
    narrated(example)
    script = describe(example, CAST.replace("rows=assets/sample.csv |", "rows=assets/sample.csv explode=yes |"))
    code, out, err = run("stills", script, "A:2.0", "--out", tmp_path / "s.png", "--elements", INVENTED)
    assert code == 3
    assert err == ("stills: scene A: the library could not draw 'sheet' (table): element 'table': its draw failed: "
                   "Failure: no font role 'mono' in the brand kit\n")
    assert not (tmp_path / "s.png").exists()


# ---- item 17 (request 15): offsets where an anchor is read, an arrow that draws on, a blank Where

POINTED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| pot1 | pot | 100 100 | 200 | | frame rect 140 218, 200 x 200: centre 240 318 |
| pot2 | pot | 500 300 | 100 | | frame rect 540 418, 100 x 100: centre 590 468 |
| line | arrow | 100 500 | | from="pot1.centre + 10 0" to="pot2.centre + 0 -5" | |
| note | callout | 400 600 | | text="edge fold" target="pot1.top-right + -20 30" | |

### Moves

- cue 1: show pot1, pot2, line, note

"""


def recorded(monkeypatch):
    """(arrows, targets): every draw.arrow call as (its two ends, its keywords) and every callout's
    target, recorded in place of the drawing."""
    from videotools import draw, scenes
    arrows, targets = [], []
    monkeypatch.setattr(draw, "arrow", lambda ctx, control, colour, **kw: arrows.append((control, kw)))
    monkeypatch.setattr(scenes.Frame, "callout", lambda self, s, target, at, **kw: targets.append(target))
    return arrows, targets


def pointed(example, cast=POINTED):
    cropped(example)
    narrated(example)
    return frame.Video(describe(example, cast), INVENTED, None)


def test_an_arrows_ends_are_its_anchors_plus_their_offsets(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    rendered(pointed(example), "A", 2.0)
    assert arrows[0][0] == [(250.0, 318.0), (590.0, 463.0)]


def test_a_callouts_target_is_its_anchor_plus_the_offset(example, monkeypatch):
    _arrows, targets = recorded(monkeypatch)
    rendered(pointed(example), "A", 2.0)
    assert targets == [(320.0, 248.0)]


GROWING = POINTED.replace('to="pot2.centre + 0 -5" |', 'to="pot2.centre + 0 -5" progress=0 |').replace(
    "- cue 1: show pot1, pot2, line, note\n",
    "- cue 1: show pot1, pot2, line, note\n- cue 1, 1.0–2.0 s: line.progress 0 → 1\n")


def test_an_arrow_draws_on_as_its_progress_is_animated(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    video = pointed(example, GROWING)                       # the span is 1.7–2.7 s into the scene
    for t in (1.4, 2.2, 3.0):
        rendered(video, "A", t)
    assert [kw["progress"] for _ends, kw in arrows] == [0.0, pytest.approx(0.5), 1.0]


def test_an_arrow_with_no_progress_is_drawn_whole(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    rendered(pointed(example), "A", 2.0)
    assert arrows[0][1]["progress"] == 1.0


def test_an_arrow_with_head_no_is_drawn_without_its_head_and_with_one_otherwise(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    headless = POINTED.replace('to="pot2.centre + 0 -5" |', 'to="pot2.centre + 0 -5" head=no |').replace(
        "| note | callout |", '| line2 | arrow | 100 500 | | from=pot1.centre to=pot2.centre head=yes | |\n'
        "| note | callout |").replace("show pot1, pot2, line, note", "show pot1, pot2, line, line2, note")
    rendered(pointed(example, headless), "A", 2.0)
    assert arrows[0][1]["head"] == 0                        # draw.arrow's head is its size in pixels
    assert arrows[1][1].get("head", 20) == 20               # its own default


BOXED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| pot1 | pot | 100 100 | 200 | | frame rect 140 218, 200 x 200: centre 240 318 |
| pot2 | pot | 500 300 | 100 | | frame rect 540 418, 100 x 100: centre 590 468 |
| line | arrow | | | from=pot2.centre to=pot1.centre | from right to left: the box is still its ends' span |
| corner | pot | line.top-left | 20 | | |
| far | pot | line.bottom-right | 20 | | |
| mid | pot | line.centre | 20 | | |

### Moves

- cue 1: show pot1, pot2, line, corner, far, mid

"""


def test_an_arrow_with_a_blank_where_has_the_box_its_two_ends_span(example):
    video = pointed(example, BOXED)
    rendered(video, "A", 2.0)
    small = [d["rect"] for d in video.library.draws if d["rect"][2] == 20.0]
    assert small == [(240.0, 318.0, 20.0, 20.0), (590.0, 468.0, 20.0, 20.0), (415.0, 393.0, 20.0, 20.0)]


SHAPED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wide | pot | 100 100 | 200x80 | | a 24 x 24 element given another shape |
| tall | table | right | 100x300 | rows=assets/sample.csv | a 300 x 200 element; the right half is 711 x 818 at 751, 118 |

### Moves

- cue 1: show wide, tall

"""


def test_a_size_given_as_w_by_h_reaches_the_element_as_its_rect_whatever_its_own_proportions(example):
    video = pointed(example, SHAPED)
    rendered(video, "A", 2.0)
    rects = {d["name"]: d["rect"] for d in video.library.draws}
    assert rects["pot"] == (140.0, 218.0, 200.0, 80.0)
    assert rects["table"] == (751.0 + (711.0 - 100.0) / 2, 118.0 + (818.0 - 300.0) / 2, 100.0, 300.0)


# ---- item 17 (request 15), 3: a blank Size on an element that offers its natural size

NATURAL = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sheet | table | 100 400 | | rows=assets/sample.csv | 4 rows of 2 columns: the stub's natural size is 240 x 120 |
| side | table | right | | rows=assets/sample.csv | the right half is 711 x 818 at 751, 118 |
| corner | pot | sheet.bottom-right | 20 | | follows the size the table was drawn at |

### Moves

- cue 1: show sheet, side, corner

"""


def test_a_blank_size_draws_an_element_that_offers_one_at_its_natural_size(example):
    video = pointed(example, NATURAL)
    rendered(video, "A", 2.0)
    rects = [d["rect"] for d in video.library.draws]
    assert rects[0] == (140.0, 518.0, 240.0, 120.0)                      # not its nominal 300 x 200
    assert rects[2] == (380.0, 638.0, 20.0, 20.0)                        # a member placed by its corner
    asked = video.library.sizes[0]["params"]                            # with what draw is given
    assert asked["rows"] == [["Rep", "Commission"], ["A", "1"], ["B", "2"], ["C", "3"]]


def test_in_a_region_it_is_centred_at_its_natural_size_and_not_fitted_to_the_region(example):
    video = pointed(example, NATURAL)
    rendered(video, "A", 2.0)
    assert video.library.draws[1]["rect"] == (751.0 + (711.0 - 240.0) / 2, 118.0 + (818.0 - 120.0) / 2, 240.0, 120.0)


def test_a_refusal_to_give_the_natural_size_is_one_message_in_words(example, tmp_path):
    cropped(example)
    narrated(example)
    script = describe(example, NATURAL.replace("rows=assets/sample.csv | 4 rows", "rows=assets/sample.csv explode=yes | 4 rows"))
    code, out, err = run("stills", script, "A:2.0", "--out", tmp_path / "s.png", "--elements", INVENTED)
    assert code == 3
    assert err == ("stills: scene A: the library could not size 'sheet' (table): element 'table': its natural_size "
                   "failed: Failure: no font role 'mono' in the brand kit\n")
    assert not (tmp_path / "s.png").exists()


def test_an_arrow_with_a_blank_where_can_be_moved_like_any_member(example):
    moved = BOXED.replace("- cue 1: show pot1, pot2, line, corner, far, mid\n",
                          "- cue 1: show pot1, pot2, line, corner, far, mid\n- cue 1, 0.5–1.0 s: move line to 100 100\n")
    video = pointed(example, moved)
    rendered(video, "A", 2.0)                       # after the move: the box's corner is at the area's 100 100
    small = [d["rect"] for d in video.library.draws if d["rect"][2] == 20.0]
    assert small[0] == (140.0, 218.0, 20.0, 20.0)


# ---- item 18 (request 16): an empty label is not a label

UNLABELLED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sheet | table | 100 400 | 300x100 | rows=assets/sample.csv tab="" | no tab name: the stub passes it through frame.label |
| named | table | 500 400 | 300x100 | rows=assets/sample.csv tab=crease | a label on the On screen list |
| helper | hand | 100 300 | | angle=1.2 scale=0.8 label="" | no letter |

### Moves

- cue 1: show sheet, named, helper

"""


def test_an_element_given_an_empty_label_is_drawn_and_one_given_a_listed_label_too(example):
    video = pointed(example, UNLABELLED)
    rendered(video, "A", 2.0)
    assert [d["params"]["tab"] for d in video.library.draws] == ["", "crease"]


def test_a_hand_with_an_empty_label_is_drawn_with_no_label(example, monkeypatch):
    from videotools import scenes
    hands = []
    monkeypatch.setattr(scenes.Frame, "hand", lambda self, x, y, angle, scale, **kw: hands.append(kw))
    rendered(pointed(example, UNLABELLED), "A", 2.0)
    assert hands[0]["label"] is None


# ---- item 19 (request 17), 1: a callout's leader colour

def test_a_callouts_leader_takes_the_colour_named_and_ink_otherwise(example, monkeypatch):
    from videotools import scenes
    leaders = []
    monkeypatch.setattr(scenes.Frame, "callout", lambda self, s, target, at, **kw: leaders.append(kw.get("leader", "ink")))
    cast = POINTED.replace('target="pot1.top-right + -20 30" | |',
                           'target="pot1.top-right + -20 30" leader=mistake | |\n'
                           '| plain | callout | 400 700 | | text="edge fold" target=pot1.centre | |').replace(
        "show pot1, pot2, line, note", "show pot1, pot2, line, note, plain")
    rendered(pointed(example, cast), "A", 2.0)
    assert leaders == ["mistake", "ink"]


# ---- item 19 (request 17), 2: curved and dashed arrows

def test_an_arrow_with_via_is_a_curve_by_its_two_points_and_with_dash_is_dashed(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    curved = POINTED.replace('to="pot2.centre + 0 -5" |',
                             'to="pot2.centre + 0 -5" via="300 50; pot2.top-left + -40 0" dash="12 8" |')
    rendered(pointed(example, curved), "A", 2.0)
    control, kw = arrows[0]                                  # area pixels 300 50 are frame pixels 340 168
    assert control == [(250.0, 318.0), (340.0, 168.0), (500.0, 418.0), (590.0, 463.0)]
    assert kw["dash"] == [12.0, 8.0]


def test_a_plain_arrow_is_handed_no_dash(example, monkeypatch):
    arrows, _targets = recorded(monkeypatch)
    rendered(pointed(example), "A", 2.0)
    assert arrows[0][1].get("dash") is None and len(arrows[0][0]) == 2


# ---- item 19 (request 17), 3: a member's own colours for an element's colour roles

def test_a_member_with_a_colour_of_its_own_is_drawn_in_it_and_its_neighbour_in_the_default(example):
    own = POINTED.replace("| pot1 | pot | 100 100 | 200 | |", "| pot1 | pot | 100 100 | 200 | colour.fill=correct |")
    video = pointed(example, own)
    s = rendered(video, "A", 2.0)
    assert pixel(s, 150, 228) == hex_rgb("#3E7D4F")          # pot1 in the paperboat kit's `correct`
    assert pixel(s, 550, 428) == ACCENT                      # pot2 as ever



# ---- item 19 (request 17), 4: a cast on the title and end cards, in frame pixels

TITLE_CAST = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sheet | pot | 1400 500 | 200 | | frame pixels: the rect is 1400 500, 200 x 200 |

### Moves

- cue 1, -0.3–0.7 s: show sheet

"""

END_CAST = """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sheet | pot | 100 700 | 200 | | |

### Moves

- 0.5–1.0 s: show sheet
- end-1.0–end-0.5 s: hide sheet
"""


def carded(example):
    """The example copy with a cast on its title card and on its end card (which has no cues)."""
    cropped(example)
    narrated(example)
    text = open(example, encoding="utf-8").read()
    notes, last = "## Notes\n\nProse between scenes", "the website, the credit lines.\n"
    assert text.count(notes) == 1 and text.endswith(last)
    open(example, "w", encoding="utf-8").write(text.replace(notes, TITLE_CAST + notes) + END_CAST)
    return frame.Video(example, INVENTED, None)


def test_a_title_cards_cast_is_drawn_over_the_card_in_frame_pixels_from_before_cue_1(example):
    video = carded(example)                                  # cue 1 starts at 0.7 s: the show is 0.4 to 1.4 s
    assert pixel(rendered(video, "title", 0.3), 1500, 600) != ACCENT
    assert pixel(rendered(video, "title", 1.6), 1500, 600) == ACCENT
    assert video.library.draws[-1]["rect"] == (1400.0, 500.0, 200.0, 200.0)


def test_an_end_cards_cast_is_drawn_and_its_moves_count_from_the_scenes_start_and_end(example):
    video = carded(example)                                  # the end card lasts 0.7 + 1.0 + 4.0 = 5.7 s
    assert pixel(rendered(video, "end", 0.4), 200, 800) != ACCENT
    assert pixel(rendered(video, "end", 2.0), 200, 800) == ACCENT
    assert pixel(rendered(video, "end", 5.3), 200, 800) != ACCENT      # hidden from 4.7 to 5.2 s


# ---- item 19 (request 17), 5: any member may be turned

TURNED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| early | pot | wide.bottom-left | 20 | | placed by the turned member's corner, before it in the cast |
| wide | pot | 100 100 | 200x80 | rotate=90 | frame rect 140 218, 200 x 80: centre 240 258; turned, it covers 200..280 by 158..358 |
| late | pot | wide.top-right | 20 | | placed by its corner, after it |
| plain | pill | 400 100 | | text=crease size=22 | |
| turned | pill | 400 400 | | text=crease size=22 rotate=90 | the same pill, a quarter turn about its own centre |
| plain-corner | pot | plain.top-left | 6 | | |
| plain-middle | pot | plain.centre | 6 | | |
| turned-corner | pot | turned.top-left | 6 | | |
| turned-middle | pot | turned.centre | 6 | | |

### Moves

- cue 1: show early, wide, late, plain, turned, plain-corner, plain-middle, turned-corner, turned-middle

"""


def test_a_turned_member_is_drawn_turned_about_the_centre_of_its_box(example):
    s = rendered(pointed(example, TURNED), "A", 2.0)
    assert pixel(s, 240, 170) == ACCENT                      # above the unturned rect, inside the turned one
    assert pixel(s, 150, 258) != ACCENT                      # inside the unturned rect, outside the turned one


def test_an_anchor_read_from_a_turned_member_is_turned_with_it_before_or_after_it_in_the_cast(example):
    video = pointed(example, TURNED)
    rendered(video, "A", 2.0)
    small = [d["rect"] for d in video.library.draws if d["rect"][2] == 20.0]
    assert small[0] == pytest.approx((200.0, 158.0, 20.0, 20.0))        # bottom-left (140 298), a quarter turn on
    assert small[1] == pytest.approx((280.0, 358.0, 20.0, 20.0))        # top-right (340 218)


def test_a_piece_is_turned_about_the_centre_of_what_it_drew(example):
    video = pointed(example, TURNED)
    rendered(video, "A", 2.0)
    (px, py), (pcx, pcy), (tx, ty), (tcx, tcy) = [d["rect"][:2] for d in video.library.draws if d["rect"][2] == 6.0]
    half_w, half_h = pcx - px, pcy - py                                 # the pill's half size, from the plain one
    assert half_w > half_h > 0
    assert (tx, ty) == pytest.approx((tcx + half_h, tcy - half_w))      # its top-left corner, a quarter turn on


def test_a_turn_is_animated_like_any_number_and_no_turn_is_exactly_the_frame_without(example):
    spun = TURNED.replace("| rotate=90 | frame rect", "| rotate=0 | frame rect").replace(
        "turned-middle\n", "turned-middle\n- cue 1, 1.5–2.5 s: wide.rotate 0 → 90\n")
    video = pointed(example, spun)
    before = bytes(rendered(video, "A", 2.0).get_data())                # rotate=0, before the move (2.2 to 3.2 s)
    assert pixel(rendered(video, "A", 3.4), 240, 170) == ACCENT         # after it, before the panels rise at 3.7 s
    cast = video.scene("A")["cast"]
    del next(m for m in cast if m["name"] == "wide")["params"]["rotate"]
    video.scene("A")["moves"][:] = [m for m in video.scene("A")["moves"] if m["action"]["kind"] != "param"]
    assert bytes(rendered(video, "A", 2.0).get_data()) == before
