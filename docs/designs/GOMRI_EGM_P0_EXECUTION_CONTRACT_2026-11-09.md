# Gomri EGM — Authoritative P0 Execution Contract After Goldfish Re-Review

**Status:** PROPOSED, CONDITIONAL; **P0 planning and isolated qualification ONLY.** Date: 2026-11-09. Baseline: TheHalfMoon/Gomri main @ \`5f299a7a6174ad3a1180f827778db5f4400a4d71\`.

This contract replaces any conflicting permission or timing sentence in the [converged EGM plan](GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md). It responds to the [post-fix Goldfish Zoom Out](reviews/2026-11-09/goldfish-postfix-zoom-out.md), which again said **CONDITIONAL / P0 only**. This is an EGM-inspired independently reviewed plan, **not full official EGM certification**. No changes to running Gomri or canonical user content are authorized by this document.

## v4 verification and isolation addendum

**P0a source evidence files now exist:**
- [P0a route/symbol/owner matrix](evidence/P0A_ROUTE_SYMBOL_MATRIX.md).
- [P0a speaker-notes/export map](evidence/P0A_EXPORT_NOTES_MAP.md).
- [P0a exact PR head baseline](evidence/P0A_PR_BASELINE.md).

**Source correction:** FastAPI has an actual authentication middleware that sets a user/owner ContextVar and a SQLAlchemy owner-filtering SELECT hook covering SlideModel. This supports authenticated owner isolation in the code path; it does not by itself establish an executed cross-owner PATCH denial test. The dedicated authenticated A/B write check remains a P0b test. Existing SlideModel and the UI type also have speaker_note; native PPTX preservation remains untested. The Next.js export/download routes already authenticate and constrain output paths; verify end-to-end requested-presentation access and revocation rather than asserting no protection.

**P0b may not run until the [disposable environment and permissions contract](GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md) passes preflight.** Explicitly separate scratch source worktree, temp database, two synthetic identities, storage/queues, ports, provider credentials/egress and cleanup. Missing isolation means BLOCKED, never permission to attach to the user's existing app. P1 preview code is **not** part of P0b.

**Independent Goldfish Implementation Readiness on v3** returned P0a GO, P0b CONDITIONAL, P1/P2 NO-GO; report at [Implementation Readiness v3](reviews/2026-11-09/goldfish-implementation-readiness-v3.md). It did not inspect this addendum or run tests; v4 remains Draft until an additional independently reviewed implementation gate.

## A. Definitions and prohibited work

**P0a — Read-only code/contract discovery.** Inspect source, metadata, routes, database models, existing tests, issue/PR status, real schema and exporter call graphs. Write only research/evidence documents in the planning branch. No code modification, schema migration, dependency install, product build, UI experiment or runtime write test is in P0a.

**P0b — Isolated baseline qualification, gated by the separate isolation contract.** On disposable synthetic test data and a disposable/isolated database, run existing test/build/smoke commands and controlled negative tests. The only permitted writes are to disposable test fixtures/artifacts and test infrastructure, never real user presentations or production data. No shipping feature code, persisted SmartLayout, agent edit endpoint, feature activation, deployment, main merge, payment or cloud/model expenditure. If required isolated test DB, runtime or access is unavailable, mark the particular check **BLOCKED**, not PASS.

**P1 — Preview-only layout experiment (not P0).** May begin *only after* P0b evidence and an explicit per-grain design decision. It is not authorized by P0a/P0b. One 16:9 \`headline-hero\` fixture in existing Template V2 without persistence/auto-save; no new schema or engine before a small-helper comparison. Visual/geometry tests belong to P1 and should not depend on P3 exporter fixes.

**P2 — Canonical write safety and selection-scoped edits.** Requires implementation plan and test-backed enforcement of server authorization, atomic revision/CAS and idempotency **for every writer**, including human auto-save and deck reorder. No production agent or SmartLayout writes without this gate.

**P3 — Native export/reimport fidelity.** Actual PowerPoint OOXML semantics, bounded archive parsing, shape/notes mapping, font/RTL and per-object downgrade receipts. First release may be approved only after P2 and P3 pass.

**P4/P5 (later):** Multi-format adaptive resize, animation/segmentation enhancements, and external head-to-head arena. These are neither P0 tasks nor blockers for the first source-to-PPTX journey.

**Strict sequence:** P0a -> P0b -> decision -> P1 preview -> P2 safe writes -> P3 qualified export. P4/P5 only afterward. A failing P0b safety test creates a specific P2 blocker, not permission to bypass the test.

## B. Exact source truth to verify in P0a

- Existing editor: \`servers/nextjs/components/slide-editor/model/model.ts\`, \`surface/TemplateV2KonvaSlide.tsx\`, \`selection/transformSession.ts\`. Verify exact public function signatures and stable component/slide identity. Do **not** assume a 12×12 grid or a new DesignIR v2 is already supported.
- Current auto-save: \`servers/nextjs/app/(presentation-generator)/presentation/hooks/useAutoSave.tsx\`, \`utils/autoSaveDiff.ts\`. It compares local JSON fingerprints, serializes writes *within one hook* and chooses full-deck vs per-slide PATCH. These are not evidence of cross-client conflict resolution.
- API transport: \`servers/nextjs/app/(presentation-generator)/services/api/presentation-generation.ts\` sends \`PATCH /api/v1/ppt/presentation/update\` and \`PATCH /api/v1/ppt/presentation/slide_update\`; current shown request body lacks \`If-Match\`, \`baseRevision\` and \`operationId\`.
- Actual backend handlers: \`servers/fastapi/api/v1/ppt/endpoints/presentation.py\`: \`update_presentation\` / \`update_presentation_slide\` (around 2471/2529 on this baseline). Slide update validates UUIDs, presentation equality, then updates/commits. **Explicit owner check / atomic revision compare are not visible in that handler**. This is not proof they are absent at a deeper DB/session policy layer. Cross-owner safety is **UNVERIFIED**.
- Redux \`servers/nextjs/store/slices/undoRedoSlice.ts\` and \`presentation/hooks/PresentationUndoRedo.ts\` represent local history, not proof of durable revisioned Undo.
- \`contracts/v1/artifact-revision.schema.json\` includes revision/idempotency fields but does not prove the current v1 API enforces them.
- Speaker-note source, storage, export and reimport identity: **UNKNOWN** until route/model/OOXML trace.
- Export authorization: inspect access at **enqueue, execution, retrieval and artifact download**, not only at the UI button.
- PR #88 (\`d4362c6d968d2746d499630d8498d3111c98c90b\` reported) and research PRs #89–#92 are **unmerged**. Re-fetch exact heads before evaluation. Never assume PR tests ran on the current head.

### P0a outputs and exit

\`docs/designs/evidence/P0A_ROUTE_SYMBOL_MATRIX.md\` — source file, function signature, request payload, authentication/owner provenance, DB query boundary, changed model, current test path and **VERIFIED or UNVERIFIED** status.

\`docs/designs/evidence/P0A_EXPORT_NOTES_MAP.md\` — speaker notes (if any), export-core runtime identity, original source component IDs, exact OOXML mapping and download authorization, with \`UNKNOWN\` where unavailable.

\`docs/designs/evidence/P0A_PR_BASELINE.md\` — current main/PR #88 exact commits, CI status and test coverage from actual records. Include fallback to main for P1 *only after* a separate decision.

**P0a preliminary outputs:** all three specified evidence documents now exist, with source verification and remaining unknowns named. Independent acceptance remains open. Code inspection is not a runtime test pass.

## C. P0b isolated qualification: scope, outcomes, failure criteria

Use an isolated account/tenant/workspace pair and disposable local database (or documented equivalent test fixtures). The test harness must not send real user content to external model APIs. Capture command, current SHA, OS, dependencies, process exit, artifacts and skipped cases.

| Test ID | Exact negative/positive scenario | Expected safety behavior | If not satisfied |
|---|---|---|---|
| P0B-OWN-01 | Synthetic owner A tries to PATCH owner B's valid slide UUID | 403 or privacy-preserving 404; B's data unchanged | BLOCKER for P2; investigate guards before claiming vulnerability |
| P0B-OWN-02 | Forged \`author_principal_id\` / foreign workspace in body | Request identity cannot replace trusted server identity | BLOCKER for P2 |
| P0B-RACE-01 | Clients A1/A2 edit same revision; stagger writes | Version conflict or explicit merge, never silently overwrite | BLOCKER for P2 if existing route is last-write-wins |
| P0B-ORDER-01 | Reorder full deck concurrent with single-slide PATCH | No orphan/missing slide; if unsafe, fail with conflict | BLOCKER for P2 |
| P0B-RETRY-01 | Replay same agent operation ID after delayed acknowledgment | One canonical effect or explicit unsupported state | Document missing capability; implement before AI writes |
| P0B-UNDO-01 | Local undo while autosave request is outstanding | No silent older-snapshot overwrite; if unsafe, preserve reproducible failing fixture | BLOCKER for P2 |
| P0B-ACCESS-01 | Revoke read/export role between export enqueue and download | Inaccessible artifact to revoked principal | BLOCKER for P3 |
| P0B-PR88-01 | Run root/Next.js/FastAPI/TypeScript/build/export-fidelity at exact PR #88 head | Exact exits, skips, failure evidence; no assumed all-green | Candidate NOT READY if required check fails |
| P0B-UI-01 | Full synthetic 8–12 slide journey on isolated Windows app | Record actual screenshots and native editable export | NOT READY if blocked/unverified |

**These are planned tests, NOT executed passes.** Before each test, meet all preflight conditions in the [P0b isolation contract](GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md). Test failures are evidence: do not "fix" by broad refactoring or silently changing application code during P0b. An appropriate next engineering PR would add minimal failing negative-control fixtures and a separate scoped repair.

**P0b exit:** runnable case receipts + authenticated test isolation + a precise **GO / CONDITIONAL / NO-GO** per implementation grain. It is acceptable to conclude **NOT READY**. No P1 work may begin simply because a test script was launched.

## D. Remaining phase decisions (no duplicate product engine)

1. **P1 preview-only, eight 16:9 fixtures:** one \`headline-hero\` layout helper in existing Template V2; verify component IDs, chart values, citations, no overlaps and Arabic readability with in-memory geometry/visual tests. P1 does **not** require P3's OOXML round-trip.
2. **P2 safe commits:** first implement the smallest v1 route repair whose necessity P0b proved. Derive actor, tenant and workspace server-side; recompute proposal hash/targets; CAS must be a single atomic DB transaction; all human/agent/reorder write paths must enforce it. Undo appends new revision N+2, never rewrites N. Agent preview cannot bypass policy. Do **not** assume a new \`slide_edit_transaction.py\` is required.
3. **P3 native editable export:** begin with eight fixtures then expand to 30; test actual OOXML objects, notes and identity mapping. A parser that accepts arbitrary OOXML must bound archive size/decompression and reject unsafe relationships. Release receipts enumerate every unsupported fallback by component ID; never advertise a flattened PNG as an editable chart.
4. **P4 later responsive format:** derive 4:3, 1:1, 9:16 variants only after qualified single-format edit/export; avoid 30×4 initial fixtures.
5. **P5 optional external benchmarks:** competitor access and credits cannot be a release gate; if available, evaluate 30 matched synthetic prompts and blind design judgments separately. **No superiority claim until measured**.

## E. Reviewer and decision authority

Initial independent reviewer notes:
- [Goldfish Zoom Out](reviews/2026-11-09/goldfish-zoom-out.md) — CONDITIONAL.
- [Goldfish Design Critic](reviews/2026-11-09/goldfish-design-critic.md) — CONDITIONAL.
- [Post-fix Goldfish Zoom Out](reviews/2026-11-09/goldfish-postfix-zoom-out.md) — CONDITIONAL; demanded this P0 split, no P1 permission and no 8-vs-30 ambiguity.
- [P0 code audit](GOMRI_EGM_P0_WRITE_PATH_AUDIT_2026-11-09.md) — read-only verification, not an external model verdict.

These were **fresh OpenCode sessions using EGM review perspectives**, not a complete official EGM five-stage orchestrator. No implementation-readiness approval is claimed. Require an independent post-P0 review of actual test results and migration/write plan before production changes.

**Decision today: CONDITIONAL — P0 ONLY.** No source is claimed shipped, no model quota/paid provider used in plan execution, and main is unchanged.
