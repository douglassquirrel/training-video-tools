"""check-script on a script with a described scene: the library opened from the flag or the
config file, one problem when it cannot be, the choreography's problems by line, cue lengths
from timing.json or the estimate (PLAN.md item 15, "Checks")."""

import os

from tests.tier2.conftest import STUBS, narrated, run
from tests.tier2.test_check_script import SUMMARY

INVENTED = os.path.join(STUBS, "video-elements")

DESCRIBED = """### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sheet | pot | left | 300 | state=plain | |
| crease | pill | sheet.centre + 0 40 | | text=crease size=22 | |

### Moves

- cue 1: show sheet
- cue 1, 1.0 s: show crease
- cue 2: hide crease

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| wrong | pill | 345 640 | | text="diagonal fold" fill=mistake anchor=centre | |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| right | pill | 345 640 | | text="edge fold" fill=correct anchor=centre | |

"""


def described(example, extra=""):
    """The example copy with scene A described (its module stays), plus `extra` lines after the moves."""
    text = open(example, encoding="utf-8").read()
    marker = "## Scene B: Corners to the centre"
    assert text.count(marker) == 1
    sections = DESCRIBED.replace("- cue 2: hide crease\n", "- cue 2: hide crease\n" + extra)
    open(example, "w", encoding="utf-8").write(text.replace(marker, sections + marker))
    return example


def test_a_described_scene_checks_clean_with_the_library_given_as_a_flag(example):
    code, out, err = run("check-script", described(example), "--elements", INVENTED)
    assert (code, err) == (0, "")
    assert out == SUMMARY + "Credits on the end card:\n  Icons: Invented Icons\n\nNo problems found.\n"


def test_the_library_from_the_config_file_when_no_flag_is_given(example, tmp_path):
    conf = tmp_path / "video-tools.conf"
    conf.write_text(f"VIDEO_ELEMENTS_DIR={INVENTED}\n")
    code, out, err = run("check-script", described(example), env={"VIDEO_TOOLS_CONF": str(conf)})
    assert (code, err) == (0, "")
    assert out.endswith("\nNo problems found.\n")


def test_no_library_setting_is_one_problem_and_the_pieces_are_still_checked(example, tmp_path):
    conf = tmp_path / "none.conf"
    script = described(example, "- cue 2: crease.text wrong\n")
    code, out, err = run("check-script", script, env={"VIDEO_TOOLS_CONF": str(conf)})
    assert (code, err) == (1, "")
    assert out.endswith(
        "\n2 problems:\n"
        f"  - VIDEO_ELEMENTS_DIR is not set in {conf} and no --elements was given; a script that describes a "
        "scene's cast needs the video-elements repository (README, \"Configuration\")\n"
        "  - line 136: scene A, moves: 'crease' draws 'wrong', which is not in the script's On screen list "
        "(top edge to bottom edge, crease, diagonal fold, edge fold)\n")


def test_an_element_the_library_lacks_is_listed_by_line(example):
    script = described(example)
    text = open(script, encoding="utf-8").read().replace("| sheet | pot |", "| sheet | teapot |")
    open(script, "w", encoding="utf-8").write(text)
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert (code, err) == (1, "")
    assert out.endswith("\n1 problem:\n  - line 128: scene A, cast: 'sheet': no element 'teapot': not one of "
                        "video-tools' pieces (pill, callout, text, badge, hand, arrow) and not in the library "
                        "(pot, table)\n")


def test_a_time_past_a_cue_is_measured_from_timing_json_when_there_is_one_else_estimated(example):
    script = described(example, "- cue 1, 5.0 s: hide sheet\n")
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert (code, err) == (1, "")
    assert out.endswith("\n1 problem:\n  - line 136: scene A, moves: 5.6 s is past the end of cue 1, which is 5.2 s long "
                        "(estimated at 2.6 words a second; run narrate for the measured length)\n")
    narrated(script)                                # 1 s clips: cue 1 is its min of 3.0 s
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert (code, err) == (1, "")
    assert out.endswith("\n1 problem:\n  - line 136: scene A, moves: 5 s is past the end of cue 1, which is 3.0 s "
                        "long\n")


def test_a_bad_library_folder_is_one_problem_in_words(example, tmp_path):
    code, out, err = run("check-script", described(example), "--elements", tmp_path / "gone")
    assert (code, err) == (1, "")
    assert out.endswith(f"\n1 problem:\n  - {tmp_path / 'gone'}: video-elements folder not found (VIDEO_ELEMENTS_DIR "
                        "in {conf}, or --elements)\n".replace("{conf}", os.path.expanduser("~/.video-tools.conf")))


# ---- request 14: the credit lines the end card will show, printed for approval

def test_the_credit_lines_are_printed_after_the_added_lines_for_a_script_with_library_elements(example):
    code, out, err = run("check-script", described(example), "--elements", INVENTED)
    assert (code, err) == (0, "")
    assert out.endswith("      -> as cue 2.\nCredits on the end card:\n  Icons: Invented Icons\n\nNo problems found.\n")


def test_element_credits_none_and_wording_are_printed_as_they_will_show(example):
    script = described(example)
    text = open(script, encoding="utf-8").read()
    open(script, "w", encoding="utf-8").write(text.replace("| credit |", "| element-credits | none | |\n| credit |"))
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert code == 0 and "Credits on the end card:\n  none\n" in out
    open(script, "w", encoding="utf-8").write(text.replace("| credit |", "| element-credits | Art by the paper crew | |\n| credit |"))
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert code == 0 and "Credits on the end card:\n  Art by the paper crew\n" in out


def test_a_credit_line_with_a_character_the_body_font_lacks_is_listed(example):
    script = described(example)
    text = open(script, encoding="utf-8").read()
    open(script, "w", encoding="utf-8").write(text.replace("| credit |", "| element-credits | Art for €1 | |\n| credit |"))
    code, out, err = run("check-script", script, "--elements", INVENTED)
    assert code == 1
    assert "end card credit line 'Art for €1' has '€' (U+20AC), which " in out
