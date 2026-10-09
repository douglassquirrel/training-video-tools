"""What every command shares: exit codes, errors in words on stderr, refusing to overwrite.

Standard library only; runs on Python 3.9.
"""

import os
import sys

OK = 0            # success, or --dry-run with everything checked
PROBLEMS = 1      # check-script / check-video: problems found and listed
USAGE = 2         # bad arguments
REFUSED = 3       # an input refuses: malformed, missing, output exists; nothing written
EXTERNAL = 4      # an external program or package is missing or failed


class Failure(Exception):
    """A failure the command reports in words and exits with `code`."""

    def __init__(self, message, code=REFUSED):
        super().__init__(message)
        self.code = code


def report(prog, failure):
    """Print a Failure on stderr as `prog: message` and return its exit code."""
    sys.stderr.write(f"{prog}: {failure}\n")
    return failure.code


def refuse_existing(path):
    """Raise Failure if `path` exists: no command writes over a file."""
    if os.path.lexists(path):
        raise Failure(f"{path} already exists; give a new name")
