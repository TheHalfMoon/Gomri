# BottomTray

`BottomTray` renders the "lower tray": a full-width coloured band under the primary element holding one to
five grid cells of text (a takeaway, a caption, a quote). It is a `GridLayoutContainer`
(`GridLayoutContainer.md`) with the `bottom_tray` layout engine. `CanvasElement` creates it from
`states[0].elementTextBlock` when `layout.elementTextBlockPosition` is `"tray"`. This document also covers the
two plain text boxes `CanvasElement` places in the same area: `ElementTextBlock` (the same model key rendered
as a text block when `layout.elementTextBlockPosition` is `"inline"`) and `ElementAttribution` (the footnote /
source line enabled by `layout.showElementAttribution`). None of them is a template's root element.

## Model location

- `states[0].elementTextBlock` — rendered by `BottomTray` (`layout.elementTextBlockPosition: "tray"`) or by
  `ElementTextBlock` (`"inline"`); the same object is used for both, with different keys.
- `states[0].elementTextBlock.items[]` — the tray's cells (`LayoutContainerItem`, `LayoutContainerItem.md`),
  each with a `childElement` (`TextAndImage`, `TextAndImage.md`).
- `states[0].elementTextBlock.elementTextBlock` — the text model (`{ blocks }`) of the inline text block.
- `states[0].elementAttribution` — `ElementAttribution`; its text model is
  `states[0].elementAttribution.elementAttribution`.

## Minimal example

Bottom tray with one text cell (`layout.elementTextBlockPosition: "tray"`):

```json
{
  "elementTextBlock": {
    "layoutEngineType": "bottom_tray",
    "gridLayout": { "cols": 12, "rows": 12, "cells": [ { "x": 0, "y": 0, "width": 12, "height": 12 } ] },
    "items": [
      {
        "id": "bt-1",
        "componentType": "TextAndImage",
        "cellColor": "background_accent",
        "childElement": {
          "text": { "blocks": [ { "id": "b1", "type": "text", "textStyle": "title", "html": "Historical data shows a consistent acceleration." } ] },
          "backdropPadding": 30,
          "verticalAlign": "middle"
        }
      }
    ]
  }
}
```

Inline text block (`layout.elementTextBlockPosition: "inline"`):

```json
{
  "elementTextBlock": {
    "elementTextBlock": {
      "blocks": [ { "id": "b1", "type": "text", "textStyle": "body", "html": "Revenue grew 28% year over year." } ]
    }
  }
}
```

Attribution (`layout.showElementAttribution: true`):

```json
{
  "elementAttribution": {
    "elementAttribution": {
      "blocks": [ { "id": "a1", "type": "text", "textStyle": "body", "html": "Source: <a href=\"https://example.com\" target=\"_blank\">Example report, 2025</a>" } ]
    }
  }
}
```

## Pitfalls

- The text of the tray form lives in `items[].childElement.text`, the text of the inline form in
  `elementTextBlock.elementTextBlock`: writing blocks under the wrong key renders an empty tray / block.
- A tray without `componentType: "TextAndImage"` on its items renders grey placeholders.
- `elementTextBlockPosition: "tray"` makes `showFooter: "on"` ineffective; use `"inline"` if the footer must
  stay.
- `showElementAttribution` is a boolean; `layout.showAttribution` (legacy) is ignored.
- `ElementTextBlock` only accepts `heading` / `title` / `body` / `caption` / `label` blocks and
  `ElementAttribution` only `body` / `title` / `caption`; bullet lists and media blocks are not allowed.
- Stored examples often carry both forms (`items` and `elementTextBlock`) plus `color` / `backgroundColor`
  from switching in the editor; copy only the form matching your `elementTextBlockPosition`.
- Do not copy `text`, `styles`, `hyphenation`, `ligatures`, `fontScale` next to `blocks` from old examples
  (pre-blocks text cache); only `blocks` is read.

## Rules and limits

- `layout.elementTextBlockPosition` decides the class: `"tray"` → `BottomTray`, `"inline"` → `ElementTextBlock`,
  `"none"` → nothing (the model key may stay in the slide, it is ignored). Legacy `"above"` is migrated to
  `"none"`, `"below"` to `"inline"`; `"grid"` is not handled (the text block is built but never positioned):
  use only the three values.
- Placement: the tray is a full-width band at the bottom of the content area (between side trays); the
  primary element and a left header shrink by its height. The inline block sits below the primary element
  with 50 px side margins; when a left header has a background colour the block is confined to the primary
  element's width. The attribution is a line at the bottom of the primary area with 50 px side margins
  (above the tray, with 20 px margins, when the tray form is used); its width is reduced by 140 px when the
  presentation shows the Beautiful.ai watermark.
- `"tray"` suppresses the footer (`Footer.md`); `"inline"` and the attribution do not. With an attribution the
  inline block gets 20 px extra bottom padding and the attribution takes the tray's background colour in tray
  mode.
- Tray height: `trayHeight` (editor clamps 70–300) or automatic; the tray's minimum height is 70 px and it is
  subtracted from the space available to the primary element, so a tall tray can make the layout not fit.
- The template flags `allowElementTextTray` / `allowElementTextInline` / `allowElementAttribution` (false for
  `title`, `contactus`, `business_card`, `authoring`, `ppt-slide`, `slidePlaceholder`; attribution also
  false for `agenda`, `image`, `wordCloud`, `picture_picture`, `imagegrid`, `culturegrid`, `aboutUs`) only
  gate the editor's layout menu; `CanvasElement` builds whatever `layout` asks for.
- Deleting the last tray cell in the editor resets `layout.elementTextBlockPosition` to `"none"`.
- Shared-model export keys: `bottomTray`, `layoutTextBlocks`, `layoutAttribution`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

`BottomTray` (`layout.elementTextBlockPosition: "tray"`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | object[] | 1–5 entries in practice (presets); `minItemCount` 0 | One `LayoutContainerItem` per cell, left to right. Missing entries are padded with placeholders (`componentType: "GridPlaceholder"`) up to the number of `gridLayout.cells`; extra entries are dropped. |
| `items[].componentType` | string | `"TextAndImage"` | The cell component; the tray is built for text cells. Absent → grey placeholder. |
| `items[].cellColor` | string | palette colour name or `"none"`; the editor / generator use `"background_accent"` | Cell background. On old slides `_migrate_10_02` re-resolves it against the slide background. |
| `items[].childElement` | object | `TextAndImage` model: `text: { blocks }` (default block style `"title"`), `backdropPadding` (default 30), `verticalAlign` (`"middle"`), optionally `textAlign`, `accentColor`, a picture | The cell content. The available "text ideas" are limited to `title`. |
| `items[].id` | string | uuid; generated when missing | Item identity (`CollectionElement.md`). |
| `layoutEngineType` | string | `"bottom_tray"` (schema default) | Layout engine; keep it. |
| `gridLayout` | object | `{ cols, rows, cells }`; default one cell (`cols: 12, rows: 12, cells: [{0,0,12,12}]`). Presets: `cols: 60, rows: 2` with 1–5 cells of width 60 / 30 / 20 / 15 / 12 and height 2 side by side | Cell split; the number of `cells` is the number of rendered cells. |
| `trayHeight` | number (px) \| null | default `null` = automatic; editor range 70–300 | Fixed tray height. Automatic height is 70 px when no cell shows text, otherwise the tallest cell text plus 2 x `backdropPadding`. |
| `showGutter` | boolean | default `false` | 10 px gaps between cells. |
| `elementTextBlock`, `color`, `backgroundColor`, `textAlign`, `accentColor` | – | leftovers of the inline form | Ignored by `BottomTray` (the editor converts the inline blocks into the first cell's text when switching to `"tray"`). Harmless, but do not rely on them. |

Plus the common fields of `GridLayoutContainer.md` and `BaseElement.md`.

`ElementTextBlock` (`layout.elementTextBlockPosition: "inline"`), a `TextElement`:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `elementTextBlock` (required for content) | object | `{ "blocks": [...] }` (`TextElement.md`); absent → one empty `body` block | The text. Free-form structure: allowed `textStyle` values `"heading"`, `"title"`, `"body"`, `"caption"`, `"label"`; default `"body"`; `title` blocks get `evenBreak: true`. The default theme centres it and allows 5 lines. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`; default from the theme (`center`) | Horizontal alignment. |
| `accentColor` | string | palette colour name; default `"theme"` (set by migration) | Colour of emphasized text. |
| `color` / `backgroundColor` | string | schema default `backgroundColor: "background_accent"`, renamed to `color` on load | Legacy background colour of the pre-v10 text tray; the inline block has no background in the default theme, so it has no visible effect. Omit. |
| `items`, `gridLayout`, `layoutEngineType`, `trayHeight` | – | leftovers of the tray form | Ignored by `ElementTextBlock`. |

`ElementAttribution` (`layout.showElementAttribution: true`), a `TextElement`:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `elementAttribution` (required for content) | object | `{ "blocks": [...] }`; absent → one empty `body` block with the placeholder "Type attribution or footnote" | The footnote / source text. Allowed `textStyle` values `"body"`, `"title"`, `"caption"`; default `"body"`. Links (`<a href>`) are allowed in `html`. |
| `textAlign` | string | `"left"`, `"center"`, `"right"`; default `"right"` (theme) | Horizontal alignment. |
| `accentColor` | string | palette colour name; default `"theme"` | Colour of emphasized text. |

### Nested elements

- `BottomTray.items[]` -> `LayoutContainerItem` (`LayoutContainerItem.md`) -> `childElement` ->
  `TextAndImage` (`TextAndImage.md`). Default item is a `GridPlaceholder`, so always give `componentType`.
- `ElementTextBlock` and `ElementAttribution` are `TextElement`s (`TextElement.md`) bound to the keys
  `elementTextBlock` / `elementAttribution` of their model object; they have no children of their own.
