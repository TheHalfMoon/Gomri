# PhotoCollage

`PhotoCollage` ("Image Grid" in the editor) is a `GridLayoutContainer` whose cells are always `TextAndImage` cells:
a 12x12 grid of image / text / icon / video tiles with optional gutters and full-bleed. It is the root element of the
`image` template (one big tile) and the `collage` template (several tiles). Its subclass `CarouselGridContainer` is
the page of an `ImageCarousel` (see `ImageCarousel.md`), and `HeadlineImages` (headline templates) reuses its items.
The grid mechanics (`gridLayout`, `layoutEngineType`, cell sizing) are those of `GridLayoutContainer.md`; this doc
lists what PhotoCollage adds or fixes.

## Model location

- `states[0].primary` for `image` and `collage`.
- `states[0].primary.items[]` for `textgrid_carousel` (each carousel page is a `CarouselGridContainer` sharing the
  page item's model).

## Minimal example

`collage`, three photos side by side with captions (`states[0]`):

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Regional Revenue Snapshot" } ] } },
  "primary": {
    "layoutEngineType": "custom",
    "gridLayout": {
      "cols": 12, "rows": 12,
      "cells": [
        { "x": 0, "y": 0, "width": 4, "height": 12 },
        { "x": 4, "y": 0, "width": 4, "height": 12 },
        { "x": 8, "y": 0, "width": 4, "height": 12 }
      ]
    },
    "showGutter": true,
    "fullBleed": false,
    "items": [
      { "componentType": "TextAndImage", "cellColor": "background_accent",
        "childElement": { "content_type": "image", "content_value": "<assetId-1>-I",
          "text": { "blocks": [ { "type": "text", "textStyle": "headline", "html": "$1.9M" } ] }, "textPosition": "bottom_left" } },
      { "componentType": "TextAndImage", "cellColor": "background_accent",
        "childElement": { "content_type": "image", "content_value": "<assetId-2>-I" } },
      { "componentType": "TextAndImage", "cellColor": "background_light",
        "childElement": { "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Midwest" } ] } } }
    ]
  }
}
```

`image` (one full-bleed photo, no header), as the template's `defaultData` plus an asset:

```json
{
  "primary": {
    "fullBleed": true,
    "showGutter": false,
    "items": [
      { "componentType": "TextAndImage", "childElement": { "content_type": "image", "content_value": "<assetId>-I" } }
    ]
  }
}
```

## Pitfalls

- `items.length` must equal `gridLayout.cells.length` (except `preserve-aspect`), otherwise placeholder tiles appear
  or trailing items vanish.
- `layoutEngineType: "flex"` (the default) re-snaps authored cells to the preset layout for that item count; use
  `"custom"` when the exact cell rectangles matter.
- Cells must tile the 12x12 grid without overlap; the layout engines do not validate overlaps.
- Do not set `fullBleed` together with `aspectRatio: "fit"` / `layoutEngineType: "preserve-aspect"`; it is forced
  off.
- Every tile needs `componentType: "TextAndImage"`; `cellColor` is on the tile, not inside `childElement` (legacy
  examples have it in both places; the inner one is ignored).
- `null` cells/items from stored examples are tolerated but should not be emitted.

## Rules and limits

- **Item/cell count sync** (all engines except `preserve-aspect`): at build time, items are appended
  (`{ componentType: "TextAndImage", childElement: {}, cellColor: <last item's> }`) until there is one per cell, and
  extra items beyond `gridLayout.cells.length` are dropped. Always give exactly as many items as cells.
- Max 10 tiles (`maxItemCount`, enforced by the editor's add/paste actions; at render time the cell-count sync
  above is what limits items); the app's own generator uses a 15-column grid for 10 tiles.
- With a single tile, animations are off by default and the footer takes its background from the tile (image ->
  "image" background, else the tile's `cellColor`).
- `fullBleed` tiles with `showGutter` get an outer gutter; without `showGutter` the single tile touches the edges.
- Pasting an image onto the grid is allowed (`canPasteImage`), and text can be dropped into empty tiles.
- Migration 10.02: legacy flat items (`content_type`/`text` directly in `items[]`, legacy `gridLayout` as a *number*
  index into preset layouts) are wrapped into `childElement`, `cellColor: "auto"` becomes the slide color, and
  `childElement.frameType` is deleted. Stored examples with `migrationVersion < 10.02` show the flat shape; new
  models must use `childElement`.
- Template flags: `image` - `allowHeader`, no trays, no element attribution, default `headerPosition: "none"`;
  `collage` - `allowHeader` with `availableHeaderPositions` `top`/`left`, element attribution allowed, no trays.
  Both: `allowFooter`, `preventDefaultFooter`, `allowColorful`, `allowColorBackgrounds: false`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array of cell items | `[{ id?, componentType: "TextAndImage", cellColor?, childElement: {...} }]`; min 1, max 10 | One entry per grid cell, in cell order. `componentType` is forced to `"TextAndImage"` by `PhotoCollageItem`; the content is `childElement` (see `TextAndImage.md`); `cellColor` is the tile background (see `LayoutContainerItem.md`). Default item (what the "+" button adds): `{ componentType: "TextAndImage", childElement: {} }`. |
| `gridLayout` | `{ cols, rows, cells: [{ x, y, width, height }] }` | default `{ cols: 12, rows: 12, cells: [{ x: 0, y: 0, width: 12, height: 12 }] }` | Cell rectangles in grid units; `cells[i]` is the cell of `items[i]`. Missing `cols`/`rows` default to 12; missing `cells` defaults to one full cell. |
| `layoutEngineType` | string | `"flex"` (default), `"preserve-aspect"`, `"custom"`, `"fixed"`, `"single_cell"` (also `"headline"`, `"dashboard"`, `"sidebar"`, `"bottom_tray"`, `"stack_diagram"` used by other containers) | How `gridLayout` is interpreted: `flex` snaps to the built-in photo-collage layouts for the item count, `custom` uses the authored cells as is, `preserve-aspect` keeps each image's aspect ratio (items are *not* synced to the cell count in that mode, and `fullBleed` is forced off). |
| `fullBleed` | boolean | default `false` (template defaults set `true`) | Grid extends to the slide edges (no 50 px canvas margins; 50 px bottom margin kept when the element text block is inline). Ignored (false) when `aspectRatio` is `"fit"`. |
| `showGutter` | boolean | default `false` | 10 px gaps between tiles (and around them when `fullBleed`). Only honored when there is more than one tile or `fullBleed` is on. Full-bleed + gutter also reserves footer space. |
| `aspectRatio` | string | `"fill"` (default) or `"fit"` | Legacy: `"fit"` disables `fullBleed` and is migrated to `layoutEngineType: "preserve-aspect"`. Prefer `layoutEngineType`. |
| `frame` | string | `"none"` (default), legacy `"light"` / `"dark"` | Legacy tile border: migrated to `borderColor` (`"white"` / `"black"`) and `borderShadow`. |
| `borderColor`, `borderShadow` | string / boolean | palette color / default none | Stroke color and shadow drawn on every tile by `LayoutContainerItem`. |
| `maskType` | string | a device/mask frame id | Applies one image frame to the whole grid (used for trays). |
| `showTitle` | boolean | default `false` | Per-cell chart titles (dashboard feature; not used for photo tiles). |
| `collectionColor` | string | palette color, default `"theme"` | Collection color inherited by the tiles' decorations/icons. Written by the 10.02 migration from the slide color. |
| `showCaption`, `matchTextScale`, `layoutType`, `customGridCols`, `customGridRows`, `cols`, `rows` | | | Present in template defaults / stored examples but **not read** by the v10 element (`layoutType: "grid"` and `matchTextScale: true` come from the template `defaultData`). Harmless; omit. |

### Nested elements

- `items[]` -> `PhotoCollageItem` (a `LayoutContainerItem.md` whose `componentType` is always `"TextAndImage"` and
  which is selectable as a "Cell"), one per `gridLayout.cells[]` entry, in array order. `maxItemCount` is 10.
- `items[].childElement` -> `TextAndImage.md`.

#### items[] model

```json
{
  "id": "optional, generated when missing",
  "componentType": "TextAndImage",
  "cellColor": "background_accent",
  "childElement": { "content_type": "image", "content_value": "<assetId>", "text": { "blocks": [] } }
}
```

`cellColor` values seen: `"none"`, `"transparent"`, `"theme"`, `"background_accent"`, `"background_light"`,
`"background_dark"`, `"accent1"`..`"accent10"`, `"black"`, `"white"`, `"use-image-background"`, `"auto"` (legacy ->
slide color). A `null` entry is replaced by `{}` (an empty placeholder tile).
