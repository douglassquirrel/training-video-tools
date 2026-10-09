"""A tiny invented variable font for the font-weights tests, built with fontTools: two glyphs
(.notdef and A), one axis wght 300–800, two masters whose A differs in width."""

from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, SourceDescriptor
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.varLib import build


def master(width, italic=False):
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder([".notdef", "A"])
    fb.setupCharacterMap({0x41: "A"})
    glyphs = {}
    for name, w in ((".notdef", 500), ("A", width)):
        pen = TTGlyphPen(None)
        pen.moveTo((0, 0))
        pen.lineTo((w, 0))
        pen.lineTo((w, 700))
        pen.lineTo((0, 700))
        pen.closePath()
        glyphs[name] = pen.glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({".notdef": (500, 0), "A": (width, 0)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    style = "Italic" if italic else "Regular"
    fb.setupNameTable({"familyName": "Tiny Var", "styleName": style, "psName": "TinyVar-" + style,
                       "typographicFamily": "Tiny Var", "typographicSubfamily": style})
    fb.setupOS2(fsSelection=1 if italic else 64, sTypoAscender=800, sTypoDescender=-200)
    fb.setupPost(italicAngle=-10 if italic else 0)
    if italic:
        fb.font["head"].macStyle |= 2
    return fb.font


def variable_font(path, italic=False):
    """Write the variable font to `path`; returns the path."""
    ds = DesignSpaceDocument()
    ds.addAxis(AxisDescriptor(tag="wght", name="Weight", minimum=300, default=300, maximum=800))
    for width, loc in ((500, 300), (800, 800)):
        s = SourceDescriptor()
        s.font = master(width, italic)
        s.location = {"Weight": loc}
        ds.addSource(s)
    font, _, _ = build(ds)
    font.save(path)
    return path
