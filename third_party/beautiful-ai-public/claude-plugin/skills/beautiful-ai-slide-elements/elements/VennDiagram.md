# VennDiagram

Overlapping circles ("bubbles") positioned freely by center offset and radius, each with a heading-style label that
can be nudged away from the circle center so it stays readable in the overlaps. The whole arrangement is scaled down
(never up) and centered to fit the element. Root element of the `vennDiagram` template. Items are `VennDiagramItem`,
the label is `VennDiagramLabel` (both documented here, no separate file).

## Model location

- `states[0].primary` – the `VennDiagram` model (root).
- `states[0].primary.items[]` – one `VennDiagramItem` per circle; later items are drawn on top of earlier ones.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Where we win" } ] }
  },
  "primary": {
    "collectionColor": "colorful",
    "items": [
      { "x": 0, "y": -100, "radius": 150, "labelCenterX": 0, "labelCenterY": 0,
        "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Design" } ] } },
      { "x": -100, "y": 100, "radius": 150, "labelCenterX": 0, "labelCenterY": 0,
        "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Speed" } ] } },
      { "x": 100, "y": 100, "radius": 150, "labelCenterX": 0, "labelCenterY": 0,
        "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Price" } ] } }
    ]
  }
}
```

## Pitfalls

- The label field is `text`, not `label`; `label` is a legacy field that is ignored on v10 models.
- Omitting `x`/`y`/`radius` gives each circle a random position and radius (50–150); always set all three.
- `radius` must be a number; strings are coerced, anything non-finite becomes 150.
- Labels are centered on the circle by default: in heavy overlaps they collide; shift them with `labelCenterX/Y` (towards the non-overlapping side) and set `userPositionedLabel: true` so the editor keeps your offsets.
- Keep to 2–4 circles; the element allows 20 but the layout only scales down, so many circles become tiny.

## Rules and limits

- Fit: the bounding box of all circles is scaled by `min(1, width/boxWidth, height/boxHeight)` and centered; coordinates are therefore relative, but keep them in the px range of the presets so the labels (whose font size does not scale with the circles) stay proportionate.
- Presets used by the editor and the app's generator (`radius` 150 unless noted): 2 circles `(-150, 0)`, `(150, 0)` radius 200; 3 circles `(0, -100)`, `(-100, 100)`, `(100, 100)`; 4 circles `(-100, -100)`, `(100, -100)`, `(-100, 100)`, `(100, 100)` radius 140.
- Legacy: items with `label: { "text" }` / `title` (v8/v9 models, `isVersion8Model`) are migrated to `text.blocks` and their positions converted from % to px at first layout; stored examples may still contain an empty `label` field, which is ignored.
- Template flags: `allowColorBackgrounds: false`; `allowColorful`; header and trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–20 objects (2–4 is the practical range) | The circles. |
| `modelVersion` | number | `2` (schema default) | Model version marker; leave at 2. |
| `collectionColor` | string | `"theme"` (default); template defaultData `"colorful"` | Circle colors, per `CollectionElement.md`. |
| `decorationStyle` | string | `"fillAndStroke"` (item default), `"filled"`, `"outlined"`, `"muted"` | Circle style: `"fillAndStroke"` fills and adds a 30%-alpha stroke, `"outlined"` a solid stroke. Items may override it. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (VennDiagramItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `x`, `y` | number | px offsets of the circle center from the diagram origin; default `0`-ish random for new items | Positive `y` is down. Only relative positions matter: the layout is translated to the element center and scaled to fit. |
| `radius` | number | px, default `150`; editor drag range 75–400; non-numeric values are coerced, invalid ones become 150 | Circle radius before fit-scaling. |
| `text` | object | `{ "blocks": [ { "type": "text", "textStyle": "heading", "html": "..." } ] }` | Label (`TextElement.md`, header structure: allowed styles `heading`, `title`, `body`, `bulleted`, `label`; auto width/height, scale-to-fit, synced across circles). |
| `labelCenterX`, `labelCenterY` | number | px, default `0` | Offset of the label center from the circle center (before scaling). The editor's "beautify" recomputes them for circles whose label collides with another circle unless `userPositionedLabel` is set. |
| `userPositionedLabel` | boolean | `false` | `true` keeps your `labelCenterX/Y` when the diagram is beautified. |
| `textWidth` | number | px | Fixed label width (default: the circle diameter). |
| `userWidth` | number | px | Label width set by dragging in the editor; when present it overrides auto width. |
| `textAlign` | string | `"left"` default; `"center"`, `"right"` | Label alignment (alignment is allowed on this text). |
| `color` | string | palette color or `null` | Overrides the collection color for this circle (`"auto"` is migrated to `null`). |
| `hilited` | boolean | `false` | Emphasizes this circle. |
| `decorationStyle` | string | inherits from root | Per-circle style. |

### Nested elements

- `items[]` -> `VennDiagramItem`; min 1, max 20 (`maxItemCount`); z-order = array order (last on top).
  - `circle` -> SVG circle.
  - `text` -> `VennDiagramLabel` (`TextElement.md`) bound to `item.text`, placed at circle center + `labelCenterX/Y`; it stays selectable through the circle.
