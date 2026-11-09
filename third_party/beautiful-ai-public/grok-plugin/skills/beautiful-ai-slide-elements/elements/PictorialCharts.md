# PictorialCharts

Rows of repeated icons (pictographs) filled left to right to a 0–100 value, with a large formatted value label on the
left and an optional one-line description under the row. Root element of the `visual_percentage` template
("Percentage with Icons"). Items are `PictorialChartItem`, the icon strip is `PictorialChartItemIcons` (both
documented here). The `Pictograph` / `PictographIcons` pair used by the `compare_vertical_pictograph` template is
described at the end.

## Model location

- `states[0].primary` – the `PictorialCharts` model (root).
- `states[0].primary.items[]` – one `PictorialChartItem` per row, top to bottom.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Market research" } ] }
  },
  "primary": {
    "fitIcons": true,
    "showDescription": true,
    "collectionColor": "theme",
    "items": [
      { "value": 75, "format": "percent", "iconId": "figure-woman",
        "description": { "blocks": [ { "type": "text", "textStyle": "body", "html": "of women surveyed would recommend us" } ] } },
      { "value": 25, "format": "percent", "iconId": "figure-man",
        "description": { "blocks": [ { "type": "text", "textStyle": "body", "html": "of men surveyed would recommend us" } ] } }
    ]
  }
}
```

## Pitfalls

- `shape: "male"` / `"female"` does nothing; the icon comes from `iconId` (`"figure-man"` when absent).
- `value` is always the fill percentage. To show "15M" fill 40% of the icons, use `value: 40`, `format: "number"`, `labelValue: 15000000`, `formatOptions.abbreviated: true`.
- `format`/`formatOptions` live on each item, not on the root.
- `description` must be a single block; extra blocks are not laid out as a list.
- The value label is computed; do not try to set its text.

## Rules and limits

- The whole block is scaled down uniformly so all rows fit the element height; with several rows the icons are drawn at the "figure" aspect ratio and non-figure icons are scaled to 75%.
- The fill denominator is the larger of 100 and the largest `value`, so values above 100 are allowed and shrink the others' fill.
- The label is formatted from `value` (percent: `value / 100` through the percent formatter) or from `labelValue`.
- Template flags: `showHeader: false`, defaultData `layout.headerPosition: "none"` (the stored examples still mostly use a top header); `allowColorful`.

## Pictograph / PictographIcons (compare_vertical_pictograph)

`Pictograph` is the bar of a `CompareVerticalPictograph.md` item (not a template root). It reads from its item model:

| Field | Type | Meaning |
|---|---|---|
| `value` | number | Fraction filled through the parent's value function (hilited icons = rows × cols × fraction). |
| `iconId` | string | Icon key, default `"figure-man"`. |

Options set by the parent (not model fields): `valuePosition` (`"top"`, `"middle"`, `"bottom"`, `"none"`), `showValue`,
`valueFunction`, `labelElement`. Icon rows/gaps come from the theme styles. The grid is `rows × ceil(width / iconWidth)`
icons, filled in reading order. See `CompareVerticalPictograph.md` / `CompareValuesCollection.md` for the item model.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–6 objects | Rows. |
| `showDescription` | boolean | `true` (schema default; migration sets it from whether any item has a description) | Shows `items[].description` under each row. |
| `fitIcons` | boolean | `false` (schema); template defaultData `true` | `true`: always 10 icons per row ("fixed number of icons"); `false`: as many icons as fit the row width (min 10px gap). |
| `collectionColor` | string | `"theme"` (default) | Icon colors, per `CollectionElement.md`. |
| `format` | string | seen on one stored slide | Not read for rendering (per-item `format` is); harmless. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (PictorialChartItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `value` | number | 0–100, schema default `50`, editor default `75` | Fill: the filled fraction is `value / max(100, largest item value)`. With `format: "percent"` it is also the displayed number. |
| `format` | string | `"percent"` (default), `"number"`, `"currency"` | Format of the value label. |
| `formatOptions` | object | formatter options, default `{ "decimal": "auto", "separator": true, "abbreviated": false, ... }` | Number formatting (decimals, separators, abbreviation, currency symbol). |
| `labelValue` | number | – | With `format` `"number"`/`"currency"`: the number shown in the label (e.g. `15000000`) while `value` still drives the fill. Ignored for `"percent"`. |
| `iconId` | string | `"figure-man"` (default); editor offers `figure-woman`, `figure-man`, `torso-female`, `torso-male`, `baby`, `pregnant`, `stroller`, `people`, `laborer`, `business-man`, `business-woman`, `female`, `male`, `star`, `full`; any icon key works | The repeated icon (`Icon.md`). |
| `description` | object | `{ "blocks": [ { "type": "text", "textStyle": "body", "html": "..." } ] }` (schema default: one empty body block) | One-block caption under the row (`TextElement.md`, single block, synced font size); only when `showDescription`. |
| `color` | string | palette color or `null` | Overrides the collection color for this row's icons. |
| `hilited` | boolean | `false` | Emphasizes this row. |
| `shape` | string | `"male"` in defaultData and most stored slides | Legacy; not read (use `iconId`). |

### Nested elements

- `items[]` -> `PictorialChartItem`; min 1, max 6 (`maxItemCount`); order = array order, rows right-aligned on the longest row and vertically centered.
  - `label` -> `PictorialChartItemLabel` (`TextElement.md`, computed text, not authored, not editable inline).
  - `icons` -> `PictorialChartItemIcons`: one `Icon.md` rendered N times with a clip mask over the filled fraction. Reads `iconId`, `value`, `color` from the item.
  - `description` -> `TextElement.md` bound to `item.description` (when `showDescription`).
