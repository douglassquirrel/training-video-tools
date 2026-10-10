"""videotools.choreography.select_rows: the rows and columns of a data file a cast row chooses
with `rows.where`, `rows.first` and `rows.columns` (PLAN.md item 20, 4). Pure: rows in, rows out."""

from videotools import choreography

ROWS = [["Sales Rep", "Date Closed", "Commission"],
        ["J. M", "2024-04-02", "5940"],
        ["C. M", "TOTAL", "7900"],
        ["L. C", "TOTAL", "1750"],
        ["A. P", "2024-04-09", "4560"]]


def _select(**qualifiers):
    return choreography.select_rows(ROWS, {f"rows.{k}": v for k, v in qualifiers.items()}, "rows")


def test_with_no_qualifier_the_rows_are_the_files():
    assert choreography.select_rows(ROWS, {"rows": "a.csv", "numeric": "B"}, "rows") == (ROWS, [])


def test_columns_by_name_and_by_number_give_the_same_rows_in_the_order_written():
    by_name, by_number = _select(columns="Sales Rep, Commission"), _select(columns="1, 3")
    assert by_name == by_number == ([["Sales Rep", "Commission"], ["J. M", "5940"], ["C. M", "7900"],
                                     ["L. C", "1750"], ["A. P", "4560"]], [])
    assert _select(columns="3,1")[0][:2] == [["Commission", "Sales Rep"], ["5940", "J. M"]]


def test_where_keeps_the_rows_that_equal_or_do_not_equal_a_value_and_always_the_header():
    assert _select(where="Date Closed = TOTAL") == ([ROWS[0], ROWS[2], ROWS[3]], [])
    assert _select(where="2 != TOTAL") == ([ROWS[0], ROWS[1], ROWS[4]], [])


def test_first_counts_data_rows_after_where_and_columns_come_last():
    assert _select(where="Date Closed != TOTAL", first="1") == ([ROWS[0], ROWS[1]], [])
    assert _select(first="2") == (ROWS[:3], [])
    assert _select(where="Date Closed = TOTAL", first="1", columns="Sales Rep, Commission") == (
        [["Sales Rep", "Commission"], ["C. M", "7900"]], [])


def test_what_is_not_there_is_a_problem_in_words():
    assert _select(columns="Sales Rep, Bonus")[1] == [
        "'rows.columns': no column 'Bonus' (the columns are Sales Rep, Date Closed, Commission)"]
    assert _select(columns="1, 9")[1] == ["'rows.columns': no column 9 (there are 3 columns)"]
    assert _select(columns=" ")[1] == ["'rows.columns' names no column"]
    assert _select(where="Date Closed is TOTAL")[1] == [
        "'rows.where' should be COLUMN = VALUE or COLUMN != VALUE, not 'Date Closed is TOTAL'"]
    assert _select(where="Closed = TOTAL")[1] == [
        "'rows.where': no column 'Closed' (the columns are Sales Rep, Date Closed, Commission)"]
    assert _select(where="Date Closed = NEVER")[1] == ["'rows.where': no row has 'NEVER' in column 'Date Closed'"]
    assert _select(first="0")[1] == ["'rows.first' should be a whole number above 0, not '0'"]
    assert _select(first="some")[1] == ["'rows.first' should be a whole number above 0, not 'some'"]


def test_an_empty_file_has_no_columns_to_choose():
    assert choreography.select_rows([], {"rows.columns": "1"}, "rows") == ([], ["'rows.columns': the file has no rows"])
