# An invented video-elements library, for the tests

The shape of the real repository (`~/projects/code/video-elements/`, read-only from here): a
package `videoelements/` with `library.open(path, renderer)`, `names()`, `element(name)`,
`credits(names)` and `cli.Failure` with `.problems`, and two tiny invented elements under
`elements/` with `ELEMENT.md` and `PROVENANCE.md` in the rows video-elements settled on
10 October 2026 (PLAN.md item 15, "Settled" 27), plus a register `licenses/SOURCES.md`. The
package here is a stub that reads those files into the same plain data the real one exposes; it
checks far less than the real reader (a missing root, `elements/` or register, an unknown name)
and draws nothing until the increment that needs it. Nothing here is from any real element or
source. The `table` has `fit` `natural` and a `natural_size` (120 a column by 30 a row of its
rows; video-elements' note of 10 October 2026, 23:32), the `pot` the default `ratio`. Each has an `## Indexes` table, read into `counts` as the
real reader does (video-elements `d203f0a`): what each index of an indexed name counts; a `rows`
parameter may be written `rows header=NAME`. The table's draw gives row and cell anchors only for
the rows on show (`rows-shown`). Tests point `--elements` or `VIDEO_ELEMENTS_DIR` at this folder.
