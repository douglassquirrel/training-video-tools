"""crop-insets: cut each `## Insets` box from the source image, sized for the reference column.

Each box becomes `work/insets/<key>.png`, scaled to fit 388 px wide and 330 px tall (360 when
the box is taller than it is wide); the whole image becomes `work/insets/title-page.png`, 750 px
tall, for the title card. Refuses a box outside the image or empty, and any existing output.
Needs Pillow, imported only when it runs.
"""

import argparse
import os

from videotools import cli, script

PROG = "crop-insets"
COLUMN_WIDTH, PANEL_HEIGHT, TALL_PANEL_HEIGHT, PAGE_HEIGHT = 388, 330, 360, 750
PAGE = "title-page"


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Cut each of the script's Insets boxes out of its "
                                "source-image, sized for the reference column, and the whole page for "
                                "the title card, into the video's work/insets/.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--dry-run", action="store_true", help="list the files it would write; write nothing")
    return p


def fit(width, height, max_width, max_height):
    """The size of a width x height image scaled to fit the box, as the prototype did."""
    scale = min(max_width / width, max_height / height)
    return int(width * scale), int(height * scale)


def plan(data, image_size):
    """[(file name, key or None, box, size)] for every inset and the page; or raises Failure."""
    width, height = image_size
    jobs, problems = [], []
    for key, value in data["insets"].items():
        x0, y0, x1, y1 = (int(v) for v in value.split())
        if key == PAGE:
            problems.append(f"an inset cannot be called '{PAGE}'; that name is the whole page's")
        elif x1 > width or y1 > height:
            problems.append(f"inset {key}: box {value} is outside the image ({width}x{height})")
        elif x1 <= x0 or y1 <= y0:
            problems.append(f"inset {key}: box {value} is empty")
        else:
            w, h = x1 - x0, y1 - y0
            size = fit(w, h, COLUMN_WIDTH, TALL_PANEL_HEIGHT if h > w else PANEL_HEIGHT)
            jobs.append((f"{key}.png", key, (x0, y0, x1, y1), size))
    if problems:
        raise cli.Failure("\n".join(problems))
    jobs.append((f"{PAGE}.png", None, (0, 0, width, height), fit(width, height, 10 ** 9, PAGE_HEIGHT)))
    return jobs


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError) as f:
        return cli.report(PROG, cli.Failure(str(f).replace("\n", "\n" + PROG + ": "), getattr(f, "code", cli.REFUSED)))


def _run(args):
    data = script.read(args.SCRIPT)
    source = script.settings(data)["source-image"]
    if not source:
        raise cli.Failure("the script's Settings have no 'source-image'; crop-insets needs one")
    try:
        from PIL import Image
    except ImportError as e:
        raise cli.Failure(f"Pillow is not installed in this Python ({e}); install it into the venv as the README says",
                          cli.EXTERNAL) from e
    folder = script.folder(args.SCRIPT)
    image = Image.open(os.path.join(folder, source))
    jobs = plan(data, image.size)
    out_dir = os.path.join(folder, "work", "insets")
    existing = [os.path.join(out_dir, name) for name, _, _, _ in jobs if os.path.lexists(os.path.join(out_dir, name))]
    if existing and not args.dry_run:
        raise cli.Failure("these would be written over; delete them first:\n" + "\n".join("  " + p for p in existing))
    for name, key, (x0, y0, x1, y1), (w, h) in jobs:
        what = f"inset {key}, {x1 - x0}x{y1 - y0} at {x0} {y0}" if key else "the whole page"
        print(f"{os.path.join(out_dir, name)}  {w}x{h}  ({what})")
        if not args.dry_run:
            os.makedirs(out_dir, exist_ok=True)
            image.crop((x0, y0, x1, y1)).resize((w, h), Image.LANCZOS).save(os.path.join(out_dir, name))
    if args.dry_run:
        print(f"{len(jobs)} files; nothing written (dry run).")
    else:
        print(f"Wrote {len(jobs)} files to {out_dir}")
    return cli.OK
