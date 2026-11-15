"""The suite's own runners: run() calls a command's main inside the test's process, as the program would
behave; run_program() starts the file itself, as a user runs it."""

import importlib
import os
import subprocess
import sys

from tests.tier2 import conftest
from tests.tier2.conftest import run, stub_calls


def no_programs(monkeypatch):
    def refuse(self, *a, **k):
        raise AssertionError("a program was started")
    monkeypatch.setattr(subprocess.Popen, "__init__", refuse)


def test_run_calls_the_command_inside_the_tests_own_process(monkeypatch):
    no_programs(monkeypatch)
    code, out, err = run("crop-insets", "--help")
    assert (code, err) == (0, "")
    assert out.startswith("usage: crop-insets")


def test_a_command_that_raises_exits_1_with_the_traceback_on_stderr_as_a_program_would(monkeypatch):
    module = importlib.import_module("videotools.crop_insets")

    def boom(argv=None):
        raise RuntimeError("boom")
    monkeypatch.setattr(module, "main", boom)
    code, out, err = run("crop-insets", "--help")
    assert (code, out) == (1, "")
    assert err.startswith("Traceback (most recent call last):") and err.endswith("RuntimeError: boom\n")


def test_run_puts_the_environment_the_working_folder_and_argv_back(tmp_path):
    env, cwd, argv, path = dict(os.environ), os.getcwd(), list(sys.argv), list(sys.path)
    run("crop-insets", "--help", cwd=tmp_path, env={"PATH": "/nowhere", "TVT_RUNNER_PROBE": "1",
                                                     "PYTHONPATH": str(tmp_path)})
    assert (dict(os.environ), os.getcwd(), sys.argv, sys.path) == (env, cwd, argv, path)


def test_what_the_command_and_its_child_programs_print_is_caught_in_order():
    def call():
        print("from python")
        sys.stdout.flush()
        os.system("echo from a child; echo child error >&2")
        sys.stderr.write("python error\n")
    assert conftest.catch_output(call) == ("from python\nfrom a child\n", "child error\npython error\n")


def test_a_speech_stand_in_on_pythonpath_is_used_for_the_call_and_the_real_package_comes_back(example, speech):
    real = importlib.import_module("kokoro_onnx")
    code, out, err = run("narrate", example, "--scenes", "A", env=speech)
    assert code == 0, err
    assert stub_calls(speech) != []
    assert sys.modules["kokoro_onnx"] is real


def test_run_program_starts_the_file_itself():
    started = []
    real = subprocess.Popen.__init__

    def counting(self, args, *a, **k):
        started.append(args)
        real(self, args, *a, **k)
    subprocess.Popen.__init__ = counting
    try:
        code, out, err = conftest.run_program("crop-insets", "--help")
    finally:
        subprocess.Popen.__init__ = real
    assert (code, err) == (0, "") and out.startswith("usage: crop-insets")
    assert started == [[sys.executable, os.path.join(conftest.REPO, "crop-insets"), "--help"]]
