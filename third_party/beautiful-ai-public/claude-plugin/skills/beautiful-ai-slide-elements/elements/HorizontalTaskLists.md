# HorizontalTaskLists

The horizontal task list: rows, each with a title on the left and a row of task chips (rounded boxes or chevron
"process" arrows) laid out left to right, with optional icons. It is the root element of the `horizontal-task-list`
template (`states[0].primary`). Structurally it is the transposed kanban (`VerticalTaskLists.md`): rows instead of
columns, chips instead of cards.

## Model location

- `states[0].primary` – the list (template `horizontal-task-list`).
- `states[0].primary.items[]` – rows (`HorizontalTaskListsRow`).
- `states[0].primary.items[].items[]` – tasks (`HorizontalTaskElement`).
- `states[0].header` – header; tray layouts as the template allows; color backgrounds disabled.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Release checklist" }] } },
  "primary": {
    "showTitles": true,
    "itemStyle": "process",
    "taskLayout": "fit",
    "items": [
      { "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Backend" }] },
        "items": [
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Migrate DB" }] } },
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Deploy API" }] }, "icon": "check-yes" }
        ] },
      { "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Frontend" }] },
        "items": [
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Build UI" }] } },
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "QA" }] }, "color": "accent2" },
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Ship" }] }, "icon": "rocket" }
        ] }
    ]
  }
}
```

The app's generator uses `itemStyle: "task"`, `taskLayout: "fit"`, string `label`s and `{ id, text: { blocks } }` tasks.

## Pitfalls

- Same nesting trap as the kanban: rows are `items[]`, chips are `items[].items[]`.
- A row needs at least one task; an empty `items` array gets a placeholder chip ("Type title" placeholder text).
- `itemStyle` lives on the root (`"task"`/`"process"`); putting it on rows does nothing.
- With `taskLayout: "stack"` long rows overflow to the right (no wrapping); prefer `"fit"`/`"fill"` for more than
  4–5 chips per row.
- `icon` is a bare icon key, not a `content_*` pair.

## Rules and limits

- Rows: 1–10 (default collection max). Rows are stacked vertically, centred as a block; each row is as tall as its
  share of the height.
- Chip min width 100px; `"stack"` layout keeps natural widths and reports `isFit` false when a row overflows (no
  wrapping). `"fill"`/`"fit"` give fixed widths and scale the text instead.
- `"process"` chips overlap by their chevron notch; the first chip of each row has a straight left edge.
- Null rows/tasks are replaced by `{}` on build (seen in several stored examples).
- Migration `_migrate_10_02` on tasks: `decorationStyle: "filled"`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 10 | Rows, top to bottom, see "items[] model". |
| `showTitles` | boolean | default `true` | Show row titles in a column on the left (width = widest title, max 300px). |
| `itemStyle` | string | `"task"` (default), `"process"` | Chip shape: rounded rectangle, or chevron arrows (first chip has a flat start). |
| `taskLayout` | string | `"stack"` (default), `"fill"`, `"fit"` | Chip widths: natural text width; all chips of a row share the row width; or every row sized as if it had as many chips as the longest row (aligned columns). |
| `collectionColor` | string | palette color, default `"theme"` | Default chip color (rows may override). |
| `style` | – | seen in 2 examples | Kanban field; not read here. |

Plus the common fields, see `CollectionElement.md`.

#### items[] model (rows, `HorizontalTaskListsRow`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `label` | object or string | `{ blocks: [...] }` (`TextElement.md`); a string becomes one block | Row title, right-aligned against the chips. Only when `showTitles`. |
| `items` (required) | array | min 1 | Tasks, left to right. An empty row gets one empty chip. |
| `collectionColor` | string | palette color | Default color of this row's chips (`"colorful"` cycles per chip). |

#### items[].items[] model (tasks, `HorizontalTaskElement`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `text` (required) | object | `{ blocks: [...] }` | Chip text, title-and-body structure, alignment allowed; font synced across the whole element. See `TextElement.md`. |
| `icon` | string | icon key or `"none"` | 30px icon at the right end of the chip (adds 40px width). See `Icon.md`. |
| `color` | string | palette color | Chip color override. |
| `decorationStyle` | string | `"filled"` (migration default); `"outlined"` seen in examples | Chip decoration style. |
| `iconColor`, `iconScale` | – | seen in examples | Not read by the chip; the icon is drawn on the chip background. |

### Nested elements

- `items[]` -> `HorizontalTaskListsRow`: `label` -> `RowHeaderTextElement` (`TextElement.md`), `taskList` ->
  `HorizontalTaskList` (collection of `HorizontalTaskElement`, min 1).
- Tasks: `shape` -> SVG path (rect or chevron), `icon` -> `Icon.md`, `text` -> `TextElement.md`.
