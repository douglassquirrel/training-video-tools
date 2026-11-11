"""videotools.config: ~/.training-video-tools.conf, read and never run."""

import re

import pytest

from videotools import config


def test_keys_values_comments_quotes_and_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    conf = tmp_path / "video-tools.conf"
    conf.write_text('# a comment\nSPEECH_MODEL_DIR=~/models/kokoro   # trailing comment\n'
                    'VOICE="af_heart"\n\nSPEED = \'0.98\'\n')
    assert config.read(str(conf)) == {"SPEECH_MODEL_DIR": str(tmp_path / "models" / "kokoro"),
                                      "VOICE": "af_heart", "SPEED": "0.98"}


def test_a_missing_file_is_an_empty_config(tmp_path):
    assert config.read(str(tmp_path / "none.conf")) == {}


def test_an_unknown_key_or_a_line_without_equals_is_refused_naming_its_line(tmp_path):
    conf = tmp_path / "c.conf"
    conf.write_text("VOICE=af_heart\nVOICES=x\njust words\n")
    with pytest.raises(config.ConfigError) as e:
        config.read(str(conf))
    assert str(e.value) == (f"{conf}: line 2: unknown setting 'VOICES' (the settings are SPEECH_MODEL_DIR, VOICE, SPEED, "
                            f"VIDEO_ELEMENTS_DIR, RSVG_CONVERT, TIME_ZONE)\n"
                            f"{conf}: line 3: not KEY=value: just words")


def test_the_default_path_is_in_home_unless_the_environment_names_another(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("TRAINING_VIDEO_TOOLS_CONF", raising=False)
    assert config.path() == str(tmp_path / ".training-video-tools.conf")
    monkeypatch.setenv("TRAINING_VIDEO_TOOLS_CONF", str(tmp_path / "other.conf"))
    assert config.path() == str(tmp_path / "other.conf")
    (tmp_path / "other.conf").write_text("SPEED=1.1\n")
    assert config.read() == {"SPEED": "1.1"}


def test_the_old_names_from_before_the_rename_are_not_read(tmp_path, monkeypatch):
    # video-tools is now another project's name: its settings file and variable are not this one's.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("TRAINING_VIDEO_TOOLS_CONF", raising=False)
    monkeypatch.setenv("VIDEO_TOOLS_CONF", str(tmp_path / "old.conf"))
    (tmp_path / "old.conf").write_text("SPEED=1.1\n")
    (tmp_path / ".video-tools.conf").write_text("SPEED=1.2\n")
    assert config.path() == str(tmp_path / ".training-video-tools.conf")
    assert config.read() == {}


def test_the_elements_folder_and_the_renderer_are_read_the_folder_expanding_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    conf = tmp_path / "c.conf"
    conf.write_text("VIDEO_ELEMENTS_DIR=~/projects/code/video-elements\nRSVG_CONVERT=/opt/rsvg/bin/rsvg-convert\n")
    assert config.read(str(conf)) == {"VIDEO_ELEMENTS_DIR": str(tmp_path / "projects" / "code" / "video-elements"),
                                      "RSVG_CONVERT": "/opt/rsvg/bin/rsvg-convert"}


def test_the_example_settings_file_is_named_for_the_project_and_sets_every_setting_once_uncommented(tmp_path, monkeypatch):
    import os
    monkeypatch.setenv("HOME", str(tmp_path))
    repo = os.path.join(os.path.dirname(__file__), "..", "..")
    with open(os.path.join(repo, "training-video-tools.conf.example"), encoding="utf-8") as f:
        text = f.read()
    assert text.startswith("# Copy to ~/.training-video-tools.conf and edit.")
    conf = tmp_path / "c.conf"
    conf.write_text(re.sub(r"(?m)^#(?=[A-Z_]+=)", "", text))
    assert sorted(config.read(str(conf))) == sorted(config.KEYS)


def test_time_zone_is_a_setting_read_as_written(tmp_path):
    conf = tmp_path / "c.conf"
    conf.write_text("TIME_ZONE=Europe/London\n")
    assert config.read(str(conf)) == {"TIME_ZONE": "Europe/London"}
