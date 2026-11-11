"""videotools.outmd: the cells and table of a video's out/OUT.md (PLAN.md item 31)."""

import time
from datetime import datetime, timezone

import pytest

from videotools import cli, outmd


@pytest.mark.parametrize("size, text", [(0, "0"), (999, "999"), (1000, "1,000"), (19630414, "19,630,414")])
def test_a_size_is_written_with_comma_thousands_separators(size, text):
    assert outmd.size_text(size) == text


def utc(*when):
    return datetime(*when, tzinfo=timezone.utc).timestamp()


@pytest.mark.parametrize("mtime, zone, text", [
    (utc(2026, 10, 24, 12, 0), "Europe/London", "24 October 2026, 13:00"),   # summer time, before the change
    (utc(2026, 10, 26, 12, 0), "Europe/London", "26 October 2026, 12:00"),   # after the clocks go back
    (utc(2026, 10, 24, 12, 0), "UTC", "24 October 2026, 12:00"),
    (utc(2026, 11, 3, 7, 5), "Europe/London", "3 November 2026, 07:05"),     # one-digit day, zero-padded hour
])
def test_a_time_is_written_day_month_year_hours_minutes_in_the_zone_given(mtime, zone, text):
    assert outmd.made_text(mtime, zone) == text


def test_with_no_zone_the_machines_own_is_used(monkeypatch):
    monkeypatch.setenv("TZ", "Asia/Tokyo")
    time.tzset()
    try:
        assert outmd.made_text(utc(2026, 10, 24, 12, 0), None) == "24 October 2026, 21:00"
    finally:
        monkeypatch.undo()
        time.tzset()


def test_an_unknown_zone_is_refused_in_words():
    with pytest.raises(cli.Failure) as e:
        outmd.made_text(0, "Europe/Atlantis")
    assert str(e.value) == ("TIME_ZONE 'Europe/Atlantis' is not a time zone this machine knows; "
                            "give a name such as Europe/London (or remove the setting to use the machine's own)")
    assert e.value.code == cli.REFUSED


def test_a_state_is_one_cell_with_its_bars_escaped():
    assert outmd.text_cell("**Accepted** (Squirrel, 11 November 2026)", "--state") == \
        "**Accepted** (Squirrel, 11 November 2026)"
    assert outmd.text_cell("a | b `c|d`", "--state") == "a \\| b `c\\|d`"


@pytest.mark.parametrize("text", ["two\nlines", "carriage\rreturn", "end\n"])
def test_a_state_with_a_line_break_is_refused_naming_its_flag(text):
    with pytest.raises(cli.Failure) as e:
        outmd.text_cell(text, "--add-state")
    assert str(e.value) == "the --add-state text has a line break; a table cell is one line: give it on one line"
    assert e.value.code == cli.REFUSED


@pytest.mark.parametrize("value", ["4e39", "4e39323", "DF328B46", "0123456789abcdef0123456789abcdef01234567"])
def test_a_commit_of_4_to_40_hexadecimal_digits_is_taken_as_given(value):
    assert outmd.commit(value, "--tools-commit") == value


@pytest.mark.parametrize("value", ["4e3", "", "4e39323; rm -rf ~", "g123456", "0123456789abcdef0123456789abcdef012345678",
                                   "`4e39323`"])
def test_anything_else_given_as_a_commit_is_refused_naming_its_flag(value):
    with pytest.raises(cli.Failure) as e:
        outmd.commit(value, "--elements-commit")
    assert str(e.value) == f"--elements-commit {value!r} is not a commit id (4 to 40 hexadecimal digits)"


def test_made_with_is_the_tools_commit_and_the_librarys_when_there_is_one():
    assert outmd.made_with("4e39323", None) == "`4e39323`"
    assert outmd.made_with("4e39323", "d32067b") == "`4e39323` (video-elements `d32067b`)"


def test_a_row_has_six_cells_with_the_name_and_hash_in_backticks_and_an_empty_state_left_blank():
    sha = "df328b46" + "0" * 52 + "f3b4"
    assert outmd.row("Build v6.mp4", "11 October 2026, 08:52", "`4e39323`", 19630414, sha, "") == (
        f"| `Build v6.mp4` | 11 October 2026, 08:52 | `4e39323` | 19,630,414 | `{sha}` | |")
    assert outmd.row("a|b.mp4", "1 May 2026, 00:00", "`abcd`", 0, sha, "ok \\| fine").endswith(
        f"| `{sha}` | ok \\| fine |")
    assert outmd.row("a|b.mp4", "1 May 2026, 00:00", "`abcd`", 0, sha, "").startswith("| `a\\|b.mp4` |")


def test_a_file_name_with_a_backtick_or_a_line_break_is_refused():
    for name in ("a`b.mp4", "a\nb.mp4"):
        with pytest.raises(cli.Failure) as e:
            outmd.row(name, "", "", 1, "0" * 64, "")
        assert str(e.value) == f"the file name {name!r} has a backtick or a line break, which a table cell cannot hold; rename the copy you record"


# An invented OUT.md: two rows, the third column named as the training-video project names it, a
# state with escaped bars and backticks, and paragraphs below the table.
SHA1, SHA2, SHA3 = "1" * 64, "2" * 64, "3" * 64
TWO_ROWS = (
    "# out/ — the “Paper Boat” video's finished files\n"
    "\n"
    "*Each version, newest last.*\n"
    "\n"
    "| File | Made | video-tools | Size (bytes) | SHA-256 | State |\n"
    "|---|---|---|---|---|---|\n"
    f"| `Paper Boat v1.mp4` | 1 October 2026, 09:00 | `aaaa111` | 1,000 | `{SHA1}` | First cut; `check-video` a \\| b. |\n"
    f"| `Paper Boat v2.mp4` | 2 October 2026, 10:00 | `bbbb222` (video-elements `cccc333`) | 2,000 | `{SHA2}` | |\n"
    "\n"
    "v0 was made by hand | not recorded.\n"
)
NEW_ROW = f"| `Paper Boat v3.mp4` | 3 October 2026, 11:00 | `dddd444` | 3,000 | `{SHA3}` | |"


def test_a_row_is_appended_after_the_tables_last_row_and_nothing_else_changes():
    expected = TWO_ROWS.replace("| |\n\nv0", "| |\n" + NEW_ROW + "\n\nv0")
    assert outmd.append(TWO_ROWS, NEW_ROW, "Paper Boat v3.mp4", "OUT.md") == expected


def test_a_row_is_appended_to_a_table_that_ends_the_file_with_or_without_a_final_newline():
    head = TWO_ROWS.split("\n\nv0")[0]
    assert outmd.append(head + "\n", NEW_ROW, "Paper Boat v3.mp4", "OUT.md") == head + "\n" + NEW_ROW + "\n"
    assert outmd.append(head, NEW_ROW, "Paper Boat v3.mp4", "OUT.md") == head + "\n" + NEW_ROW + "\n"


def test_a_file_with_windows_line_endings_keeps_them():
    crlf = TWO_ROWS.replace("\n", "\r\n")
    assert outmd.append(crlf, NEW_ROW, "Paper Boat v3.mp4", "OUT.md") == \
        crlf.replace("| |\r\n\r\nv0", "| |\r\n" + NEW_ROW + "\r\n\r\nv0")


def test_a_second_row_for_the_same_file_is_refused():
    with pytest.raises(cli.Failure) as e:
        outmd.append(TWO_ROWS, NEW_ROW, "Paper Boat v2.mp4", "out/OUT.md")
    assert str(e.value) == ("out/OUT.md already has a row for Paper Boat v2.mp4; to add to its state, "
                            "use --add-state")


def test_a_row_is_found_by_its_name_whether_written_nfc_or_nfd():
    import unicodedata
    nfc = "Café v1.mp4"
    nfd = unicodedata.normalize("NFD", nfc)
    text = TWO_ROWS.replace("Paper Boat v1.mp4", nfc)
    with pytest.raises(cli.Failure):
        outmd.append(text, NEW_ROW, nfd, "OUT.md")
    with pytest.raises(cli.Failure):
        outmd.append(TWO_ROWS.replace("Paper Boat v1.mp4", nfd), NEW_ROW, nfc, "OUT.md")


def test_a_name_with_a_bar_is_found_as_written_escaped():
    text = TWO_ROWS.replace("`Paper Boat v1.mp4`", "`a\\|b.mp4`")
    with pytest.raises(cli.Failure):
        outmd.append(text, NEW_ROW, "a|b.mp4", "OUT.md")


@pytest.mark.parametrize("text, problem", [
    ("# out/\n\nNo table yet.\n", "has no table"),
    (TWO_ROWS + "\n| A | B | C | D | E | F |\n|---|---|---|---|---|---|\n", "has 2 tables; it should have one"),
    (TWO_ROWS.replace("| SHA-256 | State |", "| SHA-256 |").replace("|---|---|---|---|---|---|", "|---|---|---|---|---|"),
     "has a table of 5 columns; it should have six (file, made, made with, size, SHA-256, state)"),
    (TWO_ROWS.replace("| State |", "| State | Extra |").replace("---|---|\n", "---|---|---|\n"),
     "has a table of 7 columns; it should have six (file, made, made with, size, SHA-256, state)"),
])
def test_an_out_md_without_exactly_one_six_column_table_is_refused(text, problem):
    for call in (lambda: outmd.append(text, NEW_ROW, "Paper Boat v3.mp4", "x/OUT.md"),
                 lambda: outmd.add_state(text, "Paper Boat v1.mp4", "ok", "x/OUT.md")):
        with pytest.raises(cli.Failure) as e:
            call()
        assert str(e.value) == f"x/OUT.md {problem}; record-output changes nothing in it"


def test_a_state_is_added_after_a_space_to_that_rows_state_cell_only():
    text, line = outmd.add_state(TWO_ROWS, "Paper Boat v1.mp4", "**Accepted** (Squirrel) \\| `x`", "OUT.md")
    old = f"| `Paper Boat v1.mp4` | 1 October 2026, 09:00 | `aaaa111` | 1,000 | `{SHA1}` | First cut; `check-video` a \\| b. |"
    new = (f"| `Paper Boat v1.mp4` | 1 October 2026, 09:00 | `aaaa111` | 1,000 | `{SHA1}` | First cut; `check-video` a \\| b. "
           "**Accepted** (Squirrel) \\| `x` |")
    assert line == new
    assert text == TWO_ROWS.replace(old, new)


def test_a_state_added_to_an_empty_cell_stands_alone():
    text, line = outmd.add_state(TWO_ROWS, "Paper Boat v2.mp4", "Superseded by v3.", "OUT.md")
    assert line == ("| `Paper Boat v2.mp4` | 2 October 2026, 10:00 | `bbbb222` (video-elements `cccc333`) | 2,000 | "
                    f"`{SHA2}` | Superseded by v3. |")
    assert text == TWO_ROWS.replace(f"`{SHA2}` | |", f"`{SHA2}` | Superseded by v3. |")


def test_adding_a_state_for_a_file_with_no_row_is_refused():
    with pytest.raises(cli.Failure) as e:
        outmd.add_state(TWO_ROWS, "Paper Boat v9.mp4", "ok", "out/OUT.md")
    assert str(e.value) == ("out/OUT.md has no row for Paper Boat v9.mp4; add one first "
                            "(record-output without --add-state)")


def test_adding_a_state_to_a_row_that_is_not_six_cells_is_refused():
    text = TWO_ROWS.replace("| 1,000 |", "|")
    with pytest.raises(cli.Failure) as e:
        outmd.add_state(text, "Paper Boat v1.mp4", "ok", "OUT.md")
    assert str(e.value) == "OUT.md: the row for Paper Boat v1.mp4 has 5 cells, not six; record-output changes nothing in it"


def test_a_new_out_md_has_a_heading_from_the_title_an_italic_line_the_header_and_the_row():
    assert outmd.new_file("The “Paper Boat” — étude", NEW_ROW) == (
        "# out/ — The “Paper Boat” — étude: finished files\n"
        "\n"
        "*Each version, newest last. Finished files are never written over or renamed.*\n"
        "\n"
        "| File | Made | Made with | Size (bytes) | SHA-256 | State |\n"
        "|---|---|---|---|---|---|\n"
        + NEW_ROW + "\n")


def test_a_new_file_is_read_back_as_one_six_column_table_holding_its_row():
    text = outmd.new_file("T", NEW_ROW)
    with pytest.raises(cli.Failure):
        outmd.append(text, NEW_ROW, "Paper Boat v3.mp4", "OUT.md")
    assert outmd.add_state(text, "Paper Boat v3.mp4", "ok", "OUT.md")[1].endswith("| ok |")


def test_a_state_is_added_to_a_row_written_without_its_closing_bar():
    text = TWO_ROWS.replace(f"`{SHA2}` | |\n", f"`{SHA2}` | Watched\n")
    new, line = outmd.add_state(text, "Paper Boat v2.mp4", "and accepted.", "OUT.md")
    assert line.endswith(f"`{SHA2}` | Watched and accepted. ")
    assert new == text.replace("| Watched\n", "| Watched and accepted. \n")


def test_a_line_starting_with_a_bar_that_is_not_a_table_is_not_counted_as_one():
    text = TWO_ROWS + "\n| a note that starts with a bar\n"
    assert outmd.append(text, NEW_ROW, "Paper Boat v3.mp4", "OUT.md") == text.replace("| |\n\nv0", "| |\n" + NEW_ROW + "\n\nv0")
