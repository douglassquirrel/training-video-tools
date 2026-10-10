"""The end card's credit lines for the library's art (PLAN.md item 16): below the script's
credit and the brand's illustration credit, in the same style, wrapped when long; a video with
no library elements draws exactly today's card."""

import os

import pytest

from tests.tier2.conftest import STUBS, cropped, narrated
from tests.tier2.test_frame import hex_rgb, pixel, rendered
from tests.tier2.test_perform import describe
from videotools import frame

INVENTED = os.path.join(STUBS, "video-elements")
MUTED = hex_rgb("#6B6560")             # the paperboat kit's muted: the credit lines' colour
BACKGROUND = hex_rgb("#F7F3EA")


def _band_has_text(surface, y, x0=500, x1=1420):
    """True when the row y (and the two beside it) hold some pixel of the muted text colour."""
    return any(pixel(surface, x, yy) == MUTED for yy in (y - 1, y, y + 1) for x in range(x0, x1, 2))


def _with_setting(script, value):
    text = open(script, encoding="utf-8").read()
    open(script, "w", encoding="utf-8").write(text.replace("| credit |", f"| element-credits | {value} | |\n| credit |"))
    return script


@pytest.fixture
def plain(example):
    cropped(example)
    narrated(example)
    return example


def test_the_library_credit_lines_are_drawn_below_the_two_existing_lines(plain):
    video = frame.Video(describe(plain), INVENTED, None)
    end = rendered(video, "end", 2.5)
    assert _band_has_text(end, 860) and _band_has_text(end, 896)      # the script's credit, the brand's
    assert _band_has_text(end, 932) and _band_has_text(end, 968)      # "Icons: Invented Icons", "People: …"
    assert not _band_has_text(end, 1004)


def test_none_draws_exactly_todays_card_and_so_does_a_video_with_no_library_elements(plain, tmp_path):
    before = rendered(frame.Video(plain), "end", 2.5)
    todays = bytes(before.get_data())
    video = frame.Video(_with_setting(describe(plain), "none"), INVENTED, None)
    assert bytes(rendered(video, "end", 2.5).get_data()) == todays


def test_wording_replaces_the_lines_and_a_long_one_wraps_without_reaching_the_bottom(plain):
    long = " ".join(["Art by the invented crew of the paper boat workshop,"] * 3)
    video = frame.Video(_with_setting(describe(plain), long), INVENTED, None)
    end = rendered(video, "end", 2.5)
    assert _band_has_text(end, 932) and _band_has_text(end, 968)      # two lines at least
    assert all(pixel(end, x, 1060) == BACKGROUND for x in range(500, 1420, 4))   # the bottom margin stays clear
