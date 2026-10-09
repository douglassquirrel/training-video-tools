"""videotools.script.read: the whole thing, refusing with every problem; typed settings."""

import os

import pytest

from tests.tier1.test_script_check_settings import video  # noqa: F401
from tests.tier1.test_script_reads import TWO_SCENES
from videotools import script

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "videos", "paper-boat", "script.md")


def test_read_returns_the_data_of_a_well_formed_script(video):
    path = video / "script.md"
    path.write_text(TWO_SCENES, encoding="utf-8")
    data = script.read(str(path))
    assert data["title"] == "Tying a Bow"
    assert [s["key"] for s in data["scenes"]] == ["A", "end"]


def test_read_refuses_a_malformed_script_with_every_problem(video):
    path = video / "script.md"
    text = TWO_SCENES.replace("| voice | af_heart | |\n", "").replace("| ribbon | #AA3355 | |", "| ribbon | red | |")
    path.write_text(text, encoding="utf-8")
    with pytest.raises(script.ScriptError) as e:
        script.read(str(path))
    assert e.value.problems == ["Settings: 'voice' is missing", "line 24: Colours: 'ribbon' is not #RRGGBB: red"]
    assert str(e.value) == "%s: 2 problems:\n  - Settings: 'voice' is missing\n  - line 24: Colours: 'ribbon' is not #RRGGBB: red" % path


def test_read_refuses_a_missing_file_by_name(tmp_path):
    with pytest.raises(script.ScriptError) as e:
        script.read(str(tmp_path / "none.md"))
    assert e.value.problems == ["no such file: %s" % (tmp_path / "none.md")]


def test_read_includes_structural_problems_from_parsing(video):
    path = video / "script.md"
    path.write_text(TWO_SCENES.replace("- first loop\n", "- first loop\nstray\n"), encoding="utf-8")
    with pytest.raises(script.ScriptError) as e:
        script.read(str(path))
    assert e.value.problems == ["line 60: scene A, on screen: not a list item: stray"]


def test_the_example_script_reads_with_no_problems():
    data = script.read(EXAMPLE)
    assert [s["key"] for s in data["scenes"]] == ["title", "A", "B", "B2", "C", "R", "end"]


def test_settings_are_typed_with_the_formats_defaults(video):
    data = script.parse(TWO_SCENES)[0]
    s = script.settings(data)
    assert (s["size"], s["fps"], s["speed"], s["quality"]) == ((1920, 1080), 30, 0.98, 18)
    assert (s["lead"], s["cue-gap"], s["tail"], s["fade"]) == (0.7, 0.55, 1.0, (0.45, 0.4))
    assert (s["subtitle"], s["source-image"], s["credit"]) == ("", "", "")
    assert (s["title"], s["brand"], s["output"], s["scene-code"]) == ("Tying a Bow", "demo", "out/Bow.mp4", "scenes/")


def test_settings_given_in_the_script_win_over_the_defaults():
    data = script.read(EXAMPLE)
    s = script.settings(data)
    assert (s["lead"], s["cue-gap"], s["tail"], s["quality"], s["fade"]) == (0.7, 0.55, 1.0, 18, (0.45, 0.4))
    data["settings"].update({"lead": "1.5", "quality": "20", "fade": "0.3 0.2"})
    s = script.settings(data)
    assert (s["lead"], s["quality"], s["fade"]) == (1.5, 20, (0.3, 0.2))


def test_scene_kind_extra_and_side_panel_are_typed():
    data = script.read(EXAMPLE)
    by_key = {s["key"]: s for s in data["scenes"]}
    assert [script.kind(by_key[k]) for k in ("title", "A", "end")] == ["title", "step", "end"]
    assert (script.extra(by_key["end"]), script.extra(by_key["A"])) == (4.0, 0.0)
    assert script.side_panel(by_key["A"]) == ("key-points", None, None)
    assert script.side_panel(by_key["B"]) == ("steps", None, None)
    assert script.side_panel(by_key["B2"]) == ("custom", "strip-fold", 1)
    assert script.side_panel(by_key["R"]) == ("checklist", None, 2)
    assert script.side_panel(by_key["title"]) == ("none", None, None)


def test_a_cues_spoken_text_minimum_and_mistake_labels_are_typed():
    data = script.read(EXAMPLE)
    a = data["scenes"][1]
    assert script.spoken(a["cues"][0]) == "Step A. Fold the sheet in half, top edge to bottom edge."
    assert script.spoken(data["scenes"][0]["cues"][1]) == "This film follows Figure seven, one fold at a time."
    assert (script.minimum(a["cues"][0]), script.minimum({"n": 1, "text": "x", "line": 1})) == (3.0, 0.0)
    assert script.mistake(a["cues"][1]) == ("Folded corner to corner", "Folded edge to edge")
    assert script.mistake(a["cues"][0]) is None


def test_folder_is_the_scripts_own_folder():
    assert script.folder(EXAMPLE) == os.path.dirname(os.path.abspath(EXAMPLE))
