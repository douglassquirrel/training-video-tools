"""check-script: the summary, the problems, --json, the exit codes."""

import json
import os

from tests.tier2.conftest import run

SUMMARY = """Folding a Paper Boat: 7 scenes, 11 cues, 125 words (about 48 s of speech at 2.6 words a second)
Tracker: A B C
Mistakes:
  A cue 2: Folded corner to corner / Folded edge to edge
Beyond the source (added:), 4, for approval and checking:
  A, cue 2: "Don't fold it corner to corner. A diagonal fold leaves no hull to open."
      -> the consequence (no hull) is our inference; the figure shows only the edge fold.
  R, cue 2: "Edges even, creases sharp, and a hull that opens. That's a boat that floats."
      -> "a boat that floats" is our framing; the figure says nothing about water.
  A, side panel: "Crease firmly"
      -> the figure's closing note.
  A, on screen: "diagonal fold"
      -> as cue 2.
"""


def test_help_describes_the_command_and_exits_0():
    code, out, err = run("check-script", "--help")
    assert code == 0
    assert out.startswith("usage: check-script [-h] [--json OUT] SCRIPT")
    assert "--json" in out and err == ""


def test_no_arguments_is_usage_exit_2():
    code, out, err = run("check-script")
    assert code == 2 and out == ""
    assert "usage: check-script" in err and "SCRIPT" in err


def test_a_well_formed_script_prints_the_summary_and_exits_0(example):
    code, out, err = run("check-script", example)
    assert (code, err) == (0, "")
    assert out == SUMMARY + "\nNo problems found.\n"


def test_a_malformed_script_prints_the_summary_then_the_problems_and_exits_1(example):
    text = open(example, encoding="utf-8").read().replace("| voice | af_heart | |\n", "")
    text = text.replace("- mistake: Folded corner to corner / Folded edge to edge", "- mistake: Folded corner to corner")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("check-script", example)
    assert (code, err) == (1, "")
    assert out.endswith("\n2 problems:\n  - Settings: 'voice' is missing\n"
                        "  - line 99: scene A cue 2: mistake needs '<wrong> / <right>'\n")
    assert out.startswith("Folding a Paper Boat: 7 scenes, 11 cues")


def test_a_missing_script_is_refused_by_name_exit_3(tmp_path):
    code, out, err = run("check-script", tmp_path / "none.md")
    assert (code, out) == (3, "")
    assert err == "check-script: no such file: %s\n" % (tmp_path / "none.md")


def test_json_writes_the_parsed_script_and_says_so(example, tmp_path):
    out_path = tmp_path / "parsed.json"
    code, out, err = run("check-script", example, "--json", out_path)
    assert (code, err) == (0, "")
    assert out == SUMMARY + f"Parsed script written to {out_path}\n\nNo problems found.\n"
    data = json.load(open(out_path, encoding="utf-8"))
    assert data["title"] == "Folding a Paper Boat"
    assert [s["key"] for s in data["scenes"]] == ["title", "A", "B", "B2", "C", "R", "end"]
    assert data["scenes"][1]["cues"][1]["mistake"] == "Folded corner to corner / Folded edge to edge"
    assert "lines" not in data


def test_json_refuses_to_write_over_an_existing_file_and_writes_nothing(example, tmp_path):
    out_path = tmp_path / "parsed.json"
    out_path.write_text("keep me")
    code, out, err = run("check-script", example, "--json", out_path)
    assert (code, out) == (3, "")
    assert err == f"check-script: {out_path} already exists; give a new name\n"
    assert out_path.read_text() == "keep me"


def test_a_script_path_with_spaces_quotes_and_accents_is_read(example, tmp_path):
    folder = tmp_path / "examples" / "videos" / 'vidéo "two" $x'
    os.rename(os.path.dirname(example), folder)
    code, out, err = run("check-script", folder / "script.md")
    assert (code, err) == (0, "")
    assert out.endswith("No problems found.\n")


def test_the_script_is_never_modified(example):
    before = open(example, "rb").read()
    run("check-script", example, "--json", example + ".json")
    assert open(example, "rb").read() == before


def test_a_malformed_brand_kit_is_listed_with_the_scripts_problems_naming_the_brand_file(example):
    kit = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(example))), "brands", "paperboat", "BRAND.md")
    text = open(kit, encoding="utf-8").read().replace("| accent | #", "| accent | orange #", 1)
    open(kit, "w", encoding="utf-8").write(text)
    code, out, err = run("check-script", example)
    assert (code, err) == (1, "")
    assert out.startswith(SUMMARY)
    assert out.endswith(f"\n1 problem:\n  - {kit}: Colours: 'accent' is not #RRGGBB: orange #1F6F8B\n")


def test_a_missing_brand_kit_is_one_problem_not_two(example):
    text = open(example, encoding="utf-8").read().replace("| brand | paperboat |", "| brand | nokit |")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("check-script", example)
    assert (code, err) == (1, "")
    assert "\n1 problem:\n" in out
    assert out.splitlines()[-1].startswith("  - line 17: Settings: brand 'nokit' has no brands/nokit/BRAND.md under ")


def test_a_step_scene_without_code_or_with_a_module_lacking_a_function_is_listed(example):
    text = open(example, encoding="utf-8").read().replace("| code | fold_in_half | |\n", "")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("check-script", example)
    assert (code, err) == (1, "")
    assert out.endswith("\n1 problem:\n  - line 85: scene A: no 'code' property, so no scene code can be found for it\n")


def test_a_caption_with_a_character_the_brand_font_lacks_is_listed_with_its_line(example):
    text = open(example, encoding="utf-8").read()
    old = "1. Step A. Fold the sheet in half, top edge to bottom edge."
    assert old in text, "the example's first caption of scene A"
    open(example, "w", encoding="utf-8").write(text.replace(old, "1. Step A. Fold the sheet in half, top edge to bottom edge, for €1."))
    kit = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(example))), "brands", "paperboat", "fonts")
    code, out, err = run("check-script", example)
    assert (code, err) == (1, "")
    line = next(n for n, text_line in enumerate(text.splitlines(), 1) if text_line.startswith(old))
    assert out.rstrip().endswith(
        "1 problem:\n"
        f"  - line {line}: scene A cue 1 caption 'Step A. Fold the sheet in half, top edge to bottom edge, for €1.' "
        f"has '€' (U+20AC), which {os.path.join(kit, 'PBS-Regular.ttf')} lacks")
