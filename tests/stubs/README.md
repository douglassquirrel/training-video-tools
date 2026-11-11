# tests/stubs/

Stand-ins for the programs and packages the commands use, so that the suite runs with none of
them installed and no network. `tests/tier2/conftest.py` puts `kokoro_onnx/` first on
`PYTHONPATH` (a fake speech model) and writes stub `ffmpeg` and `ffprobe` scripts on `PATH`.
Nothing here is real: no model, no media, no output copied from anything real.

`pystub.py` stands in for the `python3` on PATH and the venv's python `setup-linux` makes (`tests/tier2/test_setup_linux.py` puts it on PATH): it
records every call, makes a fake venv on `-m venv`, answers the import check from a marker file
that `-m pip install` writes, and fails either step on demand.

`gitstub.py` stands in for `git` for `record-output` (the `gitstub` fixture in `tests/tier2/conftest.py` writes
a `git` script on PATH that runs it): it answers `rev-parse --short HEAD` and `status --porcelain` for each
folder from `GITSTUB_HEADS` and `GITSTUB_DIRTY`, fails every call with `GITSTUB_FAIL`, and records every call.
