# SwotDiagram

A fixed 2x2 grid of four decorated text boxes (Strengths, Weaknesses, Opportunities, Threats), each with a large
single-letter badge in the corner that faces the center of the grid and a title-and-body text. Root element of the
`swot_diagram` template. Items are `SwotDiagramItem`, the badge is `SWOTCharElement` (both documented here, no
separate file).

## Model location

- `states[0].primary` – the `SwotDiagram` model (root).
- `states[0].primary.items[]` – exactly four `SwotDiagramItem` entries: index 0 = S (top-left), 1 = W (top-right), 2 = O (bottom-left), 3 = T (bottom-right).

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "SWOT analysis" } ] }
  },
  "primary": {
    "collectionColor": "colorful",
    "items": [
      { "text": { "blocks": [
        { "type": "text", "textStyle": "title", "html": "Strengths" },
        { "type": "text", "textStyle": "body", "html": "Loyal customer base" },
        { "type": "text", "textStyle": "body", "html": "Fast release cycle" }
      ] } },
      { "text": { "blocks": [
        { "type": "text", "textStyle": "title", "html": "Weaknesses" },
        { "type": "text", "textStyle": "body", "html": "Small sales team" }
      ] } },
      { "text": { "blocks": [
        { "type": "text", "textStyle": "title", "html": "Opportunities" },
        { "type": "text", "textStyle": "body", "html": "EU expansion" }
      ] } },
      { "text": { "blocks": [
        { "type": "text", "textStyle": "title", "html": "Threats" },
        { "type": "text", "textStyle": "body", "html": "New entrants" }
      ] } }
    ]
  }
}
```

## Pitfalls

- The S/W/O/T letters come from the item index, not from the title text: keep the items in S, W, O, T order.
- Never send 3 or 5 items; the layout is a fixed 2x2 grid.
- The quadrant text has no alignment option (`textAlign` on the item is ignored).
- Trays are not available on this template; put extra content in the header or a bottom tray.

## Rules and limits

- Always four items. An empty `items` array is filled with four empty quadrants; 1–3 entries render only those boxes (in the generic text-box grid), 5+ overflow it. Supply exactly four.
- The badge offset depends on the theme shape (`rect`, `circle`, `rounded_rect`, `octagon`).
- Template flags: header position `"top"` only; no trays (`availableTrayLayouts: []`); `allowColorful`.
- Importing from another template rebuilds the four items from the template `defaultData` and fills the texts in order.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | exactly 4 objects | The four quadrants in S, W, O, T order. |
| `collectionColor` | string | `"theme"` (default) | Box colors, per `CollectionElement.md` (`"colorful"` = one color per quadrant). |
| `decorationStyle` | string | theme default; `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Box style inherited by items. |
| `showCellTitle`, `showCellChar`, `showAxisLabel` | boolean | present in `defaultData` (`true`, `true`, `false`) and in every stored slide | Not read by the element: the badge and title are always drawn. Keep them for compatibility only. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (SwotDiagramItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `text` (required) | object | `{ "blocks": [ title, body... ] }` | Quadrant text (`TextElement.md`, title-and-body, scale-to-fit, font size synced across the four boxes, alignment not editable). First block `textStyle: "title"` (e.g. "Strengths"), then `"body"` or `"bulleted"` blocks. |
| `char` | object | `{ "text": "S" }` created from the index when missing; stored slides carry `{ "text": "S", "blocks": [ { "html": "S", ... } ] }` | The badge letter (`SWOTCharElement`, a single-block `TextElement.md` bound to `char`). Normally omitted. |
| `color` | string | palette color or `null` | Overrides the collection color for this box. |
| `hilited` | boolean | `false` | Emphasizes this box. |

### Nested elements

- `items[]` -> `SwotDiagramItem`; min 4, max 4 (`minItemCount` = `maxItemCount` = 4); order = S, W, O, T; items cannot be deleted (`deleteItem` is a no-op).
  - `char` -> `SWOTCharElement` (`TextElement.md`, always `"filled"` decoration): the letter badge, 40% of the box height, placed in the corner nearest the grid center.
  - `text` -> `TextElement.md` (title-and-body), laid out in the space left by the badge.
