# GanttChart

Renders a Gantt chart: one horizontal bar per task positioned on a time axis, optional vertical milestone lines with
labels above the bars, and a grid with date (or relative) labels along the bottom. It is the root element of the
`gantt_chart` template (`states[0].primary`). The time axis is derived from the tasks and milestones (earliest to
latest date, rounded to the `axisScale` unit); nothing about the axis is authored directly.

## Model location

- `states[0].primary` – the chart (template `gantt_chart`).
- `states[0].primary.items[]` – tasks (`GanttChartTask`).
- `states[0].primary.milestones[]` – milestones (`GanttChartMilestone`).
- `states[0].header` – header; tray layouts as the template allows; colorful backgrounds disabled.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Launch plan" }] } },
  "primary": {
    "isNormalized": true,
    "showGrid": true,
    "showTaskDetail": "duration",
    "axisScale": "weeks",
    "items": [
      { "startDate": 1767225600000, "endDate": 1768435200000,
        "title": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Research" }] } },
      { "startDate": 1768435200000, "endDate": 1770249600000,
        "title": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Design" }] }, "color": "accent2" },
      { "startDate": 1770249600000, "endDate": 1772668800000,
        "title": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Build" }] } }
    ],
    "milestones": [
      { "date": 1772668800000, "flipLabel": false,
        "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Launch" }] } }
    ]
  }
}
```

(Timestamps above are `Date.UTC(2026, 0, 1)`, `Date.UTC(2026, 0, 15)`, `Date.UTC(2026, 1, 5)`, `Date.UTC(2026, 2, 5)`.)
The app's generator writes `startDate` at 00:00 and `endDate` at 23:59:59.999 UTC of the respective days,
`title` as a single `"_use_styles_"` block, and at most 6 milestones built from task due dates.

## Pitfalls

- Forgetting `isNormalized: true` shifts every date by the viewer's timezone offset on first render (and persists it).
- `startDate`/`endDate`/`date` must be numeric epoch milliseconds (not seconds, not strings).
- A task whose `endDate` precedes its `startDate` is silently turned into a one-day task.
- `showTaskDetail`/`showImage`/`collectionColor` live on the root model, not on a `tasks` object.
- `milestones` must be an array even when empty; the element creates it if missing, but `null` breaks `length`.
- Too many tasks for the height (roughly >12 with a header) degrade to tiny bars; split across slides.
- Choose `axisScale` to match the span: `"days"` on a year-long plan yields hundreds of ticks (most skipped) and the
  labels show every Nth day.

## Rules and limits

- Axis: start = earliest task start or milestone date, rounded down to the `axisScale` unit (not rounded when
  `relativeTimescale`); end = latest task end or milestone date, rounded up to the next unit, and at least 7 days
  after the start. Ticks that would be closer than 150px are skipped.
- Row height = min(55px, available / task count); below 35px the small style is used, below 27px the tiny style,
  below 14px the chart reports "does not fit". 18 tasks is the editor limit.
- Task text that does not fit inside its bar is placed to the right (or left) of the bar with an outline; when neither
  side has room it is scaled inside the bar.
- Milestones reserve space above the bars equal to the tallest label.
- Dates are plain numbers: strings or ISO dates are not parsed (they produce `NaN` positions).
- Migration note: there is no v10 migration; `isNormalized` is the only legacy switch and it rewrites all dates when
  missing or `false`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 18 | Tasks in row order (top to bottom), see "items[] model". |
| `isNormalized` (required) | boolean | set `true` | Legacy date fix: when falsy, **every** `startDate`/`endDate`/`date` is shifted by the browser's UTC offset on build and the flag is set. Always write `true` with UTC timestamps. |
| `milestones` | array | default `[]`, max 6 | Milestones, see "milestones[] model". |
| `axisScale` | string | `"days"` (default), `"weeks"`, `"months"`, `"quarters"`, `"years"` | Unit of the grid ticks/labels and of the axis rounding (start of week/month/quarter/year). |
| `relativeTimescale` | boolean | default `false` | Labels become `Day 1`, `Week 1`, `Month 1`… counted from the earliest date instead of calendar dates; `showTaskDetail: "dates"` is forced to `"duration"`. |
| `showGrid` | boolean | default `true` | Draws the vertical grid lines and the axis labels. |
| `showTaskDetail` | string | `"duration"` (default), `"dates"`, `"none"` | Small label at the end of each bar: `"12 days"`, `"Jan 3 to Jan 14"`, or nothing. |
| `showImage` | boolean | default `false` | Shows a circular icon/image at the start of each bar (`items[].content_*`). |
| `collectionColor` | string | palette color, default `"theme"` | Bar colors (`"colorful"` cycles per task). |

Plus the common fields, see `BaseElement.md`.

#### items[] model (`GanttChartTask`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `startDate` (required) | number | ms since epoch (UTC) | Start of the task; the element uses the start of that UTC day. |
| `endDate` (required) | number | ms since epoch (UTC) | End of the task; the element uses the end of that UTC day. If before `startDate` it is reset to `startDate` (same-day task) in the model. |
| `title` (required) | object | `{ blocks: [{ html }] }` | Task name (`TextElement.md`, single block, default style from the stylesheet; `"_use_styles_"` or `"title"` both work). Drawn inside the bar when it fits, otherwise right of the bar, otherwise left. |
| `content_type`, `content_value` | string | `"icon"` + key, `"image"` + asset id | Media shown in a white circle at the bar start when `showImage` is true (`ContentElement.md`). |
| `color` | string | palette color | Per-task bar color; bars are always filled. |
| `label` | string | legacy `""` | Present in the template default and old examples; not read. |

#### milestones[] model (`GanttChartMilestone`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Assigned if missing. |
| `date` (required) | number | ms since epoch (UTC) | Position of the vertical line. |
| `label` | object | `{ blocks: [{ html }] }` | Text above the line (`TextElement.md`, auto width, placeholder "Type Milestone"). |
| `flipLabel` | boolean | default `false` | Puts the label to the left of the line instead of the right. |

### Nested elements

- `tasks` -> `GanttChartTasks` (collection of `GanttChartTask`, bound to `items`, max 18): each task has `title` ->
  `TextElement.md`, optional `label` (generated detail text, not authored) and optional `content` -> `ContentElement.md`.
- `milestones` -> `GanttChartMilestones` (collection bound to `milestones`, min 0, max 6; only built when the array
  is non-empty): each has `label` -> `TextElement.md` and an SVG line.
- `grid` -> `GanttChartGrid` (`GanttChartGridLines` + `GanttChartGridLabels`, no model), only when `showGrid`.
