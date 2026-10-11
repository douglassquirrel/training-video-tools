# table — an invented data-driven element

## Identity

| Key | Value | Notes |
|---|---|---|
| name | table | |
| kind | code | |
| size | 300 200 | nominal: the natural size comes from its rows |
| fit | natural | the stub's `natural_size` gives 120 a column by 30 a row |

## Anchors

| Key | Value | Notes |
|---|---|---|
| title | computed | |
| row.* | computed | row N of the data, N from 1 |
| cell.*.* | computed | row N, column M |

## Parameters

| Key | Value | Notes |
|---|---|---|
| rows | rows | first row is the header |
| tab | label Sheet1 | |
| note | text | |
| rows-shown | integer 0 1000 1000 | |
| highlight.* | number 0 1 0 | strength of row N's highlight |
| highlight-colour.* | colour accent | |
| cell-alpha.*.* | number 0 1 1 | |
| striped | boolean false | |
| explode | boolean false | the stub refuses to draw when true, as the real library refuses in words |

## Indexes

| Key | Value | Notes |
|---|---|---|
| row.* | row | |
| cell.*.* | row column | |
| highlight.* | row | |
| highlight-colour.* | row | |
| cell-alpha.*.* | row column | |

## Colours

| Key | Value | Notes |
|---|---|---|
| line | rule | |
| fill | accent | what the stub fills the rect with |
