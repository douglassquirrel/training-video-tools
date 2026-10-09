# tests/tier2/frames/ — stored frames of the example video

Each `<scene>_<seconds>.png` is a frame of `examples/videos/paper-boat/` drawn by
`videotools.frame.draw_frame` on 9 October 2026 (macOS, cairo 1.18.6, CoreText fonts), reduced
to 192×108. `tests/tier2/test_frame.py` draws the same frames and requires a mean difference
below 6/255 per channel: enough slack for another platform's text rendering, not for a layout
change. They were looked at full size before being stored (DIARY.md, 9 October 2026, "The
frame"). When the chrome changes on purpose, regenerate them with the script in that diary
entry, look at them again, and say so in the diary.

The tolerance pins layout, not fonts: drawn with cairo's fallback fonts instead of the brand's,
six of the eight frames still differ by under 2 of 6 (measured 9 October 2026; only the
text-heavy `A_5.0` and `title_2.0` would fail). Fonts are pinned by
`test_a_frame_drawn_in_a_fresh_process_uses_the_brands_fonts` in `test_frame.py`, which draws in
a new process as a command does, because on Linux fontconfig fixes its font list at a process's
first text call, so a frame drawn in the test process after other tests may not use the
brand's fonts at all.
