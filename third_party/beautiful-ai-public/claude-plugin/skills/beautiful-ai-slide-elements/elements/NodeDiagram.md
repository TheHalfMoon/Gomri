# NodeDiagram

The flow chart: free-positioned nodes (box, circle, diamond, capsule, text, bullet/numbered marker, icon or
icon-and-text callouts) connected by step/straight/angle/arc connectors with optional arrow heads and labels, on an
optional dot grid. It is the root element of the `flow_chart` template (`states[0].primary`) and extends
`CalloutsCanvas` (see `CalloutsCanvas.md`), which defines the node (`elements[]`) and connector
(`connections.items[]`) models; this doc covers what the flow chart adds or changes.

## Model location

- `states[0].primary` – the diagram (template `flow_chart`).
- `states[0].primary.elements[]` – nodes (`AuthoringElementContainer` with `type: "callout"`).
- `states[0].primary.connections.items[]` – connectors (`ConnectorItem`).
- `states[0].header` – optional header (default position top); tray layouts as the template allows; `allowCallouts: false` (no extra callout layer on top).

## Minimal example

`states[0]` fragment (vertical flow with a decision):

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Order process" }] } },
  "primary": {
    "snapToGrid": true,
    "showGrid": false,
    "elements": [
      { "id": "start", "type": "callout", "calloutType": "capsule", "x": 590, "y": 60, "width": 180, "height": 60,
        "fitToText": true, "color": "accent1",
        "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Start" }] } },
      { "id": "check", "type": "callout", "calloutType": "diamond", "x": 590, "y": 220, "width": 180, "height": 100,
        "fitToText": false,
        "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "In stock?" }] } },
      { "id": "ship", "type": "callout", "calloutType": "box", "x": 350, "y": 400, "width": 180, "height": 80,
        "fitToText": true,
        "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Ship order" }] } },
      { "id": "backorder", "type": "callout", "calloutType": "box", "x": 830, "y": 400, "width": 180, "height": 80,
        "fitToText": true,
        "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Back-order" }] } }
    ],
    "connections": { "items": [
      { "id": "c1", "source": "start", "target": "check", "connectorType": "step", "endDecoration": "arrow" },
      { "id": "c2", "source": "check", "target": "ship", "connectorType": "step", "endDecoration": "arrow",
        "labels": [{ "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "yes" }] }, "position": 0.5 }] },
      { "id": "c3", "source": "check", "target": "backorder", "connectorType": "step", "endDecoration": "arrow",
        "labels": [{ "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "no" }] }, "position": 0.5 }] }
    ] }
  }
}
```

The app's own recipe uses `"box"` for steps (180×80, `fitToText: true`), `"diamond"` for decisions (180×100,
`fitToText: false`), `"capsule"` for start/end (`color: "accent1"`), `decorationStyle: "filled"`, step connectors
with arrow heads, and spreads nodes over a 1180×475 area.

## Pitfalls

- Node ids must be unique and every connector `source`/`target` must match one; a dangling id leaves a connector with
  no geometry.
- `x`/`y` are node centres (marker centres for marker nodes), not top-left corners; keep them at least half the node
  size away from the edges or the clamp will move them.
- Leaving `x`/`y` at `0` recentres the node; stacking several zero-positioned nodes puts them all in the same place.
- `fitToText: true` on a `"diamond"` or `"circle"` produces a shape that hugs the text and looks squashed; the
  generator uses `fitToText: false` for diamonds and the code forces it off for circles.
- Connector labels are `labels[].text.blocks`; `labels[].blocks` renders empty.
- Do not author `nodeType`, `shape`, `fill`, `stroke`, `titleTextStyle` on nodes: they are legacy or app-written
  (`calloutType` is what selects the shape).
- `__generateImage` must not be left on `"content"`/`"content-and-text"` nodes you fill yourself.

## Rules and limits

- The canvas size is rounded to a multiple of 10px; node reference points are clamped into the canvas and written back.
- A node with both `x` and `y` falsy (`0`/missing) is moved to the centre of the canvas on first layout.
- Canvas margins are the theme's element margins (the app's generator assumes ~1180×475 px of usable area under a top
  header; the full slide is 1280×720).
- Deleting a node removes connectors that reference it as `source` or `target`.
- Animation order is derived from the connector graph: root nodes (no incoming connector) first, then their children.
- No item limit in the code (`minItemCount` 0).
- Migration `_migrate_10_02`: renames `connectors` to `connections`, converts legacy `items[]` (`nodeType`, fractional
  `x`/`y`) into `elements[]` callouts (see `CalloutsCanvas.md`), and gives colorless connectors their source node's
  color. 20 of the 27 stored `flow_chart` examples are still in that legacy shape (`items` + `connectors`,
  `migrationVersion` 2); only the 7 at `migrationVersion` 10.03 show the current model.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `elements` (required) | array | default `[]`; template default: one empty `"box"` at `590,248` | Nodes, see `CalloutsCanvas.md` "elements[] model". Min 0. |
| `connections` | object | `{ items: [] }`, created if absent | Connectors, see `CalloutsCanvas.md` "connections.items[] model". |
| `snapToGrid` | boolean | default `true` (template default `false`) | Snap node positions to the 10px grid in the editor. |
| `showGrid` | boolean | default `false` | Draws a `GridComponent` (10px dot grid, no model of its own) behind the nodes. |
| `showSnapLines` | boolean | default `true` | Editor only. |
| `collectionColor` | string | palette color, default `"theme"` | Default node color. |
| `connections.defaultConnectorProps` | object | – | Merged into every connector created by the editor (for example `{ connectorType: "straight" }`). |
| `connectors`, `items` | – | legacy | Pre-10.02 names (`connectors` -> `connections`, `items` -> `elements`), see Rules. |

#### Node model (elements[])

Allowed `calloutType`s: `"text"`, `"box"`, `"circle"`, `"diamond"`, `"capsule"`, `"bullet-text"`,
`"content-and-text"`, `"numbered-text"`, `"content"`. Fields: `id`, `type: "callout"`, `calloutType`, `x`, `y`
(px, reference point: shape centre or marker centre), `width`, `height`, `fitToText`, `text`, `textWidth`,
`textAlign`, `textDirection`, `color`, `decorationStyle`, `markerSize`, `content_type`/`content_value`,
`frameType`, `value`, `isLocked`, `isHidden`, `opacity`, `rotation`, `shadow` – all described in
`CalloutsCanvas.md`. Node text syncs its font size across all nodes.

#### Connector model (connections.items[])

`source`/`target` reference node ids. The editor's default connector is `startAnchor: "anchor-center"`,
`endAnchor: "anchor-free"`, `endDecoration: "arrow"`, `connectorType: "step"`; step connectors are allowed here
(`allowStepConnector`) and can be re-attached to other nodes in the editor. Default line color is `"secondary"`.
Labels: `labels: [{ text: { blocks: [...] }, position: 0–1, offset: px }]`.

### Nested elements

- `elements[]` -> callouts (`ShapeCallout`, `TextCallout`, `BulletCallout`, `NumberedCallout`, `MediaAndTextCallout`,
  `MediaCallout`), see `CalloutsCanvas.md`.
- `connections` -> `ConnectorGroup.md` (`ConnectorItem`s), drawn under the nodes.
- `grid` -> `GridComponent` when `showGrid` is true (internal, no model).
