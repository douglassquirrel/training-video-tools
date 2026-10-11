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
a curtain known to scene code, and stills at cue changes with a warning, item 14; and (10 October 2026,
10:40) from the thirteenth and fourteenth, `inbox/done/request-from-training-video-2026-10-10-13.md`
and `…-14.md` ("Settled" 24 and 25): choreography in the script drawn from the video-elements
library, item 15 (its format a proposal awaiting approval), and credits on the end card, item
16; and (10 October 2026, 23:12) from the fifteenth,
`inbox/done/request-from-training-video-2026-10-10-15.md` ("Settled" 29): offsets wherever an
anchor is read, an arrow that draws on and needs no Where, and a warning for a blank Size on an
element whose size is nominal, item 17; and (10 October 2026, 23:59) from the sixteenth,
`inbox/done/request-from-training-video-2026-10-10-16.md` ("Settled" 34): an empty label is not
checked, item 18; and (11 October 2026, 00:15) from the seventeenth,
`inbox/done/request-from-training-video-2026-10-11-17.md` ("Settled" 37): a callout's leader
colour, curved and dashed arrows, a member's own colours, a cast on title and end cards, and
turning a member, item 19; and (11 October 2026, 00:55) from the eighteenth and nineteenth,
`inbox/done/request-from-training-video-2026-10-11-18.md` and `…-19.md` ("Settled" 39 and 40):
steady moves, dimming, spans across cues and percentages, a CSV's columns and rows, item 20, and a
repeating flash, item 21; and (11 October 2026, 07:08) from the twentieth,
`inbox/done/request-from-training-video-2026-10-11-20.md` ("Settled" 41): a text parameter read
from a file and its lines chosen, item 22. CLAUDE.md says how the work is done; this file says what
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

## 15. Choreography in the script, drawn from video-elements (request 13; Squirrel, 10 October 2026, 10:36: the three details settled, "go ahead and do the format and get my approval on that")

A video's own code is mostly choreography: "this appears at cue 2 after 0.4 s, moves there,
highlights, gets a label". The request asks for the script to say it, in Markdown Squirrel reads
and approves with the words, and for video-tools to do it, drawing the things themselves from
the `video-elements` library (`~/projects/code/video-elements/`, its own repository, read-only
from here), so a video's folder holds a script, data and sources and no code except for the
genuinely unusual, which stays possible as a scene module.

### Where the library is (item 1)

Two settings in `~/.video-tools.conf`, each also a flag on every command that draws
(`stills`, `render`, `frame-hashes`, `compare-frames`) and on `check-script`, the flag winning
(Squirrel, 10 October 2026, 10:36: "yes", "repo root"):

- `VIDEO_ELEMENTS_DIR` / `--elements DIR`: the root of the video-elements repository, the folder
  holding the package `videoelements/` and the drawings `elements/`. At the point of use the
  command puts that folder on Python's import path, imports `videoelements.library`, and opens
  that folder (the library reads `elements/` and `licenses/` under it at once; video-elements'
  request of 10 October 2026, 12:59, `inbox/done/request-from-video-elements-2026-10-10.md`,
  OK'd 13:02). The package is never installed into this repository's venv.
- `RSVG_CONVERT` / `--renderer PATH`: the SVG renderer, passed through to the library as its
  `renderer`; absent, the library's own default (`rsvg-convert` on PATH). The training-video
  project's Linux shell runs one extracted from a package, not on PATH.
  **Built 10 October 2026, 13:45**: `config.KEYS` has both (`~` expanded in the folder),
  `videotools.elements.add_arguments` puts the flags on the five commands and
  `elements.settings(args, conf)` resolves them, flag first. **Increment 2, 14:10**:
  `elements.open_library(folder, renderer)` puts the root on `sys.path` once, imports
  `videoelements.library` and calls `open(folder, renderer=…)` (no renderer: the library's
  default), with the four refusals above plus a package that cannot be imported, each one
  `cli.Failure` (exit 3; the library's `.problems` listed under one line); tested against the
  invented library `tests/stubs/video-elements/` (a stub `videoelements` package reading the
  settled rows, elements `pot` (svg) and `table` (code), a register). Nothing calls it yet.
  **Increment 3, 14:40**: `videotools.choreography` reads the four sections (`script.parse`
  hands it their raw lines) into `scene["cast"]`, `scene["moves"]` and `scene["panels"]`
  (`{"mistake"|"right way": {"cast", "moves"}}`): a cast row `{name, element, where, size,
  params, line}` with Where as `{kind: pixels|region|anchor, …}`, Size as `None` or `{w, h}`
  and Parameters as `{name: value}` (shlex-split, quotes removed); a move `{cue (None in a
  panel), start, end, action, line}` with times as `("start"|"end", offset)` pairs and the
  action as `{kind: show|hide|move|param|set|state, …}`. Every malformed line is a problem
  naming it; a row with any problem is left out of the cast; a table with the wrong header is
  one problem and its rows are not read. What a row means is increment 4.
  **Increment 4, 15:20**: `choreography.check(scene, tl, lib, folder)` lists every problem of
  "Checks" below (elements, anchors with patterns and indices, the pieces' and the library's
  parameters by kind and range, data files and their row counts, states, labels, cues, times,
  shown twice or never, panels without a mistake cue), and `check-script` calls it for every
  described scene, opening the library from the settings only when a cast names a library
  element (one problem when it cannot be; the pieces are still checked) and building each
  scene's timeline from `timing.json` or the estimate. An index up to a data file's row count is
  allowed (whether its first row is a header is the element's business; the element refuses at
  draw time). Pieces' parameters: `pill` and `callout` `text`, `size`, `fill`, `colour`, `anchor`
  (+ `target`); `text` `text`, `size`, `role`, `colour`, `anchor`; `badge` `ok`, `r`; `hand`
  `angle`, `scale`, `mirror`, `label`; `arrow` `from`, `to`, `colour`, `width`; `state=` on a
  library member is its initial state. **Increment 5, 15:45**: `scenes.described(scene)`;
  `needed` drops `draw` for a described scene and `mistake`/`right_way` for a described panel;
  `load` returns None for a described step scene with no `code`; `check_code` and `load` refuse
  a step scene with neither as "has no 'code' property and no Cast, so nothing can draw it";
  `frame.draw_frame` and `mistake_panels` draw what the module has and skip what it has not.
  **Increment 6, 16:30**: `videotools.perform` draws a described cast: `Performance` resolves
  each member's alpha (its shows and hides in time order, each eased over its span, a panel
  member with no show at 1 from the start) and rect (its Where: area pixels, a region it is
  fitted into, or another member's box anchor plus an offset, resolved lazily so it follows;
  then its moves, each gliding from where it was), reads a `rows` file into rows and converts
  parameters by the description's types, and draws in cast order: `pill`, `text`, `badge`,
  `hand`, `callout` and `arrow` through the frame's methods, a library element through
  `el.draw(frame, rect, state, params, alpha)`, keeping the anchors it returns for members
  placed by them (a computed anchor of a member later in the cast is a refusal). `frame.Video`
  takes the library settings, opens the library only when a cast names a library element,
  and refuses a described scene's problems (`choreography.check`, exit 3) before anything is
  drawn; `draw_frame` performs the scene's cast before the module's `draw`, `mistake_panels` a
  described panel's cast in the panel body's pixels before the module's body. The four drawing
  commands pass `--elements`/`--renderer` or the config through `elements.from_args`.
  **Increment 7, 16:55**: `Performance.params` gives a member's parameters and state at t: the
  cast row's values converted by the description (the pieces' numbers as numbers), then its
  moves in time order: `NAME.PARAM A → B` eased over the span for a number (an integer stays
  whole; before the span the parameter is absent, so the element's default or the cast's value
  holds), a set of a number eased from its current value, a set of a word at the span's start,
  `NAME STATE → STATE` the name after and `(from, to, progress)` part-way; the pieces' own
  parameters (a badge's `r`, a pill's `size`) animate the same way. **Increment 8, 17:40**:
  anchors. A member's anchor is what its draw returned once it is drawn (a library element's
  anchors, computed ones included; a pill's, a text's and a badge's real box, the text's box
  being its width by its type size above the baseline); before it is drawn, a box anchor comes
  from its rect and a library element's *fixed* anchor is scaled into the rect as the element is
  fitted (uniformly, centred: to be confirmed against the real library's geometry in the Tier 3),
  so a member placed by a fixed anchor may come anywhere in the cast; a *computed* anchor (the
  description says `computed`, or it is indexed) exists only after its member is drawn, so a
  member placed by one, moved to one, or pointing a callout or an arrow at one must come after
  that member in the cast: `check-script` says so by line, and `perform` refuses if it is met
  at draw time anyway. **Increment 9, 18:00**: the curtain for free. `Performance.alpha`
  multiplies by `tl.before_curtain(t)` for a scene member whose first show starts before the
  mistake cue and that no move at a later cue names; a member named after the mistake, or first
  shown at or after it, is left to its moves; a panel's members and a scene with no mistake are
  untouched. **Increment 10, 18:25**: a panel's own moves count from the moment the panels start
  to rise (pinned by a member shown 1.0–1.4 s in, absent while covered before it, there after;
  the test seen to fail with the panel's clock broken on purpose); and the request's proof, a
  described scene and the same scene written as a module give equal frames through
  `frame-hashes` (scene A of the example both ways against the invented library, `--compare`
  exit 0). **Increment 11, 19:00**: the README's "Describing a scene in the script" (the format,
  the pieces, the moves, the panels, the curtain, the checks, a real run against the real
  library on a scratch copy of the example: `person`, `sun`, `gauge`, `calendar`, a callout and a
  tick on the needle's computed anchor, looked at by eye), the flags in the five usage lines, a
  dated note, two known limits; and a find from that run: a library refusal at draw time (the
  real `spreadsheet` needs the `mono` font roles the example kit lacks) came out as a
  traceback, now one line in words, exit 3, pinned by a test with the stub refusing.
  **Increment 12, 19:40, the Tier 3** on a scratch copy of the training-video project's second
  video (its script, assets, scenes, timing and brand kit copied to the session's scratchpad;
  v4 read in place; nothing written into that project): scene A2 described in the format
  against the real library (`spreadsheet` at its natural size `564x262`, `text` pieces for the
  working and for the panels' cell text since there is no `formula-bar`, ticks and the hand by
  `row.N` with offsets, `cell-alpha.3.2` for the landing total), `check-script` clean, `stills`
  at eight times and `compare-frames` against v4 at 7.0, 16.6 and 24.3 s, mean differences 2.3,
  2.5, 2.9 per channel, looked at by eye: the same picture. Three finds: a bug in the check,
  which ordered a show or hide written from the cue's end (`end-1.2 s`) by its raw offset, so a
  hide at `end-1.2` looked earlier than a show at `7.7 s` (fixed test-first); the curtain rule
  hid the "Sample output" tag that v4 keeps through the mistake, which the format could not
  say: the `keep` action was added (above); and a data-driven element is fitted into its Size,
  so a `spreadsheet` needs its natural size given (the README says so). Item 15 is complete
  but for what the training-video project does on its side (re-describe A2 and B in its own
  script, compare, retire modules).

A script with a described scene and no library setting, a folder that is missing or has no
`videoelements/` or `elements/`, or a library that refuses to open: one line in words naming the
setting and the folder, exit 3. A script with no described scene never needs the library.

**The interface**, video-elements' settled text (its PLAN.md "The interface video-tools calls";
Squirrel, 10 October 2026, 10:36: "go with the choice in video-elements"; the first line's comment
changed by its request of 12:59, OK'd 13:02). The same words are in both READMEs; a change goes
through Squirrel to both:

```python
from videoelements import library
lib = library.open(path, renderer="rsvg-convert")   # the library's root folder (elements/ and licenses/ inside); refuses in words, exit 3
el = lib.element("spreadsheet")               # description: size, anchors, states, params, colours
anchors = el.draw(frame, rect, state=None, params=None, alpha=1.0)
#   frame: video-tools' scenes.Frame (ctx, brand, colours, label(), text(), …)
#   rect:  (x, y, w, h) in frame pixels; the element is fitted into it keeping its proportions,
#          or, when its description's `fit` is `stretch`, drawn to that width and height
#   state: a name, or (from, to, p) for a change part-way (a cross-fade, or a morph for code)
#   params: the element's animatable parameters by name; unknown or out-of-range ones refused
#   returns {anchor name: (x, y)} in frame pixels, for labels, hands and arrows
el["fit"]                                     # "ratio", "stretch" or "natural" (request 3)
el.natural_size(frame, params=None)           # request 3, item 5: (w, h) in pixels for an element whose
#   fit is "natural" (spreadsheet, prompt-box, file-chip, diff): the size at which it is drawn at scale 1
#   for those params, text measured at the brand's font-size-scale; params are checked as for draw;
#   None for any other element (its size does not come from its parameters)
el["counts"]                                  # what each * of an indexed parameter or anchor counts, by pattern:
#   {"cell-alpha.*.*": [{"what": "row", "of": "rows"}, {"what": "column", "of": "rows"}], "tab-box.*": [{"what": "other", "of": None}]}
#   what: "row" (a data row of the rows parameter `of`, its header not counted), "column" (a column of it),
#   "line" (a non-blank line of the text parameter `of`), "other" (not something a caller can count; `of` None).
#   Every indexed name of the element is a key; an element with none has {}
el["params"]["rows"]["header"]                # for a rows parameter: the name of the boolean parameter that says its
#   first row is a header (not a data row), or None when the element has no such switch
lib.credits(names)                            # request 2: credit lines for the elements a video used
```

The `counts` and `header` lines are video-elements' additions of 11 October 2026, 07:29 (its
reply, `inbox/done/reply-from-video-elements-2026-10-11.md`; "Settled" 43), used by item 23.
The `fit` and `natural_size` lines and the longer `rect` comment are video-elements' additions of
10 October 2026, 23:32 (its note, `inbox/done/request-from-video-elements-2026-10-10-2.md`;
"Settled" 30), used by item 17, 3; `diff` joined the natural elements with its note of 23:53
(`inbox/done/request-from-video-elements-2026-10-10-3.md`; "Settled" 33).

### The choreography format (item 2; approved: Squirrel, 10 October 2026, 13:24, "choreography format is fine")

Two new `###` sections in a scene, after `### On screen`, and two for the mistake panels. Prose
under `### Pictures` stays for people. The training-video project's `SCRIPT-FORMAT.md` gets this
text once approved (their side).

```
## Scene <key>: <name>
   (property table)                     `code` now optional: a scene may have a module, a
   ### Narration                        description (Cast and Moves), or both
   ### Side panel
   ### On screen
   ### Pictures                         prose for people, as now
   ### Cast                             table: everything on screen, named once
   ### Moves                            list: what happens, by cue
   ### Mistake                          the "Mistake" panel: a Cast table, then an optional Moves list
   ### Right way                        the "Right way" panel: likewise
```

**The cast.** A table `| Name | Element | Where | Size | Parameters | Notes |`; the tools read the
first five columns, Notes is for people. Members are drawn in the table's order (later over
earlier).

- **Name**: letters, digits and hyphens, unique in the scene (`sample`, `tick-1`). Moves and
  anchors refer to it.
- **Element**: a library element by name (`spreadsheet`, `person`), or one of video-tools'
  own pieces, which take the same columns: `pill`, `callout`, `text` (a label, drawn by
  `frame.tag`, `frame.callout`, `frame.text`), `badge`, `hand`, `arrow`. The request's "label …
  at", "arrow from … to" and "hand at" are these: a label is a cast member, so it is shown,
  hidden and moved like anything else. The chrome's pieces stay here; everything else comes from
  the library (video-elements PLAN.md, "The starter set").
- **Where**: the member's top-left (its anchor point for a label, hand or badge), as `X Y` in the
  animation area's pixels (0 0 is the area's top-left; the area is 1422 × 818 at 40, 118 of the
  frame); or a region, `left`, `right`, `centre`, `top-left`, `top-right`, `bottom-left`,
  `bottom-right`, `full` (the halves and quarters of the area: the member is centred in it); or
  another member's anchor, `sample.row.3`, with an optional offset, `sample.row.3 + 40 -12`.
  Anchors are the element's own, from its description (`row.N`, `cell.R.C`, `tab.N`, `head`,
  `hand`, …), plus `top-left`, `top-right`, `bottom-left`, `bottom-right` and `centre` of any
  member's box. A member placed by another's anchor follows it when that one moves.
- **Size**: `W` (the width in pixels, the height from the element's own proportions) or `WxH`;
  blank for the element's own size (an SVG's, or what a data-driven element makes of its data
  and parameters). A region with a blank size fits the element inside it.
- **Parameters**: `name=value` pairs, space-separated, values with spaces in double quotes:
  `rows=assets/sample-output-2024-04.csv numeric=2 row-height=58 text-size=22`. The names are
  the element's, from its description; the state of a multi-state element is `state=lump`. A
  value naming a file under the video's folder (`assets/….csv`, `.txt`) is read by video-tools
  (CSV into rows, text as it is) and handed to the element as that parameter: the library never
  reads the video's folder. **The description's rows, as video-elements reads them** (its reply of
  10 October 2026, 13:18, `inbox/done/reply-from-video-elements-2026-10-10.md`; "Settled" 27):
  a parameter's type is one of `number MIN MAX DEFAULT`, `integer MIN MAX DEFAULT`, `colour
  ROLE`, `boolean`, `text DEFAULT` (data, may be long and multi-line), `label DEFAULT` (words
  the viewer reads) or `rows` (the data, always required, no default: a list of rows of strings
  as the csv module gives them), exposed as `params[name] == {"type": …, "min", "max",
  "default"}`; an indexed parameter or anchor has one `*` per index as a whole segment between
  dots (`highlight.*`, `cell-alpha.*.*`, `row.*`, `cell.*.*`), exposed with the pattern as its
  key, and a script fills the indices in **from 1** (row 1 the first data row, tab 1 the first
  tab), `draw` taking `params` keyed by the dotted names (`{"highlight.3": 0.18}`) and returning
  anchors the same way (`{"row.3": (x, y)}`); an anchor's value is a pair of numbers (fixed, in
  element units) or the string `"computed"` (a code element's `draw` works it out; every indexed
  anchor is computed). An index past the data is refused by the element at draw time, in words.
  A quoted value for a `label` parameter (a tab name, a prompt, a file name, a pill's `text`)
  goes through `frame.label`, so the On screen check holds; a `text` parameter is data (cell
  values) and is not checked. The pieces' own parameters: `pill` and
  `callout`: `text`, `size`, `fill`, `colour`, `anchor` (`left`, `centre`, `right`), and for
  `callout` `target` (an anchor); `text`: `text`, `size`, `role`, `colour`, `anchor`; `badge`:
  `ok` (`yes`/`no`), `r`; `hand`: `angle`, `scale`, `mirror`, `label`; `arrow`: `from`, `to`
  (anchors), `colour`, `width`. Colours by name, as `frame.colour` resolves them.

**The moves.** A list, one move a line, each `cue N[, TIME]: ACTION`:

- **`cue N`** is the cue's number in the scene's Narration; **TIME** is `A s` (from A seconds
  after the cue's start, for 0.6 s), `A–B s` (from A to B), or `over the cue` (from the start
  to the cue's end). A or B may be negative, or `end`, `end-1.2` (relative to the cue's end).
  No TIME: `0–0.6 s`. Every change is eased (smoothstep, as `tl.p` eases) over its span; a
  change with an empty span is a step.
- **`show NAME[, NAME…]`**: fade in. **`hide NAME[, …]`**: fade out. A member is on screen from
  its show to its hide; before its first show it is not drawn at all (the request's "shown at a
  cue and hidden at another, with frames sampled for its presence"). **`keep NAME[, …]`**: changes
  nothing, but names the members at that cue, so the curtain rule leaves them (added 10 October
  2026, 19:30, from the Tier 3: the real scene A2's "Sample output" tag stays through the
  mistake, and the rule would have hidden it).
- **`move NAME to WHERE`**: glide to a place written as in the Where column.
- **`NAME.PARAM A → B`**: animate a parameter (`prompt.progress 0 → 1`, `sample.rows-shown 0 → 3`,
  `gauge.level 0.2 → 0.9`); **`NAME.PARAM VALUE`**: set it (`sample.highlight-colour.3 correct`);
  **`NAME STATE → STATE`**: change state (`clay lump → vase`: a morph for a coded element, a
  cross-fade for drawn states). A parameter with an index (a row, a cell) is written with dots,
  `highlight.3`, `cell-alpha.3.2`; the names, their types and ranges are the element
  description's, and video-tools refuses what it does not list.

**The mistake panels.** `### Mistake` and `### Right way` each hold a Cast table (Where in the
panel's own pixels, 0 0 the panel body's top-left under its heading band, 690 × 728) and an
optional Moves list whose lines have no `cue N`: `0.4–0.8 s: show total` counts from the
moment the panels start to rise. A panel member with no show is shown from the start. Each
panel has its own small cast, as the request asks.

**The curtain for free.** A member shown before the mistake cue and not named in any move at or
after the cue that follows it is multiplied by `before_curtain`, so it fades while the panels
cover it and the glimpse of request 12 cannot be written by accident. One named after the
mistake (hidden, moved or changed at the next cue) is left to its moves.

**Labels**: every `text` parameter of a `pill`, `callout` or `text` member, and every library
parameter of type `label`, is checked against the scene's On screen list as `frame.label`
checks now, by `check-script` before drawing and again at draw time.

**With a module.** A scene with `code` and a description: the described cast is drawn first,
then the module's `draw(frame)` over it; a panel with a Cast table and a module: the cast, then
`mistake`/`right_way`. A scene with a description needs no `code`, and a described panel needs
no `mistake`/`right_way` function; `scenes.needed` and `check-script` ask for a function only
where no description covers it. A step scene with neither is refused by name, as now.

**Worked example: scene A2 of "App For That"**, re-described from its module
`videos/app-for-that/scenes/sample_output.py` (read, not copied), the module's frame pixels
turned into area pixels (X 110 → 70, Y 250 → 132). The element names and parameters assume
video-elements' `spreadsheet` (its PLAN.md starter set: `rows-shown`, per-row `highlight`,
per-cell alpha, anchors per cell and row) and one element the starter set does not have, a
`formula-bar` (the cell reference and its content), which the training-video project would
request from video-elements. The working lines are at fixed offsets where the module spreads
them over the cue's measured length; the compare with v4 shows whether that matters.

```markdown
### Cast

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| sample-tag | pill | sample.top-left + 0 -30 | | text="Sample output" size=22 fill=sheet-tab | |
| sample | spreadsheet | 70 132 | | rows=assets/sample-output-2024-04.csv widths="300 230" numeric=2 row-height=58 text-size=22 rows-shown=0 cell-alpha.3.2=0 | L. Chen's figure arrives from the working |
| working-1 | text | 760 352 | | text="8% of 12,500 = 1,000" size=36 role=display | |
| working-2 | text | 760 430 | | text="sector bonus 2% = 250" size=36 role=display | |
| working-3 | text | 760 508 | | text="closed April 15: + 500" size=36 role=display | |
| total | text | 760 586 | | text="= 1,750" size=40 role=display colour=accent | drops into the cell |
| checker | hand | sample.row.1 + 190 40 | | angle=3.3 scale=0.8 | someone else |
| tick-1 | badge | sample.row.1 + 40 0 | | ok=yes r=20 | |
| tick-2 | badge | sample.row.2 + 40 0 | | ok=yes r=20 | |
| tick-3 | badge | sample.row.3 + 40 0 | | ok=yes r=20 | |
| checked | pill | sample.row.3 + 40 80 | | text="checked ✓" size=24 fill=correct anchor=centre | |

### Moves

- cue 1: show sample-tag, sample
- cue 1, 0.5–1.7 s: sample.rows-shown 0 → 3
- cue 2, 0–0.5 s: sample.highlight.3 0 → 1
- cue 2, 0.4–0.8 s: show working-1
- cue 2, 1.8–2.2 s: show working-2
- cue 2, 3.2–3.6 s: show working-3
- cue 2, 4.6–5.0 s: show total
- cue 2, end-1.2–end-0.4 s: move total to sample.cell.3.2
- cue 2, end-1.2–end-0.4 s: hide total
- cue 2, end-1.2–end-0.4 s: sample.cell-alpha.3.2 0 → 1
- cue 4, 0–0.5 s: sample.highlight.3 1 → 0
- cue 4, 0–0.5 s: hide working-1, working-2, working-3
- cue 4, 0–0.4 s: show checker
- cue 4: sample.highlight-colour.1 correct
- cue 4: sample.highlight-colour.2 correct
- cue 4: sample.highlight-colour.3 correct
- cue 4, 0.3–0.6 s: show tick-1
- cue 4, 0.3–0.6 s: sample.highlight.1 0 → 0.18
- cue 4, 0.8–1.1 s: show tick-2
- cue 4, 0.8–1.1 s: sample.highlight.2 0 → 0.18
- cue 4, 1.3–1.6 s: show tick-3
- cue 4, 1.3–1.6 s: sample.highlight.3 0 → 0.18
- cue 4, 1.4–1.9 s: show checked
- cue 4, 2.2–2.6 s: hide checker

### Mistake

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| formula | formula-bar | 60 150 | 570x90 | ref="B4" text="='Sales export'!E5*10%+500" mono=yes | |
| wrong-sheet | spreadsheet | 120 330 | | rows=assets/sample-output-formulas.csv widths="230 200" row-height=50 text-size=20 box.3.2=mistake | a CSV of "=..." cells |
| wrong | badge | 610 600 | | ok=no r=30 | |

### Right way

| Name | Element | Where | Size | Parameters | Notes |
|---|---|---|---|---|---|
| answer | formula-bar | 60 150 | 570x90 | ref="B4" text="1,750" | |
| right-sheet | spreadsheet | 120 330 | | rows=assets/sample-output-2024-04.csv widths="230 200" numeric=2 row-height=50 text-size=20 box.3.2=correct | |
| answers-only | pill | 345 640 | | text="answers only" size=24 fill=correct anchor=centre | |
```

The scene's module is 60 lines; the description is 11 cast rows, 23 moves and 6 panel rows,
and the mistake cue's curtain needs no line at all (`working-1..3` are hidden at cue 4 by their
own moves; `sample` and `sample-tag` are named after the mistake, so they stay).

### Checks (item 3)

`check-script` reads the choreography (standard library, Python 3.9: the library's readers are
too, video-elements CLAUDE.md non-negotiable 4) and lists, each with its line: a cast table
with the wrong header or a row short of five cells; a name used twice; an Element that is
neither a piece nor in the library; a Where that is not pixels, a region or a member's anchor;
an anchor, state or parameter the element's description does not have, or a value out of its
range; a parameter file that does not exist; a cue number the scene does not have; a time past
the cue's length (measured from `work/narration/timing.json` when it exists, else the
words-a-second estimate, said which); an index of 0 or past the data's rows for an indexed
parameter or anchor whose data video-tools read; a move naming no cast member; a label not in the On
screen list; a cast member never shown; one shown again while still shown; a panel section in a
scene with no mistake cue; a step scene with neither `code` nor a Cast. With no library
setting and a script that needs one, one problem naming the setting. `stills --cue-changes` and
its warning work on described scenes as on coded ones; `frame-hashes` pins them.

### How it is drawn

The description is read once per video (with the script), not per frame. For each frame the
interpreter walks the cast in order: the member's alpha from its shows and hides (times
`before_curtain` where the curtain rule applies), its place from its Where and moves, its
parameters from their sets and animations at `t`, then `el.draw(frame, rect, state, params,
alpha)` for a library element or the frame's own method for a piece; the anchors returned feed
the members placed by them. Everything video-tools draws today stays as it is: the header,
tracker, caption band, side panel, panels and cards.

**Not doing** (unless asked): the camera (a described scene is flat; the bed's turning stays a
module); a cast member drawn by more than one element; conditions or loops in a description.

### Order of work

Test-first against an invented library in `tests/` (two tiny elements, one SVG through a stub
`rsvg-convert`, one data-driven, with invented `ELEMENT.md` files in the library's settled
shape), in this order: the config settings and flags, the library's import and refusals; the
Cast and Moves parser with every check above; the interpreter in the frame (show, hide, move,
parameters, states, anchors), each pinned by sampled frames; the curtain rule, with
`stills --cue-changes` quiet on it; a described scene and the same scene as a module through
`frame-hashes` equal; README ("Writing a video's script": the format), "Notes for users", lint
as its own pass. Real drawing waits on video-elements' reader and first elements (its steps 3
and 4); the first real run is a Tier 3 check on scene A2 against v4 with `compare-frames`
(the training-video project's side), recorded in DIARY.md.

## 16. Credits for external art on the end card, and a credits file (request 14; Squirrel, 10 October 2026, 10:36)

Builds on item 15. The videos use art from outside sources (Tabler Icons, Open Peeps, Fluent
Emoji: CC0 or MIT, none requiring credit); Squirrel wants to give it, briefly, on the end card.
video-tools knows which elements a video draws (every scene's cast and its panels' casts);
video-elements knows their sources (`lib.credits(names)`: the credit lines without duplicates,
grouped by category in a stable order, each with its licence name, an unknown name refused in
words).

1. **Collect**: the library elements named in every cast and panel cast of the video, in script
   order, passed once to `lib.credits`. Pieces (`pill`, `hand`, …) are not elements and credit
   nothing.
2. **Draw** the lines on the end card below the two it draws today (the script's `credit`, the
   brand's `illustration-credit`), in the same style (body, 22 px, muted, centred, 36 px apart,
   fading in with them), wrapped at the card's text width when long, the lines moving up as a
   block if they would otherwise reach the bottom margin; a video with no library elements draws
   exactly today's card (pinned by the stored frames and `frame-hashes`).
3. **A script setting** `element-credits`: `auto` (the default: the collected lines), `none`, or
   the wording itself, which wins and is drawn as one line (wrapped). Unknown settings keys stay
   refused; documented for the training-video project's `SCRIPT-FORMAT.md`.
4. **Approval**: `check-script` prints the credit lines the end card will show, after the
   `added:` lines, as `credits:` lines; and the characters-a-font-lacks check (item 12) covers
   them like any label.
5. **A credits file** beside the finished video, written by `assemble` after the video:
   `<output>.credits.txt` next to `<output>.mp4` (`out/video.credits.txt`; with `--out FILE`,
   beside FILE): every source used, its credit line, its licence name and the elements it
   supplied, one source per paragraph, for a video description or a client. Like the video it
   is never replaced: `assemble` refuses before starting if either exists, `--replace` covering
   its intermediates only as now ("Settled" 13; Claude's choice for the file, recorded in
   "Settled"). A video with no library elements writes no credits file (and nothing is said:
   `assemble` has no dry run, and its output for such a video is unchanged).

Order of work, test-first with the invented library (two elements from two invented sources):
the setting and its check; the collection; the end card (pixels where the lines go; `none`
today's card; wording replacing the lines; a long line wrapping without reaching the website
line); `check-script`'s lines; the credits file and its refusal; README, "Notes for users", lint.
After item 15's parser, which it collects from.

**Built, 10 October 2026.** Increment 13 (20:20): `element-credits` in the Settings (optional,
default `auto`); `videotools.credits`: `elements_used` (every cast's and panel's library
elements, in script order, once each), `known` (those the library has: an unknown one is the
checks' problem, not a credit), `lines` (`none` → nothing; wording → itself; `auto` → one line
per category, `Icons: Invented Icons`, from `lib.credits`), `sources` (for the file: credit
line, category, licence, elements); `check-script` opens the library once (`library_for`) for
the checks and the credits, prints `Credits on the end card:` and the lines (or `none`) after
the `added:` lines when the script uses library elements or sets the setting, and runs the
font check over the lines as `end card credit line`. The invented library gained a second
source (Invented Peeps, CC0, the `table`), so two lines can be seen. Increment 14 (20:35):
`frame.end_card` draws the lines after the two it drew (body, 22 px, muted, centred, 36 px
apart, with their fade), each wrapped inside a 260 px margin each side, the whole block moved
up when its last line would come within 90 px of the bottom; `none`, and a video with no
library elements, draw byte for byte today's card (pinned). Increment 15 (20:55): `assemble`
takes `--elements`/`--renderer`; when the video uses library elements it opens the library,
refuses an existing `<output stem>.credits.txt` before anything is written (`--replace` never
covers it), and after the video writes the file (`credits.file_text`: the title, then one
paragraph per source, `Category: credit line`, `licence:`, `elements:`) and prints `Wrote …`
after the sha256 line; whatever `element-credits` says, since the file is the record. Item 16
complete.

## 17. Offsets where an anchor is read, an arrow that draws on, and a blank Size (request 15; Squirrel, 10 October 2026, 23:09: "request 15 ok")

Four things the training-video project found describing its scenes A2 and B for real against
`08076e3`. Builds on item 15; the format's words there stand, with these additions.

1. **The offset applied wherever an anchor is read** (a bug). An arrow's `from` and `to` and a
   callout's `target` are written as a Where's anchor is, `member.anchor` or `member.anchor + X
   Y`; the offset was parsed and dropped (`perform.Performance._point`), so
   `from="export.right + 21 8"` landed on the bare anchor. The point is the anchor plus the
   offset, as in the Where column.
2. **An arrow that draws on, and needs no Where.** `arrow` gains two parameters: `progress`, a
   number from 0 to 1 (default 1), how much of the arrow is drawn from its tail
   (`draw.arrow`'s own `progress`), animated like any other (`cue 6, 1.0–1.8 s:
   paste-arrow.progress 0 → 1`), a value outside 0 to 1 a problem in `check-script`; and `head`,
   `yes` or `no` (default `yes`): whether the arrowhead is drawn (Squirrel, 10 October 2026,
   23:11: "agree with your assumption about head"). As for every parameter, before an
   animation's span the cast's value or the default holds, so an arrow shown before it grows
   has `progress=0` in its cast row. An arrow's Where may be blank, since `from` and `to` place
   it: its box, for the members placed by its corners and centre, is then the rectangle
   spanned by its two ends. An arrow with a Where keeps today's box (a point at the Where). Any
   other piece or element with a blank Where is refused as now.
3. **A blank Size: the element's natural size when it offers one, a warning when its size is nominal and it does not.**
   A code element whose description's size is nominal (the real `spreadsheet`, `prompt-box`,
   `file-chip`, `diff`: what it draws depends on its data or text) is fitted into that nominal
   size when the Size column is blank, silently, with tiny text. **The warning:** `check-script` lists
   a warning for each such cast member, by line, after the problems, under its own heading
   (`N warning(s):`); warnings do not change the exit code (0 when there are no problems;
   Squirrel, 10 October 2026, 23:11), and a member with a Size has none. video-tools learns
   that a size is nominal from the Notes cell of the `size` row in the element's `ELEMENT.md`
   (it begins `nominal`), read from the description's `folder`, because the description the
   library returns does not carry it ("Settled" 31). **The natural
   size** (built 10 October 2026, after video-elements' note of 23:32 with the interface, item
   15; Squirrel, 23:11: "do wait for natural-size in video-elements (it's being worked on
   now)", and it came): a library member with a blank Size whose element's `fit` is `natural`
   is drawn at `el.natural_size(frame, params)`, asked with the parameters `draw` is given at
   that moment (the data file read into rows, the moves applied), so its text is at the sizes
   its parameters say. Placed by pixels or by an anchor, that is its size; in a region it is
   centred at that size and not scaled to the region ("Settled" 32). A refusal from
   `natural_size` is one line in words naming the member, exit 3, as a refusal from `draw` is.
   A Size that is given wins, as before, and the library fits the element into it.
   `check-script` cannot ask for the size (it has no frame) and does not need to; the warning
   is now given only for an element that does not offer its natural size (its `fit` is not
   `natural`), and a library without the `fit` key is treated as offering none. That was the
   real `diff` until video-elements `5f98a74` gave it a natural size too (its note of 23:53);
   since then no real element is warned of, and the warning stays for any that comes later.
4. **A `WxH` Size reaches the element as its rect**, whatever the element's own proportions,
   so an element video-elements marks as stretching (its request 3, item 4) is given the shape
   the script says. Already so; pinned by a test of its own.

Order of work, test-first against the invented library: the offset (a reproducing test for an
arrow and for a callout, then the fix); `progress`, its range in `check-script`, `head`; the
blank Where (the parser, the check, the box); the warning in `check-script`; the pinning test
of 4 (seen to fail with the code broken on purpose); README ("Describing a scene in the
script"), "Notes for users", lint as its own pass; a Tier 3 run against the real library.

## 18. An empty label is not a label (request 16; Squirrel, 10 October 2026, 23:59: "check inbox and do what it says")

A library element's `label` parameter may be empty by design: the real `formula-bar`'s `ref` is
"empty for none", written `ref=""`. `check-script` refused it as `draws ''`, which is not on any
On screen list. Nothing is drawn for an empty label, so there is nothing for the viewer to read
and nothing to check.

1. **A library element's label parameter that is empty** (`""`, the value after its quotes are
   removed) is not checked against On screen: by `check-script`, in a cast row and in a move
   that sets it, nor at draw time, where `frame.label("")` returns `""` without looking at the
   list (an element, or a video's own scene code, that passes an empty label through the check
   is drawing nothing). A label that is only spaces is still a label and still checked ("Settled"
   35).
2. **The pieces** ("your call, said in the README"; "Settled" 36): the `text` of a `pill`,
   a `callout` or a `text` is what the piece is for, so an empty one stays a problem, in plainer
   words than before (`'text' is empty, so there is nothing to draw`), in the cast and in a
   move. A `hand`'s `label` is optional, so `label=""` means no label, as leaving it out does:
   not checked, and no roundel drawn.
3. **A label an element does not draw in some state** (the `formula-bar`'s `text` when
   `placeholder=yes`): the library's description says so only in prose, so video-tools cannot
   tell, and `check-script` goes on checking a value that is given. It is left to the script's
   author: leave the parameter out, or give it empty. The README says so.

Order of work, test-first: the library's label in `check-script` (cast and move; a label not
on the list and one of spaces still refused); the pieces' empty text and the hand's empty
label; `frame.label("")`; a described scene with an empty label drawn through the invented
library, whose stub now passes every label it is given through `frame.label` as the real
elements do; README, "Notes for users", lint as its own pass; a Tier 3 with the real
`formula-bar`.

## 19. What the rest of a video needs to be described (request 17; Squirrel, 11 October 2026, 00:13: "Go ahead with request 17 as written")

The training-video project is making a v5 of "App For That" with every scene described and no
Python of its own. Its scenes A2 and B are described already; these five things are what its
other ten modules do that the format of item 15 could not say. Each adds to that format.

1. **A callout's leader colour.** `callout` gains `leader`, a colour name for its leader line
   and dot (default `ink`, as `frame.callout` has it).
2. **Curved and dashed arrows.** `arrow` gains `via="P; P"`: exactly two control points
   separated by `;`, each written `X Y` in the pixels its cast uses (the animation area's in a
   scene, the panel's in a panel, the frame's on a card) or as a member's anchor with an optional
   offset; the arrow is then the cubic curve from `from` by the two points to `to`, and
   `progress` draws it on along the curve (`draw.arrow` does both already). And `dash="ON
   OFF"`, two numbers above 0: the line is dashed, the head stays solid. Anything else in
   either is a problem by line. A computed anchor in `via` follows the cast-order rule as `from`
   and `to` do. An arrow with a blank Where keeps the box its two ends span, curved or not.
3. **One member in other colours.** A library member's Parameters may map the element's colour
   roles to colours of its own, `colour.<role>=<colour name>` (`colour.fill=doc`): the role must
   be in the element's Colours table and the name one `frame.colour` knows (the script's
   Colours, else the brand's roles), each refused by line in `check-script` when the colours are
   known to it (the kit read) and at draw time in any case. The element is then handed a frame
   whose colours carry those roles, which is how video-elements already takes a role's colour
   (a role named in the frame's colours wins over the element's default); nothing in the shared
   interface changes, and video-elements is asked to keep that true. Not animatable: a move
   cannot name `colour.<role>`. The pieces keep their own `fill` and `colour`.
4. **A cast on the title and end cards.** A scene of kind `title` or `end` may have `### Cast`
   and `### Moves`. The cast is drawn over the card, after the card's own text and inside its
   clip, and before the scene's module if it has one. Where is in **frame** pixels (0 0 the
   frame's top-left, 1920 × 1080; a card has no animation area), and a region is a half or
   quarter of the frame. Moves are by cue as elsewhere; negative times reach before cue 1.
   **A scene with no cues** (an end card) writes its moves without `cue N`, as a panel does,
   timed from the scene's start, `end` being the scene's end (Squirrel, 11 October 2026,
   00:13: "yes"); `cue N` there is a problem, as a missing `cue N` is in a scene that has cues.
   No curtain and no panels on a card (a Mistake or Right way section there is the existing
   problem: no cue has a `mistake:`). The library elements on a card are credited like any others.
5. **Turning a member.** Any member, a piece or a library element, in a scene, a panel or a
   card, takes `rotate=DEGREES` in its Parameters: clockwise, about the centre of its box (a
   library element's rect; a pill's, a text's and a badge's drawn box; the point a hand or a
   callout is placed at; an arrow's box). It is animated and set like any number (`cue 1,
   0–0.6 s: pile-3.rotate 0 → -20`). `rotate` is video-tools' own name, not passed to the
   element. A member is drawn as it would be unturned and that drawing is turned, so nothing
   inside it changes; an anchor read from a turned member is turned with it, so a member placed
   on it follows. With no `rotate`, or 0, the frame is exactly what it was. The `hand` piece
   keeps its own `angle`, in radians, which turns the drawing about the wrist; `rotate` is in
   degrees like everything a script's author writes.

**Not built, and said to the training-video project instead** (request 17, item 6: "say so in
your reply rather than building it unasked"; Squirrel, 00:13: "write your comments in
training-video inbox"): what else its modules do that the format cannot say (choosing columns
or rows of a CSV; a steady rate rather than eased; a pulse and anything that repeats; a move
spanning cues or timed as a fraction of a cue; dimming to a level; growing or stretching a
member; plain shapes).

Order of work, test-first against the invented library: 1; 2 (`draw.arrow`'s dash first); 3
(the stub elements gain a `fill` role, drawn as the real library resolves one); 4 (the parser
and the check for a scene without cues, then the drawing); 5 (the turn, the anchors, the
check); README, "Notes for users", lint as its own pass; a Tier 3 against the real library.

## 20. Steady moves, dimming, spans across cues and percentages, and a CSV's columns and rows (request 18; Squirrel, 11 October 2026, 00:28: "1. and 2. both yes")

Four of the things the training-video project's modules do that item 15's format could not say
(our reply to it of 11 October; its request 18 numbers them 1, 2, 4 and 5). Built in this
order, each adding to the moves' grammar of item 15 or to the cast's Parameters.

1. **A steady rate.** A move's time may end `, linear`: `cue 2, 0–end-0.3 s, linear:
   prompt.progress 0 → 1`, `cue 1, linear: show a` (the first 0.6 s), in a panel `0.4–0.8 s,
   linear: show total`. The change then runs at a steady rate over its span; an unmarked move
   eases as before. It applies to whatever the move changes (opacity, place, a parameter, a
   state's progress).
2. **Dimming to a level.** `dim NAME[, NAME…] to LEVEL`, LEVEL a number from 0 to 1: the
   members' opacity goes to that level over the span, as `show` takes it to 1 and `hide` to 0;
   a later `show` brings it back to 1, a later `dim` to another level. The curtain, and a
   flash (item 21), multiply it as they do a shown member's. `check-script`: a level outside 0
   to 1; a dim of a member that is not shown at that moment (never shown, or hidden); a `show`
   of a member that is dimmed is not "shown again while still shown". For the curtain rule a
   dim names its members at its cue, as any move does.
3. **Times as a percentage, and a span that ends in a later cue.** A time may be `P%`, that
   share of the cue's length from its start: `cue 5, 74%–80%: …`, `cue 5, 42%: …` (from there,
   for 0.6 s), mixed with seconds if wanted (`cue 2, 0.5 s–50%`; seconds keep their ` s`, a
   percentage has none). In a panel a percentage is of the mistake cue's length, and `end`
   there is now that cue's end (it was the panel's rise, which said nothing); in a scene with
   no cues, of the scene's length. A span may end in a later cue: `cue 1, 0.5 s – cue 2,
   end-0.5 s: gauge.level 0.12 → 0.92`, each time against its own cue; or at the scene's end:
   `cue 2, 2.6 s – end of scene: …` (request 19). `check-script`: the later cue must exist
   and come after the first; each time is checked against its own cue's length as now. For the
   curtain rule a member in such a move is named at the cue the span ends in (every later cue,
   for `end of scene`).
4. **Choosing a CSV's columns and rows.** Beside a parameter that names a data file
   (`rows=FILE`), three optional qualifiers named after it, so that they cannot collide with an
   element's own parameters (Squirrel, 00:28): `rows.where="COLUMN = VALUE"` or `"COLUMN !=
   VALUE"` keeps the data rows whose cell in that column equals (or does not equal) the value;
   `rows.first=N` then keeps the first N of them; `rows.columns="A, B, C"` then keeps those
   columns, in the order written. A column is its header's name or its number from 1; the list
   is separated by commas. The file's first row is its header: it is always kept, and names are
   looked up in it. The element is handed the result exactly as it would be handed a file's
   rows, and `check-script` counts rows and indices against the result. Refused in words, by
   line in `check-script` and again when drawn: a column that is not there, by name or number;
   a `where` that is not `COLUMN = VALUE` or `COLUMN != VALUE`; a `where` with `=` that no row
   matches; a `first` that is not a whole number above 0; a qualifier of a parameter the member
   does not give or that is not a data file.

Order of work, test-first: `linear`; `dim`; percentages, then spans across cues and `end of
scene` (the moves' times resolved in one place, `choreography.window`, used by the check and by
`perform`); the CSV qualifiers as a pure function, then the check, then the drawing; README,
"Notes for users", lint as its own pass; a Tier 3 against the real library.

## 21. A repeating flash (request 19; Squirrel, 11 October 2026, 00:36: "cue up work on it (if you agree) after 17 and 18"; agreed)

`flash NAME[, NAME…] [rate=R] [phase=P] [low=L]`: over the move's span the members' opacity
is multiplied by a sine between `low` and 1: `low + (1 − low) × (0.5 + 0.5 × sin(2π × (R × τ +
P)))`, τ the seconds since the span's start. `rate` is flashes a second, default 1.4 (what the
training-video module drew: 9 radians a second), above 0 and at most 3 (the usual limit for
flashing content, three a second); `phase` is a fraction of a beat (0.25 starts at the top),
any number; `low` the lowest opacity, 0 by default, from 0 to below 1. Options are written
`name=value` after the names (the request's `, phase 1` would read as a member's name). It
multiplies the member's own opacity (its show, hide and dim, and the curtain), so a hidden
member stays hidden; outside the span the member's opacity is its plain one. Any span a move
can have, `– end of scene` among them. A flash changes nothing lasting, so for the curtain
rule it does not name its members: a sign shown before the mistake cue and flashing to the
scene's end still fades under the panels. `check-script`: a member not in the cast; a rate,
phase or low that is not a number or is out of range; an option that is not one of the three;
two flashes on one member whose spans overlap.

After item 20, which gives it its spans. Test-first: the parser; the opacity over a span (the
stub records it: 0.5 at the start, 1 a quarter-beat on, 0 at three quarters; `phase`, `low`;
hidden stays hidden; plain outside the span); the checks; README, "Notes for users", lint; a
Tier 3.

## 22. A text parameter read from a file, and its lines chosen (request 20; Squirrel, 11 October 2026, 07:05: "1. Yrs 2. Leave out. Go ahead", and 07:06: "That's 1. Yes")

video-elements' `document` takes its page as one `text` parameter, a line a line, which a cast
row cannot write. Item 15 has said since 10 October that a `.txt` file named in a cast row is
read "text as it is" and handed to the element; the code only ever read `rows`. This builds
that, and what the request adds.

1. **A `text` parameter's value that names a file** under the video's folder
   (`text=assets/plan-v1.txt`) is read (UTF-8) and the element is handed the file's text; any
   other value is the text itself, as before. `check-script`: a value with no spaces that ends
   `.txt` or `.md` and is not a file under the folder is a problem, in the words used for `rows`.
2. **Its lines chosen**, beside it and named after it as `rows.first` is: `text.skip=N` drops
   the first N lines, then `text.first=N` keeps the first N of what is left, in that order
   however written; N a whole number above 0. Lines are counted without the blank ones, and
   when either is given the element is handed the chosen lines alone, a line a line (blank
   lines gone); with neither, the text exactly as it is. A `skip` that leaves no line is a
   problem. They work on a value that is the text itself too. `skip` is for text and `where`
   and `columns` for a data file: the wrong one for a parameter is a problem saying which it
   takes. No `rows.skip` (Squirrel, 07:05: "Leave out").
3. **Indices counted against the lines chosen.** As a `rows` file's rows are, the non-blank
   lines of a member's text (from a file, or with a qualifier) are what `check-script` counts
   an indexed parameter or anchor against: `highlight.4` on three lines is a problem (`…has 3
   lines`). When a member gives both `rows` and such a text, the rows are what is counted.
4. **A fault in the existing rule, found while there, and mended:** an index is counted
   against the rows (or lines) whatever the parameter or anchor indexes, so `tab-box.4` or the
   anchor `tab.4` on a sheet of three rows with four tabs was refused, wrongly, and a refused
   check stops the drawing. The description does not say what an index counts. Until it does,
   a name that begins `tab` is not counted against rows or lines (the library's tabs are
   `tab.N`, `tab-box.N`, `active-tab`); to be put to video-elements as a question.

Order of work, test-first: the pure `select_lines`; the reading and the qualifiers in the
drawing (the invented `pot` gains a `text` parameter and a `line-alpha.*`); the check (a path
that is no file; the wrong qualifier; indices against lines; the `tab` names); README, "Notes
for users", lint as its own pass; a Tier 3 with the real `document` and the second video's
plan file; a note to training-video.

## 23. An index is counted as the element's description says (video-elements' reply of 11 October 2026, 07:29; Squirrel, 07:33: "Both yes go ahead")

Our request to video-elements ("Settled" 42) is answered and built there (`d203f0a`): the
description says what each index of an indexed parameter or anchor counts, and which boolean
parameter says a data file's first row is a header. This replaces item 15's rule (every first
index against the file's rows) and item 22, 4's stopgap (names beginning `tab` not counted).

1. **The rule.** For a library member, each index of an indexed parameter or anchor is looked
   up in `el["counts"]` by its pattern and checked by what it counts: `row`, a data row of the
   member's `rows` parameter named there, after `rows.where`, `rows.first` and `rows.columns`,
   **the header not counted** when the element has a header switch
   (`el["params"][rows]["header"]`) and the member's value of it, or its default, is true;
   `column`, a column of those rows; `line`, a non-blank line of the member's text parameter
   named there, after `text.skip` and `text.first`, whether the text came from a file or is the
   value itself; `other`, not checked (a tab: the element refuses a bad one when it is drawn).
   Every index of a name is checked, not only the first (`cell.3.9` on two columns). An index
   of 0 is a problem as before (indices count from 1). An index whose data video-tools did not
   read (the parameter not given, the file not there: its own problem) is not checked.
2. **In words.** `'highlight.5': assets/sales.csv has 4 data rows as chosen`, `'redact.7':
   assets/sales.csv has 6 columns`, `'line-alpha.5': assets/plan.txt has 4 lines as chosen`,
   `… the text has 1 line`; for an anchor, `'tick' is placed by 'sheet'.'row.9', but
   assets/sales.csv has 4 data rows`. "data rows" when a header was left out of the count,
   "rows" when the element has no header switch or it is off.
3. **A library with no `counts`** in its descriptions (before `d203f0a`): no index is checked,
   rather than checked wrongly.
4. **A row that is not on show.** A sheet that shows a window of its rows gives anchors only for
   those; an anchor that passes the count and is then not among those the element returned is
   refused at draw time in words that say so (Squirrel, 07:33: "Both yes"), where the message
   used to speak only of cast order.

The interface block of item 15 gains video-elements' two lines, in its words:

```python
el["counts"]                                  # what each * of an indexed parameter or anchor counts, by pattern:
#   {"cell-alpha.*.*": [{"what": "row", "of": "rows"}, {"what": "column", "of": "rows"}], "tab-box.*": [{"what": "other", "of": None}]}
#   what: "row" (a data row of the rows parameter `of`, its header not counted), "column" (a column of it),
#   "line" (a non-blank line of the text parameter `of`), "other" (not something a caller can count; `of` None).
#   Every indexed name of the element is a key; an element with none has {}
el["params"]["rows"]["header"]                # for a rows parameter: the name of the boolean parameter that says its
#   first row is a header (not a data row), or None when the element has no such switch
```

Order of work, test-first: the invented library reads an `## Indexes` table and `rows
header=NAME` as the real one does; the rule in the check (parameters in the cast and in moves,
anchors), the old rule and the stopgap removed; the draw-time words; README, "Notes for users",
lint as its own pass; a Tier 3 against the real library; a note to training-video.

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

`~/.video-tools.conf` (`video-tools.conf.example` committed): `SPEECH_MODEL_DIR`, `VOICE`, `SPEED`,
and from item 15 `VIDEO_ELEMENTS_DIR` (the root of the video-elements repository) and
`RSVG_CONVERT` (the SVG renderer's path, optional). Read, never run: `KEY=value`, `#` comments, optional quotes, `~` for home. The video's script
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
Kokoro-82M model and voices in `~/models/kokoro/` (`model.onnx`, `voices.npz`). From item 15, for a
script with a described scene only: the video-elements repository at the configured path (its
package imported from there, never installed here) and, through it, `rsvg-convert` (Homebrew
`librsvg`, video-elements PLAN.md "Dependencies").

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
14. **Request 13** (10 October 2026, 10:09; OK'd 10:36 with the three details settled): item 15.
   First the format, written in item 15 with scene A2 as a worked example, for Squirrel's
   approval (given 13:24, "Settled" 27). Then item 15's "Order of work", test-first against
   the invented library, written to the description rows of "Settled" 27. Real drawing waits on
   video-elements' step 4 and first elements.
15. **Request 14** (10 October 2026, 10:20; OK'd 10:36): item 16, after item 15's parser, in
   item 16's order.
16. **Request 15** (10 October 2026, 22:59; OK'd 23:09): item 17, in its order of work. The
   natural-size half of its item 3 waited on video-elements, whose note came at 23:32; built
   after it.
17. **Request 16** (10 October 2026, 23:58; OK'd 23:59): item 18, in its order of work.
18. **Request 17** (11 October 2026, 00:00; OK'd 00:13): item 19, in its order of work.
19. **Request 18** (11 October 2026, 00:22; OK'd 00:28): item 20, in its order of work, after item 19.
20. **Request 19** (11 October 2026, 00:33; OK'd 00:36): item 21, after item 20.
21. **Request 20** (11 October 2026, 06:40; OK'd 07:05): item 22, in its order of work.
22. **video-elements' reply** (11 October 2026, 07:29; OK'd 07:33): item 23, in its order of work.
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
24. The thirteenth request (`inbox/done/request-from-training-video-2026-10-10-13.md`), all three
    items, with the three details settled: the interface is video-elements' settled text, with the
    `renderer` argument and `lib.credits`; the settings are `VIDEO_ELEMENTS_DIR` and the optional
    `RSVG_CONVERT`, each also a flag; the folder setting names the repository root, put on the
    import path at the point of use (Squirrel, 10 October 2026, 10:36: "1. go with the choice in
    video-elements 2. yes 3. repo root", then "go ahead and do the format and get my approval on
    that"). The format itself waits for his approval ("Open questions" 1).
25. The fourteenth request (`inbox/done/request-from-training-video-2026-10-10-14.md`), all five
    items, after request 13 (Squirrel, 10 October 2026, 10:36, with request 13).
26. video-elements' request (`inbox/done/request-from-video-elements-2026-10-10.md`): `library.open`
    takes the library's root folder, the one `VIDEO_ELEMENTS_DIR` names, and the interface's first
    comment line says so; nothing else changes (Squirrel, 10 October 2026, 13:02: "Let's do that").
27. **The choreography format** of item 15 as written (the two `###` sections, the cast table's
    columns, the four kinds of move, the pieces as cast members, area pixels for Where, panel
    pixels for the panels, the curtain rule and the checks), with the worked example (Squirrel,
    10 October 2026, 13:24: "choreography format is fine"). And **the element description's
    rows** as video-elements' reply of 13:18 states them (`inbox/done/reply-from-video-elements-2026-10-10.md`,
    answering our request of 13:05 there; Squirrel there, 13:18: all three asks accepted): the
    `rows` and `label` parameter types, `*` as a whole segment for an index, indices from 1,
    dotted names in `params` and the returned anchors, `"computed"` anchors; the description
    `lib.element(name)` returns is plain data (`name`, `kind`, `size`, `anchors`, `states`,
    `default-state`, `params`, `colours`, `provenance`, `folder`), `open` raises
    `videoelements.cli.Failure` with `.problems` (its request of 12:59). Recorded in item 15,
    "The cast". The spreadsheet's final parameter names come with video-elements' step 6; the
    example's are guesses until then (Squirrel, 13:24: "record and move reply to done").
28. The credits file `assemble` writes beside the finished video is treated like the video: never
    replaced, `--replace` or not; `assemble` refuses before starting if it exists (item 16, 5;
    Squirrel, 10 October 2026, 21:10: "default is fine").
29. The fifteenth request (`inbox/done/request-from-training-video-2026-10-10-15.md`), all four
    items (Squirrel, 10 October 2026, 23:09: "request 15 ok"), with three choices (23:11: "on
    item 3, do wait for natural-size in video-elements (it's being worked on now). Agree with
    your assumption about head and your plan for item 3 warning exit code"): drawing a blank
    Size at the element's natural size waits until video-elements offers it; an arrow's `head`
    is `yes` or `no`, whether the arrowhead is drawn, default `yes`; the `check-script` warning
    for a blank Size on a nominal-sized element is printed and leaves the exit code as it was.
30. video-elements' note (`inbox/done/request-from-video-elements-2026-10-10-2.md`, 23:32): the
    description's `fit` and `el.natural_size(frame, params)` are in the shared interface, in its
    words (item 15, "The interface"), and video-tools uses `natural_size` for a blank Size as
    item 17, 3 says. Squirrel's OK is his answer of 23:11 on request 15 ("do wait for
    natural-size in video-elements (it's being worked on now)") to the question whether that
    half should wait until he had OK'd the interface on the video-elements side, which he then
    did there (its DIARY: his answers of 23:31, the note sent with his "Yes"). He was not asked
    again about the note itself. Squirrel, 10 October 2026, 23:48: "that was OK, although always better to
    check if not sure".
31. How `check-script` learns that an element's size is nominal (item 17, 3): from the Notes
    cell of the `size` row in the element's `ELEMENT.md`, when it begins `nominal`, read from
    the description's `folder`, and only for an element whose `fit` is not `natural` (today the
    real `diff`). It reads a file of video-elements' directly, and a prose column; left so for
    now, to be put to video-elements if more such elements appear (Squirrel, 10 October 2026, 23:48: "leave
    for now").
32. A natural-sized element in a region with a blank Size is centred in the region at its
    natural size and not scaled to it; every other element with a blank Size in a region is
    fitted to the region as before (item 17, 3; Squirrel, 10 October 2026, 23:48: "ok").
33. video-elements' second note (`inbox/done/request-from-video-elements-2026-10-10-3.md`, 23:53):
    `diff` is a fourth natural element (`fit` `natural`, its natural size its `width` by 30 a
    line plus 20, from video-elements `5f98a74`), so the interface block names it, a `diff` with
    a blank Size is drawn at that size, and `check-script` no longer warns of it; no code here
    changes. The README's example of the warning is kept and labelled as output from before that
    change, since no real element gives the warning now (Squirrel, 10 October 2026, 23:53: "yes ok").
34. The sixteenth request (`inbox/done/request-from-training-video-2026-10-10-16.md`): an empty
    label is not checked (item 18). Squirrel, 10 October 2026, 23:59, before the item was read
    out to him: "check inbox and do what it says". Its two "your call" points are "Open
    questions" 1 and 2 until he says.
35. A label that is only spaces is still a label and still checked against On screen; only the
    empty string is "none" (item 18, 1; Squirrel, 11 October 2026, 00:09: "agreed").
36. A `pill`, `callout` or `text` whose `text` is empty stays a problem; a `hand` whose `label`
    is empty is drawn without a label (item 18, 2; Squirrel, 11 October 2026, 00:09: "yes").
37. The seventeenth request (`inbox/done/request-from-training-video-2026-10-11-17.md`), its
    five asks as written, with a scene that has no cues writing its moves without `cue N`,
    timed from the scene's start (Squirrel, 11 October 2026, 00:13: "1. yes 2. yes … Go ahead
    with request 17 as written"). Its item 6 is answered with comments, not code.
38. video-tools may write its replies and comments into the training-video project's inbox: a
    standing permission, for that folder only; everything else in that project stays read-only
    (Squirrel, 11 October 2026, 00:13: "write your comments in training-video inbox, standing
    permission granted to do that"). At the time that project had no `inbox/` folder; asked.
39. The eighteenth request (`inbox/done/request-from-training-video-2026-10-11-18.md`), all four
    items, after request 17, in the order linear, dim, spans and percentages, CSV; the CSV's
    choices written `rows.columns`, `rows.where`, `rows.first`; dimming as `dim NAME to LEVEL`
    (Squirrel, 11 October 2026, 00:28: "1. and 2. both yes", to those two questions).
40. The nineteenth request (`inbox/done/request-from-training-video-2026-10-11-19.md`), after
    requests 17 and 18 (Squirrel, 11 October 2026, 00:36: "check inbox for request 19 and cue up
    work on it (if you agree) after 17 and 18"). Agreed, with five adjustments told to him at
    00:38 and not objected to: options written `name=value`; `phase` a fraction of a beat; `rate`
    at most 3 a second, default 1.4; a flash does not name its members for the curtain rule;
    `end of scene` as a span's end. If any of the five is not what he wants, it is a small change.
41. The twentieth request (`inbox/done/request-from-training-video-2026-10-11-20.md`), all three
    items, without a `rows.skip` (Squirrel, 11 October 2026, 07:05: "1. Yrs 2. Leave out. Go
    ahead"; 07:06: "That's 1. Yes"). The `tab` names left out of the index count (item 22, 4)
    are Claude's mending of a fault found while there, told to him with the result.
42. A request to video-elements, written into its inbox
    (`~/projects/code/video-elements/inbox/request-from-video-tools-2026-10-11.md`): that an
    element's description say, as data, what each index of an indexed parameter or anchor counts
    (a data row, a column, a line, or something video-tools cannot count), so that the
    count-against-rows rule and the `tab` stopgap of item 22, 4 can be replaced (Squirrel, 11
    October 2026, 07:18: "Yes, make the request"; for this request, not a standing permission to
    write there). Nothing is built here until its reply arrives and is OK'd.
43. video-elements' reply (`inbox/done/reply-from-video-elements-2026-10-11.md`): `el["counts"]`
    and a `rows` parameter's `header` are in the shared interface, in its words, and
    video-tools counts each index by them (item 23); tabs stay `other`, unchecked, and no fifth
    word is asked for; the draw-time refusal of an anchor the element did not return says the
    row may not be on show (Squirrel, 11 October 2026, 07:33: "Both yes go ahead").
