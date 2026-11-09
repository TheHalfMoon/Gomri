# RadialBarInfographic

`RadialBarInfographic` renders one circular progress ring ("radial bar"): a faint full circle, a colored arc from
12 o'clock clockwise covering `value / maxValue`, the formatted value in the middle and an optional label inside,
above or below the ring. It is the `childElement` of a `LayoutContainerItem` with `componentType: "RadialBar"`
(third default cell of the `dashboard` template). This file also covers `RadialBarInfographicValue` (the value
text) and the sibling class `RadialBarGraph`, the ring used by the compare-radial-bars template.

## Model location

- `states[0].primary.items[].childElement` of a `Dashboard` cell with `componentType: "RadialBar"` (legacy models
  put the same fields directly on the item).
- `RadialBarGraph`: inside each `CompareRadialBarItem` of the `compare_radial_bars` template (model =
  `states[0].primary.items[]`, see `CompareRadialBar.md` / `CompareValuesCollection.md`).

## Minimal example

`items[].childElement` of a `componentType: "RadialBar"` cell:

```json
{
  "value": 76,
  "maxValue": 100,
  "format": "percent",
  "color": "theme",
  "showValue": true,
  "showLabel": true,
  "labelPosition": "bottom",
  "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Customer retention" } ] }
}
```

Ring only: `{ "value": 43, "showLabel": false }` (percent format, theme color).

## Pitfalls

- With `format: "percent"` the centre text is `value / 100`, independent of `maxValue`; keep `maxValue: 100` for
  percentages, or switch to `"number"` when `maxValue` is something else (e.g. `value: 150, maxValue: 200`).
- The centre text cannot be authored: do not write `value` as text/blocks, it must be a number.
- `showLabel` defaults to `true`; without a `label` an empty label block is created. Set `showLabel: false` for a
  bare ring.
- `labelPosition` only has effect while `showLabel` is on; `"inside"` with a long label shrinks both texts.
- `formatOptions.decimal: "auto"` (default) shows up to two decimals (`2.6%`); set `decimal: 0` for whole
  percentages.

## Rules and limits

- The ring is a square of `min(width, height)` (minus the label height for top/bottom labels) centred in the
  cell; the value is laid out inside the inner 70 % of the ring.
- Minimum content size 25 x 25 px; the cell padding for this component is 30 px.
- `value` above `maxValue` draws a full ring; negative values draw nothing (clamped).
- Animation "Grow in": the arc and the centre value count up from 0.
- No migrations of its own.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | number (required) | schema default `50` | Current value. The arc covers `clamp(value / maxValue, 0, 1)` of the circle (359.99° max). |
| `maxValue` | number | default `100` | Value for a full ring. |
| `format` | string | `"percent"` (schema default), `"number"`, `"currency"`, `"none"` | Format of the centre text. `"percent"` shows `value / 100` as a percentage (so `76` -> `76%`; with `maxValue: 200`, `150` still shows `150%`). `"number"`/`"currency"` show `value` as is. |
| `formatOptions` | object | formatter options (`decimal`: number or `"auto"`, `separator`, `abbreviated`, `currency`, `textAlign`); default `{ decimal: "auto", separator: true, abbreviated: false, currency: "$", ... }` | Centre text formatting (e.g. `decimal: 1` for `2.6%`). |
| `showValue` | boolean | default `true` (schema writes it) | Show the formatted value in the ring. |
| `showLabel` | boolean | default `true` | Show `label`. |
| `labelPosition` | string | `"inside"` (default), `"top"`, `"bottom"` | Where `label` goes: under the value inside the ring, or above/below the ring (20 px margin). |
| `label` | text object | `{ "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Retention" } ] }`; default: an empty block is created | Label text (scaled to fit, multi-line allowed). |
| `color` | string | palette color name; schema default `"theme"` | Ring color (both the faint track and the arc). |

Plus the common fields, see `BaseElement.md`.

#### `RadialBarGraph` (compare template ring)

Used only by `CompareRadialBarItem`; it has no model of its own beyond the item's `value`:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | number | schema default `50` | Only a fallback: the parent passes a `valueFunction` returning the item's share (0-1) which drives the arc (`360° * share`). |

The label is a `CompareValuesItemLabel` created by the parent with the parent's formatted value; ring colors come
from the item's decoration color (track at 40 % alpha). See the compare docs for the item model.

### Nested elements

- `radialCircle` / `radialPath` -> SVG path elements (track and arc); stroke width = 15 px scaled by
  `min(width, height) / 150`.
- `value` -> `RadialBarInfographicValue` (a read-only `TextElement`; its text is generated from `value`/`format`,
  it is **not** read from the model). Built only when `showValue`.
- `label` -> `TextElement` bound to `label` (model key `label`). Built only when `showLabel`.
