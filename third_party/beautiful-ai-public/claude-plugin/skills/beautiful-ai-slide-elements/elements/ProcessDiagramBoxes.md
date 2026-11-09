# ProcessDiagramBoxes

`ProcessDiagramBoxes` ("Numbered Boxes") lays out up to 8 steps in a grid (up to 4 rows, two per row at the default
48% min item width), each step being a framed step number (1, 2, 3, ... computed from position) followed by a text
block (title + description). It is the root element of template `step_boxes` and extends `ProcessDiagram.md`.
Its item class `ProcessDiagramBoxItem` is documented here.

## Model location

- `states[0].primary` - the collection (root of `step_boxes`).
- `states[0].primary.items[]` - one `ProcessDiagramBoxItem` per step.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Points covered", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "theme",
    "items": [
      { "text": { "blocks": [{ "html": "Market overview", "type": "text", "textStyle": "title" }, { "html": "Size, growth and segments", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Product", "type": "text", "textStyle": "title" }, { "html": "What we ship this year", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Go to market", "type": "text", "textStyle": "title" }, { "html": "Channels and pricing", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Financials", "type": "text", "textStyle": "title" }, { "html": "Plan and asks", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

## Pitfalls

- There is no `body` field here (unlike `step_chevrons`): the description is the second block of `text`.
- Odd item counts leave the last row half empty (rows are left aligned); 2, 4, 6 or 8 steps look balanced.
- Do not prefix titles with "1." etc.; the number box already shows the position.

## Rules and limits

- Grid: `HorizontalGridLayout`, min item width 48% (so normally 2 columns), max 4 rows, 20px gaps, rows aligned
  left, grid vertically centered. 8 items = 4 rows of 2.
- Import from other templates truncates to 8 items and maps main text -> `title` block, secondary texts -> `body`
  blocks.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-8 items | Steps in reading order (row by row). |
| `collectionColor` | string | default `"theme"` | Color of the number frames. |

Plus the common fields, see `ProcessDiagram.md`. `textLayout`, `backgroundColor`, `gradiateColors` and
`userFontScale` seen in stored `step_boxes` models are not read by this element.

#### items[] model (`ProcessDiagramBoxItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }` (`title_and_body`), see `TextElement.md` | First block `textStyle: "title"` (28px), following blocks `textStyle: "body"` (20px). This is the only authored content; the number is computed. |
| `hilited`, `color`, `id` | | see `ProcessDiagram.md` | |

Legacy `titleTextStyle`, `title` and `content_value` fields on stored items are ignored.

### Nested elements

- `items[]` -> `ProcessDiagramBoxItem` (1-8): `index` (non-editable `TextElement` showing `itemIndex + 1` in a
  60x50 framed box, theme shape) + `text` -> `TextElement.md` (`title_and_body`, auto height, font synced across
  items). RTL text swaps the number to the right.
