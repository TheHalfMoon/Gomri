# ProcessDiagramChevrons

`ProcessDiagramChevrons` ("Process Diagram") renders a row (wrapping to a second row when needed) of arrow-shaped
chevrons, each with a short title inside the shape, an optional description (`body`) above/below it and an optional
ornament (number, letter or icon) on the shape's edge. It is the root element of template `step_chevrons`. It
extends `ProcessDiagram.md` (shared `items`/`collectionColor`). The item class `ProcessDiagramChevronItem`, the
shape `ProcessDiagramChevronShape` (SVG polygon + title text) and the description `ProcessDiagramDescription` (a
selectable wrapper around one `TextElement`) are internal and documented here.

## Model location

- `states[0].primary` - the collection (root of `step_chevrons`).
- `states[0].primary.items[]` - one `ProcessDiagramChevronItem` per step.
- `states[0].primary.items[].text` - title inside the chevron (`ProcessDiagramChevronShape.text`).
- `states[0].primary.items[].body` - description outside the chevron (`ProcessDiagramDescription.body`).

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "How we work", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "theme-to-dark",
    "ornament": "icon",
    "textLayout": "below",
    "items": [
      {
        "content_type": "icon", "content_value": "search",
        "text": { "blocks": [{ "html": "Discover", "type": "text", "textStyle": "title" }] },
        "body": { "blocks": [{ "html": "Interviews and data review", "type": "text", "textStyle": "body" }] }
      },
      {
        "content_type": "icon", "content_value": "pencil",
        "text": { "blocks": [{ "html": "Design", "type": "text", "textStyle": "title" }] },
        "body": { "blocks": [{ "html": "Prototype and validate", "type": "text", "textStyle": "body" }] }
      },
      {
        "content_type": "icon", "content_value": "rocket",
        "text": { "blocks": [{ "html": "Deliver", "type": "text", "textStyle": "title" }] },
        "body": { "blocks": [{ "html": "Ship and measure", "type": "text", "textStyle": "body" }] }
      }
    ]
  }
}
```

Without descriptions: omit `body` on every item and `textLayout` (or set `"none"`); with `ornament: "number"` the
icon fields are not needed.

## Pitfalls

- Putting the description as a second block inside `text` renders it *inside* the chevron (tiny); use `body` for
  text outside the shape.
- `textLayout: "above"`/`"below"` without any `body` does nothing (getter returns `"none"`); `textLayout: "none"`
  with bodies present does not hide them (it alternates them). To hide descriptions, remove `body` from the items.
- `ornament: "icon"` without `content_value` on an item shows an empty "add icon" ornament; give every item an icon
  or use `"number"`.
- Mixed items (some with `body`, some without) are allowed; the shapes stay aligned in the row, the body-less steps
  simply show no description. For a uniform look give every step a `body` or none.
- Do not write `__generateImage` on items you filled yourself (see `ContentElement.md`).

## Rules and limits

- The chevron height is fixed (`125px * itemHeight`); the title text scales down to fit inside, so long titles become
  small. Descriptions take the remaining height (`above`/`below`: all of it; `alternate`: half each side).
- With an ornament the shape gets extra top/bottom padding (30px/20px) so the circle does not cover the text.
- Two-row layout happens when the items do not fit one row (10 items at 200px min width); then `textLayout`
  `"above"`/`"below"` are ignored (the UI only offers `"none"`/`"alternate"` in that state).
- Migration `_migrate_10`: a legacy `body` written as a text object (`{ text, styles }`) is converted to `{ blocks }`
  with `textStyle: "body"`. Legacy `title` objects next to `text` are ignored.
- Import from other templates maps a list item's last secondary text to `body` and the rest into `text`; icons are
  copied only when `ornament` is already `"icon"`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-10 items | Steps, left to right. |
| `ornament` | string | `"none"` (default), `"number"`, `"letter"`, `"icon"` | Adds an `Ornament.md` (50px circle) on each chevron: 1,2,3 / A,B,C (computed from position) or the item's icon (`content_type`/`content_value` on the item). |
| `textLayout` | string | `"none"` (default), `"above"`, `"below"`, `"alternate"` | Where item descriptions (`body`) go. The getter returns `"none"` whenever no item has a `body`; with bodies present, `"none"` falls through to the alternating layout. When the items wrap to 2 rows the layout is forced: row 1 descriptions above, row 2 below. |
| `itemHeight` | number | `0.5`-`1.5`, default `1` | Multiplier on the chevron height (125px in the default theme). |
| `collectionColor`, `decorationStyle` | | see `ProcessDiagram.md` | |

#### items[] model (`ProcessDiagramChevronItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }` (`title_and_body`), see `TextElement.md` | Title drawn inside the chevron (scaled to fit, centered). Keep it to a few words. |
| `body` | object or `null` | `{ blocks }` (`title_and_body`, first block usually `textStyle: "body"`), default absent | Description outside the chevron. Present (non-null) = description shown (`showBody`); `null`/absent = no description for this step. Deleting the description in the UI sets `body: null`. |
| `content_type`, `content_value` | string | `"icon"` + icon key (any `ContentElement.md` media works, non-icons get a circular frame) | The ornament icon when `ornament` is `"icon"`. The ornament's `ContentElement` reads them from the item model. |
| `ornamentSize` | number | px, default 50 | Overrides the ornament circle size for this item. |
| `hilited`, `color`, `id` | | see `ProcessDiagram.md` | |

### Nested elements

- `items[]` -> `ProcessDiagramChevronItem` (1-10, `minItemWidth` 200px, at most 2 rows).
- `shapeContainer` -> `ProcessDiagramChevronShape`: `shape` (SVG polygon; the first item has a flat left edge, the
  others a notched one; chevron offset 30px) + `text` -> `TextElement.md` (`title_and_body`, scale-to-fit, font
  synced across items, alignment allowed).
- `body` -> `ProcessDiagramDescription` -> its `body` `TextElement.md` (`title_and_body`, scale-to-fit, synced).
- `ornament` -> `Ornament.md` (only when `ornament != "none"`), drawn at the top edge of the shape when the
  description is below (or there is none), at the bottom edge when the description is above; alternating per item
  in `"alternate"` layout.
