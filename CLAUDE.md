# CLAUDE.md — Working guide for video-tools

Written 9 October 2026 by Claude at Squirrel's request, from the coding template, which carries
the working rules of Squirrel's other projects (Magnificat, halmos, transcriber, filer,
book-tools, hn-submitter, scatter). Read this first in any session here, then PLAN.md, which
is the source of truth for *what* the program does and the order it gets built in, then
DIARY.md, which says where things stand. This file is the source of truth for *how* to build
it.

This folder is the repository (`git@github.com:douglassquirrel/video-tools.git`, private until Squirrel decides otherwise: PLAN.md, open question 2), one branch, `main`.
CLAUDE.md, PLAN.md and DIARY.md are committed in it. If it ever goes public, move the three
out to a folder beside the checkout (`video-tools-code/` holding `CLAUDE.md`, `PLAN.md`,
`DIARY.md` and the checkout `video-tools/`, as halmos-code/ and book-tools-code/ do), so process
notes for an AI contributor are not in a public history. In a public repository, commit
messages are written for any user too: no names, tickets or private material.

It needs no secrets: nothing it does logs in, pays or calls a service.

## What this is

A small set of command-line tools for making narrated, animated training videos of the kind
in `~/projects/non-code/training-video/`: a procedure diagram turned into a few minutes of video,
one animated scene per step, narration and captions, common mistakes shown beside the right
way, in a brand's colours and fonts. Squirrel, or Claude working in that project, runs them from
Terminal on the Mac (or in Claude's device shell) against a video's folder: narration made from
a script by a local speech model, cue timings from the narration, scene layout and branding,
stills for review, scene segments rendered through ffmpeg, and the final assembly with the
narration mixed in.

```
<command> [--dry-run] <arguments>       # one command per job; the list in PLAN.md is provisional
```

**Nothing is built yet.** The commands come from the prototype that made the first video
(`~/projects/non-code/make-bed-training-video/_work/`), by way of a review and a written request
from the training-video project; until a request arrives, PLAN.md lists only the expected scope.
The tools never contain anything particular to one video: a video's subject drawing (a bed, a
pillow), its narration and its source stay in that video's folder, and a brand's look comes from
a brand kit file. Everything runs on the machine: no source, script or sound is sent anywhere.

When PLAN.md is ambiguous, ask Squirrel rather than guessing. If the question is minor and the
work can proceed either way, pick the obvious default, record the assumption in PLAN.md under
"Open questions", and keep going; Squirrel's answer then moves it to "Settled". Do not invent
requirements.

---

## Non-negotiables

Every one of these must be true before you report the work as done:

1. **Nothing leaves the machine, and no command writes over its input.** Training videos are
   made from sources that may be confidential (a client's procedure, an internal manual), so
   narration is spoken by a local model and no command opens a network connection or calls a
   service; the speech model is downloaded once, by Squirrel, into `~/models/`. Every output
   goes to a new path; a command refuses to start if its output already exists, and never
   touches a source, a script or a finished video. Enforced by tests: one that fails if the
   package imports a networking module (`socket`, `urllib`, `http`, `ssl`), and one per command
   that pins the refusal to overwrite.
2. **No test touches the network, a real account, real data or a program that costs money or
   time.** Run the whole suite on a machine with none of the external programs installed and the
   network unreachable, and it must pass in full. External programs are replaced by stubs on
   PATH; fixtures are invented, tiny and hand-written, never copied from anything real. Checks
   against the real thing are manual, read-only, documented in the README and recorded in
   DIARY.md.
3. **Never touch credentials, and never commit a secret.** The project needs none; nothing
   from a real config file but the `.example` is committed, and no fixture contains anything
   from a real video's source.
4. **Minimal installation.** It runs on a stock Mac from Terminal with what ships with macOS
   plus the dependencies PLAN.md lists under "Dependencies" and nothing else. Drawing, speech
   and video can't be done with the standard library, so this is the one project from the
   coding template that needs some (cairo, ffmpeg, a speech-model runtime); which ones, and how
   they are installed, is Squirrel's decision (PLAN.md, open question 1). Each command imports
   only what it needs, so the commands that need none run on `/usr/bin/python3` alone, kept
   compatible with 3.9. No daemon, server, Docker or watch folder. Dev-only tooling (pytest, pytest-cov, ruff) goes in a gitignored
   `.venv/` from `requirements-dev.txt` and is mentioned only under the README's
   "Contributing". Every path is configuration; nothing assumes where anything is.
5. **Every failure is a useful error.** Each thing that can go wrong gets its own plain-English
   message on stderr saying what happened and what to do, and a non-zero exit code. Never a
   Python traceback, never a raw error from an underlying program on its own.
6. **Inputs are never modified**, and the program writes only what PLAN.md says it writes. A
   test pins each thing it must never do (overwrite, delete, move, retry, submit twice).
7. **Arguments are data, never code.** Anything that passes through a shell, a template, a
   query or another language is handed over as an argument or JSON-encoded, never pasted into
   source text. A test with quotes, backslashes, newlines, `$`, `</script>` and non-ASCII
   characters pins this.
8. **Test-driven development, with no exceptions.** Every change to behaviour starts with a
   test you have *run* and *watched fail* for the right reason, and ends with that same test
   run again and passing. Writing implementation before a failing test exists for it is a
   process violation, not a shortcut. See [Test-driven development](#test-driven-development).
9. **Thorough automated coverage.** See [Testing](#testing).
10. **The whole suite runs green and lint is clean with one command each.** Never report
    success on a run you did not execute; paste the real output.
11. **The command keeps doing exactly what PLAN.md and the README say.** A change justified by
    "the tests wanted it" that alters what a real run writes or prints is a regression, not a
    pass; check by reading the affected code path, not only by running the suite.
12. **A `README.md` a newcomer can follow.** See [README](#readme).
13. **DIARY.md is current**, written as the work happens, so a session with no memory of this
    project can pick it up from DIARY.md, PLAN.md, this file and the code alone. See
    [Diary](#diary).
14. **Squirrel's other projects are read-only** from this one: they may be read for their
    working rules or their contracts and are never modified. The same goes for any real data
    folder this project reads: never write into it; manual checks go into a scratch folder.
15. **Big model files live in `~/models/`**, never in this folder or any project folder: the
    speech model (about 325 MB) goes in `~/models/kokoro/` unless PLAN.md says otherwise, and
    its path is configuration.

---

## Test-driven development

### The loop

For each increment of behaviour (one flag, one validation rule, one error path, one outcome),
not the whole command at once:

1. **Write the test.** Express the behaviour from PLAN.md as the smallest test that captures
   it. Assert the real expected value (the exact message, the exit code, the exact file
   written, the arguments the stub received), never "does not raise" or "file exists".
2. **Run it and watch it fail.** Run that one test and confirm it fails.
3. **Verify the failure is the right one.** It must fail because the behaviour is missing (an
   assertion mismatch, an unimplemented path), not an import error, a typo, a missing fixture
   or something unrelated. If it fails for the wrong reason, fix the test and go back to step
   2. A test that passes immediately is testing something that already worked: sharpen it until
   it fails, or delete it.
4. **Write the minimum implementation** that makes it pass. No speculative generality, no
   untested branches added while you are in there.
5. **Run the full suite.** The new test passes and every previously passing test still passes.
   A green new test alongside a regression elsewhere is a failed step.
6. **Refactor if warranted**, then run the full suite again.
7. Repeat.

### Rules

- Never write implementation and its test in the same step and run the suite once at the end.
  The failing run in step 2 is the point; skipping it means you never proved the test can detect
  the bug it claims to guard against.
- Never edit a test to match output you did not predict. If a test fails after a change, the
  default assumption is that the code is wrong. Change the test only when you can say plainly
  why the *test's* expectation was wrong, and say so in DIARY.md.
- Never delete, skip, comment out or weaken a failing test to get to green.
- Fixing a bug starts with a test that reproduces it and fails. Reproduce first, fix second.
- If you cannot make a test fail before implementing (the behaviour is already correct, or the
  case is unreachable), say so explicitly instead of quietly writing the code anyway.
- The command-line surface is held to the same standard: argument parsing, `--help`,
  `--dry-run` and exit codes get tests written first, like anything else.

**The one legitimate exception**: when characterising code that already exists and is presumed
correct (a prototype being ported, a function already in use), there may be no red-then-green
cycle for the implementation. The discipline still applies to the *test*: write the assertion
before running it, confirm it fails when you deliberately break the code, then confirm it
passes against the real code. That one check is what proves the test can catch a regression.
If such a test shows the existing code does not do what PLAN.md says, stop, record it in
DIARY.md as a find (not folded into "added tests"), and tell Squirrel.

### Reporting

For each increment, report to Squirrel and record in DIARY.md the test name, the **failing**
run's output (trimmed to the assertion) and the **passing** run's output afterwards. Paste real
terminal output; never summarise a run you did not execute, and never claim red-then-green
from memory.

## Testing

PLAN.md lists the behaviours; this is the standard and the tooling.

Coverage must be thorough and complete, not token:

- Every flag, every validation rule, every refusal-to-start condition and every failure path
  (the stub returns nothing, returns malformed output, exits non-zero, hangs past a timeout)
  has a test that provokes it.
- Boundary and degenerate inputs: empty, one item, Unicode in content and in filenames (NFC
  and NFD), names with spaces, a config file with a missing key, a quoted value, a comment.
- Round trips wherever a format is both written and read.
- Tests are deterministic and hermetic: no network, no sleeps, no shared temp paths, no
  ordering dependencies. Each test gets its own temporary folders, cleaned up in teardown. The
  clock and any wait are injected, never read from the real clock.
- Name tests for the behaviour they pin down, not the function they call:
  `refuses_title_longer_than_80_characters`, `leaves_no_partial_file_when_the_tool_fails`, not
  `test_main_3`.
- Measure coverage and report the honest number. Aim for at least 90% of the code under test;
  a line that is unreachable is deleted or its reason stated in the README. Where line coverage
  cannot be measured (a gnuplot script, a shell script), every numbered behaviour in PLAN.md
  has at least one named test instead, and the tests' README says which.

Tiers, in separate folders (`tests/tier1/`, `tests/tier2/`) so each runs alone:

- **Tier 1, pure functions.** Argument validation, parsing, rendering, classifying, building
  the text handed to another program. Nothing installed beyond the test runner.
- **Tier 2, the command against stubs.** A fake of each external program on PATH (written by
  `conftest.py`) that returns canned output or fails on demand, and records what it was given.
  Every exit code, every message, `--help`, `--dry-run`, the timeout, and every "never does
  this" rule live here. No real programs, no network, no sleeps.
- **Tier 3, manual, with the real thing.** Documented in the README, not automated: run by
  Claude Code or Squirrel against a scratch copy or with `--dry-run`, read-only on anything
  real, and recorded in DIARY.md with real output (or counts only, where the output is
  private).

Tooling follows the language: Python 3 → `pytest` + `pytest-cov`, lint with `ruff`; bash →
`bats-core` and `shellcheck`; Swift → `swift test`. Configured in `pyproject.toml` so the test
command and the lint command run with no flags. Lint is a separate, clearly labelled pass from
behaviour work, so the log shows "found by testing" apart from "found by lint".

## Command-line surface

Each command is the product, not a demo, and Squirrel runs it from Terminal without reading the
code. So: `--help`; errors to stderr, results and progress to stdout, so it composes with
other tools; exit `0` only on complete success, otherwise the code PLAN.md gives for that
failure; `--dry-run` does everything up to the irreversible step and stops. Argument parsing
with the standard library (argparse), no third-party parser.

## README

Write `README.md` for someone who has never seen this repository. Include, in this order:

1. One paragraph: what it does and for whom.
2. Requirements: macOS version, packages, any one-time settings.
3. Installation: a pasteable block, verified on a fresh shell.
4. Quick start: each command with `--dry-run` on the example video in `examples/`, with real
   output pasted.
5. Usage: every form of the command, every flag, the config file, with example invocations and
   their output.
6. Errors and exit codes: each refusal and failure and what the user should do about it.
7. Testing: how to run the suite and lint, the current coverage number, and the Tier 3 manual
   checks.
8. Known limitations and deliberate non-goals (PLAN.md's "Not doing").
9. **Notes for users**: dated lines about anything a user must know or change (a new flag, a
   changed default, a changed output format).
10. Contributing: one or two lines on dev tooling.

Run every command shown before committing it.

## Working method

- Order of work: read PLAN.md and the diary; check any external program's real behaviour
  (`--help`, the real page, the real output format) before code depends on a belief about it,
  and record the observation in DIARY.md and PLAN.md's "Things checked". Tier 1 first, then
  Tier 2 against the stubs, then the README; lint last as its own pass. Tests come first in
  every increment, one red-green cycle at a time.
- Small increments. Every increment ends on a full green suite and a commit whose message says
  what changed and why, in plain English, in one line with detail underneath if needed;
  pushed to `origin` when a step in PLAN.md is finished. Squirrel reads the log.
- Trunk-based development: every commit goes straight onto `main`, and `main` is the only
  branch. No feature branches, no pull requests, no merge commits, no rebasing of pushed
  history. Work that is not ready to commit stays uncommitted in the working tree; work that is
  committed is green and complete for its increment. If a step turns out wrong, a new commit
  reverses it (`git revert`), never a rewrite of what was pushed.
- Prefer clarity over cleverness; keep it small. State the whole job in one line here, and
  resist frameworks and abstractions that one command does not need.
- When behaviour changes, update PLAN.md and the README in the same commit, and add a dated
  line to the README's "Notes for users" when a user must know.
- Dev tooling (`pytest`, `pytest-cov`, `ruff`) goes in a `.venv/` in this folder, gitignored,
  installed from `requirements-dev.txt`.
- Decisions put to Squirrel are stated in full, in plain words, a few at a time: never
  shorthand like "the draft" or "option B".
- Report honestly: if something is incomplete or a test fails, say so plainly with the output.

## Diary

`DIARY.md`, beside this file, is for handover: a session with no memory of this project must
be able to resume from it, PLAN.md, this file and the code alone. Assume the reader has none
of your context and cannot ask you a question.

### Structure

1. **`## Where things stand`** at the top, rewritten in place every session: what is built,
   what is green, the coverage number, the next step, what is known-broken, what is waiting
   on Squirrel, and how the tests work (where the stubs are, how to run one tier). A reader
   must get the current state from this section alone.
2. **`## Log`** underneath, append-only, newest last, one entry per increment: goal, test, red
   (real output), green (real output), decision or surprise, state. Never rewrite or tidy a
   past entry; if one turns out wrong, say so in a new one.

### When to write an entry

One for each meaningful increment: normally each completed red-green-refactor cycle, and also
anything that changes the shape of the work: a decision, a surprise, a dead end, a PLAN.md
clarification, a fixture added, a rule that turned out to be wrong. Not one per tool call.
Write it **as the work happens**, not reconstructed at the end of a session; a diary assembled
from memory is exactly the document that quietly invents a red-green cycle that never ran.

### What an entry contains

```markdown
### <date> — <short title>

**Goal.** The one behaviour this increment was meant to add.

**Test.** The test name, and what it asserts.

**Red.** The real failure output, trimmed to the assertion. Say why it is the *right* failure.

**Green.** The passing output, and the full-suite result alongside it.

**Decision / surprise.** Anything a future reader would otherwise have to rediscover: why an
approach was rejected, what the external program actually returned, a PLAN.md rule that
needed sharpening.

**State.** What is green now, and the next step.
```

Trim the sections that do not apply (a non-coding entry has no red or green), but never drop
**Decision / surprise** when there was one; that section is the reason the file is worth
keeping. The rest can be reconstructed from git and the suite; that cannot.

### Rules

- Paste real terminal output. Never summarise a run you did not execute or reproduce one from
  memory. Never paste anything private or secret: fixture output only, and counts for checks
  against real data.
- Record dead ends and wrong turns. A diary of unbroken success is not a record, and the next
  session will repeat whatever you quietly abandoned.
- Update `## Where things stand` in the same commit that invalidates it. A stale snapshot is
  worse than none, because it reads as current.
- Keep entries short: the whole log should be readable in ten minutes.
- If you end a session mid-increment, say so explicitly in `## Where things stand`: which test
  is red, what you were part-way through, what you had ruled out.

## Definition of done

```bash
cd ~/projects/code/video-tools
.venv/bin/pytest                # all green, with no external programs and no network
.venv/bin/ruff check .          # clean
./bin/<command> --help                 # for each command built
./bin/<command> --dry-run <arguments>  # on the example video: everything but writing the output
```

All of it succeeds with the real output pasted into DIARY.md; coverage is reported and at
least 90% or the gap explained; lint is clean; the Tier 3 checks are done and recorded; the
README is complete, its installation section pasteable on a fresh Mac and every command in it
run; "Notes for users" lists anything a user must know; `## Where things stand` describes the
finished state, dead ends included; and everything is committed and pushed.

And every piece of behaviour got there through a test that was written first, run, seen to
fail for the right reason, and then run again and seen to pass.
