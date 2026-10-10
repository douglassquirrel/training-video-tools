"""videotools.glyphs: which characters a font file has, read from its cmap with the standard
library, and the registry draw.text asks by family name."""

import os

import pytest

from videotools import cli, glyphs

FONTS = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat", "fonts")
REGULAR = os.path.join(FONTS, "PBS-Regular.ttf")


def test_the_fixture_font_has_latin_and_punctuation_and_lacks_the_tick_the_cross_and_the_euro():
    chars = glyphs.characters(REGULAR)
    assert all(ord(c) in chars for c in "Aé—…·“”")
    assert not any(ord(c) in chars for c in "✓✗€Ω")
    assert len(chars) == 200


def test_a_file_that_is_not_a_font_is_a_useful_failure(tmp_path):
    bad = tmp_path / "not-a-font.ttf"
    bad.write_bytes(b"hello, this is not a font at all" * 10)
    with pytest.raises(cli.Failure) as e:
        glyphs.characters(str(bad))
    assert str(e.value) == f"{bad} is not a TrueType or OpenType font with a character map (cmap)"


def test_a_registered_family_answers_from_its_file_and_an_unknown_family_is_assumed_to_have_everything():
    glyphs.register("Test Regular", REGULAR)
    assert glyphs.has("Test Regular", "é") is True
    assert glyphs.has("Test Regular", "✓") is False
    assert glyphs.has("No Such Family", "✓") is True
