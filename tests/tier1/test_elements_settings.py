"""videotools.elements: where the video-elements library is, from the flags or the config file."""

import argparse

from videotools import elements


def _args(**kw):
    ns = argparse.Namespace(elements=None, renderer=None)
    ns.__dict__.update(kw)
    return ns


def test_the_flags_win_over_the_config_settings():
    conf = {"VIDEO_ELEMENTS_DIR": "/conf/video-elements", "RSVG_CONVERT": "/conf/rsvg-convert"}
    assert elements.settings(_args(elements="/flag/lib", renderer="/flag/rsvg"), conf) == ("/flag/lib", "/flag/rsvg")


def test_the_config_settings_fill_in_what_the_flags_leave_out():
    conf = {"VIDEO_ELEMENTS_DIR": "/conf/video-elements", "RSVG_CONVERT": "/conf/rsvg-convert"}
    assert elements.settings(_args(elements="/flag/lib"), conf) == ("/flag/lib", "/conf/rsvg-convert")
    assert elements.settings(_args(renderer="/flag/rsvg"), conf) == ("/conf/video-elements", "/flag/rsvg")


def test_neither_set_is_none_for_both():
    assert elements.settings(_args(), {}) == (None, None)


def test_a_tilde_in_the_flag_means_the_home_folder(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert elements.settings(_args(elements="~/lib"), {}) == (str(tmp_path / "lib"), None)
