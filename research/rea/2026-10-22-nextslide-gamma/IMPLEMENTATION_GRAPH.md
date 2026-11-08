# IMPLEMENTATION_GRAPH — dependency-ordered execution plan

**Mission:** Issue #77.
**Date (UTC):** 2026-10-22
**Legend:** `▶` in progress · `●` done · `○` not started · `⊘` blocked

Each node is one independently shippable grain: its own branch, its own red→green tests, its own
review record, its own PR. No node may start until its `needs` are satisfied.

---

## 0. Graph

```
                                   ┌──────────────────────────────┐
                                   │ R0/R1 REA + evidence (DONE)   │
                                   └───────────────┬──────────────┘
                                                   │
                          ┌────────────────────────┴────────────────────────┐
                          │                                                 │
              ┌───────────▼────────────┐                    ┌───────────────▼──────────────┐
              │ W1 animation contract  │                    │ R2 matrices + ledger (DONE)  │
              │ (● SHIPPED 0c19896)    │                    └───────────────┬──────────────┘
              └───────────┬────────────┘                                    │
                          │                                    ┌───────────────┴──────────────┐
              ┌───────────▼────────────┐                    │                              │
              │ W2a animation model   │                    │                       ┌──────▼──────┐
              │ + HTML renderer wiring│                    │                       │ W3 evidence │
              │ (● PR #81, needs W1)  │                    │                       │ → artifact  │
              └───────────┬────────────┘                    │                       │ (● PR #80)  │
                          │                                 │                       └──────┬──────┘
              ┌───────────▼────────────┐                    │                              │
              │ W2b Konva animation    │                    │                       ┌──────▼──────┐
              │ twin (○ needs W2a)     │                    │                       │ W6 multi-   │
              └────────────────────────┘                    │                       │ node IR     │
                                                           │                       │ (○)          │
   ┌───────────────────────────────────────┐               │                       └──────┬──────┘
   │ W12 export fidelity harness (● #83)  │               │                              │
   │ W13 Arabic/RTL qualification (● #82) │               │              ┌───────────────┼───────────────┐
   │ W8  image export PNG/JPEG (● #84)    │               │              │               │               │
   │ W14 orphan layouts.json cleanup (○)  │               │      ┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼───────┐
   │  ↑ all four have NO upstream dep.    │               │      │ W4 presets   │ │ W5 brand   │ │ W11 deck AI │
   └───────────────────────────────────────┘               │      │ (○)         │ │ kit (○)    │ │ editing (○) │
                                                           │      └───────┬──────┘ └──────┬──────┘ └──────┬───────┘
                                                           │              │               │               │
                                                           │      ┌───────▼──────┐ ┌──────▼──────┐        │
                                                           │      │ W7 offline   │ │ W10 website │        │
                                                           │      │ HTML artifact │ │ studio (○)  │        │
                                                           │      │ (○)          │ └─────────────┘        │
                                                           │      └──────────────┘                          │
                                                           └─────────────────────────────────────────────┘
```

---

## 1. Node definitions

### ● W1 — NextSlide animation contract (**SHIPPED**)

| | |
|---|---|
| Commit | `0c19896e813b119027b930d143240ce43fbedd65` |
| Files | `servers/nextjs/lib/slide-animations/{catalog,stylesheet,index}.ts`, `servers/nextjs/tests/slide-animations.test.mjs` |
| Tests | 28 pass / 0 fail |
| Gates | all 16 executed gates green |
| Closes | `F-P08`, `F-P09`, `F-P10` |

### ○ W2a — animation field on the slide model + HTML renderer wiring

| | |
|---|---|
| **Needs** | W1 (done) |
| Files | `servers/fastapi/templates/v2/models/elements.py` (add `animation` to the element/slide schema), `contracts/v1/` (schema extension), `servers/nextjs/lib/template-v2-json-to-html.ts` (emit class attribute + inline stylesheet) |
| Behaviour | An element may declare `animation: "fade-up"`, `delay_ms`, `duration`. The HTML renderer emits `gs-anim-fade-up gs-delay-200` and inlines the generated stylesheet once per artifact. |
| Tests | FastAPI: model accepts known ids, rejects unknown ids (400, not a silent pass-through). Next.js: the renderer emits the expected class attribute and exactly one stylesheet block; the exported HTML contains a `prefers-reduced-motion` block covering every animation it uses. |
| Security | Unknown ids are rejected server-side, never interpolated into markup. The stylesheet is generated, not user-supplied. |
| Rollback | Revert the model field and the renderer hunk; W1 stays as an unwired library. |
| Advances | `F-P08`, `F-P09`, `F-C01` |

### ○ W2b — Konva animation twin

| | |
|---|---|
| **Needs** | W2a |
| Files | `servers/nextjs/components/slide-editor/surface/` — a Konva `Tween` driver reading the **same catalog** |
| Behaviour | The canvas editor and the DOM/HTML export must not drift. One catalog, two native renderers. |
| Tests | Catalog-to-driver parity test: for every animation id, the Konva driver must produce the same start/end transform/opacity values as the CSS keyframes. |
| Advances | `F-P08` (editor surface) |

### ● W3 — evidence-bound narrative → artifact producer — **DONE** (PR #80, `a0d28fe`)

| | |
|---|---|
| **Needs** | nothing — uses only in-repo P08/P09 modules |
| Files | new `servers/fastapi/gomrey/narrative.py`; hook in `utils/llm_calls/generate_presentation_outlines.py`; `contracts/v1/narrative-ir.schema.json` (per-slide citation locators) |
| Behaviour | An `EvidenceBundle` becomes a `NarrativeIR` whose claims carry resolvable locators; unresolved claims and conflicts surface as explicit markers; the artifact never contains a citation that `citations.py` cannot resolve. |
| Tests | Deterministic: (1) a supported claim yields a resolvable locator; (2) an unresolved claim yields an abstention marker, never a fabricated citation; (3) a contradictory pair is flagged; (4) `BrokenCitation` fails the export path. P09 semantics unchanged: a provider still cannot overrule a deterministic gate. |
| Security | No new network authority. No new provider registry. No silent omission: every source unit must be accounted for or explicitly marked omitted. |
| Advances | `F-R07`, `F-R08`, `F-R09` — the delta that most distinguishes Gomrey |

### ○ W4a — deterministic contrast / legibility linter **(new, high value)**

| | |
|---|---|
| **Needs** | nothing — **independent, can start now** |
| Donor input | `T-108` — `SKILL.md:276-341` (the 4.5:1 rule) + the measured 34/90 failing-pair data |
| Files | new `servers/fastapi/services/slide_quality_rules.py`; integrate into `utils/smart_slide_layout.py` |
| Behaviour | Every resolved theme is checked before export. Foreground/background pairs are compared against WCAG AA 4.5:1 (3:1 for large text). A failing pair is reported with both hex values, the computed ratio and the offending token names. Non-contrast legibility checks (density, reading order) may follow in the same module. |
| Why now | `F-P04` is a measured Gomrey gap — `smart_slide_layout.py` checks overflow, clipping and overlap but **not contrast**. The donor's own 18 presets fail their own rule in 34/90 pairs, which is the evidence that a linter earns its place. |
| Tests | Deterministic contrast arithmetic against known ratios (black-on-white = 21:1, `#767676` on white = 4.54:1, `#777777` on white = 4.48:1 → fail). The 18 donor presets act as a **negative** fixture: the linter must reject the 34 known-bad pairs and accept the rest. |
| Security | Pure arithmetic on already-resolved tokens. No I/O, no network. |
| Advances | `F-P04` — and it strengthens `F-P06` (presets) by making an unusable palette *fail loudly* instead of shipping |

### ○ W4b — named style presets + machine-matchable intent keywords

| | |
|---|---|
| **Needs** | Delta 4 (single token source) recommended; W6 optional |
| Files | `servers/fastapi/templates/v2/theme.py`, `servers/nextjs/lib/template-theme.ts`, `contracts/v1/design-ir.schema.json` |
| Behaviour | A preset is a typed token set resolved to the existing 16 semantic colours and the existing font/spacing scale. Each preset carries `color_keywords[]` and `tone_keywords[]` so it is **selectable by intent**, not only browsable by name. |
| Constraint | Presets must **extend** the canonical token model. A second theme representation is forbidden. Donor CSS is a reference only — it ships Google Fonts `<link>` dependencies. |
| Tests | Preset resolution is deterministic; every preset resolves to a complete token set; keywords are non-empty and lowercase-normalised; no preset introduces a remote font or asset URL. |
| Advances | `F-P06` |

### ○ W5 — brand kit

| | |
|---|---|
| **Needs** | W6, **and** an explicit asset-rights decision |
| Files | new `servers/fastapi/gomrey/brand.py`, `contracts/v1/design-ir.schema.json` |
| Constraint | `SOURCE_LEDGER.md` §7 — code permission ≠ asset permission. Logos and brand fonts are a separate rights identity. A brand kit must record provenance for every uploaded asset and must not silently redistribute assets it does not own. |
| Advances | `F-P07` |

### ○ W6 — multi-node artifact IR (slides / cards / pages)

| | |
|---|---|
| **Needs** | contract migration discipline; `scripts/validate-contracts.mjs` |
| Files | `contracts/v1/narrative-ir.schema.json`, `contracts/v1/design-ir.schema.json`, `contracts/v1/manifest.json` |
| Behaviour | `nodes[]` with a typed discriminated union (`slide` \| `page` \| `card`); per-node layout plan; per-node citation locators; additive schema version bump; the existing single-document form keeps validating until producers migrate. |
| Tests | Schema contract tests: old form still valid; new form valid; mixed invalid forms rejected with precise messages; `scripts/contracts.test.mjs` green. |
| Advances | `F-C01`, `F-C02`, `F-S04` |

### ○ W7 — self-contained offline HTML deck artifact

| | |
|---|---|
| **Needs** | W2a |
| Files | `servers/nextjs/lib/template-v2-json-to-html.ts` |
| Constraint | Must reuse Gomrey's renderer only. A second HTML engine is forbidden. |
| Behaviour | One HTML file, no external network reference, presentation and presenter behaviour inlined, printable to landscape. |
| Tests | The exported file contains no `http(s)://` resource reference, no `<script src>`, no `<link rel="stylesheet">`; it renders identically with the network disabled. |
| Advances | `F-E06` |

### ● W8 — image export (PNG / JPEG / WebP) (**SHIPPED**)

| | |
|---|---|
| Commit | `6b3632a093efeb320878f6cfc16c7345cf16a1c1` (branch `feature/rea/w8-image-export`, base `main@5f299a7`) |
| PR | [#84](https://github.com/TheHalfMoon/Gomrey/pull/84) |
| Files | `servers/fastapi/enums/export_format.py`, `servers/fastapi/models/image_export_options.py`, `servers/fastapi/services/image_export_service.py`, `servers/fastapi/utils/export_utils.py`, `servers/fastapi/services/export_task_service.py`, `servers/fastapi/models/generate_presentation_request.py`, `servers/fastapi/models/presentation_from_template.py`, `servers/fastapi/api/v1/ppt/endpoints/presentation.py`, `servers/fastapi/api/v2/ppt/endpoints/presentation.py`, `servers/nextjs/lib/run-bundled-presentation-export.ts`, `servers/nextjs/app/api/export-presentation/route.ts` |
| Donor | `@presenton/export-core` v1.0.34 open-source edition — its `export`/`html-to-any` task already renders one PNG per slide into a ZIP. **Copied and reused, not reimplemented.** |
| Behaviour | The export enum now covers `pptx, pdf, png, jpeg, webp`. Image exports reuse the existing slide renderer and are repackaged by a Gomrey-owned service that owns entry names, slide order, format conversion, budget and rejection rules. |
| Tests | 40 unit tests (format contract, archive layout, conversion, budget, hostile input) + 7 end-to-end tests that render a real 4-slide deck (including Arabic/RTL and mixed script) through the real Chromium export runtime and assert the produced bytes. |
| Advances | `F-E05` |

### ○ W9 — Document studio authoring + DOCX export

| | |
|---|---|
| **Needs** | W6 |
| Files | new `servers/fastapi/services/document_generation_service.py` |
| Constraint | Split further before starting — document authoring is not one grain. |
| Advances | `F-S01` |

### ○ W10 — Website studio

| | |
|---|---|
| **Needs** | W6, W4 |
| Files | new Next.js route group + a responsive renderer |
| Advances | `F-S02` |

### ○ W11 — deck-level AI editing

| | |
|---|---|
| **Needs** | W6; P09 verification semantics preserved |
| Files | `servers/fastapi/services/chat/tools.py` |
| Behaviour | Reorder / retitle / restyle / regenerate a slide, with attribution, revision safety and undo. Gamma's semantics to mirror: edits apply to existing nodes, cannot add nodes, one edit at a time, and the operation is flagged **destructive**. |
| Advances | `F-P16` |

### ● W12 — export fidelity + round-trip regression suite — **DONE** (PR #83, `690513e`)

| | |
|---|---|
| **Needs** | nothing — **independent, can start now** |
| Files | new `servers/fastapi/tests/fidelity/` |
| Behaviour | Export → reopen → assert. Cases: tables, vectors, charts, media, overflow, RTL, mixed script. Versioned failure-mode taxonomy, JSON + CSV report. |
| Tests | The suite itself is the test. |
| Advances | `F-E09`, `F-I02`; satisfies an issue §F acceptance gate |

### ● W13 — Arabic / RTL / mixed-script qualification — **DONE** (PR #82, `b16eb0b`)

| | |
|---|---|
| **Needs** | nothing — **independent, can start now** |
| Files | new `servers/fastapi/tests/qualification/` + targeted fixes |
| Behaviour | Measure first: pure Arabic, pure English, mixed in one paragraph, Arabic with Latin numerals, Arabic in a table, in a chart label, in a vector shape, and in an exported PPTX. Assert logical direction, font fallback, no glyph loss, no overflow, correct export. |
| Advances | `F-C09`; satisfies an issue §F acceptance gate |

### ○ W14 — remove the orphan root `layouts.json`

| | |
|---|---|
| **Needs** | confirmation that nothing references it (baseline survey: **zero** code references) |
| Files | repo root `layouts.json` (252 KB, 14 layouts) |
| Rationale | A 252 KB orphan file that reads like a source of truth but is not one is an active hazard for future contributors. |

---

## 2. Critical path and parallelism

**Critical path:** `W1 → W2a → W2b` and `W6 → W5 / W9 / W10 / W11`.
**Immediately available (no dependencies):** `W14`. **Delivered:** `W3` (#80), `W2a` (#81),
`W13` (#82), `W12` (#83), `W8` (#84), `W4a` (#79), wave 1 (#78).

**Recommended execution order** — start with the independent, high-value items, then work the spine:

| Order | Node | Why now |
|---|---|---|
| 1 | **W3** | Highest value; no donor needed; closes the biggest structural gap |
| 2 | **W2a** | Small; completes the Wave 1 deliverable so it is not an unwired library |
| 3 | **W13** | Independent; issue §F acceptance gate; Arabic-first is a product requirement |
| 4 | **W12** | Independent; issue §F acceptance gate; enables every later fidelity claim |
| 5 | **W4a** | Independent; closes a measured gap (`F-P04`) and makes any future preset layer safe |
| 6 | **W6** | Unblocks the whole studio surface |
| 7 | **W4b** | Depends on a single token source; unlocks presets and consistent rendering |
| 8 | **W8**, **W14** | Small, independent housekeeping — **W8 DONE (PR #84)**; **W14** remains |
| 9 | **W2b**, **W5**, **W7**, **W9**, **W10**, **W11** | Remainder |

---

## 3. Per-grain acceptance contract

Every grain, without exception:

1. Own branch from exact live `main`.
2. Red → green tests **written first**; the failing run is captured.
3. Donor material, if any, carries a `docs/donors/<name>/NOTICE.md` record and a verbatim LICENSE.
4. `docs/SOURCE_LEDGER.md` updated if a new donor slice lands.
5. All 16 gates executed on the **exact candidate commit**.
6. Review stack executed: TypeSafe Jev (real output, with the 9 required evidence fields) and Alibaba OCR
   deterministic selection. `OCR_NOT_EXECUTED` / `JEV_NOT_EXECUTED` recorded honestly if a tool is
   unavailable — never substituted.
7. PR opened, gates passed, merged, canonical merged state re-verified.
8. `STATUS.md` updated with `DONE`, the PR number, the merge SHA, the gate results and the next
   dependency-ready task.

## 4. Explicitly out of scope

| Out of scope | Reason |
|---|---|
| Gamma editor / card model / theme system / export renderer source | `SOURCE_NOT_AVAILABLE` — no snapshot supplied. Would require the founder to supply one. |
| Gamma authenticated-editor reverse engineering | Requires an authorized account. Not created, purchased or circumvented. |
| A second PPTX engine | Forbidden by issue §D; `@presenton/export-core` is canonical |
| A second slide-rendering stack | Forbidden; Konva + DOM/HTML are canonical |
| A second artifact IR or second theme model | Forbidden; `contracts/v1/` and `templates/v2/theme.py` are canonical |
| Replacing P09 verification semantics | Forbidden; the mission integrates into them, not over them |
| A hosted Gamma-compatible MCP endpoint | `BLOCKED_COST` — Gamma generation/edits charge credits; the default path must work without a paid API |
