"""videotools.choreography.check: what a cast row or a move means, checked against the scene,
the cue timing and the pieces (and, with a library, the elements: test_choreography_library.py)."""

import os

from videotools import choreography, elements, script, timeline

INVENTED = os.path.join(os.path.dirname(__file__), "..", "stubs", "video-elements")

HEAD = """# A video

## Scene A2: Example output

| Key | Value | Notes |
|---|---|---|
| letter | A | |

### Narration

1. One.
2. Two.
   - mistake: Formulas / Answers
3. Three.

### On screen

- Sample output
- checked ✓
"""

NO_MISTAKE = HEAD.replace("   - mistake: Formulas / Answers\n", "")

TL = timeline.Timeline([0.7, 3.7, 7.7], [3.0, 4.0, 2.0], 10.7, 30, estimated=[1, 2, 3], mistake=2)


def _check(text, tl=TL, lib=None, folder=None):
    data, problems = script.parse(text)
    assert problems == []
    scene = data["scenes"][0]
    return choreography.check(scene, tl, lib, folder)


def test_a_well_formed_described_scene_has_no_problems():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| tag | pill | 70 100 | | text="Sample output" size=22 fill=accent | |
| tick | badge | tag.top-right + 40 0 | | ok=yes r=20 | |
| checked | pill | tag.bottom-left | | text="checked ✓" anchor=centre | |

### Moves

- cue 1: show tag
- cue 1, 0.5–1.7 s: tag.size 22 → 30
- cue 2, 1.0 s: show tick
- cue 2, end-1.2–end-0.4 s: move tick to centre
- cue 3, -0.3–0.2 s: hide tick
- cue 3: show checked
- cue 3: tag.fill correct

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | badge | 610 600 | | ok=no r=30 | |

- 0.4–0.8 s: show wrong

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| answers-only | pill | 345 640 | | text="Sample output" fill=correct anchor=centre | |
"""
    assert _check(text) == []


def test_a_panel_section_in_a_scene_with_no_mistake_cue_is_a_problem():
    text = NO_MISTAKE + """
### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | badge | 610 600 | | ok=no | |
"""
    assert _check(text) == ["line 20: scene A2: a Mistake section, but no cue has a 'mistake:'"]


def test_an_element_that_is_neither_a_piece_nor_in_the_library_is_a_problem():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pillow | 70 100 | | text="Sample output" | |

### Moves

- cue 1: show a
"""
    lib = elements.open_library(INVENTED, None)
    assert _check(text, lib=lib) == [
        "line 25: scene A2, cast: 'a': no element 'pillow': not one of training-video-tools' pieces (pill, callout, text, "
        "badge, hand, arrow) and not in the library (pot, table)"]
    assert _check(text) == []       # no library: its elements are not checked here (check-script says why)


def test_a_where_or_a_move_to_another_member_needs_that_member_and_one_of_its_anchors():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | badge | ghost.centre | | ok=yes | |
| c | badge | a.rim | | ok=yes | |
| d | badge | d.centre | | ok=yes | |

### Moves

- cue 1: show a, b, c, d
- cue 2: move a to b.row.3
- cue 2: move a to nobody.centre
"""
    assert _check(text) == [
        "line 26: scene A2, cast: 'b' is placed by 'ghost', which is not in the cast (a, b, c, d)",
        "line 27: scene A2, cast: 'c' is placed by 'a'.'rim', but a pill's anchors are top-left, top-right, "
        "bottom-left, bottom-right and centre",
        "line 28: scene A2, cast: 'd' is placed by itself",
        "line 33: scene A2, moves: 'a' moves to 'b'.'row.3', but a badge's anchors are top-left, top-right, "
        "bottom-left, bottom-right and centre",
        "line 34: scene A2, moves: 'a' moves to 'nobody', which is not in the cast (a, b, c, d)",
    ]


def test_the_pieces_parameters_are_checked_by_name_type_and_what_is_required():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | size=big fill=accent anchor=middle | |
| b | badge | 70 100 | | ok=maybe r=2x | |
| c | arrow | 70 100 | | from=a.centre colour=ink | |
| d | hand | 70 100 | | angle=1 scale=1 mirror=yes label="Sample output" shade=dark | |
| e | text | 70 100 | | text="Sample output" role=display | |

### Moves

- cue 1: show a, b, c, d, e
"""
    assert _check(text) == [
        "line 25: scene A2, cast: 'a': a pill needs 'text'",
        "line 25: scene A2, cast: 'a': 'size' should be a number, not 'big'",
        "line 25: scene A2, cast: 'a': 'anchor' is left, centre or right, not 'middle'",
        "line 26: scene A2, cast: 'b': 'ok' is yes or no, not 'maybe'",
        "line 26: scene A2, cast: 'b': 'r' should be a number, not '2x'",
        "line 27: scene A2, cast: 'c': an arrow needs 'to'",
        "line 28: scene A2, cast: 'd': a hand has no parameter 'shade' (its parameters are angle, scale, mirror, "
        "label)",
    ]


def test_a_label_a_piece_draws_must_be_in_the_on_screen_list():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample Output" | |
| b | callout | 70 100 | | text="checked ✓" target=a.centre | |
| c | hand | 70 100 | | angle=1 scale=1 label=B | |

### Moves

- cue 1: show a, b, c

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| d | text | 10 10 | | text="answers only" | |
"""
    assert _check(text) == [
        "line 25: scene A2, cast: 'a' draws 'Sample Output', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 27: scene A2, cast: 'c' draws 'B', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 37: scene A2, right way: 'd' draws 'answers only', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
    ]


def test_a_move_needs_a_cue_the_scene_has_a_time_within_it_and_a_cast_member():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |

### Moves

- cue 4: show a
- cue 1, 2.8–3.4 s: show a
- cue 2, end+0.5 s: a.size 10 → 20
- cue 2: show ghost
- cue 2: hide ghost, a
- cue 3: move nobody to centre
- cue 3: nobody.size 1 → 2
- cue 3: nobody.size 1
- cue 3: nobody plain → cracked
- cue 3: a plain → cracked
- cue 3: a.weight 1 → 2
- cue 3: a.size 1 → big
- cue 3: a.fill correct
"""
    assert _check(text) == [
        "line 29: scene A2, moves: cue 4: the scene has 3 cues",
        "line 30: scene A2, moves: 3.4 s is past the end of cue 1, which is 3.0 s long (estimated at 2.6 words a "
        "second; run narrate for the measured length)",
        "line 31: scene A2, moves: 4.5 s is past the end of cue 2, which is 4.0 s long (estimated at 2.6 words a "
        "second; run narrate for the measured length)",
        "line 32: scene A2, moves: 'ghost' is not in the cast (a)",
        "line 33: scene A2, moves: 'ghost' is not in the cast (a)",
        "line 34: scene A2, moves: 'nobody' is not in the cast (a)",
        "line 35: scene A2, moves: 'nobody' is not in the cast (a)",
        "line 36: scene A2, moves: 'nobody' is not in the cast (a)",
        "line 37: scene A2, moves: 'nobody' is not in the cast (a)",
        "line 38: scene A2, moves: 'a' is a pill, and the pieces have no states",
        "line 39: scene A2, moves: 'a': a pill has no parameter 'weight' (its parameters are text, size, fill, "
        "colour, anchor)",
        "line 40: scene A2, moves: 'a': 'size' should be a number, not 'big'",
    ]


def test_a_measured_cue_length_is_reported_without_the_estimate_note():
    measured = timeline.Timeline([0.7, 3.7, 7.7], [3.0, 4.0, 2.0], 10.7, 30, estimated=[], mistake=2)
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |

### Moves

- cue 1, 3.1 s: show a
"""
    assert _check(text, tl=measured) == [
        "line 29: scene A2, moves: 3.1 s is past the end of cue 1, which is 3.0 s long"]


def test_a_member_never_shown_shown_again_while_shown_or_hidden_while_not_is_a_problem():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | badge | 70 100 | | ok=yes | |
| c | badge | 70 100 | | ok=yes | |

### Moves

- cue 3: hide c
- cue 1: show b
- cue 2: show b
- cue 2, 1.0 s: hide b
- cue 3: show b
- cue 3, 1.0 s: hide b
- cue 3, 1.2 s: hide b

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | badge | 610 600 | | ok=no | |
| late | badge | 610 600 | | ok=no | |

- 0.4–0.8 s: show wrong
- 1.0 s: hide late
- 1.2 s: show wrong
"""
    assert _check(text) == [
        "line 25: scene A2, cast: 'a' is never shown",
        "line 27: scene A2, cast: 'c' is never shown",
        "line 31: scene A2, moves: 'c' is hidden at cue 3 but was not shown",
        "line 33: scene A2, moves: 'b' is shown again at cue 2 while still shown (shown at line 32, not hidden "
        "since)",
        "line 37: scene A2, moves: 'b' is hidden at cue 3 but was not shown",
        "line 48: scene A2, mistake: 'wrong' is shown again while still shown (shown at line 46, not hidden since)",
    ]


def test_a_time_counted_from_the_cues_end_is_ordered_by_where_it_falls_not_by_its_offset():
    # cue 2 is 4.0 s long: end-1.2 is 2.8 s in, after a show at 0.5 s; found by the Tier 3 on the real scene A2
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |

### Moves

- cue 2, 0.5 s: show a
- cue 2, end-1.2–end-0.4 s: hide a
"""
    assert _check(text) == []
    text = text.replace("- cue 2, 0.5 s: show a", "- cue 2, end-0.9 s: show a")        # 3.1 s in: after the hide
    assert _check(text) == ["line 30: scene A2, moves: 'a' is hidden at cue 2 but was not shown"]


def test_a_keep_names_cast_members_and_changes_nothing_else():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |

### Moves

- cue 1: show a
- cue 3: keep a
- cue 3: keep ghost
"""
    assert _check(text) == ["line 31: scene A2, moves: 'ghost' is not in the cast (a)"]


# ---- item 17 (request 15): an arrow's progress and head, and a blank Where

def test_an_arrows_progress_is_a_number_from_0_to_1_in_the_cast_and_in_a_move():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | arrow | 70 100 | | from=a.centre to=a.top-right progress=1.5 | |
| c | arrow | 70 100 | | from=a.centre to=a.top-right progress=half | |
| d | arrow | 70 100 | | from=a.centre to=a.top-right progress=0.25 | |

### Moves

- cue 1: show a, b, c, d
- cue 1: d.progress 0 → 2
- cue 1: d.progress -0.5
- cue 1: d.progress 0 → 1
"""
    assert _check(text) == [
        "line 26: scene A2, cast: 'b': 'progress' is 0 to 1, not '1.5'",
        "line 27: scene A2, cast: 'c': 'progress' should be a number, not 'half'",
        "line 33: scene A2, moves: 'd': 'progress' is 0 to 1, not '2'",
        "line 34: scene A2, moves: 'd': 'progress' is 0 to 1, not '-0.5'",
    ]


def test_an_arrows_head_is_yes_or_no():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | arrow | 70 100 | | from=a.centre to=a.top-right head=no | |
| c | arrow | 70 100 | | from=a.centre to=a.top-right head=20 | |

### Moves

- cue 1: show a, b, c
"""
    assert _check(text) == ["line 27: scene A2, cast: 'c': 'head' is yes or no, not '20'"]


def test_an_arrow_with_a_blank_where_checks_clean_and_members_may_be_placed_by_its_box():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | pill | 300 200 | | text="checked ✓" | |
| line | arrow | | | from=a.centre to="b.centre + 0 -5" | |
| mid | badge | line.centre | | ok=yes | |

### Moves

- cue 1: show a, b, line, mid
"""
    assert _check(text) == []


def test_an_arrow_with_a_blank_where_cannot_point_from_or_to_its_own_box():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| line | arrow | | | from=line.centre to=a.centre | |
| placed | arrow | 10 10 | | from=placed.centre to=a.centre | its Where places it: allowed, as before |

### Moves

- cue 1: show a, line, placed
"""
    assert _check(text) == ["line 26: scene A2, cast: 'line': 'from' is its own anchor, but with a blank Where "
                            "its two ends are what place it"]


# ---- item 18 (request 16): a piece's text may not be empty; a hand's empty label is no label

def test_a_pieces_empty_text_is_a_problem_in_plain_words_and_a_hands_empty_label_means_none():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="" | |
| b | callout | 70 100 | | text="" target=d.centre | |
| c | text | 70 100 | | text="" | |
| d | hand | 70 100 | | angle=1 scale=1 label="" | |
| e | pill | 70 100 | | text="Sample output" | |
| f | hand | 70 100 | | angle=1 scale=1 label=B | |

### Moves

- cue 1: show a, b, c, d, e, f
- cue 2: e.text ""
- cue 2: f.label ""
"""
    assert _check(text) == [
        "line 25: scene A2, cast: 'a': 'text' is empty, so there is nothing to draw",
        "line 26: scene A2, cast: 'b': 'text' is empty, so there is nothing to draw",
        "line 27: scene A2, cast: 'c': 'text' is empty, so there is nothing to draw",
        "line 30: scene A2, cast: 'f' draws 'B', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 35: scene A2, moves: 'e': 'text' is empty, so there is nothing to draw",
    ]


# ---- item 19 (request 17), 2: curved and dashed arrows

def test_an_arrows_via_is_two_points_and_its_dash_two_numbers_above_0():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| good | arrow | | | from=a.centre to=a.top-right via="200 300; a.bottom-left + 10 -5" dash="12 8" | |
| one | arrow | | | from=a.centre to=a.top-right via="200 300" | |
| words | arrow | | | from=a.centre to=a.top-right via="left; 200 300" | |
| gone | arrow | | | from=a.centre to=a.top-right via="b.centre; 200 300" | |
| solid | arrow | | | from=a.centre to=a.top-right dash="12" | |
| none | arrow | | | from=a.centre to=a.top-right dash="12 0" | |

### Moves

- cue 1: show a, good, one, words, gone, solid, none
"""
    assert _check(text) == [
        "line 27: scene A2, cast: 'one': 'via' should be two points separated by ';', each X Y or a member's "
        "anchor like a.centre + 10 0, not '200 300'",
        "line 28: scene A2, cast: 'words': 'via' should be two points separated by ';', each X Y or a member's "
        "anchor like a.centre + 10 0, not 'left; 200 300'",
        "line 29: scene A2, cast: 'gone': 'via' is 'b', which is not in the cast (a, good, one, words, gone, solid, "
        "none)",
        "line 30: scene A2, cast: 'solid': 'dash' should be two numbers above 0, the dash and the gap, not '12'",
        "line 31: scene A2, cast: 'none': 'dash' should be two numbers above 0, the dash and the gap, not '12 0'",
    ]


# ---- item 19 (request 17), 4: the moves of a scene with no cues are timed from its start

def test_a_scene_with_no_cues_has_its_moves_checked_against_its_own_length():
    from tests.tier1.test_choreography_parse import NO_CUES
    text = NO_CUES.replace("- show a\n- cue 1: show a\n", "- 5.0–6.0 s: show a\n").replace(
        "| a | badge | 1500 300 | | ok=yes | frame pixels on a card |",
        "| a | badge | 1500 300 | | ok=yes | frame pixels on a card |\n| b | badge | 100 100 | | ok=no | |")
    tl = timeline.Timeline([], [], 5.7, 30, estimated=[], mistake=None)
    assert _check(text, tl=tl) == [
        "line 17: scene end, cast: 'b' is never shown",
        "line 23: scene end, moves: 6 s is past the end of the scene, which is 5.7 s long",
    ]


# ---- item 19 (request 17), 5: any member may be turned

def test_rotate_is_a_number_on_any_piece_in_the_cast_and_in_a_move():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" rotate=10 | |
| b | badge | 70 100 | | ok=yes rotate=sideways | |
| c | hand | 70 100 | | angle=1 scale=1 rotate=-90 | |

### Moves

- cue 1: show a, b, c
- cue 1: a.rotate 0 → -20
- cue 2: a.rotate upside
- cue 3: c.rotate 45
"""
    assert _check(text) == [
        "line 26: scene A2, cast: 'b': 'rotate' should be a number, not 'sideways'",
        "line 33: scene A2, moves: 'a': 'rotate' should be a number, not 'upside'",
    ]


# ---- item 20 (request 18), 2: dimming to a level

def test_a_dim_needs_a_level_from_0_to_1_and_a_member_that_is_shown_and_a_show_after_it_is_allowed():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | badge | 70 100 | | ok=yes | |
| c | badge | 70 200 | | ok=yes | |

### Moves

- cue 1: show a, c
- cue 1, 1.0 s: dim a to 0.55
- cue 2: show a
- cue 2, 1.0 s: dim a to 1.5
- cue 2: dim b to 0.5
- cue 2: hide c
- cue 3: dim c to 0.5
- cue 3: dim ghost to 0.5
"""
    assert _check(text) == [
        "line 26: scene A2, cast: 'b' is never shown",
        "line 34: scene A2, moves: a level is 0 to 1, not '1.5'",
        "line 35: scene A2, moves: 'b' is dimmed at cue 2 but is not shown",
        "line 37: scene A2, moves: 'c' is dimmed at cue 3 but is not shown",
        "line 38: scene A2, moves: 'ghost' is not in the cast (a, b, c)",
    ]


# ---- item 20 (request 18), 3: percentages, and a span that ends in a later cue

def test_each_time_of_a_span_is_checked_against_its_own_cue_and_the_later_cue_must_come_after():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |

### Moves

- cue 1: show a
- cue 2, 50%–120%: a.size 22 → 30
- cue 2, 0.5 s – cue 1, 1 s: a.size 22 → 30
- cue 1, 0.5 s – cue 9, 1 s: a.size 22 → 30
- cue 1, 0.5 s – cue 3, 5 s: a.size 22 → 30
- cue 1, 0.5 s – cue 3, 50%: a.size 22 → 30
- cue 3, 1 s – end of scene: a.size 22 → 30
"""
    assert _check(text) == [                                # the first move is line 29
        "line 30: scene A2, moves: 4.8 s is past the end of cue 2, which is 4.0 s long" + choreography.ESTIMATE_NOTE,
        "line 31: scene A2, moves: the span ends at cue 1, which is not after cue 2",
        "line 32: scene A2, moves: cue 9: the scene has 3 cues",
        "line 33: scene A2, moves: 5 s is past the end of cue 3, which is 2.0 s long" + choreography.ESTIMATE_NOTE,
    ]


# ---- item 21 (request 19): a repeating flash

def test_a_flash_needs_a_cast_member_a_rate_and_a_low_in_range_and_no_other_flash_at_the_same_time():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 70 100 | | text="Sample output" | |
| b | badge | 70 100 | | ok=yes | |

### Moves

- cue 1: show a, b
- cue 1, 1 s – end: flash a
- cue 1, 2 s – cue 2, 1 s: flash a, b
- cue 2, 2 s – end: flash a rate=5
- cue 3, 0–0.5 s: flash a rate=0
- cue 3, 1–1.5 s: flash a low=1
- cue 3: flash ghost
- cue 3, 1.6 s – end of scene: flash b phase=7.25
"""
    assert _check(text) == [                                # the first move is line 30
        "line 32: scene A2, moves: 'a' is already flashing then (line 31)",
        "line 33: scene A2, moves: a flash's rate is above 0 and at most 3 a second, not '5'",
        "line 34: scene A2, moves: a flash's rate is above 0 and at most 3 a second, not '0'",
        "line 35: scene A2, moves: a flash's low is from 0 to below 1, not '1'",
        "line 36: scene A2, moves: 'ghost' is not in the cast (a, b)",
    ]
