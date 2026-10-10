"""videotools.credits: the library elements a video uses, and the credit lines for the end card
from the script's element-credits setting (PLAN.md item 16)."""

import os

import pytest

from videotools import credits, elements, script

INVENTED = os.path.join(os.path.dirname(__file__), "..", "stubs", "video-elements")

SCRIPT = """# A video

## Settings

| Key | Value | Notes |
|---|---|---|
| title | A video | |
{setting}

## Scene A: One

| Key | Value | Notes |
|---|---|---|
| letter | A | |

### Narration

1. One.
   - mistake: X / Y

### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p | pot | 10 10 | | | |
| tag | pill | 10 10 | | text=x | |
| t | table | 10 10 | | rows=a.csv | |

### Moves

- cue 1: show p, tag, t

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| p2 | pot | 10 10 | | | |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| b | badge | 10 10 | | ok=yes | |

## Scene B: Two

| Key | Value | Notes |
|---|---|---|
| letter | B | |

### Narration

1. Two.

### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| t2 | table | 10 10 | | rows=a.csv | |

### Moves

- cue 1: show t2
"""


def _data(setting=""):
    data, problems = script.parse(SCRIPT.format(setting=setting))
    assert problems == []
    return data


@pytest.fixture
def lib():
    return elements.open_library(INVENTED, None)


def test_the_library_elements_a_video_uses_in_script_order_once_each_panels_included_pieces_not():
    assert credits.elements_used(_data()) == ["pot", "table"]
    plain, _ = script.parse("# A video\n\n## Scene A: One\n\n### Narration\n\n1. One.\n")
    assert credits.elements_used(plain) == []


def test_auto_gives_one_line_per_category_from_the_librarys_credits(lib):
    assert credits.lines(_data(), lib) == ["Icons: Invented Icons", "People: Invented Peeps by Nobody"]


def test_none_gives_no_lines_and_wording_wins(lib):
    assert credits.lines(_data("| element-credits | none | |"), lib) == []
    assert credits.lines(_data("| element-credits | Art by the invented crew | |"), lib) == ["Art by the invented crew"]


def test_a_video_with_no_library_elements_has_no_lines_unless_wording_is_given(lib):
    plain, _ = script.parse("# A video\n\n## Scene A: One\n\n### Narration\n\n1. One.\n")
    assert credits.lines(plain, None) == []
    plain, _ = script.parse("# A video\n\n## Settings\n\n| Key | Value | Notes |\n|---|---|---|\n"
                            "| element-credits | Art by the invented crew | |\n\n## Scene A: One\n\n### Narration\n\n1. One.\n")
    assert credits.lines(plain, None) == ["Art by the invented crew"]


def test_the_setting_is_optional_defaults_to_auto_and_is_read_back(lib):
    assert script.settings(_data_full())["element-credits"] == "auto"
    assert script.settings(_data_full("| element-credits | none | |"))["element-credits"] == "none"


def _data_full(setting=""):
    """A script with every required setting, for script.settings."""
    required = ("| brand | demo | |\n| voice | v | |\n| speed | 1 | |\n| language | en | |\n| speech-model | m | |\n"
                "| size | 1920x1080 | |\n| fps | 30 | |\n| source | s.png | |\n| output | out/v.mp4 | |\n"
                "| scene-code | scenes/ | |\n")
    data, problems = script.parse(SCRIPT.format(setting=required + setting))
    assert problems == []
    return data


def test_an_element_the_library_lacks_is_left_to_the_checks_and_credits_nothing(lib):
    data = _data()
    data["scenes"][0]["cast"][0]["element"] = "teapot"
    data["scenes"][0]["panels"]["mistake"]["cast"][0]["element"] = "teapot"
    assert credits.elements_used(data) == ["teapot", "table"]
    assert credits.lines(data, lib) == ["People: Invented Peeps by Nobody"]
    assert credits.sources(data, lib) == [("Invented Peeps by Nobody", "People", "CC0 1.0", ["table"])]
