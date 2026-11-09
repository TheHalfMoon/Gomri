# Gomri: EGM Elephant Design Draft — A Reliable, Editable, Source-Grounded Presentation Engine

**Status:** PROPOSED / NOT APPROVED FOR IMPLEMENTATION. **Date:** 2026-11-09. **Design method:** Google Elephant-Goldfish Model (EGM); this is the Elephant-context design, prior to independent Goldfish verdict. **Repository:** TheHalfMoon/Gomri. **Base:** main at 5f299a7a6174ad3a1180f827778db5f4400a4d71. **Do not treat PR #88–#92 as merged.**

## 1. Problem and user outcome

Gomri's original October 5 master plan describes a large agent-first knowledge and creation platform, P00–P16. The recent competitor studies add responsive design, editable slide agents, and source-grounded visual generation. The risk is building five mostly independent clones (Gamma, Beautiful.ai, VistaCreate, GPT Slides, NextSlide) rather than one reliable product. A deck that looks attractive but loses a native chart, number, citation, notes or Arabic text after edit/export is not acceptable.

**First user journey, end to end:** Given an instruction and optionally user-authorized files/URLs, build a credible outline with source annotations, allow approval/edit, produce an attractive editable 8–12 slide deck using one existing canvas, then perform one tightly scoped change and export a native editable PPTX. Open/export/reimport must preserve supported text, chart/table data, source attribution and presenter notes; unsupported items must produce an explicit loss report. No hidden paid API or user-data upload.

**Initial supported environment:** Windows desktop and local browser, using the currently working architecture. macOS/Linux parity, collaborative editing and a large partner platform are later tracks, subject to testing. Free/local deterministic mode must function for fixtures without hosted AI.

**North-star gate:** one real, reproducible, usable journey with a visually reviewed editable PPTX and no silent factual or structural loss. Do not call Gomri better than Gamma/Beautiful.ai without matched external head-to-head data.

## 2. Evidence and baselines (facts versus pending branches)

- main at **5f299a7** contains Presenton-derived Next.js presentation editor, an existing Konva/Template V2 surface, text/table editing, selection/transforms, Redux history, FastAPI generation and source/claim contracts, and bundled export runtime.
- Existing code paths checked on main: \`servers/nextjs/components/slide-editor/surface/TemplateV2KonvaSlide.tsx\`; \`servers/nextjs/components/slide-editor/model/model.ts\`; \`servers/nextjs/components/slide-editor/selection/transformSession.ts\`; \`servers/nextjs/app/(presentation-generator)/presentation/hooks/PresentationUndoRedo.ts\`; \`servers/nextjs/store/slices/undoRedoSlice.ts\`; \`servers/nextjs/lib/run-bundled-presentation-export.ts\`; \`contracts/v1/design-ir.schema.json\`; \`contracts/v1/artifact-revision.schema.json\`.
- The current DesignIR schema **does not yet define a rich scene graph**: it stores identity, a \`layout\` string, string token map, and components with \`component_id\`, \`component_type\`, \`citation_ids\`. Do not invent typed spatial/content fields inside that existing v1 schema without an explicit versioned migration.
- ArtifactRevision v1 has artifact_id, revision, tenant_id, workspace_id, parent_revision, content_digest, evidence_bundle_id, verification_state, author_principal_id and idempotency_key. A revision concept exists; this does **not** establish a deployed atomic compare-and-swap endpoint for individual slide edits.
- Open **Draft PR #88** at d4362c6d968d2746d499630d8498d3111c98c90b contains integrated source-linked narrative, animation, RTL and native export fidelity work. Its earlier local Windows tests were reported (root 55, Next.js 148, PPTX fixture 15) but full FastAPI, end-to-end UI and exact-head GitHub CI were **not verified as complete**. Treat it as a candidate baseline, never a release.
- Open **Draft PRs #89–#92** are research. Beautiful.ai first-party public Apache/MIT docs/source, VistaCreate/Crello legacy utility source and Craft Anything captures are **reference and donor candidates**, not running Gomri features or competitors' private engines.
- Current external evidence: Beautiful.ai Smart Slide docs describe a 12×12 grid and a render-before-update agent flow; Gamma research motivates story quality and citations; VistaCreate Resize sometimes requires manual repair; NextSlide public site currently shows the OpenAI announcement; GPT Slides private editor code is not exposed. The studies include no valid head-to-head product scores.
- Zero-cost/no-cloud-first; source archive provenance and original notices preserved; no unlicensed stock/template copy. Legal ability to use code still requires exact accessible source and third-party notices/assets checks.

## 3. Goals and measurable acceptance

**G1.** 30 approved synthetic deck fixtures including medical-policy-style evidence narratives, finance charts, comparative tables, timeline/diagram slides, Arabic/English mixed-script typography and long titles. Each fixture has a frozen input hash, expected semantic data, font set, data rights and known export loss inventory.

**G2.** Four initial SmartLayout families, not 73 template clones: \`headline-hero\`, \`stat-chart\`, \`comparison\`, \`timeline-process\`. These must reuse the existing Template V2 scene/editor, preserve stable IDs and provide explicit fit errors, not rasterized thumbnails pretending to be elements.

**G3.** No silently dropped \`component_id\`, citation IDs, chart series values/labels, table cells, speaker notes, document identity or revision during supported edits, layout swaps or format exports. Unsupported content is retained in canonical state and flagged in a loss receipt.

**G4.** Selected AI edit is a typed proposal/preview/commit, with user scope, base revision and server-enforced permissions, immutable source references, and Undo/Redo semantics. Conflicting concurrent writes and revoked access fail closed.

**G5.** Native editable PPTX verified by inspecting actual OOXML object types and reimporting; screenshot similarity alone is not proof. Chart data, notes, text and RTL each have separate pass/fail accounting. If a feature cannot stay native, disclose its fallback.

**G6.** Offline deterministic templates and tests incur zero inference/cloud cost. A remote provider must be explicit opt-in, never a mandatory correctness dependency.

**G7.** Release gate includes Windows real-app UI smoke, clean builds, exact-head CI, independent review and published limitations; do not merge a PR based on a research document or stale earlier test.

**Benchmark targets for design evaluation, NOT present facts:** at least 98% of slides without unintended clipping/overlap on frozen fixtures; at least 95% supported native elements retained through PPTX/reimport; at least 60% blind designer preference over incumbent Gomri output on the same 30 prompts. Hard gates (data, permissions, unauthorized network) have zero-tolerance.

## 4. Non-goals for first release

Do not reproduce every Gamma/Beautiful.ai/VistaCreate feature, 200K commercial templates, social scheduler, print marketplace, paid stock catalog, third-party private server or model weights, full online collaboration, multi-agent plugin marketplace, simultaneous 16-product support, AI-created vector paths from arbitrary photos, or an entirely new editor state store. Do not imply \`nextslide\` public animations are NextSlide.ai private code. Do not build Object Grabber, MP4 rendering, ROI sliders, interactive maps or background removal before a source-to-editable-PPTX journey passes. Those remain separate P1/P2 research hypotheses.

## 5. Proposed system shape and state ownership

\`\`\`text
User files / URLs / prompt  -> Source Gateway / unit accounting
                                  |
                           SourceIR + claim/citation evidence
                                  |
                     Typed NarrativeIR + outline approval
                                  |
             Presenter compiler: message role + template family
                                  |
                  Canonical slide semantic nodes + version
                          /                        \
         Existing Template V2/Konva editor        Export projection
           (one canvas authority)                PPTX/PDF/image
                          \                        /
                           preview + data/layout QA
                                  |
                  proposed patch -> compare/recheck -> commit
                                  |
                         revision + undo + receipt
\`\`\`

**Authority rule:** Existing Presenton/Template V2 editor and its persisted model remain authoritative for supported editing today. The new SmartLayout role/layout pass is a pure, deterministic adapter over a **versioned, small typed metadata envelope**; it must neither silently rewrite existing DesignIR v1 nor create a separate competing global canvas. New \`DesignIR v2\` may be introduced later behind explicit migration and rollback tests, only if v1 cannot encode required semantics safely.

**Identity:** Persist stable slideId, componentId, sourceId, citationId, revision and content digest in a canonical transaction. Render geometry, text measurements, thumbnails and candidate scores are **rebuildable derived data**; never let renderer caches overwrite authoritative chart values or text.

**No-loss semantics:** A layout attempt returns \`{candidate, diagnostics, lossReceipt}\` conceptually. For hard violation (dropped data, unapproved citation mutation, invalid grid cell, unreadable min font), return a typed error and keep previous canonical slide unchanged. Unsupported interactive content remains stored with a declared export fallback.

**Concurrency:** UI spinner/agent edit mark is not a lock. A server-side commit compares \`baseRevision\`, \`workspaceId\`, \`actor\`, \`operationId\`, \`targetElementIds\`, \`proposalHash\` and authorized sources at commit time, returns conflict without mutation if stale or permission changed. Actual endpoint paths and handler signatures must be discovered before implementation; none are claimed to exist today.

## 6. Decisions after competitor REA (Elephant critique)

| Option | Decision | Why / proof needed |
|---|---|---|
| Rebuild full Beautiful.ai SmartSlides engine | **No** | Public model docs, not private executable renderer; too much scope. Implement 4 families with existing Template V2 |
| Adopt 12×12 grid schema directly into current DesignIR v1 | **No** | v1 contract too shallow and \`additionalProperties:false\`; add bounded adapter and versioned contract |
| Keep one editor vs new Fabric/Excalidraw canvas | **Keep existing Konva editor** | Verified source already has selection, transforms, tables/text and undo; new canvas creates conflicting authority |
| Import Crello Electron renderer | **No** | 2017 Electron, SSRF and query-credential risk; use current export runner |
| Replace exporter with Beautiful.ai PptxGenJS fork | **Not yet** | Benchmark 30 native PPTX cases against existing runtime; vendor fork is derivative of Brent Ely's library |
| Local segmentation/AI object grabber | **Later** | Raster sprite and model-weight rights, not a first-release source-to-deck requirement |
| 73 Smart Slide templates at once | **No** | 4 role families first, expand by measured frequency |
| Huge Knowledge/RAG system before editor polish | **No new scope** | Reuse already built P03–P09 contracts; improve source integrity only where first journey requires it |
| OpenAI/Gamma private code | **No inference** | Not publicly accessible; use public documented behaviors as benchmark specs only |

## 7. Detailed Implementation Plan

### Phase 0: exact-head baseline and source admission — **blocking**

**Read only first:** inspect PR #88 changed-file list and compare HEAD to main. Run full FastAPI pytest suite, Next.js node tests, root tests, TypeScript and production build with pinned export-core; Windows screenshot/manual journey; inspect CI and any skipped failures. Do not merge if any required check has failed or not run. Inspect security and original source notices in PR #88; no "all green" from a prior head.

**Artifacts to add only:** \`docs/designs/gomri-egm-execution-ledger-20261109.md\` (NEW); \`docs/designs/gomri-egm-qualification-matrix-20261109.csv\` (NEW). Cite exact commit SHA, command, OS, exit code, input fixture hashes, skipped tests and artifacts. PR #88 is **not** an assumption.

**Gate P0:** actual current-HEAD reproducible build and a complete 1-deck user journey, or explicit NOT READY + named blockers. Before this gate, no new layout primitives in the product.

### Phase 1: SmartLayout in existing editor — first user-visible gain

**Existing files to inspect and, only after interface discovery, change in a feature PR:**
- \`servers/nextjs/components/slide-editor/model/model.ts\` — owns existing updateComponentInUi/updateElementInUi and selection models; use as integration seam, do not replace.
- \`servers/nextjs/components/slide-editor/surface/TemplateV2KonvaSlide.tsx\` — owns visual surface rendering, no second canvas.
- \`servers/nextjs/components/slide-editor/surface/componentFrameBounds.ts\` and \`.../surface/alignmentGuides.ts\` — existing geometry helpers to test/reuse.
- \`servers/nextjs/components/slide-editor/text/text-line-height.ts\` and \`.../text/template-v2-text.ts\` — existing text measurement/wrapping; inspect Arabic/diacritics before any alternative.
- \`servers/nextjs/tests/template-v2-component-bounds.test.mjs\`, \`.../flow-layout-text-sizing.test.mjs\` — existing negative-control test homes.

**New proposed bounded files** (names may be adjusted after interface discovery; not existing API claims):
- \`servers/nextjs/lib/gomri-smart-layout/types.ts\` — semantic role, typed nodes, diagnostic and candidate interfaces;
- \`servers/nextjs/lib/gomri-smart-layout/constraints.ts\` — deterministic bounds/no-loss/no-overlap rules;
- \`servers/nextjs/lib/gomri-smart-layout/compile.ts\` — four role layouts, pure input/output and no DOM mutation;
- \`servers/nextjs/tests/gomri-smart-layout.test.mjs\` — 30 deterministic fixtures, malformed cell/incomplete item/long Arabic cases.

**Implementation grain:** start with \`headline-hero\` then \`stat-chart\`, \`comparison\`, \`timeline-process\`; each can be disabled by a feature flag and falls back to current proven editor rendering. No new database table unless unavoidable. A slide supports both manual freeform override and later smart reflow, but reflow must present the diff before it overwrites intentional user positioning.

**Gate P1:** deterministic candidates and readable UI output with zero missing semantic/citation nodes across 30 fixtures; negative controls fail when a cell is dropped, chart number changes, component moves outside bounds or font falls under readable threshold.

### Phase 2: selection-scoped AI changes, revision checks and Undo

**Existing files to inspect and minimally extend:**
- \`servers/nextjs/components/slide-editor/selection/transformSession.ts\` and \`.../model/model.ts\` for selected element paths;
- \`servers/nextjs/app/(presentation-generator)/presentation/hooks/PresentationUndoRedo.ts\` and \`servers/nextjs/store/slices/undoRedoSlice.ts\` for current snapshots, while understanding their present limitations;
- \`servers/nextjs/app/(presentation-generator)/presentation/hooks/useAutoSave.tsx\` and \`.../presentation/utils/autoSaveDiff.ts\` for snapshot/autosave conflicts;
- \`servers/fastapi/api/v2/ppt/endpoints/presentation.py\` for existing write route (inspect exact signature);
- \`contracts/v1/artifact-revision.schema.json\` for existing revision fields.

**New proposed files** (write boundaries, not proof of current APIs):
- \`servers/nextjs/lib/gomri-ai-edit/patch.ts\`: typed element patch and preview, no arbitrary HTML/deck rewrite.
- \`servers/nextjs/lib/gomri-ai-edit/verify.ts\`: source/number preservation and no-unselected-change test.
- \`servers/fastapi/gomrey/slide_edit_transaction.py\`: proposal/commit and idempotency service only if existing infrastructure lacks one, with write-time authorization.
- \`servers/nextjs/tests/gomri-ai-edit.test.mjs\` and \`servers/fastapi/tests/test_gomrey_slide_edit_transaction.py\` (NEW).

**Ninerr donor rule:** inspect the owner's exact MCP/history code and source notices; adapt only the already-qualified target selection and undo transaction slice. Do not import a second editor or make an agent bypass user API permission checks.

**Gate P2:** stale revision -> conflict, revoked role -> deny, duplicate operationId -> one effect, selected element edit does not modify sibling content, renderer failure -> prior state retained, Undo restores exact previous canonical revision. No direct free-model tool call can write to a deck outside these gates.

### Phase 3: native PowerPoint fidelity, claims and authoring journey

**Existing:** \`servers/nextjs/lib/run-bundled-presentation-export.ts\`; \`servers/nextjs/lib/template-v2-json-to-html.ts\`; \`servers/fastapi/services/export_task_service.py\`; \`servers/fastapi/tests/integration/test_presentation_generation_flow.py\`; \`contracts/v1/narrative-ir.schema.json\`; source/citation contract tests. Verify path and test ownership first.

**Candidate from PR #88:** \`servers/nextjs/tests/export-fidelity.test.mjs\` and its source-target fixtures, plus RTL and contrast lint. These files are **not present on main until qualified/merged**. Do not duplicate or assume tests cover notes.

**Work:** freeze 30 synthetic decks with exact numerical/text/chart/table/notes expectations. Generate with existing export-core, parse PPTX OOXML with a safe zip reader, re-import and measure native editability; compare against Beautiful.ai's public PptxGenJS derivative and upstream PptxGenJS in an isolated evaluator. Only admit specific changes demonstrated better on current fixtures, original notices included. Run Arabic+Latin paragraph/bullet/tabular content and speaker-note assertions. Produce a typed loss receipt for browser-only features.

**Gate P3:** no unsupported native-object claim without XML evidence; clear inventory of remaining notes/bullet/shape/chart losses; product journey prompt -> approved outline -> four-family slides -> scoped edit -> native PPTX tested. Unmet hard gate means not release-ready.

### Phase 4: constrained responsive variants, then image/animation (post-P3)

**New proposed files:** \`servers/nextjs/lib/gomri-smart-layout/format-profiles.ts\` and \`servers/nextjs/tests/gomri-responsive-variants.test.mjs\`. Start 16:9, 4:3, 1:1, 9:16 only. Derive layout from semantic roles and preserved source graph, not copying/rasterizing entire slides. Apply only if variants preserve text/claims, chart datasets, citations and font shaping; fallback to manual review where impossible.

Object Grabber, complex Lottie, MP4/GIF and marketing format ecosystem stay outside the first-release promise. A separate design/rights review is required for model weights or image licenses.

**Gate P4:** 30 decks × 4 profiles, no hard integrity loss; each unsupported visual behavior is visible in preview/receipt.

### Phase 5: competitive arena, release decision and support

Run 30 matched prompts against Gomri baseline and latest qualified candidate; when legitimate authorized competitor access exists, run a **separate** blinded Gamma/Beautiful.ai comparison with plan, date and sample metadata. Panel rates composition, reading order, narrative, source support, RTL and native PPTX editability. Record confidence intervals and dissent. Local snapshots/exports must contain synthetic materials only. Gate Windows real desktop, exact-head CI, test skip inventory, E2E and rollback, provenance/rights and zero paid/secret calls.

**Gate P5:** human review + exact source identity + regression suite + performance and privacy evidence. Product “better than Gamma” remains a **hypothesis** unless matched external tests actually support it.

## 8. Legacy P00–P16 mapping

- **Reuse now:** P00–P09 investments (provenance, gateway, jobs, IR, citations, claim validation) where real code and tests pass; only repair missing capabilities required for first journey.
- **Make customer-visible:** P10 research/outline workflow + P11 creation compiler + selected P12 agent access, in the smaller Phase 0–3 path.
- **Defer by explicit decision:** full P13 plugin marketplace, P14 enterprise collaboration/analytics, broad P15 arena expansion, cross-platform P16 GA until flagship decks pass.
- **Keep existing \`docs/MASTER_PLAN.md\` and \`docs/ARCHITECTURE.md\` authoritative for recorded historical commitments;** this document is a proposed fast-track amendment. No silent overwrite, and no misleading rebrand where old Gomrey package/storage IDs still exist.

## 9. Security and failure table

| Failure / threat | Behavior / test |
|---|---|
| Untrusted PDF/web includes instruction to leak secrets | Treat source as data; restricted retrieval scope, no tool execution from content |
| Concurrent agent and human edit | Revision conflict and proposed merge, never last-write-wins silent loss |
| Agent has stale workspace membership | Revalidate role at commit and export |
| Render creates a perfect PNG but drops data | Inspect canonical IDs/chart series and OOXML; fail native-export gate |
| Chart numbers or reference citations change during restyle | Reject layout proposal and preserve old version |
| Imported layout has overlapping/invalid cells | Fail closed or return repair preview, not silent deletion |
| Arabic font coverage or bidi shaping fails | Flag per exported medium with exact fixture/font/OS |
| Source file or asset inaccessible offline | Explicit degraded/blocked state; don't invent missing evidence |
| Optional cloud provider unavailable or quota exhausted | Deterministic local path / explicit skipped generation, never paid fallback |
| Old donor renderer accepts internal URLs | Never run 2017 Crello Electron renderer; reject SSRF and remote scripts |
| AI retried after crash | Operation idempotency and durable receipts; no duplicate slides/decks |

## 10. EGM Goldfish review request and remaining unknowns

**Reviewers must receive this document alone plus explicit source links and zero previous discussion; record each fresh-session model and provider.** Official EGM personas: \`zoom_out\`, \`comprehension\`, \`design_critic\`, \`structural\`, \`style\`, \`implementation_readiness\` and \`codebase_details\`. A self-review in the Elephant context **does not count** as Goldfish.

Questions reviewers must challenge:
1. Is a new typed SmartLayout compiler justified, or can one more bounded Template V2 helper meet G2?
2. Which component IDs and revisions are truly stable in today's persisted model? Does auto-save overwrite proposed backend conflict semantics?
3. What exact source/method contracts do \`model.ts\` and FastAPI v2 expose? Must Phase 2 adapt their current workflow before adding a transaction service?
4. Does the existing bundled exporter even accept source speaker notes? Which losses are impossible without a new export model?
5. Is 30-deck × 4-format test scope appropriate for first user-visible slice, and how do we measure blind preference without expensive accounts?
6. Is the plan self-contained, legally admissible, privacy-preserving and deployable at zero hidden cloud cost?
7. Are reviewers being asked to certify interfaces that are only guessed from filenames?

**No Goldfish verdict is claimed by this Elephant draft.** Review should produce blocking/major/minor findings with exact file/source references and verification status, resolve critical items, then declare GO/CONDITIONAL/NO-GO for specific implementation grains.

## References and source provenance

- Google EGM official project: https://github.com/google/elephant-goldfish-model ; local pinned EGM source was previously checked at 403d888, Apache-2.0.
- Existing Gomri current: \`docs/MASTER_PLAN.md\`, \`docs/ARCHITECTURE.md\`, \`docs/template-v2.md\` on main @ 5f299a7.
- PR #88 integration: https://github.com/TheHalfMoon/Gomri/pull/88 (NOT MERGED).
- GPT Slides REA: PR #89; Beautiful.ai source REA: PR #90; VistaCreate source REA: PR #91; Craft Anything evidence REA: PR #92 (all DRAFT, NOT MERGED).
- Beautiful.ai public official plugin: https://github.com/beautifulai/claude-plugin ; public PptxGenJS derivative: https://github.com/beautifulai/PptxGenJS
- Gamma public API client: https://github.com/gamma-app/n8n-nodes-gamma
- Crello font metrics code: https://github.com/crello/font-metrics-sizing
- Research files in PR-specific branches are *references*, not files on this main-based planning branch.
