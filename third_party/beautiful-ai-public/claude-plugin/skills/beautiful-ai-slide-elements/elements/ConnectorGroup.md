# ConnectorGroup

`ConnectorGroup` is a non-selectable collection of lines (`ConnectorItem`) drawn between sibling elements of its
parent: each connector names a `source` and a `target` element id (or fixed points) and the group computes the
path, arrowheads and labels at render time. It is never a root element. Parents that use it: `IconCircle` (ring of
arcs between the cycle nodes, model `primary.connectors`), `HubAndSpoke` (spokes to the hub, `primary.connectors`),
`NodeDiagram`/`AnnotationLayer`/`CalloutsCanvas`/`ChartAnnotations` (free connectors, documented with those
elements; some pass a custom item class through options). `ConnectorItem` and its label classes
`ConnectorItemLabels` / `ConnectorItemLabel` are folded in here.

## Model location

- `states[0].primary.connectors` - the group (`{ items: [...] }`) for `step_circular` and `hub_and_spoke`.
- `states[0].primary.connectors.items[]` - one `ConnectorItem` per line.
- `states[0].primary.connectors.items[].labels[]` - up to 3 `ConnectorItemLabel`s per line.
- Other parents put the group elsewhere (e.g. `states[0].annotations.connections`), see their docs.

## Minimal example

One connector of `states[0].primary.connectors.items[]` in a `step_circular` slide (the source/target ids are the
`primary.items[].id` values):

```json
{
  "source": "node-0",
  "target": "node-1",
  "connectorType": "arc",
  "startDecoration": "none",
  "endDecoration": "arrow",
  "lineStyle": "solid",
  "lineWeight": 3,
  "color": "secondary",
  "labels": [
    { "position": 0.5, "offset": 0, "text": { "blocks": [{ "html": "handoff", "type": "text" }] } }
  ]
}
```

## Pitfalls

- `source`/`target` must be the exact `id` strings of existing items (and `"hub"` for the hub). Give your items
  explicit ids when you write connectors; ids auto-generated at build time are unknown to you.
- In `IconCircle` and `HubAndSpoke` the connector *list* is derived from the items: you cannot add, remove or
  re-route lines there, only style them (`startDecoration`, `endDecoration`, `lineStyle`, `lineWeight`, `color`,
  `labels`). `connectorType` you write is overwritten.
- Do not write `null` entries, `adjustments`, or `sourcePoint`/`targetPoint` for the diagram connectors.
- `labels` beyond 3 are ignored by the UI limit only; keep to 1 short label per line, long labels overlap the nodes.
- `lineStyle: "animate_*"` has no effect in static renders/exports; it is fine to use but not a way to convey meaning.

## Rules and limits

- Geometry is computed every render from the current bounds of `source`/`target`: nothing about the line position is
  stored, only the references and styling. Anchors are resolved against the target element's `connectionShape`
  (circle intersection for `"HubAndSpokeCircle"`/circle nodes, box intersection otherwise).
- A connector whose `calcProps` throws (missing source/target, arc without elements) is logged and **removed from the
  model** by the group, so a bad reference silently loses that line on the next save.
- Decorations are shortened on short paths (arrow length <= half/quarter of the path) and skipped when the path is
  empty.
- Each connector has a "Grow" animation (reversed when only `startDecoration` is set).
- `_migrate_10_02`: missing `color` becomes `"secondary"`; `"auto"` becomes the source item's color.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Group level (`ConnectorGroup`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 0..n connector objects (`minItemCount` 0, `maxItemCount` 10 from the base; the diagrams regenerate the list themselves) | On build, entries that are `null` or lack both an end (`source`/`sourcePoint` **and** `target`/`targetPoint`) are removed from the model. |
| `collectionColor` | string | default `"theme"` | Only a fallback for `ConnectorItem.color`; the diagrams set connector colors explicitly. |
| `defaultConnectorProps` | object | | Written by the connector property panel; read only by `NodeDiagram`. |

#### items[] model (`ConnectorItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `source` | string | id of a sibling element of the group's parent (an `items[].id`, `"hub"`, ...) or an element path containing `/` | Start element. Required unless `sourcePoint` is given; an id that does not resolve throws "No source element for connector was found" (render error). |
| `target` | string | same | End element. Required unless `targetPoint` is given; unresolved -> render error. |
| `sourcePoint`, `targetPoint` | object | `{ x, y }` px in the group's coordinate space | Free end points used when the matching id is absent (free connectors only; not used by the cycle/hub diagrams). |
| `connectorType` | string | `"straight"` (default), `"angle"`, `"step"`, `"arc"` | Path shape. `"arc"` needs both `source` and `target` elements (throws otherwise) and anchors at their centers. `IconCircle` and `HubAndSpoke` **overwrite** this on every build. |
| `startDecoration`, `endDecoration` | string | `"none"` (default), `"arrow"`, `"circle"` | End caps at the source / target end. |
| `lineStyle` | string | `"solid"` (default), `"dotted"`, `"dashed"`, `"animate_pulse"`, `"animate_dash"` | Dash pattern; the two `animate_*` values run a continuous animation in the editor/player (static in exports). |
| `lineWeight` | number or `"bold"` | px, default from theme (2 in the diagrams' defaults; 3 in `IconCircle`); `"bold"` = 30px band with large arrowheads | Stroke width; arrowhead size scales with it. |
| `color` | string | palette color name (`"secondary"`, `"primary"`, `"theme"`, `"accent1"`...), default none | Line and decoration color. When absent the parent's connector color applies (both diagrams use `secondary` at 50% opacity). Legacy `"auto"` is migrated to the source item's color. |
| `startAnchor`, `endAnchor` | string | `"anchor-free"` (default), `"anchor-center"`, `"anchor-top"`, `"anchor-left"`, `"anchor-right"`, `"anchor-bottom"` | Which side of the element the line attaches to; `"anchor-free"` picks the nearest. Locked by the cycle/hub diagrams (their items are circles, lines meet the circle edge). |
| `startAnchorOffsetX/Y`, `endAnchorOffsetX/Y` | number | px, default 0 | Nudges of the attach points (straight/angle/step only). |
| `adjustments` | object | default `{}` | Drag adjustments of step-connector segments (`a1`, `a2`, ...); computed by the UI, reset when the geometry changes. Do not author. |
| `labels` | array | 0-3 label objects, default `[]` | Text labels along the line, see below. |
| `canChangeConnectorType` | boolean | | Written by `IconCircle` (`false`) for its UI; ignored by the renderer. |
| `id` | string | generated when missing | Item key. |

#### labels[] model (`ConnectorItemLabel`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks: [{ html, type: "text" }] }`, see `TextElement.md` | Label text (single auto-sized block, editable). |
| `position` | number | `0`-`1`, default `0.5` | Where along the path the label sits (fraction of the full path length). |
| `offset` | number | `-1`, `0` (default), `1` | `0`: centered on the line with a slide-background box behind it; `-1`/`1`: beside the line (above/below for horizontal segments, left/right for vertical ones), no background. |
| `id` | string | generated | |

### Nested elements

- `items[]` -> `ConnectorItem` (path + decorations rendered directly as SVG; `labels` -> `ConnectorItemLabels` ->
  `ConnectorItemLabel` -> `text` `TextElement.md`).
