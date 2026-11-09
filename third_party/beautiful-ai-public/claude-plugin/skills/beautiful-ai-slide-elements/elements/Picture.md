# Picture

`Picture` renders a raster/SVG image asset as an SVG `<image>` with the pan/zoom transform, filters and optional
Ken Burns animation. It is the `asset` child that `ContentElement` builds for `content_type: "image"`; its subclass
`Logo` is built for `content_type: "logo"`. It is never a root element and has no model of its own: all fields live
on the owning element's model (see `ContentElement.md`).

## Model location

Same object as the owning `ContentElement`, e.g. `states[0].primary.items[].childElement` (TextAndImage cells),
`states[0].primary.items[]` (Team / PhotoTextList / LogoGrid items), `states[0].primary.items[].content`
(UserTestimonial photo), `states[0].tray.items[].childElement` (image trays).

## Minimal example

Image:

```json
{ "content_type": "image", "content_value": "27e64e20b02112994e8a91b8a11586434b89bf2d44c8bac38fccbc42d010df9e-I" }
```

Logo (LogoGrid item):

```json
{ "content_type": "logo", "content_value": "b1d101eb2360dfccc208cf9ff35cf26c889b6b7aa0d6d5ee6737d39c22b5c520-L" }
```

Image with a tint and a slow zoom:

```json
{
  "content_type": "image",
  "content_value": "27e64e20b02112994e8a91b8a11586434b89bf2d44c8bac38fccbc42d010df9e-I",
  "filter": "theme",
  "filterStrength": 0.8,
  "kenBurnsEffect": "zoom_in"
}
```

## Pitfalls

- A wrong or foreign `content_value` does not throw; the slot silently shows the "add image" placeholder (and in
  `TextAndImage` the cell still counts as "has image", so text keeps white-on-dark styling).
- Do not set `backgroundColor` on logos; it is ignored. Use the parent's backdrop switch instead.
- `kenBurnsEffect` only animates in the live editor/player; screenshots and exports show the still crop.
- SVG and GIF assets ignore the size optimisation; very large SVG logos still render fine but keep `scale` small.
- Carrying `aoi*`/`assetWidth`/`assetHeight` from one asset to another discards the crop (see `MediaElement.md`).

## Rules and limits

- Default transform: fill (cover) the available box; the owning `ContentElement` may pass `fitAsset` (contain) or
  the parent may use `allowScaleBelowFill` (user can shrink the image inside the frame, which then shows the
  backdrop color). When an image is scaled below fill and has no solid background, the parent's `isBackgroundVisible`
  becomes true so cell colors / frame fills show around it.
- `overflowHidden` is always on: the image is clipped to the element bounds (and to the parent's decoration clip
  path for circle/octagon/rounded frames).
- Filters: `filter` presets other than the listed ones are passed through as an SVG filter id and render nothing
  special; `"None"` (capital N, seen in legacy models) is treated as none.
- Alpha / background: `hasAlpha` on the asset makes the parent treat the slot as transparent (cell color visible
  behind it, no dark text overlay logic). `hasSolidBackground` + `imageBackgroundColor` is what the dashboard uses
  for `cellColor: "use-image-background"` style plates; nothing to author on the image itself.
- Face detection (`enableFaceDetection: true`) only runs when the default transform is being computed, i.e. when
  there is no valid authored crop.

### Logos

`Logo extends Picture` is built for `content_type: "logo"` and changes only the framing policy:

- Default transform is **fit** at `defaultScale` (0.66 from `ContentElement`, or the parent's `defaultLogoScale`:
  LogoGrid passes its own `defaultLogoScale`, template default 0.8; the raw `Logo` default is 0.75). `minScale` is
  half the fit scale, `maxScale` is exactly the fit scale, so a logo can never be cropped, only shrunk.
- `backgroundColor` is **not** read from the model: the getter returns `"none"` when the asset has alpha, else
  `"white"` (the asset's `hasAlpha` flag decides; `isTransparent` exposes it). No v10 renderer was found that draws
  this value; the visible white plate behind a logo is drawn by the parent (`LogoGridItem` when `showBackdrop`,
  `LogoElement` when its `showBackdrop` is on).
- `constrainAspectRatio` is `"fit"`; `ContentElement.getContentSize()` reports 200x200 for logos regardless of the
  asset size, so logo cells are sized by the parent, not by the image.
- A logo asset id ends in `-L`; the same id with `content_type: "image"` renders as a filled, croppable photo.

`LogoElement` (a `ContentElement` subclass used by `PresentationLogoItem` and `UserTestimonialAttribution.logo`) fits
the logo into the available box (`fitWidth` / `fitHeight` options), reads `showBackdrop` from the model (white
rectangle behind the logo; `UserTestimonial` passes the item's `showLogoBackdrop`, default true) and is otherwise a
plain `ContentElement` whose model is the `logo` sub-object (`content_type`, `content_value`, `aoi*`, `logoScale`
for UserTestimonial).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

All of `MediaElement.md` (`aoi*`, `scale`, `isDefaultTransform`, `assetWidth/Height`, `flipHorizontal`, `filter`,
`filterStrength`, `filterBrightness`, `filterContrast`, `filterBlur`, `mediaOpacity`, `backgroundColor`, `altText`,
`enableFaceDetection`), plus:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_value` (required) | string | image asset id (`<hex>-I`) or logo asset id (`<hex>-L`) | Loaded through the image asset store (`getAssetById(id, "image")`); the id suffix decides the real asset type. Load failure -> `hasMedia = false` -> the owning `ContentElement` shows its placeholder overlay. |
| `kenBurnsEffect` | string | `"none"` (default), `"zoom_in"`, `"zoom_out"`, `"pan_left"`, `"pan_right"` | 30 s looping CSS animation, only while the slide is the current canvas (not in thumbnails/exports). |

Asset-record properties the renderer uses but that are **not** in the slide model: `w`/`h` (pixel size),
`fileType` (`gif` and `svg` always load the original file; GIFs render as an empty placeholder on non-current
canvases), `hasAlpha`, `hasSolidBackground`, `imageBackgroundColor`, `modifiedAt`, `isGenerated`.

### Nested elements

None.
