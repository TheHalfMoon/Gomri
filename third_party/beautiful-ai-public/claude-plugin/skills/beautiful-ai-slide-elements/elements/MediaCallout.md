# MediaCallout

`MediaCallout` is the `calloutType: "content"` callout: a single icon, image, logo or video (a `FramedMediaElement`,
`FramedMediaElement.md`) with no text, sized by `width`. It extends `CalloutElement` (`CalloutElement.md`) and is
the child of an `AuthoringElementContainer` entry with `type: "callout"` on every callout host (flow chart,
Classic, target, thermometer, XY graph). The editor labels it "Image/Icon".

No stored examples exist; the examples are built from the editor's default model (`width: 80`, `height: 80`,
`fitToText: true`) and the `FramedMediaElement` schema (`frameType: "theme"`).

## Model location

Same object as the container entry: `states[0].primary.elements[]` (`flow_chart`, `authoring`, `xygraph`),
`states[0].primary.annotations.elements[]` (`target`, `thermometer`).

## Minimal example

`states[0].primary.elements[]` entry: a 100 px icon in a circle frame.

```json
{
  "id": "i1", "type": "callout", "calloutType": "content",
  "x": 640, "y": 300, "width": 100, "height": 100,
  "frameType": "circle", "color": "theme",
  "content_type": "icon", "content_value": "lightbulb"
}
```

An unframed picture: `{ "id": "p1", "type": "callout", "calloutType": "content", "x": 400, "y": 300,
"width": 240, "frameType": "none", "content_type": "image", "content_value": "<asset id>" }` (height follows the
image).

## Pitfalls

- Size with `width` (50–400); `markerSize` and `height` are ignored/overwritten.
- `x`/`y` are the centre of the media, not its top-left corner.
- `width` above 400 is laid out at 400 and written back as 400; below 50 it is raised to 50.
- `frameType: "none"` on an image keeps the image's aspect ratio – `height` changes; on an icon it draws the bare
  icon in `color`.
- Leave `text` off: it is not rendered, and switching the type later would surface it.
- Do not leave `__generateImage` on an entry you fill yourself; do not author `iconColor`.

## Rules and limits

- Fits its contents in both directions: `width` and `height` are recomputed from the media and written back; the
  reference point (centre) stays on `x`/`y`. Minimum 50×50, maximum 400×400 for editor resizing; the layout never
  lays the media out wider than 400.
- Aspect ratio is locked when resizing in the editor (left/right handles only, `canScale`).
- Connectors attach to the media box (optionally inflated by a host/theme `anchorPadding`, 0 by default) and are
  trimmed at the frame shape; an unframed icon is treated as a circle so the line stops close to it. Default
  connector color = `color ?? collectionColor`.
- No text direction control; `canChangeColor` on (the color picker drives frame/icon color).
- Editor: switching another callout to `"content"` writes `width: 80, height: 80`; "Media Scale" writes `width`;
  "Media Frame" writes `frameType` (and may rewrite `color`, see `MediaAndTextCallout.md`).
- Migration 10.02 (`CalloutsCanvas.md`): legacy items get `width = height = size ?? 75`; `iconColor` is deleted.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `calloutType` (required) | string | `"content"` | – |
| `x`, `y` (required) | number | px | Centre of the media box. |
| `width` | number | px, 50–400 (raised to 50, laid out at most 400 and written back; editor slider "Media Scale" 50–400) | **The size** of the media: the available box is `min(width, 400)` square, and the resulting media width is written back. |
| `height` | number | px, written on every render | Derived: equals `width` for shape frames, `width / aspect ratio` for an unframed image, the frame's height for device frames. Treat as cache (min 50). |
| `content_type` | string | `"icon"` (default asset type), `"image"`, `"logo"`, `"video"` | Media kind (`ContentElement.md`). |
| `content_value` | string | icon key or asset id | The asset. Without it the empty-media placeholder is shown. |
| `frameType` | string | `"theme"` (schema default = theme shape style), `"none"`, `"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`, device frame ids | Frame (`FramedMediaElement.md`). |
| `color` | string or null | palette color, default `null` -> `collectionColor` | Frame color (shape frame fill/stroke per `decorationStyle`, device-frame screen) and the color of an unframed icon. Always honoured on colored backgrounds (`allowColorOnColor` is forced on for this class). |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`; default theme | Shape frames only. |
| media extras | – | `aoiLeft`/`aoiRight`/`aoiTop`/`aoiBottom`, `scale`, `assetWidth`/`assetHeight`, filters, `assetName`, `assetProps` | Crop/filters of the asset, `ContentElement.md`. |
| `text`, `textWidth`, `textDirection`, `textAlign`, `fitToText`, `markerSize` | – | – | Not read by this class (`fitToText` is written by the editor). `markerSize` belongs to `"content-and-text"`; here the size is `width`. |
| `iconColor` | – | legacy, deleted by migration 10.02 | Use `color`. |

Plus the container fields (`AuthoringElementContainer.md`).

### Nested elements

- `content` -> `FramedMediaElement` (`FramedMediaElement.md`) sharing the entry model; built with the icon as
  default asset type, unframed images allowed, `allowColorOnColor`, frame color = `color ?? collectionColor`, and
  selectable (a click selects the media, double click opens the media picker; the callout can still be dragged
  while its media is selected). Its `content` child is the `ContentElement` (`ContentElement.md`).
