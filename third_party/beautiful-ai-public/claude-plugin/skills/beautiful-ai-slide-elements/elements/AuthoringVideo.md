# AuthoringVideo

`AuthoringVideo` places a `Video` (the player of the `video` template, see `Video.md`) inside an optional frame on a
Classic slide. It is the child of an `AuthoringElementContainer` with `type: "video"` (see
`AuthoringElementContainer.md`); the app writes it when a `video` slide is converted to Classic ("Convert to
Classic"), with the video fields in the entry's `element` sub-object. It is distinct from `VideoElement.md` (the
video inside a media slot, which uses `content_type: "video"`).

Behaviour below is read from the code and from the conversion routine (no example model).

## Model location

- `states[0].primary.elements[]` – the container entry (`type: "video"`, `x`, `y`, `width`, `height`, …).
- `states[0].primary.elements[].element` – the video model as written by the conversion (`videoAssetId` /
  `videoId`, `autoPlay`, …, `fullBleed: false`). When `element` is absent the same fields are read from the entry
  itself.

## Minimal example

A converted YouTube video with the fields under `element`:

```json
{
  "id": "v1", "type": "video", "x": 160, "y": 90, "width": 960, "height": 540,
  "element": {
    "videoId": "https://www.youtube.com/watch?v=2T0mRZzmnbU",
    "autoPlay": false, "startTime": 0, "fullBleed": false
  }
}
```

The same with a laptop mockup: add `"frameType": "macBook_pro_14_inch"` next to `videoId` inside `element`.

## Pitfalls

- Put the video fields where the entry expects them: inside `element` when it exists, otherwise on the entry; mixing
  the two leaves the player empty.
- Field names are `videoAssetId`/`videoId`, not `content_type`/`content_value` (that is `VideoElement.md`).
- `frameType` values differ from media frames: `"rect"`/`"rounded_rect"`/`"octagon"` are **not** box frames here –
  they are treated as device ids and fall back to a default device image.
- Agents cannot upload videos; use a YouTube/Vimeo URL in `videoId` or keep an existing `videoAssetId`.

## Rules and limits

- The authored `width`×`height` is kept (no fit-to-contents); the player stretches to the box, so pick a 16:9 box
  for 16:9 videos. Editor resizing keeps the aspect ratio (locked).
- With a frame the video is laid out in the frame's clip bounds (device screen, circle, or the box inset by the
  stroke width); for device frames the frame image is fitted into the box.
- Everything about loading, oEmbed, thumbnails and offline behaviour is the `Video` element's (`Video.md`).
- Animations: the `Video`'s "Fade in" (disabled by default). Single click selects the entry. No migrations.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `videoAssetId` or `videoId` (one required) | string | uploaded video asset id / YouTube or Vimeo URL | The video, see `Video.md`. Both empty -> the "add video" overlay. |
| `autoPlay`, `startTime`, `loop`, `muted`, `playbackRate` | – | see `Video.md` | Playback settings, read by the nested `Video`. |
| `fullBleed` | boolean | conversion writes `false` | Read by `Video` only for canvas margins of a root element; has no effect inside a container. |
| `frameType` | string | `"none"` (default), `"light"`, `"dark"`, `"circle"`, `"circle-light"`, `"circle-dark"`, or a device frame id (`"macBook_pro_14_inch"`, `"iphone_15_pro"`, …) | Frame around the player: `"light"`/`"dark"` = rectangular box frame (white stroke with soft shadow / black stroke), `"circle*"` = circular clip (with white/black stroke for the light/dark variants, no stroke for plain `"circle"`), any other string = device mockup image (unknown ids fall back to a default device). |

Container fields (`x`, `y`, `width`, `height`, `rotation`, `opacity`, `shadow`, `isLocked`, `isHidden`, `groupIds`,
`name`) are in `AuthoringElementContainer.md`; plus the common fields, see `BaseElement.md`.

### Nested elements

- `video` -> `Video` (`Video.md`), shares this element's model; built with `noPlaybackArrow` (no "next slide" click
  shield inside Classic slides).
- `frame` -> `BoxFrame` (`"light"`/`"dark"`), `CircleFrame` (`"circle*"`) or `ImageFrame` (device ids, model
  `{ frame: <frameType> }`); none for `"none"`. The frame is drawn above the video and the video is clipped to the
  frame's screen/clip area.
