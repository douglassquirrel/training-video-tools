# DIARY.md — video-tools

## Where things stand

9 October 2026. Nothing is built and nothing is specified yet. The repository holds the coding
template's guidance files, filled in for video-tools: CLAUDE.md (how), PLAN.md (the expected
scope, provisional until a request arrives from the training-video project), this diary, a
README, and the dev tooling files. One commit on `main`; no remote yet.

Green: nothing yet (no tests, no code).

Waiting on Squirrel: the open questions in PLAN.md (dependencies, public or private, layout,
creating the GitHub repository and pushing); and the first request from
`~/projects/non-code/training-video/tools/`.

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
