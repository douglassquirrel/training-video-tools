"""stills on a video file (item 24): the times, the names, the grid and ffmpeg's scene report,
as pure functions."""

import pytest

from videotools import cli, video_stills


def test_at_times_are_read_in_the_order_given_each_at_most_once():
    assert video_stills.parse_at("0,1.5,3") == [0.0, 1.5, 3.0]
    assert video_stills.parse_at("12.4, 3") == [12.4, 3.0]
    for bad, why in [("", "--at needs at least one time in seconds, such as 0,1.5,3"),
                     ("1,,2", "--at needs at least one time in seconds, such as 0,1.5,3"),
                     ("1,x", "--at: 'x' is not a time in seconds"),
                     ("1,-2", "--at: a time cannot be negative (-2)"),
                     ("1,2,1", "--at: 1 is given twice")]:
        with pytest.raises(cli.Failure) as e:
            video_stills.parse_at(bad)
        assert (str(e.value), e.value.code) == (why, cli.USAGE)


def test_every_n_seconds_runs_from_zero_while_less_than_the_length():
    assert video_stills.every_times(2, 7.0) == [0.0, 2.0, 4.0, 6.0]
    assert video_stills.every_times(2, 6.0) == [0.0, 2.0, 4.0]          # the end itself is not a frame
    assert video_stills.every_times(0.1, 0.35) == [0.0, 0.1, 0.2, 0.3]  # multiples, not a running sum
    for bad in (0, -1.5):
        with pytest.raises(cli.Failure) as e:
            video_stills.every_times(bad, 7.0)
        assert (str(e.value), e.value.code) == ("--every must be more than 0", cli.USAGE)


def test_a_still_is_named_by_its_time_so_names_sort_in_time_order():
    assert video_stills.still_name(12.4) == "t0012.40.png"
    assert video_stills.still_name(0) == "t0000.00.png"
    assert video_stills.still_name(1.005) == "t0001.00.png"          # two decimals, as the label
    assert video_stills.still_name(12345.678) == "t12345.68.png"     # the width grows past four digits
    names = [video_stills.still_name(t) for t in (0, 1.5, 3, 12.4, 100)]
    assert sorted(names) == names
    assert video_stills.label(12.4) == "12.40 s"
    assert video_stills.listing_line(12.4) == "12.40 t0012.40.png"


def test_the_default_grid_is_the_smallest_square_that_holds_the_frames_at_most_five_across():
    assert [video_stills.choose_grid(n) for n in (1, 2, 4, 5, 9, 10, 25)] == \
        [(1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (5, 5)]
    assert video_stills.choose_grid(26) == (5, 6)                    # never wider than 5 cells (1800 px)
    assert video_stills.choose_grid(31) == (5, 7)


def test_a_cell_is_360_wide_and_as_tall_as_the_video_needs_plus_the_label_strip():
    assert video_stills.cell_size(480, 854) == (360, 641 + 36)       # a vertical Short keeps its proportions
    assert video_stills.cell_size(854, 480) == (360, 203 + 36)       # landscape; 640.5 and 202.3 rounded up,
    assert video_stills.cell_size(1920, 1080) == (360, 203 + 36)     # so the frame fits at the full 360 wide
    from videotools import sheet
    assert sheet.frame_size(video_stills.cell_size(480, 854), (480, 854)) == (360, 640)
    assert sheet.frame_size(video_stills.cell_size(854, 480), (854, 480)) == (360, 202)


REPORT = """[Parsed_metadata_1 @ 0x7a0c62280] frame:0    pts:25600   pts_time:2
[Parsed_metadata_1 @ 0x7a0c62280] lavfi.scene_score=0.400000
[Parsed_metadata_1 @ 0x7a0c62280] frame:1    pts:51200   pts_time:4.04
[Parsed_metadata_1 @ 0x7a0c62280] lavfi.scene_score=0.350000
"""   # the shape real ffmpeg 9.0.2 printed (PLAN.md "Things checked", 17 October 2026)


def test_the_changes_are_the_first_frame_then_each_pts_time_of_ffmpegs_scene_report():
    assert video_stills.change_times(REPORT) == [0.0, 2.0, 4.04]
    assert video_stills.change_times("") == [0.0]                    # no cut: the first frame alone
    assert video_stills.change_times("frame:0 pts:0 pts_time:0\n") == [0.0]   # a cut at 0 is not twice


def test_the_threshold_is_a_number_from_0_to_1():
    assert video_stills.parse_threshold("0.3") == 0.3
    assert (video_stills.parse_threshold("0"), video_stills.parse_threshold("1")) == (0.0, 1.0)
    for bad in ("1.5", "-0.1", "x"):
        with pytest.raises(cli.Failure) as e:
            video_stills.parse_threshold(bad)
        assert (str(e.value), e.value.code) == (f"--threshold should be a number from 0 to 1, not '{bad}'", cli.USAGE)


def test_a_grid_needs_two_whole_numbers_each_at_least_one():
    assert video_stills.parse_grid("3x2") == (3, 2)
    assert video_stills.parse_grid("1X1") == (1, 1)
    assert video_stills.parse_grid(None) is None
    for bad in ("0x3", "3x0", "0x0", "-1x2"):
        with pytest.raises(cli.Failure) as e:
            video_stills.parse_grid(bad)
        assert (str(e.value), e.value.code) == (f"--grid needs at least one column and one row, not '{bad}'", cli.USAGE)
    for bad in ("2x", "x", "3", "2x2x2", "axb"):
        with pytest.raises(cli.Failure) as e:
            video_stills.parse_grid(bad)
        assert (str(e.value), e.value.code) == (f"--grid should be COLUMNSxROWS, not '{bad}'", cli.USAGE)
