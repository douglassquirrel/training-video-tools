# tests/tier2/frames/ — stored frames of the example video

Each `<scene>_<seconds>.png` is a frame of `examples/videos/paper-boat/` drawn by
`videotools.frame.draw_frame` on 9 October 2026 (macOS, cairo 1.18.6, CoreText fonts), reduced
to 192×108. `tests/tier2/test_frame.py` draws the same frames and requires a mean difference
below 6/255 per channel: enough slack for another platform's text rendering, not for a layout
change. They were looked at full size before being stored (DIARY.md, 9 October 2026, "The
frame"). When the chrome changes on purpose, regenerate them with the script in that diary
entry, look at them again, and say so in the diary.
