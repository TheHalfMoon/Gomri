# XYGraph

A scatter / bubble plot: labelled markers positioned by relative x/y coordinates inside a plot box with optional axes
(left-bottom or centered), axis labels, arrow heads, grid and quadrant lines with quadrant labels. The markers are
callouts in an embedded callouts canvas whose position, size, color and label are driven by a `data[]` table. Root
element of the `xygraph` template ("XY Plot"). Nested classes documented here: `XYGraphCanvas` (the marker layer, a
`CalloutsCanvas.md`), `XYGraphAxisLabel` (axis label text) and `GridComponent` (the grid lines).

## Model location

- `states[0].primary` – the `XYGraph` model (root). The marker layer (`XYGraphCanvas`) shares this same model: its callouts are `primary.elements[]`.
- `states[0].primary.data[]` – one row per marker (the authored table).
- `states[0].primary.elements[]` – one callout element per row (`dataId` links them), see `CalloutsCanvas.md`.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Industry analysis" } ] }
  },
  "primary": {
    "collectionColor": "colorful",
    "showAxis": true,
    "axisPosition": "left",
    "showAxisLabels": true,
    "showArrowHeads": true,
    "showGrid": true,
    "gridSize": 34,
    "showQuadrants": true,
    "showQuadrantLabels": true,
    "xAxisLabel": "Completeness of vision",
    "yAxisLabel": "Ability to execute",
    "label1": "Challengers",
    "label2": "Leaders",
    "label3": "Niche players",
    "label4": "Visionaries",
    "data": [
      { "id": "a1", "label": "Acme", "x": 0.2, "y": 0.75, "size": 60, "color": null },
      { "id": "a2", "label": "Globex", "x": 0.55, "y": 0.4, "size": 90, "color": null },
      { "id": "a3", "label": "Initech", "x": 0.8, "y": 0.2, "size": 120, "color": null }
    ],
    "elements": [
      { "dataId": "a1", "type": "callout", "calloutType": "flex-circle" },
      { "dataId": "a2", "type": "callout", "calloutType": "flex-circle" },
      { "dataId": "a3", "type": "callout", "calloutType": "content-and-text", "content_type": "icon", "content_value": "rocket", "frameType": "circle", "textDirection": "bottom" }
    ]
  }
}
```

`elements` may be omitted entirely for plain circle markers.

## Pitfalls

- `y` is measured from the top: `y: 0.1` is a high value, `y: 0.9` a low one. Invert your numbers.
- Every `data` row needs a unique `id`; `elements[].dataId` must match one, otherwise the callout is removed (and a row without an id cannot be linked).
- Do not put the marker text in `elements[].text` only: it is overwritten by `data[].label` at the next layout. Put it in `data[].label`.
- `calloutType`, `textDirection` and icons must go on `elements[]`, not on `data[]` (those keys in `data` are ignored).
- Quadrant labels only show with both `showQuadrants` and `showQuadrantLabels`; axis labels and arrow heads only with `showAxis`.
- A large `size` (200+) with many markers crowds the plot: the canvas keeps markers inside the plot box but does not avoid overlaps.

## Rules and limits

- Max 100 markers.
- `data` is the source of truth: on each layout every callout gets `x = data.x * plotWidth`, `y = data.y * plotHeight`, `markerSize = size`, `color`, and its first text block html = `label`. Edits made to callouts in the editor are written back into `data`.
- Duplicate `dataId`s in `elements` are repaired by cloning the data row; rows without a callout get a `flex-circle` callout; callouts without a row are deleted.
- Axis labels reserve 20px on the labelled sides; with `showGrid` the plot box is additionally trimmed to whole major grid cells.
- Legacy: models with `items[]` (markers with `nodeType: "circle"`, `size`, relative `x`/`y`, `text`) are migrated: `nodeType` becomes `calloutType: "flex-circle"`, `size` becomes `markerSize`, `items` become `elements`, and `data` is derived at the first layout.
- Template flags: `allowColorBackgrounds: false`, `allowCallouts: true`, `allowColorful`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `data` (required) | array | up to 100 rows | The markers. Built from `elements` at first layout when absent (legacy). |
| `elements` | array | one callout per data row; created automatically (`calloutType: "flex-circle"`) for rows without one, orphans removed | Callout models of the markers (`CalloutsCanvas.md`). Position, size, color and label text are overwritten from `data` on every layout; author them only to choose `calloutType` / icon / style. |
| `showAxis` | boolean | defaultData `true` | Draw the x and y axis lines. |
| `axisPosition` | string | `"left"` (defaultData), `"center"` | `"left"`: axes along the left and bottom edges. `"center"`: axes cross in the middle (adds `xAxisLabelEnd`/`yAxisLabelEnd` and arrow heads on both ends). |
| `showAxisLabels` | boolean | defaultData `true` | Draw `xAxisLabel`/`yAxisLabel` (and the `...End` labels when centered). Only with `showAxis`. |
| `showArrowHeads` | boolean | defaultData `true` | Arrow heads at the axis ends. Only with `showAxis`. |
| `showGrid` | boolean | defaultData `true` | Draw the grid (`GridComponent`): major lines every 4 cells, no minor lines; the plot box is shrunk to a whole number of major cells. |
| `gridSize` | number | defaultData `34`; editor 16–50 step 2 | Grid density: cell size in px = 300 / `gridSize` (larger value = finer grid). |
| `showQuadrants` | boolean | defaultData `false` | Draw a vertical and a horizontal rule through the plot center. |
| `showQuadrantLabels` | boolean | defaultData `false` | Draw `label1`..`label4` in the quadrants. Only with `showQuadrants`. |
| `xAxisLabel`, `yAxisLabel` | string or `{ blocks }` | defaultData `"Completeness of Vision"`, `"Ability to Execute"` | Axis captions (`XYGraphAxisLabel`, a one-line centered `TextElement.md`); a plain string is accepted and converted to a block at load. |
| `xAxisLabelEnd`, `yAxisLabelEnd` | string or `{ blocks }` | `""` | Captions at the right/top ends; only with `axisPosition: "center"`. |
| `label1`, `label2`, `label3`, `label4` | string or `{ blocks }` | defaultData `"Challengers"`, `"Leaders"`, `"Niche Players"`, `"Visionaries"` | Quadrant labels: 1 top-left, 2 top-right, 3 bottom-left, 4 bottom-right. |
| `collectionColor` | string | `"theme"` (default); defaultData `"colorful"` | Marker colors (the marker layer's collection color), per `CollectionElement.md`. |
| `decorationStyle` | string | theme default | Marker style for the callouts. |
| `snapToGrid`, `connections` | – | written by the canvas | Not used (connectors are disabled on this canvas). |

Plus the common fields, see `BaseElement.md`.

#### data[] model

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` (required) | string | unique | Row key; `elements[].dataId` references it. |
| `label` | string | plain text; `"Bubble #n"` fallback | Marker text; copied into the callout's first text block. |
| `x` | number | 0–1 | Horizontal position in the plot box, 0 = left. |
| `y` | number | 0–1 | Vertical position, 0 = top, 1 = bottom (invert "higher is better" values: `y = 1 - value/100`). |
| `size` | number | px; defaultData 50/150/200, the app's generator uses 20; pasted data is clamped 10–400 | Marker diameter (`markerSize` of the callout). |
| `color` | string | palette color or `null` | Marker color override. |
| `calloutType`, `type`, `textDirection` | – | seen in defaultData / stored rows | Not read from `data`; set them on the matching `elements[]` entry instead. |

#### elements[] model (markers, see `CalloutsCanvas.md`)

`{ "dataId", "type": "callout", "calloutType", ... }` with `calloutType` one of `"flex-circle"` (default), `"box"`, `"text"`,
`"bullet-text"`, `"numbered-text"`, `"content-and-text"`, `"content"`. For icon markers add `content_type`/`content_value`
(`ContentElement.md`), `frameType` (e.g. `"circle"`/`"theme"`), `textDirection` (`"auto"`, `"bottom"`, ...), `decorationStyle`
(`"filled"`, `"muted"`). `x`, `y`, `markerSize`, `color` and `text.blocks[0].html` are managed from `data`.

### Nested elements

- `graphCanvas` -> `XYGraphCanvas` (`CalloutsCanvas.md` restricted to the plot box, no connectors, no layering, max 100 items, font sizes synced). Its `elements[]` are the markers.
- `grid` -> `GridComponent` (when `showGrid`): SVG grid lines, major every 4 cells.
- `xAxis`, `yAxis` -> SVG polylines; `xAxisArrowHeadRight`, `yAxisArrowHeadTop` (+ `...Left`/`...Bottom` when centered) -> SVG polygons.
- `xAxisLabel`, `yAxisLabel`, `xAxisLabelEnd`, `yAxisLabelEnd` -> `XYGraphAxisLabel` (`TextElement.md`, single line, centered, y labels rotated ±90°).
- `hRule`, `vRule` -> SVG polylines; `label1`..`label4` -> `TextElement.md` (when quadrants + labels).
