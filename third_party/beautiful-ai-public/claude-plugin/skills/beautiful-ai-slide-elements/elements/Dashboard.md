# Dashboard

`Dashboard` is the `GridLayoutContainer` subclass behind every data slide: a 12 x 12 grid of cells, each holding a
chart, pie chart, table, statistic, radial bar, text/image or empty placeholder. It is the root element
(`states[0].primary`) of the templates `dashboard`, `chart_line`, `chart_column`, `chart_bar`, `chart_area`,
`chart_waterfall`, `chart_pie` and `table-v2`; the single-chart templates are just a `Dashboard` whose default data
has one full-size cell with the matching component. Everything about the grid is in `GridLayoutContainer.md`,
everything about a cell in `LayoutContainerItem.md`; this file lists what `Dashboard` adds or changes.

## Model location

- `states[0].primary` for the templates above (`template_id` is any of them; the model shape is identical).
- Cells: `states[0].primary.items[]`; cell contents: `states[0].primary.items[].childElement`.

## Minimal example

A `dashboard` slide with a column chart on the left and two statistics on the right:

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Q3 performance" } ] } },
  "primary": {
    "layoutEngineType": "dashboard",
    "gridLayout": {
      "cols": 12, "rows": 12,
      "cells": [
        { "x": 0, "y": 0, "width": 8, "height": 12 },
        { "x": 8, "y": 0, "width": 4, "height": 6 },
        { "x": 8, "y": 6, "width": 4, "height": 6 }
      ]
    },
    "items": [
      {
        "componentType": "Chart",
        "cellColor": "background_light",
        "showTitle": "above",
        "chartTitle": { "textAlign": "left", "chartTitle": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Revenue by month" } ] } },
        "childElement": {
          "legendPosition": "off",
          "chartData": {
            "series": [ { "id": "series1", "name": "Revenue", "type": "column", "colorName": "chart1", "marker": "none",
                          "data": [ { "y": 120 }, { "y": 150 }, { "y": 180 } ] } ],
            "xAxis": { "categories": [ "Jul", "Aug", "Sep" ], "labels": { "enabled": true }, "showAxisLine": true },
            "yAxis": { "labels": { "enabled": true }, "showGridLines": true, "format": "currency", "formatOptions": { "decimal": 0, "separator": true, "currency": "$", "abbreviated": "lower" } },
            "yAxis2": { "visible": false, "opposite": true }
          }
        }
      },
      {
        "componentType": "Statistic",
        "cellColor": "background_accent",
        "showTitle": "above",
        "chartTitle": { "textAlign": "left", "chartTitle": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "New accounts" } ] } },
        "childElement": {
          "ornamentType": "capsule",
          "horizontalAlign": "left",
          "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "48,500" } ] },
          "changeLabel": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "12%" } ] },
          "note": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "vs last quarter" } ] },
          "positive": true
        }
      },
      {
        "componentType": "RadialBar",
        "cellColor": "background_accent",
        "childElement": {
          "value": 76, "format": "percent", "color": "theme", "showValue": true,
          "labelPosition": "bottom",
          "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Retention" } ] }
        }
      }
    ]
  }
}
```

For `chart_*` / `table-v2` slides use one cell `{ "x": 0, "y": 0, "width": 12, "height": 12 }`, one item with
`cellColor: "none"` and the component model from `Chart.md`, `PieChart.md` or `Table.md`.

A statistic with a description instead of a change capsule (a metric and what it is, the usual case next to a
chart) is `"ornamentType": "text"` with the description in `note` and no `changeLabel`:
`{ "ornamentType": "text", "horizontalAlign": "left", "value": { "blocks": [ … "57%" … ] }, "note": { "blocks": [ … "of GDP from services" … ] } }`.
`showChangeInValue` is not read; only `ornamentType` decides what shows under the value (`Statistic.md`).

## Pitfalls

- A `chart_line` slide is not special: if you put a `Table` item in it, it renders a table. Conversely a
  `dashboard` slide can hold a single chart. Pick the `template_id` that matches the content so the editor's
  "switch template" options make sense.
- Stored examples carry `cellColor`, `formatOptions`, `customGridCols` and `showTitle` on `primary`: only
  `showTitle` means anything to the editor, none of them affect rendering. Per-cell `cellColor` is what counts.
- Do not write legacy `items[].chart` / `items[].piechart` / `items[].elementType`; use `componentType` +
  `childElement`.
- The legacy flat `table-v2` shape (`primary.cols/rows/cells`) only works because of the migration; new models
  must use the `items[]` shape with `componentType: "Table"`.
- Titles need both `items[].showTitle` and `items[].chartTitle.chartTitle.blocks`; the container `showTitle` does
  nothing by itself.

## Rules and limits

- Everything in `GridLayoutContainer.md` applies (items padded/truncated to the cell count, clipping, gutters,
  rounded corners, fit check per cell).
- A single cell holding a `Chart`, `PieChart` or `Table` with no `cellColor` (or `"none"`) gets no inner padding:
  this is how the `chart_*` and `table-v2` slides look like plain charts.
- Slide ideas / template switching are disabled for multi-cell dashboards.
- Migration `_migrate_10_02` (runs only when the stored `migrationVersion` < 10.02) rewrites the whole model:
  for `table-v2` a flat table model (`cols`/`rows`/`cells` directly on `primary`) becomes
  `items: [{ componentType: "Table", childElement: <table>, cellColor: "none" }]`; for every other item it assumes
  the pre-10.02 shape (`elementType: "piechart"` + `piechart`, or `chart`) and sets `componentType`/`childElement`
  from those keys, and a legacy `layout` name (`"2-charts-vertical"`, `"3-charts-left"`, ...) becomes a preset
  index. On a modern model this migration destroys the items (every non-pie item becomes a `Chart` with
  `childElement: undefined`), so always store `migrationVersion: 10.03`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Same as `GridLayoutContainer.md`, with these differences:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` | array (required) | see `LayoutContainerItem.md` | Cells. The default for an auto-added cell is `{ childElement: {} }` (no `componentType`, i.e. an empty placeholder). |
| `gridLayout` | object | default `{ cols: 12, rows: 12, cells: [{ x: 0, y: 0, width: 12, height: 12 }] }` | Any consistent 12 x 12 layout renders; the editor's presets are listed below. |
| `layoutEngineType` | string | default `"dashboard"` (written by the schema); `"custom"` with `customGridCols`/`customGridRows` is the other value seen in real slides | Keep `"dashboard"`. |
| `showGutter` | – | always `true` (getter ignores the model) | 10 px gaps between cells. |
| `cellFrameType` | string | `"none"` (written by the schema) | Not read by any code; harmless. |
| `showTitle` | `false` \| `"above"` \| `"below"` | the app sets `"above"` on the container whenever the cell count becomes > 1 | Editor hint only; per-cell `items[].showTitle` controls real titles. |
| `fullBleed`, `frame`, `borderColor`, `borderShadow` | – | see `GridLayoutContainer.md` | |

Template flags (all eight templates): `variations: "tabular"`, `allowColorBackgrounds: false`, `allowColorful:
true`, header allowed (`layout.headerPosition` `"top"`/`"left"`/`"none"`), trays allowed (`chart_column`,
`chart_bar`, `chart_area`, `chart_pie` default an added image to the right tray).

Template `defaultData` (what an empty slide starts with):

- `dashboard`: `gridLayout` cells `[8x12 at 0,0] [4x6 at 8,0] [4x6 at 8,6]` with items `Chart` (default column
  chart), `Statistic` (`cellColor: "background_accent"`), `RadialBar` (`cellColor: "background_accent"`).
- `chart_line` / `chart_column` / `chart_bar` / `chart_area`: one `Chart` item with the default chart model of that
  series type (8 monthly categories, one `series1` of 8 points, see `Chart.md`).
- `chart_waterfall`: one `Chart` item with the default waterfall model (10 categories, `"sum"` points).
- `chart_pie`: one `PieChart` item with the default 3-slice pie (see `PieChart.md`).
- `table-v2`: one `Table` item with `tableWidth: 1, tableHeight: 1, showTopLeftCell: true, showColGridLines: true,
  showRowGridLines: true` (the table itself fills in a 5 x 4 default grid, see `Table.md`).

### Nested elements

- `items[]` -> `LayoutContainerItem` (`LayoutContainerItem.md`); one per `gridLayout.cells[]` entry, by index.
- Hard item limit 10 (editor add/paste only). The editor presets go up to 8 cells; the app's own slide generator
  produces up to 12; rendering does not cap.

Editor presets (`cols: 12, rows: 12`), given as `x,y,w,h` per cell, in item order:

| Cells | Layouts |
|---|---|
| 1 | `0,0,12,12` |
| 2 | `0,0,6,12 / 6,0,6,12` (side by side); `0,0,12,6 / 0,6,12,6` (stacked) |
| 3 | `0,0,4,12 / 4,0,4,12 / 8,0,4,12`; `0,0,6,12 / 6,0,6,6 / 6,6,6,6` (big left); `0,0,6,6 / 0,6,6,6 / 6,0,6,12` (big right); `0,0,12,6 / 0,6,6,6 / 6,6,6,6` (big top) |
| 4 | 2 x 2 grid `0,0,6,6 / 0,6,6,6 / 6,0,6,6 / 6,6,6,6`; `0,0,4,4 / 0,4,4,4 / 0,8,4,4 / 4,0,8,12`; `0,0,8,12 / 8,0,4,4 / 8,4,4,4 / 8,8,4,4`; `0,0,4,4 / 4,0,4,4 / 8,0,4,4 / 0,4,12,8` |
| 5 | `0,0,6,6 / 6,0,6,6 / 0,6,4,6 / 4,6,4,6 / 8,6,4,6`; `0,0,12,8 / 0,8,3,4 / 3,8,3,4 / 6,8,3,4 / 9,8,3,4` |
| 6 | 3 x 2 grid of `4x6`; `0,0,6,6 / 6,0,6,6 / 0,6,3,6 / 3,6,3,6 / 6,6,3,6 / 9,6,3,6` |
| 7 | `0,0,4,6 / 4,0,4,6 / 8,0,4,6 / 0,6,3,6 / 3,6,3,6 / 6,6,3,6 / 9,6,3,6`; `0,0,6,12` + six `2x6` cells on the right |
| 8 | 4 x 2 grid of `3x6` |
