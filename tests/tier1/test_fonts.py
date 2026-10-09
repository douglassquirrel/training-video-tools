"""videotools.fonts: the brand's font files reach cairo by family name, nothing installed."""

import os
import subprocess
import sys

import pytest

from videotools import brand, fonts

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat")
PROBE = """
import sys
sys.path.insert(0, %r)
import cairo
from videotools import brand, fonts
kit = brand.read(%r)
print(sorted(os.path.basename(f) for f in fonts.load(kit, %r)))
def width(family):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
    c = cairo.Context(s)
    c.select_font_face(family)
    c.set_font_size(40)
    return round(c.text_extents("Hamburgefonstiv").x_advance, 2)
print(width(kit["fonts"]["display"]), width(kit["fonts"]["body"]), width(kit["fonts"]["italic"]), width("No Such Family Qzx"))
"""


def test_the_example_brands_fonts_are_found_by_name_in_a_fresh_interpreter(tmp_path):
    repo = os.path.join(os.path.dirname(__file__), "..", "..")
    code = "import os\n" + PROBE % (os.path.abspath(repo), os.path.abspath(EXAMPLE), str(tmp_path / "work"))
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    loaded, widths = p.stdout.strip().splitlines()
    assert loaded == "['PBS-Italic.ttf', 'PBS-Regular.ttf', 'PBS-SemiBold.ttf']"
    display, body, italic, nonsense = (float(w) for w in widths.split())
    assert len({display, body, italic}) == 3
    assert nonsense not in (display, body, italic)


def test_on_other_platforms_a_private_fontconfig_file_is_written_and_named(tmp_path, monkeypatch):
    kit = brand.read(EXAMPLE)
    monkeypatch.delenv("FONTCONFIG_FILE", raising=False)
    loaded = fonts.load(kit, str(tmp_path / "work"), platform="linux")
    conf = tmp_path / "work" / "fonts" / "fonts.conf"
    assert os.environ["FONTCONFIG_FILE"] == str(conf)
    text = conf.read_text()
    assert "<dir>{}</dir>".format(os.path.abspath(os.path.join(EXAMPLE, "fonts"))) in text
    assert "<cachedir>%s</cachedir>" % (tmp_path / "work" / "fonts" / "cache") in text
    assert '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>' in text
    assert sorted(os.path.basename(f) for f in loaded) == ["PBS-Italic.ttf", "PBS-Regular.ttf", "PBS-SemiBold.ttf"]


@pytest.mark.skipif(sys.platform != "darwin", reason="registers fonts with CoreText, which only macOS has")
def test_loading_twice_registers_each_file_once(tmp_path):
    kit = brand.read(EXAMPLE)
    first = fonts.load(kit, str(tmp_path / "work"), platform="darwin")
    second = fonts.load(kit, str(tmp_path / "work"), platform="darwin")
    assert len(first) == 3 and second == []
