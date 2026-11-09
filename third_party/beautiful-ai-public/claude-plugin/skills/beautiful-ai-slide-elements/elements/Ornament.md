# Ornament

A small circular badge drawn over an item: a running number (1, 2, 3 …), a running letter (A, B, C …) or an icon. It is never a root element and has no template of its own. The parent collection decides whether its items get one through its root-level `ornament` field: `ProcessDiagramChevrons.md` (`step_chevrons`), `SliceChart.md` (`slicechart`), `HorizontalFunnel.md` (`horizontal-funnel`) and `TextBoxGrid.md` (`textBoxGrid`) all read `primary.ornament` and add one `Ornament` per item when it is not `"none"`.

## Model location

- `states[0].primary.ornament`: the type, on the root of the parent collection (`"none"`, `"number"`, `"letter"`, `"icon"`), see the parent's doc.
- `states[0].primary.items[].ornament`: the badge's own model (an object) for `SliceChart`, `HorizontalFunnel` and `TextBoxGrid`; the parent creates `{}` when it is missing. Only matters for `"icon"`, where it holds the media slot.
- `ProcessDiagramChevrons` passes no model: its icon badge reads the media slot directly on the chevron item (`items[].content_type` / `content_value`).

## Minimal example

Root `ornament: "icon"` on a `slicechart`, one item:

```json
{
  "id": "slice-1",
  "width": 2,
  "label": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Design" }] },
  "ornament": { "content_type": "icon", "content_value": "pencil" }
}
```

## Pitfalls

- With `ornament: "icon"` every item needs a `content_value` (in `items[].ornament` or, for chevrons, on the item), otherwise that badge is an empty placeholder circle.
- Do not write numbers or letters into the model: they are derived from the item order; reorder `items[]` instead.
- `ornamentSize` is only read where the parent passes the item's model (`SliceChart`, `HorizontalFunnel`, `TextBoxGrid` root); chevrons are always 50px.

## Rules and limits

- The badge type is one value for the whole collection; there is no per-item override and no per-item "hide".
- Position and layering are decided by the parent (top edge of a chevron or slice, a corner or edge of a text box chosen by `TextBoxGrid`'s `ornamentPosition`); the badge model has no position fields.
- The badge is always outlined (white disc with a colored stroke) regardless of the item's `decorationStyle`.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `content_type` | string | `"icon"` (default when absent), `"image"`, `"logo"` | Only for type `"icon"`: what the badge shows, see `ContentElement.md`. Icons are scaled to 0.75 of the badge; a non-icon asset gets a circular 2px frame instead. |
| `content_value` | string | icon key or asset id | Only for type `"icon"`: the icon or image to show. Without it the badge shows the empty media placeholder. |
| `ornamentSize` | number | px; default 75 for `"icon"`, 50 otherwise (`TextBoxGrid` passes its root `ornamentSize`) | Diameter of the badge. |

Number and letter badges have no authored fields: the text is computed from the item's position in `items[]` (0-based index + 1, or `A` + index) and cannot be edited.

### Nested elements

- `shape` -> a circle (white fill, stroke in the item's decoration color, darkened).
- `label` -> `TextElement.md` with the generated number or letter (centered, not editable), for `"number"` / `"letter"`.
- `icon` -> `ContentElement.md` (default asset type icon) for `"icon"`.
