# Statistic

`Statistic` renders one big number (the "value") with an optional ornament under it: a change-in-value capsule
(arrow + percentage + note), a plain description line, a progress bar, or a sparkline chart. It is the
`childElement` of a `LayoutContainerItem` with `componentType: "Statistic"` (the second default cell of the
`dashboard` template and the most common dashboard cell). Its label/title is not part of this element: use the
cell's `showTitle`/`chartTitle` (`LayoutContainerItem.md`). This file also covers its internal classes
`StatisticValue`, `StatisticDescription`, `StatisticChangeInValue` and `StatisticProgressBar`.

## Model location

- `states[0].primary.items[].childElement` of a `Dashboard` cell with `componentType: "Statistic"` (legacy
  models put the same fields directly on the item).
- All ornaments share this same model object (they are built without a model of their own), so `changeLabel`,
  `note`, `positive`, `progressBarValue`, `chartData`, ... sit next to `value`.

## Minimal example

`items[].childElement` of a `componentType: "Statistic"` cell (title via the cell's `showTitle`/`chartTitle`):

```json
{
  "ornamentType": "capsule",
  "horizontalAlign": "left",
  "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "48,500" } ] },
  "changeLabel": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "12%" } ] },
  "note": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "vs last quarter" } ] },
  "positive": true
}
```

Description only (the app's generator shape):

```json
{
  "ornamentType": "text",
  "horizontalAlign": "left",
  "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "2.4M" } ] },
  "note": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "monthly active users" } ] }
}
```

Progress bar: `{ "ornamentType": "bar", "progressBarValue": 0.65, "value": { … } }`. Nothing under the value:
`{ "ornamentType": "none", "value": { … } }`.

## Pitfalls

- Always set `ornamentType`. Omitting it gives the change capsule with the schema defaults `100%` / up arrow,
  even if you wrote `showChangeInValue: false`.
- `note` is used by both `"capsule"` (trailing note) and `"text"` (description); `changeLabel` only by
  `"capsule"`. A `"text"` ornament with no `note` renders an empty line.
- The value is a single line: long text is shrunk, not wrapped. Keep it short (`"$1.2M"`, `"48%"`).
- The `note` shrinks with its length too: a sentence under a big value ends up unreadably small. Keep it to one
  short line of about 8 words ("of GDP comes from services, up from 41% in 2005"); the cell title takes the metric name.
- `label` does not render; put the metric name in the cell title (`showTitle: "above"` + `chartTitle`) or in `note`.
- The stored examples carry `value.text` next to `value.blocks` with different content; only `blocks` is used.
- `positive: false` flips the arrow and uses the negative color; it does not add a minus sign to `changeLabel`.
- Keep `value`/`changeLabel`/`note` as single-block text with `textStyle: "_use_styles_"`; other text styles
  override the statistic styling.

## Rules and limits

- Layout: ornament height 20 px (10 px in cells under 90 px tall), 50 px (30 px) for sparklines, plus a 30 px
  (15 px) gap; the value takes the rest and is vertically centered. A statistic with `ornamentType: "none"` in a
  grid row where another cell has an ornament still reserves the ornament space so values line up.
- Minimum content size 50 x 20 px.
- The cell padding is 20 px on every side (minus the title side when a title is shown).
- `value.blockFontScales` (`{ "_use_styles_": 1.5 }`) is honoured as a user font scale on top of the fit scale;
  copy it from examples only if you want that exact size.
- Children are not animated individually; the statistic animates as one block.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | text object (required) | `{ "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "$50,000" } ] }`; schema default `{ "text": "$50,000" }` (a `text` string is converted to blocks on first render) | The big number. Single line, scaled to fit the cell. |
| `ornamentType` | string | `"capsule"` (schema default, written when absent), `"none"`, `"text"`, `"bar"`, `"sparkline"` | What is shown under the value: change-in-value capsule, nothing, a description line (`note`), a progress bar, or a line sparkline. |
| `horizontalAlign` | string | `"left"` (default), `"center"`, `"right"` | Alignment of value and ornament inside the cell. |
| `positive` | boolean | schema default `true` | Capsule: up arrow + positive color vs down arrow + negative color. |
| `changeLabel` | text object | schema default `{ "text": "100%" }` | Capsule text (the change amount). Single block, `textStyle: "_use_styles_"`. |
| `note` | text object | default none | `ornamentType: "text"`: the description line. `ornamentType: "capsule"`: the note after the capsule (e.g. "vs last month"), shown when `showNote` is not `false`. |
| `showNote` | boolean | default `true` | Capsule only: show `note` next to the capsule. |
| `color` | string \| null | palette color name; default `null` = `"positive"`/`"negative"` by `positive` (white capsule on colored cells) | Capsule background color override. |
| `progressBarValue` | number | 0-1, default `0.5` | `ornamentType: "bar"`: filled fraction. |
| `progressBarColor` | string | palette color name, default `"theme"` | Progress bar color (white on colored cells). |
| `chartData` (+ `legendPosition`, `chartAnnotations`) | object | see `Chart.md`; absent -> default sample line chart written into this model | `ornamentType: "sparkline"`: the sparkline's data (`chartData.series[0]` of type `"line"` and `chartData.xAxis.categories`); axes and legend are hidden. |
| `matchTextSize` | boolean | default `true` | Match the value's font size with the other statistics in the same grid row. |
| `layout` | string | default `"auto"` | Read by the element but not used by the current layout; omit. |
| `label` / `showLabel` | – | legacy | The old secondary label is **not rendered** by this version (no label element is built); the app's own "add statistic" default still writes `label: { text: "Statistic" }`, which is dead. Use the cell title instead. |
| `showChangeInValue` | boolean | legacy | Not honoured: `ornamentType` is defaulted to `"capsule"` before the legacy conversion runs, so `showChangeInValue: false` still shows the capsule. Set `ornamentType` explicitly. |
| `icon` | string | – | Read as `iconId` default but the capsule icon is always `arrow_drop_up`/`arrow_drop_down` from `positive`. Omit. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `value` -> `StatisticValue` (a `TextElement`, see `TextElement.md`; model key `value`): single line,
  `scaleTextToFit`, font size synced across the row (`matchTextSize`).
- By `ornamentType`:
  - `"capsule"` -> `StatisticChangeInValue` (shares the model): a rounded background, an icon (material symbol
    `arrow_drop_up`/`arrow_drop_down` by `positive`), `changeLabel` (`TextElement`, key `changeLabel`) and,
    when `showNote`, `note` (`TextElement`, key `note`, single line). Colors: background = `color` or
    `positive`/`negative`; on a colored cell the capsule is white with colored text.
  - `"text"` -> `StatisticDescription` (a `TextElement`, key `note`): one description line under the value.
  - `"bar"` -> `StatisticProgressBar` (shares the model): track at 20 % alpha + bar at `progressBarValue`,
    full cell width, rounded ends.
  - `"sparkline"` -> `Chart` (`Chart.md`) with `isSparkline` (shares the model): reads `chartData` from this model.
  - `"none"` -> no ornament.
