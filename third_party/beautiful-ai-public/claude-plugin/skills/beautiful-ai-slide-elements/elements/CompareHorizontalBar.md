# CompareHorizontalBar

`CompareHorizontalBar` ("Compare Bars") stacks one horizontal bar per item, caption on the left, bar length
proportional to the value, value label inside the bar end (or just after it when the bar is too short). It is the
root element of template `compare_horizontal_bars`. The model is the shared compare model documented in
`CompareValuesCollection.md`; this chart adds nothing of its own beyond its limits. Its item class is
`CompareHorizontalBarItem` (folded in here).

## Model location

- `states[0].primary` - the chart (root of `compare_horizontal_bars`).
- `states[0].primary.items[]` - one `CompareHorizontalBarItem` per bar, top to bottom.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Revenue by region", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "format": "currency",
    "formatOptions": { "decimal": 1, "separator": true, "abbreviated": true, "currency": "$" },
    "minValue": 0,
    "maxValue": 6100000,
    "items": [
      { "value": 6100000, "hilited": true, "text": { "blocks": [{ "html": "North America", "type": "text", "textStyle": "title" }] } },
      { "value": 2800000, "text": { "blocks": [{ "html": "Europe", "type": "text", "textStyle": "title" }] } },
      { "value": 1400000, "text": { "blocks": [{ "html": "APAC", "type": "text", "textStyle": "title" }] } }
    ]
  }
}
```

## Pitfalls

- Long captions eat up to a third of the width and shrink every bar; keep captions short or move detail to a `body`
  block (it wraps under the title inside the same column).
- Items are not sorted: write them in the order you want them displayed (largest first is the usual choice).
- See `CompareValuesCollection.md` for the value/format pitfalls (missing `value` -> random, percent as 0-100,
  `format: "none"` hides labels, `formatOptions` replaces the defaults entirely).

## Rules and limits

- Bar height = `min(100px, available height / item count - gap)`; the label font size is half the bar height.
- Negative values: when `minValue < 0` a baseline is computed at `maxValue / (maxValue - minValue)` of the bar area;
  positive bars grow right from it, negative bars grow left.
- Canvas margins are asymmetric (`right: 100px`) to leave room for labels that sit after short bars.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

No fields beyond the common ones (`items`, `format`, `formatOptions`, `minValue`, `maxValue`, `collectionColor`,
`decorationStyle`), see `CompareValuesCollection.md`. `maxItemCount` is 7.

#### items[] model (`CompareHorizontalBarItem`)

Exactly the common item model: `value` (required), `text` (`{ blocks }`, `title_and_body`, allowed block styles
`title` and `body`), `color`, `hilited`, `id`. The caption column is as wide as the widest caption, capped at 33% of
the element width; the remaining width is the 100% bar length.

### Nested elements

- `items[]` -> `CompareHorizontalBarItem` (1-7): `shape` (SVG rect), `text` (`TextElement.md`), optional `label`
  (`CompareValuesItemLabel`, only when `format != "none"`).
