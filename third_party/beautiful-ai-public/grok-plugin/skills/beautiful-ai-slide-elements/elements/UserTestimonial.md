# UserTestimonial

`UserTestimonial` ("Quotes") shows one to six quotes in a text-box grid; each quote can have large design quote
marks, a speech-bubble/box/divider frame, and an attribution row with a portrait, name/role text and a logo. It is
the root element of the `user_testimonial` template. Items are `UserTestimonialItem`s; the attribution
(`UserTestimonialAttribution`), the quote text (`UserTestimonialQuoteElement`) and the portrait
(`UserTestimonialPhotoElement`) are folded below.

## Model location

- `states[0].primary` - the list.
- `states[0].primary.items[]` - one quote. The quote text, the attribution and its text share the item object;
  the portrait and the logo have their own sub-objects:
  - `states[0].primary.items[].content` - portrait media (`ContentElement.md` fields).
  - `states[0].primary.items[].logo` - logo media.

## Minimal example

Two quotes with portraits (`states[0]`):

```json
{
  "primary": {
    "frameStyle": "quote-box",
    "showDesignQuotes": true,
    "items": [
      {
        "showAttribution": true, "showImage": true, "showLogo": false,
        "quote": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "I spend more time on paperwork than with patients." } ] },
        "textGroup": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Dr. Jane Doe" }, { "type": "text", "textStyle": "body", "html": "Clinician" } ] },
        "content": { "content_type": "image", "content_value": "<assetId-1>-I", "frameType": "theme" }
      },
      {
        "showAttribution": true, "showImage": false, "showLogo": true,
        "quote": { "blocks": [ { "type": "text", "textStyle": "_use_styles_", "html": "I waited three weeks just to ask a simple question." } ] },
        "textGroup": { "blocks": [ { "type": "text", "textStyle": "title", "html": "Patient" } ] },
        "logo": { "content_type": "logo", "content_value": "<assetId-2>-L" }
      }
    ]
  }
}
```

## Pitfalls

- `showDesignQuotes` and `quoteColor` are read from the list; setting them only on items has no effect (except the
  per-item `quoteColor` override).
- `showTail` does nothing; use `frameStyle: "quote-box"` for the tail.
- `showImage: true` with an empty `content` shows an add-image placeholder in every attribution; set
  `showImage: false` when you have no portrait.
- The portrait and logo media go in `content` / `logo` sub-objects, not on the item.
- `textAlign` is shared by the quote and the attribution text.
- `maxItemCount` (6) is enforced by the editor, not at render time; the grid and divider presets only cover 1-6
  cells, so 7+ items are unsupported (behavior not verified).

## Rules and limits

- Grid: `CalcTextBoxGrid` places 1-6 cells; a cell wider than tall lays the attribution out horizontally
  (portrait, text, logo in a row, right-justified), otherwise vertically (stacked, centered). With 2 or 3 items and
  no `flipOrientation`, attribution rows are bottom-aligned across cells. With 4+ items (or 3 flipped) the
  attribution is drawn at 75 % scale.
- The quote gets the cell height minus attribution (and minus the bubble tail for `quote-box`); design quotes
  reserve `50 px * fontSize / 100` on both sides.
- `quote-box` and `box` frames are the background for the text/attribution colors; `divider`/`none` use the slide
  background.
- Template flags: `variations: "list"`, `allowColorful`; header and trays allowed (many examples use `left_tray` /
  `right_inline` with a photo).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

List (`states[0].primary`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 6 | Quotes, in grid order. Template default: two items `{ showAttribution: true, showImage: true, showLogo: false }`. New items copy the last item's three `show*` flags. |
| `frameStyle` | string | `"divider"` (code default), `"box"`, `"quote-box"` (box with a speech tail; template default), `"none"` | Frame per quote. `divider` draws thin lines between the cells instead of frames. |
| `showDesignQuotes` | boolean | default: absent = off (template default `true`) | Draw big opening/closing quote glyphs around each quote text. Read from the **list**, not the item. |
| `quoteColor` | string | palette color, schema default `"theme"` | Color of the design quotes (items may override). Migration 10.02 sets it to the slide color. |
| `flipOrientation` | boolean | default `false` | Flip the text-box grid (rows <-> columns); with 2-3 items this gives stacked wide cells. |
| `matchQuoteSizes` | boolean | default `false` | Sync the quote font size across items. |
| `collectionColor` | string | palette color, default `"theme"` | Decoration color for items without `color`. |
| `showTail` | boolean | | In the template `defaultData` but **not read**: the tail is drawn iff `frameStyle` is `"quote-box"`. |
| `decorationStyle`, `userFontScale` | | | Seen in examples; `decorationStyle` is not read by this element's own code (not verified for the frame path), `userFontScale` is legacy. |

Quote item (`items[]`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `quote` (required) | `{ blocks }` | one or more text blocks; the editor stores `textStyle: "_use_styles_"` (stylesheet-driven), the importer uses `"title"` | The quote text, scaled to fit (min scale 0.1, min font 10 px), centered. Block format: `TextElement.md`. |
| `showAttribution` | boolean | schema default `true` | Build the attribution row (text + optional portrait/logo). |
| `textGroup` | `{ blocks }` | title (name) + body (role) | Attribution text; only `"title"` and `"body"` blocks are allowed. Required when `showAttribution`. |
| `showImage` | boolean | schema default `true` | Show the portrait from `content`. |
| `content` | object | `{ content_type: "image", content_value, aoi*, frameType: "theme", ... }` | Portrait media (`UserTestimonialPhotoElement`, a `FramedMediaElement` that never shows unframed images: `frameType` `"theme"` -> theme shape, `"none"` -> unframed rect). Created as `{}` when missing. Icons work too (`content_type: "icon"`). |
| `showLogo` | boolean | schema default `false` | Show the logo from `logo` after the text, separated by a thin divider line. |
| `logo` | object | `{ content_type: "logo", content_value, logoScale?, showBackdrop? }` | Logo media (`LogoElement`, fitted to a 50 px * `logoScale` height). Created as `{}` when missing. |
| `logo.logoScale` | number | default 1 | Logo height multiplier. |
| `showLogoBackdrop` | boolean | default: `logo.showBackdrop`, else `true` | White plate behind the logo. |
| `textAlign` | string | `"left"`, `"center"`, `"right"` | Alignment of the quote text (shared model: also applies to the attribution text). |
| `quoteColor` | string | palette color | Per-item design-quote color. |
| `color` | string | palette color | Per-item decoration color (frame). |
| `showDesignQuotes` | boolean | written by the item schema (`true`) | **Ignored**: the item reads the list's `showDesignQuotes`. |
| `titleTextStyle`, `accentColor`, `body` | | | Legacy; ignored. |

### Nested elements

- `items[]` -> `UserTestimonialItem` (max 6, grid order), which builds:
  - `quoteFrame` -> `SVGPathElement` (only when `frameStyle` is `"box"` / `"quote-box"`): the bubble path.
  - `quote` -> `UserTestimonialQuoteElement` (a `TextElement.md`: auto width/height, scale-to-fit, even line
    breaks, alignment allowed).
  - `attribution` -> `UserTestimonialAttribution` (when `showAttribution`), which builds `textGroup` ->
    `TextElement.md`, optionally `content` -> `UserTestimonialPhotoElement` (`FramedMediaElement` ->
    `ContentElement.md` -> `Picture.md`) and `logo` -> `LogoElement` (`Picture.md`, "Logos") plus a divider line.
  - `leadingQuote` / `trailingQuote` -> `UserTestimonialItemDesignQuote` (SVG quote glyphs, exported as images)
    when the list's `showDesignQuotes` is true.
- `divider` -> `UserTestimonialDividers` (SVG lines between cells) when `frameStyle` is `"divider"`.
