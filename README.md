# video-tools

Command-line tools for making short narrated, animated training videos from a procedure
diagram: one scene per step, captions, common mistakes shown beside the right way, in a brand's
colours and fonts. A video is described by three Markdown files (its script, its brand kit and
the machine's config); the tools make the narration with a local speech model, time the scenes
from it, draw the frames, render and assemble the video, and check it. Written for the
training-video project (`~/projects/non-code/training-video/`) and anyone making the same kind of
video from Terminal on a Mac. Nothing leaves the machine: no service is called, nothing is
uploaded, and no command ever writes over an existing file.

**Status (9 October 2026):** `check-script`, `narrate`, `assemble`, `check-video`, `crop-insets`
and `font-weights` are built; `stills` and `render` (the drawing) are under way (see `PLAN.md`
for the full set and `DIARY.md` for where things stand).

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

### `crop-insets SCRIPT.md [--dry-run]`

Cuts each box in the script's `## Insets` table out of its `source-image`, scaled to fit the
reference column (388 px wide, 330 px tall, 360 for a box taller than it is wide), into the
video's `work/insets/<key>.png`, and the whole image at 750 px tall into
`work/insets/title-page.png` for the title card. Refuses a box outside the image or empty, an
inset called `title-page`, and any existing output. Prints each file with its size.

```
$ ./crop-insets examples/videos/paper-boat/script.md --dry-run
…/work/insets/A.png  388x167  (inset A, 1040x450 at 80 150)
…/work/insets/B.png  388x167  (inset B, 1040x450 at 80 660)
…/work/insets/C.png  388x145  (inset C, 1040x390 at 80 1170)
…/work/insets/full.png  248x360  (inset full, 1120x1620 at 40 40)
…/work/insets/title-page.png  529x750  (the whole page)
5 files; nothing written (dry run).
```

### `font-weights VARIABLE.ttf --weights 400,600,… --family-prefix PREFIX --out DIR`

cairo's simple text API cannot pick a weight from a variable font, so a brand kit names one
static file per weight. This makes them: for each weight (100–900 in hundreds) a static
instance renamed `PREFIX <Weight>` (`EBG SemiBold`; an italic font gives `EBG Italic`,
`EBG MediumItalic`, …), written to `DIR/PREFIX-<Weight>.ttf`. Refuses a font without a `wght`
axis, a weight outside its range, and any existing output. Checked against the brand's own
EB Garamond instances on 9 October 2026: names and glyph widths equal.

```
$ ./font-weights "EBGaramond[wght].ttf" --weights 400,500,600,700 --family-prefix EBG --out fonts
fonts/EBG-Regular.ttf  EBG Regular  (wght 400)
fonts/EBG-Medium.ttf  EBG Medium  (wght 500)
fonts/EBG-SemiBold.ttf  EBG SemiBold  (wght 600)
fonts/EBG-Bold.ttf  EBG Bold  (wght 700)
```

### `assemble SCRIPT.md [--out FILE] [--replace]`

Joins the rendered segments (`work/segments/<scene>_<frame>.mp4`) in script order with ffmpeg's
concat demuxer (streams copied), mixes every narration clip in at its scene's start plus its
cue's start plus 50 ms (resampled to 48 kHz, the mix peak-normalised to 0.89,
`work/assemble/narration.wav`), and muxes the two (AAC 160 kb/s, fast start) to the script's
`output` under the video's folder, or `--out`. Before writing anything it checks, and refuses
naming each: a scene with no segment, segments whose counted frames do not add up to the
scene's or do not chain from frame 0, a cue with no clip, a missing `timing.json`, an existing
output (never replaced), and existing intermediates in `work/assemble/` unless `--replace`.
ffmpeg's exit status is checked at both steps; on failure the partial file is named and left.
Ends by printing the length, size and SHA-256 of the output, for the diary.

### `check-video SCRIPT.md [VIDEO] [--sheet OUT.png]`

The same checks on every finished video (default: the script's `output`), against the script
and `timing.json`: length within one frame of the scenes' total; peak below 0 dBFS; silences
of 2 s or more (−40 dB) only outside the cues' windows, and narration heard in every cue; with
`--sheet`, one frame from the middle of each scene on a 1920×1080 sheet (refuses an existing
file). Prints a report line per check, then `No problems found.` (exit 0) or the problems
(exit 1).

```
$ ./check-video videos/x/script.md
videos/x/out/X.mp4
length 52.900 s; the script's scenes give 52.900 s: OK
peak -1.0 dBFS, mean -20.0 dBFS: OK
silences of 2 s or more: 1, at 47.200-52.900 (scene end, no cues): OK
narration in every cue's window: OK
No problems found.
```

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
| 1 | `check-script` / `check-video`: problems found, listed on stdout. | Fix the script, or the video. |
| 2 | Bad arguments, a `--scenes` key that is not in the script, a weight that is not 100–900. | See `--help`. |
| 3 | An input refuses: the script or brand kit is malformed or missing (every problem is listed), a file it names is missing, `SPEECH_MODEL_DIR` is not set or has no model, the voice is not in the voices file, timings or segments or clips are missing or do not add up, a crop box is outside the image, a weight is outside the font's axis, or an output already exists. Nothing is written. | Fix the input, delete the output, or use `--replace` where there is one. |
| 4 | A package (the speech packages, Pillow, fontTools) is not installed in the venv; ffmpeg or ffprobe is not on PATH; the speech model failed on a cue (named); ffmpeg failed (its output is shown and the partial file named). What was written before stays. | Install as above; re-run for the scene that failed. |

## Testing

```bash
.venv/bin/pytest          # the whole suite: no external programs, no network, no real data
.venv/bin/ruff check .    # lint
```

`tests/tier1/` tests pure functions (the readers, the timeline, trimming, the drawing
primitives, the camera); `tests/tier2/` runs each command as a subprocess against stubs
(`tests/stubs/`: a fake `kokoro_onnx` package, and `ffstub.py` standing in for `ffmpeg` and
`ffprobe` with fake media files) and a copy of the example. Coverage is reported by the test
command; 96% on 9 October 2026 (179 tests).

Tier 3, manual, with the real programs, on a *copy* of the example (never the one in the
repository): `./narrate COPY/script.md --dry-run`, then a real run, then a second run (it must
refuse); `./crop-insets COPY/script.md`; `./font-weights` on a real variable font into a scratch
folder. Done and recorded in `DIARY.md` on 9 October 2026. `assemble` and `check-video` wait for
`render`.

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
- 9 October 2026: `assemble`, `check-video`, `crop-insets` and `font-weights` added. Unlike the
  prototype, nothing writes over an existing file, ffmpeg's failures are reported, and clips of
  any sample rate are placed correctly. The whole-page image for the title card is
  `work/insets/title-page.png`; the italic at weight 400 is named `PREFIX Italic`.

## Contributing

Dev tooling: `.venv/bin/pip install -r requirements-dev.txt` into the same `.venv`, then
`.venv/bin/pytest` and `.venv/bin/ruff check .`. How the work is done is in `CLAUDE.md`; what is
built, and in what order, is in `PLAN.md`; where things stand, in `DIARY.md`.
