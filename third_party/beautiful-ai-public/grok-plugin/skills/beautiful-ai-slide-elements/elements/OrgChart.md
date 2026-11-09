# OrgChart

Renders a hierarchy tree: nodes (name + title text, optionally a photo/icon) laid out top-down or left-right from a
single root, with step connectors between parents and children. It is the root element of the `orgchart` template
(`states[0].primary`). The tree is defined purely by `items[]`: each node names its `parent` id and its `index`
among siblings; positions are computed by the layouter.

## Model location

- `states[0].primary` – the chart (template `orgchart`).
- `states[0].primary.items[]` – nodes (`OrgChartNode` subclasses).
- `states[0].primary.rowLabels[<rowIndex>]` – optional row labels (`OrgChartRowLabel`).
- `states[0].header` – header; tray layouts as the template allows.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Leadership team" }] } },
  "primary": {
    "defaultNodeStyle": "box",
    "layout": "expanded",
    "layoutDirection": "vertical",
    "hideRootNode": false,
    "items": [
      { "id": "ceo", "index": 0, "nodeType": "person",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Ada Lovelace" },
          { "type": "text", "textStyle": "body", "html": "CEO" } ] } },
      { "id": "cto", "parent": "ceo", "index": 0, "nodeType": "person",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Grace Hopper" },
          { "type": "text", "textStyle": "body", "html": "CTO" } ] } },
      { "id": "cfo", "parent": "ceo", "index": 1, "nodeType": "person",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Alan Turing" },
          { "type": "text", "textStyle": "body", "html": "CFO" } ] } },
      { "id": "eng", "parent": "cto", "index": 0, "nodeType": "person",
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Linus T." },
          { "type": "text", "textStyle": "body", "html": "VP Engineering" } ] } }
    ]
  }
}
```

For photo charts set `defaultNodeStyle: "photo1"` and add `content_type: "image", content_value: "<assetId>"` to
each node (the app's importer picks `photo1` when any node has media).

## Pitfalls

- `parent` must reference an existing `id` in the same array; misspelt ids make the node (and its subtree) disappear
  rather than error.
- Siblings with the same `index` have an undefined order; always number them 0..n-1 per parent.
- Node media is only visible with the `photo*` styles; `box`/`minimal` ignore `content_value`.
- Hierarchy is `parent`-based only: there is no `connections` array and no `children` list.
- `"colorful"` colors are per row, so siblings look identical; use per-node `color` for per-person colors.
- Large trees (>~20 nodes or >4 rows) shrink text heavily; consider `layout: "compressed"` or `"stacked"` and
  `smallRows` for the deepest rows.
- Do not leave `__generateImage` on photo nodes you fill yourself; four stored examples carry it on items.

## Rules and limits

- 1–40 nodes (editor limit; the element does not clamp). Rows are derived from the parent chain (`rowIndex` = depth,
  +1 extra when the parent has assistants).
- Orphans (bad `parent`) are deleted from the model silently. Exactly one root (node without `parent`) is expected; the
  layouter uses the first node without a parent as the root (behaviour with several roots not verified).
- Deleting a node in the editor re-parents its children to its parent and re-indexes siblings.
- `hideRootNode` is ignored for horizontal, stacked and table layouts.
- `layout: "table"` turns every node into a box and draws no connectors.
- Colors with `"colorful"` are assigned per row (all nodes of a row share a color).
- Migrations: `_migrate_10` maps `defaultNodeStyle: "circle"` to `"box"`; `_migrate_10_02` sets `connectorColor` from
  the slide color (`"colorful"` becomes `"theme"`) and clears `hilited` on `photo1` charts.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 40 | Nodes, see "items[] model". |
| `defaultNodeStyle` | string | `"box"` (default), `"minimal"`, `"photo1"`, `"photo2"`, `"photo3"` | Node rendering for all person nodes: framed text box, bare text, photo left of the text (`photo1`), photo above/beside (`photo2`), photo on top centred (`photo3`). Legacy `"circle"` is migrated to `"box"`. |
| `layout` | string | `"compressed"` (default), `"expanded"`, `"stacked"`, `"table"` | Tree packing: compressed subtrees, fully expanded, leaf nodes stacked vertically under their parent, or a plain table of boxes without connectors. |
| `layoutDirection` | string | `"vertical"` (default), `"horizontal"` | Root at the top (children below) or at the left (children to the right). |
| `hideRootNode` | boolean | default `false` | Hides the root node (its children become the first row). Only honoured for `"vertical"` direction with `"compressed"`/`"expanded"` layouts. |
| `horizontalSpacing`, `verticalSpacing` | number | px, default theme gaps | Gap between siblings / between rows. |
| `collectionColor` | string | palette color, default `"theme"` | Node decoration colors; `"colorful"` cycles per **row**. |
| `connectorColor` | string | palette color; default = `collectionColor`, or `"secondary"` when that is `"colorful"` | Connector line color. |
| `smallRows` | array of number | – | Row indices (0 = root row) rendered with the compact node style. |
| `rowLabels` | object | `{ "<rowIndex>": { text: { blocks: [...] } } }` | Labels drawn in a 100px column left of each listed row (`OrgChartRowLabel`, a title-and-body `TextElement`). |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, … | Node decoration style (box styles). |
| `showImage`, `shape` | – | read but unused / not verified | `showImage` is exposed on nodes but no node class uses it; `shape` feeds an unused getter. |

Plus the common fields, see `CollectionElement.md`.

#### items[] model (`OrgChartNode`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` (required) | string | any unique string (`"0"`, uuid, `"ceo"`) | Referenced by children's `parent`. Assigned if missing, but then nothing can point at it. |
| `parent` | string or absent | id of another node; absent/`null` = root | Parent link. **A node whose `parent` id does not exist is removed from the model on build.** |
| `index` | number | 0-based, default 0 | Order among siblings (left to right / top to bottom). Give every sibling a distinct index. |
| `text` (required) | object | `{ blocks: [...] }` | Node text, title-and-body structure: first block `"title"` (name), optional `"body"` (role). See `TextElement.md`. Font size syncs across all nodes. |
| `nodeType` | string | `"person"` (default), `"node"`, `"emphasized"`, `"picture-node"`, `"assistant"`, `"placeholder"`, `"label"` | `"person"`/`"node"`/`"emphasized"`/`"picture-node"`/`"assistant"` all render with `defaultNodeStyle`; `"placeholder"` is an outlined empty box (never emphasized); `"label"` is a text-only node (e.g. a department label). |
| `isAssistant` | boolean | default `false` | Draws the node beside the connector between its parent and its parent's children (assistant position); its siblings move one row further down. With `photo1`/`photo3` styles assistants render as `photo2`. |
| `content_type`, `content_value` | string | `"image"` + asset id, `"icon"` + icon key | Photo/icon for `photo1`/`photo2`/`photo3` styles (`ContentElement` bound to the item, see `ContentElement.md`; also `assetProps`, `scale`, `filter`…). Ignored by `box`/`minimal`. |
| `color` | string | palette color | Per-node decoration color override. |
| `hilited` | boolean | default `false` | Emphasizes this node; all other nodes are de-emphasized while any node is hilited. |
| `connectorType` | string | `"solid"` (default), `"dot"` | Style of the connector from this node to its parent (dotted = indirect report). |
| `textAlign` | string | `"left"`, `"center"`, `"right"` | Text alignment in `box` style (default centre for vertical, left for horizontal layouts). |
| `nodeSize`, `style` | – | unused | `nodeSize` has a getter but no reader; `style: "text-box"` is the editor's default item data. |

### Nested elements

- `items[]` -> `BoxOrgChartNode` (`box`, placeholders, and all nodes in `"table"` layout), `MinimalOrgChartNode`
  (`minimal`), `PictureOrgChartNode` (`photo1`/`photo2`/`photo3`, with `content` -> `ContentElement.md`),
  `LabelOrgChartNode` (`nodeType: "label"`), `HiddenOrgChartRootNode` (root when `hideRootNode`, size 0). Each has
  `text` -> `TextElement.md`. Order is by `parent`/`index`, not array order.
- `connectors` -> `OrgChartConnectors` (SVG step lines from each node with a `parent`, honouring `connectorType`;
  none in `"table"` layout; no model).
- `rowLabel<n>` -> `OrgChartRowLabel` for each truthy entry of `rowLabels` (fixed 100px width, shifts the tree right).
