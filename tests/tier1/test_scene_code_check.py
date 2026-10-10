"""scenes.check_code: a script's scene code checked without running it (check-script, Python 3.9)."""

import os

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import scenes, script

GOOD = "def draw(frame):\n    pass\n\n\ndef mistake(frame, rect):\n    pass\n\n\ndef right_way(frame, rect):\n    pass\n"


def check(text, video, modules=None):
    (video / "script.md").write_text(text, encoding="utf-8")
    folder = video / "scenes"
    folder.mkdir(exist_ok=True)
    for name, body in (modules if modules is not None else {"first_loop": GOOD, "end_card": "def draw(frame):\n    pass\n"}).items():
        (folder / f"{name}.py").write_text(body)
    data, structural = script.parse(text)
    assert structural == []
    return scenes.check_code(str(folder), data)


def test_a_well_formed_script_with_its_modules_has_no_problems(video):
    assert check(TWO_SCENES, video) == []


def test_a_step_scene_without_code_is_a_problem_at_its_heading_and_a_card_without_is_not(video):
    text = TWO_SCENES.replace("| code | first_loop | |\n", "").replace("| code | end_card | |\n", "")
    assert check(text, video) == ["line 33: scene A has no 'code' property and no Cast, so nothing can draw it"]


def test_a_code_whose_module_is_missing_names_the_path(video):
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_lopo | |")
    path = os.path.join(str(video / "scenes"), "first_lopo.py")
    assert check(text, video) == [f"line 41: scene A: no scene code {path} (the scene's 'code' is 'first_lopo')"]


def test_a_module_missing_a_function_the_scene_needs_names_module_function_and_why(video):
    path = os.path.join(str(video / "scenes"), "first_loop.py")
    only_draw = "def draw(frame):\n    pass\n"
    assert check(TWO_SCENES, video, {"first_loop": only_draw, "end_card": only_draw}) == [
        f"line 41: scene A: {path} has no mistake(frame, rect) function, and cue 2 is a mistake",
        f"line 41: scene A: {path} has no right_way(frame, rect) function, and cue 2 is a mistake"]
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_loop | |\n| side-panel | custom knot 1 | |")
    assert check(text, video, {"first_loop": GOOD, "end_card": only_draw}) == [
        f"line 41: scene A: {path} has no panel(frame, rect) function, and its side-panel is 'custom knot 1'"]


def test_a_module_that_does_not_parse_is_reported_by_line_not_run(video):
    path = os.path.join(str(video / "scenes"), "first_loop.py")
    bad = "import os\nos.remove('never')\ndef draw(frame)\n    pass\n"           # a syntax error on line 3
    assert check(TWO_SCENES, video, {"first_loop": bad, "end_card": "def draw(frame):\n    pass\n"}) == [
        f"line 41: scene A: {path} could not be parsed: line 3: expected ':'"]


def test_a_missing_scene_code_folder_is_one_problem(video):
    (video / "script.md").write_text(TWO_SCENES, encoding="utf-8")
    data, _ = script.parse(TWO_SCENES)
    folder = str(video / "nowhere")
    assert scenes.check_code(folder, data) == [f"line 19: Settings: scene-code folder not found: {folder}"]


DESCRIBED = """
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| a | pill | 0 0 | | text="near side" | |

### Moves

- cue 1: show a

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| b | badge | 0 0 | | ok=no | |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| c | badge | 0 0 | | ok=yes | |
"""


def test_a_described_step_scene_needs_no_code_and_its_module_if_any_no_draw_or_panel_functions(video):
    text = TWO_SCENES.replace("| code | first_loop | |\n", "")
    assert check(text, video) == ["line 33: scene A has no 'code' property and no Cast, so nothing can draw it"]
    marker = "## Scene end: End card"
    assert text.count(marker) == 1
    described = text.replace(marker, DESCRIBED.lstrip("\n") + "\n" + marker)
    assert check(described, video) == []
    with_code = TWO_SCENES.replace(marker, DESCRIBED.lstrip("\n") + "\n" + marker)
    assert check(with_code, video, {"first_loop": "x = 1\n", "end_card": "def draw(frame):\n    pass\n"}) == []
