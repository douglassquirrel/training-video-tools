"""check_script.font_problems: every text the chrome draws, checked against the resolved file of
the role it is drawn in; ✓ and ✗ excepted (drawn as strokes); On screen labels against the
display font only. The example kit's fonts lack € and Ω."""

import os
import shutil

import pytest

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import brand, check_script, script

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat")


@pytest.fixture
def kit():
    return brand.read(EXAMPLE)


def problems(text, kit):
    data, structural = script.parse(text)
    assert structural == []
    return check_script.font_problems(data, kit)


def font(kit, role):
    return kit["font_files"][role]


def test_the_fixture_script_has_nothing_the_example_fonts_lack(kit):
    assert problems(TWO_SCENES, kit) == []


def test_a_caption_with_a_character_the_body_font_lacks_is_one_problem_naming_line_text_character_and_file(kit):
    text = TWO_SCENES.replace("2. Don't pull it tight yet. It needs room for the second loop.",
                              "2. Don't pull it tight yet. It needs room for the second loop, and €5.")
    assert problems(text, kit) == [
        "line 47: scene A cue 2 caption 'Don't pull it tight yet. It needs room for the second loop, and €5.' "
        f"has '€' (U+20AC), which {font(kit, 'body')} lacks"]


def test_a_tick_or_cross_is_never_reported_since_the_tools_draw_them(kit):
    text = (TWO_SCENES.replace("2. Don't pull it tight yet.", "2. Don't pull it tight yet ✗.")
            .replace("- first loop\n", "- first loop ✓\n"))
    assert problems(text, kit) == []


def test_each_kind_of_text_is_checked_in_the_role_the_chrome_draws_it_in(kit):
    text = (TWO_SCENES
            .replace("| title | Tying a Bow | the title card |\n",
                     "| title | Tying a Bow | the title card |\n| subtitle | Bows for €5 | |\n")   # the rows below move down one
            .replace("| title | First loop | |", "| title | First loop Ω | |")
            .replace("- Loop, don't pull\n", "- Loop, don't pull, €\n")
            .replace("- room for the second\n", "- room for the second Ω\n"))
    assert problems(text, kit) == [
        f"line 10: setting 'subtitle' 'Bows for €5' has '€' (U+20AC), which {font(kit, 'italic')} lacks",
        f"line 39: scene A 'title' 'First loop Ω' has 'Ω' (U+03A9), which {font(kit, 'display')} lacks",
        f"line 55: scene A side panel item 'Loop, don't pull, €' has '€' (U+20AC), which {font(kit, 'body')} lacks",
        f"line 61: scene A on screen label 'room for the second Ω' has 'Ω' (U+03A9), which {font(kit, 'display')} lacks",
    ]


def test_a_text_with_two_lacking_characters_is_reported_once_with_the_first(kit):
    text = TWO_SCENES.replace("| title | Tying a Bow |", "| title | Tying a Ω bow for € |")
    assert problems(text, kit) == [
        f"line 9: setting 'title' 'Tying a Ω bow for €' has 'Ω' (U+03A9), which {font(kit, 'display')} lacks"]


def test_the_kits_own_website_and_credit_are_checked_too(tmp_path):
    shutil.copytree(EXAMPLE, tmp_path / "paperboat")
    path = tmp_path / "paperboat" / "BRAND.md"
    text = path.read_text(encoding="utf-8").replace("| website | paperboat.example |", "| website | paperboat.example/€ |")
    path.write_text(text, encoding="utf-8")
    kit = brand.read(str(tmp_path / "paperboat"))
    assert problems(TWO_SCENES, kit) == [
        f"{path}: Identity 'website' 'paperboat.example/€' has '€' (U+20AC), which {font(kit, 'italic')} lacks"]
