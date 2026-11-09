# EGM P0 Source Audit — Current Gomri Slide Save, Revision and Undo Boundaries

**Date:** 2026-11-09. **Inspected source:** TheHalfMoon/Gomri main @ 5f299a7a6174ad3a1180f827778db5f4400a4d71. **Status:** READ-ONLY SOURCE INSPECTION. This report is a prerequisite for any new AI slide-edit transaction; it is not a completed security test or proof of exploitation. No production code changed.

## Source correction from P0a extended inspection (2026-11-09)

**Do not interpret missing owner comparison in the slide handler as a proven security gap.** Further direct inspection found actual defenses already present in main:

- services/database.py installs a SQLAlchemy Session do_orm_execute SELECT hook applying with_loader_criteria on SlideModel and other owner-scoped models when get_current_owner_id() is set; new owned rows are stamped with owner_id.
- api/middlewares.py SessionAuthMiddleware requires authenticated API access except specifically public paths, resolves JWT/API principal, and sets current owner ID in ContextVar for the request. api/main.py installs this middleware. The deliberate DISABLE_AUTH desktop single-user mode bypasses this context, so its threat model differs.
- tests/unit/test_owner_isolation.py already checks ORM SELECT owner isolation for presentations/templates, not this precise slide PATCH endpoint. tests/unit/test_presentation_slide_update_api.py tests changing speaker_note and UUID/presentation checks with FakeAsyncSession.
- models/sql/slide.py and the browser Slide type already define speaker_note. The remaining unknown is PPTX notes OOXML/reimport, not whether Gomri models notes.
- Next.js app/api/export-presentation/route.ts authenticates and moves exports under per-user paths; app/api/export-presentation/file/route.ts checks authentication, user directory ownership, realpath containment and traversal. These are **real existing controls**. Further tests should validate presentation ID access, revocation and unexpected runtime modes, not presume exports are unauthenticated.

**Revised risk statement:** cross-owner write bypass is **UNVERIFIED**, with concrete source-level protection, and needs an isolated authenticated end-to-end test. A separate concurrency/atomic revision-CAS gap remains **not demonstrated to be solved by the existing request contract**; run two-client tests before claiming last-write-wins. No live exploit or security incident was observed.

See [verified P0a route map](evidence/P0A_ROUTE_SYMBOL_MATRIX.md), [export notes map](evidence/P0A_EXPORT_NOTES_MAP.md), and [PR heads](evidence/P0A_PR_BASELINE.md).

## 1. Verified current flow and concrete source paths

1. \`servers/nextjs/app/(presentation-generator)/presentation/hooks/useAutoSave.tsx\` maintains a locally acknowledged snapshot, serializes network saves with a per-hook \`isSavingRef\`, debounces edits, and differentiates structural deck changes vs changed slides. It records local history via \`addToHistory\`.
2. \`servers/nextjs/app/(presentation-generator)/presentation/utils/autoSaveDiff.ts\` creates \`slideFingerprints\` using \`JSON.stringify\`, checks IDs/order/indices, and decides \`structuralChange\`, \`changedSlides\`, and \`metadataChanged\`. This fingerprint is an **in-memory diff optimization**; it is not cryptographic canonical revision validation or an inter-client conflict detector.
3. For structural changes, \`useAutoSave.tsx\` calls \`PresentationGenerationApi.updatePresentationContent(JSON.stringify(createPresentationUpdatePayload(data)))\`; for isolated slide changes it calls \`PresentationGenerationApi.updatePresentationSlide(slide)\` in a loop, updating the local acknowledged fingerprint after each success.
4. \`servers/nextjs/app/(presentation-generator)/services/api/presentation-generation.ts\` sends a \`PATCH /api/v1/ppt/presentation/update\` with id/title/n_slides/slides and a \`PATCH /api/v1/ppt/presentation/slide_update\` with \`{ slide }\`. The shown request builders **do not add a base revision, If-Match precondition or operation idempotency key**.
5. \`servers/fastapi/api/v1/ppt/endpoints/presentation.py\` defines \`update_presentation\` around line 2471 and \`update_presentation_slide\` around 2529. The latter validates UUIDs, retrieves the stored slide by \`sql_session.get(SlideModel, slide_id)\`, checks presentation ID equality, applies \`sqlmodel_update\` excluding id/presentation/index, and commits. **No explicit revision compare-and-swap or owner comparison appears in that handler snippet.** Global/session-level authorization may still exist: **cross-owner exposure is UNVERIFIED and must be tested rather than asserted**.
6. \`servers/nextjs/store/slices/undoRedoSlice.ts\` and \`servers/nextjs/app/(presentation-generator)/presentation/hooks/PresentationUndoRedo.ts\` implement local Redux slide-snapshot Undo/Redo. They do not by themselves establish a durable server-side agent change journal or merge-compatible revisioned undo.
7. \`contracts/v1/artifact-revision.schema.json\` defines revision, parent_revision, content_digest, workspace, principal and idempotency fields; this contract existence is **not** proof the above legacy v1 slide route enforces them.
8. \`servers/fastapi/api/v2/ppt/endpoints/presentation.py\` primarily concerns generation/Smart presentation operations in the inspected portions; it is **not** the v1 route actually called by the autosave hook.

## 2. Main architecture risk identified

The existing front end's \`isSavingRef\` serializes network changes **within one hook instance** but does not coordinate multiple clients or an AI agent. The versionless PATCH body and update-then-commit handler suggest potential last-writer-wins behavior if two clients change the same slide, but a controlled concurrency test is required to confirm the complete stack. There is no proof of a shared atomic revision or write-time permission check from the inspected paths alone.

**Therefore Phase 2 from the Elephant draft is BLOCKED until a server write-path trace and negative tests establish:**
- cross-owner and cross-workspace write denial, even with a valid foreign slide UUID;
- stale base revision conflict handling; if absent, introduce it before allowing AI writes;
- duplicate request/idempotency semantics for retried agent operations;
- atomic handling of structural deck reorder vs per-slide patch, including no missing slides;
- local Undo/Redo after interrupted or concurrent autosave;
- permission revoked between preview and commit;
- migration/provenance compatibility with ArtifactRevision v1 and SourceIR citations.

These are explicit proposed tests, **not successful test results**.

## 3. Narrowest safe implementation path

**Do not build a new \`slide_edit_transaction.py\` until all of the above are mapped.** First add read-only tests to exercise current routes and capture status codes, ownership and concurrency. Then choose the smallest fix:

1. If an existing lower-layer owner filter or optimistic revision check exists, reuse it and prove it at API boundaries.
2. Otherwise introduce a document/slide **server-authoritative** base revision precondition at the v1 route boundary, with write-time owner/workspace verification and an idempotency key, keeping canonical content and revision mutation inside one database transaction. Reject stale edits (409/412 depending contract), return current revision, never silently overwrite.
3. Only after a typed API patch is accepted, expose agent target selection, preview and Undo using existing Redux tools plus a durable receipt. The UI spinner is not a lock.
4. Keep backwards compatibility for ordinary human autosave by explicitly defining clients that do not yet send revisions. Avoid permanently allowing unversioned writes to bypass the agent path.

**New exact implementation files are deliberately NOT approved by this audit.** The first implementation grain is negative-control tests plus write-route contract discovery, not a parallel transaction microservice.

## 4. Concrete test homes already present

- \`servers/nextjs/tests/presentation-autosave.test.mjs\` — verify structural save, changed slide updates and interrupted save recovery.
- \`servers/fastapi/tests/unit/test_presentation_slide_update_api.py\` — add **only after verifying current test fixtures**; write cross-owner, stale version, conflicting client and retry tests.
- \`servers/fastapi/tests/test_presentation_generation_api.py\` — verify deck update handling, identity and ordering.
- \`servers/nextjs/app/(presentation-generator)/presentation/hooks/useAutoSave.tsx\` + \`.../utils/autoSaveDiff.ts\` — observe precise payloads; do not change before tests.
- \`servers/fastapi/api/v1/ppt/endpoints/presentation.py\` — actual v1 route to examine, not a speculative v2 write endpoint.

## 5. Proposed Phase-0 exit evidence

| Artifact | Acceptance |
|---|---|
| Route and authorization map | Exact request fields, route, owner resolution, session filters and DB identity; no guesses |
| CAS/no-CAS proof | Two-client synthetic concurrent edit, exact final revision/content and status; failing negative test if unsafe |
| Autosave conflict trace | Local acknowledged fingerprint, interleaved PATCH, user-visible conflict or data-loss result |
| Undo source audit | Redux history and persisted revision contract traced; fail if Undo silently overwrites others |
| PR #88 qualification record | Exact head CI, NextJS, FastAPI, UI and export tests or named blockers |
| Rights and provider budget | Original notices/assets verified; deterministic local path and no accidental paid calls |

**Current EGM status: BLOCKED for autonomous production AI slide edits, P0 source/negative-test work allowed.** This is a **source-based engineering recommendation**, not the independent Goldfish reviewer verdict.

## 6. How this updates the fast-track plan

- Replace the draft's implicit "Phase 2 new transaction service" bias with conditional **reuse-or-smallest-safe-patch** based on tested legacy v1 routes.
- Require actual main-vs-PR #88 resolution before design/schema migrations.
- Keep first \`headline-hero\` layout spike ephemeral with the existing Konva/Template V2 editor; don't create a second source graph.
- Stage initial test corpus: 8 fixture deck templates to prove one journey, then expand to 30 only after P3.
- Measure current PPTX native-object retention and visual-fit baseline **before setting numerical targets**.

**References:** exact main-source paths above, EGM official Zoom Out review captured at \`docs/designs/reviews/2026-11-09/goldfish-zoom-out.md\`; draft \`docs/designs/GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md\`.
