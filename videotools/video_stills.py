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


DEFAULT_THRESHOLD = 0.3   # ffmpeg's usual scene-change score for a cut; a cut between flat colours scores 0.4
CELL_WIDTH = 360      # a frame's width on the sheet: a vertical Short's frames stay readable
MAX_COLUMNS = 5       # 1800 px across at most


def choose_grid(count):
    """(columns, rows) for `count` frames: the smallest square's side across, at most 5; rows as needed."""
    columns = 1
    while columns * columns < count and columns < MAX_COLUMNS:
        columns += 1
    return columns, -(-count // columns)


def cell_size(width, height):
    """A sheet cell for frames of width x height: 360 wide, the frame's height at that width (rounded up,
    so sheet.frame_size fits the frame at the full 360), plus the strip."""
    from videotools import sheet
    return CELL_WIDTH, -(-CELL_WIDTH * height // width) + sheet.STRIP


def change_times(report):
    """The first frame, then the `pts_time:` of every frame ffmpeg's `select='gt(scene,T)',metadata=print`
    chose, from its stderr; a frame at 0 is not listed twice."""
    times = [0.0]
    for m in re.finditer(r"\bpts_time:(\S+)", report):
        t = float(m.group(1))
        if t not in times:
            times.append(t)
    return times


def parse_grid(text):
    """(columns, rows) of `--grid CxR`, or None when no grid was given."""
    if text is None:
        return None
    try:
        columns, rows = (int(v) for v in text.lower().split("x"))
    except ValueError:
        raise cli.Failure(f"--grid should be COLUMNSxROWS, not '{text}'", cli.USAGE) from None
    if columns < 1 or rows < 1:
        raise cli.Failure(f"--grid needs at least one column and one row, not '{text}'", cli.USAGE)
    return columns, rows


def parse_threshold(text):
    try:
        value = float(text)
    except ValueError:
        value = -1.0
    if not 0 <= value <= 1:
        raise cli.Failure(f"--threshold should be a number from 0 to 1, not '{text}'", cli.USAGE)
    return value


def run(args):
    """`stills VIDEO …`: the frames chosen, written singly into --out and listed in stills.txt."""
    import os

    from videotools import ffmpeg
    video, folder = args.SCRIPT, args.out
    modes = [f for f, on in (("--at", args.at is not None), ("--every", args.every is not None),
                             ("--changes", args.changes)) if on]
    if not modes:
        raise cli.Failure("choose how to pick the frames of a video file: --at, --every or --changes", cli.USAGE)
    if len(modes) > 1:
        raise cli.Failure(f"give one of --at, --every and --changes, not {' and '.join(modes)}", cli.USAGE)
    if args.threshold is not None and not args.changes:
        raise cli.Failure("--threshold goes with --changes", cli.USAGE)
    threshold = parse_threshold(args.threshold) if args.threshold is not None else DEFAULT_THRESHOLD
    if args.every is not None and not args.every > 0:
        raise cli.Failure("--every must be more than 0", cli.USAGE)
    at = parse_at(args.at) if args.at is not None else None
    grid = parse_grid(args.grid)
    if args.sheet:
        cli.refuse_existing(args.sheet)
    ffmpeg.require("ffmpeg")
    ffmpeg.require("ffprobe")
    cli.need("PIL")
    from PIL import Image
    info = ffmpeg.probe(video)
    length, width, height = info["duration"], info["width"], info["height"]
    listing = os.path.join(folder, "stills.txt")
    cli.refuse_existing(listing)        # before the scan: nothing is read for a run that will be refused
    if args.changes:
        times = change_times(ffmpeg.scene_report(video, threshold))
    elif args.every is not None:
        times = every_times(args.every, length)
    else:
        times = at
    for t in times:
        if t >= length:
            raise cli.Failure(f"{t:g} s is past the end of {video} ({length:.3f} s)", cli.USAGE)
    stills = [(t, os.path.join(folder, still_name(t))) for t in times]
    for _, path in stills:
        cli.refuse_existing(path)
    sheets = Sheets(args.sheet, grid, len(times), width, height) if args.sheet else None
    os.makedirs(folder, exist_ok=True)
    for i, (t, path) in enumerate(stills):
        data = ffmpeg.frame_at(video, t, width, height)
        img = Image.frombytes("RGB", (width, height), data)
        img.save(path)
        if sheets:
            sheets.add(i, img, label(t))
        print(f"{os.path.basename(path)} at {t:.3f} s")
    with open(listing, "w", encoding="utf-8") as f:
        f.write("".join(listing_line(t) + "\n" for t in times))
    if sheets:
        sheets.save()
    print(f"Wrote {len(stills)} stills to {folder}" + (sheets.said() if sheets else ""))
    return 0


class Sheets:
    """The contact sheet(s) of a run: cells 360 wide in the video's proportions, `grid` (or one
    chosen to fit) per sheet, as many sheets as the frames need; each frame pasted as it is read,
    its time in the strip under it. Every sheet's name is refused before any is read."""

    def __init__(self, out, grid, count, width, height):
        from PIL import Image, ImageDraw, ImageFont

        from videotools import sheet
        self.columns, self.rows = grid or choose_grid(count)
        self.cell = cell_size(width, height)
        self.per_sheet = self.columns * self.rows
        self.paths = sheet.names(out, -(-count // self.per_sheet))
        for path in self.paths:
            cli.refuse_existing(path)
        self.images = [Image.new("RGB", (self.columns * self.cell[0], self.rows * self.cell[1]), "white")
                       for _ in self.paths]
        self.draws = [ImageDraw.Draw(im) for im in self.images]
        self.font = ImageFont.load_default(size=sheet.LABEL_SIZE)
        self.paste = sheet.paste

    def add(self, index, img, text):
        which, where = divmod(index, self.per_sheet)
        x, y = (where % self.columns) * self.cell[0], (where // self.columns) * self.cell[1]
        self.paste(self.images[which], self.draws[which], img, x, y, self.cell, text, self.font)

    def save(self):
        for im, path in zip(self.images, self.paths):
            im.save(path)

    def said(self):
        if len(self.paths) == 1:
            return f" and the sheet {self.paths[0]}"
        return f" and {len(self.paths)} sheets {', '.join(self.paths)}"
