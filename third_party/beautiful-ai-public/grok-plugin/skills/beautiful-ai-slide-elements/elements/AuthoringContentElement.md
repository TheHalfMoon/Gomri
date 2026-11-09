# AuthoringContentElement

`AuthoringContentElement` is the picture / icon / logo element of Classic slides: a `FramedMediaElement` (see
`FramedMediaElement.md`) whose media is a `ContentElement` (see `ContentElement.md`) and whose frame defaults to
`"none"`. It is the child of an `AuthoringElementContainer` with `type: "content"` (see
`AuthoringElementContainer.md`) on the `authoring` template, and "Convert to Classic" also emits it for map and
image-like elements of other templates. Its model is the parent's model: there are no fields of its own beyond the
frame fields below.

No stored example of the `authoring` template is available; the examples below follow the editor's defaults.

## Model location

- `states[0].primary.elements[]` – the entry itself (shared with the container) for `type: "content"`: the media
  fields sit next to `x`, `y`, `width`, `height`.
- `states[0].primary.elements[].element` – when the entry has an `element` sub-object (the conversion code writes
  `element: { content_type, content_value }` for converted maps); then all media fields must be in there.

## Minimal example

An icon without a frame (shared model):

```json
{
  "id": "i1", "type": "content", "x": 560, "y": 240, "width": 140, "height": 140,
  "content_type": "icon", "content_value": "rocket", "frameType": "none", "iconColor": "theme"
}
```

A photo clipped to a rounded rectangle with a dark frame:

```json
{
  "id": "img1", "type": "content", "x": 700, "y": 120, "width": 480, "height": 320,
  "content_type": "image", "content_value": "<asset id>",
  "frameType": "rounded_rect", "frameColor": "background_dark"
}
```

## Pitfalls

- Only `"none"`, `"rect"` and `"rounded_rect"` keep the authored `width`/`height`; circles, octagons and device
  frames rewrite them (and move `x`/`y`) on the first render.
- `frameType: "none"` clips the picture to the box instead of letterboxing it: choose `width`/`height` in the
  asset's aspect ratio or crop deliberately.
- `frameType: "theme"` is not "no frame": it applies the theme's shape (often a rounded rectangle or circle).
- `frameScale` has no effect here; `framePadding` neither (see `FramedMediaElement.md`).
- Device frame ids must be exact catalog ids; unknown ids fall back to a default device (`FramedMediaElement.md`).
- Delete any `__generateImage` object once you set `content_value` yourself.

## Rules and limits

- Size vs frame: the element always reports a fit-to-contents size to the canvas (anchor: centre), which is written
  back into `width`/`height`:
  - `"none"`: the authored `width`×`height` is kept and the media is **clipped** to it (the usual aspect-preserving
    behaviour of unframed media is turned off here).
  - `"rect"`, `"rounded_rect"`: the authored size is kept; the media is laid out inside the rectangle.
  - `"circle"`, `"octagon"`: the box is made square (side = the shorter of `width`/`height`) and
    `width`/`height` are rewritten; `x`/`y` shift to keep the centre.
  - device frames: the device image is fitted into the box and `width`/`height` become the device size; the
    media is clipped to the screen.
- When `frameType` changes, the size before the previous frame was applied is used as the base, so switching frames
  back and forth does not shrink the element.
- Editor resizing keeps the aspect ratio by default; it is locked (cannot be freed) for `"circle"`, `"octagon"` and
  device frames, and when the asset itself locks it.
- Colors: the frame color is `frameColor ?? color ?? collectionColor ?? "white"`; with a filled shape frame the
  content's background becomes that color so icons resolve for contrast.
- Pasting: the Classic canvas accepts a media asset from the clipboard and creates a `"content"` entry for it.
- Animations: the container's "Fade in".
- No migrations of its own (media migrations live in `ContentElement.md`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` (required) | string | `"image"`, `"logo"`, `"icon"` (`"video"` is possible but Classic video slides use `AuthoringVideo.md`) | Media kind, see `ContentElement.md`. |
| `content_value` (required) | string | asset id (`"image"`/`"logo"`), icon key (`"icon"`) | The asset. Without it the box shows the "add media" placeholder. |
| `frameType` | string | `"none"` (schema default, written on build), `"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`, any device frame id (`"macBook_pro_14_inch"`, `"iphone_15_pro"`, …), `"theme"` (= the theme's shape) | Frame around the media. Decides whether the authored size is kept (see Rules). |
| `frameColor` | string | palette color; the editor writes `"background_dark"` when a frame is added; fallback `color` -> `collectionColor` -> `"white"` | Color of the frame (shape frames when `decorationStyle` is filled, screen background of device frames). |
| `frameScale` | number | editor writes `0.9` with a frame | Written by the editor but **not read** by this element (only other templates use it); omit. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`; default theme element style | Shape frames only (`"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`). |
| `iconColor`, `color` | string | palette color | Icon color (`"icon"`), fallback frame color. |
| `scale`, `aoiLeft`, `aoiRight`, `aoiTop`, `aoiBottom`, `assetWidth`, `assetHeight`, `flipHorizontal`, `filter`, `filterBrightness`, `filterContrast`, `filterBlur`, `filterStrength`, `mediaOpacity`, `assetProps`, `assetName`, `__generateImage` | media fields | see `ContentElement.md` | Crop, zoom, filters, name, generation request. Omit the crop fields to show the whole asset fitted/clipped. |

Container fields (`x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, `isLocked`, `isHidden`, `groupIds`,
`name`) are in `AuthoringElementContainer.md`; the default `name` is the icon key (title-cased), the asset's
`assetName`, or `"Image"`.

### Nested elements

- `content` -> `ContentElement` (`ContentElement.md`), shares the model: `Picture` / `Logo` / `Icon` by
  `content_type`, plus the shape-frame decoration.
- `frame` -> `ImageFrame` for device frame ids (model `{ frame: <frameType> }`), drawn above the content and
  clipping it to the device screen.
