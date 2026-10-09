# video-tools

Command-line tools for making short narrated, animated training videos from a procedure
diagram: one scene per step, captions, common mistakes shown beside the right way, in a brand's
colours and fonts. A video is described by three Markdown files (its script, its brand kit and
the machine's config); the tools make the narration with a local speech model, time the scenes
from it, draw the frames, render and assemble the video, and check it. Written for the
training-video project (`~/projects/non-code/training-video/`) and anyone making the same kind of
video from Terminal on a Mac. Nothing leaves the machine: no service is called, nothing is
uploaded, and no command ever writes over an existing file.

**Status (9 October 2026):** `check-script` and `narrate` are built; the rest is under way (see
`PLAN.md` for the full set and `DIARY.md` for where things stand).

## Requirements

- macOS on Apple silicon (checked on macOS 26.6; Intel should work but is unchecked) with
  [Homebrew](https://brew.sh).
- Homebrew's `python@3.12` (the speech packages need Python 3.10–3.13; the Mac's own
  `/usr/bin/python3` is 3.9 and runs only `check-script`), `cairo`, `pkgconf` and `ffmpeg`.
- The Kokoro-82M speech model, about 327 MB, in `~/models/kokoro/` (one-time set-up below).
- `~/.video-tools.conf` naming the model's folder.

## Installation

Paste into Terminal, from the folder you keep code in:

```bash
brew install python@3.12 cairo pkgconf ffmpeg
git clone git@github.com:douglassquirrel/video-tools.git
cd video-tools
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install pycairo numpy soundfile "kokoro-onnx==0.6.1" Pillow fonttools
```

The commands (`./check-script`, `./narrate`, …) find that `.venv` themselves, whichever
`python3` your shell has; nothing is installed outside the folder. Then the speech model:

### One-time set-up of the speech model

These are the only steps that use the network. Run once per machine.

1. The model and the voices, into `~/models/kokoro/`:

   ```bash
   mkdir -p ~/models/kokoro && cd ~/models/kokoro
   base=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
   curl -L -C - -o model.onnx "$base/onnx/model.onnx"
   for v in af_heart bm_george am_michael bf_emma; do curl -L -o "$v.bin" "$base/voices/$v.bin"; done
   ```

   (`-C -` resumes an interrupted download.) Expected: `model.onnx` 325,532,232 bytes, md5
   `0a08987b47a82ad0a67a1d92f66d95db`; each voice 522,240 bytes.

2. The single voices file kokoro-onnx wants, from the per-voice files (no network; run from
   `~/models/kokoro` with the venv's Python):

   ```bash
   ~/projects/code/video-tools/.venv/bin/python -c "import numpy as np, glob, os
   v={os.path.basename(f)[:-4]: np.fromfile(f, dtype=np.float32).reshape(-1,1,256) for f in glob.glob('*.bin')}
   np.savez(open('voices.npz','wb'), **v); print(sorted(v))"
   ```

3. Tell the tools where it is, in `~/.video-tools.conf` (copy `video-tools.conf.example`):

   ```
   SPEECH_MODEL_DIR=~/models/kokoro
   ```

4. Check: `./narrate examples/videos/paper-boat/script.md --dry-run` names the model and the
   voice (see Quick start), and a real run on a copy of the example speaks.

## Quick start

The example video, `examples/videos/paper-boat/` (an invented subject and brand), is there to
try every command on. Each command takes the video's `script.md`.

```
$ ./check-script examples/videos/paper-boat/script.md
Folding a Paper Boat: 7 scenes, 11 cues, 125 words (about 48 s of speech at 2.6 words a second)
Tracker: A B C
Mistakes:
  A cue 2: Folded corner to corner / Folded edge to edge
Beyond the source (added:), 4, for approval and checking:
  A, cue 2: "Don't fold it corner to corner. A diagonal fold leaves no hull to open."
      -> the consequence (no hull) is our inference; the figure shows only the edge fold.
  R, cue 2: "Edges even, creases sharp, and a hull that opens. That's a boat that floats."
      -> "a boat that floats" is our framing; the figure says nothing about water.
  A, side panel: "Crease firmly"
      -> the figure's closing note.
  A, on screen: "diagonal fold"
      -> as cue 2.

No problems found.
```

```
$ ./narrate examples/videos/paper-boat/script.md --dry-run
narrate (dry run): Folding a Paper Boat
voice af_heart, speed 0.98, language en-us, model kokoro-82m from /Users/you/models/kokoro
title_01.wav  ~2.7 s  Folding a paper boat, the Paperboat way.
title_02.wav  ~3.8 s  This film follows Figure seven, one fold at a time.
A_01.wav  ~4.6 s  Step A. Fold the sheet in half, top edge to bottom edge.
…
R_02.wav  ~5.4 s  Edges even, creases sharp, and a hull that opens. That's a boat that floats.
11 cues, about 48 s of speech; nothing written (dry run).
```

A real run (`./narrate …` without `--dry-run`) writes the clips and `timing.json` into the
video's `work/narration/`; on the example it took about 10 s and printed each clip's length
(`title_01.wav  2.314 s`, …). Try it on a copy of the example rather than the one in the
repository.

## Usage

### `check-script SCRIPT.md [--json OUT.json]`

Reads a video's `script.md` (the format is the training-video project's
`videos/SCRIPT-FORMAT.md`), checks it, and prints a summary: scenes, cues, words and an estimate
of the speech, the tracker's letters, every mistake, and every line marked `added:` (what goes
beyond the source, for approval). Then either `No problems found.` or the problems, one per line,
each naming its line in the script where there is one. `--json OUT` also writes the parsed
script as JSON; it refuses to write over an existing file. Needs only Python 3.9's standard
library, so it also runs as `/usr/bin/python3 check-script …`.

### `narrate SCRIPT.md [--scenes KEY,…] [--voice V] [--speed S] [--replace] [--dry-run]`

Speaks every cue (its `say:` line if it has one, else its caption) with the local speech model,
one clip per cue, trimmed to 30 ms before the first and 80 ms after the last sound, and writes:

- `work/narration/<scene>_<NN>.wav` under the video's folder, NN the cue's number in the script;
- `work/narration/timing.json`: the voice, speed, model and sample rate used, and each scene's
  clip lengths in seconds, which time everything that follows.

The voice, speed and language come from the script's Settings; `--voice` and `--speed` win over
the script; `~/.video-tools.conf`'s `VOICE` and `SPEED` are defaults for a script that does not
set them (the format requires both, so they rarely apply). `--scenes A,B` does only those scenes
and keeps the other scenes' entries in an existing `timing.json` (with `--replace`). Nothing is
written over an existing clip or timing file: the command refuses, listing them; `--replace`
writes over them, listing them first. `--dry-run` lists every cue with the voice and an
estimate of its length (2.6 words a second) and writes nothing. The clips are written as the
model makes them (24 kHz for Kokoro), one at a time, and `timing.json` is rewritten after each
scene, so an interrupted run keeps what it did.

### Configuration: `~/.video-tools.conf`

`KEY=value` lines, `#` comments, optional quotes, `~` for your home folder; read, never run.
`VIDEO_TOOLS_CONF` in the environment names another file. The settings:

| Key | Meaning |
|---|---|
| `SPEECH_MODEL_DIR` | The folder holding `model.onnx` and `voices.npz`. Required by `narrate`. |
| `VOICE`, `SPEED` | Defaults for a script that does not set its own. |

## Errors and exit codes

Every command prints errors in words on stderr (never a traceback) and exits:

| Code | Meaning | What to do |
|---|---|---|
| 0 | Success; with `--dry-run`, everything checked and nothing written. For `check-script`, no problems. | |
| 1 | `check-script`: problems found, listed on stdout. | Fix the script. |
| 2 | Bad arguments, or a `--scenes` key that is not in the script. | See `--help`. |
| 3 | An input refuses: the script or brand kit is malformed or missing (every problem is listed), a file it names is missing, `SPEECH_MODEL_DIR` is not set or has no model, the voice is not in the voices file, or an output already exists. Nothing is written. | Fix the input, delete the output, or use `--replace`. |
| 4 | The speech packages are not installed in the venv, or the speech model failed on a cue (named). What was written before stays. | Install as above; re-run with `--scenes` for the scene that failed. |

## Testing

```bash
.venv/bin/pytest          # the whole suite: no external programs, no network, no real data
.venv/bin/ruff check .    # lint
```

`tests/tier1/` tests pure functions (the readers, the timeline, trimming); `tests/tier2/` runs
each command as a subprocess against stubs (`tests/stubs/`: a fake `kokoro_onnx` package; stub
`ffmpeg` and `ffprobe` to come) and a copy of the example. Coverage is reported by the test
command; 99% on 9 October 2026 (113 tests).

Tier 3, manual, with the real programs, on a *copy* of the example (never the one in the
repository): `./narrate COPY/script.md --dry-run`, then a real run, then a second run (it must
refuse). Done and recorded in `DIARY.md` on 9 October 2026.

## Known limitations and non-goals

- Only one frame size, 1920×1080, and only the Kokoro model through kokoro-onnx.
- No network use at run time: no cloud speech, no fetching of models or brand assets.
- No timeline editing and no graphical interface; no slide decks.
- Anything particular to one video (its drawing, narration, sources) belongs in that video's
  folder, not here.

## Notes for users

- 9 October 2026: repository created. `check-script` (replaces the training-video project's
  `tools/script-check.py`, same output) and `narrate` are the first commands. Clips are numbered
  from `01` as the script numbers cues (the prototype's were from `00`), and `timing.json` lives
  in `work/narration/` with a `scenes` map rather than at the top level.

## Contributing

Dev tooling: `.venv/bin/pip install -r requirements-dev.txt` into the same `.venv`, then
`.venv/bin/pytest` and `.venv/bin/ruff check .`. How the work is done is in `CLAUDE.md`; what is
built, and in what order, is in `PLAN.md`; where things stand, in `DIARY.md`.
