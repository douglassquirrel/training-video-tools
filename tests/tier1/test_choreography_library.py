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
        "line 27: scene A2, cast: 'a' is placed by 'p'.'lid', but a pot's anchors are rim, base, tab.*, top-left, top-right, "
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
        "rows-shown, highlight.*, highlight-colour.*, cell-alpha.*.*, striped, explode)",
        "line 25: scene A2, cast: 't': 'rows-shown' is 0 to 1000, not '2000'",
        "line 25: scene A2, cast: 't': 'highlight.3' should be a number, not 'x'",
        "line 25: scene A2, cast: 't': 'highlight-colour.1' needs a colour name",
        "line 25: scene A2, cast: 't': 'striped' is yes or no (true or false), not 'maybe'",
        "line 25: scene A2, cast: 't': a table has no parameter 'highlight.3.2' (its parameters are rows, tab, note, "
        "rows-shown, highlight.*, highlight-colour.*, cell-alpha.*.*, striped, explode)",
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
        "line 26: scene A2, cast: 'u': 'cell-alpha.2.9': assets/sample.csv has 2 columns",    # item 23: every index
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


# ---- item 17 (request 15), 3: a blank Size on an element whose size is nominal is a warning

NOMINAL = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | | | an svg element: its own size is its size |
| t | table | 10 300 | | rows=assets/sample.csv | |
| sized | table | 400 300 | 300x120 | rows=assets/sample.csv | |
| tag | pill | 10 10 | | text="Sample output" | |

### Moves

- cue 1: show p, t, sized, tag

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | table | left | | rows=assets/sample.csv | |
"""


def _scene(text):
    data, problems = script.parse(text)
    assert problems == []
    return data["scenes"][0]


def without_fit(tmp_path):
    """A copy of the invented library whose table does not offer its natural size (no `fit` row):
    nominal, as the real `diff` is. Returns (the copy's folder, the table's ELEMENT.md)."""
    import shutil
    copy = tmp_path / "library"
    shutil.copytree(INVENTED, copy)
    described = copy / "elements" / "table" / "ELEMENT.md"
    text = described.read_text(encoding="utf-8")
    row = "| fit | natural | the stub's `natural_size` gives 120 a column by 30 a row |\n"
    assert row in text
    described.write_text(text.replace(row, ""), encoding="utf-8")
    return copy, described


def test_a_blank_size_on_a_code_element_whose_size_is_nominal_is_a_warning_and_not_a_problem(tmp_path, folder):
    copy, _described = without_fit(tmp_path)
    lib = elements.open_library(str(copy), None)
    scene = _scene(NOMINAL)
    assert choreography.check(scene, TL, lib, folder) == []
    assert choreography.warnings(scene, lib) == [
        "line 26: scene A2, cast: 't': Size is blank and a table's own size (300 × 200) is nominal, so it will "
        "not be drawn at the size its data or text needs; give it a Size",
        "line 38: scene A2, mistake: 'wrong': Size is blank and a table's own size (300 × 200) is nominal, so it "
        "will not be drawn at the size its data or text needs; give it a Size",
    ]


def test_no_warning_for_an_element_that_offers_its_natural_size(lib):
    assert lib.element("table")["fit"] == "natural"
    assert choreography.warnings(_scene(NOMINAL), lib) == []


def test_no_warning_without_a_library_or_for_a_code_element_whose_size_is_not_said_to_be_nominal(tmp_path):
    assert choreography.warnings(_scene(NOMINAL), None) == []
    copy, described = without_fit(tmp_path)
    text = described.read_text(encoding="utf-8")
    assert "| size | 300 200 | nominal: " in text
    described.write_text(text.replace("| size | 300 200 | nominal: ", "| size | 300 200 | a design size: "),
                         encoding="utf-8")
    assert choreography.warnings(_scene(NOMINAL), elements.open_library(str(copy), None)) == []


def test_no_warning_and_no_crash_when_the_elements_file_is_not_there_or_has_no_size_row(tmp_path):
    copy, described = without_fit(tmp_path)
    opened = elements.open_library(str(copy), None)             # read while the files were whole
    whole = described.read_text(encoding="utf-8")
    described.write_text(whole.replace("| size | 300 200 | nominal: the natural size comes from its rows |\n", ""),
                         encoding="utf-8")
    assert choreography.warnings(_scene(NOMINAL), opened) == []
    described.unlink()
    assert choreography.warnings(_scene(NOMINAL), opened) == []


# ---- item 18 (request 16): an empty label is not a label

def test_an_empty_label_for_a_library_element_is_not_checked_and_others_still_are(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | 300x100 | rows=assets/sample.csv tab="" | none, as the element's description allows |
| u | table | 10 300 | 300x100 | rows=assets/sample.csv tab="Sheet 9" | |
| v | table | 400 300 | 300x100 | rows=assets/sample.csv tab=" " | spaces are still a label |
| w | table | 400 10 | 300x100 | rows=assets/sample.csv tab="Sample output" | |

### Moves

- cue 1: show t, u, v, w
- cue 2: w.tab ""
- cue 3: w.tab "Sheet 9"
"""
    assert _check(text, lib, folder) == [
        "line 26: scene A2, cast: 'u' draws 'Sheet 9', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 27: scene A2, cast: 'v' draws ' ', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
        "line 34: scene A2, moves: 'w' draws 'Sheet 9', which is not in the script's On screen list "
        "(Sample output, checked ✓)",
    ]


# ---- item 19 (request 17), 3: a member's own colours for an element's colour roles

OWN_COLOURS = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | 120 | colour.fill=correct | |
| q | pot | 200 10 | 120 | colour.rim=correct | no such role |
| r | pot | 400 10 | 120 | colour.fill=nosuch | |
| s | pill | 10 300 | | text="Sample output" colour.fill=correct | the pieces keep their own fill |

### Moves

- cue 1: show p, q, r, s
"""


def test_a_members_colour_must_be_a_role_the_element_has_and_a_colour_the_video_knows(lib, folder):
    scene = _scene(OWN_COLOURS)
    assert choreography.check(scene, TL, lib, folder, colours={"ink", "correct", "accent"}) == [
        "line 26: scene A2, cast: 'q': a pot has no colour role 'rim' (its colour roles are fill)",
        "line 27: scene A2, cast: 'r': 'colour.fill' names 'nosuch', which is not in the script's Colours or the "
        "brand's roles (accent, correct, ink)",
        "line 28: scene A2, cast: 's': a pill has no parameter 'colour.fill' (its parameters are text, size, fill, "
        "colour, anchor)",
    ]


def test_without_the_videos_colours_only_the_role_is_checked(lib, folder):
    assert choreography.check(_scene(OWN_COLOURS), TL, lib, folder) == [
        "line 26: scene A2, cast: 'q': a pot has no colour role 'rim' (its colour roles are fill)",
        "line 28: scene A2, cast: 's': a pill has no parameter 'colour.fill' (its parameters are text, size, fill, "
        "colour, anchor)",
    ]


# ---- item 19 (request 17), 5: any member may be turned

def test_rotate_is_a_number_on_a_library_member_too_and_is_not_one_of_the_elements_parameters(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | 120 | rotate=2.2 | |
| q | pot | 200 10 | 120 | rotate=lots | |

### Moves

- cue 1: show p, q
- cue 1, 0–0.6 s: p.rotate 0 → 180
- cue 2: q.rotate round
"""
    assert _check(text, lib, folder) == [
        "line 26: scene A2, cast: 'q': 'rotate' should be a number, not 'lots'",
        "line 32: scene A2, moves: 'q': 'rotate' should be a number, not 'round'",
    ]


# ---- item 20 (request 18), 4: a cast row chooses a data file's rows and columns

def test_a_rows_qualifier_is_checked_and_the_rows_counted_are_the_ones_chosen(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | 300x100 | rows=assets/sample.csv rows.columns="Sales Rep" rows.first=2 highlight.3=1 | 3 rows chosen |
| u | table | 10 10 | 300x100 | rows=assets/sample.csv rows.first=2 highlight.4=1 | row 4 is not among them |
| v | table | 10 10 | 300x100 | rows=assets/sample.csv rows.columns="Bonus" rows.where="Sales Rep = Nobody" | |
| w | pot | 10 10 | 100 | rows.first=2 | |
| x | table | 10 10 | 300x100 | rows.first=2 | |
| y | pill | 10 10 | | text="Sample output" rows.first=2 | |

### Moves

- cue 1: show t, u, v, w, x, y
"""
    assert _check(text, lib, folder) == [                   # the first cast row is line 25
        "line 26: scene A2, cast: 'u': 'highlight.4': assets/sample.csv has 3 rows as chosen",
        "line 27: scene A2, cast: 'v': 'rows.where': no row has 'Nobody' in column 'Sales Rep'",
        "line 27: scene A2, cast: 'v': 'rows.columns': no column 'Bonus' (the columns are Sales Rep, Commission)",
        "line 28: scene A2, cast: 'w': 'rows.first' qualifies 'rows', which a pot does not take as a data file",
        "line 29: scene A2, cast: 'x': a table needs 'rows'",
        "line 29: scene A2, cast: 'x': 'rows.first' qualifies 'rows', which is not given",
        "line 30: scene A2, cast: 'y': a pill has no parameter 'rows.first' (its parameters are text, size, fill, "
        "colour, anchor)",
    ]


def test_a_choice_that_cannot_be_made_is_refused_in_words_when_the_parameters_are_worked_out(lib, folder):
    from videotools import cli, perform
    scene = _scene(HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| v | table | 10 10 | 300x100 | rows=assets/sample.csv rows.columns="Bonus" | |
""")
    p = perform.Performance(scene["cast"], [], (40, 118, 1422, 818), TL, 1.0, lib, folder=folder)
    with pytest.raises(cli.Failure) as e:
        p.params(scene["cast"][0])
    assert str(e.value) == "'v': 'rows.columns': no column 'Bonus' (the columns are Sales Rep, Commission)"


# ---- item 22 (request 20): a text parameter read from a file, its lines chosen, and what an index counts

PLAN_TEXT = "Sales commission plan\n\n1. Eight per cent.\n2. A sector bonus.\n\n3. A timing bonus.\n4. Totalled per rep.\n"


@pytest.fixture
def planned(folder):
    with open(os.path.join(folder, "assets", "plan.txt"), "w", encoding="utf-8") as f:
        f.write(PLAN_TEXT)
    return folder


def test_a_text_file_is_checked_its_lines_chosen_and_indices_counted_against_them(lib, planned):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pot | 10 10 | 100 | text=assets/plan.txt text.skip=1 line-alpha.4=0 | four lines chosen |
| b | pot | 10 10 | 100 | text=assets/plan.txt text.skip=1 text.first=2 line-alpha.3=0 | |
| c | pot | 10 10 | 100 | text=assets/missing.txt | |
| d | pot | 10 10 | 100 | text="A line of its own" text.first=1 line-alpha.2=0 | the text itself, with a qualifier |
| e | pot | 10 10 | 100 | text=assets/plan.txt text.where="1 = x" | |
| f | table | 10 10 | 300x100 | rows=assets/sample.csv rows.skip=1 | |
| g | pot | 10 10 | 100 | text=assets/plan.txt text.skip=9 | |
| h | pot | 10 10 | 100 | text=assets/plan.txt text.first=1 tab-box.4=1 | a tab's index does not count lines |
| i | table | 10 10 | 300x100 | rows=assets/sample.csv note=assets/plan.txt note.first=1 highlight.3=1 | rows are what is counted |
| j | badge | h.tab.9 | | ok=yes | nor does a tab's anchor |
| k | pot | 10 10 | 100 | text="No file, no qualifier: the text itself" line-alpha.7=0 | one line, whatever it holds |

### Moves

- cue 1: show a, b, c, d, e, f, g, h, i, j, k
- cue 2: a.line-alpha.5 1 → 0
"""
    assert _check(text, lib, planned) == [                  # the first cast row is line 25
        "line 26: scene A2, cast: 'b': 'line-alpha.3': assets/plan.txt has 2 lines as chosen",
        f"line 27: scene A2, cast: 'c': 'text' names assets/missing.txt, which is not under {planned}",
        "line 28: scene A2, cast: 'd': 'line-alpha.2': the text has 1 line as chosen",
        "line 29: scene A2, cast: 'e': 'text.where' qualifies 'text', which is text: it takes skip and first",
        "line 30: scene A2, cast: 'f': 'rows.skip' qualifies 'rows', which is a data file: it takes where, first "
        "and columns",
        "line 31: scene A2, cast: 'g': 'text.skip': the text has only 5 lines",
        "line 35: scene A2, cast: 'k': 'line-alpha.7': the text has 1 line",          # item 23: a line is a line
        "line 40: scene A2, moves: 'a': 'line-alpha.5': assets/plan.txt has 4 lines as chosen",
    ]


def test_a_member_is_handed_a_files_text_or_its_chosen_lines_and_never_the_qualifiers(lib, planned):
    from videotools import perform
    scene = _scene(HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| whole | pot | 10 10 | 100 | text=assets/plan.txt | |
| rules | pot | 10 10 | 100 | text=assets/plan.txt text.skip=1 text.first=2 | |
| said | pot | 10 10 | 100 | text="Not a file: the text itself" | |
""")
    p = perform.Performance(scene["cast"], [], (40, 118, 1422, 818), TL, 1.0, lib, folder=planned)
    assert [p.params(m)[0] for m in scene["cast"]] == [
        {"text": PLAN_TEXT}, {"text": "1. Eight per cent.\n2. A sector bonus."}, {"text": "Not a file: the text itself"}]


def test_a_pieces_words_are_never_read_from_a_file_even_when_a_file_has_that_name(lib, planned):
    from videotools import perform
    scene = _scene(HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| tag | pill | 10 10 | | text=assets/plan.txt fill=accent | a label that happens to be a file's name |
""")
    p = perform.Performance(scene["cast"], [], (40, 118, 1422, 818), TL, 1.0, lib, folder=planned)
    assert p.params(scene["cast"][0])[0] == {"text": "assets/plan.txt", "fill": "accent"}


# ---- item 23: an index is counted as the element's description says (video-elements' `counts`)

def test_each_index_is_counted_as_the_description_says_rows_columns_and_never_tabs(lib, folder):
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | 300x100 | rows=assets/sample.csv highlight.4=1 cell-alpha.2.3=0 | 4 rows of 2 columns, no header switch |
| u | table | 10 10 | 300x100 | rows=assets/sample.csv highlight.5=1 cell-alpha.5.2=0 highlight.0=1 | |
| a | badge | t.cell.2.3 | | ok=yes | |
| b | badge | t.row.5 | | ok=yes | |

### Moves

- cue 1: show t, u, a, b
- cue 2: t.cell-alpha.4.3 1 → 0
"""
    assert _check(text, lib, folder) == [                   # the first cast row is line 25
        "line 25: scene A2, cast: 't': 'cell-alpha.2.3': assets/sample.csv has 2 columns",
        "line 26: scene A2, cast: 'u': 'highlight.5': assets/sample.csv has 4 rows",
        "line 26: scene A2, cast: 'u': 'cell-alpha.5.2': assets/sample.csv has 4 rows",
        "line 26: scene A2, cast: 'u': 'highlight.0' counts from 1",
        "line 27: scene A2, cast: 'a' is placed by 't'.'cell.2.3', but assets/sample.csv has 2 columns",
        "line 28: scene A2, cast: 'b' is placed by 't'.'row.5', but assets/sample.csv has 4 rows",
        "line 33: scene A2, moves: 't': 'cell-alpha.4.3': assets/sample.csv has 2 columns",
    ]


def _copy_of_the_library(tmp_path, change):
    """A copy of the invented library with its table's ELEMENT.md put through `change`."""
    import shutil
    copy = tmp_path / "library"
    shutil.copytree(INVENTED, copy)
    described = copy / "elements" / "table" / "ELEMENT.md"
    text = described.read_text(encoding="utf-8")
    changed = change(text)
    assert changed != text
    described.write_text(changed, encoding="utf-8")
    return elements.open_library(str(copy), None)


def test_a_header_row_is_not_a_data_row_when_the_element_has_the_switch_and_it_is_on(tmp_path, folder):
    with_header = _copy_of_the_library(tmp_path, lambda t: t.replace(
        "| rows | rows | first row is the header |",
        "| header | boolean true | the first row is a header |\n| rows | rows header=header | |"))
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t | table | 10 10 | 300x100 | rows=assets/sample.csv highlight.3=1 highlight.4=1 | the switch at its default, on |
| u | table | 10 10 | 300x100 | rows=assets/sample.csv header=no highlight.4=1 | off: every row is a data row |
| v | table | 10 10 | 300x100 | rows=assets/sample.csv rows.first=2 highlight.3=1 | the header and two rows chosen |

### Moves

- cue 1: show t, u, v
"""
    assert _check(text, with_header, folder) == [
        "line 25: scene A2, cast: 't': 'highlight.4': assets/sample.csv has 3 data rows",
        "line 27: scene A2, cast: 'v': 'highlight.3': assets/sample.csv has 2 data rows as chosen",
    ]


def test_a_library_that_does_not_say_what_an_index_counts_is_too_old_and_is_refused_when_opened(tmp_path):
    from videotools import cli
    with pytest.raises(cli.Failure) as e:       # the copy's table has no `## Indexes`, as before video-elements d203f0a
        _copy_of_the_library(tmp_path, lambda t: t[:t.index("## Indexes")] + t[t.index("## Colours"):])
    folder = tmp_path / "library"
    assert str(e.value) == (f"the video-elements library at {folder} is older than these tools need: the "
                            "description of table does not say what its indexes count (no 'counts'); update the "
                            "video-elements repository")
    assert e.value.code == cli.REFUSED
