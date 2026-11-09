# CalloutsCanvas

The shared free-form layer for callouts (text boxes, shapes with text, bullet/numbered markers, icons) and the
connectors between them. It is an `AuthoringCanvas` (see `AuthoringCanvas.md`) restricted to callout element types,
with a `ConnectorGroup` added on top. It is never a template root by itself: `NodeDiagram` (template `flow_chart`,
see `NodeDiagram.md`) extends it, and `TargetAnnotations` (`target`), `ThermometerAnnotations` (`thermometer`) and
`XYGraphCanvas` (`xygraph`) are subclasses that sit on top of their diagrams (documented in `Target.md`,
`Thermometer.md`, `XYGraph.md`). The Timeline and chart annotations use the older `AnnotationLayer` instead (note at
the end).

## Model location

- `states[0].primary` for `NodeDiagram` (`flow_chart`).
- `states[0].primary.annotations` (or the field the host element binds it to) for the other subclasses; check the host's doc.
- `<location>.elements[]` – the callouts (`AuthoringElementContainer` models with `type: "callout"`).
- `<location>.connections.items[]` – the connectors (`ConnectorItem` models).

## Minimal example

Two connected box callouts on a `flow_chart` (`states[0].primary`):

```json
{
  "snapToGrid": true,
  "showGrid": false,
  "collectionColor": "theme",
  "elements": [
    { "id": "n1", "type": "callout", "calloutType": "box", "x": 300, "y": 200, "width": 180, "height": 80, "fitToText": true,
      "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Receive order" }] } },
    { "id": "n2", "type": "callout", "calloutType": "diamond", "x": 640, "y": 200, "width": 180, "height": 100, "fitToText": false,
      "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "In stock?" }] } }
  ],
  "connections": {
    "items": [
      { "id": "c1", "source": "n1", "target": "n2", "connectorType": "step", "endDecoration": "arrow",
        "labels": [{ "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "yes" }] }, "position": 0.5 }] }
    ]
  }
}
```

## Pitfalls

- `x`/`y` are the callout's reference point, not its top-left corner: centre for shapes/text/content, marker centre for
  marker callouts. Placing a 180px-wide box at `x: 0` cuts it in half (and the clamp then moves it).
- Every callout needs `type: "callout"`; an entry without `type` is silently dropped, and an unknown `calloutType`
  falls back to a box.
- Connector labels are `labels[].text.blocks`, not `labels[].blocks` (the app's horizontal flow-chart recipe writes the
  latter, which renders an empty label).
- Only shape callouts honour `fitToText` (default `false` when omitted); text, marker, media and flex-circle
  callouts always fit their contents and rewrite `width`/`height` on every render – see `CalloutElement.md`.
- Legacy `items`/`nodeType`/fractional coordinates are only converted by the migration when the slide `version` is
  below the migration; a v10 model must use `elements` with px coordinates.

### Note: AnnotationLayer

`AnnotationLayer` is the older free-positioning layer used by `TimelineAnnotations` (see `Timeline.md`) and
`ChartAnnotations` (see `Chart.md`). Differences from `CalloutsCanvas`:

- The collection is `items[]` (not `elements[]`) and each item is a `ContentItem` picked by `nodeType`
  (`"text"`, `"box"`, `"capsule"`, `"circle"`, `"bullet-text"`, `"content-and-text"`, `"numbered-text"`,
  `"content"`, `"line"`; default `"box"`), see `ContentItem.md`.
- `x`/`y` are **fractions 0–1** of the layer size (`bounds = size * x, size * y`), measured at the item's registration
  point; items are not constrained to the bounds. An item may instead carry `snapOptions: { elementId }` to sit at a
  snap point of another element.
- `connections.items[]` is the same `ConnectorGroup` model, with start points locked to their node.
- Optional `videoOverlay: { x, y, videoAssetId, ... }` renders a `VideoOverlay` at fractional `x`/`y`.
- Min 0 items; `maxItemCount` is 10 by default (20 for the Timeline). Deleting an item removes connectors whose
  `source` is that item.

## Rules and limits

- `restrictElementsToBounds` is on: each render clamps `x`/`y` (the reference point) into the canvas bounds and writes
  the clamped values back to the model.
- Deleting a callout removes every connector whose `source` or `target` is its id. Connectors that reference an id that
  does not exist keep rendering only if they have a `sourcePoint`/`targetPoint`; otherwise they are invalid.
- Connectors cannot be dragged to other nodes (`canConnectToOtherNodes: false`) except in `NodeDiagram`; a callout never
  connects to itself.
- Colors: a callout with an explicit `color` other than `"theme"` keeps it even on colored slide backgrounds; otherwise
  the palette may swap it for a readable color.
- Migration 10.02 (`_migrate_10_02`): legacy `items[]` (annotation nodes with `nodeType` and fractional `x`/`y`) become
  `elements[]` with `type: "callout"`, `calloutType: nodeType ?? "bullet-text"`, px positions computed from the
  fractional values after the first layout (`propsToMigrate`), `width` derived from the text (`textWidth ?? 200` plus
  padding), `markerSize` from the old `size`, and `fitToText: true` (`false` for circles). Blocks get
  `accentColor` from the old node color. `collectionColor` is set from the slide color and connectors without `color`
  take their source node's color.
- `AuthoringCanvas` migration 10.02 also normalizes `shadow.color` alpha into `shadow.opacity`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `elements` (required) | array | default `[]` | Callouts, see "elements[] model". Min 0 items. |
| `connections` | object | `{ items: [] }`, created if absent | Connectors between callouts (or free connectors), see "connections.items[] model". |
| `collectionColor` | string | palette color, default `"theme"` | Default color of callouts that have no `color`. |
| `snapToGrid` | boolean | default `false` (`NodeDiagram`: `true`) | Editor snapping to a 10px grid; also used when migrating legacy positions. |
| `showSnapLines` | boolean | default `true` | Editor only. |
| `items` | array | legacy | Pre-10.02 annotation items (`nodeType`, fractional `x`/`y`); migrated into `elements`, see Rules. |

#### elements[] model (callouts)

Every entry is an `AuthoringElementContainer` (`AuthoringElementContainer.md`: `id` – referenced by
`connections.items[].source`/`.target` –, `type`, `x`, `y`, `width`, `height`, `rotation`, `opacity`, `isHidden`,
`isLocked` – always reset to `false` here –, `shadow`, `groupIds`, `name`) whose child class is picked by
`calloutType`. The callout reads the **same object**, so its own fields sit next to the container's. The fields
each class reads, their defaults and limits are in the class docs; the contract they share (text blocks,
`textWidth`, `color`/`decorationStyle`, fit-to-contents, connector anchors, migrations) is in `CalloutElement.md`.

| `calloutType` | Class | Doc | Offered by the type picker of |
|---|---|---|---|
| `"box"`, `"circle"`, `"diamond"`, `"capsule"` | `ShapeCallout` | `ShapeCallout.md` | all (diamond/capsule only on `NodeDiagram`; `XYGraphCanvas` box only) |
| `"text"` | `TextCallout` | `TextCallout.md` | all |
| `"bullet-text"`, `"numbered-text"` | `BulletCallout`, `NumberedCallout` | `MarkerCallout.md` | all |
| `"lettered-text"`, `"timeline-text"` | `LetteredCallout`, `TimelineTextCallout` | `MarkerCallout.md` | none of these canvases (lettered: the hidden `timeline2` template) |
| `"content-and-text"` | `MediaAndTextCallout` | `MediaAndTextCallout.md` | all |
| `"content"` | `MediaCallout` | `MediaCallout.md` | all |
| `"flex-circle"` | `FlexCircleCallout` | `FlexCircleCallout.md` | `XYGraphCanvas` (its default), Classic `AuthoringCanvas` |
| anything else | `ShapeCallout` drawn as a box | `ShapeCallout.md` | – |

What this canvas itself reads or enforces on every entry:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `type` (required) | string | `"callout"` | Entries without a `type` are dropped on build (warning logged). |
| `calloutType` (required) | string | table above | Class selection. The "offered" lists only restrict the editor's type picker (`CalloutsCanvas`: box, circle, text, bullet-text, numbered-text, content-and-text, content; `NodeDiagram`: the same plus diamond and capsule; `XYGraphCanvas`: flex-circle, box, text, bullet-text, numbered-text, content-and-text, content); the container renders any class on any host. `"arrow-line"` in the picker adds a free connector, not a callout. |
| `x`, `y` (required) | number | px inside the canvas element (slide 1280×720 minus the host's margins/header); `NaN` -> slide centre; `0,0` on a `NodeDiagram` -> near the canvas centre | Position of the callout's **reference point**: the centre of the shape/text/media for `"box"`, `"circle"`, `"diamond"`, `"capsule"`, `"text"`, `"content"`; the marker centre for `"bullet-text"`, `"numbered-text"`, `"lettered-text"`, `"timeline-text"`, `"content-and-text"`, `"flex-circle"`. Clamped into the canvas on every render (see Rules). |
| `width`, `height` | number | px | Authored for shapes (and `width` for `"text"` and `"content"`); every other kind, and the height of text callouts, is recomputed from the contents and written back on each render (`CalloutElement.md`, "Fit to contents"). Minimum sizes are raised in the model. |
| `color` | string or null | palette color, default `null` -> `collectionColor` | Color of the shape/marker/frame. `null` and `"theme"` adapt to colored slide backgrounds; any other value is honoured as-is. |
| `text` | object | `{ "blocks": [...] }` | Callout text (`TextElement.md`); not used by `"content"`. Font sizes are synced across the callouts of a canvas. |
| `nodeType`, `propsToMigrate`, block `accentColor` | – | legacy | Left by migration 10.02; not read by the callout classes. |

#### connections.items[] model (connectors)

See `ConnectorGroup.md` for the full connector (`ConnectorItem`) model; the fields that matter here:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `source` | string or null | element id | Start node. `null` requires `sourcePoint: { x, y }` (px). |
| `target` | string or null | element id | End node. `null` requires `targetPoint: { x, y }` (px). |
| `startAnchor`, `endAnchor` | string | `"anchor-free"` (default), `"anchor-center"`, `"anchor-left"`, `"anchor-right"`, `"anchor-top"`, `"anchor-bottom"`, `"anchor-bottom-right"`… | Where the line attaches on each node. `"anchor-free"` lets the connector pick the closest point of the node's shape. |
| `connectorType` | string | `"straight"` (default), `"angle"`, `"step"`, `"arc"` | Line routing. `"step"` only where the host allows it (`NodeDiagram`). |
| `startDecoration`, `endDecoration` | string | `"none"` (default), `"arrow"`, `"circle"` | End caps. |
| `lineStyle` | string | `"solid"` (default), `"dashed"`, `"dotted"`, `"animate_dash"`, `"animate_pulse"` | Stroke pattern / animation. |
| `lineWeight` | number | px, default theme | Stroke width (stored examples also contain string values like `"5"`). |
| `color` | string | palette color, default `"secondary"` | Line color. The 10.02 migration copied the source node's color into connectors that had none. |
| `labels` | array | `[{ text: { blocks: [...] }, position: 0.5, offset: 0 }]` | Text labels along the path; `position` is 0–1 along the line, `offset` a perpendicular distance in px (a label with `offset: 0` gets a background box). |
| `adjustments` | object | `{}` | Manual bend offsets for `"step"` connectors (editor-written). |
| `endPointIsLocked`, `canChangeConnectorType` | boolean | – | Editor flags used by hosts that generate connectors (Timeline). |

### Nested elements

- `elements[]` -> `AuthoringElementContainer` (`AuthoringElementContainer.md`) -> the callout class picked by
  `calloutType` (`CalloutElement.md` for the shared contract): `ShapeCallout.md` (`box`, `circle`, `diamond`,
  `capsule`), `TextCallout.md` (`text`), `MarkerCallout.md` (`bullet-text`, `numbered-text`, `lettered-text`,
  `timeline-text`), `MediaAndTextCallout.md` (`content-and-text`), `MediaCallout.md` (`content`),
  `FlexCircleCallout.md` (`flex-circle`). Rendered in array order (later entries on top). Min 0, no max in the
  code.
- `connections` -> `ConnectorGroup.md` (a collection of `ConnectorItem`), drawn below the callouts (`layer: -1`).
