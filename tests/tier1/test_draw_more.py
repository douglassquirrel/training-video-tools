"""videotools.draw: the branches the first tests left out (tracking, strokes, dashes, curves,
mirrored and labelled hands, alpha zero everywhere)."""

import math

from tests.tier1.test_draw import BLACK, BLUE, GREEN, RED, WHITE, pixel, surface
from videotools import draw


def test_tracked_text_is_drawn_letter_by_letter_wider_than_plain():
    s, c = surface(400, 100)
    plain = draw.text(c, "WIDE", 10, 60, "serif", 30, BLACK)
    s2, c2 = surface(400, 100)
    tracked = draw.text(c2, "WIDE", 10, 60, "serif", 30, BLACK, track=10)
    assert tracked == plain + 30
    assert any(pixel(s2, x, 55) != (255, 255, 255) for x in range(int(plain) + 12, int(tracked) + 10))


def test_poly_strokes_with_its_own_alpha_and_line_dashes():
    s, c = surface()
    draw.poly(c, [(20, 20), (180, 20), (180, 100), (20, 100)], fill=WHITE, stroke=RED, lw=6, stroke_alpha=1.0)
    assert pixel(s, 100, 20) == (255, 0, 0)
    draw.poly(c, [(20, 20), (180, 20), (180, 100)], stroke=BLUE, lw=4)
    assert pixel(s, 180, 60) == (0, 0, 255)
    s, c = surface()
    draw.line(c, [(10, 60), (190, 60)], BLACK, lw=4, dash=[20, 20])
    assert pixel(s, 20, 60) == (0, 0, 0) and pixel(s, 40, 60) == (255, 255, 255)
    draw.line(c, [(10, 60)], BLACK)                       # one point: nothing drawn, no error


def test_circle_stroke_only_and_fill_rrect_with_a_border():
    s, c = surface()
    draw.circle(c, 60, 60, 30, stroke=GREEN, lw=6)
    assert pixel(s, 60, 60) == (255, 255, 255) and pixel(s, 60, 30) == (0, 255, 0)
    draw.fill_rrect(c, 110, 20, 80, 80, 8, WHITE, stroke=RED, lw=4)
    assert pixel(s, 150, 20) == (255, 0, 0) and pixel(s, 150, 60) == (255, 255, 255)


def test_cut_keeps_whole_points_before_the_fraction_and_arrow_follows_a_curve():
    pts = [(0, 0), (10, 0), (20, 0), (30, 0)]
    assert draw.cut(pts, 0.5) == [(0, 0), (10, 0), (15.0, 0.0)]
    assert draw.cut([(0, 0), (0, 0)], 0.5) == [(0, 0), (0, 0)]           # a zero-length segment
    s, c = surface(300, 200)
    draw.arrow(c, [(10, 100), (100, 10), (200, 190), (290, 100)], RED, lw=6, progress=1.0, head=16)
    assert pixel(s, 150, 100) == (255, 0, 0)                            # the curve passes the middle
    draw.arrow(c, [(10, 100), (12, 100)], BLUE, progress=0.001)        # too short: nothing
    draw.arrow(c, [(10, 100), (290, 100)], BLUE, alpha=0.0)


def test_annotations_with_alpha_zero_draw_nothing():
    s, c = surface()
    draw.badge(c, 50, 50, True, GREEN, WHITE, alpha=0.0)
    draw.callout(c, "x", (20, 20), (100, 60), "serif", 16, leader=RED, fill=RED, colour=WHITE, alpha=0.0)
    draw.dimension(c, (20, 100), (180, 100), "160", "serif", 16, colour=GREEN, text_colour=WHITE, alpha=0.0)
    draw.hand(c, 100, 60, angle=0.0, scale=1.0, skin=RED, outline=BLACK, sleeve=BLUE, alpha=0.0)
    assert all(pixel(s, x, y) == (255, 255, 255) for x in range(0, 200, 10) for y in range(0, 120, 10))


def test_a_mirrored_labelled_hand_draws_its_label_at_the_wrist():
    s, c = surface(400, 200)
    draw.hand(c, 300, 100, angle=0.0, scale=1.0, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE, mirror=True,
              label="L", label_fill=RED, label_colour=WHITE, label_font="serif")
    assert pixel(s, 150, 100) == (255, 0, 0)                            # the label roundel, 150 px behind the fingertip
    assert pixel(s, 290, 100) == (255, 204, 153)
    s, c = surface(400, 200)
    draw.hand(c, 100, 100, angle=math.pi, scale=0.5, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE)
    assert pixel(s, 175, 100) == (0, 0, 255)                            # half size, pointing left: sleeve to the right


def test_a_tag_anchored_right_ends_at_x():
    s, c = surface()
    x, y, w, h = draw.tag(c, "Hi", 190, 60, "serif", 20, fill=BLUE, colour=WHITE, anchor="r")
    assert x + w == 190 and pixel(s, 188, 60) == (0, 0, 255)


def test_the_hands_label_takes_a_size_and_its_roundel_grows_with_it():
    small, c = surface(400, 200)
    draw.hand(c, 300, 100, angle=0.0, scale=1.0, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE,
              label="L", label_fill=RED, label_colour=(1, 1, 1), label_font="Sans")
    big, c = surface(400, 200)
    draw.hand(c, 300, 100, angle=0.0, scale=1.0, skin=(1, 0.8, 0.6), outline=BLACK, sleeve=BLUE,
              label="L", label_fill=RED, label_colour=(1, 1, 1), label_font="Sans", label_size=56)
    wrist = (300 - 150, 100)                                          # the roundel's centre at angle 0
    assert pixel(small, wrist[0] + 18, wrist[1]) == pixel(big, wrist[0] + 18, wrist[1]) == (255, 0, 0)   # inside 21
    assert pixel(small, wrist[0] + 36, wrist[1]) != (255, 0, 0)       # outside the 21 px roundel
    assert pixel(big, wrist[0] + 36, wrist[1]) == (255, 0, 0)         # inside the 42 px one
