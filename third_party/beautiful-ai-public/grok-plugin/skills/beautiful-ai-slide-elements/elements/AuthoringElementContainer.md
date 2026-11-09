# AuthoringElementContainer

`AuthoringElementContainer` is one entry of the `elements[]` array of an `AuthoringCanvas` (see `AuthoringCanvas.md`)
or of a `CalloutsCanvas` (see `CalloutsCanvas.md`). It is a collection item that positions, sizes, rotates, fades and
shadows exactly one child element; `type` selects the child class (shape, path, image/icon, callout, embedded
component, …). The child normally reads **the same object** as the container, so the fields of the shape, path or
media sit next to `x`/`y`/`width`/`height`; only when the entry has an `element` sub-object does the child read that
instead. `AuthoringElementsGroup` is a model-less placeholder class that stands for a set of containers sharing a
group id; it only exists to merge their animations into one "Group #n" entry.

No stored example of the `authoring` template is available in the examples set; the examples below come from the
code's defaults and from the app's flow-chart recipe (callout containers).

## Model location

- `states[0].primary.elements[]` – template `authoring` (root `AuthoringCanvas`) and template `flow_chart` (root
  `NodeDiagram`, a `CalloutsCanvas`).
- `<callout canvas>.elements[]` – the callout layers of `target`, `thermometer`, `xygraph` (see the host docs and
  `CalloutsCanvas.md`).
- `states[0].primary.items[].childElement.elements[]` – a `Dashboard` cell with `componentType: "Canvas"` (see
  `LayoutContainerItem.md`).
- `<entry>.element` – optional sub-model read by the child element instead of the entry itself.

## Minimal example

A container with every container-level field set, wrapping a filled rectangle (shape fields on the same object,
see `AuthoringShapeElement.md`):

```json
{
  "id": "box1",
  "type": "shape",
  "x": 80, "y": 220, "width": 420, "height": 180,
  "rotation": 0,
  "opacity": 100,
  "isLocked": false,
  "isHidden": false,
  "shadow": "soft",
  "groupIds": [],
  "name": "Revenue box",
  "shape": "rect", "adj1": 12, "fill": "theme", "stroke": "none",
  "text": { "blocks": [{ "id": "b1", "type": "text", "textStyle": "title", "html": "Revenue up 24%" }] }
}
```

A component entry whose child reads the `element` sub-model (a dashboard-style chart cell, see
`LayoutContainerItem.md` and `Chart.md`):

```json
{
  "id": "chart1",
  "type": "component",
  "componentType": "LayoutContainerItem",
  "x": 560, "y": 120, "width": 640, "height": 400,
  "element": { "componentType": "Chart" }
}
```

A callout container as written by the app's flow-chart recipe (`flow_chart`, see `CalloutsCanvas.md` for the
callout fields):

```json
{
  "id": "n1", "type": "callout", "calloutType": "box",
  "x": 590, "y": 71, "width": 180, "height": 80, "fitToText": true,
  "decorationStyle": "filled", "color": null,
  "text": { "blocks": [{ "id": "t1", "type": "text", "textStyle": "title", "html": "Receive order" }] }
}
```

## Pitfalls

- Always give `x`, `y`, `width`, `height`: a missing position is silently moved to the slide centre and a missing
  size makes the child fill the whole canvas.
- `x`/`y` mean different things per `type`: top-left corner for shapes, paths, media and components; reference point
  (centre or marker centre) for callouts.
- Do not put child fields under `element` for `"shape"`, `"path"` or `"content"` entries unless you put *all* of
  them there: once `element` exists the child ignores the fields on the entry.
- `"component"` entries need `componentType` **and** `element`; `componentType` alone renders a shape, `element`
  alone renders nothing useful.
- Never store `type: "text"` or `type: "infographic"` – they are editor commands, not element types, and break the
  slide.
- `opacity` is 0–100, not 0–1; `shadow.opacity` is 0–1.
- Array order is z-order: backgrounds first, text last. Groups are purely editorial (`groupIds`) – they do not create
  a nested element.

## Rules and limits

- Build: `element.type` is copied to `type` when `type` is missing; entries that still have no `type` are removed
  from the model. The container's schema (`isLocked: false`, `shadow: {}`, `opacity: 100`) is written into every
  entry, and the child's schema into the entry (shared model) or into `element`.
- Layout cache: a child is re-laid-out only when its entry differs (deep comparison) from the model used for the last
  layout, so unrelated edits do not touch other elements.
- Fit to contents: when the child reports `fitToContents.width`/`.height` (shapes with `fitWidthToText`/`fitToText`,
  all `"content"` entries, callouts), the canvas measures it with the full canvas size when needed, then writes the
  resulting `width`/`height` back into the entry and shifts `x`/`y` to keep the child's anchor (right/centre for
  width, bottom/centre for height; shapes anchor on the text alignment side, media on the centre).
- Minimum size: children with `limitSize` (shape callouts: 50×20 px) have `width`/`height` raised to their minimum
  in the model.
- Bounds: on `AuthoringCanvas` elements may extend beyond the slide. On `CalloutsCanvas` the reference point is
  clamped into the canvas and written back.
- Rendering order: `layer` = array index (first entry at the bottom). `rotation` is applied to the bounds;
  `isHidden` sets the rendered opacity to 0.
- Animations: the child's own animations are used when it has any (paths: "Grow in"); otherwise the entry gets a
  "Fade in". Paths never get the fade. Entries sharing a `groupIds[0]` are merged into a single "Animate in"
  entry. All authoring animations are disabled by default.
- Migration 10.02 (on the canvas): a `shadow.color` with alpha is split into an opaque `shadow.color` plus
  `shadow.opacity`.
- `canDelete` is `false` on the container itself – deletion goes through the canvas (`deleteItem`), which on callout
  canvases also removes connectors pointing at the entry.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Container fields (read by the container and by the canvas that lays it out):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` (required) | string | uuid; generated when missing | Identity of the entry; connectors reference it (`source`/`target`). |
| `type` (required) | string | see the table below | Child class. An entry without `type` takes `element.type` if present, otherwise it is dropped on build (warning logged). An unknown value throws and the whole slide fails to render. |
| `x`, `y` (required) | number | px inside the canvas; absent or `NaN` -> reset to the slide centre (640, 360) | Top-left corner of the child for `"shape"`, `"path"`, `"content"`, `"component"`, `"svg"`, `"video"`, `"radial_bar"`; the **reference point** (centre / marker centre) for `"callout"` entries. |
| `width`, `height` (required) | number | px; absent -> the whole canvas size is used | Size of the child. Rewritten on every render when the child fits to its contents (see Rules). |
| `rotation` | number | degrees clockwise, default none | Rotation around the centre of the bounds. |
| `opacity` | number | 0–100, schema default `100` (written on build) | Opacity of the whole entry. Children of type `"shape"` have their own `opacity` on the same key, so one value serves both. |
| `isLocked` | boolean | schema default `false` | Cannot be selected or dragged in the editor. Forced to `false` on canvases that disallow locking (`CalloutsCanvas` and its subclasses). |
| `isHidden` | boolean | default `false` | Rendered with opacity 0 and not selectable (still occupies its layer). |
| `shadow` | object or string | schema default `{}` (none); `"drop"` (3px 5px 6px 40 % black), `"soft"` (0 0 10px 40 % black), `"block"` (10px 10px 0 50 % black), or `{ "color": "rgb(r, g, b)", "opacity": 0–1, "x": px, "y": px, "blur": px }` | CSS drop-shadow filter on the entry. A custom object with `color: "rgba(0, 0, 0, 0)"` means none. |
| `groupIds` | string[] | created as `[]` on build | Editor grouping; the first entry is the active group id. Grouped entries move together in the editor and animate as one "Group #n". |
| `name` | string | default derived from the child (`"Text Box"`, the shape name, the icon/asset name or `"Image"`, `"Callout"`/`"Node"`, the component's name, else the type) | Label in the layers and animation panels. |
| `element` | object | – | Sub-model for the child. When present (any `type`) the child reads it and its schema defaults are written there; when absent the child shares the entry and writes its defaults (e.g. a shape's `fill`, `strokeWidth`, `textInset`) into the entry itself. The editor always writes `element: {}` for `"component"` entries; "Convert to Classic" also writes it for `"video"` and some `"content"` entries. |
| `componentType` | string | element class name, e.g. `"LayoutContainerItem"` | `"component"` only: the class to instantiate for the child (`element` holds its model). Without it the entry renders as an `AuthoringShapeElement`. |
| `calloutType` | string | see `CalloutsCanvas.md` | `"callout"` only: picks the callout class; unknown values fall back to a box (`ShapeCallout`). |

Fields of the child that the **canvas** reads through the container (they live on the entry when `element` is absent):
`fitToText` / `fitWidthToText` (shapes and callouts), the media fields of `"content"` entries and the callout
`textWidth`/`markerSize` all make the child report a fit-to-contents size, which the canvas writes back into
`width`/`height` (see Rules).

#### `type` values (`AuthoringElementType`)

| `type` | Child class | Doc | Authorable? |
|---|---|---|---|
| `"shape"` | `AuthoringShapeElement` – shapes and text boxes | `AuthoringShapeElement.md` | yes |
| `"path"` | `AuthoringPathElement` – polylines / arrows | `AuthoringPathElement.md` | yes |
| `"content"` | `AuthoringContentElement` – image, icon, logo | `AuthoringContentElement.md` | yes |
| `"callout"` | callout class picked by `calloutType` | `CalloutsCanvas.md` | yes (on `flow_chart` and the callout layers; the Classic editor only offers box, circle, flex-circle, text, bullet-text, numbered-text, content-and-text, content) |
| `"component"` | the class named by `componentType`, model in `element` | `LayoutContainerItem.md` for infographics | yes – `componentType: "LayoutContainerItem"` with `element.componentType` `"Chart"`, `"PieChart"`, `"Table"`, … |
| `"svg"` | `AuthoringSvgElement` – raw inline SVG | `AuthoringSvgElement.md` | internal (no editor command creates it) |
| `"radial_bar"` | `AuthoringRadialBar` | `AuthoringRadialBar.md` | internal (no editor command creates it) |
| `"video"` | `AuthoringVideo` – a `Video` with an optional frame | `AuthoringVideo.md` | written by "Convert to Classic" of a `video` slide; usable |
| `"header"` | `Header` (the slide header rendered as a free element) | `Header.md` | written by "Convert to Classic" only; do not create |
| `"footer"` | `Footer` | `Footer.md` | reserved; the conversion code never writes it |
| `"text"`, `"infographic"` | – | – | **editor-only** creation commands: the editor turns them into a `"shape"` text box or a `"component"` before saving. Stored in a model they throw "Unknown element type". |
| `"animation"`, `"callout-connector"` | – | – | constants without a factory: throw if stored |

### Nested elements

- `childElement` -> the class selected by `type` (table above). Model = `element` if present, else the entry itself.
  Hit testing uses the real geometry for shapes and paths and the rectangular bounds for everything else; paths,
  components, headers and footers need a double click to select their inner element.
- `AuthoringElementsGroup` – no model; built on the fly from `groupIds` when animations are collected.
