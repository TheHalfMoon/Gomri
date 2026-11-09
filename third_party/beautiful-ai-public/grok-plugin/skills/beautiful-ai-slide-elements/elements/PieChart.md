# PieChart

`PieChart` renders a pie or donut from one list of `{ value, label }` slices, with a value label (percentage by
default) and the slice name either on/next to each slice or in a legend. It is the `childElement` of a
`LayoutContainerItem` with `componentType: "PieChart"` (template `chart_pie`, or any `dashboard` cell). It is a
collection whose items are the slices; this file also covers its internal classes `PieChartWedge` (one slice),
`PieChartLabel` (the slice's value + name), `PieChartLegend` and `PieChartLegendItem`.

## Model location

- `states[0].primary.items[].childElement` of a `Dashboard` cell with `componentType: "PieChart"` (legacy models
  put the same fields directly on the item).
- Slices: `<pie model>.data[]` (the collection property is `data`, not `items`).

## Minimal example

`items[].childElement` of a `componentType: "PieChart"` cell (template `chart_pie`, single cell with
`cellColor: "none"`):

```json
{
  "isDonut": false,
  "innerRadius": 0,
  "format": "percent",
  "sortValues": true,
  "collectionColor": "theme-to-dark",
  "legendPosition": "right",
  "data": [
    { "value": 45, "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Enterprise" } ] } },
    { "value": 30, "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "SMB" } ] } },
    { "value": 15, "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Partners" } ] }, "emphasized": true },
    { "value": 10, "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Services" } ] } }
  ]
}
```

Donut: `"isDonut": true, "innerRadius": 50` (`innerRadius` is a percentage of the radius, 0–100; `0.5` is a hole
you cannot see). `emphasized` pulls the slice 30 px out of the pie. A lone pie with `legendPosition: "right"` sits
left of center and leaves the right of the slide empty: use `"bottom"`, or put a statistic cell beside it in a
`dashboard`.

## Pitfalls

- The slice array is `data`, not `items`; `chartData`/`series` belong to `Chart` and are ignored here (you get
  the default sample pie).
- Values are plain numbers in `data[].value`; do not write strings or `{ "y": … }` points.
- `legendPosition` must be exactly one of the four sides; `"off"`/`true` give no legend and labels on slices.
- `format: "percent"` ignores `formatOptions.divideBy100`-style tricks: shares are always computed from the
  total. Use `"number"` to show the raw numbers (e.g. revenue).
- Leaving `chartScale` out is fine (auto-fit); setting it to `1` with outside labels clips the labels.
- Stored examples contain stale `labelFormat`, `startRadius`, `offset`, `annotations` and per-slice
  `accentColor`/`titleTextStyle`; none of them are needed.
- Color names `"accentN"` beyond the theme's accents fall back to `"theme"`, so several slices can end up the
  same color; prefer `"chart1"`…`"chart6"` or a `collectionColor` range.

## Rules and limits

- Minimum content size 150 x 150 px, otherwise the cell renders empty.
- Slices below 1 % of the total are drawn at 1 % (the others are rescaled); if every value is 0 all slices are
  set to 1 (equal shares); if all but one are 0 the last gets a hair-line slice flagged `showZeroFlag`.
- `chartScale` is clamped to [0, 1] at build; when absent the first render runs an auto-fit (shrinking the
  radius in 5 px steps up to 25 times) and stores the result.
- Percent labels are `value / total`; `format: "number"` shows `value` as entered (apply `formatOptions`
  for currency/decimals).
- Migrations: `_migrate_10` (stored version < 10) sets `formatOptions.decimal = 2` for percent pies without
  options; `_migrate_10_02` turns `color: "auto"` into `null` and sets `collectionColor` to `"<slide color>-to-dark"`.
  Not run for models stored with `migrationVersion: 10.03`.
- Legacy pre-10.02 dashboards stored the pie as `items[].piechart` with `elementType: "piechart"`; that shape is
  only understood by the `Dashboard` migration.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `data` | array (required) | absent -> the default 3 slices (Apple 3, Pear 2, Orange 5) are written | The slices, see below. |
| `data[].value` | number (required) | `null` is turned into `0` | Slice size. Percentages are `value / sum(values)`. |
| `data[].label` | text object | `{ "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Apple" } ] }`; a plain string or `{ "text": "Apple" }` is converted to blocks on first render | Slice name (shown on the slice or in the legend). |
| `data[].color` | string \| null | palette color name (`"chart1"`…, `"accent1"`…, `"theme"`); default `null` = taken from `collectionColor` by slice index | Slice fill. |
| `data[].emphasized` | boolean | default `false` | Pulls the slice 30 px out of the pie. |
| `data[].id` | string | `"wedge<index>"`, (re)assigned at every build in display order | Internal; do not rely on it. |
| `data[].offset`, `data[].showZeroFlag` | – | defaults / internal | `offset` is written by the default model but not read; `showZeroFlag` is set by the renderer when all other slices are 0. |
| `isDonut` | boolean | default `false` | Donut instead of pie. |
| `innerRadius` | number | 0-100 (percent of the outer radius); `0`/absent -> theme default 50 | Donut hole size; only used when `isDonut` is `true`. |
| `format` | string | `"percent"` (default), `"number"`, `"none"` | Value label format: `"percent"` shows the slice share of the total, `"number"` the raw value, `"none"` hides value labels (names still show unless a legend is on). |
| `formatOptions` | object | formatter options (`decimal`: number or `"auto"`, `separator`, `abbreviated`, `currency`, ...); default `{ decimal: "auto", separator: true, abbreviated: false, currency: "$", ... }` | Formatting of the value label. |
| `labelFormat` | string | legacy `"percentage"` \| `"numeric"` \| `"none"` | Pre-2019 name of `format`; converted when `format` is absent. Write `format` instead. |
| `sortValues` | boolean | default `false` | `true` draws slices in descending value order (the stored `data` order is kept). |
| `chartScale` | number | 0-1; absent -> auto-fit computes the largest radius whose labels fit and writes it | Pie radius as a fraction of the available radius. `1` = fill the cell (outside labels may be clipped). |
| `labelScale` | number | 0-1, default 1 | Maximum text scale of slice labels. |
| `labelPosition` | string | `"auto"` (default), `"outside"` | `"auto"` puts labels inside slices when they fit (and the cell is at least 300 x 300), otherwise outside with a leader line. |
| `startAngle` | number | degrees, default `0` (first slice starts at 3 o'clock, slices run clockwise) | Rotation of the pie; `-90` starts at 12 o'clock. |
| `legendPosition` | string | `"left"`, `"right"`, `"top"`, `"bottom"`; any other value/absent = no legend | Shows a legend with a color dot and the slice name; slice names are then removed from the slices (values stay). Top/bottom legends wrap into rows. |
| `collectionColor` | string | default `"theme"`; typical `"theme-to-dark"`, `"colorful"`, `"collection-<id>"`, `"chart2-to-light"` | Palette used for slices without their own `color` (shaded ranges and collections vary by slice index). |
| `startRadius`, `annotations` | – | defaults / legacy | Not read. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `data[]` -> `PieChartWedge` (one per slice, display order = `data` order, or descending value when
  `sortValues`): an SVG wedge path plus a `PieChartLabel`.
  - `PieChartLabel` -> `value` (`TextElement`, read-only, text = formatted value, omitted when `format` is
    `"none"`) and `label` (`TextElement` bound to `data[].label`, omitted when a legend is shown). Labels are placed
    inside the slice at 58 % of the radius, or outside (10 px past the rim, aligned away from the center) when
    they would cross a slice edge, when the pie is a donut, when `labelPosition` is `"outside"` or when the cell
    is smaller than 300 x 300. Overlapping outside labels are rotated/pushed outward and get a leader line.
- `legend` -> `PieChartLegend` (only when `legendPosition` is one of the four sides), a collection over the same
  `data[]` whose `PieChartLegendItem`s show a color circle and the slice `label` (editable in the editor). Vertical
  list on the left/right, wrapping rows on top/bottom, 40 px gap from the pie.
- Slice count: no minimum beyond 1; the data-import path caps at 15 slices (`PIE_CHART_MAX_ITEMS`); rendering
  itself does not cap, but more than ~8 slices run out of label space.
