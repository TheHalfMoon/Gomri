# ContentItem

The "node" of the collection-based diagrams: one text block with an optional marker (a dot, a number, a letter, an icon or image) or text inside a shape. The class rendering a node is picked from its `nodeType`; the parent collection decides which node types it offers and where the nodes go. It is never a root element. Parents: `HubAndSpoke.md` (`hub` and `items[]`), `IconCircle.md` (`items[]`), `Timeline.md` (the milestones in `annotations.items[]`), and the legacy `items[]` of callout layers (`CalloutsCanvas.md`, whose current callouts are `AuthoringElementContainer`s with the same `text`/marker fields but px positions). Despite the name it is unrelated to `ContentElement.md` (the media slot), although media nodes contain one.

## Model location

- `states[0].primary.items[]` for `IconCircle` and `HubAndSpoke` (plus `states[0].primary.hub` for the hub node).
- `states[0].primary.annotations.items[]` for `Timeline` milestones.
- Legacy: `states[0].primary.items[]` / `annotations.items[]` of callout layers before migration 10.02 (converted to `elements[]` on load).

## Node types

| `nodeType` | Renders | Text | Marker / shape |
|---|---|---|---|
| `"text"` | plain text block | `text` | none; connectors attach to the text bounds |
| `"bullet-text"` | dot + text | `text` | filled dot, size from the theme (not authored) |
| `"numbered-text"` | number badge + text | `text` | circle with the item's 1-based index (`value` when the parent allows editing it) |
| `"lettered-text"` | letter badge + text | `text` | circle with `A`, `B`, … (`value` when the parent allows editing it) |
| `"content-and-text"` | icon/image + text | `text` | `FramedMediaElement.md` reading `content_type`/`content_value` on the node; `size` is the marker size |
| `"content"` | icon/image only | – | `FramedMediaElement.md`, default asset type icon; `size` is the marker size |
| `"box"`, `"capsule"`, `"circle"`, `"diamond"` | text inside a shape | `text` | the shape, sized from the text (`textWidth`) or from `size: { width, height }` |
| `"flex-circle"` | text inside a circle, or next to it when it does not fit | `text` | circle of `size` px; with `textDirection: "auto"` the text goes inside when it fits |
| missing / unknown | treated as `"content-and-text"` by the class picker (`nodeType` getter defaults to `"box"` for the connector shape) | | |

Each parent restricts the choice (e.g. `IconCircle`: content-and-text, bullet-text, numbered-text, lettered-text; `Timeline`: text, bullet-text, numbered-text, lettered-text, content-and-text) and usually applies one `nodeType` to all its nodes; see the parent's doc.

## Minimal example

A `"content-and-text"` node (an `IconCircle` / `HubAndSpoke` item):

```json
{
  "id": "node-1",
  "nodeType": "content-and-text",
  "content_type": "icon",
  "content_value": "rocket",
  "text": {
    "blocks": [
      { "type": "text", "textStyle": "title", "html": "Launch" },
      { "type": "text", "textStyle": "body", "html": "Q3 rollout to all regions" }
    ]
  }
}
```

A `"numbered-text"` node needs only `id`, `nodeType` and `text`.

## Pitfalls

- A `"content"` / `"content-and-text"` node without `content_value` renders the empty media placeholder; a node with media fields but `nodeType: "text"` shows no media at all.
- Do not mix node types to get a different marker on one node when the parent applies a single style (`IconCircle`, `HubAndSpoke`, `Timeline` editors set it for all nodes); the renderer accepts it but the result looks inconsistent.
- `textWidth` must be a positive number or `null`: the 50–1280 clamp only applies to the editor's resize handle, so `0` or a tiny value is used as is and gives a collapsed text column. Leave it `null` to let the layout size the text.
- `x`/`y` are only authored for `Timeline` milestones (fractions); writing px values there pushes the milestone off the element.
- Keep `value` out of numbered/lettered nodes unless the parent supports editing it: where it is supported a stale `value` ("3" on the first node) is shown as is.

## Rules and limits

- Node geometry is marker + text: the marker's bounding box and the text column are unioned; the parent places the node by its registration point (marker center for marker types, shape center for shape types, text center for `"text"`), which is what connectors aim at.
- Shape nodes: `"circle"` and `"diamond"` cap the width at 500 px, the others at 1180 px; the height follows the text unless `size` is an object.
- `"flex-circle"` only puts the text inside the circle when `textDirection` is `"auto"` and the text fits the inscribed square at its synced size; otherwise it lays the text out on the right.
- Numbered and lettered badges count every node of the collection in array order (1-based / `A`-based), including empty ones.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` (required) | string | uuid | Node key; connectors reference it (`source` / `target`), see `ConnectorGroup.md`. |
| `nodeType` | string | see above | Picks the node class. |
| `text` | object | `{ blocks: [...] }`, see `TextElement.md` | The node's text (block structure "header": a `title` block, optional `body` block). Required for every type but `"content"`. |
| `textWidth` | number or null | px, 50–1280; `null` = auto width (then 200 px when a width is needed) | Width of the text column (marker types, `"text"`) or of the shape (shape types without `size`). |
| `textDirection` | string | `"left"`, `"right"`, `"top"`, `"bottom"`, `"auto"`; default `"auto"` for marker types, `"right"` otherwise | Side of the marker the text sits on. `"auto"` picks the side facing away from the node's first connector (`"right"` when unconnected). Ignored by `"text"` and shape types. |
| `size` | number | px, 50–400 (20–400 for `"content"`, 10+ for `"flex-circle"`); default from the theme (`markerSize`) | Marker diameter of the media/number/letter/flex-circle types. |
| `size` | object | `{ width, height }` px | Shape types only: a fixed shape size instead of fitting the text. |
| `color` | string | palette color (`"theme"`, `"accent1"`, …); default the parent's `collectionColor` | Marker / shape / icon frame color, and the default color of connectors leaving the node. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`; default theme element style | Fill style of shapes and media frames. Numbered/lettered markers are always filled; `"bullet-text"` and `"text"` ignore it. |
| `content_type`, `content_value` | string | `"icon"` + icon key, `"image"` + asset id; see `ContentElement.md` | Media of `"content"` / `"content-and-text"` nodes, read directly from the node model. |
| `frameType` | string | `"theme"`, `"none"`, `"circle"`, `"rect"`, `"rounded_rect"`, `"octagon"`, … | Frame of the media marker; `"theme"` follows the theme shape. |
| `value` | object | `{ blocks: [{ type: "text", html: "1" }] }` | Badge text of `"numbered-text"` / `"lettered-text"`, only where the parent lets users edit it (annotation layers other than the timeline's, e.g. chart annotations); `IconCircle`, `HubAndSpoke` and `Timeline` derive it from the index and never read it. |
| `hilited` | boolean | `false` | Emphasized node (collection item flag); `"flex-circle"` renders muted when hilited. |
| `x`, `y` | number | parent-defined | Node position. `Timeline`: fractions 0–1 of the element, authored. `IconCircle` / `HubAndSpoke`: computed by the layout on every render, do not author. Legacy callout items: fractions, migrated to px callouts. |
| `textPosition` | string | `"center"` | Rarely read; leave absent. |

Legacy fields the 10.x migrations rewrite: `userSize` -> `textWidth`; `label` -> `value`; `title: { text }` / `blocks` (old text object) -> `text.blocks`. Do not write them.

### Nested elements

- `text` -> `TextElement.md` (title-and-body, auto width when `textWidth` is `null`, font size synced across sibling nodes in most parents).
- `marker` -> dot (`"bullet-text"`), number/letter badge (`"numbered-text"`, `"lettered-text"`: a single-block `TextElement` named `value`), or `media` -> `FramedMediaElement.md` (`"content-and-text"`).
- `content` -> `FramedMediaElement.md` (`"content"`).
- `shape` -> the SVG shape (`"box"`, `"capsule"`, `"circle"`, `"diamond"`, `"flex-circle"`).
