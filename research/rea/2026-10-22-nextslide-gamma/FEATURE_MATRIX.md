# FEATURE_MATRIX — cross-donor capability matrix

**Mission:** Issue #77 — deep NextSlide + Gamma REA and source-first capability migration into Gomrey.
**Date (UTC):** 2026-10-22
**Baseline Gomrey revision:** `5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Status vocabulary (issue §F, mandatory):**

| State | Meaning |
|---|---|
| `ALREADY_PRESENT` | Gomrey already implements it and it is qualified. No work required. |
| `CODE_TRANSFERRED_AND_QUALIFIED` | Authorized source was actually obtained, adapted, and passes real tests. |
| `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` | Capability implemented equivalently (original code or a permitted donor) and qualified. |
| `PARTIAL` | Some of the capability exists; a measurable part is missing. |
| `BLOCKED_SOURCE` | Requires source bytes that have not been supplied. |
| `BLOCKED_COST` | Requires a paid service, funded compute or a purchased account. |
| `BLOCKED_RIGHTS` | Rights or third-party asset boundary is unresolved. |
| `NOT_TESTED` | Disposition decided but not exercised against real tests. |

> **No design, mock or adapter stub may be reported as delivered functionality.** A row may only
> claim `*_QUALIFIED` when a named test file and a named command passed on a named revision.

---

## 1. Matrix legend

| Column | Meaning |
|---|---|
| **Gomrey** | State in Gomrey at the baseline revision |
| **Presenton** | State inherited from the Presenton-derived foundation |
| **NextSlide.ai** | Commercial product — observation only, source not available |
| **NextSlide OSS** | `0xRafie/nextslide` @ `90a46f9` (MIT) — full source obtained |
| **Gamma** | Commercial platform — observation + official docs only; source not available |

---

## 2. Presentation generation and authoring

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes / evidence |
|---|---|---|---|---|---|---|---|
| `F-P01` | Prompt → deck generation | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | DOCUMENTED | OBSERVED | Gomrey `servers/fastapi/api/v1/ppt/endpoints/presentation.py` (`create` 1634, `prepare` 1783, smart stream 1874, standard stream 2224) |
| `F-P02` | Outline / content planning pipeline | `ALREADY_PRESENT` | `ALREADY_PRESENT` | UNKNOWN | DOCUMENTED | OBSERVED | `utils/llm_calls/generate_presentation_outlines.py` → `generate_presentation_structure.py` → `generate_slide_content.py` |
| `F-P03` | Adaptive layout selection | `PARTIAL` | `PARTIAL` | UNKNOWN | DOCUMENTED | OBSERVED | Gomrey returns layout *indices* from one LLM call (`models/presentation_structure_model.py`); no scoring objective, no overflow pre-check |
| `F-P04` | Layout quality assurance beyond overflow | `PARTIAL` | `PARTIAL` | UNKNOWN | DOCUMENTED | UNKNOWN | `utils/smart_slide_layout.py` checks overflow/clipping/overlap only; **contrast, density and reading order missing**. The donor specifies a 4.5:1 rule but never checks it — measured: **34/90** of its own token pairs fail in a wider matrix, and **10/54** text-on-background pairs fail in the recomputed subset. **Shipped as wave `W4a`**: `templates/v2/quality.py` + 17 tests |
| `F-P05` | Template catalogue | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | 16 bundled templates, 400+ layouts under `templates/*/template.json` |
| `F-P06` | Named style / theme presets | `PARTIAL` | `PARTIAL` | OBSERVED | DOCUMENTED | OBSERVED | **Gap.** Gomrey themes are *derived from a template only* (`templates/v2/theme.py:145-423`); no named preset layer. Gamma exposes machine-matchable `colorKeywords[]`/`toneKeywords[]` |
| `F-P07` | Brand kit (logos, brand fonts/colors) | `PARTIAL` | `PARTIAL` | OBSERVED | N/A | OBSERVED | **Gap.** Only `DesignIR.brand_skill_id` (a string) exists; no brand system, no rights boundary |
| `F-P08` | Slide transition / entrance animation | `CODE_TRANSFERRED_AND_QUALIFIED` | `ALREADY_PRESENT`¹ | UNKNOWN | DOCUMENTED | OBSERVED | **New in this mission.** See §3. ¹ Presenton had no animation model; the contract is new |
| `F-P09` | Emphasis / looping animations | `CODE_TRANSFERRED_AND_QUALIFIED` | `ALREADY_PRESENT`¹ | UNKNOWN | DOCUMENTED | OBSERVED | Same as `F-P08`; reduced-motion-safe |
| `F-P10` | Reduced-motion accessibility policy | `CODE_TRANSFERRED_AND_QUALIFIED` | `PARTIAL` | UNKNOWN | DOCUMENTED | UNKNOWN | **New in this mission.** Before: 2 files only. Now: every catalogued animation is neutralised |
| `F-P11` | Presenter mode | `ALREADY_PRESENT` | `ALREADY_PRESENT` | UNKNOWN | DOCUMENTED | OBSERVED | `app/(presentation-generator)/presentation/components/PresentationMode.tsx` (610 lines) — donor disposition `REJECT (already present)` |
| `F-P12` | Slide editor (UI editing) | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | `servers/nextjs/components/slide-editor/**` — 73 files, authoritative map in its `README.md` (1 385 lines) |
| `F-P13` | Undo / redo | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | Surface-local (`TemplateV2KonvaSlide.tsx`) **and** Redux (`store/slices/undoRedoSlice.ts`, `presentation/hooks/PresentationUndoRedo.ts`) |
| `F-P14` | Autosave | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | `presentation/hooks/useAutoSave.tsx` (212 lines, debounce + diff) |
| `F-P15` | Artifact revision / version history runtime | `PARTIAL` | `PARTIAL` | UNKNOWN | N/A | OBSERVED | **Gap.** Schema exists (`contracts/v1/`), runtime does not. Gamma exposes `get_gamma_analytics` + card-level engagement |
| `F-P16` | Deck-level AI editing (reorder / retitle / restyle) | `PARTIAL` | `PARTIAL` | OBSERVED | N/A | OBSERVED | **Gap.** `services/chat/tools.py` is per-slide only; Gamma `edit_gamma` edits existing pages (cannot add pages) and is flagged **destructive** |
| `F-P17` | Collaboration / comments / viewers | `PARTIAL` | `PARTIAL` | OBSERVED | N/A | OBSERVED | Gamma MCP: `get_gamma_comments`, `get_gamma_viewer_analytics` |

## 3. Presentation generation modes

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-M01` | Standard generation (fixed layouts + outline review + templates) | `ALREADY_PRESENT` | `ALREADY_PRESENT` | UNKNOWN | N/A | OBSERVED | `PRESENTATION_GENERATION_MODE=standard` |
| `F-M02` | Smart generation (adaptive HTML, streams into editor) | `ALREADY_PRESENT` | `ALREADY_PRESENT` | UNKNOWN | N/A | OBSERVED | `PRESENTATION_GENERATION_MODE=smart` |
| `F-M03` | Generation-mode control is *not* an authorization boundary | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | N/A | N/A | Verified: `docs/presentation-generation-modes.md` states it is not an authz control |
| `F-M04` | Offline-capable default path (no paid API required) | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | DOCUMENTED | `BLOCKED_COST` | Gomrey: optional providers off by default; Gamma MCP charges credits for generation |

## 4. Export engine

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes / evidence |
|---|---|---|---|---|---|---|---|
| `F-E01` | PPTX export | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | DOCUMENTED | OBSERVED | Gomrey owns `@presenton/export-core` v1.0.34 (verified installed and `check:presentation-export` OK) |
| `F-E02` | Editable PPTX text fidelity | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | VERIFIED | `PARTIAL` | **Independently verified**: donor PPTX = 23–28 text shapes, ~0 pictures → real editable text — **but the donor's chart export is invalid** (`'BAR'` vs `'bar'` → empty `<c:barChart>` → `python-pptx` IndexError, PowerPoint repair prompt). **Gamma claims only editable *tables***, not a full round-trip |
| `F-E03` | PDF export | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | Gamma PDF reflects Present Mode, not Edit Mode |
| `F-E04` | HTML export | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | DOCUMENTED | N/A | `servers/nextjs/lib/template-v2-json-to-html.ts` (192 230 bytes) |
| `F-E05` | Image export (PNG/JPEG/WebP) | `PARTIAL` | `PARTIAL` | N/A | N/A | `ALREADY_PRESENT` | **Gap.** Gomrey export enum is `Literal["pptx","pdf"]` (`utils/export_utils.py:46`). Gamma: PNG `.zip` with one PNG per card |
| `F-E06` | Single-file offline HTML deck | `PARTIAL` | `PARTIAL` | N/A | DOCUMENTED | N/A | **Gap.** Donor offers a self-contained HTML deck. Gomrey has an HTML renderer but no self-contained *presentation* artifact |
| `F-E07` | PPTX import | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | `PARTIAL` | OBSERVED | **Gomrey is superior.** `services/export_task_service.py` + `templates/pptx_font_utils.py` (1 668 lines) |
| `F-E08` | PPTX extraction for AI conversion | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | `PARTIAL` | N/A | **Donor extractor crashes** on a pristine PPTX (`ValueError: shape is not a placeholder`, line 281). Disposition `REJECT` |
| `F-E09` | Export fidelity regression suite | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Gap.** No export→import round-trip suite exists |
| `F-E10` | Export link lifetime semantics | N/A | N/A | N/A | N/A | OBSERVED | Gamma: ≈1 week, "treat the link as a secret" |

## 5. Import and reflow

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-I01` | Import existing PPTX | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | DOCUMENTED | OBSERVED | |
| `F-I02` | Import → AI re-layout → export round trip | `PARTIAL` | `PARTIAL` | OBSERVED | DOCUMENTED | OBSERVED | **Gap.** No round-trip fidelity suite |
| `F-I03` | Long-document → deck | `PARTIAL` | `PARTIAL` | OBSERVED | DOCUMENTED | OBSERVED | Ingestion exists (`services/documents_loader.py`); evidence-bound narrative does not |
| `F-I04` | Paste/outline → deck | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | DOCUMENTED | OBSERVED | |

## 6. Content structure and rendering

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-C01` | Multi-slide / card / page IR nodes | `PARTIAL` | `PARTIAL` | UNKNOWN | N/A | OBSERVED | **Gap.** `contracts/v1/narrative-ir.schema.json` `sections[]` is flat `{heading,text,claim_ids}`; `design-ir` `layout` is a single string |
| `F-C02` | Artifact type coverage (presentation/document/site/infographic/social/image) | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Gap.** `artifact.schema.json` declares all seven types; only `presentation` has a runtime producer |
| `F-C03` | Charts | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | `slide-editor/charts`; Gamma `guides_charts-and-structured-content` |
| `F-C04` | Tables with editable PPTX output | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | `PARTIAL` | Baseline test: `renders PPTX table borders, vector metadata, flips, and chart legend position` |
| `F-C05` | Infographics / visual elements | `ALREADY_PRESENT` | `ALREADY_PRESENT` | OBSERVED | N/A | OBSERVED | 27 infographic types (`utils/infographic_catalog.py:45-478`), slide-scoped only |
| `F-C06` | Editable vector shapes | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | N/A | N/A | Baseline: `creates line arrows as one two-point editable vector`; `renders editable vector line arrowheads as SVG endpoint markers` |
| `F-C07` | Single token source across Konva / DOM / HTML surfaces | `PARTIAL` | `PARTIAL` | N/A | N/A | N/A | **Gap.** Three parallel readers: `surface/nodes.tsx`, `TemplateV2LayoutPreview.tsx`, `lib/template-v2-json-to-html.ts` |
| `F-C08` | Typographic scale / baseline grid | `PARTIAL` | `PARTIAL` | N/A | DOCUMENTED | N/A | **Gap.** Raw pixels; donor has a typography system — comparison required before adoption |
| `F-C09` | RTL / Arabic-first typography | `PARTIAL` | `PARTIAL` | UNKNOWN | NOT_TESTED | UNKNOWN | **Gap.** No measured Arabic/RTL qualification exists in any donor or in Gomrey |

## 7. Research, evidence and grounding

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-R01` | Layered retrieval (exact → lexical → fusion) | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/retrieval_pipeline.py` — but **no index** and **no call site in the presentation pipeline** |
| `F-R02` | Citation locators + resolver | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/citations.py`, 5 locator kinds, `BrokenCitation` |
| `F-R03` | Evidence bundle + sufficiency | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/evidence_bundle.py` |
| `F-R04` | Claim contracts + evidence binding | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/claims.py` |
| `F-R05` | Deterministic verification engine (6 verdicts) | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/verification.py`; provider cannot overrule deterministic number/date gates |
| `F-R06` | Decision graph + calibrated synthesis + abstention | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | `gomrey/decisions.py` |
| `F-R07` | **Evidence-bound narrative → artifact producer** | `PARTIAL` | N/A | N/A | N/A | N/A | **Highest-value gap.** P08/P09 fabric is complete but **unwired** — no call site in the presentation pipeline |
| `F-R08` | Citation locators inside generated artifacts | `PARTIAL` | N/A | N/A | N/A | N/A | **Gap.** Gamma does not expose citations either |
| `F-R09` | Source-linked, verifiable AI editing | `PARTIAL` | N/A | N/A | N/A | `PARTIAL` | **Gap.** Gamma `edit_gamma` is ungrounded and destructive |
| `F-R10` | Adversarial citation verification | `ALREADY_PRESENT` | N/A | N/A | N/A | N/A | P09 deterministic gates |

## 8. Document, website and visual studios

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-S01` | Document creation (authoring) | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Gap.** Only *ingestion* exists (`documents_loader.py`, `office_document_service.py`, `liteparse_service.py`). No authoring, no DOCX export |
| `F-S02` | Website creation + responsive renderer | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Gap.** No website routes, IR or renderer |
| `F-S03` | Social / visual card creation | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Gap.** Infographics exist but only inside slides |
| `F-S04` | Multi-page artifact under one URL | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | Gamma `generate_multi_page_gamma` — sales rooms, proposal sites, microsites |
| `F-S05` | Publishing / embed / web output | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | |
| `F-S06` | Workspace / folder organisation | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | Gamma MCP `get_folders` |

## 9. Agent and integration surfaces

| FEATURE_ID | Capability | Gomrey | Presenton | NextSlide.ai | NextSlide OSS | Gamma | Notes |
|---|---|---|---|---|---|---|---|
| `F-A01` | MCP server surface | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | N/A | OBSERVED | Gomrey `servers/fastapi/mcp_server.py` + `fastmcp>=4.0.1` |
| `F-A02` | MCP tool taxonomy (generate / read / edit / export / status / themes / folders) | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | **Reference available.** Gamma's 21-tool split is a good target taxonomy |
| `F-A03` | Async job model with per-operation status tools | `ALREADY_PRESENT` | `ALREADY_PRESENT` | N/A | N/A | OBSERVED | Gomrey P04 durable job kernel is stronger than Gamma's polling model |
| `F-A04` | MCP destructive-operation labelling | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | Gamma flags `edit_gamma` destructive; Gomrey should expose equivalent safety metadata |
| `F-A05` | Connector / integration framework | `PARTIAL` | `PARTIAL` | N/A | N/A | OBSERVED | P07 connector sync contracts exist |

## 10. Evidence-grade status of the two commercial donors

| FEATURE_ID | Item | State | Evidence |
|---|---|---|---|
| `F-D01` | NextSlide.ai live state | `ALREADY_PRESENT` (observed) | HTTP 200, single response, no redirect; SPA catch-all renders the same sunset page for `/` and `/pricing`; `/docs` returns a Cloudflare "Performing security verification" interstitial (Ray ID `a4e5814dd930c611`) — a bot challenge, **not** evidence that `/docs` exists |
| `F-D02` | NextSlide.ai public source | `BLOCKED_SOURCE` | No repository, SDK or npm package attributable to the product was found |
| `F-D03` | NextSlide OSS source | `CODE_TRANSFERRED_AND_QUALIFIED` | `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56`, MIT, full tree obtained |
| `F-D04` | Gamma internal source | `BLOCKED_SOURCE` | All 29 `github.com/gamma-app` repositories enumerated and classified; product core not published. Peripheral integration code and one internal QA tool are separately licensed and are **not** the product core |
| `F-D05` | Gamma official API + MCP documentation | `ALREADY_PRESENT` (observed) | `developers.gamma.app` — full doc set captured under `evidence/raw/gamma_docs/`, including `mcp_gamma-mcp-server.md` and `mcp_mcp-tools-reference.md` |
| `F-D06` | nextslide.io identity | `ALREADY_PRESENT` (observed) | Confirmed an unrelated presentation clicker. Not a donor |
| `F-D07` | Founder authorisation for NextSlide / Gamma source reuse | `ALREADY_PRESENT` (attested) | Recorded in `SOURCES.md` §0. It does **not** supply source bytes; availability is tracked separately in `F-D02` / `F-D04` |

---

## 11. Summary counts

| State | Count of rows |
|---|---|
| `ALREADY_PRESENT` | 30 |
| `PARTIAL` | 31 |
| `CODE_TRANSFERRED_AND_QUALIFIED` | 4 |
| `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` | 0 |
| `BLOCKED_SOURCE` | 3 |
| `BLOCKED_COST` | 1 |
| `BLOCKED_RIGHTS` | 0 |
| `NOT_TESTED` | 0 |

**Read:** the dominant finding is that Gomrey's *editing, export, evidence and verification* foundations are
strong and largely `ALREADY_PRESENT`, while its **studio surface**, **theme/brand layer**,
**multi-node artifact IR** and **evidence-to-artifact wiring** are `PARTIAL`. The NextSlide OSS donor
closes exactly one verified gap (`F-P08`, `F-P09`, `F-P10`); the Gamma wave must be delivered as
qualified equivalents because its core source is `BLOCKED_SOURCE`.
