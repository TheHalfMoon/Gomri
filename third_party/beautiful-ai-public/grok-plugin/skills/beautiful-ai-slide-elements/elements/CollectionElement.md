# CollectionElement

`CollectionElement` is the base class of every element that renders a list of similar children from an array
in its model (`TextList`, `Team`, `IconTextGrid`, `PieChart`, `PresentationTitlePresenters`, ...). It creates
one child element per entry of `items` and resolves a shared "collection color" for them. `CollectionItemElement`
(documented here as well) is the base class of those children: it knows its index in the collection and reads
the per-item `color` / `hilited` fields.

## Model location

- Collection: wherever the owning element sits, e.g. `states[0].primary` for a root collection (`TextList`),
  `states[0].primary.presenters` / `states[0].primary.logos` for nested collections of `PresentationTitle`.
- Items: `<collection>.items[]` (the array name is `items` for every class in this group; a few classes
  elsewhere override `collectionPropertyName`).
- Each `items[i]` object is the complete model of the i-th `CollectionItemElement`.

## Minimal example

Nested collection fragment (shape shared by every collection in this group; the item fields depend on the item
class):

```json
{
  "collectionColor": "theme",
  "items": [
    { "id": "item-1" },
    { "id": "item-2", "color": "accent3" },
    { "id": "item-3", "hilited": true }
  ]
}
```

## Pitfalls

- Writing `items: []` for a collection with `minItemCount > 0` silently produces default placeholder items
  (e.g. an empty bullet column); write real items instead.
- Do not reuse the same `id` for two items; the second element overwrites the first in the children map and
  only one renders.
- `color` on an item only changes that item's *decoration* color (bullet/icon/frame); text color is driven by
  the text styles (`fontColor` on blocks), see `TextElement.md`.
- `hilited` on several items is allowed but every non-hilited sibling is dimmed; it is a spotlight, not a
  selection.
- Collections created from legacy data may still carry `col`, `body`, `titleTextStyle`, `content_type` on
  text-only items (seen in stored examples); the v10 classes ignore them, do not write them.

## Rules and limits

- `maxItemCount` is enforced by the editor UI (add / paste / duplicate throw "maximum number of allowed items")
  but **not** at build time: a model with more items than the maximum still builds; whether it fits is decided
  by the element's layout (`isFit`), and an unfit layout is rejected by the editor as a layout error.
- `minItemCount` is only used to seed an empty collection; it does not delete items.
- Items without `id` are assigned a fresh uuid on every build until the model is saved, which can re-key the
  children and break animations/collaboration diffs: always write an `id`.
- Decoration color of an item = `palette.getColor(item.color ?? collectionColor, background, { itemIndex,
  maxCount })`, so `"colorful"` / `-to-` ranges spread across items by index.
- `collectionColor: "primary"` is intentionally left untouched by migrations (some elements need it).

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

Collection (`CollectionElement`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | object[] | default: `minItemCount` copies of `defaultItemData` when empty/missing | One entry per child, in display order. Entry shape is defined by the item class (see the owning element's doc). |
| `collectionColor` | string | palette color name, `"colorful"`, or shaded `"<a>-to-<b>"`; default `"theme"` (schema) | Color handed to every item's decoration (bullets, icons, frames). With `"colorful"` or a `-to-` range each item gets a different color by index. Older slides without it get the slide's `layout.slideColor` by migration. |
| `shadeColors` | legacy | any truthy | Migration only: appends `-to-white` to `collectionColor`. Do not write. |

Item (`CollectionItemElement`, every `items[i]`):

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | any unique string; generated (uuid) on build when missing | Identity of the item. Used to key the child element, for animations and for editor selection. Always provide one so the item keeps its identity across edits. |
| `color` | string \| null | palette color name; `"auto"` is rewritten to `null` | Per-item override of `collectionColor` for this item's decoration color. `null`/absent = use the collection color. |
| `hilited` | boolean | default `false` | Spotlights this item: it gets the theme's `emphasized` styles and every sibling is drawn with `deemphasized` styles. |

Plus the common fields, see `BaseElement.md` (`accentColor`, `decorationStyle`, ...).

### Nested elements

- `items[]` -> one child per entry; the class comes from `getChildItemType(itemModel)` of the concrete
  collection (e.g. `TextList` returns `TextListMediaColumn` when `itemModel.isMedia`, else `TextListColumn`).
  The child's model **is** the `items[i]` object (not a copy).
- Order is the array order; `itemIndex` is the position in `items`. `isFirstItem` / `isLastItem` derive from it.
- Counts: `minItemCount` defaults to `1`, `maxItemCount` to `10`; concrete collections override both (listed in
  their docs). When `items` is empty or missing, `minItemCount` default items are inserted automatically
  (`defaultItemData` of the class, `{}` by default).
- `null` entries in `items` are replaced by `{}` at build time (which then renders as an empty default item).
