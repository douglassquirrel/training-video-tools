# PLAN.md — what video-tools does and how it gets built

Written 9 October 2026 by Claude at Squirrel's request; rewritten the same day (17:30) from the
first request, `inbox/done/request-from-training-video-2026-10-09.md`, after Squirrel's OK
(9 October 2026, 17:15: "go ahead"); amended the same day (19:01) from the second request,
`inbox/done/request-from-training-video-2026-10-09-2.md` ("Settled" 14) and (19:31) from the
third, `inbox/done/request-from-training-video-2026-10-09-3.md` ("Settled" 15), and (19:50) from
the fourth, `inbox/done/request-from-training-video-2026-10-09-4.md` ("Settled" 16): the bed
video re-made and accepted; and (20:14) from the fifth and sixth ("Settled" 17); and (21:46) from
the ninth, `inbox/done/request-from-training-video-2026-10-09-9.md` ("Settled" 20): four checking
commands, item 11; and (10 October 2026, 07:53) from the tenth,
`inbox/done/request-from-training-video-2026-10-10.md` ("Settled" 21): ✓ and ✗ drawn when a font
lacks them, and a check for characters a font lacks, item 12; and (10 October 2026, 08:46) from the
eleventh, `inbox/done/request-from-training-video-2026-10-10-11.md` ("Settled" 22): phonemes in
`say:` lines, item 13; and (10 October 2026, 09:00) from the twelfth,
`inbox/done/request-from-training-video-2026-10-10-12.md` ("Settled" 23): the mistake panel as
a curtain known to scene code, and stills at cue changes with a warning, item 14. CLAUDE.md says how the work is done; this file says what
the commands do and in what order they are built. Squirrel's instructions are recorded here
with their date; nothing here is invented, and anything assumed is under "Open questions".

## What this is for

The training-video project (`~/projects/non-code/training-video/`, read-only from here) makes
short narrated, animated training videos from a procedure diagram: one scene per step,
captions, mistakes shown beside the right way, in a brand's look. The first, *Making the Bed*
(4 min 22 s), was made on 6–7 October 2026 by a one-off prototype of about 2,250 lines
(`~/projects/non-code/make-bed-training-video/_work/film.py`, `core.py`, `sheet.py`, read-only).
About 850 of those lines are not about beds. These tools are those lines done properly: eight
commands and a shared package, driven by three files instead of code; and, from the ninth request,
four checking commands (item 11) that replace the scripts the training-video project wrote for
approving a brand kit and accepting a re-made video.

| File | Owned by | What the tools take from it |
|---|---|---|
| `videos/<slug>/script.md` | the video | Settings (voice, speed, size, fps, sources, output), the subject's colours, inset crop boxes, and each scene: its letter, titles, inset, side panel, narration cues, mistake, on-screen labels. Its rules: `training-video/videos/SCRIPT-FORMAT.md`. |
| `brands/<name>/BRAND.md` | the brand | Colours by role, fonts by role and their files, the mark, the end-card illustration, a few settings, rules. Its rules: BRAND.md's own "How this file is read". |
| `~/.video-tools.conf` | the machine | Where the speech model is; default voice and speed (a video's script overrides them, a flag overrides both). |

A video's own drawing code stays in that video's `scenes/` folder and imports the package.
**Acceptance is in the training-video project, not here:** it re-makes the bed video with these
tools and compares it with the 7 October original, and reports back through `inbox/`.

## The commands

One executable script per command at the top of the repository, each a thin wrapper that
imports `main()` from the package `videotools/` ("Settled" 5). All take `--help`. Errors go to
stderr in plain words, results and progress to stdout. Exit codes are shared:

| Code | Meaning |
|------|---------|
| 0 | Success; or, with `--dry-run`, everything checked and nothing written. For `check-script` and `check-video`: nothing wrong. |
| 1 | `check-script` / `check-video`: problems found, listed on stdout; `frame-hashes --compare`: frames differ (Squirrel, 9 October 2026, 21:44). |
| 2 | Bad arguments or usage (argparse's own code too). Nothing touched. |
| 3 | An input refuses: the script or brand kit is malformed or missing, a file it names is missing, a config setting is missing, timings are missing, or an output already exists. Nothing written. |
| 4 | An external program (ffmpeg, ffprobe, the speech model, a Python package the command needs) is missing or failed. What was written before the failure is named, nothing is deleted. A missing package is one line naming the package and the pip line for the venv, and `VIDEO_TOOLS_PYTHON` when that is unset (request 3, item 2; Squirrel, 9 October 2026, 19:31); every package import is guarded, cairo included. |

Every command reads the script first (and the brand kit if it draws), and refuses with every
problem listed (exit 3) before doing anything else; a malformed brand kit is reported in words
like a malformed script, never as a traceback (request 2, item 2).

```
check-script SCRIPT.md [--json OUT.json]
narrate      SCRIPT.md [--scenes KEY,…] [--voice V] [--speed S] [--replace] [--dry-run]
stills       SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]
render       SCRIPT.md [--scenes KEY,…] [--frames A-B] [--replace] [--dry-run]
assemble     SCRIPT.md [--out FILE] [--replace]
check-video  SCRIPT.md [VIDEO] [--sheet OUT.png]
crop-insets  SCRIPT.md
font-weights VARIABLE.ttf --weights 400,500,… --family-prefix PREFIX --out DIR
brand-preview  BRAND_DIR --out PREVIEW.png
frame-hashes   SCRIPT.md (--out HASHES.json [--merge] | --compare HASHES.json) [--scenes KEY,…] [--step N]
compare-frames SCRIPT.md OLD.mp4 SCENE:SECONDS[,…] --out SHEET.png [--offset SCENE=SECONDS …]
compare-video  NEW.mp4 OLD.mp4 [--every SECONDS] [--sheet OUT.png]
```

### Which Python

Dev tooling and the commands run from one virtual environment, `.venv/`, made from Homebrew's
Python 3.12 (`/opt/homebrew/bin/python3.12 -m venv .venv`; the speech packages need 3.10–3.13,
the Mac's `/usr/bin/python3` is 3.9: "Things checked" 1). `check-script` and the readers use only
the standard library and stay 3.9-compatible, so `check-script` also runs on `/usr/bin/python3`;
every other command needs the venv (cairo, numpy, the speech model, Pillow or fontTools), and
says so in plain words if its package is missing (exit 4). Each module imports only what it
needs, at the point of use.

## 1. The readers: `videotools.script`, `videotools.brand`, `videotools.config`

The contract everything else rests on. The two Markdown formats are the training-video
project's (`videos/SCRIPT-FORMAT.md`; BRAND.md's "How this file is read"); two small readers there
(`tools/script-check.py`, `tools/brand-preview.py`) are the reference, rebuilt here test-first,
not copied.

**`script.read(path)`** returns plain data: the title; `settings`, `colours`, `insets` as
dictionaries; `scenes` as a list, each with `key`, `name`, `line`, `props`, `cues` (each with
`n`, `text`, `line` and the sub-bullets `say`, `min`, `mistake`, `step`, `added` when present),
`side` and `screen` lists of items (`text`, `line`, `added`). Prose, and any level-2 heading
other than Settings, Colours, Insets and `Scene …`, is skipped until the next recognised
heading. Tables: `| Key | Value | Notes |`; the first two columns are read, keys lower-case with
hyphens; a key the format does not list is a problem unless it starts with `x-`. Unicode and `·`
pass through a cell unchanged.

**It refuses a malformed script** with every problem listed, each naming its line where there is
one (the message starts `line N: `), and the command exits 3 (`check-script` exits 1). The
checks are those of `script-check.py`: a `# title` line; required settings present (`title`,
`brand`, `voice`, `speed`, `language`, `speech-model`, `size`, `fps`, `source`, `output`,
`scene-code`); numbers numeric, `size` as `WxH`; `source` and `source-image` files exist
relative to the script's folder; the brand exists (`brands/<brand>/BRAND.md`, found by walking up
from the script's folder to the first folder holding `brands/`); colours `#RRGGBB`; insets as
four whole numbers; scene keys unique and `[A-Za-z0-9-]+`; `kind` one of `title`, `step`, `end`;
a lettered step has a `source`; a scene's `inset` exists; `side-panel` is `key-points`, `steps`,
`none`, `checklist N` or `custom <name> N`, with a list where one is needed and a cue N that
exists; a scene other than `end` has cues or `extra`; cues numbered 1..n without gaps; `min`
numeric; `mistake` with ` / `, at most one per scene; `step: N` only with `side-panel: steps` and
within the list; `added:` not empty; an unknown scene property, cue sub-bullet or `###` heading
outside a scene. Defaults the format gives: `lead 0.7`, `cue-gap 0.55`, `tail 1.0`,
`quality 18`, `kind step`, `side-panel` as the format says, `extra 0`.

**`brand.read(folder)`** reads BRAND.md's Identity, Colours, Fonts, Mark, Illustration and
Settings tables (key, value; for Fonts also the third column, the file), paths relative to the
kit's folder. Under a read heading, only a table whose header row begins `| Key | Value |` is
read; any other table there (the real kit's contrast table, `| Pair | Ratio | Verdict |`) is for
people and skipped, as the script reader skips tables under unknown headings (request 2, item 1;
Squirrel, 9 October 2026, 19:01). It resolves: a colour role to an `(r, g, b)` triple in 0–1, including a role used
as a value (`fill | accent`); a font role to its file, which must exist (refused by role and
path otherwise); settings `font-size-scale` (float), `background-grid` (`dots SPACING SIZE
OPACITY` or `none`), `caption-band` (a colour role), `caption-rule` and `title-rule` (`ROLE
HEIGHT`), `small-text-accent` (`ROLE SIZE`: text under SIZE px that would be `accent` uses ROLE;
BRAND.md rule 3), `label-shape`. Required: the colour roles the chrome uses (`background`,
`surface`, `ink`, `muted`, `rule`, `grid`, `accent`, `accent-dark`, `accent-light`, `mistake`,
`correct`, `on-accent`); the font roles `display`, `body`, `italic` (the others fall back:
`display-medium` to `display`, `body-medium` to `body`, `bold` to `display`, `italic-medium` to
`italic`); the Mark table; Identity `name` and `website`. A missing role is refused by name.

**`config.read(path=~/.video-tools.conf)`**: `KEY=value` lines, `#` comments, optional quotes,
`~` for home. Keys: `SPEECH_MODEL_DIR`, `VOICE`, `SPEED`. A missing file is not an error; a
missing key is reported by the command that needs it.

**`check-script SCRIPT.md [--json OUT.json]`** does what `script-check.py` does: prints the
summary (scenes, cues, words and the estimate at 2.6 words a second; the tracker letters; every
mistake; every `added:` line with where it comes from), then the problems if any, exit 1 if there
are problems, 0 otherwise, 2 on usage. It also reads the brand kit the script names with
`brand.read` (standard library, so still Python 3.9) and lists the kit's problems after the
script's, each prefixed with the BRAND.md path, so a kit `render` would refuse is found here first
(request 2, item 3). And it checks the scene code without running it (`scenes.check_code`, `ast`,
standard library; request 7; Squirrel, 9 October 2026, 20:52): a scene other than `title` or `end`
with no `code`, a `code` whose module is missing, a module that does not parse (its line), and a
module without a top-level `def` of a function the scene needs (the same list the loader uses,
`scenes.needed`), each by the script line; a missing `scene-code` folder is one problem. `--json` writes the parsed script as JSON and refuses an
existing file (exit 3).

## 2. `narrate`: the voice

`narrate SCRIPT.md [--scenes KEY,…] [--voice V] [--speed S] [--replace] [--dry-run]`

Speaks each cue's `say:` if it has one, else its caption, with the local Kokoro model through
`kokoro-onnx` (voice, speed and `language` from the script; the voice and speed fall back to
`VOICE` and `SPEED` in the config, and the flags win over both: "Settled" 6). Each clip is
trimmed to 30 ms before the first and 80 ms after the last sample above 0.01 (silence only
otherwise: the clip is left as it is). Writes, under the video's folder:

- `work/narration/<scene>_<NN>.wav`, NN the cue's number in the script, two digits, 24 kHz
  float as the model gives it;
- `work/narration/timing.json`: `{"voice": …, "speed": …, "model": …, "sample_rate": …,
  "scenes": {"<key>": [clip lengths in seconds, 3 decimals, one per cue]}}`, rewritten whole after
  each scene so an interrupted run keeps what it did.

Refuses (exit 3) when a clip or `timing.json` it would write exists, listing them, unless
`--replace`, which prints the files it will replace first. With `--scenes`, other scenes' entries
in an existing `timing.json` are kept (that is the one case where the file is read then
rewritten, and only with `--replace`). The model: `SPEECH_MODEL_DIR` from the config (or the
`VIDEO_TOOLS_CONF` environment variable's file, for tests), holding `model.onnx` and
`voices.npz`; refuses naming the setting and the path if missing. The voice must be in the
voices file (refused by name). `--dry-run` lists each cue's file, the text it would speak, the
voice, speed and model, and an estimate of each clip's length (words ÷ 2.6), and writes nothing.
It opens no network connection, ever (a test fails if the package imports `socket`, `urllib`,
`http` or `ssl`).

The one-time set-up (packages, model, voices file, config) is README steps typed by the user,
not a command ("Settled" 9); steps 2 and 3 are done on Squirrel's Mac already.

## 3. The timeline: `videotools.timeline`

All animation is keyed to cue start times, which come from the clip lengths. For a scene: each
cue lasts its clip length plus `cue-gap`, or its `min:`, whichever is longer; the first cue starts
at `lead`; the scene ends `tail` after the last cue ends, plus the scene's `extra`; a scene with
no cues lasts `extra` (plus `tail`? No: `lead + tail + extra`, as the prototype did, so a silent
scene still fades in and out). The scene's length is rounded to whole frames.

`Timeline(starts, lengths, total, fps)` answers: `p(t, cue, a, b)` (smoothstep-eased progress of
`t` between `a` and `b` seconds after the start of `cue`, 0–1); `cue(t)` (the cue speaking at `t`:
the last cue whose start is at or before `t`, 0 before the first; one rule, no 50 ms lead);
`start(cue)`, `length(cue)`, `frames`. Cues are numbered as in the script, from 1. Easing helpers
beside it: `clamp`, `lerp`, `prog`, `ease`, `ep`, `pulse`.

`timeline.build(script, scene, timing, for_render)`: with a clip length for every cue, exact;
with any missing, **refused for rendering** (exit 3, naming the scene and cue) and allowed for
stills with the estimate (words ÷ 2.6) and a warning on stderr.

## 4. The frame: `videotools.chrome`, `videotools.draw`, `videotools.camera`, `videotools.fonts`

Everything generic is drawn from the script and the brand kit, at 1920×1080 (the only size the
format allows; every region is named in one place, `chrome.Layout`, so a second size is possible
later without touching scene code):

- **Background**: the brand's background colour and its dot grid in the animation area.
- **Header** (step and overview scenes): the step roundel with the scene's letter (drawn in the
  mark's style), the eyebrow and title, the tracker of letters in script order (scenes sharing a
  letter share one place; `tracker-label` replaces the letter; done / now / to come in ink /
  accent / rule), a rule under it.
- **Reference column**: `source-label` over the inset (`work/insets/<inset>.png`, made by
  `crop-insets`; refused by name if missing), then the side panel: `key-points` (a list with
  accent squares, headed KEY POINTS), `steps` (numbered, the current one from the cues' `step:`
  in accent, done ones in ink), `checklist N` (ticks appearing one by one during cue N),
  `custom <name> N` (the scene code's `panel` function from cue N, fading in over 0.5 s),
  `none`; the brand mark at the foot. A scene property `side-panel-heading` (request 4, item 1;
  Squirrel, 9 October 2026, 19:50) puts its text, in the small muted tracked style of KEY POINTS,
  above a `steps` or `checklist` panel (the rows move down to make room) or in place of KEY
  POINTS; with `none` or `custom` it is a problem. The property is proposed to the script format
  (`training-video/videos/SCRIPT-FORMAT.md`, theirs to change) in those words.
- **Caption band**: the brand's `caption-band` fill and `caption-rule`; the current cue's caption
  wrapped and centred in `body-medium` at 36 px, fading in at each cue; on the mistake cue a
  "COMMON MISTAKE" tag in the mistake colour and the caption shifted right.
- **Mistake panels** over the animation area during the mistake cue: two cards, "MISTAKE" with ✗
  in the mistake colour and "RIGHT WAY" with ✓ in the correct colour, headed by the two halves of
  `mistake:`, each body drawn by the scene code (never colour alone: BRAND.md rule 1).
- **Title card** (`kind: title`): the mark and wordmark, `eyebrow`, `title`, `subtitle`, the
  `title-rule`, the lettered step list from the scenes (letter and title, in order, one place per
  letter, appearing one by one during cue 2), the whole source page (`work/insets/title.png`)
  tilted with `title-image-caption`.
- **End card** (`kind: end`): the brand's `end-card` illustration, mark and wordmark, rule,
  `website` in italics, the script's `credit`, the brand's `illustration-credit`.
- **Fade** in and out of every scene (the script's `fade`, default `0.45 0.4`).
- **Text**: sizes multiplied by `font-size-scale`; text under the `small-text-accent` size that
  would be accent uses the darker role; letter-spacing and word wrap.
- **Fonts** by file, never installed: on macOS the files are registered with CoreText for the
  process ("Things checked" 4); elsewhere a private `fonts.conf` naming the brand's font folder
  is written to the video's `work/fonts/` and `FONTCONFIG_FILE` set before the first text is
  drawn (to be checked in the device shell: "Things checked" 5).

`videotools.draw` holds the primitives the prototype's `core.py` had, with colours passed in,
never defaults from a palette: text with tracking, wrapping and anchors; polygons, lines,
rounded rectangles, circles, Bézier curves, polylines cut to a fraction; arrows that draw on;
pills (tags), callouts with leader lines, dimension lines, ✓/✗ badges, mitten hands (whose
letter label takes a `label_size`, the roundel scaling with it, so scene code can pass the
brand-scaled size: request 4, item 3); `shade`,
`mix`, `rgb`. `videotools.camera` holds the oblique projection `Camera(scale, focus, centre,
direction, kx, ky)` with `point(x, y, z)`, interpolation between two cameras, points on a
plane (`front`, `top`, `end`), generalised from the prototype's box, and the prototype's two
fabric helpers: `ripple(x0, x1, z, amp, n, phase)` (a wavy edge as `(x, z)` points) and
`clip(pts, f)` (a polygon cut to the side where `f(point) >= 0`), which any cloth or paper
subject needs (request 2, item 7; Squirrel, 9 October 2026, 19:01).

### The scene-code interface ("Settled" 13)

The script's `scene-code` folder holds one Python module per scene, named by the scene's
`code` property (`bottom_sheet.py`). The tools import it from that folder and call:

```python
def draw(frame):                 # the animation area, every scene
def mistake(frame, rect):        # the "Mistake" panel body: only for a scene with a mistake cue
def right_way(frame, rect):      # the "Right way" panel body: likewise
def panel(frame, rect):          # the side panel: only for side-panel `custom <name> N`
```

A scene of kind `title` or `end` may have no `code`: the chrome draws the whole card and no
module is loaded; with one, its `draw` adds to the card (request 6, item 2). A step scene
without `code` is refused by name.

`frame` carries: `ctx` (the cairo context, clipped to the area), `t` (seconds into the scene),
`timeline` (item 3), `scene` (the scene's data from the script: `key`, `props`, `cues`, …),
`colours` (the script's Colours as `(r, g, b)`), `brand` (the brand kit, for its colours and
fonts), `area` (the animation area's rect), and `label(text)`, which returns `text` after
checking it is in the scene's "On screen" list and raises a useful error (exit 3) if not, so a
label that is drawn but not in the script is caught, and a typo on either side. `rect` is `(x, y,
w, h)` in frame pixels. A missing function is a useful error naming the module and function.
Scene code never imports `cairo` for text: it draws through `videotools.draw`, or through the
frame's brand-aware methods (request 6, item 1; Squirrel, 9 October 2026, 20:14), each a thin
layer over `videotools.draw` filling in what the brand and script say: `frame.colour(name)` (the
script's Colours, else the brand's roles, else a refusal listing both); `frame.text(s, x, y,
size, role="body", colour="ink", anchor="l", alpha=1.0, track=0, check=False)` (font by role,
size × `font-size-scale`, rule 3 on the colour at the scaled size, `check` runs `label`);
`frame.tag(s, x, y, size=22, fill="ink", colour="on-accent", role="display", anchor="l",
alpha=1.0, padx=14, pady=9, border=None)`, `frame.callout(s, target, at, size=22,
leader="ink", fill=None, colour="ink", role="display", anchor="l", alpha=1.0)` and
`frame.dimension(p0, p1, s, size=24, colour="accent", text_colour=None, side=1, alpha=1.0)`
(text through `label`, sizes scaled, colours by name, rule 3 on a pill's fill when its text is
small); `frame.badge(x, y, ok, r=24, alpha=1.0)` (`correct`/`mistake` fill, `on-accent` mark);
`frame.hand(x, y, angle, scale, alpha=1.0, mirror=False, label=None)` (skin, outline and
sleeve from the script's Colours `skin`, `skin-dark`, `sleeve` when present, else neutral
defaults named in the README; the label in the display font on an accent roundel at 28 ×
scale). Everything else (`poly`, `line`, `circle`, `arrow`, `bezier`, the camera) stays in
`videotools.draw` and `videotools.camera` with explicit colour triples, which `frame.colour`
supplies.

## 5. `stills`: looking before rendering

`stills SCRIPT.md SCENE:SECONDS[,…] --out SHEET.png [--grid CxR]`

Frames at the given times (a negative time counts back from the scene's end; a time past the
end is refused, exit 2), pasted on one sheet (`--grid` default `2x2`; the sheet is 1920×1080
whatever the grid, frames scaled to fit; more frames than cells is refused), each labelled with
its scene, time and cue in a strip under the frame, never over it: no pixel of a frame is covered,
since the header is one of the things a sheet is for checking (request 2, item 4). Works on estimated timings with the warning of item 3.
Refuses an existing `--out` (exit 3). Needs cairo and Pillow.

## 6. `render`: scene by scene

`render SCRIPT.md [--scenes KEY,…] [--frames A-B] [--replace] [--dry-run]`

Each scene (or the given ones; `--frames` only with one scene) to
`work/segments/<scene>_<first frame, 5 digits>.mp4`: frames drawn with cairo and piped as raw
BGRA to `ffmpeg -f rawvideo -pix_fmt bgra -s WxH -r FPS -i - -c:v libx264 -preset veryfast -crf
QUALITY -pix_fmt yuv420p -r FPS OUT` (`-nostdin` always, so ffmpeg never stops to ask; `-y` only
when the segment was listed under "Replacing": request 3, item 1). Refuses without a
complete `timing.json` for every scene it renders (exit 3, item 3), and refuses an existing
segment unless `--replace` (listed first). After each segment: ffmpeg's exit status must be 0
and `ffprobe -count_frames` must report the expected frame count; otherwise the partial file is
named, nothing is deleted, and the command exits 4. Prints each scene's progress and the
frames a second achieved. `--dry-run` lists the scenes with their lengths, frame counts and
segment names, and writes nothing.

## 7. `assemble`: the finished video

`assemble SCRIPT.md [--out FILE] [--replace]`

Refuses (exit 3), naming each: a scene with no segment; segments whose frame counts (ffprobe) do
not add up to the scene's; a cue with no clip; an existing output (`--out`, default the script's
`output`, relative to the video's folder); an existing intermediate unless `--replace` (which
never touches the finished video). Then: the segments in script order through ffmpeg's concat
demuxer with `-c copy` to `work/assemble/video-only.mp4` (list at `work/assemble/segments.txt`;
with `--replace`, `-y` for the two intermediates it listed, never for the output; `-nostdin` on
every call: request 3, item 1);
every clip read with its own sample rate and resampled (linear) to 48 kHz, laid at its scene's
start plus its cue's start plus 50 ms, the mix peak-normalised to 0.89, written to
`work/assemble/narration.wav`; muxed with `-c:v copy -c:a aac -b:a 160k -ar 48000 -movflags
+faststart -shortest` to the output. Each ffmpeg call's exit status is checked (exit 4). Prints
the length, size and SHA-256 of the output for the diary.

## 8. `check-video`: the same checks on every video

`check-video SCRIPT.md [VIDEO] [--sheet OUT.png]`

Compares the file (default the script's `output`) with the script: length within one frame of
the scenes' total (`ffprobe`); peak below 0 dBFS (`volumedetect`); silences of 2 s or more
(`silencedetect=n=-40dB:d=2.0`) only outside every cue's window, and narration heard in every
one. A cue's window is its clip's span as `assemble` lays it (the cue's start plus 50 ms, for
the clip's length); a silence overlapping a window by more than 0.1 s (the slack the detector's
boundaries are trusted to) is a problem, and one covering a window to within that slack means
the cue was not heard, a second problem. With `--sheet`, one frame from the middle of each
scene (`ffmpeg -ss T -frames:v 1`, into a temporary folder) pasted on a 1920×1080 sheet in a
near-square grid, each labelled in a strip under the frame (`videotools.sheet`, shared with
`stills`; request 8; Squirrel, 9 October 2026, 21:07), in the brand's display font (so the kit is
read, and refused like a script, exit 3); refuses an existing file. Lists every problem; exit 1 if any, 0 if none,
4 if ffprobe or ffmpeg fail. The real
output formats of `ffprobe` and the two filters are recorded in DIARY.md before the parsers are
written ("Things checked" 6).

## 9. Two small commands

**`crop-insets SCRIPT.md`**: each `## Insets` box cut from `source-image` with Pillow, scaled to
fit 388 px wide and 330 px tall (360 when the box is taller than it is wide), into
`work/insets/<key>.png`; the whole image scaled to 750 px tall into `work/insets/title.png`.
Refuses a box outside the image, a missing `source-image`, and any existing output (exit 3).

**`font-weights VARIABLE.ttf --weights 400,500,600,700 --family-prefix PREFIX --out DIR`**: with
fontTools, a static instance per weight (`varLib.instancer.instantiateVariableFont`), each with
its own family name (`PREFIX SemiBold`: name IDs 1, 4 and 6 set, 16, 17, 21, 22 and 25 removed),
written to `DIR/PREFIX-SemiBold.ttf`; weight names 100 Thin, 200 ExtraLight, 300 Light,
400 Regular, 500 Medium, 600 SemiBold, 700 Bold, 800 ExtraBold, 900 Black; an italic variable
font gets `Italic` appended (`PREFIX MediumItalic`). Refuses a font without a `wght` axis, a
weight outside its range, and any existing output (exit 3).

## 10. Not carried over from the prototype

ffmpeg's exit status ignored; `-y` anywhere; estimated timings used silently for a render; 24 kHz
assumed; the chrome knowing one video's letters or labels; dead code; no `--help`; tracebacks for
errors; `from core import *`; colour names (`gold`, `navy`) that no longer describe the colours.

## 11. Four checking commands (request 9; Squirrel, 9 October 2026, 21:44: "go ahead!")

The training-video project's `tools/brand-preview.py`, `frame-hashes.py` and `compare-frames.py`
are the reference for behaviour (read-only; rebuilt here test-first, not copied); the fourth is
the comparison run by hand for the bed video's acceptance (request 4) and never kept. Each
reads through the package's own readers, so what it accepts and refuses is what the tools accept
and refuse, in the same words (exit 3). Each refuses an existing output. Exit codes as the table
above; `compare-video` always exits 0 when it runs, since it reports rather than judges.

**`frame-hashes SCRIPT.md (--out HASHES.json [--merge] | --compare HASHES.json) [--scenes KEY,…]
[--step N]`**: every N-th frame (default every one) of each scene drawn as `render` draws it
(cairo, no ffmpeg) and the MD5 of its pixels recorded by scene and frame number:
`{"<scene>": {"<frame>": "<md5>"}}`. Needs a complete `timing.json` for every scene it hashes,
refused like `render` (exit 3). `--out` refuses an existing file unless `--merge`, which keeps
the file's other scenes and replaces the hashed ones (the one case where it reads then rewrites).
`--compare` draws the same frames and prints, per scene, `all match` or how many differ and the
first twelve frame numbers, and how many hashed frames are not in the reference; exit 1 if any
differ ("Settled" 20), 0 if all match. Prints each scene's frame count and the frames a second.
Needs pycairo.

**`compare-video NEW.mp4 OLD.mp4 [--every SECONDS] [--sheet OUT.png]`**: for each file, duration
and frame count (`ffprobe`) and peak and mean level (`volumedetect`); the two mono mixes decoded
to 48 kHz through ffmpeg (`-f s16le -ac 1 -ar 48000`), each cut into 0.1 s windows of RMS level,
the Pearson correlation of the two envelopes over the shorter length, and the number of windows
that are speech (above −40 dBFS) in one and silence in the other; then one frame from each file
every `--every` seconds (default 5, from 0 up to the shorter duration, `ffmpeg -ss T -frames:v 1
-f rawvideo -pix_fmt rgb24`) and their mean absolute difference over RGB (0–255): the mean, the
median, and the five largest with their times, largest first. With `--sheet`, the pairs at those
five times side by side, new left, old right, each labelled in a strip under it
(`videotools.sheet`), refused if it exists. Exit 0 always; 4 if ffmpeg or ffprobe fail. Needs
numpy and Pillow (for the sheet).

**`compare-frames SCRIPT.md OLD.mp4 SCENE:SECONDS[,…] --out SHEET.png [--offset SCENE=SECONDS …]`**:
for each time (as `stills` reads them: a negative time counts back from the scene's end, one
past the end refused, exit 2), the frame drawn now from the script and its scene code beside the
old video's frame at the same moment, new left, old right, one pair per row, each pair labelled
in a strip under it with its scene, time, the old video's time and the mean absolute difference
over RGB (0–255), printed one line per pair. The old video's moment is the scene's start plus the
time, the start being the sum of the earlier scenes' lengths from the current `timing.json`
("Settled" 20); `--offset SCENE=SECONDS` adds to one scene's start (repeatable). Needs a complete
`timing.json` as `render` does; a moment past the old video's end is refused by name (exit 3);
refuses an existing sheet. Needs pycairo, numpy, Pillow and ffmpeg.

**`brand-preview BRAND_DIR --out PREVIEW.png`**: the kit read with `brand.read` (a bad kit refused
in its words, exit 3) and drawn with `videotools.draw` in the kit's own fonts on a 1920×1080
sheet: every colour as a swatch with its role and hex; every font role the kit names (extra
roles such as `mono` included) with a specimen line in that font at its size; the mark and
wordmark drawn as the chrome draws them; sample pills and accent text at one size above and one
below `small-text-accent`, so rule 3 is visible; the end-card illustration and
`illustration-credit`; the settings table; and, always ("Settled" 20), the WCAG contrast ratio
(relative luminance, 1 to 21) of each text-on-fill pair the chrome uses (ink, muted and accent on
background and surface; on-accent on accent, accent-dark, mistake and correct; the caption text
on `caption-band`), with the 4.5 and 3 thresholds marked. Refuses an existing output. Needs
pycairo (cairo writes the PNG; no Pillow).

## 12. Characters a font lacks (request 10; Squirrel, 10 October 2026, 07:50: "display font only. go ahead")

cairo's simple text API draws a character the chosen font has no glyph for as the font's
missing-glyph box, silently, and reports the same width for every such character. The
training-video project's second video showed it: five labels ending in ✓, which EB Garamond
lacks (as do the example's fixture fonts). Two parts:

**`videotools.glyphs`** (standard library, Python 3.9): reads a TrueType/OpenType font file's
`cmap` table (formats 4 and 12) once and answers which code points it covers; `fonts.load`
registers each of the kit's files by family name, so `draw.text` and `draw.text_width` can ask
`glyphs.has(family, ch)`. A family never registered is assumed to have everything (fallback
fonts, the tests' plain cairo drawing: nothing changes for them).

**✓ (U+2713) and ✗ (U+2717) drawn** (item 1): in `draw.text` and `draw.text_width`, the one
place all text goes through (the chrome, the frame's methods, pills, callouts, dimension lines,
wrapped captions), a ✓ or ✗ the family lacks is drawn as `draw.badge`'s tick or cross without
the circle, in the text's colour and alpha, scaled to the font size (0.8 × size wide, a stroke of
0.11 × size, centred 0.3 × size above the baseline), anywhere in the string, and its width is
counted in the text's width, so pills, centring and wrapping stay right. Where the family has
the glyph, the glyph is drawn. `frame.label`'s check is unchanged: the label as written.

**`check-script` reports characters a font lacks** (item 2): for each text the chrome draws,
against the resolved file of the role the chrome draws it in: captions (`body-medium`), side
panel items and the credit (`body`), the title and eyebrow, tracker labels, the side-panel
heading and `source-label` (`display`), the subtitle, title-image caption and the website
(`italic`), and the On screen labels against the **display font only**, the frame methods'
default role for pills and callouts (Squirrel, 10 October 2026, 07:50; a label drawn by scene
code in another role, such as the training-video project's `mono`, is only as good as that
font, and the README says so). ✓ and ✗ are excepted, since item 1 draws them. One problem per
text, naming the script line, the text, the first character lacking with its code point, and the
font file; listed with the kit's problems after the script's, exit 1. Nothing is drawn.

## 13. Phonemes in `say:` lines (request 11; Squirrel, 10 October 2026, 08:46: "OK to put flag on narrate")

Where respelling cannot fix a word's stress ("Karpathy", "type in"), a `say:` line may hold
spans written `[[…]]` whose contents are phonemes for the model as they stand (kokoro-onnx
0.6.1's `create(..., is_phonemes=True)`, checked in the installed package: the text is used as
phonemes, whitespace collapsed, and any symbol outside the tokenizer's vocabulary is dropped
silently). A caption never holds a span: the brackets are for `say:` only.

**`videotools.phonemes`** (standard library): `parts(text)` splits a `say:` into text parts and
spans; `problems(text)` lists an unclosed `[[`, an empty span, and each symbol in a span that
the vocabulary lacks, with its code point. `VOCAB` is a fixed copy of the 114 symbols in
kokoro-onnx 0.6.1's `config.json` (`vocab`), named as such in the code; a tier 2 test asserts it
equals the installed package's, so an upgrade that changes it fails a test rather than drifting.

**`narrate`** (item 1): a cue whose `say:` has a span is sent as phonemes: each text part
phonemized by the model's own tokenizer (`speech.tokenizer.phonemize(part, lang)`), the spans
spliced in with the spaces as written, `create(phonemes, voice, speed, lang, is_phonemes=True)`.
A cue without a span is sent as text, the call unchanged, so every existing clip is unchanged
(proved on the scratch example: the clips byte-identical before and after). The model's failure
on a bad span is reported as today (exit 4, the cue named).

**`check-script`** (item 2): after the font check, each cue's `say:` with `phonemes.problems`
(unclosed, empty, a dropped symbol), and a caption holding `[[` (it would show on screen), each
by its line; exit 1.

**`narrate --dry-run --phonemes`** (item 3): the dry run also prints, for each cue, the full
phoneme string that would be sent, spans spliced in, so a writer can see what the voice is
given; needs the speech package (exit 4 if missing, as `narrate` says it) but not the model
file; writes nothing. The flag is on `narrate`, not a new command (Squirrel, 10 October 2026).

## 14. The curtain, and stills at cue changes (request 12; Squirrel, 10 October 2026, 09:00: "flag on stills, warning on by default. go ahead")

The mistake panels cover the animation area (the background at 0.96, then the two cards) with
strength `p(t, n, 0.0, 0.5) × (1 − p(t, n+1, −0.4, 0.1))` for the mistake cue `n` (the panel
stays to the scene's end when the mistake cue is the last). Scene code that fades its
pre-mistake picture out at the *next* cue's start, the moment the panel lifts, shows a glimpse
of it through the lifting panel (the training-video project's second video, found by ear).

**The curtain in one place** (item 1): the formula moves into the timeline, which knows the
cues; `Timeline.curtain(t)` is the panel's strength 0–1, `covered(t)` is true while it is at
full strength, and `before_curtain(t)` is 1.0 until a fade from 0.5 to 0.7 s after the mistake
cue's start (inside the covered time), then 0.0; for a scene with no mistake cue, `curtain` is
0, `covered` false and `before_curtain` 1.0 always. `frame.mistake_panels` draws with
`tl.curtain(t)`, so the stored frames are unchanged; scene code reaches them as
`frame.timeline.before_curtain(frame.t)`. The README's "Writing a video's scene code" says why.

**`stills --cue-changes`** (item 2): `stills SCRIPT.md --cue-changes [--scenes KEY,…] --out
SHEET.png [--grid CxR]`: instead of SCENE:SECONDS, for each cue start of each scene the frames
at −0.3, 0 and +0.3 s (clipped to the scene; the first cue's −0.3 falls in the lead), and +0.6 s
for the cue after a mistake, labelled as `stills` labels frames; when they outnumber the grid,
several sheets named `SHEET-1.png`, `SHEET-2.png`, … (each refused if it exists). **The warning,
on by default** (Squirrel, 10 October 2026): for each cue after a mistake, the animation area
is drawn twice *without* the panel (`frame.draw_frame(..., curtain=False)`), at the moment the
panel starts to lift (next start − 0.4) and at the moment it has gone (next start + 0.1);
pixels that differ from the background in the first and match it in the second are something
that vanished as the panel lifted; more than 0.2 % of the area is a warning on stderr naming
the scene and cue (`stills: scene B: something drawn under the panel at cue 2 vanishes as it
lifts for cue 3 (N pixels); fade it out while covered: frame.timeline.before_curtain`), exit 0
(it is a warning, the sheets are still written). It cannot see a change later than the lift,
nor a picture that fades under the curtain and comes back; the README says so.

## What is written where

- Every command writes only under the video's `work/` (intermediates: narration, insets,
  segments, assemble, fonts) or `out/` (the finished video), or the file a `--out`/`--json` flag
  names; never into a script, a brand kit, a source, or another project. The checking commands of
  item 11 write only their `--out` or `--sheet` file (`frame-hashes --merge` rewrites the hashes
  file it was given, and nothing else).
- Nothing is written over an existing file: the command refuses before starting, and the two
  with `--replace` list what they will replace first. The finished video is never replaced.
- Nothing is deleted, moved or sent anywhere. A partial file left by a failed external program is
  named, not removed.
- Tests pin each: refusal to overwrite, nothing written on refusal, no partial deletion, no
  network module imported.

## Configuration

`~/.video-tools.conf` (`video-tools.conf.example` committed): `SPEECH_MODEL_DIR`, `VOICE`, `SPEED`.
Read, never run: `KEY=value`, `#` comments, optional quotes, `~` for home. The video's script
overrides `VOICE` and `SPEED`; flags override both. `VIDEO_TOOLS_CONF` in the environment names
another config file (the tests use it). `VIDEO_TOOLS_PYTHON` names a Python to run the commands
under: each wrapper restarts itself under it before importing anything, instead of the
repository's `.venv` (for the Linux device shell, where that venv is the Mac's; request 2, item 6;
Squirrel, 9 October 2026, 19:01). Unset, the wrappers behave as before. Everything particular to
a video or a brand lives in the script and the brand kit.

## Dependencies

Allowed (Squirrel, 9 October 2026, 16:16), installed in the README's one-time step: Homebrew
`python@3.12`, `cairo`, `pkgconf`, `ffmpeg`; in `.venv/`: `pycairo`, `numpy`, `soundfile`,
`kokoro-onnx==0.6.1` (brings `onnxruntime` and `espeakng-loader`), `Pillow`, `fonttools`; the
Kokoro-82M model and voices in `~/models/kokoro/` (`model.onnx`, `voices.npz`).

## Things checked against the real thing (9 October 2026, on Squirrel's Mac, arm64, macOS 26.6)

1. **Python.** `/usr/bin/python3` is 3.9.6. Homebrew has 3.11, 3.12 and 3.14; no 3.13.
   `kokoro-onnx` 0.6.1 needs 3.10–3.13, so the venv is made from `python3.12` (open question 1).
2. **kokoro-onnx 0.6.1** on 3.12 loads `~/models/kokoro/model.onnx` and `voices.npz` (voices
   `af_heart`, `am_michael`, `bf_emma`, `bm_george`) and speaks a test line: 24,000 Hz, float32,
   peak 0.65, 1.365 s for four words.
3. **ffmpeg 9.0.2** (Homebrew) has `libx264` and `aac`, takes raw `bgra` on stdin, and exits 0 on
   good input; on truncated input it exits 69 with "Packet too small". `ffprobe -count_frames
   -show_entries stream=nb_read_frames,r_frame_rate,width,height:format=duration,size -of json`
   gives the frame count as a string (`"nb_read_frames": "3"`) and the duration in seconds.
4. **pycairo 1.29.2** builds in the venv against Homebrew cairo 1.18.6 once `pkgconf` is
   installed (it isn't on a stock Mac; `brew install pkgconf`). cairo's toy text API on macOS goes
   through CoreText, **not fontconfig**: with `FONTCONFIG_FILE` pointing at the brand's fonts
   every family name gave the same fallback width. Registering each font file with
   `CTFontManagerRegisterFontsForURL(url, kCTFontManagerScopeProcess, …)` through `ctypes` makes
   `select_font_face("EBG SemiBold")` find it (distinct widths for SemiBold, Regular, Italic),
   with nothing installed.
5. **Linux**, as reported by the training-video project (request 2, item 5; the device shell,
   9 October 2026, 18:45–18:50: Linux aarch64, Python 3.10.12, cairo 1.16.0, pycairo 1.29.1,
   ffmpeg 4.4.2, fontconfig 2.13.1), not run from here: setting `FONTCONFIG_FILE` in-process is
   enough, the brand's fonts drew correctly in every role; the suite passed but for the one
   CoreText-only test (now skipped off macOS); the example's chain ran with the real ffmpeg
   (`render` about 47 frames a second), `assemble` placed every cue to the millisecond with
   clips at 22,050 and 24,000 Hz, `check-video` clean, and the refusals held. The repository's
   `.venv` is the Mac's, so there the commands run under a venv outside the repository named by
   `VIDEO_TOOLS_PYTHON` (Configuration).
6. **ffmpeg's output formats**, recorded 9 October 2026 on a 3 s invented file (blue frames, a
   1 s tone from 1.0 s): `ffprobe -v error -show_entries format=duration,size:stream=index,codec_type,
   nb_frames,r_frame_rate,width,height,sample_rate,channels -of json` gives strings
   (`"duration": "3.000000"`, `"size": "25662"`, `"nb_frames": "90"`, `"r_frame_rate": "30/1"`,
   `"sample_rate": "48000"`) and `"channels": 1` as a number; `-count_frames -select_streams v:0
   -show_entries stream=nb_read_frames` gives `"nb_read_frames": "90"`. `-af volumedetect -f null -`
   prints on stderr `[Parsed_volumedetect_0 @ …] mean_volume: -25.8 dB` and `max_volume: -18.0 dB`
   (take the last of each: a first instance printed `n_samples: 0`). `-af silencedetect=n=-40dB:d=0.5`
   prints `silence_start: 0`, then `silence_end: 1.000042 | silence_duration: 1.000042`, per
   silence, on stderr. A frame: `ffmpeg -ss T -i V -frames:v 1 OUT.png`. The concat demuxer with
   `-c copy` joined two copies to 6.02 s, exit 0. A missing input exits 254.
7. **Raw audio and raw frames** (9 October 2026, ffmpeg 9.0.2, on the 60.067 s example video):
   `-i V -map 0:a -f s16le -ac 1 -ar 48000 -` writes 5,766,400 bytes to stdout, 2,883,200
   samples, the file's length exactly; `-ss T -i V -frames:v 1 -f rawvideo -pix_fmt rgb24 -s
   1920x1080 -` writes 6,220,800 bytes, one frame; both exit 0 with `-nostdin`.

## Build order

Each step test-first (CLAUDE.md), ending green and committed on `main`; pushed when there is a
remote ("Settled" 7).

1. **Look.** Done 9 October 2026: `.venv` on 3.12, the beliefs above checked. Then `examples/`:
   an invented video (`examples/videos/paper-boat/script.md`, an invented subject, nothing from any
   real source) and an invented brand (`examples/brands/paperboat/BRAND.md`, with three static
   weights of EB Garamond under their own family names and the OFL licence) that together exercise
   every part of the two formats.
2. Item 1 (readers, `check-script`), item 3 (timeline).
3. Item 2 (`narrate`), with the one-time set-up in the README.
4. Item 4 (chrome, primitives, camera, fonts, the scene-code interface once Squirrel settles it)
   and item 5 (`stills`), together: stills are how chrome is checked.
5. Item 6 (`render`), item 7 (`assemble`), item 8 (`check-video`).
6. Item 9 (`crop-insets`, `font-weights`).
7. README, then lint as its own pass.
8. The training-video project re-makes the bed video and reports back through `inbox/`.
   Request 3 (9 October 2026, their verification of request 2, all seven items confirmed on
   Linux with the real kit) found three things, none blocking: item 1, `--replace` against real
   ffmpeg (the stub overwrote without `-y`; the stub now refuses as ffmpeg does); item 2, a
   missing package is a traceback (numpy, soundfile and cairo were unguarded); item 3, the sheet
   label test draws its reference in-process, which on Linux gets fontconfig's fallback fonts
   when a tier 1 test drew text first (references drawn in a subprocess, as a command does).
   **Done, 9 October 2026 (request 4):** the bed video re-made in the device shell at `c1720ae`
   matches the 7 October original to the frame (262.439 s, 7,873 frames), every clip to the
   millisecond, frames every 5 s within 0.6 of 255 on average; `check-video` clean. Three
   differences seen; two asked for and built: item 1, a `side-panel-heading` scene property
   (the prototype's "CHECK BEFORE YOU LEAVE IT" over the checklist); item 3, the hand label's
   size (it was fixed at 28 px, so `font-size-scale` did not reach it). Item 2 (the prototype's
   "+ Pillows" roundel and pillow icon) is not asked for and not done. Request 5 (their
   verification of request 4) found two test faults on Linux: the fresh-process font test
   handed its child the test process's `FONTCONFIG_FILE`, and the test runner handed commands an
   exported `VIDEO_TOOLS_PYTHON`; both environments are now cleaned. Request 6: the brand-aware
   frame methods and the optional `code` for cards (item 4), so a video needs no glue module.
   Request 7 (their verification of 5 and 6, all passed on Linux): `check-script` checks scene
   code statically (item 1), closing for scene code the gap request 2 closed for brand kits.
   Request 8: the bed video rebuilt on the frame methods, every frame hash-identical, the whole
   chain with `--replace` against real ffmpeg, `check-video` clean (request 3 and 6 confirmed end
   to end); request 7 verified; `check-video --sheet` labels in a strip, as `stills` (item 8).
10. **Request 9** (9 October 2026, 21:40; OK'd 21:44): item 11, in this order, each test-first:
   `frame-hashes` (no ffmpeg; a regression check for the package at once), `compare-video` (the
   stub ffmpeg gains raw audio and raw frames), `compare-frames` (reusing the frame reader),
   `brand-preview`; then the README for the four, "Notes for users", and lint as its own pass.
   **Done 9 October 2026, 21:46–22:20**: all four built, each in the README with a real run;
   the training-video project checks them against its own scripts on the bed video and retires
   its copies (their side).
11. **Request 10** (10 October 2026, 07:42; OK'd 07:50): item 12, test-first in this order: the
   `cmap` reader and the registry; ✓ and ✗ in `draw.text` and `draw.text_width`; the
   `check-script` report; README, "Notes for users", lint as its own pass. **Done 10 October
   2026, 07:53–08:06**: both items built and in the README; the two real scripts read clean
   (their ✓ labels excepted); the training-video project re-makes its second video's stills and
   retires its `tag()` helper (their side).
12. **Request 11** (10 October 2026, 08:29; OK'd 08:46): item 13, test-first in this order: the
   span parser and the vocabulary copy; the splice in `narrate` with the stub's fake
   phonemizer; the `check-script` report; `--phonemes` on the dry run; README, "Notes for
   users", lint as its own pass; the byte-identical proof on the scratch example in Tier 3.
   **Done 10 October 2026, 08:46–08:56**: all three items built and in the README; the proof
   done (eleven clips and `timing.json` byte-identical); the training-video project writes its
   six spans and re-makes its clips (their side).
13. **Request 12** (10 October 2026, 08:53; OK'd 09:00): item 14, test-first in this order: the
   curtain functions on the timeline and `mistake_panels` on them (stored frames unchanged);
   `draw_frame(..., curtain=False)`; `stills --cue-changes` with its sheets; the warning; README,
   "Notes for users", lint as its own pass. **Done 10 October 2026, 09:00–09:07**: both items built
   and in the README with real runs; the training-video project switches its three scenes to
   `before_curtain` and adds the check to its routine (their side).
9. **Request 2** (9 October 2026, from trying the tools on the bed script and kit): in its
   order, each test-first: items 1, 2 and 3 (the brand reader's tables, `BrandError` in words
   with exit 3, `check-script` reading the kit); 4 (`stills` labels in a strip); 5 and 6 (the
   CoreText test skipped off macOS, `VIDEO_TOOLS_PYTHON` and a README section for the device
   shell); 7 (`ripple` and `clip` in the camera; the diary's time corrected). Then "Where things
   stand" says 1–4 are in, and the training-video project starts the re-make when Squirrel says.

## Testing

`tests/tier1/`: the readers, config, timeline and easing, layout and text rules, the
`timing.json` and frame-count arithmetic, argument parsing. `tests/tier2/`: each command end to
end with `conftest.py` putting stub `ffmpeg` and `ffprobe` on PATH (recording their arguments and
the bytes they were sent, failing or dying on demand) and a stub speech model (a fake
`kokoro_onnx` module on `sys.path` returning a known waveform), a config file named by
`VIDEO_TOOLS_CONF`, and the example video copied into a temporary folder. Frame tests draw a
frame of the example and compare it, reduced to 192×108, with a stored image within a tolerance
("Settled" 11); they need pycairo, which the venv has, and no external program. The tolerance
pins layout, not fonts (with fallback fonts six of eight frames are within it: request 3, item
3), so fonts are pinned by a frame drawn in a fresh process, with and without the brand's
fonts loaded; any test that compares a frame with a command's output draws its reference in a
fresh process too, because fontconfig (Linux) fixes a process's fonts at its first text call. Tier 3 (manual,
README): each command for real on the example video.

## Not doing

- Anything particular to one video: subject drawing, narration text, sources.
- Network use at run time: no cloud speech, no uploading, no fetching brand assets or models.
- Editing video in a timeline, or any graphical interface.
- Slide decks.
- A second frame size (the layout is named in one place so it can come later).

## Open questions

None.

## Settled

1. The repository is made from the coding template, described, and has no tools until a request
   arrives (Squirrel, 9 October 2026, 16:06).
2. It holds the tools pulled out of the training-video mechanism; the method itself stays in the
   training-video project (Squirrel, 9 October 2026, 16:06).
3. The dependencies listed under "Dependencies" are allowed, with every command importing only
   what it needs and everything else standard-library (Squirrel, 9 October 2026, 16:16).
4. Private for now: CLAUDE.md, PLAN.md and DIARY.md stay committed here (Squirrel, 9 October 2026, 16:16).
5. Separate scripts, like `book-tools`: one executable script per command at the top of the
   repository, each a thin wrapper that imports its `main()` from a shared package, `videotools/`
   (Squirrel, 9 October 2026, 16:22).
6. The narration voice is configurable for each video: `narrate` takes the voice, speed and
   model from the video's own settings, with defaults in `~/.video-tools.conf` and flags that win
   over both; nothing about a voice is fixed in the code (Squirrel, 9 October 2026, 16:22).
7. Squirrel creates the GitHub repository `douglassquirrel/video-tools` (private) and pushes when
   he is ready; until then there is no remote (Squirrel, 9 October 2026, 16:22).
8. The first request (`inbox/done/request-from-training-video-2026-10-09.md`) is the scope: the
   eight commands and the package above, in its build order (Squirrel, 9 October 2026, 17:15).
9. Command names as listed; the speech-model set-up is README steps typed by the user, not a
   command that fetches (Squirrel, 9 October 2026, 17:01, recorded in the request).
10. On-screen labels reach scene code by their exact text from the script's "On screen" list
    (Squirrel, 9 October 2026, 17:01).
11. Frame-image tests compare drawn frames with stored images at reduced size, with a tolerance
    (Squirrel, 9 October 2026, 17:01).
12. One venv for dev tooling and the commands; PLAN.md names which commands still run on the
    Mac's Python 3.9 (Squirrel, 9 October 2026, 17:15: "both of your proposals").
13. The scene-code interface as item 4 describes it, and four assumptions: the venv from
    Homebrew Python 3.12 (this Mac has no 3.13); `work/narration/timing.json` beside the clips,
    cues numbered from 01; `assemble --replace` covers its intermediates only, never the finished
    video; items 7, 8 and 9 built before 4 and 5 (Squirrel, 9 October 2026, 19:45: "assumptions
    all ok, please continue").
14. The second request (`inbox/done/request-from-training-video-2026-10-09-2.md`), all seven
    items, with three choices: the brand reader reads only `Key | Value` tables rather than the
    kit moving its contrast table; a `VIDEO_TOOLS_PYTHON` setting the wrappers honour, with a
    README section, rather than the section alone; the ripple and polygon-clipping helpers added
    to the package rather than left to scene code (Squirrel, 9 October 2026, 19:01: "1. agreed
    6. agreed 7. agreed. Go ahead and make the update per the request").
15. The third request (`inbox/done/request-from-training-video-2026-10-09-3.md`), all three
    items, with the missing-package message naming the package and the pip line, and
    `VIDEO_TOOLS_PYTHON` only when it is unset (Squirrel, 9 October 2026, 19:31: "agree with
    your thoughts on the package message. Go ahead and fix.").
16. The fourth request (`inbox/done/request-from-training-video-2026-10-09-4.md`): item 1 with a
    new `side-panel-heading` scene property, and item 3; not item 2 (Squirrel, 9 October 2026,
    19:50: "Do 1 (with the new property) and 3.").
17. The fifth and sixth requests (`inbox/done/request-from-training-video-2026-10-09-5.md`,
    `…-6.md`), in full, request 5 first (Squirrel, 9 October 2026, 20:14: "go ahead"). The hand's
    neutral default colours are Claude's choice, recorded in the README.
18. The seventh request (`inbox/done/request-from-training-video-2026-10-09-7.md`): `check-script`
    checks the scene code statically (Squirrel, 9 October 2026, 20:52: "go ahead").
19. The eighth request (`inbox/done/request-from-training-video-2026-10-09-8.md`): `check-video`'s
    sheet labels in a strip under each frame (Squirrel, 9 October 2026, 21:07: "go ahead").
23. The twelfth request (`inbox/done/request-from-training-video-2026-10-10-12.md`), both items,
    with the cue-change sheets and the warning as a flag on `stills` and the warning on by
    default (Squirrel, 10 October 2026, 09:00: "flag on stills, warning on by default. go ahead").
22. The eleventh request (`inbox/done/request-from-training-video-2026-10-10-11.md`), all three
    items, with the phoneme listing as a flag on `narrate --dry-run` rather than a new command
    (Squirrel, 10 October 2026, 08:46: "Right to verify. OK to put flag on narrate."). Squirrel's
    standing OK on the training-video side lets that project *send* requests; each is still
    OK'd here before anything is done (Squirrel, 10 October 2026: "My standing OK to them is to
    request changes, not for you to do them").
21. The tenth request (`inbox/done/request-from-training-video-2026-10-10.md`), both items,
    with On screen labels checked against the display font only (Squirrel, 10 October 2026,
    07:50: "display font only. go ahead").
20. The ninth request (`inbox/done/request-from-training-video-2026-10-09-9.md`), all four
    commands, with three choices (Squirrel, 9 October 2026, 21:44: "1. exit 1 2. use current
    timing plus --offset. always contrast ratios", then "go ahead!"): `frame-hashes --compare`
    exits 1 when any frame differs; `compare-frames` takes the old video's scene starts from the
    current `timing.json` plus `--offset`; `brand-preview` always lists the contrast ratios.
