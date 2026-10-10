"""check-script: read a script, check it, print the summary and every `added:` line.

Standard library only; runs on Python 3.9.
"""

import argparse
import json
import os

from videotools import brand, choreography, cli, config, elements, scenes, script, timeline

PROG = "check-script"
WORDS_PER_SECOND = 2.6


def summary(data):
    """The lines check-script prints for a script: counts, tracker, mistakes, added lines."""
    cues = [(sc, c) for sc in data["scenes"] for c in sc["cues"]]
    words = sum(len(c["text"].split()) for _, c in cues)
    out = [f"{data['title']}: {len(data['scenes'])} scenes, {len(cues)} cues, {words} words "
           f"(about {round(words / WORDS_PER_SECOND)} s of speech at {WORDS_PER_SECOND:.1f} words a second)"]
    letters = []
    for sc in data["scenes"]:
        letter = sc["props"].get("letter")
        if letter and letter not in letters:
            letters.append(letter)
    out.append("Tracker: " + " ".join(letters))
    out.append("Mistakes:")
    for sc, c in cues:
        if "mistake" in c:
            out.append(f"  {sc['key']} cue {c['n']}: {c['mistake']}")
    added = [(sc["key"], f"cue {c['n']}", c["text"], c["added"]) for sc, c in cues if "added" in c]
    for sc in data["scenes"]:
        for name, items in (("side panel", sc["side"]), ("on screen", sc["screen"])):
            added += [(sc["key"], name, it["text"], it["added"]) for it in items if "added" in it]
    out.append(f"Beyond the source (added:), {len(added)}, for approval and checking:")
    for key, where, text, why in added:
        out.append(f'  {key}, {where}: "{text}"\n      -> {why}')
    return "\n".join(out)


def brand_problems(data, script_path, script_problems):
    """(The brand kit's problems, each prefixed with its BRAND.md path; the kit when it read
    cleanly, else None). Nothing if the script's own check already found the kit missing (one
    problem, not two)."""
    name = data["settings"].get("brand")
    folder = brand.folder_for(script_path, name) if name else None
    if not folder or any(f"brand '{name}'" in p for p in script_problems):
        return [], None
    try:
        return [], brand.read(folder)
    except brand.BrandError as e:
        return [f"{os.path.join(folder, 'BRAND.md')}: {p}" for p in e.problems], None


# Which role the chrome draws each text in (PLAN.md item 12): On screen labels in the display
# font, the frame methods' default for pills and callouts (Squirrel, 10 October 2026).
SETTING_ROLES = {"title": "display", "subtitle": "italic", "eyebrow": "display", "source-label": "display",
                 "title-image-caption": "italic", "credit": "body"}
SCENE_ROLES = {"title": "display", "eyebrow": "display", "tracker-label": "display", "side-panel-heading": "display"}
KIT_ROLES = {"website": "italic", "illustration-credit": "body"}
DRAWN_ANYWAY = "✓✗"          # drawn as strokes where a font lacks them (draw.text)


def font_problems(data, kit):
    """Every text the chrome draws that holds a character the font for its role lacks: one
    problem per text, naming where it is, the text, the first such character and the file."""
    from videotools import glyphs
    problems = []

    def check(where, text, role):
        path = kit["font_files"].get(role) or kit["font_files"].get(brand.FONT_FALLBACKS.get(role, role))
        if not text or not path:
            return
        have = glyphs.characters(path)
        for ch in text:
            if ord(ch) not in have and ch not in DRAWN_ANYWAY:
                problems.append(f"{where} '{text}' has '{ch}' (U+{ord(ch):04X}), which {path} lacks")
                return

    def line(section, key):
        n = data["lines"].get((section, key))
        return f"line {n}: " if n else ""

    for key, role in SETTING_ROLES.items():
        check(f"{line('settings', key)}setting '{key}'", data["settings"].get(key, ""), role)
    for scene in data["scenes"]:
        k = scene["key"]
        for key, role in SCENE_ROLES.items():
            check(f"{line(k, key)}scene {k} '{key}'", scene["props"].get(key, ""), role)
        for cue in scene["cues"]:
            check(f"line {cue['line']}: scene {k} cue {cue['n']} caption", cue["text"], "body-medium")
        for item in scene["side"]:
            check(f"line {item['line']}: scene {k} side panel item", item["text"], "body")
        for item in scene["screen"]:
            check(f"line {item['line']}: scene {k} on screen label", item["text"], "display")
    kit_file = os.path.join(kit["folder"], "BRAND.md")
    for key, role in KIT_ROLES.items():
        check(f"{kit_file}: Identity '{key}'", kit["identity"].get(key, ""), role)
    return problems


def phoneme_problems(data):
    """Bad [[…]] spans in say: lines (unclosed, empty, a symbol the voice would drop), and a
    span in a caption, which would show on screen; each by its line."""
    from videotools import phonemes
    out = []
    for scene in data["scenes"]:
        k = scene["key"]
        for cue in scene["cues"]:
            if phonemes.OPEN in cue["text"]:
                out.append(f"line {cue['line']}: scene {k} cue {cue['n']} caption '{cue['text']}' holds "
                           f"'{phonemes.OPEN}', which would show on screen; phoneme spans go in say:")
            if "say" in cue:
                n = data["lines"].get((k, f"cue {cue['n']} say"), cue["line"])
                out += [f"line {n}: scene {k} cue {cue['n']} say: {p}" for p in phonemes.problems(cue["say"])]
    return out


def code_problems(data, script_path):
    """The scene code's problems (scenes.check_code), once the script names a scene-code folder."""
    folder = data["settings"].get("scene-code")
    if not folder:
        return []
    return scenes.check_code(os.path.join(os.path.dirname(os.path.abspath(script_path)), folder), data)


def choreography_problems(data, args, script_path):
    """The problems with every described scene (choreography.check): the library opened from
    --elements or the config file when a cast names a library element (one problem when it
    cannot be, the pieces still checked), cue lengths from work/narration/timing.json when it
    exists, else the estimate. Nothing when no scene is described or the settings are unusable
    (their problems are already listed)."""
    described = [sc for sc in data["scenes"] if sc["cast"] or sc["panels"]]
    if not described:
        return []
    problems, lib = [], None
    casts = [m for sc in described for m in sc["cast"] + [m for p in sc["panels"].values() for m in p["cast"]]]
    if any(m["element"] not in choreography.PIECES for m in casts):
        try:
            lib = elements.open_library(*elements.settings(args, config.read()))
        except (cli.Failure, config.ConfigError) as f:
            problems.append(str(f))
    try:
        settings = script.settings(data)
    except (KeyError, ValueError):
        return problems
    folder = script.folder(script_path)
    timing_path = os.path.join(folder, "work", "narration", "timing.json")
    timing = None
    if os.path.isfile(timing_path):
        with open(timing_path, encoding="utf-8") as f:
            timing = json.load(f)
    for sc in described:
        tl = timeline.build(settings, sc, timeline.clips_for(timing, sc), estimate=True)
        problems += choreography.check(sc, tl, lib, folder)
    return problems


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Read a video's script.md, check it against "
                                "the script format, and list what needs approval and checking.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--json", metavar="OUT", help="also write the parsed script as JSON (never over an existing file)")
    elements.add_arguments(p)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if not os.path.isfile(args.SCRIPT):
            raise cli.Failure(f"no such file: {args.SCRIPT}")
        if args.json:
            cli.refuse_existing(args.json)
    except cli.Failure as f:
        return cli.report(PROG, f)
    with open(args.SCRIPT, encoding="utf-8") as f:
        data, problems = script.parse(f.read())
    problems += script.check(data, args.SCRIPT)
    kit_problems, kit = brand_problems(data, args.SCRIPT, problems)
    problems += kit_problems
    if kit:
        try:
            problems += font_problems(data, kit)
        except cli.Failure as f:            # a font file that is not a font: one problem, not a crash
            problems.append(str(f))
    problems += phoneme_problems(data)
    problems += code_problems(data, args.SCRIPT)
    problems += choreography_problems(data, args, args.SCRIPT)
    print(summary(data))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in data.items() if k != "lines"}, f, indent=1, ensure_ascii=False)
        print(f"Parsed script written to {args.json}")
    if problems:
        print(f"\n{len(problems)} problem{'' if len(problems) == 1 else 's'}:")
        for p in problems:
            print("  - " + p)
        return cli.PROBLEMS
    print("\nNo problems found.")
    return cli.OK
