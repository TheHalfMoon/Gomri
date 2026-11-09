# WordCloudElement

A word cloud: a list of words with weights 1–5 laid out by a generator into a compact cluster, sized and colored by
weight, rendered as SVG glyph paths. The layout (position, rotation, font size of each word) is computed and cached
in the model the first time the element is rendered; authors only supply the words and weights. Root element of the
`wordCloud` template.

## Model location

- `states[0].primary` – the `WordCloudElement` model (root).

## Minimal example

```json
{
  "primary": {
    "style": "right_angles",
    "sort": "size",
    "scale": 25,
    "spacing": 5,
    "font": "theme",
    "color": "colorful",
    "version": 2,
    "calculatedWidth": 1180,
    "calculatedHeight": 620,
    "wordcloud": "[{\"word\":\"Beautiful\",\"weight\":\"5\",\"layout\":{}},{\"word\":\"Slides\",\"weight\":\"5\",\"layout\":{}},{\"word\":\"simple\",\"weight\":\"4\",\"layout\":{}},{\"word\":\"smart\",\"weight\":\"4\",\"layout\":{}},{\"word\":\"layout\",\"weight\":\"3\",\"layout\":{}},{\"word\":\"colors\",\"weight\":\"3\",\"layout\":{}},{\"word\":\"themes\",\"weight\":\"2\",\"layout\":{}},{\"word\":\"icons\",\"weight\":\"2\",\"layout\":{}},{\"word\":\"magic\",\"weight\":\"1\",\"layout\":{}},{\"word\":\"designer\",\"weight\":\"1\",\"layout\":{}}]"
  }
}
```

## Pitfalls

- `wordcloud` must be a JSON-encoded string, not an array: the element calls `JSON.parse` on it and an array value breaks the build.
- Write `weight` as a string: the bold check compares against the string `"5"` (stored slides with numeric weights render weight-5 words in regular weight).
- Words without `layout.x`/`layout.y` trigger generation (so `layout: {}` or no `layout` both work); any word with a partial layout still triggers it for the whole cloud.
- Do not reuse `layout` coordinates from another slide with a different element size or word list; drop them (`{}`) and let the generator run.
- Weight 1 words at `scale: 10` are 10px tall and unreadable in exports; prefer `scale` 20–25 with ≤ 50 words.

## Rules and limits

- Generation happens at render time when any word lacks `layout.x`/`layout.y` (or, in the editor, when the element size differs from `generatedForSize`); the result is saved back into `wordcloud`. In the renderer an existing complete layout is always reused, so a model whose words all carry `layout` renders exactly as stored.
- The app's generator ranks 10–50 words, splits them into 5 weight bands (fewest words in the heaviest band) and writes `weight` as strings `"1"`..`"5"` with `layout: {}`.
- A word longer than the canvas may be placed out of bounds (`drawOutOfBound` is on); keep words/phrases short.
- Template defaults: `layout.headerPosition: "none"`; the app's generator also sets an accent background (`backgroundStyle: "backgroundAccent"`, `backgroundColor: "background_accent"`). `allowElementAttribution: false`; `allowColorful`.
- Migration 10.02 set `color` from the slide color.

## Full reference

The complete field tables and the nested elements, for the fields the minimal example does not show.

### Model fields

| Field | Type | Values / default | Meaning |
|---|---|---|---|
| `wordcloud` (required) | string | a JSON **string** encoding an array of `{ "word", "weight", "layout", "drawn" }` | The words. `weight` is a string `"1"`..`"5"` (`"5"` is drawn bold); `layout` is written by the generator (`{ x, y, rotation, fontSize, offsetX, offsetY, weight }`) and may be `{}` when authoring; `drawn` is set by the generator. Surrounding quotes on a word are stripped. |
| `style` | string | `"right_angles"` (schema default and template default), `"straight"`, `"rotated"` | Word rotation: none, 0°/90° mix, or six rotation steps. |
| `sort` | string | `"size"` (default), `"random"` | Placement order: heaviest words first (center), or shuffled. |
| `scale` | number | `25` (default); editor offers 10 (tiny), 15, 20, 25 (large) | Font size per weight unit: a word of weight w is drawn at `w × scale` px. |
| `spacing` | number | `1` (default); editor offers 1 (tight), 5, 8 (wide) | Gap between words passed to the generator. |
| `font` | string | `"block"` (default), `"theme"` | Bebas Neue block font, or the theme's font. |
| `color` | string | `"colorful"` (schema default); palette color or gradient per `CollectionElement.md` | Word colors by weight (weight index into the palette, 6 steps). On a colored background all words are white. |
| `invertColors` | boolean | `false` | Reverses the weight → color mapping. |
| `version` | number | `2` | Layout coordinate system marker; always write `2` (version 1 models are re-generated). |
| `calculatedWidth`, `calculatedHeight` | number | `1180`, `620` | Legacy; present in defaultData and every stored slide, not read by the current layout. |
| `generatedForSize` | array | `[width, height]` written by the generator | Size the cached layout was generated for; the editor regenerates when the element size changes. Do not author. |

Plus the common fields, see `BaseElement.md`.

### Nested elements

None: the element renders the glyph paths itself (one SVG path per word, loading the fonts needed for every character).
