# Calendar

Renders either a month grid (weekday header row, one cell per day with the day number and an optional task text) or
a week board (one kanban-style column per day with task cards). It is the root element of both the `calendar-month`
and `calendar-week` templates (`states[0].primary`); the two templates differ only in the `calendarType` default.
The visible month/week is derived from `date`; day content is authored in a fixed 31-entry `days[]` array indexed by
day offset.

## Model location

- `states[0].primary` – the calendar (templates `calendar-month`, `calendar-week`).
- `states[0].primary.days[]` – 31 day entries (index 0 = first day of the month, or Sunday of the week).
- `states[0].primary.days[].task` – month cell text (`CalendarTaskText`, a `TextElement`).
- `states[0].primary.days[].items[]` – week day cards (`VerticalTaskElement`, see `VerticalTaskLists.md`).
- `states[0].header` – header; tray layouts as the template allows; color backgrounds allowed.

## Minimal example

Month (`calendar-month`):

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "June 2026" }] } },
  "primary": {
    "calendarType": "month",
    "date": "2026-06-01",
    "showWeekends": true,
    "startOnMonday": false,
    "showTitle": false,
    "days": [
      { "day": 0, "task": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Kickoff" }] }, "cellColor": "accent1" },
      { "day": 1 }, { "day": 2 }, { "day": 3 },
      { "day": 4, "task": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Design review" }] } },
      { "day": 5 }, { "day": 6 }, { "day": 7 }, { "day": 8 }, { "day": 9 }, { "day": 10 }, { "day": 11 }, { "day": 12 },
      { "day": 13 }, { "day": 14 }, { "day": 15 }, { "day": 16 }, { "day": 17 }, { "day": 18 }, { "day": 19 }, { "day": 20 },
      { "day": 21 }, { "day": 22 }, { "day": 23 }, { "day": 24 }, { "day": 25 }, { "day": 26 }, { "day": 27 }, { "day": 28 },
      { "day": 29 }, { "day": 30 }
    ]
  }
}
```

Week (`calendar-week`, `primary` only; `days[0]` is Sunday):

```json
{
  "calendarType": "week",
  "date": "2026-06-01",
  "showWeekends": false,
  "startOnMonday": false,
  "style": "box",
  "taskLayout": "stack",
  "days": [
    { "day": 0 },
    { "day": 1, "items": [ { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Sprint planning" }] } } ] },
    { "day": 2, "items": [] },
    { "day": 3, "items": [ { "text": { "blocks": [
        { "type": "text", "textStyle": "title", "html": "Customer call" },
        { "type": "text", "textStyle": "body", "html": "2 pm" } ] }, "icon": "star" } ] },
    { "day": 4, "items": [] },
    { "day": 5, "items": [ { "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Demo" }] } } ] },
    { "day": 6 }
  ]
}
```

(The app's generator always writes all 31 `days` entries as `{ day, text: "", label: {}, items: [] }` and fills
`task` or `items`; `date` as `YYYY-MM-DD`.)

## Pitfalls

- `days` is indexed by day offset, not by date: for a month view `days[0]` is the 1st of the month; for a week view
  `days[0]` is Sunday even when `showWeekends` is false (Mon–Fri are indices 1–5).
- Month cells read `task`, week columns read `items`; writing `items` on a month calendar (or `task` on a week one)
  shows nothing.
- Omit `showWeekends` and weekends disappear; set it explicitly.
- `date` strings in `MM/DD/YYYY` work but are locale-ambiguous in moment; prefer `YYYY-MM-DD`.
- Keep month cell text to a couple of words: the font size is shared by all cells and shrinks to the longest one.
- Week `label`s are regenerated from the date; do not try to rename columns.

## Rules and limits

- Month grid: columns = 7 (or 5 without weekends); rows = `ceil((firstWeekday + daysInMonth) / 7)`; cell size =
  available size / columns / rows, so a 6-row month gets short cells and long task text is scaled down.
- Only days that exist in the month are built; `days[28..30]` are ignored for short months.
- Week view columns are locked: they cannot be added/removed in the editor; cards can (min 0 per day).
- `showWeekends` must be written explicitly: the element reads the raw model value, so an absent flag hides weekends.
- Switching type in the editor re-maps content: month `task`s become week cards in order and vice versa.
- No migrations; legacy `task.text` strings are converted to blocks by the text element on first render.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calendarType` | string | `"month"` (default), `"week"` | Selects `MonthCalendar` or `WeekCalendar`. The template id only sets this default. |
| `date` (required) | string | any date string moment can parse: `"2026-06-01"`, `"05/01/2024"`, `"Mon Feb 01 2027"` | Anchor date. Month view uses the first of that month; week view uses the Sunday-based week containing it. Defaults to today when absent. |
| `days` | array | 31 objects, default `{ day: i, text: "" }` each | Per-day content, see "days[] model". Created empty if absent. |
| `showWeekends` (required) | boolean | template default `true`; **absent counts as false** | Month: show Sat/Sun columns; week: 7 columns instead of Mon–Fri. |
| `startOnMonday` | boolean | default `false` | Month view: week starts on Monday (header labels and column offset). Not applied to the week view (not verified). |
| `showTitle` | boolean | default `false` | Adds a read-only title above the grid: `"June 2026"` or `"Week of Jun 01"`. |
| `style` | string | week only: `"box"` (default), `"divider"`, `"no-frame"` | Column frame style of the week board (passed to the kanban). |
| `taskLayout` | string | week only: `"stack"` (default), `"fill"`, `"fit"` | Card height strategy of the week board (see `VerticalTaskLists.md`). |
| `showTimes` | boolean | – | Read by the week calendar but unused. |
| `cells`, `cols`, `rows`, `tableWidth`, `tableHeight`, `showColGridLines`, … | – | noise | Table fields left over in 3 stored month examples; ignored by the calendar. |

Plus the common fields, see `BaseElement.md`.

#### days[] model

Each entry describes one day by offset; the array always has 31 entries so that any month fits. Month view reads
`days[d]` for day `d` of the month (0-based); week view reads `days[0..6]` (Sunday..Saturday) or `days[1..5]`
(Mon..Fri when `showWeekends` is false).

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `day` | number | 0–30 | Day offset; written by the element, keep it equal to the index. |
| `task` | object | `{ blocks: [...] }` or legacy `{ text: "..." }` | Month view: the cell text (single block, centred, scaled to fit, font synced across cells). A cell renders text only when `task.blocks` is non-empty or `task.text` is non-empty. See `TextElement.md`. |
| `cellColor` | string | palette key or `"rgb(r,g,b)"`, default `"rgb(254,254,254)"`; weekends default `"rgb(230,230,230)"` | Month cell background. |
| `items` | array | default `[]` | Week view: cards of that day, each `{ id?, text: { blocks: [...] }, icon?, color? }` (`VerticalTaskElement`, see `VerticalTaskLists.md`). Max 20 cards per week on import. |
| `label` | – | overwritten | Week view writes the column title (`"Mon Jun 01"`) here on every build; authored values are ignored. |
| `text` | string | `""` | Legacy placeholder written by the element; unused. |
| `id`, `collectionColor`, `hilited`, `color`, `textAlign` | – | seen in examples | `collectionColor`/`color` on a week day act as the column's card color (kanban column model); `hilited`/`textAlign` are not read by the month cell. |

### Nested elements

- `calendar` -> `MonthCalendar` when `calendarType` is `"month"`: `header<0..6>` -> `CalendarHeader` (weekday label,
  read-only `TextElement`), `calendarCell<d>` -> `CalendarCell` per day of the month, each with `task` ->
  `CalendarTaskText` (`TextElement.md`) when it has text, and a day-number SVG label.
- `calendar` -> `WeekCalendar` when `"week"`: `board` -> `WeekCalenderVerticalTaskLists` (a locked-column
  `VerticalTaskLists`, see `VerticalTaskLists.md`) whose columns are `days[0..6]`.
- `title` -> `TextElement` (read-only) when `showTitle`.
