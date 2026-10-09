"""videotools.script.check: the Settings table and the title."""

import pytest

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import script


@pytest.fixture
def video(tmp_path):
    """A video folder with its source file and a brand kit two levels up, as in a project."""
    folder = tmp_path / "videos" / "bow"
    (folder / "sources").mkdir(parents=True)
    (folder / "sources" / "bow.png").write_bytes(b"not really a png")
    (tmp_path / "brands" / "demo").mkdir(parents=True)
    (tmp_path / "brands" / "demo" / "BRAND.md").write_text("# demo\n")
    return folder


def problems(text, folder):
    path = folder / "script.md"
    path.write_text(text, encoding="utf-8")
    data, structural = script.parse(text)
    assert structural == []
    return script.check(data, str(path))


def test_a_well_formed_script_has_no_problems(video):
    assert problems(TWO_SCENES, video) == []


def test_a_missing_required_setting_is_named(video):
    text = TWO_SCENES.replace("| voice | af_heart | |\n", "")
    assert problems(text, video) == ["Settings: 'voice' is missing"]


def test_an_empty_required_setting_counts_as_missing(video):
    text = TWO_SCENES.replace("| voice | af_heart | |", "| voice | | |")
    assert problems(text, video) == ["Settings: 'voice' is missing"]


def test_an_unknown_setting_is_a_problem_naming_its_line_unless_it_starts_with_x(video):
    text = TWO_SCENES.replace("| scene-code | scenes/ | |",
                              "| scene-code | scenes/ | |\n| colour | red | |\n| x-mine | kept | |")
    assert problems(text, video) == ["line 20: Settings: unknown key 'colour'"]


def test_a_setting_that_must_be_a_number_is_checked(video):
    text = TWO_SCENES.replace("| speed | 0.98 | |", "| speed | fast | |")
    text = text.replace("| fps | 30 | |", "| fps | 30 | |\n| lead | 0,7 | |")
    assert problems(text, video) == ["line 12: Settings: 'speed' should be a number, not 'fast'",
                                     "line 17: Settings: 'lead' should be a number, not '0,7'"]


def test_size_must_look_like_width_x_height(video):
    text = TWO_SCENES.replace("| size | 1920x1080 | |", "| size | 1920 | |")
    assert problems(text, video) == ["line 15: Settings: 'size' should look like 1920x1080, not '1920'"]


def test_a_source_file_that_does_not_exist_is_named(video):
    text = TWO_SCENES.replace("| source | sources/bow.png | |",
                              "| source | sources/bow.png | |\n| source-image | sources/missing.png | |")
    assert problems(text, video) == ["line 18: Settings: 'source-image' file not found: sources/missing.png"]


def test_a_brand_with_no_kit_is_named_with_where_it_was_looked_for(video, tmp_path):
    text = TWO_SCENES.replace("| brand | demo | |", "| brand | other | |")
    assert problems(text, video) == [
        "line 10: Settings: brand 'other' has no brands/other/BRAND.md under %s" % tmp_path]


def test_a_brand_is_refused_when_no_folder_above_the_script_has_brands(tmp_path):
    folder = tmp_path / "videos" / "bow"
    (folder / "sources").mkdir(parents=True)
    (folder / "sources" / "bow.png").write_bytes(b"")
    assert problems(TWO_SCENES, folder) == [
        "line 10: Settings: brand 'demo': no 'brands/' folder in or above %s" % folder]


def test_a_script_without_a_title_line_is_a_problem(video):
    text = TWO_SCENES.replace("# Tying a Bow\n", "")
    assert problems(text, video) == ["no '# title' line at the top"]
