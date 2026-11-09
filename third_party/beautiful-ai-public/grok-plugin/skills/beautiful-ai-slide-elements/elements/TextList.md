# TextList

`TextList` renders a bullet list laid out in 1–3 columns, each column being an independent rich-text block of
bullets (bullets, numbers, letters, checkboxes, icons, or plain lines), optionally with a column header row and
one media column (framed image/screenshot). It is the root element of the template `textlist` ("Bullet List")
and the base class of `Agenda` (template `agenda`, see `Agenda.md`) and `ProductScreenshot` (template
`product_laptop`, see `ProductScreenshot.md`). The app's generator uses it for bullet-point, before/after and
sources slides.

## Model location

- `states[0].primary` – the `TextList` model (a `CollectionElement`, see `CollectionElement.md`).
- `states[0].primary.items[]` – one entry per column: text column (`TextListColumn`) or media column
  (`TextListMediaColumn`), each item object being that column's whole model.
- `states[0].primary.items[i].text` – the column's bullets (`TextElement.md`).
- `states[0].primary.columnHeader0`, `columnHeader1`, … – header text objects when `showColumnHeaders`
  (`TextListColumnHeader`, index = column position).
- `states[0].header` – slide header (`layout.headerPosition: "top"` in all examples); `states[0].tray` –
  optional image tray (`defaultImageTrayType: "right_tray"`).

## Minimal example

Template `textlist`, header on top, two numbered columns with descriptions (generator shape):

```json
{
  "header": {
    "text": { "blocks": [ { "id": "h", "type": "text", "textStyle": "heading", "html": "Monthly review" } ] }
  },
  "primary": {
    "collectionColor": "theme",
    "listStyle": "numbered",
    "startNum": 1,
    "showColumnHeaders": false,
    "autoDistributeBullets": true,
    "items": [
      {
        "id": "col1",
        "isMedia": false,
        "text": {
          "blocks": [
            { "id": "b1", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Opening &amp; Highlights" },
            { "id": "b2", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Summary of key wins for the month" },
            { "id": "b3", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Key Metrics &amp; Trends" },
            { "id": "b4", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Top KPIs and visual trends" }
          ]
        }
      },
      {
        "id": "col2",
        "isMedia": false,
        "text": {
          "blocks": [
            { "id": "b5", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Risks / Challenges" },
            { "id": "b6", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Current risks and mitigations" }
          ]
        }
      }
    ]
  }
}
```

(`layout.headerPosition` must be `"top"`.) A checklist is the same with `"listStyle": "checkbox"` on the
list and on each top-level block plus `"checkState": "checked" | "unchecked" | "crossed-out"`. A media column
is `{ "id": "m", "isMedia": true, "size": 500, "frameType": "theme", "content_type": "image",
"content_value": "<asset id>" }`.

## Pitfalls

- Every bullet must be `textStyle: "bulleted"`; `body`/`title` blocks are not allowed in a plain `TextList`
  column (they are allowed in `ProductScreenshot`).
- Writing the whole list as one block with `<br>`s or as `<ul>` HTML produces one bullet. One block per
  bullet, `indent: 1` blocks for sub-lines.
- Forgetting `listStyle` on blocks is fine (the list's `listStyle` fills it in), but mixing e.g. `"bullets"`
  blocks under `listStyle: "numbered"` is honoured block by block and looks inconsistent.
- More than 3 columns (2 when the list is narrow) is beyond `maxItemCount`; the layout will not fit.
- With `metadata.needsLayoutProcessing` set, column ids are regenerated and empty columns removed; do not
  rely on your column ids afterwards (`autoDistributeBullets: false` does not prevent this).
- `items` entries with `isMedia: true` but no `size` get an equal share of the width; the device frame can
  become very small next to two text columns – give the media column a `size`.
- `columns`, `verticalAlign`, `orientation`, `matchSizes` seen in stored examples are legacy (old `TextGrid`
  element); they do nothing on v10.
- `null` items / `null` blocks in stored examples are storage artifacts; never write them.

## Rules and limits

- Column widths: with one column the text takes 75 % of the width, centered (100 % if it is a media column);
  with several, columns without `size` share the width left after sized columns and the 40px gap (10px when
  narrow). Columns are centered in their slot; media columns are vertically centered against the text.
- Fit: the row of columns must fit the height (headers + tallest column) and every column's text must fit
  (`scaleTextToFit`, all columns take the smallest scale). Otherwise `isFit` is false and the editor rejects
  the change. Stored examples carry 2–5 top-level bullets (each with one description line) per column.
- Numbering: sequence = `startNum` + number of top-level `listStyle` blocks in the previous text columns;
  nested (`indent: 1`) numbered blocks start at 1 under each parent; headings/dividers do not restart it,
  non-list blocks do.
- Slide-level `metadata.needsLayoutProcessing: true` (what the app's generator sets): on first render
  `distributeBullets()` runs once regardless of `autoDistributeBullets`: it regroups bullets (a top-level
  block with its indent-1 followers = one group), drops groups with no text, and spreads them evenly over the
  current number of text columns, assigning **new column ids** and keeping the media column in place (index 0
  for a single text column, else index 1). If you want the columns exactly as written, do not set
  `needsLayoutProcessing`.
- `showColumnHeaders: true` requires `columnHeader<N>` for each column (missing ones render the placeholder
  "Type column header"), disables distribution and restarts numbering per column.
- Media column `frameType: "none"` is rendered as `"unframedRect"` (image clipped to a rectangle) because
  `allowUnframedImages` is false here.
- Template `textlist` flags: `variations: "list"`, `allowColorful: true`, default right image tray,
  default data `{ "items": [], "listStyle": "bullets" }`.
- Migrations: `_migrate_10` converts legacy flat items (`title`, `body`, `col`, `content_value`,
  `text_format`, `checkState`) into column models with blocks and `blockFontScales`; `listStyle: "icons"` ->
  `"icon"`; `autoArrange` -> `autoArrangeColumnsCount`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | object[] | 1–3 entries (`maxItemCount` = theme `maxCols` 3, or 2 when the list is narrower than 800px, or 1 with `forceSingleColumn`); empty -> one default text column | Columns in left-to-right order; see "items[] model" below. |
| `listStyle` | string | `"bullets"` (schema default), `"numbered"`, `"lettered"`, `"checkbox"`, `"icon"`, `"no_bullets"` | Default `listStyle` for bullet blocks that do not set their own, and the value the editor keeps in sync across all top-level bullets. Set it to the style you use on the blocks. |
| `startNum` | number | schema default `1` | First number of a numbered/lettered list; numbering continues across text columns (unless `showColumnHeaders`, which restarts each column at 1). |
| `showColumnHeaders` | boolean | schema default `false` | Adds a header text above each column (`columnHeader<N>`), disables automatic bullet distribution. |
| `columnHeader<N>` | text object | single block, `textStyle: "_use_styles_"` | Header text of column N (0-based). Heading font 30px, max 3 lines, underline rule, font size synced across headers. |
| `collectionColor` | string | palette color / `"colorful"` / `"<a>-to-<b>"`; default `"theme"` | Color of bullets, numbers, icons and the media frame; `"colorful"` colors every top-level bullet differently (bullet index runs across columns). |
| `autoDistributeBullets` | boolean | schema default `true` | Editor behaviour only: while typing/deleting, bullets are re-balanced across the text columns by height. Forced off by `showColumnHeaders`. It does **not** gate the one-time layout processing described below. |
| `forceSingleColumn` | boolean | default none | Caps the list to one column (`maxItemCount` 1). |
| `autoArrangeColumnsCount` | number | schema default `2` | Editor bookkeeping of the preferred column count; not read by the layout. |
| `autoArrange` | legacy | | Migrated into `autoArrangeColumnsCount` and deleted. |

Plus the common fields, see `BaseElement.md` / `CollectionElement.md`. Legacy keys in examples that v10
ignores: `columns`, `verticalAlign`, `orientation`, `matchSizes`, `showIcons`, `flipOrientation`,
`userFontScale`.

#### items[] model

Text column (`TextListColumn`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Column identity (`CollectionElement.md`). |
| `isMedia` | boolean | `false` / absent | Marks a text column. |
| `text` (required) | text object | `{ "blocks": [...] }`; schema default `{ blocks: [] }` | The bullets. Allowed block styles: `bulleted` and `divider` only (`Agenda` adds `section`, `ProductScreenshot` adds `heading`/`title`/`body`). Default block style `bulleted`, default `listStyle` = the list's `listStyle`. Each top-level bullet is `{ "type": "text", "textStyle": "bulleted", "listStyle": <style>, "indent": 0, "html": ... }`; a description line under it is the same with `"listStyle": "no_bullets", "indent": 1` (or `"bullets"` for real sub-bullets). Per-block `textAlign` is stripped (columns are always left-aligned). `text.blockFontScales.bulleted: [indent0Scale, indent1Scale]` scales the fonts. |
| `size` | number (px) | `100`–`1000`; default none (share the remaining width equally) | Fixed column width. |
| `color` | string | palette color | Overrides the bullet color for this column (`CollectionItemElement`). |

Media column (`TextListMediaColumn`, at most one is meaningful):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | |
| `isMedia` (required) | boolean | `true` | Marks the media column; the item is rendered by a `FramedMediaElement` (`FramedMediaElement.md`) that shares this item model. |
| `size` | number (px) | default none | Column width (the image is fit inside, centered vertically against the text columns). |
| `frameType` | string | `"theme"` (default), `"none"` (rendered as an unframed rect), shape ids, device frame ids (e.g. `"apple_macbook_space_grey"`, `"iphone_x"`) | Frame around the image; see `FramedMediaElement.md`. |
| `content_type`, `content_value`, `aoiLeft/Right/Top/Bottom`, `scale`, `assetWidth/Height`, filters, `__generateImage` | media fields | see `ContentElement.md` | The picture. Without `content_value` the frame shows the empty-media placeholder. |
| `frameColor`, `framePadding` | see `FramedMediaElement.md` | | Device frame color / inner padding. |
| `text` | `null` | | Media items carry `text: null` in templates/examples; it is not read. |

### Nested elements

- `items[]` -> `TextListColumn` (`isMedia` falsy) -> `text` (`TextElement`: freeform structure restricted to
  the allowed block types, auto height, auto-fit, font size synced across all text columns, bullets animate
  one by one, last block may be deleted) or `TextListMediaColumn` (`isMedia: true`) -> `screenshot`
  (`FramedMediaElement`, auto width/height, framed).
- `columnHeader<N>` -> `TextListColumnHeader` (`TextElement`, single block, auto height), one per column when
  `showColumnHeaders`; model key `columnHeader<N>` on the list model.
- Counts: `minItemCount` 1, `maxItemCount` 3 (2 below 800px width, 1 with `forceSingleColumn`).
