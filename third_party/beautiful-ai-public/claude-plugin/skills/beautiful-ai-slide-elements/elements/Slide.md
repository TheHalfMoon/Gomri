# Slide

The slide model is the JSON document stored per slide. It is rendered by `CanvasElement`, the invisible root
element that every template shares: it draws the background, then places the template's root element (the
"primary" element) and the optional wrappers around it (header, side tray, footer, bottom text block /
attribution, callouts, video overlay). No template names `CanvasElement`; the template only decides which class
renders `states[0].primary` and which wrappers it permits through its capability flags (`allowHeader`,
`allowFooter`, `availableTrayLayouts`, ...).

## Model location

- The whole slide document. `CanvasElement` reads `states[0]` as its map of element models (`header`, `primary`,
  `tray`, ...) and the top-level `layout` object as its layout switches. Only `states[0]` is rendered; the array
  always has one entry.

## Minimal example

A `textlist` slide with a top header, a left image tray and the default (theme) footer:

```json
{
  "template_id": "textlist",
  "template_version": 1,
  "version": 10,
  "migrationVersion": 10.03,
  "textStylesVersion": 2,
  "hasBeenEdited": true,
  "layout": {
    "headerPosition": "top",
    "trayLayout": "left_tray",
    "showFooter": "theme",
    "elementTextBlockPosition": "none",
    "backgroundColor": "background_light",
    "backgroundStyle": "backgroundLight"
  },
  "states": [
    {
      "header": {
        "text": {
          "blocks": [
            { "id": "h1", "type": "text", "textStyle": "heading", "html": "Create a theme in minutes" },
            { "id": "h2", "type": "text", "textStyle": "body", "html": "Polished, professional and on brand." }
          ]
        }
      },
      "tray": {
        "trayWidth": 440,
        "items": [
          {
            "id": "t1",
            "componentType": "TextAndImage",
            "cellColor": "background_accent",
            "childElement": { "content_type": "image", "content_value": "<asset id>" }
          }
        ]
      },
      "primary": {
        "listStyle": "bullets",
        "items": [
          {
            "id": "i1",
            "text": {
              "blocks": [
                { "id": "b1", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Upload your logo" },
                { "id": "b2", "type": "text", "textStyle": "bulleted", "listStyle": "bullets", "indent": 0, "html": "Set the typography styles" }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

(`primary` follows `TextList.md`; every other template has its own root element doc.)

## Pitfalls

- A header is drawn by default: on any template with `allowHeader` (all but `title`, `headline2`, `section`,
  `headline`, `chapter`, `headline_image`, `picture_headline_right`, `contactus`, `business_card`, `ppt-slide`,
  `slidePlaceholder`, `action-text`) an absent `headerPosition` means `"top"` and an empty header box is
  rendered. Write `"headerPosition": "none"` when you do not want one.
- `trayLayout` outside `availableTrayLayouts` is silently dropped; `states[0].tray` then stays in the model
  but is never rendered. Check the template before adding a tray.
- `showFooter: true` / `false` (booleans, found in old stored slides) are not `"on"` / `"off"`: both fall
  through to the theme default. Use the strings.
- `elementTextBlockPosition: "tray"` suppresses the footer; `"inline"` does not.
- Omitting `migrationVersion` or `textStylesVersion` is not neutral (migrations run; legacy text sizes apply).
- `hasBeenEdited: false` can get your model replaced by the theme's default slide for that template.
- `states[0].callouts` / `annotations`: do not copy them from examples unless you intend the callouts; an
  empty `{ "elements": [] }` is created automatically.
- Stored examples carry `layout` keys the renderer ignores (`showAttribution`, `showElementTitle`,
  `showHeader`) and sometimes a `layout` or `elementTitle` key inside `states[0]`: never copy them.

## Rules and limits

- Canvas size is 1280 x 720 px. All widths below are in that space.
- **Header.** `"top"`: full content width, height from its text, capped at canvas height minus the primary
  element's minimum height (minus 40 px when a footer shows, minus the text block height when one is set).
  `"left"`: a column of `layout.headerWidth` px, vertically centred; the primary element gets the rest.
- **Side tray.** `left_tray` / `right_tray` take the full canvas height at the edge, `tray.trayWidth` wide
  (default 440) and the content area (header, primary, text block) is the remainder; the footer keeps the full
  canvas width. `left_inline` / `right_inline` sit inside the primary area (below the header, inside the canvas
  margins) with a 40 px gap to the primary element. A `trayLayout` that is not `"none"` and not in the
  template's `availableTrayLayouts` is logged, reset
  to `"none"` in the model and the tray is not built (no error, the tray just disappears). Templates with
  `availableTrayLayouts: []` (no tray at all) include `image`, `collage`, `headline2`, `section`, `title`,
  `timeline`, `journey`, `cycle_diagram`, `connection_diagram`, `swot_diagram`, `logogrid`, `textgrid_photos`,
  `product_laptop`, `contactus`, `authoring`, `sequence`, `puzzle`, `horizontal-funnel`, `action-number`;
  `arrow_bars` allows only `right_tray` / `right_inline`; every other template allows all four.
- **Footer.** Needs the template's `allowFooter` (false for `title`, `ppt-slide`, `slidePlaceholder`), and is
  impossible while `elementTextBlockPosition` is `"tray"` (or `trayLayout` is `bottom_tray`). It is a 50 px
  strip across the bottom of the canvas; the primary element gives up 40 px when it reserves footer space.
- **Text block / attribution.** `"inline"` text sits below the primary element inside the content area;
  `"tray"` is a full-width band at the bottom of the content area; the attribution is a right-aligned line
  at the bottom of the primary area (50 px side margins). They are only offered by the editor when the
  template allows them (`allowElementTextInline` / `allowElementTextTray` / `allowElementAttribution`, all
  false for `title`, `contactus`, `business_card`, `authoring`, `ppt-slide`, `slidePlaceholder`; attribution
  also false for `agenda`, `image`, `wordCloud`, `picture_picture`, `imagegrid`, `culturegrid`, `aboutUs`),
  but `CanvasElement` builds them whenever `layout` asks for them.
- **Fit.** Every wrapper takes space from the primary element; when the primary element cannot fit in what is
  left it reports `isFit: false` and the editor rejects the model ("layout does not fit"). "Not enough space
  for secondary items" is only a logged warning.
- **Versions.** Migrations run for every version in `(migrationVersion, 10.03]`; with `migrationVersion: 10.03`
  none run. `migrationVersion` smaller than `version` is raised to `version`; `migrationVersion` without
  `version` is dropped. A missing `textStylesVersion` is filled with `1`, not `2`.
- `CanvasElement` migrations: `_migrate_10_02` forces `headerPosition: "none"` and `showFooter: "off"` on
  `authoring` slides (the classic canvas draws its own header / footer); `_migrate_10_03` moves
  `annotations.videoOverlay` to `videoOverlay`.
- The app normalizes a missing `layout` to `{}` when it loads a stored slide; if a model without `layout`
  reaches the renderer anyway, the render fails with "Cannot open presentation due to an error".

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Top-level fields:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `template_id` (required) | string | a template id (`list_slide_templates`); an unknown id renders the `slidePlaceholder` template | Picks the template: the root element class for `states[0].primary`, its `defaultData` and its capability flags. |
| `states` (required) | object[] | exactly one object | `states[0]` holds the element models (keys below). |
| `layout` (required) | object | may be `{}` (all defaults); fields below | Slide-level layout: header position, tray layout, footer, background, text block. The app substitutes `{}` when it is missing, but always write it. |
| `version` | number | `10` | App version of the model format. Rewritten to `10` on every render; `create_slide` sets it when absent. |
| `migrationVersion` | number | `10.03` | Highest migration already applied. When absent it defaults to `version` (10), which makes the `10.01`–`10.03` migrations run over your model (they rewrite legacy fields and may add `accentColor` etc.). Write `10.03`. |
| `textStylesVersion` | number | `2` | Text style generation. Absent = `1`: every text block is styled with the legacy `_v1` sizes. Write `2`. |
| `template_version` | number | the template's own version: `1` for almost all templates, `2` for `section`, `wordCloud`, `chapter`, `picture_headline_right`, `8` for `contactus` | Bookkeeping; no v10 template defines a template migration, so it is never read at render time. |
| `hasBeenEdited` | boolean | write `true` | When `false` and the theme defines a default slide for this `template_id` (`theme.defaultSlides`), the renderer replaces your whole model with the theme's default slide. |
| `animations` | object | optional, default `{}` | Per-element animation settings; not covered by this skill. Leave absent. |
| `metadata` | object | optional | Generation bookkeeping (`isGenerating`, `slidePrompt`, `generateError`, `wasAiGenerated`, `needsLayoutProcessing`). A slide whose `template_id` is `"ai-generation"` is a placeholder: it renders a "Generating slide..." screen (an error screen when `generateError` is set), and the slide navigator shows it as generating, without a thumbnail, while `isGenerating` is `true`. The presentation building skill starts a new deck with such placeholders and fills each with `update_slide`, sending `metadata` with `isGenerating: false`. |
| `slide_notes` | string | optional | Speaker notes; not rendered on the canvas. |
| server fields | | `id`, `presentationId`, `createdAt`, `createdBy`, `modifiedAt`, `modifiedBy`, `_changeId`, `_id` | Set by the server; `create_slide` / `update_slide` strip them. Never author. |
| `libraryItemId` | string | only in stored slides | Ties a slide to a shared slide of the team's library, whose content it shows (`get_slide` returns that content); only the app sets it, `create_slide` strips it. Such a slide takes no changes as it is: `update_slide` with `libraryItemId: null` converts it into a regular slide owning a copy of the content (it stops following the shared slide; tell the user), applying the other fields sent on top. A slide whose `libraryItemId` is its own id is the shared slide itself and cannot be converted: add a regular slide from its model with `create_slide` and remove it with `update_presentation`. Never author a value. |
| deck fields | | `isSkipped`, `advanceOn`, `advanceDelay`, `assignedUser`, `isGallerySlide`, `sharedModel`, `assets`, `timeline` (legacy), `clientId` | Presentation / editor bookkeeping found in stored slides. Never author. |

Keys of `states[0]` (which element renders each key):

| Key | Element | Built when | Reference |
|---|---|---|---|
| `primary` (required) | the template's `elementType` class | always (an empty `{}` is created when missing, which renders the element's defaults) | the template's root element doc |
| `header` | `Header` | `layout.headerPosition` resolves to `"top"` or `"left"` (`{}` created when missing) | `Header.md` |
| `tray` | `SideBarContainer` | `layout.trayLayout` resolves to a side tray (`{}` created when missing) | `SideBarContainer.md` |
| `footer` | `Footer` | the footer is shown (see `layout.showFooter`) | `Footer.md` |
| `elementTextBlock` | `BottomTray` for `"tray"`, `ElementTextBlock` for `"inline"` | `layout.elementTextBlockPosition` is not `"none"` | `BottomTray.md` |
| `elementAttribution` | `ElementAttribution` | `layout.showElementAttribution` is `true` | `BottomTray.md` |
| `callouts` | `CalloutsCanvas` | the template's `allowCallouts` is not `false` (all but `ppt-slide`, `flow_chart`, `authoring`); seeded as `{ "elements": [] }` (or from legacy `annotations`) when missing | `CalloutsCanvas.md` |
| `videoOverlay` | `VideoOverlay` | present (`{ videoAssetId, x, y }`, `x`/`y` are 0–1 fractions of the canvas) | not documented here; leave absent |
| `annotations` | legacy | pre-callouts annotations; `annotations.videoOverlay` is moved to `videoOverlay` by migration | never author |
| `background` | – | not a key: the background model is derived from `layout` on every build | `CanvasBackground.md` |

Fields of `layout` read by `CanvasElement` and `CanvasBackground`:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `headerPosition` | string | `"top"`, `"left"`, `"none"`; default `"top"` when the template allows a header, forced `"none"` when it does not | Where the slide header goes. `"right"`, `"bottom"`, `"center"` exist in the enum but `CanvasElement` only lays out `top` and `left`: do not use them. |
| `headerWidth` | number (px) | default `400`; editor allows 50–640 (drag: 200–640) | Width of the header column when `headerPosition` is `"left"`. Ignored for `"top"`. |
| `trayLayout` | string | `"none"`, `"left_tray"`, `"right_tray"`, `"left_inline"`, `"right_inline"`; default `"none"` (no template sets `defaultTrayLayout`) | Side tray layout. Must be listed in the template's `availableTrayLayouts`; otherwise it is reset to `"none"` (see Rules). `"bottom_tray"`, `"top_tray"`, `"background"` are enum values no template allows. |
| `showFooter` | string | `"theme"`, `"on"`, `"off"`; default = theme behaviour | `"on"` always shows the footer, `"off"` never; `"theme"`/absent shows it only when the theme's `showFooterByDefault` is `true` and the template's `preventDefaultFooter` is `false`. Legacy booleans are not understood (see Pitfalls). |
| `elementTextBlockPosition` | string | `"none"`, `"inline"`, `"tray"`; default `"none"` | Adds a text area under the primary element: `"inline"` = plain text block (`ElementTextBlock`), `"tray"` = full-width coloured bottom tray (`BottomTray`). Legacy `"above"` → `"none"` and `"below"` → `"inline"` are rewritten by migration; `"grid"` is not supported. |
| `showElementAttribution` | boolean | default `false` | Adds the footnote / attribution text line (`ElementAttribution`) at the bottom of the primary area. |
| `backgroundColor` | string | `"background_light"`, `"background_dark"`, `"background_accent"`, a theme colour name (`"theme"`, `"accent1"`…), a theme gradient / background image id, or `"custom-asset"` | Slide background colour or asset; interpreted together with `backgroundStyle`. See `CanvasBackground.md`. |
| `backgroundStyle` | string | `"backgroundLight"`, `"backgroundDark"`, `"backgroundAccent"`, `"backgroundColor"`, `"backgroundGradient"`, `"backgroundImage"`; default: template `defaultBackgroundStyle`, else derived from the theme's default background | Which kind of background `backgroundColor` names. See `CanvasBackground.md`. |
| `customBackgroundImage` | object | media model (`content_type`, `content_value`, `colorStyle`, ...) | The per-slide background asset used when `backgroundColor` is `"custom-asset"`. See `CanvasBackground.md`. |
| `slideColor` | string | palette colour name or `"colorful"`; default theme `defaultSlideColor`, else `"theme"`; `"neutral"` is read as `"primary"` | Default accent / decoration colour of the slide, used by elements and migrations that have no colour of their own. |
| legacy, ignored | | `showHeader`, `showElementTitle`, `showAttribution`, `showElementCaption` | Pre-v10 switches still present in stored slides; rewritten or dropped by migration. Never write them. |

### Nested elements

- `background` -> `CanvasBackground` (always; model built from `layout.backgroundColor` / `backgroundStyle` /
  `customBackgroundImage`), see `CanvasBackground.md`.
- `header` -> `Header.md`; `primary` -> the template's root element; `tray` -> `SideBarContainer.md`;
  `footer` -> `Footer.md`; `elementTextBlock` -> `BottomTray.md` (both forms); `elementAttribution` ->
  `BottomTray.md`; `callouts` -> `CalloutsCanvas.md`; `overlay` -> a theme-driven vignette / border overlay
  with no model (`CanvasBackground.md`); `videoOverlay` -> `VideoOverlay` (no doc).
- Draw order (back to front): background, header, tray, primary, footer, elementTextBlock, elementAttribution,
  overlay, callouts, videoOverlay. With a background overlay the header is drawn above the overlay.
