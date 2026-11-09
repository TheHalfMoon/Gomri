# LogoGrid

`LogoGrid` arranges up to 30 logos in an automatic box grid; each logo sits on an optional white plate with an
optional thin frame and is fitted (never cropped) into its box. It is the root element of the `logogrid` template.
Items are `LogoGridItem`s (folded below).

## Model location

- `states[0].primary` - the grid.
- `states[0].primary.items[]` - one logo. The item's `ContentElement` (`logo`) and its `Logo` picture share the item
  object, so the media fields sit directly on the item.

## Minimal example

```json
{
  "header": { "text": { "blocks": [ { "type": "text", "textStyle": "heading", "html": "Our partners" } ] } },
  "primary": {
    "showFrame": true,
    "showBackdrop": true,
    "defaultLogoScale": 0.8,
    "items": [
      { "content_type": "logo", "content_value": "b1d101eb2360dfccc208cf9ff35cf26c889b6b7aa0d6d5ee6737d39c22b5c520-L" },
      { "content_type": "logo", "content_value": "45056fdc1d369ece510e7d4acf81b98650415c7b109a88e7f529da84c85e83c5-L" },
      { "content_type": "logo", "content_value": "93411fffc39f284c7711f1e1d866845b7fbae595ac568a6dc87c64c975eb3753-L" }
    ]
  }
}
```

## Pitfalls

- Use logo assets (`assetType: "logo"` when creating them, ids ending in `-L`); a photo id with
  `content_type: "logo"` is fitted and plated like a logo, which usually looks wrong.
- `maxItemCount` (30) is only enforced by the editor's add/paste actions; all authored items render, and more than
  ~12 get very small cells.
- `content_value: ""` is a valid "empty slot" (template default) and shows a placeholder - fill every slot or drop
  the item.
- Do not carry `aoi*` from one logo to another: the stored fit transform is asset-specific and is discarded when
  `assetWidth`/`assetHeight` differ.
- `showBackdrop: false` on a dark slide hides dark logos; keep the plate or choose a light slide background.

## Rules and limits

- Layout is the shared box-grid layouter (`calcBoxGridLayout`): equal cells, rows/columns chosen from the item
  count and the available size; no `gridLayout` field - cell geometry is not authorable.
- The logo is fitted at `defaultLogoScale` of its cell; the white plate is the item's own rect decoration
  (`showBackdrop`), drawn for every item regardless of whether the logo has transparency.
- Slide background: the app's generator sets the slide `layout.backgroundColor` to `background_accent` so white
  plates stand out; not required.
- Template flags: `variations: "list"`, `availableTrayLayouts: []` (no trays), `allowColorful: false`; header
  allowed (examples use `top` and `left`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Grid (`states[0].primary`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 30 | Logos in reading order. Template default: six items `{ content_type: "logo", content_value: "" }`. The app's generator caps at 12. |
| `showBackdrop` | boolean | default `true` | White plate behind every logo (`false` -> transparent cells). |
| `showFrame` | boolean | default `false` (template default `true`) | 1 px stroke (`secondary_dark` at 10 % alpha) around every cell. |
| `defaultLogoScale` | number | 0-1, default 0.66 (template default 0.8) | Fraction of the cell the logo is fitted into when it has no stored crop. |
| `collectionColor` | string | palette color | Written by migration; logos do not use it visually. |
| `backgroundColor` | string | | Seen once in examples at grid level; not read. |

Logo (`items[]`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"logo"` (default via `defaultAssetType`), `"image"` also works | Use `"logo"` for the fit/plate behavior (see `Picture.md`, "Logos"). |
| `content_value` | string | logo asset id (`<hex>-L`) | Empty string / absent -> add-logo placeholder in the cell. |
| `aoi*`, `scale`, `flipHorizontal`, `assetWidth/Height`, `assetName`, `assetProps`, `mediaOpacity`, `isDefaultTransform` | | see `MediaElement.md` | Stored fit transform. Logos clamp `maxScale` to the fit scale, so `aoi*` can only shrink or pan a logo. |
| `__generateImage` | object | `{ search, assetType: "logo", isGenerating, imageIntent }` | The generator's logo request (see `ContentElement.md`); remove when `content_value` is set. |
| `backgroundColor` | string | schema default `"white"` | Written into every item by the item schema and by the generator; the `Logo` picture ignores it (its plate comes from `showBackdrop`). Harmless. |
| `content_attribution` | string | | Carried, not rendered. |

### Nested elements

- `items[]` -> `LogoGridItem` (folded here; `maxItemCount` 30, array order). Each item creates a rect decoration
  (fill white or transparent per `showBackdrop`, stroke per `showFrame`) and one child `logo` ->
  `ContentElement.md` with `defaultAssetType: "logo"` and the grid's `defaultLogoScale`, which builds `Logo`
  (`Picture.md`).
