"""`stills VIDEO …` (PLAN.md item 24): frames of a video file at given times, every so many seconds
or where the picture changes, written singly and, with --sheet, on a labelled contact sheet. The
pure parts live here; `stills.py` runs the command.
"""

import re

from videotools import cli


def parse_at(text):
    """The times of --at, in seconds, in the order given, each at most once."""
    parts = [p.strip() for p in (text or "").split(",")]
    if not parts or any(p == "" for p in parts):
        raise cli.Failure("--at needs at least one time in seconds, such as 0,1.5,3", cli.USAGE)
    times = []
    for p in parts:
        try:
            t = float(p)
        except ValueError:
            raise cli.Failure(f"--at: '{p}' is not a time in seconds", cli.USAGE) from None
        if t < 0:
            raise cli.Failure(f"--at: a time cannot be negative ({p})", cli.USAGE)
        if t in times:
            raise cli.Failure(f"--at: {p} is given twice", cli.USAGE)
        times.append(t)
    return times


def every_times(step, length):
    """Every `step` seconds from 0 while less than `length`: multiples, so no running sum drifts."""
    if not step > 0:
        raise cli.Failure("--every must be more than 0", cli.USAGE)
    times, i = [], 0
    while round(i * step, 6) < length:
        times.append(round(i * step, 6))
        i += 1
    return times


def still_name(seconds):
    """`t0012.40.png`: the time to two decimals, at least four digits before the point, so names sort."""
    return f"t{seconds:07.2f}.png"


def label(seconds):
    return f"{seconds:.2f} s"


def listing_line(seconds):
    """One line of stills.txt: the time, then the file name."""
    return f"{seconds:.2f} {still_name(seconds)}"


CELL_WIDTH = 360      # a frame's width on the sheet: a vertical Short's frames stay readable
MAX_COLUMNS = 5       # 1800 px across at most


def choose_grid(count):
    """(columns, rows) for `count` frames: the smallest square's side across, at most 5; rows as needed."""
    columns = 1
    while columns * columns < count and columns < MAX_COLUMNS:
        columns += 1
    return columns, -(-count // columns)


def cell_size(width, height):
    """A sheet cell for frames of width x height: 360 wide, the frame's height at that width, plus the strip."""
    from videotools import sheet
    return CELL_WIDTH, CELL_WIDTH * height // width + sheet.STRIP


def change_times(report):
    """The first frame, then the `pts_time:` of every frame ffmpeg's `select='gt(scene,T)',metadata=print`
    chose, from its stderr; a frame at 0 is not listed twice."""
    times = [0.0]
    for m in re.finditer(r"\bpts_time:(\S+)", report):
        t = float(m.group(1))
        if t not in times:
            times.append(t)
    return times


def parse_threshold(text):
    try:
        value = float(text)
    except ValueError:
        value = -1.0
    if not 0 <= value <= 1:
        raise cli.Failure(f"--threshold should be a number from 0 to 1, not '{text}'", cli.USAGE)
    return value
