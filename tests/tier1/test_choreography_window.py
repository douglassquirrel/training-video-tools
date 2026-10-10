"""videotools.choreography.window: a move's span in scene seconds, from times written as seconds
from a cue's start or end, a percentage of its length, or the scene's end; in a scene with
cues, in a panel, and in a scene with none (PLAN.md item 20, 3)."""

import pytest

from videotools import choreography, timeline

TL = timeline.Timeline([0.7, 3.7, 7.7], [3.0, 4.0, 2.0], 10.7, 30, estimated=[], mistake=2)
BARE = timeline.Timeline([], [], 5.7, 30, estimated=[], mistake=None)


def _move(cue, start, end, end_cue=None):
    move = {"cue": cue, "start": start, "end": end, "action": {"kind": "keep", "names": ["a"]}, "line": 1}
    if end_cue:
        move["end_cue"] = end_cue
    return move


def test_seconds_count_from_the_cues_start_or_back_from_its_end():
    assert choreography.window(_move(1, ("start", 0.5), ("end", -0.4)), TL) == pytest.approx((1.2, 3.3))


def test_a_percentage_is_that_share_of_the_cues_length():
    assert choreography.window(_move(2, ("fraction", 0.74), ("fraction", 0.8)), TL) == pytest.approx((6.66, 6.9))
    assert choreography.window(_move(2, ("fraction", 0.42), ("fraction", 0.42, 0.6)), TL) == pytest.approx((5.38, 5.98))


def test_a_span_may_end_in_a_later_cue_or_at_the_scenes_end():
    assert choreography.window(_move(1, ("start", 0.5), ("end", -0.5), end_cue=2), TL) == pytest.approx((1.2, 7.2))
    assert choreography.window(_move(2, ("start", 2.6), ("scene", 0.0)), TL) == pytest.approx((6.3, 10.7))


def test_in_a_panel_times_count_from_the_mistake_cues_start_and_end_and_length():
    assert choreography.window(_move(None, ("start", 0.4), ("fraction", 0.5)), TL, panel=True) == pytest.approx((4.1, 5.7))
    assert choreography.window(_move(None, ("end", -1.0), ("end", 0.0)), TL, panel=True) == pytest.approx((6.7, 7.7))


def test_in_a_scene_with_no_cues_times_count_from_the_scenes_start_and_end_and_length():
    assert choreography.window(_move(None, ("fraction", 0.5), ("end", -1.0)), BARE) == pytest.approx((2.85, 4.7))
