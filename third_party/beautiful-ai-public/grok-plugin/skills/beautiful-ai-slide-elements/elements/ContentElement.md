# ContentElement

`ContentElement` is the generic media slot: it reads `content_type` from its model and builds exactly one child asset
element for it (`Picture` for images, `Logo` for logos, `Icon` for icons, `VideoElement` for videos). It has no
visible chrome of its own; framing and backdrops come from the parent (`FramedMediaElement`, `TextAndImage`, ...).
It is never a root element. Parents that use it: `TextAndImage` (as `contentElement`), `FramedMediaElement` (as
`content`), `LogoGridItem` (as `logo`), `Ornament`, `TableCellIcon`, `ContactInfo`, `PresentationTitleImage`,
`SequenceItem`, `JourneyIconMarker`, `PyramidIcon`, `PictureOrgChartNode`, `GanntChartMediaElement`,
`ConnectionSourceItem`.

## Model location

`ContentElement` almost never has a model object of its own: the parent passes no `model` option, so it reads and
writes **the parent's model**. The media fields therefore sit directly on the parent's model, e.g.:

- `states[0].primary.items[].childElement` (a `TextAndImage` cell of `collage`, `image`, `dashboard`, trays)
- `states[0].primary.items[]` (a `Team`, `PhotoTextList`, `LogoGrid`, icon list item: the item model is shared down
  through `FramedMediaElement` -> `ContentElement` -> `Picture`/`Icon`)
- `states[0].primary.items[].content` / `.logo` (`UserTestimonial` attribution, which does pass sub-models)

The only exceptions are parents that pass an explicit `model:` (e.g. `UserTestimonialAttribution` passes
`model.content` and `model.logo`).

## Minimal example

```json
{
  "content_type": "image",
  "content_value": "27e64e20b02112994e8a91b8a11586434b89bf2d44c8bac38fccbc42d010df9e-I"
}
```

Icon slot:

```json
{
  "content_type": "icon",
  "content_value": "thumbs-up",
  "iconColor": "accent1"
}
```

## Pitfalls

- Never leave `__generateImage` on an element you filled with a `content_value`; also do not add
  `__generateImage: { isGenerating: true }` unless you want the app to generate the asset.
- Do not invent `content_value`s: an image id that does not resolve makes the slot fall back to the placeholder
  overlay; an icon key that does not exist renders nothing (no error).
- Set `content_type` explicitly. A missing `content_type` is interpreted as the parent's default (`"logo"` in a
  LogoGrid, `"icon"` in icon lists, `"image"` elsewhere), and a value that does not match the asset id kind (e.g.
  `"icon"` with an image id) loads nothing.
- `content_type: "logo"` and `"image"` both load through the image asset store: a logo id (`-L`) with
  `content_type: "image"` works but loses the logo fit/backdrop behavior; see `Picture.md`.
- Crop fields from another asset (`aoi*`, `assetWidth`, `assetHeight`) are discarded when they do not match the new
  asset's pixel size; when swapping `content_value`, remove them (or just omit them) and the default framing is
  recomputed.
- `frameType` / `decorationStyle` written on this model are ignored when the parent defines them (they do in all
  the list/grid parents); set them on the parent (`FramedMediaElement` item, `TextAndImage` cell) instead.

### Note: ContentItem

`ContentItem` is unrelated to `ContentElement` despite the name: it is the node of the collection-based diagrams
(hub-and-spoke, icon circle, timeline milestones), see `ContentItem.md`. Its media node types hold a
`FramedMediaElement` whose media fields live on the node item itself (`content_type`, `content_value`).

## Rules and limits

- Size: the element fills the size its parent gives it; the asset child is centered in it. Icons are always "fit"
  (whole glyph visible); images fill by default (see `MediaElement.md`). Logos report a 200x200 content size.
- `hasValidAsset`: for `"image"`, `"logo"`, `"icon"` and for a missing `content_type` it requires a non-empty
  `content_value` **and** a successfully loaded asset (a `Picture` whose load failed makes it invalid -> placeholder
  overlay). For `"video"`/`"stock_video"` it is always true.
- Background/alpha: `isBackgroundVisible` is true for icons, for assets with alpha (`hasAlpha` on the asset record),
  and for images scaled below fill when `allowImageScaling` is on. `hasSolidBackground` comes from the asset record
  (`hasSolidBackground` / `imageBackgroundColor`), not from the model. Logos never get a dark overlay color; images
  with a `content_value` (or a generating `__generateImage`) set the element's background color to
  `"background-image"` (dark), which is why text over an image resolves to white.
- Icon coloring (`_applyColors`): with a filled, colored decoration the icon becomes `primary` on that color; with a
  `muted` / `fillAndStroke` decoration it takes the decoration color; without decoration and with `allowColorOnColor`
  it uses `iconColor ?? color ?? collectionColor`. Otherwise `Icon` picks its own color (see `Icon.md`).
- Migration `_migrate_10_02`: on authoring canvases, icons get `iconColor = color` and `color` is deleted.
- Export/import: `content_type`, `content_value`, `assetName`, `assetProps` plus every other model field except
  `frameType` and `text` travel with the asset when a slide is converted between templates.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"image"`, `"logo"`, `"icon"`, `"video"`, `"stock_video"`. Default: the parent's `defaultAssetType` option, else `"image"` | Picks the asset element class: `"image"` -> `Picture`, `"logo"` -> `Logo`, `"icon"` -> `Icon`, `"video"`/`"stock_video"` -> `VideoElement`. Other `AssetType` values (`"mixed"`, `"audio"`, `"map"`, `"font"`, `"svg"`) build nothing. |
| `content_value` | string | Asset id for images/logos/videos (ids look like `<hex>-I`, `<hex>-L`, `<id>` for uploads, `<hex>-S_V` for stock video); icon key for icons (a key of the built-in icon catalog, e.g. `"star"`, `"thumbs-up"`). Default: none | The asset reference. Empty/absent for image, logo, icon (or no `content_type`) -> `hasValidAsset` is false and the slot renders the "add media" placeholder overlay. For videos the element is considered valid even when empty. |
| `__generateImage` | object | `{ search, assetType, isGenerating, imageIntent, searchStock, pickIndex, imageSource, imageStyle, aspectRatio, ... }` | Request for the app/server to fill `content_value` with a generated or searched asset. While `isGenerating` is `true` the element renders a progress spinner ("Generating Image..." or "Picking Team Asset" when `imageSource` is `"team"`) instead of its asset, and `TextAndImage` counts the cell as "has image". **Authors who set `content_value` themselves must delete this object**; a leftover one re-triggers generation or shows a spinner forever. |
| `iconColor` | string | Palette color name (`"primary"`, `"secondary"`, `"theme"`, `"accent1"`..`"accent10"`, `"white"`, `"black"`, ...). Default: see `Icon.md` | Icon color when `content_type` is `"icon"`. Read before `color`. |
| `color` | string | palette color name | Fallback for the icon color (`iconColor ?? color ?? parent collection's collectionColor`). Legacy; `_migrate_10_02` copies `color` to `iconColor` for icons on authoring canvases. |
| `frameType` | string | `"theme"` (resolve to the theme's `styleShape`), a DeviceFrames id, or absent | Only consulted when the parent has no `frameType` of its own; the parent's value wins. |
| `decorationStyle` | string | `"filled"`, `"outlined"`, `"muted"`, `"fillAndStroke"`, `"none"` | Used only when `frameType` is set *and* is a Shape frame (`rect`, `circle`, `rounded_rect`, `octagon`, `none`); otherwise the parent's `decorationStyle` wins. |
| `assetName` | string | free text | Display name carried along with the asset (export/import, image block labels). Not needed for rendering. |
| `assetProps` | object | see `VideoElement.md` | Playback settings and `originalSize` for videos. Carried but ignored for images. |

All crop/scale/filter fields (`aoiLeft`..`aoiBottom`, `scale`, `flipHorizontal`, `filter`, `filterBrightness`,
`filterContrast`, `filterBlur`, `filterStrength`, `mediaOpacity`, `assetWidth`, `assetHeight`, `isDefaultTransform`,
`kenBurnsEffect`, `enableFaceDetection`, `altText`) are read by the asset child, see `MediaElement.md`,
`Picture.md`, `VideoElement.md`; `iconScale` is read by `Icon.md`. `deleteAsset()` (the UI "remove image" action)
deletes `content_value`, `content_type`, `aoi*`, `assetProps`, `assetName`, `assetWidth`, `assetHeight`, `filter`,
`filterBlur`, `filterContrast`, `scale`, `mediaOpacity`.

### Nested elements

- `asset` -> `Picture.md` when `content_type` is `"image"` (options: `allowImageScaling` default true, `allowBackdrop`
  from parent).
- `asset` -> `Logo` (see `Picture.md`, section "Logos") when `content_type` is `"logo"`; default scale 0.66 unless the
  parent passes `defaultLogoScale` (LogoGrid passes its `defaultLogoScale`).
- `asset` -> `Icon.md` when `content_type` is `"icon"`.
- `asset` -> `VideoElement.md` when `content_type` is `"video"` or `"stock_video"`.

The child is rebuilt whenever `content_type` changes; its type is decided at build time from
`content_type || options.defaultAssetType || "image"`.
