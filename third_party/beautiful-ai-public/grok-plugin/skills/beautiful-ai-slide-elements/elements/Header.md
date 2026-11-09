# Header

`Header` renders the slide header: a text block (optional label, the heading, optional sub-heading) placed
across the top of the slide or in a column on its left, with an optional coloured background band and the
theme's header decoration (underline, bar, block). It is created by `CanvasElement` for every template whose
`allowHeader` is true when `layout.headerPosition` is `"top"` or `"left"`; it is never a template's root
element.

## Model location

- `states[0].header`. The header's text element shares this object: the text lives at
  `states[0].header.text` and alignment fields sit directly on `states[0].header`.
- Its position and width are not in this object but in the slide `layout` (`layout.headerPosition`,
  `layout.headerWidth`, see `Slide.md`).

## Minimal example

```json
{
  "header": {
    "text": {
      "blocks": [
        { "id": "lbl", "type": "text", "textStyle": "label", "html": "Q3 REVIEW" },
        { "id": "hd", "type": "text", "textStyle": "heading", "html": "Margin & profitability analysis" },
        { "id": "sub", "type": "text", "textStyle": "body", "html": "Our profitability remains strong." }
      ]
    },
    "textAlign": "left",
    "accentColor": "theme"
  }
}
```

A left header with a coloured column (`layout.headerPosition: "left"`, `layout.headerWidth: 389`):

```json
{
  "header": {
    "text": { "blocks": [ { "id": "hd", "type": "text", "textStyle": "heading", "html": "Growth at a glance" } ] },
    "backgroundColor": "accent3",
    "verticalAlign": "middle"
  }
}
```

## Pitfalls

- An absent `states[0].header` on a template that allows headers still renders an (empty) header box because
  `layout.headerPosition` defaults to `"top"`; set `"none"` to remove it.
- `text.blocks` must use the header styles (`heading`, `title`, `label`, `body`); `"bulleted"`, `"caption"`
  or media blocks are not allowed here.
- Do not put the heading in a legacy `title` / `body` field: those are only read by the migration of old
  slides and are ignored when `migrationVersion` is `10.03`.
- `textAlign` on a `"left"` header is overwritten with `"left"`; use `verticalAlign` there instead.
- `backgroundColor: "none"` is legacy; omit the field.
- Stored examples contain `null` entries in `text.blocks`; never write them.

## Rules and limits

- Shown only when the template's `allowHeader` is true **and** `layout.headerPosition` is `"top"` or `"left"`.
  Hide it with `layout.headerPosition: "none"`. Templates with `allowHeader: false` (`title`, `headline2`,
  `section`, `headline`, `chapter`, `headline_image`, `picture_headline_right`, `contactus`,
  `business_card`, `ppt-slide`, `slidePlaceholder`, `action-text`, `ai-generation`) never show it, whatever
  `layout` says. Some templates list only `"top"` in `availableHeaderPositions` (`swot_diagram`,
  `arrow_bars`, `pyramid`, `funnel`, `pyramid_step`, `timeline`, `timeline2`, `cycle_diagram`,
  `connection_diagram`, `journey`, `action-number`, `horizontal-funnel`, `sequence`, `gears`, `puzzle`): this
  is only enforced by the editor UI, so prefer `"top"` on them.
- `"top"` header: width = content width (the canvas minus a side tray), height = text height, limited to the
  canvas height minus the primary element's minimum height (and minus 40 px when a footer shows, minus the
  text block height when one is set). Its bottom margin is 50 px (70 px with a background, 20 px when the
  primary element is full-bleed).
- `"left"` header: width = `layout.headerWidth` (default 400 px, editor range 50–640), height = content height
  (minus a bottom tray when `elementTextBlockPosition` is `"tray"`); text is vertically aligned by
  `verticalAlign`.
- Block limits come from `TextElement`: there is no hard block count, but a header that pushes the primary
  element below its minimum height makes the layout not fit and the editor rejects the change.
- The last block's style matters for spacing: when it is `"body"` (a sub-heading) the `top_with_background_and_subheader` / `bottomPaddingWithSubheader` spacing is used.
- Theme decoration interplay: a `bar_left` decoration is removed when `layout.trayLayout` is `"left_tray"` or
  the top header is explicitly centred / right aligned; underline decorations follow `textAlign`;
  `bar_*` and `block` decorations are removed when `backgroundColor` is set.
- Migrations: `_migrate_10` deletes legacy `userFontScale` paths; `_migrate_10_02` sets `accentColor` and
  turns `backgroundColor: "none"` into absent.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` (required for content) | object | `{ "blocks": [...] }`, see `TextElement.md`; an absent/invalid value is replaced by one empty `heading` block | The header text. Block structure is `"header"`: allowed `textStyle` values are `"heading"`, `"title"`, `"label"`, `"body"`; the default style of a new block is `"heading"`. Conventional order: `label`, `heading`, `body` (sub-heading). Heading blocks get `evenBreak: true` by default (balanced line breaks); the text scales down to fit (`scaleTextToFit`). |
| `textAlign` | string | `"left"`, `"center"`, `"right"`; default from the theme (`left` in the default stylesheet) | Horizontal alignment of a `"top"` header. For `"left"` headers it is forced to `"left"` on every build (and per-block `textAlign` is cleared). |
| `verticalAlign` | string | `"top"`, `"middle"`, `"bottom"`; default `"middle"` | Vertical placement of the text inside a `"left"` header column. Ignored for `"top"` headers (they size to their text). |
| `backgroundColor` | string | palette colour name (`"background_accent"`, `"accent3"`, `"theme"`, ...); default none | Fills a rectangle behind the header: a full-width band for `"top"` (text height + padding + 20 px), the whole column for `"left"`. Legacy `"none"` is rewritten to absent by migration. With a background the theme's bar/block decoration is dropped and `"top"` headers use the `top_with_background` spacing. |
| `accentColor` | string | palette colour name; default `"theme"` | Colour of emphasized text (`<font class="emphasized">`), of the label block and of the decoration. Migration fills it from `layout.slideColor` / theme `defaultSlideColor` (`"colorful"` becomes `"theme"`). |
| `text.blockFontScales` | object | e.g. `{ "heading": 1.2 }` | Optional per-style font scale inside the text model (see `TextElement.md`). |
| `headerPosition`, `width`, `height` | – | – | Written only on the classic (`authoring`) canvas when the header is converted into an authoring element. Do not write; the position comes from `layout.headerPosition`. |
| legacy | – | `title`, `label`, `body`, `description`, `showBody`, `userFontScale`, `selStart`, `selEnd` | Pre-blocks text fields; migrated into `text.blocks` (`label` → label block, `title` → heading block, `body` → body block). Never write. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

- `text` -> `TextElement` (`TextElement.md`), bound to `states[0].header.text`. Options: block structure
  `header`, `allowAlignment` only for `"top"` headers, `allowVerticalAlignment` only for `"left"` headers.
- `backgroundFrame` -> an SVG rectangle (no model) created only when `backgroundColor` is set.
- `decoration` -> theme decoration (underline, bar, block) from `styleDecoration`; no model.
