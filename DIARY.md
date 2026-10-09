# DIARY.md — video-tools

## Where things stand

9 October 2026, 17:35. The first request has arrived and Squirrel has OK'd it: PLAN.md is
rewritten from `inbox/done/request-from-training-video-2026-10-09.md` (eight commands and the
package `videotools/`, build order there). Build step 1 ("look") is done: `.venv/` from Homebrew
Python 3.12 with the dev tooling and the run-time packages, and every belief in PLAN.md "Things
checked" seen on the Mac (kokoro speaks, ffmpeg takes BGRA, pycairo builds after `brew install
pkgconf`, fonts need CoreText registration on macOS, not fontconfig). No code yet.

Green: nothing yet (no tests, no code).

Next: the rest of step 1, `examples/` (an invented video and brand), then step 2 (the readers
and `check-script`, then the timeline), test-first.

Waiting on Squirrel: PLAN.md open question 2, the scene-code interface, before any chrome code
(step 4). Open questions 1, 3 and 4 are assumptions he can overturn. The GitHub remote
("Settled" 7): none yet, so nothing is pushed.

How the tests work: `tests/tier1/` for pure functions; `tests/tier2/conftest.py` puts stub
`ffmpeg` and `ffprobe` on PATH and a fake `kokoro_onnx` module on `sys.path`, and names a config
file through `VIDEO_TOOLS_CONF`. `.venv/bin/pytest tests/tier1` runs one tier. Nothing written yet.

## Log

### 9 October 2026 — Setting up

**Goal.** Guidance files and dev tooling from the coding template; no tools.

**Decision / surprise.** Squirrel (16:06): make the repository from the coding template and
describe it in the guidance files, but add no tools yet; the tools will be pulled out of the
prototype that made the bed video (`~/projects/non-code/make-bed-training-video/_work/`) by way
of the training-video project. Set up by Claude in the device shell (a Linux VM, not the Mac),
so no `.venv` was made: a venv made there would not run on the Mac. `TEMPLATE.md` was moved to
`_to_delete/` (deletion is off in that shell), and `_to_delete/` is listed in
`.git/info/exclude`, so nothing in it is committed. `project.conf.example` renamed
`video-tools.conf.example`. The rule that the commands use only the standard library can't hold
for drawing, speech and video; that is PLAN.md's open question 1.

**State.** No code. Next: Squirrel's answers; then, when a request arrives, rewrite PLAN.md from
it and start step 1 (look).

### 9 October 2026 — Squirrel's answers

**Decision / surprise.** Squirrel (16:16): private for now; the dependencies in PLAN.md are
allowed. Both moved to "Settled" in PLAN.md and recorded in CLAUDE.md. With delete permission,
the files git couldn't remove after the first commit were deleted (temporary object files and
two lock files that had been renamed out of the way), as were `TEMPLATE.md`'s folder
`_to_delete/` and its line in `.git/info/exclude`; `git fsck` clean.

**State.** No code. Next: the first request from the training-video project.

### 9 October 2026 — Layout and voice settled

**Decision / surprise.** Squirrel (16:22): separate scripts like `book-tools` (checked there:
one executable wrapper per command at the top of the repository importing `main()` from the
`booktools/` package), so here the package is `videotools/` (the empty `video_tools/` folder
renamed, and `pyproject.toml`'s coverage target with it); the narration voice must be
configurable for each video; he will create the GitHub repository himself. PLAN.md has no open
questions left.

**State.** No code. Next: the first request from the training-video project.

### 9 October 2026 — The request arrives and is OK'd

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09.md` (written 16:55–17:06
by Claude on the training-video side) reported to Squirrel at 17:12 with a plan: file it into
PLAN.md, do step 1, build in its order, with two proposals (one venv on Homebrew Python 3.13, and
the scene-code interface drafted in PLAN.md for him to decide before chrome). Squirrel (17:15):
"go ahead using both of your proposals". PLAN.md rewritten from the request; his answers to its
four questions (command names, README set-up steps, labels by text, stored-image frame tests)
under "Settled" 9–11; the item moved to `inbox/done/`. The uncommitted `inbox/` section of
CLAUDE.md from the previous session goes in the same commit.

**State.** No code. Next: step 1, look.

### 9 October 2026 — Step 1, look: the beliefs checked on the Mac

**Goal.** No code depends on a guess: Python, the speech model, ffmpeg, cairo and fonts.

**Decision / surprise.** Four findings, all in PLAN.md "Things checked":

1. No Homebrew Python 3.13 here (3.11, 3.12, 3.14 are); the venv is from 3.12 (open question 1).
   `pip install -r requirements-dev.txt` and `kokoro-onnx==0.6.1 soundfile numpy Pillow
   fonttools` installed cleanly.
2. kokoro-onnx loads the model Squirrel put in `~/models/kokoro/` and spoke a test line:
   ```
   voices ['af_heart', 'am_michael', 'bf_emma', 'bm_george']
   rate 24000 samples 32768 seconds 1.365 dtype float32 peak 0.6463167667388916
   ```
3. ffmpeg 9.0.2 takes raw BGRA on stdin and exits 0 (`ffmpeg exit 0`); truncated input exits 69
   with `Packet too small (1)`. ffprobe with `-count_frames` reports `"nb_read_frames": "3"`,
   `"duration": "0.100000"` for three frames at 30 fps.
4. `pip install pycairo` failed with `metadata-generation-failed` because `pkg-config` was not
   installed; after `brew install pkgconf` it built (pycairo 1.29.2, cairo 1.18.6). Then the
   dead end: with `FONTCONFIG_FILE` naming a private fonts.conf over the brand's font folder,
   cairo's toy API returned the same width (302.36) for "EBG SemiBold", "No Such Font Xyz" and
   "Helvetica": the Homebrew build links CoreText and fontconfig both, and the toy API on macOS
   uses CoreText. Registering each file with `CTFontManagerRegisterFontsForURL` at process scope
   through `ctypes` fixed it:
   ```
   register EBG-SemiBold.ttf True
   EBG SemiBold 292.48
   EBG Regular 277.08
   EBG Italic 291.52
   No Such Font Xyz 302.36
   ```
   So `videotools.fonts` registers with CoreText on darwin and uses fontconfig elsewhere; the
   Linux route is still to be checked in the device shell.

**State.** Step 1's checks done. Next: `examples/`.
