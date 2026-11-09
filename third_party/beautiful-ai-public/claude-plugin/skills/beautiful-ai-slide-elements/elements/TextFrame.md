# TextFrame

`TextFrame` positions a block of rich text inside an area (a slide region or an image): centered, pinned to an
edge/corner, or at a user-dragged position, optionally with a colored/frosted backdrop box when the text sits
over an image. It wraps a single `TextFrameBox` (documented here) which in turn owns the `TextElement`. It is
never a root: `Headline` uses it as `HeadlineTextFrame`, `PresentationTitle` as `PresentationTitleTextFrame`,
and `TextAndImage` (dashboard / collage / tray cells, see `TextAndImage.md`) as its text layer.

## Model location

`TextFrame` and `TextFrameBox` are built **without a model of their own**: they read the model of the element
that owns them. Hence their fields sit directly on:

- `states[0].primary` for `Headline` (templates `headline2`, `section`) and `PresentationTitle` (`title`)
- `…items[i].childElement` for a `TextAndImage` cell (dashboard, collage, side/bottom tray)

and the text itself is `<that model>.text` (`TextFrameBox` builds its `TextElement` with id `text`).

## Minimal example

`Headline` primary fragment with centered text over an image and a frosted backdrop (text-frame fields only):

```json
{
  "text": {
    "blocks": [
      { "id": "h1", "type": "text", "textStyle": "headline", "html": "Work-ready slides in minutes." },
      { "id": "h2", "type": "text", "textStyle": "body", "html": "Create on-brand presentations with Smart Slides." }
    ]
  },
  "textAlign": "center",
  "textPosition": "center",
  "backdropStyle": "frosted",
  "backdropColor": "frosted",
  "backdropOpacity": 1,
  "backdropPadding": 30,
  "backdropCornerRadius": 0
}
```

## Pitfalls

- Setting `backdropColor` on a headline without an image (or with the image beside the text) does nothing;
  the backdrop only exists over images.
- `userPositionX/Y` must be fractions (0–1), not pixels; pixel values are clamped to the frame edge.
- Omitting `userWidth` with `textPosition: "left"`/`"right"` over an image lets a long headline span the whole
  image; set `userWidth` (px) to keep a column.
- `verticalAlign` is defaulted to `"middle"` by the schema; writing `"center"` is not a valid value and is
  treated as `"top"`.
- Do not write `textStyle` presets or legacy `blocks` on the owner; use `backdrop*` fields and `text.blocks`.
- In `PresentationTitle` the same `textAlign` key (together with `verticalAlign`) also decides where the whole
  text box is anchored, and `textPosition` is ignored (see `PresentationTitle.md`).

## Rules and limits

- Text box size: width = natural text width (auto) or `userWidth`, capped by the frame minus an inner padding
  (30px, 20px with backdrop, 10–20px for small frames); height = text height. The text is then placed by
  `textPosition` or by `userPositionX/Y`. Owners such as `Headline` zero the inner padding.
- A backdrop needs both `backdropColor` and text over an image; `Headline` only treats the text as "over the
  image" when `headlinePosition` is `"center"`, `PresentationTitle` only when `image.position` is
  `"background"` and the decoration is not `"block"`.
- `userPositionX/Y` are clamped so the box stays inside the frame; the clamped values are written back to the
  model.
- Migration `_migrate_10_02`: `textPosition` containing `left`/`right` without `userWidth` sets
  `userWidth: "auto"` (half width); the legacy `textStyle` presets are converted as the full reference describes.
- Migration `_migrate_10` (`TextFrameBox.migrateToV10`): legacy `blocks` arrays on the owner (content-block
  format with `content`, `bulletpoint`, `icon` blocks) are converted into `text.blocks`; `textPosition` is
  also turned into `textAlign`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` (required) | text object | see `TextElement.md`; freeform structure | The rich text (`{ blocks: [...] }`). Allowed block styles: `headline`, `heading`, `title`, `body`, `bulleted`, `caption`, `label` plus `media`, `divider`, `code`, `equation` (owners may narrow this, e.g. `PresentationTitle`). Default block style `heading`. `headline`/`heading` blocks default to even line breaking. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`; default from theme (`center` for text frames) | Horizontal alignment of all blocks (per-block `textAlign` also honoured). `PresentationTitle` derives it from its own `textAlign`/`verticalAlign` and passes it down. |
| `verticalAlign` | string | `"top"`, `"middle"` (schema default), `"bottom"` | Vertical alignment inside the box when the box has a fixed height (text frames auto-size their height, so this mostly matters for `TextAndImage` cells). |
| `textPosition` | string | `"center"` (default), `"top"`, `"bottom"`, `"left"`, `"right"`, `"top_left"`, `"top_right"`, `"bottom_left"`, `"bottom_right"` | Where the text box is anchored inside the frame when not user-positioned. Ignored when the owner passes its own position (`PresentationTitle`). With `"top"`/`"bottom"` and a backdrop, the box spans the full width (caption bar). |
| `userPositionX`, `userPositionY` | number | `0`–`1`, fraction of frame width/height; default none | Both set = free ("user") position of the box's top-left corner; clamped into the frame on every layout (and written back). Omit for auto positioning. |
| `userWidth` | number (px) | default none (auto width); legacy `"auto"` is migrated to half the frame width | Fixed max width of the text box; text wraps to it. Set this for left/right positioned text over images so it does not span the whole frame. |
| `backdropColor` | string \| null | palette color name, `"frosted"`, or `null` | Fill of the box behind the text. Only rendered when the text is **over an image** (`backgroundElement` is a picture/video, not an icon); otherwise ignored. |
| `backdropOpacity` | number | `0`–`1`; default none (= opaque) | Alpha of `backdropColor`. |
| `backdropPadding` | number (px) | schema default `30` (`40` for `PresentationTitle`) | Padding between text and backdrop edge (applied as text padding whenever a backdrop is shown). |
| `backdropCornerRadius` | number (px) | default `0` | Corner radius of the backdrop. |
| `backdropStyle` | string | `"none"`, `"white_box"`, `"transparent_light_box"`, `"transparent_dark_box"`, `"frosted"`, `"custom"` | Name of the preset the editor used to fill the four fields above (`white_box` = `background_light`/1, `transparent_light_box` = `background_light`/0.5, `transparent_dark_box` = `background_dark`/0.3, `frosted` = blurred glass). Informational for rendering, but `PresentationTitle` disables its underline decoration when it is set and not `"none"`. Keep it consistent with `backdropColor`. |
| `shadow` | string \| object \| null | `"drop"`, `"soft"`, `"block"`, or `{ x, y, blur, color, opacity }` | Drop shadow on the text (only when over an image). `color` is a palette color name. |
| `shadowStyle` | string | `"none"` or a preset name | Editor preset name for `shadow`; informational. |
| `animationStyle` | string | action-text animation name; default none | Entrance animation of the text box in playback (same names as `ActionText`; not verified). |
| `playOutroAnimation` | boolean | default `false` | Zoom/fade the text out when leaving the slide in playback. |
| `textStyle` | legacy | `"white_text"`, `"white_box"`, `"transparent_light_box"`, `"transparent_dark_box"`, `"white_text_with_shadow"`, `"dark_text"` | Pre-10.02 text-over-image preset. Migrated into `backdropColor`/`backdropOpacity`/`shadow` and per-block `fontColor` (`white`/`black`) and then deleted; ignored by v10 rendering. Do not write. |

Plus the common fields, see `BaseElement.md` (`accentColor` is the one that matters: emphasized text color).

### Nested elements

- `textFrameBox` -> `TextFrameBox` (shares the model). Selectable box that holds the text and, when a backdrop
  is active, creates the backdrop decoration (`type: "frame"`, `shape: "rect"`, `fillColor: backdropColor`,
  `fillOpacity: backdropOpacity`, `cornerRadius: backdropCornerRadius`; `"frosted"` = transparent fill with a
  `blur(15px)` backdrop filter). `backdropColor` also becomes the background color against which text colors
  are resolved.
- `textFrameBox.text` -> `TextElement` (`TextElement.md`), freeform, auto height, auto width unless
  `userWidth`, auto-fit down to 1% scale, alignment enabled, blocks can be added/reordered/removed.
