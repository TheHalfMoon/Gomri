# Chart

`Chart` renders a Highcharts line / area / column / bar / waterfall chart (one or more series over a shared list of
categories) with optional legend, axis titles, data labels and point annotations. It is the `childElement` of a
`LayoutContainerItem` with `componentType: "Chart"` (templates `chart_line`, `chart_column`, `chart_bar`,
`chart_area`, `chart_waterfall` and any `dashboard` cell), and it is also the sparkline ornament of a `Statistic`
(`ornamentType: "sparkline"`, sharing the statistic's model). Pie charts are a different element: `PieChart.md`.

## Model location

- `states[0].primary.items[].childElement` of a `Dashboard` cell with `componentType: "Chart"` (or, legacy /
  app-generated, the fields directly on `states[0].primary.items[]` when `childElement` is absent).
- `states[0].primary.items[].childElement` of a `Statistic` cell when `ornamentType: "sparkline"` (the chart reads
  `chartData` from the statistic's own model).
- Annotations: `<chart model>.chartAnnotations`.

## Minimal example

Two-series line chart (as `items[].childElement`; wrap it in a `componentType: "Chart"` item):

```json
{
  "legendPosition": "bottom",
  "chartData": {
    "series": [
      { "id": "series1", "name": "Revenue", "type": "line", "colorName": "chart1", "marker": "none",
        "data": [ { "y": 120 }, { "y": 150 }, { "y": 180 }, { "y": 210 } ] },
      { "id": "series2", "name": "Costs", "type": "line", "colorName": "chart2", "marker": "none",
        "data": [ { "y": 90 }, { "y": 95 }, { "y": 110 }, { "y": 120 } ] }
    ],
    "xAxis": {
      "categories": [ "Q1", "Q2", "Q3", "Q4" ],
      "labels": { "enabled": true },
      "showAxisLine": true,
      "dateFormatting": "none",
      "axisTitle": false
    },
    "yAxis": {
      "labels": { "enabled": true },
      "showGridLines": true,
      "axisTitle": "none",
      "format": "currency",
      "formatOptions": { "decimal": 0, "separator": true, "abbreviated": "lower", "currency": "$" }
    },
    "yAxis2": { "visible": false, "opposite": true }
  },
  "chartAnnotations": { "items": [], "connections": { "items": [] } }
}
```

Waterfall (template `chart_waterfall`, one full-size cell with `cellColor: "none"`):

```json
{
  "legendPosition": "off",
  "chartData": {
    "series": [
      { "id": "series1", "name": "Cash", "type": "waterfall", "colorName": "chart1", "showDataLabels": true,
        "data": [ { "y": 1420000 }, { "y": 250000 }, { "y": -340000 }, { "y": "sum" }, { "y": -550000 }, { "y": "sum" } ] }
    ],
    "xAxis": {
      "categories": [ "Beginning cash", "Revenue", "Adjustments", "Net revenue", "Taxes", "Net income" ],
      "labels": { "enabled": true }, "showAxisLine": true, "axisTitle": false
    },
    "yAxis": {
      "labels": { "enabled": false }, "showGridLines": true, "showAxisLine": false, "axisTitle": "none",
      "format": "currency", "formatOptions": { "abbreviated": "lower", "currency": "$", "decimal": 0, "separator": true }
    },
    "yAxis2": { "visible": false, "opposite": true }
  }
}
```

## Pitfalls

- Forgetting `labels: { enabled: true }` on `xAxis`/`yAxis` hides the category names / values: labels are off
  when the key is absent.
- `yAxis2` must exist (`{ "visible": false, "opposite": true }`); a missing object throws during layout.
- Data longer than `categories` is silently cut; data shorter leaves blank categories. Mismatched lengths are
  the most common broken chart.
- `series[0].type` sets the chart kind. A `"waterfall"` first series makes the whole chart a waterfall; use
  `"column"` for ordinary bars and `"bar"` only for horizontal bars.
- Use `"sum"` points only in waterfall series; elsewhere non-numeric `y` becomes a gap.
- `legendPosition` absent means no legend, even with several series; set `"bottom"` or `"right"`.
- `yAxis.format: "percent"` multiplies the values by 100: write `{ "y": 0.114 }` for 11.4%, not `11.4` (which
  shows as 1140%). Only `Chart` takes fractions; the compare charts, statistics and pies take whole numbers
  (`CompareValuesCollection.md`).
- The axis reserves no extra room for the last category label: a long last label ("Starship (target)") clips at
  the cell's right edge while short ones (years) fit at 20 categories. Keep the last label short, or put the long
  name on a middle category.
- `xAxis.showGridLine` (singular, from the default model) does nothing; the real key is `showGridLines`.
- Copying stored examples: strip `dataLabels` on points, Highcharts-computed zone keys (`color`, `fillColor`,
  `dashStyle`, `translated`, `lineClip`), `null` series/annotation entries, and `pt` flags.
- Annotation `elementId`/`target` paths depend on the item `id`; let the build fix them but never leave them
  empty. A highlight pointing at a `pointIndex` that does not exist is removed.
- A pie/donut is not a `Chart` series type; use `componentType: "PieChart"` (`PieChart.md`).

## Rules and limits

- Invariant: `series[i].data.length <= xAxis.categories.length` for every series. Longer data is truncated at
  build; shorter data leaves the trailing categories empty. Author exactly one point per category.
- Every series needs a unique `id` and a `type`; a series without `data` gets `null` points.
- Waterfall mode (`series[0].type === "waterfall"`): one series; numeric points are increments (positive bars in
  `positiveBarColor`, negative in `negativeBarColor`), `{ "y": "sum" }` (case-insensitive) draws a running-total
  bar in `sumBarColor`; data labels are forced on and moved above bars shorter than 40 px; typically the last
  point is `"sum"`. The default waterfall model hides the y labels and formats as abbreviated currency.
- Stacked charts: put `stacking` on every series of the stack; the stacked animation is used only when
  `series[0].stacking` is set.
- `yAxis2` becomes visible iff some series has `yAxis: 1`; otherwise it is hidden regardless of its `visible`.
- Rendering uses a compact style when the chart area is under 640 x 300 px (most dashboard cells) and a
  horizontal style when any series is `"bar"`.
- Minimum content size 75 x 75 px; below that the cell renders empty (`LayoutContainerItem.md`).
- Sparkline mode (`Statistic` with `ornamentType: "sparkline"`): axes, legend and spacing are removed; only
  `chartData.series` and `xAxis.categories` matter. `chartData` lives on the statistic's model.
- Migrations at build (no `migrationVersion` needed): `annotations` object -> `chartAnnotations`;
  `xAxis.visible`/`yAxis.visible` `false` -> explicit off flags; annotation `elementId`s fixed; stale highlight
  annotations removed; connector anchor offsets recomputed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `chartData` | object (required) | absent -> the default sample line chart (8 months, one series) is written into the model | The data and axes, see below. |
| `legendPosition` | string | `"off"`, `"top"`, `"bottom"`, `"left"`, `"right"`, `"proximate"` (labels at the end of each line; falls back to `"right"` for bar charts); default absent = no legend | Legend placement. Use `"bottom"`/`"right"` for multi-series charts. |
| `legendReverse` | boolean | default `false` | Reverses the legend order. |
| `chartAnnotations` | object | `{ "items": [], "connections": { "items": [] } }` (created when absent) | Point highlights, notes and change-in-value connectors, see "Annotations". |
| `annotations` | object | legacy | Pre-10.02 name of `chartAnnotations`; migrated at build. Do not write. |
| `showLegend`, `showXAxis`, `showYAxis`, `showAxisLabels`, `showXGridLines`, `showYGridLines`, `groupData` | boolean | written by the default model | Legacy flags, not read by the renderer. Omit. |

#### `chartData`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `series` | array (required, >= 1) | | One entry per data series; `series[0].type` decides the chart kind (`"waterfall"` -> waterfall mode, otherwise a regular chart; a series with `type: "bar"` anywhere makes the chart horizontal). |
| `xAxis` | object (required) | | Category axis. `xAxis.categories` is required. |
| `yAxis` | object (required) | `{}` works | Primary value axis (left; right when `opposite: true`). |
| `yAxis2` | object (required) | `{ "visible": false, "opposite": true }` | Secondary value axis (right); shown automatically when some series has `yAxis: 1`, hidden otherwise. The object must exist even when unused. |
| `columnPadding` / `groupPadding` | number | default 0.1 / 0.1 | Highcharts `pointPadding` / `groupPadding` for column and bar charts (0-0.5). |
| `plotOptions` | object | default none | Merged into Highcharts `plotOptions` (advanced; the theme series styles win on conflict). |
| `positiveBarColor` / `negativeBarColor` / `sumBarColor` | string | palette color names; defaults `"positive"` / `"negative"` / the waterfall series `colorName` or `"theme"`; written into the model on first render | Waterfall bar colors. |
| `legend` | object | `{ "enabled": false }` in defaults | Not read; the legend is driven by `legendPosition`. |

#### `chartData.series[]`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string (required) | `"series1"`, `"series2"`, ... (must be unique within the chart) | Referenced by annotations, dynamic text values and data links. |
| `name` | string | default none (legend shows empty) | Legend label; also exported as the series name. |
| `type` | string (required) | `"line"`, `"area"`, `"areaspline"`, `"column"`, `"bar"` (horizontal), `"waterfall"` | Series type. Types may be mixed (e.g. columns plus a line) except waterfall, which should be the only series. |
| `data` | array | default: nulls, one per point of the first series that has data | Points in category order: `{ "y": <number> }`; `{ "y": null }` or `null` = missing value (gap in lines, empty slot in columns); `{ "y": "sum" }` = subtotal bar (waterfall only). Numeric strings are parsed; anything else becomes `null`. Optional per point: `color` (palette color name; column/bar only), `pt: true` (editor marker, no effect on rendering). Points beyond `xAxis.categories.length` are **dropped** at build. |
| `colorName` | string | palette color name (`"chart1"`…`"chart6"` roll over, `"theme"`, `"accent1"`…, CSS color) or `"auto"` (chart color by series index); default `"theme"` | Series color. |
| `marker` | string | `"none"` (default/absent), `"circle"`, `"square"`, `"diamond"`, `"triangle"`, `"triangle-down"` | Point markers (line/area). Marker radius follows `lineWidth`. |
| `lineWidth` | number | theme default | Line width in px (line/area); also the stroke of highlight annotations. |
| `showDataLabels` | boolean | default `false` (waterfall: always on) | Value labels on every point, formatted with the series' y axis `format`/`prefix`/`suffix`. |
| `stacking` | string | absent/`"none"` (default), `"normal"`, `"percent"` | Stack column/bar/area series. Set it on every stacked series; the animation only looks at `series[0]`. With `"percent"` data labels show percentages. |
| `yAxis` | number | `0` (default) or `1` | Bind the series to `yAxis` or `yAxis2`. |
| `zones` / `zoneAxis` | array / `"x"` | default `[{ "style": "default" }]` | Line-style zones along the x index: `{ "style": "default" \| "emphasized" \| "projection", "value": <x index where the zone ends, omit for the last zone> }` with `zoneAxis: "x"`. `"projection"` renders dashed/faded (forecast), `"emphasized"` uses the theme's emphasis style. Highcharts keys (`color`, `fillColor`, `dashStyle`) are recomputed; do not author them. |
| `greenRed` | boolean | legacy waterfall flag | Not read. |

#### `chartData.xAxis`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `categories` | string[] (required) | | Category labels, one per point. Empty strings are replaced by `"   "`; an empty array becomes `[""]`. |
| `labels` | object | `{ "enabled": true }`; **absent = labels hidden** | Show category labels. |
| `dateFormatting` | string | `"none"` (default) or a date format: `"MMM"`, `"MMM D"`, `"MMM Do"`, `"MMM YY"`, `"MMM YYYY"`, `"ll"`, `"LL"`, `"M/D"`, `"MM/DD/YY"`, `"M/D/YYYY"`, `"L"`, `"YYYY"`, `"YYYY-MM"`, `"YYYY-MM-DD"`, `"MM-DD-YYYY"`, `"MM.DD.YYYY"`, `"D MMM"`, `"Do MMM"`, `"Do MMM YYYY"`, `"D-MMM"` | Parse each category as a date and reformat it for display; categories that do not parse are shown as written. |
| `showAxisLine` | boolean | default `false` | Draw the axis line. |
| `showGridLines` | boolean | default `false` | Vertical grid lines (note: the default model writes `showGridLine`, singular, which is ignored). |
| `showMajorTicks` | boolean | default `false` | Tick marks. |
| `axisTitle` | `false` \| `"none"` \| `true` | default `false` | `true` shows `axisTitleText` under the axis; `false`/`"none"` hides it. |
| `axisTitleText` | string | default `"Value"` when `axisTitle` is on | Axis title. |
| `zeroAxisPadding` | boolean | default `false` | For line/area charts: start the first point on the axis edge instead of padding it. |
| `visible` | boolean | legacy | `false` is migrated at build into "everything off" (`labels.enabled: false`, no line/grid/ticks/title) and reset to `true`. |

Other keys found in stored models (`type`, `autoType`, `categoryType`, `labelInterval`, `showFirstLabel`,
`showLastLabel`, `endOnTick`, `showMinorTicks`, `dateSimple`, `dateFormat`, `dateInterval`) are defaults noise.
The whole axis object is merged into the Highcharts axis options, so recognised Highcharts keys do take effect.

#### `chartData.yAxis` and `chartData.yAxis2`

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `labels` | object | `{ "enabled": true }`; absent = hidden | Show value labels. |
| `format` | string | `"number"` (default), `"currency"`, `"percent"`, `"none"` (raw value) | Number format for axis labels and data labels. `"percent"` formats **fractions** (`0.5` -> `50%`); for data stored as `0-100` add `"labelFormat": "percent"`. |
| `formatOptions` | object | `{ "decimal": 0 \| 1 \| 2 \| "auto", "separator": true, "abbreviated": false \| true \| "lower" \| "upper", "currency": "$", "accountingStyle": false, "changeStyle": "none", "changeColor": true, "dateFormat": "MMM Do" }` | Formatter options; `abbreviated: "lower"` gives `1.2k/3m`, `"upper"` gives `1.2K/3M`. |
| `labelFormat` | string | `"ones"` (default), `"thousands"`, `"millions"`, `"billions"`, `"trillions"`, `"percent"` | Scales values before formatting (`"thousands"`: 12 -> 12,000; `"percent"`: divides by 100 so that `45` with `format: "percent"` shows `45%`). |
| `prefix` / `suffix` | string | default none | Text added before/after every axis label and data label (e.g. `"suffix": "%"`). |
| `min` / `max` / `tickAmount` | number or numeric string | default auto | Axis range and tick count. |
| `showGridLines` | boolean | default `false` | Horizontal grid lines (usually `true`). |
| `showAxisLine` | boolean | default `false` | Axis line. |
| `showMajorTicks` | boolean | default `false` | Tick marks. |
| `axisTitle` | string | `"none"` (default), `"edge"` (rotated along the axis), `"top"` (horizontal above the axis; adds 50 px top spacing) | Axis title placement. |
| `axisTitleText` | string | default `"Value"` | Axis title. |
| `opposite` | boolean | `yAxis`: default `false`; `yAxis2`: must be `true` | Put the axis on the right. |
| `visible` | boolean | `yAxis2`: managed automatically; `yAxis`: legacy `false` migrated like `xAxis.visible` | |
| `labelAbbreviation`, `labelCurrency` | – | defaults noise | Not read. |

### Nested elements

- `annotations` -> `ChartAnnotations` (model `chartAnnotations`), an `AnnotationLayer` (`CalloutsCanvas.md`)
  whose `items[]` are annotation nodes and whose `connections` is a `ConnectorGroup` (`ConnectorGroup.md`).
  Item class by `annotationType`: `"DataHilite"` -> `DataHiliteNodeElement` (below); `"DataNote"`,
  `"ChangeInValue"` and others -> the generic node classes of `AnnotationLayer`.
- The chart itself is a Highcharts instance; no other child elements.

#### Annotations

`chartAnnotations.items[]`:

- `DataHilite` – a circle drawn on one data point showing that point's formatted value (the point's normal data
  label is blanked). Model:
  `{ "id": "<unique>", "annotationType": "DataHilite", "nodeType": "circle", "dataSource": { "elementId": "<chart path>", "seriesId": "series1", "pointIndex": 3 }, "snapOptions": { same three keys }, "userSize": null, "decorationStyle": "outlined", "canDrag": false, "hideNodeConnectorWidget": true }`.
  `userSize` (px, default `null` = sized to the text at 20 px) sets the circle diameter; `decorationStyle`
  `"outlined"` (series-colored ring, stroke = series `lineWidth`, max 10) or `"filled"` (series-colored disc);
  optional `color` overrides the series color. `elementId` is rewritten to the chart's real path
  (`/primary/<item id>/element`) on every build, but it must be a non-empty string or the fix is skipped.
  A highlight whose series/point no longer exists (or whose `y` is `null`) is deleted at build.
- `DataNote` – a text box (`nodeType: "box"`, `x`/`y` as 0-1 fractions of the plot area, `text: { blocks }`,
  `decorationStyle`, `canDrag: true`) connected to a point by an entry of `chartAnnotations.connections.items[]`:
  `{ "id", "source": "<note id>", "target": "<chart path>", "targetSnapOptions": { "elementId", "seriesId", "pointIndex" }, "connectorType": "straight", "endDecoration": "circle", "startAnchor": "anchor-free", "endAnchor": "anchor-free", "lineStyle": "solid", "lineWeight": 2 }`.
  `targetSnapOptions` may instead be `{ "elementId", "axis": "xAxis" | "yAxis" }` to pin to an axis.
  Node shape fields are those of `CalloutsCanvas.md`; not verified beyond the stored examples.
- `ChangeInValue` – a connector between two points of one series whose label shows the change:
  `labels: [{ "dataSource": { "seriesId", "pointAIndex", "pointBIndex", "isDiff": true, "changeType": "percent" | "absolute" | "cagr" | "multiple" | "text" } }]`.
  Not verified beyond the code paths that compute the value.
- Any element's text can show a chart value dynamically through `dataSource: { "elementId", "seriesId", "pointIndex" }`
  (or the diff form above); see `TextElement.md`.
