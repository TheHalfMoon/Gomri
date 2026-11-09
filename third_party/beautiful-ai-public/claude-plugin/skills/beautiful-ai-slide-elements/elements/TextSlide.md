# TextSlide

`TextSlide` renders one freeform rich-text area filling the primary region of the slide: headings, paragraphs,
bullets, dividers and inline media, optionally flowed into several columns. It is the root element of the
templates `text` ("Text") and `long_bio` ("Long Bio" – same element, preset with a left image tray for the
portrait). Use it for paragraphs and mixed heading/body content; for a single big statement use `Headline`,
for bullet columns use `TextList`.

## Model location

- `states[0].primary` – the `TextSlide` model.
- `states[0].primary.text` – the `TextElement` text object (child built with `bindTo: "text"`; the child
  shares the primary model for the other fields below).
- `states[0].header` – optional slide header (`Header.md`); `states[0].tray` – optional image tray
  (`long_bio` default: `layout.trayLayout: "left_tray"`, `tray: { trayWidth: 567, items: [{}] }`).

## Minimal example

Template `text`, header on top, three heading/body pairs separated by dividers:

```json
{
  "header": {
    "text": { "blocks": [ { "id": "h", "type": "text", "textStyle": "heading", "html": "Business Impact" } ] },
    "textAlign": "left"
  },
  "primary": {
    "textAlign": "left",
    "text": {
      "blocks": [
        { "id": "t1", "type": "text", "textStyle": "heading", "html": "Increased Visibility" },
        { "id": "t2", "type": "text", "textStyle": "body", "html": "Real-time access to key performance indicators across departments." },
        { "id": "t3", "type": "divider", "html": "", "blockHeight": 20 },
        { "id": "t4", "type": "text", "textStyle": "heading", "html": "Team Productivity" },
        { "id": "t5", "type": "text", "textStyle": "body", "html": "Shifted resources from administrative overhead to strategic tasks." }
      ]
    }
  }
}
```

(`layout.headerPosition` must be `"top"` for the header to show.)

## Pitfalls

- `textStyle: "headline"` is not in the allowed list of this element; use `heading` (or switch to
  `Headline`).
- The app's own generator does not build `text` slides for paragraph content – it uses `headline2` with
  `headlinePosition: "left"` + an image (see `Headline.md`); `TextSlide` is the right choice when there is no
  image and no big statement.
- `columns` is a count, not a `TextList`-style array; column breaks are automatic and cannot be placed.
- `verticalAlign` only matters when the text is shorter than the area; it is not a text-frame backdrop
  setting (there is no backdrop on `TextSlide`).
- Do not copy `backdropPadding`/`verticalGap` from examples; they are leftovers of the pre-v10 content-block
  container.

## Rules and limits

- The text is laid out in the full primary area (minus a 30px style margin) and scaled down (to 50% minimum)
  until it fits; beyond that the slide reports an unfit layout. There is no hard character limit; the stored
  examples stay within roughly 3–6 blocks of short paragraphs.
- With `columns > 1` the text is measured against the fixed height and wraps across columns; a single very
  long block can span columns.
- Numbered bullets (`textStyle: "bulleted"`, `listStyle: "numbered"`) restart after any non-list block.
- Template capabilities: `text` – `allowColorful: false`; header allowed (`layout.headerPosition` `"top"`,
  `"left"`, `"none"`, ...), image tray allowed (`layout.trayLayout` `"left_tray"`, `"right_tray"`,
  `"left_inline"`, `"right_inline"`, `"none"`). `long_bio` – `showHeader: true`, `allowColorful: true`,
  default left tray of 567px.
- Migration `_migrate_10`: legacy `blocks` (content blocks with `content`/`bulletpoint`/`icon`) are converted
  to `text.blocks` (`TextFrameBox.migrateToV10`), then `blocks` is deleted.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` (required) | text object | `{ blocks: [...] }`, see `TextElement.md` | The content. Freeform structure; allowed block styles: `heading`, `title`, `body`, `bulleted`, `caption`, `label`, plus `media`, `divider`, `code`, `equation`. Default block style is `body`. (`headline`/`bigtext` are not allowed here.) |
| `textAlign` | string | `"left"` (schema default), `"center"`, `"right"`, `"justify"` | Alignment of all blocks; per-block `textAlign` overrides are honoured. |
| `columns` | number | integer ≥ 1; default `1` | Flows the blocks into N CSS columns of equal width (text wraps from column to column). |
| `verticalAlign` | string | `"top"` (default), `"middle"`, `"bottom"` | Vertical placement of the text inside the primary area. |
| `accentColor` | string | palette color name; default slide/theme color | Color of `<font class="emphasized">` runs. |

Plus the common fields, see `BaseElement.md`. Legacy keys found in stored examples and ignored by v10:
`backdropPadding`, `verticalGap`, `userFontScale`, `listStyle`, `blocks` (old content-block array, migrated
into `text.blocks` and deleted).

### Nested elements

- `text` -> `TextElement` (`TextElement.md`): freeform, auto-fit (`scaleTextToFit`), alignment allowed,
  columns = `columns`, blocks can be added. No other children.
