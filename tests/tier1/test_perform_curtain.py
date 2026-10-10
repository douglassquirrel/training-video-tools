"""videotools.perform: the curtain for free (PLAN.md item 15). A member shown before the mistake
cue and not named in any move at or after the cue that follows it fades under the panels
(before_curtain); one named after the mistake is left to its moves. Pure: no library, no frame."""

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
