# AuthoringShapeElement

`AuthoringShapeElement` draws one vector shape (rectangle, ellipse, arrow, chevron, star, …, or a raw SVG asset)
with an optional text stack inside it. It is the child of an `AuthoringElementContainer` with `type: "shape"` (see
`AuthoringElementContainer.md`) on Classic slides (`authoring` template) and the fallback child of `"component"`
entries without a `componentType`. A **text box** on a Classic slide is simply a shape with `fill: "none"` and
`stroke: "none"`. `ShapeCallout` (the box/circle/diamond/capsule callouts of `CalloutsCanvas.md`) extends this class
and reuses its text handling.

No stored example of the `authoring` template is available; examples below are the editor's default models.

## Model location

- `states[0].primary.elements[]` – the entry itself (shared with the container) for `type: "shape"` on the
  `authoring` template; the same object also carries `x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, …
- `states[0].primary.elements[].element` – only when the entry has an `element` sub-object (then every shape field
  must be in there).

## Minimal example

The editor's default **text box** (container + shape fields on one object):

```json
{
  "id": "t1", "type": "shape", "x": 80, "y": 60, "width": 400, "height": 150,
  "shape": "rect", "fill": "none", "stroke": "none",
  "textAlign": "left", "verticalAlign": "top", "fitToText": true, "textInset": 0,
  "text": { "blocks": [{ "id": "b1", "type": "text", "textStyle": "heading", "html": "Quarterly review" }] }
}
```

A filled rounded rectangle with centred title text and a dashed outline:

```json
{
  "id": "s1", "type": "shape", "x": 80, "y": 240, "width": 420, "height": 180,
  "shape": "rect", "adj1": 16, "fill": "theme", "stroke": "background_dark", "strokeWidth": 2, "strokeStyle": "dashed",
  "textInset": 20, "textAlign": "center", "verticalAlign": "middle",
  "text": { "blocks": [{ "id": "b1", "type": "text", "textStyle": "title", "html": "Revenue up 24%" }] }
}
```

A right-pointing arrow without text: `{ "id": "a1", "type": "shape", "shape": "arrow", "direction": "right",
"adj1": 0.4, "adj2": 0.6, "fill": "accent1", "x": 540, "y": 300, "width": 200, "height": 80 }`.

## Pitfalls

- Omitting `fill` gives the theme's `background_accent` fill, not a transparent shape; a text box needs
  `fill: "none"` **and** `stroke: "none"` (or `strokeWidth: 0`).
- `fitToText: true` overwrites the authored `height` (and may widen `width`); `fitToText: false` keeps the box and
  shrinks the text down to 10 % – long text in a small shape becomes unreadable without any warning.
- `textInset: 0` is only right for text boxes; shapes with a visible fill need padding or the text touches the edge.
- `verticalAlign` does nothing with `fitToText` on; `textAlign` is per shape, not per block.
- `"circle"` draws a circle of diameter `width` centred in the box; set `height == width` or the hit area and the
  drawing disagree.
- `"triangle"`, `"plus"`, `"callout_box"`, etc. exist in the enum but render nothing in the current app – use
  `"polygon"` with `adj1: 3` for a triangle.
- `adj1`/`adj2` units differ by shape (px for `"rect"`, ratios for arrows/chevrons/stars, counts for polygon sides
  and star points, a point object for `"callout_bubble"`).
- Do not create `"equation"` blocks without `svgHTML` (they all show E=mc²) and never emit `"region-start"` /
  `"region-end"` blocks.
- Legacy `blocks` / `blockGap` on the shape are only converted for models below version 10; a current model must use
  `text.blocks`.

## Rules and limits

- Text box detection: `fill == "none"` and (`stroke == "none"` or `strokeWidth == 0`) – such entries are named
  "Text Box" and the editor shows text tools. `isShapeVisible` (used for adjustment handles) is
  `fill != "none" || (stroke != "none" && strokeWidth > 0)`.
- Resizing in the editor is constrained by the fit flags: with `fitToText` only left/right handles remain, with
  `fitWidthToText` only top/bottom. `"ellipse"`, `"circle"`, `"star"`, `"polygon"` keep their aspect ratio by default
  (circle/star/polygon cannot be unlocked); `"arrow"`/`"chevron"`/`"chevron_start"` can be rotated by 90° steps,
  which swaps `width`/`height` and updates `direction`.
- `adj1` of a `"rect"` is written back clamped/rounded; the other adjustments are clamped at read time only.
- `"raw_svg"`: the markup is sanitized; only nodes whose `fill`/`stroke` attributes are literally `"@fill"` /
  `"@stroke"` are recolored. Hit testing uses the bounds. An SVG containing `<textPath href=` or `<clipPath id=`
  is exported as an image.
- Layout: with `fitToText`, `height = textHeight + top + bottom padding` and `width = max(width, textWidth +
  left + right)`; with `fitWidthToText`, `width = textWidth + left + right`. Otherwise the text is placed by
  `verticalAlign` inside `size − padding` and scaled to fit.
- Colors: `fill`/`stroke` resolve through the theme palette (`"primary"`/`"secondary"` pick the readable variant for
  the background). Decoration styles (`decorationStyle`) are **not** used by free shapes.
- Migration `_migrate_10`: `blocks` → `text.blocks`; per `textStyle` the legacy font size / line height are
  pinned on the block (`heading` 60/1.2, `title` 26/1.4, `caption`/`body` 20/1.4, …), `"bulleted"`/`"numbered"`
  become `textStyle: "bulleted"` with `listStyle` `"bullets"`/`"numbered"`, `lineHeight` ×1.4, `letterSpacing` ÷
  `fontSize`, and `blockGap` plus the old per-style gaps become per-block `spaceAbove` (minus the 30 px default
  spacing). `blocks` and `blockGap` are deleted.
- Animations: none of its own – the container's "Fade in" applies.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Schema defaults are written into the model on build (an authored entry gains `fill`, `stroke`, `strokeWidth`, … even
if you omit them). Container fields (`x`, `y`, `width`, `height`, `rotation`, `shadow`, `isLocked`, `isHidden`,
`groupIds`, `name`) are documented in `AuthoringElementContainer.md`.

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `shape` | string | `"rect"` (default), `"ellipse"`, `"circle"`, `"capsule"`, `"diamond"`, `"arrow"`, `"chevron"`, `"chevron_start"`, `"star"`, `"polygon"`, `"callout_bubble"`, `"raw_svg"`; also in the enum but **not drawn** by the renderer: `"none"`, `"triangle"`, `"callout_box"`, `"plus"`, `"minus"`, `"times"`, `"divided"`, `"equals"`, `"greater_than"`, `"less_than"` (the shape is invisible, text still renders) | Geometry, fitted to the container `width`×`height` (`"circle"` uses `width` as its diameter). |
| `fill` | string | `"background_accent"` (default); palette name (`"theme"`, `"accent1"`…`"accent8"`, `"chart1"`…`"chart6"`, `"background_light"`, `"background_dark"`, `"primary"`, `"secondary"`, `"white"`, `"black"`), CSS color (`"#1a73e8"`, `"rgb(…)"`), or `"none"` | Fill. `"none"` is transparent. An unknown name is parsed as a CSS color and renders black when invalid; a removed `accentN` falls back to `"theme"`. |
| `stroke` | string or null | default `null` (no stroke); same values as `fill` | Stroke color. `null`/`"none"` = no stroke. |
| `strokeWidth` | number | px, default `1` | Stroke width. `0` also disables the stroke for the text-box test. |
| `strokeStyle` | string | `"solid"` (default), `"dashed"` (dash 6×, gap 4× the width), `"dotted"` (dash 1×, gap max(width, 4)) | Stroke pattern. |
| `opacity` | number | 0–100, default `100` | Written by the editor's opacity slider. The *container* applies it (shared model); the value is also copied as-is into the SVG style, where anything ≥ 1 is clamped to fully opaque, so it has no extra effect. |
| `direction` | string | `"right"` (default), `"left"`, `"up"`, `"down"` | Pointing direction of `"arrow"`, `"chevron"`, `"chevron_start"`. Ignored by other shapes. |
| `adj1` | number or object | per shape, see "Adjustments" | First shape adjustment. |
| `adj2` | number | per shape | Second shape adjustment (`"star"`, `"arrow"`, `"callout_bubble"`). |
| `text` | object | `{ "blocks": [] }` (default: no text) | The text stack, `TextElement.md` format. Blocks without `type` get `"text"`; a block without `textStyle` is styled as `"heading"` (freeform default). |
| `textAlign` | string | `"left"`, `"center"` (default), `"right"`, `"justify"` | Horizontal alignment of all blocks (the editor keeps per-block `textAlign` cleared on shapes). |
| `verticalAlign` | string | `"top"`, `"middle"` (default), `"bottom"` | Vertical placement of the text inside a fixed-height shape. Ignored when `fitToText` is on. |
| `textInset` | number | px, default `20` | Padding between the shape edge and the text on all four sides. |
| `textPadding` | object | `{ "left", "right", "top", "bottom" }` px | Per-side padding written by PowerPoint import; when present it replaces `textInset`. |
| `fitToText` | boolean | default `false` | Height follows the text (height = text + top/bottom padding); width is widened if the text is wider. The container's `height` is rewritten on every render. |
| `fitWidthToText` | boolean | default `false` | Width follows the text, anchored on the `textAlign` side (left-aligned text grows to the right, centred text grows both ways). |
| `canReshape` | boolean | default `true` | Editor flag: whether the shape picker offers other shapes for this element. |
| `svgAssetId` | string | SVG asset id | `"raw_svg"` only: the SVG asset to load (ignored when `svgHTML` is set). |
| `svgHTML` | string | inline SVG markup (inner content, without the outer `<svg>`) | `"raw_svg"` only: inline markup. Nodes with `fill="@fill"` / `stroke="@stroke"` take `fill`/`stroke`/`strokeWidth`/`strokeStyle`. |
| `viewBox` | object | `{ "x", "y", "width", "height" }` | `"raw_svg"` only: viewBox of the inline SVG. |
| `preserveAspectRatio` | boolean | default none (= stretch) | `"raw_svg"` only: `true` = `xMidYMid meet`, otherwise `none`. |
| `strokeWidthCanvasScale` | number | default `1` | `"raw_svg"` only: multiplier applied to `strokeWidth` for `@stroke` nodes. |
| `canChangeFill`, `canChangeStroke` | boolean | default falsy | `"raw_svg"` only: enable the fill/stroke pickers in the editor (without them the colors are fixed). |
| `blocks`, `blockGap` | – | legacy | Pre-v10 text model, migrated into `text.blocks` / block `spaceAbove` (see Rules). |

Plus the common fields, see `BaseElement.md`.

#### Adjustments (`adj1`, `adj2`)

| `shape` | `adj1` | `adj2` |
|---|---|---|
| `"rect"` | corner radius in px, default `0`; clamped to `min(width, height) / 2` and rounded **in the model** on every render | – |
| `"chevron"`, `"chevron_start"` | point depth as a ratio of the cross dimension (height for left/right, width for up/down), default `0.25`, clamped to `0 … width/height` | – |
| `"arrow"` | stem thickness as a ratio of the cross dimension, default `0.5` (0–1) | head length as a ratio of the cross dimension, default `0.5`; the head never exceeds the shape length |
| `"star"` | inner-radius inset as a ratio of `width` (inner radius = outer radius − adj1 × width), default `0.2` | number of points, default `5` (editor handle gives 3–19) |
| `"polygon"` | number of sides, default `5` (editor handle gives 3–10) | – |
| `"callout_bubble"` | `{ "x", "y" }` position of the tail tip in px relative to the shape's top-left, default `{ x: 100, y: 100 }` | tail base width, default `30` |
| others | ignored | ignored |

#### Text inside the shape

The text is a `TextElement` (`TextElement.md`) bound to `text`, built only when `text.blocks` is non-empty, with
these owner options:

- Block structure freeform: allowed `textStyle` values `"heading"`, `"title"`, `"body"`, `"bulleted"`, `"caption"`,
  `"label"`, `"section"`, plus the block types `"media"`, `"divider"`, `"code"`, `"equation"`. Default block style
  `"heading"`; the editor's new-text-block button creates a `"title"` block, and the Classic "add text" command
  creates a text box whose single block has the chosen style (`heading`, `title`, `body`, `bulleted` + `listStyle:
  "bullets"`, `caption`, `label`, or a `code`/`equation` block).
- Alignment from the shape's `textAlign` (per-block `textAlign` is allowed but the editor syncs it away); vertical
  alignment handled by the shape (`verticalAlign`), only when `fitToText` is off.
- Auto-fit: when neither `fitToText` nor `fitWidthToText` is set the text is scaled down (to 10 %) to fit the shape;
  no "text clipped" warning is shown. With fit flags the shape grows instead.
- `evenBreak` is off by default; emphasized runs (`<font class="emphasized">`) are allowed; font size controls are
  shown; the last block may be deleted (leaving `blocks: []` = no text).
- Text color contrast is computed against `fill` when it is not `"none"`, else against the slide background.

Block fields are documented in `TextElement.md`. What the authoring block renderer adds or changes:

| Block `type` | Extra fields | Notes |
|---|---|---|
| `"code"` | `html` (the code, HTML-escaped text), `style`: `"light"` (default) / `"dark"`, `textSize`: `"small"` (16 px) / `"medium"` (20 px, default) / `"large"` (30 px) | Monospace, pre-wrapped, left-aligned regardless of `textAlign`, zero block margins. Empty `html` shows "Type code" in the editor only. |
| `"equation"` | `svgHTML` (pre-rendered SVG markup of the formula – this is what is drawn), `equation` (LaTeX source, default `"E=mc^2"`, stored for editing only), `fontSize` px (default `25`), `textAlign` (default `"left"`), `backgroundColor` (palette color, default `"white"`) | Without `svgHTML` a built-in E=mc² SVG is drawn whatever `equation` says; the MCP cannot render LaTeX, so only reuse existing `svgHTML`. 20 px padding, zero block margins. |
| `"media"` | `elementModel` (`{ "elementType": "MediaBlock", "content_type", "content_value", … }`), `blockHeight` px (default `100`), `autoWidth` (default `true`), `backgroundColor` | Inline icon/image, see `TextElement.md`. |
| `"element"`, `"cards"` | `elementModel.elementType` (class name; `"Cards"` is created for `"cards"`), `blockHeight` (default `300`), `autoHeight` (`"cards"` default `true`), `autoWidth`, `backgroundColor` | Embedded element rendered in document mode; the element's own fields go into `elementModel`. Not verified beyond the model wiring – avoid. |
| `"divider"` | as in `TextElement.md` (`blockHeight` default `20`, `dividerWidth`, `style`, `dividerColor`) | – |
| `"region-start"`, `"region-end"` | – | Defined in the constants but the block renderer throws "Unknown block type" for them: never store them. |

`blockStyle: "inset"` / `"color"` runs are framed by the block container (white with a grey border, or
`blockColor`, default `#f1f1f1`), inflated by 30 px.

### Nested elements

- `text` -> `TextElement` (`TextElement.md`), only when `text.blocks.length > 0`. Media/element blocks inside it
  create their own child (`MediaBlock`, or the class named by `elementModel.elementType`).
- The shape itself is an inline SVG (`rect`, `ellipse`, `circle` or `path`), no child element.
