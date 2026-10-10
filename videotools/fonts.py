"""Make a brand's font files available to cairo by family name, without installing them.

cairo's simple text API looks fonts up by family name. On macOS the Homebrew build goes through
CoreText, so each file is registered with the font manager for this process only
(`CTFontManagerRegisterFontsForURL`, process scope). Elsewhere cairo uses fontconfig, so a
private `fonts.conf` naming the brand's font folder is written under the video's `work/fonts/`
and `FONTCONFIG_FILE` set before the first text is drawn. Nothing is installed either way.
"""

import os
import sys

_registered = set()


def load(kit, work_folder, platform=None):
    """Make the kit's fonts findable by name. Returns the files newly made available."""
    platform = platform or sys.platform
    from videotools import glyphs
    for role, path in kit["font_files"].items():
        glyphs.register(kit["fonts"][role], path)       # so draw.text knows which characters each family lacks
    files = sorted(set(kit["font_files"].values()))
    if platform == "darwin":
        return [f for f in files if _register_with_coretext(f)]
    return _fontconfig(files, work_folder)


def _register_with_coretext(path):
    import ctypes
    import ctypes.util
    if path in _registered:
        return False
    cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))
    ct = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreText"))
    cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
    cf.CFURLCreateFromFileSystemRepresentation.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long,
                                                           ctypes.c_bool]
    ct.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool
    ct.CTFontManagerRegisterFontsForURL.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    raw = os.fsencode(path)
    url = cf.CFURLCreateFromFileSystemRepresentation(None, raw, len(raw), False)
    error = ctypes.c_void_p()
    ct.CTFontManagerRegisterFontsForURL(url, 1, ctypes.byref(error))   # 1: this process only
    _registered.add(path)
    return True


def _fontconfig(files, work_folder):
    folder = os.path.join(work_folder, "fonts")
    conf = os.path.join(folder, "fonts.conf")
    if os.environ.get("FONTCONFIG_FILE") == conf:
        return []
    os.makedirs(folder, exist_ok=True)
    dirs = sorted({os.path.dirname(f) for f in files})
    with open(conf, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n<fontconfig>\n'
                '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>\n')
        for d in dirs:
            f.write(f"<dir>{d}</dir>\n")
        f.write(f"<cachedir>{os.path.join(folder, 'cache')}</cachedir>\n</fontconfig>\n")
    os.environ["FONTCONFIG_FILE"] = conf
    return files
