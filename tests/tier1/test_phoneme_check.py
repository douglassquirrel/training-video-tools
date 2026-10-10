"""check_script.phoneme_problems: bad [[…]] spans in say: lines, and a span in a caption."""

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import check_script, script

SAY = "   - say: Don't pull it tight yet. It needs room for the second loop!"      # line 48 of the fixture


def problems(text):
    data, structural = script.parse(text)
    assert structural == []
    return check_script.phoneme_problems(data)


def test_a_say_with_a_good_span_or_none_has_no_problems():
    assert problems(TWO_SCENES) == []
    assert problems(TWO_SCENES.replace(SAY, "   - say: Don't pull it [[tˈaɪt]] yet.")) == []


def test_an_unclosed_empty_or_unknown_symbol_span_is_a_problem_at_the_says_line():
    assert problems(TWO_SCENES.replace(SAY, "   - say: Don't pull it [[tˈaɪt yet.")) == [
        "line 48: scene A cue 2 say: '[[' at character 15 is never closed with ']]'"]
    assert problems(TWO_SCENES.replace(SAY, "   - say: Don't [[]] pull it.")) == [
        "line 48: scene A cue 2 say: '[[]]' at character 7 is empty"]
    assert problems(TWO_SCENES.replace(SAY, "   - say: [[kar$]] all.")) == [
        "line 48: scene A cue 2 say: '$' (U+0024) in '[[kar$]]' is not a symbol the voice knows"]


def test_a_span_in_a_caption_is_a_problem_since_it_would_show_on_screen():
    text = TWO_SCENES.replace("1. Step A. Make the first loop.", "1. Step A. Make the [[first]] loop.")
    assert problems(text) == [
        "line 45: scene A cue 1 caption 'Step A. Make the [[first]] loop.' holds '[[', which would show on screen; "
        "phoneme spans go in say:"]
