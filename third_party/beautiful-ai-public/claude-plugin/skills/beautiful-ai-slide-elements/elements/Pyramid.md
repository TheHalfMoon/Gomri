# Pyramid

A stack of up to 8 trapezoid sections whose top and bottom widths are interpolated between a cap width and a base
width, each section carrying either a label, a sequence number or an icon inside the shape, plus an optional
title-and-body description to the right. The same element renders the `pyramid` template (narrow cap, wide base) and
the `funnel` template (wide cap, narrow base): only the `capSize`/`baseSize` defaults differ. Sections are
`PyramidSection`, the in-shape icon is `PyramidIcon` (both documented here, no separate file).

## Model location

- `states[0].primary` – the `Pyramid` model (root) for `pyramid` and `funnel`.
- `states[0].primary.items[]` – one `PyramidSection` per section, top to bottom.

## Minimal example

```json
{
  "header": {
    "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Lead funnel" } ] }
  },
  "primary": {
    "style": "text",
    "capSize": 65,
    "baseSize": 15,
    "inverted": false,
    "step": false,
    "capAlign": "center",
    "showDescription": true,
    "collectionColor": "theme-to-light",
    "decorationStyle": "filled",
    "items": [
      {
        "pyramidLabel": { "blocks": [ { "type": "text", "html": "10,000" } ] },
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Visitors" },
          { "type": "text", "textStyle": "body", "html": "Everyone who lands on the site." }
        ] }
      },
      {
        "pyramidLabel": { "blocks": [ { "type": "text", "html": "1,000" } ] },
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Leads" },
          { "type": "text", "textStyle": "body", "html": "Signed up for the newsletter." }
        ] }
      },
      {
        "pyramidLabel": { "blocks": [ { "type": "text", "html": "300" } ] },
        "text": { "blocks": [
          { "type": "text", "textStyle": "title", "html": "Customers" },
          { "type": "text", "textStyle": "body", "html": "Converted to a paid plan." }
        ] }
      }
    ]
  }
}
```

For a `pyramid` slide use the same model with `capSize: 0`–`5` and `baseSize: 47`–`60`. For `style: "sequence"` omit
`pyramidLabel`; for `style: "icon"` replace it with `"content_type": "icon", "content_value": "<icon key>"` on the section.

## Pitfalls

- `pyramidLabel` is only drawn with `style: "text"`; with the default `"sequence"` style it is ignored and numbers are shown instead.
- The description flag is `showDescription` (singular). `showDescriptions` (plural, written by the app's own pyramid recipe) is not read.
- `capSize`/`baseSize` are percentages of the element width, not px; `capSize: 0` is a sharp apex. Both are capped by the width left after the description column.
- A section `color` of `"auto"` is migrated to `null`; use palette names or `null`.
- Do not author `title`/`body` on sections; use `pyramidLabel` and `text.blocks`.

## Rules and limits

- `pyramid` vs `funnel`: same element and fields; the template only presets `capSize`/`baseSize`. A cap narrower than the base reads as a pyramid, wider as a funnel; `inverted: true` flips either. The app's generator uses `capSize: 5`, `baseSize: 47` for both templates.
- Section height = element height / item count (at least the theme's minimum); more sections than fit make the slide report not fitting.
- The in-shape content width follows the section's mid width: with `style: "text"` and a tiny cap (`capSize: 0`), the top label has very little room and the text scale drops for all sections (scales are synced to the smallest).
- `showDescription: true` reduces the shape width by the description column; the shape is centered only when descriptions are off.
- Migrations: `title` on a section becomes `pyramidLabel` (style `"text"`); `title`/`body` become `text.blocks`.
- Template flags: header position `"top"` only; `allowColorful`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1–8 objects | Sections, top to bottom. |
| `style` | string | `"sequence"` (schema default), `"text"`, `"icon"` (`"image"` works in code but is not offered by the editor) | What is drawn inside each section: its 1-based number, the section's `pyramidLabel`, or its `content_type`/`content_value` media. |
| `capSize` | number | 0–100, default `0` | Width of the top edge as % of the element width. `pyramid` defaultData: `0`; `funnel` defaultData: `65`. |
| `baseSize` | number | 0–100, default `50` | Width of the bottom edge as % of the element width. `pyramid` defaultData: `60`; `funnel` defaultData: `15`. |
| `inverted` | boolean | `false` | Swaps cap and base (a pyramid becomes a funnel and vice versa). |
| `step` | boolean | `false` | Each section becomes a rectangle as wide as its wider edge (stepped pyramid). Also hides the description rules. |
| `capAlign` | string | `"center"` (default), `"left"` | Sections centered on a vertical axis, or flush with the left edge. |
| `showDescription` | boolean | `true` (schema default) | Shows the `items[].text` description column to the right of the shape (at least 300px reserved, at most 500px). |
| `sectionContentColor` | string | palette color, `"white"`, `"black"` or `null` | Color of the in-shape content (label / number / icon). `null`: computed from the section color. |
| `collectionColor` | string | `"theme"` (default); both templates' defaultData use `"theme-to-light"` | Section colors, per `CollectionElement.md` (`"colorful"` = one color per section, gradients like `"theme-to-light"` shade from top to bottom). |
| `decorationStyle` | string | theme default; both templates' defaultData use `"filled"` | `"filled"`/`"muted"` add a 6px gap between sections. |
| `color`, `pyramidCapWidth`, `showTitle`, `showDescriptions` | – | seen in defaultData / stored slides | Not read by the element (legacy); harmless. |

Plus the common fields, see `BaseElement.md` and `CollectionElement.md`.

#### items[] model (PyramidSection)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | generated if missing | Section key. |
| `pyramidLabel` | object | `{ "blocks": [ { "type": "text", "html": "..." } ] }` | Single-block text drawn inside the shape; only used with `style: "text"` (`TextElement.md`, scale-to-fit, font size synced across sections). |
| `content_type` / `content_value` | string | `"icon"` + icon key (default asset type); images/videos are clipped to the section polygon | Media drawn inside the shape; only used with `style: "icon"` (or `"image"`). Read from the section itself by `PyramidIcon`, a `ContentElement.md`. |
| `text` | object | `{ "blocks": [ title, body... ] }` | Description to the right (`TextElement.md`, title-and-body, scale-to-fit, synced); only rendered when `showDescription` is `true`. |
| `color` | string | palette color or `null` | Overrides the collection color for this section. |
| `hilited` | boolean | `false` | Emphasizes this section. |
| `decorationStyle` | string | inherits | `"muted"` on a section is migrated to `"filled"`. |

### Nested elements

- `items[]` -> `PyramidSection`; min 1, max 8 (`maxItemCount`); order = array order, top to bottom.
  - `shape` -> SVG polygon (the section).
  - one of: `pyramidLabel` -> `TextElement.md` (style `"text"`), `number` -> `TextElement.md` with the computed index (style `"sequence"`), `content` -> `PyramidIcon` (`ContentElement.md`, style `"icon"`/`"image"`).
  - `text` -> `TextElement.md` (description, when `showDescription`), `rule` -> SVG polyline separator (when `showDescription` and not `step`).
