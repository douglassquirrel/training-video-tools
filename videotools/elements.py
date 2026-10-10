"""Where the video-elements library is: the `--elements` and `--renderer` flags, else the config
file's `VIDEO_ELEMENTS_DIR` and `RSVG_CONVERT` (PLAN.md item 15, "Where the library is").

Standard library only; runs on Python 3.9.
"""

import os


def add_arguments(p):
    """The two flags, on every command that draws and on check-script."""
    p.add_argument("--elements", metavar="DIR", help="the video-elements repository, the folder holding "
                   "videoelements/ and elements/ (default: VIDEO_ELEMENTS_DIR in the config file)")
    p.add_argument("--renderer", metavar="PATH", help="the SVG renderer, rsvg-convert (default: RSVG_CONVERT in the "
                   "config file, else rsvg-convert on PATH)")


def settings(args, conf):
    """(folder, renderer): each the flag, else the config setting, else None; `~` means home."""
    folder = args.elements or conf.get("VIDEO_ELEMENTS_DIR")
    renderer = args.renderer or conf.get("RSVG_CONVERT")
    return (os.path.expanduser(folder) if folder else None), (renderer or None)
