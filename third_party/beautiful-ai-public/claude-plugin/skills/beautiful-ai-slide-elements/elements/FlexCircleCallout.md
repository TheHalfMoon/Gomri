# FlexCircleCallout

`FlexCircleCallout` is the `calloutType: "flex-circle"` callout: a circle of `markerSize` px whose text sits
**inside the circle when it fits** and otherwise beside it like a marker callout. It extends `MarkerCallout`
(`MarkerCallout.md`) and is the child of an `AuthoringElementContainer` entry with `type: "callout"`. Hosts: the
XY graph (`xygraph`, where it is the default marker and `data[]` drives it, see `XYGraph.md`) and Classic slides
(`authoring`); the flow chart and the target/thermometer layers do not offer it (the container still renders it).
Shared contract: `CalloutElement.md`.

No stored examples exist; examples come from the schema (`markerSize: 100`, `textDirection: "auto"`) and the
editor's default model (`width: 130`, `height: 130`, `color: "theme"`).

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`xygraph`, `authoring`).

## Minimal example

`states[0].primary.elements[]` entry on a Classic slide: a 120 px bubble with its label inside.

```json
{
  "id": "b1", "type": "callout", "calloutType": "flex-circle",
  "x": 500, "y": 300, "markerSize": 120, "textDirection": "auto", "color": "accent1",
  "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "42%" }] }
}
```

With a long label the same entry renders the text to the right of the circle; add `"textDirection": "bottom"` to
force it below.

## Pitfalls

- Whether the text ends up inside or outside depends on the text length versus `markerSize / √2` at the theme's
  font size: a label that fits on one theme may pop outside on another. Use short labels or a large
  `markerSize` when the text must stay inside.
- Inside text is never shrunk; outside text is laid out at `textWidth` – set `textWidth` when you force a
  direction.
- `width`/`height` are rewritten: size the bubble with `markerSize` only.
- `decorationStyle` has no effect; the bubble is always a filled circle.
- On the XY graph do not author `x`/`y`/`markerSize`/`color`/label on the entry: `data[]` overwrites them.

## Rules and limits

- Fit test (`"auto"` only): the text is laid out in the largest square inside the circle (side =
  `markerSize / √2`), centred, without scaling. If every block fits, the callout is exactly the circle and
  `width = height = markerSize` is written; otherwise the normal marker layout applies (text outside).
- Fits its contents in both directions; the theme adds a 10 px margin around the box.
- Editor: no resize handles while the text is inside; left/right handles (changing `textWidth`) when outside.
  "Bubble Size" writes `markerSize`; "Text Position" writes `textDirection`.
- Connectors attach to the circle (anchor bounds = circle, line trimmed at the circle edge); default connector
  color = `color ?? collectionColor`.
- Animation: "Grow in" (the circle grows from 0, the text fades in).
- XY graph: `x`, `y`, `markerSize`, `color` and the first block's `html` are overwritten from the matching `data[]`
  row on every layout; author only `calloutType`/`textDirection` there (`XYGraph.md`).
- Migration 10.02 (`CalloutsCanvas.md`): legacy flex circles get `width = text width + 40`, `fitToText: true`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"flex-circle"` | – |
| `x`, `y` (required) | number | px | Centre of the circle. |
| `markerSize` | number | px, default `100` (schema); clamped 10–400 at layout; editor "Bubble Size" slider 10–400 | Diameter of the circle. |
| `textDirection` | string | `"auto"` (schema default), `"right"`, `"left"`, `"top"`, `"bottom"`; an explicit `null` behaves as `"right"` | `"auto"`: text inside the circle if it fits, else outside on the side away from the first connector (`MarkerCallout.md` rule, `"right"` when unconnected). Explicit values always put the text outside on that side. |
| `text` | object | `{ "blocks": [...] }`, `TextElement.md`; default style `"title"` | The label. Inside the circle it is centred and **not** scaled down; outside it is laid out at `textWidth`. |
| `textWidth` | number | px, default `200` | Width of the text column when the text is outside. |
| `color` | string or null | palette color, default `null` -> `collectionColor` | Circle fill. Text inside the circle takes its contrast from this color. |
| `width`, `height` | number | px, written on every render | `= markerSize` when the text is inside; marker + 15 + `textWidth` (or stacked) when outside. Minimum width 10. |
| `fitToText`, `textAlign`, `decorationStyle` | – | – | Ignored (`decorationStyle` is not applied to the circle: it is always filled). |

Plus the container fields (`AuthoringElementContainer.md`).

### Nested elements

- `marker` -> `SVGCircleElement` (no model): the circle, filled with `color`.
- `text` -> `TextElement` (`TextElement.md`): header structure, default `"title"`, no block adding, font size synced
  with siblings, not selectable by a single click (double click edits).
