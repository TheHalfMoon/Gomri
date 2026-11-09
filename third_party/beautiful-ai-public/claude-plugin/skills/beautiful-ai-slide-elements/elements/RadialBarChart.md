# RadialBarChart

Concentric 270° arcs, one per item, each filled proportionally to its value over a shared maximum, with a text label
at the arc start and a formatted value at the arc end; optional background track and radial grid lines. Root element
of the `radial_bar_chart` template, and available as a dashboard cell (`componentType: "RadialBarChart"`, see
`LayoutContainerItem.md`). Items are `RadialBarChartItem`, the grid is `RadialBarChartGrid` (both documented here).

## Model location

- `states[0].primary` – the `RadialBarChart` model (root) of `radial_bar_chart`.
- `states[0].primary.items[].childElement` – when used as a dashboard cell with `componentType: "RadialBarChart"`.
- `...items[]` – one `RadialBarChartItem` per arc, outermost first.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Traffic sources" } ] }
  },
  "primary": {
    "collectionColor": "theme-to-light",
    "trackStyle": "bar",
    "startPosition": "top",
    "showGrid": false,
    "minValue": 0,
    "maxValue": 100,
    "format": "percent",
    "items": [
      { "value": 75, "label": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Organic" } ] } },
      { "value": 50, "label": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Direct" } ] } },
      { "value": 33, "label": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Email" } ] } }
    ]
  }
}
```

## Pitfalls

- With `format: "percent"` the label is `value / 100`: a `value` of `0.75` renders as a fraction of a percent, not "75%", and its arc is almost empty. Use 0–100 numbers (the app's generator multiplies fractional inputs by 100).
- For currency/number formats with large values set `maxValue` to the intended scale, otherwise the largest value becomes the full arc.
- The first item is the outermost ring; reorder items to change ring order.
- Labels sit outside the arc start; long labels on inner rings overlap the track of outer rings. Keep them short.
- Value text is computed from `value` + `format`; it cannot be authored.

## Rules and limits

- `maxValue` is rewritten at build time to `max(maxValue, largest item value)`, so a value above `maxValue` never overflows; it instead stretches the scale for all rings.
- Minimum element size 150×150px; the inner hole keeps a 50px radius.
- The app's generator uses `maxValue = max(100, values)` for percent and `max(1, values)` otherwise, `trackStyle: "bar"`, `startPosition: "top"`, labels with `textStyle: "body"`.
- Template flags: `allowColorful`; header and trays allowed. In a dashboard cell the chart has no own control bar (the dashboard's is used).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–8 objects | Arcs; index 0 is the outer ring. |
| `maxValue` | number | default `100`; raised at build to the largest item value if that is bigger; editor min 1 | Value that fills the full 270° arc. |
| `minValue` | number | default `0` | Stored and shown in the editor; not used by the arc math (0 is always the arc start). |
| `format` | string | `"percent"` (default), `"number"`, `"currency"`, `"none"` | Value label format; `"none"` hides the value labels. |
| `formatOptions` | object | formatter options (e.g. `{ "abbreviated": "lower" }`, `{ "decimal": 0, "separator": true, "currency": "$" }`) | Number formatting for the value labels. |
| `trackStyle` | string | `"bar"` (schema default), `"line"`, `"none"` | Background track: a full 270° muted bar, a thin line from the value end to the arc end, or nothing. |
| `startPosition` | string | `"top"` (default), `"bottom"` | Arcs start at 12 o'clock and run clockwise to 9 o'clock (labels right-aligned to the left of the start), or start at 6 o'clock (labels to the right). |
| `showGrid` | boolean | `false` | Radial tick lines every 45° across the rings. |
| `collectionColor` | string | `"theme"` (default); template defaultData `"theme-to-light"` | Arc colors, per `CollectionElement.md`. |

Decoration style is forced to `"filled"`. Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (RadialBarChartItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `value` | number | ≥ 0, editor default `50` | Arc length = `clamp(value / maxValue, 0, 1)` × 270°. With `format: "percent"` the label shows `value / 100` as a percent. |
| `label` | object | `{ "blocks": [ { "type": "text", "html": "Organic" } ] }` | Text at the arc start (`TextElement.md`, auto width/height, synced). Block style may be omitted or `"body"`. |
| `color` | string | palette color or `null` | Overrides the collection color (`"auto"` migrates to `null`). |
| `hilited` | boolean | `false` | Emphasizes this arc. |

### Nested elements

- `items[]` -> `RadialBarChartItem`; min 1, max 8 (`maxItemCount`); order = array order from the outside in. Bar width ≤ 30px with a 10px gap; the chart reports not fitting when bars drop below 12px.
  - `track` -> SVG path (when `trackStyle` != `"none"`), `radialBar` -> SVG path (the value arc).
  - `label` -> `RadialBarChartItemLabel` (`TextElement.md`) bound to `item.label`.
  - `value` -> `RadialBarChartItemValue` (`TextElement.md`, computed text, when `format` != `"none"`), placed just past the arc end.
- `grid` -> `RadialBarChartGrid` (when `showGrid`): SVG lines.
