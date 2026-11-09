# HorizontalFunnel

`HorizontalFunnel` draws a horizontal profile (slope, ramp, bump, mirrored funnel, wedge, bowtie) defined by a
curve of control points, sliced into vertical colored sections, one per item, each with an optional big value on
the section, an optional ornament (number/letter/icon) on the curve and an optional description under the funnel;
optional start/end labels sit left and right of the shape. It is the root element of template `horizontal-funnel`.
The internal classes `Funnel` (the clipped shape), `HorizontalFunnelSection` (an item) and
`HorizontalFunnelAxisLabel` (the start/end label text) are documented here.

## Model location

- `states[0].primary` - the funnel (root of `horizontal-funnel`).
- `states[0].primary.funnel[]` - the curve control points (read by `Funnel`).
- `states[0].primary.items[]` - one `HorizontalFunnelSection` per section, left to right.
- `states[0].primary.startLabel` / `endLabel` - `{ blocks }` of the axis labels (`HorizontalFunnelAxisLabel`).
- `states[0].primary.items[].ornament` - the ornament's own model (icon media for `ornament: "icon"`).

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Sales pipeline", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "theme-to-dark",
    "ornament": "number",
    "showValues": true,
    "showSectionDescriptions": true,
    "funnel": [{ "x": 0, "y": 0, "hx": 0.36, "hy": 0 }, { "x": 1, "y": 1, "hx": 0.85, "hy": 0 }],
    "mirror": true,
    "straightLines": true,
    "items": [
      { "value": { "blocks": [{ "html": "$8.2M", "type": "text", "textStyle": "title" }] }, "text": { "blocks": [{ "html": "Prospecting", "type": "text", "textStyle": "title" }, { "html": "33% of pipeline", "type": "text", "textStyle": "body" }] } },
      { "value": { "blocks": [{ "html": "$5.4M", "type": "text", "textStyle": "title" }] }, "text": { "blocks": [{ "html": "Proposal", "type": "text", "textStyle": "title" }, { "html": "22% of pipeline", "type": "text", "textStyle": "body" }] } },
      { "value": { "blocks": [{ "html": "$3.1M", "type": "text", "textStyle": "title" }] }, "text": { "blocks": [{ "html": "Closed won", "type": "text", "textStyle": "title" }, { "html": "13% of pipeline", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

Add `"showStartLabel": true, "startLabel": { "blocks": [{ "html": "Leads", "type": "text", "textStyle": "title" }] }`
(and the `end` pair) for axis labels.

## Pitfalls

- `startLabel`/`endLabel` render only with `showStartLabel`/`showEndLabel: true` (the generator writes the labels
  without the flags, so they never show).
- Do not leave `null` entries in `funnel`: the curve builder reads `.x` of every point and throws.
- `value` is text, not a number: write the formatted string you want to see (`"42%"`), there are no
  `format`/`formatOptions`.
- `y` is inverted relative to "height": `y: 0` is the tallest edge, `y: 1` the thinnest. A funnel narrowing to the
  right needs `y` increasing with `x`.
- Section `size`s that do not sum to 1 leave a gap or overflow; omit `size` on all items for an equal split.
- `showArrow` crashes the render; `funnelType` seen in the UI is not a model field.
- Keep descriptions short: they share the tallest description's height and shrink the funnel.

## Rules and limits

- `maxItemCount` 10 (`minItemCount` 1). Section widths come from `size` (fallback equal split) times the funnel
  width (element width minus label columns).
- Vertical budget: description height (max over sections, capped at 25% of the height) is reserved under the
  funnel; the value heights plus 60px (80px with an ornament) are reserved inside it; the curve uses what is left.
- `mirror`: the top edge is drawn in the upper half and reflected around the middle line, so the shape is
  symmetric; `y: 0` is still the thickest point and `y: 1` the thinnest, which in mirror mode never pinches below
  the band reserved for the values.
- Ornament position: on the curve at the section's horizontal center (intersection of a vertical line with the
  curve); with `mirror` and no values, at mid height.
- `funnel: []` is replaced by a fallback whose handles are in pixels (`hx: 300` / `900`) and renders a distorted
  curve: always provide real points.
- Colors: section fill = collection/section color; descriptions take the slide background; ornament circle = slide
  background with a stroke in the section color (inverted on colored backgrounds).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-10 sections (`defaultData`: 3) | Sections, left to right. |
| `funnel` (required) | array | 2+ points `{ x, y, hx, hy }`; `defaultData`: `[{ x: 0, y: 0, hx: 0.36, hy: 0 }, { x: 1, y: 1, hx: 0.85, hy: 0 }]` | The top edge of the shape. `x` 0-1 left to right; `y` 0-1 top to bottom of the curve area (`0` = full height, `1` = thinnest); `hx`/`hy` = bezier handle lengths as fractions of the width/height (outgoing handle at `+hx` from the point, incoming handle of the next point at `-hx`). Points must be sorted by `x`. The area **below** the curve is filled. |
| `mirror` | boolean | default absent (`false`) | Mirrors the curve vertically so the shape is symmetric around the middle (funnel/wedge/bowtie). Values and ornaments move to the vertical center. |
| `straightLines` | boolean | default absent (`false`) | Connect points with straight segments instead of bezier curves (`hx`/`hy` ignored). |
| `showValues` | boolean | `true` in `defaultData` | Builds each section's `value` text (big number on the section). |
| `showSectionDescriptions` | boolean | `true` in `defaultData` | Builds each section's `text` (description below the funnel). |
| `showStartLabel`, `showEndLabel` | boolean | default absent (`false`) | Show `startLabel` / `endLabel` (200px wide columns at the sides, vertically aligned to the curve ends). |
| `startLabel`, `endLabel` | object | `{ blocks }`, see `TextElement.md` (`title_and_body`, auto width, alignment allowed) | Axis label texts; only read when the matching `show*Label` is `true`. |
| `ornament` | string | `"none"` (default), `"number"`, `"letter"`, `"icon"`; `defaultData`: `"number"` | A 50px (icon: 75px) outlined circle on the curve at each section's center: 1,2,3 / A,B,C (computed) or the section's icon. |
| `collectionColor` | string | default `"theme"`; `defaultData` `"theme-to-dark"` | Section fill colors, shaded along the sections (always dark shading). |
| `showArrow` | boolean | | **Do not set**: it reserves 30px and then colors an `arrow` element that is never built -> render error. |

Presets used by the editor's shape picker (and the generator) for `funnel` / `mirror` / `straightLines`:

| Shape | `funnel` | `mirror` | `straightLines` |
|---|---|---|---|
| slope | `[{x:0,y:0,hx:0.36,hy:0},{x:1,y:1,hx:0.85,hy:0}]` | false | false |
| ramp | `[{x:0,y:1,hx:0.8,hy:0},{x:1,y:0,hx:0,hy:0}]` | false | false |
| bump | `[{x:0,y:1,hx:0.25,hy:0},{x:0.5,y:0.1,hx:0.25,hy:0},{x:1,y:1,hx:0.25,hy:0}]` | false | false |
| funnel | same points as slope | true | true |
| wedge | same points as bump | true | true |
| bowtie | `[{x:0,y:0,hx:0.3,hy:0},{x:0.5,y:0.75,hx:0.2,hy:0},{x:1,y:0,hx:0.3,hy:0}]` | true | false |

#### items[] model (`HorizontalFunnelSection`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | object | `{ blocks }` (`title_and_body`, up to 3 lines, placeholder `#`), see `TextElement.md` | The big figure drawn on the section (e.g. `"$8.2M"`, `"42%"`). Free text, not a number: there is no formatting. Shown when `showValues`. |
| `text` | object | `{ blocks }` (`title_and_body`, synced font and alignment) | Description under the funnel (title + optional body). Shown when `showSectionDescriptions`. |
| `size` | number | 0-1 fraction of the funnel width; default `1 / itemCount` | Relative width of the section. Sizes should sum to 1 (the UI redistributes them); larger sums overflow to the right. |
| `color` | string | palette color name | Per-section fill override (the ornament follows it). |
| `ornament` | object | `{ content_type: "icon", content_value: "<icon key>" }`, see `ContentElement.md` | The ornament's model (created as `{}` when missing). Only the icon fields matter, and only for `ornament: "icon"`; number/letter ornaments compute their label. |
| `id` | string | generated when missing | |

### Nested elements

- `funnel` -> `Funnel`: renders the clip path from `primary.funnel` and one colored block per section inside it (no
  model of its own).
- `startLabel` / `endLabel` -> `HorizontalFunnelAxisLabel` (`TextElement.md`), only when `show*Label`.
- `items[]` -> `HorizontalFunnelSection` (1-10): optional `ornament` -> `Ornament.md` (model `items[].ornament`),
  optional `value` -> `TextElement.md`, optional `text` -> `TextElement.md`.
