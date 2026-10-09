"""Tier 1 fixtures shared by the script tests."""

import pytest


@pytest.fixture
def video(tmp_path):
    """A video folder with its source file and a brand kit two levels up, as in a project."""
    folder = tmp_path / "videos" / "bow"
    (folder / "sources").mkdir(parents=True)
    (folder / "sources" / "bow.png").write_bytes(b"not really a png")
    (tmp_path / "brands" / "demo").mkdir(parents=True)
    (tmp_path / "brands" / "demo" / "BRAND.md").write_text("# demo\n")
    return folder
