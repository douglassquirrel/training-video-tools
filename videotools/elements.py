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


def open_library(folder, renderer):
    """The video-elements library at `folder` (the repository root), opened through its
    interface: the root goes on the import path at this point of use (once), `videoelements` is
    imported from it, and `library.open(folder, renderer=…)` is called; `renderer` None leaves
    the library its own default. A library whose descriptions lack `counts` (and so is older
    than video-elements d203f0a) is refused too. Every refusal is one message in words, exit 3."""
    import importlib
    import sys

    from videotools import cli, config
    if not folder:
        raise cli.Failure(f"VIDEO_ELEMENTS_DIR is not set in {config.path()} and no --elements was given; a script "
                          "that describes a scene's cast needs the video-elements repository "
                          "(README, \"Configuration\")")
    if not os.path.isdir(folder):
        raise cli.Failure(f"{folder}: video-elements folder not found (VIDEO_ELEMENTS_DIR in {config.path()}, "
                          "or --elements)")
    if not os.path.isdir(os.path.join(folder, "videoelements")):
        raise cli.Failure(f"{folder} has no videoelements/ package: VIDEO_ELEMENTS_DIR names the root of the "
                          "video-elements repository, the folder holding videoelements/ and elements/")
    root = os.path.abspath(folder)
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        library = importlib.import_module("videoelements.library")
    except Exception as e:   # the library's own code: any error is reported, none classified
        raise cli.Failure(f"videoelements at {folder} could not be imported: {type(e).__name__}: {e}") from e
    kwargs = {"renderer": renderer} if renderer else {}
    try:
        lib = library.open(folder, **kwargs)
    except Exception as e:   # its Failure carries .problems; anything else is reported as it is
        problems = getattr(e, "problems", None) or [f"{type(e).__name__}: {e}"]
        listed = "\n".join("  - " + p for p in problems)
        raise cli.Failure(f"the video-elements library at {folder} refuses to open:\n{listed}") from e
    old = [name for name in lib.names() if "counts" not in lib.element(name)]
    if old:                  # no older library is allowed for: every description has `fit` and `counts`
        raise cli.Failure(f"the video-elements library at {folder} is older than these tools need: the description "
                          f"of {old[0]} does not say what its indexes count (no 'counts'); update the video-elements "
                          "repository")
    return lib


def from_args(args):
    """(folder, renderer) for a command: the flags, else the config file; a malformed config file
    is a refusal in words (exit 3)."""
    from videotools import cli, config
    try:
        conf = config.read()
    except config.ConfigError as e:
        raise cli.Failure(str(e)) from e
    return settings(args, conf)
