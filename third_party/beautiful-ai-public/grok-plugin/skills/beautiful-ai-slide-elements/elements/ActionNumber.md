# ActionNumber

`ActionNumber` renders one huge animated number (drawn as font glyph paths so it can count up / zoom in
during playback) with a short label and an optional rule line. It is the root element of the template
`action-number` ("Action Number"). The app's generator uses it for a dashboard with a single statistic.

## Model location

- `states[0].primary` – the `ActionNumber` model (also shared with its `number` and `label` children).
- `states[0].primary.label` – the label text object (`TextElement` with id `label`).
- `states[0].header` – optional header; the template default is `layout.headerPosition: "none"`, only
  `"top"` is available.

## Minimal example

Template `action-number` (generator shape, currency value with a bottom label):

```json
{
  "primary": {
    "value": 125000000,
    "format": "currency",
    "formatOptions": { "decimal": 0, "separator": true, "abbreviated": false, "currency": "$" },
    "labelPosition": "bottom",
    "showLine": true,
    "numberColor": "primary",
    "animationStyle": "count",
    "startValue": 0.9,
    "playOutroAnimation": true,
    "label": {
      "blocks": [
        { "id": "l1", "type": "text", "textStyle": "_use_styles_", "html": "Completed construction projects across commercial, residential and public sectors." }
      ]
    }
  }
}
```

## Pitfalls

- Omitting `format` renders a currency (`$50,000`), not a plain number; set `"number"` explicitly.
- Passing a string in `value` (`"14%"`) breaks formatting and the count animation; `value` must be numeric and
  `format`/`formatOptions` carry the presentation.
- Percent values are whole numbers (`14`, not `0.14`).
- `label.blocks[].textStyle` is ignored for styling (single-block element: the label style comes from the
  element); write `"_use_styles_"` or omit it, and do not expect `heading`/`body` to change the look.
- `labelPosition: "right"` with a long label leaves little room for the number; prefer `bottom` for sentences.
- `numberColor` equal to the slide background is silently replaced by `primary`.

## Rules and limits

- The number always fits: it is scaled to the available width, never wrapped. Very long values
  (`125000000` with separators) simply get smaller; use `formatOptions.abbreviated: true` to keep digits big.
- The label gets 75 % of the slide width (`top`/`bottom`), the number's width (`bottom_right`, from the last
  comma onward) or the remaining width (`right`); it auto-shrinks to fit the leftover height.
- `format: "percent"` divides by 100 before formatting, so `value: 99.3` with `formatOptions.decimal: 1`
  renders `99.3%`; `value: 0.993` would render `1%`.
- `decimal: "auto"` is resolved to the number of decimals of the formatted final value during the count
  animation so the digits do not jump.
- Template flags: `allowHeader: true` (`availableHeaderPositions: ["top"]`), no tray layouts,
  `canConvertToAuthoring: false`, `canSwitchTemplate: false`, `allowColorful: true`; default data only sets
  `layout.headerPosition: "none"`.
- The generator sets `layout.backgroundColor: "theme"` / `backgroundStyle: "backgroundColor"` and
  `startValue: 0.5` for values above 1000.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` (required) | number | schema default `50000` | The number. For `format: "percent"` give the percentage as a whole number (`14` renders `14%`); the element divides by 100 itself. |
| `format` | string | `"currency"` (default when absent), `"number"`, `"percent"`, `"date"`, `"none"`, `"text"` | Number format (`formatter`). Stored examples use `currency`, `number`, `percent`. |
| `formatOptions` | object | default `{ "decimal": "auto", "separator": true, "abbreviated": false, "changeStyle": "none", "changeColor": true, "currency": "$", "dateFormat": "MMM Do", "accountingStyle": false, "textAlign": "center" }` | Formatting details: `decimal` = number of decimals or `"auto"`, `separator` = thousands separator, `abbreviated` = `1.2M` style (also widens the gap to a right-side label), `currency` = symbol prefix. |
| `label` | text object | `{ "blocks": [ { "textStyle": "_use_styles_", "html": "..." } ] }`; default none | Caption next to/under the number. Single-block text styled by the element (body font, 40px base), auto width/height; several blocks are allowed but it is meant to be one short sentence. |
| `labelPosition` | string | `"bottom_right"` (default), `"bottom"`, `"top"`, `"right"` | Where the label sits relative to the number; also sets label alignment (`bottom_right` -> right-aligned, `bottom`/`top` -> centered, `right` -> left-aligned). |
| `showLine` | boolean | schema default `true` | Draws a thin rule between number and label (horizontal for bottom/top/bottom-right, vertical for right). |
| `numberColor` | string | palette color; schema default `"theme"` | Fill color of the digits (resolved against the background; falls back to `primary` if it equals the background). |
| `animationStyle` | string | `"count"` (schema default), `"zoom"`, `"slide"`, `"scroll"`, `"multi-zoom"` | Entrance animation in playback. `"count"` counts from `value × startValue` up to `value`. |
| `startValue` | number | `0`–`1`; schema default `0.9` | Fraction of `value` the count animation starts from (`0.9` = starts at 90 %, `0` = from zero). |
| `playOutroAnimation` | boolean | schema default `true` | Zoom/fade the number and label out when leaving the slide. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `number` -> `ActionNumberNumber` (shares the model). Reads `value`, `numberColor` and the parent's
  `format`/`formatOptions`; lays the formatted string out glyph by glyph with the theme header font (500px
  base, weight 900), currency symbol at half size, `%` in a thin weight, and scales the whole number down to
  fit the available width (1100px, 900px with a right-side label). No model fields of its own.
- `label` -> `TextElement` (`TextElement.md`), single block, auto width/height, newlines allowed.
- `line` -> `SVGPathElement`, only when `showLine`; stroke = `primary` at 50 % opacity. No model.
