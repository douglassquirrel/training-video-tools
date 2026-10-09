"""check-script: read a script, check it, print the summary and every `added:` line.

Standard library only; runs on Python 3.9.
"""

import argparse
import json
import os

from videotools import brand, cli, scenes, script

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
    """The brand kit's problems, each prefixed with its BRAND.md path; nothing if the script's
    own check already found the kit missing (one problem, not two)."""
    name = data["settings"].get("brand")
    folder = brand.folder_for(script_path, name) if name else None
    if not folder or any(f"brand '{name}'" in p for p in script_problems):
        return []
    try:
        brand.read(folder)
    except brand.BrandError as e:
        return [f"{os.path.join(folder, 'BRAND.md')}: {p}" for p in e.problems]
    return []


def code_problems(data, script_path):
    """The scene code's problems (scenes.check_code), once the script names a scene-code folder."""
    folder = data["settings"].get("scene-code")
    if not folder:
        return []
    return scenes.check_code(os.path.join(os.path.dirname(os.path.abspath(script_path)), folder), data)


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Read a video's script.md, check it against "
                                "the script format, and list what needs approval and checking.")
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--json", metavar="OUT", help="also write the parsed script as JSON (never over an existing file)")
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
    problems += brand_problems(data, args.SCRIPT, problems)
    problems += code_problems(data, args.SCRIPT)
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
