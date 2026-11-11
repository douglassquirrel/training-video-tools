"""record-output's write: OUT.md replaced whole or not at all (PLAN.md item 31, 7)."""

import os

import pytest

from videotools import cli, record_output


def test_a_failure_after_the_part_file_is_made_removes_it_and_leaves_the_old_file(tmp_path, monkeypatch):
    out_md = tmp_path / "OUT.md"
    out_md.write_text("old\n")

    def full(src, dst):
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(os, "replace", full)
    with pytest.raises(cli.Failure) as e:
        record_output._write(str(out_md), "new\n")
    assert str(e.value) == f"{out_md} could not be written (No space left on device); it is as it was"
    assert out_md.read_text() == "old\n"
    assert os.listdir(tmp_path) == ["OUT.md"]
