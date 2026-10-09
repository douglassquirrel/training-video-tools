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
