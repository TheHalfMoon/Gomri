# FramedMediaElement

`FramedMediaElement` renders a picture, icon, logo or video inside a frame: a theme shape (rectangle, rounded
rectangle, circle, octagon), a device mockup (laptop, phone, tablet, monitor, browser window …), or no frame at
all. It wraps a `ContentElement` (the media itself, see `ContentElement.md`) and, for device frames, an
`ImageFrame`. It is never a root; it is the media child of `TextListMediaColumn` (`TextList`/`Agenda`/
`ProductScreenshot`), `TeamItem`, `IconTextGridItem`, `PhotoTextListItem`, `SequenceItem`, `ContactItemIcon`,
`UserTestimonialPhotoElement` and `AuthoringContentElement`.

## Model location

Built **without its own model** by every owner in this group: it reads the owner's model. Typical locations:

- `states[0].primary.items[i]` for a `TextList` media column (`isMedia: true`), a `Team` member, an
  `IconTextGrid` cell, a `PhotoTextList` item, a `Sequence` item.
- `states[0].primary.items[i].childElement` when the owner is a layout-container cell (`TextAndImage`).

The media fields (`content_type`, `content_value`, crop, filters) sit on the same object.

## Minimal example

A `TextList` media column with a laptop mockup:

```json
{
  "id": "device",
  "isMedia": true,
  "size": 600,
  "frameType": "macBook_pro_14_inch",
  "content_type": "image",
  "content_value": "<asset id>"
}
```

A circular photo (e.g. a `Team` member): `{ "id": "m1", "frameType": "circle", "content_type": "image",
"content_value": "<asset id>" }`; an icon in the theme shape: `{ "frameType": "theme", "content_type":
"icon", "content_value": "rocket" }`.

## Pitfalls

- `frameType` is a frame *id*, not a category: `"laptop"` or `"phone"` are not valid and fall back to an
  iPad; use `"macBook_pro_14_inch"`, `"iphone_15_pro"`, etc.
- Writing `frame: "<id>"` (the `ImageFrame` sub-model key, seen in legacy examples) on the item has no effect;
  the element reads `frameType`.
- `frameColor` does nothing for shape frames; set the item's `color` (or the collection's `collectionColor`)
  instead.
- A device frame with no `content_value` renders the device with the empty-media placeholder on screen – fine
  in the editor, empty in exports.
- Crop fields (`aoi*`, `scale`) are in asset pixel coordinates and must match the asset's real size
  (`assetWidth`/`assetHeight`); when in doubt omit them and let the element fit the asset.
- Don't leave `__generateImage.isGenerating: true` together with a `content_value`.

## Rules and limits

- Sizing: shape frames are forced square when the owner sizes the element automatically (`autoWidth` /
  `autoHeight`); the content is laid out in the frame and centered. `"none"` keeps the asset aspect ratio and
  fits the width (or the height with `fitToHeight`). Device frames are fit into the available box; with
  `autoWidth`/`autoHeight` the element shrinks to the device image.
- Device frame ids are looked up in the device catalog; an unknown id silently falls back to the first device
  (an iPad Pro portrait) – check spelling (`ipad_pro_13_inch_portait` is spelt that way in the catalog).
  Catalog categories: Shape (`none`, `rect`, `circle`, `rounded_rect`, `octagon`), Computers, Phones,
  Displays, Other (tablets, watches, polaroid, browser/laptop/phone/tablet outlines `*_solid` / `*_stroke`),
  Cisco, Masks (`triangle1`, `triangle2`, `parallelogram`, `stacked-capsules`, `arrows`, `boxes` – behaviour
  as a `frameType` not verified).
- Owners that pass `allowUnframedImages: false` (`TextList` media column) turn `frameType: "none"` into
  `"unframedRect"` once an asset is present: the asset is clipped to a rectangle with no frame.
- Colors: for device frames and on the authoring canvas the decoration color is `frameColor ?? color ??
  collectionColor ?? "white"` (item-index aware for `"colorful"`); for filled shape frames the frame fill
  becomes the content's background color, so icons/text on it resolve for contrast.
- Videos in circular device frames get a 0.5px padding to hide anti-aliasing.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `frameType` | string | `"theme"` (schema default; owner option or theme `styleShape`), `"none"`, `"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`, any device frame id (`"macBook_pro_14_inch"`, `"apple_macbook_space_grey"`, `"apple_imac"`, `"iMac_24_inch"`, `"iphone_15_pro"`, `"iphone_x"`, `"ipad_pro_13_inch_portait"`, `"apple_watch_ultra"`, `"browser_solid"`, `"laptop_stroke"`, …); legacy `"light"`, `"dark"`, `"square"` (= rect), `"circle-light"`, `"circle-dark"` (= circle) | The frame. `"theme"` follows the theme's shape style. `"none"` shows the raw asset at its own aspect ratio (unless the owner forbids unframed images, in which case it becomes an unframed clipped rectangle). Device ids draw the device PNG and clip the asset to its screen. |
| `frameColor` | string \| null | palette color name; default: `color` -> collection color -> `"white"` | Color of a device frame's screen background (and of the frame on the authoring canvas). Not used by shape frames (their fill comes from the item's `color`/`collectionColor` through `decorationStyle`). Ignored for `"unframedRect"`. |
| `framePadding` | number (px) | default `0` | Exposed as a getter but not used by this element's own layout (no effect verified); omit. |
| `color` | string \| null | palette color | Fallback for `frameColor`; for shape frames the item color used by the frame fill/stroke. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`, `"none"`; default inherited (theme `styleElementStyle`) | How a shape frame is painted (only shape frames honour it; `"none"` frame forces no decoration). With `"muted"`/`"fillAndStroke"` or no frame, icons keep their own color on colored backgrounds. |
| `content_type` (required for a visible asset) | string | `"image"`, `"icon"`, `"logo"`, `"video"` | Asset kind (`ContentElement.md`). |
| `content_value` (required for a visible asset) | string | asset id, or icon key for icons | The asset. Without it the frame shows the "add media" placeholder. |
| `aoiLeft`, `aoiRight`, `aoiTop`, `aoiBottom`, `scale`, `assetWidth`, `assetHeight`, `flipHorizontal`, `mediaOpacity`, `filter`, `filterBrightness`, `filterContrast`, `filterBlur`, `filterStrength`, `assetProps`, `assetName`, `iconColor`, `iconScale`, `__generateImage` | media fields | see `ContentElement.md` | Crop (area of interest in asset pixels), scaling, filters, generation request. Omit the crop to show the whole asset fitted. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `content` -> `ContentElement` (`ContentElement.md`), shares the model: the actual picture/icon/logo/video,
  centered in the frame; for shape frames it owns the shape decoration (`rect`/`circle`/`octagon`,
  `rounded_rect` = rect with 10px corners, stroke width from the theme's icon-frame style).
- `frame` -> `ImageFrame`, only for device frames; model `{ frame: <frameType> }`. Loads the device PNG,
  exposes its screen `clip` rectangle (the content is clipped and, when the device has rounded corners,
  rounded) and draws above the content.
