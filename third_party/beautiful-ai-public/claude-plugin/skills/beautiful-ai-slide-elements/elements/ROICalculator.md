# ROICalculator

An interactive ROI calculator: a column of labelled sliders (inputs) on the left and a column of computed results on
the right, each result being a formula over the input names, formatted as number/currency/percent. It is the root
element of the `roi_calculator` template (`states[0].primary`). Sliders work during playback; the formulas are
re-evaluated live, but moved slider values are not saved back to the model.

## Model location

- `states[0].primary` – the calculator (template `roi_calculator`).
- `states[0].primary.inputs[]` – sliders (`ROIInput`).
- `states[0].primary.calculations[]` – results (`ROICalculation`).
- `states[0].header` – header; tray layouts as the template allows.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "What could you save?" }] } },
  "primary": {
    "inputs": [
      { "name": "users", "label": "Number of users", "min": 0, "max": 2000, "step": 1, "format": "number", "value": 50 },
      { "name": "hourly_cost", "label": "Hourly cost", "min": 0, "max": 300, "step": 1, "format": "currency", "value": 75 },
      { "name": "hours_spent", "label": "Hours spent per week", "min": 0, "max": 50, "step": 1, "format": "number", "value": 5 },
      { "name": "savings", "label": "Percent of time saved", "min": 0, "max": 100, "step": 1, "format": "percent", "value": 0.25 }
    ],
    "calculations": [
      { "label": "Savings per month", "formula": "users * hourly_cost * hours_spent * 4 * savings", "format": "currency", "text": "/month" },
      { "label": "Savings per year", "formula": "users * hourly_cost * hours_spent * 52 * savings", "format": "currency", "text": "/year" }
    ]
  }
}
```

## Pitfalls

- `name` must be a valid identifier and every identifier in a `formula` must be an input `name`; a typo yields
  "Error parsing formula" for that result.
- Percent inputs mix units: `value: 0.25` but `min: 0, max: 100`. Writing `value: 25` shows 2500%.
- `label`/`text` are plain strings, not `{ blocks }` objects.
- Keep ≤5 inputs and ≤4 calculations; the element does not shrink rows to fit.
- Only `+ - * /` and parentheses are supported: `^`, `%` and function names (`pow`, `round`…) end as
  "Error parsing formula"; thousands separators are stripped (`1,000` evaluates as `1000`). Write `x * x` instead
  of `x^2` and `x / 100` instead of `x%`.

## Rules and limits

- Layout: both columns are `max(66% of width, 600px)` wide in total with an 80px gap, centred; items are vertically
  centred in their column. Rows are not scaled: more than ~5 inputs or 4 results overflow.
- Percent inputs: `value` is stored as a fraction, the slider and `min`/`max`/`step` operate in percent units
  (the element multiplies/divides by 100 when moving between them).
- Formulas are evaluated with `eval` after sanitizing to numeric expressions; function calls, strings and names
  that are not inputs cannot be used.
- Slider changes are kept in memory (`values`) for the open canvas only; the stored model keeps the initial `value`s.
- No migrations.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `inputs` (required) | array | min 1, max 5 | Sliders, top to bottom, see "inputs[] model". |
| `calculations` (required) | array | min 1, max 4 | Results, top to bottom, see "calculations[] model". |
| `collectionColor` | string | default `"theme"` | Written by the collections; sliders and values use the theme color regardless. |

Plus the common fields, see `BaseElement.md`.

#### inputs[] model (`ROIInput`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `name` (required) | string | identifier: letters, digits, `_`, not starting with a digit (`"users"`, `"hourly_cost"`) | Variable name referenced by formulas. Must be unique. |
| `label` (required) | string | plain text | Caption shown as `"<label>: <formatted value>"`. |
| `value` (required) | number | within `min`–`max`; for `"percent"` a fraction (`0.25` = 25%) | Initial slider value and the value used in formulas. |
| `min`, `max` (required) | number | slider range; for `"percent"` in percent units (`0`–`100`) | Slider bounds. |
| `step` | number | default none (continuous) | Slider step, in the same units as `min`/`max`. |
| `format` | string | `"number"`, `"currency"`, `"percent"` (`"text"`, `"date"`, `"icon"`, `"none"` exist but are meaningless here) | Display format of the value in the label. |
| `formatOptions` | object | formatter options: `decimal` (`"auto"` or digits), `separator` (bool), `abbreviated` (bool), `currency` (`"$"`), … | Overrides the default number formatting. |
| `id` | string | uuid | Assigned if missing. |

#### calculations[] model (`ROICalculation`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `label` (required) | string | plain text | Caption above the value. |
| `formula` (required) | string | arithmetic over input names: `+ - * /`, parentheses, numbers, `×`/`÷` accepted | Evaluated with each input's current value; identifiers are replaced by `(value)`, everything else except digits, `.`, operators, parentheses and whitespace is stripped. Any unknown identifier (or empty result) renders `"Error parsing formula"`. |
| `format` | string | `"number"`, `"currency"`, `"percent"` | Display format; `"percent"` multiplies the result by 100 for display (so formulas should produce fractions). |
| `formatOptions` | object | as for inputs | Formatting overrides. |
| `text` | string | e.g. `"/month"` | Suffix drawn after the value. |
| `id` | string | uuid | Assigned if missing. |

### Nested elements

- `inputs` -> `ROIInputs` (collection bound to `inputs`, max 5): each `ROIInput` has a read-only `label`
  `TextElement` and an HTML slider (30px tall).
- `calculations` -> `ROICalculations` (collection bound to `calculations`, max 4): each `ROICalculation` has
  read-only `label`, `value` and optional `text` `TextElement`s.
