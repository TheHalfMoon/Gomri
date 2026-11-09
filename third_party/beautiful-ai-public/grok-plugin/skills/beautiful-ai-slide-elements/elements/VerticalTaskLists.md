# VerticalTaskLists

The kanban board: up to 7 vertical columns, each with a title and a stack of task cards (title/body text, optional
icon at the top-right, per-card color). It is the root element of the `kanban` template (`states[0].primary`) and is
reused by the week calendar (`WeekCalenderVerticalTaskLists`, see `Calendar.md`) with locked columns.

## Model location

- `states[0].primary` – the board (template `kanban`).
- `states[0].primary.items[]` – columns (`VerticalTaskListsColumn`).
- `states[0].primary.items[].items[]` – task cards (`VerticalTaskElement`).
- `states[0].header` – header; tray layouts as the template allows; color backgrounds disabled.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Sprint board" }] } },
  "primary": {
    "showTitles": true,
    "style": "box",
    "taskLayout": "stack",
    "items": [
      { "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "To do" }] },
        "items": [
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Write spec" }] } },
          { "text": { "blocks": [
              { "type": "text", "textStyle": "title", "html": "Design review" },
              { "type": "text", "textStyle": "body", "html": "Owner: Ana" } ] }, "icon": "star", "color": "accent1" }
        ] },
      { "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "In progress" }] },
        "items": [
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Build API" }] } }
        ] },
      { "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Done" }] },
        "items": [
          { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Kickoff" }] }, "icon": "check-yes" }
        ] }
    ]
  }
}
```

The app's generator writes `label` as a plain string (`"To do"`) and cards as `{ id, text: { blocks } }`.

## Pitfalls

- Columns are `items[]` and cards are `items[].items[]`; a flat list of cards at the root renders each card as an
  empty column.
- An empty column is valid (`items: []`), but omitting `items` on a column is also fine (created empty).
- `icon` is a bare icon key string, not `content_type`/`content_value`; `"none"` disables it.
- Card text has no width to spare: 2–3 short lines per card, otherwise the whole board's font shrinks.
- `style` values are `"box"`, `"divider"`, `"no-frame"` (not `"none"`).
- Column titles are hidden entirely when `showTitles` is false, even if `label` is set.

## Rules and limits

- 1–7 columns (editor limit; not clamped on render). Columns share the width equally; the tallest header sets the
  header height for all columns (max 200px).
- Cards: `"stack"` layout searches a common text scale between 0.5 and 1 so every column fits; when even 0.5 does not
  fit, `isFit` is false (the slide reports a bad fit) but nothing is hidden.
- Null entries in `items` are replaced by `{}` on build (several stored examples contain `null` cards/columns).
- Migration `_migrate_10_02` on cards: sets `decorationStyle: "filled"` and clears `color: "auto"`.
- With `style: "divider"` and one column, no divider is drawn; the last column never gets a divider.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 7 | Columns, left to right, see "items[] model". |
| `showTitles` | boolean | default `true` | Show the column header text. |
| `style` | string | `"box"` (default), `"divider"`, `"no-frame"` | Column frame: white boxes with a stroke, vertical divider lines between columns (none with a single column), or no frame. |
| `taskLayout` | string | `"stack"` (default), `"fill"`, `"fit"` | Card sizing: natural heights with a shared text scale (0.5–1) found by best fit; every card in a column stretched to share the column height; or all cards sized as if every column had as many cards as the longest one. |
| `collectionColor` | string | palette color, default `"theme"` | Default card color (columns may override). |
| `orientation` | string | `"vertical"` | Read by an unused getter; omit. |
| `itemStyle`, `decorationStyle` | – | seen in examples | `itemStyle` belongs to `HorizontalTaskLists`; not read here. |

Plus the common fields, see `CollectionElement.md`.

#### items[] model (columns, `VerticalTaskListsColumn`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `label` | object or string | `{ blocks: [...] }` (`TextElement.md`); a plain string is converted to one block | Column title (placeholder "Type title"). Only rendered when `showTitles`. |
| `items` (required) | array | min 0 | Task cards, top to bottom, see below. |
| `collectionColor` | string | palette color | Default color of this column's cards (`"colorful"` cycles per card). |

#### items[].items[] model (cards, `VerticalTaskElement`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `text` (required) | object | `{ blocks: [...] }` | Card text, title-and-body structure (`"title"` block + optional `"body"` blocks). Font size is synced across all cards on the board and scaled to fit. See `TextElement.md`. |
| `icon` | string | icon key (`"star"`, `"check-yes"`, `"warning"`…) or `"none"` | 30px icon at the top-right of the card; adds right padding to the title. See `Icon.md`. |
| `color` | string | palette color | Card background color override (`"auto"` was migrated to none). |
| `decorationStyle` | string | `"filled"` | Cards are always filled (migration writes it). |

### Nested elements

- `items[]` -> `VerticalTaskListsColumn`: `label` -> `ColumnHeaderTextElement` (`TextElement.md`), `taskList` ->
  `VerticalTaskList` (collection of `VerticalTaskElement`, min 0 cards).
- Cards: `text` -> `TextElement.md`, `icon` -> `Icon.md`.
