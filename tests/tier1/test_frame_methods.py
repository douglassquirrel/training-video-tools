"""scenes.Frame's brand-aware drawing: colours by name, fonts by role, sizes scaled, rule 3, labels checked."""

import math
import os

import cairo
import pytest

from videotools import brand, cli, scenes

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "brands", "paperboat")
SCENE = {"key": "A", "name": "A", "line": 1, "props": {}, "cues": [], "side": [],
         "screen": [{"text": "near side", "line": 2}, {"text": "12 in", "line": 3}]}
PAPER, SLEEVE, SKIN = (1.0, 0.5, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)


def rgb255(c):
    return tuple(round(v * 255) for v in c)


def pixel(surface, x, y):
    data, stride = surface.get_data(), surface.get_stride()
    i = int(y) * stride + int(x) * 4
    return data[i + 2], data[i + 1], data[i]


@pytest.fixture
def kit():
    return brand.read(EXAMPLE)


def frame(kit, colours=None, w=600, h=300):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    colours = {"paper": PAPER} if colours is None else colours
    return scenes.Frame(ctx, 0.0, None, SCENE, colours, kit, (0, 0, w, h)), surface


def test_colour_finds_the_scripts_colours_then_the_brands_roles_and_refuses_the_rest(kit):
    f, _ = frame(kit)
    assert f.colour("paper") == PAPER
    assert f.colour("accent") == kit["colours"]["accent"]
    with pytest.raises(cli.Failure) as e:
        f.colour("cover")
    assert str(e.value) == ("scene A: no colour 'cover' in the script's Colours (paper) or the brand's roles "
                            "(" + ", ".join(kit["colours"]) + ")")


def test_a_small_accent_pill_takes_the_darker_fill_and_a_large_one_keeps_accent(kit):
    assert kit["settings"]["small-text-accent"] == ("accent-dark", 24) and kit["settings"]["font-size-scale"] == 1.12
    f, s = frame(kit)
    f.tag("near side", 50, 100, size=20, fill="accent", anchor="l")           # 20 × 1.12 = 22.4 < 24: rule 3
    f.tag("near side", 50, 200, size=24, fill="accent", anchor="l")           # 24 × 1.12 = 26.9: not small
    assert pixel(s, 52, 100) == rgb255(kit["colours"]["accent-dark"])
    assert pixel(s, 52, 200) == rgb255(kit["colours"]["accent"])


def test_text_tag_callout_and_dimension_refuse_a_label_the_script_does_not_list(kit):
    f, _ = frame(kit)
    for call in (lambda: f.tag("near sid", 50, 100), lambda: f.callout("near sid", (10, 10), (100, 100)),
                 lambda: f.dimension((10, 10), (100, 10), "13 in"), lambda: f.text("near sid", 50, 100, 30, check=True)):
        with pytest.raises(cli.Failure) as e:
            call()
        assert "which is not in the script's On screen list (near side, 12 in)" in str(e.value)
    f.text("anything at all", 50, 100, 30)                                    # unchecked text is free


def test_text_uses_the_brands_font_role_and_scales_the_size_and_applies_rule_3(kit):
    kit = dict(kit, settings=dict(kit["settings"], **{"font-size-scale": 2.0}))
    f, s = frame(kit)
    f.text("II", 20, 100, 10, role="display", colour="accent")                 # 10 × 2 = 20 < 24: darker
    f.text("II", 20, 200, 12, role="display", colour="accent")                 # 12 × 2 = 24: accent
    small = {pixel(s, x, 95) for x in range(20, 60)}
    assert rgb255(kit["colours"]["accent-dark"]) in small
    assert rgb255(kit["colours"]["accent"]) in {pixel(s, x, 190) for x in range(20, 80)}
    with pytest.raises(cli.Failure) as e:
        f.text("x", 0, 0, 10, role="handwriting")
    assert str(e.value).startswith("scene A: no font role 'handwriting' in the brand kit (")


def test_badge_fills_correct_or_mistake_with_the_brands_mark_colour(kit):
    f, s = frame(kit)
    f.badge(100, 100, True)
    f.badge(300, 100, False)
    assert pixel(s, 100 + 18, 100 - 14) == rgb255(kit["colours"]["correct"])
    assert pixel(s, 300 + 18, 100 - 14) == rgb255(kit["colours"]["mistake"])


def test_hand_takes_skin_and_sleeve_from_the_scripts_colours_else_neutral_defaults(kit):
    f, s = frame(kit, {"skin": SKIN, "skin-dark": (0, 0.5, 0), "sleeve": SLEEVE})
    f.hand(400, 150, angle=0.0, scale=1.0, label="L")
    assert pixel(s, 400 - 190, 150) == rgb255(SLEEVE)                          # the sleeve's end (it spans x-200..x-96)
    assert pixel(s, 400 - 30, 150) == rgb255(SKIN)                             # the palm
    assert pixel(s, 400 - 150 + 12, 150) == rgb255(kit["colours"]["accent"])   # the label's roundel
    g, s2 = frame(kit, {})
    g.hand(400, 150, angle=0.0, scale=1.0)
    for probe_x, name in ((400 - 190, "sleeve"), (400 - 30, "skin")):
        got, want = pixel(s2, probe_x, 150), rgb255(scenes.HAND_DEFAULTS[name])
        assert all(abs(a - b) <= 1 for a, b in zip(got, want)), (name, got, want)   # cairo's own 8-bit rounding


def test_callout_and_dimension_draw_their_pills_with_named_colours(kit):
    f, s = frame(kit)
    f.callout("near side", (20, 20), (200, 100), fill="paper", leader="ink")
    assert pixel(s, 202, 100) == rgb255(PAPER)
    f.dimension((100, 250), (300, 250), "12 in", colour="accent", side=-1)
    assert pixel(s, 200, 250) == rgb255(kit["colours"]["accent"])              # the line itself
    assert pixel(s, 200, 220) == rgb255(kit["colours"]["accent"])              # the pill, 30 px to the side
    assert math.isclose(1, 1)


def test_a_label_ending_in_a_tick_the_brand_font_lacks_is_a_wider_pill_with_the_tick_drawn(kit, tmp_path):
    from videotools import fonts
    fonts.load(kit, str(tmp_path / "work"), platform="linux")     # registers the families with the glyph registry
    scene = dict(SCENE, screen=[{"text": "done", "line": 2}, {"text": "done ✓", "line": 3}])
    f, surface = frame(kit)
    f.scene = scene
    _, _, plain, _ = f.tag("done", 10, 100, size=30)
    bx, by, ticked, bh = f.tag("done ✓", 10, 200, size=30)
    assert ticked > plain + 20                                      # the tick is counted
    size = 30 * kit["settings"]["font-size-scale"]
    tick_x = bx + 14 + (ticked - 28) - 0.8 * size                   # the tick starts 0.8 × size before the text's end
    assert pixel(surface, tick_x + 0.32 * size, 200 + 0.2 * size) == rgb255(kit["colours"]["on-accent"])
