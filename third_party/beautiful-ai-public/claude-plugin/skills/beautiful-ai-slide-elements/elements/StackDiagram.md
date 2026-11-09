# StackDiagram

`StackDiagram` is a `GridLayoutContainer` whose cells are stacked, colored text boxes: layers, pillars, a header
bar spanning the top, a base spanning the bottom. It is the root element (`states[0].primary`) of the
`stackDiagram` template. Every cell is a `LayoutContainerItem` with `componentType: "TextAndImage"` (text and/or
an image or icon) on a colored background; the grid is a free-form 12 x 12 layout, so any "architecture diagram"
arrangement of rectangles is possible. The grid machinery is documented in `GridLayoutContainer.md`, the cells in
`LayoutContainerItem.md` and the cell content in `TextAndImage.md`.

## Model location

- `states[0].primary` for `template_id: "stackDiagram"`.
- Cells: `states[0].primary.items[]`; cell text/image: `states[0].primary.items[].childElement`.

## Minimal example

Header bar, three pillars, footer bar (the app's own "pillar slide" recipe):

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Platform architecture" } ] } },
  "primary": {
    "showGutter": true,
    "fullBleed": false,
    "gridLayout": {
      "cols": 12, "rows": 12,
      "cells": [
        { "x": 0, "y": 0, "width": 12, "height": 2 },
        { "x": 0, "y": 2, "width": 4, "height": 8 },
        { "x": 4, "y": 2, "width": 4, "height": 8 },
        { "x": 8, "y": 2, "width": 4, "height": 8 },
        { "x": 0, "y": 10, "width": 12, "height": 2 }
      ]
    },
    "items": [
      { "componentType": "TextAndImage", "cellColor": "theme",
        "childElement": { "backdropPadding": 10, "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Applications" } ] } } },
      { "componentType": "TextAndImage", "cellColor": "colorful",
        "childElement": { "backdropPadding": 10, "textPosition": "top", "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Web" },
          { "type": "text", "textStyle": "body", "html": "React front end" } ] } } },
      { "componentType": "TextAndImage", "cellColor": "colorful",
        "childElement": { "backdropPadding": 10, "textPosition": "top", "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Mobile" },
          { "type": "text", "textStyle": "body", "html": "iOS and Android" } ] } } },
      { "componentType": "TextAndImage", "cellColor": "colorful",
        "childElement": { "backdropPadding": 10, "textPosition": "top", "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "API" },
          { "type": "text", "textStyle": "body", "html": "Public GraphQL" } ] } } },
      { "componentType": "TextAndImage", "cellColor": "theme",
        "childElement": { "backdropPadding": 10, "text": { "blocks": [ { "type": "text", "textStyle": "caption", "html": "Shared infrastructure" } ] } } }
    ]
  }
}
```

## Pitfalls

- Each box needs `componentType: "TextAndImage"`; an item without `componentType` (the legacy `{ text, x, y,
  width, height }` shape) renders as an empty placeholder cell.
- `items.length` must equal `gridLayout.cells.length`; a header/footer bar is just a wide cell, not a separate
  field.
- Thin bars (`height: 1` of 12 with a gutter) are about 40 px tall: use a single `caption`/`title` block and
  small `backdropPadding`, or the text will not fit.
- Text boxes do not reserve space for images automatically; a `content_value` icon with `textPosition: "top"`
  needs a tall cell.
- `cellColor` is per item; `"colorful"` only varies when the items are siblings in the same container (it uses
  the item index).

## Rules and limits

- Everything in `GridLayoutContainer.md` applies: items are padded/truncated to the cell count, cells are matched
  by index, cells outside the grid are not laid out.
- Boxes are filled (`decorationStyle: "filled"`) with their `cellColor`; `"colorful"` / `"collection-…"` /
  `"theme-to-light"` colors rotate per item index, `"none"` gives a transparent box (text only).
- The whole diagram fades in as one unit (child animations are disabled by default).
- Migration `_migrate_10_02` (stored `migrationVersion` < 10.02): legacy items with `x/y/width/height` on the item
  and `cols`/`rows` on `primary` are converted into `gridLayout` + `TextAndImage` items (`color: "transparent"`
  becomes a placeholder cell). Do not write that legacy shape.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Same as `GridLayoutContainer.md`, with these differences:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` | array (required) | each `{ "componentType": "TextAndImage", "cellColor": …, "childElement": { "text": … } }` | Cells. Auto-added cells default to `{ componentType: "TextAndImage", childElement: {} }` (empty text box), so the template's empty `defaultData: { primary: {} }` renders 6 empty boxes. |
| `gridLayout` | object | default = first preset: `cols 12, rows 12`, cells `0,0,12,4 / 0,4,6,4 / 6,4,6,4 / 0,8,4,4 / 4,8,4,4 / 8,8,4,4` (1 + 2 + 3 pyramid) | Free-form 12 x 12 layout; each cell is one box. |
| `layoutEngineType` | string | default `"stack_diagram"`; `"custom"` (with `customGridCols`/`customGridRows`) in a third of the stored examples | Keep the default. |
| `showGutter` | boolean | schema default `true` (written) | 10 px gaps between boxes; `false` makes them touch. |
| `fullBleed` | boolean | default `false` | Boxes run to the slide edges. |
| `borderColor` / `borderShadow` | string / boolean | default none | Box frame color / drop shadow. |
| `cellColor` | – | present on `primary` in examples | Not read; set `cellColor` per item. |

Template flags: `allowColorBackgrounds: true`, `allowColorful: false`, header allowed.

Editor presets (`x,y,w,h` per cell): pyramid `0,0,12,4 / 0,4,6,4 / 6,4,6,4 / 0,8,4,4 / 4,8,4,4 / 8,8,4,4`;
header + 4 pillars + base `0,0,12,3 / 0,3,3,6 / 3,3,3,6 / 6,3,3,6 / 9,3,3,6 / 0,9,12,3`; an 8-cell mixed layout;
and a 2 x 2 grid `0,0,6,6 / 0,6,6,6 / 6,0,6,6 / 6,6,6,6`. Real slides mostly use custom layouts such as
`0,0,12,2 / 0,2,4,8 / 4,2,4,8 / 8,2,4,8 / 0,10,12,2` (header, three pillars, footer).

### Nested elements

- `items[]` -> `LayoutContainerItem` (`LayoutContainerItem.md`) with `componentType: "TextAndImage"` ->
  `TextAndImage` (`TextAndImage.md`): `childElement.text.blocks` (title/body/bullets), optional
  `content_type`/`content_value` (icon, image), `backdropPadding` (10-30 px in examples), `textAlign`,
  `verticalAlign`, `textPosition`, `boxHAlign`.
- A cell can also hold any other `componentType` (chart, statistic, ...) but the template is meant for text boxes.
- Item count: 1 to 10 (editor cap); presets use 4-8; one item per `gridLayout.cells` entry.
