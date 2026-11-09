# CompareValuesCollection

`CompareValuesCollection` is the shared base of the five "compare values" charts: a collection of items that each
carry one numeric `value` and a text block, drawn as circles (`CompareBubble`, template `compare_circles`),
horizontal bars (`CompareHorizontalBar`, `compare_horizontal_bars`), radial arcs (`CompareRadialBar`,
`compare_radial_bars`), columns (`CompareVerticalBar`, `compare_vertical_bars`) or icon grids
(`CompareVerticalPictograph`, `compare_vertical_pictograph`). It is never a root element itself; it defines the
common items model, the value range and the value formatting that the subclasses render. The item classes
`CompareValuesItem` (base of every item) and `CompareValuesItemLabel` (the computed value label) are described here
and have no doc of their own.

All five templates share the `variations: "compare"` group, so a stored model can be switched between them; the only
thing that tells them apart is `template_id` (which selects the root element class), not a field in `primary`.

## Model location

- `states[0].primary` - the collection (root of the five compare templates).
- `states[0].primary.items[]` - one `CompareValuesItem` subclass per entry.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [{ "html": "Market Size", "type": "text", "textStyle": "heading" }] }
  },
  "primary": {
    "collectionColor": "colorful",
    "format": "currency",
    "formatOptions": { "decimal": 1, "separator": true, "abbreviated": "upper", "currency": "$" },
    "minValue": 0,
    "maxValue": 134000000,
    "items": [
      { "value": 134000000, "text": { "blocks": [{ "html": "Total addressable market", "type": "text", "textStyle": "title" }] } },
      { "value": 51000000, "text": { "blocks": [{ "html": "Serviceable market", "type": "text", "textStyle": "title" }] } },
      { "value": 26700000, "text": { "blocks": [{ "html": "Obtainable market", "type": "text", "textStyle": "title" }, { "html": "Year 3 target", "type": "text", "textStyle": "body" }] } }
    ]
  }
}
```

(`template_id` decides which chart draws this: `compare_circles`, `compare_horizontal_bars`, `compare_radial_bars`,
`compare_vertical_bars` or `compare_vertical_pictograph`.)

## Pitfalls

- Forgetting `value` gives the item a random size on every build; `value: null` gives an empty shape. Always write a
  number.
- Percent values are plain numbers (`75` means 75%). Writing `0.75` with `format: "percent"` renders `0.75%` (the
  generator multiplies fractional inputs by 100 for this reason).
- `maxValue` smaller than the largest value is corrected automatically, but a `maxValue` much larger than the
  values makes everything tiny; when unsure set `minValue: 0` and `maxValue` = the largest value.
- Hiding values means `format: "none"`; `showValue: false` does nothing.
- `formatOptions` replaces the defaults as a whole (`model.formatOptions ?? defaults`): when you set it, include every
  key you rely on (at least `decimal`, `separator`, `abbreviated`, and `currency` for currency).
- Do not put the formatted value in `text`; the label is generated from `value`. Do not write `label` objects on items.
- `hilited` on more than one item de-emphasizes every other item; it is a spotlight, not a color.

## Rules and limits

- Relative size of an item = `(|value| - max(0, minValue)) / (maxValue - minValue)` (0-1). A value above `maxValue` is
  never clipped: `maxValue` is expanded to it on build. All items share one range.
- Negative values: `minValue` is expanded below zero; bars and columns are then drawn from a computed baseline
  (positive to one side, negative to the other). Circles, radial arcs and pictographs use `|value|` only.
- `maxValue == minValue` (e.g. one item with `value: 0` and `maxValue: 0`) divides by zero -> `NaN` sizes. Keep
  `maxValue > minValue`.
- At least one item must have a numeric `value`: the range computation takes the min/max over item values and
  throws (render error) when every value is `null`.
- Items beyond `maxItemCount` are not dropped by the renderer (only the UI/paste path refuses to add more); extra
  items are laid out anyway and may overflow or trigger the "does not fit" state.
- Import from another template (`_importFromSharedModel`) truncates to `maxItemCount` and gives value-less items a
  random 40-80 value.
- Text style: every item's `text` is `title_and_body`; a block without `textStyle` takes the structural default
  (`title` for the first block, `body` after).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1..`maxItemCount` objects (see the subclass doc: 7 for bubble/bars/columns, 12 for radial, 4 for pictograph) | One item per compared value. An empty array is filled with one default item (`{ value: 50 }`). `null` entries are replaced by `{}` (which then gets a random value, see below). |
| `format` | string | `"percent"` (default), `"number"`, `"currency"`, `"none"` | How item values are rendered in the value label. `"none"` hides the labels entirely (no label element is built). Other `FormatType` values (`"text"`, `"date"`, `"icon"`) are not offered by the UI and are not meaningful here. |
| `formatOptions` | object | default `{ decimal: "auto", separator: true, abbreviated: false, changeStyle: "none", changeColor: true, currency: "$", dateFormat: "MMM Do", accountingStyle: false, textAlign: "center" }` | Number formatting. Useful keys: `decimal` (`"auto"` or an integer count), `separator` (thousands separator), `abbreviated` (`false`, `true`/`"lower"` -> `1.2m`, `"upper"` -> `1.2M`), `currency` (symbol, e.g. `"$"`, `"€"`), `scale` (`"thousands"`, `"millions"`, `"billions"`, `"trillions"`: multiplies the value before formatting, used for number/currency). |
| `minValue` | number | default `0` | Lower end of the value range. On every build it is **rewritten** to `min(minValue, smallest item value)`, so it can only grow downwards. |
| `maxValue` | number | default `100` | Upper end of the value range. On every build it is rewritten to `max(maxValue, largest item value)`: a too-small `maxValue` is silently expanded, a too-large one is kept and makes every item smaller. The UI "AutoFit" sets `minValue = 0`, `maxValue = largest value`. |
| `collectionColor` | string | palette color name, default `"theme"`; the generator uses `"colorful"` | Item color; with `"colorful"` each item gets the next palette accent. See `CollectionElement.md`. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Shape style of the bars/circles (not offered for radial bars and pictographs). |
| `scaling` | string | `"linear"` in every `defaultData` | Not read by the current code (a log scale was planned and is commented out). Safe to omit. |

Fields seen in stored models that the code does not read: `showValue`, `valuePosition` (on anything but the
pictograph), `labelFormat`, `userFontScale` (a text-scale cache), `scaling`.

#### items[] model (`CompareValuesItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` (required) | number | any finite number; percent values are authored as `0-100`, not `0-1` | The compared value. If the field is absent the item gets a **random** value in 0-100 (the schema default), so always set it. `null` stays `null` and renders as an empty/zero shape with a `0` label. |
| `text` | object | `{ blocks: [...] }`, see `TextElement.md`; structure `title_and_body` | The item's caption: first block `textStyle: "title"`, optional following blocks `textStyle: "body"`. Omit `text` for an unlabeled item. |
| `id` | string | any unique string; generated when missing | Item key; assigned on first build when absent, so it is not required for a new slide. |
| `color` | string | palette color name, default none (`"auto"` is migrated to `null`) | Per-item color override of `collectionColor`. |
| `hilited` | boolean | default `false` | Emphasizes this item and de-emphasizes its siblings (bars, columns and circles only; the pictograph and radial items have no emphasize control). |

The value label (`CompareValuesItemLabel`, a non-editable `TextElement`) is **computed** from `value` + `format` +
`formatOptions` through the collection's `formatValue()`; it has no model fields. `label` objects found on stored
items are legacy and ignored. Percent formatting divides the value by 100 (`50` -> `50%`); number/currency apply
`formatOptions.scale` then the format string.

### Nested elements

- `items[]` -> one `CompareBubbleItem` / `CompareHorizontalBarItem` / `CompareRadialBarItem` /
  `CompareVerticalBarItem` / `CompareVerticalPictographItem` per entry (chosen by the subclass). Items render in
  array order, left to right (top to bottom for horizontal bars).
- `items[].text` -> `TextElement.md` (`title_and_body`, auto height, font size synced across items).
- `items[].label` (computed) -> `CompareValuesItemLabel` (only when `format != "none"`).
- `minItemCount` is 1 (base `CollectionElement`), `maxItemCount` is 10 here and overridden per subclass.
