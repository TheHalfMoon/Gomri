# ContactInfo

The "Contact Us" slide: a vertical list of contact lines (a header, the address, phone/email/website/social lines
with an icon, free text) next to either a static street map of the address or a picture. It is the root element of the
`contactus` template (`states[0].primary`); the hidden `business_card` template uses the same element with
`layout: "left_picture"`. The map is a Google Static Maps image generated from `map_address` and cached as an asset
by the app.

## Model location

- `states[0].primary` – the element (template `contactus`). The picture (`ContentElement`) and the map (`StreetMap` -> `Map`) read the root model directly.
- `states[0].primary.items[]` – contact lines (`ContactItem` subclasses).
- `states[0].primary.map_address` – the address text, shared by the `"address"` item and the map.
- No header (`allowHeader: false`), no tray; footer allowed (default footer suppressed); default background dark.

## Minimal example

```json
{
  "primary": {
    "layout": "left_map",
    "map_address": { "blocks": [{ "id": "map_address", "type": "text", "textStyle": "title", "html": "888 Brannan St, San Francisco, CA 94103" }] },
    "showMarker": true,
    "zoom": 13,
    "mapStyle": "light",
    "items": [
      { "type": "contact_header", "text": { "blocks": [{ "type": "text", "textStyle": "title", "html": "Contact us" }] } },
      { "type": "address" },
      { "type": "phone", "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "+1 415 555 0100" }] } },
      { "type": "email", "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "hello@example.com" }] } },
      { "type": "social", "social_type": "linkedin", "text": { "blocks": [{ "type": "text", "textStyle": "body", "html": "linkedin.com/company/example" }] } }
    ]
  }
}
```

For a picture layout replace `layout` with `"left_picture"` and add `"content_type": "image", "content_value":
"<assetId>"` at the root (the app's generator leaves a `__generateImage` request there; do not keep it when you
supply the asset yourself).

## Pitfalls

- `map_address` must be `{ blocks: [...] }` on a v10 model; a bare string is only migrated for old versions, and the
  map code indexes `blocks[0]` without a guard. The app's recipe writes the raw address object into `map_address`,
  which relies on that migration and is not a safe pattern.
- The picture's `content_type`/`content_value` sit on `primary`, not inside `items`.
- `type: "address"` items ignore their own `text`; put the address in `map_address`.
- `social_type` is required for `"social"` lines, otherwise the icon is `undefined`.
- The list has no header slot: use a `"contact_header"` item as the title (the slide header is disabled).
- `assetId`/`assetMapCachingKey` are caches of the rendered map; copying them from another slide shows the wrong map
  until regenerated.

## Rules and limits

- Map/picture takes exactly half the width (`left_*`/`right_*`) or the top half (`top_picture`); the list gets the rest.
- The map is loaded asynchronously (3s debounce) by geocoding `map_address`; in thumbnails/exports the cached asset or
  the static map URL is used. An address that Google cannot resolve shows an empty map, not an error.
- `map_address` is the only address storage: an `"address"` item has no `text` of its own.
- Icon lines are single-line; long text is scaled to fit the half width (min height 50px per line).
- Migration `_migrate_10`: `map_address` given as a string or `{ text }` is converted to `{ blocks: [...] }`.
- 1–10 items (collection default); the list is centred vertically, so very few items leave empty space.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `items` (required) | array | min 1, max 10 | Contact lines in display order, see "items[] model". |
| `layout` | string | `"left_map"` (default), `"right_map"`, `"left_picture"`, `"right_picture"`, `"top_picture"`, `"none"` | Which side (or half) holds the map or picture; `"none"` uses the full width for the list. |
| `map_address` | object | `{ blocks: [{ html: "<address>" }] }`; default address "251 S. Van Ness Ave. San Francisco, CA 94103" when empty | Address geocoded for the map and shown by the `"address"` item. Write it as blocks: the map reads `map_address.blocks[0].html` directly. |
| `showMarker` | boolean | default `true` | Marker pin on the map. |
| `zoom` | number | Google zoom level, default 12 (examples 11–14) | Map zoom. |
| `mapStyle` | string | `"default"`, `"light"`, `"dark"`, `"retro"`, `"satellite"`, `"hybrid"`, `"terrain"` | Map styling. |
| `markerColor` | string | palette color or rgb, default `"theme"` | Marker pin color. |
| `content_type`, `content_value` | string | `"image"` + asset id | Picture for the `*_picture` layouts (`ContentElement.md`; `assetProps`, `scale`, `filter`, … also apply). |
| `collectionColor` | string | palette color, default `"theme"` | Icon frame colors of the list items. |
| `assetId`, `assetMapCachingKey`, `assetMapUrl` | – | written by the element | Cached rendered-map asset; do not author (a stale key just triggers a regeneration). |

Plus the common fields, see `BaseElement.md`.

#### items[] model (`ContactItem` subclasses)

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `type` (required) | string | `"contact_header"`, `"address"`, `"text"`, `"phone"`, `"email"`, `"fax"`, `"website"`, `"social"` | Line kind. `"contact_header"` is a single-block title; `"address"` shows `map_address` (single line, editable); `"text"` is free text; the rest are icon + single-line text. Unknown types render as icon items with no icon. |
| `text` | object | `{ blocks: [...] }` | Line text for every type except `"address"` (which uses the root `map_address`). See `TextElement.md`. Header defaults to `"title"` style; icon lines are single-line. |
| `social_type` | string | `"twitter"`, `"instagram"`, `"facebook"`, `"linkedin"` | For `type: "social"`: selects the icon (the icon key equals the social type) and the placeholder. |
| `content_type`, `content_value` | string | `"icon"` + key | Icon of icon lines. Auto-filled from `type` when absent: `phone` -> `"phone-call"`, `email` -> `"symbol-at"`, `fax` -> `"printer"`, `website` -> `"internet"`, `social` -> `social_type`. Set both to override the icon. |
| `frameType` | string | `"theme"` (seen in all examples) | Frame of the icon (`FramedMediaElement.md`). |
| `id` | string | uuid | Assigned if missing. |

### Nested elements

- `list` -> `ContactInfoItemList` (collection, column layout, vertically centred): `items[]` -> `ContactItemHeader`
  (`text` -> `TextElement.md`), `ContactItemAddress` (`map_address` -> `TextElement.md` bound to the root model),
  `ContactItemText` (`text`), `ContactItemIcon` (`icon` -> `FramedMediaElement.md`, `text` -> `TextElement.md`).
- `map` -> `StreetMap` (`*_map` layouts): `map` -> `Map` (the static map image, 720px square scaled ×2, centred in
  the half) and `copyright` (fixed "Map data ©<year> Google" badge). No model of their own.
- `picture` -> `ContentElement.md` (`*_picture` layouts), bound to the root model.
