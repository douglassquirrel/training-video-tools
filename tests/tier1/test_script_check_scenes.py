"""videotools.script.check: Colours, Insets, scene properties, cues and side panels."""

from tests.tier1.test_script_check_settings import problems, video  # noqa: F401
from tests.tier1.test_script_reads import TWO_SCENES


def test_a_colour_must_be_six_hex_digits(video):
    text = TWO_SCENES.replace("| ribbon | #AA3355 | |", "| ribbon | red | |\n| bow | #ABC | |")
    assert problems(text, video) == ["line 25: Colours: 'ribbon' is not #RRGGBB: red",
                                     "line 26: Colours: 'bow' is not #RRGGBB: #ABC"]


def test_an_inset_must_be_four_whole_numbers(video):
    text = TWO_SCENES.replace("| A | 10 20 300 400 | |", "| A | 10 20 300 | |")
    assert problems(text, video) == ["line 31: Insets: 'A' should be four whole numbers x0 y0 x1 y1: 10 20 300"]


def test_a_scene_key_used_twice_is_a_problem(video):
    text = TWO_SCENES.replace("## Scene end: End card", "## Scene A: End card")
    assert problems(text, video) == ["line 67: scene A: key used twice (first at line 33)"]


def test_an_unknown_scene_property_is_a_problem_unless_it_starts_with_x(video):
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_loop | |\n| colour | red | |\n| x-note | ok | |")
    assert problems(text, video) == ["line 42: scene A: unknown property 'colour'"]


def test_kind_must_be_title_step_or_end(video):
    text = TWO_SCENES.replace("| kind | end | |", "| kind | credits | |")
    assert problems(text, video) == ["line 71: scene end: kind must be title, step or end, not 'credits'"]


def test_a_lettered_step_needs_a_source(video):
    text = TWO_SCENES.replace("| source | Figure 1, panel A | |\n", "")
    assert problems(text, video) == ["line 33: scene A: a lettered step needs a 'source'"]


def test_an_inset_the_scene_names_must_be_in_insets(video):
    text = TWO_SCENES.replace("| inset | A | |", "| inset | Z | |")
    assert problems(text, video) == ["line 39: scene A: inset 'Z' is not in Insets"]


def test_extra_must_be_a_number_of_seconds(video):
    text = TWO_SCENES.replace("| extra | 4.0 | |", "| extra | four | |")
    assert problems(text, video) == ["line 72: scene end: extra should be a number of seconds, not 'four'"]


def test_side_panel_must_be_one_of_the_kinds(video):
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_loop | |\n| side-panel | bullets | |")
    assert problems(text, video) == ["line 42: scene A: side-panel 'bullets' not understood"]


def test_a_side_panel_kind_that_needs_a_list_is_refused_without_one(video):
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_loop | |\n| side-panel | steps | |")
    text = text.replace("### Side panel\n\n- Loop, don't pull\n  - added: the figure's note.\n", "")
    assert problems(text, video) == ["line 42: scene A: side-panel 'steps' but no Side panel list"]


def test_a_side_panel_cue_number_must_exist(video):
    text = TWO_SCENES.replace("| code | first_loop | |", "| code | first_loop | |\n| side-panel | checklist 3 | |")
    assert problems(text, video) == ["line 42: scene A: side-panel refers to cue 3, which doesn't exist"]


def test_a_scene_that_is_not_the_end_needs_cues_or_extra(video):
    text = TWO_SCENES.replace("| kind | end | |\n| extra | 4.0 | |\n", "")
    assert problems(text, video) == ["line 67: scene end: no narration and no 'extra'"]


def test_cues_must_be_numbered_from_one_without_gaps(video):
    text = TWO_SCENES.replace("2. Don't pull it tight yet.", "3. Don't pull it tight yet.")
    assert problems(text, video) == ["line 47: scene A: cue numbered 3 where 2 was expected"]


def test_min_must_be_seconds(video):
    text = TWO_SCENES.replace("- min: 2.5", "- min: two")
    assert problems(text, video) == ["line 45: scene A cue 1: min should be a number of seconds, not 'two'"]


def test_an_unknown_cue_sub_bullet_is_a_problem(video):
    text = TWO_SCENES.replace("   - min: 2.5\n", "   - min: 2.5\n   - note: a note\n")
    assert problems(text, video) == ["line 45: scene A cue 1: unknown sub-bullet 'note'"]


def test_a_mistake_needs_both_labels(video):
    text = TWO_SCENES.replace("- mistake: Pulled tight / Left loose", "- mistake: Pulled tight")
    assert problems(text, video) == ["line 47: scene A cue 2: mistake needs '<wrong> / <right>'"]


def test_at_most_one_mistake_per_scene(video):
    text = TWO_SCENES.replace("   - min: 2.5\n", "   - min: 2.5\n   - mistake: Too soon / In time\n")
    assert problems(text, video) == ["line 33: scene A: 2 mistakes; one per scene"]


def test_step_needs_a_steps_side_panel_and_an_item_that_exists(video):
    text = TWO_SCENES.replace("   - min: 2.5\n", "   - min: 2.5\n   - step: 1\n")
    assert problems(text, video) == ["line 45: scene A cue 1: step 1 needs 'side-panel: steps'"]
    text = text.replace("| code | first_loop | |", "| code | first_loop | |\n| side-panel | steps | |")
    text = text.replace("- step: 1", "- step: 2")
    assert problems(text, video) == ["line 46: scene A cue 1: step 2 is not in the Side panel list (1 item)"]


def test_added_must_say_where_it_comes_from(video):
    text = TWO_SCENES.replace("- added: our inference from panel B.", "- added:")
    text = text.replace("  - added: the figure's note.", "  - added:")
    assert problems(text, video) == ["line 47: scene A cue 2: 'added:' must say where it comes from",
                                     "line 54: scene A, side panel: 'added:' must say where it comes from"]
