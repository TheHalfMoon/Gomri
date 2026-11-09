# CompareVerticalPictograph

`CompareVerticalPictograph` ("Percentage Comparison") draws, for each item, a grid of repeated icons (6 rows) in
which the share of highlighted icons equals the item's relative value, with the formatted value above (or below) the
grid and the caption underneath. It is the root element of template `compare_vertical_pictograph`. The model is
the shared compare model (`CompareValuesCollection.md`) plus an icon per item and a value position. Its item class
is `CompareVerticalPictographItem` (folded in here); the icon grid is a `Pictograph` (see `PictorialCharts.md` (section "Pictograph")).

## Model location

- `states[0].primary` - the chart (root of `compare_vertical_pictograph`).
- `states[0].primary.items[]` - one `CompareVerticalPictographItem` per icon grid, left to right.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Device usage", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "format": "percent",
    "valuePosition": "top",
    "minValue": 0,
    "maxValue": 100,
    "items": [
      { "value": 87, "iconId": "figure-man", "text": { "blocks": [{ "html": "Mobile", "type": "text", "textStyle": "title" }] } },
      { "value": 11, "iconId": "figure-man", "text": { "blocks": [{ "html": "Desktop", "type": "text", "textStyle": "title" }] } },
      { "value": 2, "iconId": "figure-man", "text": { "blocks": [{ "html": "Tablet", "type": "text", "textStyle": "title" }] } }
    ]
  }
}
```

## Pitfalls

- `iconId` is an icon key, not `content_type`/`content_value`; an unknown key renders empty glyph cells.
- This chart reads as "x out of 100 people": with `format: "number"`/`"currency"` and non-percent values the grid
  still shows the share of `maxValue`, which readers rarely expect; prefer percent data (and `maxValue: 100`).
- Keep to 2-4 items; a 5th item makes the layout report "does not fit".
- Common pitfalls (missing `value` -> random, percent as 0-100, `format: "none"`) are in
  `CompareValuesCollection.md`.

## Rules and limits

- The grid has 6 rows; the number of columns is derived from the item width and icon size. Highlighted icon count =
  `rows * cols * share`, filled row by row from the top-left; highlighted icons use the item color at full opacity,
  the rest the same color dimmed (theme `unhilited_icons` opacity, 0.3 in the default theme).
- `share` uses `|value|`, negative values are not meaningful here.
- `isFit` is false when `items.length > 4`; the renderer still draws them.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `valuePosition` | string | `"top"` (default), `"bottom"` (UI); `"middle"` and `"none"` are also understood by the code | Where the formatted value sits relative to the icon grid. `"none"` hides it like `format: "none"`. |
| `maxItemCount` | - | 4 | Max grids; with more items the element reports "does not fit". |

Plus the common fields (`items`, `format`, `formatOptions`, `minValue`, `maxValue`, `collectionColor`), see
`CompareValuesCollection.md`. `decorationStyle` is not offered for this chart. `showValue: true` in the template's
`defaultData` is not read (use `format`).

#### items[] additions (`CompareVerticalPictographItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `iconId` | string | icon key from the built-in icon catalog; default `"figure-man"`. The UI offers `"figure-woman"`, `"figure-man"`, `"torso-female"`, `"torso-male"`, `"baby"`, `"pregnant"`, `"stroller"`, `"people"`, `"laborer"`, `"business-man"`, `"business-woman"`, `"female"`, `"male"`, `"star"`, `"full"` but any icon key works | The icon repeated in this item's grid. Usually the same for all items (the panel sets it on every item at once). |

Plus the common item fields `value` (required), `text`, `color`, `id`. `hilited` has no emphasize control here.
Legacy `icon` / `label` fields on stored items are ignored.

### Nested elements

- `items[]` -> `CompareVerticalPictographItem` (1-4): `pictograph` -> `PictorialCharts.md` (section "Pictograph") (an `icons` grid of
  `Icon` glyphs and, when `format != "none"`, a `label` = `CompareValuesItemLabel` with the formatted value), `text`
  -> `TextElement.md` (`title_and_body`).
