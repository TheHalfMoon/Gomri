# MediaElement

`MediaElement` is the abstract base of `Picture` (images and logos) and `VideoElement`. It owns the *media transform*:
how the source asset is scaled and panned inside the box the parent gives it, plus flips, filters and opacity. It
never renders anything itself and is never a root element. Everything here applies to any element whose
`content_type` is `"image"`, `"logo"`, `"video"` or `"stock_video"`.

## Model location

Shares the model of its `ContentElement` parent (which in turn usually shares its own parent's model). In practice
the fields below sit next to `content_type` / `content_value`, e.g. `states[0].primary.items[].childElement` for a
`TextAndImage` cell, `states[0].primary.items[]` for a `Team` / `PhotoTextList` / `LogoGrid` item,
`states[0].primary.items[].content` for a `UserTestimonial` photo.

## Minimal example

An authored crop (show the left 2/3 of a 3000x2000 photo, no filters):

```json
{
  "content_type": "image",
  "content_value": "27e64e20b02112994e8a91b8a11586434b89bf2d44c8bac38fccbc42d010df9e-I",
  "aoiLeft": 0,
  "aoiTop": 0,
  "aoiRight": 2000,
  "aoiBottom": 2000,
  "isDefaultTransform": false
}
```

Default framing (recommended unless you know the asset's pixel size): just `content_type` + `content_value`.

## Pitfalls

- Partial `aoi*` (three of four values, `null`, `NaN`) means "undefined transform" and the default fill is used
  silently; `scale` alone does nothing for images.
- `isDefaultTransform: true` combined with authored `aoi*` discards your crop on the next layout.
- `assetWidth`/`assetHeight` that do not match the real asset also discard the crop; omit them if unsure.
- `filterBrightness: 0` is treated as "not set" (falsy) and becomes 0.5 inside the filter; use `1` for "unchanged".
- Copying a stored example keeps its `aoi*` for *that* asset; after replacing `content_value`, drop the `aoi*`,
  `scale`, `assetWidth`, `assetHeight`, `filter*` fields unless you intend them.

## Rules and limits

- Default transform (no valid `aoi*`, or `isDefaultTransform: true`): **fill** the box (cover) for images and
  videos without controls, **fit** (contain) for logos and for videos with `assetProps.controls`, capped at scale 1.5.
  Parents can force fit (`fitAsset` option; `ContentElement` forces it for icons). The computed transform is written
  back into the model (`aoiLeft`.., `scale`, `flipHorizontal`, `version: 1`, `assetWidth`, `assetHeight`,
  `isDefaultTransform: true`), so stored examples always carry these fields even when nobody authored them.
- Scale clamps: `minScale` = half of the fit scale, `maxScale` = `max(1.5, fill scale)`; the pan offset is clamped so
  the image keeps covering the frame (or stays inside it when scaled below fit). Values outside are clamped, never
  rejected. A crop that does not fit the box after a layout change is enlarged to at least the fill scale.
- `hasAlpha` / `hasSolidBackground` come from the asset record (set when the asset was uploaded), not from the model.
- The media is always centered on the `aoi*` center; there is no separate offset field.
- Thumbnails/exports load the "xlarge" rendition; the editor starts with "xsmall" and upgrades to the optimal size
  for the rendered area. Nothing to author.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_value` | string | asset id | Read as `assetId` (the field name can be changed by the parent's `bindTo` option; nothing in the templates does). |
| `aoiLeft`, `aoiTop`, `aoiRight`, `aoiBottom` | number | px in the **source asset's** pixel space; may exceed the asset bounds. Default: none | Area of interest: the rectangle of the source image that must be visible. The render scale is derived from it (`max(height / (aoiBottom - aoiTop), width / (aoiRight - aoiLeft))`, clamped to `[minScale, maxScale]`) and the pan offset from its center. The transform is only used when **all four** are finite numbers and `isDefaultTransform` is not `true`. |
| `scale` | number | asset px -> element px | Written by the app together with the `aoi*` values; for images the render scale is recomputed from `aoi*` and the element size, so this is a cache. `VideoElement` reads it for fitted (controls on) videos. |
| `isDefaultTransform` | boolean | default `false` | `true` means "ignore `aoi*`, recompute the default transform on every layout" (the app writes it after resetting a crop). Set to `false` (or omit) to keep an authored crop. |
| `assetWidth`, `assetHeight` | number | px of the source asset | Written with the transform. If present and different from the loaded asset's real size, the stored `aoi*` crop is discarded and the default transform is used (protects against stale crops after an asset swap). |
| `flipHorizontal` | boolean | default `false` | Mirrors the media horizontally. |
| `filter` | string | `"none"` / `null` (default), tone presets `"brannan"`, `"earlybird"`, `"inkwell"`, `"lofi"`, `"mayfair"`, `"nashville"`, color tints `"theme"`, `"accent1"`..`"accent10"`, `"background_accent"` | Image filter. Color tints desaturate and multiply with the palette color. Applied by `Picture` only. |
| `filterStrength` | number | 0-1, default 1 | Opacity of the color tint flood (color filters only). |
| `filterBrightness` | number | linear slope, 1 = unchanged; examples use 0.45-1 | Brightness; any non-zero value turns on the adjustment filter. |
| `filterContrast` | number | 1 = unchanged | Contrast slope. |
| `filterBlur` | number | px std-dev, 0 = none | Gaussian blur. |
| `mediaOpacity` | number | 0-1, default 1 | Opacity of the media only (not of a backdrop). |
| `backgroundColor` | string | palette color or `"none"`; default: the asset's own `imageBackgroundColor` when the asset record has `hasSolidBackground` | Exposed as the element's `backgroundColor` getter; no v10 renderer was found that draws it (not verified to have a visible effect). `Logo` overrides the getter and ignores the field (see `Picture.md`). Visible plates come from parents (`cellColor`, `LogoGridItem`, `LogoElement.showBackdrop`). |
| `altText` | string | default: the asset's alt text, else `""` | `alt` attribute of the rendered image. |
| `enableFaceDetection` | boolean | default `false` | When the default transform is applied and `faceDetectionApplied` is not yet set, runs face detection asynchronously and rewrites `aoi*`/`scale` to frame faces (`faceDetectionApplied: true` is written). Used by the app's generated photo grids and team slides. |
| `faceDetectionApplied` | boolean | written by the app | Marks that face detection already ran. |
| `version` | number | always `1`, written by the app | Transform format version. Not required. |
| `constrainAspectRatio` | string | `"fit"` / `"fill"`; not set by any template | Read by `ContentElement.constrainAspectRatio` from the asset, not the model, except through this field; leave absent. |

Everything else (`content_url`, `previewUrl`, `assetProps`, `kenBurnsEffect`) belongs to the subclasses.

### Nested elements

None. `Picture` and `VideoElement` render the media directly.
