# Gamma 5 Deep REA — 05: Gomri Gap Analysis and Copy-First Execution Contract

**Date:** 2026-11-09. Scope: actual inspected Gomri sources, Gamma5 official user contracts, public Gamma-owned source snapshots and a practical path to shipping. This is NOT a claim that Gamma's private editor/agent source was obtained.

Companion inventories:
- [207 Gamma5 capability/contract/unknown rows](../../registry/gamma5-capability-engine-matrix-2026-11-09.csv), 18 domains. Rows include UI behavior, documentation, source code operations, and unknowns; NOT 207 independently verified product features.
- [29 Gamma public GitHub repos](../../registry/gamma-public-source-inventory-2026-11-09.csv), 10 original + 19 fork.
- [24 publicly disclosed Gamma import failure modes](../../registry/gamma-import-failure-modes-2026-11-09.csv).

## 1. What Gomri actually has

Main branch baseline is **Presenton-derived** code plus Gomri P03–P09 source/evidence/verification layers. It includes:
- Next.js editor in servers/nextjs/components/slide-editor.
- FastAPI generation API in servers/fastapi/api/v1/ppt/endpoints/presentation.py.
- Template V2 system and semantic/HTML slide rendering in servers/nextjs/lib/template-v2-json-to-html.ts.
- Presenton export runtime, native PPTX/PDF path, templates, layouts, Electron desktop.
- source ingestion, source accounting, parser/OCR worker contracts, web/media connector scaffolding, lexical retrieval/citations, evidence verification.

**Important qualification gaps on main:** OCR workers/weights and measured Arabic quality; dense/visual retrieval/benchmark; challenger verification provider; source-bound production UX; full user-ready notebook/research/agent platform/collaboration, phase P10–P16.

Open draft PR #88 combines seven development branches with a real W3 source-backed narrative path, W13 Arabic/RTL, W12 PPTX fidelity, W8 image export, NextSlide OSS animation contracts and contrast checks. Local Windows evidence: root 55/55, Next.js 148/148, native export fidelity 15/15, production build passed. But **PR #88 is not main**; FastAPI full suite / exact-head CI were not qualified as complete in the prior session. Do not count draft features as shipped.

## 2. Gamma's distinctive engineering strengths vs current Gomri

| Capability | Gamma evidence | Gomri current/draft condition | Priority and direct action |
|---|---|---|---|
| Plan vs Express vs Research | Current official Gamma 5 guide | Basic standard/smart generation; no verified equivalent conversational plan approval | P0: add durable intent/plan approval before generation; reuse existing jobs |
| Lite/Standard/Max | Official quality selector and live Standard | No equivalent scored quality-vs-budget mode | P1: deterministic quality profiles and local provider choices |
| Editable grid + freeform | Official 16:9 proportional grid and freeform boxes | Template V2 flex/grid/absolute primitives, but no qualified user-facing Gamma5 grid/freeform dual edit | P0: typed grid/cell conversion and native editing UI adapter |
| Targeted AI editing & diff | Official Agent and Original/Modified | Per-slide chat tools and undo foundations; no full shared canonical per-object patch transaction | P0: adapt Ninerr MCP/transaction/undo; use existing editor |
| Version history even Free | Official docs | Partial version contracts, no equivalent audited user workflow | P1: attributable deck revisions and recovery |
| Source research and citations | Gamma Plan Research Pro+ and quick search | Gomri source IR and W3 narrative draft can differentiate | P0: source-to-slide evidence and post-edit claims verification |
| Strong native PPTX import | Gamma5 import marketing and internal evaluator | Presenton import base; W12 fidelity harness partial; no 24-mode visual QA | P0: run new evaluator with 24 categories, structure+pixel+human grades |
| Two visual output modes | Gamma native elements vs image slides | Presenton editable native; optional image generation not same pixel pipeline | P1: explicit native vs raster with flattening reports |
| Theme vs per-document Styles | Official Gamma help | Theme derived from templates, limited named preset/brand tokens | P1: Skilit brand/reference adapter |
| Intelligent charts and editable data | Official Smart Charts | Native chart components exist; exported reimport data needs expanded qualification | P0: chart loss/no-fabrication QA |
| Sites, social, documents | Product/UI + API | Product contracts broader but only presentation runtime truly verified | P2: don't overextend before flagship deck |
| Comments + analytics + API | Public n8n actions, product docs | MCP/REST foundations but full parity not demonstrated | P2: bounded APIs, comments and view stats |
| Gamma5 vs Classic engines | Public Gamma n8n source | Presenton Standard/Smart modes | P1: versioned APIs with strict capability/field validation |
| Browser PPTX preview | Public fork gamma-app/pptx-renderer from aiden0z | Presenton importer and rendering exist | P0 comparison: test native fidelity vs existing, keep winner |
| Import eval with VLM calibration | Original gamma-app/import-grader-annotator source | W12 15 real deterministic PPTX fixtures but no human+VLM calibration | P0 design independent tool; do not copy unlicensed source blindly |
| Private Gamma core model and editor | No public source | Cannot transplant | BLOCKED_SOURCE; independently implement observable behavior |

**Core decision:** Gomri should NOT be a duplicate of Gamma's private product. Copy public, admitted and owner-held source and match verified product behavior. To win, improve both visual quality and evidence/native editability.

## 3. Source admission rank — what was actually obtained

**Source snapshots committed (NOT installed or running in Gomri):**

1. gamma-app/pptx-renderer at 68cb570940fb28d5c4628f31d1365016c4483521, Apache-2.0, 381 files. Important upstream attribution: aiden0z/pptx-renderer fork. It is a read-only browser viewer/parser, not Gamma's private editor. The fork appears older than its upstream; test against both.
2. gamma-app/n8n-nodes-gamma at 5d0b466a9ae4be994a722577daa0a761cb28cfaf, MIT, 54 files. Gamma API client code and tests, not backend.
3. gamma-app/aijsx at 2900075d8251b7a83c6b855fcf36e6df4c5d2539, MIT, 39 files. Historical Gamma/Fixie-AI derivative prompt construction, not proof Gamma5 uses it.

**Real source inspected but NOT copied:**
- gamma-app/import-grader-annotator: original Gamma app, 24 failure modes, 22 mapped VLM graders, 3 output variants, kappa calibration; no publicly detected LICENSE. Its referenced private gamma monorepo evaluator rubrics are missing. Do not conflate read access with public redistribution permission.
- gamma-app/tiptap, y-prosemirror, chakra-ui, tldraw and others: forks, historical clues, no evidence used in the current private editor.

**Owner-controlled donors:**
- TheHalfMoon/Ninerr: actual selection, MCP, authorization, edit history and Undo agent change.
- TheHalfMoon/Skilit: design patterns, brand/reference intelligence.
- TheHalfMoon/Gomri (Presenton): existing templates, slides, charts/tables and export.
- Gitbrent/PptxGenJS: independent native editable PPTX benchmark/provider.
- SlidePoise: image-to-editable PPTX comparator only after measured QA.
- RAGFlow/Open Notebook for source knowledge later, not as a replacement for the editor.

## 4. Ordered implementation waves with acceptance gates

### G5-00: qualify the source snapshot (no runtime behavior yet)

- Pin SHA, source license, third-party notices, binary assets and provenance.
- Run npm/vitest and TypeScript compile against pinned source in a disposable worktree, with zero credentials and network disabled at runtime.
- Evaluate security: ZIP expansion, external relationships, embedded font and PDF.js worker, third-party font/image fetching.
- Record performance/bundle footprint, startup time and renderer screenshot reproducibility.
- Keep source under third_party quarantine until its intended integration is proven.

### G5-01: frozen native PowerPoint import benchmark (P0)

- Build 30 originally authored synthetic PPTX decks: 16:9, grid layouts, charts with numeric series, tables with merged cells, grouped shapes, notes, images, Arabic+English, unsupported fonts, SmartArt and malformed archives.
- Render source in independent native PowerPoint/LibreOffice and parsed DOM with the imported @aiden0z/pptx-renderer; render Gomri's imported output.
- Compare structured XML (object type/data preservation) before comparing pixels.
- Export/import through Gomri and record unsupported flattening.
- Derive original failure taxonomy from public 24-category Gamma source *descriptions*, with independent code and synthetic fixtures.
- Human grade and deterministic screenshot/diff metrics; optional licensed local/hosted vision grader under explicit zero-cost controls.
- Gate zero data-loss failures for charts/tables on supported object types and zero malformed PPTX.

### G5-02: structural grid/freeform editor bridge (P0)

- Add a canonical user-editable SlideScene IR type for Grid(rows, columns, cells) + FreeformLayer(items).
- Map into existing Template V2 flex/grid/absolute nodes; do not replace editor.
- Expose resize/reorder/convert/undo with stable IDs and versioned history.
- Handle 16:9 fixed and fluid separately; warn when export requires fixed-size transforms.
- Visual QA on 20 differently composed layouts: no clipped title, no chart data loss and correct Arabic direction.

### G5-03: Plan/Express and scoped agent edits (P0)

- Plan prompts for goal, audience, source selection, outline/story; explicit approval checkpoint. Express creates quickly but still verifies facts.
- Reuse W3 evidence source/claims and durable jobs.
- Borrow bounded Ninerr authorization and history; target one slide/element per edit, produce typed patch with selection, base revision, idempotency key.
- Original/Modified preview, accept/reject and reversible undo.
- Prevent changes to unselected slides and denial on stale state.

### G5-04: style/reference intelligence and visual quality (P1)

- Adapt Skilit design patterns and named brand tokens, reference deck styling.
- Generate a bounded set of editable layout candidates, render to PNG and score against hard overflow/contrast/RTL checks.
- Independent designer blind-preference tests for Gamma, Gomri and GPT Slides; measure per-task true match quality, not marketing claims.

### G5-05: broader API, comments, analytics and publishing (P2)

- Use the public n8n client as a competitor API contract reference; never call Gamma from Gomri production.
- Typed REST/MCP operations for create/search/get/edit/export/comments; durable status polls, idempotency, revision conflicts, permission checks.
- Comments trigger bounded agent jobs with ACL; viewer cannot escalate.
- Publish decks/sites and add view statistics only after core quality passes.

## 5. Release gates / must-not-claim

**NO-GO** until:
- root/backend/Next.js tests and exact-head CI are green, not merely queued;
- typed editor export fidelity measured across at least 30 decks;
- source admission confirms no problematic transitive licensing/assets;
- no viewer/agent cross-workspace source leakage or SSRF;
- all edits are scoped, reversible and revision controlled;
- Windows/macOS/Linux smoke tests where release promises them;
- native/raster object downgrade report is accurate;
- blind comparison demonstrates objective improvements.

The user asked to acquire Gamma source. **This branch actually contains 474 public source files** plus research. It does **not** contain Gamma's closed editor/backend, and source snapshots are not functioning feature implementations yet.

## 6. Fifty controlled black-box test prompts (planned, not executed)

A — creation: create from paragraph; create from spreadsheet; create with links; create with PPTX reference; create without web research.
B — agent: Plan outline approval; Express quick; Research mode (plan-gated); Lite vs Standard vs Max; stop/retry a generation.
C — layout: resize grid row; resize grid column; convert grid to freeform; overlap shape; change fixed/ fluid height.
D — elements: modify native chart; modify merged table; edit image crop; adjust logo/header/footer; edit shape/vector.
E — quality: conflicting theme fonts; unavailable font; Arabic+English mixed text; notes and citations; long overflowing text.
F — import: faithful PPTX preserve; PPTX redesign; multi-PPTX 50-file accounting; PDF import; XLSX/CSV import.
G — editor: selected-slide AI edit; global theme edit; original/modified toggle; manual undo; Version History recovery.
H — export: PPTX editable table; PPTX chart source data; speaker notes; PDF layout; PNG slide export.
I — integrations: API async generation; API edit one page; API concurrent same-page 429/conflict; MCP permission; Gamma Classic webpage.
J — adversarial: viewer edit denied; external source access denied; malicious PPTX zip/relationship; invented chart figures; duplicate delayed job.

There are 5 scenarios in each A–J group, **50 total**. They are a protocol for authorized future tests; no 50-case Gamma production run occurred in this REA. Collect input hashes, screenshots, native OOXML object diffs, credits spent (if any), result, severity and confidence for each case.

## 7. Suggested priorities relative to "beat Gamma"

**First demonstrable competitive wedge:** perfect native editable PowerPoint import/export + Arabic + evidence-backed factual charts. This is more testable and defensible than claiming that new AI visuals beat Gamma after one screenshot.

**Second wedge:** selection-scoped AI editing with complete undo and no lost user changes.

**Third wedge:** outstanding design quality and reference style matching from real held-out decks.

Measure them separately. 55/55 root or 148/148 Next.js local tests on draft PR #88 demonstrate code sanity; they do **not** establish superiority.

## 8. Current answer to the source question

- YES: actual publicly accessible Gamma-org source packages were copied, pinned and preserved into Gomri GitHub.
- YES: actual Gamma-authored import-evaluation system source was inspected and analyzed, and its 24 mode names reproduced as a reference matrix.
- NO: no Gamma proprietary web-editor server code, agent model composition, current template database or private workspace source was acquired.
- NO: new Gamma source snapshots have not been activated inside Gomri or benchmarked as superior.
