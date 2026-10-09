"""videotools.scenes: a scene's module is found by its code, checked, and given a frame to draw with."""

import pytest

from videotools import cli, scenes

SCENE = {"key": "A", "name": "A", "line": 1, "props": {"code": "fold"}, "cues": [], "side": [],
         "screen": [{"text": "near side", "line": 2}, {"text": "far side", "line": 3}]}


def module(tmp_path, body):
    (tmp_path / "fold.py").write_text(body)
    return str(tmp_path)


def test_the_module_named_by_code_is_loaded_from_the_scene_code_folder(tmp_path):
    folder = module(tmp_path, "def draw(frame):\n    frame.drawn = True\n")
    mod = scenes.load(folder, SCENE)
    f = scenes.Frame(ctx=None, t=1.0, timeline=None, scene=SCENE, colours={}, brand=None, area=(0, 0, 10, 10))
    mod.draw(f)
    assert f.drawn is True


def test_a_missing_module_or_draw_function_is_a_useful_error(tmp_path):
    with pytest.raises(cli.Failure) as e:
        scenes.load(str(tmp_path), SCENE)
    assert str(e.value) == f"scene A: no scene code {tmp_path / 'fold.py'} (the scene's 'code' is 'fold')"
    folder = module(tmp_path, "x = 1\n")
    with pytest.raises(cli.Failure) as e:
        scenes.load(folder, SCENE)
    assert str(e.value) == f"scene A: {tmp_path / 'fold.py'} has no draw(frame) function"


def test_a_scene_without_a_code_property_is_refused(tmp_path):
    with pytest.raises(cli.Failure) as e:
        scenes.load(str(tmp_path), dict(SCENE, props={}))
    assert str(e.value) == "scene A has no 'code' property, so no scene code can be found for it"


def test_a_scene_with_a_mistake_needs_both_panel_functions(tmp_path):
    folder = module(tmp_path, "def draw(frame): pass\ndef mistake(frame, rect): pass\n")
    scene = dict(SCENE, cues=[{"n": 1, "text": "x", "line": 5, "mistake": "A / B"}])
    with pytest.raises(cli.Failure) as e:
        scenes.load(folder, scene)
    assert str(e.value) == f"scene A: {tmp_path / 'fold.py'} has no right_way(frame, rect) function, and cue 1 is a mistake"


def test_a_custom_side_panel_needs_a_panel_function(tmp_path):
    folder = module(tmp_path, "def draw(frame): pass\n")
    scene = dict(SCENE, props={"code": "fold", "side-panel": "custom hem 1"}, cues=[{"n": 1, "text": "x", "line": 5}])
    with pytest.raises(cli.Failure) as e:
        scenes.load(folder, scene)
    assert str(e.value) == f"scene A: {tmp_path / 'fold.py'} has no panel(frame, rect) function, and its side-panel is 'custom hem 1'"


def test_a_module_that_fails_to_import_reports_the_error(tmp_path):
    folder = module(tmp_path, "def draw(frame)\n")
    with pytest.raises(cli.Failure) as e:
        scenes.load(folder, SCENE)
    assert str(e.value).startswith(f"scene A: {tmp_path / 'fold.py'} could not be loaded: ")
    assert "SyntaxError" in str(e.value)


def test_label_returns_text_that_the_script_lists_and_refuses_text_it_does_not():
    f = scenes.Frame(ctx=None, t=0.0, timeline=None, scene=SCENE, colours={}, brand=None, area=(0, 0, 10, 10))
    assert f.label("near side") == "near side"
    with pytest.raises(cli.Failure) as e:
        f.label("near sid")
    assert str(e.value) == "scene A: the scene code draws 'near sid', which is not in the script's On screen list (near side, far side)"


def test_loading_twice_gives_the_same_module_and_the_folder_is_not_left_on_sys_path(tmp_path):
    import sys
    folder = module(tmp_path, "def draw(frame): pass\n")
    a = scenes.load(folder, SCENE)
    b = scenes.load(folder, SCENE)
    assert a is b and folder not in sys.path


def test_a_title_or_end_scene_without_code_has_no_module_and_a_step_scene_still_must(tmp_path):
    assert scenes.load(str(tmp_path), dict(SCENE, props={"kind": "title"})) is None
    assert scenes.load(str(tmp_path), dict(SCENE, props={"kind": "end"})) is None
    with pytest.raises(cli.Failure) as e:
        scenes.load(str(tmp_path), dict(SCENE, props={"kind": "step"}))
    assert str(e.value) == "scene A has no 'code' property, so no scene code can be found for it"
