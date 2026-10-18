# DIARY.md — video-tools

## Where things stand

18 October 2026, afternoon, session open ("mac" on duty, the watch running). **Item 30 (audio-description-tools' request 7) is built: the lead-in that keeps a quiet first consonant (every cue and line given to the voice as phonemes, `, ` in front, a first s, f, θ, ʃ or h doubled; Squirrel's choice by ear), the `Say` column, and `--phonemes` with `--lines --dry-run`.** **Requests 1 to 20 are built in full**, each in the README: the eight commands
of the first request; the four checking commands (PLAN.md item 11); ✓ and ✗ as strokes and the
characters-a-font-lacks report (12); phoneme spans (13); the curtain and `stills --cue-changes`
(14); choreography described in the script and drawn from the video-elements library (15);
credits for the library's art (16); offsets where an anchor is read, the arrow's `progress`,
`head` and blank Where, a blank Size at the natural size, the blank-Size warning (17); an empty
label is no label (18); a callout's `leader`, an arrow's `via` and `dash`, `colour.ROLE=NAME`,
casts on title and end cards, a scene with no cues, `rotate` (19); **`linear` moves, `dim`,
percentages and spans across cues and to the scene's end, a CSV's rows and columns chosen with
`rows.where`, `rows.first`, `rows.columns` (20, request 18); `flash` (21, request 19); a text
parameter read from a file, `text.skip` and `text.first`, indices counted against the lines
chosen (22, request 20); every index counted as the element's description says: data rows,
columns, lines, tabs left to the element (23, video-elements' reply); **`stills` on any video file:
`--at`, `--every`, `--changes`, one PNG a frame at the video's own size, `stills.txt`, `--sheet`
with cells in the video's proportions (24, audio-description-tools' request 1, by mail); a grid of
0 or fewer columns or rows refused in words in both forms (25, their request 2); `narrate --lines
TABLE.md --out FOLDER`, each line of a description table to its own clip at speed 1.5 in af_heart, with
`timing.json` and an overrun warning (26, their request 3); **`setup-linux --venv DIR --model DIR
--conf FILE [--dry-run]`, the device shell's venv, packages, model check, config and three `export`
lines in one standard-library command (27, their request 4); `stills VIDEO --changes` scoring at
10 fps with the audio skipped (`--detect-fps`), `--from`/`--until` windows on `--every` and
`--changes` with slices into one folder, `stills.txt` a line at a time, `--sheet` alone drawing a
folder's listing (28, their request 5); each still written to a part name, listed, then renamed,
and in a window an unlisted still or a part file written over (29, their request 6)**. A new
session starts with `lobster-mail start` (the hook runs it; CLAUDE.md "Mail"), then CLAUDE.md,
PLAN.md (items 15 to 29 in full) and this section, then `inbox/`.

**Inbox: empty.** Everything that has arrived is in `inbox/done/`. **Mail: nothing open.** Request 7 (item 30) is in `done/`, its reply in `sent/` (18 October, 14:02 UTC). Requests
from other projects arrive by `lobster-mail` in `~/projects/mail/video-tools/` (CLAUDE.md
non-negotiable 17 and "Mail", since 17 October 2026; the command is
`~/projects/code/lobster-tools-code/lobster-tools/lobster-mail`, not on PATH). audio-description-tools'
request 1 (item 24) is in `done/`, its reply in `sent/` (17 October, 12:40); request 2 (item 25,
the grid crash) likewise, its reply sent at 13:15; request 3 (item 26) likewise, its reply sent at 14:40; request 4 (item 27) likewise, its reply
sent at 19:33; request 5 (item 28) likewise, its reply sent at 22:00, and their answer with the
device-shell timing (18:08 UTC) read and closed at 22:10; request 6 (item 29) likewise, its reply
sent at 23:00. The speed samples
Squirrel listened to were deleted on his OK (17 October, 17:00). A reply or a new
message goes only on Squirrel's OK ("Settled" 47). The handover for the next session was left by
`lobster-mail handover` at the end of this one (17 October, 23:10); `lobster-mail start` reads it
first. No watch is running; nobody is on duty.

Green: 718 tests, coverage 99%, `ruff check .` clean, committed and pushed to `origin/main`. **The
repository moved** to `~/projects/code/videos/video-tools` between 11 and 17 October; CLAUDE.md and the
README name the new path since 17 October, 17:05, and the venv was rebuilt there the same day.

**Waiting on Squirrel:** nothing. PLAN.md "Open questions" is empty: the lead-in's doubled
consonants (s, f, θ, ʃ, h) are "Settled" 57, and request 19's five adjustments are confirmed
("Settled" 58). Earlier: `-skip_frame noref` stays out
("Settled" 53, on audio-description-tools' device-shell timing of 18:08 UTC: 600 s slices in 15.6
and 21.4 s where the old whole run took 86 s).
The Tier 3 check of `setup-linux` in the real device shell is not done (a Mac dry run against the
real model folder is in the README). His other answers are in "Settled" 30
to 44; one is a rule for every session: when unsure whether an earlier OK covers a new inbox
item, ask. **video-tools may write into `~/projects/non-code/training-video/inbox/`** ("Settled"
38) and nowhere else in that project: replies to its requests go there, naming the commit to
check against; five notes are there so far. Writing into video-elements' inbox was OK'd once,
for one request ("Settled" 42), and is not a standing permission.

**video-tools needs video-elements at `d203f0a` or later, and says so:** a library whose
descriptions have no `counts` is refused when it is opened; nothing in the code allows for an
older one ("Settled" 44).

How a move's time works now, since four requests changed it in one night: a time is seconds
from its cue's start or back from its end, a percentage of its cue's length, or the scene's
end; a span may end in a later cue; `choreography.window(move, tl, panel)` is the one place
that turns a move into scene seconds, used by the check and by `perform`; with no cue, a
panel's times are within the mistake cue and a cue-less scene's within the scene. A parsed
move carries `end_cue` and `linear` only when it has them.

The stub `python3` for `setup-linux` is `tests/stubs/pystub.py` (records every call; makes a fake
venv on `-m venv`; the import check passes once `-m pip install` has written `VENV/installed`;
`PYSTUB_FAIL=venv|pip`). The stub speech model serves `narrate --lines` as it serves the script form (its clip length is 0.5 + 0.25 a
word, plus the trim). The stub ffmpeg also serves the scene scan of item 24 (`scenes=` in a fake media file) and ffprobe
the fake's `width=`/`height=`. The suite needs pycairo, numpy, soundfile, Pillow and fontTools from the venv (libraries, not
programs) and no external program, model, library or network: ffmpeg, ffprobe and the speech
model are stubs in `tests/stubs/` (the stub ffmpeg refuses an existing output without `-y` and
serves raw audio and raw frames from fake media), and **the video-elements library is the
invented one at `tests/stubs/video-elements/`** (a stub `videoelements` package reading the
settled `ELEMENT.md` rows; elements `pot` (svg, two states, fixed anchors, from "Invented
Icons") and `table` (code, `rows`, a `label`, indexed parameters, computed anchors, a size
noted `nominal`, `fit` `natural` with a `natural_size` of 120 a column by 30 a row recorded in
`lib.sizes`, an `explode` parameter that makes its draw and its `natural_size` refuse, from
"Invented Peeps"); its draw fills the rect with the brand's accent and records every call in
`lib.draws`, and passes every label parameter it is given through `frame.label`, as the real
elements do; its README says what it checks and what it does not). The warning's tests use a
copy of it with the table's `fit` row removed (`without_fit`). One test is skipped off macOS
(CoreText). **The whole suite takes about 3 min 15 s**, longer than a foreground command's
default two minutes: run it with a longer timeout or in the background.

How the tests work: `tests/tier1/` pure functions (`test_choreography_parse.py`, `_check.py`,
`_library.py`, `test_perform_curtain.py`, `test_credits.py`, `test_elements_*.py` for items 15
to 17); `tests/tier2/` runs each command as a subprocess through `conftest.run()` under the
venv's Python, with the `speech` and `ffstub` fixtures, `example` (a copy of `examples/`),
`narrated()` and `rendered()`; `test_frame.py` compares drawn frames with `tests/tier2/frames/`
at 192×108; `test_perform.py` and `test_end_card_credits.py` draw frames in-process on scene A
of the example described (`describe()`, `CAST`, `pointed()`, `three_cues()`) and sample pixels
or `lib.draws`; for arrows and callouts `recorded(monkeypatch)` replaces `draw.arrow` and
`Frame.callout` with recorders, so the points and keywords handed over are asserted exactly;
`test_check_script_choreography.py` and `test_assemble.py` run the commands with `--elements
tests/stubs/video-elements`. One tier: `.venv/bin/pytest tests/tier1`. Never `git add -A`
while a suite is running (coverage fragments).

Tier 3 done on this Mac, in the session's scratchpad, read-only on everything real: the whole
chain on the example (9–10 October); the described scenes against the **real** video-elements
library (`~/projects/code/video-elements`, at `65227bc`): the example's scene A with `person`,
`sun`, `gauge` and `calendar` (the README's run); the real second video's scene A2 against v4
(19:40); the credit lines and credits file against the real register (20:55); and for item 17
(the entry of 23:45): arrows with offsets, a growing arrow, a headless one and a badge on a
blank-Where arrow's centre on the example, by eye; `check-script`'s warning for a real `diff`
with no Size and none for a `spreadsheet` (since video-elements `5f98a74` `diff` offers its
natural size too, and the same run prints no warning: no real element gives it now); and the second video's scene B as the training-video
project described it, with every Size blank and the arrow with no Where, against v4 through
`compare-frames`: 1.8 to 4.3 mean difference at four moments, the same picture by eye.
For item 18 (00:02): the real `formula-bar` with `ref="" placeholder=yes` in that scene B's
Mistake panel: `check-script` clean where it was refused before, and the bar drawn with no
reference, no divider and its grey placeholder.
`~/.video-tools.conf` on this Mac names `SPEECH_MODEL_DIR` only; the Tier 3 runs passed
`--elements` on the command line.

Known limits worth knowing: a described scene is flat (no camera); a text piece's box for its
corners is approximate; a fixed anchor of an element not yet drawn assumes uniform, centred
fitting, which is not how a `stretch` element spreads its anchors (video-elements' note: over
the rectangle's width and height separately), so a member placed by a stretching element's
fixed anchor *before* that element in the cast may be a little off (after it, the drawn anchor
is used: put it after); a Size of `W` alone takes its height from the nominal proportions even
for a natural-sized element; an arrow with a Where keeps a point as its box; `check-script`
sees only a module's own top-level `def`s; the stored-image frame tests pin layout, not fonts;
`brand-preview`'s layout is checked by eye. Known-wrong in past entries: the `check-video`
entry says `180 passed` (it was 179); an early "21:30" was 18:30; commit `71293d0` went out
without its diary entry, which followed in `6dd4704`; the 23:10 handover named `08076e3` as the
last commit when the handover's own commit, `713f5f3`, followed it.

Also the other projects': the training-video project re-describing its scenes A2 and B in its
own script with these (blank Sizes, the arrow) and retiring modules; it is told through
Squirrel.

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

### 9 October 2026 — The ninth request arrives and is OK'd: four checking commands

**Decision / surprise.** `inbox/request-from-training-video-2026-10-09-9.md` (21:39–21:40,
training-video side, after Squirrel asked why their `brand-preview`, `compare-frames` and
`frame-hashes` scripts were not video-tools commands): four commands, `brand-preview`,
`frame-hashes`, `compare-frames` and `compare-video` (the last the acceptance comparison run by
hand at request 4 and never kept). Their three scripts read as the reference for behaviour.
Reported at 21:43 with the build order (`frame-hashes` first, no ffmpeg; then `compare-video`,
whose stub needs raw audio and raw frames; `compare-frames` reusing that; `brand-preview` last)
and three questions. Squirrel (21:44): `frame-hashes --compare` exits 1 when frames differ;
`compare-frames` uses the current `timing.json` plus `--offset`; contrast ratios always, and
"Describe all three when describing what you change"; then "go ahead!". PLAN.md item 11, the
commands list, the exit-code table, build step 10, "Settled" 20; the item moved to `inbox/done/`.

**State.** Next: `frame-hashes`, test-first.

### 9 October 2026 — Request 9, `frame-hashes`

**Goal.** Item 11's first command: every N-th frame of each scene drawn as `render` draws it,
its pixels' MD5 by scene and frame number; `--out` (refusing an existing file unless `--merge`,
which keeps the file's other scenes), `--compare` (per scene, the differing frames and those not
in the record; exit 1 if any differ), `--scenes`, `--step`, complete timings required, a missing
pycairo as one line, exit 4.

**Test.** `tests/tier1/test_frame_hashes_compare.py` (two: `compare` and `describe` on
hand-written dictionaries) and `tests/tier2/test_frame_hashes.py` (thirteen, on the example with
`--scenes` and `--step` to keep each under a second of drawing), plus one case in
`test_missing_packages.py`. The difference test changes the example copy's `water` colour, which
only scene R draws.

**Red.** With the wrapper and a module of `NotImplementedError` stubs: `16 failed, 10 deselected`,
every one `NotImplementedError` or `assert (1, '') == (4, '')` against it.

**Green.** `1 failed, 15 passed` after implementing: my expectation, not the code. I had written
that three of scene R's five hashed frames differ (`50, 100, 150`); frame 200 (6.7 s of 8.1 s) is
before the fade-out and shows the water too, so four differ. Frame 0 is the full fade and never
differs, as predicted. Corrected to `4 differ (frames 50, 100, 150, 200)`. Full suite:
```
TOTAL                         2222     23    756     28    98%
296 passed in 83.64s (0:01:23)
All checks passed!
```

**Tier 3.** On the scratch copy of the example (narrated, insets cut): the whole video hashed,
`Wrote …/hashes.json: 1802 frames, 7 scenes` (76,788 bytes); `--compare` unchanged, `All frames
match.`, exit 0; `water` changed in the scratch copy's script, `--compare --step 10`: every scene
`all match` but `R  27 frames: 26 differ (frames 10, 20, … 120, …)`, `26 frames differ.`, exit 1.
The README's section shows this run.

**Decision / surprise.** A frame the record does not have counts as differing (their script did
the same: `ref.get(n) != h`), and is counted separately in the line, so `--step` mismatches are
visible. Hashing runs at about 80–90 frames a second here against `render`'s 200: the MD5 of
eight megabytes a frame and a copy of the surface's bytes; not worth tuning for a check that
takes twenty seconds on a minute of video. The output format follows their script's (`key:8`,
`frames:5`, seconds to one decimal) so their comparison with the bed video can be by eye.

**State.** Green: 296 tests, 98%, lint clean. Next: `compare-video` (the stub ffmpeg gains raw
audio and raw frames).

### 9 October 2026 — Request 9, `compare-video`

**Goal.** Item 11's second command: two finished files compared on length, frames, levels, the
narration envelopes' correlation and speech/silence disagreements, and the frames every N
seconds (mean, median, five largest); `--sheet` with the five pairs; exit 0 always; ffmpeg's
failures exit 4; a missing numpy or Pillow one line, exit 4.

**Test.** First the real formats (PLAN.md "Things checked" 7): raw 48 kHz mono audio is the
file's length to the sample, a raw rgb24 frame is width × height × 3 bytes. Then
`tests/tier1/test_compare_video_measures.py` (five, on hand-written arrays: the envelope, the
correlation and its undefined case, the disagreements, the speech line, the summary with ties by
time) and `tests/tier2/test_compare_video.py` (thirteen) against the stub, which gained two
behaviours: `-f s16le` writes samples loud (−20 dBFS) in a fake file's `tone` spans and silent
elsewhere, and `-frames:v 1 … -f rawvideo … -` writes one frame of the colour the fake's
`colours` gives for that time. The expected numbers were worked by hand before the run: eleven
pairs with three at 151.7 and three at 161.7 give mean 85.5 and median 151.7; two envelopes
loud 0–10 and 20–30 s against 0–10 and 25–30 s give 50 disagreeing windows and Pearson 0.8069.
Two missing-package cases added.

**Red.** `20 failed, 11 deselected`: `NotImplementedError` (tier 1) and exit 1 with the
traceback against every expectation (tier 2).

**Green.** Four rounds, none a fault in the command's logic. (1) The stub dispatched `-f rawvideo`
to its render branch before looking for `-frames:v`, so a frame request read an empty stdin and
wrote a fake file named `-` into the repository (deleted; the branch now excludes `-frames:v`).
(2) My "different lengths" fixture was loud for the whole 20 s compared, so both envelopes were
flat and `undefined` was the right answer; the fixture now varies within the 20 s. (3) The
strip probe at x=100 landed on a letter of the label (248, not 85); moved to x=600. (4) The
`is_speech` test's threshold value was exactly the −40 dBFS line, 327.68, where float rounding
decides; the test uses 328 and 327. `20 passed`; the suite:
```
TOTAL                          2337     24    780     29    98%
316 passed in 106.19s (0:01:46)
```
Lint: one line over 120 columns, wrapped; `All checks passed!`

**Tier 3.** The scratch example video against the copy `assemble --replace --out` made earlier:
identical in every measure (`correlation 1.0000`, `0 windows`, every difference 0.0). Then
scene R re-rendered in a second scratch copy with `water` red and assembled to `red.mp4`;
`compare-video red.mp4 new.mp4 --every 2 --sheet`: the levels and envelopes identical, `mean
difference 3.0, median 0.0`, the five largest 18.9 at 46, 48, 50, 52 s and 18.4 at 54 s, all in
scene R; the sheet looked at: five rows, new left with the red water, old right with the blue,
labels in the strips. The README's section shows this run.

**Decision / surprise.** The sheet is 1920 wide by five rows of 570 (two 949×533 frames and a
36 px strip), not 1920×1080, since five pairs need the height; its label font is Pillow's
default (the command has no brand kit to take one from). `ffmpeg.run` takes `binary=True` for
raw output; `audio_samples` and `frame_at` beside it will serve `compare-frames` too. The
`frames` count comes from ffprobe's `nb_frames`, falling back to a decode count when a file
has none.

**State.** Green: 316 tests, 98%, lint clean. Next: `compare-frames`.

### 9 October 2026 — Request 9, `compare-frames`

**Goal.** Item 11's third command: the frame drawn now beside the old video's frame at the
scene's start (from the current `timing.json`, plus `--offset`) plus the time; one pair a row,
labelled under each frame with the mean absolute RGB difference, printed too; refusals for a
time past the scene (exit 2, as `stills`), a moment past the old video (exit 3, by name, before
any frame is read), an existing sheet, a missing old video, missing timings; missing packages
one line, exit 4.

**Test.** `tests/tier2/test_compare_frames.py`, eleven tests on the example against stub media
of one colour (the `colours` field the previous entry added), and three missing-package cases.
The old video's moments were worked by hand from the example's scene lengths (title 8.3 s, A 8.7,
B 7.9, B2 5.3): `A:1.5` is 9.8 s, `B2:-1` is 29.2 s, `--offset B2=1.5` makes it 30.7 and
`--offset A=-0.3` makes 9.5.

**Red.** `11 failed` in the file and the three package cases: `NotImplementedError`.

**Green.** `3 failed, 11 passed` after implementing, all three my tests: argparse wraps the usage
line (compared with whitespace collapsed, as `render`'s test does); the difference lambda was
handed the file path instead of the command's output; and I miscounted the padding of the
printed line (`{key:8} {t:7.2f}` puts ten spaces after `B2`). Then one more mine: I had guessed
a near-background colour would differ from frame A by under 20, and it is 32.7 (the header,
inset and text are ink on the background); the bound is now 100, which is what the test is
for (black against the frame differs far more than a near-background colour). `11 passed`;
the suite:
```
TOTAL                           2421     25    798     30    98%
330 passed in 119.58s (0:01:59)
All checks passed!
```

**Tier 3.** The scratch example's script against its own finished video, five pairs across
title, A, R and end: differences 0.8–1.0 (H.264's loss); against `red.mp4` (scene R with red
water): A 0.8, R 19.5 and 19.4; the sheet looked at: the red water left, blue right, the
labels under each frame in the brand's display font. The README's section shows that run.

**Decision / surprise.** A wrong turn found by `git status`: the `compare-video` commit
(`65a20b5`) swept in 215 `.coverage.<host>.<pid>.*` fragments that a parallel suite run had
left on disk at the moment of `git add -A` (coverage.py's `parallel = true` writes one per
subprocess and combines them at the end of the run). They are deleted from git in this commit
(never rewriting the pushed one), and `.gitignore` now has `.coverage.*`. Lesson: never
`git add -A` while a suite is running; look at `git status` first. The `--offset` parser
checks the scene exists (usage error naming the scenes) so a typo cannot silently do nothing.

**State.** Green: 330 tests, 98%, lint clean. Next: `brand-preview`, the last of the four.

### 9 October 2026 — Request 9, `brand-preview`; request 9 complete

**Goal.** Item 11's last command: the kit through `brand.read`, drawn with `videotools.draw` in
its own fonts: swatches, a specimen per named font role, the mark via `frame.mark`, pills, the
rule-3 pair, settings, the illustration and credit, the caption band, and the WCAG contrast
ratios of the chrome's thirteen text-on-fill pairs, printed too; a bad kit refused in the
reader's words, an existing output refused, a missing pycairo one line.

**Test.** `tests/tier1/test_contrast.py` (three: black on white 21, a colour on itself 1, the
WCAG example `#767676` on white 4.54 either way round, the verdicts at 4.5 and 3) and
`tests/tier2/test_brand_preview.py` (eight) on a copy of the example kit, plus a missing-package
case. The thirteen ratios of the example kit, and those of a `muted` and `correct` changed to
fail, were worked by hand outside the package before the run (two of my first guesses for the
changed colours were wrong, 2.6 and 3.5 for 2.13 and 3.43; corrected before implementing).

**Red.** `12 failed`: `NotImplementedError` from both stub modules.

**Green.** `1 failed, 11 passed` after implementing: the missing-package case, because the
module imported `videotools.draw` (and so cairo) at the top, ahead of `cli.need`; moved to the
point of use. `12 passed`. Lint: a `%` format and a long line, fixed. The suite:
```
TOTAL                           2569     26    826     33    98%
342 passed in 125.65s (0:02:05)
All checks passed!
```

**Tier 3.** The example kit's preview looked at; a second run refused (exit 3). Then the real kit
(`training-video/brands/douglassquirrel`, read-only, the preview into the scratchpad): reads,
12 colours, 7 fonts; its ratios by role: three pairs are `large text only (3-4.5)` (accent on
background 3.63, accent on surface 4.11, on-accent on accent 4.11; the rest 4.96–12.63), which
is what rule 3 and `small-text-accent` are for, since accent text is 24 px and up. **Looking at
the real kit's preview found two layout faults the example's three fonts had hidden:** with
seven specimen lines the pills and the rule-3 line ran into the illustration, and thirteen
contrast rows at 26 px ran into the caption band. The specimen pitch is now `size + 16`, the
contrast list is two columns of up to seven rows, and the illustration is fitted to a 540×150
box anchored above the band. Both previews looked at again: clean. No test pins that layout
(as none pins the chrome's beyond the stored images); the README's section shows the run.

**Decision / surprise.** The preview is drawn by cairo and written by cairo, so Pillow is not
needed (PLAN.md item 11 corrected). `frame.mark` takes a tiny namespace with `brand` and
`scale`, so the roundel and wordmark are the chrome's own drawing, not a second copy. The
contrast pairs are fixed in `brand_preview.PAIRS` plus the caption band; a kit's `caption-band`
role names the last pair.

**State.** Request 9 complete: four commands, 342 tests, 98%, lint clean, README and PLAN.md
current. Nothing waiting.

### 10 October 2026 — The tenth request arrives and is OK'd: characters a font lacks

**Decision / surprise.** `inbox/request-from-training-video-2026-10-10.md` (07:42,
training-video side, after their second video, made at `c782a56`, showed five labels ending in ✓
as empty boxes: EB Garamond has no ✓ or ✗ glyph and cairo's simple text API draws the font's
missing-glyph box, silently). Two asks: ✓ and ✗ drawn as strokes wherever a font lacks them, and
a `check-script` report for any other character a font lacks. Checked here before reporting
(07:44–07:48): the example's fixture fonts lack ✓ and ✗ too (and have `·`, `—`, `…`, `é`), and
cairo gives the same width (27.4 at 30 px) for ✓, ✗ and U+FFFD, so measuring the box cannot
tell them apart; the font's `cmap` can. Reported at 07:48 with the plan: a standard-library
`cmap` reader shared by the drawing and by `check-script` (which stays on Python 3.9), the marks
drawn in `draw.text` so every text path gets them, and one question: which font to check On
screen labels against, since the script does not say the role scene code will draw them in.
Squirrel (07:49) asked what a role is (answered: the kit's name for a font's job, `display`,
`body`, `italic` and the optional ones, which the chrome and scene code ask for instead of a
font); (07:50): "display font only. go ahead". PLAN.md item 12, build step 11, "Settled" 21;
the item moved to `inbox/done/`.

**State.** Next: `videotools.glyphs`, test-first.

### 10 October 2026 — Request 10, item 1: the character-map reader, and ✓ and ✗ drawn as strokes

**Goal.** `videotools.glyphs` (standard library): a font file's `cmap` (formats 4 and 12) as
a set of code points, cached; `register(family, file)` and `has(family, ch)`, an unregistered
family assumed to have everything. `fonts.load` registers the kit's families. In `draw.text`
and `draw.text_width`, a ✓ or ✗ the family lacks is drawn as a tick or cross stroke in the
text's colour and alpha, 0.8 × size wide, anywhere in the string, counted in the width, so pills,
centring, tracking and wrapping follow.

**Test.** `tests/tier1/test_glyphs.py` (three: the fixture font has `Aé—…·“”` and lacks `✓✗€Ω`,
200 code points; a file that is not a font is a useful Failure; the registry), 
`tests/tier2/test_glyphs_against_fonttools.py` (two: the reader equals fontTools' `getBestCmap`
on every fixture font; a tiny invented font with a format 12 table and glyphs for ✓, ✗ and
U+1F600 reads back exactly), `tests/tier1/test_draw_marks.py` (five: widths, strokes and no box
past the advance, anchor and alpha, a font that has the glyph is left alone, pills and wrap),
`test_fonts.py` (loading a kit registers each family) and `test_frame_methods.py` (a label
ending in ✓ through `frame.tag` is a wider pill with the tick in the label colour).

**Red.** Reader: `5 failed`, `NotImplementedError`. Drawing: `5 failed`: widths short by the
fallback glyph (`94.09 == 99.07`), `(255, 255, 255) == (0, 0, 0)` where the stroke should be,
`has('PBS Regular', '✓')` True because nothing registered. Two of the seven passed before the
implementation (the anchored-and-alpha pixel test, because the fallback font's own ✓ happens to
land on those pixels; and the font-has-the-glyph test, which cannot fail before). After the
green, `_mark` was made to return at once: `3 failed, 10 passed`, the anchored test among them,
so it does detect a missing stroke; restored.

**Green.** `34 passed` for the five tier 1 files; the suite `354 passed`, 98%; lint one long
line, wrapped, then clean.

**Tier 3.** The scratch example with "edge fold ✓" and "diagonal fold ✗" in scene A's On
screen list and its scene code: `check-script` clean; `stills A:5`: both pills show the mark,
stroked in the label colour, the pills wider by the mark; looked at.

**Decision / surprise.** The mark's geometry is in size units (tick through (0.08, −0.30),
(0.32, −0.06), (0.72, −0.60); cross between 0.12–0.68 and −0.62 to −0.06; stroke 0.11, at
least 1.5 px) rather than scaled from `draw.badge`, so a mark sits on the baseline like a
glyph. `line()` changes the context's source and line width, so `text` re-selects the font
after each mark. The reader keeps a code point only when it maps to a non-zero glyph, as
fontTools does, which is why the two agree exactly. A `.ttc` collection reads its first font.

**State.** Item 1 done. Next: item 2, `check-script` reports characters a font lacks.

### 10 October 2026 — Request 10, item 2: `check-script` reports characters a font lacks; request 10 complete

**Goal.** For every text the chrome draws, against the resolved file of the role it is drawn in
(On screen labels against the display font only: "Settled" 21), one problem per text naming the
line, the text, the first lacking character with its code point and the file; ✓ and ✗ excepted;
the kit's website and credit too; listed after the kit's problems, exit 1.

**Test.** `tests/tier1/test_font_check.py`, six tests on the two-scene fixture script and the
example kit (which lacks € and Ω): nothing in the plain fixture; a caption with € names line 47,
the text, `'€' (U+20AC)` and `PBS-Regular.ttf`; ✓ and ✗ never reported; one problem each for a
subtitle (italic), a scene title (display), a side-panel item (body) and an On screen label
(display), with their lines; two lacking characters in one text reported once with the first;
a kit's website with € reported with the BRAND.md path. `tests/tier2/test_check_script.py`: the
example copy with € in a caption, exit 1, the one problem with its line.

**Red.** `6 failed` with `NotImplementedError`; the tier 2 test failed first in its own set-up
(I had guessed the caption's words; the example's cue reads "Step A. Fold the sheet…"),
corrected, then the right failure.

**Green.** `1 failed, 18 passed`: my line count again (the inserted subtitle row moves the On
screen label to line 61, which I had left at 60; the other three shifted lines I had counted).
Corrected, `6 passed`; the suite:
```
TOTAL                           2727     32    906     41    98%
361 passed in 113.79s (0:01:53)
All checks passed!
```

**Tier 3.** The scratch example with € in scene A's first caption: `1 problem: line 98: scene A
cue 1 caption '…' has '€' (U+20AC), which …/PBS-Regular.ttf lacks`. The two real scripts
(`make-bed`, `app-for-that`, read-only): no problems, exit 0; their five labels ending in ✓ are
excepted, as item 1 draws them.

**Decision / surprise.** `brand_problems` now returns the kit it read, so the kit is read once
per run; a font file that is not a font is one problem line, not a crash (`glyphs.characters`'s
Failure caught). The roles are a table in `check_script` (`SETTING_ROLES`, `SCENE_ROLES`,
`KIT_ROLES`, captions `body-medium`, panels `body`, labels `display`); a fallback role resolves
through `brand.FONT_FALLBACKS`. The `--json` output is unchanged.

**State.** Request 10 complete: 361 tests, 98%, lint clean, README and PLAN.md current. Nothing
waiting.

### 10 October 2026 — The eleventh request arrives and is OK'd: phonemes in `say:` lines

**Decision / surprise.** `inbox/request-from-training-video-2026-10-10-11.md` (08:29,
training-video side, after Squirrel heard six wrongly stressed words in the second video):
`[[…]]` spans of phonemes in a `say:` line, a `check-script` report for bad spans, and a way to
see the phoneme string each cue gets. Checked in the installed kokoro-onnx 0.6.1 before
reporting (08:40–08:44): `create` takes `is_phonemes=True` and then uses the text as phonemes
with whitespace collapsed; the tokenizer drops any symbol outside `config.json`'s `vocab` (114
symbols, the space among them) silently; `tokenizer.phonemize(text, lang)` is public. Reported
at 08:45 with the plan and one question (a flag on `narrate --dry-run`, or a new command).
Squirrel (08:46): his standing OK on their side is for them to request changes, not for them
to be done here without his OK; "Right to verify. OK to put flag on narrate." Taken as the
go-ahead with the flag on `narrate`. PLAN.md item 13, build step 12, "Settled" 22; the item
moved to `inbox/done/`.

**State.** Next: `videotools.phonemes`, test-first.

### 10 October 2026 — Request 11: phoneme spans in `say:` lines; request 11 complete

**Goal.** Item 13: `videotools.phonemes` (`parts`, `has_span`, `problems`, `splice`, `VOCAB`);
`narrate` sending a cue with a span as phonemes spliced from the model's own phonemizer, a cue
without one exactly as before; `check-script` reporting bad spans and a span in a caption, each
by the `say:` line; `--phonemes` on the dry run.

**Test.** `tests/tier1/test_phonemes.py` (five), `tests/tier2/test_phonemes_vocab.py` (the fixed
vocabulary equals the installed package's), four in `tests/tier2/test_narrate.py` against the
stub, which gained a `tokenizer` submodule whose `phonemize` upper-cases and strips (so a splice
is visible) and an `is_phonemes` field in its record, `tests/tier1/test_phoneme_check.py`
(three), one in `tests/tier2/test_check_script.py`, and one in `test_script_reads.py` for the
parser recording each cue sub-bullet's line (`data["lines"][(key, "cue 2 say")]`), which the
report needs.

**Red.** Phonemes: `6 failed`, `NotImplementedError`. Narrate: `5 failed`: `unrecognized
arguments: --phonemes`, the create call without the splice. Check: `3 failed` and `(0, '') ==
(1, '')`. Parser: `KeyError: ('A', 'cue 2 say')`.

**Green.** Three faults of mine on the way, none in the request's logic. (1) The first splice
test let the phonemizer keep whitespace; the model's strips it, so a span would have been glued
to its neighbours. The test was sharpened to a stripping phonemizer (`'SAYkɑːɹpˈæθiHERE' ==
'SAY kɑːɹpˈæθi HERE'`), and `splice` keeps each text part's own leading and trailing spaces.
(2) `import kokoro_onnx` does not bind its `tokenizer` submodule (the real package happens to,
the stub did not): imported by name. (3) The dry run printed two lines before finding the
package missing with `--phonemes`; the package is now needed before anything is printed. One
wrong guess of mine at the example's first cue text, corrected from a real dry run. Lint: the
114-symbol literal is split across lines without breaking an escape, and one long line wrapped.
The suite:
```
TOTAL                           2809     32    942     41    98%
376 passed in 120.15s (0:02:00)
All checks passed!
```

**Tier 3.** On the scratch example, with the real model: (1) the eleven clips from last night
kept, `narrate --replace` run again on the unchanged script: every clip and `timing.json`
byte-identical (`cmp`), the proof the request asked for. (2) `--dry-run --phonemes` prints
espeak's phonemes for each cue (the README shows the title scene). (3) A span `[[fˈɪɡjɚ]]` for
"Figure" gave a clip byte-identical to the text-only one, because espeak already gives exactly
those phonemes, which proves the splice is character-exact; a span `[[fˈɪɡɚ]]` (one phoneme
dropped) gave a clip 2,404 bytes shorter and different; the text restored, the clip was
byte-identical to last night's again. (4) An unclosed span in the scratch script:
`check-script` lists `line 67: scene title cue 2 say: '[[' at character 19 is never closed with
']]'`, exit 1.

**Decision / surprise.** The vocabulary is copied as escaped code points from the installed
package's `config.json`, so no combining character is mangled in transcription, and the tier 2
test will fail when an upgrade changes it. The model collapses whitespace itself, so the splice
only has to keep the spaces as written. Kokoro's own vocabulary has no `$` pad symbol in this
package's `config.json`: 114 symbols, the space among them.

**State.** Request 11 complete: 376 tests, 98%, lint clean, README and PLAN.md current. Nothing
waiting.

### 10 October 2026 — The twelfth request arrives and is OK'd: the curtain, and stills at cue changes

**Decision / surprise.** `inbox/request-from-training-video-2026-10-10-12.md` (08:53,
training-video side, after a glimpse of an old picture through the lifting mistake panel in
their second video): a way for scene code to know when the panel covers the area, and a way to
see every cue change with a warning for the glimpse. Checked the panel's formula in
`frame.mistake_panels` before reporting (08:57); noted that the curtain is the background at
0.96, not opaque, and that it stays to the scene's end when the mistake cue is last. Reported at
08:58 with the plan and two questions. Squirrel (09:00): "flag on stills, warning on by default.
go ahead". PLAN.md item 14, build step 13, "Settled" 23; the item moved to `inbox/done/`.

**State.** Next: the curtain functions on the timeline, test-first.

### 10 October 2026 — Request 12, item 1: the curtain on the timeline

**Goal.** `Timeline.curtain(t)` (the mistake panels' strength, the formula moved from
`frame.mistake_panels`), `covered(t)`, `before_curtain(t)` (1.0, then a fade 0.5–0.7 s after
the mistake cue's start, inside the covered time), `mistake` (the cue number or None); the
panels drawn from `curtain`, so there is one place for the timing.

**Test.** Three in `tests/tier1/test_timeline.py` on a three-cue scene with 1 s clips (starts
0.7, 2.25, 3.8): the curtain 0 at the mistake cue's start, 1 at +0.5 and at the next start
−0.4, between at −0.15, 0 at +0.1; `covered` true only at full strength; `before_curtain` 1 at
+0.5, 0.5 at +0.6 while covered, 0 at +0.7; no mistake: never covered, 1.0 always; the mistake
cue last: covered to the scene's end.

**Red.** `3 failed`: `'Timeline' object has no attribute 'curtain'` (and `covered`).

**Green.** `42 passed` for the timeline, frame and frame-method files: the eight stored frames
are unchanged with the panels drawn from `tl.curtain(t)`, which is the proof the formula moved
without changing.

**State.** Item 1 done. Next: `draw_frame(..., curtain=False)`, then `stills --cue-changes`.

### 10 October 2026 — Request 12, item 2: `stills --cue-changes` and the curtain warning; request 12 complete

**Goal.** `draw_frame(..., curtain=False)`; `stills --cue-changes [--scenes]`: the frames at
−0.3, 0, +0.3 s around every cue start and +0.6 s for the cue after a mistake, on numbered
sheets when they outnumber the grid, each refused if it exists; and the warning: the area drawn
without the panels at the lift's start and end, pixels drawn then and background after counted,
more than 0.2 % of the area a warning naming the scene and cues, exit 0.

**Test.** `test_frame.py`: a frame at the mistake cue without the curtain has no MISTAKE header
where the one with it does, and the same header above. `test_stills.py` (six): B2's one cue
gives three frames on the one sheet as named; a copy whose scene A has a third cue after the
mistake (its module replaced by a tiny one, timings written for three 1 s clips: starts 0.7,
3.7, 7.7) gives ten frames at the predicted times on `sheet-1/2/3.png`; `--cue-changes` with
SCENE:SECONDS, and neither, are usage errors; a numbered sheet that exists is refused before
anything is drawn; the faulty module (the rectangle goes at cue 3's start) warns naming scene A
and cues 2 and 3 with a pixel count; the same module on `before_curtain` does not.

**Red.** `7 failed`: `unrecognized arguments: --cue-changes` and `draw_frame() got an unexpected
keyword argument 'curtain'`.

**Green.** `2 failed, 40 passed` after implementing, both my expectations: the old help test's
usage line (new flags, and argparse wraps it), and I had put the three `Wrote` lines last when
each sheet prints its own after its frames, which is the better order. Corrected; `15 passed`;
the suite:
```
TOTAL                           2888     31    976     41    98%
386 passed in 120.81s (0:02:00)
All checks passed!
```

**Tier 3.** The scratch example, every scene: 33 frames on three 4×3 sheets, the first looked
at (the title's two cues and scene A's, the mistake panels rising at 4.53 and 4.83 s); no
warning, since the example's mistake cue is the last in its scene. A second scratch copy with a
third cue after scene A's mistake and a module that keeps a 500×400 rectangle until cue 3's
start: `stills: scene A: something drawn under the panel at cue 2 vanishes as it lifts for cue
3 (199932 pixels); fade it out while covered: frame.timeline.before_curtain`, exit 0, the
sheets written; the same module on `tl.before_curtain(t)`: no warning. The README shows that
line.

**Decision / surprise.** The warning compares the scene code's own drawing, not the frame as
seen: with the panels at full strength nothing behind them is visible, so the two looks are
drawn with `curtain=False`. "Background" is the scene's background surface (grid included)
within 8 of 255 per channel, so anti-aliased edges do not count. The first cue's −0.3 s frame
falls in the lead; a time clipped to the scene is kept once. `--scenes` applies only with
`--cue-changes`. The README says what the check cannot see.

**State.** Request 12 complete: 386 tests, 98%, lint clean, README and PLAN.md current. Nothing
waiting.

### 10 October 2026 — Session end and handover

**Decision / surprise.** The session's record, for whoever picks this up: it began 9 October at
21:25 with the inbox empty, checked `assemble --replace` against the real ffmpeg, then built
requests 9 (four checking commands), 10 (✓ and ✗ drawn where a font lacks them; the font check),
11 (phoneme spans) and 12 (the curtain; stills at cue changes), fourteen commits after
`6b07320`, each green on the full suite with lint clean and pushed to `origin/main`; every
behaviour through a test seen red first, the exceptions named in their entries. Wrong turns,
all recorded: 215 coverage fragments swept into one commit (removed in the next; `.coverage.*`
ignored); several of my own test expectations wrong before the green (line numbers, a guessed
caption, a guessed pixel count in a README draft, replaced by the real run). Squirrel's
standing OK on the training-video side lets that project send requests; each one was OK'd here
before anything was done ("Settled" 22). Scratch copies of the example live only in the
session's scratchpad. "Where things stand" above is the handover.

**State.** Green: 386 tests, 98%, lint clean, pushed at `124413e` plus this entry. Inbox empty.
Nothing waiting on Squirrel.

### 10 October 2026 — Requests 13 and 14 arrive at the handover

**Decision / surprise.** The previous entry's "Inbox empty" was true at 09:07 and wrong by the
time it was committed at 10:22: `inbox/request-from-training-video-2026-10-10-13.md` (10:09)
and `…-14.md` (10:20) had arrived. 13: choreography (a cast and moves by cue) described in a
scene's section of the script and drawn by video-tools from a new, separate repository
`~/projects/code/video-elements/` (a library of drawn elements, its own request sent there), with
a config setting for the library's folder, `check-script` checks on the choreography, the
curtain applied automatically to pre-mistake elements, and a proposed Python interface between
the two repositories (`library.open`, `lib.element(name).draw(frame, rect, state, params,
alpha)` returning anchors). 14: the elements' sources credited on the end card (`element-credits`
setting: `auto`, `none`, or wording), printed by `check-script` for approval, and a
`<output>.credits.txt` written by `assemble`. Both read and reported to Squirrel at 10:23 with a
first comment; **nothing done**: no PLAN.md change, no code. "Where things stand" corrected in
this commit. Observations for the next session: 13 is the biggest change since the first
request (a script format for choreography, a reader, an interpreter in the frame, and a
dependency on a repository that does not yet have its reader), and its order of work depends
on video-elements; the interface text must stay the same in both READMEs, through Squirrel.

**State.** Green and pushed as before. Waiting on Squirrel for 13 and 14.

### 10 October 2026 — Requests 13 and 14 OK'd and recorded; the choreography format proposed

**Goal.** Record both requests in PLAN.md (items 15 and 16, "Settled" 24 and 25), move them to
`inbox/done/`, and write the choreography format with a worked example for Squirrel's approval.
No code (Squirrel, 10:36: "go ahead and do the format and get my approval on that").

**Decision / surprise.** Squirrel settled the three details put to him at 10:36: the interface is
video-elements' settled text (with the `renderer` argument and `lib.credits`), the config keys
are `VIDEO_ELEMENTS_DIR` and an optional `RSVG_CONVERT`, each also a flag, and the folder
setting is the repository root, put on the import path at the point of use. The format's shape,
decided while re-describing scene A2 from its module (read, not copied): the request's "label
… at", "arrow from … to" and "hand at" are not verbs but cast members of video-tools' own
pieces (`pill`, `callout`, `text`, `badge`, `hand`, `arrow`), so the moves reduce to four kinds
(show/hide, move, a parameter, a state) and a label is shown, hidden and moved like anything
else; a member may be placed by another's anchor with an offset, so ticks and hands follow a
row; data is a named parameter (`rows=assets/x.csv`) read by video-tools, so the library never
reads a video's folder (an interface point for video-elements, "Open questions" 2). Where is in
area pixels as the request asked (the area is 1422 × 818 at 40, 118), panels in panel pixels.
Two things the example showed: the starter set lacks an element the panel needs (a
`formula-bar`), and the module spreads its working lines over the cue's measured length, which
the format writes as fixed offsets; whether that matters is for the `compare-frames` check. The
mistake cue's curtain needs no line at all in the example. PLAN.md's "Settled" list is out of
order after 19 (23, 22, 21, 20) from earlier insertions; 24 and 25 are appended at the end,
not re-ordered. A shell slip: `git mv -k` on the gitignored request 13 silently did nothing, so
the file sat in `inbox/` for a few minutes before a plain `mv`; nothing else was affected.

**State.** PLAN.md items 15 and 16 written; inbox empty; no code, suite untouched (386 green at
the last run). Waiting on Squirrel's approval of the format.

### 10 October 2026 — video-elements' request: `library.open` takes the root folder

**Goal.** Read and report the item that arrived at 12:59 (`inbox/request-from-video-elements-2026-10-10.md`),
then on Squirrel's OK (13:02: "Let's do that") record it and stop.

**Decision / surprise.** video-elements' step 3 reads the whole library at once, the sources
register under `licenses/` included, so `open` needs the repository root, which is the folder
`VIDEO_ELEMENTS_DIR` already names: the command passes it straight through instead of joining
`elements/`. One comment line of the shared interface changes; confirmed in its repository
(commit `8e946a7`, `library.open`, `names`, `element`, `credits` present; `draw` not yet).
Recorded in PLAN.md item 15 (the sentence and the interface block), "Settled" 26, and "Open
questions" 2 narrowed: the request answers what the description exposes (plain data with
`anchors`, `states`, `params` {type, min, max, default}, and `Failure.problems` for errors);
still to go to video-elements through Squirrel: data as named parameters read by video-tools,
which parameters are labels, and indexed parameter names. Item moved to `inbox/done/`.

**State.** No code; suite untouched (386 green at the last run). Waiting on Squirrel's approval
of the choreography format ("Open questions" 1).

### 10 October 2026 — The request to video-elements, sent through its inbox

**Goal.** Put "Open questions" 2 to video-elements as a request file in its inbox (Squirrel,
13:04: "make the requests to video-elements through its inbox"), the one write into that
repository he has authorised; nothing else there is touched.

**Decision / surprise.** Written at 13:05 as
`~/projects/code/video-elements/inbox/request-from-video-tools-2026-10-10.md`, four points:
data as a named `rows` or `text` parameter read by video-tools; a mark for `text` parameters that
are labels; a pattern form (`highlight.*`, `cell.*.*`) for indexed parameters and computed
anchors, passed with dotted keys; and the parameter names item 15's example guesses for the
`spreadsheet`. Its "Report" step asks for the answer as a file in our inbox in the words its
README will carry. Reading its PLAN.md "The element files" showed its `## Parameters` types are
`number`, `integer`, `colour`, `boolean`, `text` and its anchors fixed `X Y`, so a data-driven
element's per-row anchors need a form it does not have yet: that is point 3.

**State.** No code; suite untouched. Waiting on Squirrel's approval of the format, and on
video-elements' answer.

### 10 October 2026 — The format approved; video-elements' reply recorded

**Goal.** Record Squirrel's approval of the choreography format (13:24: "choreography format is
fine") and video-elements' reply of 13:18 to our request, move the reply to `inbox/done/`, and
say what comes next.

**Decision / surprise.** The reply accepted all three asks in the shapes we suggested, built and
tested on its side (its commit `4dd19c8`; checked read-only: `PARAM_TYPES` has `label` and
`rows`, the `computed` anchor value and the whole-segment `*` rule are in its element module).
Recorded in PLAN.md item 15 "The cast" (the description's rows as it reads them), the Labels
paragraph (type `label`), the Checks (an index of 0 or past the data), "Settled" 27; "Open
questions" 1 and 2 are closed, the credits-file default is now "Open questions" 1. One rule
worth remembering from the reply: indices count **from 1**, and an index past the data is the
element's refusal at draw time, so `check-script`'s own index check covers only data video-tools
read itself (a CSV in the cast row).

**State.** No code; suite untouched (386 green at the last run). Next: item 15's "Order of
work", first increment: `VIDEO_ELEMENTS_DIR` / `RSVG_CONVERT` in `config.read` and `--elements` /
`--renderer` on the drawing commands and `check-script`, test-first.

### 10 October 2026 — Item 15, increment 1: the config settings and the flags

**Goal.** `VIDEO_ELEMENTS_DIR` and `RSVG_CONVERT` read from the config file, and `--elements DIR`
and `--renderer PATH` on the five commands, resolved flag-first (Squirrel, 13:32: "go ahead with
the config settings"). Baseline first: the full suite, `386 passed in 121.82s`, coverage 98%.

**Test.** `test_the_elements_folder_and_the_renderer_are_read_the_folder_expanding_tilde`
(tier 1, `test_config.py`): a file with the two keys reads back as both, `~` expanded in the
folder. Then `tests/tier1/test_elements_settings.py` (four tests: the flags win; the config fills
what a flag leaves out; neither is `(None, None)`; `~` in the flag means home) and
`tests/tier2/test_elements_flags.py` (`--help` of each of the five commands names both flags and
both settings).

**Red.**
```
E           videotools.config.ConfigError: …/c.conf: line 1: unknown setting 'VIDEO_ELEMENTS_DIR' (the settings are SPEECH_MODEL_DIR, VOICE, SPEED)
1 failed, 4 passed in 0.04s
```
the right failure: the reader refuses the key. The resolver's tests failed on
`ImportError: cannot import name 'elements' from 'videotools'` (a new module: the behaviour
missing is the module), and the help tests on `assert ('--elements DIR' in "usage: check-script
[-h] [--json OUT] SCRIPT…")` for all five, `5 failed in 0.63s`.

**Green.** `config.KEYS` gains the two keys (the `_DIR` suffix already expands `~`);
`videotools/elements.py` (standard library, 3.9) with `add_arguments(p)` and `settings(args,
conf)`; the five parsers call `add_arguments` last. `14 passed in 0.57s` for the new tests and
the config file; the full suite `396 passed in 121.63s (0:02:01)`, `TOTAL … 98%`,
`ruff check .` clean.

**Decision / surprise.** Two predicted test changes, made before the runs: the unknown-key
message's settings list grows (`test_an_unknown_key_…` now expects the five names), and the
five `--help` usage-line assertions gain `[--elements DIR] [--renderer PATH]` before `SCRIPT`.
The flags are accepted and resolved but nothing opens the library yet; the README's
configuration section and "Notes for users" say so plainly, and `video-tools.conf.example` has
the two keys commented out. `elements.settings` expands `~` in the flag too, so a quoted
`--elements "~/x"` behaves like the config file.

**State.** 396 green, 98%, lint clean. Next: increment 2, the import and `library.open` with
the refusals, against an invented library.

### 10 October 2026 — Item 15, increment 2: the library imported from the configured root and opened

**Goal.** `elements.open_library(folder, renderer)`: the root on the import path at the point
of use, `videoelements.library.open(folder, renderer=…)`, every refusal one line in words
(Squirrel, 13:55: "go ahead with increment 2").

**Test.** `tests/tier1/test_elements_open.py`, eight tests: no setting and no flag refused
naming both and the config path; a missing folder refused by path; a folder without
`videoelements/` refused saying what the setting names; a package that raises on import refused
with its error; a library that refuses (the stub package copied into a root with no `elements/`
or register) reported with its problems listed; the invented library opens with `pot` and
`table`, the renderer given, the settled description rows (`highlight.*` as a number 0–1,
`row.*` computed, `rim` at (12, 4)) and one credit line; no renderer leaves the library's
default `rsvg-convert`; the root is on `sys.path` once however often it is opened. A
`fresh_import` fixture drops `videoelements*` from `sys.modules` and restores `sys.path`.

**Red.**
```
E           AttributeError: module 'videotools.elements' has no attribute 'open_library'
8 failed in 0.06s
```

**Green.** After the implementation, three still failed on the stub's own bug (`TypeError:
open() got an unexpected keyword argument 'encoding'`: the stub's module-level `open`, named as
the interface names it, shadowed the builtin inside its readers; fixed with `builtins.open`),
then `12 passed in 0.03s` with the settings tests; lint found an import block to sort and a
line of 122 characters, both fixed; the full suite `404 passed in 121.88s (0:02:01)`,
`TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** The invented library lives at `tests/stubs/video-elements/` with the
real repository's shape (`videoelements/`, `elements/`, `licenses/`), so the same root works for
`--elements` in tier 2 later and for the import path now. Its stub package reads the
`ELEMENT.md` rows video-elements settled rather than a private JSON, so the fixture files are
in the format Squirrel will read in the real library and the stub's `element(name)` exposes
the same keys (`name`, `kind`, `size`, `anchors`, `states`, `params`, `colours`,
`provenance`, `folder`); it checks little, by design, and its README says so. The import stays
on `sys.path` after `open_library` returns, since the package imports its own modules at the
point of use. The real library's `Failure` is caught by its `.problems` attribute, not by
class, so video-tools never imports from `videoelements` directly; any other exception from
`open` is reported as it is, under the same one line.

**State.** 404 green, 98%, lint clean, pushed. Nothing calls `open_library` yet. Next:
increment 3, the Cast and Moves parser with `check-script`'s checks.

### 10 October 2026 — Item 15, increment 3: the Cast and Moves parser

**Goal.** The four choreography sections read into plain data by `script.parse`, every
malformed line a problem naming it (Squirrel, 14:20: "continue with increments 3-5, stop if you
need anything from me else keep going").

**Test.** `tests/tier1/test_choreography_parse.py`, seven tests on an invented scene: no
sections give empty `cast`, `moves`, `panels`; cast rows read back with Where (pixels, a region,
a member's anchor with and without an offset), Size (blank, W, WxH) and Parameters (quoted
values with spaces, file values, indexed names) parsed; moves with every time form (none, `A s`,
`A–B s`, `over the cue`, `end-1.2–end-0.4 s`, a negative start) and every action (show of two
names, hide, move to an anchor, a parameter animated with `→` and with `->`, a parameter set, a
state change); the two panels each with a cast and moves without a cue; a mis-headed table one
problem with its rows unread; a bad name, a repeated name, a Where, a Size, a parameter without
`=` and a short row each a problem; an action not understood, a scene move without `cue`, a time
not understood, a `move` to nowhere, a list item that is no move, a non-list line, a panel move
with a cue and a panel line that is neither, each a problem.

**Red.** `7 failed in 0.03s`: `KeyError: 'cast'`, `'moves'`, `'panels'` on the data, and `assert
[] == ['line 22: …']` for the problems.

**Green.** `videotools/choreography.py` (standard library, 3.9) and three lines in `script.py`
(`_new_scene` gains the keys; the four sub-headings' lines are collected and handed over after
the loop). Then `7 passed in 0.02s`; the full suite `411 passed in 124.53s (0:02:04)`, `TOTAL …
98%`, `ruff check .` clean.

**Decision / surprise.** My test text's line numbers were off by one throughout (the heredoc's
leading blank line), corrected against the parser's output once the parser was seen to be right;
and three expectations were wrong, each changed with a reason: `sample.row` is a well-formed
anchor (whether `row` exists is increment 4's check); a list item under Moves or in a panel is a
move, so one that is not understood gets the move grammar's message, and only a non-list line
gets "not a move"; and a table with the wrong header is now skipped whole, since its columns
cannot be trusted, which was a design change rather than a test fix. A row with any problem is
left out of the cast, so increment 4 never checks a half-read row. Squirrel noted video-elements'
progress mid-increment (its steps 4 and 5); nothing in our inbox.

**State.** 411 green, 98%, lint clean, pushed. Next: increment 4, the checks.

### 10 October 2026 — Item 15, increment 4: the checks, and check-script running them

**Goal.** Every check of item 15 "Checks" on a described scene, against the invented library,
and `check-script` listing them by line.

**Test.** Three files. `tests/tier1/test_choreography_check.py` (nine tests, no library): a
well-formed described scene clean; a panel section without a mistake cue; an element nobody
has (with the library) and no complaint without one; Where and `move … to` needing the member
and one of its anchors (a piece's are the five box corners and centre; not itself); the
pieces' parameters by name, kind and what is required; labels against On screen (a pill's
`text`, a hand's `label`, in a panel too); a move's cue, time (past the end, with and without
the estimate note) and member; never shown, shown again while shown, hidden while not, in the
scene and in a panel. `tests/tier1/test_choreography_library.py` (five tests, the invented
library): clean with `pot` and `table`; anchors the element lacks, `row.0`, `cell.3` (wrong
depth), `tab.2`; parameters by name, kind (number, whole number, colour, yes/no, label) and
range, indexed names, `rows` required; a data file under the video and an index past its rows
(an index up to the count allowed); states. `tests/tier2/test_check_script_choreography.py`
(six tests): scene A of the example described, clean with `--elements` and with the config
file; no setting is one problem and the pieces are still checked; an element the library
lacks by line; a time past a cue estimated, then measured after `narrated()`; a bad folder.

**Red.** Tier 1: `9 failed` / `3 failed` on `AttributeError: module 'videotools.choreography' has
no attribute 'check'` and `assert [] == […]`; tier 2: `assert (0, '') == (1, '')` for the three
tests that can fail before the wiring (the three "clean" ones pass trivially until it exists).

**Green.** Tier 1 `21 passed in 0.05s`, tier 2 `6 passed in 1.05s`; the full suite
`431 passed in 128.40s (0:02:08)`, `TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** The parser now records each panel section's heading line, for the
"no mistake cue" message. A library element's `state=` in the cast is its initial state,
checked against its states. Index 0 is "counts from 1" for parameters and anchors alike (the
anchor case first gave the anchors-list message; the pattern match now accepts 0 and the index
check names it). An index up to a data file's row count is allowed: whether the first row is a
header is the element's business and it refuses at draw time (video-elements' reply). The
first offending time of a move is reported, start before end. The anchors-with-library test
passed first time: increment 4a's anchor code already read the library's patterns; it was
then sharpened with the `row.0` case, which failed and passed. Several of my expected line
numbers were miscounted again and corrected against the real output after the code was read
and seen right; one expected message (`highlight.4` on a four-row file) contradicted the
generous rule and was dropped; one expected time (`3.5 s` on a `5.2 s` cue) was not past the
end at all. The example's cue 1 is 12 words, so its estimate is 5.2 s, not the 4.8 I first
assumed.

**State.** 431 green, 98%, lint clean. Next: increment 5.

### 10 October 2026 — Item 15, increment 5: the scene-loading rule

**Goal.** A described scene needs no module, a described panel no panel function, a scene with
both keeps its module, and a step scene with neither is refused naming both.

**Test.** `test_scenes.py`: `needed` drops `draw` for a scene with a Cast and `mistake` /
`right_way` for each described panel, keeping `panel` for a custom side panel; `load` gives
None for a described step scene without `code`, loads a module without requiring `draw` when
the scene is described, and refuses a scene with neither. `test_scene_code_check.py`:
`check_code` on a script whose step scene has no `code`, then described (clean), then described
with a module that defines nothing (clean). `test_stills.py`: scene A of the example described
with its `code` removed renders two stills, exit 0, nothing on stderr. Three pinned messages
changed in advance to the new wording.

**Red.** `assert ['draw', 'mistake', 'right_way'] == ['mistake', 'right_way']` and the old
message against the new, in `test_scenes.py` and `test_scene_code_check.py`.

**Green.** `49 passed` over the four files after the implementation (`scenes.described`,
`needed`, `load`, `check_code`; `frame.draw_frame` calls `draw` only when the module has it,
`mistake_panels` takes each body with `getattr`); the full suite `437 passed in 131.89s
(0:02:11)`, `TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** The first run of the stills test failed on stderr: the `prepared`
fixture is cropped but not narrated, so `stills` printed its "times are estimated" notice; the
test now narrates first, as its neighbours do, which was the test's omission, not the command's.
A described scene without a module now renders as chrome and empty panels until increment 6;
the README's notes say so rather than leaving it to be discovered.

**State.** 437 green, 98%, lint clean, pushed. Increments 3–5 done as asked at 14:20. Next:
increment 6, on Squirrel's word.

### 10 October 2026 — Item 15, increment 6: a described cast drawn: show, hide, move, placement

**Goal.** A described scene drawn frame by frame through the library and the frame's pieces;
the commands opening the library and refusing a bad description before drawing.

**Test.** `tests/tier2/test_perform.py`, eight tests on scene A of the example described
(its `code` removed, a `pot`, a `pill`, a `table` from a CSV the test writes, a badge placed by
the pot's corner, a `pot` and a `pill` in the panels), frames drawn in-process as
`test_frame.py` draws them: absent before its show, mid-fade half way, there after; the table
in place after its own span; a move glides the pot to its new place and a hide removes it; the
badge follows the pot it is placed by; the panel's pot drawn in panel pixels while the curtain
is up; the stub asked to draw with the rect, state, converted params (rows as lists) and alpha;
`frame.Video` refused without a library and with the description's problems listed; `stills`
and `render --dry-run` with `--elements`, and `render` refused without. The increment-5 stills
test now passes `--elements`, since its scene needs the library.

**Red.** `3 failed, 5 errors`: `TypeError: Video.__init__() takes 2 positional arguments but 4
were given`, `DID NOT RAISE Failure`, `assert (0 == 3)`.

**Green.** `8 passed in 2.48s`; the full suite `445 passed in 131.34s (0:02:11)`, `TOTAL …
97%`, `ruff check .` clean. Three expectations of mine were wrong and corrected against the
code once it was read and seen right: the table sampled at 1.4 s was mid-fade (its span is
1.2–1.8 s; sampled at 2.0 s now); the badge sampled at its centre hit the ✓ mark (sampled above
it); the paperboat kit's `correct` is `#3E7D4F`, not the `#2E7D4F` I had typed. The refusal's
line numbers moved up one because `describe()` removes the `code` line.

**Decision / surprise.** `perform.Performance` resolves rects lazily and recursively so a
member placed by another's corner follows it wherever the cast order puts them; a cycle is a
refusal in words. A computed anchor (a row, a cell) is known only after its member is drawn,
so a member placed by one must come later in the cast (a refusal otherwise; `check-script`
gains that check in increment 8). A piece's rect is a point unless it has a Size; its real
extent for its corners is increment 8's. `elements.from_args` turns a malformed config file
into a refusal, so the four commands never see `ConfigError`. Coverage dipped to 97%: the
`text`, `hand`, `callout` and `arrow` branches, region fitting, the parameter conversions and
the two refusals in `perform.py` have no test yet; 7 and 8 bring them.

**State.** 445 green, 97%, lint clean, pushed. Next: increment 7.

### 10 October 2026 — Item 15, increment 7: parameters and states change in moves

**Goal.** `NAME.PARAM A → B`, `NAME.PARAM VALUE` and `NAME STATE → STATE` take effect over their
spans, for the library's elements and the pieces alike.

**Test.** `test_perform.py`, four more tests on scene A described with moves: an animated number
absent before its span (the element's default holds), eased half way at the middle, whole for an
integer, final after; a word set at the span's start, a number set eased (a badge's `r` 20 → 40
seen in pixels); a state `plain` before, `("plain", "cracked", 0.5)` half way, `cracked` after;
and the other pieces (`text`, `hand`, `callout`, `arrow`) drawn with a pot fitted into the
`centre` region (409 × 409 at 546, 322). The stub `pot` gained a second state, `cracked`, for
the state test, which moved two expectations (`test_elements_open`, and the states test in
`test_choreography_library`, which now asks for `broken`, a state the pot truly lacks).

**Red.** `KeyError: 'highlight.2'`, `KeyError: 'highlight-colour.2'`, `assert 'plain' ==
('plain', 'cracked', 0.5)`; the pieces test failed only on my rounding (Python rounds 546.5
to 546).

**Green.** `12 passed in 3.67s` for `test_perform.py`; the full suite `449 passed in 133.07s
(0:02:13)`, `TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** Before a parameter's first move the cast's value or the element's
default holds, not the move's `A`: a script that wants `A` from the start says so in the cast.
A set of a number eases from the current value over the span, so a bare `cue 2: tick.r 40`
grows the badge over 0.6 s rather than jumping; a set of a word is a step at the span's start.
Three expectations of mine were corrected against the code once read: the "before" value is
absent, not 0; the badge sampled at 2.9 s met the pot mid-move (sampled at 2.6 s); float
progress needs `approx`.

**State.** 449 green, 98%, lint clean, pushed. Session ended here at Squirrel's word. Next:
increment 8.

### 10 October 2026 — Item 15, increment 8: anchors, computed and fixed, and the pieces' extents

**Goal.** A member placed by a library element's computed anchor (a row, a cell) lands there;
a fixed anchor places a member before its element is drawn; a pill and a text have their drawn
extent for the members placed by their corners; `check-script` requires a member placed by a
computed anchor to come after that member (Squirrel, 17:20: "continue with increments 8-10").

**Test.** `test_choreography_library.py`: a badge before the table placed by `t.row.1`, a
callout before it targeting `t.row.1`, and a move to `t.row.2` by a member before it, each a
problem naming both members; a badge placed by `p.rim` with `p` last, and members after the
table, fine. `test_perform.py`: a badge 60 px above the pot's rim placed *before* the pot in
the cast (at 240, 191: the rim 12 4 of 24 24 scaled into 200 px); a badge at the stub's
`row.2` (440, 558) after the table; a pot placed by the pill's bottom-right corner lands right
of and below the pill's point; one placed by the text's top-right lands right of and above its
baseline.

**Red.** `assert [] == ["line 25: …"]` and `videotools.cli.Failure: 'rim' of 'pot1' is computed
when it is drawn, so a member placed by it must come after 'pot1' in the cast` (a fixed anchor
treated as computed).

**Green.** `28 passed` over the three files after the implementation (`_is_computed` and the
cast order in `choreography`, `anchors_of` in `perform` taking drawn anchors first, then box
anchors, then fixed anchors fitted into the rect; `frame.text` now returns the width drawn,
`scenes.Frame.text` passes it on); the full suite `452 passed in 131.75s (0:02:11)`, `TOTAL …
98%`, `ruff check .` clean after two unused locals went.

**Decision / surprise.** My test first had a member before the table move to the table's row
and called it fine; the code flagged it, rightly, since a move's target is resolved when the
mover is drawn: the test's cast was reordered. A fixed anchor is scaled as if the element is
fitted uniformly and centred in its rect, which is how video-elements' `geometry` fits an SVG
as far as its PLAN.md says; the Tier 3 confirms it against the real library. A text's box is
its width by its type size, 0.75 of the size above the baseline: approximate, said so in
PLAN.md.

**State.** 452 green, 98%, lint clean, pushed. Next: increment 9 (tests written).

### 10 October 2026 — Item 15, increment 9: the curtain for free

**Goal.** A member shown before the mistake cue and not named in any move at or after the cue
that follows it fades under the panels, so the glimpse of request 12 cannot be written.

**Test.** `tests/tier1/test_perform_curtain.py` (pure, badges only, an invented Timeline with
the mistake on cue 2 of 3): such a member is at 1 while the panels rise, between 0 and 1 from
0.5 to 0.7 s after the mistake cue's start, and 0 after; one hidden at cue 3 is left to its
moves (1 at 5.0 s, 0 after the hide); one first shown at cue 2 is untouched; a scene with no
mistake has no curtain. `test_perform.py`: scene A of the example given a third cue (and a 1 s
timing written into `timing.json`), the pot shown at cue 1 and never named again: there just
before the mistake cue, gone 0.2 s into cue 3 when the panels have lifted; and
`stills --cue-changes` on that scene quiet, exit 0.

**Red.** `assert 1.0 < 1.0` in tier 1; in tier 2, with `perform.py` stashed, `assert (31, 111,
139) != (31, 111, 139)`: the pot still there after the lift.

**Green.** `20 passed in 4.57s` for the two files; the full suite `458 passed in 142.71s
(0:02:22)`, `TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** My first tier 2 pin was wrong twice before it was right: sampling 0.2 s
into the mistake cue met the rising panels' tint, and sampling at the pot's first place forgot
that the cast moves it; the honest pin is the pot's moved place just before the mistake cue and
after the lift. The `stills --cue-changes` test cannot fail on this rule: without the rule the
pot stays visible through the lift, which the warning does not see (it looks for a picture
that vanishes as the panels lift); the test stays as the request's "no warning" check, and the
pixel test is the proof. "Named at a later cue" is any move whose cue is greater than the
mistake cue's.

**State.** 458 green, 98%, lint clean, pushed. Next: increment 10.

### 10 October 2026 — Item 15, increment 10: a panel's own moves, and the equivalence proof

**Goal.** A Mistake or Right way section's moves count from the panels' rise; and the request's
proof, a described scene and the same scene as a module giving equal frames.

**Test.** `test_perform.py`: the Mistake panel's pot shown `1.0–1.4 s` after the rise, absent at
cue 2 + 0.8 s (covered, before its show) and there at + 1.6 s; and scene A of the example
described (a pot, a pill, a pot and a pill in the panels) hashed with `frame-hashes --out`,
then the same scene as a module (`fold_in_half.py` rewritten to draw exactly what the stub
draws: the accent rectangle, `frame.tag` with the same arguments) hashed with `--compare`, exit
0 and nothing printed.

**Red.** Neither test failed first: panel moves were built in increment 6 without a test of
their own, and the proof is a proof. So, as CLAUDE.md's exception asks, the panel test was
checked against the code broken on purpose: with the panel's clock set to 0 it failed
(`assert (31, 111, 139) != (31, 111, 139)`), restored it passed. My first version of that test
did not fail even then, because it sampled while the panels were still translucent; it now
samples while they are fully up. The proof's power rests on `frame-hashes --compare` exiting 1
when frames differ, which its own tests pin.

**Green.** `2 passed in 1.53s`; the full suite `460 passed in 134.72s (0:02:14)`, `TOTAL … 98%`,
`ruff check .` clean.

**Decision / surprise.** The equivalence holds bit for bit on this scene: the described cast
and the module go through the same `frame.tag` and the same cairo fill, so the hashes match
with no tolerance. With the real library the Tier 3 compares a described scene A2 against v4
of the second video by `compare-frames`, where differences are expected and looked at by eye.

**State.** 460 green, 98%, lint clean, pushed. Increments 8–10 done as asked at 17:20. Next:
increment 11, the README's format section, then 12, the Tier 3.

### 10 October 2026 — Item 15, increment 11: the README, and a find from the first real run

**Goal.** The format documented for users, with a real run, and the flags in every usage line
(Squirrel, 18:45: "go ahead with 11-15", then "rest of item 15 and then request 14").

**Done.** README: "Describing a scene in the script" (the cast, Where, Size, Parameters, the
pieces, the moves and their times, the panels, the curtain, the checks, two limits), the five
usage headings with `[--elements DIR] [--renderer PATH]`, the configuration table, a dated
note, two known limits. The real run, on a scratch copy of the example in the session's
scratchpad with the real library read-only: scene A described with `person` (standing →
pointing), `sun` (moved), `gauge` (`level` 0.2 → 0.9), `calendar` (plain → marked), a `callout`
on the sun and a `badge` on the gauge's `needle` (a computed anchor); `check-script` "No
problems found."; `stills` at 0.9, 2.3, 3.2 and 5.5 s, the sheet looked at: every move as
described, the tick on the needle's tip, the cross-fade mid-way at 2.3 s.

**Find.** The first attempt used the real `spreadsheet`, which draws in the brand's `mono`
font roles; the example's invented kit has none, and the library's refusal came out as a
**traceback** (non-negotiable 5). Test first: the stub `table` gained an `explode` parameter
that makes its draw raise the library's `Failure`; `stills` on such a scene must exit 3 with
one line, `stills: scene A: the library could not draw 'sheet' (table): element 'table': its
draw failed: …`, and write nothing. Red: `assert 1 == 3` (the traceback's exit). Green after
`perform.draw` wraps `el.draw`: `1 passed`; the expected parameter lists in
`test_choreography_library.py` gained `explode`. Full suite `461 passed in 134.37s (0:02:14)`,
`TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** The example video stays free of described scenes, so the quick start
never needs the library; the README's real run is on a copy and says so. The real
`spreadsheet`'s `row.N` anchor is the *left* end of data row N and `cell.N.M` the middle of
the cell, so the worked example in PLAN.md item 15 (which put ticks 40 px right of `row.N` as
if it were the right end) is adjusted when A2 is described for real (increment 12).

**State.** 461 green, 98%, lint clean, pushed. Next: increment 12.

### 10 October 2026 — Item 15, increment 12: the Tier 3 on the real scene A2, and three finds

**Goal.** The request's proof on the real thing: scene A2 of the training-video project's
second video described in the format, drawn from the real library, compared with v4.

**Done.** A scratch copy in the session's scratchpad (the script, `assets/`, `scenes/`,
`sources/`, `work/narration/timing.json`, the douglassquirrel brand kit; v4 read in place;
nothing written into that project). A2 described from its module and PLAN.md's worked example,
adapted to the real library: `spreadsheet` at its natural size (`564x262`: 34 + 530 wide,
24 + 4 × 58 + 6 high), `numeric=B`, `row.N` being the left end of a data row so the ticks sit
at `+ 570 0` and the hand at `+ 680 11`, the working as `text` pieces, the landing total moved
to `cell.3.2` and hidden while `cell-alpha.3.2` rises, the panels' cell text as `text` pieces
(no `formula-bar`) and their sheets from a scratch CSV of `=...` cells, `highlight` rather than
a cell box. `check-script` "No problems found."; `stills` at 1.5, 7.0, 15.0, 16.6, 19.0, 23.5,
24.3 and 25.5 s; `compare-frames` against v4 at 7.0, 16.6 and 24.3 s:

```
A2          7.00 s  old  110.60 s  mean difference   2.3
A2         16.60 s  old  120.20 s  mean difference   2.5
A2         24.30 s  old  127.90 s  mean difference   2.9
```

By eye: the same picture, sheet, highlight, working lines, the landed total, ticks, hand and
"checked ✓" pill in place; the panels as designed. The sheets stay in the scratchpad.

**Finds.** (1) The first run refused: `'total' is hidden at cue 2 but was not shown`. The
check ordered shows and hides by `tl.start(cue) + offset`, ignoring a time written from the
cue's end, so `end-1.2 s` (10.2 s in) sorted before `7.7 s`. Test first
(`test_a_time_counted_from_the_cues_end_is_ordered_by_where_it_falls_not_by_its_offset`):
red `assert ['line 30: …'] == []`, green after `_check_moves` resolves the time; its second
case first picked `end-0.3 s`, which also ran past the cue's end (a correct second problem),
now `end-0.9 s`. (2) The first comparison (mean differences 3.7, 3.8, 3.2) showed the
"Sample output" tag gone after the mistake: the curtain rule hid it, as the request asked,
but v4 keeps it and the format could not say so without a fake move. The `keep NAME[, …]`
action was added test-first (parser, check: its names must exist; curtain: a keep at a later
cue leaves the member; red on the parser's grammar message, green with `keep` in `_SHOW_RE`
and skipped by the check's move branches), documented in README and PLAN.md. (3) The yellow
highlight was the script's `highlight` colour, which the description had to name
(`sample.highlight-colour.3 highlight`); and a data-driven element is fitted into its Size, so
a `spreadsheet` must be given its natural size or it is scaled into the description's nominal
400 × 300 (README). After (2) and (3): 2.3, 2.5, 2.9.

**Green.** Full suite `464 passed in 135.31s (0:02:15)`, `TOTAL … 98%`, `ruff check .` clean.
The commit `71293d0` went out without this entry (my script's search string was stale); this
entry follows in its own commit.

**State.** Item 15 complete on this side. Next: request 14, item 16.

### 10 October 2026 — Item 16, increments 13 and 14: the setting, the lines, check-script, the end card

**Goal.** `element-credits` in the Settings; the library elements a video uses collected and
credited through `lib.credits`; the lines printed by `check-script` for approval and checked
against the body font; and drawn on the end card below the two it draws today.

**Test.** `tests/tier1/test_credits.py` (six tests on an invented two-scene script and the
invented library, which gained a second source, Invented Peeps for the `table`): the elements
used in script order, once each, panels included, pieces not; `auto` one line per category;
`none` nothing; wording wins; no library elements no lines unless wording; the setting optional
and read back; an element the library lacks left to the checks. `test_check_script_choreography.py`:
the block after the `added:` lines; `none` and wording printed; a credit line with `€` listed
by the font check. `tests/tier2/test_end_card_credits.py`: the two library lines at 932 and
968 px below the existing two, nothing at 1004; `none` byte for byte the plain example's card;
a long wording wrapping to two lines with the bottom margin clear.

**Red.** `ImportError: cannot import name 'credits'`; `assert False` on the block;
`assert (1 == 0)` (the setting unknown); the font-check line absent; `_band_has_text(…, 932)`
false.

**Green.** Each file green after its implementation; the full suite `476 passed in 135.22s
(0:02:15)`, `TOTAL … 98%`, `ruff check .` clean.

**Decision / surprise.** `check-script` now opens the library once (`library_for`) for both the
checks and the credits. The first run of the "element the library lacks" test ended in a
traceback: `lib.credits` refuses an unknown name, so `credits.known` keeps only the elements
the library has and leaves the unknown one to the checks (test first). Three expectations of
mine were corrected against the code: the described example's exact output gains the credits
block; the end card has *two* library lines because the `table` now has a source; a test that
changed one pot to a teapot had left the panel's pot. The block prints only when the script
uses library elements or sets the setting, so every plain script's output is unchanged.

**State.** 476 green, 98%, lint clean, pushed. Next: increment 15, the credits file.

### 10 October 2026 — Item 16, increment 15: the credits file beside the finished video; request 14 complete

**Goal.** `assemble` writes `<output stem>.credits.txt` after the video: every source the
video's elements came from, its credit line, licence and elements; refused if it exists.

**Test.** `test_assemble.py`: the described example (a `pot` from Invented Icons, a `table`
from Invented Peeps) assembled with `--elements` writes the file with the exact text (the
title, then one paragraph per source) and prints `Wrote …credits.txt`; an existing file is
refused before anything is written, `--replace` or not, and kept; a plain video gets no file and
its output has no word of credits; a video with library elements and no library is refused in
words. The usage line gains the two flags (predicted change to `test_help_and_usage`).

**Red.** `assert (2, 'usage: a…') == (0, '')` (no `--elements` on `assemble`) and the usage
line.

**Green.** `21 passed in 18.96s` for `test_assemble.py`; the full suite `480 passed in 137.96s
(0:02:17)`, `TOTAL … 98%`, `ruff check .` clean. Against the real library, read-only, on the
scratch example of 19:00 (`person`, `sun`, `gauge`, `calendar`):

```
['Icons: Tabler Icons', 'People: Open Peeps by Pablo Stanley']
Credits for Folding a Paper Boat

Icons: Tabler Icons
  licence: MIT
  elements: sun, calendar

People: Open Peeps by Pablo Stanley
  licence: CC0 1.0
  elements: person
```

the gauge, drawn in the library, credited nothing, as the register says.

**Decision / surprise.** The file is written whatever `element-credits` says, since it is the
record for a client and the setting governs only the card. The `Wrote` line for the file comes
after the video's three lines, so a plain video's last three lines are as pinned. PLAN.md item
16 (5) had said "the dry run says so" for a video with no library elements; `assemble` has no
dry run, so nothing is said and its output for such a video is unchanged (the PLAN.md wording
corrected). The source name in the file is the credit line itself, since the interface's
`lib.credits` gives category, credit line and licence and not the register's key.

**State.** 480 green, 98%, lint clean, pushed. Items 15 and 16 complete. Nothing in progress.

### 10 October 2026 — The credits file's default settled

**Decision.** Squirrel (21:10): "default is fine": the credits file is never replaced, like the
video ("Settled" 28); "Open questions" is empty. Nothing changes in the code, which was built
that way and is pinned by `test_an_existing_credits_file_is_refused_before_anything_is_written_even_with_replace`.

**State.** 480 green, 98%, lint clean, pushed. Nothing in progress.

### 10 October 2026 — Session end: request 15 arrives; handover

**Decision / surprise.** At 22:59, while the handover was being written, request 15 arrived
from the training-video project (`inbox/request-from-training-video-2026-10-10-15.md`): four
items found by describing its scenes A2 and B for real against `08076e3`. Read and reported to
Squirrel with a first comment; **nothing done**. (1) is a real bug of ours: `perform._point`
parses `member.anchor + X Y` with `parse_where` and drops `dx`, `dy`, so an arrow's `from`/`to`
and a callout's `target` land on the bare anchor (a one-line fix with a test; it escaped the
tests because none used an offset there). (2) `progress` and `head` on `arrow`, animatable, and
a blank Where for an arrow (its box from its ends): small, test-first. (3) a blank Size at the
element's natural size needs video-elements' `el.natural_size` (its request 3) through the shared
interface, so the words must be the same in both READMEs through Squirrel; the `check-script`
warning for a nominal-sized code element with no Size can be built now. (4) a pinning test
only. That project also verified requests 13 and 14 on Linux (479 passed, 1 skipped) and A2
described against v4 at 1.1 on every step frame, better than our 2.3–2.9 here (their
description, not ours). "Where things stand" rewritten above as the handover.

**State.** 480 green, 98%, lint clean, pushed. Nothing in progress; request 15 waits for
Squirrel's OK.

### 10 October 2026 — The fifteenth request is OK'd

**Decision.** Squirrel (23:09): "request 15 ok"; then (23:11): "on item 3, do wait for
natural-size in video-elements (it's being worked on now). Agree with your assumption about
head and your plan for item 3 warning exit code". Recorded as PLAN.md item 17 and "Settled" 29;
the item moved to `inbox/done/`. So: all four items, with drawing a blank Size at the element's
natural size **waiting** on video-elements; `head` on an arrow is `yes`/`no` (whether the
arrowhead is drawn, default `yes`); the `check-script` warning does not change the exit code.

**Surprise.** Two things from reading the code before any test. `draw.arrow` already takes
`progress` and `head`, and its `head` is a size in pixels (default 20), not a yes/no; the
described `head=no` is built as agreed, by handing `draw.arrow` a head of 0, and a size can be
offered later if anyone asks. And the request's "a code element whose size row says nominal"
cannot be read through the interface: the real library's description (`lib.element(name)`) has
`size` as two numbers and nothing of the row's note (`videoelements/element.py`, read-only),
though the real `ELEMENT.md` files do say it there (`spreadsheet`, `prompt-box`, `file-chip`,
`diff`: `nominal: …`; `chat-window`: `the design size; it fits whatever rectangle it is given`).
Assumed: video-tools reads that Notes cell from the description's `folder`; recorded as PLAN.md
"Open questions" 1 for Squirrel.

**State.** 480 green as left. Next: item 17, 1, the offset bug, a reproducing test first.

### 10 October 2026 — Item 17, 1: an arrow's ends and a callout's target at their offsets

**Goal.** `from`, `to` and `target` written `member.anchor + X Y` land on the anchor plus the
offset, as a Where does (request 15, item 1: a bug).

**Test.** `test_an_arrows_ends_are_its_anchors_plus_their_offsets` and
`test_a_callouts_target_is_its_anchor_plus_the_offset` (tier 2, `test_perform.py`): scene A of
the example described with two pots, an arrow `from="pot1.centre + 10 0" to="pot2.centre + 0 -5"`
and a callout `target="pot1.top-right + -20 30"`; `draw.arrow` and `Frame.callout` replaced by
recorders, so the assertion is on the exact points handed over.

**Red.** The bug reproduced, the points on the bare anchors:

```
E       assert [(240.0, 318....590.0, 468.0)] == [(250.0, 318....590.0, 463.0)]
E         At index 0 diff: (240.0, 318.0) != (250.0, 318.0)
E       assert [(340.0, 218.0)] == [(320.0, 248.0)]
E         At index 0 diff: (340.0, 218.0) != (320.0, 248.0)
2 failed, 19 deselected in 1.15s
```

**Green.** `perform.Performance._point` adds the parsed `dx`, `dy`:

```
2 passed, 19 deselected in 0.66s
482 passed in 142.49s (0:02:22)
```

**Decision / surprise.** It escaped because no test put an offset in `from`, `to` or `target`;
`check-script` had always accepted the offset (the same `parse_where`), so the script read
clean and drew wrong. First written as one test, split in two so that each assertion was seen
to fail. The suite now takes about 2 min 20 s, longer than a foreground command's two minutes
here: run it with a longer timeout.

**State.** 482 green, 98%. Next: item 17, 2, `progress` on an arrow (its two tests are written
and red).

### 10 October 2026 — Item 17, 2: an arrow that draws on, with or without its head, and needs no Where

**Goal.** `progress` (0 to 1) and `head` (`yes`/`no`) on the `arrow` piece, and a blank Where
allowed for an arrow, its box the span of its two ends (request 15, item 2). Five cycles.

**Tests, red and green, in order.**

1. `test_an_arrow_draws_on_as_its_progress_is_animated` and
   `test_an_arrow_with_no_progress_is_drawn_whole` (tier 2; `draw.arrow` recorded). Red, the
   parameter refused and nothing passed on:
   ```
   E   - line 129: scene A, cast: 'line': an arrow has no parameter 'progress' (its parameters are from, to, colour, width)
   E       KeyError: 'progress'
   2 failed, 1 passed, 20 deselected in 0.88s
   ```
   Green: `3 passed, 20 deselected in 0.86s`; suite `484 passed in 148.68s`.
2. `test_an_arrows_progress_is_a_number_from_0_to_1_in_the_cast_and_in_a_move` (tier 1). Red,
   only the non-number caught:
   ```
   E   At index 0 diff: "line 27: scene A2, cast: 'c': 'progress' should be a number, not 'half'" != "line 26: scene A2, cast: 'b': 'progress' is 0 to 1, not '1.5'"
   ```
   Green with a new parameter kind `unit` in `PIECE_PARAMS`: `4 passed, 31 deselected in 0.79s`.
3. `test_an_arrows_head_is_yes_or_no` (tier 1) and
   `test_an_arrow_with_head_no_is_drawn_without_its_head_and_with_one_otherwise` (tier 2). Red:
   ```
   E   At index 0 diff: "line 26: scene A2, cast: 'b': an arrow has no parameter 'head' (its parameters are from, to, colour, width, progress)" != "line 27: scene A2, cast: 'c': 'head' is yes or no, not '20'"
   ```
   Green: `11 passed, 36 deselected in 1.45s` (every arrow test); suite `488 passed` beside the
   next cycle's test, already written and red.
4. `test_an_arrow_may_have_a_blank_where_and_nothing_else_may` (tier 1, the parser),
   `test_an_arrow_with_a_blank_where_checks_clean_and_members_may_be_placed_by_its_box` (tier 1,
   the check), `test_an_arrow_with_a_blank_where_has_the_box_its_two_ends_span` (tier 2: pots
   placed at the arrow's `top-left`, `bottom-right` and `centre`, the arrow written right to
   left). Red, one after the other as each layer was done: the parser's refusal at line 25;
   then `TypeError: 'NoneType' object is not subscriptable` at `choreography.py:339` (the check
   reading a Where that is not there); then the same at `perform.py:44`. Green: `3 passed, 44
   deselected in 0.36s`.
5. `test_an_arrow_with_a_blank_where_cannot_point_from_or_to_its_own_box` (tier 1). Red:
   `assert [] == ["line 26: … 'from' is its own anchor, but with a blank Where its two ends are what place it"]`.
   Green: `1 passed, 14 deselected in 0.02s`.

Full suite at the end: `492 passed in 145.28s (0:02:25)`, 98%; `ruff check .`: `All checks
passed!` (one line over 120 characters found by lint, shortened).

**Decision / surprise.** `draw.arrow` took `progress` and `head` already, so the piece only
passes them on; its `head` is a size, so `head=no` hands it 0, and
`test_an_arrow_with_a_head_of_0_is_a_line_to_its_end_and_no_head` (tier 1, `test_draw.py`)
characterises that: it passed against the existing code once its sample pixel was moved off
the head's antialiased edge (my first pixel, 165 56, read 255 13 13: the test's expectation
was wrong, not the code), and was seen to fail with `draw.arrow` broken on purpose (`head =
head or 20`: `assert (255, 0, 0) == (255, 255, 255)`), then the code restored. Cycle 5 was not
in the request: without it a blank-Where arrow pointing at its own corner read clean and was
refused only at draw time ("round in a circle"); an arrow with a Where pointing at its own box
stays allowed, as before. An arrow with a Where keeps its old box, a point at the Where: only
the blank case is new. Before an animation's span the cast's value or the default (1) holds,
as for every parameter, so an arrow shown before it grows needs `progress=0` in its row: the
README will say so.

**State.** 492 green, 98%, lint clean. Next: item 17, 3, the `check-script` warning.

### 10 October 2026 — Item 17, 3 (first half): a blank Size on a nominal-sized element is a warning

**Goal.** `check-script` lists a warning, by line, for a cast member with a blank Size whose
element is code with a nominal size; a warning does not change the exit code (request 15,
item 3; Squirrel, 23:11). Drawing at the natural size waits on video-elements.

**Tests.** Tier 1 (`test_choreography_library.py`):
`test_a_blank_size_on_a_code_element_whose_size_is_nominal_is_a_warning_and_not_a_problem` (a
scene's cast and a panel's; none for an svg element, a piece, or a member with a Size),
`test_no_warning_without_a_library_or_for_a_code_element_whose_size_is_not_said_to_be_nominal`
(a copy of the invented library with the note changed),
`test_no_warning_and_no_crash_when_the_elements_file_is_not_there_or_has_no_size_row`. Tier 2
(`test_check_script_choreography.py`):
`test_a_blank_size_on_a_nominal_sized_element_is_listed_as_a_warning_and_the_exit_is_still_0`,
`test_warnings_come_after_the_problems_and_the_exit_is_1_for_the_problems`.

**Red.** First `AttributeError: module 'videotools.choreography' has no attribute 'warnings'`;
with an empty `warnings` in place, the assertions:

```
E       assert [] == ['line 26: sc...ve it a Size']
E       AssertionError: assert '| size | 300 200 | nominal: ' in '# table — an invented data-driven element…
2 failed, 6 deselected in 0.04s
```

and for the command, the output ending at `No problems found.` with no warning after it:
`2 failed, 1 passed, 9 deselected in 0.47s`.

**Green.** `2 passed, 6 deselected in 0.10s`; `2 passed, 9 deselected in 0.31s`; suite
`498 passed in 143.76s (0:02:23)`, 98%; `All checks passed!`.

**Decision / surprise.** The invented library's `table` now says `nominal: …` in its size row,
as the real spreadsheet does. A third tier 2 test, "no warning when the element is given a
Size", passed the moment it was written (tier 1 already pins that with the `sized` row), so it
was deleted rather than kept as a test that had never failed. The third tier 1 test covers two
defensive lines (no `ELEMENT.md`, no size row: the real reader would have refused both, but a
traceback here would be worse); it passed against the code as written and was seen to fail with
those lines broken on purpose (`return True` at the end, the file check removed), then the code
restored. **video-elements moved while this was being built**: at 23:20 its repository
(read-only) had commits `bd2b4fb` (a `fit` key: `ratio`, `stretch`, `natural`) and `41673a5`
(`el.natural_size(frame, params)`), with its request 3 still in progress and its diary saying
the interface change is to be told to video-tools through Squirrel at the end. Nothing here is
built on either yet; the warning reads the note, which is what tells for `diff` (nominal, fit
`ratio`) in any case. PLAN.md "Open questions" 1 says so.

**State.** 498 green, 98%, lint clean. Next: item 17, 4.

### 10 October 2026 — Item 17, 4: a `WxH` Size reaches the element as its rect

**Goal.** Pin that a Size written `WxH` is the rect the element is handed, whatever the
element's own proportions, so an element video-elements marks as stretching gets the shape the
script says (request 15, item 4: "nothing to do if that is already so").

**Test.** `test_a_size_given_as_w_by_h_reaches_the_element_as_its_rect_whatever_its_own_proportions`
(tier 2): the 24 × 24 pot at `200x80`, and the 300 × 200 table in the `right` region at
`100x300`, centred there and not fitted.

**Red / green.** It was already so, so no red-then-green for the code; the characterising
discipline instead. Passing as written: `1 passed, 25 deselected in 0.38s`. With `own_size`
broken on purpose (the `WxH` branch removed, so the height came from the element's ratio):

```
E       assert (140.0, 218.0, 200.0, 200.0) == (140.0, 218.0, 200.0, 80.0)
E         At index 3 diff: 200.0 != 80.0
1 failed, 25 deselected in 0.34s
```

Restored: `1 passed`; suite `498 passed in 143.76s (0:02:23)`.

**Decision / surprise.** `test_the_library_is_asked_to_draw_with_the_rect_state_params_and_alpha`
had pinned one such case in passing (the table at `300x100`); this one is named for the rule.
What an element does with the rect (stretch, or fit keeping its ratio) is the library's.

**State.** 498 green, 98%, lint clean. Next: the README, then the Tier 3 against the real library.

### 10 October 2026 — video-elements' note arrives; item 17, 3 (second half): a blank Size at the natural size

**What arrived.** `inbox/request-from-video-elements-2026-10-10-2.md` (23:32): the description's
`fit` (`ratio`, `stretch`, `natural`) and `el.natural_size(frame, params)` are in the shared
interface, in video-elements' words; it asks video-tools to use `natural_size` for a blank Size
when `fit` is `natural`, and to put the two lines where the interface is quoted. It also lists
changes we may notice (text measured at the brand's scale, `chat-window` and `bubble` stretching,
the renderer called without `-`, `box.*.*` on the spreadsheet, a new `formula-bar`); none needs
anything here (no test of ours stubs `rsvg-convert`).

**Decision.** Built without asking Squirrel again, on this reading, recorded as "Settled" 30
so that he can say if it is wrong: he OK'd request 15 (23:09), whose item 3 is this; my question
was whether this half should wait until he had OK'd the interface on the video-elements side; his
answer (23:11) was "do wait for natural-size in video-elements (it's being worked on now)"; he
then settled it there (its DIARY, 23:31) and the note came. The note is moved to `inbox/done/`.
The interface block in PLAN.md item 15 has the two lines (the README never quoted the block).
A second assumption, PLAN.md "Open questions" 2: in a region, a natural-sized element with a
blank Size is centred at its natural size, not scaled to the region as other elements are.

**Tests.** Tier 2 (`test_perform.py`):
`test_a_blank_size_draws_an_element_that_offers_one_at_its_natural_size` (the rect, a member
placed by its corner, and `natural_size` asked with the rows `draw` gets),
`test_in_a_region_it_is_centred_at_its_natural_size_and_not_fitted_to_the_region`,
`test_a_refusal_to_give_the_natural_size_is_one_message_in_words`. The invented library's
`table` has `fit` `natural` and a `natural_size` (120 a column by 30 a row; recorded in
`lib.sizes`). For the warning: `test_no_warning_for_an_element_that_offers_its_natural_size`
(tier 1 and tier 2).

**Red.**

```
E       assert (140.0, 518.0, 300.0, 200.0) == (140.0, 518.0, 240.0, 120.0)
E       assert (751.0, 290.0, 711.0, 474.0) == (986.5, 467.0, 240.0, 120.0)
E         - stills: scene A: the library could not size 'sheet' (table): element 'table': its natural_size failed: …
E         + stills: scene A: the library could not draw 'sheet' (table): element 'table': its draw failed: …
```

and, for the warning, still given for the natural-fit table:
`2 failed, 5 passed, 15 deselected in 0.56s`.

**Green.** `30 passed in 9.06s` (`test_perform.py`); `22 passed in 2.03s` (the warning's two
files); suite `504 passed in 142.72s (0:02:22)`, 98%; `All checks passed!`.

**Decision / surprise.** `Performance` keeps the frame it is drawing on, since `natural_size`
needs it to measure text, and asks with the member's parameters at that moment (now worked out
once a frame, not once for the size and again for the draw: the data file was being read each
time). The earlier warning tests changed their expectation on purpose, not to match output:
the rule itself changed (PLAN.md item 17, 3: no warning for an element that offers its natural
size), so they now run against a copy of the invented library with the table's `fit` row
removed, which is what the real `diff` looks like. A mistake of mine caught by reading, not
by a test: the first version left `natural` unset for an arrow with a blank Where that has a
`move`; fixed, then `test_an_arrow_with_a_blank_where_can_be_moved_like_any_member` written
and seen to fail with the fix undone (`UnboundLocalError: cannot access local variable
'natural'`). Lint found one thing in the stub (a bare expression), now an assertion. Not built,
not asked: a Size of `W` alone still takes its height from the nominal proportions, even for a
natural-sized element (the library then fits the natural shape inside it).

**State.** 504 green, 98%, lint clean. Next: the README, "Notes for users", the Tier 3 against
the real library.

### 10 October 2026 — Item 17: README, and the Tier 3 against the real library

**Tier 3** (23:30–23:45, in the session's scratchpad; nothing written in any other project).

1. A copy of the example, scene A described against the real library: a `sun`, a `gauge`, a
   pill, an arrow with no Where `from="sun.right + 20 0" to="fuel.left + -20 0"` and
   `progress=0` animated `0 → 1` over 0.6–1.6 s of cue 1, a second arrow with `head=no`, and a
   badge at `link.centre`. `check-script`: `No problems found.` `stills` at 0.9, 1.8, 2.6 and
   3.4 s, by eye: no accent arrow at 0.9 s; half of it, with its head, at 1.8 s; whole at 2.6 s,
   starting 20 px right of the sun and stopping 20 px short of the gauge; the plain line from
   the pill has no head; the tick sits on the middle of the arrow at 3.4 s. (First drawn with
   the scene's module still in the script, which drew its paper over the cast: the `code` row
   taken out of the scratch copy, as the tests' `describe` does.)
2. The warning, real output, the same copy with a `diff` and a `spreadsheet` both without a
   Size (exit 0):
   ```
   No problems found.

   1 warning:
     - line 133: scene A, cast: 'changes': Size is blank and a diff's own size (300 × 260) is nominal, so it will not be drawn at the size its data or text needs; give it a Size
   ```
   Before video-elements' `fit` the same run warned of the spreadsheet (`400 × 300`).
3. The training-video project's second video, scene B, in a scratch copy (script, assets, its
   four scratch CSVs, timing, the douglassquirrel kit), described as that project wrote it
   (`checks/elements-check-2026-10-10/scene-B-described.md`, read) with the Sizes of the three
   file chips, the prompt and the four spreadsheets blanked, the chat window `790x790`, and the
   arrow given no Where, its two offsets, `progress=0` and `paste-arrow.progress 0 → 1` over
   1.0–1.8 s of cue 6. `check-script` clean, no warnings. `compare-frames` against v4:
   ```
   B           2.50 s  old  131.90 s  mean difference   1.8
   B          14.50 s  old  143.90 s  mean difference   4.3
   B          33.00 s  old  162.40 s  mean difference   3.8
   B          35.50 s  old  164.90 s  mean difference   4.0
   ```
   By eye the same picture: the chips and the sheets the size of v4's, the window square, the
   arrow half grown at 33.0 s where v4's is and whole at 35.5 s between the same two points.
   That project's own run with sizes by hand and the old arrow gave 4.7–8.3 in cues 1–4. What
   still differs is not ours: the prompt wraps a few words later than v4's, the reply bubble's
   file icon is Tabler's, and the export's last row fades in a little earlier.

**README.** "Describing a scene in the script": the arrow's blank Where, `progress` and `head`,
offsets in `from`, `to` and `target`, a blank Size at the natural size, `WxH` as written, the
warnings with the real output above; `check-script`'s usage; three known limits; the testing
paragraph's numbers (504 tests, 98%) and the Tier 3; a dated note for users, which says that a
cast row with a blank Size on a spreadsheet, prompt-box or file-chip changes size.

**Green.** `504 passed in 145.81s (0:02:25)`, 98%; `All checks passed!`.

**Decision / surprise.** Reading video-elements' note against our code: a `stretch` element
spreads its fixed anchors over the rectangle's width and height separately, while
`anchors_of` scales a fixed anchor uniformly and centred for a member placed *before* its
element is drawn. Not touched (nobody asked, and after the element is drawn its own anchors
are used); written into "Where things stand" as a known limit.

**State.** Item 17 complete. 504 green, 98%, lint clean, pushed. Three things for Squirrel in
"Where things stand".

### 10 October 2026 — Squirrel's three answers

**Decision.** Squirrel (23:48): "1. that was OK, although always better to check if not sure
2. leave for now 3. ok". So: building the natural-size half when video-elements' note arrived,
on his 23:11 answer, was acceptable, and when unsure whether an earlier OK covers a new inbox
item the thing to do is ask ("Settled" 30); `check-script` goes on reading "nominal" from the
note beside `size` in the element's `ELEMENT.md` ("Settled" 31); a natural-sized element with a
blank Size in a region is centred at its natural size ("Settled" 32). "Open questions" is
empty. No code changes.

**State.** 504 green, 98%, lint clean, pushed. Nothing in progress; the inbox is empty.

### 10 October 2026 — video-elements' second note: `diff` is a fourth natural element

**What arrived.** `inbox/request-from-video-elements-2026-10-10-3.md` (23:53): our Tier 3 run of
the warning had named the real `diff`, rightly, and video-elements gave it a natural size
(`5f98a74`: `fit` `natural`, its `width` by 30 a line plus 20). It asks for `diff` to be named
with the natural elements in PLAN.md's interface block and the README, and for the README's
example of the warning to be put right, since that run no longer warns. Read and reported;
checked read-only in its repository (`elements/diff/ELEMENT.md`: `| fit | natural |`, the size
row still noted `nominal`).

**Decision.** Squirrel (23:53): "yes ok", to the changes as proposed, with the README's example
kept and labelled as from before the change. PLAN.md: the interface line, item 17, 3, "Settled"
33. README: `diff` in "Size" and in the note for users; the warnings paragraph says that no
element in the library gives the warning today and that the example is real output against the
library before `5f98a74`. The item moved to `inbox/done/`. No code or test changed: the suite
uses the invented library, which has a natural element and (in a copy) a nominal one without.

**Tier 3.** The same scratch copy (a `diff` and a `spreadsheet`, both without a Size) against
video-elements at `23c4f5d`:

```
No problems found.
exit 0
```

and no warning after it.

**State.** 504 green as last run (documents only since), lint clean, pushed. Nothing in
progress; the inbox is empty.

### 10 October 2026 — The sixteenth request arrives and is OK'd: an empty label

**What arrived.** `inbox/request-from-training-video-2026-10-10-16.md` (23:58): `check-script`
refuses a library element's label parameter that is empty by design (`formula-bar`'s `ref=""`:
`'bar' draws '', which is not in the script's On screen list`); it asks that an empty label not
be checked, by `check-script` or at draw time, leaves a piece's empty text to us, and asks
whether a label an element does not draw in some state can be skipped too. Their second check
(`checks/elements-check-2026-10-10b/REPORT.md`, read) reports request 15 verified on Linux
(503 passed, 1 skipped) and A2 and B re-described with the new features at 1.1 and 1.3–1.6
against v4 on every step frame.

**Decision.** Squirrel (23:59): "check inbox and do what it says", said before the item was
read out to him: taken as his OK for it, the item being an ordinary request in this project's
scope from the project he had told to make it. PLAN.md item 18, "Settled" 34; the item moved
to `inbox/done/`. Two points the request leaves open are assumed and recorded as "Open
questions" 1 and 2 (spaces only: still a label; a pill's, callout's or text's empty `text`:
still a problem; a hand's empty `label`: none).

**Surprise.** Read before any test: at draw time video-tools never checks a library element's
label; the real elements call `frame.label` themselves (`formula-bar` skips an empty one,
`prompt-box` passes its text whatever it is). So the refusal is `check-script`'s
(`choreography._library_value_problem`), and for the draw-time half of the ask the place that
makes it true whatever an element does is `Frame.label`.

**State.** 504 green as left. Next: item 18, 1, test first.

### 11 October 2026 — Item 18: an empty label is not a label

**Goal.** Request 16: an empty label parameter is not checked, by `check-script` or at draw
time; a piece's empty text decided and pinned. Four cycles.

**Tests, red and green, in order.**

1. `test_an_empty_label_for_a_library_element_is_not_checked_and_others_still_are` (tier 1,
   `test_choreography_library.py`: `tab=""` in a cast row and set in a move; a label not on the
   list and one of a single space still refused). Red, the bug reproduced:
   ```
   E   At index 0 diff: "line 25: scene A2, cast: 't' draws '', which is not in the script's On screen list (Sample output, checked ✓)" != "line 26: scene A2, cast: 'u' draws 'Sheet 9', …
   E   Left contains 2 more items, first extra item: "line 33: scene A2, moves: 'w' draws '', …
   ```
   Green: `1 passed, 10 deselected in 0.12s`.
2. `test_a_pieces_empty_text_is_a_problem_in_plain_words_and_a_hands_empty_label_means_none`
   (tier 1, `test_choreography_check.py`). Red:
   ```
   E   At index 0 diff: "line 25: scene A2, cast: 'a' draws '', which is not in the script's On screen list (Sample output, checked ✓)" != "line 25: scene A2, cast: 'a': 'text' is empty, so there is nothing to draw"
   ```
   Green with a new parameter kind `caption` for the hand's optional label: `27 passed in 0.13s`
   (both check files).
3. `test_an_empty_label_is_no_label_and_is_not_checked_but_one_of_spaces_is` (tier 1,
   `test_scenes.py`). Red: `videotools.cli.Failure: scene A: the scene code draws '', which is
   not in the script's On screen list (near side, far side)`. Green: `14 passed in 0.03s`.
4. `test_a_hand_with_an_empty_label_is_drawn_with_no_label` (tier 2; `Frame.hand` recorded).
   Red: `AssertionError: assert '' is None`. Green: `2 passed, 30 deselected in 0.57s`.

Full suite: `509 passed in 141.52s (0:02:21)`, 98%; `All checks passed!`.

**Decision / surprise.** The invented library's `draw` now passes every label parameter it is
given through `frame.label`, as the real `prompt-box` and `file-chip` do, so
`test_an_element_given_an_empty_label_is_drawn_and_one_given_a_listed_label_too` (tier 2) draws
through the same door. It passed the moment it was written, cycle 3 having been done, so it
was seen to fail with that fix undone (`the library could not draw 'sheet' (table): scene A:
the scene code draws '', which is not in the script's On screen list`), and the fix put back.
`frame.label("")` passing also holds for a video's own scene code: an empty label there draws
nothing either. The request's second ask (skip a label the element does not draw in some
state) is not built: the library says it only in prose; the README tells the author to leave
the parameter out or give it empty.

**Tier 3** (00:02, the scratch copy of the second video from item 17's check): the real
`formula-bar` added to scene B's Mistake panel as `ref="" placeholder=yes`. With this commit's
code: `No problems found.`, exit 0. With the changes stashed, the refusal the request quoted:
`line 457: scene B, mistake: 'bar' draws '', which is not in the script's On screen list (…)`.
`stills` at 26.0 s (cue 5), by eye: the bar above the sheet, no reference, no divider, a grey
placeholder bar.

**State.** Item 18 complete. 509 green, 98%, lint clean, pushed. Two assumptions for Squirrel in
"Where things stand".

### 11 October 2026 — Squirrel's answers on item 18

**Decision.** Squirrel (00:09): "1. agreed 2. yes": a label of spaces only is still a label
("Settled" 35); a piece's empty text stays a problem and a hand's empty label is none
("Settled" 36). "Open questions" is empty. No code changes.

### 11 October 2026 — The seventeenth request arrives; read and commented on, not started

**What arrived.** `inbox/request-from-training-video-2026-10-11-17.md` (00:00): what the other
ten scenes of "App For That" need the format to say, for a v5 with no Python in that project:
(1) a Cast and Moves on title and end cards, in frame pixels; (2) `rotate` for any member, in
the cast and animatable; (3) `via` (a curve) and `dash` on `arrow`; (4) `leader` on `callout`;
(5) a member's own colours for an element's colour roles (`colour.<role>=<name>`); (6) to say
what else we see the format cannot say, rather than build it. Its companion,
`video-elements/inbox/request-from-training-video-2026-10-11-4.md` (read), asks that library
for new elements and parameters.

**Decision.** Squirrel (00:09): "look in the inbox and comment (don't start yet)". **Nothing
done**: no PLAN.md item, no test, no code; the item stays in `inbox/`.

**What reading found** (their ten modules, `frame.py` and video-elements' `draw.py`, all
read-only), told to Squirrel:

- (5) needs no change to the shared interface: the real library takes an element's colour
  role from `frame.colours` when the role's name is there (`draw.colours_for`,
  `shapes.py:134`), so video-tools can hand each member a frame whose colours carry its own.
- (1) the end card has no cues (`extra 4.6`), and a move is written `cue N`: a scene without
  cues needs moves timed from its start, as a panel's are. The title's drawing before cue 1 is
  already sayable (`cue 1, -0.3–0.7 s`).
- (2) a piece's box (a pill's) is known only once it is drawn, so turning about the box's centre
  means drawing the member aside and painting it turned; anchors can be turned with it. The
  `hand` piece already has `angle`, in radians, where `rotate` would be degrees.
- (3) `draw.arrow` already draws a four-point curve and `draw.line` already takes `dash`.
- (6) things the format cannot say that the modules do: a member dimmed to a level between
  shown and hidden (takeaways: 0.55); a member growing or stretching (review's carton); a move
  spanning two cues or timed as a fraction of a cue's length (add_data, dont_vibe); a change at
  a steady rate rather than eased (typing, rows appearing, the history scrolling); a pulse (up
  and back) other than as two moves, and anything that repeats with time (flashing warnings,
  sparkles, steam); choosing columns or rows of a CSV (every module picks some); plain shapes
  (a rounded bar, a disc, a line of dashes) other than through an element.

**State.** 509 green, 98%, lint clean. Waiting on Squirrel's OK for request 17.

### 11 October 2026 — The seventeenth request is OK'd

**Decision.** Squirrel (00:13): "1. yes 2. yes 3. write your comments in training-video inbox,
standing permission granted to do that. Go ahead with request 17 as written." So: the five
asks, PLAN.md item 19 and "Settled" 37, the item moved to `inbox/done/`; a scene with no cues
writes its moves without `cue N`; the "what else" list is not built but written to the
training-video project ("Settled" 38: a standing permission to write into that project's inbox,
and nothing else there). **That project has no `inbox/` folder** and its CLAUDE.md names none,
so nothing has been written there: Squirrel asked where it should go.

**Design, decided before the tests** (PLAN.md item 19 has the rules): `via` is exactly two
points, pixels or anchors; `dash` leaves the head solid; `colour.<role>` is cast-only and works
by handing the element a frame whose colours carry the role, with no interface change; on a
card Where is frame pixels; `rotate` turns the member's finished drawing about its box's
centre, and its anchors with it.

**State.** 509 green as left. Next: item 19, 1, test first.

### 11 October 2026 — Item 19, 1 and 2: a callout's leader colour; curved and dashed arrows

**Goal.** `leader` on `callout`; `via` and `dash` on `arrow` (request 17, items 4 and 3).

**Tests, red and green, in order.**

1. `test_a_callouts_leader_takes_the_colour_named_and_ink_otherwise` (tier 2, `Frame.callout`
   recorded). Red: `'note': a callout has no parameter 'leader' (its parameters are text, target,
   size, fill, colour, anchor)`. Green: `49 passed in 9.49s` (the two files).
2. `test_a_dashed_arrow_has_gaps_in_its_line_and_a_solid_head` (tier 1, `test_draw.py`, by
   pixels). Red: `TypeError: arrow() got an unexpected keyword argument 'dash'`. Green: `11
   passed in 0.05s`.
3. `test_an_arrows_via_is_two_points_and_its_dash_two_numbers_above_0` (tier 1: one point, a
   region, a member not in the cast, one number, a zero) and
   `test_an_arrow_with_via_is_a_curve_by_its_two_points_and_with_dash_is_dashed` (tier 2,
   `draw.arrow` recorded: four control points, the area's pixels turned into the frame's, the
   anchor with its offset; `dash` as two numbers). Red:
   ```
   E   At index 0 diff: "line 26: scene A2, cast: 'good': an arrow has no parameter 'via' (its parameters are from, to, colour, width, progress, head)" != "line 27: scene A2, cast: 'one': 'via' should be two points separated by ';', …
   ```
   Green: `63 passed in 10.38s` (the three files).

Full suite: `514 passed in 143.88s (0:02:23)`, 98%; `All checks passed!` (one line over 120
characters found by lint and split).

**Decision / surprise.** `draw.line` already took `dash` and `draw.arrow` already drew a
four-point curve; the primitive only needed to hand `dash` to its line, which leaves the head
solid. `test_a_plain_arrow_is_handed_no_dash` passed as soon as written (an arrow without the
two is drawn as before) and is kept as the other half of the same rule, not as a test that
failed. `Performance._point` now reads a place in the cast's pixels as well as an anchor
(`_place`), which is what `via` needs; `from` and `to` are still anchors only, by the check.

**Also done** (00:17): at Squirrel's word ("create the inbox") the folder
`~/projects/non-code/training-video/inbox/` made, with a short README saying who made it and
why, and `reply-from-video-tools-2026-10-11.md` in it: the rules of item 19 as they are being
built, and the seven things its modules do that the format cannot say. Nothing else in that
project was touched.

**State.** 514 green, 98%, lint clean. Next: item 19, 3, a member's own colours.

### 11 October 2026 — Item 19, 3: one member in other colours

**Goal.** `colour.<role>=<colour name>` on a library member (request 17, item 5).

**Tests.** Tier 1: `test_a_colour_role_is_a_parameter_named_colour_dot_the_role` (the parser);
`test_a_members_colour_must_be_a_role_the_element_has_and_a_colour_the_video_knows` and
`test_without_the_videos_colours_only_the_role_is_checked` (the check, with and without the
video's colour names). Tier 2:
`test_a_member_with_a_colour_of_its_own_is_drawn_in_it_and_its_neighbour_in_the_default` (two
pots, by pixels) and
`test_a_members_own_colour_that_the_video_does_not_know_is_listed_by_line` (`check-script`).

**Red.** All of the first four on the parser's refusal, the behaviour missing at its first
step: `Parameters: 'colour.fill=correct' is not name=value` (`4 failed, 1 passed`); the
command's, once the rest was built, on `assert (0, '') == (1, '')`: `check-script` was not yet
handing the check the video's colours.

**Green.** `58 passed in 10.65s` (the three files); `13 passed in 2.33s`
(`test_check_script_choreography.py`); suite `519 passed in 147.04s (0:02:27)`, 98%;
`All checks passed!`.

**Decision / surprise.** No interface change: the real library takes a role's colour from
`frame.colours` when the role's name is a key there (`videoelements/draw.py`, `colours_for`;
`shapes.py:134`), so the member's element is handed a shallow copy of the frame whose
`colours` carry its own under the roles' names (`Performance._in_its_colours`); every other
member gets the frame itself. The invented elements gained a `fill` role and the stub fills
with it, resolved as the real one resolves a role, so the tests go through the same door.
`choreography.check` takes the names `frame.colour` knows as an optional `colours`:
`frame.Video` always has them, `check-script` has them when the brand kit read. Only
`colour.<role>` values are checked against them; a piece's `fill` or a library `colour`
parameter with an unknown name is still found at draw time, as before (not asked; a possible
follow-up). A move cannot name `colour.<role>`: the move grammar does not match it, so it is
refused as "not show NAME, …" as any unknown action is.

**State.** 519 green, 98%, lint clean. Next: item 19, 4 (its tests are written, set aside
while this is committed).

### 11 October 2026 — The eighteenth request arrives; read and commented on, not started

**What arrived.** `inbox/request-from-training-video-2026-10-11-18.md` (00:22), from four of the
seven things in our reply to that project (its Squirrel, 00:22: "make new request 18 for 1, 2,
4, and 5"): (1) choosing a CSV's columns and rows beside `rows=FILE`; (2) a move marked
`linear`; (4) a span that ends in a later cue, and a time as a percentage of its cue's length;
(5) dimming a member to a level. Squirrel here (00:24): "When you get to a good stopping place,
check the inbox for new requests and comment on them before continuing." Read at the stopping
place after item 19, 3; **nothing done**; the item stays in `inbox/`.

**Comment given to Squirrel.** All four are sayable and none needs video-elements. (2), (4) and
(5) all change the moves' grammar and timing (`parse_move`, `perform.window`,
`_check_moves`), as item 19, 4 (a scene with no cues) is changing now, so they are best built
after item 19 is finished, in the order linear, dim, spans and percentages, then the CSV.
Proposed: the CSV's choices written as `rows.columns`, `rows.where`, `rows.first`, named after
the parameter they qualify, so that they cannot collide with an element's own parameter names
(`columns`, `where`, `first` bare would be reserved on every element for ever); columns
separated by commas, a name or a number from 1; `where` then `first` then `columns`. `dim NAME
to LEVEL` as an action beside `show` and `hide`. In a span across cues, the member counts as
named at the later cue for the curtain rule.

**State.** 519 green, pushed. Continuing item 19, 4.

### 11 October 2026 — Item 19, 4: a cast on the title and end cards; a scene with no cues

**Goal.** `### Cast` and `### Moves` on a title or end scene, in frame pixels, drawn over the
card; a scene with no cues writes its moves without `cue N` (request 17, item 1; Squirrel,
00:13).

**Tests, red and green, in order.**

1. `test_a_scene_with_no_cues_writes_its_moves_without_a_cue_timed_from_its_start` and
   `test_a_scene_with_cues_still_needs_cue_n_on_every_move` (tier 1, the parser). Red:
   ```
   E   At index 0 diff: "line 20: scene end, moves: a scene's move starts 'cue N' (a panel's moves have no cue)" != "line 22: scene end, moves: the scene has no cues, so its moves have no 'cue N': times count from the scene's start"
   ```
   Green: `11 passed in 0.02s`.
2. `test_a_scene_with_no_cues_has_its_moves_checked_against_its_own_length` (tier 1, the check:
   a time past the scene's end, a member never shown). Red: `TypeError: '<=' not supported
   between instances of 'int' and 'NoneType'` at `choreography.py:673`, the check comparing a
   cue that is not there. Green: `42 passed in 0.15s` (the three tier 1 choreography files).
3. `test_a_title_cards_cast_is_drawn_over_the_card_in_frame_pixels_from_before_cue_1` and
   `test_an_end_cards_cast_is_drawn_and_its_moves_count_from_the_scenes_start_and_end` (tier 2,
   by pixels and the rect the stub was handed). Red, nothing of the cast drawn:
   ```
   E       assert (158, 156, 153) == (31, 111, 139)
   E       assert (247, 243, 234) == (31, 111, 139)
   ```
   Green: `38 passed in 10.80s`.

Full suite: `524 passed in 145.49s (0:02:25)`, 98%; `All checks passed!`.

**Decision / surprise.** Two expectations changed with a reason. My new test's line number was
a miscount (the refused move is the script's line 23, not 22): the test was wrong. And an
existing test's message changed on purpose, since the words now have to cover a scene with no
cues: "a scene's move starts 'cue N' (a panel's moves and those of a scene with no cues have
none)". `parse_move` takes `cueless` (`'panel'`, `'scene'` or None) in place of `in_panel`;
`perform.window` times a cue-less scene's move from 0 with `end` at the scene's total, a
panel's from its rise as before. On a card `draw_scene` is given the whole frame as its area;
the title card's own clip (the card, above the caption band) still applies, so a cast member
placed below 948 would be cut there.

**State.** 524 green, 98%, lint clean. Request 18 OK'd meanwhile (Squirrel, 00:28: "1. and 2.
both yes": after request 17, in the order linear, dim, spans and percentages, CSV, with
`rows.columns`, `rows.where`, `rows.first`); it goes into PLAN.md when request 17 is finished.
Next: item 19, 5, turning a member.

### 11 October 2026 — Item 19, 5: turning a member

**Goal.** `rotate=DEGREES` on any member, clockwise about its box's centre, animated and set
like any number; an anchor read from a turned member turned with it (request 17, item 2).

**Tests.** Tier 1: `test_rotate_is_a_number_on_any_piece_in_the_cast_and_in_a_move`,
`test_rotate_is_a_number_on_a_library_member_too_and_is_not_one_of_the_elements_parameters`.
Tier 2 (`test_perform.py`, one cast: a 200 × 80 pot turned 90°, two small pots placed by its
corners, one before it in the cast and one after, and the same pill plain and turned with
small pots on each one's corner and centre):
`test_a_turned_member_is_drawn_turned_about_the_centre_of_its_box` (pixels),
`test_an_anchor_read_from_a_turned_member_is_turned_with_it_before_or_after_it_in_the_cast`,
`test_a_piece_is_turned_about_the_centre_of_what_it_drew`,
`test_a_turn_is_animated_like_any_number_and_no_turn_is_exactly_the_frame_without` (a frame
with `rotate=0` byte for byte the frame with no `rotate`).

**Red.** The checks: `'a': a pill has no parameter 'rotate' (its parameters are text, size,
fill, colour, anchor)`, `'p': a pot has no parameter 'rotate' (its parameters are )`. Then,
the checks done, the drawing: `TypeError: 'NoneType' object is not subscriptable` four times
(`_kind` looking `rotate` up among the element's parameters): `4 failed, 38 deselected`.

**Green.** `33 passed in 0.07s` (the two check files); `42 passed in 12.13s`
(`test_perform.py`); suite `530 passed in 148.69s (0:02:28)`, 98%; `All checks passed!`.

**Decision / surprise.** How: the member is drawn exactly as it would be unturned, on a cairo
recording surface (a copy of the frame with its `ctx` swapped), and that recording is painted
onto the frame turned about the centre of the box the drawing reported. So nothing inside a
piece or an element knows about the turn, a pill's box (known only once it is drawn) is no
special case, and colours come out exact (the turned pot's pixels equal the accent). With no
turn the member is drawn straight onto the frame as before, which is what makes `rotate=0`
the same bytes. `Performance.draw` split into `draw` (the turn) and `_draw_member` (one
member, returning its box). A turned member's stored anchors are its box's corners and centre
and whatever its drawing returned, all turned; before it is drawn, a box corner or a fixed
anchor is turned from its rect (`_turned`), which is what places the member listed before it.
One test of mine was wrong, not the code: the animated turn was sampled at 3.75 s, 0.05 s
after scene A's mistake panels start to rise, so the pixel was the accent under 4% of
curtain (`(34, 110, 136)`); the move and the sample moved earlier. The `stub records the
transform` idea of the request does not apply to this way of doing it: the element draws in an
unturned context, so the tests look at pixels and at where the followers land.

**State.** 530 green, 98%, lint clean. Item 19's five parts built; the README, the Tier 3 and
the note to training-video are left. Squirrel (00:36): "check inbox for request 19 and cue up
work on it (if you agree) after 17 and 18": next.

### 11 October 2026 — Item 19: README, the Tier 3 against the real library, and a find

**Tier 3** (00:40–00:50, the scratch copy of the second video; nothing written in that
project). Its title card with its `code` row taken out and a cast in its place: the
`spreadsheet` of April's totals at its natural size with `rotate=2.2`, a `bubble` and
`typing-dots`, three `bricks` with `colour.brick=sheet-tab`, `doc` and `correct` (the second
`rotate=-12`), an arrow with no Where, `via="1050 320; 1150 480"`, `dash="14 10"` and its
progress animated, a callout with `leader=mistake`; and its end card (no cues) with a `sun`
shown at `0.5–1.0 s` and `sun.rotate 0 → 180` over `1.0–end-0.5 s`. `check-script`: `No
problems found.` `stills` at title 0.6, 2.0 and 3.2 s and end 3.0 s, by eye: the tilted sheet
fading in before cue 1; the bubble and dots; three bricks in three colours, the middle one
turned; the dashed curve half grown at 2.0 s and whole at 3.2 s with a solid head at the
sheet's turned corner; the callout's red leader to the sheet's other turned corner; the icon
on the end card.

**Find, from that run.** The first `stills` was refused: `the library could not size 'sheet'
(spreadsheet): element 'spreadsheet' has no parameter 'rotate'`. `_natural` handed
`natural_size` the member's parameters with our `rotate` still among them; the invented
library does not check parameters, so no test saw it. Reproduced first
(`test_a_turned_member_with_a_blank_size_is_sized_without_its_turn_among_the_elements_parameters`:
`AssertionError: assert ('rotate' not in {'rows': […], 'rotate': 2.2})`), then fixed: `43
passed in 11.93s`. The same class of thing as item 15's increment 11: what the stub does not
refuse, only the real library finds.

**README.** The cast's Where on a card; `leader`; `via` and `dash`; a paragraph on turning and
tinting; a paragraph on title and end cards and a scene with no cues; the checks; a dated note
for users; three known limits; the testing paragraph (531 tests) and this Tier 3.

**Also.** A second note left in the training-video project's inbox
(`reply-from-video-tools-2026-10-11-2.md`): request 17 built, the commit to check against, the
rules as built, and what was found.

**Green.** `531 passed in 149.48s (0:02:29)`, 98%; `All checks passed!`.

**State.** Item 19 complete, pushed. Next: request 18 into PLAN.md as item 20, then test-first.

### 11 October 2026 — Requests 18 and 19 into PLAN.md

**Decision.** Both OK'd earlier (00:28 and 00:36; the entries above): now PLAN.md items 20 and
21, "Settled" 39 and 40, the two items moved to `inbox/done/`. The rules were worked out
together, since both change how a move's time is written and resolved: a time may be seconds
from a cue's start, from its end, a percentage of its length, or the scene's end; a span may
end in a later cue; a move may be `linear`; `dim` and `flash` join `show` and `hide` in
deciding a member's opacity. One change to something already there: in a panel, `end` now
means the mistake cue's end (it meant the panel's rise, the same as 0, which said nothing).

**State.** 531 green as left. Next: item 20, 1, `linear`, test first.

### 11 October 2026 — Item 20, 1: a move marked linear

**Goal.** A move whose time ends `, linear` changes at a steady rate (request 18, item 2).

**Tests.** `test_a_moves_time_may_end_linear_in_a_scene_and_in_a_panel` (tier 1, the parser:
with a span, with none, in a panel, and `steady` refused);
`test_a_linear_move_changes_at_a_steady_rate_and_an_unmarked_one_eases` (tier 2: a quarter of
the way through, a linear parameter is at 0.25 and an eased one at 0.15625; a linear show at
0.25).

**Red.** `'cue 1, 0.5–1.7 s, linear: sample.rows-shown 0 → 3' is not cue N[, A s | A–B s | over
the cue]: ACTION`, from the parser and from the script the drawing test builds.

**Green.** `301 passed in 13.39s` (tier 1 and `test_perform.py`); suite `533 passed in 155.57s
(0:02:35)`, 98%; `All checks passed!`.

**Decision / surprise.** A parsed move has `linear: True` only when it is marked; my first
version gave every move the key, which broke nine existing tests that compare whole moves, for
no gain, so the shape was left as it was. Two expectations changed with a reason: the refusal's
help text now ends `[, linear]: ACTION` (two existing tests), and my new test's line number was
a miscount (34, not 39). `perform.progress(t, a, b, move)` is the one place that chooses eased
or steady, used for opacity, place, parameters and a state's progress.

**State.** 533 green, 98%, lint clean. Next: item 20, 2, `dim`.

### 11 October 2026 — Item 20, 2: dimming to a level

**Goal.** `dim NAME[, NAME…] to LEVEL`: opacity to a level over the span; a later `show`
brings it back (request 18, item 5).

**Tests.** `test_dim_names_members_and_a_level` (tier 1, the parser);
`test_a_dim_needs_a_level_from_0_to_1_and_a_member_that_is_shown_and_a_show_after_it_is_allowed`
(tier 1, the check); `test_a_dim_takes_the_opacity_to_its_level_over_the_span_and_a_show_brings_it_back`
(tier 2: the alpha the stub is handed half way down, at the level, half way back, and at 1).

**Red.** `'dim sample, pot to 0.55' is not show NAME, hide NAME, keep NAME, move NAME to WHERE,
…` from the parser, in all three (`3 failed, 75 deselected`).

**Green.** `304 passed in 13.91s` (tier 1 and `test_perform.py`); suite `536 passed in 146.03s (0:02:26)`, 98%; `All checks passed!`.

**Decision / surprise.** A dimmed member is still shown, so a `show` after a `dim` is not
"shown again while still shown" (the check keeps the set of dimmed members), and a dim of a
member that is not shown at that moment is a problem of its own. The level's range is the
check's, not the parser's, so `dim a to 1.5` reads and is refused in words. The refusal for an
unknown action now lists `dim NAME to LEVEL`, which changed two existing expectations on
purpose. My new check test's line numbers were all one too high (a miscount, the third
tonight: I now count from a known line in the same file rather than by eye).

**State.** Green, lint clean. Next: item 20, 3, percentages and spans across cues.

### 11 October 2026 — Item 20, 3: percentages, spans across cues, and the scene's end

**Goal.** A time as `P%` of its cue's length; a span that ends in a later cue (`cue 1, 0.5 s –
cue 2, end-0.5 s`) or at the scene's end (`– end of scene`); each resolved in one place
(request 18, item 4; request 19's spans).

**Tests.** Tier 1: `test_a_time_may_be_a_percentage_and_a_span_may_end_in_a_later_cue_or_at_the_scenes_end`
(the parser: seven forms read, five refused); `test_choreography_window.py`, new, five tests
of `choreography.window` (seconds, percentages, a later cue, the scene's end, a panel, a scene
with no cues);
`test_each_time_of_a_span_is_checked_against_its_own_cue_and_the_later_cue_must_come_after`
(the check);
`test_a_member_in_a_span_that_ends_at_a_later_cue_or_at_the_scenes_end_is_left_to_its_moves`
(the curtain rule). Tier 2: `test_a_show_timed_in_percentages_of_its_cue_is_drawn_at_those_moments`.

**Red.** `9 failed, 304 passed in 13.50s`: the parser's refusal of `74%–80%`, `module
'videotools.choreography' has no attribute 'window'`, and the drawing test on the script the
parser refused.

**Green.** `313 passed in 14.17s` (tier 1 and `test_perform.py`); suite `545 passed in 148.03s
(0:02:28)`, 98%; `All checks passed!`.

**Decision / surprise.** A written time is now one of `("start", s)`, `("end", s)`,
`("fraction", share)` (and `("fraction", share, 0.6)` for a lone `42%`, which runs the usual
0.6 s from there) or `("scene", 0.0)`; a move has `end_cue` only when its span ends in a later
cue, so every existing parsed move is the same data as before. `choreography.window(move, tl,
panel)` replaces `perform.window` and the check's own arithmetic (`_in_scene` is gone), so the
check and the drawing cannot disagree about when a move happens. **One behaviour changed on
purpose** (PLAN.md item 20, 3): in a panel a time counts within the mistake cue, so `end`
there is that cue's end (it was the panel's rise, the same as 0) and a percentage is of its
length. Seconds keep their ` s` and a percentage has none, which is what tells `74–80%` (refused)
from `74%–80%`; the first time of a span may share the second's ` s` only when both are seconds
in the same cue, as `0.5–1.7 s` always did. The refusal's help text grew, changing three
expectations. For the curtain rule a member is named at the cue its span ends in, and at every
cue for `end of scene`. Coverage showed two new refusals unreached (`74% s`; `0.5` with no
` s`): added to the parser's test as two more refused lines.

**State.** 545 green, 98%, lint clean. Next: item 20, 4, a CSV's columns and rows (its pure
function's tests are written and red).

### 11 October 2026 — Item 20, 4: a cast row chooses a data file's rows and columns

**Goal.** `rows.where`, `rows.first`, `rows.columns` beside `rows=FILE` (request 18, item 1;
the names by Squirrel's answer of 00:28).

**Tests.** Tier 1: `test_choreography_rows.py`, new, six tests of the pure
`choreography.select_rows` (columns by name and number and in the order written; `where` with
`=` and `!=`; `first` after `where`, columns last; the header always kept; every refusal in
words; an empty file); `test_a_rows_qualifier_is_checked_and_the_rows_counted_are_the_ones_chosen`
and `test_a_choice_that_cannot_be_made_is_refused_in_words_when_the_parameters_are_worked_out`
(`test_choreography_library.py`). Tier 2:
`test_an_element_is_handed_the_rows_and_columns_its_cast_row_chooses_and_sized_by_them`.

**Red.** `AttributeError: module 'videotools.choreography' has no attribute 'select_rows'` for
the function; then, for the check and the drawing, `'t': a table has no parameter
'rows.columns' (its parameters are rows, tab, …)` (`3 failed, 60 deselected`).

**Green.** `6 passed in 0.02s`; `322 passed in 13.66s` (tier 1 and `test_perform.py`); suite
`554 passed in 146.92s (0:02:26)`, 98%; `All checks passed!` (three lines over 120 characters
found by lint along the way).

**Decision / surprise.** The order is fixed whatever order the qualifiers are written in:
`where`, then `first`, then `columns`, so a `where` can test a column that `columns` then
drops. The check counts rows for indices against what was chosen and says so (`assets/sample.csv
has 3 rows as chosen`). A `where` with `=` that no row matches is a problem (a misspelt value
would otherwise give an empty sheet); with `!=` it is not. The qualifiers are never among the
parameters the element is handed, for its draw or its natural size (pinned: the stub gets
`{"rows": […]}` alone). The same function serves the check and the drawing, and the drawing
refuses in words too, for a caller that did not check first.

**State.** Item 20's four parts built. 554 green, 98%, lint clean. Next: item 21, `flash`; then
the README and the Tier 3 for both.

### 11 October 2026 — Item 21: a repeating flash

**Goal.** `flash NAME[, NAME…] [rate=R] [phase=P] [low=L]`: over its span the members' opacity
is multiplied by a sine between `low` and 1 (request 19).

**Tests.** Tier 1: `test_flash_names_members_and_takes_a_rate_a_phase_and_a_low` (the parser);
`test_a_flash_needs_a_cast_member_a_rate_and_a_low_in_range_and_no_other_flash_at_the_same_time`
(the check); and four on `Performance.alpha` in `test_perform_curtain.py`:
`test_a_flash_is_a_sine_from_the_spans_start_and_the_plain_opacity_outside_it` (0.5 at the
start, 1 a quarter-beat on, 0 at three quarters, 1 before the span),
`test_a_flashs_rate_phase_and_low_shape_it`,
`test_a_flash_multiplies_what_the_member_already_is_so_a_hidden_member_stays_hidden`,
`test_a_flash_does_not_name_its_member_for_the_curtain_so_it_still_fades_under_the_panels`.

**Red.**

```
E   At index 0 diff: "line 32: scene A2, moves: 'flash sample' is not show NAME, hide NAME, keep NAME, dim NAME to LEVEL, move NAME to WHERE, …" != "line 34: scene A2, moves: 'flash pot speed=2': a flash's options are rate, phase and low, each a number, not 'speed=2'"
E       assert 1.0 == 0.5 ± 5.0e-07
E       assert 1.0 == 0.6 ± 6.0e-07
E       AssertionError: assert 1.0 == 0.0
```

**Green.** `328 passed in 14.00s` (tier 1 and `test_perform.py`); suite `560 passed in 159.58s
(0:02:39)`, 98%; `All checks passed!`.

**Find, from the request's own example.** With the flash built, two of my new tests still
failed in the parser: `cue 1, 1 s – end: flash a` was refused. A bare `end` had always needed a
` s` after it (`0–end s`), and the span rules of item 20, 3 kept that; but `end` with no offset
is not a number of seconds, and request 19 writes it bare (`cue 2, 2.6 s – end: flash warn-1`).
Now a bare `end` may be written with or without ` s`; `end-0.5` still takes it. `parse_span`
rewritten round one small rule (each time says whether it needs ` s`: seconds yes, a
percentage no, a bare `end` either), pinned in the parser's flash test.

**Decision / surprise.** The five adjustments told to Squirrel at 00:38 are built as told
("Settled" 40): options `name=value`; `phase` a fraction of a beat; `rate` above 0 and at most
3, default 1.4; a flash does not name its members for the curtain rule; `end of scene`. Within
its span a flash multiplies last, after show, hide, dim and the curtain; at the span's end the
opacity steps back to the plain one (no easing in or out was asked). Overlap is by the same
`choreography.window` the drawing uses, so "overlap" means the same thing in both.

**State.** Items 20 and 21 built. 560 green, 98%, lint clean. Next: the README (written), the
Tier 3 against the real library, the note to training-video.

### 11 October 2026 — Items 20 and 21: README and the Tier 3 against the real library

**Tier 3** (01:20–01:30, the scratch copy of the second video; nothing written in that
project). The title card's sheet read from the video's own `assets/commissions-2024-04.csv`
with `rows.where="Date Closed = TOTAL"` and `rows.columns="Sales Rep, Commission"` in place of
the hand-made totals file: the six reps and their commissions, as before. Scene B: the prompt
typed `linear`; `cue 3, 0.8 s – cue 4, 50%: reply.highlight.1 0 → 0.2`; `cue 3, 20%–40%: dim
chip-1, chip-2, chip-3 to 0.4` and `cue 4, 1.0 s: show` them; two `warning` icons, `cue 1,
1.5 s – end of scene: flash warn` and `cue 1, 1.5 s – end: flash warn-2 phase=0.5 low=0.3`.
`check-script`: `No problems found.` `stills` at title 3.2 s and B 2.2, 2.4, 2.55, 6.0 and
17.5 s, by eye: the sheet right; the two signs at different strengths in each of the three
close frames, out of step, the second never gone; the second sign plain again after cue 1 while
the first goes on; the prompt part typed at 6.0 s; the chips back at full strength in cue 4.

**README.** The moves' paragraph (percentages, a later cue, the scene's end, `linear`); `dim`
and `flash` in the actions table; a panel's times within the mistake cue; the CSV qualifiers
under Parameters; the checks; a dated note for users that names the one change (a panel's
`end`); the testing paragraph (560 tests) and this Tier 3.

**Also.** A third note in the training-video project's inbox
(`reply-from-video-tools-2026-10-11-3.md`): requests 18 and 19 built, the commit, the rules as
built, the five adjustments to request 19 and the change to a panel's `end`.

**Green.** `560 passed in 159.58s (0:02:39)`, 98%; `All checks passed!`.

**State.** Requests 1 to 19 built and pushed. Nothing in progress; the inbox is empty.

### 11 October 2026 — The twentieth request arrives; read and reported, not started

**What arrived.** `inbox/request-from-training-video-2026-10-11-20.md` (06:40): video-elements'
new `document` takes its page as one `text` parameter, a line a line, which a cast row cannot
write. It asks (1) that a `text` parameter's value naming a file under the video's folder be
read and handed over as the file's text, as `rows=` is read as CSV, with `check-script` saying
when a value looks like a path and is not a file; (2) `text.first=N` and `text.skip=N` to keep
or drop leading non-blank lines; (3) indexed parameters checked against the lines chosen.
Squirrel (07:03): "Check your inbox". Read and reported; **nothing done**; the item stays in
`inbox/`.

**Find, from reading.** PLAN.md item 15 has said since 10 October that "a value naming a file
under the video's folder (`assets/….csv`, `.txt`) is read by video-tools (CSV into rows, text as
it is) and handed to the element", and the code never did the second half: `perform._convert`
reads a file only for a parameter of type `rows`, and nothing checks a `text` value. No test
pinned it and no element needed it until `document`. So part 1 of the request is partly a gap
between PLAN.md and the code, not a new idea. Told to Squirrel.

**State.** 560 green as left, pushed. Waiting on Squirrel's OK for request 20.

### 11 October 2026 — The twentieth request is OK'd

**Decision.** Squirrel (07:05): "1. Yrs 2. Leave out. Go ahead"; (07:06): "That's 1. Yes". So
request 20 in full, with no `rows.skip`: PLAN.md item 22, "Settled" 41, the item moved to
`inbox/done/`.

**Find, before any test.** The index rule of item 15 counts every indexed parameter and anchor
against the data's rows, whatever it indexes. video-elements added `tab-box.N` to the
spreadsheet last night, and `document` has it too: `tab-box.4` on a three-row sheet with four
tabs would be refused, wrongly, and `frame.Video` refuses to draw a scene with a problem. With
lines counted too (this request) it gets likelier. The description does not say what an index
counts, so the mending is a stopgap, written into item 22 as part 4: a name beginning `tab` is
not counted against rows or lines.

**State.** 560 green as left. Next: item 22, `select_lines`, test first.

### 11 October 2026 — Item 22: a text parameter read from a file, and its lines chosen

**Goal.** Request 20: a `text` parameter's value that names a file is read; `text.skip` and
`text.first` choose its lines; indices are counted against the lines chosen. And item 22, 4: a
tab's index is not one of rows or lines.

**Tests.** Tier 1: `test_choreography_lines.py`, new, six tests (the pure `select_lines` and
`lines_of`; `text_file`); in `test_choreography_library.py`,
`test_a_text_file_is_checked_its_lines_chosen_and_indices_counted_against_them` (eleven cast
rows: a file with a skip; an index past the chosen lines, in the cast and in a move; a file
that is not there; the text itself with a qualifier; the wrong qualifier for a text and for a
data file; a skip that leaves nothing; a tab's index and a tab's anchor; rows winning over a
text; plain text with nothing to count against),
`test_a_member_is_handed_a_files_text_or_its_chosen_lines_and_never_the_qualifiers`,
`test_a_pieces_words_are_never_read_from_a_file_even_when_a_file_has_that_name`.

**Red.** `AttributeError: module 'videotools.choreography' has no attribute 'select_lines'`;
then `Parameters: 'text.skip=1' is not name=value` from the parser for the check and the
parameters (`2 failed, 16 deselected`).

**Green.** `5 passed in 0.02s`; `335 passed in 13.77s` (tier 1 and `test_perform.py`); suite
`568 passed in 148.68s (0:02:28)`, 98%, then one test more (`text_file`, below): `569 passed in 145.19s (0:02:25)`; `All checks passed!`.

**A fault I introduced and caught by reading, before it was committed.** Reading files for a
parameter of kind `text` also caught the pieces: `Performance._kind` called every piece
parameter that is not a number `text`, so a pill whose label happened to be a file's name
(`text=assets/plan.txt`) would have been drawn with the file's contents. Reproduced first
(`assert {'text': 'Sal…', …} == {'text': 'assets/plan.txt', …}`), then mended: a piece's
words are kind `word`, never `text`.

**Decision / surprise.** A value is a file when a file of that name is under the video's
folder, nothing more; `check-script` adds the guard the other way (a value with no spaces
ending `.txt` or `.md` and no such file). `_rows_file` now answers "what are this member's
indices counted against": its rows, or else its one text that names a file or has a qualifier,
with the unit in the message (`has 2 lines as chosen`, `the text has 1 line as chosen`). The
`tab` exemption is two guards (`NOT_COUNTED`), in the parameter check and the anchor check. The
invented `pot` gained a `text`, a `line-alpha.*`, a `tab-box.*` and a `tab.*` anchor; I first put
the anchor on the invented `table` and took it off again, because an existing test uses
`t.tab.2` as its example of an anchor a table does not have. One expectation changed on
purpose: the pot's list of anchors in a refusal now includes `tab.*`. Coverage showed
`text_file`'s guard (no folder; a value of more than a line) unreached: a test added, seen to
fail with the guard removed (`TypeError: expected str, bytes or os.PathLike object, not
NoneType`), the guard restored.

**Tier 3** (07:20, the scratch copy of the second video; nothing written in that project). Its
scene A with the `code` row taken out and three real `document`s from `assets/plan-v1.txt`: one
with `text.skip=1`, `title="Commission plan"` and `highlight.2` animated; one with the file as
it is; one with `text.skip=1 text.first=2 bullets=yes`. `check-script`: `No problems found.`
`stills` at 2.5 s, by eye: the first card under its tag with the four rules and the second
highlighted, the second card with "Sales commission plan" above them, the third with two
bulleted rules. With the file's name changed: `'whole': 'text' names assets/plan-v9.txt, which
is not under …/videos/app-for-that`. The real `document` has no `icon` parameter (my first row
gave it one, from the training-video project's request to video-elements; refused in the
library's words, as it should be).

**Also.** A fourth note in the training-video project's inbox
(`reply-from-video-tools-2026-10-11-4.md`).

**State.** Requests 1 to 20 built. Green, lint clean, pushed. Nothing in progress; the inbox is
empty.

### 11 October 2026 — A request to video-elements: what each index counts

**Decision.** Squirrel (07:18): "Yes, make the request". Written into video-elements' inbox as
`request-from-video-tools-2026-10-11.md` (PLAN.md "Settled" 42; this one file, no standing
permission to write there): for each indexed parameter and anchor, the description to say as
data what each `*` counts (a data row, a column, a line of a text, or something we cannot
count), and whether a `rows` parameter's first row is a header; with a table of the library's
indexed names today, what video-tools does with them at `8cc0302`, and what it will do with the
answer. It asks for the reply as a file in our inbox, in the words the README there will carry.

**Find, from making the table.** Reading every indexed name in the real library (read-only):
the stopgap of item 22, 4 covers the tabs and misses two more that count columns, the
spreadsheet's anchor `header.*` and its parameter `redact.*` (added to the library last night).
Checked against rows, `redact.5` on a sheet of six columns and four rows would be refused,
wrongly. Not mended: lengthening a list of another project's names in our code is the thing
the request is meant to end, and it was not asked. Said in the request, and to Squirrel.

**State.** 569 green as left; documents only. Waiting on video-elements' reply.

### 11 October 2026 — video-elements' reply arrives; read and reported, not started

**What arrived.** `inbox/reply-from-video-elements-2026-10-11.md` (07:29), to our request of
07:17: all three asks built in its `d203f0a`. A `## Indexes` table in each `ELEMENT.md`, read
into `el["counts"]`: a dict by pattern, one `{"what", "of"}` for each `*`, `what` one of `row`
(a data row of the `rows` parameter `of`, its header not counted), `column`, `line` (a
non-blank line of the text parameter `of`) or `other` (not for a caller to check; `of` None);
required for every indexed name, so the library refuses to open without it. And
`el["params"][rows]["header"]`: the name of the boolean parameter that says the first row is a
header, or None. It gives the words for the interface block, notes that our stub needs the
same, and three things we will meet: a row scrolled off a windowed sheet has no anchor; tabs
are `other` on purpose; `line` counts as we do. Checked read-only: three real elements have
`## Indexes` (`spreadsheet`, `document`, `range-bars`; `ledgers` per the reply), and the
spreadsheet's `rows` row reads `rows header=header`.

**Decision.** Squirrel (07:30): "Video-elements replied". Read and reported; **nothing done**;
the item stays in `inbox/`. Proposed to him: replace the count-against-rows rule and the `tab`
stopgap with one driven by `el["counts"]` (each index against the data rows, columns or lines
chosen for the member, `other` not checked, a second index checked as the first; a library
without `counts` not checked at all), put the two interface lines in PLAN.md, give the invented
library an `## Indexes` table. My question of 07:17 (lengthen the stopgap meanwhile) falls away.

**State.** 569 green as left, pushed. Waiting on Squirrel's OK for the reply.

### 11 October 2026 — video-elements' reply is OK'd

**Decision.** Squirrel (07:33): "Both yes go ahead": build on the reply as proposed, and reword
the draw-time refusal for an anchor a windowed sheet did not return. PLAN.md item 23 and
"Settled" 43; the reply moved to `inbox/done/`.

**State.** 569 green as left. Next: the invented library's `## Indexes`, then the rule, test
first.

### 11 October 2026 — Item 23: an index is counted as the element's description says

**Goal.** Replace "every first index against the file's rows" and the `tab` stopgap with a rule
read from `el["counts"]`: data rows (the header left out when the element has one), columns,
lines; `other` not checked; every index of a name, not only the first.

**Tests.** Tier 1 (`test_choreography_library.py`):
`test_each_index_is_counted_as_the_description_says_rows_columns_and_never_tabs` (parameters in
the cast and in a move, anchors; a second index past the columns);
`test_a_header_row_is_not_a_data_row_when_the_element_has_the_switch_and_it_is_on` (the switch
at its default, switched off in the cast row, and with rows chosen);
`test_with_a_library_that_does_not_say_what_an_index_counts_no_index_is_checked`. Tier 2:
`test_an_anchor_within_the_count_that_the_element_did_not_give_is_refused_saying_it_may_not_be_on_show`.
The invented library first: an `## Indexes` table on both elements read into `counts`, `rows
header=NAME`, row and cell anchors only for the rows on show; with that alone, `337 passed`,
nothing moved.

**Red.**

```
E   At index 0 diff: "line 26: scene A2, cast: 'u': 'highlight.5': assets/sample.csv has 4 rows" != "line 25: scene A2, cast: 't': 'cell-alpha.2.3': assets/sample.csv has 2 columns"
E   assert [] == ['line 25: sc...ws as chosen']
E   Left contains 3 more items, first extra item: "line 25: scene A2, cast: 't': 'highlight.9': assets/sample.csv has 4 rows"
E   assert "'row.3' of '...' in the cast" == "'sheet' did ...show has none"
4 failed, 66 deselected in 0.53s
```

**Green.** `341 passed in 14.22s` (tier 1 and `test_perform.py`); suite `573 passed in 151.33s
(0:02:31)`, 98%; `All checks passed!`.

**Decision / surprise.** `_rows_file` (one counted thing for a member) became `_data_of` (what
was read for it, by parameter: a rows parameter's chosen rows, a text parameter's chosen
lines), and `_index_trouble` walks a name's indices beside the description's words for them.
`NOT_COUNTED` and `_first_index` are gone. Two existing expectations changed on purpose, both
because the rule is now exact: `cell-alpha.2.9` on a file of two columns is a problem (a second
index was never looked at), and `line-alpha.7` on a one-line text written in the cast row is a
problem (a text with no file and no qualifier was not counted). The invented `table` has no
header switch, so its existing "has 4 rows" messages stand; the header rule is tested on a copy
of the library given one, as the real spreadsheet has. Coverage showed a `try` in
`_index_trouble` that could not fail (its callers have already found the element): removed
rather than left untested.

**Tier 3** (the scratch copy of the second video, against video-elements `d718dba`). The whole
described script as left last night: `No problems found.` under the new rule. Then scene B's
`reply` sheet (a header and three rows of two columns) given indices on purpose:

```
3 problems:
  - line 448: scene B, cast: 'reply': 'highlight.4': assets/sample-output-2024-04.csv has 3 data rows
  - line 448: scene B, cast: 'reply': 'redact.3': assets/sample-output-2024-04.csv has 2 columns
  - line 451: scene B, cast: 'past' is placed by 'reply'.'header.3', but assets/sample-output-2024-04.csv has 2 columns
```

and in the same run `redact.2`, `box.3.2`, `tab-box.2` and the anchor `cell.3.2` accepted. The
scratch script put back as it was.

**README, PLAN.md.** The cast's Parameters paragraph says what an index counts; a dated note
for users names the change (a row index counts data rows; `highlight.4` on a header and three
rows was accepted and is now a problem); the testing paragraph (573) and this Tier 3. PLAN.md
item 15's interface block has video-elements' two lines.

**Also.** A fifth note in the training-video project's inbox
(`reply-from-video-tools-2026-10-11-5.md`).

**State.** Item 23 complete. 573 green, 98%, lint clean, pushed. Nothing in progress; the inbox
is empty.

### 11 October 2026 — No older library

**Decision.** Squirrel (07:42): "No need to support older libraries". Item 23, 3 was the other
way (a library without `counts`: no index checked); rewritten, "Settled" 44.

**Test.** `test_a_library_that_does_not_say_what_an_index_counts_is_too_old_and_is_refused_when_opened`
(tier 1), in place of `test_with_a_library_that_does_not_say_what_an_index_counts_no_index_is_checked`,
which pinned the rule that is withdrawn: the same copy of the invented library, its table's
`## Indexes` taken out, must now fail to open, with the message, exit 3.

**Red.** `Failed: DID NOT RAISE Failure`.

**Green.** `341 passed in 14.22s` (tier 1 and `test_perform.py`); suite `573 passed in 163.38s
(0:02:43)`, 98%; `All checks passed!`.

**Decision / surprise.** "Not supported" still has to be a useful error, not a `KeyError`
(CLAUDE.md, non-negotiable 5), so `elements.open_library` checks once, after the library
opens, that every description has `counts`, and refuses naming the folder and the first
element without. With that, the three allowances are gone from the code: `el.get("counts")`,
and `el.get("fit")` in the blank-Size warning and in `Performance._natural` (item 17, 3's
allowance, withdrawn with it). `counts` is the newest key, so its presence stands for `fit`'s.
README: the note for users, the errors table, and yesterday's "an older library draws as
before" taken out. A sixth note to training-video corrects the fifth's sentence on this.

**State.** 573 green, 98%, lint clean, pushed. Nothing in progress; the inbox is empty.

### 17 October 2026 — Mail: audio-description-tools' request 1 arrives; planned, not started

**Goal.** Read the mail, report it, write the plan; build nothing (Squirrel: "Just tell me about
it, write the plan but don't start it yet").

**Decision / surprise.** The session's setup (CLAUDE.md, PLAN.md, the diary, `inbox/`) found
nothing new: `inbox/` is empty. Squirrel said there should be something; it was in a place none
of the guidance names: **`~/projects/mail/video-tools/new/`**, a mailbox of `lobster-mail`
(`~/projects/code/lobster-tools-code/lobster-tools/lobster-mail`, not on PATH; `lobster-mail start
--as video-tools` prints what waits and what to do). Every project under `~/projects` has one;
video-tools' was made 10 October and this is its first message. One message, from
`audio-description-tools` (a sibling project describing short YouTube videos for blind viewers):
request 1, `stills` to take a video file as well as a script, taking frames at given times, every
N seconds, or where the picture changes, writing one PNG a frame at the video's own size and a
`stills.txt`, and with `--sheet` a labelled contact sheet whose cells keep a vertical Short's
proportions. Squirrel's instruction to them is quoted in it: use and improve video-tools rather
than make their own. Planned as PLAN.md item 24, with the form settled our way (a first argument
not ending `.md` is a video; `--out` is then a folder; the script form untouched), the build
order's line 23, "Settled" 45, and three open questions: whether the Tier 3 check may use a real
video fetched by their tool into a scratch folder, whether video-tools may reply to them by mail
(replies into another project's inbox have been OK'd case by case), and whether CLAUDE.md should
name the mailbox at session start. The message is claimed (`lobster-mail ack`, `new/` to
`open/`), which the mail README defines as "read and reported"; it is not done until a reply is
sent. Nothing else moved or written: no test, no code, no `inbox/` change.

**State.** 573 green, 98%, lint clean as at the last entry (the suite was not run this session:
nothing in the code changed). Item 24 waits for Squirrel's go-ahead and the three answers.

### 17 October 2026 — Item 24 OK'd; the mail rules brought in; the venv rebuilt

**Decision / surprise.** Squirrel's answers (open questions 1 to 3, now "Settled" 46 to 48): the
Tier 3 check may use a real Short fetched by their tool into a scratch folder; a reply by mail
needs his OK each time; and the mailbox belongs in CLAUDE.md: "was that not part of the
coding-template setup used to create this folder??" It was, from 10 October; this folder was made
from the template on 9 October and never brought up to date, so the template needed no fix and
this CLAUDE.md gained non-negotiable 17, the "Mail" section and `.claude/settings.json` (the
`SessionStart` hook that runs `lobster-mail start`), with a dated note in its header. Then "go
ahead and build this request".

Two things found on the way. **Real ffmpeg 9.0.2's scene detection** was run on a scratch file of
three flat colours cut at 2 s and 4 s before any code depended on it: `select='gt(scene,0.3)',
metadata=print` with `-f null -` prints `frame:0 pts:25600 pts_time:2` and `lavfi.scene_score=
0.400000` per chosen frame on stderr, the first frame of the file never among them (recorded under
"Things checked"; item 24, 5 now names that form). **The venv was broken**: `.venv/bin/python3.12`
pointed at `~/projects/code/video-tools/.venv`, so the repository had been moved to
`~/projects/code/videos/video-tools` since 11 October; rebuilt with the README's install block
(python 3.12.14, same packages, `a1_coverage.pth` back for the subprocess coverage), tier 1
green on it before any new test.

### 17 October 2026 — Item 24, Tier 1: the times, the names, the grid, the scene report

**Goal.** The pure parts of `stills VIDEO`, in `videotools/video_stills.py`, one red-green cycle
a function, in `tests/tier1/test_video_stills.py`.

**Tests, red, green.** Each ran red with `AttributeError: module 'videotools.video_stills' has no
attribute '<name>'` (the module existed, empty: the right failure, the behaviour missing), then
green:
- `at_times_are_read_in_the_order_given_each_at_most_once` (`parse_at`: `"0,1.5,3"`, spaces,
  and five refusals in words, exit 2): `1 passed`.
- `every_n_seconds_runs_from_zero_while_less_than_the_length` (`every_times`: 7 s every 2 is
  0, 2, 4, 6; the end itself is not a frame; multiples not a running sum; 0 or less refused):
  `2 passed`.
- `a_still_is_named_by_its_time_so_names_sort_in_time_order` (`still_name`, `t0012.40.png`,
  `t12345.68.png`; `label` `12.40 s`; `listing_line`): `3 passed`.
- `the_default_grid_is_the_smallest_square_that_holds_the_frames_at_most_five_across`
  (`choose_grid`: 5 is 3x2, 26 is 5x6) and
  `a_cell_is_360_wide_and_as_tall_as_the_video_needs_plus_the_label_strip` (`cell_size`: 480×854
  is 360×676, 854×480 is 360×238): `5 passed`.
- `the_changes_are_the_first_frame_then_each_pts_time_of_ffmpegs_scene_report` (`change_times`
  on the shape ffmpeg printed; an empty report is the first frame alone; 0 not twice) and
  `the_threshold_is_a_number_from_0_to_1`: `7 passed in 0.34s`; `ruff`: `All checks passed!`.

**State.** Tier 1 of item 24 green; next the stub's fake media (width, height, scene changes,
the `metadata=print` report) and Tier 2.

### 17 October 2026 — Item 24, Tier 2: the video form, --at, --every, --changes, the refusals

**Goal.** `stills VIDEO …` end to end against the stubs, in `tests/tier2/test_video_stills.py`;
the command in `video_stills.run`, dispatched from `stills._run` when the first argument does not
end in `.md`.

**Tests, red, green.**
- `help_names_both_forms` and `at_writes_one_png_a_time_at_the_videos_own_size_and_lists_them`:
  red `assert (2, 'usage: s...ents: --at\n') == (0, '')` (argparse did not know `--at`: the flags
  missing, the right failure) and the usage line without the new flags. Green with the parser's
  video flags, the dispatch and the `--at` path: `18 passed` with `test_stills.py`, whose
  `help_and_usage` now expects the new usage line (`--out SHEET.png|FOLDER`, `SCRIPT|VIDEO`): a
  change of the help surface by design, item 24, 1, not a test bent to output. The stub's ffprobe
  now reports `width=`/`height=` from the fake media (default 1920×1080 as before).
- `every_takes_a_frame_every_n_seconds_from_zero_while_less_than_the_length` (8.342 s every 2:
  0, 2, 4, 6, 8) and `every_of_zero_or_less_is_refused_before_ffmpeg_runs`: red `(2, 'stills:
  ...as 0,1.5,3\n') == (0, '')` (the command insisted on `--at`); green `4 passed`.
- `changes_takes_the_first_frame_and_each_cut_ffmpeg_reports_with_the_threshold_as_data`: the
  stub gained the scene scan (`-vf …metadata=print`, printing the lines real ffmpeg printed for
  `scenes=2,4.04`; `FFSTUB_FAIL=scenes`); red the same `(2, …) == (0, '')`; green `12 passed` with
  `ffmpeg.scene_report` (`ffmpeg.run` gained `want_stderr`, since filters report on stderr) and
  the `-vf` value asserted as one argument, `select='gt(scene,0.3)',metadata=print`.
- `a_bad_choice_of_frames_is_refused_before_ffmpeg_runs` (eight cases: none, each pair,
  `--threshold` without `--changes` or out of range, a bad `--grid`, a bad `--at`) and
  `a_time_past_the_end_is_refused_naming_the_length_and_nothing_is_written`: seven red (`(0,
  't0000.00...', '') == (2, '', …)`: two modes ran as one; the wrong message for none); green
  `37 passed` with the mode check, `--threshold` defaulting to None so "given" can be told,
  `parse_grid` shared with the script form (its inline parse moved out, default `2x2` kept).

**Decision / surprise.** The past-the-end check was written with the `--at` path, before its
test: a slip against "no untested branches". Made good the way CLAUDE.md allows for code that
already exists: the check replaced by `if False:`, the test failed (`(0, 't0001.00...stills\n',
'') == (2, '', 'stil... (8.342 s)\n')`), restored, `1 passed`.

**State.** 37 stills tests green (tier 1 and 2); next the refusal to write over, the sheet, the
two forms' flags kept apart, no ffmpeg, a failing frame, odd names, missing Pillow.

### 17 October 2026 — Item 24, Tier 2: never written over, the sheet, the forms kept apart, odd names

**Tests, red, green.**
- `an_existing_still_or_listing_is_never_written_over_and_the_folder_is_left_as_it_was`: red
  `['ffprobe', '...be', 'ffmpeg'] == ['ffprobe', 'ffprobe']` (with `--changes`, `stills.txt` was
  checked only after the scan had run); green with the listing refused before the scan, `1
  passed`. Its first half (an existing still) had passed at once, since `refuse_existing` on the
  stills went in with `--at` (the same slip as the past-the-end check); the refusal removed, the
  test failed (`(0, 't0000.00...stills\n', '') == (3, '', 'stil...a new name\n')`), restored, `15
  passed`.
- `the_sheet_keeps_a_vertical_videos_proportions_in_360_wide_cells_with_the_label_under_each`,
  `a_landscape_video_gets_short_cells_and_a_given_grid_spreads_over_numbered_sheets`,
  `an_existing_sheet_is_refused_before_anything_is_read_or_written`, the five cases of
  `the_script_forms_flags_are_refused_with_a_video_file`, the five of
  `the_video_forms_flags_are_refused_with_a_script`, and
  `names_with_spaces_and_non_ascii_pass_through_as_data`: 14 red (`--sheet` ignored, the flags of
  one form accepted by the other). Green: `84 passed` across the stills, missing-package and
  check-video tests, with `Sheets` in `video_stills` (every sheet's name refused before a frame is
  read; each frame pasted as it is read, so no frame is held twice), `sheet.names` (moved from
  `stills.sheet_names`, now shared), the form checks in `stills._run`, and a `("stills",
  ["VIDEO", "--at", …], "PIL", "Pillow")` case in `test_missing_packages`.
- `without_ffmpeg_the_video_form_says_so_and_a_failing_frame_is_reported_with_what_stays` passed
  at once: both paths are `ffmpeg.require` and `ffmpeg.run`'s, which existed. Broken twice to
  prove it: the two `require` calls removed, the test failed on the message (`ffprobe is not on
  PATH` where `ffmpeg` is expected: probe's own check spoke first); a failing frame swallowed, it
  failed `(0 == 4)`; restored, `1 passed`.

**Decision / surprise.** The first sheet run failed on two pixels: the cell's height took the
floor of the frame's height at 360 wide (640 for 480×854), and `sheet.frame_size` then fitted
the frame to that height, 359 wide, leaving a white sliver. The width assertion caught it; the
fix is to round the cell's height up (641, 203), and the Tier 1 expectations of 676 and 238
were wrong by that one pixel and now say 677 and 239, with `sheet.frame_size` asserted to give
the full 360. A test changed because its expectation was wrong, not to match output.

Lint, as its own pass: three lines over 120 and an `os` import `stills.py` no longer uses; fixed,
`All checks passed!`. Then the command for real, with ffmpeg 9.0.2 on the invented three-colour
file of the morning's check: `--changes` found 2 s and 4 s, the stills are 160×90 in the file's
own colours, the sheet 720×478 with the times under the frames; `--every 2` and a time past the
end as the README now shows.

### 17 October 2026 — Item 24, Tier 3: the real Short

**Goal.** The video form against real ffmpeg on the file the request names ("Settled" 46).

**Done.** `fetch-video` from audio-description-tools fetched the Short into the session's
scratchpad (network use by their tool, out of git; nothing of it in a fixture). ffprobe: 480×854,
51 s. `./stills short/video.mp4 --every 5 --out every5 --sheet every5.png`: eleven lines
`t0000.00.png at 0.000 s` … `t0050.00.png at 50.000 s`, `Wrote 11 stills to every5 and the sheet
every5.png`; the stills 480×854, the sheet 1440×2031 (4×3 cells of 360×677), looked at: each frame
at its own proportions with its time in the strip under it, the twelfth cell white. `--changes
--out changes --sheet changes.png`: 14 stills (the first frame and 13 cuts, the last at 49.000 s),
`stills.txt` 14 lines, the sheet 1440×2708. Counts only here; the pictures stay in the scratchpad.

**State.** Item 24 built, in the README; the full suite's run is recorded in the next entry.

### 17 October 2026 — Item 24 done: the suite, lint, committed

**Green.** The full suite after the last change to code:

```
videotools/video_stills.py       143      0     54      0   100%
TOTAL                           4322     44   1726     50    98%
611 passed in 173.28s (0:02:53)
```

`ruff check .`: `All checks passed!` (its own pass, above). README: the `stills VIDEO …` section
with the real run, the errors table, "Notes for users", Tier 3, the count. PLAN.md build order 23
says done.

**State.** Items 1 to 24 built. Waiting on Squirrel: the reply to audio-description-tools, drafted
in the session's scratchpad and shown to him ("Settled" 47); on his OK it goes by `lobster-mail
reply` and the message moves to `done/`.

### 17 October 2026 — The reply to audio-description-tools sent

**Decision.** Squirrel (12:40): "Yes, send the reply to audio-description-tools as drafted and
mark the message done." `lobster-mail reply --as video-tools <id> reply.md`: `Replied
2026-10-17-1040-video-tools-re-request-1-stills-from-any-video-file to audio-description-tools`
(in their `new/`, a copy in our `sent/`); `lobster-mail done`: `open/ -> done/`. The reply names
commit `430a72f`, the exact commands on both machines, what was built and checked, and the one
thing not done (no score per cut; the threshold is the only tuning).

**State.** Items 1 to 24 built, pushed; the mailbox empty of open messages; `lobster-mail wait`
watching in the background. Nothing waits on Squirrel. No handover left yet: the session is open.

### 17 October 2026 — Mail: request 2 (a grid of 0x3 crashes); item 25, done

**Goal.** audio-description-tools' request 2 (10:45, claimed 12:50, OK'd 12:55): `stills VIDEO …
--grid 0x3` died with a `ZeroDivisionError` traceback, exit 1. Refuse it in words in both forms.

**Tests, red, green.**
- Tier 1 `a_grid_needs_two_whole_numbers_each_at_least_one` (`0x3`, `3x0`, `0x0`, `-1x2` refused
  as `--grid needs at least one column and one row`; `2x`, `x`, `3`, `2x2x2`, `axb` as before):
  red `Failed: DID NOT RAISE Failure`.
- Tier 2, two rows in `a_bad_choice_of_frames_is_refused_before_ffmpeg_runs`: red `(1, '',
  'Trac...lo by zero\n') == (2, '', …)` (the traceback the request reports, reproduced on the
  stub) and, for `--grid -1x2`, argparse's own `expected one argument`: a negative grid can only
  reach the command as `--grid=-1x2`, so the case is written that way (the test's form, not its
  expectation). `a_grid_with_no_columns_or_rows_is_refused_in_words_in_the_script_form_too`
  (`A:1` and `--cue-changes` with `0x3`): red `'stills: 1 frames do not fit a 0x3 grid; give a
  bigger --grid\n' != …` (in words already for frames given; `--cue-changes` would have crashed in
  the chunking).
- Green with two lines in `video_stills.parse_grid`, shared by both forms: `57 passed in 30.22s`
  (the three stills files); `ruff check .` `All checks passed!`.

**Decision / surprise.** A boundary the morning's coverage missed, for all its "empty, one item"
rule: the grid's zero. The script form had it too, behind `--cue-changes`, and would have shown a
`ValueError` from `range(0, n, 0)`; one parser for both closes both. README: the exit-2 row and a
note for users.

**Green, the suite.** `615 passed in 193.67s (0:03:13)`, `TOTAL … 98%`. For real on the invented
file: `stills: --grid needs at least one column and one row, not '0x3'`, exit 2, nothing made.

**State.** Items 1 to 25 built and pushed; the reply to request 2 drafted, waiting for Squirrel's OK.

### 17 October 2026 — The reply to request 2 sent

**Decision.** Squirrel (13:15): "Yes, send the reply to request 2 as drafted and mark the message
done." `lobster-mail reply`: `Replied 2026-10-17-1100-video-tools-re-request-2-stills-on-a-video-file-cras
to audio-description-tools`; `lobster-mail done`: `open/ -> done/`.

**State.** Items 1 to 25 built and pushed; nothing open in the mailbox; `lobster-mail wait` watching
in the background; nothing waits on Squirrel. No handover left: the session is open.

### 17 October 2026 — Mail: request 3 (speak a description table's lines); item 26 begun

**Decision / surprise.** audio-description-tools' request 3 (11:04, claimed 13:20): speak each line
of their timed Markdown table to its own clip, very fast, through `narrate`; and settle with
Squirrel the speed, the voice and whether the model is here. Proposed as a `--lines` form of
`narrate`; Squirrel (13:30): "Go ahead with request 3 as proposed: plan it, build it test-first,
and put the speed samples in _to_delete/ in this checkout." PLAN.md item 26, "Settled" 49.

Checked first, read-only: their two real tables (headers `| # | Start (s) | Words | Est. end (s) |
<one column that differs> | Checked against | Line |`, 12 and 14 rows; nothing copied). And the
model's speed: a first reading of kokoro-onnx's source saw only the rounding in `_speed_value` and
PLAN.md said "no limit"; the sample run at 2.5 then raised `ValueError: Speed should be between 0.5
and 2.0, got 2.5` from `_prepare`. PLAN.md corrected ("Things checked"): 2.0 is the fastest, and
`--lines` refuses a speed outside 0.5 to 2.0 before loading the model. **Samples** in
`_to_delete/speed-samples/` (ignored by git), an invented 15-word line: `af_heart` at 1.0 (4.69 s,
3.4 words/s), 1.5 (2.98 s, 5.4), 2.0 (2.62 s, 6.1); `am_michael`, `bf_emma`, `bm_george` at 2.0
(6.0, 6.4, 5.8 words/s); the model's voices are those four. Their scripts assume 5 words a second,
which is about speed 1.5.

**Tier 1, `videotools/lines.py`, `tests/tier1/test_lines.py`.**
- `the_columns_are_found_by_header_in_any_order_and_the_rest_ignored`: red `AttributeError: module
  'videotools.lines' has no attribute 'parse'`; a first implementation still failed its own
  "no table" fallback because the separator-row regex did not match `|---|---|` (a trailing `|`
  doubled); replaced by `is_separator` (pipes, dashes, colons, spaces, at least one dash); green `1
  passed`. An escaped `\|` in a cell is a pipe.
- `a_table_that_cannot_be_spoken_is_refused_in_words` (eleven cases): ten red (no refusal yet;
  the "no table at all" case passed at once, being increment 1's fallback); green `12 passed` with
  the missing columns named, each row checked in order (cell count, `#`, twice, start, negative,
  empty line) and an empty table refused.
- `clips_are_named_by_number_with_as_many_digits_as_the_largest_needs`,
  `a_line_that_runs_past_the_next_lines_start_is_warned_about_naming_both`,
  `the_estimate_scales_the_words_a_second_by_the_speed`,
  `the_speed_must_be_within_what_the_model_accepts`: four red (`AttributeError` each); green `16
  passed` once the message wrote "2.0" rather than `:g`'s "2" (the test's wording kept: it matches
  the model's own).

**Tier 2, `tests/tier2/test_narrate_lines.py`**, against the stub speech model and an invented
three-line table (`TABLE` in the file: a kite, a harbour, gulls; nothing from theirs).
- `each_line_becomes_a_clip_named_by_its_number_with_timing_json`: red `(2, 'usage: n...')` (no
  `--lines`); green `24 passed` with `test_narrate.py`, by `narrate._run_lines` reusing
  `_model_dir`, `_load_model`, `trim` and the refusal/replace shape of the script form, and
  `lines.read`.
- Nine more tests at once: six red (`--dry-run` ignored, no overrun warning, the two forms'
  flags accepted across, `--out` without `--lines`); green `38 passed`. The other three
  (`existing_clips_are_refused…`, the table/missing-file refusal, the voice flag and default, the
  model failure, and four rows of the kept-apart table) passed at once: the base run had carried
  those branches over from the script form untested. Each was broken in turn in the `--lines` copy
  only (the script form has the same text) and its test failed: replace refusal, `--out` missing,
  `--speed` missing, no arguments, a missing table file, the af_heart default, exit 4 on a model
  failure; `15 passed` restored.

**Decision / surprise.** Squirrel, 14:05, after listening to `_to_delete/speed-samples/`: "2x speed
is too fast, 1.5 is probably good. Make that the default and include it in your reply. af_heart is
fine, also make it default and include in reply." So `--speed` is no longer required with `--lines`:
the missing-speed row left the kept-apart table and `the_voice_flag_wins…` asserts a run without
`--speed` records 1.5 (red `assert 2 == 0`, the command still demanding it); `LINES_SPEED = 1.5` in
`narrate.py`; PLAN.md item 26, 2 and "Settled" 50; the README. af_heart was already the default.

### 17 October 2026 — Item 26, Tier 3: the real model

**Done.** Lint as its own pass (four long lines wrapped; `All checks passed!`). Then the command for
real with Kokoro on an invented three-line table in the scratchpad: `--dry-run` lists the three
lines at 1.5 with estimates 1.8, 1.3 and 1.0 s; the run writes clips of 1.244, 1.283 and 0.748 s and
warns `line 2 (at 4.00 s, 1.28 s long) runs 0.28 s into line 3 (at 5.00 s)`; `timing.json` as
specified (pasted into the README). The estimate runs long for short lines: the model is quicker
than 2.6 × 1.5 words a second on them; said in the README, not changed (the real length is what
counts). Then a scratch copy of their first real table (read-only on the original; counts only):
14 clips, 31.4 s of speech, the longest clip 3.409 s, no overrun warning; nothing of it kept.

**Green, the suite.** `645 passed in 175.79s (0:02:55)`, `TOTAL … 98%`; `ruff check .` clean.

**State.** Items 1 to 26 built, pushed; the reply to request 3 drafted, waiting for Squirrel's OK.

### 17 October 2026 — The reply to request 3 sent

**Decision.** Squirrel (14:40): "Send it". `lobster-mail reply`: `Replied
2026-10-17-1129-video-tools-re-request-3-narrate-a-description-scrip to audio-description-tools`;
`lobster-mail done`: `open/ -> done/`. The reply names commit `2f4148a`, the command on both
machines, the defaults he chose (1.5, af_heart) and why, where the samples are, and what was checked.

**State.** Items 1 to 26 built and pushed; nothing open in the mailbox; `lobster-mail wait` watching
in the background; nothing waits on Squirrel. No handover left: the session is open. `_to_delete/`
is now in `.git/info/exclude` here (it had not been, since the move).

### 17 October 2026 — Session end: handover

**Decision.** Squirrel (15:25): "Stop and write up handover". The background `lobster-mail wait`
stopped (the mailbox had been quiet since 11:04; three waits of 25 minutes returned empty).
"Where things stand" brought up to date, committed and pushed; then `lobster-mail handover --as
video-tools --session mac -` with where things stopped, what waits (nothing) and what to do next,
which also gives up the duty.

**State.** Items 1 to 26 built, 645 tests, 98%, lint clean, pushed. Nothing waits on Squirrel. Next
session: `lobster-mail start` (the hook), CLAUDE.md, PLAN.md items 15 to 26, this section, `inbox/`.
Two small things a session might tidy with his OK: CLAUDE.md and the README still name the old
path `~/projects/code/video-tools` (the folder is now under `videos/`), and the README's example for
`narrate --lines` shows the estimate running long for short lines.

### 17 October 2026 — Session resumed; the two tidies

**Decision.** `lobster-mail start` (the hook, 16:01) claimed and closed the 15:30 handover; nothing
new or open in the mailbox, `inbox/` empty, tree clean at `e45b093`. `lobster-mail wait --as
video-tools --session mac` watching in the background; `duty status` says `on duty mac since
2026-10-17T16:02:03Z`. Squirrel (17:00): "Fix the path in CLAUDE.md and the README, and delete
_to_delete/speed-samples/." CLAUDE.md's "Definition of done" `cd` line and the README's
`voices.npz` example now say `~/projects/code/videos/video-tools`; no other live mention of the
old path (the log's past entries keep it, as they should). `_to_delete/speed-samples/` (six WAVs
and a README, excluded from git) removed with `rm -r`; `_to_delete/` itself is left, empty but
for a `.DS_Store`. No behaviour changed, so no test.

**State.** Items 1 to 26 built, 645 tests, 98%, lint clean. The README's `narrate --lines` example
still shows the estimate running long for short lines (the other tidy the handover named), not
raised with Squirrel yet.

### 17 October 2026 — Request 4 arrived by mail; proposed, OK'd, item 27

**Decision.** `lobster-mail wait` returned at 18:15 with audio-description-tools' request 4 (id
`2026-10-17-1715-audio-description-tools-request-4-a-setup-linux-command-for-the`, sent 17:15):
a `setup-linux --venv DIR --model DIR --conf FILE [--dry-run]` command for the device shell, the
venv, the packages, the model check, the config and the three environment lines, to be called by
their `setup-device`. Claimed with `ack`, reported with a proposal (two departures from the ask:
only `SPEECH_MODEL_DIR` written into the config; the wrapper on the system `python3` with no venv
bootstrap, since it makes that venv). Squirrel (18:30): "go ahead". Written as PLAN.md item 27 and
"Settled" 51. While it was being built the watch returned again with **request 5** (id
`2026-10-17-1726-audio-description-tools-request-5-stills-changes-fast-enough-for`, sent 17:26):
`stills --changes` on a 35-minute 60 fps video takes longer than the device shell's three-minute
call (4 s of wall time per 30 s of video); they ask for the scene detection to decode fewer frames
and/or a `--from T --until T` window so a long video goes in slices into one `--out` folder.
Claimed with `ack` (in `open/`), reported, nothing done on it: it waits for Squirrel.

### 17 October 2026 — setup-linux: help and usage

**Test.** `test_help_and_usage`: `--help` exits 0 with `usage: setup-linux [-h] --venv DIR --model
DIR --conf FILE [--dry-run]`; no arguments exits 2 naming the three required flags.

**Red.** No command yet, so Python cannot open it:
```
>       assert code == 0 and " ".join(out.split()).startswith(
E       assert (2 == 0)
```
**Green.** `1 passed in 0.22s`, with the wrapper `setup-linux` (standard library, no bootstrap) and
`videotools/setup_linux.py` holding only the parser.

### 17 October 2026 — setup-linux: a venv inside the checkout refused

**Test.** `test_a_venv_inside_the_checkout_is_refused_in_words_before_anything_runs`: the checkout
itself, a folder in it and a deeper one, each exit 2 with the one-line message, nothing made.

**Red.** `AssertionError: assert (0, '') == (2, '')` (no refusal). **Green.** `2 passed in 0.60s`.

### 17 October 2026 — setup-linux: the venv made, the packages installed, the three lines

**Test.** `test_makes_the_venv_installs_the_packages_and_prints_the_three_lines`, against the new
stub `tests/stubs/pystub.py` (a `python3` on PATH that records every call, makes a fake venv on
`-m venv`, answers `-c "import …"` from a marker that `-m pip install` writes): the three calls
exactly, stdout the three `export` lines alone, the three progress lines on stderr, exit 0.

**Red.** `AssertionError: assert [] == [['/private/v...'numpy', ...]]` (nothing run).
**Green.** `3 passed in 1.58s`.

### 17 October 2026 — setup-linux: a second run runs only the import check

**Test.** `test_a_second_run_finds_the_venv_the_packages_and_the_config_and_runs_only_the_import_check`:
after one run, a second adds one call (the import check), prints the lines, says nothing on
stderr and leaves the config's content and mtime alone.

**Red.** `At index 2 diff: 'setup-linux: wrote …/video-tools.conf\n' != ''` (the config was rewritten
every run). **Green.** `4 passed in 3.58s`: the config is read through `config.read` and left alone
when its `SPEECH_MODEL_DIR` is the model folder; on a rewrite only that line is replaced, or added
at the end.

### 17 October 2026 — setup-linux: the config's edge cases

**Tests.** `test_a_config_naming_another_model_is_rewritten_with_its_other_lines_kept` (a comment,
`VOICE`, a quoted old value with a trailing comment, `SPEED`: only the model line changes),
`test_a_config_without_the_setting_gains_it_at_the_end` (no final newline),
`test_the_config_folder_is_made_when_it_is_missing`,
`test_a_config_that_cannot_be_read_is_refused_in_words_and_left_alone` (exit 3, the reader's own
line-numbered problem under the message).

**Red.** The folder and the unreadable config: `assert (1 == 0)` and `assert (1, '') == (3, '')`, a
traceback each (`FileNotFoundError`, `ConfigError`). **The other two passed at once**: the rewrite
came in with the previous cycle. Proven by breaking the rewrite into a plain overwrite on purpose:
```
E       AssertionError: assert 'SPEECH_MODEL...r_m0/kokoro\n' == '# this machi...\nSPEED=1.0\n'
E         - # this machine
E         - VOICE=bm_george
E           SPEECH_MODEL_DIR=/private/var/…/kokoro
E         - SPEED=1.0
E       AssertionError: assert 'SPEECH_MODEL...ett0/kokoro\n' == 'VOICE=bm_geo...ett0/kokoro\n'
```
then restored: `2 passed`. **Green.** `8 passed in 6.42s` (the folder made with `os.makedirs`, a
`ConfigError` reported as a `Failure`).

### 17 October 2026 — setup-linux: the model check

**Tests.** `test_a_model_folder_without_the_files_is_reported_file_by_file_after_the_venv_is_made_exit_3`
(both files named, the venv, packages and config done first, stdout empty),
`test_one_missing_model_file_is_the_one_named`, `test_a_model_folder_that_does_not_exist_is_one_message`.

**Red.** All three `AssertionError: assert (0, 'export V...BYTECODE=1\n') == (3, '')` (the lines
printed with no model). **Green.** `11 passed in 9.10s`.

### 17 October 2026 — setup-linux: --dry-run

**Tests.** `test_dry_run_with_nothing_in_place_says_what_it_would_do_and_runs_makes_and_writes_nothing`,
`test_dry_run_with_everything_in_place_runs_only_the_import_check_and_prints_the_lines`,
`test_dry_run_with_the_venv_but_not_the_packages_would_install_and_installs_nothing`,
`test_dry_run_with_the_model_missing_reports_it_after_what_it_would_do_exit_3`.

**Red.** Three failed, the flag being ignored: `'setup-linux: made the venv at …' != ''`,
`'setup-linux: installed … into …' != ''`, `assert '' == 'Would make t..._mi0/kokoro\n'`. The
everything-in-place one passed at once (a dry run there does what a real run does); proven after
the implementation by making a dry run skip the import check on purpose:
```
E       AssertionError: assert (0, 'Would in...CODE=1\n', '') == (0, 'export V...CODE=1\n', '')
E         At index 1 diff: 'Would install pycairo numpy … into …/work/venv\nexport VIDEO_TOOLS_PYTHON=…
```
then restored: `1 passed`.

**Decision / surprise.** The first implementation skipped the import check whenever the venv had
just been made, in real runs too; the happy-path and model tests caught it at once (`At index 1
diff: [… '-m', 'pip', 'install', …] != [… '-c', 'import cairo, …']`, `assert (2 == 3)`). With
`--system-site-packages` a fresh venv may already import everything, so the check stays; it is
skipped only when a dry run has no venv to ask. **Green.** `15 passed in 11.70s`.

### 17 October 2026 — setup-linux: failures, no python3, quoting

**Tests.** `test_a_failing_venv_is_reported_in_words_with_its_last_lines_exit_3_and_nothing_else_runs`,
`test_a_failing_pip_is_reported_in_words_with_its_last_lines_exit_3_and_the_venv_kept`,
`test_no_python3_on_path_is_reported_in_words_exit_3_and_nothing_runs`,
`test_with_python3_on_path_but_the_venv_in_place_no_python3_is_needed`,
`test_paths_with_spaces_and_non_ascii_are_quoted_for_the_shell` (`wörk space`, `vidéo tools.conf`:
the two paths single-quoted in the lines, made and written as given).

**Red.** The failures: `assert (1, '') == (3, '')` (a traceback after the ignored `venv` failure),
`assert (0, 'export V...') == (3, '')` (the `pip` failure ignored), `assert (1, '') == (3, '')`
(`None` handed to subprocess). The other two passed at once (`shlex.quote` and the early return
came in with the first cycle). Proven by breaking each on purpose: without quoting,
```
E         - export VIDEO_TOOLS_PYTHON='/private/var/…/wörk space/venv/bin/python'
```
and with `python3` looked for before the venv is checked,
```
E       AssertionError: assert (3, '', 'setu...it on PATH\n') == (0, 'export V...CODE=1\n', '')
```
then restored: `2 passed`. **Green.** `20 passed in 15.18s`: `run_or_fail` reports a non-zero step
with the program's last five lines and advice; `shutil.which("python3")` is asked only when the
venv must be made.

### 17 October 2026 — setup-linux: README, lint, the whole suite

**Decision.** README: "Running from the Linux device shell" now leads with `eval "$(./setup-linux
…)"` and says what it does; a usage section before "Configuration" with a dry run's real output
(paths shortened); codes 2 and 3 in the errors table; a "Notes for users" line. `tests/stubs/README.md`
describes `pystub.py`. Real runs on this Mac, read-only: `--help`; `--dry-run` with the scratchpad
venv and config and the real `~/models/kokoro` printed the three `Would` lines and the three
`export` lines, exit 0, and made nothing; the same with a missing model folder exit 3; `--venv
./linux-venv` refused, exit 2.

**Lint**, its own pass: three `UP032` (`.format` calls) in `tests/stubs/pystub.py`, fixed with
`ruff --fix`; `All checks passed!`; the 20 `setup-linux` tests run again after it: `20 passed`.

**Green.**
```
videotools/setup_linux.py        115      0     38      0   100%
TOTAL                           4588     44   1828     52    99%
======================= 665 passed in 192.04s (0:03:12) ========================
```

**State.** Items 1 to 27 built, 665 tests, 99%, lint clean. The reply to request 4 and a
proposal for request 5 wait on Squirrel. The Tier 3 run of `setup-linux` in the real device shell
is not done.

### 17 October 2026 — The reply to request 4 sent

**Decision.** Squirrel (19:30): "reply on request 4 and describe plan for req 5". `lobster-mail
reply`: `Replied 2026-10-17-1733-video-tools-re-request-4-a-setup-linux-command-for-t to
audio-description-tools`; `lobster-mail done`: `open/ -> done/`. The reply names commit `f9f47d0`,
the exact device-shell invocation, what each step does, the two departures from the ask (only
`SPEECH_MODEL_DIR` written; progress on stderr so stdout is the three lines alone), what was
checked, and that no real device-shell run has happened yet (the first `setup-device` that calls
it is that check).

**State.** Items 1 to 27 built and replied to; request 5 open in the mailbox, its plan described
in chat and waiting on Squirrel.

### 17 October 2026 — Request 5 OK'd as item 28; real ffmpeg checked first

**Decision.** Squirrel (19:45): "Go ahead with request 5 as described: write it into PLAN.md as item
28, check real ffmpeg first, then build part 1 (the detection at 10 fps) and part 2 (the
--from/--until window) test-first." Item 28, "Settled" 52 and a "Things checked" entry written.

**Decision / surprise.** The checks, on scratch lavfi files in the session's scratchpad (ffmpeg
9.0.2): with `fps=10,` in front of the `select` a cut at 4.04 s is reported at `pts_time:4.1`,
the first sampled frame after it; a seek before `-i` restarts the times at 0 unless `-copyts` is
given; `-to` before `-i` is a position in the file, not a length; a slice's first frame is not
reported as a change. **But the rate buys little:** on a 60 s 480p60 h264 file the plain scan took
0.63 s and `fps=10` 0.48 s, a bare decode 0.45 s, so the decode is the cost and `fps=` drops frames
after it; on VP9, 0.70 s either way; `-an` took 0.48 to 0.46. Two dead ends: `-skip_frame nonref`
is not a value in ffmpeg 9 (its 0.05 s "run" was an error exit, found by counting frames out),
and `-skip_frame bidir` was no faster. The valid `-skip_frame noref` took the h264 scan from 0.49
to 0.35 s and found the same cuts on a file whose cuts fall on P and B frames; it changes which
frames are scored, so it is an "Open question", not built. Part 2 is what makes a long video
possible; the reply will say so with the numbers. Also: a red-to-green cut between lavfi `color`
sources scored 0 at every threshold (frames are red and green; not understood, not needed);
white, black and red score 1.0 and 0.65.

### 17 October 2026 — Item 28, part 1: the scan at 10 fps with the audio skipped

**Test.** `test_the_scan_samples_at_10_fps_and_skips_the_audio_and_the_frame_reads_do_not`: the
scan's `-vf` is `fps=10,select='gt(scene,0.3)',metadata=print`, `-an` after `-i`, no seek flags;
the frame reads have none of it.

**Red.**
```
E       assert "select='gt(s...etadata=print" == 'fps=10,selec...etadata=print'
E         - fps=10,select='gt(scene,0.3)',metadata=print
E         + select='gt(scene,0.3)',metadata=print
```
**Green.** `33 passed in 13.11s`. **The item-24 test
`test_changes_takes_the_first_frame_and_each_cut_ffmpeg_reports_with_the_threshold_as_data`
pinned the old filter exactly; its two assertions now say `fps=10,select=…`**, since item 28
changes what the scan is given (a test changed to match a specified change, not an unpredicted
output).

### 17 October 2026 — Item 28, part 1: --detect-fps

**Test.** `test_detect_fps_sets_the_scans_rate_as_data_and_is_refused_when_not_a_rate_or_without_changes`:
`--detect-fps 5` gives `fps=5,select=…`; `0`, `-2`, `x` and `--every 2 --detect-fps 5` are refused
in words, exit 2, running nothing.

**Red.** `AssertionError: assert (2, 'usage: s...detect-fps\n') == (0, '')` (argparse: an unknown
flag). **Green.** `42 passed in 14.97s`, after two test corrections of my own: the help test pins the
usage line, which now has `[--detect-fps N]` (updated to the new surface); and my test counted the
stub's calls as 2 where the first run makes 5 (the probe, the scan, three frames) and the refusals
add none: `assert (5 == 2)`, the test's arithmetic, not the code.

### 17 October 2026 — Item 28, part 2: the window's arithmetic (Tier 1)

**Tests.** `test_every_times_step_from_a_start_while_less_than_the_end` (3, 5, 7 from 3 on 8.342;
multiples from the start, no drift), `test_a_window_is_from_and_until_in_seconds_with_until_held_to_the_length`
(absent flags are 0 and the length; `--until 100` on 8.342 is 8.342),
`test_a_bad_window_is_refused_in_words` (not a number, negative, `--from` at or past the end naming
the length, `--until` not after `--from`; exit 2 each).

**Red.** `TypeError: every_times() takes 2 positional arguments but 3 were given`;
`AttributeError: module 'videotools.video_stills' has no attribute 'parse_window'`.
**Green.** `18 passed in 0.04s` (`every_times(step, length, start=0.0)`, `parse_time`, `parse_window`).

### 17 October 2026 — Item 28, part 2: --from and --until on the command

**Tests.** `test_every_with_a_window_steps_from_the_start_while_less_than_until` (`--every 2 --from 3
--until 7`: 3 and 5, read at 3.000 and 5.000), `test_changes_with_a_window_seeks_the_scan_on_the_files_clock_and_lists_no_first_frame`
(the scan has `-ss 3.000 -to 8.342 -copyts` before `-i`, `-an`, the filter; the cut at 2 is outside;
no first frame; `--from 0 --until 3` has it). The stub's scan now reads a seek before `-i` and
serves only the fake's cuts in the window, on the file's clock only with `-copyts`.

**Red.** Both `AssertionError: assert (2, 'usage: s... --until 7\n') == (0, '')` (unknown flags).
**Green.** `54 passed in 16.91s`; the help test's usage line gains `[--from T] [--until T]`.

### 17 October 2026 — Item 28, part 2: slices, the listing a line at a time, the sheet of a folder, refusals

**Tests.** `test_two_slices_into_one_folder_give_what_one_whole_run_gives_for_changes_and_for_every`,
`test_a_slice_refuses_a_still_already_there_and_a_whole_run_refuses_an_existing_listing`,
`test_the_listing_is_written_a_line_at_a_time_so_a_run_that_dies_leaves_what_it_wrote_listed` (the
stub's new `FFSTUB_FAIL=frame@3.000` fails one chosen frame), `test_sheet_alone_draws_the_folders_listing_in_its_order_reading_nothing_from_the_video`,
`test_sheet_alone_refuses_a_missing_listing_or_still_or_a_bad_line_in_words` (three cases),
`test_a_bad_window_on_the_command_is_refused_before_ffmpeg_runs` (four), `test_a_window_past_the_end_is_refused_naming_the_length_after_the_probe_only`,
`test_the_script_form_refuses_the_window_flags`.

**Red.** Each for its own reason: the second slice `assert (3, 'stills: ...a new name\n') == (0, '')`
(refused on `stills.txt`); the slice over a still refused on the listing instead of the still; after
the failed third frame `['t0000.00.pn...t0001.00.png'] == ['stills.txt'...]` (no listing); `--sheet`
alone and its refusals met `choose how to pick the frames…`; `--at` with a window ran (`0 != 2`); a
bad `--from` was parsed only after the probe (`[{'ffprobe': …}] == []`).

**Green.** `67 passed in 49.68s`, after two mistakes in my tests: the sheet's strip is 36 px
(`sheet.STRIP`), not the 28 I wrote (`(1080, 677) == (1080, 669)`), and my `--every 3` slices
overlapped at 3 s (`[0, 4)` then `[3, …)`), so the second was rightly refused (`assert 3 == 0`);
the first slice now ends at 3. Both are the tests' errors, not the code's.

**Decision.** The listing is written with one `open(…, "a")` per still (PLAN.md item 28, 6); the
sheet of a folder reads the PNGs' size from the first still and never probes the video, so it needs
Pillow but not ffmpeg; `Wrote 1 still` is singular now (was `1 stills`).

### 17 October 2026 — Item 28: an empty listing, the README, the whole suite

**Test.** `test_sheet_alone_still_needs_the_video_file_to_exist` pinned the one line coverage
showed unreached; proving it by removing the check showed a **traceback, `division by zero`**, for
an empty `stills.txt` with the video present: `Sheets` with no stills. So
`test_sheet_alone_refuses_an_empty_listing_in_words`, **red** `assert (1, '', 'Trac...lo by zero\n')
== (3, '', 'stil...ng to draw\n')`, **green** `6 passed` with the refusal `… lists no stills; there is
nothing to draw`. The first full run had one failure: `tests/tier2/test_stills.py::test_help_and_usage`
pins the usage line too (updated to the new surface, as the video form's was).

**Tier 3** on the Mac, real ffmpeg 9.0.2, scratch files in the scratchpad: `nokey.mp4` (160×90,
60 fps, cuts at 2 and 4.04 s on P and B frames) whole: `t0000.00`, `t0002.00`, `t0004.10`; in
slices `--until 3` then `--from 3`, then `--sheet` alone: the same three, `stills.txt` identical,
the PNGs identical by md5, `Drew 3 stills from … on the sheet …`; `--every 4` in slices `--until 6`
and `--from 6 --until 999`: 0, 4, 6, 10; a slice over an existing still refused. On the 60 s
480p60 h264 file the scan by hand as before (`select` alone) took 0.619 s and the whole command
0.653 s (the probe, the scan at 10 fps and one frame read); in two slices 0.415 and 0.353 s.

**Lint**, its own pass: `All checks passed!`. **Green.**
```
videotools/video_stills.py       228      0     94      0   100%
TOTAL                           4675     44   1866     52    99%
======================= 694 passed in 195.10s (0:03:15) ========================
```
**State.** Items 1 to 28 built; the reply to request 5 waits on Squirrel's OK; `-skip_frame noref`
is an open question. No real device-shell run of either item 27 or 28.

### 17 October 2026 — The reply to request 5 sent

**Decision.** Squirrel (21:50): "Write and send the reply to audio-description-tools' request 5,
with the measurements, and close the message." `lobster-mail reply`: `Replied
2026-10-17-1800-video-tools-re-request-5-stills-changes-fast-enough to audio-description-tools`;
`lobster-mail done`: `open/ -> done/`. The reply names commit `da5e125`, says plainly that the
10 fps scoring saves about a quarter on h264 and nothing on VP9 and why, that the window is what
fits a long video into their three-minute call, gives the slice invocations and the joining rules,
the `stills.txt` line-at-a-time change (the cause of their 66 stills with no listing), `--sheet`
alone, what was checked, and asks for the `time` of a slice of their 33-minute video in the device
shell, which decides whether `-skip_frame noref` is worth trying.

**State.** Items 1 to 28 built and replied to; nothing open in the mailbox; nothing waits on Squirrel.

### 17 October 2026 — audio-description-tools' timing from the device shell; the open question settled

**Decision.** The watch returned at 22:05 with their answer to request 5 (id
`2026-10-17-1808-…-the-slice-timing-from-the-d`): on their 33-minute 480p 60 fps h264 file in the
device shell (ffmpeg 4.4.2, at `10dcf63`), `--changes --from 0 --until 600` took 15.6 s (93 cuts),
`--from 600 --until 1200` into the same folder 21.4 s (132 cuts, 225 in all), where the old whole
run took 86 s for 398 cuts; the slices joined with nothing refused; their tightest step is
`--every 2` on the whole video at 166 s, now also run in windows; "the reference-frames-only decode
is not needed for these files; nothing more asked". Reported; Squirrel (22:10): "ok". Closed with
`lobster-mail done` (`open/ -> done/`); the "Open questions" entry on `-skip_frame noref` moved to
"Settled" 53, left out. No reply needed, none sent.

**State.** Items 1 to 28 built and replied to; the mailbox has nothing open; nothing waits on
Squirrel.

### 17 October 2026 — Request 6 arrived; OK'd as item 29

**Decision.** The watch returned at 22:15 with audio-description-tools' request 6 (id
`2026-10-17-1820-audio-description-tools-request-6-stills-to-write-each-still-ato`): a slice killed
between a still and its line left an unlisted still, which the next slice made again and was
refused on. Reported with a proposal (part name, line, rename; an unlisted still written over and
said; a part file silently; a listed still refused). Squirrel (22:25): "Go ahead with request 6 as
proposed: write it into PLAN.md as item 29 and build it test-first." Item 29 and "Settled" 54.

### 17 October 2026 — Item 29: the order of writing a still (Tier 1)

**Tests.** `test_a_still_is_saved_to_a_part_name_listed_and_only_then_renamed` (a stand-in image
records the path it saves to: `.t0001.00.png.part`; afterwards the folder holds `t0001.00.png`
and the listing its line) and `test_a_still_is_not_renamed_when_its_line_cannot_be_written` (the
listing a directory: `OSError`, and the folder holds the part file, no named still).

**Red.** `AttributeError: module 'videotools.video_stills' has no attribute 'write_still'` (both).
**Green.** With Tier 2 below, `90 passed in 38.32s`.

### 17 October 2026 — Item 29: a folder as a kill leaves it (Tier 2)

**Tests.** `test_a_folder_as_a_kill_leaves_it_is_finished_by_the_next_window_with_files_and_listing_agreeing`
(a listing of one, an unlisted still, a part file; `--changes --from 2`: exit 0, the one stderr
line, both written over with the stub's frames, no part file, the listing of three; `--sheet`
alone then draws three) and `test_a_listed_still_is_refused_before_anything_is_read_even_beside_a_part_file`.

**Red.** The first: `assert (3 == 0)` (the unlisted still refused). The second passed at once (an
existing still was refused whatever the listing said); proven after the code by making a window
skip the listing check: `assert (0, 't0000.00...tten again\n') == (3, '', 'stil...a new name\n')`,
then restored, `2 passed`.

**Decision / surprise.** Two. PIL cannot tell the format from `.part`: the first green run was a
traceback, `unknown file extension: .part`; the part file is saved with `format="PNG"`. And the
item 24 test `test_an_existing_still_or_listing_is_never_written_over_and_the_folder_is_left_as_it_was`
failed (`assert (0, 't0000.00...tten again\n') == (3, …)`): my item 29 text let an unlisted still be
written over in a whole run too, where there is no kill to carry on from. The test is right; item
29, 2 now says the overwrite is in a window only, and without a window any existing still is
refused as item 24 says. **Green.** `90 passed in 38.32s`.

### 17 October 2026 — Item 29: README, lint, the whole suite

**Decision.** README: the slices paragraph (the part name, the leftover written over and said,
without a window every existing still refused), the errors table, "Notes for users". **Lint**, its
own pass: `All checks passed!`. **Green.**
```
videotools/video_stills.py       239      0     96      0   100%
TOTAL                           4686     44   1868     52    99%
======================= 698 passed in 196.51s (0:03:16) ========================
```
**State.** Items 1 to 29 built; the reply to request 6 waits on Squirrel's OK.

### 17 October 2026 — The reply to request 6 sent

**Decision.** Squirrel (22:55): "Write and send the reply to audio-description-tools' request 6 and
close the message." `lobster-mail reply`: `Replied
2026-10-17-1831-video-tools-re-request-6-stills-to-write-each-still to audio-description-tools`;
`lobster-mail done`: `open/ -> done/`. The reply names commit `3dc4b4b`, the order of writing, the
window rule and the unchanged whole-run rule, what was checked, and that the next killed slice in
the device shell is the real check.

**State.** Items 1 to 29 built and replied to; nothing open in the mailbox; nothing waits on
Squirrel.

### 17 October 2026 — Session end: handover

**Decision.** Squirrel (23:05): "close down and write handover". The background `lobster-mail wait`
stopped; the mailbox has nothing new or open, `inbox/` is empty, the tree is clean at `d64d8df`.
"Where things stand" brought up to date, committed and pushed; then `lobster-mail handover --as
video-tools --session mac -` with where things stopped, what waits (nothing) and what to do next,
which also gives up the duty.

**State.** Items 1 to 29 built, replied to and pushed; 698 tests, 99%, lint clean. Nothing waits on
Squirrel. Not done on any machine but the Mac: a real device-shell run of `setup-linux` (item 27)
and of a killed slice carried on (item 29); audio-description-tools' first uses are those checks.
Next session: `lobster-mail start` (the hook), CLAUDE.md, PLAN.md items 15 to 29, this section,
`inbox/`.


### 18 October 2026 — Session start; audio-description-tools' request 7 arrives

**Decision.** `lobster-mail start` read the handover of 17 October; `inbox/` empty; the watch
(`lobster-mail wait --as video-tools --session mac`) took the duty at 13:30 UTC and returned at
13:31 with request 7 (id `2026-10-18-1331-audio-description-tools-request-7-narrate-keeps-a-quiet-first-co`),
claimed with `ack`: a line's quiet first consonant cut, a `Say` column with phoneme spans for a
table, `--phonemes` with `--lines --dry-run`. Reported with a proposal (measure the real model
first, then a trim that walks back from the first loud sample, capped near 150 ms). Squirrel:
"Go ahead with request 7 as proposed, with the new trim for scripts as well as --lines." Recorded
as PLAN.md item 30 and "Settled" 55.

### 18 October 2026 — Item 30, 1: the measurement says the trim is not the cause

**Goal.** See how quiet the real model's soft onsets are before choosing the trim's method.

**Decision / surprise.** The proposal assumed the trim cuts the "s"; it does not, on this Mac. The
real model (kokoro-onnx 0.6.1, `af_heart`, speed 1.5, invented lines, scratchpad scripts) starts
sound 30 to 70 ms into its output, and the trim keeps 30 ms before the first sample above 0.01,
which reaches back into the onset's first rise or before it. The "s" is missing in the model's own
output: its energy above 3.5 kHz before the first vowel is 1.1 for "Silas smiles." against 8.9 for
the same "s" mid-line in "Then Silas smiles.", 0.06 for "Sam sits.", and 8.2 for "Silas" at speed
1. A comma before the phonemes doubles it, a comma with the first consonant doubled about triples
it, still short of mid-line; "f" and "h" stay faint. Numbers in PLAN.md "Things checked". So a new
trim would change nothing heard here; building it would have been a change that fixes nothing.
Part 1 went back to Squirrel as PLAN.md "Open questions" 1, with four listening samples (as now,
comma, comma and doubled consonant, speed 1) in the session's scratchpad. Not ruled out: the
device shell's espeak or onnxruntime giving different output (their track may have been made
there). Parts 2 and 3 do not depend on it and go ahead.

**State.** Nothing built yet; next the `Say` column, Tier 1.

### 18 October 2026 — Item 30, 2: the `Say` column read (Tier 1)

**Goal.** A table's optional `Say` column read; a wrong span refused naming the row.

**Test.** `test_a_say_column_gives_what_is_spoken_and_an_empty_say_leaves_the_line_alone` (a row
carries `say` only when its `Say` is filled in) and
`test_a_say_whose_spans_are_wrong_is_refused_naming_its_row_and_the_problem` (unclosed, stray,
empty, an unknown symbol; `check-script`'s own wording after `row 2 of the table in x.md: 'Say': `).

**Red.** The column was ignored:
```
E         At index 0 diff: {'n': 1, 'start': 0.1, 'text': 'Silas smiles.'} != {'n': 1, 'start': 0.1, 'text': 'Silas smiles.', 'say': '[[sˈɪləs]] smiles.'}
E       Failed: DID NOT RAISE Failure     (×4)
5 failed, 16 deselected in 0.38s
```
**Green.** `21 passed in 0.36s`. The first problem of a bad `Say` is the message, as every other
row refusal names one thing.

### 18 October 2026 — Item 30, 2 and 3: speaking from `Say`; `--phonemes` with `--lines` (Tier 2)

**Tests.** `test_a_row_with_say_is_spoken_from_it_spans_as_phonemes_and_timing_keeps_the_line`,
`test_dry_run_shows_each_say_and_estimates_from_what_is_spoken`,
`test_dry_run_with_phonemes_prints_each_lines_phonemes_spans_spliced_and_writes_nothing`,
`test_a_say_with_a_wrong_span_is_refused_before_the_model_is_loaded`, and the flag-separation
case for `--phonemes` changed (below).

**Red.**
```
E         At index 2 diff: 'narrate: --phonemes goes with a script, not --lines\n' != 'narrate: --phonemes goes with --dry-run (it only shows what the voice would be given)\n'
E         At index 0 diff: ('Silas smiles.', False, 'en-us') != ('sˈɪləs SMILES.', True, 'en-us')
E         At index 1 diff: '02.wav  at 2.00 s  ~0.8 s  Thea nods.' != '    say: [[sˈɪləs]] smiles.'
E         At index 0 diff: 2 != 0
4 failed, 14 passed in 3.70s
```
The refusal of a wrong span passed at once (the reader of the Tier 1 cycle already refuses it);
proven by replacing the span check with `wrong = []`: `assert (0, '01.wav  ...iming.json\n') ==
(3, '')`, `1 failed`; restored, `1 passed`.

**Green.** `62 passed in 8.05s` (both narrate files and the table reader).

**Decision / surprise.** The flag-separation case `--lines … --dry-run --phonemes` expected
"--phonemes goes with a script, not --lines"; request 7 asks for exactly that combination, so
the expectation was item 26's and is no longer PLAN.md's. It now pins the new refusal,
`--lines --phonemes` without `--dry-run`, in the script form's words. The `--help` of `--lines`
and `--phonemes` now names `Say` and "each cue or line": its own test
(`test_help_names_the_optional_say_column_and_phonemes_for_a_line`), red first (`assert "('#',
'Start (s)', 'Line', and optionally 'Say' …" in 'usage: narrate …'`), then `42 passed in 7.76s`.

### 18 October 2026 — Item 30, 2 and 3: Tier 3 on the Mac

**Decision.** In the session's scratchpad, an invented two-row table (`Silas smiles.` with `Say`
`[[sˈaɪləs]] smiles.`; `Thea nods.` with no `Say`) against the real model: `--dry-run --phonemes`
printed the README's block (exit 0); `--phonemes` alone, `narrate: --phonemes goes with --dry-run
(it only shows what the voice would be given)`, exit 2; the real run wrote `01.wav  0.661 s` and
`02.wav  0.561 s`, `timing.json` with each `Line` as `text`. The same table without the column:
row 2 byte-identical; row 1, spoken from the same phonemes as text, 15,860 samples against 15,856
by the span route (the model's own text route differs by four samples).

### 18 October 2026 — Item 30, parts 2 and 3: README, lint, the whole suite

**Decision.** README: the `Say` column paragraph with the real dry run, `[--dry-run [--phonemes]]`
in the heading, the errors table (exit 2 and exit 3), "Notes for users". **Lint**, its own pass:
`All checks passed!`. **Green.**
```
videotools/lines.py               86      0     40      2    98%   17->19, 19->21
videotools/narrate.py            202      0     62      0   100%
TOTAL                           4708     44   1880     52    99%
======================= 708 passed in 176.80s (0:02:56) ========================
```
**State.** Item 30 parts 2 and 3 built and committed; part 1 waits on Squirrel's choice; the
reply to request 7 is drafted, not sent.

### 18 October 2026 — Item 30, 1: Squirrel chooses the lead-in

**Decision.** Squirrel listened to the four samples and chose the third: "3 is the best" (a comma
before the phonemes and the first consonant doubled). PLAN.md item 30, 1 rewritten: every cue and
line goes to the voice as phonemes with `, ` in front and a quiet first consonant doubled; the trim
unchanged; "Settled" 56. Assumed and put in "Open questions" 1: only `s`, `f`, `θ`, `ʃ`, `h` are
doubled (the samples doubled only s, f, h). The stub voice counts a lone `,` as a word; it will
count only tokens with a letter or digit, since the real voice does not speak a comma as one.

### 18 October 2026 — Item 30, 1: the lead-in (Tier 1, then Tier 2)

**Goal.** Every cue and line given to the voice as phonemes with `, ` in front and a quiet first
consonant doubled.

**Test.** Tier 1, `test_the_lead_in_puts_a_comma_first_and_doubles_a_quiet_first_consonant`
(s, f, θ, ʃ, h doubled; b, a vowel and voiced ð only the comma; leading spaces dropped; empty
stays empty), against a skeleton `lead_in` that returned its input. The first run failed for the
wrong reason, `NameError: name 'pytest' is not defined` (the file never imported it); fixed in the
test, then the right red:
```
E       AssertionError: assert 'sˈaɪləs smˈaɪlz.' == ', ssˈaɪləs smˈaɪlz.'
```
**Green.** `15 passed in 0.02s`.

**Tier 2.** The expectations of seven narrate tests changed, because PLAN.md item 30, 1 changes
what the voice is given: a cue with no span was sent as text (`is_phonemes: False`) and is now
phonemes with the lead-in; the phonemizer's calls now sit between the creates, so tests that
indexed calls by position index the creates. The hostile-characters test (non-negotiable 7) now
pins the text handed to the phonemizer unchanged, then the lead-in on its output. Red:
```
E         At index 0 diff: ('sˈɪləs SMILES.', True, 'en-us') != (', ssˈɪləs SMILES.', True, 'en-us')
E         At index 2 diff: '    phonemes: sˈɪləs SMILES.' != '    phonemes: , ssˈɪləs SMILES.'
7 failed, 35 passed in 7.74s
```
**Decision / surprise.** Three. The stub voice counted the lead-in's lone `,` as a word; it now
counts only tokens with a letter or digit, and `Gulls wheel | dip.` went from four stub words to
three, so that one expected length changed (the `|` was never a word). The first green attempt
failed with exit 4, `cannot access local variable 'given'`: `_run` has a loop variable `given`
that hid the new function of that name; renamed `for_voice`. And
`test_existing_clips_or_timing_are_refused_and_nothing_is_changed` counted the first run's calls
(3) to show the refused run made none; it now compares with the first run's own count. **Green.**
`57 passed in 8.00s`; lint, its own pass, found one line over 120 (wrapped): `All checks passed!`.

### 18 October 2026 — Item 30, 1: Tier 3, the growth on the real model; README; the whole suite

**Decision.** On thirteen invented lines (scratchpad), old route against the lead-in, both trimmed:
at speed 1.5 the first vowel came at most 40 ms later and a clip at most 0.063 s longer ("Gulls
wheel and dip." +0.063, "Sam sits." +0.061, the first vowel +40 ms); at 0.98 at most 80 ms and
0.140 s. These are in the README as measured, not as a bound. The README's two `--phonemes` blocks
re-run for real (the example copy and the invented table) and pasted; the item 13 sentence "existing
clips are unchanged" is no longer true and was replaced; "Notes for users".
```
TOTAL                           4709     44   1878     52    99%
======================= 718 passed in 188.56s (0:03:08) ========================
```
**State.** Item 30 built in full; the reply to request 7 drafted, not sent; "Open questions" 1
(which consonants are doubled) waits on Squirrel.

### 18 October 2026 — The reply to request 7 sent

**Decision.** Squirrel: "Send the reply to audio-description-tools' request 7 and close the
message." One sentence of the draft was corrected before sending: it said a row without `Say` is
byte-identical on the real model, true at `724ee87` but not since the lead-in. `lobster-mail reply`:
`Replied 2026-10-18-1402-video-tools-re-request-7-narrate-keeps-a-quiet-first to
audio-description-tools`; `lobster-mail done`: `open/ -> done/`. The reply names commits `724ee87`
and `866cb69`, says the trim was not the cause, describes the lead-in and its measured growth, and
asks for a line that still loses its "s" in the device shell, which was not measured.

**State.** Item 30 built and replied to; nothing open in the mailbox. Put to Squirrel and
unanswered: which first consonants are doubled ("Open questions" 1) and request 19's five
adjustments.

### 18 October 2026 — Two open questions settled

**Decision.** Squirrel: "Doubling s, f, th, sh and h is right; settle it. Request 19's five
adjustments are also fine as built." PLAN.md "Open questions" 1 moved to "Settled" 57; the five
adjustments of 11 October, told to him then and never answered, confirmed as "Settled" 58. No code
changes.

**State.** Items 1 to 30 built and replied to; 718 tests, 99%, lint clean; nothing open in the
mailbox; nothing waits on Squirrel.
