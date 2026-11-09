# WebView

`WebView` embeds a live web page in an iframe, optionally inside a device frame image, scaled down by a zoom
factor. It is the root element of the `web-view` template ("WebView"). Thumbnails and exports render a black
placeholder with the URL instead of the page.

## Model location

- `states[0].primary` for `web-view`.

## Minimal example

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Live Demo" } ] } },
  "primary": { "url": "https://www.beautiful.ai/pricing", "scale": 0.78, "fullBleed": false }
}
```

With a browser frame:

```json
{
  "primary": { "url": "https://www.beautiful.ai/pricing", "scale": 1, "frameType": "browser_solid" }
}
```

## Pitfalls

- Many sites refuse to be framed; the element shows a blank iframe with no error. Prefer pages you know allow
  embedding.
- `frameType` must be a device/mask frame id that has an image; `"rect"`, `"circle"`, `"theme"` resolve to an empty
  file and break the frame.
- `scale` above 1 crops the page; values far below 1 make text unreadable in screenshots (which do not render the
  page at all).
- `items` is inert; do not try to put content in it.
- Screenshots of this slide never show the page content, so visual verification through renders is impossible.

## Rules and limits

- With a frame, `autoWidth`/`autoHeight` layout options let the frame dictate the element width/height; the frame
  is centered and drawn on layer 1 above the iframe.
- The iframe is sandboxed (`allow-forms allow-scripts allow-same-origin allow-presentation allow-orientation-lock
  allow-pointer-lock`) and reloads whenever the slide becomes current (unique `itemID`), so audio/video in the page
  stops when leaving the slide.
- Only the current canvas renders the iframe; other canvases, thumbnails and exports show the "WebView <url>"
  placeholder.
- Template flags: `canConvertToAuthoring: false`; header allowed (examples use `top` and `left`); trays and
  element text blocks allowed.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `url` (required) | string | schema default `"https://www.beautiful.ai/?"` | Page to load. `javascript:` URLs are replaced by the default; the value is HTML-sanitized before use. The page must allow being framed (no `X-Frame-Options: DENY`), which the element cannot check. |
| `scale` | number | > 0, schema default 1 (example: 0.78) | Zoom factor: the iframe is rendered at `100 / scale` % size and CSS-scaled by `scale`, so 0.5 shows twice as much page. |
| `fullBleed` | boolean | schema default `false` | No canvas margins (bottom 10 px when the footer shows or the element text block is inline); otherwise 50 px margins. |
| `frameType` | string | `"none"` (default) or a **device/mask** frame id with an image file (e.g. `"browser_solid"`, `"browser_stroke"`, `"laptop_solid"`, `"desktop_stroke"`, `"iphone_15_pro"`, `"ipad_pro_13_inch_landscape"`, `"macBook_pro_14_inch"`) | Draws the frame PNG and clips the iframe to the frame's screen area. Shape ids (`rect`, `circle`, ...) have no image file and are **not** valid here. |
| `items` | array | template default `[{}]` | Present in the template `defaultData` and all examples but **not read** by the element. Omit or keep as is. |

### Nested elements

- `frame` -> `ImageFrame` (only when `frameType` is not `"none"`), folded here.

#### ImageFrame / Frame

`Frame` is an abstract, non-selectable base; `BoxFrame` / `CircleFrame` (legacy light/dark borders) and
`ImageFrame` extend it. `ImageFrame` has its own tiny model `{ frame: <device frame id> }` (the parent passes it;
never authored directly): it loads `/images/frames/<file>` for that id, fits the image into the available size and
exposes `clipBounds` (the screen rectangle inside the frame, scaled), `frameClipPath` (rounded corners) and a
custom clip path for masks. An unknown id falls back to the first device that has an image (`iphone_x` is the
default lookup, which is hidden but valid). `FramedMediaElement` uses the same `ImageFrame` for device frames around
pictures (see `TextAndImage.md`, `PhotoTextList.md`, `Team.md` for the `frameType` field on those items).
