# CompareVerticalBar

`CompareVerticalBar` ("Compare Columns") draws one column per item with the caption under the column and the value
label inside the column top (or above it when the column is too short). It is the root element of template
`compare_vertical_bars`. The model is the shared compare model (`CompareValuesCollection.md`); this page lists only
the one option it adds. Its item class is `CompareVerticalBarItem` (folded in here).

## Model location

- `states[0].primary` - the chart (root of `compare_vertical_bars`).
- `states[0].primary.items[]` - one `CompareVerticalBarItem` per column, left to right.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Conversion by channel", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "format": "percent",
    "minValue": 0,
    "maxValue": 40,
    "items": [
      { "value": 28, "text": { "blocks": [{ "html": "Paid search", "type": "text", "textStyle": "title" }] } },
      { "value": 34, "text": { "blocks": [{ "html": "Referral", "type": "text", "textStyle": "title" }] } },
      { "value": 22, "text": { "blocks": [{ "html": "Organic", "type": "text", "textStyle": "title" }] } },
      { "value": 19, "text": { "blocks": [{ "html": "Social", "type": "text", "textStyle": "title" }] } }
    ]
  }
}
```

## Pitfalls

- `maxValue` well above the largest value flattens all columns (e.g. values 4-5 with the default `maxValue: 100`):
  set `maxValue` to the largest value (or a round number just above it) whenever values are not percentages.
- Narrow columns (6-7 items) shrink the inside label down to `minTextScale` 0.1; abbreviate large numbers.
- Common pitfalls (missing `value`, percent as 0-100, `format: "none"`) are in `CompareValuesCollection.md`.

## Rules and limits

- Column height = `(available height - caption height) * share`; captions share one height (the tallest) so all
  column bases align.
- Negative values: when `minValue < 0` the baseline sits at `maxValue / (maxValue - minValue)` of the column area;
  positive columns rise above it, negative ones hang below.
- Label placement: inside the column when the column is taller than the label, else centered above the column.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `showBaseline` | boolean | default absent (falsy) | When truthy an SVG polyline element named `baseline` is created, but the current layout code never gives it a path, so there is nothing useful to show (whether an un-laid-out child renders cleanly is not verified). Leave it out. |

Plus the common fields (`items`, `format`, `formatOptions`, `minValue`, `maxValue`, `collectionColor`,
`decorationStyle`), see `CompareValuesCollection.md`. `maxItemCount` is 7.

#### items[] model (`CompareVerticalBarItem`)

The common item model: `value` (required), `text` (`{ blocks }`, `title_and_body`), `color`, `hilited`, `id`.
`minValue`/`maxValue`/`label` on stored items are ignored.

### Nested elements

- `items[]` -> `CompareVerticalBarItem` (1-7): `shape` (SVG rect), `text` (`TextElement.md`), optional `label`
  (`CompareValuesItemLabel`, when `format != "none"`; scaled to fit the column width, font synced across columns).
