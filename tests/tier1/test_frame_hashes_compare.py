"""frame-hashes: which hashed frames differ from a reference, and how that reads."""

from videotools import frame_hashes


def test_differing_and_missing_frames_are_found_in_frame_order():
    hashes = {"0": "a", "10": "b", "20": "c", "30": "d"}
    reference = {"0": "a", "10": "x", "30": "d", "40": "e"}
    bad, missing = frame_hashes.compare(hashes, reference)
    assert bad == [10, 20] and missing == [20]


def test_the_report_line_names_the_first_twelve_frames_then_an_ellipsis():
    assert frame_hashes.describe([], []) == "all match"
    assert frame_hashes.describe([3, 7], []) == "2 differ (frames 3, 7)"
    assert frame_hashes.describe([3, 7], [7]) == "2 differ (frames 3, 7), 1 not in the reference"
    assert frame_hashes.describe(list(range(0, 130, 10)), []) == (
        "13 differ (frames 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, …)")
