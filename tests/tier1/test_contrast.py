"""brand-preview: WCAG contrast ratios (relative luminance, 1 to 21) and the text thresholds."""

from videotools import contrast


def test_black_on_white_is_21_and_a_colour_on_itself_is_1():
    assert round(contrast.ratio((0, 0, 0), (1, 1, 1)), 1) == 21.0
    assert contrast.ratio((0.5, 0.2, 0.9), (0.5, 0.2, 0.9)) == 1.0


def test_the_ratio_is_the_same_either_way_round_and_matches_the_known_value_for_767676_on_white():
    grey, white = (0x76 / 255,) * 3, (1, 1, 1)
    assert round(contrast.ratio(grey, white), 2) == 4.54          # the WCAG example pair
    assert contrast.ratio(grey, white) == contrast.ratio(white, grey)


def test_the_verdict_names_the_4_5_and_3_thresholds():
    assert contrast.verdict(4.5) == "OK for text"
    assert contrast.verdict(4.49) == "large text only (3-4.5)"
    assert contrast.verdict(3.0) == "large text only (3-4.5)"
    assert contrast.verdict(2.99) == "fails (under 3)"
