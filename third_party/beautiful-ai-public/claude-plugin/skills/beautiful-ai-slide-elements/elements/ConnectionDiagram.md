# ConnectionDiagram

`ConnectionDiagram` shows one `target` node (a framed text/image box, a `TextAndImage.md`) connected by flat
ribbon paths to a list of source items (`column1`), and in `"many-to-many"` style a second list (`column2`) on the
other side. It is the root element of template `connection_diagram`. The ribbons are computed from the item
positions (no connector model). Internal classes documented here: `ConnectionSourceList` (a column collection),
`ConnectionSourceItem` (an item: text + number/letter/icon marker), `ConnectionTarget` (the target wrapper),
`ConnectionTargetContents` (the `TextAndImage` inside it) and `ConnectionHeader` (optional column header texts).

## Model location

- `states[0].primary` - the diagram (root of `connection_diagram`).
- `states[0].primary.column1` - first `ConnectionSourceList` (`{ items, labelType, collectionColor, decorationStyle }`).
- `states[0].primary.column2` - second list, only used (and created) when `style` is `"many-to-many"`.
- `states[0].primary.column1.items[]` / `column2.items[]` - `ConnectionSourceItem`s.
- `states[0].primary.target` - the `ConnectionTarget` model (a `TextAndImage` model: `text`, `frameType`, ...).
- `states[0].primary.sourceHeader` / `targetHeader` / `source2Header` - `{ blocks }` header texts, only when
  `showHeaders` is `true`.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "html": "Where the budget goes", "type": "text", "textStyle": "heading" }] } },
  "primary": {
    "style": "many-to-one",
    "show3DEffect": false,
    "showHeaders": false,
    "extendToEdge": true,
    "column1": {
      "collectionColor": "theme-to-dark",
      "decorationStyle": "filled",
      "labelType": "none",
      "items": [
        { "text": { "blocks": [{ "html": "Payroll &amp; benefits", "type": "text", "textStyle": "title" }] } },
        { "text": { "blocks": [{ "html": "Marketing", "type": "text", "textStyle": "title" }] } },
        { "text": { "blocks": [{ "html": "Software &amp; infrastructure", "type": "text", "textStyle": "title" }] } },
        { "text": { "blocks": [{ "html": "Operations", "type": "text", "textStyle": "title" }] } }
      ]
    },
    "target": {
      "frameType": "circle",
      "frameColor": "accent3",
      "text": { "blocks": [{ "html": "Operating expenses", "type": "text", "textStyle": "title" }] }
    }
  }
}
```

For `"many-to-many"` add a `column2` with the same shape; for `labelType: "icon"` give each item
`"content_type": "icon", "content_value": "<icon key>"`.

## Pitfalls

- `column2` is only rendered with `style: "many-to-many"`; in the other styles it is dead data (and `defaultData`
  ships one anyway).
- `target.text` is required for a sensible result; `target` itself is created empty when missing and then shows the
  placeholder. Do not put the target text in `column1`.
- Leave `showHeaders` false; header texts are not laid out correctly in two of the three styles.
- Icons live on the items (`content_type`/`content_value`), but only show when the **column's** `labelType` is
  `"icon"`; `labelType` per item does nothing.
- Long first blocks make thick ribbons (ribbon height = first block height + 40px); put detail in a second `body`
  block, which stays outside the ribbon.
- 7+ items per column scale everything down; 3-5 reads best.

## Rules and limits

- Source lists scale down (text and markers) when the items do not fit the column height.
- Ribbons: one per item, three segments (horizontal under the text, diagonal to the target column, horizontal into
  the target center); their thickness is the first text block's height + 40px, capped so all ribbons fit the target
  height. They are masked to stop at the target's center line.
- Column widths: `"many-to-many"` 25% / 25% * `targetScale` / 25%; one-sided styles 40% source, 30% * `targetScale`
  target.
- `_importFromSharedModel` always produces `style: "one-to-many"` and maps node types to `labelType`
  (`lettered-text` -> `"letter"`, `numbered-text` -> `"number"`, `content-and-text` -> `"icon"`).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `style` | string | `"many-to-many"` (default via schema and `defaultData`), `"one-to-many"`, `"many-to-one"` | `"one-to-many"`: target on the left, `column1` on the right (ribbons fan out). `"many-to-one"`: `column1` on the left, target on the right. `"many-to-many"`: `column1` left, target center, `column2` right. |
| `column1` (required) | object | `{ items: [...], labelType, collectionColor, decorationStyle }` | Source list; created as `{}` when missing (then one empty item). |
| `column2` | object | same shape | Second source list for `"many-to-many"`; ignored otherwise (the UI copies `column2` into `column1` when switching to a one-sided style). |
| `target` (required) | object | `TextAndImage.md` model; `defaultData`: `{ frameType: "circle", text: { blocks: [{}] } }` | The hub. See "target model" below. |
| `show3DEffect` | boolean | default `true` | Darkens the diagonal ribbon segment by 15% for a folded-ribbon look. |
| `extendToEdge` | boolean | default `false` | Extends each item's ribbon to the slide edge behind the source column ("full bleed"). |
| `showHeaders` | boolean | default `false` | Builds `sourceHeader`, `targetHeader` (and `source2Header`) texts above the columns. The UI toggle is disabled; the layout for headers is only partially implemented (`"many-to-one"` reserves space, the others overlap). Leave `false`. |
| `targetScale` | number | default `1` (UI slider 0.5-1.5 is disabled) | Multiplies the target column width (25% of the width in `"many-to-many"`, 30% otherwise). |
| `columns` | number | default `2` | Read by a getter, unused. |

#### column model (`ConnectionSourceList`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | 1-10 items | Sources, top to bottom. |
| `labelType` | string | `"letter"` (default), `"number"`, `"icon"`, `"none"` | Marker before each item's text: A,B,C / 1,2,3 (computed, 50px circle), the item's icon (70px), or nothing. |
| `collectionColor` | string | default `"theme"`; `defaultData` `"theme-to-dark"` | Ribbon/marker colors for this column (see `CollectionElement.md`). |
| `decorationStyle` | string | `"filled"` (`defaultData`), `"outlined"`, `"muted"`, `"fillAndStroke"` | Ribbon fill style; `"outlined"` also fills the marker circle with the item color. |

#### items[] model (`ConnectionSourceItem`)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }`, see `TextElement.md`; freeform structure, default block style `title`, allowed `title` and `body` | Item text. The ribbon height follows the **first** block's height; extra blocks hang below it on a canvas-colored background. |
| `content_type`, `content_value` | string | `"icon"` + icon key, see `ContentElement.md` | The marker when the column's `labelType` is `"icon"` (a `ContentElement` built on the item model). |
| `color` | string | palette color name | Per-item ribbon/marker color. |
| `hilited` | boolean | | Emphasis (ribbon colors use the hilite state). |
| `id` | string | generated when missing | |

`frameType`, `textWidth`, `title` on stored items are not read here.

#### target model (`ConnectionTarget` + `ConnectionTargetContents`)

A `TextAndImage.md` model with these specifics:

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `text` | object | `{ blocks }`; allowed styles `heading`, `title`, `body`, `bulleted`; default `title` | Target text. |
| `frameType` | string | `"circle"` (default), `"rect"`, `"rounded_rect"`, `"octagon"`, `"theme"` (= the theme's shape), or a device frame id (e.g. `"browser_solid"`) | Frame around the target; "no frame" is not allowed. |
| `frameColor` | string | palette color name, default `"primary"` via schema; `"theme"` in the generator | Fill of a shape frame (device frames keep their own colors). The frame stroke is the slide background (5px) unless `column1.decorationStyle` is `"outlined"`. |
| `content_type`, `content_value`, `backdropPadding`, `verticalAlign`, `frameScale`, `textAlign`, ... | | see `TextAndImage.md` | Image slot and text layout options of the `TextAndImage`. Stored slides carry `backdropPadding: 30`, `verticalAlign: "middle"`, `frameScale` ~0.7. |

### Nested elements

- `column1` / `column2` -> `ConnectionSourceList` (1-10 `ConnectionSourceItem`s each: `text` -> `TextElement.md`,
  `marker` -> non-editable `TextElement` or `ContentElement.md`).
- `target` -> `ConnectionTarget` -> `child` = `ConnectionTargetContents` (`TextAndImage.md`).
- `sourceHeader`, `targetHeader`, `source2Header` -> `ConnectionHeader` (`TextElement.md`), when `showHeaders`.
