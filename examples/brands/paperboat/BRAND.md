# Brand kit: Paperboat Press

*An invented brand for video-tools' example video (`examples/videos/paper-boat/`), written by
Claude on 9 October 2026. Nothing here comes from a real brand. Its shape follows the
training-video project's brand-kit convention: the tables under **Identity, Colours, Fonts,
Mark, Illustration** and **Settings** are read by the tools (first column the key, second the
value; the Fonts table's third column is the file); every other column and all prose is for
people. Paths are relative to this folder.*

## Identity

| Key | Value | Notes |
|---|---|---|
| name | Paperboat Press | The wordmark. |
| website | paperboat.example | Shown on the end card. |
| tagline | Small things, folded well | Not used in videos. |
| illustration-credit | Illustrations by the Paperboat crew | The end card's credit line. |

## Colours

| Key | Value | Used for |
|---|---|---|
| background | #F7F3EA | The frame behind everything (a warm paper white). |
| surface | #FFFFFF | Panels, cards, the inset frame. |
| ink | #2B2B2B | Text, the caption band. |
| muted | #6B6560 | Secondary text. |
| rule | #DAD2C4 | Rules and panel borders, future steps in the tracker. |
| grid | #D6CDBC | The dot grid in the animation area. |
| accent | #1F6F8B | The roundel, step letters, arrows, highlights, text of 24 px or more. |
| accent-dark | #15506A | Accent for text under 24 px (Settings, small-text-accent). |
| accent-light | #CFE3EA | Tints of the accent. |
| mistake | #A33A2E | "Mistake" panels and the "COMMON MISTAKE" tag. |
| correct | #3E7D4F | "Right way" panels and ✓ badges. |
| on-accent | #FFFFFF | Text on accent, mistake and correct fills. |

## Fonts

| Key | Value | File | Notes |
|---|---|---|---|
| display | PBS SemiBold | fonts/PBS-SemiBold.ttf | Titles, step letters, panel headings. |
| body | PBS Regular | fonts/PBS-Regular.ttf | Running text, credits, captions. |
| italic | PBS Italic | fonts/PBS-Italic.ttf | Subtitles, the web address, image captions. |

The three files are static instances of EB Garamond (SIL Open Font License 1.1, `fonts/OFL.txt`),
subset to Latin and renamed `PBS …` so that cairo's simple text API can choose a weight, and so
that the reserved name "EB Garamond" is not used for a modified font. `display-medium`,
`body-medium`, `bold` and `italic-medium` are not given, so they fall back as the tools say.

## Mark

| Key | Value | Notes |
|---|---|---|
| shape | circle | |
| fill | accent | |
| letter | P | |
| letter-colour | on-accent | |
| letter-font | display | |
| wordmark | Paperboat Press | Display font, ink, to the right of the circle. |
| reference | images/roundel.png | For checking the drawn roundel; never pasted. |

## Illustration

| Key | Value | Notes |
|---|---|---|
| end-card | images/boat-ink.png | A paper boat on waves, ink on a transparent background, 980 px wide. |

## Settings

| Key | Value | Notes |
|---|---|---|
| font-size-scale | 1.12 | Multiplies every font size. |
| background-grid | dots 40 2 0.55 | Spacing and dot size in pixels, opacity. |
| caption-band | ink | The band's fill. |
| caption-rule | accent 4 | Colour and height of the rule along its top. |
| small-text-accent | accent-dark 24 | Below this size, text that would be accent uses accent-dark. |
| title-rule | accent 3 | Colour and height of the short rule under titles. |
| label-shape | pill | Labels and callouts as rounded pills. |

## Rules

1. Mistake and correct are never the accent, and never colour alone: ✗ and "MISTAKE", ✓ and
   "RIGHT WAY".
2. A subject's colours stand clear of the background.
3. Text under 24 px uses accent-dark.
