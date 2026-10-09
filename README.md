# video-tools

Command-line tools for making short narrated, animated training videos: narration from a script
with a local speech model, timing from the narration, branded scene layout, stills for review,
rendering and assembly.

**Nothing is built yet.** The tools will be pulled out of the prototype that made the first
video, and specified in PLAN.md when they are requested. Until then this repository holds only
its guidance files.

## Notes for users

- 9 October 2026: repository created. No commands yet.

## Contributing

Dev tooling: `/usr/bin/python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`,
then `.venv/bin/pytest` and `.venv/bin/ruff check .`. How the work is done is in `CLAUDE.md`;
what is built, and in what order, is in `PLAN.md`.
