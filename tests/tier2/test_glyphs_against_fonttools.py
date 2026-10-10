"""The standard-library cmap reader agrees with fontTools on the fixture fonts, and reads a
format 12 table (characters beyond the Basic Multilingual Plane)."""

import glob
import os

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from videotools import glyphs

FONTS = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat", "fonts")


def test_the_reader_agrees_with_fonttools_on_every_fixture_font():
    for path in sorted(glob.glob(os.path.join(FONTS, "*.ttf"))):
        assert glyphs.characters(path) == set(TTFont(path).getBestCmap()), path


def tiny_font(path, code_points):
    """An invented font with a box glyph for each code point (fontTools writes a format 12 cmap
    when a code point is beyond U+FFFF)."""
    fb = FontBuilder(1000, isTTF=True)
    names = [".notdef"] + [f"g{cp:X}" for cp in code_points]
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({cp: f"g{cp:X}" for cp in code_points})
    glyph = {}
    for name in names:
        pen = TTGlyphPen(None)
        pen.moveTo((50, 0))
        pen.lineTo((550, 0))
        pen.lineTo((550, 700))
        pen.lineTo((50, 700))
        pen.closePath()
        glyph[name] = pen.glyph()
    fb.setupGlyf(glyph)
    fb.setupHorizontalMetrics({n: (600, 50) for n in names})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "Tiny Ticks", "styleName": "Regular", "psName": "TinyTicks-Regular"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200)
    fb.setupPost()
    fb.save(path)
    return path


def test_a_format_12_table_is_read_and_a_font_with_the_tick_has_it(tmp_path):
    path = tiny_font(str(tmp_path / "ticks.ttf"), [0x41, 0x2713, 0x2717, 0x1F600])
    assert any(t.format == 12 for t in TTFont(path)["cmap"].tables)
    assert glyphs.characters(path) == {0x41, 0x2713, 0x2717, 0x1F600}
