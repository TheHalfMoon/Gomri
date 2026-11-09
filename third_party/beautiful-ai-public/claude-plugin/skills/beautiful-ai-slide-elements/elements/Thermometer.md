# Thermometer

A single vertical thermometer gauge (stem with optional bulb) filled to a 0–100 value, with a tick scale and tick
values on the left of the stem, a formatted current-value badge at the fluid top, and an annotation layer for
callouts connected to the gauge. Root element of the `thermometer` template. Nested classes documented here:
`ThermometerGauge` (the SVG gauge), `ThermometerTicks` (the scale), `ThermometerAnnotations` (a `CalloutsCanvas.md`).

## Model location

- `states[0].primary` – the `Thermometer` model (root).
- `states[0].primary.annotations` – the callouts model (`{ "items": [...], "connections": { "items": [...] } }`), see `CalloutsCanvas.md`.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Progress to goal" } ] }
  },
  "primary": {
    "value": 65,
    "targetMax": 100,
    "format": "percent",
    "tickCount": 5,
    "showTickValues": true,
    "showValue": true,
    "showBulb": true,
    "position": "center",
    "color": "theme",
    "annotations": { "items": [], "connections": { "items": [] } }
  }
}
```

## Pitfalls

- `value` is a percentage of the stem even when `format` is `"number"`/`"currency"`: for "13,000 of 20,000" send `value: 65`, `targetMax: 20000`, `format: "number"`.
- `tickCount: 1` divides by zero in the tick spacing; use 2–15.
- Every annotation needs its connector to `/primary/thermometerGauge`; a callout without one is not attached to the gauge (the editor's paste handler adds the missing connectors, hand-built models must include them).
- Annotation positioning: the stored examples carry legacy callouts (`nodeType`, `x`/`y` as 0–1 fractions) that are migrated at load, while the current callouts model stores `x`/`y` in px (`CalloutsCanvas.md`); the thermometer's side-alignment code still reads `x` as a fraction. How a freshly authored px `x` is treated is not verified: render and check the callout positions.
- `valuePosition` has no effect.

## Rules and limits

- `value` is not clamped by the element: keep it within 0–100 (the editor slider is 0–100; the editor rewrites `value` when `targetMax` changes so the displayed number stays the same).
- Tick values are `targetMax × (i / (tickCount − 1))` formatted with `format`.
- Annotations are pushed to the side of the gauge away from the ticks: with `position: "left"` to the right of the gauge, with `"right"` to the left of the ticks, centered: whichever side the callout is on. The element does this by rewriting the callout's `x` (treated there as a fraction of the annotation width).
- Migrations: v8 `items`/`connections` annotation lists were moved into `annotations`; 10.02 set `color` from the slide color.
- Template flags: `allowCallouts: true`; header and trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `value` (required) | number | 0–100; schema default `75`, defaultData `50` | Fill level in percent of the stem. `100` fills the stem to the very top. The displayed number is `value / 100 × targetMax`. |
| `targetMax` | number | default `100`; editor 1–99999999 | The number shown at the top tick and used to scale the displayed value (e.g. `value: 65`, `targetMax: 20000` shows 13,000). |
| `format` | string | `"percent"` (default), `"number"`, `"currency"` | Format of the value badge and tick values (percent divides by 100 first). |
| `formatOptions` | object | formatter options, default `{ "decimal": "auto", "separator": true, "abbreviated": false, ... }` | Number formatting. |
| `tickCount` | number | default `5`; editor 2–15 | Number of major ticks from `targetMax` (top) down to 0; minor ticks are added automatically when there is room. |
| `showTickValues` | boolean | `true` | Draw the numbers next to the major ticks. |
| `showValue` | boolean | `true` | Draw the current-value badge at the fluid top. |
| `showBulb` | boolean | `true` | Round bulb at the bottom (gauge width 120px) or a plain rounded stem (60px). |
| `position` | string | `"center"` (default), `"left"`, `"right"` | Horizontal placement of the gauge in the element. |
| `color` | string | palette color; `"theme"` default; stored slides also use `"auto"`, `"accent2"`, ... | Fluid color. |
| `annotations` | object | `{ "items": [], "connections": { "items": [] } }` created if missing | Callouts (max 11) tied to the gauge; see below and `CalloutsCanvas.md`. |
| `valuePosition` | string | `"fluidTop"` in defaultData and every stored slide | Not read by the layout (the badge is always at the fluid top); keep for compatibility. |

Plus the common fields, see `BaseElement.md`.

#### annotations model (ThermometerAnnotations)

A `CalloutsCanvas.md` spanning the full element width and the stem height. Each `items[]` entry is a callout
(`type: "callout"`, `calloutType` e.g. `"text"`, `"bullet-text"`, `"content-and-text"`, `text.blocks`, `x`, `y`, `color`;
text direction is automatic and cannot be changed). Each callout must have a connector in `connections.items[]`:
`{ "source": "<callout id>", "target": "/primary/thermometerGauge", "endPointIsLocked": true, "canChangeConnectorType": false }`
(the editor adds `connectorType: "straight"`, `endDecoration`, `lineStyle`, `lineWeight`). Connectors cannot be added
or deleted independently of their callout; their end point snaps to the stem edge at the callout's height.

### Nested elements

- `thermometerGauge` -> `ThermometerGauge`: SVG outline + clipped fluid rect; connector anchor for annotations.
- `thermometerTicksContainer` -> `ThermometerTicks`: SVG major/minor ticks and tick value texts (computed from `tickCount`, `targetMax`, `format`).
- `label` -> `ThermometerLabel` (`TextElement.md`, computed value text, white badge; when `showValue`).
- `annotations` -> `ThermometerAnnotations` (`CalloutsCanvas.md`, layer above the gauge).
