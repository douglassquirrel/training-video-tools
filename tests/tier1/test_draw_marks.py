"""✓ and ✗ drawn as strokes where the font lacks them: in draw.text and counted by draw.text_width,
so pills, centring, tracking and wrapping stay right. The registry stands in for the font: a family
registered to the fixture font (which lacks both) gets the strokes; an unregistered family, or one
registered to a font that has them, gets the font's own glyph."""

import os

import pytest

from tests.tier1.test_draw import BLACK, WHITE, pixel, surface
from videotools import draw, glyphs

LACKING = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat", "fonts",
                       "PBS-Regular.ttf")
FAMILY = "Marks Test Family"          # cairo falls back to a real font for the letters; the registry decides the marks


@pytest.fixture(autouse=True)
def lacking():
    glyphs.register(FAMILY, LACKING)


def test_a_mark_the_font_lacks_is_counted_as_0_8_of_the_size_anywhere_in_the_string():
    s, c = surface()
    plain = draw.text_width(c, "done ", FAMILY, 30)
    assert draw.text_width(c, "done ✓", FAMILY, 30) == pytest.approx(plain + 24)
    assert draw.text_width(c, "done ✗", FAMILY, 30) == pytest.approx(plain + 24)
    assert draw.text_width(c, "a ✓ b", FAMILY, 30) == pytest.approx(draw.text_width(c, "a ", FAMILY, 30) + 24
                                                                     + draw.text_width(c, " b", FAMILY, 30))
    assert draw.text_width(c, "✓✗", FAMILY, 30, track=5) == pytest.approx(48 + 5)


def test_the_tick_and_cross_are_drawn_as_strokes_in_the_colour_and_nothing_where_the_box_would_be():
    s, c = surface()
    draw.text(c, "✓", 20, 80, FAMILY, 50, BLACK)                  # tick: (x+0.32s, y-0.06s) is on the stroke
    assert pixel(s, 36, 77) == (0, 0, 0)
    assert pixel(s, 20 + 40 + 6, 80 - 15) == (255, 255, 255)      # past the advance: no missing-glyph box
    s, c = surface()
    draw.text(c, "✗", 20, 80, FAMILY, 50, BLACK)                  # cross: its centre (x+0.4s, y-0.34s)
    assert pixel(s, 40, 63) == (0, 0, 0)
    assert pixel(s, 20 + 40 + 6, 80 - 15) == (255, 255, 255)


def test_a_mark_is_drawn_with_the_texts_alpha_and_anchored_like_the_text():
    s, c = surface()
    draw.text(c, "✓", 100, 80, FAMILY, 50, BLACK, anchor="c")     # 40 wide, so it starts at 80
    assert pixel(s, 96, 77) == (0, 0, 0)
    s, c = surface()
    draw.text(c, "✓", 20, 80, FAMILY, 50, BLACK, alpha=0.5)
    assert 100 < pixel(s, 36, 77)[0] < 160


def test_a_font_that_has_the_glyph_draws_its_own_and_an_unregistered_family_is_left_alone(tmp_path):
    from tests.tier2.test_glyphs_against_fonttools import tiny_font
    glyphs.register(FAMILY, tiny_font(str(tmp_path / "ticks.ttf"), [0x41, 0x2713]))
    a, ca = surface()
    draw.text(ca, "A ✓", 20, 80, FAMILY, 50, BLACK)
    b, cb = surface()
    draw.text(cb, "A ✓", 20, 80, "Some Family Nobody Registered", 50, BLACK)
    a.flush(), b.flush()
    assert bytes(a.get_data()) == bytes(b.get_data())
    assert draw.text_width(ca, "A ✓", FAMILY, 50) == draw.text_width(cb, "A ✓", "Some Family Nobody Registered", 50)


def test_a_pill_with_a_tick_is_wider_by_the_tick_and_wrap_counts_it():
    s, c = surface(400, 120)
    _, _, plain, _ = draw.tag(c, "done", 10, 60, FAMILY, 30, BLACK, WHITE)
    _, _, ticked, _ = draw.tag(c, "done ✓", 10, 60, FAMILY, 30, BLACK, WHITE)
    assert ticked - plain == pytest.approx(draw.text_width(c, " ", FAMILY, 30) + 24)
    width = draw.text_width(c, "done ✓", FAMILY, 30)
    assert draw.wrap(c, "done ✓ done ✓", FAMILY, 30, width + 1) == ["done ✓", "done ✓"]
    assert draw.wrap(c, "done ✓ done ✓", FAMILY, 30, 2 * width + 20) == ["done ✓ done ✓"]

