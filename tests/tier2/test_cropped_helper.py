"""The suite's own helper `cropped()`: the example's insets are cut once a run and copied after, and are the
same files crop-insets writes; an example that is not the pristine one is cropped for real."""

import filecmp
import os
import shutil

from tests.tier2 import conftest
from tests.tier2.conftest import EXAMPLES, cropped, run


def copy_example(folder):
    shutil.copytree(EXAMPLES, folder / "examples")
    return str(folder / "examples" / "videos" / "paper-boat" / "script.md")


def insets(script):
    return os.path.join(os.path.dirname(script), "work", "insets")


def same_files(a, b):
    names = sorted(os.listdir(a))
    assert names == sorted(os.listdir(b))
    match, mismatch, errors = filecmp.cmpfiles(a, b, names, shallow=False)
    return (mismatch, errors) == ([], [])


def counting_crop_insets(monkeypatch):
    calls = []
    real = conftest.run

    def counting(command, *args, **kw):
        if command == "crop-insets":
            calls.append(args)
        return real(command, *args, **kw)
    monkeypatch.setattr(conftest, "run", counting)
    return calls


def test_a_second_pristine_example_is_cropped_without_running_crop_insets_again(tmp_path, monkeypatch):
    cropped(copy_example(tmp_path / "first"))
    calls = counting_crop_insets(monkeypatch)
    cropped(copy_example(tmp_path / "second"))
    assert calls == []


def test_the_copied_insets_are_the_files_crop_insets_writes(tmp_path):
    helped = cropped(copy_example(tmp_path / "helped"))
    real = copy_example(tmp_path / "real")
    code, out, err = run("crop-insets", real)
    assert code == 0, err
    assert same_files(insets(helped), insets(real))


def test_an_example_whose_script_was_changed_is_cropped_for_real(tmp_path, monkeypatch):
    cropped(copy_example(tmp_path / "first"))
    changed = copy_example(tmp_path / "changed")
    with open(changed, encoding="utf-8") as f:
        text = f.read()
    with open(changed, "w", encoding="utf-8") as f:
        f.write(text.replace("| source-label | FIG. 7 · ORIGINAL |", "| source-label | FIG. 8 |"))
    calls = counting_crop_insets(monkeypatch)
    cropped(changed)
    assert calls == [(changed,)]
