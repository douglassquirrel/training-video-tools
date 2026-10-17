"""narrate: one narration clip per cue, with the local Kokoro model, and timing.json.

Reads the script and the config, speaks each cue's `say:` (or its caption) through kokoro-onnx
in the voice, speed and language the script names (flags win over the script, the script over
the config), trims the silence, and writes `work/narration/<scene>_<NN>.wav` and
`work/narration/timing.json` under the video's folder. Refuses to write over anything unless
--replace. Needs numpy, soundfile and kokoro-onnx, imported only when a real run starts.
"""

import argparse
import json
import os
import sys

from videotools import cli, config, phonemes, script

PROG = "narrate"
WORDS_PER_SECOND = 2.6
LINES_SPEED = 1.5       # --lines' default: chosen by ear from the samples (Squirrel, 17 October 2026; Settled 50)
THRESHOLD = 0.01        # a sample above this is sound
BEFORE, AFTER = 0.03, 0.08  # seconds kept before the first and after the last sound


def trim(samples, rate):
    """The clip without its leading and trailing silence, keeping 30 ms before the first and
    80 ms after the last sample above the threshold; an all-silent clip is returned whole."""
    import numpy as np
    loud = np.where(np.abs(samples) > THRESHOLD)[0]
    if not len(loud):
        return samples
    return samples[max(0, loud[0] - int(BEFORE * rate)): loud[-1] + 1 + int(AFTER * rate)]


def parser():
    p = argparse.ArgumentParser(prog=PROG, description="Speak every cue of a video's script with the "
                                "local speech model, one clip per cue, and write the clip lengths "
                                "to timing.json. Flags win over the script; the script over "
                                "~/.video-tools.conf.")
    p.add_argument("SCRIPT", nargs="?", help="the video's script.md (not with --lines)")
    p.add_argument("--lines", metavar="TABLE.md",
                   help="instead of a script: a Markdown table of description lines ('#', 'Start (s)', 'Line'), "
                        "each spoken to its own clip in --out (PLAN.md item 26)")
    p.add_argument("--out", metavar="FOLDER", help="with --lines: the folder for the clips and timing.json")
    p.add_argument("--scenes", metavar="KEY,...", help="only these scenes (keys as in the script)")
    p.add_argument("--voice", help="the voice, e.g. af_heart (default: the script's; with --lines, VOICE in the "
                                   "config, else af_heart)")
    p.add_argument("--speed", type=float, help="the speed, e.g. 0.98 (default: the script's; with --lines 1.5, "
                                               "within the model's 0.5 to 2.0)")
    p.add_argument("--replace", action="store_true",
                   help="write over existing clips and timing.json, listing them first")
    p.add_argument("--phonemes", action="store_true",
                   help="with --dry-run: also print the phoneme string each cue would be given, [[…]] spans spliced in")
    p.add_argument("--dry-run", action="store_true",
                   help="list the cues, the voice and an estimate of each clip; write nothing")
    return p


def clip_name(scene, cue):
    return f"{scene['key']}_{cue['n']:02d}.wav"


def _model_dir(conf):
    """The folder holding model.onnx and voices.npz, from SPEECH_MODEL_DIR."""
    folder = conf.get("SPEECH_MODEL_DIR")
    if not folder:
        raise cli.Failure(f"SPEECH_MODEL_DIR is not set in {config.path()}; see the README's one-time set-up")
    model, voices = os.path.join(folder, "model.onnx"), os.path.join(folder, "voices.npz")
    if not (os.path.isfile(model) and os.path.isfile(voices)):
        raise cli.Failure(f"no model.onnx and voices.npz in {folder} (SPEECH_MODEL_DIR in {config.path()}); "
                          "see the README's one-time set-up")
    return model, voices


def _load_model(model, voices):
    return cli.need("kokoro_onnx").Kokoro(model, voices)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, config.ConfigError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def _phonemizer(lang):
    """text -> phonemes, through the model's own tokenizer (espeak), as create() would; needs
    the speech package (the usual one line if it is missing) but not the model file."""
    import importlib
    cli.need("kokoro_onnx")
    tokenizer = importlib.import_module("kokoro_onnx.tokenizer").Tokenizer()
    return lambda text: tokenizer.phonemize(text, lang)


def spoken_phonemes(cue, phonemize):
    """The phoneme string for a cue whose say: holds a [[…]] span: text parts phonemized, spans
    as they stand, spaces as written."""
    return phonemes.splice(script.spoken(cue), phonemize)


def _run(args):
    if args.lines:
        for given, flag in ((args.SCRIPT, "SCRIPT goes with a script's narration"),
                            (args.scenes, "--scenes goes with a script"),
                            (args.phonemes, "--phonemes goes with a script")):
            if given:
                raise cli.Failure(f"{flag}, not --lines", cli.USAGE)
        return _run_lines(args)
    if args.out is not None:
        raise cli.Failure("--out goes with --lines", cli.USAGE)
    if args.SCRIPT is None:
        raise cli.Failure("give the video's script.md, or --lines TABLE.md --out FOLDER", cli.USAGE)
    if args.phonemes and not args.dry_run:
        raise cli.Failure("--phonemes goes with --dry-run (it only shows what the voice would be given)", cli.USAGE)
    data = script.read(args.SCRIPT)
    settings = script.settings(data)
    conf = config.read()
    scenes = script.select(data, args.scenes)
    voice = args.voice or settings["voice"] or conf.get("VOICE", "")
    speed = args.speed if args.speed is not None else settings["speed"]
    model, voices = _model_dir(conf)
    folder = os.path.join(script.folder(args.SCRIPT), "work", "narration")
    timing_path = os.path.join(folder, "timing.json")
    cues = [(sc, cue) for sc in scenes for cue in sc["cues"]]
    if args.dry_run:
        phonemize = _phonemizer(settings["language"]) if args.phonemes else None   # before anything is printed
        print("narrate (dry run): {}".format(data["title"]))
        print(f"voice {voice}, speed {speed}, language {settings['language']}, model {settings['speech-model']} "
              f"from {os.path.dirname(model)}")
        words = 0
        for sc, cue in cues:
            n = len(script.spoken(cue).split())
            words += n
            print(f"{clip_name(sc, cue)}  ~{n / WORDS_PER_SECOND:.1f} s  {script.spoken(cue)}")
            if phonemize:
                print(f"    phonemes: {spoken_phonemes(cue, phonemize)}")
        print(f"{len(cues)} cues, about {round(words / WORDS_PER_SECOND)} s of speech; nothing written (dry run).")
        return cli.OK
    outputs = [os.path.join(folder, clip_name(sc, cue)) for sc, cue in cues] + [timing_path]
    existing = [p for p in outputs if os.path.lexists(p)]
    if existing and not args.replace:
        raise cli.Failure("these would be written over; delete them, or run with --replace:\n"
                          + "\n".join("  " + p for p in existing))
    cli.need("numpy")
    cli.need("soundfile")
    speech = _load_model(model, voices)
    available = sorted(speech.get_voices())
    if voice not in available:
        raise cli.Failure("the model has no voice '{}' (it has {})".format(voice, ", ".join(available)))
    if existing:
        print("Replacing:\n" + "\n".join("  " + p for p in existing))
    import numpy as np
    import soundfile
    timing = {"voice": voice, "speed": speed, "model": settings["speech-model"], "sample_rate": None, "scenes": {}}
    if args.replace and os.path.isfile(timing_path):
        with open(timing_path, encoding="utf-8") as f:
            timing["scenes"] = json.load(f).get("scenes", {})
    os.makedirs(folder, exist_ok=True)
    written = 0
    for sc in scenes:
        lengths = []
        for cue in sc["cues"]:
            try:
                if phonemes.has_span(script.spoken(cue)):
                    given = spoken_phonemes(cue, lambda text: speech.tokenizer.phonemize(text, settings["language"]))
                    samples, rate = speech.create(given, voice=voice, speed=speed, lang=settings["language"],
                                                  is_phonemes=True)
                else:
                    samples, rate = speech.create(script.spoken(cue), voice=voice, speed=speed,
                                                  lang=settings["language"])
            except Exception as e:  # the model's own errors are not ours to classify
                raise cli.Failure(f"the speech model failed on scene {sc['key']} cue {cue['n']} ({e}); "
                                  "nothing written for it", cli.EXTERNAL) from e
            samples = trim(np.asarray(samples, dtype=np.float32), rate)
            soundfile.write(os.path.join(folder, clip_name(sc, cue)), samples, rate)
            timing["sample_rate"] = rate
            length = round(len(samples) / rate, 3)
            lengths.append(length)
            written += 1
            print(f"{clip_name(sc, cue)}  {length:.3f} s", flush=True)
        timing["scenes"][sc["key"]] = lengths
        with open(timing_path, "w", encoding="utf-8") as f:
            json.dump(timing, f, indent=1)
    print(f"Wrote {written} clips and {timing_path}")
    return cli.OK



def _run_lines(args):
    """`narrate --lines TABLE.md --out FOLDER --speed S`: each line of the table to its own clip."""
    from videotools import lines as lines_
    if args.out is None:
        raise cli.Failure("--lines needs --out FOLDER for the clips", cli.USAGE)
    speed = lines_.check_speed(args.speed if args.speed is not None else LINES_SPEED)
    conf = config.read()
    voice = args.voice or conf.get("VOICE", "") or "af_heart"
    model, voices = _model_dir(conf)
    rows = lines_.read(args.lines)
    folder, timing_path = args.out, os.path.join(args.out, "timing.json")
    largest = max(line["n"] for line in rows)
    names = [lines_.clip_name(line["n"], largest) for line in rows]
    if args.dry_run:
        print(f"narrate (dry run): {args.lines}")
        print(f"voice {voice}, speed {speed}, model kokoro-82m from {os.path.dirname(model)}")
        total = 0.0
        for line, name in zip(rows, names):
            seconds = lines_.estimate(line["text"], speed)
            total += seconds
            print(f"{name}  at {line['start']:.2f} s  ~{seconds:.1f} s  {line['text']}")
        print(f"{len(rows)} lines, about {round(total)} s of speech; nothing written (dry run).")
        return cli.OK
    outputs = [os.path.join(folder, name) for name in names] + [timing_path]
    existing = [p for p in outputs if os.path.lexists(p)]
    if existing and not args.replace:
        raise cli.Failure("these would be written over; delete them, or run with --replace:\n"
                          + "\n".join("  " + p for p in existing))
    cli.need("numpy")
    cli.need("soundfile")
    speech = _load_model(model, voices)
    available = sorted(speech.get_voices())
    if voice not in available:
        raise cli.Failure("the model has no voice '{}' (it has {})".format(voice, ", ".join(available)))
    if existing:
        print("Replacing:\n" + "\n".join("  " + p for p in existing))
    import numpy as np
    import soundfile
    timing = {"voice": voice, "speed": speed, "model": "kokoro-82m", "sample_rate": None, "lines": []}
    os.makedirs(folder, exist_ok=True)
    spoken = []
    for i, (line, name) in enumerate(zip(rows, names)):
        try:
            samples, rate = speech.create(line["text"], voice=voice, speed=speed, lang="en-us")
        except Exception as e:  # the model's own errors are not ours to classify
            raise cli.Failure(f"the speech model failed on line {line['n']} ({e}); nothing written for it",
                              cli.EXTERNAL) from e
        samples = trim(np.asarray(samples, dtype=np.float32), rate)
        soundfile.write(os.path.join(folder, name), samples, rate)
        length = round(len(samples) / rate, 3)
        timing["sample_rate"] = rate
        timing["lines"].append({"n": line["n"], "start": line["start"], "text": line["text"], "length": length})
        with open(timing_path, "w", encoding="utf-8") as f:
            json.dump(timing, f, indent=1, ensure_ascii=False)
        print(f"{name}  {length:.3f} s", flush=True)
        spoken.append((line, length))
        warning = lines_.overrun(spoken + [(rows[i + 1], 0.0)] if i + 1 < len(rows) else spoken, i)
        if warning:
            print(f"{PROG}: {warning}", file=sys.stderr, flush=True)
    print(f"Wrote {len(rows)} clips and {timing_path}")
    return cli.OK
