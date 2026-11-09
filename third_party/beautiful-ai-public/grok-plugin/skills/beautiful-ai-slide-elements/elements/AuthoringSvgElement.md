# AuthoringSvgElement

`AuthoringSvgElement` renders a fragment of raw SVG markup stored in the model, recolored with `fill`/`stroke`. It is
the child of an `AuthoringElementContainer` with `type: "svg"` (see `AuthoringElementContainer.md`) on Classic
slides (`authoring` template). **No current editor command or conversion creates this type**: it is a legacy /
internal element kept for existing models. For new SVG content use a `"shape"` entry with `shape: "raw_svg"`
(`AuthoringShapeElement.md`), which supports assets, a viewBox and aspect-ratio fitting.

Behaviour below is read from the code only (no example model, not verified at runtime).

## Model location

- `states[0].primary.elements[]` – the entry itself (shared with the container) for `type: "svg"`.
- `states[0].primary.elements[].element` – when the entry has an `element` sub-object.

## Minimal example

```json
{
  "id": "svg1", "type": "svg", "x": 100, "y": 100, "width": 200, "height": 200,
  "svg": "<path d=\"M0,0 L200,0 L100,200 Z\" style=\"\"/>",
  "fill": "theme", "stroke": "none", "strokeWidth": 0
}
```

## Pitfalls

- Omitting `svg` breaks the whole slide render; omitting `fill` paints the shape red.
- Not a replacement for `raw_svg` shapes: no asset loading, no viewBox scaling, no `@fill`/`@stroke` placeholders.
- Do not create new entries of this type; nothing in the app's UI produces or edits them.

## Rules and limits

- The markup is not scaled: coordinates in `svg` are px inside the container box (no `viewBox`), anything outside
  the box still draws (overflow visible), and the box only matters for selection, rotation and shadows.
- Only one element can be recolored (first `style` attribute); other nodes keep their own attributes.
- Colors resolve through the theme palette (`"theme"`, `"accent1"`, `"background_dark"`, …); `"none"` is
  transparent.
- Hit testing uses the container bounds. Animations: the container's "Fade in". No migrations.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Schema defaults are written into the model on build.

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `svg` (required) | string | inner SVG markup (e.g. `<path d="…" style=""/>`), no default | Injected (sanitized) into an `<svg>` of the container's `width`×`height` with visible overflow. **Absent -> the render throws** (string method on `undefined`). The first `style="…"` attribute in the string is replaced by `fill`/`stroke`/`stroke-width`; without a `style` attribute nothing is recolored. |
| `fill` | string | default `"red"`; palette name, CSS color, or `"none"` (transparent) | Fill written into that style attribute. |
| `stroke` | string | default `"black"`; palette name, CSS color, or `"none"` | Stroke color; transparent when `"none"` or when `strokeWidth` is `0`. |
| `strokeWidth` | number | default `2` | Stroke width written into the style attribute. |

Container fields (`x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, …) are in
`AuthoringElementContainer.md`; plus the common fields, see `BaseElement.md`.

### Nested elements

None.
