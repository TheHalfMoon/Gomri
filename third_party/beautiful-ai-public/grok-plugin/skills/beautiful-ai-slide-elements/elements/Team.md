# Team

`Team` ("Team Members") shows up to eight people, each as a framed portrait with a name/title text block, arranged
in one or more rows; the orientation (portrait above text vs. beside it) is chosen automatically unless fixed. It is
the root element of the `team` template. Items are `TeamItem`s (folded below).

## Model location

- `states[0].primary` - the list.
- `states[0].primary.items[]` - one member. The item's `FramedMediaElement` -> `ContentElement` -> `Picture` share
  the item object, so the portrait fields sit directly on the item next to `text`.

## Minimal example

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Recent Hires" } ] } },
  "primary": {
    "items": [
      { "content_type": "image", "content_value": "<assetId-1>-I",
        "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Ada Lovelace" }, { "type": "text", "textStyle": "body", "html": "Head of Engineering" } ] } },
      { "content_type": "image", "content_value": "<assetId-2>-I",
        "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Grace Hopper" }, { "type": "text", "textStyle": "body", "html": "CTO" } ] } }
    ]
  }
}
```

## Pitfalls

- Portrait fields live on the item (no `childElement`); `text` is `{ blocks }`, not `title`/`body` strings.
- More than 8 members is outside the supported range (the editor refuses to add them); they still render, in the
  compact fallback layout.
- `frameType: "none"` does not give a frameless photo here; it becomes an unframed rectangle (image still clipped to
  a rect). Use `"circle"`/`"rounded_rect"` for a visible frame or leave `"theme"`.
- An empty `content_value` shows the silhouette placeholder, which looks intentional in thumbnails - make sure every
  member has a portrait or drop the item.
- Long `body` text forces the horizontal/small layouts; keep name + one-line role for the vertical card look.

## Rules and limits

- Vertical items: portrait at the style's fixed content size (square), text centered under it. Horizontal items:
  portrait left, text vertically centered (or top-aligned when taller).
- Auto orientation falls back step by step until the layouter reports `isFit` and the text fits; the result is not
  stored in the model.
- `decorationStyle` is always `"outlined"` for the portrait frame; `decorationStyle` in the model is ignored.
- Template flags: `allowColorful: false`; header and trays allowed (examples use `right_inline` trays and inline
  element text blocks for a conclusion).
- `maxItemCount` (8) is enforced by the editor's add/duplicate/paste actions and by template import
  (`items.splice(8)`), not at render time: extra authored items are still built and squeezed by the layouter.
- `collectionColor` is written as `"theme"` on build when absent.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

List (`states[0].primary`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 8 | Members in order. Template default: three `{ content_type: "image", content_value: "" }`. |
| `orientation` | string | `"vertical"` (portrait above text), `"horizontal"` (portrait left of text), absent = auto | Auto tries vertical, then horizontal, then horizontal with 100 px min item height, then a compact "small" style. |
| `collectionColor` | string | palette color, default `"theme"` | Frame color for items without their own `color`. |
| `userFontScale`, `forceSingleColumn` | | | Legacy; ignored. |

Member (`items[]`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"image"` (default via `defaultAssetType`) | Portrait kind; icons/logos are possible but not the intent. |
| `content_value` | string | image asset id (`<hex>-I`) | Empty -> a built-in person-silhouette placeholder is drawn inside the frame (no "add image" overlay text). |
| `aoi*`, `scale`, `flipHorizontal`, `filter*`, `mediaOpacity`, `assetWidth/Height`, `assetName`, `assetProps`, `enableFaceDetection`, `__generateImage` | | see `MediaElement.md` / `Picture.md` | Crop/filters. The generator sets `enableFaceDetection`-friendly prompts; `__generateImage` must be removed once `content_value` is set. |
| `text` | `{ blocks }` | title + body | Name (`textStyle: "title"`) and role/details (`"body"`); block format in `TextElement.md`. Font size is synced across members. |
| `frameType` | string | `"theme"` (schema default: theme `styleShape`), `"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`, device ids; `"none"` is turned into an unframed rect (`unframedRect`) because unframed images are not allowed here | Portrait frame; `decorationStyle` is fixed to `"outlined"`. |
| `color` | string | palette color | Per-member frame color. |
| `frameColor` | string | palette color | Explicit frame color (wins over `color`). |
| `titleTextStyle`, `showBody`, `accentColor`, `body`, `title` | | | Legacy (pre-10) fields present in most stored examples; ignored by v10. |

### Nested elements

- `items[]` -> `TeamItem` (folded here), max 8, array order. Each builds:
  - `content` -> `FramedMediaElement` (`defaultAssetType: "image"`, no unframed images, silhouette placeholder) ->
    `ContentElement.md` -> `Picture.md`.
  - `text` -> `TextElement.md` (title + body, auto height, synced font size).
- The list uses the row layouter (`calcRowLayout`) with per-orientation styles (`vertical`, `horizontal`, `small`).
