# tests/stubs/

Stand-ins for the programs and packages the commands use, so that the suite runs with none of
them installed and no network. `tests/tier2/conftest.py` puts `kokoro_onnx/` first on
`PYTHONPATH` (a fake speech model) and writes stub `ffmpeg` and `ffprobe` scripts on `PATH`.
Nothing here is real: no model, no media, no output copied from anything real.
