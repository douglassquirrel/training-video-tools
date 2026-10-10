"""Credits for the library's art (PLAN.md item 16): which library elements a video uses, and the
lines the end card shows for them, from the script's `element-credits` setting (`auto`, `none`,
or the wording itself). Standard library only; runs on Python 3.9.
"""

from videotools import choreography


def elements_used(data):
    """The library elements named in every scene's cast and panel casts, in script order, once
    each; the tools' own pieces are not elements."""
    out = []
    for scene in data["scenes"]:
        casts = [scene["cast"]] + [p["cast"] for p in scene["panels"].values()]
        for cast in casts:
            for m in cast:
                if m["element"] not in choreography.PIECES and m["element"] not in out:
                    out.append(m["element"])
    return out


def setting(data):
    return data["settings"].get("element-credits") or "auto"


def lines(data, lib):
    """The credit lines for the end card: none for `none`; the wording itself; or, for `auto`,
    one line per category from the library's credits for the elements used, `Icons: Tabler
    Icons`; [] when the video uses no library elements (then `lib` may be None)."""
    value = setting(data)
    if value == "none":
        return []
    if value != "auto":
        return [value]
    names = known(data, lib)
    if not names:
        return []
    by_category = {}
    for entry in lib.credits(names):
        by_category.setdefault(entry["category"], []).append(entry["credit"])
    return [f"{category}: {', '.join(credits)}" for category, credits in by_category.items()]


def known(data, lib):
    """The elements used that the library has (an unknown one is a problem for the checks, not
    a credit); [] without a library."""
    if lib is None:
        return []
    have = set(lib.names())
    return [name for name in elements_used(data) if name in have]


def sources(data, lib):
    """For the credits file: [(credit line, category, licence, [elements])], one per source the
    video's elements came from, in the library's stable order; nothing for art drawn there."""
    found = {}
    for name in known(data, lib):
        for entry in lib.credits([name]):
            key = (entry["category"], entry["credit"])
            found.setdefault(key, {"licence": entry["licence"], "elements": []})["elements"].append(name)
    return [(credit, category, v["licence"], v["elements"])
            for (category, credit), v in sorted(found.items())]


def file_text(data, lib):
    """The credits file beside the finished video: every source the video's elements came from,
    its credit line, licence and elements, one source per paragraph."""
    out = [f"Credits for {data['title']}", ""]
    for credit, category, licence, names in sources(data, lib):
        out += [f"{category}: {credit}", f"  licence: {licence}", f"  elements: {', '.join(names)}", ""]
    return "\n".join(out)


def file_path(out_file):
    """`out/video.credits.txt` beside `out/video.mp4`."""
    import os
    return os.path.splitext(out_file)[0] + ".credits.txt"
