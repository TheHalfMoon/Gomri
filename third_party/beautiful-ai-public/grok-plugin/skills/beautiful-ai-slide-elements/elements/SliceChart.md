# SliceChart

A row of up to 8 adjacent rectangular "slices" whose widths are proportional to a relative `width` weight, each with
a label inside the slice and an optional description below it, plus an optional number/letter/icon badge on the top
edge. Root element of the `slicechart` template ("Compare Slices"). Items are `SliceChartItem`, the slice body is
`SliceChartShape` (both documented here, no separate file).

## Model location

- `states[0].primary` – the `SliceChart` model (root).
- `states[0].primary.items[]` – one `SliceChartItem` per slice, left to right.
- `states[0].primary.items[].ornament` – the badge model of a slice (only for `ornament: "icon"`).

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "The market" } ] }
  },
  "primary": {
    "showSecondaryText": true,
    "sliceHeight": 0.4,
    "collectionColor": "colorful",
    "items": [
      { "width": 3,
        "label": { "blocks": [ { "type": "text", "textStyle": "title", "html": "$10B" } ] },
        "description": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Total addressable market" } ] } },
      { "width": 2,
        "label": { "blocks": [ { "type": "text", "textStyle": "title", "html": "$1B" } ] },
        "description": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Served market" } ] } },
      { "width": 1, "hilited": true,
        "label": { "blocks": [ { "type": "text", "textStyle": "title", "html": "20%" } ] },
        "description": { "blocks": [ { "type": "text", "textStyle": "body", "html": "Share of market" } ] } }
    ]
  }
}
```

## Pitfalls

- `width` is a weight, not a percentage or px; a missing `width` counts as 1, a `0` width collapses the slice and its label.
- Very unequal weights (e.g. 100 vs 1) leave no room for the narrow slice's label; the synced font scale then shrinks every label.
- `description` is ignored unless `showSecondaryText` is `true`; `body` is the legacy name and is only migrated for old slides.
- `ornament: "icon"` needs `items[].ornament.content_value` on every slice.

## Rules and limits

- The description row is as tall as the tallest description; all slices share the same slice height.
- More than the theme's `maxItemCount` (8) makes the slide report not fitting.
- Migrations: `body` on an item becomes `description`; models older than 10.02 get `sliceHeight: 0.4`.
- The app's importer sets `width` to at least 30 when converting values from other compare charts; it derives `showSecondaryText` from whether any item has a description.
- Template flags: `allowColorBackgrounds: true`, `allowColorful`; header and trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–8 objects | Slices, left to right. |
| `showSecondaryText` | boolean | `true` (schema default) | Shows `items[].description` under each slice. |
| `sliceHeight` | number | 0.1–1 (editor), stored slides often `0.4`; theme default when absent | Slice height as a fraction of the height left after the descriptions. |
| `ornament` | string | `"none"` (default), `"number"`, `"letter"`, `"icon"` | Badge centered on the top edge of each slice (50px). |
| `collectionColor` | string | `"theme"` (default) | Slice colors, per `CollectionElement.md`. |
| `decorationStyle` | string | theme default | Slice style inherited by items. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (SliceChartItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `width` | number | > 0, default `1` | Relative weight: slice width = `width / sum(widths)` of the available width. Any positive scale works (1/2/3 or 42/63/66). |
| `label` | object | `{ "blocks": [ { "type": "text", "textStyle": "title", "html": "$10B" } ] }` | Text inside the slice (`TextElement.md`, title-and-body, scale-to-fit, synced across slices). |
| `description` | object | `{ "blocks": [ { "type": "text", "textStyle": "body", "html": "..." } ] }` | Text under the slice, default block style body; only when `showSecondaryText`. |
| `ornament` | object | `{ "content_type": "icon", "content_value": "<icon key>" }` | Badge media, only read when the root `ornament` is `"icon"` (`ContentElement.md`). |
| `hilited` | boolean | `false` | Emphasizes this slice. |
| `color` | string | palette color or `null` | Overrides the collection color. |

### Nested elements

- `items[]` -> `SliceChartItem`; min 1, max 8 (`maxItemCount`); order = array order, left to right, separated by the theme gap.
  - `shapeContainer` -> `SliceChartShape`: `shape` -> SVG rect, `label` -> `TextElement.md` bound to `item.label`, vertically centered in the slice.
  - `description` -> `TextElement.md` bound to `item.description` (when `showSecondaryText`), auto height, synced font size.
  - `ornament` -> `Ornament.md` (when root `ornament` != `"none"`), drawn over the top edge.
