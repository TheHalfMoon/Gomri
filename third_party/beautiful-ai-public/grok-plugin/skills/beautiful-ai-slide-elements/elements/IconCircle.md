# IconCircle

`IconCircle` ("Cycle") places 2-8 content nodes (icon/text nodes, see `ContentItem.md`) evenly on a circle,
ellipse or polygon and draws a connector from each node to the next, closing the loop. It is the root element of
template `step_circular`. The nodes are `ContentItem` subclasses chosen by each item's `nodeType`; the lines are a
`ConnectorGroup.md` whose list is generated from the items.

## Model location

- `states[0].primary` - the cycle (root of `step_circular`).
- `states[0].primary.items[]` - one node (`ContentItem` subclass) per step, clockwise from the top.
- `states[0].primary.connectors` - the `ConnectorGroup` (`{ items: [...] }`), one connector per step.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Product loop", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "clockwise": true,
    "shape_is_polygon": false,
    "ellipse_size": 1,
    "items": [
      { "id": "node-0", "nodeType": "content-and-text", "content_type": "icon", "content_value": "search", "text": { "blocks": [{ "html": "Research", "type": "text", "textStyle": "title" }] } },
      { "id": "node-1", "nodeType": "content-and-text", "content_type": "icon", "content_value": "pencil", "text": { "blocks": [{ "html": "Design", "type": "text", "textStyle": "title" }] } },
      { "id": "node-2", "nodeType": "content-and-text", "content_type": "icon", "content_value": "code", "text": { "blocks": [{ "html": "Build", "type": "text", "textStyle": "title" }] } },
      { "id": "node-3", "nodeType": "content-and-text", "content_type": "icon", "content_value": "chart-line", "text": { "blocks": [{ "html": "Measure", "type": "text", "textStyle": "title" }] } }
    ],
    "connectors": {
      "items": [
        { "source": "node-0", "target": "node-1", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 3 },
        { "source": "node-1", "target": "node-2", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 3 },
        { "source": "node-2", "target": "node-3", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 3 },
        { "source": "node-3", "target": "node-0", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 3 }
      ]
    }
  }
}
```

The `connectors` block is optional: leaving it out produces exactly these four arcs. Include it only to change the
line style (e.g. `"lineStyle": "dotted"`, `"endDecoration": "none"`, a `color`, or `labels`).

## Pitfalls

- Writing `connectors` with ids that do not match `items[].id` (or relying on auto-generated ids) throws the whole
  list away and regenerates default arrows: either give items explicit ids and reference them, or omit `connectors`.
- `connectorType` is not yours to set: use `shape_is_polygon` to choose arcs vs straight lines.
- Leave `content_value` empty only if you want the "add icon" placeholder; `defaultData` does exactly that.
- `clockwise` absent is not the same as `true` (the layouter treats `undefined` as counter-clockwise); set it.
- Do not reuse `hub`, `connectorStyle`, `layout` from a `HubAndSpoke` model here; they are ignored (and a `hub`
  item would be turned into a plain node).
- 7-8 nodes with long captions overlap; keep captions to a title block and 3-6 nodes for legibility.
- Do not leave `__generateImage` on nodes whose `content_value` you set (see `ContentElement.md`).

## Rules and limits

- `minItemCount` 2, `maxItemCount` 8 (the UI refuses more; the layouter still draws extra nodes, overlapping).
- Connectors: on every build the element (1) creates `connectors = { items: [] }` when missing; (2) if any connector
  references an id that is not an item, **discards all connectors** (logged warning) and regenerates; (3) when the
  list is empty, pushes one connector per item from item *i* to item *i+1* (last -> first) with the defaults
  `startDecoration: "none"`, `endDecoration: "arrow"` (or `"none"` when `show_arrows === false`), `lineStyle: "solid"`,
  `lineWeight: 3`; (4) for existing connectors, fills those defaults where absent and **forces** `connectorType` to
  `"arc"` (ellipse) or `"straight"` (polygon). Authors therefore control only `startDecoration`, `endDecoration`,
  `lineStyle`, `lineWeight`, `color` and `labels` per connector; `source`/`target` must match the ring.
- Adding/removing items in the UI re-wires the two affected connectors, copying the style of the removed one.
- Layout: node slot width 300px. With 3+ items the first item sits at 12 o'clock and the others follow clockwise
  (or counter-clockwise when `clockwise` is not `true`); with 2 items the first sits on the left. In polygon mode
  2 items use a square, 4 items start at the top-left corner.
- Migration from `HubAndSpoke` (an item with `id: "hub"`) converts the hub into a regular node.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 2-8 node objects (schema default `[{}, {}]`) | The steps. With 0 or 1 entries the schema pads the array to 2 with an empty `{}` node, which renders as an empty `"bullet-text"` placeholder. |
| `connectors` | object | `{ items: [...] }`, default generated | See "Connectors" below. Omit it for a new slide: it is built from `items`. |
| `clockwise` | boolean | default `true` in `defaultData` (`undefined` is treated as not clockwise by the layouter) | Direction in which items are placed around the circle. Always set it explicitly. |
| `shape_is_polygon` | boolean | default `false` | `false`: nodes on an ellipse with `"arc"` connectors; `true`: nodes on the corners of a regular polygon with `"straight"` connectors ("Use Straight Lines"). |
| `ellipse_size` | number | `1`-`2` (UI slider), default `1` | Horizontal stretch of the circle into an ellipse (only when `shape_is_polygon` is false). |
| `show_arrows` | boolean | legacy, default treated as `true` | Only sets the default `endDecoration` of generated connectors (`"arrow"` unless `false`). Prefer setting the connectors' decorations directly. |
| `collectionColor` | string | default `"theme"`; the generator uses `"colorful"` | Node color (see `CollectionElement.md`). |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Node frame style. |
| `useLegacyNodes` | boolean | migration flag | Legacy; forces `nodeType: "content-and-text"` on old items during migration. Do not write. |

Fields found in stored models that this element does not read: `connectorStyle`, `hub`, `reverseArrowDirection`,
`useAlternateRotation` (left over from a `HubAndSpoke` conversion; a `hub` item is merged into the ring on build).

#### items[] model (nodes)

Each item is a `ContentItem` node (see `ContentItem.md` for the full node model). The fields that matter here:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | any unique string; **set it yourself** when you also write `connectors` | Referenced by `connectors.items[].source/target`. |
| `nodeType` | string | `"content-and-text"` (icon/image + text, the template default), `"bullet-text"`, `"numbered-text"`, `"lettered-text"` (UI choices); missing -> `"bullet-text"` | Node style; the UI applies one style to all nodes. |
| `content_type`, `content_value` | string | `"icon"` + icon key (or an image/logo id), see `ContentElement.md` | The node's media for `"content-and-text"`; `defaultData` ships `content_type: "icon", content_value: ""` (empty placeholder). |
| `text` | object | `{ blocks }` (`title` block, optional `body`), see `TextElement.md` | Node caption; placed outside the circle (above for top nodes, below for bottom nodes). |
| `color`, `frameType`, `decorationStyle`, `textWidth`, `size` | | see `ContentItem.md` | Per-node overrides (`frameType: "theme"` is what stored slides carry). |

`x`/`y` on nodes are written by the layouter every render (circle positions); do not author them.

### Nested elements

- `items[]` -> `ContentItem.md` subclass per `nodeType` (frame forced to circle, text direction computed from the
  angle, font synced across nodes). Order = order around the circle.
- `connectors` -> `ConnectorGroup.md` with `ConnectorItem`s whose start/end points are locked to the node circles
  and which cannot be deleted from the UI.
