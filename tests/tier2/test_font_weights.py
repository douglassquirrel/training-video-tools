"""font-weights: static instances under their own family names; refusals."""

import os

from fontTools.ttLib import TTFont

from tests.tier2.conftest import run, run_program
from tests.tier2.fontfixture import variable_font


def names(path):
    n = TTFont(path)["name"]
    return {i: n.getDebugName(i) for i in (1, 2, 4, 6, 16, 17, 21, 22, 25)}


def test_help_and_usage():
    code, out, err = run_program("font-weights", "--help")
    assert code == 0 and out.startswith("usage: font-weights [-h] --weights")
    code, out, err = run_program("font-weights", "x.ttf")
    assert code == 2 and "usage: font-weights" in err


def test_one_static_instance_per_weight_each_under_its_own_family_name(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar[wght].ttf"))
    out_dir = tmp_path / "out"
    code, out, err = run_program("font-weights", src, "--weights", "300,400,600", "--family-prefix", "TV", "--out", out_dir)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(out_dir)) == ["TV-Light.ttf", "TV-Regular.ttf", "TV-SemiBold.ttf"]
    assert names(out_dir / "TV-SemiBold.ttf") == {1: "TV SemiBold", 2: "Regular", 4: "TV SemiBold", 6: "TVSemiBold",
                                                   16: None, 17: None, 21: None, 22: None, 25: None}
    f = TTFont(out_dir / "TV-SemiBold.ttf")
    assert "fvar" not in f and "gvar" not in f
    # the A at wght 600 is 500 + (800 - 500) * (600 - 300) / (800 - 300) = 680 wide
    assert f["hmtx"]["A"][0] == 680
    assert TTFont(out_dir / "TV-Light.ttf")["hmtx"]["A"][0] == 500
    assert out.splitlines() == [f"{out_dir / 'TV-Light.ttf'}  TV Light  (wght 300)",
                                f"{out_dir / 'TV-Regular.ttf'}  TV Regular  (wght 400)",
                                f"{out_dir / 'TV-SemiBold.ttf'}  TV SemiBold  (wght 600)"]


def test_an_italic_variable_font_gets_italic_in_its_names(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar-Italic[wght].ttf"), italic=True)
    out_dir = tmp_path / "out"
    code, out, err = run("font-weights", src, "--weights", "500", "--family-prefix", "TV", "--out", out_dir)
    assert (code, err) == (0, "")
    assert os.listdir(out_dir) == ["TV-MediumItalic.ttf"]
    assert names(out_dir / "TV-MediumItalic.ttf")[1] == "TV MediumItalic"
    assert names(out_dir / "TV-MediumItalic.ttf")[6] == "TVMediumItalic"


def test_a_weight_outside_the_axis_or_not_a_number_is_refused(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar[wght].ttf"))
    code, out, err = run("font-weights", src, "--weights", "200,400", "--family-prefix", "TV", "--out", tmp_path / "out")
    assert (code, out) == (3, "")
    assert err == "font-weights: weight 200 is outside the font's wght axis (300 to 800)\n"
    assert not os.path.exists(tmp_path / "out")
    code, out, err = run("font-weights", src, "--weights", "bold", "--family-prefix", "TV", "--out", tmp_path / "out")
    assert code == 2 and "usage: font-weights" in err


def test_a_font_without_a_weight_axis_is_refused(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar[wght].ttf"))
    out_dir = tmp_path / "out"
    run("font-weights", src, "--weights", "400", "--family-prefix", "TV", "--out", out_dir)
    static = str(out_dir / "TV-Regular.ttf")
    code, out, err = run("font-weights", static, "--weights", "400", "--family-prefix", "TW", "--out", tmp_path / "out2")
    assert (code, out) == (3, "")
    assert err == f"font-weights: {static} has no 'wght' axis (is it a variable font?)\n"


def test_a_missing_font_file_is_refused(tmp_path):
    code, out, err = run("font-weights", tmp_path / "none.ttf", "--weights", "400", "--family-prefix", "TV", "--out", tmp_path / "out")
    assert (code, out) == (3, "")
    assert err == f"font-weights: no such file: {tmp_path / 'none.ttf'}\n"


def test_existing_outputs_are_refused_before_anything_is_written(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar[wght].ttf"))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "TV-Regular.ttf").write_bytes(b"keep")
    code, out, err = run("font-weights", src, "--weights", "400,500", "--family-prefix", "TV", "--out", out_dir)
    assert (code, out) == (3, "")
    assert err == f"font-weights: these would be written over; delete them first:\n  {out_dir / 'TV-Regular.ttf'}\n"
    assert os.listdir(out_dir) == ["TV-Regular.ttf"] and (out_dir / "TV-Regular.ttf").read_bytes() == b"keep"


def test_the_variable_font_is_never_modified(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar[wght].ttf"))
    before = open(src, "rb").read()
    run("font-weights", src, "--weights", "400", "--family-prefix", "TV", "--out", tmp_path / "out")
    assert open(src, "rb").read() == before


def test_the_italic_at_regular_weight_is_just_italic(tmp_path):
    src = variable_font(str(tmp_path / "TinyVar-Italic[wght].ttf"), italic=True)
    out_dir = tmp_path / "out"
    code, out, err = run("font-weights", src, "--weights", "400,600", "--family-prefix", "TV", "--out", out_dir)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(out_dir)) == ["TV-Italic.ttf", "TV-SemiBoldItalic.ttf"]
    assert names(out_dir / "TV-Italic.ttf")[1] == "TV Italic"
