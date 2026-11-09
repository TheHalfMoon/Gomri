# BaseElement

`BaseElement` is the abstract root of every slide element (root elements such as `TextSlide`, `Headline`,
`TextList`, as well as every nested child). It never renders anything itself; it defines how an element is
bound to its model, which generic model fields every element honours, how defaults and migrations are applied,
and how children are created. Every other element doc refers back to this file for the "common fields".

## Model location

- Root element: `states[0].primary` (the class is chosen by the template's `elementType`).
- Slide header: `states[0].header` (Header element, see `Header.md`); tray: `states[0].tray`.
- Child elements: a child created with a `model` option gets that sub-object (e.g. `states[0].primary.image`);
  a child created **without** a `model` option shares its parent's model object. This is very common in the
  text templates: e.g. `Headline` builds its `textFrame` and `TextFrameBox` without a model, so `text`,
  `textAlign`, `backdropColor`, ... are read directly from `states[0].primary`. Each element doc states which
  of its children share the parent model.
- Collection children: `…items[i]` (see `CollectionElement.md`).

## Minimal example

`BaseElement` has no model of its own. Its fields (the full reference below) are set on the element that owns them, e.g.:

```json
{
  "primary": {
    "accentColor": "accent2",
    "decorationStyle": "outlined"
  }
}
```

## Pitfalls

- Do not store the canonical element id in the model (except collection item `id`s): element ids are
  structural (`"text"`, `"textFrame"`, `"image"`) and are chosen by the parent class.
- Do not copy computed/cache fields from stored examples (`blockBounds`, `textStyles`, `blockMargin`,
  `topSpace`, `bottomSpace`, `calculatedWidth`, ...): they are rewritten by the layouter on every render.
- Stored examples often contain `null` entries inside arrays (`items`, `blocks`) and legacy keys
  (`userFontScale`, `verticalGap`, `textStyle`, `styleVariation`, `showLabel`, `showBody`, `description`,
  `label`). They are tolerated by migrations and filters but should never be written by an agent.
- `color: "auto"` is legacy; use `null`/omit for "automatic".
- Leaving `__generateImage` with `isGenerating: true` on an element that already has `content_value` shows an
  endless spinner in the editor until the generation job runs.

## Rules and limits

- **Schema defaults are written into the model.** On every build the class's `static schema` is merged into the
  model with "defaults-deep" semantics (only absent keys are filled). This is why stored slides carry fields you
  did not author (e.g. `backdropPadding: 30`, `showFooter: false`). You may omit them; you may also set them.
- **Migrations.** `BaseElement.migrate()` runs the `_migrate_<version>` chain between the slide's stored
  `migrationVersion` and the current one (`10.03`). Models you create should carry `version: 10`,
  `migrationVersion: 10.03` and `textStylesVersion: 2` so no legacy rewrite runs. Legacy fields documented in
  each element are only rewritten when an older `migrationVersion` is present. `_migrate_10_02` on
  `BaseElement` turns `color: "auto"` into `null`.
- **Text style versions.** When the slide's `textStylesVersion` is not `2`, text styles are looked up as
  `<textStyle>_v<N>` variants (e.g. `heading_v1`); always write `textStylesVersion: 2`.
- `accentColor` resolution walks up the element tree; `TextElement` additionally honours a per-block
  `accentColor` (see `TextElement.md`).
- Layout fit: every element reports `isFit`; a root whose layout does not fit makes the editor refuse the model
  change ("layout error"). Element docs list what makes `isFit` false (usually too many items or too much text).
- Nothing in `BaseElement` validates field types; a wrong type usually surfaces as a render exception in the
  element that reads it.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

These are the only fields `BaseElement` itself reads from `this.model`. Subclasses add their own.

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `accentColor` | string | palette color name; default: parent's `accentColor`, else `"theme"` | Color used for emphasized text (`<font class="emphasized">`) and some decorations. Inherited down the tree, so setting it on the root applies to all nested text. |
| `color` | string \| null | palette color name; `"auto"` is legacy and is rewritten to `null` by migration | Generic per-element user color (decoration / shape color). Most subclasses read it through their own getters; see each element doc. |
| `decorationStyle` | string | `"none"`, `"outlined"`, `"filled"`, `"muted"`, `"fillAndStroke"`; default: parent's value, else the theme's `styleElementStyle` | How framed/decorated children (icon frames, shape frames) are drawn. `frameType: "none"` on the same model forces `"none"`. |
| `isLocked` | boolean | default `false` | Editor-only: prevents selection/edit. No effect on rendering. |
| `groupIds` | string[] | default none | Editor grouping on the authoring canvas only. Do not set on smart-slide elements. |
| `dataSourceLink` | object | `{ dataSourceId, ownerIds, createdBy }`; default none | Live data binding (Google Sheets etc). Leave absent. |
| `__generateImage` | object | `{ search, assetType, isGenerating, ... }` | Marks a media element for server-side image generation (`isGenerating: true` shows a spinner). Only set it when you want the app to generate the image; never leave it on an element you filled yourself. |
| `userFontScale` | object | legacy (`{ "CanvasElement/...": scale }`) | Pre-v10 text scaling by element path. Migrated into `text.blockFontScales`; do not write. |

Color values accepted wherever a "palette color name" is expected: theme palette names (`"theme"`, `"primary"`,
`"secondary"`, `"accent1"`…`"accent8"`, `"chart1"`…`"chart6"`, `"background_light"`, `"background_dark"`,
`"background_accent"`, `"primary_light"`, `"primary_dark"`, `"secondary_light"`, `"secondary_dark"`,
`"positive"`, `"negative"`, `"hyperlink"`), `"black"`, `"white"`, `"neutral"` (white), `"colorful"` (rotates
through the collection colors by item index), shaded ranges `"<base>-to-<shade>"` (e.g. `"theme-to-dark"`,
`"accent1-to-white"`), or any CSS color string (`"#ff0000"`, `"rgb(...)"`). A `"collection…"` id refers to a
theme-defined collection palette. Unknown `accentN` names fall back to `"theme"`.

### Nested elements

- Children are created in `_build()` with `addElement(id, Class, options)`. The child's model is
  `options.model` if given, otherwise the parent's model object (shared). Child ids become the element path
  used for styles and animations; they are not stored in the model.
- `decoration` -> `DecorationElement`: created automatically from theme styles (frames, underline bars, ...);
  no model fields.
