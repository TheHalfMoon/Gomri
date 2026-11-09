# Table

`Table` renders a grid of text/number/icon cells with styled header, summary, emphasized and "clean" rows and
columns, grid lines, an outer border and optional alternating row tint. Its model is held by `TableFrame`, the
element a `LayoutContainerItem` builds for `componentType: "Table"`; `TableFrame` centres the table in the cell at
`tableWidth` x `tableHeight` of the available area and `Table` lays out the cells. Templates: `table-v2` (one
full-size table cell) and any `dashboard` cell. This file also covers the internal classes `TableCell` (a plain
object per cell, not an element), `TableCellIcon` (icon/logo cell content), `TableGridLines` and
`TableBackgrounds` (SVG layers).

## Model location

- `states[0].primary.items[].childElement` of a `Dashboard` cell with `componentType: "Table"`.
- Legacy `table-v2` slides stored the same fields directly on `states[0].primary` (`cols`, `rows`, `cells`, ...);
  the `Dashboard` migration wraps them into a single `Table` cell. New models must use the `items[]` shape.
- Columns, rows and cells: `<table model>.cols[]`, `.rows[]`, `.cells[]`.

## Minimal example

`items[].childElement` of a `componentType: "Table"` cell (template `table-v2`: one `12 x 12` cell with
`cellColor: "none"`), 3 columns x 3 rows with a header row:

```json
{
  "tableWidth": 1,
  "tableHeight": 1,
  "showTopLeftCell": true,
  "showBorder": true,
  "showColGridLines": true,
  "showRowGridLines": true,
  "tableBackgroundColor": "background_light",
  "color": "theme",
  "cols": [
    { "index": 0, "style": "headerCol", "size": 1.5 },
    { "index": 1, "style": "defaultCol", "size": 1 },
    { "index": 2, "style": "emphasizedCol", "size": 1 }
  ],
  "rows": [
    { "index": 0, "style": "headerRow", "size": 1 },
    { "index": 1, "style": "defaultRow", "size": 1 },
    { "index": 2, "style": "defaultRow", "size": 1 }
  ],
  "cells": [
    { "row": 0, "col": 0, "cellText": { "text": "Feature" } },
    { "row": 0, "col": 1, "cellText": { "text": "Basic" } },
    { "row": 0, "col": 2, "cellText": { "text": "Pro" } },
    { "row": 1, "col": 0, "cellText": { "text": "Users" } },
    { "row": 1, "col": 1, "cellText": { "text": "5" }, "format": "number" },
    { "row": 1, "col": 2, "cellText": { "text": "Unlimited" } },
    { "row": 2, "col": 0, "cellText": { "text": "SSO" } },
    { "row": 2, "col": 1, "format": "icon", "content_type": "icon", "content_value": "x", "cellStyle": "text", "cellColor": "negative" },
    { "row": 2, "col": 2, "format": "icon", "content_type": "icon", "content_value": "check-yes", "cellStyle": "text", "cellColor": "positive" }
  ]
}
```

## Pitfalls

- `cells` is a flat list keyed by `row`/`col`, not a 2-D array; forgetting a pair yields an empty cell, a wrong
  index yields a dropped cell. Generate cells from `rows x cols`.
- `format` must match the text: a `"currency"` cell with `"n/a"` or a `"percent"` cell with `"45"` (no `%`,
  shows `4500%`) renders wrong. Default to `"text"` and only use numeric formats for numbers.
- The header is the row/column `style`, not `showHeaderRow`/`showHeaderCol` (ignored).
- `size` must be present on every row/column or on none; a single missing `size` counts as weight 1 and
  distorts the others.
- `cellStyle` without `cellColor` uses `"primary"` (text color): a `"fill"` cell would be filled with the text
  color. Always pair `cellStyle` with a `cellColor`.
- Icon cells need `format: "icon"` **and** `content_type`/`content_value`; a `cellText` on an icon cell is
  ignored. Do not leave `__generateImage` on logo cells you fill yourself.
- More than ~8 columns or ~12 rows gets hard to read at slide size; the renderer only starts shrinking fonts
  beyond 25 x 25.

## Rules and limits

- Completeness: the renderer recreates any missing (row, col) cell as `{ format: "text" }` and drops cells whose
  `row`/`col` do not exist, so the table always has `rows.length * cols.length` cells after a render; author them
  all to keep ids stable.
- `index` values must match positions (`cols[i].index === i`); the code looks cells up by `index`, so gaps or
  duplicates produce missing/duplicated cells.
- Sizes are weights, not pixels: a column with `size: 2` is twice as wide as `size: 1`; the table always fills
  `tableWidth` x `tableHeight` of the cell.
- Header text style is applied by `style` (`headerRow`/`headerCol`), not by position; the first row is a normal
  row unless its style says otherwise.
- Numeric formats parse the text with numeral: `"$1,200"`, `"1200"`, `"45%"`, `"-3.5"` all work; non-numeric text
  under a numeric format is not displayed as written, so keep `format: "text"` for words.
- The emphasized column overflows the table box by 5 % above and below; leave room when `tableHeight` is 1.
- Migration `_migrate_10_02` (stored `migrationVersion` < 10.02): sets `color` to the slide color and clears
  `cellStyle: "fill"` on header-row cells. The flat `table-v2` shape is migrated by `Dashboard`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `cols` | array (required) | see below; `[]` with empty `cells` -> a default 5 x 4 table is written | Column definitions in order. |
| `rows` | array (required) | see below | Row definitions in order. |
| `cells` | array (required) | one entry per (row, col) pair | Cell contents. Missing pairs are recreated as empty text cells; entries pointing to a non-existing row/col (or `null`) are dropped. |
| `tableWidth` / `tableHeight` | number | 0-1, schema default `1` / `1` | Fraction of the cell area the table occupies (centred). The editor's auto-fit toggles these. |
| `showTopLeftCell` | boolean | default `true` | `false` hides the top-left cell (no fill, no border): use with a header row + header column. |
| `showBorder` | boolean | default `true` | Outer border lines. |
| `showColGridLines` / `showRowGridLines` | boolean | default `true` / `true` | Inner vertical / horizontal lines. |
| `tableBackgroundColor` | string | palette color name; schema default `"background_light"` (`"background_dark"`, `"background_accent"` in examples) | Base fill of the table. |
| `color` | string | palette color name; schema default `"theme"` | Accent color: header-row fill, summary-row / summary- and emphasized-column tint (25 %), emphasized-column outline. |
| `alternateRows` | boolean | default `false` | Tints every odd `defaultRow` by 6 %. |
| `matchCellFontSizes` | boolean | default `true` | When `true`, cells without their own `fontSize` share one size that shrinks for tables denser than 25 x 25 (min 6 px). |
| `dataSourceLink` | object | default none | Live spreadsheet link; leave absent. |
| `showHeaderRow`, `showHeaderCol`, `autoFit` | – | written by the template / legacy models | Not read by the current renderer (row/column `style` is what matters). |

#### `cols[]` / `rows[]`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `index` | number (required) | 0-based, unique, matching the array position | Column / row id referenced by `cells[].col` / `cells[].row`. Entries without an index are removed. |
| `style` | string | columns: `"defaultCol"` (default), `"headerCol"`, `"emphasizedCol"`, `"summaryCol"`, `"cleanCol"`; rows: `"defaultRow"` (default), `"headerRow"`, `"summaryRow"`, `"cleanRow"` | Visual role. `headerRow`: filled with `color`, header text style. `headerCol`: 5 % tint, header text style. `summaryRow`/`summaryCol`: 25 % `color` tint (totals). `emphasizedCol`: 25 % tint, drawn 10 % taller than the table with a 2 px `color` outline (the "recommended plan" column). `cleanRow`/`cleanCol`: no fill and no grid lines (section labels / spacer). |
| `size` | number | relative weight, default `1`; the default table uses 50/60 for columns and 40/30 for rows | Width / height share: `colWidth = size / sum(sizes) * tableWidth`. Omit for equal columns. |
| `break` | boolean | default `false`; always `false` on the last column/row | Adds a gap after this column / row (visually splits the table). |
| `scale`, `autoSize` | – | internal / legacy | Written by auto-fit; not needed. |

#### `cells[]`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `row` / `col` | number (required) | indexes into `rows[]` / `cols[]` | Cell position. Every (row, col) pair must appear exactly once. |
| `id` | string | generated when missing | Internal key. |
| `cellText` | object | `{ "text": "Q1 revenue" }`; default none (empty cell) | Cell text. `"\r"` inside the string starts a new line. A text starting with `=` is evaluated as a spreadsheet formula over other cells (`=SUM(B2:B4)`, columns `A…`, rows `1…`). |
| `format` | string | `"text"` (default), `"number"`, `"currency"`, `"percent"`, `"date"`, `"icon"` | How `cellText.text` is displayed: numeric formats re-format the text with `formatOptions` (`"1200"` -> `1,200`, `"45%"` -> `45%`); `"date"` reformats with `formatOptions.dateFormat`; `"icon"` ignores the text and shows `content_value`. |
| `formatOptions` | object | `{ "decimal": 0, "separator": true, "abbreviated": false, "changeStyle": "none" \| ">" \| "+", "changeColor": true, "currency": "$", "dateFormat": "MMM Do", "accountingStyle": false, "textAlign": "left" \| "center" \| "right" }`; default: formatter defaults, `textAlign` from the column/row style (centre) | Number formatting and alignment. `changeStyle: ">"` adds up/down arrows, `"+"` a sign; `changeColor` colors negative/positive numbers; `accountingStyle` puts the currency symbol at the left edge and negatives in parentheses. |
| `fontSize` | number | px; default from the row/column style | Per-cell font size (disables the shared size for this cell). |
| `bold` / `italic` / `strikeThrough` | boolean | default `false` | Text styling. |
| `cellStyle` | string | `"none"` (default), `"text"`, `"fill"`, `"stroke"`, `"flag"` | Per-cell color treatment using `cellColor`: `"text"` colors the text, `"fill"` fills the cell (text in primary), `"stroke"` draws a 2 px border, `"flag"` puts a small triangle in the top-right corner. |
| `cellColor` | string | palette color name (`"positive"`, `"negative"`, `"theme"`, `"accent1"`…); default `"primary"` | Color used by `cellStyle`. |
| `content_type` / `content_value` | string | `format: "icon"` only: `content_type` `"icon"` with an icon key (`"check-yes"`, `"x"`, …), or `"logo"` / `"image"` with an asset id | Icon or image shown in the cell (see `ContentElement.md`). Icons take the cell text color (`cellColor` with `cellStyle: "text"`). |
| `link` | string | URL | Makes the cell a hyperlink. |
| `linkToSlide` | string | slide id | Editor link to another slide. |
| `width` / `height` | number | default 1 | Merged cell span (editor feature); the covered cells carry `isHidden: true`. Not verified in stored examples. |
| `isHidden` | boolean | default `false` | Hides the cell (used for merged cells). |
| `emphasized`, `color`, `aoi*`, `scale`, `version` | – | legacy / image crop data | Not needed when authoring. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `table` -> `Table` (shares the `TableFrame` model).
  - `cells[]` -> `TableCell` objects (plain JS, one per model cell) rendered as absolutely positioned divs.
  - `cells[]` with `format: "icon"` -> `TableCellIcon` (a `ContentElement`, see `ContentElement.md`; model = the
    cell) sized to the shortest icon cell so icons match.
  - `tableBackground` -> `TableBackgrounds` and `tableGridLines` -> `TableGridLines`: SVG layers drawing cell
    fills, grid lines, border and the emphasized-column outline. No model fields.
- Limits: `MAX_COLS` / `MAX_ROWS` 60 (editor); minimum content size 200 x 100 px; auto-fit minimum column width
  50 px and row height 30 px; tables over 25 x 25 cells switch to a lightweight layout (no cell padding,
  shrunken font).
