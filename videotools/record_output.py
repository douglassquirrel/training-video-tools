"""record-output: a finished video's row in the OUT.md beside it (PLAN.md item 31).

Adds a row for VIDEO (the script's `output` by default) after the table's last row: its name, its
modification time in TIME_ZONE (else the machine's zone), the commits it was made with, its size and
SHA-256, and a state; or, with --add-state, adds to the State of its row. Creates OUT.md when there is
none. Reads the script, the video (never opened for writing) and OUT.md; writes only OUT.md, whole,
through a temporary file and a rename. Refuses, before writing, everything PLAN.md item 31 lists.
Standard library only; runs git only to read a commit not given.
"""

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import tempfile

from videotools import cli, config, credits, outmd, script

PROG = "record-output"
TOOLS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))   # the checkout this runs from


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Add a finished video's row to the OUT.md beside it, or "
                                "add to the State of its row.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("VIDEO", nargs="?", help="the finished video (default: the script's output setting)")
    form = p.add_mutually_exclusive_group()
    form.add_argument("--state", metavar="TEXT", help="the new row's State (default: empty)")
    form.add_argument("--add-state", metavar="TEXT", help="add TEXT to the State of VIDEO's existing row instead")
    p.add_argument("--tools-commit", metavar="C", help="the training-video-tools commit the video was made with "
                   "(default: read with git from this checkout, which must be clean)")
    p.add_argument("--elements-commit", metavar="C", help="the video-elements commit (default: read with git from "
                   "the library's checkout, for a script that draws from it)")
    p.add_argument("--elements", metavar="DIR", help="the video-elements repository, to read its commit from "
                   "(default: VIDEO_ELEMENTS_DIR in the config file)")
    p.add_argument("--dry-run", action="store_true", help="print the row and write nothing")
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.add_state is not None and (args.tools_commit or args.elements_commit or args.elements):
        p.error("--add-state changes only a row's State; --tools-commit, --elements-commit and --elements are for "
                "adding a row")
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def _git(folder, what, flag):
    """The short commit of the git checkout at `folder`, which must have no uncommitted change."""
    if not os.path.exists(os.path.join(folder, ".git")):
        raise cli.Failure(f"{folder} is not a git checkout, so the {what} commit cannot be read from it; "
                          f"give {flag} COMMIT")
    git = shutil.which("git")
    if not git:
        raise cli.Failure(f"git is not installed, and is needed to read the commit of {folder}; install Xcode's "
                          f"command-line tools (xcode-select --install), or give {flag} COMMIT", cli.EXTERNAL)
    answers = []
    for question in (["rev-parse", "--short", "HEAD"], ["status", "--porcelain"]):
        p = subprocess.run([git, "-C", folder] + question, capture_output=True, text=True)
        if p.returncode != 0:
            raise cli.Failure(f"git could not read the commit of {folder} ({p.stderr.strip()}); give {flag} COMMIT",
                              cli.EXTERNAL)
        answers.append(p.stdout)
    changes = [line for line in answers[1].splitlines() if line.strip()]
    if changes:
        n = len(changes)
        raise cli.Failure(f"{folder} has {n} uncommitted change{'' if n == 1 else 's'}, so its commit would not say "
                          f"what made the video; commit them, or give {flag} COMMIT")
    return answers[0].strip()


def _elements_commit(args, data, conf):
    """The library's commit for the Made-with cell, or None when the script does not draw from it."""
    if args.elements_commit:
        return outmd.commit(args.elements_commit, "--elements-commit")
    if not credits.elements_used(data):
        return None
    folder = args.elements or conf.get("VIDEO_ELEMENTS_DIR")
    if not folder:
        raise cli.Failure("this script draws from the video-elements library, so its commit is recorded too; give "
                          "--elements-commit COMMIT, or --elements DIR (or VIDEO_ELEMENTS_DIR in "
                          f"{config.path()}) naming the library's checkout")
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        raise cli.Failure(f"{folder}: video-elements folder not found (--elements, or VIDEO_ELEMENTS_DIR in "
                          f"{config.path()}); give it, or --elements-commit COMMIT")
    return _git(os.path.realpath(folder), "video-elements", "--elements-commit")


def _sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
    except OSError as e:
        raise cli.Failure(f"{path} could not be read ({e.strerror}); nothing written") from e
    return h.hexdigest()


def _write(path, text):
    """Write `text` to `path` whole, through a temporary file in the same folder and a rename,
    keeping an existing file's permissions; on failure the old file is as it was."""
    if os.path.exists(path):
        mode = stat.S_IMODE(os.stat(path).st_mode)
    else:
        mask = os.umask(0)
        os.umask(mask)
        mode = 0o666 & ~mask
    part = None
    try:
        fd, part = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".OUT.md.", suffix=".part")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(part, mode)
        os.replace(part, path)
    except OSError as e:
        if part and os.path.exists(part):
            os.remove(part)
        raise cli.Failure(f"{path} could not be written ({e.strerror}); it is as it was") from e


def _read(out_md):
    """OUT.md's text as it stands (line endings kept), or None when there is none."""
    if not os.path.lexists(out_md):
        return None
    unchanged = "; record-output changes nothing in it"
    if not os.path.isfile(out_md):
        raise cli.Failure(f"{out_md} is not a file{unchanged}")
    try:
        with open(out_md, encoding="utf-8", newline="") as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise cli.Failure(f"{out_md} is not UTF-8 text{unchanged}") from e
    except OSError as e:
        raise cli.Failure(f"{out_md} could not be read ({e.strerror}){unchanged}") from e

def _run(args):
    data = script.read(args.SCRIPT)
    settings = script.settings(data)
    try:
        conf = config.read()
    except config.ConfigError as e:
        raise cli.Failure(str(e)) from e
    video = args.VIDEO or os.path.join(script.folder(args.SCRIPT), settings["output"])
    name = os.path.basename(video)
    out_md = os.path.join(os.path.dirname(os.path.abspath(video)), "OUT.md")
    if not os.path.isfile(video):
        raise cli.Failure(f"{video}: no such file; give the finished video (by default the script's output)")
    size = os.path.getsize(video)
    if size == 0:
        raise cli.Failure(f"{video} is empty (0 bytes); record a finished video")
    existing = _read(out_md)

    if args.add_state is not None:
        addition = outmd.text_cell(args.add_state, "--add-state")
        if existing is None:
            raise cli.Failure(f"{out_md} does not exist, so there is no row for {name} to add to; add one first "
                              "(record-output without --add-state)")
        text, line = outmd.add_state(existing, name, addition, out_md)
    else:
        state = outmd.text_cell(args.state or "", "--state")
        tools = outmd.commit(args.tools_commit, "--tools-commit") if args.tools_commit else None
        made = outmd.made_text(os.stat(video).st_mtime, conf.get("TIME_ZONE"))
        elements = _elements_commit(args, data, conf)
        tools = tools or _git(TOOLS, "training-video-tools", "--tools-commit")
        line = outmd.row(name, made, outmd.made_with(tools, elements), size, _sha256(video), state)
        text = outmd.append(existing, line, name, out_md) if existing is not None \
            else outmd.new_file(settings["title"], line)

    print(line)
    if args.dry_run:
        print(f"Would write: {out_md} (--dry-run: nothing written)")
        return cli.OK
    _write(out_md, text)
    print(f"{'Written' if existing is not None else 'Created'}: {out_md}")
    return cli.OK
