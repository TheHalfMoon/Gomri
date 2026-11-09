# PresentationTitle

`PresentationTitle` renders the deck's title slide: a title text block (label / heading / description / date)
with a theme decoration (border, underline, frame, block), an optional image (side tray, top/bottom band or
full background), optional presenter names, company logos and a footer line. It is the root element of the
template `title` ("Title"). It uses the whole canvas (no margins) and does not allow a slide header, footer,
tray or element text block.

## Model location

- `states[0].primary` – the `PresentationTitle` model. The title text frame (`PresentationTitleTextFrame` ->
  `TextFrameBox` -> `TextElement`) and the footer share this model, so `text`, `textAlign`, `backdrop*`,
  `info`, `disclaimer` sit directly on it.
- `states[0].primary.text` – title text object.
- `states[0].primary.image` – the image (`PresentationTitleImage`, a `ContentElement`).
- `states[0].primary.presenters` – presenters collection; items at `.presenters.items[]`, each with `.text`.
- `states[0].primary.logos` – logos collection; items at `.logos.items[]` (media fields directly on the item).
- `states[0].primary.info` / `.disclaimer` – footer texts (when `showFooter`).

## Minimal example

Template `title` with a left image, presenters and a centered logo (generator-style model):

```json
{
  "primary": {
    "showFooter": false,
    "textAlign": "left",
    "verticalAlign": "middle",
    "accentColor": "theme",
    "text": {
      "blocks": [
        { "id": "l", "type": "text", "textStyle": "label", "html": "Q3 2026" },
        { "id": "h", "type": "text", "textStyle": "heading", "html": "Board Meeting" },
        { "id": "b", "type": "text", "textStyle": "body", "html": "Quarterly business review" }
      ]
    },
    "image": { "position": "left", "traySize": 511, "content_type": "image", "content_value": "<asset id>" },
    "showPresenters": true,
    "presenters": {
      "horizontalAlign": "left",
      "items": [
        { "id": "p1", "text": { "blocks": [
          { "id": "p1n", "type": "text", "textStyle": "title", "html": "Ada Lovelace" },
          { "id": "p1t", "type": "text", "textStyle": "body", "html": "CEO" }
        ] } }
      ]
    },
    "showLogos": true,
    "logos": {
      "position": "center",
      "scale": 0.65,
      "items": [ { "id": "lg1", "content_type": "logo", "content_value": "<asset id>", "showBackdrop": true } ]
    }
  }
}
```

Background image with a white box behind the text: `"image": { "position": "background", ... }`,
`"backdropStyle": "white_box"`, `"backdropColor": "background_light"`, `"backdropOpacity": 1`.

## Pitfalls

- An `image` without `position` is not rendered at all; an image object with only `__generateImage` must
  still carry `position`.
- `presenters.items` without `showPresenters: true` are ignored; conversely `showPresenters: true` with an
  empty array shows nothing.
- Presenter names go in a `title` block and roles in a `body` block of the same item; a `heading` block in a
  presenter is not styled.
- Logos use flat media fields on each item (`content_type`/`content_value` on `logos.items[i]`); the shared
  model importer writes a nested `logo: {...}` object, but the renderer does not read that shape.
- `backdrop*` fields only take effect with `image.position: "background"`; on a side image they are ignored.
- `textAlign: "center"` with `decoration: "left_border"` is valid but the bar stays at the slide edge; pick
  `decoration` to match the alignment or leave it to the theme.
- Do not write `textPosition` (ignored), `showLabel`/`showBody`/`label`/`description` (legacy) or a
  `bulleted` block (not allowed here).

## Rules and limits

- Layout order: decoration insets (`top_border`/`left_border`: 3 stroke widths, `frame`: 4) -> footer height
  reserved at the bottom -> image tray/band (`traySize`) removed from the free area -> logos pinned (top
  corners) or stacked above the text (`center`) -> presenters row at the bottom -> text box anchored by
  `textAlign` × `verticalAlign` in the remaining area.
- `image.position: "background"` makes the element background "black" for color resolution: `primary` /
  `secondary` text resolves to the light variants; use per-block `fontColor: "white"` only if you need to
  force it. Presenters then use `presenters.textStyle` (default white text).
- `decoration: "block"` ignores the background image for the text band and forces the band color to
  `accentColor`; `underline` is skipped when `backdropStyle` is set and not `"none"`.
- Presenters are only built when `showPresenters` is true **and** `presenters.items` is non-empty; logos only
  when `logos.items` is non-empty; the footer only when `showFooter` is true.
- The whole title slide disables animations by default (`disableAllAnimationsByDefault`).
- Template flags: `allowHeader`, `allowFooter`, `allowElementCaption`, `allowElementAttribution`,
  `allowElementTextInline`, `allowElementTextTray`, `allowColorful` all `false`; no tray layouts; default
  data `{ "showFooter": false }`.
- Migrations: `_migrate_10` deletes `body` and (when `showLogos` is falsy) `logos`; `_migrate_10_02` converts
  `textPosition` into `textAlign`/`verticalAlign` (falling back to the theme decoration: centered for
  `*center*` decorations, else left).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` (required) | text object | see `TextElement.md` | Title text. Allowed block styles: `heading` (the title), `title`/`body` (description), `label`, `date` (empty `html` renders today's date). Default block style `heading`. Blocks cannot be added in the editor beyond these; keep one block per role. |
| `textAlign` | string | `"left"`, `"center"` (default), `"right"` | Horizontal anchor of the text box **and** text alignment. |
| `verticalAlign` | string | `"top"`, `"bottom"`, anything else/absent = vertically centered (`"middle"` is what the schema stores) | Vertical anchor of the text box in the free area. |
| `decoration` | string | `"none"`, `"left_border"`, `"top_border"`, `"frame"`, `"block"`, `"underline"`; default derived from the theme's `styleDecoration` (`bar_left` -> `left_border`, `bar_top_*` -> `top_border`, `border` -> `frame`, `block*` -> `block`, `underline_*` -> `underline`, else `none`) | Theme-colored title decoration. `block` paints a full-width band in `accentColor` behind the text (text turns light); `underline` follows `textAlign` (left/center/right) and is dropped when a backdrop is set. |
| `accentColor` | string | palette color; default `layout.slideColor` -> theme default slide color -> `"theme"` (written into the model on build) | Decoration color and emphasized-text color. |
| `image` | object | `{ "position": "left" \| "right" \| "top" \| "bottom" \| "background", "traySize": px (default 400), "content_type", "content_value", crop/filter fields…, "backgroundColor"?: palette color }`; default none | The title image. It is shown only when `image.position` is a non-empty string. `traySize` = width of a left/right tray or height of a top/bottom band. `"background"` fills the whole slide behind the text (background treated as dark: primary text resolves to light). `backgroundColor` fills behind a non-covering image (default transparent). Media fields: see `ContentElement.md`; use `__generateImage` to have the app generate it. |
| `showPresenters` | boolean | default `false` | Show the presenters row (also requires at least one `presenters.items` entry). |
| `presenters` | object | `{ "items": [...], "horizontalAlign": "left" (default) \| "center" \| "right", "textStyle"?, "collectionColor"? }` | Presenters collection (`PresentationTitlePresenters`). `textStyle` only applies over a background image: `"white_text"` (default), `"white_box"`, `"transparent_light_box"`, `"transparent_dark_box"`, `"white_text_with_shadow"`, `"dark_text"`. |
| `presenters.items[i]` | object | `{ "id", "text": { "blocks": [ { "textStyle": "title", "html": name }, { "textStyle": "body", "html": role } ] }, "textAlign"?, "accentColor"?, "color"? }` | One presenter (`PresentationTitlePresenterItem`). Text is `title_and_body` structure: `title` = name, `body` = role/affiliation; alignment per item allowed. |
| `logos` | object | `{ "items": [...], "position": "top_left" (default) \| "top_right" \| "center", "scale": 0–1 (schema `0.75`), "collectionColor"? }` | Logos row (`PresentationLogos`). `"center"` places the logos just above the title text; `top_*` pins them to the top corners. `scale` multiplies the style logo height and gap. `backgroundColor` appears in stored examples but is not read by the collection (not verified). |
| `logos.items[i]` | object | `{ "id", "content_type": "logo" \| "image", "content_value": asset id, "showBackdrop": boolean (default `true` for new items), crop fields… }` | One logo (`PresentationLogoItem` -> `LogoElement`, fitted to the row height). The media fields are directly on the item (no `logo` sub-object). `showBackdrop` draws a white box behind the logo. |
| `showLogos` | boolean | default none | Legacy flag; `_migrate_10` deletes `logos` when it is falsy, so set it to `true` alongside `logos` for safety. Rendering itself only checks `logos.items.length > 0`. |
| `showFooter` | boolean | schema default `false` | Shows the footer line: `info` left, `disclaimer` right. |
| `info`, `disclaimer` | text object | single-block text, `textStyle: "_use_styles_"` | Footer texts (left half / right half, single line). |
| `backdropStyle`, `backdropColor`, `backdropOpacity`, `backdropPadding` (schema `40`), `backdropCornerRadius`, `shadow`, `shadowStyle`, `userWidth`, `userPositionX/Y` | see `TextFrame.md` | | Text-box backdrop/shadow/size. Effective only with `image.position: "background"` and `decoration` other than `"block"`. |
| `textPosition` | legacy | `"top_left"`, `"center"`, … | Pre-10.02 position; migrated into `textAlign` + `verticalAlign` and deleted. The text frame's own `textPosition` is overridden by the element, so writing it has no effect. |

Plus the common fields, see `BaseElement.md`. Legacy keys seen in examples and ignored: `showLabel`,
`showBody`, `label`, `description`, `body` (deleted by `_migrate_10`), `styleVariation`, `textStyle` (preset,
migrated by `TextFrame`), `userFontScale`, `titleTextStyle` on presenter items.

### Nested elements

- `textFrame` -> `PresentationTitleTextFrame` (`TextFrame.md`), shares the model; not selectable/draggable;
  backdrop padding 40px; text options: no alignment UI, fixed block set (`heading`, `title`, `body`, `label`,
  `date`), `accentColor` passed through.
- `image` -> `PresentationTitleImage` (`ContentElement.md`), model `image`; clipped, drawn behind the text for
  `"background"` and above otherwise.
- `presenters` -> `PresentationTitlePresenters` (`CollectionElement.md`), model `presenters`; `minItemCount`
  0, `maxItemCount` 10; items -> `PresentationTitlePresenterItem` -> `text` (`TextElement.md`,
  `title_and_body`, auto width/height). Laid out horizontally with a theme gap, aligned by `horizontalAlign`,
  at the bottom of the free area (above the footer).
- `logos` -> `PresentationLogos` (`CollectionElement.md`), model `logos`; `minItemCount` 0, `maxItemCount`
  10; items -> `PresentationLogoItem` -> `logo` (`LogoElement`, fit to height). Distributed horizontally.
- `footer` -> `PresentationTitleFooter` (shares the model) -> `info` and `disclaimer` `TextElement`s
  (single line, left/right aligned, half width each; the right half shrinks by 150px when the branding
  watermark is shown).
