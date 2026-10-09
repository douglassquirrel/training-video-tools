"""videotools.script: what the parser skips, what passes through, and the structural problems."""

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import script

NOTES = """## Notes

Prose for people between two scenes, with a table the tools must not read:

| Key | Value |
|---|---|
| title | Not the title |

### Not a narration heading? No: a ### inside notes is outside a scene, so leave it out here.
"""


def _without_lines(data):
    """The data with every 'line' dropped, so two scripts can be compared across an insertion."""
    out = {k: v for k, v in data.items() if k != "scenes"}
    out["scenes"] = []
    for sc in data["scenes"]:
        s = {k: v for k, v in sc.items() if k != "line"}
        for name in ("cues", "side", "screen"):
            s[name] = [{k: v for k, v in it.items() if k != "line"} for it in sc[name]]
        out["scenes"].append(s)
    return out


def test_an_unrecognised_section_between_scenes_is_skipped_table_and_all():
    notes = "\n".join(line for line in NOTES.splitlines() if not line.startswith("###")) + "\n"
    with_notes = TWO_SCENES.replace("## Scene end:", notes + "\n## Scene end:")
    assert _without_lines(script.parse(with_notes)[0]) == _without_lines(script.parse(TWO_SCENES)[0])
    assert script.parse(with_notes)[1] == []


def test_prose_inside_a_scene_section_before_its_table_is_skipped():
    text = TWO_SCENES.replace("## Scene A: First loop\n", "## Scene A: First loop\n\nA note for people.\n")
    assert _without_lines(script.parse(text)[0]) == _without_lines(script.parse(TWO_SCENES)[0])


def test_unicode_and_middle_dot_pass_through_a_table_cell_and_a_cue():
    text = TWO_SCENES.replace("| scene-code | scenes/ | |",
                              "| scene-code | scenes/ | |\n| source-label | FIG. 7 · ORIGINAL — café | |")
    text = text.replace("1. Step A. Make the first loop.", "1. Step A. Make the first loop, naïvely · 45°.")
    data = script.parse(text)[0]
    assert data["settings"]["source-label"] == "FIG. 7 · ORIGINAL — café"
    assert data["scenes"][0]["cues"][0]["text"] == "Step A. Make the first loop, naïvely · 45°."


def test_a_level_three_heading_outside_a_scene_is_a_problem_naming_its_line():
    text = TWO_SCENES.replace("## Colours\n", "### Narration\n\n## Colours\n")
    assert script.parse(text)[1] == ["line 21: '### Narration' outside a scene"]


def test_a_line_in_narration_that_is_not_a_cue_is_a_problem_naming_its_line():
    text = TWO_SCENES.replace("   - min: 2.5\n", "   - min: 2.5\nA stray sentence.\n")
    assert script.parse(text)[1] == ["line 47: scene A: not a cue or a cue's sub-bullet: A stray sentence."]


def test_a_line_in_a_list_that_is_not_an_item_is_a_problem_naming_its_line():
    text = TWO_SCENES.replace("- first loop\n", "- first loop\nstray\n")
    assert script.parse(text)[1] == ["line 60: scene A, on screen: not a list item: stray"]


def test_a_sub_bullet_before_any_cue_is_a_problem():
    text = TWO_SCENES.replace("### Narration\n\n1. Step A.", "### Narration\n\n   - min: 2.5\n1. Step A.")
    assert script.parse(text)[1] == ["line 45: scene A: not a cue or a cue's sub-bullet: - min: 2.5"]
