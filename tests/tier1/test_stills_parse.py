"""stills' own parsing of SCENE:SECONDS and --grid (the grid's tests came here from the video form's,
which moved to video-tools on 13 November 2026)."""

import pytest

from videotools import cli, stills


def test_a_grid_needs_two_whole_numbers_each_at_least_one():
    assert stills.parse_grid("3x2") == (3, 2)
    assert stills.parse_grid("1X1") == (1, 1)
    for bad in ("0x3", "3x0", "0x0", "-1x2"):
        with pytest.raises(cli.Failure) as e:
            stills.parse_grid(bad)
        assert (str(e.value), e.value.code) == (f"--grid needs at least one column and one row, not '{bad}'", cli.USAGE)
    for bad in ("2x", "x", "3", "2x2x2", "axb"):
        with pytest.raises(cli.Failure) as e:
            stills.parse_grid(bad)
        assert (str(e.value), e.value.code) == (f"--grid should be COLUMNSxROWS, not '{bad}'", cli.USAGE)


def test_a_frame_needs_a_scene_key_a_colon_and_a_number_of_seconds():
    assert stills.parse_frames("A:1.5, B:-2") == [("A", 1.5, "A:1.5"), ("B", -2.0, "B:-2")]
    for bad in (":1.5", "A1.5", "A:", "A:x"):
        with pytest.raises(cli.Failure) as e:
            stills.parse_frames(bad)
        assert (str(e.value), e.value.code) == (f"'{bad}' is not SCENE:SECONDS", cli.USAGE)
