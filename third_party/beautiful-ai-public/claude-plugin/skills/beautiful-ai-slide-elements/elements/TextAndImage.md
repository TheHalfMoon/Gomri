# TextAndImage

`TextAndImage` is the content of a grid cell: an optional media slot (`ContentElement`: image, logo, icon or video)
and/or an optional free-form text box (`TextFrame`) laid over or beside it. It is the `childElement` of a
`LayoutContainerItem` with `componentType: "TextAndImage"`, which is what every `PhotoCollage` cell (`image`,
`collage` templates), every dashboard "text / image" cell, every carousel page cell, every side tray and the bottom
tray are made of. It is never a root element.

## Model location

- `states[0].primary.items[].childElement` (PhotoCollage: `image`, `collage`; `dashboard` cells with
  `componentType: "TextAndImage"`; also `headline*` photo cells)
- `states[0].primary.items[].items[].childElement` (`textgrid_carousel` pages, see `ImageCarousel.md`)
- `states[0].tray.items[].childElement` (left/right trays) and `states[0].elementTextBlock.items[].childElement`
  (bottom tray)
- Legacy/flat: when a `LayoutContainerItem` has `componentType: "TextAndImage"` but **no `childElement`**, the
  element shares the item's own model, so the same fields can sit directly on `items[]` next to `componentType` and
  `cellColor`. Stored examples contain both shapes; author the `childElement` form.

The cell itself (`componentType`, `cellColor`, `id`) belongs to `LayoutContainerItem.md`.

## Minimal example

A dashboard / collage cell with an image and a headline over it (`states[0].primary.items[]` entry):

```json
{
  "componentType": "TextAndImage",
  "cellColor": "background_accent",
  "childElement": {
    "content_type": "image",
    "content_value": "27e64e20b02112994e8a91b8a11586434b89bf2d44c8bac38fccbc42d010df9e-I",
    "text": {
      "blocks": [
        { "type": "text", "textStyle": "headline", "html": "$1.9M" },
        { "type": "text", "textStyle": "heading", "html": "West Coast" }
      ]
    },
    "textPosition": "bottom_left",
    "textAlign": "left"
  }
}
```

Text-only cell:

```json
{
  "componentType": "TextAndImage",
  "cellColor": "background_light",
  "childElement": {
    "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Overview" } ] },
    "textAlign": "center",
    "verticalAlign": "middle"
  }
}
```

Icon + text, side by side, framed:

```json
{
  "componentType": "TextAndImage",
  "childElement": {
    "content_type": "icon",
    "content_value": "pencil",
    "iconPosition": "left",
    "frameType": "rounded_rect",
    "text": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Start with any input" } ] }
  }
}
```

## Pitfalls

- `componentType` on the cell must be `"TextAndImage"`; a cell without `componentType` becomes a `GridPlaceholder`
  and ignores `childElement`.
- A leftover `__generateImage` makes an otherwise empty cell behave as an image cell (dark text overlay colors,
  spinner) - delete it when you fill `content_value` or want a text-only cell.
- `text` must be `{ "blocks": [...] }`; a bare string or `blocks` at the top level is legacy and only partially
  migrated. Omit `text` entirely (do not write `{ "blocks": [] }`) for image-only cells.
- `backdropStyle` alone does nothing: set `backdropColor` (+ `backdropOpacity`) for a visible box, or set both.
- `frameType: "theme"` depends on the theme (`styleShape` may be `"none"`); use an explicit shape id when the
  frame matters. `frameType` written on a legacy `items[]` level (not in `childElement`) is deleted by the 10.02
  migration.
- `iconPosition` on an image cell changes the layout to side-by-side; do not copy it from icon examples into image
  cells unless that is intended.
- Crop fields copied from an example belong to that example's asset; drop `aoi*`/`scale`/`assetWidth`/`assetHeight`
  when you change `content_value` (see `MediaElement.md`).

## Rules and limits

- Layout cases: text only -> text fills the cell; image only -> image fills the cell; image + text -> text box
  positioned by `textPosition`/`userPosition` over the image; icon + text (or `iconPosition` set) -> side by side
  (`left`/`right`) or `background` (icon full cell, text over it).
- Colors: text over an image resolves its color against a dark "background-image" color (white text by default);
  text beside an icon or in a text-only cell resolves against the cell color (or the frame when framed).
- Blocks keep their own `fontColor` (e.g. `"white"`); the 10.02 migration wrote `fontColor` from the legacy
  `textStyle` and `accentColor` from the slide color.
- Minimum size with text: 20x20 px; the grid marks the cell "not fit" below that.
- `name` in the editor is `"<Image|Icon|Logo|Video> + Text"`, `"Text"` or `"Empty"` depending on the two flags.
- An empty cell (no image, no text) shows the grid placeholder overlay ("add image / add text").

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Media (read by `ContentElement` / `Picture` / `Icon` / `VideoElement`, shared model):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"image"`, `"logo"`, `"icon"`, `"video"`, `"stock_video"`; default `"image"` | Kind of media, see `ContentElement.md`. |
| `content_value` | string | asset id / icon key | `showImage` is `content_value != null || __generateImage != null`; with neither, the cell is text-only (or an empty placeholder). |
| `__generateImage` | object | see `ContentElement.md` | Counts as "has image" and shows a spinner while `isGenerating`. Remove when you set `content_value`. |
| `aoi*`, `scale`, `flipHorizontal`, `filter`, `filterBrightness/Contrast/Blur/Strength`, `mediaOpacity`, `kenBurnsEffect`, `assetProps`, `assetName` | | see `MediaElement.md`, `Picture.md`, `VideoElement.md` | Crop/filters/video settings. All optional. |
| `iconColor` | string | palette color | Icon color (icons only), see `Icon.md`. |

Text:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | `{ blocks: [...] , syncFontSizeWithSiblings? }` | default: none | The text box. `showText` is `text.blocks.length > 0` (legacy `blocks` at the top level also counts). Blocks are `{ type: "text", textStyle, html }`; allowed `textStyle`s: `"headline"`, `"heading"` (default), `"title"`, `"body"`, `"bulleted"`, `"caption"`, `"label"`, plus `"media"`, `"divider"`, `"code"`, `"equation"` block types. Block format: see `TextElement.md`. |
| `text.syncFontSizeWithSiblings` | boolean | default `false` | Match the font scale with the other cells of the grid (only offered when the grid has > 1 cell). |
| `textPosition` | string | `"center"` (default), `"top"`, `"bottom"`, `"left"`, `"right"`, `"top_left"`, `"top_right"`, `"bottom_left"`, `"bottom_right"` | Where the text box sits in the cell when there is no user position. With `"top"`/`"bottom"` plus a backdrop the box stretches to the full cell width (caption style). |
| `userWidth` | number | px; `"auto"` = half the cell (migration value) | Fixed width of the text box; absent = auto width from the text. Left/right positions get `userWidth: "auto"` on migration. |
| `userPositionX`, `userPositionY` | number | 0-1 fraction of the cell | Free text-box position (overrides `textPosition`); clamped into the cell. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`, `"justify"`; default from styles (left) | Horizontal text alignment. |
| `verticalAlign` | string | `"top"`, `"middle"` (default via schema), `"bottom"` | Vertical alignment of the blocks inside the box. |
| `backdropColor` | string | palette color (`"background_light"`, `"background_dark"`, ...) or `"frosted"`; default none | Box behind the text, only drawn when the text is over an image (`isOverImage`: the media is an image/logo/video, not an icon). |
| `backdropOpacity` | number | 0-1 | Opacity of `backdropColor`. |
| `backdropPadding` | number | px, default 30 | Padding inside the backdrop box; also the gap between an icon and its text (`iconPosition` layouts). |
| `backdropCornerRadius` | number | px, default 0 | Corner radius of the backdrop. |
| `backdropStyle` | string | `"none"`, `"white_box"`, `"transparent_light_box"`, `"transparent_dark_box"`, `"frosted"`, `"custom"` | UI preset name. Setting it in the editor rewrites `backdropColor`/`backdropOpacity`/`backdropPadding`/`backdropCornerRadius` (`white_box` -> `background_light`/1, `transparent_light_box` -> `background_light`/0.5, `transparent_dark_box` -> `background_dark`/0.3, `frosted` -> `"frosted"`/1). The renderer reads only the four concrete fields, so set those. |
| `shadow` | `"drop"` / `"soft"` / `"block"` / `{ x, y, blur, color, opacity }` | default none | Drop shadow on text over an image. |
| `shadowStyle` | string | `"none"` ... | UI preset name only; not read by the renderer. |
| `iconPosition` | string | `"left"` (default when an icon and text coexist), `"right"`, `"background"` | Side-by-side layout: media gets `min(height, width/3)` on that side, text the rest. Applies automatically for icons; setting it on an image cell forces the same split layout for images (text then takes its colors from the cell, not the image). |

Framing and color:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `frameType` | string | `"none"` (default), `"theme"` (theme `styleShape`: `rect`, `rounded_rect`, `circle` or `none`), a shape id (`"rect"`, `"rounded_rect"`, `"circle"`, `"octagon"`) or a device/mask frame id (e.g. `"browser_solid"`, `"laptop_stroke"`, `"iphone_15_pro"`, `"polaroid"`, `"triangle1"`) | Frame drawn around the whole cell content (image **and** text). Shape frames become a decoration behind the content; device frames are PNG overlays with a clip. |
| `frameScale` | number | 0-1, default 1 | Shrinks the frame inside the cell (examples: 0.9-0.95). |
| `frameColor` | string | palette color, default `"theme"` | Decoration color of a shape frame (fill when `decorationStyle` is `"filled"`). |
| `decorationStyle` | string | `"filled"` (default), `"outlined"`, `"muted"`, `"fillAndStroke"` | Only for shape frames; image frames are always filled. `muted`/`fillAndStroke` blend the frame color with the background at 50 %. |
| `cellColor` | string | | Not read here: the cell color lives on the `LayoutContainerItem` (`items[].cellColor`), see `LayoutContainerItem.md`. `allowBackgroundColor` tells the cell whether its color may show: true when framed, when there is no media, when the media is an icon, scaled below fill, has alpha or a solid background, or when `caption` is set. |
| `caption` | object | | Legacy: only affects `allowBackgroundColor`; no caption element is built in v10. |
| `attribution` | `{ blocks }` | | When non-null and there is an image, a small white-plated text (`PhotoCollageAttribution`) is placed bottom-right over the image. Not present in any stored example (not verified visually). |
| `textWidth`, `listStyle`, `boxHAlign`, `textStyle` | | | Legacy/unused: `boxHAlign` is written by the 10.02 migration but never read; `textStyle` (`"white_text"`, `"white_box"`, ...) is migrated into `backdropColor`/`shadow`/block `fontColor` and deleted. |

### Nested elements

- `contentElement` -> `ContentElement.md` (only when `showImage`), rendered at layer -1 behind the text; filled to
  the cell, aspect-free scaling unless the grid's `layoutEngineType` is `"preserve-aspect"`.
- `textFrame` -> `TextFrame.md` -> `TextFrameBox` -> `TextElement.md` (only when `showText`); the text box is
  draggable/resizable only when there is an image; otherwise it fills the cell. The text-box fields above
  (`textPosition`, `userWidth`, `userPosition*`, `backdrop*`, `shadow`) are read by `TextFrame`/`TextFrameBox` from
  this same model.
- `attribution` -> `PhotoCollageAttribution` (a `TextElement` with a white fill decoration; folded here).
