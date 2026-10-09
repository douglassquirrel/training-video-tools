"""brand-preview: a picture of a brand kit, for approving it.

`brand-preview BRAND_DIR --out PREVIEW.png`: the kit read with `videotools.brand` (a bad kit is
refused in its words, exit 3) and drawn with `videotools.draw` in its own fonts on a 1920x1080
sheet: every colour as a swatch with its role and hex; a specimen line for every font role the
kit names; the mark and wordmark as the chrome draws them; sample pills, and accent text at a
size above and below `small-text-accent` (rule 3); the end-card illustration and its credit;
the settings; and the WCAG contrast ratio of each text-on-fill pair the chrome uses, printed
too. Refuses an existing output. Needs pycairo.
"""

import argparse
import tempfile
import types

from videotools import brand as brand_
from videotools import cli, contrast, fonts

PROG = "brand-preview"
WIDTH, HEIGHT = 1920, 1080
SWATCH = (62, 210, 200, 150, 180, 84)      # x0, y0, column pitch, row pitch, width, height
SWATCHES_A_ROW = 4
SPECIMEN_X, SPECIMEN_Y = 900, 230
SPECIMEN_SIZES = {"display": 46, "display-medium": 36, "body-medium": 30, "bold": 26}
TABLES_Y, ROW = 700, 24                      # the settings and contrast tables, under the swatches
CONTRAST_COLUMNS = (480, 900)                # the contrast rows run down one column, then the next
ART_WIDTH, ART_HEIGHT = 540, 150             # the illustration fits this box, bottom right, above the band
BAND_Y, RULE_Y = 948, 948

# The text-on-fill pairs the chrome draws, as (text role, fill role); the caption band is added.
PAIRS = [("ink", "background"), ("muted", "background"), ("accent", "background"), ("accent-dark", "background"),
         ("ink", "surface"), ("muted", "surface"), ("accent", "surface"), ("accent-dark", "surface"),
         ("on-accent", "accent"), ("on-accent", "accent-dark"), ("on-accent", "mistake"), ("on-accent", "correct")]


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Draw a one-page preview of a brand kit: its colours, fonts, "
                                "mark, labels, illustration, settings and contrast ratios, for approving it.")
    p.add_argument("BRAND_DIR", help="the kit's folder, holding BRAND.md")
    p.add_argument("--out", metavar="PREVIEW.png", required=True, help="the preview to write (never over a file)")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, brand_.BrandError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def hex_of(colour):
    return "#" + "".join(f"{int(round(v * 255)):02X}" for v in colour)


def pairs(kit):
    """[(name, ratio)] for every pair the chrome uses, the caption band last."""
    out = [(f"{t} on {f}", contrast.ratio(kit["colours"][t], kit["colours"][f])) for t, f in PAIRS]
    band = kit["settings"]["caption-band"]
    out.append((f"on-accent on {band} (caption band)", contrast.ratio(kit["colours"]["on-accent"],
                                                                        brand_.colour(kit, band))))
    return out


def _run(args):
    cli.refuse_existing(args.out)
    cairo = cli.need("cairo")
    kit = brand_.read(args.BRAND_DIR)
    fonts.load(kit, tempfile.mkdtemp(prefix="brand-preview-"))   # a private fonts.conf off macOS; nothing else
    video = types.SimpleNamespace(brand=kit, scale=kit["settings"]["font-size-scale"])   # what frame.mark needs
    from videotools import draw, frame
    c, fnt, scale = kit["colours"], kit["fonts"], video.scale
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_source_rgb(*c["background"])
    ctx.paint()
    grid = kit["settings"]["background-grid"]
    if grid:
        _, spacing, size, opacity = grid
        for x in range(40, WIDTH, spacing):
            for y in range(190, BAND_Y - 20, spacing):
                ctx.rectangle(x - size / 2, y - size / 2, size, size)
        ctx.set_source_rgba(*c["grid"], opacity)
        ctx.fill()

    # The mark and wordmark, the identity line, the title rule.
    frame.mark(ctx, video, 94, 74, 34, 40)
    draw.text(ctx, f"BRAND KIT  ·  {kit['identity']['website']}", 62, 150, fnt["display"], 18 * scale,
              brand_.text_colour(kit, "accent", 18 * scale), track=1)
    rule_role, rule_h = kit["settings"]["title-rule"]
    ctx.rectangle(62, 168, 230, rule_h)
    ctx.set_source_rgb(*brand_.colour(kit, rule_role))
    ctx.fill()

    # Every colour as a swatch with its role and hex.
    x0, y0, dx, dy, sw, sh = SWATCH
    for i, (role, colour) in enumerate(c.items()):
        x, y = x0 + (i % SWATCHES_A_ROW) * dx, y0 + (i // SWATCHES_A_ROW) * dy
        draw.fill_rrect(ctx, x, y, sw, sh, 10, colour, stroke=c["rule"], lw=2)
        draw.text(ctx, role, x, y + sh + 24, fnt["display"], 20 * scale, c["ink"])
        draw.text(ctx, hex_of(colour), x, y + sh + 48, fnt["body"], 18 * scale, c["muted"])

    # A specimen line for every font role the kit names, in that font.
    y = SPECIMEN_Y
    for role in kit["font_files"]:
        size = SPECIMEN_SIZES.get(role, 26) * scale
        draw.text(ctx, f"{role}: {fnt[role]}", SPECIMEN_X, y, fnt[role], size, c["ink"])
        y += size + 16

    # Sample pills, and accent text above and below the small-text size (rule 3).
    y += 24
    x = SPECIMEN_X
    for label, fill in (("COMMON MISTAKE", "mistake"), ("RIGHT WAY", "correct"), ("label", "ink")):
        _, _, w, _ = draw.tag(ctx, label, x, y, fnt["display"], 22 * scale, c[fill], c["on-accent"])
        x += w + 16
    dark_role, limit = kit["settings"]["small-text-accent"]
    above, below = limit + 8, limit - 6
    y += 58
    draw.text(ctx, f"accent at {above:g} px", SPECIMEN_X, y, fnt["display"], above,
              brand_.text_colour(kit, "accent", above))
    draw.text(ctx, f"accent at {below:g} px: {dark_role} (rule 3)", SPECIMEN_X + 320, y, fnt["display"], below,
              brand_.text_colour(kit, "accent", below))

    # The end-card illustration and its credit, bottom right, above the band.
    art = cairo.ImageSurface.create_from_png(kit["illustration"]["end-card"])
    s = min(ART_WIDTH / art.get_width(), ART_HEIGHT / art.get_height())
    ax, ay = WIDTH - 60 - ART_WIDTH, BAND_Y - 64 - art.get_height() * s
    ctx.save()
    ctx.translate(ax, ay)
    ctx.scale(s, s)
    ctx.set_source_surface(art, 0, 0)
    ctx.paint()
    ctx.restore()
    credit = kit["identity"].get("illustration-credit", "")
    if credit:
        draw.text(ctx, credit, ax, BAND_Y - 30, fnt["italic"], 18 * scale, c["muted"])

    # The settings, and the contrast ratios in two columns.
    y = TABLES_Y
    draw.text(ctx, "SETTINGS", 62, y, fnt["display"], 16 * scale, c["muted"], track=2)
    for key, value in kit["settings"].items():
        y += ROW
        draw.text(ctx, f"{key}: {shown(value)}", 62, y, fnt["body"], 18 * scale, c["ink"])
    draw.text(ctx, "CONTRAST (WCAG: 4.5 FOR TEXT, 3 FOR LARGE TEXT)", CONTRAST_COLUMNS[0], TABLES_Y, fnt["display"],
              16 * scale, c["muted"], track=2)
    rows = pairs(kit)
    a_column = (len(rows) + 1) // 2
    for i, (name, r) in enumerate(rows):
        x = CONTRAST_COLUMNS[i // a_column]
        y = TABLES_Y + ROW * (i % a_column + 1)
        draw.text(ctx, f"{name}: {r:.2f}  {contrast.verdict(r)}", x, y, fnt["body"], 18 * scale, c["ink"])
    named = ", ".join(f"{role}: {fnt[role]}" for role in kit["font_files"])
    print(f"{kit['identity']['name']} ({kit['identity']['website']}): {len(c)} colours, "
          f"{len(kit['font_files'])} fonts ({named})")
    print(f"small-text-accent: text under {limit:g} px that would be accent uses {dark_role}; "
          f"shown at {above:g} px (accent) and {below:g} px ({dark_role})")
    print("contrast (WCAG ratio; 4.5 for text, 3 for large text):")
    for name, r in pairs(kit):
        print(f"  {name}: {r:.2f}  {contrast.verdict(r)}")

    # The caption band with its rule, as the chrome draws it.
    band = kit["settings"]["caption-band"]
    ctx.rectangle(0, BAND_Y, WIDTH, HEIGHT - BAND_Y)
    ctx.set_source_rgb(*brand_.colour(kit, band))
    ctx.fill()
    rule_role, rule_h = kit["settings"]["caption-rule"]
    ctx.rectangle(0, RULE_Y, WIDTH, rule_h)
    ctx.set_source_rgb(*brand_.colour(kit, rule_role))
    ctx.fill()
    draw.text(ctx, f"Caption band ({band}), with its rule ({rule_role}) along the top.", WIDTH / 2, 1022,
              fnt["body-medium"], 36 * scale, c["on-accent"], anchor="c")
    surface.flush()
    surface.write_to_png(args.out)
    print(f"Wrote {args.out}")
    return cli.OK


def shown(value):
    """A typed setting as its BRAND.md words."""
    if value is None:
        return "none"
    if isinstance(value, tuple):
        return " ".join(f"{v:g}" if isinstance(v, float) else str(v) for v in value)
    return f"{value:g}" if isinstance(value, float) else str(value)
