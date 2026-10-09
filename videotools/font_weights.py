"""font-weights: static instances of a variable font, each under its own family name.

cairo's simple text API cannot choose a weight from a variable font, so a brand kit names one
static file per weight. For each `--weights` value an instance is made with fontTools and
renamed `PREFIX <Weight>` (`PREFIX MediumItalic` for an italic font): name IDs 1, 4 and 6 set,
16, 17, 21, 22 and 25 removed; written to `DIR/PREFIX-<Weight>.ttf`. Refuses a font without a
`wght` axis, a weight outside its range, and any existing output. Needs fontTools.
"""

import argparse
import os

from videotools import cli

PROG = "font-weights"
WEIGHT_NAMES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
                600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
REMOVED_NAME_IDS = (16, 17, 21, 22, 25)


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Make a static font file per weight from a variable "
                                "font, each under its own family name, so that cairo's simple text API "
                                "(and a brand kit) can name a weight.")
    p.add_argument("--weights", required=True, type=weights, metavar="400,600,...",
                   help="the weights wanted, from 100 to 900 in hundreds")
    p.add_argument("--family-prefix", required=True, metavar="PREFIX", help="the family name's start, e.g. EBG")
    p.add_argument("--out", required=True, metavar="DIR", help="the folder to write into (never over a file)")
    p.add_argument("FONT", help="the variable font file")
    return p


def weights(value):
    out = []
    for part in value.split(","):
        part = part.strip()
        if not part.isdigit() or int(part) not in WEIGHT_NAMES:
            raise argparse.ArgumentTypeError(f"'{part}' is not a weight from 100 to 900 in hundreds")
        out.append(int(part))
    return out


def style_name(weight, italic):
    """Thin … Black, with Italic appended for an italic font; the italic at 400 is just Italic."""
    if italic:
        return "Italic" if weight == 400 else WEIGHT_NAMES[weight] + "Italic"
    return WEIGHT_NAMES[weight]


def is_italic(font):
    """Whether the font calls itself italic (OS/2 fsSelection bit 0, head macStyle bit 1, or its
    subfamily name)."""
    name = font["name"]
    sub = (name.getDebugName(2) or "") + " " + (name.getDebugName(17) or "")
    return bool(font["OS/2"].fsSelection & 1) or bool(font["head"].macStyle & 2) or "italic" in sub.lower()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except cli.Failure as f:
        return cli.report(PROG, f)


def _run(args):
    if not os.path.isfile(args.FONT):
        raise cli.Failure(f"no such file: {args.FONT}")
    try:
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
    except ImportError as e:
        raise cli.Failure(f"fontTools is not installed in this Python ({e}); install it into the venv as the "
                          "README says", cli.EXTERNAL) from e
    font = TTFont(args.FONT)
    axes = {a.axisTag: a for a in font["fvar"].axes} if "fvar" in font else {}
    if "wght" not in axes:
        raise cli.Failure(f"{args.FONT} has no 'wght' axis (is it a variable font?)")
    low, high = axes["wght"].minValue, axes["wght"].maxValue
    for w in args.weights:
        if not low <= w <= high:
            raise cli.Failure(f"weight {w} is outside the font's wght axis ({low:g} to {high:g})")
    italic = is_italic(font)
    outputs = [os.path.join(args.out, f"{args.family_prefix}-{style_name(w, italic)}.ttf") for w in args.weights]
    existing = [p for p in outputs if os.path.lexists(p)]
    if existing:
        raise cli.Failure("these would be written over; delete them first:\n" + "\n".join("  " + p for p in existing))
    os.makedirs(args.out, exist_ok=True)
    for w, path in zip(args.weights, outputs):
        instance = instancer.instantiateVariableFont(TTFont(args.FONT), {"wght": w})
        family = f"{args.family_prefix} {style_name(w, italic)}"
        name = instance["name"]
        for name_id in REMOVED_NAME_IDS:
            name.removeNames(nameID=name_id)
        for name_id, value in ((1, family), (4, family), (6, family.replace(" ", ""))):
            name.setName(value, name_id, 3, 1, 0x409)
            name.setName(value, name_id, 1, 0, 0)
        instance.save(path)
        print(f"{path}  {family}  (wght {w})")
    return cli.OK
