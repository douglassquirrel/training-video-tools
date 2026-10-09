# DIARY.md — video-tools

## Where things stand

9 October 2026. Nothing is built and nothing is specified yet. The repository holds the coding
template's guidance files, filled in for video-tools: CLAUDE.md (how), PLAN.md (the expected
scope, provisional until a request arrives from the training-video project), this diary, a
README, and the dev tooling files. Three commits on `main`; no remote yet.

Green: nothing yet (no tests, no code).

Waiting on: the first request from `~/projects/non-code/training-video/tools/`. Squirrel will
create the GitHub repository and push when he is ready. Settled: private for now, and the
dependencies in PLAN.md allowed (Squirrel, 9 October 2026, 16:16).

How the tests will work: `tests/tier1/` for pure functions (timing, layout, colour and font
parsing); `tests/tier2/conftest.py` will put stub `ffmpeg`, `ffprobe` and a stub speech model
first on PATH or in config. Nothing written yet.

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
