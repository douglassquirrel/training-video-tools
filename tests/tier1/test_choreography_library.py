"""videotools.choreography.check with a library: elements, their anchors, states and parameters
(by name, kind and range, with indices and data files), against the invented library."""

import os

import pytest

from tests.tier1.test_choreography_check import HEAD, TL
from videotools import choreography, elements, script

INVENTED = os.path.join(os.path.dirname(__file__), "..", "stubs", "video-elements")


@pytest.fixture
def lib():
    return elements.open_library(INVENTED, None)


@pytest.fixture
def folder(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "sample.csv").write_text("Sales Rep,Commission\nJ. M,5940\nC. M,7900\nL. C,1750\n")
    return str(tmp_path)


def _check(text, lib, folder):
    data, problems = script.parse(text)
    assert problems == []
    return choreography.check(data["scenes"][0], TL, lib, folder)


def test_a_well_described_scene_with_library_elements_has_no_problems(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | 120 | state=plain | |
| t | table | p.rim + 20 0 | | rows=assets/sample.csv tab="Sample output" rows-shown=0 highlight.3=0.5 highlight-colour.2=correct cell-alpha.3.2=0 striped=yes | |
| tick | badge | t.row.1 + 40 0 | | ok=yes | |
| cell | badge | t.cell.3.2 | | ok=yes | |

### Moves

- cue 1: show p, t, tick, cell
- cue 1, 0.5–1.7 s: t.rows-shown 0 → 3
- cue 2: t.highlight.3 0 → 1
- cue 2: t.highlight-colour.3 correct
- cue 2: t.cell-alpha.3.2 0 → 1
- cue 3: p plain → plain
"""
    assert _check(text, lib, folder) == []


def test_an_anchor_the_element_does_not_have_or_an_index_of_0_is_a_problem(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | | | |
| t | table | 10 10 | | rows=assets/sample.csv | |
| a | badge | p.lid | | ok=yes | |
| b | badge | t.row.0 | | ok=yes | |
| c | badge | t.cell.3 | | ok=yes | |

### Moves

- cue 1: show p, t, a, b, c
- cue 2: move a to t.tab.2
"""
    assert _check(text, lib, folder) == [
        "line 27: scene A2, cast: 'a' is placed by 'p'.'lid', but a pot's anchors are rim, base, top-left, top-right, "
        "bottom-left, bottom-right and centre",
        "line 28: scene A2, cast: 'b' is placed by 't'.'row.0', but rows count from 1",
        "line 29: scene A2, cast: 'c' is placed by 't'.'cell.3', but a table's anchors are title, row.*, cell.*.*, "
        "top-left, top-right, bottom-left, bottom-right and centre",
        "line 34: scene A2, moves: 'a' moves to 't'.'tab.2', but a table's anchors are title, row.*, cell.*.*, "
        "top-left, top-right, bottom-left, bottom-right and centre",
    ]


def test_a_library_elements_parameters_are_checked_by_name_kind_range_and_what_is_required(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | | colour=ink rows-shown=2000 highlight.3=x highlight-colour.1= striped=maybe highlight.3.2=1 | |
| u | table | 10 10 | | rows=assets/sample.csv rows-shown=1.5 tab=Sheet2 note="any text at all" | |

### Moves

- cue 1: show t, u
- cue 2: u.highlight.3 0 → 2
- cue 2: u.highlight.0 0 → 1
- cue 2: u.rows-shown 0 → x
- cue 2: u.tab Sheet9
"""
    assert _check(text, lib, folder) == [
        "line 25: scene A2, cast: 't': a table needs 'rows'",
        "line 25: scene A2, cast: 't': a table has no parameter 'colour' (its parameters are rows, tab, note, "
        "rows-shown, highlight.*, highlight-colour.*, cell-alpha.*.*, striped)",
        "line 25: scene A2, cast: 't': 'rows-shown' is 0 to 1000, not '2000'",
        "line 25: scene A2, cast: 't': 'highlight.3' should be a number, not 'x'",
        "line 25: scene A2, cast: 't': 'highlight-colour.1' needs a colour name",
        "line 25: scene A2, cast: 't': 'striped' is yes or no (true or false), not 'maybe'",
        "line 25: scene A2, cast: 't': a table has no parameter 'highlight.3.2' (its parameters are rows, tab, note, "
        "rows-shown, highlight.*, highlight-colour.*, cell-alpha.*.*, striped)",
        "line 26: scene A2, cast: 'u': 'rows-shown' should be a whole number, not '1.5'",
        "line 26: scene A2, cast: 'u' draws 'Sheet2', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 31: scene A2, moves: 'u': 'highlight.3' is 0 to 1, not '2'",
        "line 32: scene A2, moves: 'u': 'highlight.0' counts from 1",
        "line 33: scene A2, moves: 'u': 'rows-shown' should be a whole number, not 'x'",
        "line 34: scene A2, moves: 'u' draws 'Sheet9', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
    ]


def test_a_data_file_must_exist_under_the_video_and_an_index_may_not_pass_its_rows(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | | rows=assets/missing.csv | |
| u | table | 10 10 | | rows=assets/sample.csv highlight.4=1 highlight.0=1 cell-alpha.2.9=0 | |
| v | badge | u.row.5 | | ok=yes | |

### Moves

- cue 1: show t, u, v
- cue 2: u.highlight.6 0 → 1
"""
    assert _check(text, lib, folder) == [
        f"line 25: scene A2, cast: 't': 'rows' names assets/missing.csv, which is not under {folder}",
        "line 26: scene A2, cast: 'u': 'highlight.0' counts from 1",      # highlight.4: a 4-row file, allowed
        "line 27: scene A2, cast: 'v' is placed by 'u'.'row.5', but assets/sample.csv has 4 rows",
        "line 32: scene A2, moves: 'u': 'highlight.6': assets/sample.csv has 4 rows",
    ]


def test_a_state_must_be_one_the_element_has_and_a_code_element_without_states_takes_none(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | | state=broken | |
| t | table | 10 10 | | rows=assets/sample.csv state=plain | |

### Moves

- cue 1: show p, t
- cue 2: p plain → broken
- cue 2: t plain → cracked
"""
    assert _check(text, lib, folder) == [
        "line 25: scene A2, cast: 'p': a pot has no state 'broken' (its states are plain, cracked)",
        "line 26: scene A2, cast: 't': a table has no states",
        "line 31: scene A2, moves: 'p': a pot has no state 'broken' (its states are plain, cracked)",
        "line 32: scene A2, moves: 't': a table has no states",
    ]


def test_a_member_placed_by_or_moved_to_a_computed_anchor_must_come_after_that_member(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | badge | t.row.1 | | ok=yes | before t: its rows are computed when t is drawn |
| c0 | callout | 10 10 | | text="Sample output" target=t.row.1 | likewise |
| t | table | 10 10 | | rows=assets/sample.csv | |
| d | badge | p.rim | | ok=yes | p's rim is fixed: any order will do; after t, so it may move to t's rows |
| b | badge | t.cell.2.2 | | ok=yes | after t: fine |
| c | callout | 10 10 | | text="Sample output" target=t.row.1 | after t: fine |
| p | pot | 10 10 | | | |

### Moves

- cue 1: show a, c0, d, t, b, c, p
- cue 2: move d to t.row.2
- cue 2: move a to t.row.2
"""
    assert _check(text, lib, folder) == [
        "line 25: scene A2, cast: 'a' is placed by 't'.'row.1', which is computed when 't' is drawn, so 'a' must "
        "come after 't' in the cast",
        "line 26: scene A2, cast: 'c0': 'target' is 't'.'row.1', which is computed when 't' is drawn, so 'c0' must "
        "come after 't' in the cast",
        "line 37: scene A2, moves: 'a' moves to 't'.'row.2', which is computed when 't' is drawn, so 'a' must "
        "come after 't' in the cast",
    ]
