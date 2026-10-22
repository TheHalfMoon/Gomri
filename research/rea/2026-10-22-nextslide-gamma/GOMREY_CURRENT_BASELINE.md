# GOMREY_CURRENT_BASELINE — what already exists, measured

**Baseline revision:** `5f299a7a6174ad3a1180f827778db5f4400a4d71` (main)
**Full survey:** `evidence/GOMREY_BASELINE_SURVEY.md` (941 lines)
**Gate evidence:** `evidence/BASELINE_GATE_RUN.md`

This document exists to prevent the classic failure of a capability-migration mission: rebuilding
something that already works because a donor has a different implementation of it.

---

## 1. Pre-change gate baseline (all green)

| Gate | Result |
|---|---|
| `npm test` (repo root) | **48 pass / 0 fail** |
| FastAPI `pytest` | **1125 passed** |
| Next.js `node --test` | **73 pass / 0 fail** |
| Next.js `eslint` | **0 errors**, 68 warnings |
| Next.js production build | success |
| Electron typecheck / build / main-globals / path-migration | all pass |
| `scan-secrets` / `check-fixtures` / `check-platform-support` / `validate-release-config` / `generate-release-manifest --check-only` | all OK |
| `presentation-export` runtime | `@presenton/export-core` **1.0.34** installed and verified |

## 2. Capability map

### 2.1 Presentation pipeline — COMPLETE

| Concern | Location |
|---|---|
| Orchestration | `servers/fastapi/api/v1/ppt/endpoints/presentation.py` (3 334 lines) — `create` 1634, `prepare` 1783, smart stream 1874, standard stream 2224, `update` 2470, `export` 1595 |
| Routers | `api/v1/ppt/router.py`, `api/v2/ppt/router.py` |
| LLM provider seam | `utils/llm_provider.py:47-193` — `get_llm_provider`, `get_model`, 15 `is_*_selected` predicates; clients in `utils/llm_config.py` (524 lines) via `llmai==0.3.15` |
| Planning | `generate_presentation_outlines.py` (404) → `generate_presentation_structure.py` (211, **layout index selection**) → `generate_slide_content.py` (275); smart path `generate_smart_presentation.py` (936) |
| Generation modes | `PRESENTATION_GENERATION_MODE` = `both` \| `standard` \| `smart`; **not** an authorization control |

**Do not add a second provider registry, a second planner, or a second generation mode.**

### 2.2 Templates, themes, layouts

| Concern | State |
|---|---|
| Templates | **16 bundled**, 400+ layouts, `templates/{civic,dynamic,editorial,executive,general,horizon,landmark,modern,momentum,mosaic,nova,pulse,signal,standard,swift,verdant}/template.json`. Schema: `id,name,description,thumbnail,merged_components,layouts,fonts,theme` |
| Theme | **Derived from the template only** — `templates/v2/theme.py:145-423`; 16 semantic colours mirrored in `servers/nextjs/lib/template-theme.ts` |
| Named style presets | **MISSING** — no preset layer exists above the template |
| Brand kit | **MISSING** — only `DesignIR.brand_skill_id`, a string |
| Root `layouts.json` (252 KB, 14 layouts) | **ORPHAN** — zero code references; not a source of truth. Cleanup candidate (`W14`) |

### 2.3 Editor — COMPLETE and large

`servers/nextjs/components/slide-editor/**` — **73 files**, authoritative map in
`components/slide-editor/README.md` (1 385 lines).

Sub-systems: `charts`, `clipboard`, `events`, `images`, `importing`, `infographics`, `insert`,
`layout`, `math`, `model`, `selection`, `shapes`, `shortcuts`, `state`, `surface`, `tables`, `text`,
`toolbar`, `types.ts`, `utils`.

- **Rendering**: Konva canvas — `surface/TemplateV2KonvaSlide.tsx` (3 400 lines)
- **Undo/redo**: two layers — surface-local (`TemplateV2KonvaSlide.tsx:423-424,1250,1282,1290`)
  and Redux (`store/slices/undoRedoSlice.ts` 142, `presentation/hooks/PresentationUndoRedo.ts` 99)
- **Autosave**: `presentation/hooks/useAutoSave.tsx` (212 lines, debounce + diff)
- **Presenter mode**: `app/(presentation-generator)/presentation/components/PresentationMode.tsx` (610 lines)

### 2.4 Export — PPTX/PDF only, owned by an external package

```
utils/export_utils.py:43-75           →  Literal["pptx","pdf"]
services/export_task_service.py:425    →  Next /pdf-maker
lib/run-bundled-presentation-export.ts →  presentation-export/runner.mjs
                                      →  @presenton/export-core  v1.0.34
```

`presentation-export/` is gitignored and installed by `scripts/sync-presentation-export.cjs`.

**PPTX import already beats every donor**:
`services/export_task_service.py:690 convert_pptx_to_json` + `templates/pptx_font_utils.py`
(1 668 lines of python-pptx font/geometry handling). Baseline tests prove Template V2 metadata,
text-list gaps and marker gaps survive import.

### 2.5 Evidence / verification (P08–P09) — COMPLETE BUT **UNWIRED**

| Module | Capability |
|---|---|
| `gomrey/retrieval_pipeline.py` | ACL → exact → lexical → fusion (no index) |
| `gomrey/citations.py` | 5 locator kinds, `BrokenCitation` |
| `gomrey/evidence_bundle.py` | evidence bundle + sufficiency |
| `gomrey/claims.py` | claim contracts + evidence binding |
| `gomrey/verification.py` | 6 verdicts; deterministic number/date gates; **the provider cannot overrule a deterministic check** |
| `gomrey/decisions.py` | decision graph, verified-only synthesis, calibration registry, `ABSTAIN` |

> **There is no call site for any of this in the presentation pipeline.** This is the single largest
> structural gap in the baseline and the highest-value target of the mission.

### 2.6 Contracts

`contracts/v1/` — 23 schemas + `manifest.json`.

- `artifact.schema.json` — `artifact_type ∈ {presentation,document,site,infographic,social,image,other}`.
  **Only `presentation` has a runtime producer.**
- `narrative-ir.schema.json` — `sections[]` is a flat `{heading,text,claim_ids}` list. **No
  multi-slide/card/page nodes.**
- `design-ir.schema.json` — `layout` is a **single string**. No per-section layout plan.

### 2.7 Absent studios

| Studio | State |
|---|---|
| Document **authoring** | **ABSENT** — only *ingestion* exists (`services/documents_loader.py`, `office_document_service.py`, `liteparse_service.py`). No authoring, no DOCX export. |
| Website / responsive pages | **ABSENT** — no routes, no IR, no renderer, no publish path |
| Social / visual cards | **PARTIAL** — 27 infographic types exist, but only inside slides (`utils/infographic_catalog.py:45-478`) |
| Multi-page artifact under one URL | **ABSENT** |

### 2.8 Animation — ABSENT (the gap this mission closed)

| Check | Result |
|---|---|
| `slideTransition` / `entranceAnimation` / `transitionName` / `animationPreset` in `app components lib utils` | **0 files** |
| `prefers-reduced-motion` in `app components lib utils` | **2 files** (partial) |
| `@keyframes` in `app/globals.css` | **12** — all product chrome (typing, blink, slideUp, ripple, backgroundAnimation, generatingSlides, configuration-loader, splash); **none** are slide animations |

## 3. What this baseline forbids

1. **A second PPTX engine.** `@presenton/export-core` is canonical.
2. **A second slide-rendering stack.** The Konva canvas + the DOM/HTML renderer are canonical.
3. **A second LLM provider registry.** `utils/llm_provider.py` is canonical.
4. **A second artifact IR.** `contracts/v1/` is canonical.
5. **A second theme representation.** `templates/v2/theme.py` + `lib/template-theme.ts` are canonical;
   a donor preset layer must extend them, not shadow them.
6. **A second evidence or verification authority.** `servers/fastapi/gomrey/` is canonical.
7. **A second generation-mode switch.** `PRESENTATION_GENERATION_MODE` is canonical.

Every `REJECT` and `DEFER` in `TRANSPLANT_MATRIX.md` traces back to one of these seven.
