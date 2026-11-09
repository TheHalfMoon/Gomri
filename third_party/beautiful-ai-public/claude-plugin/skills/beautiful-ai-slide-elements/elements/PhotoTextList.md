# PhotoTextList

`PhotoTextList` ("Image with Text") lays out up to six equal-width columns, each with a framed image on top and a
title/body text underneath. It is the root element of the `textgrid_photos` template. Items are `PhotoTextListItem`s
(folded below).

## Model location

- `states[0].primary` - the list.
- `states[0].primary.items[]` - one column. The item's `FramedMediaElement` -> `ContentElement` -> `Picture` all
  share the item object, so the media fields sit directly on the item next to `text`.

## Minimal example

`states[0]` with a header and three photo columns (the app's own generator shape):

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Materials & Craftsmanship" } ] } },
  "primary": {
    "items": [
      { "content_type": "image", "content_value": "<assetId-1>-I", "frameType": "rect",
        "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Oak" }, { "type": "text", "textStyle": "body", "html": "Dense and durable." } ] } },
      { "content_type": "image", "content_value": "<assetId-2>-I", "frameType": "rect",
        "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Walnut" } ] } },
      { "content_type": "image", "content_value": "<assetId-3>-I", "frameType": "rect",
        "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Linen" } ] } }
    ]
  }
}
```

## Pitfalls

- Media fields go **on the item**, not in a `childElement` (that is the grid-cell shape; two stored examples carry
  stray `childElement`/`componentType` keys from a template switch - ignore them).
- `text` must be `{ "blocks": [...] }` with the title first; `body`/`title` string fields are legacy and ignored.
- More than 6 items is outside the supported range (the editor refuses to add them); they still render, squeezed.
- `mediaHeight` smaller than ~100 px makes the images tiny; leave it absent (9999) unless you need a short image
  row.
- `frameType: "theme"` can resolve to `"none"` on themes with `styleShape: "none"`; use `"rect"` for a predictable
  frame.
- Keep `frameType` identical across items unless mixed frames are intended; the list control writes all items at
  once, but the model allows per-item values.

## Rules and limits

- Columns are `(width - hGap * (n - 1)) / n` wide; all captions get the height of the tallest caption and all images
  the height of the tallest fitted image, so columns align. Items are then centered as a group.
- Rect / rounded-rect frames fill the column width at the media height; circle, octagon and device frames use
  `autoHeight` (they shrink to keep their aspect ratio).
- `frameType: "none"` keeps the photo's aspect ratio (`preserveAspectRatioForUnframed`), fitted to the media height.
- Every column's item background is reported as "image" for the selection widgets; text color is computed against
  the slide background.
- `maxItemCount` (6) is enforced by the editor's add/duplicate/paste actions and by template import
  (`items.splice(maxItemCount)`), not at render time: every authored item is built and the width is divided by all
  of them, so 7+ items render as ever narrower columns (not verified visually).
- Template flags: `variations: "list"`, `availableTrayLayouts: []` (no trays), `allowColorful`; header allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

List (`states[0].primary`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 6 | Columns, left to right. Template default: three empty items `[{}, {}, {}]`. New items copy the last item's `frameType`/`decorationStyle` (defaults `"rect"` / `"filled"`). |
| `mediaHeight` | number | px, written by schema as 9999 (= "as tall as the text allows"); UI range 100 .. available height | Max height of the image row. The effective height is `min(mediaHeight, slide height - tallest text)`, then further capped by the tallest fitted image. |
| `decorationStyle` | string | `"filled"` (schema default), `"outlined"`, `"muted"`, `"fillAndStroke"` | Default frame style for shape-framed images; items may override. |
| `collectionColor` | string | palette color, default `"theme"`; `"colorful"` gives each item its own accent | Frame/decoration color for items without their own `color`. |
| `frameType`, `frame`, `aspectRatio`, `forceSingleColumn`, `userFontScale`, `orientation`, `listStyle` | | | Seen in stored examples (legacy or template-switch leftovers); not read by the element. Item `frameType` is what counts. |

Column (`items[]`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"image"` (default via `defaultAssetType`), `"icon"`, `"logo"`, `"video"` | Media kind, see `ContentElement.md`. |
| `content_value` | string | asset id / icon key | The media. Empty -> add-image placeholder in the frame. |
| `aoi*`, `scale`, `flipHorizontal`, `filter*`, `mediaOpacity`, `assetWidth/Height`, `assetName`, `assetProps`, `enableFaceDetection`, `__generateImage` | | see `MediaElement.md` / `Picture.md` | Crop and filters. `__generateImage` must be removed when you set `content_value`. |
| `text` | `{ blocks }` | title + body structure | The caption: first block `textStyle: "title"`, optional second `"body"` (block format: `TextElement.md`). Font size is synced across columns. |
| `textAlign` | string | `"left"`, `"center"`, `"right"` | Alignment of the caption (and of the unused `title`). |
| `frameType` | string | `"rect"` (schema default), `"rounded_rect"`, `"circle"`, `"octagon"`, `"none"` (unframed, keeps the image aspect ratio), `"theme"` (theme shape), or a device frame id (`"browser_solid"`, `"laptop_stroke"`, `"iphone_15_pro"`, ...) | Image frame. The list-level "Item Frames" control writes it to every item. |
| `decorationStyle` | string | as above | Per-item override of the list's `decorationStyle` (shape frames only). |
| `color` | string | palette color | Per-item frame color (overrides `collectionColor`). |
| `frameColor` | string | palette color | Explicit frame color (wins over `color`). |
| `framePadding` | number | px, default 0 | Inset of the media inside a shape frame. |
| `title` | `{ blocks }` | | A `title` text element is built but never laid out; stored examples carry an empty `title` block. Omit. |
| `blocks`, `body`, `titleTextStyle`, `showText`, `cellColor`, `backdropPadding`, `verticalGap`, `accentColor` | | | Legacy fields from older versions/templates; `blocks` is deleted by `_migrate_10`, the others are ignored. |

### Nested elements

- `items[]` -> `PhotoTextListItem` (folded here), max 6, in array order. Each builds:
  - `media` -> `FramedMediaElement` (`defaultAssetType: "image"`, `fitToHeight`, unframed allowed) -> `content` ->
    `ContentElement.md` -> `Picture.md` / `Icon.md` / `VideoElement.md`.
  - `text` -> `TextElement.md` (title + body, auto height, alignment allowed, font size synced with siblings).
  - `title` -> `TextElement` (built, never positioned - dead).
