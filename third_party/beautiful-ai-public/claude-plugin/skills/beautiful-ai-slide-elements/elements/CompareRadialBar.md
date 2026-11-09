# CompareRadialBar

`CompareRadialBar` ("Compare Radial Bars") draws one ring per item whose arc covers the item's share of the range,
with the formatted value in the ring's center and the caption below (or to the right when the row does not fit).
It is the root element of template `compare_radial_bars`. The model is the shared compare model
(`CompareValuesCollection.md`); this page lists only its differences. Its item class is `CompareRadialBarItem`
(folded in here); the ring itself is a `RadialBarGraph` (see `RadialBarInfographic.md` (section "RadialBarGraph")) driven by the item's value.

## Model location

- `states[0].primary` - the chart (root of `compare_radial_bars`).
- `states[0].primary.items[]` - one `CompareRadialBarItem` per ring.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Goal completion", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "format": "percent",
    "minValue": 0,
    "maxValue": 100,
    "items": [
      { "value": 75, "text": { "blocks": [{ "html": "Hiring plan", "type": "text", "textStyle": "title" }] } },
      { "value": 50, "text": { "blocks": [{ "html": "Product roadmap", "type": "text", "textStyle": "title" }] } },
      { "value": 25, "text": { "blocks": [{ "html": "Market expansion", "type": "text", "textStyle": "title" }] } }
    ]
  }
}
```

## Pitfalls

- Values above `maxValue` expand the range, so a "110%" item makes every other ring smaller than its percent; set
  `maxValue` explicitly when values exceed 100.
- The label is drawn inside the ring and scaled down to fit (`minTextScale` 0.1): long currency strings become tiny;
  prefer `formatOptions.abbreviated: true` for large numbers.
- Common pitfalls (missing `value`, percent as 0-100, `format: "none"`) are in `CompareValuesCollection.md`.

## Rules and limits

- Arc angle = `min(359.99°, 360° * share)` where `share = (|value| - max(0, minValue)) / (maxValue - minValue)`; a
  value equal to `maxValue` draws a full ring.
- Layout tries a single row with captions below; if that does not fit (too many items or text too long) it falls
  back to a vertical list with captions to the right of each ring.
- The ring track is the item color at 40% alpha, the arc the item color; no decoration style.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

No fields beyond the common ones (`items`, `format`, `formatOptions`, `minValue`, `maxValue`, `collectionColor`),
see `CompareValuesCollection.md`. `decorationStyle` is not offered for this chart. `maxItemCount` is 12.

#### items[] model (`CompareRadialBarItem`)

The common item model: `value` (required), `text` (`{ blocks }`, `title_and_body`), `color`, `id`. `hilited` is
accepted but the UI offers no emphasize toggle for radial items. `minValue`/`maxValue` found on stored items are
ignored (the range lives on the collection).

### Nested elements

- `items[]` -> `CompareRadialBarItem` (1-12): `radialBar` -> `RadialBarInfographic.md` (section "RadialBarGraph") (arc = relative value, label =
  formatted value when `format != "none"`, label font synced across rings), `text` -> `TextElement.md`.
