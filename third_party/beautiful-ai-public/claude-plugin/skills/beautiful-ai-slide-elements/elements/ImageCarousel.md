# ImageCarousel

`ImageCarousel` is a flip-through list: each item is a full-size *page* that is itself a photo grid
(`CarouselGridContainer`, a `PhotoCollage`), and only the current page is visible; playback advances page by page
with a slide/fade transition and optional auto-play. It is the root element of the `textgrid_carousel` template
("Image Carousel"). Pages are `ImageCarouselItem`s; their cells are `TextAndImage` cells.

## Model location

- `states[0].primary` - the carousel.
- `states[0].primary.items[]` - one page (`ImageCarouselItem`; the page's `CarouselGridContainer` shares the same
  object, so the grid fields sit directly on the page item).
- `states[0].primary.items[].items[]` - the cells of a page (`PhotoCollageItem`), with
  `states[0].primary.items[].items[].childElement` -> `TextAndImage.md`.

## Minimal example

Two pages, each an image on the left and text on the right (`states[0]`):

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "How to use our AI workflow" } ] } },
  "primary": {
    "transition": "slide-left",
    "items": [
      {
        "layoutEngineType": "custom",
        "gridLayout": { "cols": 12, "rows": 12, "cells": [ { "x": 0, "y": 0, "width": 6, "height": 12 }, { "x": 6, "y": 0, "width": 6, "height": 12 } ] },
        "items": [
          { "componentType": "TextAndImage", "childElement": { "content_type": "image", "content_value": "<assetId-1>-I", "frameType": "rounded_rect", "frameScale": 0.95 } },
          { "componentType": "TextAndImage", "childElement": { "text": { "blocks": [
              { "type": "text", "textStyle": "title", "html": "Start with any input" },
              { "type": "text", "textStyle": "body", "html": "Prompt a topic, paste an outline, or add source material." } ] },
            "textAlign": "left", "verticalAlign": "middle" } }
        ]
      },
      {
        "layoutEngineType": "custom",
        "gridLayout": { "cols": 12, "rows": 12, "cells": [ { "x": 0, "y": 0, "width": 6, "height": 12 }, { "x": 6, "y": 0, "width": 6, "height": 12 } ] },
        "items": [
          { "componentType": "TextAndImage", "childElement": { "content_type": "image", "content_value": "<assetId-2>-I", "frameType": "rounded_rect", "frameScale": 0.95 } },
          { "componentType": "TextAndImage", "childElement": { "text": { "blocks": [
              { "type": "text", "textStyle": "title", "html": "Shape the story before design" } ] }, "textAlign": "left" } }
        ]
      }
    ]
  }
}
```

## Pitfalls

- Do not put `content_type`/`text` directly on a page item (legacy shape): nothing renders them in v10 unless the
  slide goes through the 10.02 migration. A page is a grid: `gridLayout` + `items[]` of `TextAndImage` cells.
- Keep every page's `items.length` equal to its `gridLayout.cells.length`.
- Use `layoutEngineType: "custom"` on pages whose cell rectangles you author; `"flex"` re-snaps them to presets.
- `autoPlayInterval` is milliseconds in the model (the UI shows seconds).
- Only the current page is editable/selectable in the editor; thumbnails show page 0.
- `wasMigratedFromV10` switches the text styling to the legacy stylesheet; never copy it from an example.

## Rules and limits

- Pages: at least one; the carousel keeps `currentIndex` in range when pages are deleted. Each page is a playback
  stage (`type: "carousel"`), so in the player every page is a click.
- Each page's cell count is synced to its `gridLayout.cells.length` (see `PhotoCollage.md`); the "+" page starts with
  one empty placeholder cell (`items: [{}]`, no `componentType`), which renders the grid placeholder until filled.
- Element animations are disabled by default (`disableAllAnimationsByDefault`); the carousel exposes a single
  "Fade in" animation.
- Migration 10.02 (`wasMigratedFromV10`): each legacy page (`content_type`/`content_value`/`text` flat on the item)
  becomes a two-cell page (image cell + text cell with `textPosition: "left"`, `textAlign: "left"`,
  `userWidth: 1100`), image on the left unless `layout: "right"`. Most stored examples predate this and show the
  legacy flat page shape; new models must use the page/grid/cell shape.
- Template flags: `allowColorful`, `canConvertToAuthoring: true`; header allowed (default `top`); trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Carousel (`states[0].primary`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1 page (`minItemCount` 1), max 10 (`CollectionElement` default) | Pages, in order. Template default: `[{ id }]`; the "+" page is `{ layoutEngineType: "flex", gridLayout: one 12x12 cell, items: [{}] }`. |
| `transition` | string | `"slide-left"` (default), `"slide-up"`, `"fade"` | Page change animation (direction reverses when going back in the editor; always forward in playback). |
| `autoPlay` | boolean | default `false` | In playback, advance automatically every `autoPlayInterval`. |
| `autoPlayInterval` | number | ms, default 2000 (UI edits in seconds) | Delay between auto-advances. |
| `loop` | boolean | default `false` | After the last page, go back to the first (auto-play and "next"). |
| `collectionColor` | string | palette color, default `"theme"` | Collection color for the cells. |
| `wasMigratedFromV10` | boolean | | Written by the 10.02 migration; makes text boxes use legacy v10 text styles. Do not set on new models. |
| `flip` | string | `"left"`, `"right"`, `"alternate"` | Read by `ImageCarouselItem.flip` but not used by the layout; legacy. |
| `forceSingleColumn`, `userFontScale` | | | Legacy (pre-10.02) fields seen in examples; ignored. |

Page (`items[]`, see `PhotoCollage.md` / `GridLayoutContainer.md` for the grid semantics):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated when missing | Page id. |
| `gridLayout` | `{ cols, rows, cells[] }` | default one full cell | Cell rectangles of this page. |
| `layoutEngineType` | string | `"flex"` (default), `"custom"`, `"preserve-aspect"`, `"headline"` | Grid engine for this page (the importer uses `"headline"` for image+text pages, the migration `"flex"`). |
| `items` | array of cells | one per `gridLayout.cells[]` | `{ componentType: "TextAndImage", cellColor?, childElement: {...} }`. |
| `showGutter`, `fullBleed` | boolean | default `false` | Gutters/full-bleed for this page's grid (`fullBleed` is disabled by the carousel: `allowFullScreen` is false, but the grid still reads `fullBleed`; examples use `showGutter` only). |
| `layout`, `contentSize`, `blocks` | | | Legacy page fields (`layout: "left"|"right"` chose the image side before 10.02); `blocks` is deleted by `_migrate_10`. |

### Nested elements

- `items[]` -> `ImageCarouselItem` (a `CollectionItemElement`; folded here). It builds exactly one child, `grid`
  -> `CarouselGridContainer` (a `PhotoCollage` without the 10.02 flat-item migration and without full-screen),
  sized to the whole carousel. Only the current page (`currentIndex`) is selectable/interactive; other pages are
  rendered at opacity 0 so their assets preload.
- `items[].items[]` -> `PhotoCollageItem` -> `childElement` -> `TextAndImage.md`.
