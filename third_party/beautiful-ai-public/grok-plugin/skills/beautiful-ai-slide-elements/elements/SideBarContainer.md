# SideBarContainer

`SideBarContainer` renders the side tray ("sidebar") of a slide: a vertical strip on the left or right that
holds one to four grid cells, typically a photo, sometimes text, an icon list or a second image. It is a
`GridLayoutContainer` (see `GridLayoutContainer.md`) whose cells are `LayoutContainerItem`s
(`LayoutContainerItem.md`), with a `sidebar` layout engine and a fixed width instead of a free grid.
`CanvasElement` creates it for any template whose `availableTrayLayouts` contains the requested layout when
`layout.trayLayout` is `"left_tray"`, `"right_tray"`, `"left_inline"` or `"right_inline"`. It is never a
template's root element.

## Model location

- `states[0].tray` (the whole tray).
- `states[0].tray.items[]` — one `LayoutContainerItem` per grid cell; `states[0].tray.items[].childElement` —
  the cell's component (`TextAndImage` for pictures and text).
- The layout that places the tray is `layout.trayLayout` on the slide (see `Slide.md`).

## Minimal example

A single picture tray (`layout.trayLayout: "left_tray"`):

```json
{
  "tray": {
    "trayWidth": 440,
    "layoutEngineType": "sidebar",
    "gridLayout": { "cols": 12, "rows": 12, "cells": [ { "x": 0, "y": 0, "width": 12, "height": 12 } ] },
    "items": [
      {
        "id": "tray-1",
        "componentType": "TextAndImage",
        "cellColor": "background_accent",
        "childElement": { "content_type": "image", "content_value": "<asset id>" }
      }
    ]
  }
}
```

Two stacked cells, picture above a coloured text cell (`sidebar` preset, `cols: 6, rows: 60`):

```json
{
  "tray": {
    "trayWidth": 440,
    "layoutEngineType": "sidebar",
    "gridLayout": { "cols": 6, "rows": 60, "cells": [ { "x": 0, "y": 0, "width": 6, "height": 30 }, { "x": 0, "y": 30, "width": 6, "height": 30 } ] },
    "items": [
      { "id": "tray-1", "componentType": "TextAndImage", "cellColor": "none",
        "childElement": { "__generateImage": { "search": "team working in a bright office", "assetType": "image", "isGenerating": true } } },
      { "id": "tray-2", "componentType": "TextAndImage", "cellColor": "accent2",
        "childElement": { "text": { "blocks": [ { "id": "b1", "type": "text", "textStyle": "title", "html": "Our team" } ] } } }
    ]
  }
}
```

## Pitfalls

- Writing `states[0].tray` without `layout.trayLayout` (or with `"none"`) renders nothing; writing
  `layout.trayLayout` without `states[0].tray` renders one empty placeholder cell.
- A `trayLayout` the template does not allow is dropped silently: check `availableTrayLayouts` in the template
  list first (many image / headline / diagram templates allow none).
- `items` without `componentType` render as grey placeholders (`GridPlaceholder`); always set
  `"componentType": "TextAndImage"`.
- Mixing the legacy item form (`content_value` on the item) with `childElement` on the same item: only
  `childElement` is read then. Put the content in `childElement`.
- Leaving `__generateImage.isGenerating: true` next to a `content_value` shows a generation spinner in the
  editor until a generation job runs.
- Copy neither `aoiLeft`/`aoiTop`/`scale`/`assetProps`/`assetWidth` (crop cache computed for a specific
  asset, see `MediaElement.md`) nor `null` entries in `items` / `gridLayout.cells` from stored examples.
- `layoutEngineType: "preserve-aspect"` is only meaningful for inline trays; with a full-bleed tray the editor
  switches it back to `"sidebar"`.

## Rules and limits

- Only built when `layout.trayLayout` is one of `left_tray`, `right_tray`, `left_inline`, `right_inline`
  **and** that value is in the template's `availableTrayLayouts` (default: all four; `[]` for `image`,
  `collage`, `headline2`, `section`, `title`, `timeline`, `journey`, `logogrid`, `product_laptop`,
  `swot_diagram`, `cycle_diagram`, `connection_diagram`, `contactus`, `authoring`, `textgrid_photos`,
  `sequence`, `puzzle`, `horizontal-funnel`, `action-number`, ...; `arrow_bars`: right side only). Otherwise
  `layout.trayLayout` is reset to `"none"` and the tray is not rendered (no error). `bottom_tray` /
  `top_tray` values are mapped to `right_tray` internally but are never permitted by a template.
- Full-bleed trays (`left_tray` / `right_tray`): the full canvas height (minus the theme border, if the theme
  draws one), `trayWidth` wide, flush with the slide edge; header, primary and footer are laid out in the
  remaining width.
- Inline trays (`left_inline` / `right_inline`): placed inside the primary area, after the header and inside
  the canvas margins, `trayWidth` wide with a 40 px gap to the primary element.
- `trayWidth` is clamped to 50–640 by the editor only; a wider tray simply leaves less room for the primary
  element, which then may not fit (layout error). `CanvasElement` considers 200 px the minimum useful width.
- Item count follows `gridLayout.cells`: more cells than items creates empty `TextAndImage` cells, fewer cells
  drops items. Keep `items.length === gridLayout.cells.length`. The maximum of 4 is enforced by the editor
  UI, not at build time.
- Deleting the last item from the editor resets `layout.trayLayout` to `"none"` and `states[0].tray` to
  `null`.
- A `maskType` on a right-side tray is mirrored horizontally.
- The tray exports to the shared model under `sidebar`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | object[] | 0–4 entries (`minItemCount` 0, `maxItemCount` 4); default `[{}]` from the schema | One `LayoutContainerItem` per grid cell, in cell order. Missing entries are padded with `{ "componentType": "TextAndImage", "childElement": {} }` (and the previous item's `cellColor`) up to the number of cells; extra entries beyond the cell count are dropped. |
| `trayWidth` | number (px) | default `440`; editor range 50–640 | Width of the tray. For `left_tray` / `right_tray` the content area is the canvas minus this width; for inline trays the primary element loses this width plus a 40 px gap. |
| `gridLayout` | object | `{ cols, rows, cells: [{ x, y, width, height }] }`; default one cell `{ cols: 12, rows: 12, cells: [{ x: 0, y: 0, width: 12, height: 12 }] }` | How the cells split the tray. The `sidebar` presets use `cols: 6, rows: 60`: 1 cell `6x60`; 2 cells stacked `6x30` each; 3 stacked `6x20`; 4 stacked `6x15`; 2 side by side `3x60`; 2x2 `3x30`. The number of `cells` defines the number of rendered items. |
| `layoutEngineType` | string | `"sidebar"` (default, schema), `"preserve-aspect"` (inline trays only, keeps the image aspect) | Layout engine. The editor forces `"sidebar"` when switching to a full-bleed tray. Other engines (`"flex"`, `"custom"`, ...) are not offered for trays. |
| `showGutter` | boolean | default `false` | 10 px gaps between cells (and around them when full-bleed). |
| `items[].id` | string | uuid; generated when missing | Item identity (see `CollectionElement.md`). |
| `items[].componentType` | string | `"TextAndImage"` (what trays are for); any other `LayoutContainerItem` component (`"Chart"`, `"Table"`, ...) builds too; absent → `"GridPlaceholder"` (empty placeholder) | Which element renders the cell. |
| `items[].cellColor` | string | palette colour name, `"none"`; default: previous item's colour, else none | Cell background colour (behind text, or behind a transparent image). |
| `items[].childElement` | object | `TextAndImage` model (`TextAndImage.md`): `content_type` + `content_value` for a picture, `text` for text, or both | The cell content. If `childElement` is absent the component reads the item object itself (legacy form: `content_type` / `content_value` / `text` directly on the item, as in older examples). Prefer `childElement`. |
| `items[].childElement.__generateImage` | object | `{ "search": "<image prompt>", "assetType": "image", "isGenerating": true }` | Asks the app to generate / find the tray picture instead of giving `content_value`. Only set it when you want generation; remove it when you fill `content_value` yourself. |
| `maskType`, `borderColor`, `borderShadow`, `frame` | | see `GridLayoutContainer.md` | Shared grid container styling (image mask / frame); `frame: "light"` / `"dark"` are legacy and migrated to `borderColor` / `borderShadow`. |
| `fullBleed` | – | ignored | Derived: a tray is full-bleed when `trayLayout` is `left_tray` / `right_tray`, never for inline trays. |
| legacy | – | `trayElement`, `aspectRatio`, `layoutType`, `trayColor`, `userFontScale`, a numeric string `gridLayout` (`"1"`), `content_*` / `aoi*` / `scale` on the tray object itself, `text` on the tray object | Pre-v10 tray models; `_migrate_10_02` of `GridLayoutContainer` converts them (`text` becomes an item, `gridLayout` index becomes a cells object, `aspectRatio: "fit"` becomes `layoutEngineType: "preserve-aspect"`). Never write. |

Plus the common fields of `GridLayoutContainer.md` and `BaseElement.md`.

### Nested elements

- `items[]` -> `LayoutContainerItem` (`LayoutContainerItem.md`), 0–4 items, in `gridLayout.cells` order; the
  item's `childElement` -> the component named by `componentType`, normally `TextAndImage`
  (`TextAndImage.md`) which renders a `Picture` / `Icon` / `Video` (`ContentElement.md`) and/or a text block.
- Default item (`defaultItemData`): `{ "componentType": "TextAndImage", "childElement": {} }`.
