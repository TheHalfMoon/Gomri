# Video

`Video` is the root element of the `video` template (and the hidden `video_title` variant): one video that fills
the primary area (optionally full-bleed) on a black background, played from an uploaded video asset or embedded
from YouTube/Vimeo through oEmbed. It is a different class from `VideoElement.md` (the video *inside* a media slot)
and has its own field names.

## Model location

- `states[0].primary` for `video` (and `video_title`).

## Minimal example

Uploaded video, full bleed, no header/footer (`states[0]` + the matching `layout`):

```json
{
  "layout": { "headerPosition": "none", "showFooter": "off" },
  "states": [ { "primary": { "fullBleed": true, "autoPlay": true, "startTime": 0, "videoAssetId": "-MLF4fM7k_cxKamez5Z_", "muted": false } } ]
}
```

YouTube embed with a header:

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Product tour" } ] } },
  "primary": { "fullBleed": false, "autoPlay": false, "startTime": 0, "videoId": "https://www.youtube.com/watch?v=2T0mRZzmnbU" }
}
```

## Pitfalls

- Field names differ from media slots: `videoAssetId` / `videoId`, not `content_type` / `content_value`;
  `startTime`/`loop`/`muted` are top-level, not under `assetProps`.
- Agents cannot upload video assets through the MCP; use a YouTube/Vimeo URL in `videoId`, or keep an existing
  `videoAssetId`.
- `videoId` must be a full URL for Vimeo; a bare id is assumed to be a YouTube id.
- Private/unlisted-without-embed videos fail oEmbed and show an error label instead of the video.
- `fullBleed` is ignored when the slide shows element attribution or an inline element text block; headers still
  take their space.

## Rules and limits

- Only one video; no items. The template `defaultData` is `primary: { fullBleed: true, autoPlay: true, startTime: 0 }`
  with `layout: { headerPosition: "none", showFooter: "off" }`.
- Uploaded videos render a `<video controls>` (controls always on outside the Zoom app, download disabled); embeds
  render the provider iframe (YouTube with `enablejsapi`, `rel=0`, `modestbranding`; Vimeo with `allow='autoplay'`).
- Thumbnails/exports show the poster (upload: the asset's `previewAssetId`; embeds: the oEmbed thumbnail) with a
  YouTube/Vimeo badge, never the video.
- Offline player: only uploads play; embeds show "Video is not available offline". oEmbed errors render
  "Could not load video" / "The permissions on the video do not allow oembed" / "Video not found" as a label.
- In playback a click shield on the right third of the element advances to the next slide (unless
  `noPlaybackArrow`).
- Element animations are disabled by default; one "Fade in" animation is available.
- Template flags: `allowHeader`, `allowFooter`, `canConvertToAuthoring: false`, `allowColorful: false`; trays are
  allowed (examples use `left_inline` trays with a text cell).
- Import from another template takes the first `video`/`stock_video` asset: `videoAssetId` = its id, and the rest of
  the asset props are spread onto the model.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `videoAssetId` | string | uploaded video asset id (e.g. `"-MLF4fM7k_cxKamez5Z_"`) | Uploaded video; takes precedence over `videoId` (`videoType` is `"upload"` when set). |
| `videoId` | string | full YouTube URL (`https://www.youtube.com/watch?v=...`, `youtu.be/...`) or Vimeo URL; a bare legacy value is treated as a YouTube video id | Embedded video (`videoType` `"youtube"` / `"vimeo"`). Any other URL -> `"none"`. |
| `autoPlay` | boolean | template default `true` | Start playing when the slide is shown in playback (in the editor it is never auto-played; in the Zoom app always). |
| `startTime` | number | seconds, default 0 | Start offset (`#t=` for uploads/Vimeo, `start=` for YouTube). |
| `loop` | boolean | default `false` | Loop playback (YouTube uses a one-video playlist for this). |
| `muted` | boolean | default `false` | Mute. Also muted automatically when auto-playing with an active presenter view. |
| `playbackRate` | number | default 1 | Playback speed for uploaded videos. |
| `fullBleed` | boolean | template default `true` | No canvas margins (bottom 10 px when a footer shows); forced off when `layout.showElementAttribution` is on or the element text block is `inline`. Otherwise 50 px margins. |

Both `videoAssetId` and `videoId` empty -> `videoType` `"none"` -> the "add video" default overlay.

### Nested elements

- `background` -> `SVGRectElement` (black rectangle behind the video, layer -1). No model.
