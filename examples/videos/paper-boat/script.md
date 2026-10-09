# Folding a Paper Boat

*The example video for video-tools: an invented subject and an invented source (`sources/figure7.png`,
drawn for this example), written by Claude on 9 October 2026 in the training-video project's
script format (`videos/SCRIPT-FORMAT.md`). It is small, and it uses every part of the format:
every setting, colours, insets, a title card, lettered steps, a shared letter with a tracker
label, each kind of side panel, `say:`, `min:`, `mistake:`, `step:`, `added:`, on-screen labels,
`extra`, notes between scenes, and an end card.*

## Settings

| Key | Value | Notes |
|---|---|---|
| title | Folding a Paper Boat | |
| subtitle | Figure 7, step by step, with the mistakes to avoid | |
| eyebrow | THE PAPERBOAT METHOD | |
| brand | paperboat | `examples/brands/paperboat/BRAND.md` |
| voice | af_heart | |
| speed | 0.98 | |
| language | en-us | |
| speech-model | kokoro-82m | |
| size | 1920x1080 | |
| fps | 30 | |
| quality | 18 | |
| lead | 0.7 | |
| cue-gap | 0.55 | |
| tail | 1.0 | |
| fade | 0.45 0.4 | |
| source | sources/figure7.png | The invented figure. |
| source-image | sources/figure7.png | |
| source-label | FIG. 7 · ORIGINAL | |
| title-image-caption | Figure 7, the source diagram | |
| credit | Folding sequence from the invented Figure 7 | |
| output | out/Folding a Paper Boat.mp4 | |
| scene-code | scenes/ | |
| x-note | ignored by the tools | A key starting with `x-` is allowed. |

## Colours

| Key | Value | Notes |
|---|---|---|
| paper | #FFFDF5 | The sheet. Outlined in paper-edge (BRAND.md, rule 2). |
| paper-edge | #B8AE98 | |
| paper-back | #EDE6D3 | The back of the sheet, where a fold shows it. |
| water | #BFD9E6 | The waves on the last scene. |

## Insets

| Key | Value | Notes |
|---|---|---|
| A | 80 150 1120 600 | Panel A, fold in half. |
| B | 80 660 1120 1110 | Panel B, corners to the centre. |
| C | 80 1170 1120 1560 | Panel C, open out the hull. |
| full | 40 40 1160 1660 | The whole figure. |

## Scene title: Title card

| Key | Value | Notes |
|---|---|---|
| kind | title | |
| code | title_card | |

### Narration

1. Folding a paper boat, the Paperboat way.
   - min: 3.0
2. This film follows Figure 7, one fold at a time.
   - say: This film follows Figure seven, one fold at a time.
   - min: 3.6

### On screen

- Fold in half
- Corners to the centre
- Open the hull

## Notes

Prose between scenes, under a heading the tools do not recognise, is skipped. Tables here are
skipped too:

| Key | Value |
|---|---|
| not-a-setting | ignored |

## Scene A: Fold in half

| Key | Value | Notes |
|---|---|---|
| letter | A | |
| eyebrow | STEP A · FIGURE 7 | |
| title | Fold in half | |
| inset | A | |
| source | Figure 7, panel A | |
| code | fold_in_half | |

### Narration

1. Step A. Fold the sheet in half, top edge to bottom edge.
   - min: 3.0
2. Don't fold it corner to corner. A diagonal fold leaves no hull to open.
   - min: 4.0
   - mistake: Folded corner to corner / Folded edge to edge
   - added: the consequence (no hull) is our inference; the figure shows only the edge fold.

### Side panel

- Top edge to bottom edge
- Crease firmly
  - added: the figure's closing note.

### On screen

- top edge to bottom edge
- crease
- diagonal fold
  - added: as cue 2.
- edge fold

### Pictures

The sheet lies flat; a hand brings the top edge down to the bottom edge and a crease line
appears (cue 1). Cue 2: mistake panels, a diagonal fold against the edge fold.

## Scene B: Corners to the centre

| Key | Value | Notes |
|---|---|---|
| letter | B | |
| eyebrow | STEP B · FIGURE 7 | |
| title | Corners to the centre | |
| inset | B | |
| source | Figure 7, panel B | |
| side-panel | steps | |
| code | corners_to_centre | |

### Narration

1. Step B. One. Find the centre of the folded edge.
   - min: 2.6
   - step: 1
2. Two. Fold each top corner down to the centre line, one after the other.
   - min: 3.6
   - step: 2

### Side panel

1. Find the centre
2. Corners to the centre line

### On screen

- centre
- corner to the centre line

### Pictures

Cue 1: a dashed centre line appears on the folded sheet. Cue 2: the left corner folds down to
it, then the right.

## Scene B2: The strip at the bottom

| Key | Value | Notes |
|---|---|---|
| letter | B | Shares B's place in the tracker. |
| tracker-label | Corners | What the tracker shows for B. |
| eyebrow | STEP B · CONTINUED | |
| title | The strip at the bottom | |
| inset | B | |
| source | Figure 7, panel B, the strip below the triangle | |
| side-panel | custom strip-fold 1 | The strip diagram, drawn by the scene code, from cue 1. |
| code | strip_fold | |

### Narration

1. Fold the strip at the bottom up over the triangle, on both sides.
   - min: 3.6

### On screen

- fold the strip up
- both sides

### Pictures

The strip below the triangle folds up on the near side, then the sheet flips and it folds up
on the far side. The side panel shows the strip diagram.

## Scene C: Open the hull

| Key | Value | Notes |
|---|---|---|
| letter | C | |
| eyebrow | STEP C · FIGURE 7 | |
| title | Open the hull | |
| inset | C | |
| source | Figure 7, panel C | |
| code | open_hull | |

### Narration

1. Step C. Open the bottom of the triangle, and flatten it into a square.
   - min: 3.2
2. Pull the two top corners of the square apart, and the boat opens out.
   - min: 4.0

### Side panel

- Open, then flatten
- Pull the corners apart

### On screen

- open
- flatten into a square
- pull apart

### Pictures

Cue 1: the triangle opens from below and flattens into a square. Cue 2: the square's top
corners pull apart and the boat shape appears.

## Scene R: The finished boat

| Key | Value | Notes |
|---|---|---|
| eyebrow | INSPECTION | |
| title | The finished boat | |
| side-panel | checklist 2 | Ticks appear during cue 2. |
| code | finished_boat | |

### Narration

1. The finished boat.
   - min: 2.0
2. Edges even, creases sharp, and a hull that opens. That's a boat that floats.
   - min: 4.4
   - added: "a boat that floats" is our framing; the figure says nothing about water.

### Side panel

- Edges even
- Creases sharp
- Hull opens

### On screen

- CHECK BEFORE YOU LAUNCH IT

### Pictures

The boat on a strip of water, slowly zooming in; the checklist ticks off during cue 2.

## Scene end: End card

| Key | Value | Notes |
|---|---|---|
| kind | end | |
| extra | 4.0 | No narration; held for 4 s plus the tail. |
| code | end_card | |

### Narration

### Pictures

The brand's boat drawing, the mark and wordmark, the website, the credit lines.
