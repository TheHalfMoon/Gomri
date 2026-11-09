# MediaAndTextCallout

`MediaAndTextCallout` is the `calloutType: "content-and-text"` callout: an icon, image, logo or video in a frame
(the marker) with a text block beside, above or below it. It extends `MarkerCallout` (`MarkerCallout.md`) and
replaces the dot with a `FramedMediaElement` (`FramedMediaElement.md`). It is the child of an
`AuthoringElementContainer` entry with `type: "callout"` on every callout host (flow chart, Classic, target,
thermometer, XY graph, timeline2) – see `CalloutElement.md` for the shared contract.

No stored examples exist; examples are built from the schema (`frameType: "theme"`, `markerSize: 75`) and the
editor's default model (`width: 200`, `height: 150`, `color: "theme"`, `textDirection: "auto"`).

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`flow_chart`, `authoring`, `xygraph`),
`states[0].primary.annotations.elements[]` (`target`, `thermometer`), `states[0].primary.milestones.elements[]`
(`timeline2`).

## Minimal example

`states[0].primary.elements[]` entry: a framed icon with its label to the right.

```json
{
  "id": "m1", "type": "callout", "calloutType": "content-and-text",
  "x": 300, "y": 240, "textWidth": 220, "textDirection": "right",
  "markerSize": 75, "frameType": "circle", "color": "theme",
  "content_type": "icon", "content_value": "rocket",
  "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Launch" }] }
}
```

An image marker: `"content_type": "image", "content_value": "<asset id>", "frameType": "rounded_rect"`.

## Pitfalls

- `markerSize` is the marker side, not the whole callout: the box becomes `markerSize + 15 + textWidth` wide.
- `width`/`height` are overwritten; use `markerSize` and `textWidth` to size it.
- `markerSize` below 50 is raised to 50; the layout does not cap large values (the editor stops at 400).
- `frameType` must be a real frame id (`FramedMediaElement.md`); `"theme"` follows the theme, which may be a
  circle on one theme and a square on another.
- `decorationStyle` only matters with a shape frame; a device frame or `"none"` ignores it.
- Do not leave a `__generateImage` object on an entry you fill yourself, and do not author `iconColor`.

## Rules and limits

- Marker size = `max(50, markerSize)` square; the frame then decides the drawn shape (square shape frames, device
  frames scaled into the square, unframed assets fitted by width).
- Layout and direction rules are those of `MarkerCallout.md` (the marker is centred on the first text line for
  side text).
- Connectors attach to the media marker's rectangle (connection shape `rect`, anchor bounds = marker). Default
  connector color = `color ?? collectionColor`.
- Editor: "Media Scale" slider writes `markerSize` (50–400); "Media Frame" writes `frameType` and may also rewrite
  `color` (picking a shape frame while `color` is a background color sets `color: "primary"`; picking a device frame
  while `color` is `"primary"`/`"secondary"` sets `"background_dark"`); double click on the marker opens the media
  picker; videos get the media property panel.
- The legacy `iconColor` is removed by migration 10.02; the 10.02 annotation migration maps the old `size` to
  `markerSize` and sets `width = text width + size + 40`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"content-and-text"` | – |
| `x`, `y` (required) | number | px | Centre of the media marker. |
| `content_type` | string | `"icon"` (default asset type), `"image"`, `"logo"`, `"video"` | Media kind (`ContentElement.md`). Without `content_value` the frame shows the empty-media placeholder. |
| `content_value` | string | icon key or asset id | The asset. |
| `markerSize` | number | px, default `75` (schema; theme value 70 is only used when the key is deleted); minimum 50; editor slider 50–400 | Side of the square media marker. No upper clamp in the layout. |
| `frameType` | string | `"theme"` (schema default = the theme's shape style), `"none"`, `"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`, device frame ids | Frame around the media (`FramedMediaElement.md`). Shape frames make the marker square; `"none"` shows the raw asset. |
| `color` | string or null | palette color, default `null` -> `collectionColor` | Frame fill/stroke (shape frames, per `decorationStyle`), device-frame screen color, and the icon color when unframed. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`; default theme | Honoured only with a shape frame (the editor shows the style picker only then). |
| `text`, `textWidth`, `textDirection` | – | as `MarkerCallout.md` | Text block (default style `"title"`, 20 px body size from the theme), its width (default 200), and its side (`"auto"` default). |
| `width`, `height` | number | px, written on every render | `markerSize + 15 + textWidth` for side text; treat as cache. Minimum width 150. |
| `showFrameButton` | boolean | editor flag | Shows the frame button on unframed media; not needed in authored models. |
| media extras | – | `aoiLeft`/`aoiRight`/`aoiTop`/`aoiBottom`, `scale`, `assetWidth`/`assetHeight`, filters, `assetName`, `assetProps` | Crop/filters of the asset, see `ContentElement.md`; omit to show the whole asset. |
| `iconColor` | – | legacy, deleted by migration 10.02 | Do not author; use `color`. |

`fitToText`, `textAlign` are ignored (see `MarkerCallout.md`).

### Nested elements

- `content` -> `FramedMediaElement` (`FramedMediaElement.md`), sharing the entry model: the marker. Built with the
  icon as default asset type, unframed images allowed, `allowColorOnColor`, and the `markerSize` limits. Its
  `content` child is the `ContentElement` (`ContentElement.md`) holding the asset.
- `text` -> `TextElement` (`TextElement.md`), as in `MarkerCallout.md`.
