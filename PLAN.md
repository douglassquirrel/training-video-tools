# PLAN.md — what video-tools does and how it gets built

Written 9 October 2026 by Claude at Squirrel's request. CLAUDE.md says how the work is done;
this file says what the commands do and in what order they are built. Squirrel's instructions
are recorded here with their date; nothing here is invented, and anything assumed is under
"Open questions".

**Status: nothing is specified or built yet.** Squirrel's instruction (9 October 2026, 16:06):
create this repository from the coding template and describe it, "but don't start adding any
tools yet". The commands will be specified by a request written in the training-video project
(`~/projects/non-code/training-video/tools/request-to-claude-code-YYYY-MM-DD.md`), after its
review of the prototype. When that request arrives, this file is rewritten from it in the
coding template's shape (the command, how it works, the steps of a run, exit codes, what is
written where), one section per command, and Squirrel's decisions go under "Settled".

## Where the tools come from

The first training video, *Bed Making* (4 min 22 s, U.S. Navy Hospital Corps Figure 173), was
made on 6–7 October 2026 by a one-off prototype of about 2,200 lines of Python
(`~/projects/non-code/make-bed-training-video/_work/film.py`, `core.py`, `sheet.py`). That
folder is read-only from here. Its working method, in the order a video is made:

1. A script: scenes in order, each a list of narration cues (caption text, and spoken text where
   it must differ, such as "Core" for "Corps"), with a minimum duration where the animation
   needs longer than the words.
2. Narration: one clip per cue from a local speech model (Kokoro-82M, ONNX, voice `af_heart`,
   speed 0.98, 24 kHz), silence trimmed, lengths written to a timing file.
3. Timing: each cue's start and length from its clip, a gap and its minimum; the scene's length
   from its cues. Animations are keyed to cue start times.
4. Drawing, frame by frame with cairo at 1920×1080, 30 fps: subject drawing (particular to the
   video) inside standard chrome (header with step letter and tracker, caption band, a reference
   column with a cropped inset of the source figure and key points, "Mistake" / "Right way"
   split panels, title and end cards), in the brand's colours and fonts.
5. Stills and contact sheets for review before rendering.
6. Rendering: frames piped to ffmpeg (H.264, CRF 18), one segment per scene.
7. Assembly: segments joined, narration clips mixed in at their cue times, peak-normalised,
   AAC 160 kb/s, fast start.

## Expected commands (provisional, until the request)

Names and boundaries are guesses for orientation only; the request decides.

| Command | Job |
|---|---|
| `narrate` | Script cues to one narration clip each and a timing file, with a local speech model, in the voice, speed and model the video's settings name ("Settled" 6). |
| `timeline` | Cue and scene timings from clip lengths, gaps and minimums (possibly part of a library rather than a command). |
| `stills` | Frames at given times, and four-up contact sheets, from a video's scene code. |
| `render` | One scene, or a frame range of it, to a video segment. |
| `assemble` | Segments and narration into the finished video, with checks of length and audio level. |
| `crop-insets` | Panels cropped from a source figure at named boxes, sized for the reference column. |
| `font-weights` | Static, uniquely named weights from a variable font, so the drawing library can choose a weight. |

And the shared package `videotools/`, which the commands and a video's scene code import: the chrome, the drawing primitives (text with
tracking and wrapping, pills, callouts, arrows, dimension lines, badges, hands), easing, an
oblique 3D camera, and the brand kit reader.

## Dependencies

Allowed (Squirrel, 9 October 2026, 16:16), installed in one documented step. The prototype used:

- ffmpeg and ffprobe (Homebrew `ffmpeg`), for encoding, joining and checking;
- cairo and pycairo (Homebrew `cairo`, `py3cairo`), for drawing;
- numpy, soundfile, onnxruntime and kokoro-onnx (pip), for speech;
- Pillow (pip), for cropping and contact sheets;
- fontTools (pip), for font weights;
- the Kokoro-82M model and voices (about 325 MB), in `~/models/kokoro/`.

## What is written where (principles, until the request)

- Every command writes only into the output path it is given, inside the video's folder;
  never into a source, a script, a brand kit or a finished video, and never over an existing
  file (it refuses instead).
- Intermediate files (clips, timings, segments, stills) are rebuildable and go in the video's
  `work/` folder; finished videos go in its `out/` folder under a new name.
- Nothing is deleted, moved or sent anywhere.

## Configuration (until the request)

`~/.video-tools.conf` (`video-tools.conf.example` is committed): the speech model's folder and
the default voice and speed. Each video's own settings override those defaults (its voice above
all: "Settled" 6), and a flag overrides both. Everything particular to a video or a brand lives
in that video's script and the brand kit file, not here.

## Things to be checked against the real thing before code depends on them

These are beliefs from the prototype, which ran in a Linux device shell (aarch64), not on the
Mac. Step 1 of the build checks each on the Mac, without making a video, and records what was
seen in DIARY.md.

- Homebrew's `py3cairo` imports in the Python the commands will run under.
- kokoro-onnx 0.6.1 loads the onnx-community `model.onnx` (inputs `input_ids`, `style`,
  `speed`) with a voices file built from the per-voice `.bin` arrays, and speaks with
  espeak-ng from `espeakng_loader`.
- ffmpeg on the Mac has `libx264` and `aac`, and accepts raw BGRA frames on stdin.
- cairo's simple text API finds fonts through a private `fonts.conf` named in
  `FONTCONFIG_FILE`, on the Mac as in the device shell.

## Build order

Starts only when a request arrives. Each step is done test-first (CLAUDE.md), ends on a green
suite, a commit and a push, all on `main`.

1. **Look.** Set up `.venv` on the Mac. Check everything in the list above. Make the example
   video in `examples/`: a tiny invented subject (not the bed video, nothing from a real
   source), two scenes, two cues each.
2. **Each requested command**, one at a time in the request's order, tier 1 then tier 2 (the
   speech model and ffmpeg replaced by stubs on PATH), with its exit codes and its "never does
   this" tests.
3. **The real thing.** Each command on the example video, and the training-video project
   re-makes the bed video with these commands as its acceptance test (that is the project's
   work, recorded in its diary).
4. **README**, then lint as its own pass.

## Not doing

- Anything particular to one video: subject drawing, narration text, sources.
- Network use at run time: no cloud speech, no uploading, no fetching brand assets.
- Editing video in a timeline, or any graphical interface.
- Slide decks.

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
   repository (`narrate`, `render`, …), each a thin wrapper that imports its `main()` from a
   shared package, `videotools/` (Squirrel, 9 October 2026, 16:22).
6. The narration voice is configurable for each video: `narrate` takes the voice, speed and
   model from the video's own settings, with defaults in `~/.video-tools.conf` and flags that win
   over both; nothing about a voice is fixed in the code (Squirrel, 9 October 2026, 16:22).
7. Squirrel creates the GitHub repository `douglassquirrel/video-tools` (private) and pushes when
   he is ready; until then there is no remote (Squirrel, 9 October 2026, 16:22).
