# Agenda

`Agenda` is a `TextList` preset for agendas / tables of contents: numbered items with an optional description
line each, laid out in 1–3 columns, with optional "section" divider labels between groups of items and the
ability to link an item to a slide of the deck. It is the root element of the template `agenda` ("Agenda").
The model is the `TextList` model (see `TextList.md`); this file lists only the differences.

## Model location

- `states[0].primary` – `Agenda` model (same shape as `TextList`).
- `states[0].primary.items[i].text.blocks[]` – agenda items (`TextListColumn` columns).
- `states[0].header` – slide header; template `headerPosition: "top"`.

## Minimal example

Template `agenda`, single column (generator shape; layout processing may split it):

```json
{
  "header": {
    "text": { "blocks": [ { "id": "h", "type": "text", "textStyle": "heading", "html": "Agenda" } ] }
  },
  "primary": {
    "listStyle": "numbered",
    "startNum": 1,
    "showColumnHeaders": false,
    "autoDistributeBullets": false,
    "items": [
      {
        "id": "col1",
        "isMedia": false,
        "text": {
          "blocks": [
            { "id": "s1", "type": "text", "textStyle": "section", "html": "Morning" },
            { "id": "a1", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Welcome &amp; objectives" },
            { "id": "a1d", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Why we are here and what we decide today" },
            { "id": "a2", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Q3 results", "linkToSlide": "<slide id>" },
            { "id": "a3", "type": "text", "textStyle": "bulleted", "listStyle": "numbered", "indent": 0, "html": "Roadmap" }
          ]
        }
      }
    ]
  }
}
```

## Pitfalls

- Agenda items are `textStyle: "bulleted"` blocks, not `"agendaitem"` (that constant has no styles).
- A `section` block is a label, not a column header; for per-column titles use `showColumnHeaders` +
  `columnHeader<N>`.
- `listStyle: "bullets"` on the primary with numbered blocks (as in old examples) renders numbered items but
  is inconsistent; keep both at `"numbered"`.
- If you rely on a fixed column split, omit `metadata.needsLayoutProcessing`; otherwise the agenda may be
  re-flowed into more columns (`autoDistributeBullets: false` does not prevent that one-time pass).
- `linkToSlide` must be an id of a slide in the same presentation; unknown ids silently do nothing.

## Rules and limits

- Layout processing (`metadata.needsLayoutProcessing: true`): unlike `TextList`, `Agenda` may **change the
  number of columns**. With 1 column: if the text had to shrink, it is redistributed into 2 columns (3 if it
  shrank below 50 %); with 2 columns and any shrinking: 3 columns; with 3 columns: plain redistribution.
  Column ids are regenerated in the process.
- Numbering continues across columns from `startNum` and is not interrupted by `section` or `divider` blocks.
- Links to slides are not rendered as hyperlinks (`linkToSlideAsLink` is false); they only affect playback
  navigation.
- Template flags: `headerPosition: "top"`, `variations: "list"`, `allowElementTitle`/`Caption`/`Attribution`
  `false`, `allowColorful: true`, default data `{ "items": [] }` (one empty numbered column is created).
- Migration `_migrate_10`: legacy `items[]` of `{ title, body, type: "section", linkToSlide }` are converted
  into 1 column (< 6 items) or 2 columns of blocks; `_migrate_10_02` sets `listStyle: "numbered"`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Same as `TextList.md`, with these differences:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `listStyle` | string | `"numbered"` (schema default and getter fallback); `"lettered"`, `"bullets"`, … accepted | Default marker of agenda items. Migration `_migrate_10_02` forces it back to `"numbered"` on old slides. |
| `items[i].text.blocks[]` | blocks | allowed `textStyle`: `"bulleted"` (agenda item, `indent: 0`, `listStyle: "numbered"`), `"bulleted"` + `listStyle: "no_bullets"` + `indent: 1` (description), `"section"` (section label), `"divider"` | Agenda items. A `section` block is a centered, decoration-colored label with rules on both sides (title font, 20px); it does **not** restart the numbering. |
| `items[i].text.blocks[].linkToSlide` | string | slide id; default none | Makes the item clickable in playback, jumping to that slide. Kept as a block field here (other elements migrate it into an `<a href="bai://…">` wrapper). |
| `startNum`, `showColumnHeaders`, `columnHeader<N>`, `collectionColor`, `autoDistributeBullets`, `forceSingleColumn`, media columns | see `TextList.md` | | Identical behaviour. |

Legacy keys in stored examples ignored by v10: `showIndex`, `userFontScale`, and `listStyle: "bullets"` on
old slides whose blocks are already `"numbered"`.

### Nested elements

Same as `TextList.md` (`TextListColumn` / `TextListMediaColumn` items, optional `TextListColumnHeader`s).
Placeholders differ ("Type agenda item" / "Type description (or hit ENTER for a new agenda item)").
Counts: `minItemCount` 1, `maxItemCount` 3.
