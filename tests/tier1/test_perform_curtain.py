"""videotools.perform: the curtain for free (PLAN.md item 15). A member shown before the mistake
cue and not named in any move at or after the cue that follows it fades under the panels
(before_curtain); one named after the mistake is left to its moves. Pure: no library, no frame."""

import pytest

from videotools import perform, timeline

TL = timeline.Timeline([0.7, 3.7, 7.7], [3.0, 4.0, 2.0], 10.7, 30, estimated=[], mistake=2)
AREA = (40, 118, 1422, 818)


def _member(name):
    return {"name": name, "element": "badge", "where": {"kind": "pixels", "x": 0, "y": 0}, "size": None,
            "params": {"ok": "yes"}, "line": 1}


def _move(cue, kind, names, start=0.0, end=0.6):
    return {"cue": cue, "start": ("start", start), "end": ("start", end), "action": {"kind": kind, "names": names},
            "line": 1}


def test_a_member_shown_before_the_mistake_and_not_named_after_it_fades_while_covered():
    p = perform.Performance([_member("a")], [_move(1, "show", ["a"])], AREA, TL, 4.0, None)
    assert p.alpha("a") == 1.0                     # cue 2 + 0.3 s: the panels still rising, the member still there
    p = perform.Performance([_member("a")], [_move(1, "show", ["a"])], AREA, TL, 4.3, None)
    assert 0.0 < p.alpha("a") < 1.0                # 0.5–0.7 s after the mistake cue's start: fading, covered
    p = perform.Performance([_member("a")], [_move(1, "show", ["a"])], AREA, TL, 5.0, None)
    assert p.alpha("a") == 0.0                     # gone before the panels lift for cue 3


def test_a_member_named_in_a_move_at_a_later_cue_is_left_to_its_moves():
    moves = [_move(1, "show", ["b"]), _move(3, "hide", ["b"], 0.0, 0.3)]
    assert perform.Performance([_member("b")], moves, AREA, TL, 5.0, None).alpha("b") == 1.0
    assert perform.Performance([_member("b")], moves, AREA, TL, 8.5, None).alpha("b") == 0.0


def test_a_member_first_shown_at_or_after_the_mistake_cue_is_not_touched():
    moves = [_move(2, "show", ["c"], 1.0, 1.5)]
    assert perform.Performance([_member("c")], moves, AREA, TL, 6.0, None).alpha("c") == 1.0


def test_a_scene_with_no_mistake_cue_has_no_curtain():
    tl = timeline.Timeline([0.7, 3.7], [3.0, 4.0], 8.7, 30, estimated=[], mistake=None)
    assert perform.Performance([_member("a")], [_move(1, "show", ["a"])], AREA, tl, 5.0, None).alpha("a") == 1.0


def test_a_keep_at_a_later_cue_leaves_the_member_to_stay_through_the_mistake():
    # found by the Tier 3 on the real scene A2: its "Sample output" tag stays while the panels come and go
    moves = [_move(1, "show", ["d"]), _move(3, "keep", ["d"])]
    assert perform.Performance([_member("d")], moves, AREA, TL, 5.0, None).alpha("d") == 1.0
    assert perform.Performance([_member("d")], moves, AREA, TL, 8.5, None).alpha("d") == 1.0


def test_a_member_in_a_span_that_ends_at_a_later_cue_or_at_the_scenes_end_is_left_to_its_moves():
    # item 20, 3: the member is named at the cue its span ends in
    across = dict(_move(1, "keep", ["e"]), end_cue=3)
    assert perform.Performance([_member("e")], [_move(1, "show", ["e"]), across], AREA, TL, 5.0, None).alpha("e") == 1.0
    to_the_end = dict(_move(1, "keep", ["f"]), end=("scene", 0.0))
    assert perform.Performance([_member("f")], [_move(1, "show", ["f"]), to_the_end], AREA, TL, 5.0, None).alpha("f") == 1.0


# ---- item 21 (request 19): a repeating flash multiplies a member's opacity over its span

def _flash(cue, names, start, end, **options):
    action = dict({"kind": "flash", "names": names, "rate": 1.0, "phase": 0.0, "low": 0.0}, **options)
    return {"cue": cue, "start": start, "end": end, "action": action, "line": 1}


def _alpha(moves, t, name="g"):
    return perform.Performance([_member(name)], moves, AREA, TL, t, None).alpha(name)


def test_a_flash_is_a_sine_from_the_spans_start_and_the_plain_opacity_outside_it():
    moves = [_move(1, "show", ["g"]), _flash(1, ["g"], ("start", 1.0), ("start", 3.0))]     # 1.7 to 3.7 s, once a second
    assert _alpha(moves, 1.5) == 1.0                         # before the span: its plain opacity
    assert _alpha(moves, 1.7) == pytest.approx(0.5)          # the start
    assert _alpha(moves, 1.95) == pytest.approx(1.0)         # a quarter-beat on
    assert _alpha(moves, 2.45) == pytest.approx(0.0)         # three quarters


def test_a_flashs_rate_phase_and_low_shape_it():
    def at(t, **options):
        return _alpha([_move(1, "show", ["g"]), _flash(1, ["g"], ("start", 1.0), ("start", 3.0), **options)], t)
    assert at(1.7, phase=0.25) == pytest.approx(1.0)         # a quarter-beat ahead
    assert at(2.45, low=0.6) == pytest.approx(0.6)           # never below its low
    assert at(1.7 + 0.25 / 1.4, rate=1.4) == pytest.approx(1.0)


def test_a_flash_multiplies_what_the_member_already_is_so_a_hidden_member_stays_hidden():
    assert _alpha([_flash(1, ["g"], ("start", 1.0), ("start", 3.0))], 1.95) == 0.0          # never shown
    dimmed = [_move(1, "show", ["g"]), dict(_move(1, "dim", ["g"], 0.6, 0.8), action={"kind": "dim", "names": ["g"],
                                                                                      "level": 0.5}),
              _flash(1, ["g"], ("start", 1.0), ("start", 3.0))]
    assert _alpha(dimmed, 1.95) == pytest.approx(0.5)        # at the flash's top: the dim's level


def test_a_flash_does_not_name_its_member_for_the_curtain_so_it_still_fades_under_the_panels():
    moves = [_move(1, "show", ["g"]), _flash(1, ["g"], ("start", 1.0), ("scene", 0.0))]
    assert _alpha(moves, 5.0) == 0.0                         # covered, cue 2 + 1.3 s: gone, though flashing to the end
