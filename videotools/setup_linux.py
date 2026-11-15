"""setup-linux: retired (PLAN.md item 27, Settled 67). lobster-tools' prepare-venv now makes the Linux device
shell's venv, installs the packages, checks the model, writes the config and prints the environment lines,
from this checkout's prepare-venv.conf. Every form of this command says so and exits 2, doing nothing.

Standard library only; runs on whatever python3 the shell has (3.9 or later).
"""

from videotools.cli import USAGE, Failure, report

PROG = "setup-linux"
RETIRED = ("setup-linux is retired; prepare the device shell with lobster-tools' prepare-venv, which reads this "
           "checkout's prepare-venv.conf: eval \"$(python3 ~/mnt/lobster-tools/prepare-venv --project "
           "~/mnt/training-video-tools --venv DIR --model DIR --conf FILE)\" "
           "(README, \"Running from the Linux device shell\")")


def main(argv=None):
    return report(PROG, Failure(RETIRED, USAGE))
