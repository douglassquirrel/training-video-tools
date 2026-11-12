"""thumbnail's pure parts (PLAN.md item 32): the two new settings and check-script's word on them,
the moment's reading, the default path, the title's fitting, the picture's crop, the fade warning."""

import os

import pytest

from tests.tier1.test_script_reads import TWO_SCENES
from videotools import brand, check_script, cli, script, thumbnail

EXAMPLE_KIT = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat")
SETTING_ROW = "| scene-code | scenes/ | |"


def problems(text, folder):
    path = folder / "script.md"
    path.write_text(text, encoding="utf-8")
    data, structural = script.parse(text)
    assert structural == []
    return script.check(data, str(path))


def with_settings(*rows):
    return TWO_SCENES.replace(SETTING_ROW, "\n".join((SETTING_ROW,) + rows))


# ---------------------------------------------------------------- the settings
def test_thumbnail_title_and_thumbnail_at_are_known_settings(video):
    assert problems(with_settings("| thumbnail-title | Bows | |", "| thumbnail-at | A:2.5 | |"), video) == []


def test_thumbnail_at_that_is_not_scene_colon_seconds_is_a_problem_naming_its_line(video):
    assert problems(with_settings("| thumbnail-at | A at 2 | |"), video) == [
        "line 20: Settings: 'thumbnail-at' should be SCENE:SECONDS, like A:2.5, not 'A at 2'"]


def test_thumbnail_at_naming_a_scene_the_script_lacks_is_a_problem_listing_the_scenes(video):
    assert problems(with_settings("| thumbnail-at | Z:1 | |"), video) == [
        "line 20: Settings: 'thumbnail-at' names no scene 'Z' (scenes: A, end)"]


def test_the_settings_carry_the_two_new_texts_empty_when_absent():
    data, _ = script.parse(with_settings("| thumbnail-title | Bows “for all” | |", "| thumbnail-at | A:-1 | |"))
    st = script.settings(data)
    assert (st["thumbnail-title"], st["thumbnail-at"]) == ("Bows “for all”", "A:-1")
    data, _ = script.parse(TWO_SCENES)
    assert (script.settings(data)["thumbnail-title"], script.settings(data)["thumbnail-at"]) == ("", "")


def test_a_thumbnail_title_with_a_character_the_display_font_lacks_is_a_font_problem():
    kit = brand.read(EXAMPLE_KIT)
    data, _ = script.parse(with_settings("| thumbnail-title | Bows Ω | |"))
    assert check_script.font_problems(data, kit) == [
        f"line 20: setting 'thumbnail-title' 'Bows Ω' has 'Ω' (U+03A9), which {kit['font_files']['display']} lacks"]


# ---------------------------------------------------------------- the moment
def test_a_moment_is_scene_colon_seconds_and_a_negative_time_is_kept_for_counting_back():
    assert thumbnail.parse_at("B:3.5") == ("B", 3.5)
    assert thumbnail.parse_at(" B2:-1 ") == ("B2", -1.0)


@pytest.mark.parametrize("text", ["B", "B:", ":3", "B:three", "B 3"])
def test_a_moment_that_is_not_scene_colon_seconds_is_a_usage_error(text):
    with pytest.raises(cli.Failure) as e:
        thumbnail.parse_at(text)
    assert (str(e.value), e.value.code) == (f"'{text.strip()}' is not SCENE:SECONDS", cli.USAGE)


# ---------------------------------------------------------------- the path
def test_the_default_path_is_the_output_with_thumbnail_png_in_place_of_its_extension(tmp_path):
    script_path = str(tmp_path / "v" / "script.md")
    assert thumbnail.default_out(script_path, "out/Folding a Paper Boat.mp4") == \
        str(tmp_path / "v" / "out" / "Folding a Paper Boat thumbnail.png")
    assert thumbnail.default_out(script_path, "out/Bow") == str(tmp_path / "v" / "out" / "Bow thumbnail.png")


# ---------------------------------------------------------------- the title
def half_em(s, size):
    """A fake font: every character half the size wide."""
    return len(s) * size * 0.5


def cap_07(size):
    """A fake font whose capitals are 0.7 of the size tall: 40 px from 58 px up."""
    return size * 0.7


def test_a_short_title_takes_one_line_at_the_largest_size():
    assert thumbnail.fit_title("Boat", 500, half_em, cap_07) == (96, ["Boat"])


def test_a_title_too_wide_for_one_line_wraps_at_the_largest_size_when_it_can():
    assert thumbnail.fit_title("Folding a Paper Boat", 500, half_em, cap_07) == (96, ["Folding a", "Paper Boat"])


def test_a_title_that_needs_four_lines_at_the_largest_size_shrinks_until_it_takes_three():
    # 10 characters a line up to 91 px; 11 from 90 px down.
    assert thumbnail.fit_title("Build Your Own App For That Today", 500, half_em, cap_07) == \
        (90, ["Build Your", "Own App For", "That Today"])


def test_curly_quotes_and_accents_are_measured_like_any_other_character():
    assert thumbnail.fit_title("“Café” Boat", 500, half_em, cap_07) == (96, ["“Café”", "Boat"])


def test_a_title_that_cannot_fit_three_lines_at_the_smallest_readable_size_gives_none():
    long = "A very long title that will never fit in three lines whatever size we try"
    assert thumbnail.fit_title(long, 500, half_em, cap_07) is None


def test_a_word_wider_than_the_block_at_every_readable_size_gives_none():
    assert thumbnail.fit_title("Pneumonoultramicroscopic", 500, half_em, cap_07) is None


def test_no_size_with_capitals_under_the_minimum_is_tried():
    tried = []

    def measure(s, size):
        tried.append(size)
        return half_em(s, size)
    thumbnail.fit_title("A very long title that will never fit in three lines whatever size we try", 500, measure,
                        cap_07)
    assert (max(tried), min(tried)) == (96, 58)         # 0.7 x 58 = 40.6; 0.7 x 57 = 39.9


# ---------------------------------------------------------------- the picture
def test_the_crop_keeps_the_middle_of_a_picture_wider_or_taller_than_the_card():
    assert thumbnail.cover_box(200, 100, 100, 100) == (50.0, 0.0, 150.0, 100.0)
    assert thumbnail.cover_box(100, 200, 100, 100) == (0.0, 50.0, 100.0, 150.0)
    assert thumbnail.cover_box(300, 150, 100, 50) == (0.0, 0.0, 300.0, 150.0)


# ---------------------------------------------------------------- the fade
def test_a_moment_inside_the_fade_in_or_fade_out_is_named_and_one_between_is_not():
    assert thumbnail.fade_warning("B", 0.2, 7.9, (0.45, 0.4)) == \
        "scene B at 0.200 s is inside its fade-in (the first 0.45 s): the picture is partly faded"
    assert thumbnail.fade_warning("B", 7.7, 7.9, (0.45, 0.4)) == \
        "scene B at 7.700 s is inside its fade-out (the last 0.4 s): the picture is partly faded"
    assert thumbnail.fade_warning("B", 0.45, 7.9, (0.45, 0.4)) is None
    assert thumbnail.fade_warning("B", 7.5, 7.9, (0.45, 0.4)) is None


# ---------------------------------------------------------------- the size
def test_a_thumbnail_over_two_million_bytes_is_refused_in_words():
    assert thumbnail.size_problem(2_000_000) is None
    assert thumbnail.size_problem(2_000_001) == \
        "the thumbnail would be 2,000,001 bytes, over the 2,000,000-byte limit; nothing written"


# ---------------------------------------------------------------- the write
def test_a_rename_that_fails_leaves_no_temporary_file_and_no_final_file(tmp_path, monkeypatch):
    def refuse(src, dst):
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(thumbnail.os, "replace", refuse)
    out = tmp_path / "t.png"
    with pytest.raises(cli.Failure) as e:
        thumbnail._write(str(out), b"png bytes")
    assert (str(e.value), e.value.code) == (f"cannot write {out}: No space left on device", cli.REFUSED)
    assert os.listdir(tmp_path) == []
