# ProcessDiagram

`ProcessDiagram` is the thin shared base of the two "steps" collections: `ProcessDiagramChevrons` (template
`step_chevrons`, arrow-shaped chevrons in a row) and `ProcessDiagramBoxes` (template `step_boxes`, numbered text
boxes in a grid). It is never a root element itself and adds no model fields of its own: it is a
`CollectionElement` (see `CollectionElement.md`) whose default layout lays the items out horizontally and centers
them vertically; both subclasses override that layout. The two templates are in the same `variations: "process"`
group and differ only by `template_id`; their item models are different (see the subclass docs).

## Model location

- `states[0].primary` - the collection (root of `step_chevrons` / `step_boxes`, through the subclass).
- `states[0].primary.items[]` - one item per step.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Our process", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "theme-to-dark",
    "items": [
      { "text": { "blocks": [{ "html": "Discover", "type": "text", "textStyle": "title" }] } },
      { "text": { "blocks": [{ "html": "Design", "type": "text", "textStyle": "title" }] } },
      { "text": { "blocks": [{ "html": "Deliver", "type": "text", "textStyle": "title" }] } }
    ]
  }
}
```

## Pitfalls

- Pick the subclass doc for the item shape: chevrons put the description in a separate `body` object, boxes put
  everything in `text` blocks. Copying a `step_chevrons` item with `body` into `step_boxes` silently drops the
  description.
- Do not number the steps in the text; the number is drawn by the element.

## Rules and limits

- Items render in array order; the step number/letter shown by the ornament or box index is the array position
  (1-based), not a model field.
- Nothing is sorted or clamped: extra items beyond `maxItemCount` are laid out anyway (the UI only refuses to add
  more).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | `[{}, {}, {}]` in both templates' `defaultData` | One object per step, in display order. An empty array is filled with one empty item; `null` entries become `{}`. |
| `collectionColor` | string | palette color name, default `"theme"`; the generator uses `"theme-to-dark"` | Step color; `"colorful"` cycles the accents, `"<color>-to-dark"` / `"-to-light"` shade along the items. See `CollectionElement.md`. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Shape style (chevrons only expose this in the UI). |

Fields present in the templates' `defaultData` but not read by any element: `backgroundColor: "theme"` and
`gradiateColors: true` (legacy; safe to omit or copy).

#### items[] model (shared part)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks: [...] }`, see `TextElement.md`; structure `title_and_body` | The step's main text: first block `textStyle: "title"`, optional `body` blocks after it. |
| `id` | string | generated when missing | Item key. |
| `hilited` | boolean | default `false` | Emphasize this step, de-emphasize the others. |
| `color` | string | palette color name | Per-item override of `collectionColor`. |

### Nested elements

- `items[]` -> `ProcessDiagramChevronItem` (see `ProcessDiagramChevrons.md`) or `ProcessDiagramBoxItem` (see
  `ProcessDiagramBoxes.md`), chosen by the subclass. `minItemCount` 1; `maxItemCount` 10 for chevrons, 8 for
  boxes.
