# ArrowBars

A vertical stack of up to 5 horizontal arrow-shaped bars whose length is a 0–100 value, each carrying a single-line
label and an optional index number; an optional perspective "fold" on the left edge makes the bars look like they
emerge from the slide edge. Root element of the `arrow_bars` template. Items are `ArrowBarItem` (documented here, no
separate file).

## Model location

- `states[0].primary` – the `ArrowBars` model (root).
- `states[0].primary.items[]` – one `ArrowBarItem` per bar, top to bottom.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Our key demographics" } ] }
  },
  "primary": {
    "showIndex": true,
    "showFoldEffect": true,
    "arrowHeadStyle": "arrow",
    "collectionColor": "colorful",
    "items": [
      { "value": 82, "label": { "blocks": [ { "type": "text", "html": "Parents" } ] } },
      { "value": 69, "label": { "blocks": [ { "type": "text", "html": "3rd graders" } ] } },
      { "value": 57, "label": { "blocks": [ { "type": "text", "html": "4th graders" } ] } },
      { "value": 36, "hilited": true, "label": { "blocks": [ { "type": "text", "html": "Siblings" } ] } }
    ]
  }
}
```

## Pitfalls

- The label is `label`, not `text`; a `text` field on an item is ignored.
- Keep `label` to one short line: it must fit inside the bar at the given `value`, and a `value` of 0–15 leaves almost no room.
- More than 5 items: the editor and importer refuse; a hand-built model with 6+ bars renders but is marked as not fitting.
- `showArrowHead: false` silently overrides `arrowHeadStyle` with a square end; do not use it to hide arrow heads for the whole slide, set `arrowHeadStyle: "square"` instead.
- Left trays are not available for this template; use `"right_tray"` / `"right_inline"` or none.

## Rules and limits

- `value` is clamped to 0–100; the shared-model importer never sets it below 20. Values below ~15 leave no room for a label.
- With `showFoldEffect` the left canvas margin is 0 and a fold at least 120px wide is reserved, reducing the usable bar width.
- Template flags: header position `"top"` only; trays limited to `"right_tray"` and `"right_inline"`; `allowColorful`.
- Legacy: `label: { "text": "..." }` (no blocks) is still accepted and converted to a block at load.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–5 objects | One bar per entry. |
| `arrowHeadStyle` | string | `"arrow"` (default), `"triangle"`, `"rounded"`, `"square"` | Shape of the bar end. |
| `showIndex` | boolean | `true` (default) | Draws the 1-based item number at the left of each bar. |
| `showFoldEffect` | boolean | `true` (default) | Draws the perspective fold at the left edge and removes the left canvas margin. |
| `matchFontSizes` | boolean | `true` in the schema | Not read by the element (labels always sync their font size); harmless. |
| `collectionColor` | string | `"theme"` (default) | Bar color, per `CollectionElement.md`. |
| `decorationStyle` | string | theme default | `"outlined"` disables the darker fold shading. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (ArrowBarItem)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Item key. |
| `value` | number | 0–100 (clamped); `50` schema default, `75` for bars added in the editor; editor slider 15–100 | Bar length: 11.5% of the width at 0, 100% at 100 (linear). |
| `label` | object | `{ "blocks": [ { "type": "text", "html": "..." } ] }` | Single-block label drawn on the bar (`TextElement.md`); block `textStyle` may be omitted (`"_use_styles_"` in stored slides) or `"title"`. Text scales to fit the bar. |
| `showArrowHead` | boolean | `true` | Legacy flag: `false` forces a `"square"` end for this bar regardless of `arrowHeadStyle`. Leave `true` or omit. |
| `hilited` | boolean | `false` | Emphasizes this bar, de-emphasizes the others. |
| `color` | string | palette color or `null` | Overrides the collection color for this bar. |

### Nested elements

- `items[]` -> `ArrowBarItem`; min 1, max 5 (`maxItemCount`); order = array order, top to bottom.
  - `arrow` -> SVG path (the bar shape), `fold` -> SVG path (only when `showFoldEffect`).
  - `index` -> `TextElement.md` with the computed number (not authored), only when `showIndex`.
  - `label` -> `TextElement.md` bound to `item.label`, single block, scale-to-fit, font size synced across bars.
