# ShapeCallout

`ShapeCallout` is the text-in-a-shape callout: `calloutType` `"box"` (rounded rectangle), `"circle"`, `"diamond"`
or `"capsule"`, filled or outlined in the callout's `color` with centred text inside. It extends
`AuthoringShapeElement` (`AuthoringShapeElement.md`), whose shape geometry, text stack and adjustments it reuses,
and it is also the fallback class for any unknown `calloutType` (drawn as a box). It is the child of an
`AuthoringElementContainer` entry with `type: "callout"` on the flow chart (`flow_chart`, all four kinds), Classic
slides (`authoring`: box, circle), the target/thermometer layers (box, circle) and the XY graph (box). Shared
callout contract: `CalloutElement.md`; what follows is what this class adds or changes relative to
`AuthoringShapeElement.md`.

No stored examples exist; the examples come from the app's flow-chart recipe and the editor defaults (Classic:
box 130×100, circle 130×130; flow chart template default: one empty box at 590,248).

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`flow_chart`, `authoring`, `xygraph`),
`states[0].primary.annotations.elements[]` (`target`, `thermometer`).

## Minimal example

Flow-chart nodes (`states[0].primary.elements[]`) as the app's recipe writes them – a step, a decision and a
start/end capsule:

```json
[
  { "id": "step", "type": "callout", "calloutType": "box", "x": 590, "y": 120, "width": 180, "height": 80,
    "fitToText": true, "decorationStyle": "filled", "color": null,
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Receive order" }] } },
  { "id": "check", "type": "callout", "calloutType": "diamond", "x": 590, "y": 280, "width": 180, "height": 100,
    "fitToText": false, "decorationStyle": "filled",
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "In stock?" }] } },
  { "id": "end", "type": "callout", "calloutType": "capsule", "x": 590, "y": 440, "width": 180, "height": 60,
    "fitToText": true, "color": "accent1",
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Done" }] } }
]
```

A circle: `{ "id": "c1", "type": "callout", "calloutType": "circle", "x": 300, "y": 300, "width": 130,
"height": 130, "color": "theme", "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "A" }] } }`.

## Pitfalls

- Use `calloutType` to pick the shape; `shape` is overwritten and `fill`/`stroke`/`strokeStyle` are ignored –
  color the callout with `color` + `decorationStyle`.
- `fitToText` defaults to `false` when omitted: a long text in a small box is shrunk down to 10 % without any
  warning in exports. The recipe sets `fitToText: true` on boxes and `false` on diamonds (a diamond hugging its
  text looks squashed).
- Give every block a `textStyle`; an omitted style renders as a 30 px heading.
- `x`/`y` are the centre: keep them at least `width / 2` / `height / 2` from the canvas edges or the reference
  point clamp moves the shape.
- `height` is overwritten whenever `fitToText` is on; `textWidth` is never read – size the text with `width` and
  `textInset`.
- A circle whose `width` and `height` differ is squared on build (`height = width`).
- `verticalAlign` does nothing with `fitToText` on.

## Rules and limits

- Geometry from `calloutType`, not from `shape`; `"circle"` additionally sets `height = width` and
  `fitToText = false` at build, keeps its aspect ratio when resized and has no "Fit Height to Text" toggle.
- Layout: `fitToText` -> `height = textHeight + top + bottom inset` (written back); otherwise the text is placed by
  `verticalAlign` and scaled down to fit. Text wider than `width − insets` wraps; a single word wider than that
  widens the drawn shape without changing the stored `width`.
- Minimum 50×20; no maximum. No adjustment handles, no reshape, no stroke picker.
- Colors: `color ?? collectionColor` resolved against the host background (colorful palettes use the entry
  index), then split by `decorationStyle`; an outlined/none style fills the shape with the slide background.
- Connectors: anchors `"anchor-free"`, left, right, top, bottom and `"anchor-bottom-right"` on the shape's bounds;
  centre anchors are trimmed at the real outline (`rect`, `circle`, `diamond`, `capsule`); a connector from a
  node back into itself is collapsed. Default connector color (when the host has none; the flow chart uses
  `"secondary"`): the stroke color for `"outlined"`/`"fillAndStroke"`, else the fill color.
- Editor: Type picker (switching writes `fitToText: calloutType == "box"`), Color picker with decoration styles,
  "Fit Height to Text" (not for circles), "Text Inset"; width/height handles follow the fit flags
  (`AuthoringShapeElement.md`).
- Migrations: 10.02 (`CalloutsCanvas.md`) gives legacy box/capsule/diamond/circle items `width = text width + 40`
  (`height = width`, `fitToText: false` for circles, `fitToText: true` otherwise); the shape's own `_migrate_10`
  converts legacy `blocks`/`blockGap` into `text.blocks` (`AuthoringShapeElement.md`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Authorable fields (the `AuthoringShapeElement` schema is also written into the entry on build – see the second
table for what to leave alone):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"box"`, `"circle"`, `"diamond"`, `"capsule"` (anything else = box) | Chooses the geometry; the class writes the matching `shape` into the model on every build. |
| `x`, `y` (required) | number | px | **Centre** of the shape. |
| `width`, `height` (required) | number | px, min 50×20 (raised in the model) | Size of the shape. `"circle"` forces `height = width` on build. With `fitToText` the height is recomputed and written back. |
| `text` | object | `{ "blocks": [...] }`, `TextElement.md`; allowed `textStyle` `"heading"` (30 px), `"title"` (24 px), `"body"` (20 px), `"label"` (20 px); a block without `textStyle` renders as `"heading"`; the editor creates `"title"` blocks | The text, centred in the shape, inset by `textInset`. Several blocks render stacked; the editor cannot add or remove the last block. Emphasized runs allowed. Per-block `textAlign` is honoured (not synced). |
| `color` | string or null | palette color, default `null` -> `collectionColor` (default `"theme"`) | The shape's color, applied through `decorationStyle`. `null`/`"theme"` adapt to colored slide backgrounds, explicit values do not. |
| `decorationStyle` | string | `"filled"` (color fill, no stroke), `"outlined"` (stroke in color, fill = slide background), `"muted"` (30 % fill), `"fillAndStroke"` (30 % fill + stroke), `"none"`; default: theme element style | How `color` is painted. Stroke width comes from the theme. |
| `fitToText` | boolean | default `false` (schema); the editor writes `true` for new boxes and `calloutType == "box"` on type change; forced `false` for `"circle"` | `true`: height = text height + 2×`textInset`, written back on every render (the width stays as authored). `false`: the shape keeps its size and the text is scaled down (to 10 %) to fit. |
| `fitWidthToText` | boolean | default `false`; no editor control on callouts | `true`: the width follows the text too (anchored on the alignment side). |
| `textInset` | number | px, default `20` (schema and theme) | Padding between the shape edge and the text; editor "Text Inset" stepper. |
| `textAlign` | string | `"left"`, `"center"` (default), `"right"`, `"justify"` | Horizontal alignment of the text. |
| `verticalAlign` | string | `"top"`, `"middle"` (default), `"bottom"` | Vertical placement inside a fixed-height shape; ignored with `fitToText`. |
| `textWidth` | number | px | Written by the editor's resize (100–1280) but not read by the shape layout; the text wraps in `width − 2×textInset`. |
| `textPadding` | object | `{ left, right, top, bottom }` px | PowerPoint-import per-side padding; when present replaces `textInset`. |

Written by the app, do not author:

| Field | Written as | Note |
|---|---|---|
| `shape` | `"rect"` / `"circle"` / `"diamond"` / `"capsule"` from `calloutType` | Overwritten on every build; authoring another value has no lasting effect. |
| `adj1` | the theme's shape corner radius | Overwritten when styles load; the box corner radius is theme-driven. |
| `fill`, `stroke`, `strokeWidth`, `strokeStyle` | schema defaults (`"background_accent"`, `null`, `1`, `"solid"`) | **Not used to draw** the callout: fill/stroke come from `color` + `decorationStyle`, the stroke width from the theme, and `strokeStyle` is ignored. `strokeWidth > 0` only decides that outlined callouts hand their stroke color to connectors. |
| `canReshape`, `direction`, `opacity`, `titleTextStyle` | `true`, `"right"`, `100`, `"title"` | Editor/legacy flags; the shape picker is disabled (`canReshape` is reported as `false` regardless), `direction` is meaningless for these shapes, `titleTextStyle` is only used by the legacy text migration. |

Plus the container fields (`AuthoringElementContainer.md`).

### Nested elements

- `text` -> `TextElement` (`TextElement.md`), built only when `text.blocks` is non-empty: header block structure,
  allowed styles above, no block adding, last block not deletable, scaled to fit, no font size control (sizes are
  synced across the callouts of the canvas), advanced styles menu only on Classic slides, the shape as the text's
  background for contrast.
- The shape is an inline SVG (`rect` with the theme corner radius, `circle`, or a diamond/capsule path); no child
  element.
