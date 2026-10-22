# W13 — Arabic / RTL / mixed-script qualification: implementation design

**Wave:** W13 (Issue #77 §F acceptance gate; `research/rea/2026-10-22-nextslide-gamma/IMPLEMENTATION_GRAPH.md:201-208`)
**Repo:** `/Users/abdulazizalsh/work/Gomrey` @ `87b6bf9` (branch `feature/rea/w3-evidence-bound-narrative`)
**Nature:** READ-ONLY analysis. No source file was modified. No commit was made.
**W13 is measure-first:** build the qualification suite, let it measure real behaviour, then fix what it finds. This document is the design for both halves.

---

## A. Current-state facts

Every claim below is a file:line citation against `87b6bf9`. Where something does not exist, the text says **"does not exist"**.

### A.1 Text direction — every place a direction is set or assumed

**Places where a direction IS set (3 total, all in the editor, all on `text`/`text-list` only):**

| Location | What it does | Limit |
|---|---|---|
| `servers/nextjs/components/slide-editor/text/StaticHtmlTextLayer.tsx:193-203` | Inner content `<div dir="auto" style="...unicodeBidi:'plaintext'">` | Only reaches `text` + `text-list` elements (see A.4). The *outer* wrapper (`:159-192`) has no `dir`, and sets `textAlign: horizontal` (`:186`) where `horizontal` defaults to `"left"` (`:155`). |
| `servers/nextjs/components/slide-editor/text/TiptapInlineTextEditor.tsx:979` | `unicode-bidi:plaintext` in the inline editor root style | No `dir` attribute anywhere in that file (`rg 'dir='` → 0 hits). `unicode-bidi:plaintext` alone gives per-paragraph base direction from the first strong character, so this is functional, but it is not a `dir` declaration. |
| `servers/nextjs/components/slide-editor/text/html-text-attrs.ts:50-52` | `containsRtlText()` — the *detector*, regex `[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufefc]/u` (Hebrew, Arabic, Arabic Presentation Forms-A, FB1D-FDFF) | Hebrew + Arabic only. Not Arabic-Indic digits (U+0660-0669), not Arabic Extended-A/B, not Syriac/Thaana/NKo. |

**Places where LTR is hard-coded (the load-bearing set):**

| Location | Hard-coded LTR assumption |
|---|---|
| `servers/nextjs/lib/template-v2-json-to-html.ts:4068-4072` | `function textAlign(value)` → `value === "center" \|\| "right" \|\| "justify" ? value : "left"`. **No `start`/`end` is ever emitted.** This is the export renderer. |
| `servers/nextjs/lib/template-v2-json-to-html.ts:4056-4058` | `horizontalAlign()` → `flex-start` / `flex-end` only. |
| `servers/nextjs/lib/template-v2-json-to-html.ts:391-413` | `renderText()` emits `text-align:${textAlign(horizontal)}` and **no `dir`, no `direction`, no `unicode-bidi`**. Verified: `rg -c 'dir=|unicodeBidi|unicode-bidi' servers/nextjs/lib/template-v2-json-to-html.ts` → **zero matches in the whole 4145-line file.** |
| `servers/nextjs/lib/template-v2-json-to-html.ts:454-483` | `renderTable()` — grid of cells, `tableCellStyle()` (`:3642-…`) / `cellText()` (`:3730-…`) — no `dir`. |
| `servers/nextjs/lib/template-v2-json-to-html.ts:1157-1170` | `renderChart()` — `<canvas data-chart-config="…">`; the canvas has no `direction` and Chart.js is not configured for RTL. |
| `servers/nextjs/lib/template-v2-json-to-html.ts:3491-3516` | `fontStyle()` → `font-family:'${family}'` — a **single family, no fallback chain at all** (`:3501`). |
| `servers/nextjs/lib/template-v2-json-to-html.ts:4130-4132` | `escapeCssFont()` → `'${value}'`, no fallback appended. |
| `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1144-1157` | `lineStartX()` — `center` → centred, `right` → right edge, **everything else → 0 (left)**. No RTL branch. |
| `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1640-1652` | `readHorizontalAlignment()` → `center` / `right` / `justify` / **else `left`**. `start`/`end` are not in the vocabulary. |
| `servers/nextjs/components/slide-editor/surface/nodes.tsx:2500` | `const align = readString(element.alignment?.horizontal) ?? "left";` |
| `servers/nextjs/components/slide-editor/surface/nodes.tsx:2537` | `const startX = lineStartX(align, width, lineMetric.width, false);` — LTR x advance. |
| `servers/nextjs/components/slide-editor/surface/nodes.tsx:2589` | Konva `fontFamily={`${segment.font.family}, Helvetica, sans-serif`}` — hard-coded Latin fallback chain. |
| `servers/nextjs/components/slide-editor/surface/nodes.tsx:2648` | Same for text-list tokens. |
| `servers/nextjs/components/slide-editor/tables/TemplateV2TableElement.tsx:281` | Table cell Konva `fontFamily={`${token.font.family}, Inter`}` — a **different** Latin fallback chain from the text path. |
| `servers/nextjs/components/slide-editor/text/css-text.ts:1-8` | `cssFontFamilyStack(family)` → `"${family}", Helvetica, sans-serif`. This is the editor's only font stack; **it names no Arabic-capable family.** |
| `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1615-1619` | `richFontCss()` (the *measurement* font) → `${italic}${weight}${size}px "${family}", Helvetica, sans-serif` — same Latin-only chain, and it is **different from the export renderer's single-family chain** (A.3). |
| `servers/fastapi/templates/v2/models/elements.py:30-34` | `class HorizontalAlignment(str, Enum): LEFT="left"; CENTER="center"; RIGHT="right"; JUSTIFY="justify"` — **no `start`/`end`**. |
| `servers/fastapi/templates/v2/models/elements.py:121-124, 203-222` | `Alignment` = `{horizontal, vertical}`; `Text` has no `direction` field. **A per-element direction field does not exist in the schema.** |

**Not-direction `direction:` hits:** `layouts.json`, `templates/executive/template.json`, and every `*.test.mjs` match on **flex `direction: "row"/"column"`** — layout direction, not text direction. `servers/nextjs/app/globals.css:554` is `text-align:center` on `.container__content` (a chrome class, not a slide). `servers/nextjs/app/(export)/pdf-maker/PdfMakerPage.tsx:45` is `flex-direction: column !important`.

**Direction does not exist in the FastAPI template/theme layer at all** — `rg -i 'rtl|bidi|arabic' servers/fastapi/templates/v2/` → zero matches.

### A.2 Font handling

**Loading path.** `servers/nextjs/components/slide-editor/surface/fontLoading.ts`:
- `useFontLoadState(ui, templateFonts, enabled)` (`:25-135`) computes a *signature* of the fonts used by the UI (`:153-168`), then injects `@font-face` rules and waits on `document.fonts` (`:80-99`).
- `fontLoadSignatureForUi` (`:153-168`) walks `ui.elements` and `ui.components[].elements`; `collectElementFontDescriptors` (`:170-187`) only descends into element types `text`, `text-list`, **`table`** (`:175`).
- `addFontLoadDescriptor` (`:258-267`) builds `"<style> <weight> 16px \"<family>\""` — **family name only. There is no script awareness, no script fallback, and no coverage check.**

**The font catalogue.** `servers/nextjs/components/slide-editor/text/local-fonts.ts`:
- `LOCAL_FONT_OPTIONS` (`:70-172`) — 111 entries across `display`, `handwritten`, `monospace`, `sans_serif`, `script`, `serif`, `slab_serif`. `APPLICATION_FONT_OPTIONS` (`:174-179`) adds `Syne`.
- **No Arabic-capable family is present.** `find servers/nextjs/public/vendor/fonts -iname '*arab*' -o -iname '*naskh*' -o -iname '*amiri*'` → **zero hits**. The 222 vendored font files are all Latin.
- `Noto Sans Mono` (`:106`) and `Noto Serif` (`:151`) are present but are **Latin-only Noto** — the `Noto*` name does not imply Arabic coverage.
- `SYSTEM_FONT_FAMILY_KEYS` (`:181-200`) lists `arial, helvetica, times, times new roman, georgia, courier, courier new, verdana, tahoma, trebuchet ms, impact, comic sans ms, system-ui, sans-serif, serif, monospace` — these are *skipped* by `ensureLocalFontsForDescriptors` (`:225-243`) because they are assumed to be system-resident. **`tahoma` and `arial` are the two system families here that do have Arabic coverage on Windows**; they are on the skip list, so they are never loaded from the vendor tree.
- Template-declared fonts are parsed by `localFontOptionsFromUnknown` (`:249-375`) and can point at any `/vendor/fonts/…`, `data:font/…`, or `.ttf/.woff/.woff2/.otf/.eot` URL (`:391-396`).

**Theme font model.**
- TypeScript: `servers/nextjs/lib/template-theme.ts:23-30` — `TemplateThemeTextFont = { name: string; url: string }`; `TemplateTheme.fonts?: { textFont?: TemplateThemeTextFont }` — **one font, one script**.
- `template-theme.ts:329-352` picks the *dominant* font by occurrence count in the template's layouts (`:240-269`) — a Latin-frequency heuristic. There is no script dimension.
- Python: `servers/fastapi/templates/v2/theme.py:382-400` — `selected_font` is `profile.fonts[selection.text_font]` else `profile.fonts[0]`, else `"Inter"`. **The theme font is chosen from the template's own fonts; the request `language` never enters this function.**
- DOM application: `servers/nextjs/app/(presentation-generator)/presentation/utils/applyPresentationThemeDom.ts:69-71` sets `font-family: "<textFont.name>"` on the slide wrapper — again a single Latin family.

**What happens today when a glyph is missing from the chosen font?**
- **Editor (Konva surface + `StaticHtmlTextLayer`):** `cssFontFamilyStack` → `"Lato", Helvetica, sans-serif`. Latin comes from Lato. Arabic has no glyph in Lato or Helvetica, so the **browser's per-glyph system fallback** finds an Arabic-capable installed font. This is accidental, not designed: no family is *named*.
- **Export HTML renderer:** `fontStyle` → `font-family:'Lato'` — **a single family, no CSS fallback list at all**. Per-glyph fallback still happens, but now it is *purely* a system-font lookup, and the rendered font is entirely different from the design's.
- **Is there a fallback chain? Is it per-script?** There is a *Latin-only* chain in the editor (`css-text.ts:7`, `template-v2-text.ts:1618`, `nodes.tsx:2589`, `TemplateV2TableElement.tsx:281`) and *no chain at all* in the export renderer (`template-v2-json-to-html.ts:3501`). **Neither is per-script.** There is no code anywhere that maps a script to a font.

**Does the deployment have an Arabic-capable font?**
- `Dockerfile:95-97` and `Dockerfile.dev:26-30` install `fonts-liberation fonts-noto-core fonts-noto-extra fonts-noto-mono fonts-noto-ui-core fonts-noto-ui-extra fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji`.
- `Dockerfile:115-117` and `Dockerfile.dev:44-46` then `find /usr/share/fonts -type f ! -iname 'Noto*' -delete` — **every non-Noto font is removed**, so `Helvetica`/`Tahoma`/`Arial` do **not** exist in the image.
- Debian's `fonts-noto-core` contains **Noto Naskh Arabic** and **Noto Sans**; `fonts-noto-ui-core` contains **Noto Sans Arabic UI** (packages.debian.org/unstable/fonts/fonts-noto-core). So the container **does** have Arabic-capable Noto families installed system-wide.
- Consequence: in the container, Arabic renders via *system fontconfig fallback* into Noto Naskh Arabic / Noto Sans Arabic — **not tofu**, but a different face from the design's Latin font, and with no recorded font name that tells a reader which face was used.
- On macOS dev, CoreText substitutes (Geeza Pro / Al Bayan). On a stock Windows PowerPoint opening the exported PPTX, substitution depends on the *recorded* font name, which today is the Latin theme font.

### A.3 The text layout engine

**Location.** `servers/nextjs/components/slide-editor/text/template-v2-text.ts` (1693 lines) is the shared layout engine; `servers/nextjs/lib/template-v2-json-to-html.ts` is the HTML renderer; `servers/fastapi/templates/v2/` holds the Python schema/theme/content layer.

**Measurement — width-based, browser-shaped:**
- `measureRenderText(text, font)` (`:1626-1638`): creates a canvas, sets `context.font = richFontCss(font)`, and returns `context.measureText(text).width + letterSpacing * (len-1)`.
- Fallback when `document` is undefined: `text.length * font.size * (font.bold ? 0.58 : TEXT_AVERAGE_CHAR_EM)` (`:1627-1628`) — a pure length heuristic.
- `measureText` returns the width of the **shaped** run (the browser applies Arabic shaping and the UBA to compute the advance), so the *width* of Arabic is measured reasonably. But it is measured for a **single logical string**; the engine then *splits* that string and lays the pieces out itself.

**Line breaking — split-then-place, LTR:**
- `layoutRenderTextRuns(runs, width, wrap)` (`:1002-1068`): splits each run with `run.text.match(/\n|[^\S\n]+|[^\s]+/g)` (`:1037`) — i.e. **on whitespace** — then `splitOversizedTextSegment(...)` for over-long words, then accumulates `lineWidth` and calls `pushLine()` when a segment would overflow (`:1050-1057`).
- `lineStartX(align, boxWidth, lineWidth, allowOverflow)` (`:1144-1157`): `center` → centred, `right` → right edge, **else 0**. No RTL branch.
- Consequence: a multi-word Arabic sentence is split into words and placed **left to right**. The Konva path therefore renders Arabic words in the wrong order. (The editor avoids this by routing RTL `text`/`text-list` to the DOM layer — see A.4 — but table cells are not routed.)

**Auto-fit / font size:** `effectiveLineHeight({text, width, fontSize, lineHeight, fallback, wrap})` (`nodes.tsx:2502-2509`) computes a line height, not a shrink-to-fit. `measureRenderTextRunsHeight` (`:703-716`) and `textVisualLocalBox` (`:557-…`) compute visual bounds from measured widths. There is no font-size auto-fit in the text engine.

**Is measurement script-aware?** **No.** There is no script detection in `template-v2-text.ts` at all. `richFontCss` (`:1615-1619`) uses the Latin-only stack, so measurement and rendering use *different* font stacks in the export path (measure: `"Lato", Helvetica, sans-serif`; render: `font-family:'Lato'`) — the two already disagree, and both are Latin-only.

**Would it handle Arabic shaping/ligatures?** Shaping and ligatures are delegated entirely to the browser's text engine:
- In the **DOM path**, yes — the browser shapes Arabic (initial/medial/final forms, mandatory ligatures) and applies the UBA. This is why the editor's `StaticHtmlTextLayer` route works at all.
- In the **Konva path**, `ctx.fillText` shapes each *segment* independently, so a segment that is a whole Arabic word is shaped correctly, but the *order of the words* is LTR (wrong), and a word split mid-word by `splitOversizedTextSegment` would be shaped as two independent fragments (broken joining).

**FastAPI templates/v2 layout:** `servers/fastapi/templates/v2/content.py`, `generation.py`, `theme.py`, `schema.py`, `models/elements.py` are **schema + content-hydration + LLM-prompt** code. They perform **no text measurement and no layout**. `servers/fastapi/templates/fonts_and_slides_preview.py:568-570` emits `text-left/center/right` classes only.

### A.4 The renderers

#### (i) Konva canvas renderer

Files: `servers/nextjs/components/slide-editor/surface/TemplateV2KonvaSlide.tsx` (3400 lines), `servers/nextjs/components/slide-editor/surface/nodes.tsx` (6548 lines).

- **Does it set `dir`?** **No.** `rg -n 'dir=|direction|rtl|bidi' nodes.tsx TemplateV2KonvaSlide.tsx` → zero `dir`/bidi hits. Konva is a canvas; it has no `dir` concept.
- **Does it emit `text-align` or logical `start`/`end`?** Konva `Text` has an `align` prop, but the engine computes x itself. `nodes.tsx:2500` reads `alignment.horizontal` and `:2537` calls `lineStartX`, which is LTR-only. The Konva path never uses `start`/`end`.
- **How is a text run converted to canvas text?** `RawTextElement` (`:2480-2605`): `rawRenderTextRuns(element)` → `layoutRenderTextRuns(layoutRuns, width, "word")` (`:2513`) → per-line, per-segment `<Text>` nodes (`:2582-2600`) with `text={renderKonvaTextSegment(segment.text)}`, `fontFamily={`${segment.font.family}, Helvetica, sans-serif`}`, `wrap="none"`. Each segment is a separate canvas `fillText` at a computed `x`.
- **Would Arabic be shaped correctly in canvas?** Shaping: yes, within a single segment (the browser shapes the string passed to `fillText`). Ordering: **no** — segments are placed LTR, so a multi-word Arabic sentence appears with words in reversed order. Joining: no — a word split across segments loses its joining forms.
- **Is the Konva path even used for Arabic?** `nodes.tsx:1325-1326`: `const usesHtmlText = renderTextAsHtml && shouldRenderTextElementAsHtml(element);` and `nodes.tsx:1860` renders the HTML layer instead of the Konva text when true. `TemplateV2KonvaSlide.tsx:3000, 3032` pass `renderTextAsHtml` (always true) and `:3125-3131` mounts `<StaticHtmlTextLayer>`.
  - **But `shouldRenderTextElementAsHtml` (`html-text-attrs.ts:11-35`) only handles `type === "text"` and `type === "text-list"`.** It returns `false` for `table`, `chart`, `vector`, `svg`, `image`. Therefore **Arabic in a table cell is rendered by the Konva path and is broken** (LTR word order).

#### (ii) HTML renderer

File: `servers/nextjs/lib/template-v2-json-to-html.ts` (4145 lines). Entry point `templateV2UiToHtmlFragment(ui, opts)` (`:172`).

- **Does it set `dir`?** **No — zero occurrences of `dir=`, `direction`, `unicodeBidi`, `unicode-bidi`, `bidi` in the entire file.** Verified: `rg -c 'dir=|unicodeBidi|unicode-bidi' …` → no match (exit 1).
- **Does it emit `text-align` or logical `start`/`end`?** It emits **physical** `text-align` only: `renderText` (`:412`) → `text-align:${textAlign(horizontal)}`, and `textAlign` (`:4068-4072`) maps `center|right|justify` through and **everything else to `left`**. `start`/`end` never appear. `horizontalAlign` (`:4056-4058`) likewise emits only `flex-start|flex-end|center`.
- **How is a text run converted to DOM text?** `renderText` (`:391-413`) → `normalizedRunsForHtml(item, font)` → `renderTextRunHtml(run, runFont)` (`:3877-3897`) → `<span style="${fontStyle(font)}">${escapeHtml(text)}</span>` per run, all runs concatenated into a single `<span style="display:block;width:100%">` inside a flex `<div>`.
- **Would Arabic be shaped correctly?** Shaping and *intra-run* character order: **yes** — the browser shapes and applies the UBA inside each span. But because the paragraph base direction is LTR (no `dir`) and `text-align` is `left`, a pure-Arabic paragraph is **left-aligned** and a mixed paragraph places its Arabic segment by **LTR** rules. So: **shaped, ordered within the run, mis-positioned at the paragraph level.**

**The two renderers are not interchangeable** and there is no shared direction decision between them. `StaticHtmlTextLayer` uses `dir="auto"` + `unicode-bidi:plaintext`; `template-v2-json-to-html.ts` uses neither.

### A.5 The export path

**PPTX export is external.** `presentation-export/presenton-export-version.json` → `{"version":"v1.0.34","package":"presenton-export-core-opensource-1.0.34.tgz"}`. Installed by `scripts/sync-presentation-export.cjs`; `presentation-export/` is gitignored; the installed package is `presentation-export/node_modules/@presenton/export-core/dist/index.js` — **minified/obfuscated**.

**What the repo knows about it:**
- `servers/nextjs/lib/run-bundled-presentation-export.ts:179-186` — the export task is `{ type: "export", url: pptUrl, format, title, fastapiUrl, cookieHeader }`, where `pptUrl` = `${NEXT_PUBLIC_URL}/pdf-maker?id=…&format=…` (`:157-171`). The child process is `presentation-export/runner.mjs` (`:39-43, 199`).
- The export core's own task router (from the installed bundle) supports `export`, `html-to-any`, `pptx-from-json`, `pptx-to-html`, `pptx-to-json`, `html-to-image(s)`, `json-to-image(s)`, `json-to-html`. The `export` path launches a headless browser, loads the `/pdf-maker` URL, and converts the live DOM to PPTX/PDF/PNG.
- **Critical:** the export renders the **DOM** path, not the Konva path. `servers/nextjs/app/(export)/pdf-maker/PdfMakerPage.tsx:19-21` imports `shouldRenderTemplateV2HtmlPreview` / `TemplateV2HtmlSlidePreview`, and `TemplateV2HtmlSlidePreview.tsx:257-262` calls `templateV2UiToHtmlFragment(...)` and injects it with `dangerouslySetInnerHTML` (`:475`). So **the PPTX/PDF deliverable is produced from `template-v2-json-to-html.ts`'s output** — the file with zero `dir` support.
- The export core's DOM→PPTX text conversion resolves logical alignment from the DOM's computed style: `text-align:start` → `right` when `direction === 'rtl'`, `end` → `left` (the only two `rtl` occurrences in the whole bundle are in that resolver). **It reads the computed `direction`, but Gomrey never sets one, and it emits only physical `left|center|right`, never `start|end`.** So the export core's RTL path is present but unreachable from Gomrey today.
- The bundle contains **no** reading of a DOM `dir` attribute, and **no** writing of the OOXML paragraph flag `<a:pPr rtl="1">` (`rtl` appears exactly 2× in the bundle, both in the computed-style resolver above).

**PPTX import.** `servers/fastapi/services/export_task_service.py`:
- `convert_pptx_to_json(pptx_path)` (`:690-729`) and `convert_pptx_to_html(pptx_path, get_fonts)` (`:460-…`) both delegate to the **same external export-core** with task type `"pptx-to-json"` / `"pptx-to-html"` (`:694-698`). The Python side only runs the child process and rewrites asset URLs (`:731-773`).
- The actual OOXML parsing lives in the obfuscated bundle. From that bundle: the reader *does* parse `<a:pPr algn="…">` (`textAlignment(/\balgn="([^"]+)"/)`) and merges paragraph/run styles, and it *does* collect `<a:latin typeface="…">` / theme fonts — but there is **no `rtl` attribute read anywhere**, so `<a:pPr rtl="1">` from a PowerPoint-authored RTL deck is silently dropped on import.
- `servers/fastapi/templates/pptx_font_utils.py` (1668 lines) handles fonts only: `extract_used_fonts_from_pptx` (`:807`), `extract_used_font_variants_from_pptx` (`:365`), `replace_fonts_in_pptx` (`:1068`), `create_font_alias_config` (`:887`). `rg -i 'rtl|bidi|arabic'` over it → **zero matches**.
- `rg -i 'rtl|bidi|arabic'` over `servers/fastapi/services/export_task_service.py` and `servers/fastapi/templates/v2/*.py` → **zero matches**.

**Verdict on the export path:** RTL/bidi attributes are **not** handled on import (the `rtl` paragraph flag is dropped), and are **not** produced on export (no `dir`, no `start`/`end`, no `rtl="1"`).

### A.6 Existing multilingual support — what `language` does and does not change

**The request field.** `servers/fastapi/models/generate_presentation_request.py:25-28`:
```python
language: Optional[str] = Field(
    default=None,
    description="Language for the presentation. If omitted, model auto-detects language.",
)
```
Also `GenerateSmartPresentationRequest.language` (`:52`). It is a free-form `Optional[str]` — **not** an enum, **not** a BCP-47 tag.

**The UI.** `servers/nextjs/app/(presentation-generator)/upload/type.ts:16-33` — `enum LanguageType`, including `Arabic = "Arabic (العربية)"` (`:31`). The value is a **display string**, not a locale code.

**Where `language` actually flows (FastAPI):**
| Consumer | File:line | Effect |
|---|---|---|
| DB persistence | `servers/fastapi/models/sql/presentation.py:48, 90` | stored as a string column |
| Document/OCR loading | `servers/fastapi/api/v1/ppt/endpoints/outlines.py:122-126`; `services/documents_loader.py` | `DocumentsLoader(presentation_language=…)` — affects the **translation/OCR of uploaded source documents**, not the deck. |
| **Outline LLM prompt** | `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py:169-177` (`_resolve_prompt_language`), `:196-208` (`get_user_prompt` → `f"Language: {display_language}\n"`), `:126-127` ("generate every presentation title and slide outline in exactly that language") | **This is the entire effect: a line of prompt text telling the model what language to write in.** |
| Chat memory | `services/chat/memory_layer.py:595, 1027`; `services/chat/service.py:297` | stored/recalled as context |
| Cloud persistence | `services/presenton_cloud_persistence.py:89-91, 159, 173-174` | round-tripped |

**What `language` does NOT change:**
- **Not** the theme font. `servers/fastapi/templates/v2/theme.py:382-400` selects the font from the *template's* font profile; `language` is not a parameter of `build_theme_profile`, `materialize_theme`, or `template_theme_for_presentation`.
- **Not** the element schema. `servers/fastapi/templates/v2/models/elements.py` has no language/script/direction field.
- **Not** the LLM layout prompt. `servers/fastapi/templates/v2/generation.py` (the layout-generation system prompt at `:86-…`) contains no language or script instruction; the only match for "language" in that file is `"visual language: typography, colors, spacing, geometry, decorative assets, and …"` (`:93`) — an unrelated phrase.
- **Not** the renderer. `template-v2-json-to-html.ts` has no language/script input at all.
- **Not** layout mirroring, column order, bullet side, or numbering direction.

**There is a *separate*, unrelated "language" concept**: `servers/fastapi/gomrey/media_pipeline.py:36, 109` — `language: str = "und"` for media subtitle tracks. Not the deck language.

### A.7 Test conventions for qualification suites

**`servers/nextjs/tests/` — 20 files, `node --test`, no browser.**
- Runner: `servers/nextjs/package.json` → `"test": "node --test"` (cwd = `servers/nextjs`).
- Convention: `node:test` + `node:assert/strict`. To test a TypeScript module, the test **bundles it with esbuild** into a temp `.mjs` and dynamic-imports it. Canonical example — `servers/nextjs/tests/latex-html-text-rendering.test.mjs:1-36`:
  ```js
  import assert from "node:assert/strict";
  import { mkdtemp, rm } from "node:fs/promises";
  import { tmpdir } from "node:os";
  import path from "node:path";
  import test from "node:test";
  import { pathToFileURL } from "node:url";
  import { build } from "esbuild";

  test.before(async () => {
    temporaryDirectory = await mkdtemp(path.join(tmpdir(), "presenton-math-html-"));
    const outputFile = path.join(temporaryDirectory, "html-text-attrs.mjs");
    await build({ entryPoints: [path.resolve("components/slide-editor/text/html-text-attrs.ts")],
      outfile: outputFile, bundle: true, platform: "node", format: "esm",
      tsconfig: path.resolve("tsconfig.json"), logLevel: "silent" });
    htmlText = await import(`${pathToFileURL(outputFile).href}?cache=${Date.now()}`);
  });
  test.after(async () => { await rm(temporaryDirectory, { recursive: true, force: true }); });
  ```
  17 of the 20 test files use this esbuild pattern. `template-theme-infographics.test.mjs:14-24` shows the variant where a synthetic `entry.ts` re-exports several modules.
- **Assertions are string/regex on generated markup**, e.g. `template-v2-json-to-html-metadata.test.mjs:87-97` uses `assert.match(html, /transform:scaleY\(-1\)/)`, `:144-151` uses `assert.match(html, /width:136\.34px;height:133\.62px;[^>]*display:flex;flex-direction:column/)`.
- **Source-text assertions** are also used where the artifact is a source file rather than a runtime value: `pdf-maker-export-layout.test.mjs:10-19` reads `PdfMakerPage.tsx` with `readFile` and `assert.match(source, /align-items:\s*flex-start\s*!important/)`.
- **A headless browser is NOT available in the nextjs test environment.** `servers/nextjs/package.json` devDependencies contain **no** puppeteer, playwright, or jsdom. The only Chromium in the repo is the export-core's (`presentation-export/node_modules/@presenton/export-core`) and the electron app's (`electron/scripts/prepare-export-chromium.cjs`, `electron/app/utils/export-chromium.ts` — puppeteer via `@n/browsers`). The nextjs Dockerfile stage runs `npm run build`, **not** `npm test`.
  → **Consequence: W13's nextjs assertions must be on generated markup strings and on module return values. They cannot assert pixel geometry, glyph shapes, or visual bidi order.** That is an architectural constraint, not a preference.

**`servers/fastapi/tests/` — pytest.**
- `servers/fastapi/pyproject.toml:66-67` → `[tool.pytest.ini_options] testpaths = ["tests"]`.
- Layout: `tests/conftest.py` (root fixtures: `fake_async_session`, `snapshots_dir`, `load_snapshot`), then `tests/unit/`, `tests/edge_cases/`, `tests/integration/`, `tests/regression/`, `tests/mocks/` (`llm.py`, `normalizers.py`), plus flat `tests/test_*.py` for the `gomrey/` package.
- Style: plain `def test_*(...) -> None:` functions, `pytest.raises`, no classes. Example — `servers/fastapi/tests/test_gomrey_ocr_worker.py:1-37`:
  ```python
  import pytest
  from gomrey.ocr_worker import (ARABIC_P0_CASES, OCRRegion, check_arabic_case,
                                 map_ocr_regions, quality_observations, script_profile)

  def _region(region_id: str, text: str, **overrides) -> OCRRegion: ...

  def test_script_profiles_arabic_english_mixed() -> None:
      arabic = script_profile("مرحبا بالعالم")
      assert arabic.arabic is True and arabic.latin is False
      assert arabic.direction == "rtl"
  ```
  This is the **closest existing analogue to W13's target**: it already contains Arabic fixtures (`"مرحبا بالعالم"`, `"تقرير Report 2026"`, `"العدد ١٢٣"`) and the nine frozen `ARABIC_P0_CASES` names (`servers/fastapi/gomrey/ocr_worker.py:46-56`).
- `servers/fastapi/tests/unit/` is where module-level unit tests live (e.g. `test_template_theme.py`, `test_pptx_json_element_metadata.py`).

### A.8 What genuinely exists for Arabic today

**Existing Arabic capability in the repo — five pieces, none of which is end-to-end deck support:**

1. **A script/direction classifier in Python.** `servers/fastapi/gomrey/ocr_worker.py:41-44` defines `ARABIC_RE = [\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]`, `LATIN_RE`, `ARABIC_INDIC_RE = [\u0660-\u0669]`, `WESTERN_DIGIT_RE`; `:78-89` `script_profile(text)` returns `ScriptProfile(arabic, latin, arabic_indic_digits, western_digits, direction)` with `direction = "rtl" | "mixed" | "ltr"`. **This is the single most reusable asset in the repo for W13** — but it lives in the *OCR* module and is not used by the template, theme, or renderer.
2. **A frozen Arabic P0 case list.** `servers/fastapi/gomrey/ocr_worker.py:46-56` — `arabic-only, english-only, mixed-arabic-english, rtl-tables, numerals-both-systems, rotated-scanned, poor-scans, decimals-units-dates, charts-formulas`; judged by `check_arabic_case` (`:154-…`). These are **OCR/ingestion** cases, not **rendering** cases, but the *names* map almost 1:1 onto W13's proposed case list. `docs/MASTER_PLAN.md:263-273` is the same list under "Arabic P0 tests".
3. **An RTL detection + DOM-routing rule in TypeScript.** `servers/nextjs/components/slide-editor/text/html-text-attrs.ts:11-52`, already unit-tested with Arabic strings at `servers/nextjs/tests/latex-html-text-rendering.test.mjs:104-110` (`"عنصر عربي"`) and Hebrew at `:56-69`.
4. **A working `dir="auto"` + `unicode-bidi:plaintext` DOM text layer** for the editor surface: `servers/nextjs/components/slide-editor/text/StaticHtmlTextLayer.tsx:193-203`.
5. **Arabic-capable system fonts in the deployment image** (Noto Naskh Arabic / Noto Sans Arabic via `fonts-noto-core`; `Dockerfile:95-97`).

**What does NOT exist:**
- Any `dir` / `direction` / `unicode-bidi` in the export renderer (`template-v2-json-to-html.ts`) — **the deliverable path**.
- Any Arabic-capable family in the vendored font catalogue (`local-fonts.ts:70-172`, 222 files, zero Arabic).
- Any per-script font selection, anywhere.
- Any `start`/`end` alignment in the schema (`elements.py:30-34`) or the renderer.
- Any `direction` field in the element schema (`elements.py:203-222`).
- Any RTL/bidi handling in `pptx_font_utils.py` or the export_task_service.
- Any Arabic/RTL qualification test that asserts on rendered output, fonts, or export. `rg -i 'rtl' servers/nextjs/tests/` → only `template-preview-density.test.mjs` (flex `direction`) and `template-v2-canonical-model-compatibility.ts:111` (flex `direction: "row"`).

**Fonts named in the request** (`Noto Naskh`, `Noto Sans Arabic`, `Amiri`, `Tahoma`, `Arial`, `Segoe UI`):
- `Noto Naskh` — **does not exist** in the repo (only in the container's system font set).
- `Noto Sans Arabic` — **does not exist** in the repo's vendor tree; exists in the container's system font set.
- `Amiri` — **does not exist** anywhere.
- `Tahoma`, `Arial` — appear **only** in `local-fonts.ts:181-200` `SYSTEM_FONT_FAMILY_KEYS` (i.e. as *skip-list* entries assumed to be system-resident). No file is vendored for them. In the Docker image they are **deleted** (`Dockerfile:115-117`).
- `Segoe UI` — **does not exist** anywhere in the repo.
- Wide-Unicode Noto families present: `Noto Sans Mono` (`local-fonts.ts:106`) and `Noto Serif` (`:151`) — both **Latin-only**.

---

## B. What Arabic does today — step-by-step trace

Scenario: a deck whose slides contain Arabic text, generated with `language: "Arabic (العربية)"`.

| # | Step | Code | Status | Why |
|---|---|---|---|---|
| 1 | **Request** | `servers/fastapi/models/generate_presentation_request.py:25-28` | **OK** | `language` is accepted and stored. It is a display string, not a locale. |
| 2 | **Template / theme** | `servers/fastapi/templates/v2/theme.py:382-400`; `servers/nextjs/lib/template-theme.ts:329-352` | **DEGRADED** | The theme font is the template's *dominant Latin* font. Nothing about `language` reaches the theme. There is no Arabic face, no direction, and the model has no `direction` field (`elements.py:203-222`). |
| 3 | **Outline prompt** | `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py:196-208` | **OK** (for text) | The LLM is told `Language: Arabic (العربية)` and asked to write in that language. The **outline** is Arabic. The layout prompt (`templates/v2/generation.py:86-…`) has **no** language/script instruction — the layout is generated from a Latin-oriented template. |
| 4 | **Slide content** | `templates/v2/content.py` (hydration) | **DEGRADED** | The LLM's Arabic text is written into `runs[].text` verbatim — no mangling, no bidi isolation marks, no stripping. But the **run's font stays the template's Latin font**, so the Arabic run is assigned a face with zero Arabic coverage. |
| 5 | **Konva render — `text` / `text-list`** | `html-text-attrs.ts:11-52` → `StaticHtmlTextLayer.tsx:193-203` | **OK (editor surface only)** | RTL is detected and the element is routed to the DOM layer with `dir="auto"` + `unicode-bidi:plaintext`. The browser shapes and orders the Arabic correctly. **But** the outer wrapper has no `dir` and sets `text-align: left` (`:155, 186`), so an Arabic paragraph is left-aligned, and the font stack `cssFontFamilyStack` (`css-text.ts:7`) names only `Helvetica, sans-serif`. |
| 6 | **Konva render — `table` cells** | `html-text-attrs.ts:11-35` returns `false` for `type === "table"`; `tables/TemplateV2TableElement.tsx:243-291` | **BROKEN** | Arabic table-cell text is split on whitespace by `layoutRenderTextRuns` (`template-v2-text.ts:1037`) and the words are placed **left to right** (`nodes.tsx:2537` → `lineStartX` at `template-v2-text.ts:1144-1157`). The sentence reads in the wrong order. |
| 7 | **Konva render — `chart` labels** | `nodes.tsx` chart path; Chart.js canvas | **DEGRADED** | Chart labels are drawn on a canvas. The browser shapes the glyphs, but the canvas base direction is LTR, so labels are left-aligned and mixed-script labels follow LTR rules. |
| 8 | **Konva render — `vector` shape text** | `nodes.tsx` vector path | **BROKEN** (same mechanism as 6) | Vector text is laid out by the same LTR segment engine. |
| 9 | **HTML render (export path)** | `template-v2-json-to-html.ts:391-413` (`renderText`), `:415-452` (`renderTextList`), `:454-483` (`renderTable`), `:1157-1170` (`renderChart`) | **BROKEN at the paragraph level** | No `dir`, no `direction`, no `unicode-bidi` anywhere in the file. `text-align` is physical and defaults to `left` (`:4068-4072`). The browser still shapes the Arabic and orders characters *within* the run, so the text is **readable but left-aligned and mis-ordered for mixed runs**. `fontStyle` (`:3501`) emits a single family with no fallback. |
| 10 | **PPTX export** | `run-bundled-presentation-export.ts:179-186` → `/pdf-maker` → `TemplateV2HtmlSlidePreview.tsx:257-262` → external export-core | **DEGRADED** | The deliverable is produced from the (broken) HTML of step 9. The export core *does* understand `text-align:start` under `direction:rtl`, but Gomrey emits neither, so the core's RTL path is unreachable. The exported PPTX will carry Arabic text in the theme's Latin font name, with LTR paragraph alignment and no `rtl` flag. |
| 11 | **PPTX re-import** | `export_task_service.py:690-729` → external export-core; `pptx_font_utils.py` | **BROKEN** | The external reader parses `algn` but **not** `<a:pPr rtl="1">` (the bundle contains exactly 2 `rtl` occurrences, both in the DOM computed-style resolver). `pptx_font_utils.py` has zero RTL/bidi awareness. An RTL paragraph authored in PowerPoint loses its direction flag on round-trip. |

**Summary of B:** Arabic **text generation** works (step 1-4 OK/DEGRADED). Arabic **shaping** works in the DOM (step 5) because the browser shapes it. Arabic **direction** is never declared anywhere in the deliverable path (steps 9-10 broken/degraded). Arabic **in tables, charts, and vector shapes** is laid out in the wrong word order (steps 6-8 broken). Arabic **font** is never chosen deliberately (step 2 degraded) — it is whatever the system falls back to.

**No tofu risk in the shipped Docker image** (Noto Arabic is installed system-wide), but the **font name recorded in the PPTX is the Latin theme font**, so a reader without that font gets an arbitrary substitution, and a reader *with* it gets Latin metrics applied to Arabic.

---

## C. The qualification cases

Ten cases, per the W13 definition. "**Assertable now**" = a test can be written today against the code as it exists (it will either pass — a regression guard — or fail — a documented gap). "**Needs new code**" = the assertion itself cannot exist until a behaviour is added.

The suite is **markup-level and model-level**, not pixel-level, because no headless browser is available in `servers/nextjs/tests/` (A.7).

### C.1 `arabic-only`
- **Fixture:** `"مرحبا بالعالم"` in a `text` element, `font.family: "Inter"`, `size: 18`, `alignment.horizontal: "left"`.
- **Must assert:** (a) the element is routed to the HTML text engine; (b) the rendered container declares a base direction that resolves to RTL; (c) the *string* is present verbatim (no escaping damage, no reordering by the renderer, no bidi control characters injected); (d) the CSS font stack names an Arabic-capable family.
- **Assertable now:** (a) yes — `shouldRenderTextElementAsHtml` already returns `true`; the existing test at `latex-html-text-rendering.test.mjs:104-110` proves it. (c) yes — the text is already emitted verbatim. (b) **no** — nothing emits `dir`; a *failing* test documents it. (d) **no** — `css-text.ts:7` names no Arabic family.
- **Also assert (Python side):** `script_profile("مرحبا بالعالم").direction == "rtl"` — **assertable now**, and already covered by `tests/test_gomrey_ocr_worker.py:29-31`.

### C.2 `english-only`
- **Fixture:** `"Hello world"` — the same element shape.
- **Must assert:** (a) the element is **not** routed to the HTML text engine; (b) the rendered markup contains **no** `dir`, no `direction`, no `unicode-bidi`; (c) the output is **byte-identical** to the pre-fix output.
- **Assertable now:** yes, entirely. This is the **regression guard** that makes every other fix safe. (c) is the strongest form: snapshot the pre-fix HTML string, then assert the post-fix HTML differs only by the additive RTL attributes.

### C.3 `mixed-arabic-english`
- **Fixture:** one paragraph, two runs: `[{text: "تقرير"}, {text: "Quarterly Report 2026"}]`.
- **Must assert:** (a) the two runs live inside **one** container (not split into separately-positioned spans — splitting destroys bidi ordering); (b) the container delegates ordering to the browser (`dir="auto"` + `unicode-bidi:plaintext`, **not** per-run `dir`); (c) the run boundaries and run-level fonts are preserved; (d) the Latin run keeps the design font.
- **Assertable now:** (a) and (c) yes — the run structure is already one container with one span per run (`template-v2-json-to-html.ts:397-402`, `:412`). (b) **no** in the export renderer.
- **Must NOT assert:** the *visual* order of the two runs. That needs a UBA engine or a browser; asserting it in-repo would be a fake test.

### C.4 `arabic-with-latin-numerals`
- **Fixture:** `"الإيرادات 2026 من 2500 دولار"` (Arabic + Western digits) and the Arabic-Indic variant `"الإيرادات ٢٠٢٦"`.
- **Must assert:** (a) the digit run stays **contiguous** in the emitted markup (no per-character wrapping, no injected LRM/RLM/`U+2066`-style isolates, no digit-by-digit splitting); (b) the source digits are preserved exactly (Western `2026` ≠ Arabic-Indic `٢٠٢٦`); (c) both numeral systems are *detected* by the classifier.
- **Assertable now:** (a) and (b) yes — the text is emitted as one escaped string (`escapeHtml`), no splitting happens in the HTML renderer. (c) yes in Python — `script_profile` already reports `arabic_indic_digits` / `western_digits` (`ocr_worker.py:78-89`), and `tests/test_gomrey_ocr_worker.py:34-36` already asserts it.
- **Why it matters:** if a future fix splits runs to apply per-script fonts, this test is what catches the "digits reversed" regression. Per CSS, `font-family` fallback is **per character**, so a correct fix does **not** need to split runs — this test should assert that no splitting happens.

### C.5 `arabic-in-table-cell`
- **Fixture:** a `table` element, one cell with `runs: [{text: "مقدمة"}]`.
- **Must assert:** (a) the cell's text container declares a direction; (b) the *cell* content is direction-resolved independently of its neighbours; (c) the table's **column order is not mirrored** (mirroring is a layout decision and explicitly out of W13 scope — assert it is *absent*, so a future mirroring change is a deliberate, visible decision); (d) in the editor, the cell is routed to the HTML text engine (currently it is not).
- **Assertable now:** (c) yes — column order is currently unchanged, and asserting it stays so is meaningful. (a), (b), (d) **no** — `renderTable` (`:454-483`) emits no `dir`, and `shouldRenderTextElementAsHtml` returns `false` for `type === "table"`.
- **Note:** (d) is the highest-risk fix in the suite — see D.2.

### C.6 `arabic-in-chart-label`
- **Fixture:** a `chart` element with `categories: ["المبيعات"]`, `series: [{name: "الإيرادات", values: [...]}]`.
- **Must assert:** (a) the Arabic label string survives verbatim into the `data-chart-config` JSON (`:1165-1167`); (b) the config carries a direction flag the chart runtime can honour; (c) the chart canvas is not given a conflicting `direction`.
- **Assertable now:** (a) yes — the config is `JSON.stringify(config)` and the label is preserved. (b) **no** — Chart.js RTL options (`plugins.legend.rtl`, `options.textDirection`) are not set.
- **Honest limit:** the *rendered* chart label is canvas-drawn; its base direction is a runtime property of Chart.js + the browser. W13 can assert the *config contract* but not the pixels.

### C.7 `arabic-in-vector-shape`
- **Fixture:** a `vector` element with an Arabic text run.
- **Must assert:** (a) the text is emitted verbatim; (b) it is not silently dropped by the vector renderer; (c) — the decisive one — the vector text is *not* laid out by the LTR segment engine, or is routed to the HTML engine.
- **Assertable now:** (a), (b) yes. (c) **no** — the vector path uses the same `layoutRenderTextRuns` split-and-place mechanism as the table path.

### C.8 `arabic-in-speaker-note`
- **Fixture:** a slide `note` containing Arabic.
- **Must assert:** (a) the note text is preserved end-to-end through the template model and the export payload; (b) no direction attribute is required (notes are not rendered on a slide) — i.e. W13 must **not** bolt `dir` onto notes.
- **Assertable now:** yes, entirely, at the model level. This is the cheapest case in the suite and it closes the "did we lose the text" question for notes.

### C.9 `arabic-plus-english-in-one-table-row`
- **Fixture:** row 0 = `["الإيرادات", "Revenue"]`.
- **Must assert:** (a) both cells' text is present and unmodified; (b) the two cells are **not** reordered (the Arabic cell does not jump to the right); (c) each cell's direction is derived from **its own** content, not from the row's or the deck's — so the Arabic cell resolves RTL and the English cell resolves LTR, in the same row.
- **Assertable now:** (a), (b) yes. (c) **no** — no per-cell direction exists. (c) is the case that proves the design decision "direction is per element, not per deck".

### C.10 `long-arabic-with-diacritics`
- **Fixture:** a 3-line Arabic sentence with tashkīl, e.g. `"اللُّغَةُ الْعَرَبِيَّةُ مِنْ أَجْمَلِ اللُّغَاتِ"`.
- **Must assert:** (a) every diacritic code point (U+064B-U+0652, U+0670) survives verbatim — count them before and after; (b) the text is not NFC/NFKC-normalised into a different form; (c) no bidi control characters are injected; (d) the string is not truncated or wrapped mid-word by the renderer.
- **Assertable now:** (a), (b), (c) yes at the markup level (the text is escaped, not transformed). (d) **no** for the HTML renderer (it does no wrapping) and **no** for the editor (the Konva engine splits on whitespace, but the HTML layer wraps in the browser — neither is measurable without a browser).
- **Diacritics are a specific risk:** a naive future "Arabic normalisation" fix (stripping tashkīl to normalise) would silently destroy content. This test is the guard.

### C.11 Suite-level properties
- **P1 — one classifier, two languages.** The TS detector (`html-text-attrs.ts:50-52`) and the Python detector (`ocr_worker.py:41-44`) currently use **different ranges** (TS omits Arabic-Indic digits U+0660-0669; TS includes U+FB1D-U+FDFF which Python also has; TS omits U+0750-077F which Python *has*). A shared fixture table must assert that both classify the same corpus identically. **Assertable now — and it will fail now**, which is the point.
- **P2 — the English path is untouched.** The C.2 byte-identical assertion must hold after every fix.
- **P3 — no glyph loss.** Every fixture's text must appear in the output with the same code-point multiset. Assertable now.
- **P4 — no fabricated claims.** The suite must not assert visual bidi order, glyph shape, kashida, or overflow. Those are not measurable in-repo (A.7).

---

## D. The fix surface

Ranked by (value, risk). **"Assertion-only"** = a test that documents current behaviour and fails; it changes no product code. **"Behaviour change"** = requires a source edit.

### D.1 — F1 ★★★★★ / LOW RISK — `servers/nextjs/lib/template-v2-json-to-html.ts` (export path)
**Behaviour change.** The single highest-value edit in W13: this file produces the actual PPTX/PDF deliverable.
1. Add a `directionOf(text)` helper (first-strong-character resolution) and emit `dir="auto"` + `unicode-bidi:plaintext` on the text/content container in `renderText` (`:391-413`) and `renderTextList` (`:415-452`).
2. Emit **logical** alignment: change `textAlign` (`:4068-4072`) to return `start`/`end`/`center`/`justify`, mapping the model's `left`→`start` and `right`→`end`. The export core already resolves `start`/`end` against `direction` (verified in the installed bundle), so this single change fixes alignment in the PPTX *and* in the PDF *and* in the HTML preview at once.
3. Emit the same on table cells (`renderTable` `:454-483` → `tableCellStyle` `:3642-…` / `cellText` `:3730-…`).
4. Change `fontStyle` (`:3501`) to emit a **fallback chain** that names an Arabic-capable family, e.g. `font-family:'Lato','Noto Naskh Arabic','Noto Sans Arabic','Noto Sans Arabic UI',sans-serif`.
**Why low risk:** additive attributes only; the export core's `start`/`end` resolver is already shipped and correct; the English path is provably unchanged (P2).
**Why highest value:** the export path is the *deliverable*. Every other fix only improves the on-screen editor.

### D.2 — F2 ★★★★☆ / MEDIUM RISK — `servers/nextjs/components/slide-editor/text/html-text-attrs.ts` + `StaticHtmlTextLayer.tsx`
**Behaviour change.**
- Extend `shouldRenderTextElementAsHtml` (`:11-35`) to cover `type === "table"` (table cells) and any other text-bearing element type. Today it returns `false` for `table`/`chart`/`vector`/`svg` (`:20, 275-276`).
- In `StaticHtmlTextLayer.tsx`, add `dir` to the outer wrapper (`:159-192`) and map `horizontal` `"left"→"start"`, `"right"→"end"` (`:186`).
- Extend the collector (`:262-296`) to descend into table cells.
**Why medium risk:** the editor's table rendering currently uses `TemplateV2TableElement.tsx` (Konva) with its own selection/hit-testing (`useTableCellSelection.ts`, `TableInlineEditor.tsx`). Routing cells to the HTML overlay must not break cell selection, double-click-to-edit, or the `layoutManaged={false}` contract at `TemplateV2KonvaSlide.tsx:3000`. **This is the one fix in W13 that can regress interactive behaviour; it needs its own manual UI check.**

### D.3 — F3 ★★★★☆ / LOW RISK — `servers/nextjs/components/slide-editor/text/css-text.ts` (one function)
**Behaviour change.** `cssFontFamilyStack` (`:1-8`) becomes script-aware:
```ts
export function cssFontFamilyStack(family: string) {
  return `"${esc}", "Noto Naskh Arabic", "Noto Sans Arabic", "Noto Sans Arabic UI", Helvetica, sans-serif`;
}
```
**Why low risk:** the chain is only a *fallback*; Latin glyphs still come from `family` first. This single edit makes the editor surface, the inline Tiptap editor (`TiptapInlineTextEditor.tsx:979`), and the measurement font (`template-v2-text.ts:1618`) all name an Arabic face. Because the Docker image already ships Noto Naskh Arabic / Noto Sans Arabic (A.2), **no new font binary is required** and no licence question is opened.

### D.4 — F4 ★★★☆☆ / LOW RISK — `servers/nextjs/components/slide-editor/text/template-v2-text.ts` (measurement font)
**Behaviour change.** `richFontCss` (`:1615-1619`) must use the **same** stack as the renderer, otherwise measurement and render disagree. Today they already disagree (measure = `"Lato", Helvetica, sans-serif`; export render = `font-family:'Lato'`). Route both through `cssFontFamilyStack`.
**Note:** the Konva path's own stack (`nodes.tsx:2589, 2648`, `TemplateV2TableElement.tsx:281`) is a *third* variant. Consolidating all four onto one function is the correct cleanup and removes the `, Inter` inconsistency in the table path.

### D.5 — F5 ★★★☆☆ / MEDIUM RISK — `servers/fastapi/templates/v2/models/elements.py` (+ `templates/v2/schema.py`)
**Behaviour change.** Add an optional `direction: Optional[Literal["auto","ltr","rtl"]] = None` to `Text` (`:203-222`) and `TextList`, and add `START="start"` / `END="end"` to `HorizontalAlignment` (`:30-34`).
**Why medium risk:** `elements.py` feeds the LLM JSON schema (`templates/v2/schema.py`), so the schema change ripples into the generation prompt, the Next.js model reader (`components/slide-editor/model/model.ts`), and the canonical-model compatibility test (`servers/nextjs/tests/template-v2-canonical-model-compatibility.ts`). **This can wait for a later wave** — D.1's `dir="auto"` already produces correct direction *without* a schema change, because `auto` derives from content.

### D.6 — F6 ★★☆☆☆ / LOW RISK — `servers/nextjs/lib/template-theme.ts` + `servers/fastapi/templates/v2/theme.py`
**Behaviour change.** Extend the theme font model from one font to an optional **per-script map**: `TemplateThemeTextFont` (`:23-26`) gains `scripts?: { arabic?: {name, url} }`, and `theme.py`'s `materialize_theme` (`:382-400`) gains a matching slot. The selection rule: use the script-specific font when the deck's language is RTL, else the dominant font.
**Note:** this is the *only* way to make the Arabic face a **deliberate design choice** rather than a system fallback. It is also the only place `language` would legitimately influence typography. It is lower value than D.1 because the *default* (system Noto Arabic) already renders without tofu.

### D.7 — F7 ★★★☆☆ / LOW RISK — shared script/direction classifier
**Behaviour change + assertion-only.** `servers/fastapi/gomrey/ocr_worker.py:41-89` already has a correct `script_profile`. Extract the ranges into a shared, single-source module (e.g. `servers/fastapi/templates/v2/text_direction.py`) and have the TS detector mirror it. The suite then asserts the two agree (C.11 P1). **This is the fix that makes the two-language agreement enforceable rather than accidental.**

### D.8 — F8 ★★☆☆☆ / LOW RISK — the qualification suite itself
**New files** (see F-section below).

### D.9 — Explicitly OUT of W13 scope (documented, not fixed)
- **PPTX import `<a:pPr rtl="1">`** — the reader lives in the obfuscated external export-core (`presentation-export/node_modules/@presenton/export-core/dist/index.js`); the repo has no hook. `pptx_font_utils.py` could *detect* RTL paragraphs in the raw OOXML and surface them as a **degraded observation** (the repo's established pattern — see `ocr_worker.py:141-151` `quality_observations`), but it cannot fix the import. **Round-trip fidelity is W12's wave.**
- **Canvas/Konva Arabic layout.** Fixing it means writing a bidi + shaping engine for canvas, or routing every text-bearing element to the DOM. The second is D.2. The first is out of scope.
- **Chart.js RTL runtime** — assert the *config contract* only.
- **Arabic typography** — kashida justification, Arabic line spacing, `Noto Naskh` vs `Noto Sans Arabic` selection, Arabic-style numerals. Out of scope.
- **Mirrored layouts** (RTL slide masters, right-side bullet markers, right-to-left chart axes, right-to-left progress bars). Out of scope; W13 asserts they are *absent* so that adding them is a visible decision.

---

## E. The design decisions

### E.1 How direction is decided — per element, from content, never per deck
**Decision:** direction is a property of **one text element**, resolved from **that element's own first strong character**, emitted as `dir="auto"` (plus `unicode-bidi:plaintext` on the content span).

**Why per element, not per deck:** a real Arabic deck mixes scripts. A chart legend may be English, a table header Arabic, a caption English. A deck-level direction flag forces all of them to one base direction and breaks the mixed case (C.9).

**Why `auto` and not a computed `rtl`/`ltr`:** `dir="auto"` is the CSS-native, bidi-correct way to derive the base direction from the first strong character — it is exactly what the editor's HTML layer already does (`StaticHtmlTextLayer.tsx:194`), and it is *per paragraph*, so a single element containing two paragraphs of different scripts resolves each correctly. A JS-computed `rtl`/`ltr` on the container would apply one base direction to the whole element.

**Why `unicode-bidi:plaintext`:** it makes the UBA determine the base level *per paragraph* rather than per element, which is what a reader expects from a multi-paragraph text box.

**Resolution rule (identical in TS and Python):** scan the element's concatenated run text; the first character with strong bidi type determines the base direction. R (Hebrew/Arabic) → RTL; L (Latin/Greek/Cyrillic) → LTR; no strong character → LTR. Digits and punctuation are *not* strong and do not decide. This is the same rule as `dir="auto"` in CSS, so **the JS classifier and the browser agree** — the JS classifier is only needed where a *decision* is required (schema defaults, test expectations, the `shouldRenderTextElementAsHtml` gate), not to set the attribute.

**Element-level `direction` override:** D.5's optional `direction` field lets a template or the LLM pin an element to `ltr`/`rtl` regardless of content. It is **optional and off by default**; `auto` is the default everywhere.

### E.2 How a script-appropriate font is selected without shipping a licensed font binary
**Decision:** name an **already-installed, SIL-OFL, Arabic-capable family** in the CSS fallback chain, and make the *recorded* PPTX font name a portable one.

**The chain (both the editor stack and the export stack):**
```
"<design font>", "Noto Naskh Arabic", "Noto Sans Arabic", "Noto Sans Arabic UI", Helvetica, sans-serif
```
**Why this needs no new binary:**
- `Dockerfile:95-97` already installs `fonts-noto-core` (contains **Noto Naskh Arabic**) and `fonts-noto-ui-core` (contains **Noto Sans Arabic UI**). These are SIL OFL 1.1, redistributable, and already in the image.
- The repo already vendors OFL fonts (Lato, Inter, Noto Serif, Noto Sans Mono, …) in `servers/nextjs/public/vendor/fonts/` with 222 files, and `NOTICE` covers them. So a Noto Arabic file *could* be vendored under the same licence — but it is **not needed**, and vendoring a new binary is exactly the kind of asset-rights decision W13 should not make unilaterally.
- `Noto Naskh Arabic` is a **serif/naskh** face, `Noto Sans Arabic` a **sans** face. Putting Naskh first gives Arabic body copy the conventional naskh look; a template that wants sans Arabic can reorder the chain. The ordering is a one-line change.

**Per-script *selection* (not just fallback):** CSS per-glyph fallback means an Arabic character inside a Latin-design run automatically lands on the Arabic face. That is sufficient for correctness and requires **no run splitting** — which is exactly why C.4 and C.3 must assert that no splitting happens.

**The PPTX-facing font name.** This is the subtle part. The export core reads the *computed* `font-family` and writes it into the PPTX run properties. If the computed family is `'Lato','Noto Naskh Arabic',…`, PowerPoint will try `Lato` first, find no Arabic glyphs, and substitute — possibly badly. So the **export** font stack should lead with a **portable Arabic-capable family for RTL content**, and the design font for Latin content, with the *run* split only when the element direction is RTL. Concretely, for an RTL element the export stack should be `"<portable-arabic-family>", "Noto Naskh Arabic", <design font>, sans-serif`.
- **Portable Arabic-capable families** that exist on Windows PowerPoint, macOS, and (as a system font) Linux: **Arial** (Windows/macOS/corefonts) and **Tahoma** (Windows). Both are on the repo's `SYSTEM_FONT_FAMILY_KEYS` skip-list (`local-fonts.ts:181-200`) and are **deleted** from the Docker image (`Dockerfile:115-117`) — so they must be named *first* but cannot be relied on for *rendering* in the container; the Noto entries behind them carry the render. On the render side in the container, the Noto entry wins because Arial/Tahoma aren't installed.
- **Consequence for the PPTX:** the recorded font name should be the **portable** one for RTL runs, so the deck opens with correct Arabic on a reader's machine.

**Bring-your-own (the licensed-font escape hatch).** `servers/fastapi/api/v1/ppt/endpoints/fonts.py` already implements font upload (persisting via `utils/ns.py`); a template's `fonts.textFont.url` can point at an uploaded font. D.6's per-script theme slot lets a deployment that has licensed Arabic fonts point at them. **This is the route for any deployment that must not rely on Noto.**

### E.3 How mixed-script runs are handled
**Decision:** mixed runs are handled by **the browser**, not by the renderer. One container, one `dir="auto"`, one `unicode-bidi:plaintext`, one `<span>` per run, and **no per-run `dir`, no bidi isolate characters, no run reordering, no run splitting**.

**Why:** the Unicode Bidirectional Algorithm is a solved problem with a reference implementation in every browser and in the export core's rendering engine. Re-implementing it in the renderer would be strictly worse. The renderer's only jobs are (1) declare a base direction and (2) not destroy the logical order.

**The two things a naive fix gets wrong, and the tests that catch them:**
1. **Splitting runs to apply a per-script font.** This destroys the UBA's ability to reorder across the split, and it reverses digits inside a split (C.4, C.10). CSS per-glyph fallback makes the split unnecessary. → C.3, C.4 assert no splitting.
2. **Setting `dir` per run.** A `dir="ltr"` on the English run inside an Arabic paragraph creates a *separate* bidi context and moves the run to a different position than the reader expects. → C.3 asserts a single container and no inner `dir`.

**The one place a split IS legitimate:** an RTL element whose *design* wants a different face for the Latin portion of a mixed paragraph (a real typographic need — Arabic decks often set Latin in a Latin face). That is a **run-level font** change only (`font-family` on the span), never a `dir` change and never a container split. The existing run model (`TextRun.font`, `elements.py:181-190`) already carries per-run fonts, so this needs no schema change.

### E.4 The honest "supported" claim
**W13 may claim:**
1. Arabic text is **shaped** (initial/medial/final forms, ligatures) in the DOM/HTML export path — the browser engine does it.
2. Arabic text is **ordered per the UBA within a paragraph** in the DOM/HTML export path.
3. Elements whose content is Arabic resolve to an **RTL base direction** and are **right-aligned** (via logical `start`/`end`).
4. **Mixed Arabic/English paragraphs** resolve per the UBA with a single base direction derived from content.
5. **No glyph loss** in the shipped container image: Arabic resolves to an installed Noto Arabic face, not tofu.
6. **Text fidelity**: diacritics, Arabic-Indic digits, and Western digits all survive generation → template → render → export → re-import byte-for-byte.
7. The editor surface and the export surface now agree on direction for `text` and `text-list`.

**W13 must NOT claim:**
- **Full Arabic typography parity.** No kashida justification, no Arabic-specific line spacing, no Arabic-aware line-breaking rules (a real Arabic typesetter breaks on word boundaries with different rules), no Arabic-Indic numeral normalisation, no contextual `Noto Naskh` vs `Noto Sans Arabic` selection.
- **Visual bidi correctness as a *tested* property.** The suite asserts *markup contract*, not rendered order. A human must eyeball a rendered deck; W13 supplies the fixtures and the harness for that, and says so.
- **Bidi fidelity in the exported PPTX.** The export core is external, obfuscated, and its `rtl` handling is limited to resolving `text-align:start/end` against the DOM's computed `direction`. Whether PowerPoint's own bidi engine reorders the exported runs correctly is **not observable in-repo** and is **W12's** round-trip concern.
- **Round-trip preservation of `<a:pPr rtl="1">`.** The import path demonstrably drops it.
- **RTL layout mirroring** — slide masters, bullet sides, chart axes, progress bars, column order. W13 asserts these are *absent*.
- **Any Arabic/OCR accuracy percentage.** The repo's own rule (`ocr_worker.py:20-22`: "no accuracy percentages are asserted here; coverage and explicit uncertainty remain the contract") applies: W13 asserts **coverage** (N cases exercised, each with a named assertion) and **explicit uncertainty** (which assertions are markup-level, not pixel-level).

**The one-line claim W13 should be willing to make:** *"Arabic and mixed Arabic/English text is measured, direction-correct and glyph-complete through generation, template hydration, DOM rendering and export; Arabic-specific typography and exported-PPTX bidi fidelity are explicitly out of scope and tracked."*

---

## F. Test plan

### F.1 Files to create

| Path | Language | Runner | Content |
|---|---|---|---|
| `servers/fastapi/tests/qualification/__init__.py` | Python | pytest | package marker (matches `tests/mocks/__init__.py`, `tests/__init__.py`) |
| `servers/fastapi/tests/qualification/arabic_rtl_contract.json` | JSON | — | **the shared fixture table** (see F.3) |
| `servers/fastapi/tests/qualification/test_arabic_rtl_qualification.py` | Python | pytest | the FastAPI-side cases (C.1, C.4, C.8, C.9, C.10 model-level; C.11 P1) |
| `servers/nextjs/tests/arabic-rtl-qualification.test.mjs` | JS | `node --test` | the renderer-side cases (C.1, C.2, C.3, C.5, C.6, C.7, C.8, C.9, C.10) |

`IMPLEMENTATION_GRAPH.md:203` names `servers/fastapi/tests/qualification/` as W13's file location; the nextjs half is added because **all** the code under test lives in `servers/nextjs/`.

### F.2 Files to modify

| Path | Change | Wave |
|---|---|---|
| `servers/nextjs/lib/template-v2-json-to-html.ts` | D.1 — `dir` + `unicode-bidi` + logical `text-align` + font chain | F1 |
| `servers/nextjs/components/slide-editor/text/css-text.ts` | D.3 — script-aware `cssFontFamilyStack` | F3 |
| `servers/nextjs/components/slide-editor/text/template-v2-text.ts` | D.4 — `richFontCss` uses the shared stack | F4 |
| `servers/nextjs/components/slide-editor/text/html-text-attrs.ts` | D.2 — cover `table` cells; align the detector with the Python one | F2 |
| `servers/nextjs/components/slide-editor/text/StaticHtmlTextLayer.tsx` | D.2 — outer `dir`, logical alignment | F2 |
| `servers/nextjs/components/slide-editor/surface/nodes.tsx` | D.4 — route the Konva stack through the shared helper (consistency only) | F4 |
| `servers/nextjs/components/slide-editor/tables/TemplateV2TableElement.tsx` | D.4 — same (removes the `, Inter` variant) | F4 |
| `servers/fastapi/gomrey/ocr_worker.py` | D.7 — extract the ranges into a shared module (re-export, no behaviour change) | F7 |

**Schema/theme changes (D.5, D.6) are explicitly deferred** to a later wave so W13 stays a measure-first grain with a small, reversible diff.

### F.3 The shared contract fixture
`servers/fastapi/tests/qualification/arabic_rtl_contract.json`:
```json
{
  "script_ranges": {
    "arabic": "\\u0600-\\u06FF\\u0750-\\u077F\\uFB50-\\uFDFF\\uFE70-\\uFEFF",
    "latin": "[A-Za-z]",
    "arabic_indic_digits": "\\u0660-\\u0669",
    "western_digits": "[0-9]"
  },
  "cases": [
    { "id": "arabic-only",            "text": "مرحبا بالعالم",                       "expected_direction": "rtl"   },
    { "id": "english-only",           "text": "Hello world",                        "expected_direction": "ltr"   },
    { "id": "mixed-arabic-english",   "text": "تقرير Report 2026",                   "expected_direction": "mixed" },
    { "id": "numerals-both-systems",  "text": "الإيرادات 2026 من ٢٥٠٠",              "expected_direction": "rtl"   },
    { "id": "long-arabic-diacritics", "text": "اللُّغَةُ الْعَرَبِيَّةُ مِنْ أَجْمَلِ", "expected_direction": "rtl"   }
  ],
  "required_html_attributes": {
    "text_container":     ["dir", "unicode-bidi"],
    "logical_alignment": ["start", "end"]
  },
  "arabic_capable_families": ["Noto Naskh Arabic", "Noto Sans Arabic", "Noto Sans Arabic UI"]
}
```
The **Python** test reads it with `Path(__file__).parent / "arabic_rtl_contract.json"`. The **Next.js** test reads it with `path.resolve("../fastapi/tests/qualification/arabic_rtl_contract.json")` (cwd is `servers/nextjs`). The Next.js test **must fail loudly** (not skip) if the file is missing, with a message naming the expected path. See G.3 for the coupling risk.

### F.4 Concrete test names

**`servers/nextjs/tests/arabic-rtl-qualification.test.mjs`** (node:test; esbuild-bundles `lib/template-v2-json-to-html.ts`, `components/slide-editor/text/html-text-attrs.ts`, `components/slide-editor/text/css-text.ts`, `components/slide-editor/text/local-fonts.ts` in one synthetic `entry.ts`, following `template-theme-infographics.test.mjs:14-24`):

1. `routes Arabic text elements through the HTML text engine`
2. `routes Arabic table cells through the HTML text engine` — *fails today*
3. `emits a direction-resolved container for Arabic runs` — *fails today*
4. `emits logical start alignment instead of physical left` — *fails today*
5. `keeps English text free of direction overrides` — *passes today; regression guard*
6. `keeps mixed Arabic and English in one paragraph container` — *fails today (no `dir`)*
7. `preserves Arabic digits and diacritics verbatim in the rendered markup` — *passes today*
8. `names an Arabic-capable fallback family in the CSS font stack` — *fails today*
9. `renders Arabic table cells with per-cell direction` — *fails today*
10. `keeps chart label Arabic text intact in the chart config` — *passes today for the string; the direction flag is a separate assertion*
11. `preserves Arabic vector shape text verbatim` — *passes today for the string*
12. `preserves Arabic speaker-note text through the template model` — *passes today*

**`servers/fastapi/tests/qualification/test_arabic_rtl_qualification.py`** (pytest; plain `def test_*() -> None:`):

1. `test_script_profile_matches_the_shared_contract`
2. `test_script_profile_classifies_arabic_english_and_mixed`
3. `test_script_profile_reports_both_numeral_systems`
4. `test_script_profile_preserves_diacritic_coverage`
5. `test_direction_defaults_to_ltr_for_content_without_strong_characters`
6. `test_element_schema_declares_no_direction_field` — *assertion-only; documents that the schema has no direction today; becomes a failing test when D.5 lands*
7. `test_theme_font_model_exposes_a_single_font_slot` — *assertion-only; same rationale for D.6*
8. `test_pptx_font_utils_has_no_rtl_awareness` — *assertion-only; documents the import gap for W12*
9. `test_ocr_worker_script_profile_agrees_with_the_shared_contract`

**Naming convention** matches the repo exactly: `test_*` snake_case in Python, `test("sentence", …)` in JS. The Python file follows `servers/fastapi/tests/test_gomrey_ocr_worker.py` (module docstring, `import pytest`, a private `_helper` for fixtures, plain asserts).

### F.5 How to run
```bash
# Next.js (cwd = servers/nextjs)
cd servers/nextjs && npm test

# FastAPI (cwd = servers/fastapi)
cd servers/fastapi && uv run pytest tests/qualification -v
```
`servers/fastapi/pyproject.toml:66-67` sets `testpaths = ["tests"]`, so the new directory is picked up automatically.

### F.6 The suite's own acceptance criterion
W13 is complete when: **every one of the 10 cases has at least one named assertion; every assertion is either passing (a verified property) or failing-with-a-documented-cause (a known gap); and the "English path is untouched" assertion passes.** A test that fails because the *fix* has not landed yet is a **defect report**, not a reason to relax the assertion. A test that fails because the *expectation* was wrong is a **contract change** and must be argued in the design, not silently edited.

---

## G. Risks and non-goals

### G.1 The biggest risk — **the "supported" claim outruns the evidence**
The temptation in W13 is to say "Arabic is supported" because the text *renders*. But the evidence available in-repo is **markup-level**: the suite can prove that a direction attribute is emitted, that a font family is named, that the string is intact. It **cannot** prove that the rendered glyph order is right, that the PPTX reorders correctly, or that the Arabic typography looks right.

**Mitigation:** the report template must carry a **per-assertion evidence class** — `markup` / `model` / `rendered` — and the summary must state, in those words, which classes were exercised. W13's headline claim is restricted to the classes it actually measured.

**Corollary:** if the suite only asserts markup, W13 is a *contract* test, not a *behaviour* test. That is still worth doing (it is the only kind available in this repo without a browser) — but it must be named as such. A follow-up that runs the real Chromium (via the export-core's bundled browser, `electron/scripts/prepare-export-chromium.cjs`) against the `/pdf-maker` page and screenshots the slides would convert markup assertions into rendered assertions. **That is the single highest-value follow-up after W13, and it is deliberately not in W13's scope.**

### G.2 Second risk — **the fix could make the export worse**
D.1 changes the *export* renderer, whose output feeds an **external, obfuscated** package that we cannot read. Changing `text-align:left` → `text-align:start` and adding `dir` could:
- make the export core's alignment resolver take a path it has never taken in this codebase, and
- change how the core measures and positions text (it measures elements in a 3000px-wide viewport — see the comment at `PdfMakerPage.tsx:46-50`).

**Mitigation:** (a) C.2's byte-identical English assertion proves the English path is unchanged; (b) the first change to land should be `dir`/`unicode-bidi` **without** the logical-alignment switch, so the two can be bisected independently; (c) an end-to-end smoke (generate one Arabic deck, export one PPTX, reopen it) must be run manually before W13 closes. **W13 must not close on unit tests alone.**

### G.3 Third risk — **cross-directory test coupling**
The Next.js test would read a fixture owned by the FastAPI test tree (`../fastapi/tests/qualification/...`). The Next.js Docker stage copies only `servers/nextjs` (`Dockerfile:36-44`) — but that stage runs `npm run build`, not `npm test`, so nothing breaks today. A future CI step that runs `npm test` inside a Next.js-only image would fail.
**Mitigation:** the test must **fail with an actionable message** (not skip) if the contract file is missing, and the design should note the alternative (duplicate the fixture and add a drift test). Accepted as a known, documented coupling.

### G.4 Fourth risk — **font substitution masks the bug during local development**
On macOS, Chromium substitutes an Arabic-capable system font, so Arabic *looks* fine locally even when the container would render differently. A developer could conclude "it works" from a macOS screenshot.
**Mitigation:** the qualification suite must assert the **named** family in the markup, not the rendered pixels. The "named family" assertion is exactly what catches the macOS-vs-container divergence.

### G.5 Fifth risk — **over-claiming through the `auto` keyword**
`dir="auto"` is correct but it is *content-derived*. A slide whose first strong character is a Latin brand name (e.g. a title starting `"Gomrey —"` followed by an Arabic subtitle) resolves **LTR** even if the deck is Arabic. This is standard CSS behaviour and matches what a native Arabic reader would see in a browser, but it is **not** what an Arabic designer expects.
**Mitigation:** D.5's optional per-element `direction` override is the escape hatch, and it is deliberately deferred — W13 should measure the `auto` behaviour first and let the evidence drive whether the override is needed. **Do not add a deck-level `direction` flag to "fix" this**; that is the per-deck anti-pattern E.1 rejects.

### G.6 Non-goals — what W13 must NOT do
- **Must not** claim full Arabic typography parity (kashida, Arabic line-breaking, Arabic-Indic normalisation, naskh vs sans selection).
- **Must not** claim exported-PPTX bidi fidelity (the core is external; the reader drops `rtl="1"`).
- **Must not** claim round-trip preservation of RTL paragraph properties — that is **W12**.
- **Must not** implement bidi or Arabic shaping in the renderer — delegate to the browser.
- **Must not** mirror layouts (slide masters, bullet sides, chart axes, column order, progress bars). W13 asserts these are **absent** so that adding them later is a visible, deliberate act.
- **Must not** vendor a new font binary. Noto Naskh Arabic / Noto Sans Arabic are already in the deployment image; a deployment that needs a specific licensed Arabic face must use the existing font-upload path (`servers/fastapi/api/v1/ppt/endpoints/fonts.py`) — a **product/rights decision, not an engineering one**.
- **Must not** change the LLM layout prompt to ask for RTL layouts. That is a W6/W11 (artifact IR) concern; W13 is measurement.
- **Must not** add a headless-browser dependency to `servers/nextjs/` in W13. It would be the right long-term move but it changes the dependency surface and the Docker build; the export-core already bundles Chromium, and a follow-up can use it.
- **Must not** assert a visual result. No "the Arabic reads rightward" assertion without a rendering engine. No accuracy percentages — the repo's rule (`ocr_worker.py:20-22`) is coverage and explicit uncertainty, not accuracy.
- **Must not** extend the `language` request field into a locale enum or a BCP-47 tag in W13. `language` is a prompt string today (A.6); turning it into a locale is a separate API change with a migration story.

### G.7 Coverage statement W13 should publish
W13's report should carry, verbatim, the nine `ARABIC_P0_CASES` names from `servers/fastapi/gomrey/ocr_worker.py:46-56` **and** W13's own ten rendering case names, with a cross-reference column stating which are *ingestion* cases (already qualified by P06-G3) and which are *rendering* cases (qualified by W13). This keeps the repo's two Arabic suites legible as one program rather than two overlapping lists, and it makes the coverage claim auditable: **N cases, M assertions, K evidence classes, 0 accuracy claims.**

---

## Appendix — citation index

| # | Claim | Location |
|---|---|---|
| 1 | RTL detection + DOM routing (text, text-list only) | `servers/nextjs/components/slide-editor/text/html-text-attrs.ts:11-52` |
| 2 | `dir="auto"` + `unicode-bidi:plaintext` (editor only) | `servers/nextjs/components/slide-editor/text/StaticHtmlTextLayer.tsx:193-203` |
| 3 | `unicode-bidi:plaintext` (inline editor, no `dir`) | `servers/nextjs/components/slide-editor/text/TiptapInlineTextEditor.tsx:979` |
| 4 | Editor font stack, Latin-only | `servers/nextjs/components/slide-editor/text/css-text.ts:1-8` |
| 5 | Font catalogue, 111 families, zero Arabic | `servers/nextjs/components/slide-editor/text/local-fonts.ts:70-172` |
| 6 | `SYSTEM_FONT_FAMILY_KEYS` incl. `tahoma`, `arial` | `servers/nextjs/components/slide-editor/text/local-fonts.ts:181-200` |
| 7 | Font-load signature, family-only, no script | `servers/nextjs/components/slide-editor/surface/fontLoading.ts:153-168, 258-267` |
| 8 | Canvas measurement (width-based, browser-shaped) | `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1626-1638` |
| 9 | Measurement font stack (Latin-only) | `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1615-1619` |
| 10 | Whitespace split → LTR segment layout (split regex at `:1036`) | `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1002-1068` |
| 11 | `lineStartX` — LTR only | `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1144-1157` |
| 12 | `readHorizontalAlignment` — `left` default | `servers/nextjs/components/slide-editor/text/template-v2-text.ts:1640-1652` |
| 13 | Konva text, LTR x advance | `servers/nextjs/components/slide-editor/surface/nodes.tsx:2500, 2537, 2582-2600` |
| 14 | Konva text-list, LTR | `servers/nextjs/components/slide-editor/surface/nodes.tsx:2641-2658` |
| 15 | Konva table cell, LTR, `, Inter` | `servers/nextjs/components/slide-editor/tables/TemplateV2TableElement.tsx:243-291` |
| 16 | HTML renderer: **zero** `dir`/`bidi` | `servers/nextjs/lib/template-v2-json-to-html.ts` (4145 lines, verified zero matches) |
| 17 | `renderText` — physical `text-align`, no `dir` | `servers/nextjs/lib/template-v2-json-to-html.ts:391-413` |
| 18 | `textAlign` — `left` default, no `start`/`end` | `servers/nextjs/lib/template-v2-json-to-html.ts:4068-4072` |
| 19 | `fontStyle` — single family, no fallback | `servers/nextjs/lib/template-v2-json-to-html.ts:3491-3516` |
| 20 | `renderTable` / `tableCellStyle` / `cellText` — no `dir` | `servers/nextjs/lib/template-v2-json-to-html.ts:454-483, 3642-…, 3730-…` |
| 21 | `renderChart` — canvas, no direction | `servers/nextjs/lib/template-v2-json-to-html.ts:1157-1170` |
| 22 | Export path = DOM path | `servers/nextjs/app/(presentation-generator)/components/TemplateV2HtmlSlidePreview.tsx:257-262`; `servers/nextjs/app/(export)/pdf-maker/PdfMakerPage.tsx:19-21` |
| 23 | Export task shape | `servers/nextjs/lib/run-bundled-presentation-export.ts:179-186` |
| 24 | Export core version | `presentation-export/presenton-export-version.json` (v1.0.34) |
| 25 | Export core resolves `start`/`end` vs `direction:rtl`; 2 `rtl` occurrences total; no DOM `dir` read; no `rtl="1"` write | `presentation-export/node_modules/@presenton/export-core/dist/index.js` |
| 26 | PPTX import delegates to the external core | `servers/fastapi/services/export_task_service.py:690-729, 460-…` |
| 27 | `pptx_font_utils.py` — no RTL/bidi/Arabic | `servers/fastapi/templates/pptx_font_utils.py` (1668 lines, verified zero matches) |
| 28 | `language` request field (free-form `Optional[str]`) | `servers/fastapi/models/generate_presentation_request.py:25-28, 52` |
| 29 | `language` → prompt string only | `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py:126-127, 169-177, 196-208` |
| 30 | Theme font: template-dominant, no language input | `servers/fastapi/templates/v2/theme.py:382-400`; `servers/nextjs/lib/template-theme.ts:329-352` |
| 31 | Theme font model = one font | `servers/nextjs/lib/template-theme.ts:23-30` |
| 32 | Element schema: no `direction`, alignment enum without `start`/`end` | `servers/fastapi/templates/v2/models/elements.py:30-34, 121-124, 203-222` |
| 33 | Python script/direction classifier (**the reusable asset**) | `servers/fastapi/gomrey/ocr_worker.py:41-56, 78-89` |
| 34 | Frozen Arabic P0 case names | `servers/fastapi/gomrey/ocr_worker.py:46-56`; `docs/MASTER_PLAN.md:263-273` |
| 35 | Python Arabic test conventions | `servers/fastapi/tests/test_gomrey_ocr_worker.py:1-37` |
| 36 | Next.js test conventions (node:test + esbuild) | `servers/nextjs/tests/latex-html-text-rendering.test.mjs:1-36`; `template-v2-json-to-html-metadata.test.mjs:1-38`; `template-theme-infographics.test.mjs:14-24`; `pdf-maker-export-layout.test.mjs:10-19` |
| 37 | No headless browser in nextjs tests | `servers/nextjs/package.json` (no puppeteer/playwright/jsdom); `Dockerfile:36-44` (build only) |
| 38 | pytest config | `servers/fastapi/pyproject.toml:66-67`; `servers/fastapi/tests/conftest.py` |
| 39 | Noto Arabic in the image; non-Noto fonts deleted | `Dockerfile:95-97, 115-117`; `Dockerfile.dev:26-30, 44-46` |
| 40 | `LanguageType.Arabic` exists in the UI | `servers/nextjs/app/(presentation-generator)/upload/type.ts:31` |
| 41 | W13 definition | `research/rea/2026-10-22-nextslide-gamma/IMPLEMENTATION_GRAPH.md:201-208` |
| 42 | i18n gap row | `docs/NO_GAPS_CHECKLIST.md:85` |
| 43 | Font upload path (bring-your-own licensed font) | `servers/fastapi/api/v1/ppt/endpoints/fonts.py` |
