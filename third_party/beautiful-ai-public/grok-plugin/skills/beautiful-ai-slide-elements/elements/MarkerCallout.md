# MarkerCallout

`MarkerCallout` is the "marker and text" callout: a marker (a dot, a numbered or lettered circle, an icon/image)
with a text block beside, above or below it. It is the base of `BulletCallout` (`calloutType: "bullet-text"`),
`NumberedCallout` (`"numbered-text"`), `LetteredCallout` (`"lettered-text"`), `TimelineTextCallout`
(`"timeline-text"`) – all four folded into this doc – and of `MediaAndTextCallout` (`"content-and-text"`,
`MediaAndTextCallout.md`) and `FlexCircleCallout` (`"flex-circle"`, `FlexCircleCallout.md`). It is the child of an
`AuthoringElementContainer` entry with `type: "callout"` on a callout canvas (`CalloutsCanvas.md`,
`AuthoringCanvas.md`); the shared callout contract is in `CalloutElement.md`.

No stored examples exist; the examples are built from the code defaults (the editor's default model for a new
marker callout is `{ width: 200, height: 150, color: "theme", textDirection: "auto", fitToText: true }`).

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`flow_chart`, `authoring`, `xygraph`),
`states[0].primary.annotations.elements[]` (`target`, `thermometer`), `states[0].primary.milestones.elements[]`
(hidden `timeline2`). See `CalloutElement.md`.

## Minimal example

A bullet and a numbered callout (`states[0].primary.elements[]`), both laid out automatically:

```json
[
  { "id": "a1", "type": "callout", "calloutType": "bullet-text", "x": 420, "y": 180,
    "textWidth": 220, "textDirection": "right", "color": null,
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Kick-off" },
                         { "type": "text", "textStyle": "body", "html": "Scope agreed with the client" }] } },
  { "id": "a2", "type": "callout", "calloutType": "numbered-text", "x": 420, "y": 320,
    "textWidth": 220, "textDirection": "auto", "color": "accent2",
    "value": { "blocks": [{ "type": "text", "html": "2" }] },
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Build" }] } }
]
```

## Pitfalls

- `x`/`y` are the marker centre; with `textDirection: "right"` the text runs from `x + 7 + 15` to
  `x + 22 + textWidth` – keep that inside the canvas.
- A hand-written `width`/`height` is overwritten; size the text with `textWidth`.
- Numbered/lettered defaults count **all** entries of the canvas: a numbered callout stored after two boxes shows
  "3". Always write `value` yourself when the numbering matters.
- `value` is never regenerated: reordering entries does not renumber them.
- `"auto"` direction depends on the first connector in the connector list; with several connectors on one node
  set the direction explicitly.
- `textAlign` and `markerSize` have no effect on these kinds; `decorationStyle` cannot change their filled
  marker.
- `"lettered-text"` and `"timeline-text"` are not offered by the flow chart/Classic editors: the user cannot switch
  back to them once the type is changed.

## Rules and limits

- Always fits its contents: `width` and `height` are recomputed and written back on every render; `fitToText` is
  ignored. Minimum width 150 (raised in the model), minimum text width 150 in the editor.
- The marker centre is clamped into the canvas on `CalloutsCanvas` hosts (text may extend outside).
- Connectors attach to the **marker** (anchor bounds = marker bounds; the line is trimmed at the marker circle
  when the anchor is the centre); default connector color = the marker color (unless the host sets its own, e.g.
  the flow chart's `"secondary"`).
- `color` resolution: `color ?? collectionColor`; colorful palettes use the entry index.
- Font sizes are synced across all callouts of the canvas (`text.blockFontScales` copied from the first sibling
  when missing).
- Migration 10.02 (`CalloutsCanvas.md`): legacy items become `width = text width + 34` with `fitToText: true`;
  10.03: on `collage` slides a marker callout without `color` on a light/dark/accent background gets `"primary"`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"bullet-text"`, `"numbered-text"`, `"lettered-text"`, `"timeline-text"` (this doc); `"content-and-text"`, `"flex-circle"` (own docs) | Picks the marker kind. |
| `x`, `y` (required) | number | px | **Centre of the marker.** The text hangs off it on the `textDirection` side; the box is laid out so that the marker centre lands on `x`/`y`. |
| `text` | object | `{ "blocks": [...] }`, `TextElement.md`; default style `"title"`; allowed `"heading"`, `"title"`, `"body"`, `"label"` | The text. Several blocks render stacked; the marker is centred on the first line of the first block. |
| `textWidth` | number | px, default `200`; editor clamps 150–1280 | Width of the text column. The text wraps to it and is scaled down if it still does not fit the slide height. |
| `textDirection` | string | `"auto"` (default), `"right"`, `"left"`, `"top"`, `"bottom"` | Side of the marker the text sits on. `"auto"` = away from the first connector, `"right"` when unconnected (rule below). Hosts may force auto (thermometer). |
| `color` | string or null | palette color, default `null` -> canvas `collectionColor` | Marker color (dot fill, number/letter circle). `null`/`"theme"` adapt to colored backgrounds, explicit values do not. |
| `decorationStyle` | – | forced `"filled"` by bullet/numbered/lettered | Not authorable on these kinds. |
| `width`, `height` | number | px, **written on every render** (min 150×20) | `width` = marker + 15 px gap + `textWidth` for left/right text, `max(marker, text)` for top/bottom; `height` from the text. Treat as cache. |
| `value` | object | `{ "blocks": [{ "type": "text", "html": "3" }] }`; generated when absent | `"numbered-text"` / `"lettered-text"` only: the marker text (see the subsections). |
| `frameType` | – | reset to `null` by numbered/lettered | Not used by the kinds in this doc. |
| `fitToText`, `textAlign`, `markerSize` | – | – | Written by the editor / other kinds; **ignored** here (the callout always fits its contents; alignment follows `textDirection`; marker sizes are theme-fixed). |

Plus the container fields (`AuthoringElementContainer.md`) and the common fields (`BaseElement.md`).

#### Text direction rules

- Alignment follows the direction: text on the right is left-aligned, on the left right-aligned, above/below
  centred.
- Vertical placement (left/right): the marker is centred on the first line of the first block (for a single
  block shorter than the marker, the text is centred on the marker instead). Above/below: marker and text are
  centred on a common vertical axis, 15 px apart.
- `"auto"`: if the callout has at least one connector, take its first outgoing connector (else its first incoming
  one), find the point at the other end (the other node's anchor point, or the free `targetPoint`/`sourcePoint`)
  and the angle from that point to `x`/`y` (0° = the callout is to the right of it, 90° = below, 180° = left,
  270° = above). Angle > 300° or < 60° -> `"right"`; 240°–300° -> `"top"`; 115°–240° -> `"left"`; otherwise
  `"bottom"`. So the text always sits on the side **away from** the connector. Without connectors: `"right"`.
- Editor resize handles: only the side the text extends to (right handle for `"right"`, left for `"left"`, both
  for top/bottom) – they change `textWidth`, keeping the marker in place (`referencePointAnchor`).

### Nested elements

- `marker` -> `SVGCircleElement` (no model; bullet, timeline-text) or `value` -> `TextElement` with a circle
  decoration (numbered, lettered); filled with `color`.
- `text` -> `TextElement` (`TextElement.md`) bound to `text`: header block structure, default `"title"`, no block
  adding, scaled to fit, font size synced with sibling callouts, double click to edit.

### Kinds

#### BulletCallout (`"bullet-text"`)

A 14 px dot (theme `markerSize`) filled with `color`, `decorationStyle` forced to `"filled"`. Adds nothing to the
model. Offered by every host (flow chart, Classic, target, thermometer, XY graph, timeline2). It is the default
`calloutType` of the 10.02 migration for legacy annotation items without `nodeType`.

#### NumberedCallout (`"numbered-text"`)

A 50 px circle (theme) filled with `color` containing the `value` text (title style, 20 px, centred). Adds:

- `value` – `{ "blocks": [{ "type": "text", "textStyle": "_use_styles_", "html": "<n>" }] }`. When absent at build
  it is generated as **the entry's position in `elements[]` + 1** (counting every element of the canvas, not only
  numbered ones) and written to the model; it is not renumbered afterwards. Any text works (`"3"`, `"Q4"`); it is
  editable in the editor (single block, double click).
- `frameType` – set to `null` on every build (guards against a `"none"` left by a type change).
- `decorationStyle` forced `"filled"`.

#### LetteredCallout (`"lettered-text"`)

Identical to `NumberedCallout` except the generated `value` is the letter at the entry's index (`"A"` for index 0,
`"B"`, …; index 26 and above give characters after `"Z"`). Only the hidden `timeline2` template offers it in its
UI; the container renders it on any host.

#### TimelineTextCallout (`"timeline-text"`)

A `MarkerCallout` with a fixed 10 px dot: `markerSize` is hard-coded to 10 (model values ignored), the anchor
bounds are the 10×10 top-left corner of the callout and **every connector attaches at the fixed point (0, 50)
relative to the callout's top-left**, whatever anchor is requested. No host currently offers or creates
`"timeline-text"` (the Timeline's annotations are `ContentItem`s, see `Timeline.md`); it renders like a bullet
callout with a smaller dot. Not verified on a rendered slide – avoid unless a host asks for it.
