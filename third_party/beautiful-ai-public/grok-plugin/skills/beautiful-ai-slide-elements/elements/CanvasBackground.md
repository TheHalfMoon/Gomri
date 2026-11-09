# CanvasBackground

`CanvasBackground` renders the slide background: a flat palette colour, a theme colour, a theme gradient, a
theme background image / video, or a custom image / video uploaded for this slide, plus an optional theme
overlay (vignette or border) drawn above the content. `CanvasElement` always creates it, with a model it
derives from the slide `layout` (`backgroundColor`, `backgroundStyle`, `customBackgroundImage`). It also
provides the "canvas background colour" every other element uses to pick contrasting colours. It is never a
template's root element.

## Model location

- Not a key of `states[0]`: the three fields live on the slide `layout` object (`layout.backgroundColor`,
  `layout.backgroundStyle`, `layout.customBackgroundImage`) and are copied into the background's model on every
  build.

## Minimal example

Light background (the usual case; both fields may also be omitted to use the theme default):

```json
{
  "layout": { "backgroundColor": "background_light", "backgroundStyle": "backgroundLight" }
}
```

Theme colour fill:

```json
{
  "layout": { "backgroundColor": "accent2", "backgroundStyle": "backgroundColor", "slideColor": "neutral" }
}
```

Custom image background:

```json
{
  "layout": {
    "backgroundStyle": "backgroundImage",
    "backgroundColor": "custom-asset",
    "customBackgroundImage": { "content_type": "image", "content_value": "<asset id>", "colorStyle": "dark", "isCustomAsset": true }
  }
}
```

## Pitfalls

- `backgroundStyle` and `backgroundColor` must agree: `"backgroundColor"` with `"background_light"` renders a
  flat light fill but is read as a "colour" background (gradient themes then swap it for `"theme"`);
  `"backgroundLight"` with `"accent2"` ignores the accent. Write the pairs shown above.
- `"backgroundImage"` / `"backgroundGradient"` with an id that is not in the current theme silently renders a
  light background.
- `"custom-asset"` without `customBackgroundImage` (or without `content_value`) renders nothing behind the
  slide.
- Pick `colorStyle` honestly for custom images: it drives the text / footer colours placed over the picture.
- Do not copy `assetProps`, `assetName`, `content_url`, `aoi*`, `assetWidth` / `assetHeight` from examples;
  they belong to a specific asset.

## Rules and limits

- The canvas background colour (used for contrast decisions, footer logo variant, text colours) is: the
  palette colour of the resolved type for the colour styles; for gradients / images the entry's `colorStyle`
  (`"dark"` → black, `"color"` → theme colour, otherwise white); white-ish light when the id is unknown.
- `allowColorBackgrounds` is declared `false` by many templates (`image`, `collage`, `dashboard` and all
  `chart_*`, `table`, `xygraph`, `vennDiagram`, `target`, `kanban`, `horizontal-task-list`, `aboutUs`, ...) but
  the v10 renderer does **not** enforce it (the check is disabled) and the background picker does not read it:
  a `backgroundColor` style still renders. Treat it as the product's intent: keep those templates on light /
  dark / accent backgrounds.
- `allowBackgroundImage` (true for every template) only gates the editor's "custom background image" button.
- The editor sets `layout.slideColor` to `"neutral"` when choosing a theme colour background and back to
  `"theme"` when returning to light / dark / accent; it is not required but keeps element colours readable
  on a coloured background.
- Theme gradient / image ids are theme-specific uuids: they only make sense with the presentation's theme;
  copying one from an example of another presentation renders a light fill.
- `_migrate_10_02`: on old slides whose `backgroundStyle` held an RGB value it is converted back to the
  matching style name.
- The custom image is loaded through the asset service during the load phase; a `content_value` that does not
  resolve to an asset makes that load fail (the exact failure mode — render error or blank background — is
  not verified).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `backgroundStyle` | string | `"backgroundLight"`, `"backgroundDark"`, `"backgroundAccent"`, `"backgroundColor"`, `"backgroundGradient"`, `"backgroundImage"`; default: the template's `defaultBackgroundStyle` (`"backgroundDark"` for `contactus` / `business_card`, `"backgroundLight"` for `headline_image` / `picture_headline_right`), else derived from the theme's `defaultBackgroundColor` (a gradient id → gradient, an image id → image, `background_light` / `_dark` / `_accent` → the matching style, anything else → `"backgroundColor"`) | What kind of background `backgroundColor` names. Decides which renderer is used. |
| `backgroundColor` | string | depends on `backgroundStyle` (below); default: theme `defaultBackgroundColor` | The colour / asset reference. |
| `customBackgroundImage` | object | media model, see below; default none | The per-slide asset used when `backgroundStyle` is `"backgroundImage"` and `backgroundColor` is `"custom-asset"`. |

How the two fields combine:

| `backgroundStyle` | `backgroundColor` | Rendered as |
|---|---|---|
| `"backgroundLight"` | `"background_light"` (the value is ignored: the style wins) | the theme's light background colour |
| `"backgroundDark"` | `"background_dark"` (ignored) | the theme's dark background colour |
| `"backgroundAccent"` | `"background_accent"` (ignored) | the theme's accent background colour |
| `"backgroundColor"` | a theme colour name: `"theme"`, `"accent1"`…`"accent8"`, `"primary"`, ... (any palette colour name) | a flat fill in that colour; when the theme's `styleBackground` is a gradient and the colour is empty or `background_light`, `"theme"` is used instead |
| `"backgroundGradient"` | the `id` of an entry of the theme's `backgroundGradients` | the theme gradient; an unknown id falls back to a flat light fill |
| `"backgroundImage"` | the `id` of an entry of the theme's `backgroundImages` | the theme image or video (full-bleed, cover-cropped); an unknown id falls back to a flat light fill |
| `"backgroundImage"` | `"custom-asset"` | `customBackgroundImage` rendered full-bleed through a `ContentElement` |

`customBackgroundImage` fields (a `ContentElement` / `MediaElement` model, see `ContentElement.md`,
`MediaElement.md`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` (required) | string | `"image"`, `"video"`, `"stock_video"` | Kind of asset (icons and logos are refused by the editor). |
| `content_value` (required) | string | asset id | The uploaded / generated asset. |
| `colorStyle` | string | `"light"` (default), `"dark"`, `"color"` | How the app should treat the picture when choosing colours of the content on top of it: `"light"` → the canvas background colour is white, `"dark"` → black, `"color"` → the theme colour. |
| `isCustomAsset` | boolean | `true` | Set by the editor; marks the asset as slide-specific. |
| crop / filters | | `aoiLeft`, `aoiTop`, `aoiRight`, `aoiBottom`, `scale`, `isDefaultTransform`, `filter`, `filterBrightness`, `filterContrast`, `filterBlur`, `mediaOpacity`, `flipHorizontal` | Optional, see `MediaElement.md`; omit to get the default cover crop. |

### Nested elements

- `background` -> one of (no model of their own): `BackgroundColor` (flat fill), `BackgroundGradient` /
  `BackgroundGradientReverse` (flat fill plus a dark ramp, only when the theme stylesheet gives the style a
  `gradient` / `reverseGradient` effect), `CustomBackgroundGradient` (theme gradient), `ThemeBackgroundImage`
  (theme picture), `ThemeBackgroundVideo` (theme video), `CustomBackgroundImage` (the slide's own asset,
  rendered by a `ContentElement`).
- `overlay` (added by `CanvasElement` above the content) -> `VignetteOverlayElement` or `BorderOverlayElement`,
  only when the theme stylesheet gives the current style the effect `vignette`, `greyBorder`, `whiteBorder` or
  `colorBorder`. The default stylesheet has no effects, so normally there is no overlay. Nothing to author.
