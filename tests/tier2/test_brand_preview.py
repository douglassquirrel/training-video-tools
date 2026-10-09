"""brand-preview: a picture of a brand kit, read with the package's own reader."""

import os
import shutil

import pytest
from PIL import Image

from tests.tier2.conftest import EXAMPLES, run

PAIRS = [  # the text-on-fill pairs the chrome uses, with the example kit's ratios worked by hand
    ("ink on background", 12.79), ("muted on background", 5.19), ("accent on background", 5.12),
    ("accent-dark on background", 7.94), ("ink on surface", 14.16), ("muted on surface", 5.74),
    ("accent on surface", 5.67), ("accent-dark on surface", 8.80), ("on-accent on accent", 5.67),
    ("on-accent on accent-dark", 8.80), ("on-accent on mistake", 6.56), ("on-accent on correct", 4.94),
    ("on-accent on ink (caption band)", 14.16)]


@pytest.fixture
def kit(tmp_path):
    """A copy of the example kit, so a test can change it."""
    shutil.copytree(os.path.join(EXAMPLES, "brands", "paperboat"), tmp_path / "paperboat")
    return str(tmp_path / "paperboat")


def edit(kit, old, new):
    path = os.path.join(kit, "BRAND.md")
    text = open(path, encoding="utf-8").read()
    assert old in text
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))


def test_help_and_usage():
    code, out, err = run("brand-preview", "--help")
    assert code == 0 and out.startswith("usage: brand-preview [-h] --out PREVIEW.png BRAND_DIR")
    code, out, err = run("brand-preview")
    assert code == 2 and "usage: brand-preview" in err


def test_the_sheet_shows_every_colour_as_a_swatch_the_mark_and_the_caption_band(kit, tmp_path):
    out_png = str(tmp_path / "preview.png")
    code, out, err = run("brand-preview", kit, "--out", out_png)
    assert (code, err) == (0, "")
    im = Image.open(out_png).convert("RGB")
    assert im.size == (1920, 1080)
    assert im.getpixel((1000, 20)) == (0xF7, 0xF3, 0xEA)        # the kit's background, top edge
    assert im.getpixel((94, 74)) == (0x1F, 0x6F, 0x8B)          # the mark's roundel, accent, at its edge
    swatch = lambda i: (62 + (i % 4) * 200 + 90, 210 + (i // 4) * 150 + 42)   # noqa: E731  centre of swatch i
    assert im.getpixel(swatch(0)) == (0xF7, 0xF3, 0xEA)          # background
    assert im.getpixel(swatch(6)) == (0x1F, 0x6F, 0x8B)          # accent
    assert im.getpixel(swatch(9)) == (0xA3, 0x3A, 0x2E)          # mistake
    assert im.getpixel(swatch(11)) == (0xFF, 0xFF, 0xFF)         # on-accent
    assert im.getpixel((300, 1060)) == (0x2B, 0x2B, 0x2B)        # the caption band (ink)
    assert im.getpixel((300, 949)) == (0x1F, 0x6F, 0x8B)         # its rule (accent, 4 px)
    lines = out.splitlines()
    assert lines[0] == "Paperboat Press (paperboat.example): 12 colours, 3 fonts (display: PBS SemiBold, body: PBS Regular, italic: PBS Italic)"
    assert lines[1] == "small-text-accent: text under 24 px that would be accent uses accent-dark; shown at 32 px (accent) and 18 px (accent-dark)"
    assert lines[2] == "contrast (WCAG ratio; 4.5 for text, 3 for large text):"
    assert lines[3:16] == [f"  {name}: {ratio:.2f}  {v}" for (name, ratio), v in
                           zip(PAIRS, ["OK for text"] * 13)]
    assert lines[16] == f"Wrote {out_png}"


def test_a_contrast_that_fails_or_is_for_large_text_only_says_so(kit, tmp_path):
    edit(kit, "| muted | #6B6560 |", "| muted | #B0A89A |")          # 2.13 on background, 2.36 on surface
    edit(kit, "| correct | #3E7D4F |", "| correct | #4E9A62 |")      # white on it: 3.43
    code, out, err = run("brand-preview", kit, "--out", str(tmp_path / "p.png"))
    assert (code, err) == (0, "")
    assert "  muted on background: 2.13  fails (under 3)" in out
    assert "  muted on surface: 2.36  fails (under 3)" in out
    assert "  on-accent on correct: 3.43  large text only (3-4.5)" in out


def test_an_extra_font_role_such_as_mono_gets_a_specimen_line(kit, tmp_path):
    edit(kit, "| italic | PBS Italic | fonts/PBS-Italic.ttf | Subtitles, the web address, image captions. |",
         "| italic | PBS Italic | fonts/PBS-Italic.ttf | Subtitles, the web address, image captions. |\n"
         "| mono | PBS Regular | fonts/PBS-Regular.ttf | Code. |")
    code, out, err = run("brand-preview", kit, "--out", str(tmp_path / "p.png"))
    assert (code, err) == (0, "")
    assert out.splitlines()[0].endswith("4 fonts (display: PBS SemiBold, body: PBS Regular, italic: PBS Italic, mono: PBS Regular)")


def test_a_malformed_kit_is_refused_in_the_readers_words_exit_3_and_nothing_written(kit, tmp_path):
    edit(kit, "| website |", "| x-website |")
    edit(kit, "| accent | #1F6F8B |", "| accent | blue |")
    code, out, err = run("brand-preview", kit, "--out", str(tmp_path / "p.png"))
    assert (code, out) == (3, "")
    assert "Traceback" not in err
    assert err == f"brand-preview: {kit}: Identity: 'website' is missing\nColours: 'accent' is not #RRGGBB: blue\n"
    assert not os.path.exists(tmp_path / "p.png")


def test_a_folder_without_a_kit_is_refused(tmp_path):
    code, out, err = run("brand-preview", str(tmp_path), "--out", str(tmp_path / "p.png"))
    assert (code, out) == (3, "")
    assert err == f"brand-preview: {tmp_path}: no BRAND.md in {tmp_path}\n"


def test_an_existing_output_is_refused_before_the_kit_is_read(tmp_path):
    out_png = tmp_path / "p.png"
    out_png.write_bytes(b"keep")
    code, out, err = run("brand-preview", str(tmp_path / "nokit"), "--out", str(out_png))
    assert (code, out) == (3, "")
    assert err == f"brand-preview: {out_png} already exists; give a new name\n"
    assert out_png.read_bytes() == b"keep"


def test_the_kit_is_never_modified_and_only_the_preview_is_written(kit, tmp_path):
    before = {f: open(os.path.join(kit, f), "rb").read() for f in os.listdir(kit) if os.path.isfile(os.path.join(kit, f))}
    assert run("brand-preview", kit, "--out", str(tmp_path / "p.png"))[0] == 0
    after = {f: open(os.path.join(kit, f), "rb").read() for f in os.listdir(kit) if os.path.isfile(os.path.join(kit, f))}
    assert after == before
    assert sorted(os.listdir(tmp_path)) == ["p.png", "paperboat"]
