#!/bin/sh
# The one launcher for every stand-in program the Tier 2 tests put on PATH. tests/tier2/conftest.py links
# it into a test's folder under the program's name (ffmpeg, ffprobe, git, python3); it runs the matching
# Python stand-in in this folder with the test's Python. It finds both from the environment conftest.run()
# sets, TVT_STUBS (this folder) and TVT_STUB_PYTHON, never from text written into it. No test writes it:
# macOS charges a first run of each new script file, and a new link costs a few thousandths.
name=$(basename "$0")
case "$name" in
  ffmpeg|ffprobe) FFSTUB_NAME=$name exec "$TVT_STUB_PYTHON" "$TVT_STUBS/ffstub.py" "$@" ;;
  git) exec "$TVT_STUB_PYTHON" "$TVT_STUBS/gitstub.py" "$@" ;;
  python3) PYSTUB_SELF=$0 exec "$TVT_STUB_PYTHON" "$TVT_STUBS/pystub.py" "$@" ;;
  *) echo "stub.sh: no stand-in named $name" >&2; exit 127 ;;
esac
