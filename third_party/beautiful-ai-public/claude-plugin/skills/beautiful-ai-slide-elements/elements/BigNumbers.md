# BigNumbers

`BigNumbers` renders up to eight "big number" tiles arranged in one or more centred rows: each tile is a label, a
large value, an optional change-in-value arrow with text, and an optional description line. It is the root element
(`states[0].primary`) of the `big-numbers` template. It is a `CollectionElement`; this file also covers the item
class `BigNumberItem` and its internal parts `BigNumberValue`, `BigNumberLabel`, `BigNumberChangeInValue` and
`BigNumberDescription`.

## Model location

- `states[0].primary` for `template_id: "big-numbers"`.
- Tiles: `states[0].primary.items[]`.

## Minimal example

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Key metrics" } ] } },
  "primary": {
    "layout": "fill",
    "collectionColor": "background_light",
    "items": [
      { "row": 0, "showLabel": true, "showChangeInValue": true, "showDescription": false, "positive": true,
        "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Revenue" } ] },
        "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "$4.2M" } ] },
        "changeLabel": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "18%" } ] } },
      { "row": 0, "showLabel": true, "showChangeInValue": true, "showDescription": false, "positive": false,
        "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Churn" } ] },
        "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "2.1%" } ] },
        "changeLabel": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "0.4 pt" } ] } },
      { "row": 1, "showLabel": true, "showChangeInValue": false, "showDescription": true,
        "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "Customers" } ] },
        "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "12,400" } ] },
        "text": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "across 38 countries" } ] } },
      { "row": 1, "showLabel": true, "showChangeInValue": false, "showDescription": true,
        "label": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "NPS" } ] },
        "value": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "62" } ] },
        "text": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "up from 54 last year" } ] } }
    ]
  }
}
```

## Pitfalls

- The description key is `text`, not `description`/`note`; `showDescription: true` with no `text` renders an
  empty line.
- `showChangeInValue` defaults to `true` through the schema: set it to `false` explicitly on tiles without a
  change, or every tile shows `100%` with an up arrow.
- Set `row` on every item; items without it all land in row 0 and may not fit (layout error).
- Keep values short: tiles are not individually shrunk, the whole row is, so one long value makes every tile
  small.
- Tile `color` overrides `collectionColor`; text colors are computed against the tile color, do not set font
  colors yourself.
- Stored examples carry `null` items and legacy `text`/`styles` strings; write only `blocks`.

## Rules and limits

- Rows: tiles are grouped by `row`; each row gets `(height - gaps) / rowCount` of the height and is laid out left
  to right with a 10 px gap, then centred; the block of rows is vertically centred.
- Each row is scaled as a whole (styles scale 0.1-1) until every tile's text fits and the row fits the width;
  when even the smallest scale does not fit, the slide reports a layout error (`isFit: false`). Long values or
  many tiles in one row trigger this.
- Minimum tile width 200 px; with `layout: "fill"` the tiles of a row are widened proportionally to fill the row.
- A tile's height is label + value (+ description); the change-in-value sits to the right of the value, vertically
  centred on it.
- Examples: 2-7 tiles, 1-3 rows; 4 tiles in 2 rows of 2 is the most common.
- Migration `_migrate_10_02` (stored `migrationVersion` < 10.02): derives `collectionColor` from the slide color
  (`"background_light"`/`"background_accent"` for neutral slides). Not run on models stored with `10.03`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` | array (required, 1-8) | see "items[] model" | The tiles. Order within a row = array order. |
| `layout` | string | `"fill"` or anything else (`"fit"`, absent) | `"fill"` stretches each row's tiles to the full width; otherwise tiles keep their natural width and the row is centred. |
| `collectionColor` | string | palette color name; schema default `"background_light"`; `"theme"`, `"colorful"`, `"collection-<id>"`, `"theme-to-dark"` in examples | Tile background for items without their own `color`. |
| `horizontalAlign` | string | schema default `"center"` (written) | Not used by the current layout (rows are always centred). |

Template `defaultData`: `layout.slideColor: "neutral"`, `layout.backgroundColor: "background_accent"`,
`layout.backgroundStyle: "backgroundAccent"`, and one item `{ showLabel: true, showChangeInValue: true,
showDescription: false, value: { text: "$50,000" }, label: { text: "My Statistic" }, changeLabel: { text: "100%" },
positive: true }`.

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (`BigNumberItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` | text object (required) | `{ "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "$50,000" } ] }`; schema default `{ "text": "$50,000" }` (converted to blocks) | The big number. Single line; not shrunk to fit (see rules). |
| `label` | text object | schema default `{ "text": "My Statistic" }` | Label above the value. Shown when `showLabel`. |
| `showLabel` | boolean | schema default `true` | Show `label`. |
| `showChangeInValue` | boolean | schema default `true` | Show the arrow + `changeLabel` to the right of the value. |
| `changeLabel` | text object | schema default `{ "text": "100%" }` | Change-in-value text (e.g. `"12%"`). |
| `positive` | boolean | schema default `true` | Up arrow in `"positive"` color vs down arrow in `"negative"` color. |
| `arrowColor` | string \| null | palette color name; default `null` = by `positive` | Arrow color override. |
| `showDescription` | boolean | schema default `false` | Show the description line under the value. |
| `text` | text object | default none | The description (the element is named `text`, hence the key). Shown when `showDescription`. |
| `row` | number | 0-based row index, default `0` | Which row the tile is in. Rows are renumbered contiguously at render (`[0, 2]` becomes `[0, 1]`). |
| `color` | string \| null | palette color name; default `null` = `collectionColor` | Tile background. |
| `decorationStyle` | string | schema default `"filled"` | Tile decoration (filled background). |
| `id` | string | generated when missing | Collection item id. |
| `accentColor`, `title` | – | legacy / stray | Not read by the item. |

Each text field is a `TextElement` (`TextElement.md`) with one block; `textStyle: "_use_styles_"` takes the
theme's big-number styling. Stored examples still carry `value.text` / `label.text` / `styles[]` next to `blocks`
with *different* content: only `blocks` is rendered.

### Nested elements

- `items[]` -> `BigNumberItem` (one per tile; `minItemCount` 1, `maxItemCount` 8, enforced on add/paste and by
  the shared-model import).
  - `label` -> `BigNumberLabel` (`TextElement`, key `label`, single line, font size synced across tiles).
  - `value` -> `BigNumberValue` (`TextElement`, key `value`, single line, synced).
  - `changeInValue` -> `BigNumberChangeInValue` (shares the item model): a 50 px icon
    (`arrow-up`/`arrow-down` by `positive`, colored `arrowColor` or positive/negative) and `changeLabel`
    (`TextElement`, key `changeLabel`, synced).
  - `text` -> `BigNumberDescription` (`TextElement`, key `text`, multi-line, synced).
