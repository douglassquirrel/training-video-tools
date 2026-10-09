# video-tools

Command-line tools for making short narrated, animated training videos from a procedure
diagram: one scene per step, captions, common mistakes shown beside the right way, in a brand's
colours and fonts. A video is described by three Markdown files (its script, its brand kit and
the machine's config); the tools make the narration with a local speech model, time the scenes
from it, draw the frames, render and assemble the video, and check it. Written for the
training-video project (`~/projects/non-code/training-video/`) and anyone making the same kind of
video from Terminal on a Mac. Nothing leaves the machine: no service is called, nothing is
uploaded, and no command ever writes over an existing file.

**Status (9 October 2026):** all eight commands are built and the whole chain has made the
example video for real (`DIARY.md`, "Tier 3"). The order of a run: `check-script`, `crop-insets`,
`narrate`, `stills` (to look), `render`, `assemble`, `check-video`. Three of four checking
commands are added, `frame-hashes`, `compare-video` and `compare-frames` (`brand-preview` is in
PLAN.md item 11 and not built yet).

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

### Running from the Linux device shell

Where the checkout is shared with a Linux machine (Claude's device shell sees this folder over a
mount), the repository's `.venv` is the Mac's and cannot run there. Make a venv *outside* the
repository, once, and name its Python in `VIDEO_TOOLS_PYTHON`; every command restarts itself
under it:

```bash
python3 -m venv --system-site-packages /tmp/work-$(id -u)/venv
/tmp/work-$(id -u)/venv/bin/pip install pycairo numpy soundfile "kokoro-onnx==0.6.1" Pillow fonttools
export VIDEO_TOOLS_PYTHON=/tmp/work-$(id -u)/venv/bin/python
./check-script videos/make-bed/script.md
```

Never build that venv inside the repository from Linux (it would shadow the Mac's). With
`VIDEO_TOOLS_PYTHON` unset the commands use `.venv` as above; a path that does not exist is
refused with exit 3.

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
repository. Then, on that copy:

```
$ ./crop-insets COPY/script.md
…/work/insets/A.png  388x167  (inset A, 1040x450 at 80 150)
…
Wrote 5 files to …/work/insets

$ ./stills COPY/script.md "title:3.0,A:2.0,B:4.0,R:6.0" --out sheet.png
title at 3.000 s (of 8.333 s, cue 1)
A at 2.000 s (of 10.500 s, cue 1)
B at 4.000 s (of 10.000 s, cue 1)
R at 6.000 s (of 8.967 s, cue 2)
Wrote sheet.png: 4 frames, 2x2

$ ./render COPY/script.md --dry-run
title  8.333 s  250 frames  -> …/work/segments/title_00000.mp4
A  10.500 s  315 frames  -> …/work/segments/A_00000.mp4
…
7 scenes, 60.067 s, 1802 frames; nothing written (dry run).

$ ./render COPY/script.md
title  8.333 s  250 frames
Rendered title: 250 frames in 1.3 s (190.2 frames/s) -> …/work/segments/title_00000.mp4
…
Rendered end: 171 frames in 0.8 s (205.9 frames/s) -> …/work/segments/end_00000.mp4

$ ./assemble COPY/script.md
Narration mixed: 60.067 s to …/work/assemble/narration.wav
Segments joined to …/work/assemble/video-only.mp4
Wrote …/out/Folding a Paper Boat.mp4
length 60.067 s (1802 frames), size 2546758 bytes
sha256 dcee4bb1adbd11215f8e7fb288572524b234764c30c593959396274539b0211b

$ ./check-video COPY/script.md --sheet check.png
…/out/Folding a Paper Boat.mp4
length 60.067 s; the script's scenes give 60.067 s: OK
peak -1.0 dBFS, mean -21.9 dBFS: OK
silences of 2 s or more: 6, at 6.782-9.109 (between cues), … 52.799-60.067 (scene end, no cues): OK
narration in every cue's window: OK
sheet of 7 frames written to check.png
No problems found.
```

(On this Mac, 9 October 2026: the whole example, 60 s of video, in under a minute.)

## Usage

### `check-script SCRIPT.md [--json OUT.json]`

Reads a video's `script.md` (the format is the training-video project's
`videos/SCRIPT-FORMAT.md`), checks it, and prints a summary: scenes, cues, words and an estimate
of the speech, the tracker's letters, every mistake, and every line marked `added:` (what goes
beyond the source, for approval). Then either `No problems found.` or the problems, one per line,
each naming its line in the script where there is one. It also reads the brand kit the script
names and lists the kit's problems, each prefixed with the `BRAND.md` path, and checks the scene
code without running it: a step scene with no `code`, a module that is missing or does not
parse, and a module without a top-level `def` of a function the scene needs (`draw`; `mistake`
and `right_way` for a mistake cue; `panel` for a custom side panel). So anything `stills` or
`render` would refuse is found here first. (A function a module gets any other way than its own
`def`, say by import, is reported as missing.) `--json OUT` also writes the parsed
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

### `stills SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]`

Draws the frames at the given times (a negative time counts back from the scene's end) onto
one 1920×1080 sheet, `--grid` columns by rows (default `2x2`; more frames than cells is
refused), each with its scene, time and cue in a grey strip under the frame, so no part of the
frame (the header above all) is covered. This is how a scene's layout is checked
before rendering. It needs the insets (`crop-insets`) and, for exact times, the narration; with
no clips it estimates the timing at 2.6 words a second and says so on stderr. Refuses an
existing sheet and a time past the scene's end.

### `render SCRIPT.md [--scenes KEY,…] [--frames A-B] [--replace] [--dry-run]`

Draws every frame of each scene (all, or `--scenes`) and pipes them to ffmpeg as raw BGRA
(`libx264`, the script's `quality` as CRF, `veryfast`, `yuv420p`, the script's `fps`) into
`work/segments/<scene>_<first frame>.mp4`. `--frames 100-130` renders that range of the one
scene named, into `<scene>_00100.mp4`. Refuses without a complete `timing.json` (timings are
never estimated for a render), and an existing segment unless `--replace` (listed first; ffmpeg
is then allowed to write over those segments only).
After each segment, ffmpeg's exit status is checked and the segment's frames counted; a
failure names the partial file and leaves it (exit 4). Prints each scene's progress and the
frames a second achieved. `--dry-run` lists the scenes, lengths, frame counts and segment
names and writes nothing.

### Writing a video's scene code

A video's own drawing lives in the folder its script's `scene-code` names, one Python module
per scene, named by the scene's `code` property (`examples/videos/paper-boat/scenes/` is the
worked example; its README has the details). A title or end card needs none: the chrome draws
the whole card, and a card that names a `code` has that module's `draw` add to it. A module
defines:

- `draw(frame)`: the animation area, every scene;
- `mistake(frame, rect)` and `right_way(frame, rect)`: the two panel bodies, for a scene whose
  narration has a `mistake:` cue;
- `panel(frame, rect)`: the side panel, for a scene whose `side-panel` is `custom <name> N`.

`frame` carries `ctx` (the cairo context, clipped to the area), `t` (seconds into the scene),
`timeline` (`p(t, cue, a, b)` for eased progress between two offsets from a cue's start, `cue(t)`
for the cue speaking now, `start(cue)`, `length(cue)`, `total`), `scene` (its data from the
script), `colours` (the script's Colours as red-green-blue triples in 0–1), `brand` (the kit:
`colours`, `fonts`, `settings`), `area` (its rectangle) and `label(text)`, which returns the
text after checking it is in the scene's "On screen" list and stops the run with a message if
it is not. A scene's `side-panel-heading` property puts a small heading above a `steps` or
`checklist` panel, or in place of KEY POINTS.

Draw words and pills through the frame, which fills in what the brand and script already say
(the font by role, the size multiplied by the brand's `font-size-scale`, colours by name, the
brand's rule 3 that accent below the small-text size becomes the darker role, for text and for a
pill's fill alike, and the On screen check on every label):

| Method | What it draws |
|---|---|
| `frame.colour(name)` | An (r, g, b): the script's Colours first (`paper`), then the brand's roles (`accent`); an unknown name stops the run listing both. |
| `frame.text(s, x, y, size, role="body", colour="ink", anchor="l", alpha=1.0, track=0, check=False)` | Text; `check=True` runs it through `label` (words on screen that are not pills). Font roles: `display`, `display-medium`, `body`, `body-medium`, `bold`, `italic`, `italic-medium`. |
| `frame.tag(s, x, y, size=22, fill="ink", colour="on-accent", role="display", anchor="l", alpha=1.0, padx=14, pady=9, border=None)` | A pill label, always checked. Returns the pill's rectangle. |
| `frame.callout(s, target, at, size=22, leader="ink", fill="surface", colour="ink", role="display", anchor="l", alpha=1.0)` | A checked pill at `at` with a leader line to a dot at `target`. |
| `frame.dimension(p0, p1, s, size=24, colour="accent", text_colour="on-accent", role="display", side=1, alpha=1.0)` | A dimension line with its (checked) measurement in a pill beside it. |
| `frame.badge(x, y, ok, r=24, alpha=1.0)` | A ✓ or ✗ in the brand's `correct` or `mistake` colour with its `on-accent` mark. |
| `frame.hand(x, y, angle, scale, alpha=1.0, mirror=False, label=None)` | A mitten hand in the script's `skin`, `skin-dark` and `sleeve` colours when it names them, else a neutral skin, its darker outline and a slate sleeve; the letter label in the display font on an accent roundel at 28 px scaled. |

Shapes stay in `videotools.draw` (`poly`, `line`, `circle`, `fill_rrect`, `arrow`, `bezier`,
`cut`, shading) with explicit colour triples, which `frame.colour` supplies, and the oblique 3D
view in `videotools.camera` (`Camera`, `between`, `front`, `top`, `end`, with `ripple` and `clip`
for cloth and paper). Import the primitives as `d` (`from videotools import draw as d`), since
the module's own function is called `draw`. The example's `_sheet.py` shows both styles.

### `assemble SCRIPT.md [--out FILE] [--replace]`

Joins the rendered segments (`work/segments/<scene>_<frame>.mp4`) in script order with ffmpeg's
concat demuxer (streams copied), mixes every narration clip in at its scene's start plus its
cue's start plus 50 ms (resampled to 48 kHz, the mix peak-normalised to 0.89,
`work/assemble/narration.wav`), and muxes the two (AAC 160 kb/s, fast start) to the script's
`output` under the video's folder, or `--out`. Before writing anything it checks, and refuses
naming each: a scene with no segment, segments whose counted frames do not add up to the
scene's or do not chain from frame 0, a cue with no clip, a missing `timing.json`, an existing
output (never replaced), and existing intermediates in `work/assemble/` unless `--replace`,
which lets ffmpeg write over the intermediates it listed and nothing else.
ffmpeg's exit status is checked at both steps; on failure the partial file is named and left.
Ends by printing the length, size and SHA-256 of the output, for the diary.

### `check-video SCRIPT.md [VIDEO] [--sheet OUT.png]`

The same checks on every finished video (default: the script's `output`), against the script
and `timing.json`: length within one frame of the scenes' total; peak below 0 dBFS; silences
of 2 s or more (−40 dB) only outside the cues' windows, and narration heard in every cue; with
`--sheet`, one frame from the middle of each scene on a 1920×1080 sheet, each labelled in a
strip under the frame as `stills` does, in the brand's display font (refuses an existing
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

### `frame-hashes SCRIPT.md (--out HASHES.json [--merge] | --compare HASHES.json) [--scenes KEY,…] [--step N]`

Proof that a change (to scene code, a brand kit, or video-tools itself) changes no pixel of a
video, or exactly which frames it changes, without rendering: every N-th frame of each scene
(default every one) is drawn as `render` draws it and the MD5 of its pixels recorded by scene
and frame number. `--out` writes the record (`{"<scene>": {"<frame>": "<md5>"}}`) and refuses an
existing file unless `--merge`, which keeps the file's other scenes and replaces the ones hashed
now. `--compare` draws the same frames again and reports, per scene, `all match` or how many
differ with the first twelve frame numbers, and how many are not in the record at all (they
count as differing); then `All frames match.` (exit 0) or `N frames differ.` (exit 1). Needs
complete timings, as `render` does, and pycairo; no ffmpeg. Hash the example (or a video) before
a change and compare after it.

```
$ ./frame-hashes COPY/script.md --out before.json
title      250 frames in   3.2 s
…
end        171 frames in   1.8 s
Wrote before.json: 1802 frames, 7 scenes

$ ./frame-hashes COPY/script.md --compare before.json --step 10      # after changing one colour
title       25 frames in   0.3 s: all match
…
R           27 frames in   0.3 s: 26 differ (frames 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, …)
end         18 frames in   0.2 s: all match
26 frames differ.
```

### `compare-video NEW.mp4 OLD.mp4 [--every SECONDS] [--sheet OUT.png]`

The acceptance of a re-made or revised video: two finished files compared and reported, never
judged (exit 0 whenever it runs; a remake that is meant to differ still compares). For each
file, the length, frame count, peak and mean level; then the narration envelopes (each file's
audio decoded to 48 kHz mono, the RMS of every 0.1 s window), their correlation over the shorter
file (`undefined` when one is flat), and the windows that are speech (above −40 dBFS) in one and
silence in the other; then one frame from each file every `--every` seconds (default 5) and the
mean absolute difference of the pair over RGB, 0 to 255: the mean, the median and the five largest
with their times. With `--sheet`, those five pairs side by side, new left, old right, each
labelled under the frame (refuses an existing file). Needs ffmpeg, ffprobe and numpy, and Pillow
for the sheet.

```
$ ./compare-video videos/x/out/X-v2.mp4 videos/x/out/X.mp4 --every 2 --sheet compare.png
NEW videos/x/out/X-v2.mp4
  length 60.067 s, 1802 frames; peak -1.0 dBFS, mean -21.9 dBFS
OLD videos/x/out/X.mp4
  length 60.067 s, 1802 frames; peak -1.0 dBFS, mean -21.9 dBFS
narration envelopes (0.1 s windows, 600 compared): correlation 1.0000; speech in one and silence in the other: 0 windows
frames every 2 s (31 pairs): mean difference 3.0, median 0.0 (0-255)
  largest: 18.9 at 46.0 s, 18.9 at 48.0 s, 18.9 at 50.0 s, 18.9 at 52.0 s, 18.4 at 54.0 s
sheet of 5 pairs written to compare.png
```

(That run: the example re-made with one colour changed in its last step scene; the five largest
differences are all in that scene, and the sheet shows the colour.)

### `compare-frames SCRIPT.md OLD.mp4 SCENE:SECONDS[,…] --out SHEET.png [--offset SCENE=SECONDS …]`

For a remake or a revision: the frame the scene code draws now beside an earlier video's frame
at the same moment, with a number for how different they are. Times are read as `stills` reads
them (a negative time counts back from the scene's end; a time past the end is refused, exit 2).
The old video's moment is the scene's start plus the time, the start being the sum of the
earlier scenes' lengths from the current `timing.json`; `--offset SCENE=SECONDS` moves one
scene's start when the old video's differs (repeatable). Each pair goes on a row of the sheet,
new left, old right, labelled under each frame in the brand's display font with the mean
absolute RGB difference (0–255), which is printed too. Refuses an existing sheet, a moment past
the old video's end (by name, before any frame is read), and missing timings as `render` does.
Needs pycairo, numpy, Pillow and ffmpeg. A pair of the same video differs by about 1 (H.264);
a changed colour over a sixth of the frame by about 20.

```
$ ./compare-frames COPY/script.md COPY/out/earlier.mp4 "A:5,R:3,R:-1" --out compare.png
A           5.00 s  old   13.33 s  mean difference   0.8
R           3.00 s  old   48.40 s  mean difference  19.5
R           7.97 s  old   53.37 s  mean difference  19.4
Wrote compare.png: 3 pairs
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
| 1 | `check-script` / `check-video`: problems found, listed on stdout; `frame-hashes --compare`: frames differ, listed on stdout. | Fix the script, or the video; or look at the frames that changed. |
| 2 | Bad arguments, a `--scenes` key that is not in the script, a weight that is not 100–900, a `SCENE:SECONDS` past the scene's end. | See `--help`. |
| 3 | An input refuses: the script or brand kit is malformed or missing (every problem is listed), a file it names is missing, `SPEECH_MODEL_DIR` is not set or has no model, the voice is not in the voices file, timings or segments or clips are missing or do not add up, a crop box is outside the image, a weight is outside the font's axis, or an output already exists. Nothing is written. | Fix the input, delete the output, or use `--replace` where there is one. |
| 4 | A package (pycairo, numpy, soundfile, Pillow, fontTools, kokoro-onnx) is not installed in the Python running the command: one line names the package, its `pip install` line and, when `VIDEO_TOOLS_PYTHON` is unset, the device-shell set-up; ffmpeg or ffprobe is not on PATH; the speech model failed on a cue (named); ffmpeg failed (its output is shown and the partial file named). What was written before stays. | Install as above; re-run for the scene that failed. |

## Testing

```bash
.venv/bin/pytest          # the whole suite: no external programs, no network, no real data
.venv/bin/ruff check .    # lint

In the Linux device shell, where deleting is off and old `pytest-of-…` folders cannot be cleared,
give pytest a fresh temporary folder that has no `brands/` folder above it:
`pytest --basetemp=/tmp/work-$(id -u)/pytest-$(date +%s)`.
```

The tests hand every command a clean environment: `VIDEO_TOOLS_PYTHON`, `VIDEO_TOOLS_CONF` and
`FONTCONFIG_FILE` are dropped unless a test sets them on purpose, so the suite passes with the
device-shell settings exported.

`tests/tier1/` tests pure functions (the readers, the timeline, trimming, the drawing
primitives, the camera, the chrome's rules, the scene loader); `tests/tier2/` runs each command
as a subprocess against stubs (`tests/stubs/`: a fake `kokoro_onnx` package, and `ffstub.py`
standing in for `ffmpeg` and `ffprobe` with fake media files) and a copy of the example, and
draws whole frames of the example to compare with stored images (`tests/tier2/frames/`, at
192×108 with a tolerance). Coverage is reported by the test command; 98% on 9 October 2026
(330 tests, lint clean).

Tier 3, manual, with the real programs, on a *copy* of the example (never the one in the
repository): the whole chain in the Quick start above, plus a second `narrate` run (it must
refuse) and `font-weights` on a real variable font into a scratch folder. Done and recorded in
`DIARY.md` on 9 October 2026, on macOS. On Linux (the device shell, 9 October 2026, reported by
the training-video project, recorded in PLAN.md "Things checked" 5): the suite passes with the
one CoreText test skipped, the fonts draw through fontconfig, and the example's chain runs
with ffmpeg 4.4.

## Known limitations and non-goals

- Only one frame size, 1920×1080 (every region is named in one place, `chrome.Layout`, so a
  second size can come later), and only the Kokoro model through kokoro-onnx.
- Fonts are found through CoreText on macOS and fontconfig elsewhere (run on Linux once, by
  the training-video project, not from here).
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
- 9 October 2026 (evening): a brand kit's `BRAND.md` may hold other tables under the read
  headings (a contrast table under Colours, say): only a table whose header row begins
  `| Key | Value |` is read. `check-script` now checks the brand kit too. A malformed kit is
  reported in words with exit 3 by every command. `stills` puts each label in a strip under
  its frame instead of over its corner. `VIDEO_TOOLS_PYTHON` names the Python the commands run
  under (for the Linux device shell, above). `videotools.camera` gains the prototype's `ripple`
  (a wavy edge) and `clip` (a polygon cut to one side of a line) for cloth and paper.
- 9 October 2026 (later): `assemble --replace` and `render --replace` now work with the real
  ffmpeg (it was asked to write over the listed files without `-y`, and gave up); every ffmpeg
  call carries `-nostdin`, so it can never stop to ask. A package the command needs but its
  Python lacks is one line naming the package and the install (it was a traceback for numpy,
  soundfile and pycairo).
- 9 October 2026 (evening, after the bed video's re-make): a scene may set
  `side-panel-heading` (a heading above a `steps` or `checklist` panel, or instead of KEY
  POINTS; a problem with `none` or `custom`); `draw.hand` takes `label_size` (default 28, the
  roundel scales with it), so scene code can pass the brand-scaled size.
- 9 October 2026 (late): `frame-hashes`, `compare-video` and `compare-frames` added, three of
  four checking commands requested by the training-video project. `frame-hashes` and
  `compare-frames` replace that project's `tools/frame-hashes.py` and `tools/compare-frames.py`
  with the same output; `frame-hashes --compare` exits 1 when frames differ; `compare-video`
  keeps the comparison that was run by hand for the bed video's acceptance.
- 9 October 2026 (night): a title or end scene no longer needs a `code`; the example's two empty
  card modules are gone. The frame object has brand-aware drawing (`colour`, `text`, `tag`,
  `callout`, `dimension`, `badge`, `hand`, the table above), so a video needs no glue module
  for fonts, sizes, rule 3 and label checks. `check-script` now checks the scene code too
  (missing `code`, module, or function), without running it. `check-video --sheet` labels each
  frame in a strip under it, as `stills` does, in the brand's display font.
- 9 October 2026: `stills` and `render` added; scene code moves to one module per scene with
  the functions above (the prototype's `d_A`/`mA` pairs become `draw`, `mistake`, `right_way`),
  and a label drawn on screen must be in the script's "On screen" list. The caption band's text
  waits for the first cue; small accent text uses the brand's darker role.

## Contributing

Dev tooling: `.venv/bin/pip install -r requirements-dev.txt` into the same `.venv`, then
`.venv/bin/pytest` and `.venv/bin/ruff check .`. How the work is done is in `CLAUDE.md`; what is
built, and in what order, is in `PLAN.md`; where things stand, in `DIARY.md`.
