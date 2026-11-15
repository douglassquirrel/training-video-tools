# tests/stubs/

Stand-ins for the programs and packages the commands use, so that the suite runs with none of
them installed and no network. `tests/tier2/conftest.py` puts `kokoro_onnx/` first on
`PYTHONPATH` (a fake speech model) and puts stub `ffmpeg` and `ffprobe` on `PATH`.
Nothing here is real: no model, no media, no output copied from anything real.

`stub.sh` is the one launcher for every stand-in program: each test's folder gets a symbolic link to it
under the program's name (`ffmpeg`, `ffprobe`, `git`, `python3`), and it runs the matching Python stand-in
below with the test's Python, found from `TVT_STUBS` and `TVT_STUB_PYTHON`, which `conftest.run()` sets.
No test writes it (macOS charges the first run of each new script file); the suite checks at its end that
it was not written over.

`pystub.py` stands in for the `python3` on PATH and the venv's python `setup-linux` makes (`tests/tier2/test_setup_linux.py` links `stub.sh` onto PATH as `python3`): it
records every call, makes a fake venv on `-m venv`, answers the import check from a marker file
that `-m pip install` writes, and fails either step on demand.

`gitstub.py` stands in for `git` for `record-output` (the `gitstub` fixture in `tests/tier2/conftest.py` links
`stub.sh` onto PATH as `git`): it answers `rev-parse --short HEAD` and `status --porcelain` for each
folder from `GITSTUB_HEADS` and `GITSTUB_DIRTY`, fails every call with `GITSTUB_FAIL`, and records every call.
