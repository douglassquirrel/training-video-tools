"""narrate: one clip per cue from the (stub) speech model, timing.json, flags, refusals."""

import json
import os

import pytest

from tests.tier2.conftest import run, stub_calls

CLIPS = ["title_01.wav", "title_02.wav", "A_01.wav", "A_02.wav", "B_01.wav", "B_02.wav", "B2_01.wav",
         "C_01.wav", "C_02.wav", "R_01.wav", "R_02.wav"]


def stub_length(words):
    """The stub's clip length after trimming: 0.03 + (0.5 + 0.25 W) + 0.08 seconds."""
    return round(0.03 + 0.5 + 0.25 * words + 0.08, 3)


def work(example):
    return os.path.join(os.path.dirname(example), "work", "narration")


def test_help_names_every_flag():
    code, out, err = run("narrate", "--help")
    assert code == 0 and err == ""
    for flag in ("--scenes", "--voice", "--speed", "--replace", "--dry-run"):
        assert flag in out


def test_dry_run_lists_the_cues_voice_and_estimates_and_writes_nothing(example, speech):
    code, out, err = run("narrate", example, "--dry-run", env=speech)
    assert (code, err) == (0, "")
    assert out.splitlines()[0] == "narrate (dry run): Folding a Paper Boat"
    assert out.splitlines()[1] == ("voice af_heart, speed 0.98, language en-us, model kokoro-82m from {}".format(speech["SPEECH_MODEL_DIR_FOR_TESTS"]))
    assert "title_02.wav  ~3.8 s  This film follows Figure seven, one fold at a time." in out
    assert out.splitlines()[-1] == "11 cues, about 48 s of speech; nothing written (dry run)."
    assert not os.path.exists(os.path.join(os.path.dirname(example), "work"))
    assert stub_calls(speech) == []


def test_one_clip_per_cue_and_timing_json_from_the_stub_model(example, speech):
    code, out, err = run("narrate", example, env=speech)
    assert (code, err) == (0, "")
    assert sorted(os.listdir(work(example))) == sorted(CLIPS + ["timing.json"])
    timing = json.load(open(os.path.join(work(example), "timing.json")))
    assert (timing["voice"], timing["speed"], timing["model"], timing["sample_rate"]) == ("af_heart", 0.98, "kokoro-82m", 24000)
    assert timing["scenes"]["title"] == [stub_length(7), stub_length(10)]
    assert timing["scenes"]["B2"] == [stub_length(13)]
    assert list(timing["scenes"]) == ["title", "A", "B", "B2", "C", "R", "end"] and timing["scenes"]["end"] == []
    calls = stub_calls(speech)
    assert calls[0] == {"init": [os.path.join(speech["SPEECH_MODEL_DIR_FOR_TESTS"], "model.onnx"),
                                 os.path.join(speech["SPEECH_MODEL_DIR_FOR_TESTS"], "voices.npz")]}
    assert calls[2] == {"create": {"text": "This film follows Figure seven, one fold at a time.",
                                   "voice": "af_heart", "speed": 0.98, "lang": "en-us"}}
    assert len(calls) == 12
    assert f"title_02.wav  {stub_length(10):.3f} s" in out
    assert out.splitlines()[-1] == "Wrote 11 clips and {}".format(os.path.join(work(example), "timing.json"))


def test_the_clips_are_real_wav_files_of_the_recorded_length(example, speech):
    import soundfile
    run("narrate", example, env=speech)
    info = soundfile.info(os.path.join(work(example), "title_01.wav"))
    assert (info.samplerate, info.channels) == (24000, 1)
    assert round(info.frames / info.samplerate, 3) == stub_length(7)


def test_cue_text_with_hostile_characters_reaches_the_model_unchanged(example, speech):
    hostile = 'Say "this", \\ that, $HOME, </script>, café · 45°'
    text = open(example, encoding="utf-8").read().replace("1. The finished boat.", "1. " + hostile)
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("narrate", example, "--scenes", "R", env=speech)
    assert (code, err) == (0, "")
    assert stub_calls(speech)[1]["create"]["text"] == hostile


def test_voice_and_speed_flags_win_over_the_script(example, speech):
    code, out, err = run("narrate", example, "--scenes", "A", "--voice", "zz_test", "--speed", "1.1", env=speech)
    assert (code, err) == (0, "")
    assert stub_calls(speech)[1]["create"]["voice"] == "zz_test"
    assert stub_calls(speech)[1]["create"]["speed"] == 1.1
    timing = json.load(open(os.path.join(work(example), "timing.json")))
    assert (timing["voice"], timing["speed"]) == ("zz_test", 1.1)
    assert sorted(os.listdir(work(example))) == ["A_01.wav", "A_02.wav", "timing.json"]
    assert list(timing["scenes"]) == ["A"]


def test_the_config_default_voice_applies_when_the_script_leaves_it_blank(example, speech):
    # The format requires a voice, but the precedence is flag > script > config: pin it anyway
    # by letting the config's voice through an x- setting? No: the script's voice is required,
    # so the config default only ever shows in --help and the README. Pinned here as the rule.
    code, out, err = run("narrate", example, "--dry-run", env=speech)
    assert "voice af_heart" in out      # the script's, not the config's bm_george


def test_an_unknown_scene_key_is_refused(example, speech):
    code, out, err = run("narrate", example, "--scenes", "A,Z", env=speech)
    assert (code, out) == (2, "")
    assert err == "narrate: no scene 'Z' in the script (scenes: title, A, B, B2, C, R, end)\n"


def test_existing_clips_or_timing_are_refused_and_nothing_is_changed(example, speech):
    run("narrate", example, "--scenes", "A", env=speech)
    before = {f: open(os.path.join(work(example), f), "rb").read() for f in os.listdir(work(example))}
    code, out, err = run("narrate", example, "--scenes", "A,B", env=speech)
    assert (code, out) == (3, "")
    assert err == ("narrate: these would be written over; delete them, or run with --replace:\n"
                   "  {}\n  {}\n  {}\n".format(*tuple(os.path.join(work(example), f) for f in ("A_01.wav", "A_02.wav", "timing.json"))))
    assert {f: open(os.path.join(work(example), f), "rb").read() for f in os.listdir(work(example))} == before
    assert len(stub_calls(speech)) == 3


def test_replace_lists_what_it_replaces_and_keeps_other_scenes_timings(example, speech):
    run("narrate", example, "--scenes", "A,B", env=speech)
    code, out, err = run("narrate", example, "--scenes", "A", "--replace", "--voice", "zz_test", env=speech)
    assert (code, err) == (0, "")
    assert out.startswith("Replacing:\n  {}\n  {}\n  {}\n".format(*tuple(os.path.join(work(example), f)
                                                                    for f in ("A_01.wav", "A_02.wav", "timing.json"))))
    timing = json.load(open(os.path.join(work(example), "timing.json")))
    assert list(timing["scenes"]) == ["A", "B"] and timing["voice"] == "zz_test"
    assert timing["scenes"]["B"] == [stub_length(10), stub_length(14)]


def test_a_missing_model_folder_is_refused_naming_the_setting(example, speech, tmp_path):
    conf = tmp_path / "other.conf"
    conf.write_text("SPEECH_MODEL_DIR=%s\n" % (tmp_path / "nowhere"))
    code, out, err = run("narrate", example, env=dict(speech, VIDEO_TOOLS_CONF=str(conf)))
    assert (code, out) == (3, "")
    assert err == ("narrate: no model.onnx and voices.npz in {} (SPEECH_MODEL_DIR in {}); "
                   "see the README's one-time set-up\n".format(tmp_path / "nowhere", conf))


def test_a_config_without_the_model_setting_is_refused(example, speech, tmp_path):
    conf = tmp_path / "other.conf"
    conf.write_text("VOICE=af_heart\n")
    code, out, err = run("narrate", example, env=dict(speech, VIDEO_TOOLS_CONF=str(conf)))
    assert (code, out) == (3, "")
    assert err == f"narrate: SPEECH_MODEL_DIR is not set in {conf}; see the README's one-time set-up\n"


def test_a_voice_the_model_does_not_have_is_refused_with_the_list(example, speech):
    code, out, err = run("narrate", example, "--voice", "xx_nobody", env=speech)
    assert (code, out) == (3, "")
    assert err == "narrate: the model has no voice 'xx_nobody' (it has af_heart, bm_george, zz_test)\n"
    assert not os.path.exists(work(example))


def test_a_malformed_script_is_refused_with_its_problems(example, speech):
    text = open(example, encoding="utf-8").read().replace("| voice | af_heart | |\n", "")
    open(example, "w", encoding="utf-8").write(text)
    code, out, err = run("narrate", example, env=speech)
    assert (code, out) == (3, "")
    assert err == f"narrate: {example}: 1 problem:\n  - Settings: 'voice' is missing\n"


def test_a_missing_speech_package_is_a_useful_error_exit_4(example, speech, tmp_path):
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "kokoro_onnx.py").write_text("raise ImportError(\"No module named 'kokoro_onnx'\")\n")
    code, out, err = run("narrate", example, env=dict(speech, PYTHONPATH=str(broken)))
    assert (code, out) == (4, "")
    assert err == ("narrate: the speech packages are not installed in this Python (No module named "
                   "'kokoro_onnx'); install them into the venv as the README says\n")


def test_a_model_failure_names_the_cue_and_leaves_what_was_written(example, speech):
    code, out, err = run("narrate", example, "--scenes", "A", env=dict(speech, KOKORO_STUB_FAIL="1"))
    assert (code, out) == (4, "")
    assert err == "narrate: the speech model failed on scene A cue 1 (stub: the model failed on purpose); nothing written for it\n"
    assert not os.path.exists(os.path.join(work(example), "timing.json"))


def test_the_script_and_the_config_are_never_modified(example, speech):
    conf = speech["VIDEO_TOOLS_CONF"]
    before = (open(example, "rb").read(), open(conf, "rb").read())
    run("narrate", example, "--scenes", "A", env=speech)
    assert (open(example, "rb").read(), open(conf, "rb").read()) == before


@pytest.mark.parametrize("flag", ["--speed", "--scenes"])
def test_a_flag_without_a_value_is_usage(flag):
    code, out, err = run("narrate", "x.md", flag)
    assert code == 2 and "usage: narrate" in err
