# scenes/ — the example video's own drawing code

One module per scene, named by the scene's `code` property in `script.md`. Each defines
`draw(frame)`; a scene with a mistake cue also `mistake(frame, rect)` and `right_way(frame,
rect)`; a scene with a `custom` side panel also `panel(frame, rect)`. `frame` carries the cairo
context (clipped to the area), `t`, `timeline`, `scene`, `colours`, `brand`, `area` and
`label(text)`, which checks a label against the script's On screen list. Everything is drawn
with `videotools.draw`, imported as `d` because the scene function is itself called `draw`; the subject here is a sheet of paper, invented for the example.
