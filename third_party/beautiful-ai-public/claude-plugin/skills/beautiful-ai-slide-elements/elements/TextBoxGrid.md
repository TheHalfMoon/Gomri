# TextBoxGrid

A grid of up to 8 decorated text boxes, each holding a title-and-body text and an optional ornament (number, letter
or icon badge) on its edge. The grid is either one of the named cell layouts (`text-grid-*`) or a procedural grid
computed from the item count. Root element of the `textBoxGrid` template ("Text Boxes"). Items are `TextBoxGridItem`
(documented here, no separate file).

## Model location

- `states[0].primary` – the `TextBoxGrid` model (root).
- `states[0].primary.items[]` – one `TextBoxGridItem` per box.
- `states[0].primary.items[].ornament` – the ornament model of a box (only for `ornament: "icon"`).

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Three pillars" } ] }
  },
  "primary": {
    "collectionColor": "colorful",
    "fitToText": true,
    "ornament": "icon",
    "items": [
      {
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Keep decks on brand" },
          { "type": "text", "textStyle": "body", "html": "Locked themes and a shared asset library." }
        ] },
        "ornament": { "content_type": "icon", "content_value": "paint-palette" }
      },
      {
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Build together" },
          { "type": "text", "textStyle": "body", "html": "Real-time editing, comments and assignments." }
        ] },
        "ornament": { "content_type": "icon", "content_value": "people-circle" }
      },
      {
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Share with confidence" },
          { "type": "text", "textStyle": "body", "html": "Password protection and secure links." }
        ] },
        "ornament": { "content_type": "icon", "content_value": "link-chain" }
      }
    ]
  }
}
```

## Pitfalls

- `ornament` on the root is a string (the badge type); `ornament` on an item is an object (the icon slot). Mixing them up renders no badge.
- With `ornament: "icon"` every item needs `ornament.content_value`, otherwise that badge is an empty icon placeholder.
- Do not copy `gridLayout`/`textBoxGridLayoutId` from a slide with a different item count: a layout with fewer cells is silently ignored, one with more cells leaves empty cells.
- `fitToText` is not set by the template `defaultData`; set it explicitly (`true` is what the app's generator uses) if you want compact boxes.
- Long bodies shrink the font of every box (sizes are synced); keep boxes balanced.
- A box looks right with 2–4 lines of text; the layout decides how many lines the same text gets. Three stacked full-width boxes (`flipOrientation: true`) with one-line bodies are hollow frames with empty space under the text, and the same boxes side by side with `fitToText: false` have the text sitting at the top of tall cards. Pick the layout by lines per box: 2–3 items with one or two short lines each, stacked (`flipOrientation: true`) with `fitToText: true` and a side tray (`layout.trayLayout`) that narrows them so the lines wrap; items with two or three sentences side by side (`flipOrientation: false`) so they wrap to 3–4 lines; `fitToText: false` only when the text fills the cell anyway.

## Rules and limits

- More than 8 items: the layouter marks the slide as not fitting (`maxItemCount` 8 is also enforced by the editor and importer).
- Deleting an item in the editor resets `gridLayout`/`textBoxGridLayoutId` so the layout matches the new count; when you change the item count yourself, drop both fields (or set an id with the right cell count) to avoid empty cells.
- A layout with fewer cells than items is ignored; the procedural grid for that count is used instead.
- Boxes narrower than 100px or wider than their cell make the slide report not fitting.
- `null` entries in `items` are replaced by `{}` (empty box) at build time.
- Migration: models older than v10 get `fitToText: true`.
- Template flags: `allowColorful`, header allowed, trays allowed. The app's generator uses `collectionColor: "colorful"`, `fitToText: true`, `singleRow` when there are at most 4 items, `ornament: "icon"` when items carry icons (else `"number"`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–8 objects | One entry per box, in reading order of the layout cells. |
| `textBoxGridLayoutId` | string | one of `text-grid-1`, `text-grid-2-horizontal`, `text-grid-2-vertical`, `text-grid-3-horizontal`, `text-grid-3-vertical`, `text-grid-4-grid`, `text-grid-4-row`, `text-grid-4-vertical`, `text-grid-5-horizontal-top`, `text-grid-5-horizontal-bottom`, `text-grid-6-grid`, `text-grid-7-top-heavy`, `text-grid-7-bottom-heavy`, `text-grid-8-grid` | Picks a named cell layout; takes precedence over `gridLayout`. When absent, a default is chosen from the item count, `flipOrientation` and `singleRow`, and both fields are written back to the model. |
| `gridLayout` | object | `{ "id", "cols": 12, "rows": 12, "cells": [ { "x", "y", "width", "height" } ] }` | The resolved layout (12x12 grid units). Written by the element; you may supply it instead of the id. Ignored (procedural grid used) when it has fewer cells than items. |
| `flipOrientation` | boolean | `false` (default) | 2–3 items: stack boxes vertically instead of side by side; 5 and 7 items: pick the mirrored layout. Also moves the ornament to the left edge for <4 items. |
| `fitToText` | boolean | absent = `false` for new models; set `true` by migration for old ones | `true`: boxes shrink to their text height and are vertically centered in the cell; `false`: boxes fill the cell. |
| `singleRow` | boolean | `false` | 4 items: `text-grid-4-row` instead of the 2x2 grid; 6 items and 5 items fall back to the procedural single-row grid (no named layout exists). |
| `ornament` | string | `"none"` (default), `"number"`, `"letter"`, `"icon"` | Badge drawn on the top (or left) edge of every box: 1,2,3… / A,B,C… / the icon in `items[].ornament`. |
| `ornamentSize` | number | `75` for icon, `50` otherwise | Badge diameter in px; only honored with fewer than 4 items. |
| `collectionColor` | string | `"theme"` (default) | Box color, per `CollectionElement.md`. |
| `decorationStyle` | string | theme default; `"none"`, `"outlined"`, `"filled"`, `"muted"`, `"fillAndStroke"` | Box style inherited by items. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (TextBoxGridItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `text` (required) | object | `{ "blocks": [...] }` | Title-and-body text (`TextElement.md`): a `"title"` block followed by `"body"` / `"bulleted"` blocks. Text scales down to fit the box. |
| `textAlign` | string | `"left"` default; `"center"`, `"right"` | Alignment of the box text (alignment is allowed on this text). |
| `ornament` | object | `{ "content_type": "icon", "content_value": "<icon key>" }` | Only read when the root `ornament` is `"icon"`; the badge is a `ContentElement.md` slot (default asset type icon, images get a circular frame). Created as `{}` when missing. |
| `color` | string | palette color or `null` | Overrides the collection color for this box. |
| `hilited` | boolean | `false` | Emphasizes this box, de-emphasizes the others. |
| `decorationStyle` | string | inherits from root | Per-box style. |

### Nested elements

- `items[]` -> `TextBoxGridItem`; min 1, max 8 (`maxItemCount`); order = array order mapped onto the layout cells in order.
  - `text` -> `TextElement.md` (title-and-body, scale-to-fit, font size synced across boxes, box decoration behind the text).
  - `ornament` -> `Ornament.md` (badge). `"number"`/`"letter"` need no model (they use the item index); `"icon"` reads `items[].ornament` as a `ContentElement.md`.
