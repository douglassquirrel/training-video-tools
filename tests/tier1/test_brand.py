"""videotools.brand: a brand kit reads into colours, fonts, mark, illustration and settings."""

import os

import pytest

from videotools import brand

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat")

KIT = """# Brand kit: Demo

## Identity

| Key | Value | Notes |
|---|---|---|
| name | Demo Co | |
| website | demo.example | |
| illustration-credit | Drawings by D. | |

## Colours

| Key | Value | Used for |
|---|---|---|
| background | #F0F0F0 | |
| surface | #FFFFFF | |
| ink | #202020 | |
| muted | #606060 | |
| rule | #D0D0D0 | |
| grid | #C0C0C0 | |
| accent | #FF8000 | |
| accent-dark | #804000 | |
| accent-light | #FFE0C0 | |
| mistake | #A00000 | |
| correct | #008000 | |
| on-accent | #FFFFFF | |

## Fonts

| Key | Value | File | Notes |
|---|---|---|---|
| display | Demo Bold | fonts/Demo-Bold.ttf | |
| body | Demo | fonts/Demo.ttf | |
| italic | Demo Italic | fonts/Demo-Italic.ttf | |

## Mark

| Key | Value | Notes |
|---|---|---|
| shape | circle | |
| fill | accent | |
| letter | D | |
| letter-colour | on-accent | |
| letter-font | display | |
| wordmark | Demo Co | |

## Illustration

| Key | Value | Notes |
|---|---|---|
| end-card | images/end.png | |

## Settings

| Key | Value | Notes |
|---|---|---|
| font-size-scale | 1.1 | |
| background-grid | dots 40 2 0.55 | |
| caption-band | ink | |
| caption-rule | accent 4 | |
| small-text-accent | accent-dark 24 | |
| title-rule | accent 3 | |
| label-shape | pill | |

## Rules

1. Prose for people.
"""


@pytest.fixture
def kit(tmp_path):
    folder = tmp_path / "brands" / "demo"
    (folder / "fonts").mkdir(parents=True)
    (folder / "images").mkdir()
    for f in ("Demo-Bold.ttf", "Demo.ttf", "Demo-Italic.ttf"):
        (folder / "fonts" / f).write_bytes(b"\0")
    (folder / "images" / "end.png").write_bytes(b"\0")
    (folder / "BRAND.md").write_text(KIT, encoding="utf-8")
    return folder


def write(kit, text):
    (kit / "BRAND.md").write_text(text, encoding="utf-8")
    return str(kit)


def test_identity_colours_fonts_mark_illustration_and_settings_read_back(kit):
    b = brand.read(str(kit))
    assert b["identity"] == {"name": "Demo Co", "website": "demo.example", "illustration-credit": "Drawings by D."}
    assert b["colours"]["accent"] == (1.0, pytest.approx(128 / 255), 0.0)
    assert b["colours"]["ink"] == (pytest.approx(32 / 255),) * 3
    assert b["fonts"] == {"display": "Demo Bold", "body": "Demo", "italic": "Demo Italic",
                          "display-medium": "Demo Bold", "body-medium": "Demo", "bold": "Demo Bold",
                          "italic-medium": "Demo Italic"}
    assert b["font_files"] == {"display": str(kit / "fonts" / "Demo-Bold.ttf"),
                               "body": str(kit / "fonts" / "Demo.ttf"),
                               "italic": str(kit / "fonts" / "Demo-Italic.ttf")}
    assert b["mark"] == {"shape": "circle", "fill": "accent", "letter": "D", "letter-colour": "on-accent",
                         "letter-font": "display", "wordmark": "Demo Co"}
    assert b["illustration"] == {"end-card": str(kit / "images" / "end.png")}
    assert b["settings"] == {"font-size-scale": 1.1, "background-grid": ("dots", 40, 2, 0.55),
                             "caption-band": "ink", "caption-rule": ("accent", 4),
                             "small-text-accent": ("accent-dark", 24), "title-rule": ("accent", 3),
                             "label-shape": "pill"}
    assert b["folder"] == str(kit)


def test_a_colour_role_used_as_a_value_resolves_to_its_colour(kit):
    b = brand.read(str(kit))
    assert brand.colour(b, "accent") == b["colours"]["accent"]
    assert brand.colour(b, b["mark"]["fill"]) == b["colours"]["accent"]
    assert brand.colour(b, "#000000") == (0.0, 0.0, 0.0)
    with pytest.raises(brand.BrandError) as e:
        brand.colour(b, "gold")
    assert e.value.problems == ["no colour role 'gold' in the brand kit (and it is not #RRGGBB)"]


def test_small_accent_text_uses_the_darker_role(kit):
    b = brand.read(str(kit))
    assert brand.text_colour(b, "accent", 24) == b["colours"]["accent"]
    assert brand.text_colour(b, "accent", 23.9) == b["colours"]["accent-dark"]
    assert brand.text_colour(b, "ink", 10) == b["colours"]["ink"]


def test_the_example_brand_reads_with_fonts_that_exist():
    b = brand.read(EXAMPLE)
    assert b["identity"]["name"] == "Paperboat Press"
    assert all(os.path.isfile(f) for f in b["font_files"].values())
    assert os.path.isfile(b["illustration"]["end-card"])
    assert b["settings"]["font-size-scale"] == 1.12


def test_a_missing_font_file_is_refused_by_role_and_path(kit):
    (kit / "fonts" / "Demo.ttf").unlink()
    with pytest.raises(brand.BrandError) as e:
        brand.read(str(kit))
    assert e.value.problems == ["Fonts: file for 'body' not found: %s" % (kit / "fonts" / "Demo.ttf")]


def test_a_missing_colour_or_font_role_is_refused_by_name(kit):
    text = KIT.replace("| mistake | #A00000 | |\n", "").replace("| italic | Demo Italic | fonts/Demo-Italic.ttf | |\n", "")
    with pytest.raises(brand.BrandError) as e:
        brand.read(write(kit, text))
    assert e.value.problems == ["Colours: 'mistake' is missing", "Fonts: 'italic' is missing"]


def test_a_colour_that_is_not_hex_and_a_bad_setting_are_refused(kit):
    text = KIT.replace("| accent | #FF8000 | |", "| accent | orange | |")
    text = text.replace("| caption-rule | accent 4 | |", "| caption-rule | accent | |")
    text = text.replace("| background-grid | dots 40 2 0.55 | |", "| background-grid | lines | |")
    with pytest.raises(brand.BrandError) as e:
        brand.read(write(kit, text))
    assert e.value.problems == ["Colours: 'accent' is not #RRGGBB: orange",
                                "Settings: 'background-grid' should be 'dots SPACING SIZE OPACITY' or 'none', not 'lines'",
                                "Settings: 'caption-rule' should be 'ROLE HEIGHT', not 'accent'"]


def test_a_missing_table_name_website_mark_or_illustration_is_refused(kit):
    text = KIT.replace("| website | demo.example | |\n", "")
    text = text.replace("## Mark\n", "## Marque\n").replace("| end-card | images/end.png | |\n", "")
    with pytest.raises(brand.BrandError) as e:
        brand.read(write(kit, text))
    assert e.value.problems == ["Identity: 'website' is missing", "no 'Mark' table",
                                "Illustration: 'end-card' is missing"]


def test_settings_have_the_formats_defaults_when_absent(kit):
    text = KIT.split("## Settings")[0]
    b = brand.read(write(kit, text))
    assert b["settings"] == {"font-size-scale": 1.0, "background-grid": ("dots", 40, 2, 0.55),
                             "caption-band": "ink", "caption-rule": ("accent", 4),
                             "small-text-accent": ("accent-dark", 24), "title-rule": ("accent", 3),
                             "label-shape": "pill"}


def test_a_missing_kit_is_refused_by_path(tmp_path):
    with pytest.raises(brand.BrandError) as e:
        brand.read(str(tmp_path / "none"))
    assert e.value.problems == ["no BRAND.md in %s" % (tmp_path / "none")]
    assert str(e.value) == "{}: no BRAND.md in {}".format(tmp_path / "none", tmp_path / "none")


def test_the_brand_a_script_names_is_found_above_the_script(kit, tmp_path):
    video = tmp_path / "videos" / "demo-video"
    video.mkdir(parents=True)
    assert brand.folder_for(str(video / "script.md"), "demo") == str(kit)


CONTRAST = """
**Contrast**, as WCAG ratios, for people:

| Pair | Ratio | Verdict |
|---|---|---|
| ink on background | 11.2 | Any size. |
| accent on background | 3.6 | Large text only. |
"""


def test_a_table_under_a_read_heading_without_a_key_value_header_is_for_people_and_skipped(kit):
    plain = brand.read(write(kit, KIT))
    with_contrast = brand.read(write(kit, KIT.replace("## Fonts", CONTRAST + "\n## Fonts")))
    assert with_contrast["colours"] == plain["colours"]
    assert with_contrast == plain


def test_a_key_value_table_with_a_bad_colour_is_still_refused_beside_a_skipped_one(kit):
    text = KIT.replace("| accent | #FF8000 | |", "| accent | orange | |").replace("## Fonts", CONTRAST + "\n## Fonts")
    with pytest.raises(brand.BrandError) as e:
        brand.read(write(kit, text))
    assert e.value.problems == ["Colours: 'accent' is not #RRGGBB: orange"]
