# HubAndSpoke

`HubAndSpoke` draws one central `hub` node and up to 8 `items` ("spokes") on an ellipse around it, each spoke joined
to the hub by a straight connector. It is the root element of template `hub_and_spoke`. Hub and spokes are
`ContentItem` nodes (see `ContentItem.md`) chosen by `nodeType`; the lines are a `ConnectorGroup.md` whose list is
regenerated from the spokes on every build.

## Model location

- `states[0].primary` - the diagram (root of `hub_and_spoke`).
- `states[0].primary.hub` - the hub node (a `ContentItem` subclass; its `id` is always `"hub"`).
- `states[0].primary.items[]` - one spoke node per entry, placed around the ellipse starting at the top.
- `states[0].primary.connectors` - the `ConnectorGroup` (`{ items: [...] }`), one connector per spoke.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Platform ecosystem", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "connectorStyle": "hub",
    "layout": "center",
    "useAlternateRotation": true,
    "ellipse_size": 1.9,
    "hub": {
      "id": "hub",
      "nodeType": "circle",
      "color": "theme",
      "textWidth": 120,
      "text": { "blocks": [{ "html": "Core platform", "type": "text", "textStyle": "title" }] }
    },
    "items": [
      { "id": "spoke-0", "nodeType": "content-and-text", "content_type": "icon", "content_value": "mobile", "text": { "blocks": [{ "html": "Mobile app", "type": "text", "textStyle": "title" }] } },
      { "id": "spoke-1", "nodeType": "content-and-text", "content_type": "icon", "content_value": "cloud", "text": { "blocks": [{ "html": "Cloud sync", "type": "text", "textStyle": "title" }] } },
      { "id": "spoke-2", "nodeType": "content-and-text", "content_type": "icon", "content_value": "plug", "text": { "blocks": [{ "html": "Integrations", "type": "text", "textStyle": "title" }] } },
      { "id": "spoke-3", "nodeType": "content-and-text", "content_type": "icon", "content_value": "chart-line", "text": { "blocks": [{ "html": "Analytics", "type": "text", "textStyle": "title" }] } }
    ],
    "connectors": {
      "items": [
        { "source": "spoke-0", "target": "hub", "connectorType": "straight", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 2 },
        { "source": "spoke-1", "target": "hub", "connectorType": "straight", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 2 },
        { "source": "spoke-2", "target": "hub", "connectorType": "straight", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 2 },
        { "source": "spoke-3", "target": "hub", "connectorType": "straight", "startDecoration": "none", "endDecoration": "arrow", "lineStyle": "solid", "lineWeight": 2 }
      ]
    }
  }
}
```

Omitting `connectors` gives the same lines with the default `startDecoration: "arrow"` (arrows pointing out at the
spokes). For text-only spokes use `nodeType: "text"` with a title + body block and no media fields.

## Pitfalls

- Connectors you write are matched by `source` = spoke id: connectors with `source: "hub"` (the generator's recipe
  does this) never match, are dropped, and only their style survives as the default for the regenerated ones. Write
  `source: <spoke id>, target: "hub"`, or omit `connectors` and accept the defaults.
- Do not put `null` entries in `items` or `connectors.items` (stored slides contain some, but the connector
  rebuild does not guard against null connectors; verify with a render if you must keep them).
- `hub.id` must be `"hub"`; a hub with another id is unreachable for the connectors.
- `useAlternateRotation` only changes 2/4/6-spoke layouts; with 3, 5, 7 or 8 spokes the first spoke is always at
  the top.
- Spoke `x`/`y`, hub `x`/`y` and `userSize` are computed/legacy; omit them.
- Long spoke captions overlap at `ellipse_size: 1`; for 6-8 spokes use a larger `ellipse_size` and title-only text.
- Do not leave `__generateImage` on the hub or spokes whose `content_value` you set (see `ContentElement.md`).

## Rules and limits

- `maxItemCount` 8 (`minItemCount` 1). Spokes are placed at equal angles starting from the top (`-90°`, or the
  alternate start for 2/4/6 spokes), clockwise, on an ellipse `rx = 150 + (ellipse_size - 1) * (maxRx - 150)`,
  `ry = min(height / 2 - 30, rx)`; node slot size 300x200.
- Connectors (`buildConnectorsModel`, every build): for each spoke, the connector whose `source` is that spoke's id
  is kept (or created), then rewritten to `source: <spoke id>, target: "hub", connectorType: "straight"` (in `"hub"`
  style). Connectors whose `source` is not a current spoke are dropped. So the connector *list* is always one per
  spoke; the author controls `startDecoration` / `endDecoration` / `lineStyle` / `lineWeight` / `color` / `labels`.
- Defaults for a newly created connector come from the **last existing connector** (`startDecoration`,
  `endDecoration`, `lineStyle` default `"solid"`, `lineWeight` default `2`, `color`); with no connector at all:
  `startDecoration: "arrow"` (arrowhead at the spoke), unless legacy `pointing_in === false` (then
  `endDecoration: "arrow"`, at the hub) or `show_arrows === false` (no arrows).
- Because the direction is spoke -> hub, an arrow **at the spokes** is `startDecoration: "arrow"`, an arrow **at the
  hub** is `endDecoration: "arrow"`.
- Connector color: `color` on the connector, else the group's secondary color at 50% alpha.
- `_migrate_10_02` sets `hub.color` from the slide color; it assumes `hub` exists (legacy models only).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-8 spoke nodes (`defaultData`: 4 x `{ nodeType: "content-and-text" }`) | The spokes. |
| `hub` | object | node model; created as `{ id: "hub", nodeType: "circle", userSize: 100, color: "theme" }` when missing | The center node. Its `id` must stay `"hub"` (connectors target it). |
| `connectors` | object | `{ items: [...] }`, regenerated | See "Connectors" below; omit for a new slide unless you want a specific line style. |
| `connectorStyle` | string | `"hub"` (default via schema), `"arc"`, anything else = straight ring | `"hub"`: every spoke connects to the hub (and the hub is shown). Other values connect spoke *i* to spoke *i+1* (arc or straight) and show the hub only when `showHub` is `true`. The UI only produces `"hub"`. |
| `showHub` | boolean | default absent | Forces the hub to be shown when `connectorStyle` is not `"hub"`. |
| `layout` | string | `"center"` (default), `"top"`, `"bottom"` | Hub position: centered with spokes all around, or at the top/bottom with spokes on a half ellipse below/above it. |
| `ellipse_size` | number | `1`-`3` (UI "Spoke Length"), default `1`; the generator uses `1.9` | Horizontal radius: `1` = 150px, `2` = the widest ring that keeps a 300px node slot inside the element, values above 2 push the spokes further out (and may overflow). The vertical radius is capped by the element height. |
| `useAlternateRotation` | boolean | default `true` (schema and `defaultData`) | With `layout: "center"` and exactly 2, 4 or 6 spokes, rotates the ring so spokes sit at the diagonals instead of top/bottom/left/right. Ignored for other counts. |
| `collectionColor` | string | default `"theme"`; the generator uses `"colorful"` | Spoke color (see `CollectionElement.md`). The control bar also copies the chosen color to `hub.color`. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Spoke frame style. |
| `reverseArrowDirection` | boolean | `false` in schema | Not read by the current code. |
| `show_arrows`, `pointing_in` | boolean | legacy (v5) | Only influence the *default* connector decorations when no connector exists yet (see below). Prefer explicit connector fields. |
| `startDecoration`, `endDecoration`, `lineStyle`, `lineWeight` (root level) | | | Passed to the connector group as `defaultProps`, which it never reads: no effect. Set them on `connectors.items[]`. |

#### hub model

A `ContentItem.md` node with `id: "hub"`. `nodeType` choices in the UI: `"circle"` (default; text in a circle,
size = `textWidth` 50-300px), `"box"`, `"diamond"` (same, `textWidth`), `"text"` (plain text, no size control),
`"content"` (an image/icon; size = `size` 50-300px, frame = `frameType` from the shape/device frames,
`content_type`/`content_value` as in `ContentElement.md`). `text` is `{ blocks }`; `color` (`"theme"` default),
`decorationStyle` and `frameType` override the collection. Legacy `userSize` is migrated to `textWidth`.

#### items[] model (spokes)

`ContentItem.md` nodes. UI `nodeType` choices: `"content-and-text"` (default; icon/image + text), `"bullet-text"`,
`"numbered-text"`, `"lettered-text"`; one style is applied to all spokes. Relevant fields: `id` (set it yourself if
you write `connectors`), `nodeType`, `content_type`/`content_value` (media for `"content-and-text"`), `text`
(`{ blocks }`, title + optional body), `color`, `frameType` (`"theme"` in stored slides), `decorationStyle`,
`textWidth`. `x`/`y` are written by the layout every render; do not author them.

### Nested elements

- `hub` -> `ContentItem.md` subclass per `hub.nodeType` (not draggable/deletable; `connectionShape`
  `"HubAndSpokeCircle"` when it is a circle so lines stop at its edge).
- `items[]` -> `ContentItem.md` subclass per `nodeType` (frame forced to circle, font synced across spokes).
- `connectors` -> `ConnectorGroup.md`, end points locked, connectors not deletable.
