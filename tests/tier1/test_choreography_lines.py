"""videotools.choreography.select_lines: the lines of a text a cast row chooses with `text.skip`
and `text.first` (PLAN.md item 22, 2). Pure: text in, text out."""

from videotools import choreography

PLAN = "Sales commission plan\n\n1. Eight per cent.\n2. A sector bonus.\n\n3. A timing bonus.\n4. Totalled per rep.\n"


def _select(**qualifiers):
    return choreography.select_lines(PLAN, {f"text.{k}": v for k, v in qualifiers.items()}, "text")


def test_with_no_qualifier_the_text_is_exactly_as_it_is():
    assert choreography.select_lines(PLAN, {"text": "assets/plan.txt", "title": "Plan"}, "text") == (PLAN, [])


def test_skip_drops_leading_lines_and_first_keeps_leading_lines_blank_ones_not_counted():
    assert _select(skip="1") == ("1. Eight per cent.\n2. A sector bonus.\n3. A timing bonus.\n4. Totalled per rep.", [])
    assert _select(first="2") == ("Sales commission plan\n1. Eight per cent.", [])


def test_skip_comes_before_first_however_they_are_written():
    assert _select(first="2", skip="2") == ("2. A sector bonus.\n3. A timing bonus.", [])
    assert _select(skip="4", first="9") == ("4. Totalled per rep.", [])


def test_what_cannot_be_done_is_a_problem_in_words():
    assert _select(skip="5")[1] == ["'text.skip': the text has only 5 lines"]
    assert _select(skip="0")[1] == ["'text.skip' should be a whole number above 0, not '0'"]
    assert _select(first="two")[1] == ["'text.first' should be a whole number above 0, not 'two'"]


def test_lines_counts_the_lines_that_are_not_blank():
    assert choreography.lines_of(PLAN) == ["Sales commission plan", "1. Eight per cent.", "2. A sector bonus.",
                                           "3. A timing bonus.", "4. Totalled per rep."]
    assert choreography.lines_of("  \n\n") == []


def test_a_value_is_a_file_only_when_one_of_that_name_is_under_the_folder(tmp_path):
    (tmp_path / "plan.txt").write_text("x", encoding="utf-8")
    assert choreography.text_file(str(tmp_path), "plan.txt") == str(tmp_path / "plan.txt")
    assert choreography.text_file(str(tmp_path), "other.txt") is None
    assert choreography.text_file(None, "plan.txt") is None             # no folder to look in
    assert choreography.text_file(str(tmp_path), "two\nlines") is None  # text of more than a line is no name
