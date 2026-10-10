"""videotools.draw: the primitives, checked by the pixels they leave on a small surface."""

import math

import cairo
import pytest

from videotools import draw

RED, GREEN, BLUE, WHITE, BLACK = (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1), (0, 0, 0)


def surface(w=200, h=120, background=WHITE):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s)
    c.set_source_rgb(*background)
    c.paint()
    return s, c


def pixel(s, x, y):
    """(r, g, b) of a pixel, in 0–255, from cairo's BGRA bytes."""
    s.flush()
    stride, data = s.get_stride(), s.get_data()
    i = y * stride + x * 4
    return data[i + 2], data[i + 1], data[i]


def test_shade_mix_and_rgb():
    assert draw.shade((0.5, 0.5, 1.0), 0.5) == (0.25, 0.25, 0.5)
    assert draw.shade((0.5, 0.5, 1.0), 3) == (1.0, 1.0, 1.0)
    assert draw.mix(BLACK, WHITE, 0.25) == (0.25, 0.25, 0.25)
    assert draw.rgb("#FF8000") == (1.0, pytest.approx(128 / 255), 0.0)


def test_text_width_grows_with_tracking_and_text_lands_where_anchored():
    s, c = surface()
    plain = draw.text_width(c, "Hello", "serif", 30)
    assert plain > 0 and draw.text_width(c, "Hello", "serif", 30, track=4) == pytest.approx(plain + 16)
    assert draw.text_width(c, "", "serif", 30) == 0
    w = draw.text(c, "Hello", 100, 60, "serif", 30, BLACK, anchor="c")
    assert w == pytest.approx(plain)
    assert pixel(s, 100, 55) != (255, 255, 255)        # ink in the middle of a centred word
    assert pixel(s, 5, 55) == (255, 255, 255)           # none at the far left


def test_text_anchors_right_and_left():
    s, c = surface()
    draw.text(c, "Hi", 190, 60, "serif", 30, BLACK, anchor="r")
    assert all(pixel(s, x, 55) == (255, 255, 255) for x in range(0, 120))
    s, c = surface()
    draw.text(c, "Hi", 10, 60, "serif", 30, BLACK)
    assert all(pixel(s, x, 55) == (255, 255, 255) for x in range(100, 200))


def test_wrap_breaks_lines_at_the_width_and_never_splits_a_word():
    s, c = surface()
    one = draw.text_width(c, "word", "serif", 20)
    lines = draw.wrap(c, "word word word word word", "serif", 20, one * 2.5)
    assert lines == ["word word", "word word", "word"]
    assert draw.wrap(c, "supercalifragilistic", "serif", 20, 10) == ["supercalifragilistic"]
    assert draw.wrap(c, "", "serif", 20, 100) == []


def test_fill_rrect_and_circle_paint_their_insides_and_not_outside():
    s, c = surface()
    draw.fill_rrect(c, 20, 20, 100, 60, 12, RED)
    assert pixel(s, 70, 50) == (255, 0, 0)
    assert pixel(s, 21, 21) == (255, 255, 255)          # the rounded corner is cut
    assert pixel(s, 150, 50) == (255, 255, 255)
    draw.circle(c, 160, 60, 20, fill=BLUE, stroke=BLACK, lw=4)
    assert pixel(s, 160, 60) == (0, 0, 255)
    assert pixel(s, 160, 41) == (0, 0, 0)


def test_poly_and_line_with_alpha_blend_onto_the_background():
    s, c = surface()
    draw.poly(c, [(10, 10), (110, 10), (110, 110), (10, 110)], fill=BLACK, alpha=0.5)
    assert pixel(s, 60, 60) in ((127, 127, 127), (128, 128, 128))   # half black, either rounding
    draw.line(c, [(120, 60), (190, 60)], GREEN, lw=6)
    assert pixel(s, 150, 60) == (0, 255, 0)
    draw.poly(c, [(0, 0), (1, 1)], fill=BLACK)           # too few points: nothing drawn, no error


def test_bezier_cut_and_arrow_progress():
    pts = draw.bezier((0, 0), (0, 0), (100, 0), (100, 0), n=10)
    assert pts[0] == (0, 0) and pts[-1] == (100, 0) and len(pts) == 11
    assert draw.cut([(0, 0), (100, 0)], 0.5) == [(0, 0), (50.0, 0.0)]
    assert draw.cut([(0, 0), (100, 0)], 1.0) == [(0, 0), (100, 0)]
    s, c = surface()
    draw.arrow(c, [(10, 60), (190, 60)], RED, lw=6, progress=0.0)
    assert pixel(s, 50, 60) == (255, 255, 255)
    draw.arrow(c, [(10, 60), (190, 60)], RED, lw=6, progress=0.5)
    assert pixel(s, 50, 60) == (255, 0, 0) and pixel(s, 150, 60) == (255, 255, 255)
    draw.arrow(c, [(10, 60), (190, 60)], RED, lw=6, progress=1.0, head=20)
    assert pixel(s, 186, 60) == (255, 0, 0)


def test_tag_returns_its_pill_and_fills_it():
    s, c = surface()
    x, y, w, h = draw.tag(c, "Hi", 20, 60, "serif", 20, fill=BLUE, colour=WHITE)
    assert (x, y) == (20, 60 - h / 2) and w > 20 and h == 20 + 18
    assert pixel(s, int(x + 3), 60) == (0, 0, 255)
    assert draw.tag(c, "Hi", 20, 60, "serif", 20, fill=BLUE, colour=WHITE, alpha=0) == (20, 60, 0, 0)


def test_callout_dimension_badge_and_hand_leave_their_marks():
    s, c = surface()
    draw.callout(c, "x", (20, 20), (100, 60), "serif", 16, leader=RED, fill=RED, colour=WHITE)
    assert pixel(s, 20, 20) == (255, 0, 0)               # the dot on the target
    s, c = surface()
    draw.dimension(c, (20, 100), (180, 100), "160", "serif", 16, colour=GREEN, text_colour=WHITE)
    assert pixel(s, 100, 100) in ((0, 255, 0), (255, 255, 255))
    assert pixel(s, 20, 108) == (0, 255, 0)              # the end tick
    s, c = surface()
    draw.badge(c, 50, 50, True, GREEN, WHITE, r=20)
    draw.badge(c, 150, 50, False, RED, WHITE, r=20)
    assert pixel(s, 50, 35) == (0, 255, 0) and pixel(s, 150, 35) == (255, 0, 0)
    s, c = surface(400, 200)
    draw.hand(c, 300, 100, angle=0.0, scale=1.0, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE)
    assert pixel(s, 290, 100) == (255, 204, 153)         # skin at the fingers
    assert pixel(s, 160, 100) == (0, 0, 255)             # the sleeve behind the wrist
    draw.hand(c, 100, 100, angle=math.pi, scale=1.0, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE,
              label="L", label_fill=RED, label_colour=WHITE, label_font="serif", alpha=0.0)


def test_an_arrow_with_a_head_of_0_is_a_line_to_its_end_and_no_head():
    s, c = surface()
    draw.arrow(c, [(20, 50), (180, 50)], RED, lw=6, head=20)
    assert pixel(s, 164, 55) == (255, 0, 0)                 # well inside the head, beside the 6 px line
    s, c = surface()
    draw.arrow(c, [(20, 50), (180, 50)], RED, lw=6, head=0)
    assert pixel(s, 164, 55) == (255, 255, 255) and pixel(s, 178, 50) == (255, 0, 0)
