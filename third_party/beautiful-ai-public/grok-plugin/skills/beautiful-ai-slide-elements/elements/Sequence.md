# Sequence

`Sequence` renders a horizontal chain of 1-10 interlocking shapes (diamonds, gears, puzzle pieces, hexagons or arc
circles), each with a step ornament (number, letter, icon or free text) in or on the shape and the step text above
or below it, alternating by default. It is the root element of three templates that differ only in their
`defaultData`: `sequence` (`shapeType: "diamond"`), `gears` (`shapeType: "gear"`) and `puzzle` (`shapeType:
"puzzle"`, `labelType: "none"`). **The field that selects the shape is `primary.shapeType`**, not `template_id`:
stored `puzzle` slides with `shapeType: "hexagon"` or `"gear"` exist and render as such. Its item class
`SequenceItem` is documented here; `SequenceInputOutput` (input/output bars at both ends) exists in the code but is
disabled (`showInputOutput` always returns `false`), so `input`/`output` models are never read.

## Model location

- `states[0].primary` - the sequence (root of `sequence`, `gears`, `puzzle`).
- `states[0].primary.items[]` - one `SequenceItem` per shape, left to right.
- `states[0].primary.items[].text` - step text; `items[].ornament` - text ornament (`ornamentType: "text"`);
  `items[].content_type` / `content_value` - icon ornament (`ornamentType: "icon"`).

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Delivery pipeline", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "collectionColor": "colorful",
    "shapeType": "gear",
    "layout": "alternating",
    "showItemText": "alternate",
    "ornamentType": "number",
    "items": [
      { "text": { "blocks": [{ "html": "Plan", "type": "text", "textStyle": "title" }, { "html": "Scope and priorities", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Build", "type": "text", "textStyle": "title" }, { "html": "Implement and review", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Test", "type": "text", "textStyle": "title" }, { "html": "Automated and manual", "type": "text", "textStyle": "body" }] } },
      { "text": { "blocks": [{ "html": "Release", "type": "text", "textStyle": "title" }, { "html": "Ship to customers", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

With `ornamentType: "icon"` add `"content_type": "icon", "content_value": "<icon key>"` to each item; with
`ornamentType: "text"` add `"ornament": { "blocks": [{ "html": "Phase 1", "type": "text" }] }` instead.

## Pitfalls

- Set `shapeType` explicitly: when absent the code falls back to `"puzzle"` even on the `sequence`/`gears`
  templates (their `defaultData` sets it, a hand-written model may not).
- `labelType: "none"` does not hide the numbers; use `ornamentType: "none"`.
- `ornamentType: "text"` on puzzle pieces is ignored (renders no marker); pick `"number"`/`"letter"`/`"icon"` or
  another shape.
- `showItemText: "above"`/`"below"` with an alternating `layout` still works in code but is not offered by the UI;
  expect `"alternate"` behavior to be the one users see.
- Icons need `content_type: "icon"`; an empty `content_value` shows the "add icon" placeholder in the shape. Do not
  leave `__generateImage` on items you filled yourself (see `ContentElement.md`).
- Keep step text short: it is scaled down to fit the half-height band and cannot wrap outside its slot.

## Rules and limits

- `maxItemCount` 10 (`minItemCount` 1). Shape size = `min(slot width, 40% of height)` (50% with 1-2 items); the
  slot width is `(width - gaps) / (n - overlap * n + overlap)`, so 8-10 shapes get small.
- Step text gets the space above/below the shape (`height/2 - shape*3/4` in alternating layouts), is scaled to fit
  and can spill wider than the shape (1.4-1.7x for gears/hexagons/circles).
- With exactly 2 items and `showItemText != "none"`, texts are placed to the left of the first and right of the
  second shape, whatever placement `showItemText` names.
- Later items are layered under earlier ones (`layer = n - index`) so the first shape sits on top where they overlap.
- Import from other templates: main text -> `title` block, secondary texts -> `body` blocks, truncated to 10.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-10 items (`defaultData`: 5 for `sequence`/`gears`, 6 for `puzzle`) | Steps, left to right. |
| `shapeType` | string | `"diamond"`, `"gear"`, `"puzzle"`, `"hexagon"`, `"circle"`; code default `"puzzle"` when absent | Shape of every step. `"circle"` is an open arc ring (drawn progressively in animations); `"gear"` rotates continuously in the editor/player when `playAnimation` is on. |
| `layout` | string | `"alternating"` (default), `"alternating-flipped"`, `"straight"` | Odd/even shapes offset up/down (text on the opposite side), the same with the first step down, or all shapes on one line. |
| `showItemText` | string | `"alternate"` (default), `"none"`, `"above"`, `"below"` | Where `items[].text` goes. `"above"`/`"below"` are only offered for `layout: "straight"`; with 2 items the texts go left/right of the shapes instead. `"none"` builds no text element. |
| `ornamentType` | string | `"number"` (default), `"letter"`, `"icon"`, `"text"`, `"none"` | Marker on each shape: computed 1,2,3 / A,B,C; the item's icon (`content_type`/`content_value`); the item's `ornament` text; or nothing. For `shapeType: "puzzle"`, `"text"` is treated as `"none"`. Drawn centered in the shape (66% of it), or as a 40px circle on the shape's top/bottom edge for puzzle pieces. |
| `playAnimation` | boolean | default `true` via schema | Gear rotation on/off (gears only). |
| `collectionColor` | string | default `"colorful"` via schema | Shape colors (see `CollectionElement.md`). |
| `decorationStyle` | string | `"filled"` (default via schema), `"outlined"`, `"muted"`, `"fillAndStroke"` | Shape style; outlined/fillAndStroke add small gaps between gears/diamonds/hexagons. |
| `overlap` | number | `0`-`1`, default `0.3` | How much neighbouring shapes overlap; **overridden for every known `shapeType`** (gear 0.05 / -0.07 straight, puzzle 0.5 / 0, diamond 0.5 / 0.2, hexagon 0.25 / 0, circle 0.125 / 0), so effectively not an option. |
| `showInputOutput`, `input`, `output` | | | Disabled feature; not read. |

`labelType` (in the `puzzle` template's `defaultData` and in stored `puzzle` slides) is not read by this element;
the marker is controlled by `ornamentType`.

#### items[] model (`SequenceItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }` (`title_and_body`), see `TextElement.md` | Step text (title + optional body), scaled to fit the slot, font synced across steps. Not built when `showItemText` is `"none"`. |
| `ornament` | object | `{ blocks: [{ html, type: "text" }] }` (single block) | Free text drawn inside the shape when `ornamentType` is `"text"` (e.g. a short phase name). |
| `content_type`, `content_value` | string | `"icon"` + icon key (images get a circular frame), see `ContentElement.md` | The marker when `ornamentType` is `"icon"`; read by a `FramedMediaElement.md` built on the item model. `iconScale`, `flipHorizontal`, `mediaOpacity` from that element are honored. |
| `color` | string | palette color name | Per-step shape color (also tints an icon marker). |
| `decorationStyle` | string | | Per-step override of the shape style. |
| `id` | string | generated when missing | |

`frameType: "theme"` appears on stored items but is not read here.

### Nested elements

- `items[]` -> `SequenceItem` (1-10): `shape` (SVG path), optional `text` -> `TextElement.md`, optional `ornament`
  -> non-editable `TextElement` (number/letter), `FramedMediaElement.md` (icon) or editable `TextElement` (text).
  Circles and gears also get a `backShape` circle behind them (owned by the collection).
- `input` / `output` -> `SequenceInputOutput` (disabled).
