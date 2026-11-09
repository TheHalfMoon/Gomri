# GridLayoutContainer

`GridLayoutContainer` is the generic cell grid: it splits its area into a `cols` x `rows` grid (default 12 x 12), places
one rectangular cell per entry of `gridLayout.cells`, and renders one `LayoutContainerItem` per cell. The item's
`componentType` decides what the cell shows (chart, table, statistic, text/image, ...). It is never a template root
itself; the roots are its subclasses `Dashboard` (templates `dashboard`, `chart_*`, `table-v2`), `StackDiagram`
(`stackDiagram`) and `PhotoCollage` (`image`, `collage`, documented in `PhotoCollage.md`).

## Model location

- `states[0].primary` when the template's root is a subclass (`Dashboard`, `StackDiagram`, `PhotoCollage`).
- The same model shape is used by the bottom/side tray grid (`states[0].elementTextBlock` with `items[]`, see
  the tray docs); this file only covers the primary usage.

## Minimal example

`GridLayoutContainer` is abstract; this is the shared shape (shown as a `Dashboard` root, two cells side by side):

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Dashboard" } ] } },
  "primary": {
    "layoutEngineType": "dashboard",
    "showGutter": true,
    "gridLayout": {
      "cols": 12, "rows": 12,
      "cells": [
        { "x": 0, "y": 0, "width": 6, "height": 12 },
        { "x": 6, "y": 0, "width": 6, "height": 12 }
      ]
    },
    "items": [
      { "componentType": "Statistic", "cellColor": "background_accent", "childElement": { "ornamentType": "none", "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "$1.2M" } ] } } },
      { "componentType": "RadialBar", "cellColor": "background_accent", "childElement": { "value": 72, "format": "percent" } }
    ]
  }
}
```

## Pitfalls

- `items.length` must equal `gridLayout.cells.length`: extra items are silently dropped from the model, missing
  ones become empty placeholder cells.
- Cells are matched to items **by index**; reordering `cells` without reordering `items` moves content.
- Keep every cell inside the grid (`x + width <= cols`, `y + height <= rows`) and non-overlapping; the code only
  clips, it does not reflow.
- Do not rely on `cellColor` at the container level: it is ignored. Set `cellColor` on each item.
- A `frame` other than `"none"` shrinks chart/table cells by 20 px on each side; small cells may then fail the
  child's minimum size and render empty (see `LayoutContainerItem.md`).

## Rules and limits

- Cell geometry: with `showGutter`, column width is `(width - (cols-1)*10) / cols` and a cell spanning `w`
  columns is `w * colWidth + (w-1) * 10` wide; same for rows. Without gutter cells touch.
- Cells are rounded when the theme's shape style is rounded-rect (never when `fullBleed` without a gutter): with
  a gutter every cell gets rounded corners; without gutter only the corners that touch the grid's outer corners
  (computed from `x/y/width/height` vs `cols/rows`).
- `null` entries in `items` are replaced by `{}` (which becomes a placeholder); `null` entries in
  `gridLayout.cells` are skipped, leaving the matching item without a position. Do not write either.
- `fullBleed` + no gutter + exactly one cell: the footer takes the cell's color/image as its background.
- Layout engine presets (`DashboardLayouts`, `StackDiagramLayouts`, `PhotoCollageLayouts`, ...) are only
  editor pickers; any consistent `gridLayout` renders with the `"flex"`/`"dashboard"`/`"stack_diagram"` engines.
- Migration (`_migrate_10_02`, runs only when the stored `migrationVersion` < 10.02): legacy `text` /
  `elementTextBlock` become `TextAndImage` items, `frame: "light"|"dark"` becomes `borderColor`/`borderShadow`,
  a numeric legacy `gridLayout` index is resolved against `PhotoCollageLayouts`, item `cellColor` `"auto"`/missing
  becomes the slide color. Always write `migrationVersion: 10.03` so this does not run on your models.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` | array (required) | one object per grid cell, see `LayoutContainerItem.md` | The cell contents. `items[i]` is placed in `gridLayout.cells[i]`. If there are fewer items than cells, placeholder items are appended; if there are more, the extra items are **deleted** from the model. |
| `gridLayout` | object | default `{ cols: 12, rows: 12, cells: [{ x: 0, y: 0, width: 12, height: 12 }] }` (subclasses override, see below) | The grid and its cells. |
| `gridLayout.cols` / `gridLayout.rows` | number | default 12 / 12 (filled in when missing or not a number) | Number of grid columns / rows. Cell coordinates are in these units. |
| `gridLayout.cells` | array of `{ x, y, width, height }` | default one full-size cell | One rectangle per item, in grid units, `x`/`y` 0-based from the top-left. `width`/`height` below 1 are treated as 1; a cell that starts beyond the grid (`x > cols - 1` or `y > rows - 1`) is not laid out at all; a cell that overflows the grid is clipped to it. Overlaps are not detected. |
| `gridLayout.fitGridLayout` | number | only with `layoutEngineType: "preserve-aspect"` | Index of the preset used by the aspect-preserving engine (PhotoCollage). |
| `layoutEngineType` | string | `"flex"` (default here; `Dashboard` defaults to `"dashboard"`, `StackDiagram` to `"stack_diagram"`), `"fixed"`, `"preserve-aspect"`, `"headline"`, `"dashboard"`, `"sidebar"`, `"bottom_tray"`, `"single_cell"`, `"custom"`, `"stack_diagram"` | Which layout engine positions the cells. All engines except `"preserve-aspect"`, `"fixed"` and `"single_cell"` use the free-form `gridLayout.cells` above; the named ones only differ in the preset list the editor offers. `"custom"` reads the grid size from `customGridCols`/`customGridRows` instead of `gridLayout.cols/rows`. |
| `customGridCols` / `customGridRows` | number | default 12 / 12 | Grid size for `layoutEngineType: "custom"` only. |
| `showGutter` | boolean | default `false` (`Dashboard` always `true`, `StackDiagram` schema `true`) | Puts a 10 px gap between cells (and a 10 px outer gutter when also `fullBleed`). |
| `fullBleed` | boolean | default `false` | Removes the canvas margins so the grid touches the slide edges (bottom margin 50 px is kept when the slide has an inline text block). Ignored when the legacy `aspectRatio` is `"fit"`. |
| `frame` | string | default `"none"` | Frame style name. Any value other than `"none"` adds 20 px padding inside every non-`TextAndImage` cell. Legacy values `"light"` / `"dark"` are migrated to `borderColor` / `borderShadow`. |
| `borderColor` | string | palette color name; default none | Stroke color of the 1 px cell frame. |
| `borderShadow` | boolean | default none | Adds a soft drop shadow (blur 10, opacity 0.2) to every cell. |
| `maskType` | string | default none | Frame/mask type applied to the whole container (`styles.frame.frameType`). Rarely used. |
| `showTitle` | `false` \| `"above"` \| `"below"` | default `false` | Container-level hint only (the editor sets it to `"above"` on multi-cell dashboards). What actually shows titles is `items[].showTitle`. |
| `collectionColor` | string | default `"theme"` | Inherited from `CollectionElement`; used by `"colorful"` / `"collection-…"` / `"<a>-to-<b>"` cell colors to pick per-item colors. |

Not read by this class although present in stored examples and in the app's own generator output: `cellColor` on
the container (per-cell `items[].cellColor` is what counts), `cellFrameType`, `formatOptions`, legacy `cols`/`rows`/
`text`/`elementTextBlock`/`aspectRatio`/`color`/`backgroundColor` (migrated when `migrationVersion` < 10.02).

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `items[]` -> `LayoutContainerItem` (`LayoutContainerItem.md`), one per entry, in array order; item `i` gets
  cell `gridLayout.cells[i]`. Items without an `id` get a generated uuid on first render.
- Item count: `minItemCount` 1, `maxItemCount` 10 (`CollectionElement` default; enforced only by the editor's
  add/paste actions, not by rendering). The real driver is `gridLayout.cells.length`: after every build
  `items.length === gridLayout.cells.length`.
- Default item appended for missing cells: `{ componentType: "GridPlaceholder", childElement: {}, cellColor: <cellColor of the last item> }`
  (`Dashboard` and `StackDiagram` override `defaultItemData`).
