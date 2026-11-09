# SlidePlaceholder

A "hold my spot" slide: a fixed white background graphic (static placeholder SVG) with one free-text note on top,
used to reserve a slide whose content is not decided yet. It is the root element of the `slidePlaceholder`
template (`states[0].primary`). No header, footer, tray, layouts, callouts or conversion to Classic are available,
and the slide ignores the theme background color (always white).

## Model location

- `states[0].primary` – the placeholder; its only authored content is `text`.
- `states[0].primary.text` – the note (`TextElement`, id `text`).

## Minimal example

```json
{
  "primary": {
    "text": {
      "blocks": [
        { "type": "text", "textStyle": "title", "html": "TODO: customer case study — waiting for approved logos" }
      ]
    }
  }
}
```

## Pitfalls

- Do not add `header`/`tray` or layout options: the template disallows them and they are not rendered.
- The slide stays white with a placeholder graphic regardless of theme; it is meant to be replaced, not presented.
- Keep the note short; it is scaled to fit the full slide and very long notes become small.
- The field is `text` on `primary` (not `title`/`body`), as `{ blocks: [...] }`.

## Rules and limits

- `allowHeader`, `allowFooter`, `allowLayouts`, element text inline/tray and attribution are all disabled by the
  template; `availableTrayLayouts` is empty and `canConvertToAuthoring` is false. Any `header`/`tray` in `states[0]`
  is ignored.
- The background color is forced to white (`preventSlideBackgroundColor`), so theme/background settings have no effect.
- Text is one block; multiple blocks are collapsed into the first block's structure by the importer (main text plus
  secondary lines). There are no font-size or style controls (`allowStyling: false`).
- No migrations. No stored examples exist for this template; the model is taken from the code.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks: [...] }`, default empty (placeholder "Add a note about this slide") | The note, a single block (`BlockStructureType.SINGLE_BLOCK`), scaled to fit the whole slide, line breaks allowed, no styling controls. See `TextElement.md`. Legacy `{ text: "..." }` / strings are converted on first render. |

No other model fields are read. Plus the common fields, see `BaseElement.md` (decorations are not used).

### Nested elements

- `background` -> `SlidePlaceholderBackground` (static SVG image, excluded from export; no model).
- `text` -> `TextElement.md`, filling the entire element bounds (no canvas margins).
