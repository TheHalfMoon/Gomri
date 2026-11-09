# VideoElement

`VideoElement` plays an uploaded, stock (Pexels) or embedded (YouTube/Vimeo) video inside any media slot: it is the
`asset` child `ContentElement` builds for `content_type: "video"` or `"stock_video"`. It is **not** the root of the
`video` template (that is `Video`, see `Video.md`). It renders a `<video>` tag (upload/stock) or the provider's
oEmbed iframe, positioned with the same pan/zoom transform as pictures. Never a root element; no model of its own.

## Model location

Same object as the owning `ContentElement`: typically `states[0].primary.items[].childElement` (a `TextAndImage`
cell of `image`, `collage`, `dashboard`, carousel pages or trays) or directly on `states[0].primary.items[]` for
legacy/flat cells.

## Minimal example

Stored by the app for an uploaded 1920x1080 clip (trim and flags are what the editor writes):

```json
{
  "content_type": "video",
  "content_value": "-OvGQf-YR5_3Pw9Z0OU9",
  "assetProps": {
    "originalSize": { "width": 1920, "height": 1080 },
    "startTime": 0,
    "endTime": 32.02,
    "duration": 32.02,
    "autoPlay": true,
    "loop": true,
    "muted": true,
    "speed": 1,
    "controls": false
  }
}
```

## Pitfalls

- Agents cannot create video assets through the MCP (only image/logo assets): reuse an existing video element from
  the slide or a `content_url`; do not invent video ids.
- Omitting `assetProps.originalSize` collapses the video to a zero-size box (not verified at runtime, but the code
  derives the media size only from it).
- An absent `assetProps` is filled from the schema defaults (`startTime: 0, controls: false, loop: false,
  autoPlay: true, speed: 1, muted: true`) at build time, but `originalSize` is not part of the schema; always
  include `assetProps.originalSize`.
- `content_url` wins over `content_value`: a stale `content_url` keeps playing the old video after you change the
  asset id. Remove it when swapping.
- Filters (`filter`, `filterBrightness`...) are stored but not applied to video.

## Rules and limits

- Framing: uploads and stock videos (`canBeBackgroundVideo`) are filled (cover) with the `aoi*` transform like a
  picture; YouTube/Vimeo iframes are fitted at `scale` inside the box. Circle/octagon decorations of the parent get a
  50 % border-radius so the video does not bleed.
- The default overlay (add-media placeholder) only shows when `videoType` is `"none"`, i.e. neither `content_url`
  nor a resolvable `content_value`.
- Offline player: only uploaded videos play; others show "Video is not available offline". oEmbed failures show
  "Could not load video" / permission text inside the slot instead of failing the render.
- Thumbnails render the poster (`previewUrl` / preview asset) with a YouTube/Vimeo badge, never the video.
- Playback: `autoPlay` is honored only on the current canvas and after any click-gated animation on the element has
  run; `_stopElement` pauses when the slide leaves.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

All of `MediaElement.md` (`aoi*`, `scale`, `flipHorizontal`, `mediaOpacity`, `filter*` are stored; only the
transform and `mediaOpacity`/`filter*` props are applied to the wrapper, filters are not rendered on video), plus:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` (required) | string | `"video"` (uploaded asset) or `"stock_video"` (Pexels) | Selects this element. |
| `content_value` | string | video asset id (uploads look like `-OvGSERtzda7fdi1TmEw`; stock like `<hex>-S_V`) | Loaded with `getAssetById(id, "video")` **only when `content_url` is absent**; the asset also provides `previewAssetId` for the poster. |
| `content_url` | string | direct media URL, or a YouTube/Vimeo page URL | Takes precedence over `content_value`. Decides `videoType`: contains `youtube`/`youtu.be` -> oEmbed iframe; `vimeo` + `external` -> stock mp4; other `vimeo` -> oEmbed iframe; anything else -> `<video src>` upload. Stock videos stored with a legacy `player.vimeo.com` URL are re-resolved through Pexels using `previewUrl`. |
| `previewUrl` | string | image URL | Poster frame / thumbnail. Set by the app for stock videos; for uploads the asset's `previewAssetId` is used instead. |
| `assetProps` (required in practice) | object | schema default `{ startTime: 0, controls: false, loop: false, autoPlay: true, speed: 1, muted: true }` | Playback settings, see below. |
| `assetProps.originalSize` | `{ width, height }` | px | **The media size.** Without it `mediaSize` is 0x0 and the video box collapses (transform scale falls back to 1 on a zero-size box). Always provide it. |
| `assetProps.startTime`, `assetProps.endTime` | number | seconds; `endTime` default: the video duration | Trim range; playback loops/pauses at `endTime`. |
| `assetProps.duration` | number | seconds | Written by the app for the trim slider; informational. |
| `assetProps.loop` | boolean | default `false` (runtime fallback: loop when shorter than 10 s) | Loop between start and end. |
| `assetProps.autoPlay` | boolean | default `true` | Start playing when the slide is shown. |
| `assetProps.muted` | boolean | default `true` | Audio off. Non-current canvases are always muted. |
| `assetProps.speed` | number | 0.25, 0.5, 1, 1.5, 2 (UI choices), default 1 | `playbackRate`. |
| `assetProps.controls` | boolean | default `false` | Show player controls. Turning controls on also switches to **fit** (contain) framing for non-background videos and, through the UI, sets `autoPlay`, `loop`, `muted` to false. YouTube/Vimeo embeds force `controls: true`, `loop: false`. |

### Nested elements

None.
