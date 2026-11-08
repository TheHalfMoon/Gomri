# TRANSPLANT_MATRIX — source-to-target integration matrix

**Mission:** Issue #77 — deep NextSlide + Gamma REA and source-first capability migration into Gomrey.
**Date (UTC):** 2026-10-22
**Gomrey target revision (baseline):** `5f299a7a6174ad3a1180f827778db5f4400a4d71`

Every row states the exact donor revision, the exact source paths, the Gomrey
target, the adaptation strategy, the tests that qualify it, and the rollback.
Rows whose disposition is `DEFER` or `REJECT` state the measurable reason.

---

## 0. Donor revision register

| Key | Donor | Revision / digest | License | Source obtained? |
|---|---|---|---|---|
| `D1` | `0xRafie/nextslide` | `90a46f933b3056d27460400c915ef268a9ec3f56` | MIT, © 2026 Danish Rafie Ekaputra | **Yes** — full tree (13 tracked files) |
| `D1-LICENSE` | `0xRafie/nextslide` LICENSE blob | `1f0239b87b6b390ade2cb7f8c4180e6c02f457d4`, sha256 `e8aa250f23393942b2c952d0c45109926b1bffc6e5e9b3d6a3f09abe691bd7a9` | MIT | **Yes** — verbatim copy at `docs/donors/nextslide-skill/LICENSE` |
| `D2` | NextSlide.ai | — | proprietary | **No** — `BLOCKED_SOURCE` |
| `D3` | Gamma product core | — | proprietary | **No** — `BLOCKED_SOURCE` (29 `gamma-app` repos enumerated; core not published) |
| `D4` | Presenton (existing foundation) | `e158a014cc1e29da0a27fe539db08dcbcea5c69d` | Apache-2.0 | Already adopted; **preserved, not re-adopted** |

---

## 1. ADOPTED — Wave 1 (shipped in this PR)

### T-001 — Slide animation contract

| Field | Value |
|---|---|
| `FEATURE_ID` | `F-P08`, `F-P09`, `F-P10` |
| Donor | `D1` — `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56` |
| Original source path | `animation-library.md` (487 lines; blob `a3484b2ae4c13c7a2139e2ed2588f5e58344902c`) |
| Adopted slice | Keyframe bodies (24), easing curves (7), stagger delays (8), duration modifiers (3), reduced-motion policy, per-animation defaults |
| **Target Gomrey module** | `servers/nextjs/lib/slide-animations/catalog.ts`<br>`servers/nextjs/lib/slide-animations/stylesheet.ts`<br>`servers/nextjs/lib/slide-animations/index.ts` |
| Dependencies | **None.** Pure TypeScript data + string generation. No React, no DOM access, no npm package. |
| Required notices | `docs/donors/nextslide-skill/NOTICE.md` (adaptation record) + `docs/donors/nextslide-skill/LICENSE` (verbatim MIT) + in-file header in each adopted source file |
| Adaptation strategy | **ADAPT** — behaviour preserved, public contract re-namespaced. See `docs/donors/nextslide-skill/NOTICE.md` §4 for the 7 enumerated changes and the rationale for each. |
| Tests | `servers/nextjs/tests/slide-animations.test.mjs` — 28 assertions:<br>catalog shape (24 = 20 entrance + 4 emphasis), id/class uniqueness, namespace isolation, Tailwind collision avoidance, stylesheet determinism, no wildcard selectors, no `@import`/`url()`/URL, keyframe resolution, brace balance, both activation modes, reduced-motion coverage of **every** animation, reduced-motion scoping, controller honesty, class-attribute construction and rejection of unknown ids |
| Test command | `cd servers/nextjs && node --test tests/slide-animations.test.mjs` → **28 pass / 0 fail** |
| Performance impact | None measurable. The module is not imported by any rendering surface yet. When adopted, the generated stylesheet is 472 lines / ~11 KB, inlined once per export artifact; keyframes are declarative and composited on the GPU. |
| Security implications | **None added.** The module performs no I/O. The generated stylesheet is asserted to contain no `@import`, no `url(...)` and no absolute URL, so it cannot trigger an egress. Unknown animation ids produce an empty class string rather than a caller-supplied token, so an untrusted value cannot inject a class name. |
| Rollback | Delete the three module files and the test file. No runtime dependency exists, so removal changes no product behaviour. |
| `why_reuse_beats_native` | The donor ships a hand-tuned 24-animation catalog with curated easings, stagger steps and a reduced-motion policy. Re-deriving that motion design would be slower and worse. Gomrey owns the contract and namespace; the donor supplied the tuning. |

### T-002 — Source ledger admission

| Field | Value |
|---|---|
| Donor | `D1` |
| Target Gomrey module | `docs/SOURCE_LEDGER.md` §2 (new `### NextSlide OpenCode slide skill` subsection) |
| Adaptation strategy | ADAPT — the ledger's 23-field admission record for this donor |
| Tests | `node scripts/check-fixtures.mjs` → OK; `node scripts/scan-secrets.mjs` → OK |
| Rollback | Revert the ledger hunk. |

---

## 2. REJECTED — donor material that must not be adopted

Each rejection cites a **measured** reason, not a preference.

### T-101 — Donor PPTX exporter (`scripts/export-pptx.js`, 414 lines, PptxGenJS `^3.12.0`)

| Field | Value |
|---|---|
| Donor path | `D1:scripts/export-pptx.js` (blob `81062d4268656d0502ef59e89f9b02dae75abf73`) |
| Disposition | **REJECT — parallel PPTX engine** |
| Reason | Gomrey's export path is owned by `@presenton/export-core` v1.0.34, installed by `scripts/sync-presentation-export.cjs` and verified by `npm run check:presentation-export` → `[presentation-export] OK (1.0.34)`. Issue #77 §D forbids a duplicated PPTX engine "unless bounded fidelity tests justify them". No fidelity delta has been demonstrated, and the donor's exporter would add a new Node runtime dependency (`pptxgenjs`) to a Python-owned path. |
| What the donor's exporter *does* prove | Its output is genuinely editable for text, shapes and notes: verified independently with `python-pptx` — 4 probe decks, 23–28 text shapes each, 0–2 pictures. This confirms Gomrey's *existing* editable-PPTX posture is not a regression risk, but it does **not** establish superiority over `@presenton/export-core`. |
| What the donor's exporter *does not* prove | **The donor's chart export is invalid.** `export-pptx.js:226` hard-codes the chart type as `'BAR'` while `pptxgenjs@3.12.0` expects `'bar'`; the resulting `ppt/charts/chart1.xml` has a `plotArea` with no `<c:barChart>`, `python-pptx` raises `IndexError`, and PowerPoint would prompt to repair. Charts are a first-class Gomrey capability. |
| Rollback | N/A — nothing adopted. |

### T-102 — Donor PPTX extractor (`scripts/extract-pptx.py`, 463 lines)

| Field | Value |
|---|---|
| Donor path | `D1:scripts/extract-pptx.py` (blob `e3d97b1139dfbff6db905dced2c81154aa889ce8`) |
| Disposition | **REJECT — inferior, defective, and unsafe** |
| Reason 1 — inferior | Gomrey already owns PPTX→JSON import at `services/export_task_service.py` (`convert_pptx_to_json`) plus `templates/pptx_font_utils.py` (1 668 lines of python-pptx font/geometry handling). Baseline tests prove Template V2 metadata, text-list gaps and marker gaps survive import. |
| Reason 2 — defective | **Reproduced crash.** Running the donor extractor unmodified on a pristine donor-generated PPTX aborts with `ValueError: shape is not a placeholder` at `extract-pptx.py` line 281 (`hasattr(shape, "placeholder_format")` → `python-pptx` raises for non-placeholder shapes). The same guard appears at three sites. Log: `research/rea/2026-10-22-nextslide-gamma/evidence/probe/extract_pptx_PRISTINE_crash.log`. |
| Reason 3 — unsafe | **Silent total data loss.** After patching the crash so it could run, the extractor reported `✓ Found 0 elements` **with a success exit code**. It also loses all typography (paragraph-level read vs run-level storage) and all original layouts. A tool that reports success while extracting nothing must not be placed in a product import path. |
| Rollback | N/A — nothing adopted. |

### T-103 — Donor presenter mode (`presenter-mode.md`, 458 lines)

| Field | Value |
|---|---|
| Donor path | `D1:presenter-mode.md` (blob `5905fdf4f764e87792953059d227ca76aa083969`) |
| Disposition | **REJECT — already present** |
| Reason | Gomrey owns `app/(presentation-generator)/presentation/components/PresentationMode.tsx` (610 lines) as part of the qualified editor surface. Adopting a second presenter implementation would create the parallel stack issue #77 §D prohibits. |
| Rollback | N/A — nothing adopted. |

### T-104 — Donor single-file HTML engine (`html-template.md`, 946 lines)

| Field | Value |
|---|---|
| Donor path | `D1:html-template.md` (blob `89cf7f907668a441fad8102d6a4984fa7b013b45`) |
| Disposition | **DEFER** — a real capability (`F-E06`) but not as a parallel engine |
| Reason | Gomrey already owns `servers/nextjs/lib/template-v2-json-to-html.ts` (192 230 bytes) and a Konva canvas renderer. A second HTML renderer is a parallel stack. The **capability** worth taking — a self-contained, offline, single-file deck artifact — is a legitimate `F-E06` gap, but it must be delivered on Gomrey's own renderer. |
| Rollback | N/A — nothing adopted. |

### T-105 — Donor style presets (`STYLE_PRESETS.md`, 817 lines)

| Field | Value |
|---|---|
| Donor path | `D1:STYLE_PRESETS.md` (blob `0e18484ae76bc983654255ce053a8bf1334c044c`) |
| Disposition | **DEFER** — real gap (`F-P06`), wrong integration point |
| Reason | The donor presets are CSS style sheets; Gomrey's theme model is a typed token model derived from templates (`templates/v2/theme.py:145-423`) and mirrored in `servers/nextjs/lib/template-theme.ts`. Landing donor presets as raw CSS would create a second theme representation. The Gamma observation that themes should be **machine-matchable** (`colorKeywords[]`, `toneKeywords[]`) is the more valuable design input, and it belongs in Gomrey's token model. |
| Rollback | N/A — nothing adopted. |

### T-106 — Donor typography system (`typography-system.md`, 255 lines)

| Field | Value |
|---|---|
| Donor path | `D1:typography-system.md` (blob `505ae09f37e576b2ee9667d476c93a0a3c07b595`) |
| Disposition | **DEFER** — compare against Gomrey's own typography first |
| Reason | Issue #77 §D: "Compare against current Presenton components and adopt only the proven better path." Gomrey's text layout lives in `components/slide-editor/text/*` and `model/design-variables.ts` with raw-pixel sizing; the donor has a scale-based system. A measured comparison (overflow rate, reading order, Arabic/RTL) is required before any adoption. |
| Rollback | N/A — nothing adopted. |

### T-107 — Donor interactive elements / viewport CSS (`interactive-elements.md` 730 lines, `viewport-base.css` 663 lines)

| Field | Value |
|---|---|
| Donor path | `D1:interactive-elements.md` (blob `688ec8211dbf5838275de71df1e040919ac570b3`), `D1:viewport-base.css` (blob `dce13d8d52a637a074bb33ba232e26c2690253fe`) |
| Disposition | **DEFER** |
| Reason | Gomrey's editor already implements selection, shapes, images, tables, math, charts, infographics, clipboard, keyboard shortcuts and layout. Each donor widget needs an individual comparison; none may be adopted as a batch. |
| Extra disqualifier | The donor's own pipeline **never inlines** the widget CSS (`SKILL.md:126-142` lists 5 things in the `<style>` block; the widget CSS is not among them), so per the donor's own instructions charts, KPI cards, timelines, donuts, tables and code blocks render **completely unstyled**. Reproduced as the paired screenshots `evidence/probe/shot_chart_UNSTYLED_per_SKILL.md.png` and `shot_chart_STYLED_with_interactive_CSS.png`. |
| Rollback | N/A — nothing adopted. |

### T-108 — Donor contrast / design-quality rules (`SKILL.md:276-341`)

| Field | Value |
|---|---|
| Donor path | `D1:SKILL.md` lines 276–341 (the donor's design-rule checklist, including the 4.5:1 contrast requirement) |
| Disposition | **ADAPT — queued as wave `W4a`** |
| Original source path | `SKILL.md:276-341` plus the measured failure data in `evidence/NEXTSLIDE_SKILL_SOURCE_INVENTORY.md` §11 |
| Target Gomrey module | `servers/fastapi/services/slide_quality_rules.py` (new) — a deterministic contrast/legibility linter that runs on every resolved theme before export |
| Dependencies | **None.** Pure arithmetic on already-resolved theme tokens. |
| Required notices | `docs/donors/nextslide-skill/NOTICE.md` must record this slice when it lands. |
| Adaptation strategy | **ADAPT.** The *rule* (4.5:1 for text) is an accessibility standard, not donor IP, and is implemented independently against Gomrey's own 16 semantic colours. The donor's *palette set* is not adopted — it fails its own rule in 34/90 pairs, and its presets carry Google Fonts network dependencies. |
| Why this is high value | `F-P04` is a measured Gomrey gap: `utils/smart_slide_layout.py` checks overflow, clipping and overlap but **not contrast**. The donor supplies (a) the machine-checkable rule and (b) proof that a plausible-looking palette set violates it in 38 % of pairs — which is exactly the evidence needed to justify a linter that catches it before a user sees it. |
| Tests | Deterministic: every resolved theme's foreground/background pairs are checked against 4.5:1 (and 3:1 for large text); a failing pair is reported with both hex values and the computed ratio; the linter is applied to the 18 donor presets as a *negative* fixture and must reject the 34 known-bad pairs. |
| Rollback | Delete the new module. It is additive and gates nothing until wired. |
| Status | **NOT YET IMPLEMENTED.** Listed here so the plan is auditable before execution. |

---

## 3. BLOCKED — Gamma wave

### T-200 — Gamma card/editor UX

| Field | Value |
|---|---|
| Donor | `D3` — Gamma product core |
| Disposition | **BLOCKED_SOURCE** |
| Missing input | An exact authorized Gamma source snapshot (archive or repository) plus its permission scope, third-party/asset boundary and provenance record. `docs/SOURCE_LEDGER.md` §2 Gamma gate: *"A public `gamma.app` URL is not a source archive."* |
| Available substitute | `GAMMA.md` — a 13-area capability inventory built from official documentation, the full MCP tool reference and live unauthenticated API responses, with every claim tagged `OBSERVED_UI` / `OFFICIAL_DOCUMENTATION` / `API_RESPONSE` / `INFERENCE` / `UNKNOWN` / `BLOCKED`. |
| Delivery path | `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` — original Gomrey code, shaped by observed Gamma behaviour. Never reported as parity. |
| Rollback | N/A — nothing adopted. |

### T-201 — Gamma themes / brand kits

| Field | Value |
|---|---|
| Donor | `D3` |
| Disposition | **BLOCKED_SOURCE` (core) / `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` (planned)** |
| Missing input | Same as T-200. |
| Available substitute | Gamma's `get_themes` contract returns `colorKeywords[]` and `toneKeywords[]` — machine-matchable theme metadata. Design intent to carry into Gomrey's token model: **a theme must be selectable by intent, not only browsable by name.** |
| Rollback | N/A — nothing adopted. |

### T-202 — Gamma MCP tool taxonomy

| Field | Value |
|---|---|
| Donor | `D3` |
| Disposition | **BLOCKED_SOURCE` (core) / `REFERENCE` (taxonomy)** |
| Missing input | Same as T-200. |
| Available substitute | The documented 21-tool split (`generate`, `generate_multi_page_gamma`, `generate_from_template`, `get_generation_status`, `generate_image`, `get_image_generation_status`, `export_gamma`, `get_export_status`, `edit_gamma`, `get_edit_status`, `get_gammas`, `search_gammas`, `search_templates`, `read_gamma`, `get_gamma_comments`, `get_gamma_analytics`, `get_gamma_card_analytics`, `get_gamma_viewer_analytics`, `get_gamma_viewer_detail_analytics`, `get_themes`, `get_folders`) plus per-tool read-only / destructive / idempotent flags. |
| Note | Gomrey already has a stronger async model (P04 durable job kernel) than Gamma's polling model. The taxonomy is worth adopting for *shape*, not for the runtime. |
| Rollback | N/A — nothing adopted. |

### T-203 — Gamma multi-page / website / social output

| Field | Value |
|---|---|
| Donor | `D3` |
| Disposition | **BLOCKED_SOURCE` (core) / `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` (planned)** |
| Missing input | Same as T-200. |
| Available substitute | Documented Gamma behaviour: one artifact, several pages, one URL, per-page content and settings; explicit formats presentation / document / webpage / social post; export to PDF, PPTX, PNG (PNG = `.zip` with one PNG per card). |
| Rollback | N/A — nothing adopted. |

### T-204 — Gamma agentic editing (`edit_gamma`)

| Field | Value |
|---|---|
| Donor | `D3` |
| Disposition | **BLOCKED_SOURCE` (core) / `REFERENCE` (safety semantics)** |
| Missing input | Same as T-200. |
| Available substitute | Documented semantics worth carrying into Gomrey's own agent surface: edits apply to *existing* pages only, cannot add pages, run one at a time, and are flagged **destructive**. |
| Rollback | N/A — nothing adopted. |

---

## 4. NEXT — dependency-ready grains that follow Wave 1

These are **planned**, not delivered. Each is `PARTIAL` in `FEATURE_MATRIX.md` and must earn its own PR, tests and review.

| Grain | Target | FEATURE_ID | Donor input | Prerequisite |
|---|---|---|---|---|
| **W2 — Wire the animation contract into the HTML renderer** | `servers/nextjs/lib/template-v2-json-to-html.ts` + a slide-model `animation` field | `F-P08` | T-001 | Model field must exist first |
| **W2 — Slide-level animation model** | `servers/fastapi/templates/v2/models/` | `F-P08`, `F-C01` | T-001 | Must not fork the IR; extend `contracts/v1/` |
| **W3 — Evidence-bound narrative → artifact producer** | new `servers/fastapi/gomrey/narrative.py` + hook in `utils/llm_calls/generate_presentation_outlines.py` | `F-R07` | P08/P09 fabric already in-repo | **Highest value.** Uses only admitted in-repo modules |
| **W4 — Named theme/style preset layer with machine-matchable keywords** | `servers/fastapi/templates/v2/theme.py`, `servers/nextjs/lib/template-theme.ts` | `F-P06` | Gamma `get_themes` observation | Must extend, not replace, the token model |
| **W5 — Brand kit** | new `servers/fastapi/gomrey/brand.py` + `contracts/v1/design-ir.schema.json` | `F-P07` | Gamma observation | Requires an asset-rights boundary decision first |
| **W6 — Multi-node artifact IR (slides/cards/pages)** | `contracts/v1/narrative-ir.schema.json`, `design-ir.schema.json` | `F-C01`, `F-C02` | Gamma multi-page observation | Schema change — needs contract migration discipline |
| **W7 — Self-contained offline HTML deck artifact** | `servers/nextjs/lib/template-v2-json-to-html.ts` | `F-E06` | T-104 deferred | Must reuse Gomrey's renderer only |
| **W8 — Image export (PNG/JPEG/WebP)** | `servers/fastapi/utils/export_utils.py:46`, `models/generate_presentation_request.py` | `F-E05` | Gamma PNG behaviour | Export enum change |
| **W9 — Document studio authoring + DOCX export** | new `servers/fastapi/services/document_generation_service.py` | `F-S01` | Gamma document behaviour | Large grain — split further |
| **W10 — Website studio** | new Next.js route group + backend | `F-S02` | Gamma webpage behaviour | Depends on W6 |
| **W11 — Deck-level AI editing** | `servers/fastapi/services/chat/tools.py` | `F-P16` | Gamma `edit_gamma` semantics | Must preserve P09 verification semantics |
| **W12 — Export fidelity + round-trip regression suite** | new test roots | `F-E09`, `F-I02` | Gamma export-fidelity gaps | Can start independently |
| **W13 — Arabic / RTL / mixed-script qualification** | new test roots + fixes | `F-C09` | none — original work | Issue §F acceptance gate; currently unmeasured everywhere |
| **W14 — Clean up orphan root `layouts.json`** (252 KB, zero code references) | repo root | — | — | Housekeeping; risk of being mistaken for a source of truth |

---

## 5. Adoption-mode accounting

| Mode | Count | Which |
|---|---|---|
| `COPY_BOUNDED` | 0 | — |
| `ADAPT` | 2 | T-001, T-002 |
| `DEPEND` | 0 | — |
| `WORKER` | 0 | — |
| `MODEL_PACK` | 0 | — |
| `REFERENCE` | 2 | T-202, T-204 (Gamma taxonomy / safety semantics) |
| `BENCHMARK_ONLY` | 1 | Donor PPTX exporter — used as a comparand, not adopted |
| `DEFER` | 3 | T-104, T-105, T-106, T-107 (grouped) |
| `REJECT` (measured) | 3 | T-101, T-102, T-103 |
| `BLOCKED_SOURCE` | 5 | T-200 … T-204 (Gamma core) |

> `COPY_BOUNDED` is **zero** by deliberate design: every donor candidate that reached a real
> implementation was either already superseded by a stronger in-repo path or required a
> re-namespacing that makes it an `ADAPT`. Recording `COPY_BOUNDED` without a verbatim slice would
> have misrepresented the work.
