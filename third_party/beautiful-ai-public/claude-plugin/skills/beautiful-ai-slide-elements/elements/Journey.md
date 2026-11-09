# Journey

Renders a winding "road" SVG across the slide with 1–10 milestones placed at fixed positions along it, each with a
marker (map pin, dot, or icon/image in a circle) and a title/body text, plus an optional start text and an optional
end flag with text. It is the root element of the `journey` template (`states[0].primary`). Milestone positions come
from a built-in layout table keyed by `milestoneStyle` and item count; authors only provide the ordered items.

## Model location

- `states[0].primary` – the Journey model (template `journey`).
- `states[0].primary.items[]` – milestones (`JourneyItem`).
- `states[0].primary.startMarker.start_marker` – start text (`JourneyStart`, a `TextElement`).
- `states[0].primary.endMarker.end_marker` – end flag text (`JourneyEnd`).
- `states[0].header` – header, top position only; no tray layouts (inline/tray element text and attribution allowed).

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Product journey" }] } },
  "primary": {
    "milestoneStyle": "with-icons",
    "showStartMarker": true,
    "showEndMarker": false,
    "startMarker": { "start_marker": { "blocks": [{ "type": "text", "textStyle": "title", "html": "2019" }] } },
    "collectionColor": "theme",
    "items": [
      { "content_type": "icon", "content_value": "lightbulb",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "2019: Idea" },
          { "type": "text", "textStyle": "body", "html": "First prototype" }
        ] } },
      { "content_type": "icon", "content_value": "rocket",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "2021: Launch" },
          { "type": "text", "textStyle": "body", "html": "Public release" }
        ] } },
      { "content_type": "icon", "content_value": "line-chart-up",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "2024: Scale" },
          { "type": "text", "textStyle": "body", "html": "10k customers" }
        ] } }
    ]
  }
}
```

The app's generator joins date and title into one `"title"` block, adds a `"body"` block, and chooses
`"with-icons"` when any milestone has an icon, else `"dots"`.

## Pitfalls

- `milestoneStyle` values are `"no-icons"`, `"with-icons"`, `"dots"` – not `"icons"`/`"pins"`; a typo breaks the render.
- Icons are ignored unless `milestoneStyle` is `"with-icons"`; conversely `"with-icons"` items without
  `content_value` show an empty circle (the default asset type is icon).
- Positions cannot be authored: items are laid out in array order along the road; reorder the array to reorder
  milestones.
- More than 10 items: the extras are silently not laid out.
- Keep text short (title + one short body line); the text box is fixed at roughly 160×100 px and the font scales down
  for the whole collection.
- `startMarker.start_marker` / `endMarker.end_marker` are nested one level deeper than the `show*Marker` flags;
  `endMarker.color` is the only per-marker color.
- `startConfig`/`endConfig`/`contentConfig` in stored examples are cache written by the element; do not copy them.

## Rules and limits

- Item count 1–10: the layout table has entries for exactly 1..10 items; the element lays out at most 10 and ignores
  extra items (they get no bounds). The editor refuses to add beyond 10.
- Layout is fixed: the road needs 1280×410 px (`minSize`); when the element is smaller, `isFit` is false and the
  slide may report a bad fit. Items are placed at table positions and centred in the available area; text boxes are
  160×100 px (per-item overrides in the table), markers 52×52 px by default.
- The road and markers recolor from the palette (`[foreground]` tags in the SVG) only on light/dark/accent/image
  backgrounds; on colored backgrounds markers fall back to white.
- `milestoneStyle` must be one of the three strings; the fallback path sets an unrelated `configType` field and still
  fails.
- No migrations in the current code (legacy per-item `x`/`title`/`body` fields are simply not read).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 10 | Milestones in path order (first item is at the start of the road). |
| `milestoneStyle` | string | `"no-icons"` (default), `"with-icons"`, `"dots"` | Marker style and layout table: map pins, icon/image circles, or small dots. Any other value crashes the render (no layout config). |
| `showStartMarker` | boolean | default `false` | Shows the start text near the beginning of the road (changes the road SVG). |
| `showEndMarker` | boolean | default `false` | Shows the end flag and its text at the end of the road. |
| `startMarker` | object | `{ start_marker: <text> }` | Start text (`{ blocks: [...] }`, see `TextElement.md`; legacy `{ text }`/string is converted). |
| `endMarker` | object | `{ end_marker: <text>, color? }` | End flag text; `color` (palette key) overrides the flag color. |
| `collectionColor` | string | palette color, default `"theme"` | Marker colors (`"colorful"`/`"collection-colorful"` cycles per item). Markers are always drawn filled. |
| `startConfig`, `endConfig`, `contentConfig` | object | written by the element | Layout cache copied from the built-in config on build; do not author. |
| `fit`, `scale`, `scroll`, `showContent` | – | legacy | Present in template defaults / old examples, not read. |

Plus the common fields, see `CollectionElement.md`.

#### items[] model (`JourneyItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `text` (required) | object | `{ blocks: [...] }` | Milestone text, block structure title-and-body (`"title"` + optional `"body"` blocks), see `TextElement.md`. Font size syncs across items and scales to fit the fixed text box (~160×100 px). |
| `content_type`, `content_value` | string | `"icon"` + icon key (default asset type), `"image"` + asset id | Marker media, only rendered when `milestoneStyle` is `"with-icons"` (`JourneyIconMarker`, a circle-framed `ContentElement`, see `ContentElement.md`; icons are scaled 0.6, pictures 0.9 inside the circle). |
| `color` | string | palette color | Per-item marker color override. |
| `x`, `hasBeenDragged`, `title`, `body`, `type`, `value`, `showArrowHead` | – | legacy / ignored | Seen in old examples; the current element positions items from its config table only. |

### Nested elements

- `items[]` -> `JourneyItem`: `text` -> `TextElement.md`; marker -> `JourneySvg` (static map-pin / dot SVG, no model)
  or, for `"with-icons"`, `content` -> `JourneyIconMarker` (`ContentElement.md`) bound to the item model.
- `path` -> `JourneySvg`: the road SVG selected by style and by `showStartMarker`/`showEndMarker` (no model).
- `start_marker` -> `JourneyStart` (`TextElement.md`) bound to `startMarker.start_marker`.
- `end_marker` -> `JourneyEnd`: `text` -> `TextElement.md` bound to `endMarker.end_marker`, `marker` -> `JourneySvg` flag.
