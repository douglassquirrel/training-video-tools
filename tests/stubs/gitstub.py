"""A stand-in for `git`, for record-output's tests: answers `git -C DIR rev-parse --short HEAD` and
`git -C DIR status --porcelain` from the environment and records every call. Nothing real.

GITSTUB_LOG    a file to append each call to, as JSON: {"args": [...]}
GITSTUB_HEADS  JSON {real path of DIR: short commit}; a folder not named answers 0000000
GITSTUB_DIRTY  JSON [real path of DIR, ...]: folders whose status lists two changes
GITSTUB_FAIL   when set, every call fails as git does outside a checkout (exit 128)
"""

import json
import os
import sys

args = sys.argv[1:]
if os.environ.get("GITSTUB_LOG"):
    with open(os.environ["GITSTUB_LOG"], "a", encoding="utf-8") as f:
        f.write(json.dumps({"args": args}) + "\n")
if os.environ.get("GITSTUB_FAIL"):
    sys.stderr.write("fatal: not a git repository (or any of the parent directories): .git\n")
    sys.exit(128)
folder, rest = (args[1], args[2:]) if args[:1] == ["-C"] else (os.getcwd(), args)
key = os.path.realpath(folder)
if rest == ["rev-parse", "--short", "HEAD"]:
    print(json.loads(os.environ.get("GITSTUB_HEADS", "{}")).get(key, "0000000"))
elif rest == ["status", "--porcelain"]:
    if key in json.loads(os.environ.get("GITSTUB_DIRTY", "[]")):
        print(" M videotools/outmd.py\n?? notes.txt")
else:
    sys.stderr.write(f"gitstub: not a call record-output makes: {args}\n")
    sys.exit(2)
