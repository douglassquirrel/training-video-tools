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
        "line 25: scene A2, cast: 'a': no element 'pillow': not one of video-tools' pieces (pill, callout, text, "
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
