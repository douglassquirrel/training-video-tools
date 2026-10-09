"""The frame around the subject: background, header and tracker, reference column, caption
band, mistake panels, title and end cards, fades; all from the script and the brand kit.

This half is the rules, standard library only; `chrome_draw` draws them.
"""

from videotools import timeline as tl_


class Layout:
    """Every region of the frame, named in one place. Only 1920x1080 is laid out so far."""

    def __init__(self, size):
        if tuple(size) != (1920, 1080):
            raise ValueError(f"no layout for a {size[0]}x{size[1]} frame; only 1920x1080 is laid out")
        self.width, self.height = size
        self.area = (40, 118, 1422, 818)            # the animation area
        self.column = (1492, 118, 388, 818)         # the reference column
        self.caption = (0, 948, 1920, 132)          # the caption band
        self.header_rule = 112                      # y of the rule under the header
        self.card = (0, 0, 1920, 948)               # title and end cards draw here


def px(scale, size):
    """A font size in the brand's scale."""
    return size * scale


def tracker(data):
    """The tracker's places in script order: [(letter, label, [scene keys])], scenes sharing a
    letter sharing a place, labelled by the first `tracker-label` given for it."""
    places = []
    for scene in data["scenes"]:
        letter = scene["props"].get("letter")
        if not letter:
            continue
        for place in places:
            if place[0] == letter:
                place[2].append(scene["key"])
                if place[1] == letter and scene["props"].get("tracker-label"):
                    place[1] = scene["props"]["tracker-label"]
                break
        else:
            places.append([letter, scene["props"].get("tracker-label") or letter, [scene["key"]]])
    return [tuple(p) for p in places]


def tracker_place(data, scene):
    """A lettered scene's place in the tracker; for a scene without a letter, the number of
    places whose scenes all come before it in the script (so an overview before the steps is 0
    and a recap after them is the number of places)."""
    places = tracker(data)
    for i, (_, _, keys) in enumerate(places):
        if scene["key"] in keys:
            return i
    order = [s["key"] for s in data["scenes"]]
    at = order.index(scene["key"]) if scene["key"] in order else len(order)
    return sum(1 for _, _, keys in places if all(order.index(k) < at for k in keys))


def tracker_done_now(data, scene):
    """([done place indexes], the current place or None) for the header's tracker."""
    place = tracker_place(data, scene)
    lettered = scene["props"].get("letter") is not None
    return (list(range(place)), place) if lettered else (list(range(place)), None)


def title_steps(data):
    """[(letter, title)] for the title card: one per letter, the first lettered scene's title."""
    out, seen = [], set()
    for scene in data["scenes"]:
        letter = scene["props"].get("letter")
        if letter and letter not in seen:
            seen.add(letter)
            out.append((letter, scene["props"].get("title", "")))
    return out


def current_step(scene, timeline, t):
    """The side-panel step the speaking cue names (`step:`), or None."""
    n = timeline.cue(t)
    if n == 0:
        return None
    cue = scene["cues"][n - 1]
    return int(cue["step"]) if "step" in cue else None


def steps_done(scene, timeline, t):
    """The steps named by cues already past."""
    n = timeline.cue(t)
    return sorted({int(c["step"]) for c in scene["cues"][:max(0, n - 1)] if "step" in c})


def checklist_progress(timeline, cue, count, t):
    """How far (eased, 0–1) each of `count` ticks has appeared: one by one during `cue`, spaced
    (length - 0.6) / count apart, each taking 0.4 s."""
    start, length = timeline.start(cue), timeline.length(cue)
    step = (length - 0.6) / count
    return [tl_.ep(t, start + i * step, start + i * step + 0.4) for i in range(count)]
