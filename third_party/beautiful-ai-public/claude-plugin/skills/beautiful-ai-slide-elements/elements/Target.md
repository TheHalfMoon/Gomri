# Target

Concentric rings (bands) drawn from the center outwards, each band split into one or more equal arc segments, with
optional labels drawn inside the arc or attached as callouts in an annotation layer. Root element of the `target`
template. Bands are `TargetBand`, segments `TargetBandSegment`, the callout layer `TargetAnnotations` (a
`CalloutsCanvas.md`); all documented here, no separate files.

## Model location

- `states[0].primary` – the `Target` model (root).
- `states[0].primary.items[]` – one `TargetBand` per ring, innermost first.
- `states[0].primary.items[].segments[]` – the `TargetBandSegment` models of a ring.
- `states[0].primary.annotations` – the `TargetAnnotations` callouts model (`{ "items": [...], "connections": { "items": [...] } }`), see `CalloutsCanvas.md`.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "2026 customer targets" } ] }
  },
  "primary": {
    "position": "center",
    "innerRadius": 0,
    "outerRadius": 100,
    "collectionColor": "colorful-to-light",
    "annotations": { "items": [], "connections": { "items": [] } },
    "items": [
      { "segments": [ { "labelType": "inside", "label": "Core" } ] },
      { "segments": [ { "labelType": "inside", "label": "Early adopters" } ] },
      { "segments": [
        { "labelType": "inside", "label": "SMB" },
        { "labelType": "inside", "label": "Mid-market" },
        { "labelType": "inside", "label": "Enterprise" }
      ] }
    ]
  }
}
```

## Pitfalls

- `segments[].label` is a plain string; an object (`{ "blocks": [...] }`) is not a valid SVG text child and breaks the render. Use `labelType: "callout"` with an annotation when you need rich text.
- A segment without `labelType: "inside"` shows no label even if `label` is set (default `labelType` is `"none"`).
- Labels are drawn on the arc of their segment: long labels on small inner rings or on rings split into many segments overflow; keep them short.
- `items` order is inner → outer; the first item is the bullseye.
- When authoring callouts, give rings explicit `id`s first: the connector `target` path embeds the ring id and the segment index.

## Rules and limits

- The hole never eats into the 50px each ring needs: `innerRadius` is a % of (outer radius − 50px × ring count), and the hole is 0 when that is not positive.
- All segments of a ring have the same arc length (360° / count), starting at the top and going clockwise; a single segment is a full ring.
- Deleting a ring also deletes the annotation connected to it.
- Callout labels: the editor creates a `bullet-text` callout with `text.blocks[0]` = the label, placed ~150px outside the ring, and a connector `{ "source": <callout id>, "target": "/primary/<bandId>/segment<i>", "endDecoration": "circle", "connectorType": "angle" }`. To author one yourself set the ring `id`, set the segment `labelType: "callout"`, and add both the callout and the connector; see `CalloutsCanvas.md` for the callout fields.
- Migration: slides older than v8 had their target callouts in the slide-level annotation layer; they were moved into `primary.annotations`. Stored examples still contain legacy callout items (`nodeType`, `x`/`y` as 0–1 fractions) which the callouts canvas converts to the current px model at load.
- Template flags: `allowColorBackgrounds: false`; header and trays allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–6 objects | Rings, index 0 = center, last = outer ring. |
| `position` | string | `"center"` (default), `"left"`, `"right"` | Where the target sits horizontally in the element. |
| `outerRadius` | number | 0–100, default `100` | Outer radius as % of half the smaller element dimension. |
| `innerRadius` | number | 0–100, default `0` | Radius of the empty hole in the center, as % of the maximum hole (outer radius minus 50px per ring). `0` = solid bullseye. |
| `annotations` | object | `{ "items": [], "connections": { "items": [] } }` created if missing | Callouts and the connectors that tie them to segments, `CalloutsCanvas.md`. Connectors cannot be added/deleted freely by the user here; they are created with `labelType: "callout"`. |
| `collectionColor` | string | `"theme"` (default); template defaultData `"colorful"`; the app's generator uses `"colorful-to-light"` | Segment colors, per `CollectionElement.md`; with a single color per ring, rings are shaded by index. |

Decoration style is forced to `"filled"`. Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (TargetBand)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing; set it yourself when you add callouts | Ring key; also part of the connector target path `/primary/<bandId>/segment<i>`. |
| `segments` (required) | array | 1–8 objects (editor range); schema default `[{}]` | Equal arc segments, clockwise from 12 o'clock. |

#### items[].segments[] model (TargetBandSegment)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `color` | string | palette color or `null` (default: collection color for this ring) | Fill of this segment. `"auto"` is migrated to `null`. |
| `labelType` | string | `"none"` (default), `"inside"`, `"callout"` | `"inside"`: draws `label` along the arc (centered text for a full inner disc). `"callout"`: the label lives in an annotation connected to this segment. |
| `label` | string | plain text; `"Double-click to edit"` placeholder when empty | The in-arc label. A plain string, not a `{ blocks }` object. |

### Nested elements

- `items[]` -> `TargetBand`; min 1, max 6 (`maxItemCount`); order = inner to outer. Band width = (outer − inner radius) / band count.
  - `segment<i>` -> `TargetBandSegment` (one per `segments[]` entry): `path` -> SVG arc; `label` -> SVG text on a path when `labelType` is `"inside"`.
- `annotations` -> `TargetAnnotations` (`CalloutsCanvas.md`, layered above the rings). Its `items[]` are callout elements (`type: "callout"`, `calloutType`, `x`/`y` in px of the primary element, `text.blocks`, `color`, ...), its `connections.items[]` connectors with `source: <callout id>` and `target: "/primary/<bandId>/segment<i>"`.
