"""videotools.timeline: cue starts from clip lengths, the two questions scene code asks, easing."""

import pytest

from videotools import cli, script, timeline
from videotools.timeline import clamp, ease, ep, lerp, prog, pulse

SETTINGS = {"lead": 0.7, "cue-gap": 0.55, "tail": 1.0, "fps": 30}


def scene(cues, extra=None):
    """A scene with the given cue dicts (text, min) and an optional extra."""
    props = {} if extra is None else {"extra": str(extra)}
    return {"key": "A", "name": "A", "line": 1, "props": props, "side": [], "screen": [],
            "cues": [dict({"n": i, "line": i, "text": c[0]}, **({"min": c[1]} if len(c) > 1 else {}))
                     for i, c in enumerate(cues, 1)]}


def test_easing_helpers_give_the_prototypes_values():
    assert (clamp(-1), clamp(0.5), clamp(2), clamp(5, 0, 3)) == (0.0, 0.5, 1.0, 3)
    assert lerp(10, 20, 0.25) == 12.5
    assert (prog(0, 1, 3), prog(2, 1, 3), prog(9, 1, 3), prog(2, 3, 3), prog(3, 3, 3)) == (0.0, 0.5, 1.0, 0.0, 1.0)
    assert (ease(0), ease(0.5), ease(1)) == (0.0, 0.5, 1.0)
    assert ease(0.25) == pytest.approx(0.15625)
    assert ep(2, 1, 3) == 0.5
    assert (pulse(1, 1, 3), pulse(2, 1, 3), pulse(3, 1, 3)) == (pytest.approx(0.0), pytest.approx(1.0), pytest.approx(0.0))


def test_hand_written_clip_lengths_give_exact_cue_starts_and_a_frame_rounded_total():
    sc = scene([("Step A. Make the loop.",), ("Now pull.",), ("Done.",)])
    tl = timeline.build(SETTINGS, sc, [1.2, 2.0, 0.813])
    assert [tl.start(n) for n in (1, 2, 3)] == [0.7, 0.7 + 1.75, 0.7 + 1.75 + 2.55]
    assert [tl.length(n) for n in (1, 2, 3)] == [1.75, 2.55, pytest.approx(1.363)]
    # 0.7 + 1.75 + 2.55 + 1.363 + 1.0 = 7.363 s = 220.89 frames -> 221 frames
    assert (tl.frames, tl.total) == (221, pytest.approx(221 / 30))
    assert tl.estimated == []


def test_a_cues_minimum_wins_when_it_is_longer_than_the_clip_and_gap():
    sc = scene([("Step A.", "3.0"), ("Now pull.", "1.0")])
    tl = timeline.build(SETTINGS, sc, [1.2, 2.0])
    assert (tl.length(1), tl.length(2)) == (3.0, 2.55)
    assert tl.start(2) == 3.7


def test_extra_holds_the_scene_after_its_last_cue():
    sc = scene([("Step A.",)], extra=2.0)
    tl = timeline.build(SETTINGS, sc, [1.0])
    # 0.7 + 1.55 + 1.0 + 2.0 = 5.25 s = 157.5 frames -> 158 (round half to even: 157.5 -> 158)
    assert tl.frames == 158


def test_a_scene_with_no_cues_lasts_lead_tail_and_extra():
    tl = timeline.build(SETTINGS, scene([], extra=4.0), [])
    assert (tl.frames, tl.total) == (171, 5.7)
    assert tl.cue(3.0) == 0


def test_cue_is_the_cue_speaking_now_and_zero_before_the_first():
    sc = scene([("One.",), ("Two.",), ("Three.",)])
    tl = timeline.build(SETTINGS, sc, [1.0, 1.0, 1.0])
    assert [tl.cue(t) for t in (0.0, 0.69, 0.7, 2.24, 2.25, 9.0)] == [0, 0, 1, 1, 2, 3]


def test_p_is_eased_progress_between_two_offsets_from_a_cues_start():
    sc = scene([("One.",), ("Two.",)])
    tl = timeline.build(SETTINGS, sc, [1.0, 1.0])
    assert (tl.p(2.25, 2, 0.0, 1.0), tl.p(2.75, 2, 0.0, 1.0), tl.p(3.25, 2, 0.0, 1.0), tl.p(9, 2, 0.3, 1.8)) == (0.0, 0.5, 1.0, 1.0)
    assert tl.p(0.0, 2, 0.0, 1.0) == 0.0


def test_a_cue_without_a_clip_is_refused_for_rendering_naming_the_scene_and_cue():
    sc = scene([("One.",), ("Two three four five six.",)])
    with pytest.raises(cli.Failure) as e:
        timeline.build(SETTINGS, sc, [1.0, None])
    assert str(e.value) == "scene A cue 2 has no narration clip; run narrate first"
    assert e.value.code == cli.REFUSED
    with pytest.raises(cli.Failure) as e:
        timeline.build(SETTINGS, sc, None)
    assert str(e.value) == "scene A has no narration clips; run narrate first"


def test_a_missing_clip_may_be_estimated_from_its_words_for_stills_and_is_listed():
    sc = scene([("One.",), ("Two three four five six.",)])
    tl = timeline.build(SETTINGS, sc, [1.0, None], estimate=True)
    assert tl.length(2) == pytest.approx(5 / 2.6 + 0.55)
    assert tl.estimated == [2]
    tl = timeline.build(SETTINGS, sc, None, estimate=True)
    assert tl.estimated == [1, 2]


def test_clip_lengths_come_from_timing_data_by_scene_key():
    sc = scene([("One.",), ("Two.",)])
    timing = {"scenes": {"A": [1.0, 2.0], "B": [0.5]}}
    assert timeline.clips_for(timing, sc) == [1.0, 2.0]
    assert timeline.clips_for({"scenes": {}}, sc) is None
    assert timeline.clips_for({"scenes": {"A": [1.0]}}, sc) == [1.0, None]
    assert timeline.clips_for(None, sc) is None


def test_the_example_scripts_scenes_build_with_estimates():
    data = script.read("examples/videos/paper-boat/script.md")
    st = script.settings(data)
    for sc in data["scenes"]:
        tl = timeline.build(st, sc, None, estimate=True)
        assert tl.frames > 0 and len(tl.estimated) == len(sc["cues"])
