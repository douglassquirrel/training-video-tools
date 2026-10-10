"""videotools.elements.open_library: the configured root put on the import path, the library
opened through its interface, and every refusal in words (PLAN.md item 15, "Where the library is")."""

import os
import shutil
import sys

import pytest

from videotools import cli, config, elements

INVENTED = os.path.join(os.path.dirname(__file__), "..", "stubs", "video-elements")


@pytest.fixture
def fresh_import():
    """No `videoelements` module from an earlier test, and sys.path restored afterwards."""
    def drop():
        for name in [m for m in sys.modules if m == "videoelements" or m.startswith("videoelements.")]:
            del sys.modules[name]
    drop()
    path = list(sys.path)
    yield
    drop()
    sys.path[:] = path


def test_no_setting_and_no_flag_is_refused_naming_both(fresh_import, monkeypatch):
    monkeypatch.setenv("VIDEO_TOOLS_CONF", "/nowhere/video-tools.conf")
    with pytest.raises(cli.Failure) as e:
        elements.open_library(None, None)
    assert str(e.value) == ("VIDEO_ELEMENTS_DIR is not set in /nowhere/video-tools.conf and no --elements was given; "
                            "a script that describes a scene's cast needs the video-elements repository "
                            "(README, \"Configuration\")")
    assert e.value.code == cli.REFUSED


def test_a_missing_folder_is_refused_by_path(fresh_import, tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEO_TOOLS_CONF", "/nowhere/video-tools.conf")
    with pytest.raises(cli.Failure) as e:
        elements.open_library(str(tmp_path / "gone"), None)
    assert str(e.value) == (f"{tmp_path / 'gone'}: video-elements folder not found "
                            f"(VIDEO_ELEMENTS_DIR in {config.path()}, or --elements)")
    assert e.value.code == cli.REFUSED


def test_a_folder_without_the_package_is_refused_saying_what_the_setting_names(fresh_import, tmp_path):
    (tmp_path / "elements").mkdir()
    with pytest.raises(cli.Failure) as e:
        elements.open_library(str(tmp_path), None)
    assert str(e.value) == (f"{tmp_path} has no videoelements/ package: VIDEO_ELEMENTS_DIR names the root of the "
                            "video-elements repository, the folder holding videoelements/ and elements/")
    assert e.value.code == cli.REFUSED


def test_a_package_that_cannot_be_imported_is_refused_with_its_error(fresh_import, tmp_path):
    pkg = tmp_path / "videoelements"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("raise RuntimeError('broken on purpose')\n")
    with pytest.raises(cli.Failure) as e:
        elements.open_library(str(tmp_path), None)
    assert str(e.value) == f"videoelements at {tmp_path} could not be imported: RuntimeError: broken on purpose"
    assert e.value.code == cli.REFUSED


def test_a_library_that_refuses_to_open_is_reported_with_its_problems(fresh_import, tmp_path):
    shutil.copytree(os.path.join(INVENTED, "videoelements"), tmp_path / "videoelements")
    with pytest.raises(cli.Failure) as e:
        elements.open_library(str(tmp_path), None)
    assert str(e.value) == (f"the video-elements library at {tmp_path} refuses to open:\n"
                            f"  - {tmp_path / 'elements'}: folder not found\n"
                            f"  - {tmp_path / 'licenses' / 'SOURCES.md'}: file not found")
    assert e.value.code == cli.REFUSED


def test_the_invented_library_opens_with_its_two_elements_and_the_renderer_given(fresh_import):
    lib = elements.open_library(INVENTED, "/opt/rsvg/bin/rsvg-convert")
    assert lib.names() == ["pot", "table"]
    assert lib.renderer == "/opt/rsvg/bin/rsvg-convert"
    assert lib.element("table")["params"]["highlight.*"] == {"type": "number", "min": 0.0, "max": 1.0, "default": 0.0}
    assert lib.element("table")["anchors"]["row.*"] == "computed"
    assert lib.element("pot")["anchors"]["rim"] == (12.0, 4.0)
    assert lib.credits(["pot", "table"]) == [{"category": "Icons", "credit": "Invented Icons", "licence": "MIT"}]


def test_no_renderer_leaves_the_library_its_own_default(fresh_import):
    assert elements.open_library(INVENTED, None).renderer == "rsvg-convert"


def test_the_root_goes_on_the_import_path_once_however_often_it_is_opened(fresh_import):
    elements.open_library(INVENTED, None)
    elements.open_library(INVENTED, None)
    assert sys.path.count(os.path.abspath(INVENTED)) == 1
