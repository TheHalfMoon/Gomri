# TextCallout

`TextCallout` is the `calloutType: "text"` callout: a plain block of text with no marker and no shape, placed
anywhere on a callout canvas and connectable with connectors. It extends `CalloutElement` (`CalloutElement.md`)
and is the child of an `AuthoringElementContainer` entry with `type: "callout"` on every callout host (flow chart,
Classic, target, thermometer, XY graph, timeline2).

No stored examples exist; the examples are built from the editor's default model (`width: 130`, `height: 150`,
`fitToText: true`) and the layout code.

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`flow_chart`, `authoring`, `xygraph`),
`states[0].primary.annotations.elements[]` (`target`, `thermometer`), `states[0].primary.milestones.elements[]`
(`timeline2`).

## Minimal example

`states[0].primary.elements[]` entry: a two-line caption centred at (640, 520).

```json
{
  "id": "t1", "type": "callout", "calloutType": "text",
  "x": 640, "y": 520, "width": 320, "textAlign": "center",
  "text": { "blocks": [
    { "type": "text", "textStyle": "title", "html": "Peak season" },
    { "type": "text", "textStyle": "body", "html": "Orders double between November and January" }
  ] }
}
```

## Pitfalls

- `x`/`y` are the centre of the box; a 320 px wide callout at `x: 100` sticks out of the canvas on the left.
- Size the text with `width`, not `textWidth` (ignored) or `height` (overwritten).
- `color` does not color the text: there is no per-callout text color; use block-level emphasis or the theme.
- Long text in a narrow `width` wraps and grows the box downward; it is only scaled down when it would exceed the
  slide height.
- `textDirection` has no effect on text callouts.

## Rules and limits

- Height fits the text (`fitToContents.height`); `width` is authored and only changed by the editor's left/right
  resize handles. Minimum 40×20 (raised in the model).
- The box centre is clamped into the canvas on `CalloutsCanvas` hosts (`CalloutsCanvas.md`).
- Connectors attach to the box: side anchors on its edges, centre anchors trimmed at the rectangle. On the
  `timeline2` template a text milestone's connector starts at the left anchor.
- Default connector color `"secondary"` (see `color`); the flow chart forces `"secondary"` for all connectors.
- Editor: no color picker and no text-direction control (unless the host enables color); the text toolbar offers
  the block style, alignment and emphasis.
- Migration 10.02 (`CalloutsCanvas.md`): legacy text annotations get `width = text width + 20`, `fitToText: true`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"text"` | – |
| `x`, `y` (required) | number | px | **Centre** of the text box (including its 10 px theme padding). |
| `width` | number | px, min 40; editor default 130 | Width of the box; the text wraps in `width − 20` (10 px padding each side). Author it. |
| `height` | number | px, **written on every render** | Text height + 20. Treat as cache. |
| `text` | object | `{ "blocks": [...] }`, `TextElement.md`; default style `"title"` (24 px); allowed `"heading"`, `"title"`, `"body"`, `"label"` | The text. Several blocks render stacked. |
| `textAlign` | string | `"left"`, `"center"` (default), `"right"` (`"justify"` exists in the enum, not verified here) | Horizontal alignment of the text inside the box; the editor's alignment buttons write it. |
| `textWidth` | number | px | Written by the editor's resize (kept between 100 and 1280) but **not read** by this class's layout – `width` is what sizes the text. |
| `color` | string or null | palette color | Not used to draw the text (text color comes from the theme's primary text color). Only hosts that enable the color picker for text callouts (the thermometer layer) use it as the default connector color; elsewhere connectors default to `"secondary"`. |
| `fitToText`, `textDirection`, `decorationStyle`, `markerSize` | – | – | Written by the editor / other kinds; ignored here (the height always fits the text). |

Plus the container fields (`AuthoringElementContainer.md`): `rotation`, `opacity`, `shadow`, `isHidden`, … apply to
the text box.

### Nested elements

- `text` -> `TextElement` (`TextElement.md`) bound to `text`: header block structure, default `"title"`, alignment
  allowed, no block adding, scaled down only if the text would exceed the slide height, font size synced with the
  sibling callouts, not selectable by a single click (double click edits), 20 px blocks with 24 px titles from the
  theme.
