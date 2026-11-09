# AuthoringRadialBar

`AuthoringRadialBar` wraps a `RadialBarGraph` ring (the ring of the compare-radial-bars template, see
`RadialBarInfographic.md`) as a free element of a Classic slide: the child of an `AuthoringElementContainer` with
`type: "radial_bar"` (see `AuthoringElementContainer.md`). **No current editor command or conversion creates this
type**, and the class is incomplete (see Rules): for a radial progress ring on a Classic slide use a `"component"`
entry – `componentType: "LayoutContainerItem"` with `element: { "componentType": "RadialBar", ... }` – which renders a
full `RadialBarInfographic` (`LayoutContainerItem.md`, `RadialBarInfographic.md`).

Behaviour below is read from the code only (no example model, not verified at runtime).

## Model location

- `states[0].primary.elements[]` – the entry itself (shared with the container) for `type: "radial_bar"`.
- `states[0].primary.elements[].element` – when the entry has an `element` sub-object.

## Minimal example

The only form that renders without an error (an empty track circle):

```json
{ "id": "rb1", "type": "radial_bar", "x": 200, "y": 200, "width": 150, "height": 150, "value": 50, "format": "none" }
```

## Pitfalls

- Do not create this type: without `format: "none"` it throws, with it the arc is still missing. Use a
  `"component"` entry with a `"RadialBar"` cell instead.
- Existing entries in old models can be left alone only if they already carry `format: "none"`.

## Rules and limits

- The ring is driven by a value function the element is supposed to provide (`percentageValue`, a 0–1 share), but
  this class does not define it, so the arc receives `undefined` and its path is not drawn; only the faint track
  circle remains. `value` is never read for drawing.
- The label text is produced by asking the nearest collection (here the `AuthoringCanvas`) to format the value; the
  canvas has no such method, so building the label throws and the slide fails to render unless `format: "none"`.
- The ring is a square of `min(width, height)` centred in the box; the element keeps its authored size and reports
  no fit-to-contents. Editor resizing keeps the aspect ratio.
- Animations: the container's "Fade in". No migrations.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | number | schema default `50` (written on build) | Intended ring value. Stored, but **not used for the arc** by the current code (see Rules). |
| `format` | string | `"none"`, or any other value / absent | `"none"` hides the centre label; anything else (including absent) builds a label. |

Container fields (`x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, …) are in
`AuthoringElementContainer.md`; plus the common fields, see `BaseElement.md`.

### Nested elements

- `radialBar` -> `RadialBarGraph` (documented in `RadialBarInfographic.md`): a faint full circle and an arc, with a
  `CompareValuesItemLabel` in the middle when the label is shown.
