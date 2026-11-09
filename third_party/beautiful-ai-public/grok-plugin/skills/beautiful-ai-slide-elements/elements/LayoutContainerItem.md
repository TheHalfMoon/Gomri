# LayoutContainerItem

`LayoutContainerItem` is one cell of a `GridLayoutContainer` (`Dashboard`, `StackDiagram`, `PhotoCollage`). It paints
the cell background (`cellColor`, frame, rounded corners), optionally a one-line title above or below the content,
and builds exactly one child element chosen by `componentType`, whose model is `childElement`. The cell is the
unit the editor selects, moves and recolors; the component inside is what the agent actually fills in.

This file also covers the two tiny classes that only exist inside a cell: `LayoutPlaceholder` (the empty cell) and
`LayoutContainerTitleCaption` (the cell title).

## Model location

- `states[0].primary.items[]` for `Dashboard` (templates `dashboard`, `chart_line`, `chart_column`, `chart_bar`,
  `chart_area`, `chart_waterfall`, `chart_pie`, `table-v2`) and `StackDiagram` (`stackDiagram`).
- `states[0].primary.items[]` of `PhotoCollage` uses the subclass `PhotoCollageItem` (see `PhotoCollage.md`).
- The cell title model is `items[].chartTitle`; the component model is `items[].childElement`.

## Minimal example

One `items[]` entry: a titled chart cell.

```json
{
  "componentType": "Chart",
  "cellColor": "background_light",
  "showTitle": "above",
  "chartTitle": {
    "textAlign": "left",
    "chartTitle": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Active users" } ] }
  },
  "childElement": {
    "legendPosition": "off",
    "chartData": {
      "series": [ { "id": "series1", "name": "Users", "type": "line", "colorName": "chart1", "marker": "none",
                    "data": [ { "y": 120 }, { "y": 180 }, { "y": 260 } ] } ],
      "xAxis": { "categories": [ "Jan", "Feb", "Mar" ], "labels": { "enabled": true }, "showAxisLine": true },
      "yAxis": { "labels": { "enabled": true }, "showGridLines": true, "format": "number" },
      "yAxis2": { "visible": false, "opposite": true }
    }
  }
}
```

A text cell (`StackDiagram` style):

```json
{
  "componentType": "TextAndImage",
  "cellColor": "theme",
  "childElement": {
    "backdropPadding": 10,
    "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Platform layer" } ] }
  }
}
```

## Pitfalls

- `componentType` must match what is in `childElement`: a `"Chart"` with pie `data` renders the default sample
  line chart; a `"PieChart"` with `chartData` renders the default sample pie. Nothing warns.
- Omitting `componentType` (or misspelling it, e.g. `"Statistics"`, `"chart"`) yields an empty placeholder cell
  and the model is rewritten to `"GridPlaceholder"`.
- The title text is at `chartTitle.chartTitle.blocks`, not `chartTitle.blocks`; and it only shows when
  `showTitle` is `"above"`/`"below"`.
- Do not put component fields both on the item and in `childElement`; the flat copies are ignored and confuse
  later edits (stored examples contain such stale `value`/`changeLabel` duplicates).
- Small cells (e.g. 3 x 4 of 12 x 12 with a frame and a title) can fall under the component's minimum size and
  render blank; give charts/tables the larger cells.
- `cellColor` is per item; a missing one means a transparent cell, not the container's or the last item's color
  (only cells auto-added for extra `gridLayout.cells` copy the previous item's color).

## Rules and limits

- Inner padding around the component, from the theme (`childPadding` per component type): `Statistic` 20 px,
  `Chart` 20 px top/bottom 10 px left/right, `PieChart` 20 px, `RadialBar` 30 px, `Table` 20 px,
  `RadialBarChart` 30 px, `TextAndImage` 0. The padding on the title side is removed when a title is shown.
  Padding is dropped entirely for a single-cell grid whose cell has no `cellColor` (or `"none"`/`"transparent"`)
  and holds a `Chart`, `PieChart` or `Table` (the "plain chart slide" case).
- A container `frame` other than `"none"` deflates the cell by 20 px on every side (not for `TextAndImage`).
- Fit check: after title and padding, the remaining area must be at least the child's `minWidth` x `minHeight`
  (table above). If not, the child is **not rendered** (the cell shows only its background and, in the editor, a
  "does not fit" overlay). The slide itself still reports as fitting, so the error is silent.
- Cell background resolution: `cellColor` -> palette color with `itemIndex`/`maxCount` (so `"colorful"` rotates
  per cell); `"none"`/`"transparent"`/absent -> no fill, text contrasts with the slide background. A cell with an
  automatic color holding a transparent image whose artwork matches that color may get a contrasting "ink plate"
  color instead (measured at load time).
- Chart and PieChart cells animate their content instead of fading the cell; all other cells fade in as a unit.
- Migration (`migrationVersion` < 10.02 only): an item with `text` or `content_value` and no `componentType`
  becomes `componentType: "TextAndImage"` with those fields moved into `childElement` and the legacy
  `textPosition` mapped to `boxHAlign`/`verticalAlign`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `componentType` | string (required) | `"TextAndImage"`, `"Chart"`, `"PieChart"`, `"Table"`, `"RadialBar"`, `"Statistic"`, `"RadialBarChart"`, `"Canvas"`; anything else (including absent) is rewritten to `"GridPlaceholder"` | Picks the child class, see "Nested elements". |
| `childElement` | object | default: absent | The child component's model. **When absent, the child reads its fields from the item object itself** (shared model), which is why old slides and the app's own chart generator put `chartData`, `value`, ... directly on the item. Prefer a `childElement` object; when both exist only `childElement` is used. `{}` is valid for `Table`, `Statistic`, `RadialBar` and `Chart` (they fill defaults). |
| `cellColor` | string | palette color name (`"background_accent"`, `"background_light"`, `"background_dark"`, `"theme"`, `"accent1"`…, `"colorful"`, `"collection-…"`, `"theme-to-dark"`), `"none"`/`"transparent"` (no fill), `"use-image-background"`, any CSS color; default: absent = transparent | Fill of the cell. The child's text/colors are computed against it. `"colorful"` and `"<a>-to-<b>"` vary by item index. |
| `showTitle` | `false` \| `"above"` \| `"below"` | default `false`; `true` behaves like `"above"` | Shows `chartTitle` as a single scaled line at the top or bottom of the cell. Ignored when `componentType` is absent. |
| `chartTitle` | object | `{ "textAlign": "left" \| "center" \| "right", "chartTitle": { "blocks": [ … ] } }`; default `{}` | Model of the title text. Note the nesting: the text blocks live at `chartTitle.chartTitle.blocks` (the title element is named `chartTitle`, so it binds to that key inside its own model). Blocks use `"textStyle": "_use_styles_"`. |
| `id` | string | generated uuid when missing | Collection item id; also appears in chart annotation paths (`/primary/<id>/element`). |
| `dataSourceLink` | object | default none | Live spreadsheet link for Chart/PieChart/Table cells; leave absent. |
| `useV10Padding`, `wasMigratedFromV10` | boolean | internal | Migration flags written by the app; never set. |

Legacy flat fields on the item (`text`, `content_value`, `textPosition`, `textAlign`, `value`, `changeLabel`,
`positive`, `showChangeInValue`, …) come from pre-10.02 models. `text`/`content_value` without a `componentType`
are migrated into a `TextAndImage` `childElement`; the others are only read when `childElement` is absent (shared
model) and are otherwise stale leftovers.

### Nested elements

- `chartTitle` -> `LayoutContainerTitleCaption` (a `TextElement`, see `TextElement.md`): built only when
  `showTitle` is truthy; options `singleLine`, `autoHeight`, `scaleTextToFit`, `allowAlignment`. Reserves 15 px
  below it (Chart) / 20 px (PieChart), or 35 px / 20 px above it when `showTitle: "below"`. No animations.
- `element` -> the component, by `componentType`:

| `componentType` | Class | Doc | Minimum cell content size (w x h px) |
|---|---|---|---|
| `"TextAndImage"` | `TextAndImage` | `TextAndImage.md` | – |
| `"Chart"` | `Chart` | `Chart.md` | 75 x 75 |
| `"PieChart"` | `PieChart` | `PieChart.md` | 150 x 150 |
| `"Table"` | `TableFrame` | `Table.md` | 200 x 100 |
| `"Statistic"` | `Statistic` | `Statistic.md` | 50 x 20 |
| `"RadialBar"` | `RadialBarInfographic` | `RadialBarInfographic.md` | 25 x 25 |
| `"RadialBarChart"` | `RadialBarChart` | `RadialBarChart.md` | – |
| `"Canvas"` | `AuthoringCanvas` | `AuthoringCanvas.md` | – |
| `"GridPlaceholder"` / other | `LayoutPlaceholder` | below | 0 x 0 |

- `LayoutPlaceholder` ("Empty Cell"): has no model fields of its own; it renders nothing but the cell background
  and offers "add text / paste image" affordances in the editor. It is excluded from exports. A placeholder is
  what you get for any item whose `componentType` is missing or unknown.
