"""videotools.chrome: what the chrome works out from the script before it draws anything."""

import pytest

from videotools import chrome, script, timeline

EXAMPLE = "examples/videos/paper-boat/script.md"
SETTINGS = {"lead": 0.7, "cue-gap": 0.55, "tail": 1.0, "fps": 30}


def test_the_layout_names_every_region_of_a_1920_by_1080_frame():
    lay = chrome.Layout((1920, 1080))
    assert (lay.width, lay.height) == (1920, 1080)
    assert lay.area == (40, 118, 1422, 818)          # x, y, w, h: the animation area
    assert lay.column == (1492, 118, 388, 818)       # the reference column
    assert lay.caption == (0, 948, 1920, 132)        # the caption band
    assert lay.header_rule == 112
    assert lay.card == (0, 0, 1920, 948)             # title and end cards: everything but the band
    with pytest.raises(ValueError):
        chrome.Layout((1280, 720))


def test_the_tracker_has_one_place_per_letter_in_script_order_with_labels():
    data = script.read(EXAMPLE)
    assert chrome.tracker(data) == [("A", "A", ["A"]), ("B", "Corners", ["B", "B2"]), ("C", "C", ["C"])]


def test_the_trackers_current_place_and_the_recap_after_the_last():
    data = script.read(EXAMPLE)
    by_key = {s["key"]: s for s in data["scenes"]}
    assert chrome.tracker_place(data, by_key["A"]) == 0
    assert chrome.tracker_place(data, by_key["B2"]) == 1
    assert chrome.tracker_place(data, by_key["C"]) == 2
    assert chrome.tracker_place(data, by_key["R"]) == 3        # a scene after the steps: all done
    assert chrome.tracker_place(data, by_key["title"]) == 0    # before any step: none done


def test_a_scene_without_a_letter_between_steps_shows_the_steps_so_far_as_done():
    data = script.read(EXAMPLE)
    overview = {"key": "o", "name": "o", "line": 1, "props": {"title": "x"}, "cues": [], "side": [], "screen": []}
    data["scenes"].insert(2, overview)                          # after A, before B
    assert chrome.tracker_place(data, overview) == 1            # A done; nothing is "now"
    assert chrome.tracker_done_now(data, overview) == ([0], None)
    assert chrome.tracker_done_now(data, data["scenes"][3]) == ([0], 1)      # B: A done, B now
    assert chrome.tracker_done_now(data, data["scenes"][-2]) == ([0, 1, 2], None)   # R: all done


def test_the_title_cards_step_list_is_one_entry_per_letter_with_the_first_scenes_title():
    data = script.read(EXAMPLE)
    assert chrome.title_steps(data) == [("A", "Fold in half"), ("B", "Corners to the centre"), ("C", "Open the hull")]


def test_the_current_step_follows_the_speaking_cues_step_property():
    data = script.read(EXAMPLE)
    b = [s for s in data["scenes"] if s["key"] == "B"][0]
    tl = timeline.build(SETTINGS, b, [1.0, 1.0])
    assert chrome.current_step(b, tl, 0.0) is None
    assert chrome.current_step(b, tl, 0.7) == 1
    assert chrome.current_step(b, tl, 3.3) == 2
    assert chrome.steps_done(b, tl, 3.3) == [1]


def test_checklist_items_tick_one_by_one_during_the_cue():
    scene = {"key": "R", "name": "R", "line": 1, "props": {}, "side": [], "screen": [],
             "cues": [{"n": 1, "text": "The end.", "line": 2}, {"n": 2, "text": "a b c d e f g h i j k l m n o p", "line": 3}]}
    tl = timeline.build(SETTINGS, scene, [1.0, 6.0])        # cue 2 starts at 2.25, lasts 6.55
    assert chrome.checklist_progress(tl, 2, 3, 0.0) == [0.0, 0.0, 0.0]
    assert chrome.checklist_progress(tl, 2, 3, 2.25 + 0.4) == [1.0, 0.0, 0.0]
    # items are spaced (length - 0.6) / count apart and each takes 0.4 s to appear
    assert chrome.checklist_progress(tl, 2, 3, 2.25 + (6.55 - 0.6) / 3 + 0.2) == [1.0, 0.5, 0.0]
    assert chrome.checklist_progress(tl, 2, 3, 30.0) == [1.0, 1.0, 1.0]


def test_scaled_font_sizes_follow_the_brands_scale():
    assert chrome.px(1.12, 36) == pytest.approx(40.32)
