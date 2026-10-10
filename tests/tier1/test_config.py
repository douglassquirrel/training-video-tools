"""videotools.config: ~/.video-tools.conf, read and never run."""

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
                            f"VIDEO_ELEMENTS_DIR, RSVG_CONVERT)\n"
                            f"{conf}: line 3: not KEY=value: just words")


def test_the_default_path_is_in_home_unless_the_environment_names_another(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("VIDEO_TOOLS_CONF", raising=False)
    assert config.path() == str(tmp_path / ".video-tools.conf")
    monkeypatch.setenv("VIDEO_TOOLS_CONF", str(tmp_path / "other.conf"))
    assert config.path() == str(tmp_path / "other.conf")
    (tmp_path / "other.conf").write_text("SPEED=1.1\n")
    assert config.read() == {"SPEED": "1.1"}


def test_the_elements_folder_and_the_renderer_are_read_the_folder_expanding_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    conf = tmp_path / "c.conf"
    conf.write_text("VIDEO_ELEMENTS_DIR=~/projects/code/video-elements\nRSVG_CONVERT=/opt/rsvg/bin/rsvg-convert\n")
    assert config.read(str(conf)) == {"VIDEO_ELEMENTS_DIR": str(tmp_path / "projects" / "code" / "video-elements"),
                                      "RSVG_CONVERT": "/opt/rsvg/bin/rsvg-convert"}
