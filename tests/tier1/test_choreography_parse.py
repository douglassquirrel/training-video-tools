"""videotools.choreography: a scene's Cast, Moves, Mistake and Right way sections read into plain
data by script.parse, and every malformed line a problem naming its line (PLAN.md item 15)."""

from videotools import script

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
"""

CAST = """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sample-tag | pill | sample.top-left + 0 -30 | | text="Sample output" size=22 fill=sheet-tab | a note |
| sample | table | 70 132 | | rows=assets/sample.csv widths="300 230" rows-shown=0 cell-alpha.3.2=0 | |
| checker | hand | sample.row.1 + 190 40 | 80x60 | angle=3.3 |
| pot | pot | centre | 120 | |
"""

MOVES = """
### Moves

- cue 1: show sample-tag, sample
- cue 1, 0.5–1.7 s: sample.rows-shown 0 → 3
- cue 2, 1.0 s: sample.highlight.3 0 -> 1
- cue 2, end-1.2–end-0.4 s: move checker to sample.cell.3.2
- cue 2, over the cue: pot plain → cracked
- cue 3, -0.3–0.2 s: hide checker
- cue 3: sample.highlight-colour.1 correct
"""

PANELS = """
### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | badge | 610 600 | | ok=no r=30 | |

- 0.4–0.8 s: show wrong

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| answers-only | pill | 345 640 | | text="answers only" fill=correct anchor=centre | |
"""


def _scene(text):
    data, problems = script.parse(text)
    return data["scenes"][0], problems


def test_a_scene_without_the_sections_has_an_empty_cast_moves_and_panels():
    scene, problems = _scene(HEAD)
    assert problems == []
    assert (scene["cast"], scene["moves"], scene["panels"]) == ([], [], {})


def test_cast_rows_read_back_with_where_size_and_parameters_parsed():
    scene, problems = _scene(HEAD + CAST)
    assert problems == []
    names = [m["name"] for m in scene["cast"]]
    assert names == ["sample-tag", "sample", "checker", "pot"]
    tag, sample, checker, pot = scene["cast"]
    assert tag["element"] == "pill" and tag["line"] == 24
    assert tag["where"] == {"kind": "anchor", "member": "sample", "anchor": "top-left", "dx": 0.0, "dy": -30.0}
    assert tag["size"] is None
    assert tag["params"] == {"text": "Sample output", "size": "22", "fill": "sheet-tab"}
    assert sample["where"] == {"kind": "pixels", "x": 70.0, "y": 132.0}
    assert sample["params"] == {"rows": "assets/sample.csv", "widths": "300 230", "rows-shown": "0",
                                "cell-alpha.3.2": "0"}
    assert checker["where"] == {"kind": "anchor", "member": "sample", "anchor": "row.1", "dx": 190.0, "dy": 40.0}
    assert checker["size"] == {"w": 80.0, "h": 60.0}
    assert pot["where"] == {"kind": "region", "name": "centre"}
    assert pot["size"] == {"w": 120.0, "h": None} and pot["params"] == {}


def test_moves_read_back_with_cue_times_and_actions():
    scene, problems = _scene(HEAD + CAST + MOVES)
    assert problems == []
    m = scene["moves"]
    assert [x["cue"] for x in m] == [1, 1, 2, 2, 2, 3, 3]
    assert m[0]["start"] == ("start", 0.0) and m[0]["end"] == ("start", 0.6)
    assert m[0]["action"] == {"kind": "show", "names": ["sample-tag", "sample"]}
    assert m[0]["line"] == 31
    assert m[1]["start"] == ("start", 0.5) and m[1]["end"] == ("start", 1.7)
    assert m[1]["action"] == {"kind": "param", "name": "sample", "param": "rows-shown", "from": "0", "to": "3"}
    assert m[2]["start"] == ("start", 1.0) and m[2]["end"] == ("start", 1.6)
    assert m[2]["action"] == {"kind": "param", "name": "sample", "param": "highlight.3", "from": "0", "to": "1"}
    assert m[3]["start"] == ("end", -1.2) and m[3]["end"] == ("end", -0.4)
    assert m[3]["action"] == {"kind": "move", "name": "checker",
                              "to": {"kind": "anchor", "member": "sample", "anchor": "cell.3.2", "dx": 0.0, "dy": 0.0}}
    assert m[4]["start"] == ("start", 0.0) and m[4]["end"] == ("end", 0.0)
    assert m[4]["action"] == {"kind": "state", "name": "pot", "from": "plain", "to": "cracked"}
    assert m[5]["start"] == ("start", -0.3) and m[5]["end"] == ("start", 0.2)
    assert m[5]["action"] == {"kind": "hide", "names": ["checker"]}
    assert m[6]["action"] == {"kind": "set", "name": "sample", "param": "highlight-colour.1", "value": "correct"}


def test_the_panels_read_back_each_with_a_cast_and_moves_timed_from_the_rise():
    scene, problems = _scene(HEAD + CAST + MOVES + PANELS)
    assert problems == []
    assert sorted(scene["panels"]) == ["mistake", "right way"]
    wrong = scene["panels"]["mistake"]
    assert [m["name"] for m in wrong["cast"]] == ["wrong"]
    assert wrong["cast"][0]["params"] == {"ok": "no", "r": "30"}
    assert wrong["moves"] == [{"cue": None, "start": ("start", 0.4), "end": ("start", 0.8),
                               "action": {"kind": "show", "names": ["wrong"]}, "line": 45}]
    right = scene["panels"]["right way"]
    assert [m["name"] for m in right["cast"]] == ["answers-only"] and right["moves"] == []


def test_a_cast_table_with_the_wrong_header_is_one_problem_and_its_rows_are_not_read():
    text = HEAD + """
### Cast

| Name | Element | Where | Parameters | Notes |
|---|---|---|---|---|
| a | pill | 1 2 | text=x | |
| b | pill |
"""
    scene, problems = _scene(text)
    assert problems == [
        "line 22: scene A2, cast: the table's columns are Name | Element | Where | Size | Parameters | Notes, "
        "not Name | Element | Where | Parameters | Notes; its rows are not read",
    ]
    assert scene["cast"] == []


def test_a_bad_name_a_repeated_name_a_where_a_size_and_a_parameter_pair_not_understood_are_problems():
    text = HEAD + """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sam ple | pill | 1 2 | | | |
| a | pill | 1 2 | | | |
| a | pill | somewhere | | | |
| b | pill | 1 2 | big | | |
| c | pill | sample.row | | text | |
| d | pill | 1 2 3 | 10x | size=22 colour | |
| e | pill |
"""
    scene, problems = _scene(text)
    assert problems == [
        "line 24: scene A2, cast: 'sam ple' is not a name (letters, digits and hyphens)",
        "line 26: scene A2, cast: 'a' is already in the cast (line 25)",
        "line 26: scene A2, cast: Where 'somewhere' is not X Y in area pixels, a region (left, right, centre, "
        "top-left, top-right, bottom-left, bottom-right, full) or a member's anchor like sample.row.3 + 40 -12",
        "line 27: scene A2, cast: Size 'big' is not W or WxH in pixels, or blank",
        "line 28: scene A2, cast: Parameters: 'text' is not name=value",
        "line 29: scene A2, cast: Where '1 2 3' is not X Y in area pixels, a region (left, right, centre, "
        "top-left, top-right, bottom-left, bottom-right, full) or a member's anchor like sample.row.3 + 40 -12",
        "line 29: scene A2, cast: Size '10x' is not W or WxH in pixels, or blank",
        "line 29: scene A2, cast: Parameters: 'colour' is not name=value",
        "line 30: scene A2, cast: a row needs five cells (Name | Element | Where | Size | Parameters), this one has 2",
    ]
    assert [m["name"] for m in scene["cast"]] == ["a"]      # a row with any problem is left out


def test_a_move_not_understood_a_scene_move_without_a_cue_and_a_panel_move_with_one_are_problems():
    text = HEAD + CAST + """
### Moves

- cue 1: wave sample
- 0.4 s: show sample
- cue 1, soon: show sample
- cue 1: move sample to nowhere
- prose in the list
just prose

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | badge | 610 600 | | ok=no | |

- cue 2: show wrong
- what is this
"""
    scene, problems = _scene(text)
    assert problems == [
        "line 31: scene A2, moves: 'wave sample' is not show NAME, hide NAME, move NAME to WHERE, NAME.PARAM A → B, "
        "NAME.PARAM VALUE or NAME STATE → STATE",
        "line 32: scene A2, moves: a scene's move starts 'cue N' (a panel's moves have no cue)",
        "line 33: scene A2, moves: 'cue 1, soon: show sample' is not cue N[, A s | A–B s | over the cue]: ACTION",
        "line 34: scene A2, moves: Where 'nowhere' is not X Y in area pixels, a region (left, right, centre, "
        "top-left, top-right, bottom-left, bottom-right, full) or a member's anchor like sample.row.3 + 40 -12",
        "line 35: scene A2, moves: 'prose in the list' is not cue N[, A s | A–B s | over the cue]: ACTION",
        "line 36: scene A2, moves: not a move (a list item '- cue N[, TIME]: ACTION'): just prose",
        "line 44: scene A2, mistake: a panel's moves have no 'cue N': times count from the panel's rise",
        "line 45: scene A2, mistake: 'what is this' is not show NAME, hide NAME, move NAME to WHERE, "
        "NAME.PARAM A → B, NAME.PARAM VALUE or NAME STATE → STATE",
    ]
    assert len(scene["moves"]) == 0 and scene["panels"]["mistake"]["moves"] == []
