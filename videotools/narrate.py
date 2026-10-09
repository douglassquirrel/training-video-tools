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

from videotools import cli, config, script

PROG = "narrate"
WORDS_PER_SECOND = 2.6
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
    p.add_argument("SCRIPT", help="the video's script.md")
    p.add_argument("--scenes", metavar="KEY,...", help="only these scenes (keys as in the script)")
    p.add_argument("--voice", help="the voice, e.g. af_heart (default: the script's)")
    p.add_argument("--speed", type=float, help="the speed, e.g. 0.98 (default: the script's)")
    p.add_argument("--replace", action="store_true",
                   help="write over existing clips and timing.json, listing them first")
    p.add_argument("--dry-run", action="store_true",
                   help="list the cues, the voice and an estimate of each clip; write nothing")
    return p


def clip_name(scene, cue):
    return "%s_%02d.wav" % (scene["key"], cue["n"])


def _scenes(data, keys):
    """The scenes to narrate: all, or those named in --scenes (refused if one does not exist)."""
    if not keys:
        return data["scenes"]
    by_key = {s["key"]: s for s in data["scenes"]}
    wanted = [k.strip() for k in keys.split(",") if k.strip()]
    for k in wanted:
        if k not in by_key:
            raise cli.Failure("no scene '%s' in the script (scenes: %s)" % (k, ", ".join(by_key)), cli.USAGE)
    return [by_key[k] for k in wanted]


def _model_dir(conf):
    """The folder holding model.onnx and voices.npz, from SPEECH_MODEL_DIR."""
    folder = conf.get("SPEECH_MODEL_DIR")
    if not folder:
        raise cli.Failure("SPEECH_MODEL_DIR is not set in %s; see the README's one-time set-up" % config.path())
    model, voices = os.path.join(folder, "model.onnx"), os.path.join(folder, "voices.npz")
    if not (os.path.isfile(model) and os.path.isfile(voices)):
        raise cli.Failure("no model.onnx and voices.npz in %s (SPEECH_MODEL_DIR in %s); "
                          "see the README's one-time set-up" % (folder, config.path()))
    return model, voices


def _load_model(model, voices):
    try:
        from kokoro_onnx import Kokoro
    except ImportError as e:
        raise cli.Failure("the speech packages are not installed in this Python (%s); install them "
                          "into the venv as the README says" % e, cli.EXTERNAL)
    return Kokoro(model, voices)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return _run(args)
    except (cli.Failure, script.ScriptError, config.ConfigError) as f:
        return cli.report(PROG, cli.Failure(str(f), getattr(f, "code", cli.REFUSED)))


def _run(args):
    data = script.read(args.SCRIPT)
    settings = script.settings(data)
    conf = config.read()
    scenes = _scenes(data, args.scenes)
    voice = args.voice or settings["voice"] or conf.get("VOICE", "")
    speed = args.speed if args.speed is not None else settings["speed"]
    model, voices = _model_dir(conf)
    folder = os.path.join(script.folder(args.SCRIPT), "work", "narration")
    timing_path = os.path.join(folder, "timing.json")
    cues = [(sc, cue) for sc in scenes for cue in sc["cues"]]
    if args.dry_run:
        print("narrate (dry run): %s" % data["title"])
        print("voice %s, speed %s, language %s, model %s from %s"
              % (voice, speed, settings["language"], settings["speech-model"], os.path.dirname(model)))
        words = 0
        for sc, cue in cues:
            n = len(script.spoken(cue).split())
            words += n
            print("%s  ~%.1f s  %s" % (clip_name(sc, cue), n / WORDS_PER_SECOND, script.spoken(cue)))
        print("%d cues, about %d s of speech; nothing written (dry run)." % (len(cues), round(words / WORDS_PER_SECOND)))
        return cli.OK
    outputs = [os.path.join(folder, clip_name(sc, cue)) for sc, cue in cues] + [timing_path]
    existing = [p for p in outputs if os.path.lexists(p)]
    if existing and not args.replace:
        raise cli.Failure("these would be written over; delete them, or run with --replace:\n"
                          + "\n".join("  " + p for p in existing))
    speech = _load_model(model, voices)
    available = sorted(speech.get_voices())
    if voice not in available:
        raise cli.Failure("the model has no voice '%s' (it has %s)" % (voice, ", ".join(available)))
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
                samples, rate = speech.create(script.spoken(cue), voice=voice, speed=speed, lang=settings["language"])
            except Exception as e:  # the model's own errors are not ours to classify
                raise cli.Failure("the speech model failed on scene %s cue %d (%s); nothing written for it"
                                  % (sc["key"], cue["n"], e), cli.EXTERNAL)
            samples = trim(np.asarray(samples, dtype=np.float32), rate)
            soundfile.write(os.path.join(folder, clip_name(sc, cue)), samples, rate)
            timing["sample_rate"] = rate
            length = round(len(samples) / rate, 3)
            lengths.append(length)
            written += 1
            print("%s  %.3f s" % (clip_name(sc, cue), length), flush=True)
        timing["scenes"][sc["key"]] = lengths
        with open(timing_path, "w", encoding="utf-8") as f:
            json.dump(timing, f, indent=1)
    print("Wrote %d clips and %s" % (written, timing_path))
    return cli.OK
