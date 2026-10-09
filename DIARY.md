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

### 9 October 2026 — Step 1, the example video and brand

**Goal.** `examples/` for every test, `--dry-run` and Tier 3 check: invented, nothing real.

**Decision / surprise.** `examples/brands/paperboat/` (Paperboat Press: colours, three fonts,
mark, illustration, settings) and `examples/videos/paper-boat/` (*Folding a Paper Boat*: seven
scenes, eleven cues, every setting and every scene feature the format has, including a `## Notes`
section with a table between scenes and an `x-` key). The source figure, the end-card drawing
and the mark reference were drawn with Pillow (scratch script, not kept). The fonts are static
instances of EB Garamond (OFL) at 400, 600 and italic 400, subset to Latin, renamed `PBS …` as
the OFL requires for a modified font; `fonts/OFL.txt` beside them. 150 KB each. Checked with the
reference reader, read-only from its folder:
```
Folding a Paper Boat: 7 scenes, 11 cues, 125 words (about 48 s of speech at 2.6 words a second)
Tracker: A B C
…
No problems found.
exit 0
```

**State.** Step 1 done. Next: step 2, `videotools.script`, test-first.

### 9 October 2026 — Script reader: a well-formed script reads back

**Goal.** `script.parse(text)` returns the title, the three tables and the scenes with their
properties, cues (with sub-bullets), side-panel and on-screen items, each with its line number.

**Test.** `tests/tier1/test_script_reads.py`: `title_settings_colours_and_insets_read_back`,
`scenes_read_back_with_properties_cues_lists_and_lines`,
`parse_reports_no_problems_for_a_well_formed_script`, on a hand-written two-scene script.

**Red.** First run: `ImportError: cannot import name 'script'`, the wrong reason; with the module
and an unimplemented `parse`: `NotImplementedError` ×3, the right one.

**Green.** After implementing, one assertion still failed:
```
AssertionError: assert ('A', 'First loop', 33) == ('A', 'First loop', 31)
```
The test's line numbers were wrong, not the code: the fixture string begins on line 5 of the
test file, so every line I had counted from the file was 4 too high. Counted again with a
four-line script (`33 ## Scene A`, `45 1. Step A`, `47 2. Don't`, `54 - Loop`, `59 - first loop`,
`60 - room for the second`), corrected the six numbers: `3 passed in 0.01s`.

**Decision / surprise.** The parser was written whole in this increment (sections, tables, cues,
sub-bullets, lists, the three structural problems), more than the minimum for these three tests.
The tests for its other behaviours (next entry) are therefore characterisation tests: each is
checked by breaking the code and seeing it fail before it is trusted.

**State.** Green: 3 tests. Next: the skipped sections, Unicode, and the structural problems.

### 9 October 2026 — Script reader: skipped sections, Unicode, structural problems

**Goal.** Notes sections (with tables) and prose are skipped; Unicode and `·` pass through;
a `###` outside a scene, junk in narration, junk in a list and a sub-bullet before any cue are
problems naming their line.

**Test.** `tests/tier1/test_script_skips_and_structure.py`, seven tests.

**Red / Green.** Characterisation (previous entry): all seven passed at once (`7 passed`). Then
the code was broken five ways in turn, each restored with `git checkout`, and each break made
the right test fail: notes read as settings `1 failed, 6 passed`; no problem for a `###` outside
a scene `1 failed`; narration junk ignored `2 failed` (the stray-line and the sub-bullet-first
tests); list junk ignored `1 failed`; non-ASCII stripped `1 failed`.

**State.** Green: 10 tests. Next: `script.check`, the validation rules, in groups.
