# Countdown

A live countdown (or count-up) to a target date and time, shown as three or four decorated two-digit tiles (days,
hours, minutes, optionally seconds) with an uppercase unit caption under each. The digits are computed from the
clock at render/playback time; nothing numeric is authored. Root element of the `countdown` template. Tiles are
`CountdownDigit` (with `CountdownValue` / `CountdownUnit` texts), documented here, no separate file.

## Model location

- `states[0].primary` – the `Countdown` model (root).

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Launch day" } ] }
  },
  "primary": {
    "date": "12/31/2026",
    "time": "05:00 PM",
    "direction": "down",
    "showSeconds": true,
    "collectionColor": "theme"
  }
}
```

## Pitfalls

- `date` and `time` are strings in US formats; ISO dates (`"2026-12-31"`) are not parsed reliably. Use `"MM/DD/YYYY"` and `"hh:mm AM/PM"`.
- Do not author digit values; they are derived from the current time at render.
- The captions always read DAYS / HOURS / MINUTES / SECONDS; `days.text` etc. do not relabel them.
- `frameType: "none"` removes the tiles' decoration and enlarges the digits; other frame types only change the shape.

## Rules and limits

- The element ticks every second while the slide is shown (not in thumbnails) and animations are disabled by default.
- A target in the past with `direction: "down"` shows 00 in every tile (negative durations are zeroed); use `direction: "up"` for elapsed time.
- Template flags: `allowHeader`, `allowFooter`, `allowColorful`; trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `date` (required) | string | `"M/D/YYYY"`, e.g. `"05/07/2026"` (the editor writes `MM/DD/YYYY`); defaultData = today + 10 days | Target date. |
| `time` (required) | string | `"h:mm A"`, e.g. `"05:00 PM"` | Target time of day, parsed together with `date` as `"M/D/YYYY H:mm a"` in the viewer's local time. |
| `direction` | string | `"down"` (default), `"up"` | Count down to the target (time remaining) or up from it (time elapsed). |
| `showSeconds` | boolean | defaultData `true` | Adds the seconds tile. |
| `frameType` | string | theme shape when absent; `"circle"`, `"rect"`, `"rounded_rect"`, `"octagon"`, `"none"` | Shape behind each digit tile (`"none"` = bare digits, drawn 1.4× larger). |
| `collectionColor` | string | `"theme"` (default; set from the slide color by migration) | Tile color, per `CollectionElement.md` (`"colorful"` = one color per tile). |
| `color` | string | `"theme"` (schema default) | Passed to the tiles; the tile decoration color comes from `collectionColor`. |
| `days`, `hours`, `minutes`, `seconds` | object | `{ "text": "Days" }` etc.; created from the unit name when missing or blank | Kept in the model and used for the slide's text summary, but the rendered caption is the unit name itself (uppercased by the theme), so changing these texts does not change the caption (verified in the digit build code). |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `days`, `hours`, `minutes`, (`seconds`) -> `CountdownDigit`, one per unit, laid out in a centered row sized to fit (gap 20px):
  - `value` -> `CountdownValue` (`TextElement.md`, computed two-digit number, max 999, framed by `frameType`).
  - `<unit>` -> `CountdownUnit` (`TextElement.md`, the unit caption).
