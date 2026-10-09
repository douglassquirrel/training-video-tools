"""Cue and scene timing from clip lengths, and the easing helpers scene code animates with.

Each cue lasts its clip plus the script's `cue-gap`, or its `min:`, whichever is longer; the
first cue starts at `lead`; the scene ends `tail` after the last cue, plus the scene's `extra`;
the length is rounded to whole frames. Standard library only; runs on Python 3.9.
"""

import math

from videotools import cli, script

WORDS_PER_SECOND = 2.6      # the estimate when a cue has no clip (stills only)
EPSILON = 1e-9              # floating-point slack when asking which cue has started


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def lerp(a, b, p):
    return a + (b - a) * p


def prog(t, a, b):
    """Linear progress of t from a to b, 0–1; a step at b when the span is empty."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def ease(p):
    """Smoothstep."""
    return p * p * (3 - 2 * p)


def ep(t, a, b):
    """Eased progress of t from a to b."""
    return ease(prog(t, a, b))


def pulse(t, a, b):
    """0 -> 1 -> 0 over [a, b]."""
    return math.sin(math.pi * prog(t, a, b))


class Timeline:
    """A scene's timing: cue starts and lengths (by the script's cue numbers, from 1), the
    total in seconds and frames, and which cues were estimated rather than measured."""

    def __init__(self, starts, lengths, total, fps, estimated=()):
        self._starts, self._lengths = list(starts), list(lengths)
        self.fps = fps
        self.frames = int(round(total * fps))
        self.total = self.frames / fps
        self.estimated = list(estimated)

    def start(self, cue):
        return self._starts[cue - 1]

    def length(self, cue):
        return self._lengths[cue - 1]

    def cue(self, t):
        """The cue speaking at t: the last whose start is at or before t; 0 before the first."""
        now = 0
        for n, s in enumerate(self._starts, 1):
            if t >= s - EPSILON:
                now = n
        return now

    def p(self, t, cue, a, b):
        """Eased progress of t between a and b seconds after the start of `cue`."""
        s = self.start(cue)
        return ep(t, s + a, s + b)


def clips_for(timing, scene):
    """The clip lengths for a scene from timing.json's data (None where there is none)."""
    if not timing:
        return None
    clips = timing.get("scenes", {}).get(scene["key"])
    if clips is None:
        return None
    return [clips[i] if i < len(clips) else None for i in range(len(scene["cues"]))]


def build(settings, scene, clips, estimate=False):
    """The scene's Timeline from its cues and clip lengths (a list, None entries for missing
    clips, or None for no clips at all). A missing clip is refused unless `estimate`, when it
    is taken as the cue's words at 2.6 a second and listed in the result's `estimated`."""
    cues = scene["cues"]
    if clips is None:
        if cues and not estimate:
            raise cli.Failure("scene %s has no narration clips; run narrate first" % scene["key"])
        clips = [None] * len(cues)
    starts, lengths, estimated = [], [], []
    t = settings["lead"]
    for cue in cues:
        clip = clips[cue["n"] - 1]
        if clip is None:
            if not estimate:
                raise cli.Failure("scene %s cue %d has no narration clip; run narrate first" % (scene["key"], cue["n"]))
            clip = len(cue["text"].split()) / WORDS_PER_SECOND
            estimated.append(cue["n"])
        length = max(clip + settings["cue-gap"], script.minimum(cue))
        starts.append(t)
        lengths.append(length)
        t += length
    total = t + settings["tail"] + script.extra(scene)
    return Timeline(starts, lengths, total, settings["fps"], estimated)
