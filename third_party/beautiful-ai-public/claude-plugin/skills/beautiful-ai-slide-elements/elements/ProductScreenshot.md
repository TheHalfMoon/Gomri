# ProductScreenshot

`ProductScreenshot` is a `TextList` preset that shows a screenshot inside a device mockup (laptop, phone,
desktop, tablet, watch, browser window …) next to one or two text columns of feature bullets or heading/body
text. It is the root element of the template `product_laptop` ("Product Screenshot" – the same template is
used for every device; the device is just the media column's `frameType`). The model is the `TextList` model
(see `TextList.md`); this file lists only the differences.

## Model location

- `states[0].primary` – `ProductScreenshot` model (same shape as `TextList`).
- `states[0].primary.items[]` – exactly one media column (`isMedia: true`, the device) plus 1–2 text columns.
- `states[0].header` – slide header (`layout.headerPosition: "top"` in all examples). No tray
  (`availableTrayLayouts: []`).

## Minimal example

Template `product_laptop`, laptop on the left, feature bullets on the right (generator shape):

```json
{
  "header": {
    "text": { "blocks": [ { "id": "h", "type": "text", "textStyle": "heading", "html": "Smart Slides" } ] }
  },
  "primary": {
    "listStyle": "bullets",
    "startNum": 1,
    "showColumnHeaders": false,
    "items": [
      {
        "id": "device",
        "isMedia": true,
        "size": 600,
        "text": null,
        "frameType": "macBook_pro_14_inch",
        "content_type": "image",
        "content_value": "<asset id>"
      },
      {
        "id": "features",
        "isMedia": false,
        "text": {
          "blocks": [
            { "id": "f1", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Adaptive layouts" },
            { "id": "f1d", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Slides re-arrange as you add content." },
            { "id": "f2", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Brand themes" },
            { "id": "f2d", "type": "text", "textStyle": "bulleted", "listStyle": "no_bullets", "indent": 1, "html": "Fonts and colors applied everywhere." }
          ]
        }
      }
    ]
  }
}
```

To let the app generate the screenshot, replace `content_type`/`content_value` on the media item with
`"__generateImage": { "search": "<description>", "assetType": "image", "isGenerating": true }`.

## Pitfalls

- Omitting the media column turns the slide into a plain bullet list; the device only exists as an
  `isMedia: true` item with a device `frameType`.
- `frameType: "theme"`/`"none"`/shape ids give a plain framed picture, not a device; use a device id.
- A phone frame with `size: 700` is huge and squeezes the text; use ~300px for portrait phones.
- `showCallout`, `frame` and crop fields on the primary are legacy; they belong on the media item (and
  `showCallout` is not read on v10 – not verified).
- Three text columns are not possible (max 3 items including the device).

## Rules and limits

- Column order is the array order: media first = device on the left; `[text, media]` = device on the right;
  `[text, media, text]` = device between two columns (the migration uses index 0 for one text column and
  index 1 for two).
- The media column's `size` is its width in px; the device frame is fit inside it and vertically centered
  against the text column. Text columns share the remaining width (slide width minus `size`, outer padding
  and 40px gaps).
- Layout processing (`metadata.needsLayoutProcessing`) redistributes bullets across the text columns exactly
  as `TextList` and keeps the media column at index 0 (one text column) or 1 (two).
- Template `product_laptop` flags: no tray layouts, `allowColorful: true`; default data:
  `{ "listStyle": "bullets", "showColumnHeaders": false, "startNum": 1, "items": [ { media, size 700,
  frameType "apple_macbook_space_grey" }, { text column with one empty bullet + one empty indent-1 line } ] }`.
- Migration `_migrate_10`: legacy root media fields (`content_type`, `content_value`, `showCallout`,
  `frame`, `aoiLeft/Right/Top/Bottom`, `scale`, `version`, `frameType`, `size`) become a media item (size 700,
  or 500 with two text columns).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Same as `TextList.md`, with these differences:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items[i]` media column | object | `{ "id", "isMedia": true, "size": px, "frameType": device id, "content_type": "image", "content_value": asset id, crop fields…, "frameColor"?, "text": null }` | The device. Template default: `size: 700`, `frameType: "apple_macbook_space_grey"`. Generator uses `size` 300 (phone) / 600 and `frameType` `"macBook_pro_14_inch"` (laptop), `"iphone_15_pro"` (phone), `"iMac_24_inch"` (desktop), `"apple_watch_ultra"` (watch), `"ipad_pro_13_inch_portait"` (tablet). Any id from the device-frame catalog works (e.g. `"apple_imac"`, `"iphone_x"`, `"browser_solid"`, `"laptop_stroke"`); see `FramedMediaElement.md`. |
| `items[i].text.blocks[]` (text columns) | blocks | allowed `textStyle`: `"heading"`, `"title"`, `"body"`, `"bulleted"`, `"divider"` | Unlike `TextList`, headings and paragraphs are allowed, so a column can be `title` + `body` pairs or bullets. Default block style for new blocks is `"title"` (not `bulleted`). Text columns do not auto-size to their content width (`autoTextWidth` false) – they fill their slot. |
| `listStyle` | string | template default `"bullets"` | As in `TextList`. |
| `showCallout`, `frame`, `aoi*`, `scale`, `content_*` on the primary | legacy | | Pre-v10 root-level media fields; `_migrate_10` moves them into the media item. Do not write them on the primary. |

### Nested elements

Same as `TextList.md`: `TextListMediaColumn` -> `screenshot` (`FramedMediaElement`, device frame, image
clipped to the frame's screen area) and `TextListColumn` -> `text`. Column headers (`showColumnHeaders`)
are available as in `TextList`. The editor cannot add columns by dragging blocks here (no custom drop
targets), but the "add block" button is enabled inside columns. Counts: `minItemCount` 1, `maxItemCount` 3
(media + up to 2 text columns).
