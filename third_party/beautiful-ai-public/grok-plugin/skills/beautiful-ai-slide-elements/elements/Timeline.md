# Timeline

Renders a horizontal timeline: a line (or a row of chevron/slice "spans") across the middle of the element, optional
start/end marker texts at both ends, and milestones placed above and below the line, each connected to the line by
a short connector with a dot. It is the root element of the `timeline` template (`states[0].primary`). Milestones are
callout-style nodes managed by an annotation layer (`TimelineAnnotations`, a subclass of `AnnotationLayer`, see
`CalloutsCanvas.md` for the shared annotation/callout concepts); the connectors are regenerated from the milestones on
every build, so an author only has to write the milestones.

The hidden `timeline2` template uses a different element (`Timeline2`) and is not covered here.

## Model location

- `states[0].primary` – the Timeline model (template `timeline`).
- `states[0].primary.annotations.items[]` – milestones (one `TextContentItem`-family node per entry).
- `states[0].primary.annotations.connections.items[]` – milestone connectors (generated, do not author).
- `states[0].primary.spans[]` – spans (`TimelineSpanItemContainer`), only when `spanStyle` is `"chevron"` or `"slice"`.
- `states[0].primary.startMarker.start_marker` / `states[0].primary.endMarker.end_marker` – marker texts (`TimelineMarker`).
- `states[0].header` – the slide header; only `headerPosition: "top"` is available, no tray layouts.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Our Supply Chain" }] }
  },
  "primary": {
    "showStartMarker": true,
    "showEndMarker": true,
    "startMarker": { "start_marker": { "blocks": [{ "type": "text", "textStyle": "body", "html": "2019" }] } },
    "endMarker": { "end_marker": { "blocks": [{ "type": "text", "textStyle": "body", "html": "2024" }] } },
    "autoPositionOnLoad": false,
    "annotations": {
      "collectionColor": "theme",
      "items": [
        {
          "id": "m1",
          "nodeType": "content-and-text",
          "x": 0.15, "y": 0.25,
          "content_type": "icon", "content_value": "lemon", "frameType": "theme",
          "text": { "blocks": [
            { "type": "text", "textStyle": "label", "html": "Q1 2019" },
            { "type": "text", "textStyle": "title", "html": "Buy lemons" }
          ] }
        },
        {
          "id": "m2",
          "nodeType": "content-and-text",
          "x": 0.45, "y": 0.75,
          "content_type": "icon", "content_value": "train", "frameType": "theme",
          "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Take lemons home" }] }
        },
        {
          "id": "m3",
          "nodeType": "content-and-text",
          "x": 0.75, "y": 0.25,
          "content_type": "icon", "content_value": "water-glass", "frameType": "theme",
          "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Make lemonade" }] }
        }
      ],
      "connections": { "items": [] }
    }
  }
}
```

The app's own generator uses `nodeType: "bullet-text"` for milestones without an icon, three blocks
(`label` date, `title`, `body` description), `x` from `0.1` in steps of `0.8 / count`, `y` alternating `0.25`/`0.65`,
and `showStartMarker`/`showEndMarker: false`.

## Pitfalls

- Do not author `annotations.connections`: it is rebuilt from the milestones each render (the generator's
  `annotations.connectors` key is simply ignored). Likewise do not write `annotations.items[].color` expecting the
  connector color to follow it: connector colors are reset to `null` and derived from the milestone.
- Omitting `autoPositionOnLoad` means `true`: your `x`/`y`/`textWidth` are overwritten on the first render. That is
  the easy path: give the milestones `x` in order (and `y` alternating `0.25`/`0.65` or none), keep
  `autoPositionOnLoad: true` and let the layout space them and size their text; it comes out right the first time
  for up to 6–8 milestones. Set `autoPositionOnLoad: false` only for positions you have placed deliberately.
- Milestones share one `nodeType` in the UI; mixing types works but switching the style in the editor rewrites all of
  them. `frameType` only applies to `"content-and-text"`.
- A `"text"` milestone with `y: 0.5` counts as the bottom row (`>= 0.5`); use clearly distinct values (`0.25`/`0.75`).
- Text that cannot fit between its row edge and the line is scaled down, not clipped; long bodies on many milestones
  end up tiny. Keep 1–2 short blocks per milestone and no more than ~6–8 milestones per row.
- `spanStyle` other than `"line"` needs at least one entry in `spans`, each with a `label`; without spans the element
  silently falls back to a line.
- `startMarker.start_marker` and `endMarker.end_marker` are nested one level deeper than the flags
  (`startMarker: { start_marker: {...} }`), not `startMarker: { blocks }`.
- Stored examples contain layout cache on blocks (`blockBounds`, `textStyles`, …) and node cache
  (`aoi*`, `assetWidth`, `scale`, `version`); none of it is authored.

## Rules and limits

- Max 20 milestones, max 10 spans (enforced by the editor's add actions; the element does not clamp authored arrays).
- `x`/`y` are fractions (0–1) of the annotation layer, which is the element minus the marker squares at the ends.
  Nodes are not constrained to the bounds; values outside 0–1 render off-element.
- Layout passes (every render): a milestone whose text would cross the line is moved to the edge of its row and, if it
  still does not fit, gets `maxMilestoneHeight` so its text scales down; all milestones in a row are re-aligned to the
  same `y`. These passes mutate `annotations.items[].y`.
- Auto layout (`autoPositionOnLoad: true` or after adding a milestone in the editor, and only if no milestone has
  `hasBeenDragged: true`): sorts by `x`, spreads milestones evenly, alternates rows (`0.25`/`0.75`, swapped when
  `reversed`), computes `textWidth` so neighbours do not overlap (single milestone: 50% of width), and resets
  `isNew`/`hasBeenDragged`/`autoTextWidthManaged`.
- `spanStyle: "line"` deletes `spans` (`this.model.spans = []`). Deleting the last span in the editor switches
  `spanStyle` back to `"line"`.
- `showStartMarker` / `showEndMarker` shrink the timeline by one marker square on that side and add 50px canvas margin.
- The editor only offers the block styles `"title"`, `"body"`, `"label"`, `"bulleted"` for milestone text (other
  styles are not verified to render correctly); connectors always end on the line (or on the top/bottom edge of the
  spans) with a theme-sized dot.
- Migrations: `_migrate_10` converts the V1 model (`items[]` with `title`, `body`, `content_type`, `content_value`,
  `x`, `y`, `hasBeenDragged`; `showContent` selecting icon milestones) into `annotations.items[]` (`nodeType`
  `"content-and-text"` when `showContent`, else `"text"`; missing `x` spread by index, missing `y` alternating
  `0.25`/`0.75`) and deletes `items`. `_migrate_10_02` sets `color` from the slide color (`"colorful"` becomes
  `"theme"`; `"primary"` is copied onto every milestone `color`). 13 of the 30 stored examples still carry
  `version: 1` milestones (`title`/`body` objects next to `text`); the current element reads only `text`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `annotations` (required) | object | `{ items: [], connections: { items: [] }, collectionColor: "theme" }` | Milestone layer. Created empty if absent, but a timeline without milestones is pointless. |
| `annotations.items[]` | array | see "annotations.items[] model" | Milestones (max 20). |
| `annotations.collectionColor` | string | palette color, default `"theme"` | Color of milestone markers/frames and connector dots (`"theme"`, `"colorful"`, `"accent1"`…, `"primary"`). |
| `annotations.decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"` | Decoration style of milestone markers (only meaningful for non-text node types). |
| `showStartMarker` | boolean | default `false` (template default `true`) | Shows the start marker text at the left end. |
| `showEndMarker` | boolean | default `false` (template default `true`) | Shows the end marker text at the right end. |
| `startMarker` | object | `{ start_marker: <text> }` | Text of the start marker; `<text>` is `{ blocks: [...] }` (see `TextElement.md`) or the legacy `{ text: "Start" }` / plain string which the text element converts to one `"body"` block. |
| `endMarker` | object | `{ end_marker: <text> }` | Same for the end marker. |
| `spanStyle` | string | `"line"` (default), `"chevron"`, `"slice"` | `"line"` draws a plain line and **clears `spans`**. Any other value renders `spans[]`; if `spans` is empty the style falls back to `"line"`. |
| `spans[]` | array | default `[]`, max 10 | Span segments, see "spans[] model". |
| `collectionColor` | string | palette color, default `"theme"` | Color set of the spans (the span collection shares the root model). |
| `reversed` | boolean | default `false` | Only when spans exist: auto layout puts the first milestone below the line instead of above. |
| `color` | string | palette color, default `"theme"` | Color of the line and of the start/end marker decorations. |
| `lineWidth` | number | px, default theme connector stroke width | Stroke width of the line when `spanStyle` is `"line"`. |
| `autoPositionOnLoad` | boolean | default `true` (schema) | When true, the element runs its auto layout once on the next render (distributes milestones, assigns `textWidth`, alternates rows) and then sets the flag to `false`. Set it to `false` when you author explicit `x`/`y`. |
| `fit`, `scale`, `scroll`, `showContent`, `timeline_start`, `timeline_end`, `items` | – | legacy | Present in `defaultData` and old examples; not read by the current element except by the migration (`showContent`, `items`). |

Plus the common fields, see `BaseElement.md`.

#### annotations.items[] model (milestones)

Each milestone is a content item (class chosen from `nodeType`, see `ContentItem.md`; the `"text"` variant
`TextContentItem` is described in `TextElement.md`).

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` (required) | string | uuid | Identifies the milestone; connectors use `source: <id>` and `id: "from-<id>"`. Items without an id get one on build. |
| `nodeType` | string | `"text"` (default), `"bullet-text"`, `"numbered-text"`, `"lettered-text"`, `"content-and-text"` | Milestone style. `"text"` is a plain text block; the others add a marker (dot, number, letter, icon/image) left of the text. The editor applies one `nodeType` to all milestones. |
| `x` (required) | number | 0–1 | Horizontal position of the milestone anchor as a fraction of the timeline width (left to right). |
| `y` (required) | number | 0–1 | Vertical position as a fraction of the element height. `< 0.5` = above the line, `>= 0.5` = below. Auto layout uses `0.25` / `0.75` and then re-aligns each row. |
| `text` (required) | object | `{ blocks: [...] }` | Milestone text; see `TextElement.md`. Block `textStyle`s offered by the editor: `"title"`, `"body"`, `"label"`, `"bulleted"`. Text is left-aligned and placed to the right of the anchor (`textDirection` is forced to `"right"`). |
| `textWidth` | number or null | px, default `null` (auto, 200 when neither auto nor set) | Width of the text block. Auto layout assigns it (min 40) unless `autoTextWidthManaged` is `false`. |
| `content_type` / `content_value` | string | `"icon"` + icon key, `"image"` + asset id | Media for `"content-and-text"` milestones; see `ContentElement.md`. |
| `frameType` | string | `"theme"` (default for content-and-text), `"none"`, `"rect"`, `"circle"`, `"rounded_rect"`, `"octagon"` | Frame of the icon/image marker. Not used for other node types. |
| `size` | number | px 50–400 (clamped) | Marker size for `"content-and-text"`, `"numbered-text"`, `"lettered-text"` (bullet dots use the stylesheet size). |
| `color` | string | palette color | Per-milestone color override of `annotations.collectionColor`. |
| `hasBeenDragged` | boolean | default `false` | `true` marks the milestone as manually placed: auto layout is skipped entirely while any milestone has it set. |
| `autoTextWidthManaged` | boolean | default `true` | `false` means the user resized the text; auto layout keeps `textWidth`. |
| `hideNodeConnectorWidget` | boolean | `true` | Editor flag written by the app; harmless to omit. |
| `textDirection` | string | `"right"` | Written by the app; the element forces `"right"` anyway. |
| `isNew`, `maxMilestoneHeight`, `_checkTimelineConstraint` | – | internal | Layout scratch fields; do not author. |

#### annotations.connections.items[] (generated)

`_build` rewrites this array from `annotations.items` on every render: one connector per milestone with
`id: "from-<milestoneId>"`, `source: <milestoneId>`, `target: "<timeline path>/spans"` or `".../timeline"`,
`endPointIsLocked: true`, `canChangeConnectorType: false`, `startAnchor: "anchor-left"` for `"text"` milestones or
`"anchor-free"` otherwise, and `color: null`. Anything you write here is discarded.

#### spans[] model (`TimelineSpanItemContainer`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Item id (assigned if missing). |
| `label` | object | `{ blocks: [...] }` or `{ text: "..." }` | Text drawn inside the chevron/slice (`TextElement`, single block, scaled to fit). |
| `width` | number | relative weight, default `1` | Spans share the width proportionally to `width` (a span with `2` is twice as wide as one with `1`). Deleting `width` resets to equal widths. |
| `color`, `decorationStyle` | string | palette color / decoration style | Per-span overrides of the span collection color (`primary.collectionColor`). |

The shape is `TimelineSpanChevronItem` (arrow-shaped polygon, first span has a flat start) when `spanStyle` is
`"chevron"`, else `TimelineSpanSliceItem` (rounded rectangle). Both are internal and have no model of their own.

#### startMarker / endMarker (`TimelineMarker`)

`TimelineMarker` is a `TextElement` bound to `startMarker.start_marker` / `endMarker.end_marker`. It is a single
block with default `textStyle` `"body"`, scaled to fit a fixed square (theme `markerSize`), and gets a circular
decoration in the `color` of the timeline when `spanStyle` is `"line"` (no decoration with spans). Both markers sync
their font size.

### Nested elements

- `annotations` -> `TimelineAnnotations` (an `AnnotationLayer`, see `CalloutsCanvas.md`): `items[]` -> `TextContentItem`
  (`"text"`), `BulletTextContentItem`, `NumberedTextContentItem`, `LetteredTextContentItem` or `MediaAndTextContentItem`
  (`"content-and-text"`), see `ContentItem.md`. Min 0, max 20 items. Items are sorted by `x` for numbering, animation
  and layout; the array order itself does not matter.
- `annotations.connections` -> `ConnectorGroup.md` (generated `ConnectorItem`s).
- `timeline` -> `TimelineLine` (an `SVGPolylineElement`) when `spanStyle` is `"line"`; otherwise `spans` ->
  `TimelineSpans` (collection of `TimelineSpanItemContainer`, min 0, max 10, laid out left to right in array order).
- `start_marker` / `end_marker` -> `TimelineMarker` (`TextElement.md`), only when the corresponding `show*Marker` is true.
