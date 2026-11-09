# Headline

`Headline` renders one large statement (headline + optional label/sub-text) with an optional image grid: text
beside the image (top/bottom/left/right split) or centered on top of it. It is the root element of the
templates `headline2` ("Headline") and `section` ("Section Break", same element with a label block and a
colored background preset). It is also the slide the app's generator uses for paragraphs-with-image
("text" category), quotes, section breaks and key concepts.

## Model location

- `states[0].primary` – the `Headline` model. Its text frame (`HeadlineTextFrame` -> `TextFrameBox` ->
  `TextElement`) and its image grid (`HeadlineImages`, a `PhotoCollage`) are built **without their own
  model**, so all their fields live directly on `states[0].primary`.
- `states[0].primary.text` – the text object.
- `states[0].primary.items[]` – image cells (`LayoutContainerItem` models, see `LayoutContainerItem.md` /
  `PhotoCollage.md`).
- No `states[0].header` (`allowHeader: false`); the headline text *is* the header. No tray
  (`availableTrayLayouts: []`). A bottom text block (`layout.elementTextBlockPosition`, `states[0].elementTextBlock`)
  and element attribution are allowed.

## Minimal example

Template `headline2`, text on the left, image on the right (shape produced by the app's generator):

```json
{
  "primary": {
    "fullBleed": true,
    "showGutter": false,
    "headlinePosition": "left",
    "dividerSize": 0.5,
    "textPosition": "left",
    "textAlign": "left",
    "text": {
      "blocks": [
        { "id": "l", "type": "text", "textStyle": "label", "html": "Section 1" },
        { "id": "h", "type": "text", "textStyle": "headline", "html": "Work-ready slides in <font class=\"emphasized\">minutes</font>." },
        { "id": "d", "type": "divider", "html": "", "dividerWidth": "short" },
        { "id": "b", "type": "text", "textStyle": "body", "html": "Create on-brand presentations with Smart Slides." }
      ]
    },
    "items": [
      {
        "id": "img1",
        "componentType": "TextAndImage",
        "childElement": { "content_type": "image", "content_value": "<asset id>" }
      }
    ]
  }
}
```

Text over a full-bleed image: same model with `"headlinePosition": "center"`, `"textPosition": "center"`,
`"backdropStyle": "frosted"`, `"backdropColor": "frosted"` and no `dividerSize`.

## Pitfalls

- `items: [{}]` or `items: [null]` counts as "no image" (`items[0]` must have keys) but still leaves a junk
  entry; omit `items` entirely when there is no picture.
- Putting `content_value` directly on `items[i]` (legacy shape) is not read on v10 models with
  `migrationVersion: 10.03`; always nest media under `childElement` with `componentType: "TextAndImage"`.
- `headlinePosition` without an image is ignored; `dividerSize` outside `0.33–0.75` (left/right) is clamped
  silently.
- `backdropColor`/`shadow` do nothing unless `headlinePosition` is `"center"` and the first item is a
  picture/video.
- `allowHeader` is false: a `states[0].header` on a headline slide is not rendered; put the label in the text
  blocks instead.
- With `aspectRatio: "fit"` the image cannot be full-bleed and leaves background around it.
- `textStyle` (legacy preset), `layoutType` and `blocks` on the primary are not v10 fields; do not write them.

## Rules and limits

- No image: `headlinePosition` is treated as `"center"` and the text frame fills the primary area; backdrop
  settings are ignored (text is not over an image).
- Text over image (`"center"`): the text frame's background is the first image, so `backdropColor` /
  `shadow` / per-block `fontColor: "white"` become effective; the image can be darkened with
  `childElement.filterBrightness` (e.g. `0.33`) or `mediaOpacity`.
- Split layouts: text region = `dividerSize` share, 100px horizontal gap (left/right) or 50px block spacing
  (top/bottom); `fullBleed` lets the image reach the canvas edges on its outer sides.
- Text is auto-fit (down to 1%); a headline that does not fit at a readable size is still "fit" – keep
  headlines to one or two lines (`headline` ≈ 80px, `heading` ≈ 50px base size). The generator switches
  from `headline` to `heading` above ~100 characters.
- Template `section` (`version: 2`) defaults: blocks `[label "Section 1", headline ""]`, `fullBleed`,
  `showGutter`, `layout.backgroundStyle: "backgroundColor"`, `layout.backgroundColor: "theme"`.
- Template flags (both): `allowHeader: false`, `allowFooter: true`, `preventDefaultFooter: true`,
  `allowElementTextInline`/`Tray: true`, `allowElementAttribution: true`, no tray layouts.
- Migrations: `_migrate_10` renames legacy `userFontScale` paths; `_migrate_10_02` deletes legacy `blocks`,
  stamps `accentColor` on text blocks and `elementModel.color` on media blocks, and (`PhotoCollage`) wraps
  flat items into `{ componentType: "TextAndImage", childElement }` while preserving `text`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` (required) | text object | see `TextElement.md`; when missing/empty one empty `headline` block is created | The statement. Freeform structure; allowed block styles `headline`, `heading`, `title`, `body`, `bulleted`, `caption`, `label` plus `media`, `divider`, `code`, `equation` (`bigtext` has theme styles here but is not offered by the editor). Default block style `heading`; the template default is one `headline` block. |
| `items` | object[] | default none (no image). Each: `{ "id", "componentType": "TextAndImage", "childElement": { media fields }, "cellColor"? }` | Image cells of the grid. The image is shown when `items[0]` is a non-empty object. One item = one picture; several items = collage (`gridLayout` decides the cells). `childElement` holds `content_type` (`"image"`, `"video"`, `"logo"`, `"icon"`), `content_value` (asset id) and crop fields (`aoiLeft/Right/Top/Bottom`, `scale`, `assetWidth/Height`, filters) – see `ContentElement.md`; or `__generateImage` to let the app generate it. |
| `headlinePosition` | string | `"top"` (default with an image), `"bottom"`, `"left"`, `"right"`, `"center"`; forced to `"center"` when there is no image | Where the text goes relative to the image. `"center"` = text over the image (backdrop/shadow fields apply, text box is draggable). |
| `dividerSize` | number | `0`–`1`; default `0.5`; clamped to `0.33`–`0.75` for left/right and `0.1`–`0.75` for top/bottom | Fraction of the width (left/right) or height (top/bottom) given to the text. |
| `fullBleed` | boolean | default none (falsy); template default `true`; forced `false` when `aspectRatio` is `"fit"` | Image extends into the slide margins (and footer area unless `showGutter`). |
| `showGutter` | boolean | default `false`; template default `true` | 10px gutter around/between images. With `fullBleed` it also keeps the footer area free. |
| `aspectRatio` | string | `"fill"` (default), `"fit"` | `"fit"` shows the whole picture (letterboxed) and disables `fullBleed`. |
| `gridLayout` | object | `{ "cols": 12, "rows": 12, "cells": [ { "x", "y", "width", "height" } ] }`; default: the layout engine's automatic grid | Cell geometry for several images (one cell per item, in item order). For a single image use one 12x12 cell or omit. |
| `layoutEngineType` | string | `"flex"`, `"custom"`, `"preserve-aspect"`, `"fixed"`, …; migration sets `"preserve-aspect"` for `aspectRatio: "fit"`, else `"flex"` | Grid engine; see `GridLayoutContainer.md`. Omit unless you supply `gridLayout`. |
| `textPosition` | string | `"center"` (default), `"top"`, `"bottom"`, `"left"`, `"right"`, `"top_left"`, … | Anchor of the text box inside its region (the text half, or the whole slide when `headlinePosition` is `"center"`). See `TextFrame.md`. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`; default `center` (theme) | Text alignment. The generator uses `"left"` for left/right layouts. |
| `verticalAlign` | string | `"top"`, `"middle"` (schema default), `"bottom"` | Vertical alignment inside the text box (rarely visible, the box is auto-height). |
| `userWidth`, `userPositionX`, `userPositionY` | number | px / 0–1 fractions | Fixed text width and dragged position; see `TextFrame.md`. |
| `backdropStyle`, `backdropColor`, `backdropOpacity`, `backdropPadding`, `backdropCornerRadius`, `shadow`, `shadowStyle` | see `TextFrame.md` | | Box/shadow behind the text, only when `headlinePosition` is `"center"` over a picture/video. |
| `accentColor` | string | palette color; default slide color | Emphasized-text color (also copied onto blocks by migration). |
| `frame` | string | legacy (`"dark"`, `"light"`, `"none"`); default `"none"` | Legacy image frame of the collage; leave out. |
| `borderColor` | string | palette color | Grid border color (`GridLayoutContainer`); rarely used. |

Plus the common fields, see `BaseElement.md`. Legacy keys in stored examples that v10 ignores or migrates:
`layoutType`, `blocks` (old content blocks -> `text.blocks`), `textStyle` presets, `userFontScale`,
`verticalGap`, flat image fields on `items[i]` (`content_value` directly on the item – migrated into
`childElement`).

### Nested elements

- `textFrame` -> `HeadlineTextFrame` (a `TextFrame`, `TextFrame.md`), shares the model; cannot be deleted;
  draggable/resizable only when the text is over the image.
- `images` -> `HeadlineImages` (a `PhotoCollage` / `GridLayoutContainer`, `PhotoCollage.md`), shares the
  model, built only when `items[0]` is non-empty; `minItemCount` 0, `maxItemCount` 10, gutter 10px; cells
  are `HeadlinePhotoItem` (`PhotoCollageItem` with text disabled) whose `childElement` is a `TextAndImage`
  media cell.
- `items[]` -> `HeadlinePhotoItem`, model = `items[i]`; `childElement` -> media (`ContentElement.md`).
