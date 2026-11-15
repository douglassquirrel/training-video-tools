"""crop-insets: every inset box cut and sized, the whole page for the title card, refusals."""

import os

from PIL import Image

from tests.tier2.conftest import run, run_program


def insets(example):
    return os.path.join(os.path.dirname(example), "work", "insets")


def test_help_and_usage():
    code, out, err = run_program("crop-insets", "--help")
    assert code == 0 and out.startswith("usage: crop-insets [-h] [--dry-run] SCRIPT")
    code, out, err = run_program("crop-insets")
    assert code == 2 and "usage: crop-insets" in err


def test_each_inset_is_cut_and_sized_for_the_column_and_the_page_for_the_title(example):
    code, out, err = run_program("crop-insets", example)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(insets(example))) == ["A.png", "B.png", "C.png", "full.png", "title-page.png"]
    # A: box 80 150 1120 600 is 1040 x 450, wider than tall: fits 388 x 330 -> scale 388/1040
    assert Image.open(os.path.join(insets(example), "A.png")).size == (388, 167)
    # full: 1120 x 1620, taller than wide: fits 388 x 360 -> scale 360/1620
    assert Image.open(os.path.join(insets(example), "full.png")).size == (248, 360)
    # the page: 1200 x 1700 scaled to 750 tall
    assert Image.open(os.path.join(insets(example), "title-page.png")).size == (529, 750)
    assert out.splitlines()[0] == f"{os.path.join(insets(example), 'A.png')}  388x167  (inset A, 1040x450 at 80 150)"
    assert out.splitlines()[-1] == f"Wrote 5 files to {insets(example)}"


def test_the_cut_is_the_box_itself(example):
    src = Image.open(os.path.join(os.path.dirname(example), "sources", "figure7.png"))
    run("crop-insets", example)
    a = Image.open(os.path.join(insets(example), "A.png")).convert("RGB")
    expected = src.crop((80, 150, 1120, 600)).resize((388, 167), Image.LANCZOS).convert("RGB")
    assert a.tobytes() == expected.tobytes()


def test_dry_run_lists_the_files_and_writes_nothing(example):
    code, out, err = run("crop-insets", example, "--dry-run")
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == f"{os.path.join(insets(example), 'A.png')}  388x167  (inset A, 1040x450 at 80 150)"
    assert out.splitlines()[-1] == "5 files; nothing written (dry run)."
    assert not os.path.exists(os.path.join(os.path.dirname(example), "work"))


def test_a_box_outside_the_image_or_empty_is_refused_by_name(example):
    text = open(example, encoding="utf-8").read()
    text = text.replace("| A | 80 150 1120 600 |", "| A | 80 150 1300 600 |").replace("| B | 80 660 1120 1110 |", "| B | 80 660 80 1110 |")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("crop-insets", example)
    assert (code, out) == (3, "")
    assert err == ("crop-insets: inset A: box 80 150 1300 600 is outside the image (1200x1700)\n"
                   "crop-insets: inset B: box 80 660 80 1110 is empty\n")
    assert not os.path.exists(os.path.join(os.path.dirname(example), "work"))


def test_no_source_image_is_refused(example):
    text = open(example, encoding="utf-8").read().replace("| source-image | sources/figure7.png | |\n", "")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("crop-insets", example)
    assert (code, out) == (3, "")
    assert err == "crop-insets: the script's Settings have no 'source-image'; crop-insets needs one\n"


def test_an_inset_named_title_page_is_refused(example):
    text = open(example, encoding="utf-8").read().replace("| full | 40 40 1160 1660 |", "| title-page | 40 40 1160 1660 |")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("crop-insets", example)
    assert (code, out) == (3, "")
    assert err == "crop-insets: an inset cannot be called 'title-page'; that name is the whole page's\n"


def test_existing_outputs_are_refused_and_nothing_changes(example):
    run("crop-insets", example)
    before = open(os.path.join(insets(example), "A.png"), "rb").read()
    os.remove(os.path.join(insets(example), "B.png"))
    code, out, err = run("crop-insets", example)
    assert (code, out) == (3, "")
    assert err.startswith("crop-insets: these would be written over; delete them first:\n")
    assert f"  {os.path.join(insets(example), 'A.png')}\n" in err and "B.png" not in err
    assert open(os.path.join(insets(example), "A.png"), "rb").read() == before
    assert not os.path.exists(os.path.join(insets(example), "B.png"))


def test_the_source_image_is_never_modified(example):
    src = os.path.join(os.path.dirname(example), "sources", "figure7.png")
    before = open(src, "rb").read()
    run("crop-insets", example)
    assert open(src, "rb").read() == before
