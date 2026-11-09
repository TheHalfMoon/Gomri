# CompareBubble

`CompareBubble` ("Compare Circles") draws one circle per item, sized by its value (area-proportional) and laid out in
a row with the caption below each circle. It is the root element of template `compare_circles`. Its model is the
shared compare model: read `CompareValuesCollection.md` for `items[]`, `value`, `text`, `format`, `formatOptions`,
`minValue`/`maxValue`, `collectionColor`, `hilited`; this page lists only what the bubble chart adds. Its item class
is `CompareBubbleItem` (folded in here).

## Model location

- `states[0].primary` - the chart (root of `compare_circles`).
- `states[0].primary.items[]` - one `CompareBubbleItem` per circle.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Addressable market", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "format": "number",
    "formatOptions": { "decimal": 0, "separator": true, "abbreviated": true, "currency": "$" },
    "minValue": 0,
    "maxValue": 2000000000,
    "circleAlign": "bottom",
    "items": [
      { "value": 2000000000, "text": { "blocks": [{ "html": "Trips booked worldwide", "type": "text", "textStyle": "title" }, { "html": "Total available market", "type": "text", "textStyle": "body" }] } },
      { "value": 560000000, "text": { "blocks": [{ "html": "Budget and online trips", "type": "text", "textStyle": "title" }, { "html": "Serviceable market", "type": "text", "textStyle": "body" }] } },
      { "value": 84000000, "text": { "blocks": [{ "html": "Trips with us", "type": "text", "textStyle": "title" }, { "html": "Market share", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

## Pitfalls

- Values spanning several orders of magnitude give near-invisible small circles (area scale). Either accept it, set
  `useValueForSize: false` with hand-picked `items[].size`, or pick another compare template.
- `items[].size` does nothing while `useValueForSize` is `true` (the default).
- More than 7 items are not refused by the renderer but will not fit; keep it to 2-5 for readable captions.
- Everything else (random value when `value` is missing, percent as 0-100, `format: "none"` to hide labels) is in
  `CompareValuesCollection.md`.

## Rules and limits

- Circle diameter (value mode) = `min(column width, available height) * sqrt(max(share*100, 0.25) / pi) / 5.64`, where
  `share` is the 0-1 relative value; the largest value fills the column, a zero value still shows a tiny circle.
- Captions are vertically aligned across items and font size is synced between items.
- The generator (`compare_circles` recipe) only emits this template when there are at most 4 items.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `useValueForSize` | boolean | default `true` | `true`: circle diameter is derived from the item's relative value (`sqrt(value share)` so **area** is proportional). `false`: the diameter is `items[].size` x item width instead, and the value only drives the label ("Unlock Size and Value" in the UI). |
| `circleAlign` | string | `"bottom"` (default), `"middle"`, `"top"` | How circles of different sizes are aligned relative to each other; with `"top"`/`"middle"` the caption sits below the tallest possible circle, with `"bottom"` directly under each circle. |
| `maxItemCount` | - | 7 | Max circles (the UI refuses to add more). |

Plus the common fields, see `CompareValuesCollection.md`.

#### items[] additions (`CompareBubbleItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `size` | number | `0-1` fraction of the item's column width, default `1` | Circle diameter when `useValueForSize` is `false`. Ignored otherwise. |

The value label is placed inside the circle when it fits, otherwise above-right of the circle with a short connector
line (computed, no model).

### Nested elements

- `items[]` -> `CompareBubbleItem` (1-7, left to right): `shape` (SVG circle), `text` (`TextElement.md`,
  `title_and_body`), and when `format != "none"` a `label` (`CompareValuesItemLabel`) plus a `connector` polyline.
