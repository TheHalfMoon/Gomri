# TextElement

`TextElement` renders a vertical stack of *blocks* (paragraphs, list items, dividers, inline media, code,
equations) from a text model of the form `{ "blocks": [ ... ] }`. It is the text building block of nearly every
element: `TextSlide`, `Headline`/`PresentationTitle` (through `TextFrame`/`TextFrameBox`), `TextList` columns and
column headers, `ActionNumber` labels, the slide `Header`, dashboard cells, diagram labels, etc. Which block
types are allowed, the default block style and whether alignment/auto-fit are enabled are **options passed by
the owning element**, not model fields; each owner doc lists them. This file documents the text model itself.

## Model location

A `TextElement` reads `ownerModel[bindTo]`, where `bindTo` is the owner-chosen key (defaults to the element id).
Common locations:

- `states[0].primary.text` (`TextSlide`, `Headline`, `PresentationTitle`, `TextAndImage`)
- `states[0].primary.items[i].text` (`TextList`/`Agenda`/`ProductScreenshot` columns, presenters, most
  collection items)
- `states[0].primary.label` (`ActionNumber`), `states[0].primary.info` / `.disclaimer` (`PresentationTitle`
  footer), `states[0].primary.columnHeader<N>` (`TextList` column headers)
- `states[0].header.text` (slide header, see `Header.md`)
- Legacy alternatives on the owner model: `dataSource: { elementId, ... }` (dynamic value pulled from another
  element, read-only) and plain strings / `{ text: "..." }` objects, which are migrated into blocks on build.

## Minimal example

A freeform text object as used by `TextSlide` / `Headline` (`states[0].primary.text`):

```json
{
  "blocks": [
    { "id": "b1", "type": "text", "textStyle": "heading", "html": "Increased Visibility" },
    { "id": "b2", "type": "text", "textStyle": "body", "html": "Real-time access to <font class=\"emphasized\">key performance indicators</font> across departments." },
    { "id": "b3", "type": "divider", "html": "", "dividerWidth": "half" },
    { "id": "b4", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Open a presentation" },
    { "id": "b5", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Navigate to the slide you want to share." },
    { "id": "b6", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Choose <a href=\"https://www.beautiful.ai\">Share Slide</a>" }
  ],
  "blockFontScales": { "heading": 1.25 }
}
```

A single-block text (`ActionNumber.label`, `TextList.columnHeader0`):

```json
{ "blocks": [ { "id": "l1", "type": "text", "textStyle": "_use_styles_", "html": "Completed projects" } ] }
```

## Pitfalls

- Using a `textStyle` the owner does not allow (e.g. `"headline"` in a `TextList` column, `"bulleted"` in a
  `PresentationTitle`) gives the block no theme styles: it renders with fallback sizing and cannot be edited
  consistently. Check the owner's allowed list.
- Putting several paragraphs in one block with `<br>` works but defeats per-block styling, bullet markers and
  animations; use one block per paragraph/bullet.
- Sub-bullets are `indent: 1` blocks placed right after their parent, not nested arrays. A description line
  under a bullet is `textStyle: "bulleted", listStyle: "no_bullets", indent: 1`.
- `listStyle` on a `"body"`/`"title"` block is silently dropped; list markers require `textStyle: "bulleted"`.
- Numbered lists in several columns continue numbering across columns (via `startNum`); a heading or body
  block between bullets restarts the count.
- `<strong>` renders as browser bold only; use `<font class="emphasized">` for the theme's emphasized style
  and accent color. Do not emit `<p>`, `<ul>`, `<li>`.
- Copying `blockBounds` / `textStyles` / `blockMargin` / `topSpace` / `bottomSpace` from examples is harmless
  but pointless; copying a stale `fontSize` / `fontScale` from another slide is not – it overrides the theme.
- Too much text does not overflow silently: auto-fit shrinks it and, past the minimum scale, the slide is
  reported as not fitting. Keep headlines short and bullets to a few words.
- Empty `html` shows an italic placeholder in the editor and nothing in playback/export; do not leave empty
  blocks around.

## Rules and limits

- Block normalization on every build: missing `id` -> uuid, missing `html` -> `""`, missing `type` ->
  `"text"`, missing `textStyle` / `listStyle` -> owner defaults, `listStyle` on non-`"bulleted"` blocks ->
  `null`, missing `indent` -> `0`, `"date"` blocks with empty `html` -> today's date (`"MMMM D, YYYY"`).
- Block structures (set by the owner): `single_block` (one block, `textStyle: "_use_styles_"`, styled by the
  owner's own style sheet entry – e.g. `ActionNumber.label`, `TextList.columnHeaderN`), `title_and_body`
  (`title`, `body`, `bulleted`), `header` (`heading`, `title`, `label`, `body`), `none`/freeform (`heading`,
  `title`, `body`, `bulleted`, `caption`, `label`, plus `headline` in text frames, plus `media`, `divider`,
  `code`, `equation`). Owner docs list the exact allowed set.
- `"numbered"` as a *textStyle* exists in the constants but has no theme styles; numbered lists are
  `textStyle: "bulleted"` + `listStyle: "numbered"`.
- Auto-fit: owners that enable `scaleTextToFit` shrink the whole text uniformly (default minimum 50%; 1% in
  `TextFrameBox`, 10% for the `ActionNumber` number) until it fits the available box, the style's `maxLines`
  and the width. If it still does not fit, `isTextFit` is false: the editor shows a warning badge and the root
  element reports an unfit layout. Siblings that sync font sizes (e.g. `TextList` columns) all take the
  smallest scale.
- Alignment: `textAlign` on the owner model is honoured only when the owner enables alignment; `"bulleted"`
  blocks are always left-aligned (right in RTL themes). `verticalAlign` on the owner model (`"top"` default,
  `"middle"`, `"bottom"`) applies when the element has a fixed height.
- Colors: text color = block `fontColor` ?? style `fontColor` (`"primary"`/`"secondary"` resolve against the
  actual background, so text stays legible on dark/colored backgrounds). `fontColor: "decoration"` uses the
  decoration color, `"slide"` the collection/slide color. Emphasized color = white on colored backgrounds,
  else block/owner `accentColor`, else `"theme"`.
- Migrations (`_migrate_10`): legacy `title`/`body`/`label`/`description` text objects and `text_format`
  (`"bullet_list"`, `"numbered_list"`) are converted into blocks; root `userFontScale` paths are converted into
  `blockFontScales`. `_migrate_10_02` assigns `accentColor`/`bulletColor` from the slide color.

## Related: TextContentItem

`TextContentItem` (an item of `Timeline` annotation layers, see `Timeline.md`) is a `CollectionItemElement`
wrapping one `TextElement` in `header` structure (`heading`/`title`/`label`/`body`, default `"title"`) with
auto-fit and alignment enabled; its text lives at `items[i].text` and follows this document.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

#### Text object (`ownerModel[bindTo]`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `blocks` (required) | object[] | at least one block; an empty array gets one empty `"title"` block unless the owner allows deleting the last block | Ordered list of blocks (see below). `null` entries are dropped; an object instead of an array is converted with `Object.values`. |
| `blockFontScales` | object | `{ "<textStyle>": number }`, and for `"bulleted"` an array `[indent0, indent1]`; default `1` each | User font-size multiplier applied to every block of that text style (e.g. `{ "heading": 1.25, "bulleted": [0.75] }`). Applied before auto-fit. |
| `syncFontSizeWithSiblings` | boolean | default `true` where the owner enables syncing (e.g. `TextList` columns, column headers) | When the owner syncs sibling text sizes, `false` opts this text out. |
| `hyphenation` | boolean | default `true` | Text-object level: allows hyphenated word breaks during layout measurement (ignored for even-break blocks). |

#### Text block (`blocks[i]`, `type: "text"`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `html` (required) | string | default `""` (renders the placeholder) | Inline HTML of the paragraph. See "HTML markup" below. |
| `type` | string | `"text"` (default), `"divider"`, `"media"`, `"code"`, `"equation"`, `"element"`, `"cards"` | Block kind. Fields below apply to `"text"`; other kinds are described further down. |
| `textStyle` | string | `"headline"`, `"heading"`, `"title"`, `"body"`, `"label"`, `"caption"`, `"bulleted"`, `"bigtext"`, `"date"`, `"section"` (Agenda only), `"_use_styles_"` (single-block owners); default = owner's default block style | Theme text style of the block (font, size, color). Must be one of the owner's allowed block types, otherwise it has no styles and renders unstyled/oversized. |
| `listStyle` | string | `"bullets"`, `"numbered"`, `"lettered"`, `"checkbox"`, `"icon"`, `"no_bullets"`; default = owner's default list style | List decoration. Only kept when `textStyle` is `"bulleted"` (or the rarely used `"numbered"`); on any other style it is reset to `null`. `"no_bullets"` = indented text without a marker. |
| `indent` | number | `0` (default) or `1` | List nesting level. `0` = top-level bullet, `1` = sub-bullet / description line. Deeper levels are not styled by the theme. |
| `id` | string | uuid; generated when missing | Block identity (animations, editor selection, caches). Provide one. |
| `listIconId` | string | icon key, default `"star"` | Icon for `listStyle: "icon"`. |
| `checkState` | string | `"checked"` (default), `"unchecked"`, `"crossed-out"` | State for `listStyle: "checkbox"`: green check, dimmed check, red X. Unchecked bullets dim their sub-blocks. |
| `listDecorationStyle` | string | `"numbers"`, `"letters"`; default `"theme"` | Marker style for numbered lists (`"lettered"` listStyle forces letters). |
| `useThemedListDecoration` | boolean | default `true` | `false` forces the plain `"1."` text marker instead of the theme's fancy numbered badge. |
| `bulletColor` | string \| null | palette color name; default: the collection color (inside collections), else the owner's decoration color (theme color) | Color of the bullet / number badge / icon of this block; indent-1 bullets default to `primary`. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`, `"justify"` | Per-block alignment; only honoured when the owner allows alignment (`TextSlide`, text frames, presenters, content items). `TextList` columns strip it. |
| `fontColor` | string | palette color name, `"white"`, `"black"`, or CSS color; default from the text style | Text color override for the block. User colors are allowed "color on color". |
| `accentColor` | string | palette color name; default: owner's `accentColor` | Color of `<font class="emphasized">` runs in this block (ignored on colored backgrounds, where emphasized text is white). |
| `emphasized` | boolean | default `false` | Render the whole block in the theme's emphasized font/color. |
| `evenBreak` | boolean | default from style (`true` for `headline`/`heading` in text frames) | Balance line lengths instead of filling lines. Forced `false` for `"bulleted"`. |
| `fontSize` | number (px) | default: style size | Overrides the base font size of the block (then multiplied by `blockFontScales` and auto-fit). |
| `lineHeight` | number | multiplier; default style | Line height override. |
| `letterSpacing` | number (em) | default style | Letter spacing override. |
| `fontWeight` | number | default style | Weight override. |
| `fontFamily` | string | font id | Font override (font is loaded on demand). |
| `spaceAbove` | number (px) | default `0` | Extra space above this block on top of the style's block spacing. |
| `hyphenation` | boolean | default `false` | CSS `hyphens: auto` for this block. |
| `ligatures` | boolean | default `true` | `false` disables font ligatures. |
| `fontKerning` | boolean | default `true` | `false` disables kerning. |
| `columns` | number | default none | CSS `column-count` inside this single block. |
| `blockStyle` | string | `"none"` (default), `"inset"`, `"color"` | Draws a background frame behind a run of consecutive blocks with the same `blockStyle` (`inset` = white with border, `color` = `blockColor`). |
| `blockColor` | string | palette color / CSS; default `"#f1f1f1"` | Fill for `blockStyle: "color"`. |

#### Other block kinds

- `type: "divider"`: `blockHeight` (px, default `20`), `dividerWidth` (`"full"` default, `"half"`,
  `"short"` = 25%), `style` (`"line"` default, `"spacer"` (invisible gap), `"dotted"`, `"dashed"`, `"fancy"`,
  `"flourish1"`, `"flourish2"`), `dividerColor` (palette color; default a 20% black/white line). `html` is
  ignored; keep `""`. A divider does not break numbering continuity of surrounding bullets.
- `type: "media"`: inline icon/image. Model: `elementModel: { "elementType": "MediaBlock", "content_type":
  "icon" | "image" | "logo", "content_value": "<icon key or asset id>", "frameType": "none" | ..., "iconScale":
  number, "color": palette color }` plus `blockHeight` (px, default `100`), `autoWidth` (default `true`).
  `elementModel` is created with `{ elementType: "MediaBlock" }` when missing. Media fields follow
  `ContentElement.md`.
- `type: "code"`: `html` (code text), `style`, `textSize` — not verified in detail.
- `type: "equation"`: `equation` (LaTeX), `fontSize`, `textAlign`, `backgroundColor` — not verified in detail.
- `type: "element"` / `"cards"`: embedded element with `elementModel.elementType`; `blockHeight`
  (default 300) / `autoHeight`. Authoring canvas only.

#### Computed caches (never author)

The layouter writes these back onto every block after rendering: `blockBounds`, `textStyles`, `blockMargin`,
`topSpace`, `bottomSpace`. Slides read with `get_slide` are full of them (`get_slide_examples` strips them); strip
them when copying. Also ignore legacy leftovers seen in stored slides: per-block `fontScale` (not read; scales live in `blockFontScales`),
`listStyleOptions` (migrated to `listIconId`), `content` (migrated to `html`), `linkToSlide` (migrated to an
`<a href="bai://<slideId>">` wrapper), block `type` values `"title"`/`"legacytitle"`/`"icon"`.

#### HTML markup allowed in `html`

The string is sanitized with DOMPurify (HTML profile, `bai:` URLs allowed) and rendered as inline HTML inside
the block. Meaningful markup:

- `<font class="emphasized">…</font>` – theme "emphasized" style: emphasized font/weight and the block's
  `accentColor` (white on colored backgrounds). This is the canonical bold/highlight; the app's own generator
  rewrites `<strong>` to this.
- `<b>…</b>` – heavier weight only (no color change); `<i>…</i>` – italic; `<br>` – line break inside a block.
- `<a href="https://…">…</a>` – hyperlink (theme `hyperlink` color); `<a href="bai://<slideId>">…</a>` – link
  to another slide of the same presentation.
- `<font style="color: …">` / `<span style="font-weight: normal">` – explicit inline overrides;
  `<font class="color-primary|color-secondary|color-auto">` – legacy color classes still honoured.
- Any `font-family` inline style is normalized to the primary font id. Block-level tags (`<div>`, `<p>`,
  `<ul>`) are not used; one block = one paragraph, bullets are separate blocks. Plain text is fine; escape `<`.

### Nested elements

- `listDecoration<blockId>` -> one of the list decorations below, one per `"bulleted"` block whose `listStyle`
  is not `"no_bullets"`.
- `<blockId>` -> `MediaBlock` (or the class named by `elementModel.elementType`) for `"media"` / `"element"` /
  `"cards"` blocks; its model is `blocks[i].elementModel`.
- `decoration` -> theme decoration (e.g. backdrop box, underline ornament), no model fields of its own; the
  backdrop fields live on the owner (`TextFrame.md`).

#### List decorations

These classes have no model of their own; they are driven by the block fields above and by the owner
(`bulletColor`, `collectionColor`, theme styles).

| `listStyle` | Decoration class | Rendering |
|---|---|---|
| `"bullets"` | `BulletDecoration` | Filled circle (30% of the line height). Color = block `bulletColor` ?? decoration/collection color (item index aware for `"colorful"`); indent-1 bullets use `"primary"`. |
| `"numbered"` / `"lettered"` | `NumberedListDecoration` | Theme badge containing the sequence number (`1`, `2`…) or letter (`A`, `B`…); indent-1 markers get a trailing `.`. Falls back to a plain text marker (`SimpleNumberedDecoration`, e.g. `1.`) when the style has no fancy badges or `useThemedListDecoration: false`. |
| `"checkbox"` | `CheckListDecoration` | Check icon: `checked` = theme `positive` color, `unchecked` = 50% primary, `crossed-out` = `x` icon in `negative`. |
| `"icon"` | `IconListDecoration` | Icon `listIconId` (default `"star"`), colored like a bullet. |
| `"no_bullets"` | none | No marker and no marker padding; block is still indented by `indent`. |

Numbering: the sequence restarts at the owner's start number (`TextList.startNum`, continued across columns)
and resets whenever a non-list block (heading, body, …) appears; each indent level has its own counter.
