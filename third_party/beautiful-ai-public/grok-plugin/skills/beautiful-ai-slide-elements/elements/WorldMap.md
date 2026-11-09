# WorldMap

An interactive vector map (MapLibre with hosted tile styles) showing a saved viewport (center, zoom, pitch, bearing),
a style (light/dark/bright/outdoors/toner/terrain), toggleable label layers and point markers with labels. It is the
root element of the `world_map` template (`states[0].primary`). There is no country/region highlighting in the model:
the only overlays are `markers[]`. Thumbnails and exports use a cached snapshot image (`mapImageAssetId`) that the
app generates; the live map needs network access.

## Model location

- `states[0].primary` – the map (template `world_map`).
- `states[0].primary.markers[]` – point markers.
- `states[0].header` – header; tray layouts as the template allows.

## Minimal example

```json
{
  "header": { "text": { "blocks": [{ "type": "text", "textStyle": "heading", "html": "Our offices" }] } },
  "primary": {
    "mapStyle": "light",
    "fullBleed": false,
    "latitude": 30.0,
    "longitude": 10.0,
    "zoom": 1.3,
    "pitch": 0,
    "bearing": 0,
    "showCountries": true,
    "showCities": false,
    "showStates": false,
    "showTransportation": false,
    "showOtherLabels": false,
    "markers": [
      { "id": "hq", "label": "HQ", "latitude": 45.533467, "longitude": -122.650095, "color": "theme", "style": "pin" },
      { "id": "emea", "label": "EMEA", "latitude": 48.858705, "longitude": 2.342865, "color": "theme", "style": "marker" },
      { "id": "apac", "label": "APAC", "latitude": -37.825071, "longitude": 144.978682, "color": "accent2", "style": "star" }
    ]
  }
}
```

## Pitfalls

- There is no way to highlight countries or regions; only point markers exist. Use a marker per location with a label.
- Coordinates are `latitude`/`longitude` (not `lat`/`lng`, not `[lng, lat]` arrays).
- Choose `zoom` consistently with the spread of markers: the editor's auto-fit only runs when markers change inside
  the app, not when a model is written by an agent.
- `style` values are `"marker"`, `"circle"`, `"star"`, `"pin"`; anything else renders no glyph (labels still show).
- `color` defaults to `"red"`, not the theme color; set `"theme"` or an accent explicitly for on-brand markers.
- Do not copy `mapImageAssetId`/`mapCachingKey` from another slide: thumbnails would show the other map until the
  cache is regenerated.

## Rules and limits

- The viewport is authored, not derived: markers outside the saved viewport are off-screen. Adding a marker through
  the editor's dialog triggers an automatic fit-to-markers (single marker: centre at `max(zoom, 8)`; several: fit
  bounds with label padding), which then rewrites `latitude`/`longitude`/`zoom` into the model. Marker changes that
  arrive through the model (undo/redo, external updates) skip that fit.
- Markers with non-numeric or out-of-range coordinates are ignored by the fit and placed wherever MapLibre puts them.
- `animateMap` is ignored when `zoom` ≤ 2 (nothing to fly to).
- Rendering in the offline player shows a placeholder; the renderer/thumbnails show `mapImageAssetId` when present,
  otherwise the live map must load (network).
- No migrations.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `markers` | array | default `[]` | Point markers, see "markers[] model". |
| `latitude`, `longitude` | number | degrees; defaults `30.949145108528683`, `6.6875181735344995` (world view) | Map centre. |
| `zoom` | number | MapLibre zoom (0 = world); default `0.79627716192145` | Zoom level. Values ≤ 2 count as "world view". |
| `pitch`, `bearing` | number | degrees, default 0 | Camera tilt and rotation. |
| `mapStyle` | string | `"light"` (default), `"dark"`, `"bright"`, `"outdoors"`, `"toner"`, `"terrain"` (also `"satellite"`, `"watercolor"` in code but not offered in the UI) | Tile style. Marker label colors invert on `"dark"`/`"satellite"`. |
| `fullBleed` | boolean | default `false` | Map covers the whole slide (no canvas margins; 50px bottom margin when inline element text is on). |
| `showCountries`, `showStates`, `showCities`, `showTransportation`, `showOtherLabels` | boolean | default `true` | Visibility of the corresponding label layers of the tile style. |
| `showStreets` | boolean | schema default `true` | Present in the schema but no code reads it. |
| `animateMap` | boolean | default `false` | In playback, start from the world view and fly to the saved viewport; only effective when `zoom` > 2. |
| `allowNav` | boolean | default `false` | Lets viewers pan/zoom during playback. |
| `mapImageAssetId`, `mapCachingKey` | string | written by the app | Cached snapshot used for thumbnails/export and its viewport key; the editor regenerates it after changes. Do not author. |
| `items` | – | noise | One stored example carries an unrelated `items` object; ignored. |

Plus the common fields, see `BaseElement.md`.

#### markers[] model

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `id` | string | uuid | Identifies the marker for editing (`id: ""` in the GeoJSON when missing). |
| `latitude`, `longitude` (required) | number | degrees (−90..90, −180..180); numeric strings are parsed for fitting but write numbers | Marker position. |
| `label` | string | default `""` (no label) | Text drawn next to the marker (20px, auto-placed left/right/top/bottom, overlapping labels hidden). |
| `color` | string | palette key (`"theme"`, `"accent1"`…) or `"rgb(r, g, b)"`; default `"red"` | Marker color. |
| `style` | string | `"marker"` (default; a dot) or `"circle"`, `"star"`, `"pin"` | Marker glyph. |
| `location`, `size`, `addresstype` | string / number | written by the marker dialog | Geocoded address string and dialog state; not used for rendering. |

### Nested elements

None: the map is rendered directly into the element's DOM node (no child elements, no text elements).
