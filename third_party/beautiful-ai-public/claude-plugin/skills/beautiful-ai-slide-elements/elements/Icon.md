# Icon

`Icon` renders one glyph from the built-in icon catalog as an inline SVG path, colored from the palette. It is the
`asset` child `ContentElement` builds for `content_type: "icon"`, and is also used directly (with an `icon` option
instead of a model) by list decorations, task markers, pictographs and big-number change indicators. It is never a
root element and never has a model of its own: it reads the owning element's model.

## Model location

Same object as the owning `ContentElement` / list item, e.g. `states[0].primary.items[]` (icon list items,
`textgrid_vertical_icons`), `states[0].primary.items[].childElement` (a `TextAndImage` cell holding an icon),
`states[0].primary.items[].content` (UserTestimonial attribution with an icon), inline media blocks
(`text.blocks[].elementModel`).

## Minimal example

```json
{ "content_type": "icon", "content_value": "thumbs-up" }
```

With an explicit color (only honored on neutral backgrounds / unframed):

```json
{ "content_type": "icon", "content_value": "growth", "iconColor": "accent2" }
```

## Pitfalls

- `content_value` must be a catalog key: look it up (the MCP `list_icons` tool searches names and tags); a guessed
  key renders an empty slot without any error.
- Do not write `icon-chunky-star`: the element prepends `icon-<style>-` itself (a legacy `icon-...` value is passed
  through only by the asset store, not by the element's `_migrateIcons`).
- `iconColor` has no effect inside filled/colored frames or on colored cells; change the frame's
  `decorationStyle` (e.g. `"outlined"`, `"muted"`) or the cell color instead.
- Crop fields (`aoi*`, `scale`) are meaningless for icons; leave them out.

## Rules and limits

- Sizing: the glyph is fit into the given box (128x128 view box, aspect preserved) and then scaled by `iconScale`;
  `ContentElement` always passes `fitAsset: true` for icons, so the icon never crops.
- Legacy key migration: `table-check-circle` -> `check-yes-circle`, `table-check` -> `check-yes`, `table-x-circle`
  -> `cross-out-circle`, `table-x` -> `cross-out`, `table-circle-cross` -> `prohibit`, `table-star-outline` ->
  `star-none`, `table-star-half` -> `star-half`, `table-star-full` -> `star`, `table-thumb-down` -> `thumbs-down`,
  `table-thumb-up` -> `thumbs-up`, `table-circle-full` -> `full`, `table-circle-three-fourths` -> `quarters-three`,
  `table-circle-half` -> `contrast`, `table-circle-one-fourth` -> `quarter`, `table-circle-outline` -> `none`,
  `family-*` -> `family`, `hand-shake-multi` -> `hand-shake`. Use the new keys.
- Color resolution order (`_applyColors`), unless the owning `ContentElement` already set a color (see
  `ContentElement.md`):
  1. authoring canvas with `iconColor` -> that color (color-on-color allowed);
  2. the background (decoration/backdrop or the slide background) is a *color* (not light/dark neutral) -> `primary`
     (auto white/black on the color);
  3. neutral background and `iconColor` -> that color; else the stylesheet `iconColor`; else the element's decoration
     color (which for collection items is the item `color` / parent `collectionColor`).
  So on colored cells and filled frames, `iconColor` is ignored and the glyph becomes white/black automatically.
- Loading: a missing key (404) is silent (no glyph, no error); other fetch errors are logged. The icon style follows
  the theme; a model never names the style.
- Icons report 200x200 as content size to `ContentElement`, so they do not drive the parent's layout.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_value` (required) | string | an icon **key** from the built-in catalog (1072 keys, e.g. `"star"`, `"quote"`, `"thumbs-up"`, `"check-yes"`, `"pencil"`, `"paint-palette"`). Default: none -> nothing rendered | The element composes the asset id `icon-<style>-<key>`, where `<style>` is the theme's `iconStyle` (`"chunky"` or `"classic"`, default `"chunky"`), and fetches that SVG. Use the key only; never store the `icon-...` id. |
| `iconColor` | string | palette color name: `"primary"`, `"secondary"`, `"theme"`, `"accent1"`..`"accent10"`, `"background_light"`, `"background_dark"`, `"white"`, `"black"`, ...; default: none (auto) | Explicit glyph color. |
| `color` | string | palette color name | Legacy fallback: used for bullet icons on authoring canvases and by `ContentElement` as `iconColor ?? color`. Prefer `iconColor`. |
| `iconScale` | number | > 0, default: parent option, else style, else 1 | Multiplies the glyph size inside its box (e.g. 0.75 for ornaments, 1.5 for big markers). |

### Nested elements

None.
