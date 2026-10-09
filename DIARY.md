# DIARY.md — video-tools

## Where things stand

9 October 2026, 21:34 (from the clock), after the Tier 3 check of `assemble --replace`.
**Requests 1 to 8 are built in full, and the bed video is accepted and rebuilt on the frame
methods.** A new session starts by reading CLAUDE.md, PLAN.md and this section, then `inbox/`
(empty at 21:22; anything at its top level other than README.md is new and is reported to
Squirrel, never acted on without his OK). All eight commands work (`check-script`, `narrate`, `crop-insets`, `stills`,
`render`, `assemble`, `check-video`, `font-weights`) on the package `videotools/`. Every build
step of PLAN.md is done: step 8, the re-make, was done by the training-video project at
`c1720ae` and matches the 7 October original to the frame and the millisecond (request 4).
**For the training-video project:** request 5's two test faults are fixed (the tests hand every
command and child a clean environment), and request 6 is in: the frame object's brand-aware
methods (`colour`, `text`, `tag`, `callout`, `dimension`, `badge`, `hand`: README, "Writing a
video's scene code"), and `code` optional for title and end scenes, so `_kit.py`, `title_card.py`
and `end_card.py` can go. The script format's wording for the optional `code` is in PLAN.md
item 4. Request 7: `check-script` checks the scene code without running it (a step scene with no
`code`, a missing or unparsable module, a missing top-level `def` the scene needs), so what
`stills` and `render` would refuse is found first. Request 8: `check-video --sheet` labels each
frame in a strip under it, as `stills` does (`videotools.sheet`, shared). Request 4's item 2
(the "+ Pillows" roundel and icon) was not asked for and is not done.

Green: 280 tests, coverage 98%, `ruff check .` clean, commits pushed to `origin/main`. The suite
needs pycairo, numpy, soundfile, Pillow and fontTools from the venv (libraries, not programs) and
no external program, model or network: ffmpeg, ffprobe and the speech model are stubs in
`tests/stubs/`; the stub ffmpeg refuses an existing output without `-y`, as the real one does.
One test is skipped off macOS (CoreText). The suite also passes with tier 2 run before tier 1,
and with `VIDEO_TOOLS_PYTHON` and `VIDEO_TOOLS_CONF` exported (`conftest.clean_env()`).

Tier 3 done on a scratch copy of the example, on this Mac: the whole chain made the 60 s example
video, which `check-video` passes clean (the entry "Tier 3: the whole chain"); since then the
real brand kit read (counts only), a sheet looked at, the wrappers run under
`VIDEO_TOOLS_PYTHON`, `crop-insets` under the Mac's Python 3.9 without Pillow (the one-line
message, exit 4), and the whole chain again at request 8 (same SHA-256 as the first time;
`check-video --sheet` looked at). `~/.video-tools.conf` on this Mac now names
`SPEECH_MODEL_DIR=~/models/kokoro` (Squirrel set it at 21:17; `narrate --dry-run` on the
example finds the model). Scratch copies of the example live only in the session's scratchpad,
never in the repository. Linux was tried by the training-video project (PLAN.md "Things checked" 5),
not from here. A real `assemble --replace` against the real ffmpeg on this Mac was tried on
9 October at 21:34 (the entry "Tier 3: `assemble --replace` against real ffmpeg"): the three
intermediates rewritten, the finished video untouched, the new output the same SHA-256. Clips at
a rate other than 24 kHz are not worth a check here: `narrate` always writes Kokoro's 24 kHz, so
another rate arises only from another model or a hand-made clip, and the Linux report covered
22,050 Hz (Squirrel, 9 October 2026, between 21:25 and 21:34).

Known limits worth knowing: the stored-image frame tests pin layout, not fonts (with fallback
fonts six of eight frames stay within the tolerance; the fresh-process font test pins fonts).

Waiting on Squirrel: nothing. The inbox is empty. The bed video is re-made and accepted
(request 4), rebuilt on the frame methods (request 8); what comes next is the training-video
project's (a second video, and any request it sends here). Known limits, all deliberate and
recorded: request 4's item 2 (the prototype's "+ Pillows" roundel and icon) is not done; the
checklist rows are 60 px apart where the prototype's were 66 (request 5, not asked for);
`check-script` sees only a module's own top-level `def`s; the stored-image frame tests pin
layout, not fonts (the fresh-process font test pins fonts).

Known-wrong in past entries: the `check-video` entry says `180 passed`; the run was `179
passed`. An earlier version of this section was dated "21:30"; that session ended at 18:30.

How the tests work: `tests/tier1/` pure functions (pycairo for `test_draw*.py` and
`test_fonts.py`); `tests/tier2/` runs each command as a subprocess through `conftest.run()`
under the venv's Python (a variable given as `None` is unset), with `tests/stubs/kokoro_onnx/`
(fake speech model, on `PYTHONPATH` by the `speech` fixture) and `tests/stubs/ffstub.py` (fake
ffmpeg and ffprobe on PATH by the `ffstub` fixture: media as `key=value` text files, every call
logged, `FFSTUB_FAIL`/`FFSTUB_DIE`/`FFSTUB_DROP` to make a job fail, an existing output refused
without `-y`). `example` copies `examples/` to a temporary folder; `narrated()` and `rendered()`
fake the products of `narrate` and `render`; `test_frame.py` compares drawn frames with
`tests/tier2/frames/` at 192×108 (its README says how to renew them and what the tolerance does
not see); `test_missing_packages.py` hides a package with a module on `PYTHONPATH`. One tier:
`.venv/bin/pytest tests/tier1`. Coverage of the subprocesses comes through
`COVERAGE_PROCESS_START`, which `run()` sets.

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

### 9 October 2026 — Script check: the Settings table and the title

**Goal.** `script.check(data, path)`: missing or empty required settings, unknown keys (unless
`x-`), numbers, `size`, source files, the brand kit found by walking up to `brands/`, the title.

**Test.** `tests/tier1/test_script_check_settings.py`, ten tests on a temporary project folder.

**Red.** `AttributeError: module 'videotools.script' has no attribute 'check'` ×10.

**Green.** First run after implementing: `5 failed, 15 passed`. Three were my line numbers again
(`"line 12: Settings: 'speed'…" != "line 11: …"`): the Settings rows are lines 9–19 of the
fixture, so speed is 12, size 15, an inserted `lead` 17 and `source-image` 18; counted by hand
and corrected. Two were the previous file's "same data" helper, which did not drop the new
`lines` map that `parse` now records for every table row; it drops it now. `20 passed in 0.03s`.

**Decision / surprise.** `parse` records the line of every table row (`data["lines"]`, keyed by
section or scene key and the row's key) so that a check can say `line N:`; PLAN.md item 1 says
"where there is one". A missing setting has no line, so its message starts `Settings:`.

**State.** Green: 20 tests. Next: Colours, Insets and scene-property checks.

### 9 October 2026 — Script check: Colours, Insets, scenes, cues and side panels

**Goal.** The rest of the format's rules: `#RRGGBB`, four-number insets, unique scene keys,
known properties, `kind`, a lettered step's `source`, insets that exist, numeric `extra` and
`min`, the side-panel kinds with their list and their cue, cues or `extra`, cue numbering,
known sub-bullets, `mistake` with ` / ` and at most one per scene, `step` with a steps panel
and an item that exists, `added:` not empty in cues and lists.

**Test.** `tests/tier1/test_script_check_scenes.py`, nineteen tests.

**Red.** `19 failed`: every one an assertion mismatch against `[]`.

**Green.** After implementing: `5 failed, 34 passed`, all five my line numbers once more (I had
forgotten the `### Pictures` lines before the end scene: it starts at 67, not 65; the inset row
is 39, not 40). Printed the fixture with its numbers, corrected the five, `39 passed in 0.07s`.

**Decision / surprise.** A side-panel problem names the `side-panel` row's line when the
property is written, and the scene heading's line when the default applies. Three fixture
miscounts in three increments: from now on every expected line number is read off a numbered
print of the fixture before the test is run, not counted by eye.

**State.** Green: 39 tests. Next: `script.read` (refusal as an exception), typed settings with
defaults, then the `check-script` command.

### 9 October 2026 — Script reader: `read`, `ScriptError`, typed settings and accessors

**Goal.** `script.read(path)` returns the data or raises `ScriptError` listing every problem
(a missing file too); `settings(data)` types the Settings table with the format's defaults;
`kind`, `extra`, `side_panel`, `spoken`, `minimum`, `mistake`, `folder`; the example script
reads clean.

**Test.** `tests/tier1/test_script_read_and_settings.py`, ten tests.

**Red.** `AttributeError … has no attribute 'read'` (5), `'ScriptError'` (3), `'settings'`,
`'folder'`: `10 failed`.

**Green.** `49 passed in 0.08s`, first run after implementing.

**Decision / surprise.** The public `side_panel(scene)` returns a typed `(kind, name, cue)`; the
string form the checker uses became `_side_panel_text`.

**State.** Green: 49 tests. Next: the `check-script` command, Tier 2.

### 9 October 2026 — `check-script`

**Goal.** The first command: `--help`, usage, the summary, problems listed with exit 1, a
missing file (exit 3), `--json` writing the parsed script and refusing an existing file, a
path with spaces, quotes, `$` and an accent, and the script never modified.

**Test.** `tests/tier2/test_check_script.py`, nine tests, run through `tests/tier2/conftest.py`'s
`run()` (the wrapper as a subprocess under the venv's Python).

**Red.** `8 failed, 1 passed`: exit 1 with `NotImplementedError` tracebacks against every
expectation. The ninth, `the_script_is_never_modified`, cannot fail against a command that
writes nothing, so after the green run the code was broken to write `--json` over the script:
`1 failed, 8 deselected`; restored (by hand: the file was not yet in git, so `git checkout`
could not).

**Green.** First run after implementing: `2 failed, 7 passed`, both test errors: the mistake
cue's line (101 in the example, 100 with the voice row removed; I had written 69 without
counting), and the hostile-path test had moved the video folder out from under `examples/`, so
the brand kit could not be found (a manual run on a copy kept under `examples/videos/` passed).
Then `9 passed`; the whole suite `58 passed`.

**Decision / surprise.** Coverage showed 0% for the two command modules because Tier 2 runs them
in subprocesses. pytest-cov 7 no longer hooks subprocesses itself; coverage.py 7's `.pth` hook
does when `COVERAGE_PROCESS_START` names the config and `parallel = true` is set, so `run()`
sets the variable and `pyproject.toml` the option: `TOTAL 99%`. `videotools/cli.py` holds what
every command shares: the exit codes, `Failure`, `report`, `refuse_existing`.

**State.** Green: 58 tests, coverage 99%. `check-script` works on the example. Next: the
timeline (item 3).

### 9 October 2026 — The timeline

**Goal.** `timeline.build(settings, scene, clips, estimate)`: cue starts and lengths from clip
lengths, gap, minimum, lead, tail and extra, rounded to frames; `cue(t)` and `p(t, cue, a, b)`;
a missing clip refused for rendering, estimated (and listed) for stills; `clips_for(timing,
scene)`; the easing helpers.

**Test.** `tests/tier1/test_timeline.py`, eleven tests with hand-written clip lengths.

**Red.** `NotImplementedError` ×10 and `no attribute 'clips_for'`: `11 failed`.

**Green.** `69 passed`, coverage 99%, first run after implementing.

**Decision / surprise.** One rule for "now": the cue whose start is at or before `t`, with a
nanosecond of floating-point slack (`0.7 + 1.55` is not exactly `2.25` in binary); the prototype's
50 ms early switch is gone. Rounding to frames uses Python's `round` (half to even), pinned by a
test at 157.5 frames.

**State.** Green: 69 tests. Next: the brand-kit and config readers (the rest of item 1).

### 9 October 2026 — The brand-kit and config readers

**Goal.** `brand.read(folder)`: Identity, Colours (as 0–1 triples), Fonts (role → name and
file, files checked, fallbacks for the four optional roles), Mark, Illustration (files checked),
Settings typed with defaults; `colour()` resolving a role or a hex value; `text_colour()` with
the small-text rule; `folder_for()`; every problem listed in `BrandError`. `config.read()`:
`KEY=value`, comments, quotes, `~`, unknown keys refused, `VIDEO_TOOLS_CONF`.

**Test.** `tests/tier1/test_brand.py` (eleven) and `tests/tier1/test_config.py` (four).

**Red.** `NotImplementedError` ×12, `no attribute 'folder_for'`, `'ConfigError'`, `'path'`:
`15 failed`.

**Green.** After implementing: `1 failed, 83 passed`: the problems came out in the wrong order
(missing tables reported before everything else). Two changes to the code, not the test: a
missing table is reported in its place, and a table whose header is there but whose rows are
gone counts as present, so its missing key is named (`Illustration: 'end-card' is missing`
rather than `no 'Illustration' table`). Then `84 passed`, coverage 99%.

**Decision / surprise.** The brand reader resolves font fallbacks (`body-medium` → `body`, …)
so the chrome never has to; `font_files` holds only the roles the kit names, for the font
loader. `config.read` expands `~` only in `_DIR` keys.

**State.** Green: 84 tests. Item 1 and item 3 done: build step 2 complete. Next: step 3, `narrate`.

### 9 October 2026 — `narrate`

**Goal.** One clip per cue from the speech model, trimmed; `timing.json`; voice and speed from
flags over script over config; `--scenes`; refusal to overwrite and `--replace`; `--dry-run`;
the model folder and the voice checked; the packages' absence and the model's failure as
useful errors; no networking module anywhere in the package.

**Test.** `tests/tier1/test_narrate_trim.py` (five, on numpy arrays), `tests/tier1/test_no_network.py`
(two: a scan of the package's imports, and every module imported in a fresh interpreter),
`tests/tier2/test_narrate.py` (nineteen) against `tests/stubs/kokoro_onnx/`, a fake package the
conftest puts on `PYTHONPATH`, which logs its calls and returns a waveform whose length depends
on the word count, with silence at both ends for the trimming to remove.

**Red.** `23 failed, 3 passed`: `NotImplementedError` and exit 1 tracebacks against every
expectation. The three that passed (the two no-network invariants and "the script and the
config are never modified") were then proved by breaking the code: narrate appending to the
script `1 failed`; `import socket` added to a module `2 failed`; both restored.

**Green.** First run after implementing: `1 failed, 23 passed`, the test's own word counts for
scene B (10 and 14 words, counted with the reader; I had written 8 and 12). Then `19 passed`;
the whole suite `110 passed`, coverage 99%.

**Decision / surprise.** Flags over script over config: the format requires `voice` and `speed`
in the script, so the config's `VOICE` and `SPEED` only ever apply to a script that leaves them
blank, which the reader refuses; they stay as documented defaults. `timing.json` is rewritten
whole after every scene, and `--replace --scenes` keeps the other scenes' entries. A missing
package is detected by a stub `kokoro_onnx.py` that raises `ImportError` first on `PYTHONPATH`,
since the real package is installed in the venv.

**State.** Green: 110 tests. Next: Tier 3 (a real run on a scratch copy), the README's set-up
steps, then step 4 once Squirrel settles the scene-code interface.

### 9 October 2026 — The wrappers run under the venv; Tier 3 for `narrate`

**Goal.** A command typed in Terminal runs under the repository's `.venv` whatever `python3` the
shell finds.

**Test.** `tests/tier2/test_wrappers.py`: three tests on a copy of the wrappers beside a fake
`.venv/bin/python` shim that logs its use.

**Red.** The Tier 3 real run first: `./narrate COPY/script.md` under the shell's `python3`
(`/opt/homebrew/bin/python3`, 3.14) failed with `the speech packages are not installed in this
Python`: the wrapper's `#!/usr/bin/env python3` ran the Homebrew default, not the venv (the
suite had passed because `run()` uses the venv's interpreter). Then the test:
`FileNotFoundError: … venv.log` (the shim never ran).

**Green.** First fix (an environment marker alone) re-ran even when already under the shim
(`'used-the-venv\nused-the-venv\n' == 'used-the-venv\n'`); the wrapper now knows it is under the
venv by `sys.prefix` (a real venv) or the marker (the test's shim sets it). `113 passed`. Then
Tier 3 on a scratch copy with `VIDEO_TOOLS_CONF` naming a scratch config (Squirrel's own
`~/.video-tools.conf` is his to write, README step 3):
```
title_01.wav  2.314 s
title_02.wav  3.094 s
A_01.wav  3.283 s
…
R_02.wav  4.714 s
Wrote 11 clips and …/work/narration/timing.json
33.44s user 0.27s system 339% cpu 9.934 total
```
A second run on scene A refused with the three files listed, exit 3. `check-script`'s code under
`/usr/bin/python3` (3.9): `No problems found.`

**Decision / surprise.** The wrapper re-executes itself with `os.execv` under `.venv/bin/python`
when that file exists beside it; with no `.venv` (the device shell, `pip install --user`) it runs
as it is. README written (install, set-up, the two commands, exit codes); the example's `work/`
and `out/` are gitignored so a Tier 3 run never lands in a commit.

**State.** Green: 113 tests, 99%. Steps 1–3 done. Step 4 (chrome) waits on Squirrel's decision on
the scene-code interface (PLAN.md open question 2); meanwhile the parts that do not depend on it
(fonts, drawing primitives, camera, `crop-insets`, `font-weights`, `assemble`, `check-video`) can
go first: a reordering of PLAN.md's build order, to be confirmed by him.

### 9 October 2026 — The font loader and the camera

**Goal.** `fonts.load(kit, work_folder)`: CoreText registration for the process on macOS, a
private `fonts.conf` and `FONTCONFIG_FILE` elsewhere, each file once; `camera.Camera` and the
plane helpers, as numbers.

**Test.** `tests/tier1/test_fonts.py` (three; the first in a fresh interpreter so the fonts are
loaded before cairo's first text) and `tests/tier1/test_camera.py` (five).

**Red.** Camera: an `ImportError` for `front`, `top`, `end` first (wrong reason; stubs added),
then `NotImplementedError` ×7 and the probe subprocess failing: `8 failed`.

**Green.** `1 failed` after implementing: the fontconfig file held
`tests/tier1/../../examples/brands/paperboat/fonts`, because `brand.read` kept the folder as
given. The reader now absolutises it. `121 passed`, coverage 99%.

**Decision / surprise.** The fontconfig branch (`platform="linux"`) is tested on the Mac only
as far as the file it writes and the variable it sets; whether cairo there honours a
`FONTCONFIG_FILE` set in-process before the first text is still "Things checked" 5, for the
device shell. New code is written with f-strings; the lint pass will convert the earlier
`%`-formatting (ruff's UP031 flags 98 of them) rather than mixing styles by hand now.

**State.** Green: 121 tests. Next: the drawing primitives.

### 9 October 2026 — The drawing primitives

**Goal.** `videotools.draw`: the prototype's `core.py` primitives with every colour passed in:
`rgb`, `shade`, `mix`; `text` (anchors, tracking, alpha), `text_width`, `wrap`; `poly`, `line`,
`rrect`, `fill_rrect`, `circle`, `bezier`, `cut`, `arrow` (drawn on to a fraction); `badge`,
`tag` (pill), `callout`, `dimension`, `hand`.

**Test.** `tests/tier1/test_draw.py`, nine tests reading pixels back from small surfaces.

**Red.** `AttributeError` for each missing function and `NotImplementedError` for `shade`:
`9 failed`.

**Green.** `2 failed, 7 passed` after implementing: both the tests' precision, not the code
(half-alpha black on white is 127 under cairo's rounding, not 128; the pixel in the middle of a
pill is anti-aliased text). Then `130 passed`, coverage 99%.

**Decision / surprise.** `callout`'s leader-line colour is `leader`, since a parameter named
`line` would shadow the function. The hand keeps the prototype's geometry (fingertip at the
origin, sleeve 150 px behind) with its skin, outline and sleeve colours as arguments; a video's
colours table supplies them.

**State.** Green: 130 tests. Next: `crop-insets` and `font-weights` (item 9), then `assemble`
and `check-video` against stub ffmpeg/ffprobe; chrome and `stills` when the interface is settled.

### 9 October 2026 — `crop-insets` and `font-weights`

**Goal.** Item 9: every Insets box cut from `source-image` and sized for the column (388 wide,
330 tall, 360 for a tall box), the page at 750 tall for the title card, into `work/insets/`;
static instances of a variable font per weight under `PREFIX <Weight>` names.

**Test.** `tests/tier2/test_crop_insets.py` (nine) on the example; `tests/tier2/test_font_weights.py`
(eight) on a tiny invented variable font built by `tests/tier2/fontfixture.py` with fontTools
(two glyphs, a `wght` axis 300–800, the A's width varying), including an italic one.

**Red.** crop-insets `NotImplementedError`/exit 1 against each expectation. font-weights first
failed in the fixture (`KeyError: 'wwsFamily'`: fontBuilder's name-table keys), the wrong
reason; with the fixture fixed, `7 failed, 1 passed`. The two "never modified" tests were proved
by breaking each command to append to its input: `1 failed` each.

**Green.** `17 passed` first run after implementing; the suite `147 passed`, coverage 96%
(`draw.py` at 85% pulls it down: its untested branches are listed for the coverage pass).

**Decision / surprise.** The whole page's file is `title-page.png` and an inset of that name is
refused. `crop-insets` has `--dry-run` like every other command though the request did not ask
for it. A weight is one of 100–900 in hundreds (argparse refuses anything else, exit 2); the
axis range is checked against the font (exit 3). An italic font is known by OS/2 fsSelection,
head macStyle or its subfamily name.

**State.** Green: 147 tests. Next: Tier 3 for both, then `assemble` and `check-video` against
stub ffmpeg/ffprobe.

### 9 October 2026 — Tier 3 for the small commands; a naming find; ffmpeg's formats recorded

**Goal.** Both commands on the real thing, and the beliefs `assemble` and `check-video` rest on.

**Red / Green.** `crop-insets` on the scratch copy of the example wrote the five files as the
tests say (`A.png 388x167`, `full.png 248x360`, `title-page.png 529x750`). `font-weights` on the
real EB Garamond variable fonts (read-only, output into the scratchpad) made files whose names
and glyph widths equal the brand's own six `EBG-*.ttf`, except one: the italic at 400 came out
`EBG RegularItalic` where the brand has `EBG Italic`. A test for that (`the_italic_at_regular_
weight_is_just_italic`) failed `1 failed`, the fix made it `9 passed`, and the re-run matched:
`EBG-Italic.ttf names equal: True A advance equal: True`.

**Decision / surprise.** The real formats of ffprobe (JSON with numbers as strings),
`volumedetect` and `silencedetect` (lines on stderr) are in PLAN.md "Things checked" 6, from an
invented 3 s file made in the scratchpad; a missing input makes ffmpeg exit 254. The stub ffmpeg
and ffprobe will speak these formats.

**State.** Green: 149 tests. Next: `assemble` against the stubs.

### 9 October 2026 — `assemble`

**Goal.** Segments joined in script order (concat demuxer, streams copied), every clip at its
scene's start plus its cue's start plus 50 ms in a 48 kHz mix normalised to 0.89, muxed with
AAC; refusals naming every missing segment and clip, segments that do not add up or chain,
missing timings, an existing output (never replaced) and existing intermediates (unless
`--replace`); ffmpeg's exit status checked at both steps, the partial file named; length, size
and SHA-256 printed.

**Test.** `tests/tier2/test_assemble.py`, seventeen tests. `tests/stubs/ffstub.py` stands in for
ffmpeg and ffprobe (the conftest puts two shell wrappers on PATH that name it through
`FFSTUB_NAME`): media files are fake `key=value` text files, every call is logged, and
`FFSTUB_FAIL` makes a named job fail after writing a partial output. The conftest's `narrated()`
writes real 1 s clips with soundfile and a `timing.json`; `rendered()` fakes one segment per
scene with the frame counts the timing gives (249, 261, 237, 159, 267, 243, 171).

**Red.** `16 failed, 1 passed`: `NotImplementedError` tracebacks. "Never modified" proved after
the green by making assemble append to a segment: `1 failed`.

**Green.** Three rounds: the stub dispatched on its own file name instead of `FFSTUB_NAME` (every
ffprobe call hit the ffmpeg branch: `unexpected arguments`), fixed in the stub; then the
fixture's sine tone began with a zero sample so the first loud sample was 36001 not 36000 (a
cosine now); and two failure tests wrongly expected an empty stdout, when progress printed
before the failure stays there. `17 passed`; the suite `165 passed`, coverage 94% (`ffmpeg.py`'s
probe, levels and silences are for `check-video`).

**Decision / surprise.** Resampling is linear (`numpy.interp`), enough for speech at 24 kHz to
48 kHz. A scene's segments must chain from frame 0 (`A_00000`, `A_00100`, …) and their counted
frames must equal the timeline's; both are checked with ffprobe before anything is written.
`videotools/ffmpeg.py` holds the running and parsing of ffmpeg and ffprobe for every command.

**State.** Green: 165 tests. Next: `check-video`.

### 9 October 2026 — `check-video`

**Goal.** Length within a frame, peak below 0 dBFS, silences only outside cue windows and every
cue heard, a sheet of one frame per scene; every problem listed, exit 1.

**Test.** `tests/tier2/test_check_video.py`, fourteen tests; the stub's fake media carry
`max_volume`, `mean_volume` and `silences`, and its frame extraction writes a real 4×4 PNG so
the sheet can be pasted.

**Red.** `12 failed, 1 passed`: `NotImplementedError`. "Never modified" proved after the green
(check-video appending to the video: `1 failed`).

**Green.** `1 failed, 12 passed` after implementing: my test said a silence beginning 0.3 s into
a 1 s cue meant the cue was not heard, and the code said only that it overlapped. The rule was
not pinned down, so it is now (PLAN.md item 8): a cue's window is its clip's span as `assemble`
lays it (start + 50 ms), overlaps under 0.1 s are the detector's slack, a silence overlapping a
window by more than that is a problem, and one covering the window to within the slack means the
cue was not heard. Three tests pin the three cases. `14 passed`; the suite `180 passed`, 94%.

**Decision / surprise.** The sheet is four frames a row; frames are extracted into a temporary
folder, the one place a command writes outside the video's `work/`. README brought up to date
with the four commands added since its first draft.

**State.** Green: 180 tests. Six of eight commands built. Next: the scene-code interface
(Squirrel), then chrome, `stills` and `render`; then a coverage pass (`draw.py`, `ffmpeg.py`)
and lint.

### 9 October 2026 — The frame: chrome, scene modules, stored images

**Goal.** Item 4: `videotools.scenes` (the loader and the `Frame` object, the interface of
"Settled" 13), `videotools.chrome` (the rules: layout, tracker, title steps, current step,
checklist progress) and `videotools.frame` (`Video`, loading everything once, and `draw_frame`
with every chrome element), plus the example video's seven scene modules.

**Test.** `tests/tier1/test_scenes.py` (eight), `tests/tier1/test_chrome_rules.py` (eight),
`tests/tier2/test_frame.py` (seventeen: nine by pixels, eight against stored images at 192×108
with a mean difference below 6/255; `tests/tier2/frames/README.md`).

**Red.** `8 failed` (scenes), `8 failed` (chrome rules), `1 failed, 16 errors` (frame):
`NotImplementedError` throughout.

**Green.** Scenes: first run. Chrome rules: `tracker_place` could not know an unlettered
scene's position from the places alone, so it and `tracker_done_now` take the script data (the
tests changed to match before the green). Frame: two faults, then `9 passed` with only the
stored images missing: the example's scene modules named their function `draw` and so shadowed
the `videotools.draw` module they had imported (they import it as `d` now; the scenes README says
why), and `Video` loaded only the insets scenes name where the table has more. The eight frames
were drawn at full size, looked at (header, roundel, tracker with the shared "Corners" place, the
inset and key points, the steps panel with 2 current and 1 done, the custom panel, the ticking
checklist, the mistake panels with their tags, the title card with the tilted page, the end card
with both credits), one example label moved clear of the hand, and stored reduced. Then
`33 passed` for the three files.

**Decision / surprise.** The loader puts the scene-code folder on `sys.path` only while a
module is imported, so scene modules can share a helper (`_sheet.py` in the example) without the
folder staying importable. Captions: the band is drawn for any scene with cues, the text only once
the first cue has started (so a scene opens on an empty band, as the prototype did). The stored
images are characterisation references, made by the code and inspected, not drawn by hand.

**State.** Green: 33 new tests. Next: `stills` and `render`.

### 9 October 2026 — `stills` and `render`

**Goal.** Items 5 and 6: frames at given times on a labelled sheet, estimates with a warning,
every refusal; scenes piped frame by frame to ffmpeg with the script's settings, `--frames`,
`--dry-run`, refusal without timings or over a segment, ffmpeg's failures (exit, death, a wrong
frame count) reported with the partial file named.

**Test.** `tests/tier2/test_stills.py` (seven), `tests/tier2/test_render.py` (twelve); the stub
gained `FFSTUB_DROP` (reports one frame fewer, as a bad encode would) beside `FFSTUB_DIE`.

**Red.** `18 failed, 1 passed`: `NotImplementedError`. "Never modified" proved after the green
(render appending to the script: `1 failed`).

**Green.** Five faults on the first run: four in the tests (a pixel probed under the sheet's own
label; argparse wrapping the usage line; two argument indexes) and one real: `communicate()`
after closing ffmpeg's stdin raised `write to closed file`; render reads stderr and waits
instead. `19 passed`; the whole suite below.

**Decision / surprise.** `script.select(data, keys)` is the one place `--scenes` is parsed
(`narrate` still has its own copy: to fold in at the lint pass). Dry run reports each scene's
length, frame count and segment path and the totals. The sheet labels each frame with its
scene, time and cue in the brand's display font.

**State.** All eight commands built. Next: Tier 3 of the whole chain on the scratch copy, then
coverage, README and lint.

### 9 October 2026 — Tier 3: the whole chain on the example; the sheet's grid

**Goal.** Every command for real, in order, on the scratch copy of the example (narration and
insets already made there).

**Green.** `stills` (four frames, 2×2; estimated nothing, the clips were there); `render --dry-run`
(7 scenes, 60.067 s, 1802 frames); `render`: every scene, e.g.
```
Rendered C: 320 frames in 1.5 s (212.1 frames/s)
./render … 24.70s user 4.45s system 247% cpu 11.763 total
```
`assemble`: `length 60.067 s (1802 frames), size 2546758 bytes`, sha256 `dcee4bb1…`; `check-video
--sheet`: length OK, `peak -1.0 dBFS, mean -21.9 dBFS`, six silences all between cues or on the
end card, every cue heard, `No problems found.`, exit 0.

**Decision / surprise.** The real sheet showed `check-video`'s grid wrong: four columns of 16:9
frames filled only half of each 480×540 cell. The test was changed first (a near-square grid,
three by three for seven, frames fitted to their cells, `1 failed`), then the code (`14 passed`).
Rendering runs at about 200 frames a second on this Mac, four to five times the device shell's
prototype. The 1,802-frame video took under a minute end to end.

**State.** Every command works on the real thing. Next: coverage and lint.

### 9 October 2026 — Coverage pass and lint pass

**Goal.** Coverage of `draw.py`'s untested branches (it was 85%); then lint as its own pass.

**Test.** `tests/tier1/test_draw_more.py`, seven characterisation tests (tracking, strokes,
dashes, `cut`, curved arrows, alpha zero, mirrored and labelled hands, right-anchored pills):
`7 passed` at once, then the code broken seven ways: six breaks caught (`1 failed` each); the
seventh, removing the badge's alpha guard, was not, because at alpha 0 cairo paints nothing
either way: that guard is a shortcut, not a behaviour, and the test pins the behaviour.

**Lint.** `pyproject.toml` takes book-tools' rule set (`E, F, W, I, B, UP`; tests may have long
lines; the example's scene modules import their shared helper by name), line length 120.
`ruff --fix --unsafe-fixes` converted 130 things (printf formatting to f-strings, mostly) and
the suite stayed green (`238 passed`); the remaining 86 by hand: the rest of the `%` formats,
`from e`/`from None` on every raise inside an except, 25 long lines wrapped, and the shared
`video` fixture moved to `tests/tier1/conftest.py` (ruff's F811 on fixture imports). `narrate`'s
own `--scenes` parser folded into `script.select`. `All checks passed!`; suite `238 passed`,
coverage 98%. Found by lint, not by testing: nothing in behaviour; two unused imports and one
unused variable were the only non-style finds.

**State.** Lint clean, 238 tests, 98%. README complete for all eight commands.

### 9 October 2026 — The second request arrives and is OK'd

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-2.md` (18:44–18:55, from
Claude on the training-video side, after trying the tools on the bed script and kit in the Linux
device shell): the tools fit, but seven things, one blocking. Reported to Squirrel at 18:57 with
each claim checked against the code: (1) `brand._tables` reads every row under a read heading,
so the real kit's contrast table is refused; (2) `stills` and `render` let `BrandError` escape as
a traceback with exit 1; (3) `check-script` never reads the kit; (4) the sheet's label covers the
frame's header (seen on their `s1.png`); (5) one fonts test is CoreText-only; (6) the wrappers
find no usable venv on Linux; (7) the prototype's `ripple` and `clip_half` are missing, and the
diary's "21:30" was wrong (the clock said 18:57, the last commit 18:30). Squirrel (19:01): "1.
agreed 6. agreed 7. agreed. Go ahead and make the update per the request": read only `Key |
Value` tables; a `VIDEO_TOOLS_PYTHON` setting plus a README section; the two helpers added to
the package. Recorded in PLAN.md ("Settled" 14, build step 9, items 1, 4, 5, Configuration,
"Things checked" 5); the item moved to `inbox/done/`.

**State.** Next: item 1, the brand reader's tables, test-first.

### 9 October 2026 — Request 2, item 1: only `Key | Value` tables are read

**Goal.** A table under a read heading whose header is not `| Key | Value |` is for people and
skipped; a `Key | Value` table beside it is still checked.

**Test.** `tests/tier1/test_brand.py`:
`a_table_under_a_read_heading_without_a_key_value_header_is_for_people_and_skipped` (the demo
kit with a contrast table under Colours reads identically to the kit without it) and
`a_key_value_table_with_a_bad_colour_is_still_refused_beside_a_skipped_one`.

**Red.** `2 failed, 11 passed`:
```
E   videotools.brand.BrandError: …/brands/demo: Colours: 'Pair' is not #RRGGBB: Ratio
E   Colours: 'ink on background' is not #RRGGBB: 11.2
```
The request's failure exactly: the contrast rows read as colours.

**Green.** `_tables` now treats the first line of each table as its header and reads the rows
only when its first two cells are `Key` and `Value`; a table ends at its first non-table line.
`13 passed`; the suite `240 passed`, 98%. Read-only check on the real kit
(`training-video/brands/douglassquirrel`): reads, 12 colours, 7 fonts (with fallbacks),
7 settings.

**State.** Item 1 done. Next: item 2, `BrandError` in words with exit 3.

### 9 October 2026 — Request 2, item 2: a refused brand kit is reported in words, exit 3

**Goal.** `stills` and `render` (the two commands that load the kit; `assemble`, `check-video`,
`crop-insets` and `narrate` never do) print the kit's problems on stderr and exit 3, never a
traceback or exit 1.

**Test.** `test_a_malformed_brand_kit_is_refused_in_words_with_exit_3_not_a_traceback` in
`tests/tier2/test_render.py` (a bad colour) and `tests/tier2/test_stills.py` (a missing
`website`); both check no segment or sheet is written.

**Red.** `2 failed`: `assert (1, '') == (3, '')` for each: the uncaught `BrandError`'s exit 1.

**Green.** `brand.BrandError` caught beside `ScriptError` in both commands' `main`.
`21 passed` for the two files.

**State.** Items 1 and 2 done. Next: item 3, `check-script` reads the brand kit.

### 9 October 2026 — Request 2, item 3: `check-script` reads the brand kit

**Goal.** A kit `render` would refuse is found by `check-script`: its problems listed after the
script's, each prefixed with the BRAND.md path; a kit the script check already found missing is
one problem, not two.

**Test.** `tests/tier2/test_check_script.py`:
`a_malformed_brand_kit_is_listed_with_the_scripts_problems_naming_the_brand_file` and
`a_missing_brand_kit_is_one_problem_not_two`.

**Red.** `2 failed`: the first `assert (0, '') == (1, '')` (the kit's bad colour passed), the
right failure. The second failed on my own wrong prediction of the existing message (it has a
`line 17:` prefix and says "has no brands/nokit/BRAND.md under"); the test's string was
corrected to the real message, and the behaviour (one problem) was already right, so that test
is a characterisation of the guard, not a red-green cycle.

**Green.** `check_script.brand_problems` reads the kit through `brand.folder_for` and
`brand.read` and skips it when the script's problems already name the brand. `11 passed`; the
suite `244 passed`, 98%. Still Python 3.9: `videotools.check_script.main` run under
`/usr/bin/python3` (3.9.6) on the example prints "No problems found."

**State.** Items 1–3 done. Next: README for the three, commit; then item 4.

### 9 October 2026 — Request 2, item 4: the sheet's label under the frame

**Goal.** `stills` covers no pixel of a frame: the frame is scaled to fit the cell above a
36 px strip that holds the label.

**Test.** `tests/tier2/test_stills.py::the_label_sits_in_a_strip_under_the_frame_and_covers_no_pixel_of_it`:
the frame region of a cell equals the same frame drawn alone and scaled (`ImageChops.difference`
empty), the header's corner is the frame's background, the strip has its fill and white text.

**Red.** First `AttributeError: … no attribute 'frame_size'`; with that function alone,
the right failure: `assert (0, 8, 896, 504) is None` (the label box from row 8 down differed).

**Green.** The frame goes into `frame_size(cell)` (896×504 in a 960×540 cell; 1856×1044 at
1x1) and the label into the strip beneath. Three pixel probes in the two older tests moved,
predictably: one had landed on the tracker's roundels once the frame shrank, and the band
probes sit 36 px higher. The first real sheet showed the strip in the band's own grey, so the
two read as one; the strip is `#555555` now (test changed to match before the code).
`9 passed`.

### 9 October 2026 — Request 2, item 5: the CoreText test skipped off macOS

**Goal.** `test_loading_twice_registers_each_file_once` (the only test calling `fonts.load`
with `platform="darwin"`) is skipped where there is no CoreText.

**Test / check.** No red-green: it is a `skipif` marker, not behaviour. Its failure on Linux
is the training-video project's report (`undefined symbol: CFURLCreateFromFileSystemRepresentation`),
not reproduced here. Checked that the marker fires: with `sys.platform` set to `linux` in the
test process, `1 skipped … registers fonts with CoreText, which only macOS has`; on this Mac
`3 passed`. The Linux Tier 3 results are in PLAN.md "Things checked" 5, marked as reported.

**State.** Items 1–5 done. Next: item 6, `VIDEO_TOOLS_PYTHON`.

### 9 October 2026 — Request 2, item 6: `VIDEO_TOOLS_PYTHON`

**Goal.** A wrapper runs under the Python `VIDEO_TOOLS_PYTHON` names, even beside a `.venv`,
once (no loop); a path that does not exist is a useful error, exit 3; unset, as before.

**Test.** `tests/tier2/test_wrappers.py`:
`video_tools_python_names_the_python_the_wrapper_runs_under_even_beside_a_venv` (a shim logs
that it was used; the log has exactly one line) and
`video_tools_python_that_does_not_exist_is_a_useful_error_exit_3`.

**Red.** `2 failed`: `assert 'used-the-venv\n' == 'used-other-python\n'` and
`assert (0, 'usage: n…') == (3, '')`: the setting was ignored.

**Green.** The same block in all eight wrappers: `PYTHON` is the setting, else `.venv`'s Python
if it exists; re-run under it unless already there (the `VIDEO_TOOLS_VENV` marker the exec
sets, or `sys.prefix` for the venv). `5 passed`. README: "Running from the Linux device shell".

### 9 October 2026 — Request 2, item 7: `ripple` and `clip`; the diary's time

**Goal.** The prototype's two fabric helpers in `videotools.camera`, generic: `ripple(x0, x1,
z, amp, n, phase)` and `clip(pts, f)`.

**Test.** `tests/tier1/test_camera.py`:
`ripple_runs_from_x0_to_x1_in_n_steps_about_z_within_the_amplitude` and
`clip_keeps_the_side_of_a_polygon_where_f_is_not_negative_cutting_edges_where_it_crosses`.

**Red.** First an `ImportError` (wrong reason); with stubs, `NotImplementedError` ×2. Before
that run I corrected my own hand-derived expectation for `clip`: walking the prototype's
algorithm, the cut square starts at the first crossing, `[(1.0, 0.0), (4, 0), (4, 4), (1.0,
4.0)]`, not where I had first written it.

**Green.** Both ported as they were (the prototype's `clip_half` renamed `clip`). `7 passed`.

**Decision / surprise.** The "21:30" in the previous "Where things stand" was never a clock
reading; the session that wrote it ended at 18:30. Corrected in the rewrite below, from the
clock, and a reminder to take every time from `TZ=Europe/London date +%H:%M`.

### 9 October 2026 — The third request arrives and is OK'd

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-3.md` (19:18–19:22,
training-video side): request 2 verified, all seven items, on Linux with the real kit; three
finds. Checked against the code and reported at 19:27: (1) `assemble` passes no `-y`, so real
ffmpeg prompts over an existing intermediate and `--replace` never works; the stub overwrote
silently, so the test lied; `render --replace` has the same latent fault. (2) numpy, soundfile
(assemble, narrate) and cairo (render, stills, frame, at module level) are unguarded imports.
(3) the label test's in-process reference gets fontconfig's fallback fonts on Linux once a tier
1 test has drawn text; the stored-image tests share the structure and their tolerance may hide
it. Squirrel (19:31): "agree with your thoughts on the package message. Go ahead and fix."
PLAN.md "Settled" 15; the item moved to `inbox/done/`.

**State.** Next: item 1, the stub made honest, then `-nostdin`/`-y`.

### 9 October 2026 — Request 3, item 1: `--replace` against real ffmpeg

**Goal.** `assemble --replace` and `render --replace` write over the files they listed, through
ffmpeg, and the finished video never; ffmpeg never stops to ask.

**Test.** The stub first: `tests/stubs/ffstub.py` now refuses an existing output without `-y`
with ffmpeg's own words ("Not overwriting - exiting", exit 1). Then the two existing replace
tests, sharpened: `test_existing_intermediates_are_refused_unless_replace` asserts no ffmpeg
call before the refusal, `-y` and `-nostdin` on the concat call, no `-y` on the mux;
`test_an_existing_segment_is_refused_unless_replace` asserts `-y` on the segment's call.

**Red.** With the honest stub alone, `2 failed, 28 passed`: both replace tests exit 4 with
`File '…' already exists. Overwrite? [y/N] Not overwriting - exiting`, the real failure the
request reported, and for `render` the latent one it had not reached.

**Green.** `QUIET` gains `-nostdin`; `assemble` passes `-y` for the concat output when it was
listed under "Replacing"; `render.encode` takes `replace`. Four exact argument lists in older
tests gained `-nostdin` (predicted). Full suite below.

**Decision / surprise.** The stub had been kinder than ffmpeg, so a test passed that the real
program failed: a reminder that a stub is only as good as its record of the real thing
("Things checked" 3 said nothing about an existing output). The `narration.wav` and
`segments.txt` intermediates are written by Python, so `--replace` already covered them.

### 9 October 2026 — Request 3, item 2: a missing package is one line, exit 4

**Goal.** Every package import a command needs (numpy, soundfile, cairo, Pillow, fontTools,
kokoro-onnx) fails as one line naming the package and its install, with the device-shell
setting mentioned only when `VIDEO_TOOLS_PYTHON` is unset (Squirrel, 19:31), exit 4, before
anything is written or printed.

**Test.** `tests/tier2/test_missing_packages.py`: nine cases, one per command and package, each
with the package shadowed by a module on `PYTHONPATH` that raises `ImportError`; and
`with_video_tools_python_set_the_device_shell_hint_is_left_out`. `conftest.run()` now unsets a
variable given as `None`.

**Red.** `10 failed`: `render` and `stills` with cairo hidden gave a traceback and exit 1 (the
module-level import); Pillow and fontTools cases gave the old wording; `assemble` and `narrate`
tracebacks. Three cases first failed in my set-up (no segments, no `--replace`, no video) and
were fixed before the real red.

**Green.** `cli.need(module)` does the import or raises the one-line Failure; used at each point
of use; `render` and `stills` no longer import cairo (or `frame`) at module level. `check-video`
checks for Pillow before running its checks when `--sheet` is given, so nothing is half done.
The narrate test's expected wording changed to the new one (predicted). Suite `259 passed`,
98%, lint clean. Tier 3: `crop-insets` under `/usr/bin/python3` (no Pillow) prints the line and
exits 4.

**State.** Items 1 and 2 done. Next: item 3, the label test's reference in a subprocess.

### 9 October 2026 — Request 3, item 3: references drawn in a fresh process; what the tolerance hides

**Goal.** The sheet-label test cannot depend on what ran before it in the process; the suite has
no other order dependence; the device-shell `--basetemp` note is in the README.

**Test.** `test_the_label_sits_in_a_strip_under_the_frame_and_covers_no_pixel_of_it` now draws
its reference frame in a new interpreter (the same code path as the command), exact comparison
kept. No red on this Mac: CoreText registration works at any time, so the Linux failure (their
report: bbox `(7, 14, 866, 487)` after `test_draw.py` ran first) cannot be reproduced here; the
change removes the cause (fontconfig fixing its font list at a process's first text call).
The suite run with tier 2 before tier 1: `259 passed`; no other order dependence found on macOS.

**Decision / surprise.** The thing I suspected when reporting: the stored-image tests (tolerance
6 at 192×108) had passed on Linux, so could they be drawing with fallback fonts and not know?
Measured on the scratch copy with `fonts.load` stubbed out:
```
title 2.0 fallback fonts, mean diff [5.95, 5.89, 5.71]
A 1.5 fallback fonts, mean diff [1.6, 1.46, 1.39]
A 5.0 fallback fonts, mean diff [15.85, 16.6, 20.89]
B 3.5 fallback fonts, mean diff [1.77, 1.67, 1.61]
B2 3.0 fallback fonts, mean diff [1.66, 1.57, 1.51]
C 6.0 fallback fonts, mean diff [2.82, 2.4, 2.22]
R 5.0 fallback fonts, mean diff [1.91, 1.85, 1.82]
end 1.5 fallback fonts, mean diff [1.43, 1.21, 1.11]
```
Six of eight within tolerance: those tests pin layout, not fonts, and say nothing about the
fonts on Linux. So a new test, `test_a_frame_drawn_in_a_fresh_process_uses_the_brands_fonts`:
frame A at 5.0 s in a fresh process with the fonts and without; the count of pixels that change
must exceed 20,000 (58,956 here); and a second fresh draw with fonts is pixel-identical. Checked
that it can fail: with both draws using the fonts, `0.0 > 5.0` failed, as it must. Recorded in
`tests/tier2/frames/README.md`, PLAN.md "Testing", and the README's Testing section (with the
`--basetemp` line).

**State.** Request 3 done. Next: "Where things stand", commit, push.

### 9 October 2026 — The fourth request: the bed video accepted; two small asks OK'd

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-4.md` (19:26–19:46,
training-video side; Squirrel had said "go ahead and do the remake" at 19:26): PLAN.md step 8
done, the re-made bed video matching the original to the frame and the millisecond, `check-video`
clean, 1,672 lines of scene code through the interface as documented. Three differences:
no heading over the checklist (the prototype had one); the pillow step's roundel and icon; the
hand's label at a fixed 28 px. Reported at 19:48. Squirrel (19:50): "Do 1 (with the new
property) and 3." So: a `side-panel-heading` scene property, proposed to the script format in
PLAN.md item 4 (the format file is theirs); a `label_size` on `draw.hand`. Item 2 not done.
PLAN.md "Settled" 16; the item moved to `inbox/done/`.

**State.** Next: item 1, the script reader's new property, test-first.

### 9 October 2026 — Request 4, item 3: the hand label's size

**Goal.** `draw.hand(..., label_size=28)`: the letter and its roundel scale with the size the
scene code passes.

**Test.** `tests/tier1/test_draw_more.py::the_hands_label_takes_a_size_and_its_roundel_grows_with_it`:
at 56, the roundel's fill reaches 36 px from the wrist; at the default it does not.

**Red.** `TypeError: hand() got an unexpected keyword argument 'label_size'`.

**Green.** Roundel radius `21 * label_size / 28`, text baseline likewise. `17 passed` for the
two draw files.

### 9 October 2026 — Request 4, item 1: `side-panel-heading`

**Goal.** A scene property `side-panel-heading`: accepted by the reader; a problem with a
`none` or `custom` panel; drawn in KEY POINTS' style above a `steps` or `checklist` panel, the
rows 38 px lower, or in place of KEY POINTS for `key-points`.

**Test.** `tests/tier1/test_script_check_scenes.py::side_panel_heading_is_a_scene_property_for_steps_checklist_and_key_points`;
`tests/tier2/test_frame.py::a_side_panel_heading_sits_above_a_checklist_and_moves_its_rows_down`
(scene R's first tick moves from row 153 to 191 and muted text appears above) and
`a_side_panel_heading_replaces_key_points_without_moving_the_list` (scene A's first accent
square stays put while the frame changes).

**Red.** Reader: `unknown property 'side-panel-heading'`. Frames: `153 == 153 + 38` failed and
the two scene A frames were byte-identical: the property was ignored.

**Green.** `SCENE_KEYS` gains the key and the rule; `frame.reference_column` draws the heading
and adds `HEADING_HEIGHT` for steps and checklist. The stored-image tests are unchanged, since
nothing moves without the property. `20 passed`, `20 passed`; suite below.

**Decision / surprise.** A pause before scanning for the first tick: scene R has no inset, so
its checklist starts at the column's top and the "first green row at 153" that looked like a
header pixel was the tick itself. The script-format wording for the property is proposed in
PLAN.md item 4; the format file is the training-video project's to change.

### 9 October 2026 — Requests 5 and 6 arrive and are OK'd

**Decision / surprise.** Request 5 (19:56–20:01): request 4 verified; two Linux test faults,
both confirmed by reading: `fresh_frame` hands its child the whole environment, so a
`FONTCONFIG_FILE` set by an earlier in-process frame gives the "without fonts" child the fonts;
and `conftest.run()` hands commands an exported `VIDEO_TOOLS_PYTHON`, so the wrappers re-run
under it. Request 6 (20:09): brand-aware methods on the frame object (colour, text, tag,
callout, dimension, badge, hand) so a video's glue module can go, and `code` optional for
title and end cards. Reported at 20:12 with the plan; Squirrel (20:14): "go ahead". PLAN.md
"Settled" 17, item 4 rewritten; both items moved to `inbox/done/`.

**State.** Next: request 5, item 2 first (it can be made red here), then item 1.

### 9 October 2026 — Request 5: the tests' environments cleaned

**Goal.** The suite passes with `VIDEO_TOOLS_PYTHON` (and `VIDEO_TOOLS_CONF`) exported, as the
README tells device-shell users; a child process drawing "without fonts" does not inherit a
`FONTCONFIG_FILE` an earlier in-process frame set.

**Test.** Item 2: the two tests they named, run with the variable exported. Item 1: no test of
its own (the leak is Linux-only); `test_frame.py` in file order and the suite with tier 2 first.

**Red.** Item 2, on this Mac with `VIDEO_TOOLS_PYTHON=/usr/bin/python3`: `2 failed` (`assert
False`: the wrappers re-ran under that Python). Then, with the runner fixed, the full suite the
same way: `1 failed, 216 passed, 47 errors`: every fixture that ran `crop-insets` through
`subprocess.run` directly inherited the variable too (exit 4, no Pillow in that Python).

**Green.** `conftest.clean_env()` drops `VIDEO_TOOLS_PYTHON`, `VIDEO_TOOLS_CONF` and
`FONTCONFIG_FILE`; `run()`, the wrapper tests and the two fresh-process children use it; the
five direct `crop-insets` calls became `cropped(example)` through `run()`. With both variables
exported: `264 passed`, 98%; `test_frame.py` in order `20 passed`; lint clean.

**Decision / surprise.** The request named two tests; the fixtures were the bigger leak, found
only by running the whole suite the way a device-shell user would. The README's Testing section
says the tests clean the environment.

### 9 October 2026 — Request 6, item 2: no code for title and end cards

**Goal.** A title or end scene without `code` loads no module and the chrome draws the card; a
step scene without one is still refused by name.

**Test.** `tests/tier1/test_scenes.py::a_title_or_end_scene_without_code_has_no_module_and_a_step_scene_still_must`,
and the example itself: its two `code` lines removed and `title_card.py`, `end_card.py` deleted,
so the stored-image tests for the two cards must still pass.

**Red.** `4 failed`: the loader's `scene title has no 'code' property…` for the tier 1 case and
for the title and end frames of the example.

**Green.** `scenes.load` returns `None` for a title or end scene without `code`;
`frame.draw_frame` draws the module only when there is one. Stored images unchanged.
`29 passed` for the two files; suite below.

**Decision / surprise.** Dropping the title card's `code` line moved the example's mistake
cue from line 100 to 99, and the check-script test names that line: changed to 99 (the test
pinned a position in the example, not a behaviour).

**State.** Request 5 and request 6 item 2 done. Next: item 1, the brand-aware frame methods.

### 9 October 2026 — Request 6, item 1: brand-aware drawing on the frame

**Goal.** Methods on `scenes.Frame`, each a thin layer over `videotools.draw`: `colour(name)`
(script's Colours, then brand roles, else a refusal listing both); `text`, `tag`, `callout`,
`dimension` (font by role, size × `font-size-scale`, colours by name, rule 3 on text and on a
pill's fill at the scaled size, every label through `label`); `badge`; `hand` (the script's
`skin`, `skin-dark`, `sleeve` or neutral defaults, the label on an accent roundel at 28 ×
scale). So a video needs no glue module.

**Test.** `tests/tier1/test_frame_methods.py`, seven tests on the example kit and a tiny scene
(a 20 px accent pill at scale 1.12 is 22.4 px and takes `accent-dark`; at 24 px, 26.9, it keeps
`accent`; unlisted text refused by all four; a font role that does not exist; badge colours;
the hand's sleeve, palm and roundel; callout and dimension pills). And the example's
`_sheet.label` rewritten as one `frame.tag` call: the stored images must not change.

**Red.** `NotImplementedError` ×6 (stubs), and one wrong test assumption corrected first: I had
asserted the example's `font-size-scale` was 1.0; it is 1.12 (the pill sizes still fall either
side of the limit).

**Green.** Two more faults in my tests, not the code: the sleeve probe sat where the label's
roundel is (the sleeve spans x−200..x−96, the roundel at x−150; probe moved to x−190), and the
default skin came back one unit off my `round()` (cairo's own 8-bit rounding; compared within
1). `7 passed`; suite below, stored images unchanged with the example on `frame.tag`.

**Decision / surprise.** `frame.colour` tries the script's Colours before the brand's roles, so a
script could shadow a role name; the refusal lists both so a typo is caught. `callout`'s pill
fill defaults to `surface` (the request left it open). The hand defaults (a neutral skin
`(0.93, 0.80, 0.66)`, its outline, a slate sleeve) are mine, named in the README.

### 9 October 2026 — Request 7: `check-script` checks the scene code without running it

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-7.md` (20:34–20:37):
requests 5 and 6 verified on Linux (the suite with the variables exported and in both tier
orders; twelve drawing cases pixel-identical between their glue module and the frame methods;
the cards identical without their modules). One ask: `check-script` passed a script whose step
scene had no `code`, which `stills` then refused. Reported 20:40; Squirrel (20:52): "go ahead".
PLAN.md "Settled" 18; the item moved to `inbox/done/`.

**Goal.** `check-script` reports, by script line: a step scene with no `code`; a `code` whose
module is missing (path named); a module that does not parse (its line); a module without a
top-level `def` of a function the scene needs; a missing `scene-code` folder. Standard library
(`ast`), nothing run, Python 3.9.

**Test.** `tests/tier1/test_scene_code_check.py`, six tests on the two-scene script with modules
written into a `scenes/` folder (one of them a module with a syntax error on line 3 after an
`os.remove` call that must never run); `tests/tier2/test_check_script.py::a_step_scene_without_code_or_with_a_module_lacking_a_function_is_listed`
on the example.

**Red.** `NotImplementedError` ×6 and, for `check-script`, `assert (0, '') == (1, '')`: it said
"No problems found." with scene A's `code` removed. One wrong guess of mine in the tier 2
expectation (the heading's line, 85 not 93) corrected before the green; a muddled line in that
test (appending `del mistake` to a module) removed.

**Green.** The loader's list of needed functions is now `scenes.needed(scene)`, used by both
`load` and the new `scenes.check_code(folder, data)`; `check_script.code_problems` calls it.
`27 passed` for the three files; the suite and the 3.9 run below.

**Decision / surprise.** The check sees only top-level `def`s: a function a module gets by
import or assignment is reported missing. The README says so; the bed's modules define theirs.
The loader's own runtime refusals are unchanged, so a module that parses but fails on import is
still caught by `stills`/`render`, with the error named.

### 9 October 2026 — Request 8: `check-video`'s sheet labels in a strip

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-8.md` (20:44–20:59): the
bed video rebuilt on the frame methods with no glue module, all 7,873 frames hash-identical
before and after, the whole chain with every `--replace` against real ffmpeg, `check-video`
clean; request 7 verified; one ask, `check-video --sheet`'s label still over the frame's corner.
Reported 21:03; Squirrel (21:07): "go ahead". PLAN.md "Settled" 19; item moved to `inbox/done/`.

**Goal.** `check-video --sheet` lays out each cell as `stills` does: the frame scaled to fit
above a 36 px strip holding the label in the brand's display font; no frame pixel covered.

**Test.** `tests/tier2/test_check_video.py::the_sheets_label_sits_in_a_strip_under_each_frame_and_covers_no_pixel_of_it`:
the stub's square frame fills 324×324 of a 640×360 cell, white beside it, the strip's fill and
white text under it.

**Red.** `assert (200, 40, 40) == (255, 255, 255)`: the frame still filled the whole cell.

**Green.** `videotools.sheet` (the strip, `frame_size`, `paste`) shared by `stills` and
`check-video`; `check-video` reads the brand kit for the label's font when `--sheet` is given
(a bad kit refused, exit 3, like the two drawing commands). The older sheet test's probes were
unaffected (they sat inside the smaller frame). `24 passed` for the two files; suite
`280 passed`, 98%, lint clean.

**Tier 3.** The whole chain again on the scratch copy of the example, on this Mac (a scratch
config naming `~/models/kokoro`, since `~/.video-tools.conf` here has no `SPEECH_MODEL_DIR`):
```
Wrote 11 clips and …/work/narration/timing.json
Rendered end: 171 frames in 0.7 s (234.4 frames/s) -> …/work/segments/end_00000.mp4
length 60.067 s (1802 frames), size 2546758 bytes
sha256 dcee4bb1adbd11215f8e7fb288572524b234764c30c593959396274539b0211b
narration in every cue's window: OK
sheet of 7 frames written to …/cv-sheet.png
No problems found.
```
The same length and SHA-256 as the first Tier 3 (9 October, "the whole chain"). The sheet
looked at: seven frames in a 3×3 grid, every header and roundel visible, each label in its
strip in the display font.

**State.** Request 8 done. Next: nothing waiting.

### 9 October 2026 — Session end and handover

**Decision / surprise.** Squirrel set `SPEECH_MODEL_DIR=~/models/kokoro` in
`~/.video-tools.conf` (21:17), checked with `narrate --dry-run` on the example (11 cues, the
model found, nothing written). The session's record, for whoever picks this up: nine commits
today after `a30428a`, one or more per request, every one green on the full suite with lint
clean, each pushed to `origin/main`; every behaviour through a test seen red first, with the
exceptions named in their entries (two Linux-only faults that cannot go red on this Mac, and
one `skipif` marker). "Where things stand" above is the handover.

**State.** Green: 280 tests, 98%, lint clean, pushed at `92006d9` plus this entry. Inbox
empty. Nothing waiting on Squirrel.

### 9 October 2026 — Tier 3: `assemble --replace` against real ffmpeg

**Goal.** The one thing the handover listed as untried on this Mac: `assemble --replace` with
the real ffmpeg 9.0.2 (the stub was made to mirror ffmpeg's refusal at request 3, but the real
program had only been seen by the training-video project on Linux).

**Check.** A fresh scratch copy of the example in the session's scratchpad; the chain
`check-script`, `crop-insets`, `narrate`, `render`, `assemble`: the same output as every earlier
Tier 3, `length 60.067 s (1802 frames), size 2546758 bytes`, sha256 `dcee4bb1…`. Then, with the
SHA-256 of the three intermediates and the output taken first:

1. `assemble` again, plain: `… /out/Folding a Paper Boat.mp4 already exists; give a new name`,
   exit 3; nothing changed.
2. `assemble --replace`, no `--out`: the same refusal, exit 3 ("Settled" 13: `--replace` never
   covers the finished video).
3. `assemble --replace --out new.mp4` with stdin closed: printed the three intermediates under
   "Replacing:", rewrote all three (new mtimes 21:34:21, same bytes and SHA-256 as before), did
   not stop to ask, wrote `new.mp4` with the same SHA-256 `dcee4bb1…`, exit 0. The finished video
   in `out/` kept its mtime and SHA-256.

**Decision / surprise.** No fault. One observation, not acted on: the refusal in case 2 says
"give a new name" and does not say that `--replace` leaves the finished video alone, so a user
who typed `--replace` to get past it may try it twice. A sentence in that message would cost
nothing; raised with Squirrel, not changed.

**State.** Green and clean as at the handover (280 tests, 98%; the suite not re-run this
session, no code changed). Nothing waiting.
