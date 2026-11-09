# AuthoringCanvas

The free-form "Classic" slide: a collection of absolutely positioned elements (shapes with text, text boxes, images
and icons, free paths, embedded components) drawn in array order. It is the root element of the `authoring` template
(`states[0].primary`) and the base class of `CalloutsCanvas` (see `CalloutsCanvas.md`), which `NodeDiagram`
(`flow_chart`), `TargetAnnotations`, `ThermometerAnnotations` and `XYGraphCanvas` build on. It is also the child of
a `Dashboard` cell with `componentType: "Canvas"` (see `LayoutContainerItem.md`). Each entry of `elements[]` is an
`AuthoringElementContainer` (see `AuthoringElementContainer.md`) – position, size, rotation, opacity, shadow, lock
state – wrapping one child element selected by its `type`.

No stored example of the `authoring` template exists in the examples set; the model below is taken from the code.

## Model location

- `states[0].primary` – the canvas (template `authoring`).
- `states[0].primary.elements[]` – one `AuthoringElementContainer` per element (`AuthoringElementContainer.md`).
- `states[0].primary.items[].childElement` – a `Dashboard` cell with `componentType: "Canvas"`; its `elements[]`
  follow the same rules inside the cell.
- `states[0].header` – allowed (`layout.headerPosition` defaults to `"none"` in the template); no tray layouts;
  footer allowed.

## Minimal example

`states[0]` for an `authoring` slide with a title text box, a filled rounded rectangle and an icon (entry fields are
documented in `AuthoringElementContainer.md`, `AuthoringShapeElement.md`, `AuthoringContentElement.md`):

```json
{
  "primary": {
    "snapToGrid": false,
    "elements": [
      {
        "id": "title", "type": "shape", "shape": "rect", "fill": "none", "stroke": "none",
        "x": 80, "y": 60, "width": 800, "height": 100, "fitToText": true, "textInset": 0,
        "textAlign": "left", "verticalAlign": "top",
        "text": { "blocks": [{ "id": "b1", "type": "text", "textStyle": "heading", "html": "Quarterly review" }] }
      },
      {
        "id": "box", "type": "shape", "shape": "rect", "adj1": 12,
        "fill": "theme", "stroke": "none", "x": 80, "y": 220, "width": 420, "height": 180, "textInset": 20,
        "text": { "blocks": [{ "id": "b2", "type": "text", "textStyle": "title", "html": "Revenue up 24%" }] }
      },
      {
        "id": "icon", "type": "content", "content_type": "icon", "content_value": "rocket", "frameType": "none",
        "x": 560, "y": 240, "width": 140, "height": 140
      }
    ]
  }
}
```

## Pitfalls

- Element order is z-order: put backgrounds first, text last.
- Every entry needs a valid `type`; `"text"` and `"infographic"` are editor commands, not stored types, and break
  the render.
- `x`/`y` are top-left corners for shapes, content, paths and components but reference points (centre / marker
  centre) for callouts.
- Nothing keeps elements on the slide: check that `x + width <= 1280` and `y + height <= 720` yourself (minus the
  header area when there is one).
- `connections` are not rendered on an `authoring` slide; draw arrows with `"path"` entries or use `flow_chart`.
- `snapToGrid` does not round authored coordinates; write multiples of 10 yourself if you want grid alignment.

## Rules and limits

- Coordinates are px inside the canvas element. The canvas has no margins, so with `headerPosition: "none"` it is the
  full 1280×720 slide; with a header it is the primary area left by the header.
- Z-order is array order: `layer` = index, the first entry is at the bottom.
- Elements are **not** constrained to the canvas (they may extend past the slide edges); entries whose `x`/`y` are
  missing or `NaN` are moved to the slide centre.
- Build cleanup: entries without `type` take `element.type` when present, otherwise they are dropped (warning logged);
  an unknown `type` throws and the slide does not render.
- Only entries whose model changed since the last layout are re-measured (deep comparison); fit-to-content children
  write their new `width`/`height` (and shifted `x`/`y`) back into the model on every render – see
  `AuthoringElementContainer.md` for the per-type behaviour.
- Grid: 10 px snap grid, 20 px guide spacing, 40 px padding – editor concerns only.
- Editor default sizes (useful starting points): text box 400×150 (`fitToText: true`, `textInset: 0`), shape
  150×150, path 130×130, component 400×200 (`element: {}`), infographic component (`LayoutContainerItem`) 400×300,
  callouts 130×100 (box) / 130×130 (circle) / 130×150 (text) / 80×80 (content) / 200×150 (marker callouts).
- Callout types offered on a Classic slide: `"box"`, `"circle"`, `"flex-circle"`, `"text"`, `"bullet-text"`,
  `"numbered-text"`, `"content-and-text"`, `"content"`.
- Pasting into a Classic slide only accepts media assets or elements copied from another Classic slide.
- Animations: every element gets at most one animation (its own or "Fade in"), all disabled by default; entries
  sharing a group id are merged into one "Group #n" animation.
- Migration 10.02: for every entry, a `shadow.color` with alpha is split into opaque `shadow.color` +
  `shadow.opacity`.

### How CalloutsCanvas builds on it

`CalloutsCanvas` (`CalloutsCanvas.md`) is this class with: the element set restricted to `"callout"` entries; a
`ConnectorGroup` (`ConnectorGroup.md`) built from `connections.items[]` and drawn below the elements; the callout
reference point clamped into the canvas on every render (`restrictElementsToBounds`, by registration point);
locking and grouping disabled (`isLocked` is reset to `false`); no image paste; `collectionColor` as the default
callout color; and migration 10.02 that converts legacy annotation `items[]` into `elements[]`. `NodeDiagram`
(`NodeDiagram.md`) adds grid drawing and step connectors on top of that.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `elements` (required) | array | schema default `[]` | The element containers, bottom to top. Min 0 items, no max. A non-array value is reset to `[]`. |
| `snapToGrid` | boolean | schema default `false` | Editor: snap drags/resizes to the 10 px grid. No effect on authored coordinates. |
| `showSnapLines` | boolean | default `true` | Editor: show alignment guides. |
| `collectionColor` | string | palette color, default `"theme"` (written by the collection schema) | Fallback color for children that have none (frame color of `"content"` entries, callout colors in subclasses). |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`. The template `defaultData` is
`{ layout: { headerPosition: "none" }, primary: {} }`; template flags: `allowHeader`, `allowFooter`,
`allowColorBackgrounds`, `availableTrayLayouts: []`, `allowColorful: false`, `canSwitchTemplate: false`.

### Nested elements

- `elements[]` -> `AuthoringElementContainer` (`AuthoringElementContainer.md`); each one builds a `childElement` from
  its `type`:
  - `"shape"` -> `AuthoringShapeElement.md` (shapes and text boxes)
  - `"path"` -> `AuthoringPathElement.md` (lines, arrows, polygons)
  - `"content"` -> `AuthoringContentElement.md` (image, icon, logo)
  - `"callout"` -> the callout classes, see `CalloutsCanvas.md`
  - `"component"` -> the class named by `componentType` (infographics via `LayoutContainerItem.md`)
  - `"video"` -> `AuthoringVideo.md`; `"svg"` -> `AuthoringSvgElement.md`; `"radial_bar"` -> `AuthoringRadialBar.md`
    (the last two are legacy/internal)
  - `"header"` / `"footer"` -> `Header.md` / `Footer.md` (written by "Convert to Classic" only)
- No `ConnectorGroup` on the plain canvas: a `connections` object on an `authoring` slide is ignored (connectors
  exist only on `CalloutsCanvas`).
