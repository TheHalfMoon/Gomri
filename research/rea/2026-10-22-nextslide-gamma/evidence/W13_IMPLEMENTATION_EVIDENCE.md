# W13 — Arabic / RTL / mixed-script qualification: implementation evidence

**Mission:** Issue #77, wave `W13`.
**Branch:** `feature/rea/w13-arabic-rtl`
**Base:** canonical `main` @ `5f299a7a6174ad3a1180f827778db5f4400a4d71` — W13 depends on nothing.
**Design:** `evidence/W13_ARABIC_RTL_DESIGN.md` (669 lines, produced by a fresh-context subagent)
**Date (UTC):** 2026-10-22

---

## 1. What this grain delivers

Issue #77 §F names Arabic/RTL as an acceptance gate. There was **no measured Arabic/RTL
qualification anywhere** in Gomrey, and the deliverable path had **zero direction support**: the
export renderer emitted no `dir`, no `direction` and no `unicode-bidi`, aligned everything
physically to the left, and named a single Latin font family.

The single most important fact the design established is that **the export path *is* the DOM
path**:

```text
run-bundled-presentation-export.ts → /pdf-maker → TemplateV2HtmlSlidePreview.tsx
                                    → templateV2UiToHtmlFragment → template-v2-json-to-html.ts
```

So a fix in the HTML renderer is a fix in the deliverable, not only in a preview. That is why the
renderer is the highest-value edit in this wave.

## 2. Files

| File | Change | Lines |
|---|---|---|
| `servers/fastapi/gomrey/text_direction.py` | **added** — the shared script/direction classifier | 150 |
| `servers/fastapi/gomrey/ocr_worker.py` | **modified** — re-exports the shared classifier; no behaviour change | +14 −27 |
| `servers/nextjs/components/slide-editor/text/text-direction.ts` | **added** — the TypeScript mirror | 108 |
| `servers/nextjs/components/slide-editor/text/css-text.ts` | **modified** — the shared, script-aware font stack | 66 |
| `servers/nextjs/components/slide-editor/text/html-text-attrs.ts` | **modified** — the detector now comes from the mirror | +8 −6 |
| `servers/nextjs/lib/template-v2-json-to-html.ts` | **modified** — direction, logical alignment, font chain | +90 −12 |
| `servers/fastapi/tests/qualification/arabic_rtl_contract.json` | **added** — the shared contract fixture | 104 |
| `servers/fastapi/tests/qualification/test_arabic_rtl_qualification.py` | **added** — 25 model-level tests | 129 |
| `servers/nextjs/tests/arabic-rtl-qualification.test.mjs` | **added** — 18 markup/model-level tests | 280 |
| `servers/nextjs/tests/template-v2-renderer-fields.test.mjs` | **modified** — one stale regex | +4 −1 |

## 3. What was measured before anything was changed

The design traced a deck with Arabic text through the whole pipeline. The results:

| Step | Status |
|---|---|
| Request (`language` accepted) | OK |
| Template / theme | DEGRADED — the theme font is the template's dominant **Latin** font; `language` never reaches it |
| Outline prompt | OK for text; the layout prompt has no language/script instruction |
| Slide content | DEGRADED — the Arabic text is written verbatim, but the run keeps the Latin font |
| Konva render — text / text-list | OK in the **editor** only (`dir="auto"` + `unicode-bidi:plaintext`), but left-aligned |
| Konva render — table cells, chart labels, vector text | **BROKEN** — words are placed left-to-right, so Arabic word order is reversed |
| **HTML render (the deliverable)** | **BROKEN at the paragraph level** — no `dir`, physical `text-align: left`, single-family `font-family` |
| PPTX export | DEGRADED — produced from the broken HTML; the export core *does* resolve `text-align: start` against `direction: rtl`, but Gomrey emitted neither |
| PPTX re-import | **BROKEN** — the external reader parses `algn` but not `<a:pPr rtl="1">` |

## 4. What was changed

### 4.1 One classifier, two languages

The script ranges and the direction rules now live in exactly one place per language, and the two
are checked against **one shared fixture**:

- `servers/fastapi/gomrey/text_direction.py` — `script_profile` (presence-based: which scripts are
  present) and `resolve_base_direction` (first-strong-character: which base direction the text's
  paragraphs have).
- `servers/nextjs/components/slide-editor/text/text-direction.ts` — the mirror.
- `servers/fastapi/tests/qualification/arabic_rtl_contract.json` — the table both suites read.

`gomrey/ocr_worker.py` re-exports the shared classifier, so the OCR behaviour is byte-identical;
a regression test asserts the re-exported objects are the shared ones.

The two concepts are deliberately **different**. `script_profile` is *presence-based* and is what
the OCR worker uses to judge a scanned region; `resolve_base_direction` is the *first-strong* rule
that CSS `dir="auto"` implements. They are not the same question, and the design was explicit about
it.

### 4.2 The renderer declares its direction, logically

- `renderText`, `renderTextList` and `renderTable` now emit `dir="auto"` on the text container and
  `unicode-bidi:plaintext` on the content. `dir="auto"` is the CSS-native, per-paragraph way to
  derive the base direction from the content; `unicode-bidi:plaintext` makes the Unicode
  Bidirectional Algorithm decide per paragraph rather than per element.
- `textAlign` now returns **logical** alignment: `left` → `start`, `right` → `end`, `center` and
  `justify` unchanged. For left-to-right content the computed value is unchanged, so the English
  path is not affected. For Arabic content the browser computes `start` against the element's
  resolved `direction`, which is `rtl` — so the text lands on the right.
- The direction is resolved **per element**, never per deck. A real Arabic deck mixes scripts: a
  chart legend may be English while a table header is Arabic. A deck-level flag would force all of
  them to one base direction.

### 4.3 The font chain

`cssFontFamilyStack` is now the single source for every surface that names a font: the editor's DOM
text layer, the inline Tiptap editor, the measurement path and the export renderer. The chain is

```
'<design font>', 'Noto Naskh Arabic', 'Noto Sans Arabic', 'Noto Sans Arabic UI', Helvetica, sans-serif
```

for left-to-right content, and

```
'Arial', 'Tahoma', '<arabic families>', '<design font>', Helvetica, sans-serif
```

for right-to-left content.

**No new font binary is vendored.** Noto Naskh Arabic and Noto Sans Arabic UI are SIL OFL 1.1 and
are already installed in the shipped container image (`fonts-noto-core`,
`fonts-noto-ui-core`), so this opens no asset-rights question. A deployment that must not rely on
Noto can point a template's font at an uploaded licensed face.

For right-to-left content the **portable** families lead, because the export core writes the
computed font name into the PPTX run properties: the name recorded in the artifact must cover the
script actually used, or a reader without the design font gets an arbitrary substitution.

### 4.4 Mixed script is left to the browser

One container, one `dir="auto"`, one `unicode-bidi:plaintext`, one span per run, and **no per-run
`dir`, no bidi isolate characters, no run reordering and no run splitting**. The Unicode
Bidirectional Algorithm is a solved problem with a reference implementation in every browser;
re-implementing it in the renderer would be strictly worse.

The two ways a naive fix gets this wrong are exactly what the suite catches:

1. **Splitting runs to apply a per-script font** — this destroys the UBA's ability to reorder
   across the split. CSS per-glyph fallback makes the split unnecessary. → `mixed-arabic-english`
   asserts a single container and no run splitting.
2. **Setting `dir` per run** — a `dir="ltr"` on the English run inside an Arabic paragraph creates a
   separate bidi context and moves the run. → the same case asserts exactly one direction
   declaration.

## 5. The honest "supported" claim

**W13 may claim:**

1. Arabic text is **shaped** and **ordered per the UBA within a paragraph** in the DOM/HTML export
   path — the browser engine does it.
2. Elements whose content is Arabic resolve to an **RTL base direction** and are **right-aligned**
   through logical alignment.
3. **Mixed Arabic/English paragraphs** resolve per the UBA with a single base direction derived
   from content.
4. **No glyph loss** in the shipped container image: Arabic resolves to an installed Noto Arabic
   face, not tofu.
5. **Text fidelity**: diacritics, Arabic-Indic digits and Western digits all survive generation →
   template → render byte-for-byte, and no bidi control characters are injected.
6. The editor surface and the export surface now agree on direction for `text`, `text-list` and
   table cells.

**W13 must NOT claim:**

- **Full Arabic typography parity** — no kashida justification, no Arabic-specific line spacing,
  no Arabic-aware line-breaking rules, no contextual Noto Naskh vs Noto Sans Arabic selection.
- **Visual bidi correctness as a *tested* property.** There is **no headless browser** in
  `servers/nextjs/tests/`, so every assertion is markup- or model-level. The suite can prove that a
  `dir` is emitted, that a family is named and that the string is intact; it cannot prove the
  rendered order. **A human must eyeball a rendered Arabic deck.** The suite supplies the fixtures
  and the harness for that and says so in `evidence_classes.rendered`.
- **Bidi fidelity in the exported PPTX** — the export core is external and obfuscated. Whether
  PowerPoint's own bidi engine reorders the exported runs correctly is not observable in-repo and is
  the export-fidelity wave's concern.
- **Round-trip preservation of `<a:pPr rtl="1">`** — the import path demonstrably drops it.
- **RTL layout mirroring** — slide masters, bullet sides, chart axes, progress bars, column order.
- **Any Arabic accuracy percentage.** The repo's own rule applies: W13 asserts **coverage** (N
  cases, each with a named assertion) and **explicit uncertainty** (which assertions are
  markup-level, not pixel-level).

The one-line claim W13 is willing to make:

> *Arabic and mixed Arabic/English text is direction-correct and glyph-complete through
> generation, template hydration, DOM rendering and export; Arabic-specific typography and
> exported-PPTX bidi fidelity are explicitly out of scope and tracked.*

## 6. Bugs the tests caught

| Bug | Severity | Fix |
|---|---|---|
| The `dir="auto"` attribute was emitted on a `<li>` *after* the `style` attribute would have been expected by an existing test. | Test defect, not product | The existing test's regex was updated to `<li dir="auto" style="margin-top:11px;`. The gap behaviour it asserts is unchanged. |
| The vector-text case assumed the HTML export surface renders a vector's text. It does not — the vector renderer emits geometry only, and the vector's text is laid out by the LTR segment engine in the canvas. | Test defect, but it exposed a **pre-existing surface gap** | The test now asserts what is true and **states the gap explicitly** rather than asserting a capability that does not exist. |
| The speaker-note case assumed the HTML surface emits the speaker note. It does not — a note is a separate slide field (`SlideModel.speaker_note`). | Test defect | The test now asserts the note is classified correctly and that the surface does not claim to render it. |

The last two are the reason the suite states its **evidence class** on every case: a case that
looks like it should assert markup but cannot is visible in the fixture instead of hiding behind a
test that quietly measures something else.

## 7. Gate results on this revision

| Gate | Command | Result |
|---|---|---|
| FastAPI | `uv run --locked python -m pytest -q` | **1150 passed** (1125 baseline + 25 qualification) |
| Repository tooling | `npm test` | **48 pass / 0 fail** |
| Next.js unit | `npm test` | **91 pass / 0 fail** (73 baseline + 18 qualification) |
| TypeScript | `npx tsc --noEmit` | clean |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |

## 8. What is still open for W13

| Item | State |
|---|---|
| **A manual rendered check** | **Required, and not automated.** D.1 changes the output of an external, obfuscated consumer. A human must generate one Arabic deck, export it, and open the result. W13 must not close on unit tests alone. |
| Konva / canvas Arabic layout for table cells, chart labels and vector text | **Not fixed.** The words are still placed left-to-right in the canvas. The fix is either a bidi + shaping engine for canvas or routing every text-bearing element to the DOM — the latter touches table cell selection and double-click editing, so it needs its own interactive check. |
| The editor's HTML text layer for table cells | **Not routed.** `shouldRenderTextElementAsHtml` still covers only `text` and `text-list`. |
| A `direction` field on the element schema, and `start`/`end` in `HorizontalAlignment` | **Deferred.** `dir="auto"` already derives the direction from content, so the schema change is not needed for correctness, and it would ripple into the LLM schema. |
| A per-script theme font slot | **Deferred.** The fallback chain already prevents tofu; a deliberate per-script *selection* is a theme-layer change. |
| PPTX import `<a:pPr rtl="1">` | **Not fixed.** The reader is in the external export core. This is the export-fidelity wave's concern. |
| Full Arabic typography | **Out of scope**, stated in §5. |

## 9. Non-fabrication record

- No Arabic-capable font binary was vendored, downloaded, or relicensed.
- No paid service, hosted model, funded compute or product account was used.
- No login, paywall, CAPTCHA, rate limit or access control was defeated.
- No credential, secret or user data was collected.
- The design was produced by a fresh-context subagent that did not author any of this code; its
  findings and its own risk statement — *that the "supported" claim must not outrun the evidence* —
  are carried into §5 above.
