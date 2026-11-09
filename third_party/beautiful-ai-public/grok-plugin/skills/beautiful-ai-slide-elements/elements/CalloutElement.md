# CalloutElement

`CalloutElement` is the abstract base of the callout classes: a text block with an optional marker (dot, number,
letter, icon or image) or a bare icon/image, placed freely on a callout canvas and connectable with connectors. It
is never a root and never instantiated directly: an `AuthoringElementContainer` entry with `type: "callout"` (see
`AuthoringElementContainer.md`) creates the concrete class from `calloutType`. `ShapeCallout` (box, circle, diamond,
capsule) does not inherit from this class – it extends `AuthoringShapeElement` – but implements the same callout
contract (reference point, connectors, colors) and is listed here for completeness. The canvases that host callouts
are documented in `CalloutsCanvas.md` (flow chart `NodeDiagram`, the annotation layers of `target`, `thermometer`,
`xygraph`) and `AuthoringCanvas.md` (Classic `authoring` slides).

There are no stored example models in the repository; the examples in this doc and in the per-class docs are built
from the classes' schemas/defaults and from the app's flow-chart recipe.

## `calloutType` -> class -> document

| `calloutType` | Class | Doc | Offered by (editor type picker) |
|---|---|---|---|
| `"box"` | `ShapeCallout` | `ShapeCallout.md` | flow chart, Classic, target/thermometer layers, XY graph |
| `"circle"` | `ShapeCallout` | `ShapeCallout.md` | flow chart, Classic, target/thermometer layers |
| `"diamond"` | `ShapeCallout` | `ShapeCallout.md` | flow chart |
| `"capsule"` | `ShapeCallout` | `ShapeCallout.md` | flow chart |
| `"text"` | `TextCallout` | `TextCallout.md` | all hosts |
| `"bullet-text"` | `BulletCallout` | `MarkerCallout.md` | all hosts |
| `"numbered-text"` | `NumberedCallout` | `MarkerCallout.md` | all hosts |
| `"lettered-text"` | `LetteredCallout` | `MarkerCallout.md` | only the hidden `timeline2` template's milestone picker |
| `"timeline-text"` | `TimelineTextCallout` | `MarkerCallout.md` | no host offers it |
| `"content-and-text"` | `MediaAndTextCallout` | `MediaAndTextCallout.md` | all hosts |
| `"content"` | `MediaCallout` | `MediaCallout.md` | all hosts |
| `"flex-circle"` | `FlexCircleCallout` | `FlexCircleCallout.md` | Classic, XY graph (its default marker) |
| any other value | `ShapeCallout` drawn as a box | `ShapeCallout.md` | – |

`"arrow-line"` appears in the pickers but is not a callout: it adds a free connector (`ConnectorGroup.md`). The enum
also contains `"markerAndText"`, `"line"` and `"dashed-line"`, which have no class (a stored model with them renders
as a box). The "offered by" column is only what the editor UI proposes per host; the container instantiates any of
the classes on any host.

## Model location

The callout reads **the same object** as its container entry; all fields below sit next to `id`, `type`, `x`, `y`:

- `states[0].primary.elements[]` – `flow_chart` (`NodeDiagram`), `authoring` (Classic, `AuthoringCanvas`), `xygraph`
  (`XYGraphCanvas`, one entry per data row).
- `states[0].primary.annotations.elements[]` – `target` and `thermometer` annotation layers.
- `states[0].primary.milestones.elements[]` – the hidden `timeline2` template.

Do not put callout fields under an `element` sub-object: the container would hand that object to the callout while
it still reads `calloutType` from the entry (behaviour not verified; keep everything on the entry).

## Minimal example

One entry of each family on a `flow_chart` (`states[0].primary.elements[]`), from the recipe and the class defaults:

```json
[
  { "id": "n1", "type": "callout", "calloutType": "box", "x": 300, "y": 200, "width": 180, "height": 80,
    "fitToText": true, "decorationStyle": "filled",
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Receive order" }] } },
  { "id": "n2", "type": "callout", "calloutType": "bullet-text", "x": 640, "y": 200, "textWidth": 200,
    "textDirection": "auto", "color": "accent1",
    "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Check stock" }] } },
  { "id": "n3", "type": "callout", "calloutType": "content", "x": 980, "y": 200, "width": 80, "height": 80,
    "content_type": "icon", "content_value": "truck", "frameType": "circle" }
]
```

## Pitfalls

- `x`/`y` are the reference point (centre or marker centre), not the top-left corner.
- `calloutType` decides the class **and** must be spelt exactly; a typo silently renders a box.
- Only shapes honour `fitToText`; everything else resizes itself and overwrites `width`/`height`, so never encode
  layout intent in the `height` of a text or marker callout.
- `textWidth` sizes the text of marker callouts only; for `"text"` and shapes use `width`.
- `textAlign` is ignored by marker callouts, `textDirection` by everything but marker callouts.
- Set `textStyle` on every block: an omitted style gives `"heading"` (30 px) inside shapes.
- Keep `color` `null`/`"theme"` unless you want a fixed color: explicit colors are not adapted to colored slide
  backgrounds.
- Do not author `nodeType`, `shape`, `fill`, `stroke`, `adj1`, `textColor`; they are legacy, app-written or unused.

## Rules and limits

- **Fit to contents** (what the canvas writes back into the entry on every render): `TextCallout` height;
  `ShapeCallout` height only when `fitToText` (width when `fitWidthToText`); `MarkerCallout` family,
  `MediaAndTextCallout`, `MediaCallout`, `FlexCircleCallout` width **and** height. The reference point stays where
  `x`/`y` say; the box grows around it.
- **Minimum sizes** (`limitSize`: `width`/`height` are raised in the model): base 40×20; marker callouts 150×20;
  `"flex-circle"` 10 wide; `"content"` 50×50 and at most 400×400; shapes 50×20.
- **Bounds**: on every `CalloutsCanvas` the reference point is clamped into the canvas and written back (a box whose
  centre is at `x: 0` is half outside and stays there; `AuthoringCanvas` does not clamp). `flow_chart` additionally
  recentres entries whose `x` and `y` are both falsy.
- **Connectors** (`ConnectorGroup.md`): connectors reference the entry `id`. Anchors offered: `"anchor-free"`,
  `"anchor-left"`, `"anchor-right"`, `"anchor-top"`, `"anchor-bottom"` (shapes add `"anchor-bottom-right"`); the
  side anchors are taken on the **anchor bounds** – the whole box for shape/text/media callouts, the marker only for
  marker callouts. With `"anchor-center"` (or free + straight) the line is trimmed at the callout's connection shape
  (`rect`/`circle`/`diamond`/`capsule` for shapes, circle for marker dots, the frame shape for media). A connector
  that would start and end inside the same callout is collapsed (`preventSelfPointingConnector`).
- **Default connector color** (connector without `color`, host without a default; the flow chart forces
  `"secondary"`): `"secondary"` for text callouts, the marker color for marker/media callouts, the shape's stroke
  (outlined styles) or fill color for shapes.
- **Editor-only options**: text direction can be changed only on marker callouts (hosts may lock it: the thermometer
  layer uses `useAutoDirection` and hides the control); `canChangeColor` is on for every class except `"text"`
  (the thermometer layer turns it on).
- **Colors**: see `color` above. `"theme"`/`null` adapt to the slide background; explicit colors do not.
- **Migrations**: 10.02 converts legacy annotation `items[]` into these entries (`CalloutsCanvas.md`) and deletes
  `iconColor` from `"content"`/`"content-and-text"` entries. 10.03: on the `collage` template a marker callout
  without `color` on a `"background_light"`/`"background_dark"`/`"background_accent"` slide gets
  `color: "primary"`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Container fields (`id`, `type: "callout"`, `calloutType`, `rotation`, `opacity`, `isHidden`, `isLocked`, `shadow`,
`groupIds`, `name`) are in `AuthoringElementContainer.md`. What every callout class reads or writes:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `x`, `y` (required) | number | px inside the canvas; `NaN` -> slide centre; on `flow_chart` both `0`/missing -> near the canvas centre (`canvas size / 2 − box size / 2`) | Position of the **reference point**: the centre of the shape/text/media box for `"box"`, `"circle"`, `"diamond"`, `"capsule"`, `"text"`, `"content"`; the **marker centre** for `"bullet-text"`, `"numbered-text"`, `"lettered-text"`, `"timeline-text"`, `"content-and-text"`, `"flex-circle"`. The box is laid out around that point. |
| `width`, `height` | number | px; absent -> canvas size is used for the first layout | Size of the box. Rewritten on every render by every class except the shapes (see "Fit to contents" below), so author them for shapes and treat them as cache elsewhere. |
| `text` | object | `{ "blocks": [...] }`; absent or empty: marker/text callouts write one empty `"title"` block (editor placeholder), shapes render no text, `"content"` ignores it | The text, `TextElement.md` block format; blocks get `id`, `html`, `type: "text"` filled in when missing. Block structure "header": allowed `textStyle` `"heading"`, `"title"`, `"body"`, `"label"`; set `textStyle` explicitly on every block (missing = `"title"` on marker/text callouts, `"heading"` on shapes). The editor does not add blocks (`canAddBlocks` false) but several blocks in the model render. Optional `text.blockFontScales` (`{ "title": 0.66 }`) scales a style; it is copied between sibling callouts (font sizes are synced across the canvas). |
| `textWidth` | number | px, default `200`; editor keeps it 150–1280 (100–1280 on text/shape callouts) | Width of the text column of **marker callouts** (`MarkerCallout.md`, `MediaAndTextCallout.md`, `FlexCircleCallout.md`). `TextCallout` and `ShapeCallout` lay their text out in `width`; on them `textWidth` is only kept in sync by the editor's resize and is not read by the layout. |
| `color` | string or null | palette color (`"theme"`, `"accent1"`…, `"primary"`, `"secondary"`, `"background_light"`…), default `null` -> the canvas `collectionColor` (default `"theme"`) | Shape fill/stroke, marker dot/number circle, media frame or unframed-icon color. `null` and `"theme"` are "automatic": on a colored slide background the palette swaps them for a readable color; any other explicit value is honoured as-is (`allowColorOnColor`). |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`, `"none"`; default: the theme's element style | How `color` is applied to shapes and shape-framed media. Forced to `"filled"` by `"bullet-text"`, `"numbered-text"`, `"lettered-text"`. See the class docs. |
| `fitToText` | boolean | read by `ShapeCallout` only (default `false` when absent; the editor writes `true` for new boxes) | See `ShapeCallout.md`. Every other class ignores it (they always fit their contents) even though the editor writes it. |
| `textDirection` | string | `"auto"`, `"right"`, `"left"`, `"top"`, `"bottom"` | Marker callouts and `"flex-circle"` only (`MarkerCallout.md`). |
| `textAlign` | string | `"left"`, `"center"`, `"right"` | `"text"` and shape callouts only (`TextCallout.md`, `ShapeCallout.md`); ignored by marker callouts (their alignment follows `textDirection`). |
| `markerSize` | number | px | `"content-and-text"` (default 75, min 50) and `"flex-circle"` (default 100, 10–400) only. Bullet/numbered/lettered markers have theme-fixed sizes. |
| `content_type`, `content_value`, `frameType` | string | see `MediaCallout.md`, `MediaAndTextCallout.md` | Media of `"content"` / `"content-and-text"`. `frameType` is reset to `null` by numbered/lettered callouts. |
| `value` | object | `{ "blocks": [{ "type": "text", "html": "1" }] }` | Marker text of `"numbered-text"` / `"lettered-text"`; generated from the entry index when absent. |
| `textInset`, `shape`, `fill`, `stroke`, `strokeWidth`, `strokeStyle`, `verticalAlign`, `adj1`, `direction`, `canReshape`, `fitWidthToText`, `titleTextStyle` | – | shape callouts | `ShapeCallout.md`: `textInset` and `verticalAlign` are authorable, the rest is written by the app. |
| `textColor` | – | written as `null` by the editor when the type changes | Not read by any callout class (not verified further); omit. |
| `nodeType`, `propsToMigrate`, `accentColor` (on blocks), `iconColor` | – | legacy | Left by the 10.02 migration (`CalloutsCanvas.md`) or deleted by it (`iconColor` on media callouts); never author them. |

### Nested elements

- `text` -> `TextElement` (`TextElement.md`) bound to `text`, on every class except `MediaCallout`. Options common
  to all callouts: header block structure, default style `"title"` (shapes: `"heading"`), no block adding, text
  scaled down to fit where the class fixes the box, font size synced with the sibling callouts, double click to
  edit.
- Per class: `marker` (`SVGCircleElement`, no model) for bullet/flex-circle/timeline-text, `value` (`TextElement`
  with a circle decoration) for numbered/lettered, `content` (`FramedMediaElement`, `FramedMediaElement.md`) for the
  media callouts; the shape is an inline SVG. See the class docs.
