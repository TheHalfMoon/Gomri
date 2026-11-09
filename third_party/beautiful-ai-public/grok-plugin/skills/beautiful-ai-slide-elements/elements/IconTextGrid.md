# IconTextGrid

A grid of items that each pair an icon (or image/logo) with a title-and-body text. Items are laid out in one row of
vertical cards (icon above text) when they fit, otherwise in a column of horizontal cards (icon left of text). Root
element of the `textgrid_vertical_icons` template ("Icon List"). Items are `IconTextGridItem` (documented here, no
separate file).

## Model location

- `states[0].primary` – the `IconTextGrid` model (root).
- `states[0].primary.items[]` – one `IconTextGridItem` per entry.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Why customers choose us" } ] }
  },
  "primary": {
    "collectionColor": "colorful",
    "orientation": "auto",
    "items": [
      {
        "content_type": "icon",
        "content_value": "rocket",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Fast" },
          { "type": "text", "textStyle": "body", "html": "Decks in minutes, not hours." }
        ] }
      },
      {
        "content_type": "icon",
        "content_value": "shield",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Safe" },
          { "type": "text", "textStyle": "body", "html": "Brand guardrails on every slide." }
        ] }
      },
      {
        "content_type": "icon",
        "content_value": "people",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Collaborative" },
          { "type": "text", "textStyle": "body", "html": "Comments and real-time editing." }
        ] }
      }
    ]
  }
}
```

## Pitfalls

- Put the icon on the item itself (`content_type`/`content_value`), not inside `text`: the media slot reads the item model directly.
- `content_value: ""` renders an empty icon placeholder; use a real icon key from `list_icons` (the app's own generator falls back to `"star"`).
- Do not author `title`/`body` on new items; they are legacy fields that only get migrated into `text.blocks` when the stored slide version is older.
- More than 12 items, or very long bodies, make `"auto"` fall back to the horizontal column layout and may still not fit; check the render.
- `forceSingleColumn` does nothing; use `orientation` instead.

## Rules and limits

- The editor refuses to add a 13th item; the shared-model importer truncates to 12. A model with more items still builds but the layouter reports it as not fitting.
- `orientation: "auto"` switches to the horizontal layout when the vertical layout or its text does not fit. With a left/right tray or inline tray wider than 300px the horizontal layout uses tighter "large tray" styles.
- Item text font sizes are synchronized across all items (the smallest scale wins).
- Migrations: legacy `title`/`body` objects on an item are converted into `text.blocks` (title, then body); a stray `blocks` array left on an item by template switching is deleted.
- Template flags: `allowColorful`, header allowed; no special tray restriction.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–12 objects | One entry per card, rendered in array order. |
| `orientation` | string | `"auto"` (default), `"vertical"`, `"horizontal"` | `"vertical"`: one row of icon-above-text cards. `"horizontal"`: a column of icon-left-of-text cards, centered. `"auto"`: tries vertical, falls back to horizontal when the cards or their text do not fit. |
| `iconScale` | number | `1` (default); editor range 0.5–2 | Multiplies the icon/media box of every item. |
| `collectionColor` | string | `"theme"` (default) | Palette color for the item decorations/icons, per `CollectionElement.md` (`"colorful"` gives each item its own color). |
| `decorationStyle` | string | theme default; `"none"`, `"outlined"`, `"filled"`, `"muted"`, `"fillAndStroke"` | Inherited by items that do not set their own. |
| `forceSingleColumn` | boolean | present in `defaultData` as `false` | Not read by the element; harmless. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (IconTextGridItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. Provide a stable unique id when you update items in place. |
| `content_type` | string | `"icon"` (default asset type), `"image"`, `"logo"` | Media slot of the card, rendered by `FramedMediaElement.md` (unframed images are not allowed, so images always get a frame). See `ContentElement.md` for the slot fields. |
| `content_value` | string | icon key or asset id; `""` = empty placeholder | The icon (`list_icons`) or asset. |
| `frameType` | string | `"theme"` in every stored example | Frame of the media slot, see `FramedMediaElement.md`. |
| `text` | object | `{ "blocks": [...] }` | Title-and-body text (`TextElement.md`): first block `textStyle: "title"`, following blocks `"body"` or `"bulleted"`. |
| `color` | string | palette color or `null` | Overrides the collection color for this item. |
| `hilited` | boolean | `false` | Emphasizes this item and de-emphasizes its siblings. |
| `decorationStyle` | string | inherits from root | Per-item decoration style. |

### Nested elements

- `items[]` -> `IconTextGridItem`; min 1, max 12 (`maxItemCount`); order = array order. Each item nests:
  - `media` -> `FramedMediaElement.md` reading `content_type`/`content_value`/`frameType` (and the crop/scale fields) from the item itself.
  - `text` -> `TextElement.md` bound to `item.text`, block structure title-and-body, font size synced across items.
