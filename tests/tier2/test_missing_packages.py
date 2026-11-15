"""A package a command needs but this Python lacks is one line naming it and the install, exit 4."""

import os
import sys

import pytest

from tests.tier2.conftest import cropped, fake_media, narrated, rendered, run_program

HINT = ('; from the Linux device shell, set TRAINING_VIDEO_TOOLS_PYTHON to a Python that has it '
        '(README, "Running from the Linux device shell")')


def hidden(tmp_path, module):
    """A folder for PYTHONPATH where `module` raises ImportError, shadowing the real one."""
    folder = tmp_path / "hidden"
    folder.mkdir(exist_ok=True)
    (folder / f"{module}.py").write_text(f"raise ImportError(\"No module named '{module}'\")\n")
    return {"PYTHONPATH": str(folder), "TRAINING_VIDEO_TOOLS_PYTHON": None}


def message(prog, pip):
    return (f"{prog}: the Python package '{pip}' is not installed in this Python ({sys.executable}); "
            f"install it with .venv/bin/pip install {pip}")


@pytest.fixture
def prepared(example, ffstub):
    cropped(example)
    narrated(example)
    rendered(example)
    fake_media(os.path.join(os.path.dirname(example), "out", "Folding a Paper Boat.mp4"), frames=1587, duration="52.9")
    return example


@pytest.mark.parametrize("command, args, module, pip", [
    ("assemble", ["--out", "new.mp4"], "soundfile", "soundfile"),
    ("assemble", ["--out", "new.mp4"], "numpy", "numpy"),
    ("narrate", ["--scenes", "A", "--replace"], "soundfile", "soundfile"),
    ("render", ["--scenes", "A"], "cairo", "pycairo"),
    ("frame-hashes", ["--scenes", "A", "--out", "h.json"], "cairo", "pycairo"),
    ("compare-frames", ["SELF", "A:1.5", "--out", "sheet.png"], "cairo", "pycairo"),
    ("compare-frames", ["SELF", "A:1.5", "--out", "sheet.png"], "numpy", "numpy"),
    ("compare-frames", ["SELF", "A:1.5", "--out", "sheet.png"], "PIL", "Pillow"),
    ("brand-preview", ["--out", "sheet.png"], "cairo", "pycairo"),
    ("stills", ["A:1.5", "--out", "sheet.png"], "cairo", "pycairo"),
    ("stills", ["A:1.5", "--out", "sheet.png"], "PIL", "Pillow"),
    ("crop-insets", [], "PIL", "Pillow"),
    ("check-video", ["--sheet", "sheet.png"], "PIL", "Pillow"),
    ("font-weights", ["--weights", "400", "--family-prefix", "X", "--out", "weights"], "fontTools", "fonttools"),
])
def test_a_missing_package_is_named_with_its_install_line_exit_4(prepared, ffstub, speech, tmp_path, monkeypatch,
                                                                   command, args, module, pip):
    monkeypatch.chdir(tmp_path)
    env = dict(ffstub, **speech)
    env.update(hidden(tmp_path, module))
    env["PYTHONPATH"] = env["PYTHONPATH"] + os.pathsep + speech["PYTHONPATH"]   # the fake speech model stays
    target = tmp_path / "font.ttf" if command == "font-weights" else prepared
    if command == "font-weights":
        target.write_bytes(b"\0")
    args = [target if a == "SELF" else a for a in args]
    code, out, err = run_program(command, target, *args, env=env, cwd=tmp_path)
    assert (code, out) == (4, ""), err
    assert "Traceback" not in err
    assert err == message(command, pip) + HINT + "\n"
    assert not any(os.path.exists(tmp_path / f) for f in ("sheet.png", "weights", "new.mp4"))


def test_with_video_tools_python_set_the_device_shell_hint_is_left_out(prepared, ffstub, tmp_path):
    env = dict(ffstub, **hidden(tmp_path, "soundfile"))
    env["TRAINING_VIDEO_TOOLS_PYTHON"] = sys.executable
    code, out, err = run_program("assemble", prepared, "--out", tmp_path / "new.mp4", env=env)
    assert (code, out) == (4, "")
    assert err == message("assemble", "soundfile") + "\n"
