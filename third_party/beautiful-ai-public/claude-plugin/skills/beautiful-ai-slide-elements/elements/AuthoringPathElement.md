# AuthoringPathElement

`AuthoringPathElement` draws a free polyline – a straight line, a multi-segment line or a closed polygon – with
optional arrow/circle end caps. It is the child of an `AuthoringElementContainer` with `type: "path"` (see
`AuthoringElementContainer.md`) on Classic slides (`authoring` template). It has no text and no fill by default; for
connectors between callouts use the `connections` of `CalloutsCanvas.md` instead.

No stored example of the `authoring` template is available; the examples below are the editor's default model.

## Model location

- `states[0].primary.elements[]` – the entry itself (shared with the container) for `type: "path"`; `x`, `y`,
  `width`, `height`, `rotation`, `opacity`, `shadow`, … are the container fields.
- `states[0].primary.elements[].element` – only when the entry has an `element` sub-object.

## Minimal example

The editor's default diagonal line (container + path fields on one object):

```json
{
  "id": "p1", "type": "path", "x": 200, "y": 200, "width": 130, "height": 130,
  "points": [{ "x": 0, "y": 0 }, { "x": 130, "y": 130 }]
}
```

A horizontal theme-colored arrow and a filled triangle:

```json
{
  "id": "p2", "type": "path", "x": 300, "y": 400, "width": 400, "height": 0,
  "points": [{ "x": 0, "y": 0 }, { "x": 400, "y": 0 }],
  "stroke": "theme", "strokeWidth": 4, "endDecoration": "arrow"
}
```

```json
{
  "id": "p3", "type": "path", "x": 800, "y": 300, "width": 200, "height": 160,
  "points": [{ "x": 100, "y": 0 }, { "x": 200, "y": 160 }, { "x": 0, "y": 160 }, { "x": 100, "y": 0 }],
  "stroke": "none", "fill": "accent2"
}
```

## Pitfalls

- `points` are relative to the container, not slide coordinates: a line from (300, 400) to (700, 400) is `x: 300,
  y: 400` with points `(0,0)` and `(400,0)`.
- A perfectly horizontal or vertical line has `height: 0` / `width: 0`; it renders fine but cannot be resized in the
  editor later – give it a small non-zero size if that matters.
- Forgetting to repeat the first point leaves a polygon visually open when `fill` is `"none"` (the fill itself is
  drawn either way).
- `stroke: "none"` with `fill: "none"` renders nothing; `strokeWidth: 0` also removes the arrow heads.
- Decorations other than `"arrow"`/`"circle"` are silently ignored.

## Rules and limits

- `width`/`height` should enclose the points: the SVG is `width`×`height` with visible overflow, so points outside
  still draw, but selection, snapping and rotation use the box. Resizing in the editor scales every point by
  `newWidth / oldWidth` and `newHeight / oldHeight`, so a box with a zero dimension cannot be resized afterwards
  (division by zero).
- Caps are shortened on short paths: with caps at both ends each may use at most a quarter of the path length, with
  one cap at most half; the line is trimmed by the cap length so the tip sits on the point.
- `strokeWidth: "bold"` (a string, inherited from connector models) switches to the connector preset (30 px stroke,
  fixed cap sizes). Use numbers.
- Hit testing uses a 10 px stroke and, for closed paths or a non-`"none"` fill, the filled area.
- Colors resolve through the theme palette like shape colors (`AuthoringShapeElement.md`). Decoration styles are not
  used.
- Animation: "Grow in" (the line is drawn from the first point; the start cap appears immediately, the end cap when
  complete). The container does not add a "Fade in" for paths.
- No migrations of its own.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Schema defaults are written into the model on build.

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `points` (required) | array of `{ "x", "y", "id"? }` | default two points at `0,0` (a zero-length line) | Vertices in px **relative to the container's `x`/`y`**, in drawing order. Missing `id`s are generated. Two points = a straight line; more = a polyline; repeat the first point last to close a polygon. |
| `stroke` | string | default `"black"`; palette name (`"theme"`, `"accent1"`, `"primary"`, …), CSS color, or `"none"` | Line color. Also the color of the end caps. |
| `strokeWidth` | number | px, default `2` | Line width. `0` (or no stroke color) hides the line and the end caps. |
| `strokeStyle` | string | `"solid"` (default), `"dashed"`, `"dotted"` | Dash pattern (6×/4× the width, or 1×/max(width, 4)). End caps are always solid. |
| `fill` | string | default `"none"`; palette name or CSS color | Fill of the area enclosed by the points (SVG closes the path implicitly for filling). Keep `"none"` for lines. |
| `startDecoration`, `endDecoration` | string | `"arrow"`, `"circle"`; anything else = none | Cap at the first / last point. |
| `arrowHeads` | object | `{ "offset": px (default 0), "arrowLength": px (default 10) }` | Arrow head geometry: length and width are `arrowLength + 2 × strokeWidth`; `offset` moves the tip along the line. Circle caps have radius `2 + strokeWidth`. |

Container fields (`x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, `isLocked`, `isHidden`, `groupIds`,
`name`) are in `AuthoringElementContainer.md`; plus the common fields, see `BaseElement.md`.

### Nested elements

None – the path, its caps and the SVG wrapper are rendered inline. The container exposes the path as the selection
target (double-click to select).
