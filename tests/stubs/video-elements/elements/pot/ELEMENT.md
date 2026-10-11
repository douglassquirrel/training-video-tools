# pot — an invented SVG element with one state

## Identity

| Key | Value | Notes |
|---|---|---|
| name | pot | |
| kind | svg | |
| size | 24 24 | |
| description | An invented flower pot. | |

## Anchors

| Key | Value | Notes |
|---|---|---|
| rim | 12 4 | fixed, element units |
| base | 12 22 | |
| tab.* | computed | tab N: an index that does not count lines |

## States

| Key | Value | Notes |
|---|---|---|
| plain | element.plain.svg | |
| cracked | element.cracked.svg | the same drawing: the stub cross-fades nothing |

## Parameters

| Key | Value | Notes |
|---|---|---|
| text | text | a line a line, as the real `document` takes its page |
| line-alpha.* | number 0 1 1 | of line N |
| tab-box.* | number 0 1 0 | of tab N: an index that does not count lines |

## Colours

| Key | Value | Notes |
|---|---|---|
| fill | accent | what the stub fills the rect with |
