"""prepare-venv.conf and requirements.txt, read by lobster-tools' prepare-venv in the Linux device shell,
agree with what the commands themselves need (cli.PACKAGES) and the settings they read (config.KEYS)."""

import os

from videotools import cli, config

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def settings():
    pairs = {}
    with open(os.path.join(REPO, "prepare-venv.conf"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                pairs[key] = value
    return pairs


def requirements(name):
    with open(os.path.join(REPO, name), encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def test_the_file_names_this_projects_variables_its_requirements_and_the_speech_model():
    conf = settings()
    assert sorted(conf) == ["ENV_PREFIX", "IMPORTS", "MODEL_FILES", "MODEL_HELP", "MODEL_SETTING", "REQUIREMENTS"]
    assert conf["ENV_PREFIX"] == "TRAINING_VIDEO_TOOLS"
    assert conf["MODEL_FILES"].split() == ["model.onnx", "voices.npz"]
    assert conf["MODEL_SETTING"] == "SPEECH_MODEL_DIR" and conf["MODEL_SETTING"] in config.KEYS
    assert conf["MODEL_HELP"] == "the README's \"One-time set-up of the speech model\""


def test_the_imports_are_the_packages_the_commands_ask_for():
    assert sorted(settings()["IMPORTS"].split()) == sorted(cli.PACKAGES)


def test_the_requirements_are_the_install_lines_the_commands_give_when_a_package_is_missing():
    wanted = sorted(spec.strip('"') for _name, spec in cli.PACKAGES.values())
    assert sorted(requirements(settings()["REQUIREMENTS"])) == wanted
