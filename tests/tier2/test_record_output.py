"""record-output: a finished video's row in the OUT.md beside it (PLAN.md item 31), run as a command
against invented files and a stub git."""

import json
import os
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone

import pytest

from tests.tier2.conftest import REPO, clean_env, git_calls, run, run_program

SHA_BOAT = "25cdb46d8d2115a24eb15c3c58f34f3330cfca4fec249ff70b7cad2bb560a0dd"   # sha256 of b"boat"
MTIME = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc).timestamp()           # 13:00 in London
SHA1, SHA2 = "1" * 64, "2" * 64
TWO_ROWS = (
    "# out/ — the “Paper Boat” video's finished files\n"
    "\n"
    "*Each version, newest last.*\n"
    "\n"
    "| File | Made | video-tools | Size (bytes) | SHA-256 | State |\n"
    "|---|---|---|---|---|---|\n"
    f"| `Paper Boat v1.mp4` | 1 October 2026, 09:00 | `aaaa111` | 1,000 | `{SHA1}` | First cut; `check-video` a \\| b. |\n"
    f"| `Paper Boat v2.mp4` | 2 October 2026, 10:00 | `bbbb222` | 2,000 | `{SHA2}` | |\n"
    "\n"
    "v0 was made by hand.\n"
)
INVENTED = os.path.join(REPO, "tests", "stubs", "video-elements")


@pytest.fixture
def setup(example, tmp_path, gitstub):
    """The example's script, an out/ folder beside it holding a 4-byte video and the invented
    two-row OUT.md, a config naming Europe/London, and the stub git. Returns a namespace."""
    out = os.path.join(os.path.dirname(example), "out")
    os.makedirs(out)
    video = os.path.join(out, "Paper Boat v3.mp4")
    with open(video, "wb") as f:
        f.write(b"boat")
    os.utime(video, (MTIME, MTIME))
    out_md = os.path.join(out, "OUT.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(TWO_ROWS)
    conf = tmp_path / "tvt.conf"
    conf.write_text("TIME_ZONE=Europe/London\n")
    env = dict(gitstub, TRAINING_VIDEO_TOOLS_CONF=str(conf))

    class S:
        pass
    s = S()
    s.script, s.out, s.video, s.out_md, s.env, s.conf = example, out, video, out_md, env, conf
    return s


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def row(name="Paper Boat v3.mp4", made_with="`4e39323`", state=""):
    return f"| `{name}` | 24 October 2026, 13:00 | {made_with} | 4 | `{SHA_BOAT}` | {state + ' ' if state else ''}|"


def untouched(s):
    """OUT.md is the invented file still, byte for byte, and the video is as it was."""
    assert read(s.out_md) == TWO_ROWS
    assert open(s.video, "rb").read() == b"boat" and os.stat(s.video).st_mtime == MTIME


# --- the command line ---

def test_help_and_usage():
    code, out, err = run_program("record-output", "--help")
    assert code == 0
    assert " ".join(out.split()).startswith(
        "usage: record-output [-h] [--state TEXT | --add-state TEXT] [--tools-commit C] [--elements-commit C] "
        "[--elements DIR] [--dry-run] SCRIPT [VIDEO]")


def test_state_and_add_state_together_are_a_usage_error(setup):
    code, out, err = run("record-output", setup.script, setup.video, "--state", "a", "--add-state", "b", env=setup.env)
    assert code == 2 and "not allowed with argument" in err
    untouched(setup)


@pytest.mark.parametrize("flag", [["--tools-commit", "4e39323"], ["--elements-commit", "d32067b"], ["--elements", INVENTED]])
def test_add_state_with_a_commit_flag_is_a_usage_error(setup, flag):
    code, out, err = run("record-output", setup.script, setup.video, "--add-state", "ok", *flag, env=setup.env)
    assert code == 2
    assert err.endswith("record-output: error: --add-state changes only a row's State; --tools-commit, "
                        "--elements-commit and --elements are for adding a row\n")
    untouched(setup)


# --- adding a row ---

def test_a_row_is_appended_after_the_tables_last_row_and_nothing_else_changes(setup):
    code, out, err = run_program("record-output", setup.script, setup.video, "--tools-commit", "4e39323",
                         "--state", "First of the new | cut", env=setup.env)
    assert (code, err) == (0, "")
    new_row = row(state="First of the new \\| cut")
    assert read(setup.out_md) == TWO_ROWS.replace("| |\n\nv0", "| |\n" + new_row + "\n\nv0")
    assert out == f"{new_row}\nWritten: {setup.out_md}\n"
    assert git_calls(setup.env) == []           # a commit given is not looked up
    assert sorted(os.listdir(setup.out)) == ["OUT.md", "Paper Boat v3.mp4"]
    assert open(setup.video, "rb").read() == b"boat" and os.stat(setup.video).st_mtime == MTIME


def test_the_video_defaults_to_the_scripts_output(setup):
    video = os.path.join(setup.out, "Folding a Paper Boat.mp4")
    shutil.move(setup.video, video)
    code, out, err = run("record-output", setup.script, "--tools-commit", "4e39323", env=setup.env)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == row(name="Folding a Paper Boat.mp4")


def test_a_new_out_md_is_created_with_a_heading_from_the_title(setup):
    os.remove(setup.out_md)
    text = read(setup.script).replace("| title | Folding a Paper Boat |", "| title | The “Paper Boat” — étude |", 1)
    with open(setup.script, "w", encoding="utf-8") as f:
        f.write(text)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert (code, err) == (0, "")
    assert read(setup.out_md) == (
        "# out/ — The “Paper Boat” — étude: finished files\n"
        "\n"
        "*Each version, newest last. Finished files are never written over or renamed.*\n"
        "\n"
        "| File | Made | Made with | Size (bytes) | SHA-256 | State |\n"
        "|---|---|---|---|---|---|\n"
        f"{row()}\n")
    assert out == f"{row()}\nCreated: {setup.out_md}\n"


def test_the_time_is_the_machines_own_zone_when_none_is_set(setup):
    setup.conf.write_text("")
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323",
                         env=dict(setup.env, TZ="UTC"))
    assert (code, err) == (0, "")
    assert "| 24 October 2026, 12:00 |" in out.splitlines()[0]


def test_an_unknown_time_zone_is_refused(setup):
    setup.conf.write_text("TIME_ZONE=Mars/Olympus\n")
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3
    assert err == ("record-output: TIME_ZONE 'Mars/Olympus' is not a time zone this machine knows; give a name such "
                   "as Europe/London (or remove the setting to use the machine's own)\n")
    untouched(setup)


def test_a_malformed_config_file_is_refused_in_words(setup):
    setup.conf.write_text("TIMEZONE=Europe/London\n")
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3 and err.startswith(f"record-output: {setup.conf}: line 1: unknown setting 'TIMEZONE'")
    untouched(setup)


def test_a_name_with_spaces_and_nfd_accents_matches_its_nfc_row(setup):
    nfd = unicodedata.normalize("NFD", "Café boat v1.mp4")
    video = os.path.join(setup.out, nfd)
    shutil.move(setup.video, video)
    text = TWO_ROWS.replace("Paper Boat v1.mp4", "Café boat v1.mp4")
    with open(setup.out_md, "w", encoding="utf-8") as f:
        f.write(text)
    code, out, err = run("record-output", setup.script, video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3 and err == (f"record-output: {setup.out_md} already has a row for {nfd}; to add to its state, "
                                 "use --add-state\n")
    assert read(setup.out_md) == text


# --- adding to a row's State ---

def test_add_state_adds_to_that_rows_state_only_and_prints_the_row(setup):
    code, out, err = run("record-output", setup.script, os.path.join(setup.out, "Paper Boat v1.mp4"),
                         "--add-state", "**Accepted** (Squirrel, 11 November 2026) | `v1`", env=setup.env)
    # The video named need not be this one: the row is found by name; a v1 file must exist, so make it.
    assert code == 3 and "Paper Boat v1.mp4: no such file" in err
    with open(os.path.join(setup.out, "Paper Boat v1.mp4"), "wb") as f:
        f.write(b"v1")
    code, out, err = run("record-output", setup.script, os.path.join(setup.out, "Paper Boat v1.mp4"),
                         "--add-state", "**Accepted** (Squirrel, 11 November 2026) | `v1`", env=setup.env)
    assert (code, err) == (0, "")
    old = f"| `{SHA1}` | First cut; `check-video` a \\| b. |"
    new = f"| `{SHA1}` | First cut; `check-video` a \\| b. **Accepted** (Squirrel, 11 November 2026) \\| `v1` |"
    assert read(setup.out_md) == TWO_ROWS.replace(old, new)
    line = [ln for ln in TWO_ROWS.replace(old, new).splitlines() if "Paper Boat v1" in ln][0]
    assert out == f"{line}\nWritten: {setup.out_md}\n"
    assert git_calls(setup.env) == []


def test_add_state_for_a_video_with_no_row_is_refused(setup):
    code, out, err = run("record-output", setup.script, setup.video, "--add-state", "ok", env=setup.env)
    assert code == 3
    assert err == (f"record-output: {setup.out_md} has no row for Paper Boat v3.mp4; add one first "
                   "(record-output without --add-state)\n")
    untouched(setup)


def test_add_state_with_no_out_md_is_refused_and_creates_none(setup):
    os.remove(setup.out_md)
    code, out, err = run("record-output", setup.script, setup.video, "--add-state", "ok", env=setup.env)
    assert code == 3
    assert err == (f"record-output: {setup.out_md} does not exist, so there is no row for Paper Boat v3.mp4 to add "
                   "to; add one first (record-output without --add-state)\n")
    assert not os.path.exists(setup.out_md)


# --- --dry-run ---

@pytest.mark.parametrize("form", [["--tools-commit", "4e39323"], ["--add-state", "ok"]])
def test_dry_run_prints_the_row_and_writes_nothing(setup, form):
    if form[0] == "--add-state":
        shutil.copy(setup.video, os.path.join(setup.out, "Paper Boat v2.mp4"))
        video = os.path.join(setup.out, "Paper Boat v2.mp4")
    else:
        video = setup.video
    before = os.stat(setup.out_md).st_mtime_ns
    code, out, err = run("record-output", setup.script, video, *form, "--dry-run", env=setup.env)
    assert (code, err) == (0, "")
    expected = row() if form[0] != "--add-state" else \
        f"| `Paper Boat v2.mp4` | 2 October 2026, 10:00 | `bbbb222` | 2,000 | `{SHA2}` | ok |"
    assert out == f"{expected}\nWould write: {setup.out_md} (--dry-run: nothing written)\n"
    assert read(setup.out_md) == TWO_ROWS and os.stat(setup.out_md).st_mtime_ns == before


def test_dry_run_with_no_out_md_creates_none(setup):
    os.remove(setup.out_md)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", "--dry-run",
                         env=setup.env)
    assert (code, err) == (0, "")
    assert out.endswith(f"Would write: {setup.out_md} (--dry-run: nothing written)\n")
    assert os.listdir(setup.out) == ["Paper Boat v3.mp4"]


# --- refusals: nothing written ---

def test_a_missing_video_is_refused(setup):
    code, out, err = run("record-output", setup.script, os.path.join(setup.out, "v9.mp4"), "--tools-commit", "4e39323",
                         env=setup.env)
    assert code == 3
    assert err == (f"record-output: {os.path.join(setup.out, 'v9.mp4')}: no such file; give the finished video "
                   "(by default the script's output)\n")
    untouched(setup)


def test_an_empty_video_is_refused(setup):
    open(setup.video, "wb").close()
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3
    assert err == f"record-output: {setup.video} is empty (0 bytes); record a finished video\n"
    assert read(setup.out_md) == TWO_ROWS


def test_a_second_row_for_the_same_video_is_refused(setup):
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 0
    once = read(setup.out_md)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3
    assert err == (f"record-output: {setup.out_md} already has a row for Paper Boat v3.mp4; to add to its state, "
                   "use --add-state\n")
    assert read(setup.out_md) == once


@pytest.mark.parametrize("text, problem", [
    ("# out/\n\nNothing yet.\n", "has no table"),
    (TWO_ROWS + "\n| A | B | C | D | E | F |\n|---|---|---|---|---|---|\n", "has 2 tables; it should have one"),
    (TWO_ROWS.replace("| SHA-256 | State |", "| SHA-256 |"),
     "has a table of 5 columns; it should have six (file, made, made with, size, SHA-256, state)"),
])
def test_an_out_md_without_one_six_column_table_is_refused(setup, text, problem):
    with open(setup.out_md, "w", encoding="utf-8") as f:
        f.write(text)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3 and err == f"record-output: {setup.out_md} {problem}; record-output changes nothing in it\n"
    assert read(setup.out_md) == text


@pytest.mark.parametrize("flag", ["--state", "--add-state"])
def test_a_state_with_a_line_break_is_refused(setup, flag):
    code, out, err = run("record-output", setup.script, setup.video, flag, "one\ntwo",
                         *(["--tools-commit", "4e39323"] if flag == "--state" else []), env=setup.env)
    assert code == 3
    assert err == f"record-output: the {flag} text has a line break; a table cell is one line: give it on one line\n"
    untouched(setup)


def test_a_commit_that_is_not_one_is_refused(setup):
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323; echo $HOME </script>",
                         env=setup.env)
    assert code == 3
    assert err == ("record-output: --tools-commit '4e39323; echo $HOME </script>' is not a commit id "
                   "(4 to 40 hexadecimal digits)\n")
    untouched(setup)


def test_an_unreadable_video_is_refused_and_out_md_left_as_it_was(setup):
    os.chmod(setup.video, 0)
    try:
        code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    finally:
        os.chmod(setup.video, 0o644)
    assert code == 3
    assert err == f"record-output: {setup.video} could not be read (Permission denied); nothing written\n"
    untouched(setup)


def test_a_failed_write_leaves_out_md_as_it_was_and_no_part_file(setup):
    os.chmod(setup.out, 0o555)
    try:
        code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
        listing = sorted(os.listdir(setup.out))
    finally:
        os.chmod(setup.out, 0o755)
    assert code == 3
    assert err == f"record-output: {setup.out_md} could not be written (Permission denied); it is as it was\n"
    assert listing == ["OUT.md", "Paper Boat v3.mp4"]
    untouched(setup)


def test_a_rewritten_out_md_keeps_its_permissions(setup):
    os.chmod(setup.out_md, 0o640)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 0 and os.stat(setup.out_md).st_mode & 0o777 == 0o640


def test_a_new_out_md_gets_the_usual_permissions(setup):
    os.remove(setup.out_md)
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    mask = os.umask(0)
    os.umask(mask)
    assert code == 0 and os.stat(setup.out_md).st_mode & 0o777 == 0o666 & ~mask


# --- the commits, read from the checkouts when not given ---

def test_with_no_commit_given_the_tools_checkouts_is_read_with_git(setup):
    env = dict(setup.env, GITSTUB_HEADS=json.dumps({os.path.realpath(REPO): "abc1234"}))
    code, out, err = run("record-output", setup.script, setup.video, env=env)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == row(made_with="`abc1234`")
    assert git_calls(env) == [["-C", os.path.realpath(REPO), "rev-parse", "--short", "HEAD"],
                              ["-C", os.path.realpath(REPO), "status", "--porcelain"]]


def test_a_tools_checkout_with_uncommitted_changes_is_refused(setup):
    env = dict(setup.env, GITSTUB_DIRTY=json.dumps([os.path.realpath(REPO)]))
    code, out, err = run("record-output", setup.script, setup.video, env=env)
    assert code == 3
    assert err == (f"record-output: {os.path.realpath(REPO)} has 2 uncommitted changes, so its commit would not say "
                   "what made the video; commit them, or give --tools-commit COMMIT\n")
    untouched(setup)


def test_git_failing_is_exit_4_naming_the_flag(setup):
    env = dict(setup.env, GITSTUB_FAIL="1")
    code, out, err = run("record-output", setup.script, setup.video, env=env)
    assert code == 4
    assert err == (f"record-output: git could not read the commit of {os.path.realpath(REPO)} (fatal: not a git "
                   "repository (or any of the parent directories): .git); give --tools-commit COMMIT\n")
    untouched(setup)


def test_git_missing_is_exit_4_naming_the_flag(setup, tmp_path):
    empty = tmp_path / "nothing-on-path"
    empty.mkdir()
    code, out, err = run("record-output", setup.script, setup.video, env=dict(setup.env, PATH=str(empty)))
    assert code == 4
    assert err == (f"record-output: git is not installed, and is needed to read the commit of "
                   f"{os.path.realpath(REPO)}; install Xcode's command-line tools (xcode-select --install), "
                   "or give --tools-commit COMMIT\n")
    untouched(setup)


def test_a_copy_of_the_tools_with_no_git_folder_is_refused_naming_the_flag(setup, tmp_path):
    copy = tmp_path / "export"
    copy.mkdir()
    shutil.copy(os.path.join(REPO, "record-output"), copy / "record-output")
    shutil.copytree(os.path.join(REPO, "videotools"), copy / "videotools",
                    ignore=shutil.ignore_patterns("__pycache__"))
    p = subprocess.run([sys.executable, str(copy / "record-output"), setup.script, setup.video], capture_output=True,
                       text=True, env=clean_env(**setup.env))
    assert p.returncode == 3
    assert p.stderr == (f"record-output: {os.path.realpath(copy)} is not a git checkout, so the training-video-tools "
                        "commit cannot be read from it; give --tools-commit COMMIT\n")
    assert git_calls(setup.env) == []
    untouched(setup)


def described(setup):
    from tests.tier2.test_perform import describe
    return describe(setup.script)


def test_a_script_drawing_from_the_library_records_the_librarys_commit_given(setup):
    code, out, err = run("record-output", described(setup), setup.video, "--tools-commit", "4e39323",
                         "--elements-commit", "d32067b", env=setup.env)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == row(made_with="`4e39323` (video-elements `d32067b`)")


def test_the_librarys_commit_is_read_from_its_checkout_when_not_given(setup, tmp_path):
    library = tmp_path / "video-elements"
    (library / ".git").mkdir(parents=True)
    env = dict(setup.env, GITSTUB_HEADS=json.dumps({os.path.realpath(library): "eee5555"}))
    setup.conf.write_text(f"TIME_ZONE=Europe/London\nVIDEO_ELEMENTS_DIR={library}\n")
    code, out, err = run("record-output", described(setup), setup.video, "--tools-commit", "4e39323", env=env)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == row(made_with="`4e39323` (video-elements `eee5555`)")
    assert git_calls(env) == [["-C", os.path.realpath(library), "rev-parse", "--short", "HEAD"],
                              ["-C", os.path.realpath(library), "status", "--porcelain"]]


def test_a_library_folder_that_is_not_a_checkout_is_refused_naming_the_flag(setup):
    code, out, err = run("record-output", described(setup), setup.video, "--tools-commit", "4e39323",
                         "--elements", INVENTED, env=setup.env)
    assert code == 3
    assert err == (f"record-output: {os.path.realpath(INVENTED)} is not a git checkout, so the video-elements commit "
                   "cannot be read from it; give --elements-commit COMMIT\n")
    untouched(setup)


def test_a_library_folder_that_does_not_exist_is_refused(setup, tmp_path):
    code, out, err = run("record-output", described(setup), setup.video, "--tools-commit", "4e39323",
                         "--elements", tmp_path / "nowhere", env=setup.env)
    assert code == 3
    assert err == (f"record-output: {tmp_path / 'nowhere'}: video-elements folder not found (--elements, or "
                   f"VIDEO_ELEMENTS_DIR in {setup.conf}); give it, or --elements-commit COMMIT\n")
    untouched(setup)


def test_a_script_drawing_from_the_library_with_no_way_to_its_commit_is_refused(setup):
    code, out, err = run("record-output", described(setup), setup.video, "--tools-commit", "4e39323", env=setup.env)
    assert code == 3
    assert err == ("record-output: this script draws from the video-elements library, so its commit is recorded "
                   f"too; give --elements-commit COMMIT, or --elements DIR (or VIDEO_ELEMENTS_DIR in {setup.conf}) "
                   "naming the library's checkout\n")
    untouched(setup)


def test_a_library_commit_given_for_a_script_without_elements_is_recorded_as_given(setup):
    code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323",
                         "--elements-commit", "d32067b", env=setup.env)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == row(made_with="`4e39323` (video-elements `d32067b`)")


@pytest.mark.parametrize("make, problem", [
    (lambda p: (os.remove(p), os.mkdir(p)), "is not a file"),
    (lambda p: open(p, "wb").write(b"| File |\xff\xfe\n"), "is not UTF-8 text"),
    (lambda p: os.chmod(p, 0), "could not be read (Permission denied)"),
])
def test_an_out_md_that_cannot_be_read_as_text_is_refused_in_words(setup, make, problem):
    make(setup.out_md)
    try:
        code, out, err = run("record-output", setup.script, setup.video, "--tools-commit", "4e39323", env=setup.env)
    finally:
        if os.path.isfile(setup.out_md):
            os.chmod(setup.out_md, 0o644)
    assert code == 3
    assert err == f"record-output: {setup.out_md} {problem}; record-output changes nothing in it\n"
