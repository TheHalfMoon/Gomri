# CycleDiagram

`CycleDiagram` ("Arrow Cycle") draws 2-6 curved arrow segments (or plain segments, puzzle pieces, bumpers) arranged
in a ring, numbered/lettered in the ring, with each item's text listed in a column to the right of the ring or split
on both sides, and an optional text in the ring's center. It is the root element of template `cycle_diagram`. Its
item class `CycleDiagramItem` is documented here. The ring shapes themselves are computed; items only carry text.

## Model location

- `states[0].primary` - the diagram (root of `cycle_diagram`).
- `states[0].primary.items[]` - one `CycleDiagramItem` per ring segment (array order = clockwise order from
  `startAngle`).
- `states[0].primary.centerText` - the center text (`{ blocks }`), used when `showCenterText` is `true`.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Continuous improvement", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "style": "arrow2",
    "columns": "right",
    "labelType": "number",
    "innerRadius": 0.5,
    "showShadowEffect": true,
    "showCenterText": true,
    "centerText": { "blocks": [{ "html": "PDCA", "type": "text", "textStyle": "title" }] },
    "items": [
      { "text": { "blocks": [{ "html": "Plan", "type": "text", "textStyle": "title" }, { "html": "Set goals and hypotheses", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Do", "type": "text", "textStyle": "title" }, { "html": "Run the experiment", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Check", "type": "text", "textStyle": "title" }, { "html": "Measure the outcome", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Act", "type": "text", "textStyle": "title" }, { "html": "Standardize or adjust", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

## Pitfalls

- A 7th item is silently dropped; split the content or use `step_circular`/`step_chevrons` for longer cycles.
- Writing `startAngle` pins the rotation; omit it (or set `null`) to get the per-count default that makes the ring
  look balanced.
- `centerText` without `showCenterText: true` is ignored; `showCenterText: true` with a missing `centerText`
  renders an empty editable text in the ring.
- The text does not sit on the segments: it is a list beside the ring; the only link is the number/letter marker.
  Setting `labelType: "none"` removes that link, so keep markers unless the order is obvious.
- `columns: "split"` uses fixed slot positions per item count (2-6); more items than slots stack on the last slot.
- Only `columns`, `style`, `labelType`, `innerRadius`, `startAngle`, `showShadowEffect`, `showCenterText` are
  options; `textLayout`, `ornament`, `decorationStyle` do nothing here.

## Rules and limits

- `minItemCount` 2, `maxItemCount` 6 (hard: excess items are sliced off before build).
- Ring size: outer radius = `min(width - columns * (300 + gap), height) / 2`; the text column(s) get the rest
  (`MIN_COLUMN_WIDTH` 300px, column gap 50px, row gap 30px).
- Segment arc = `360 / itemCount` degrees each, drawn clockwise from `startAngle`.
- Import from other templates: a "target"/hub node becomes `centerText` (+ `showCenterText: true`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 2-6 items (`defaultData`: `[{}, {}, {}, {}]`) | Segments. More than 6 are **cut** to the first 6 on build. |
| `style` | string | `"arrow2"` (default via schema), `"arrow1"`, `"segments"`, `"bumper"`, `"puzzle"` | Segment shape: curved arrows with a large (`arrow2`) or small (`arrow1`) head, plain arcs, bumper shapes, puzzle pieces. |
| `columns` | string | `"right"` (default via schema; code fallback `"split"`), `"split"`, `"left"` (not in the UI) | Text placement: one column right of the ring, items split left/right of the ring (predefined positions per item count), or one column on the left. |
| `labelType` | string | `"number"` (default), `"letter"`, `"none"` | Marker drawn on each segment and before each text item: 1,2,3 / A,B,C (computed from position) or nothing. |
| `showCenterText` | boolean | default `false` | Shows `centerText` inside the ring (scaled to fit the inner circle). |
| `centerText` | object | `{ blocks }`, see `TextElement.md` | Center text; only read when `showCenterText` is `true`. |
| `innerRadius` | number | `0.1`-`0.66` (UI), default `0.5` via schema | Hole radius as a fraction of the outer radius (segment thickness = `1 - innerRadius`). For `"arrow2"` the hole is at least 50px. |
| `startAngle` | number | degrees, `0`-`360` in the UI; default depends on item count: 2 -> `90`, 3 -> `150`, 4 -> `-180`, 5 -> `198`, 6 -> `-180` | Angle (clockwise from 3 o'clock) at which the first segment starts. The UI resets it to `null` when items are added/removed so the per-count default applies again. |
| `showShadowEffect` | boolean | default `true` via schema | Drop shadow where each segment overlaps the previous one (`false` draws a 5px background-colored seam instead). |
| `collectionColor` | string | default `"theme"`; `defaultData` uses `"colorful"` | Segment colors (one accent per segment with `"colorful"`). Segments are always `"filled"`. On a colored slide background segments become white tints instead. |
| `animateRotation` | number | default `0` | Read by a getter but not used in layout/render. |

`textLayout` found in stored models (written by the generator) is not read.

#### items[] model (`CycleDiagramItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }` (`title_and_body`), see `TextElement.md` | Item text: a `title` block plus optional `body` blocks. In `"split"` layout the text is wrapped to the column width; in `"right"`/`"left"` it is auto-width. |
| `color` | string | palette color name | Override of the segment color (also tints the item's number marker). |
| `id` | string | generated when missing | |

`textWidth` and `decorationStyle` on stored items are not read by this element.

### Nested elements

- `items[]` -> `CycleDiagramItem` (2-6): `text` -> `TextElement.md` (scale-to-fit, synced, vertically centered) +
  `number` (non-editable `TextElement` with the computed 1/A marker, when `labelType != "none"`).
- `centerText` -> `TextElement.md` (scale-to-fit), when `showCenterText`.
- `labelText0..n` -> non-editable `TextElement`s drawn in white on each segment (when `labelType != "none"`).
