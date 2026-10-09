"""videotools.script: a well-formed script reads back as plain data."""

from videotools import script

TWO_SCENES = """# Tying a Bow

Prose before the settings is for people.

## Settings

| Key | Value | Notes |
|---|---|---|
| title | Tying a Bow | the title card |
| brand | demo | |
| voice | af_heart | |
| speed | 0.98 | |
| language | en-us | |
| speech-model | kokoro-82m | |
| size | 1920x1080 | |
| fps | 30 | |
| source | sources/bow.png | |
| output | out/Bow.mp4 | |
| scene-code | scenes/ | |

## Colours

| Key | Value | Notes |
|---|---|---|
| ribbon | #AA3355 | |

## Insets

| Key | Value | Notes |
|---|---|---|
| A | 10 20 300 400 | |

## Scene A: First loop

| Key | Value | Notes |
|---|---|---|
| letter | A | |
| title | First loop | |
| inset | A | |
| source | Figure 1, panel A | |
| code | first_loop | |

### Narration

1. Step A. Make the first loop.
   - min: 2.5
2. Don't pull it tight yet. It needs room for the second loop.
   - say: Don't pull it tight yet. It needs room for the second loop!
   - mistake: Pulled tight / Left loose
   - added: our inference from panel B.

### Side panel

- Loop, don't pull
  - added: the figure's note.

### On screen

- first loop
- room for the second
  - added: as cue 2.

### Pictures

What the viewer sees, for people.

## Scene end: End card

| Key | Value | Notes |
|---|---|---|
| kind | end | |
| extra | 4.0 | |
| code | end_card | |

### Narration

"""


def test_title_settings_colours_and_insets_read_back():
    data = script.parse(TWO_SCENES)[0]
    assert data["title"] == "Tying a Bow"
    assert data["settings"]["title"] == "Tying a Bow"
    assert data["settings"]["scene-code"] == "scenes/"
    assert data["colours"] == {"ribbon": "#AA3355"}
    assert data["insets"] == {"A": "10 20 300 400"}


def test_scenes_read_back_with_properties_cues_lists_and_lines():
    data = script.parse(TWO_SCENES)[0]
    a, end = data["scenes"]
    assert (a["key"], a["name"], a["line"]) == ("A", "First loop", 33)
    assert a["props"] == {"letter": "A", "title": "First loop", "inset": "A",
                          "source": "Figure 1, panel A", "code": "first_loop"}
    assert a["cues"] == [
        {"n": 1, "text": "Step A. Make the first loop.", "line": 45, "min": "2.5"},
        {"n": 2, "text": "Don't pull it tight yet. It needs room for the second loop.", "line": 47,
         "say": "Don't pull it tight yet. It needs room for the second loop!",
         "mistake": "Pulled tight / Left loose", "added": "our inference from panel B."},
    ]
    assert a["side"] == [{"text": "Loop, don't pull", "line": 54, "added": "the figure's note."}]
    assert a["screen"] == [{"text": "first loop", "line": 59},
                           {"text": "room for the second", "line": 60, "added": "as cue 2."}]
    assert (end["key"], end["props"], end["cues"]) == ("end", {"kind": "end", "extra": "4.0", "code": "end_card"}, [])


def test_parse_reports_no_problems_for_a_well_formed_script():
    assert script.parse(TWO_SCENES)[1] == []
