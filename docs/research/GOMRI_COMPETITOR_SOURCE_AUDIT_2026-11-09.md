# Gomri — Competitive and Source Audit (9 November 2026)

**Type:** research / architectural recommendation, not implementation acceptance.
**Evidence boundary:** GitHub default-branch inspection + source README/LICENSE pages as of 2026-11-09. No competitor account benchmarking, cloned donor test, full runtime QA, or production parity has been executed in this research grain.

## Executive decision

**Gomri** is an evidence-grounded, agent-first creation system. **Presenton remains the qualified executable foundation.** Do not replace its working editor/export path without a measured regression-safe alternative. Win over AI presentation systems by combining **source-supported narrative + genuine native editability + excellent visual quality + reproducible exports + agent/human control**.

The requested competitor is **NextSlide AI** at https://nextslide.ai/ (joined OpenAI in 2026), not the unrelated clicker product at nextslide.io. NextSlide's historical core: turn prompts/notes/documents/research into polished editable presentations. Its source code is not in this repository. Gamma's present site and help center show AI Agent, conversational edits, 16:9/freeform canvas, source research/citations, brand themes, connected tools, sharing, APIs/MCP, documents, websites, and exports. These are **competitive reference claims**, not Gomri benchmarks.

## Verified current Gomri status and gaps

- Repository renamed from `TheHalfMoon/Gomrey` to `TheHalfMoon/Gomri` on 2026-11-09; default branch `main`.
- Source tree inspected: **11,927 Git tree paths** (files and directories); not 11,927 independently implemented features.
- P01 Presenton import: `docs/evidence/P01_PRESENTON_IMPORT.md` records exact donor snapshot, 11,468 matching non-README files and past source/CI qualification. **Not** a freshly performed production smoke test.
- P02 identity baseline existed under **Gomrey** before GitHub rename. `product-identity.json`, npm locks, desktop ID, code symbols, scripts and test expectations still depend on the legacy name. **Do not globally search/replace** without migration and compatibility tests.
- P03-P09 have code modules and phase evidence for contracts, durable jobs, source accounting/security, parser/OCR worker contracts, web/media connector scaffolding, lexical retrieval/citations, and verification/decision fabric.
- `docs/evidence/P06_EXIT.md`: worker packaging and measured parser/OCR qualifications still pending.
- `docs/evidence/P08_EXIT.md`: no dense/visual index and **no frozen benchmark proving retrieval beats the baseline**.
- `docs/evidence/P09_EXIT.md`: no measured challenger decision-provider calibration; deterministic verification only.
- No P10-P16 exit evidence found in `docs/evidence/` as of this audit. Notebook/research UX, new presentation compiler, agent platform, plugins, collaboration, benchmark arena and GA **must not be claimed complete**.
- Exact current-head CI, live Windows/macOS/Linux installers, native PPTX object fidelity, and end-to-end competitor quality remain **UNVERIFIED** in this research grain.

## First-party GitHub source shortlist

| Priority | Repository | Use in Gomri | Evidence / caution |
|---|---|---|---|
| P0 | `TheHalfMoon/Gomri` | Keep Presenton editor, FastAPI, Next.js, Electron, editable export baseline | Actual imported code; preserving product tests/provenance is critical |
| P0 | `TheHalfMoon/Ninerr` | Adapt node/layer inspector, HTML/CSS editing, history/undo, MCP-assisted live editing, source-bound components | Real modules in README: `packages/document-model`, `packages/history`, `packages/canvas`, `packages/studio-web`; test slice and API compatibility first |
| P0 | `TheHalfMoon/Skilit` | Visual-reference indexing, brand/design tokens, quality/pattern library and capture workflow | Existing local-first design intelligence; study `docs/brand/`, `UPSTREAMS.lock.yml`; avoid copying a second entire app |
| P1 | `TheHalfMoon/Morize` | Temporal evidence, contradiction/supersession, explainable recall and source revision graph | README/donor-ledger describe intended local-first memory; inventory executable implementation before copy |
| P1 | `AbdulazizShehri/MedOrigin` | Generalize source/evidence-span provenance and deterministic checks from medical domain | Research/synthetic-only guarantees; do not transfer patient/clinical assumptions to generic product |
| P1 | `TheHalfMoon/Winds` / `TheHalfMoon/Ascout` | Reproducible independent verification, proof-before-done receipts and regression gates | Tooling for Gomri engineering and artifact quality, not editor foundation |
| P2 | `TheHalfMoon/Ecra` | Future search/browser permission/trust interfaces and donor discovery | `EXECUTION.md` shows ECR-001/002/004 substrate, not shipped integrated Perplexica-class search; no source-copy claim |
| P2 | `TheHalfMoon/Flind` | Optional future analytics / experiment funnels | README explicitly says imported pre-alpha with release parity unverified; not suitable as near-term critical dependency |
| P3 | `TheHalfMoon/Inercative` / `TheHalfMoon/SafeEvidence` | Architecture/evaluation ideas | README currently describes planning/foundation; do not confuse planning with reusable production code |

**Unresolved:** No repository named `Elum` was discovered in either linked GitHub account's accessible repository list or installed-repository search. Exact locator needed before claiming its implementation can be reused. `Ecra` is present and was inspected.

## External source shortlist (freshly reviewed candidate, not admitted code)

| Priority | Repository | Proposed bounded use | Posture |
|---|---|---|---|
| P0 | https://github.com/presenton/presenton | Keep stable current executable foundation | **Already imported** at pinned 2026-10-02 snapshot; compare upstream changes |
| P0 | https://github.com/hugohe3/ppt-master | Native OOXML editability; slide masters/layouts, templates, charts/tables, transitions, animations, speaker narration | **Bench + selective adapt**; MIT project but its optional PyMuPDF dependency can impose AGPL obligations |
| P0 | https://github.com/henryhyw/slidepoise | Design image → semantic object map → OpenCV measurement → editable PPTX reconstruction and visual QA | **Bench + selective adapt**; MIT; expensive image inference is optional, never correctness dependency |
| P0 | https://github.com/zarazhangrui/frontend-slides | Visual style discovery with samples, HTML slide artistry, rich non-generic style presets, web deck production | **Adapt skills/rules**; MIT; do not confuse attractive HTML with native PPTX objects |
| P1 | https://github.com/nexu-io/open-design | Agentic design-system workflow, deck studio, slide notes, live preview, asset library | **Bench + selective adapt**; Apache-2.0 main repo; per-template bundled licenses retained |
| P1 | https://github.com/alchaincyf/huashu-design | Style library, distinct candidate directions, expert design critique and motion/infographic routes | **Adapt skills/design benchmark**; README reports MIT relicense in 2026 |
| P1 | https://github.com/slidevjs/slidev | Web slide authoring, presentation mode, theme/runtime, explicit editable-PPTX pathway | **Depend/benchmark**; editable export has documented partial-raster fallback/unsupported browser effects |
| P1 | https://github.com/gitbrent/PptxGenJS | Deterministic native PowerPoint text/charts/tables/shapes/master slides and RTL support | **Dependency/adapt**; MIT; benchmark with existing export core first |
| P1 | https://github.com/infiniflow/ragflow | Strong RAG/agentic retrieval, knowledge compilation, connector/dataset workflows | **Selective donor only**; existing ledger already lists it |
| P1 | https://github.com/langchain-ai/open_deep_research | Iterative research plan/search/reflection/citations and multi-agent workload design | **Optional bounded research engine**; qualify network/model costs |
| P1 | https://github.com/microsoft/markitdown | Supplemental conversion of PPTX/DOCX/XLSX/PDF and other files | **Sandboxed adapter**; structure loss and privileged I/O warnings matter |
| P2 | https://github.com/lfnovo/open-notebook | Notebook-like source management and podcast/audio summaries | **Selective donor**; already planned |
| P2 | https://github.com/MODSetter/SurfSense | Web, Drive, YouTube and browser source integrations | **Optional connector patterns**; already planned |
| P2 | https://github.com/yjs/yjs or https://github.com/loro-dev/loro | Realtime collaborative document/canvas revisions, offline merge | **Pick one via CRDT spike**; never bolt two competing authorities onto the same artifact |
| P2 | https://github.com/excalidraw/excalidraw | Diagram/canvas authoring and whiteboard-like media | **Optional embedded editor**; MIT component notices |
| Review-only | https://github.com/tldraw/tldraw | Canvas interaction patterns | **DO NOT blindly copy/deploy**: current tldraw license has special production/license-key restrictions |

**Gamma source**: founder authorization is asserted in existing ledger, but **no exact accessible repository/archive is provided**. Do not copy from Gamma website or assume NextSlide/OpenAI source is public. Competitor research is behavior/reference only until a pinned source artifact and rights boundary exists.

## Differentiated product architecture (strict implementation order)

1. **Narrative and truth before pixels.** User brief → audience/decision → outline → typed claim/evidence graph → approved story → Design IR → semantic slide objects. Source omissions and contradictory evidence are visible, not papered over.
2. **Three editing modes share one Artifact IR:** conversational AI edit, manual structured slide editor (freeform, grids, drag/resize/inspect), and code/HTML edit for advanced/agent users. Use expected-revision/idempotent transactions and real undo/redo.
3. **Native PPTX is an acceptance gate, not marketing copy.** Text, tables, charts, connectors and images are represented as individual editable entities when supported. Unsupported effects produce a declared per-object rasterization report, not silent full-slide screenshots.
4. **Beautiful by design:** style exploration gives at least three visually distinct candidates; templates/brand kits/design tokens; semantic composition constraints; inspect at multiple slide sizes. Add purposeful animation/diagrams only after native editability is sound.
5. **Research mode:** source scope, web search, notebook, citations with exact locators, verification states, PDF/web/video import, freshness and retrieval sufficiency. Use optional local models, with no hidden paid inference dependency.
6. **Artifact verification:** source-claim support, numeric integrity, Arabic/RTL fidelity, figure/table correctness, contrast/accessibility, overflow/clipping, font substitution, export/readback, and social/website responsive screenshots.
7. **Agent-first:** identical capabilities exposed through versioned REST, MCP tasks/tools, and later A2A. No hidden UI-only path for normal create→verify→edit→export workflows.
8. **Local + self-hosted:** local-first core workflow, optional explicit hosted adapters, pinned budgets and resumable jobs. Do not pull enterprise hosting or analytic complexity ahead of deck quality.

## Build sequence

**S0 — Name migration and truth lock**
- Brand/GitHub locator = Gomri (GitHub rename complete).
- Keep a **versioned compat migration**: `GOMREY_*` and `PRESENTON_*` env reads preserved (with documented priority) while new writes become `GOMRI_*`. Preserve existing user data, app migrations, SQLite/state paths, updater settings, OAuth callback compatibility, file extensions, API auth header aliases, npm/pip locks, Docker, and installer identifiers. No bulk replace in provenance/NOTICE, URL paths, old exact-pin evidence, or snapshots.
- Require Windows/macOS/Linux packaging, state migration and upgrade/downgrade tests before changing desktop ID. Update code tests atomically.
- Record a proper canonical rename PR rather than pretending the GitHub repo rename updates application internals.

**S1 — Baseline certification**
- Reproduce current Presenton-derived real prompt→edit→export flow; frozen fixture deck; capture editable-object counts and export screenshots; verify source/permissions and QA. Stop/repair current regression before donor absorption.

**S2 — Native deck/render arena**
- Implement one adapter each for current Presenton export, PPT Master, SlidePoise, and PptxGenJS on 10 representative fixture decks. Compare native editability, render parity, runtime/cost, source fidelity; promote winner per workload, never by stars.

**S3 — Design intelligence**
- Borrow style-preview selection from Frontend Slides/Huashu and visual/design systems from Skilit/OpenDesign; build typed reusable brand/design packs. Integrate with Ninerr-style inspector and history only after stable IR.

**S4 — Research-to-deck**
- Integrate P06-P09 into one working P10 flow: source notebooks, RAG, citations, claim-level verification and conflict surfacing, source-change refresh. Add genuine dense/visual retrieval only if measured gains justify complexity.

**S5 — Team/agent modes and release**
- Add collaboration through a single CRDT layer after revisions/authorization are stable. Then template libraries, share/revoke, version history, publishing and analytics. Qualify API/MCP parity and cross-platform installers.

## Competitive acceptance arena

Use identical briefs/source bundles and fixed budgets to compare Gomri versus Gamma and available historical NextSlide artifacts/representative outputs. **Proposed target thresholds, not current results:**

- 50+ tasks (pitch, consulting, research, finance, teaching, Arabic RTL, mixed-language, PPTX import/edit, large sourced corpus), held-out across difficulty.
- 100% of declared source units accounted for; no silent drops.
- 100% of unsupported claims either repaired, downgraded with visible caveat, or blocked.
- ≥95% of supported semantic native elements editable in export across benchmark deck set (track exceptions).
- ≥98% of slides free from material clipping/overflow by screenshot inspection (plus zero unresolved critical failures).
- Exact citation locator precision audited on all material sourced claims, with measurable recall/precision and source-staleness reporting.
- Visual quality: blind independent expert preference / task-specific win rate, not model self-grading; aim for a statistically supportable lead, report confidence intervals.
- Export round-trip test (PPTX→PowerPoint/LibreOffice render→re-import) must preserve content and identify substitutions.
- Cold-start, generation latency, peak RAM/VRAM, token/API cost, offline compatibility, crash recovery, security/ACL cross-tenant tests.

## Exclusions and legal/security gates

- A project being on GitHub is not equivalent to unrestricted rights in nested models/fonts/templates/images. Record exact revision/path/permissions/notices/transitives for each adopted slice.
- Never transfer private repo code or third-party proprietary source into public Gomri without verifying public redistribution rights.
- Never erase Presenton/Gamma/other third-party provenance from license/NOTICE or historical evidence.
- `tldraw` production license cannot be assumed permissive.
- No model-provided claim is evidence. Publish user-controlled, traceable source receipts.
- No benchmark/performance claims are approved until executed on a frozen exact candidate.

## References reviewed

- https://nextslide.ai/
- https://gamma.app/
- https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api
- https://help.gamma.app/en/articles/11016396-what-are-slides-in-gamma-and-how-do-they-work
- https://github.com/hugohe3/ppt-master
- https://github.com/henryhyw/slidepoise
- https://github.com/zarazhangrui/frontend-slides
- https://github.com/nexu-io/open-design
- https://github.com/alchaincyf/huashu-design
- https://github.com/slidevjs/slidev/blob/main/docs/guide/exporting.md
- https://github.com/gitbrent/PptxGenJS
- https://github.com/infiniflow/ragflow
- https://github.com/langchain-ai/open_deep_research
- https://github.com/microsoft/markitdown
- https://github.com/yjs/yjs
- https://github.com/loro-dev/loro
- https://github.com/tldraw/tldraw/blob/main/LICENSE.md
- First-party canonical phase documents: `docs/MASTER_PLAN.md`, `docs/SOURCE_LEDGER.md`, `docs/evidence/P01_PRESENTON_IMPORT.md`, `P06_EXIT.md`, `P08_EXIT.md`, `P09_EXIT.md`.


## Addendum — Open REA implementation PR inventory (verified 2026-11-09)

The default branch alone understated actual progress. **Eight previous REA PRs (#78–#85) are OPEN and unmerged.** Their precise code and review packets were inspected. Existing work should be qualified/merged rather than recreated. The PRs describe local passing test evidence, but their October 22 GitHub Actions jobs were blocked at runner admission by an account billing/spending-limit condition; this is **not a CI PASS**. The new docs PR #86 was still QUEUED on GitHub Actions run `42531699780` when this addendum was prepared.

| PR | Actual branch work | Integration consequence |
|---|---|---|
| [#78](https://github.com/TheHalfMoon/Gomri/pull/78) | Deep REA evidence, imported bounded MIT NextSlide *skill* donor `0xRafie/nextslide@90a46f9...`, 24-animation catalog, deterministic stylesheet | Animation catalog is NOT the proprietary `nextslide.ai` source; review donor attribution separately. Base branch = `main` |
| [#79](https://github.com/TheHalfMoon/Gomri/pull/79) | WCAG contrast/legibility checks, with fixture audit of 18 upstream skill palettes | **Stacked on #78**; GitHub reported CONFLICTING as of 2026-11-09. Must land/reconcile #78 first and resolve conflicts without unreviewed rebases |
| [#80](https://github.com/TheHalfMoon/Gomri/pull/80) | Actual app integration of P08/P09 evidence into `POST /presentation/generate`, narrative IR, citation identity and containment gates | **High-value P10/P11 bridge**; do not describe grounded-deck workflow as absent from every branch. Independent `main` branch |
| [#81](https://github.com/TheHalfMoon/Gomri/pull/81) | Animation field on slide element model and Next.js HTML renderer wiring | Requires wave-1 catalog (#78); check declared dependency graph and retest after #78 |
| [#82](https://github.com/TheHalfMoon/Gomri/pull/82) | Arabic/RTL script direction and renderer/export qualification | High priority for genuine bilingual deck quality; independent `main` branch |
| [#83](https://github.com/TheHalfMoon/Gomri/pull/83) | Deterministic PPTX export→re-import regression harness | Measured drops documented: notes not reimported, stroke/table/rotation/shape-type fidelity; does NOT prove visual/pixel round-trip. Independent `main` branch |
| [#84](https://github.com/TheHalfMoon/Gomri/pull/84) | PNG/JPEG/WebP slide-image ZIP export via current `@presenton/export-core` renderer; API/OpenAPI tests | Existing renderer reused; independent `main` branch |
| [#85](https://github.com/TheHalfMoon/Gomri/pull/85) | Delete unused root `layouts.json` and add orphan-file guard tests | Repo hygiene only; independent `main` branch |

**Live merge recommendation:**
1. Confirm the account-side GitHub Actions billing limit and restore runner admission at no unapproved cost.
2. Requalify exact current heads for the independent PRs #80, #82, #83, #84, #85; check for intersecting files/migration conflicts; merge them in a tested dependency order, with post-merge regression and reviews.
3. Qualify #78 and then carefully reconcile #79 and #81 on top, respecting the canonical merge/CI policy. Do not force-merge #79 while CONFLICTING.
4. Integrate surviving changes with S0 Gomri identity migration and the donor adoption/benchmark plan; rerun tests on the integrated tree. Product capability is not complete while sitting in a detached PR.
5. The March/October REA packets are historical, not substitutes for a fresh QA run. No part of the current study asserts GitHub CI success or a finished feature based only on PR body claims.

**Revision to previous audit summary:** P10–P16 lack merged phase exit evidence on `main`, **but there are substantive unmerged executable candidates implementing parts of the P10/P11 gap**. Baseline truth and active work truth must both be considered.
