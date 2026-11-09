# Timer

A circular countdown timer: a ring track with a progress arc that empties over a fixed duration and an `mm:ss`
readout in the center, with an emphasized (glowing) phase for the last seconds and an optional auto-advance to the
next slide when it expires. The timer starts 1.5s after the slide is shown and counts in real time; nothing numeric
is authored beyond the duration. Root element of the `timer` template. The readout is `TimerLabel` (a computed,
non-editable `TextElement.md`), documented here, no separate file.

## Model location

- `states[0].primary` – the `Timer` model (root).

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [
      { "type": "text", "textStyle": "heading", "html": "Questions & open discussion" },
      { "type": "text", "textStyle": "body", "html": "Submit your questions while the clock runs" }
    ] }
  },
  "primary": {
    "duration": 600,
    "emphasize": 60,
    "autoAdvanceSlide": false,
    "color": "theme"
  }
}
```

## Pitfalls

- `duration` and `emphasize` are seconds, not minutes (`5` renders `00:05`).
- `emphasize` larger than `duration` keeps the arc in the emphasized style for the whole run.
- The readout cannot be authored; the only text on the slide is the header/tray.
- Static renders (thumbnails, exports) show the full duration and a full ring.

## Rules and limits

- The ring radius is 36.75% of the smaller element dimension; the arc ends are rounded when the theme shape is `circle` or `rounded_rect`.
- The readout is `floor(duration / 60)` minutes and `duration % 60` seconds; durations ≥ 3600s show minutes ≥ 60 (e.g. `90:00`).
- Changing `duration` in the editor restarts the timer; in thumbnails and when the slide is not current the timer is reset and does not run.
- Template flags: `allowHeader`, `allowFooter`, `allowColorful`; trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `duration` (required) | number | seconds; defaultData `300` (5 min); stored slides use 300, 600, 1500 | Total time; the readout starts at `mm:ss` of this value. |
| `emphasize` | number | seconds; defaultData `60` | When the remaining time is ≤ this value (and > 0) the progress arc switches to the emphasized style and pulses. `0` disables it. |
| `autoAdvanceSlide` | boolean | `false` | In playback, advance to the next slide ~2s after the timer reaches 0. |
| `color` | string | `"theme"` (schema default; set from the slide color by migration) | Palette color of the progress arc; the track uses the same color at 50% alpha. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `time` -> `TimerLabel` (`TextElement.md`, computed `mm:ss`, centered, not selectable/editable).
- `track`, `progress`, `glow` -> SVG paths (ring, progress arc, animated glow).
