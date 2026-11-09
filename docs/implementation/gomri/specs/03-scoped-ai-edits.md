# S03 — Trusted Selection-Scoped AI Editing, CAS and Undo

**Goal:** A user selects an existing slide object, requests a bounded AI text/style/layout edit, previews a diff, commits it exactly once, and can undo it without overwriting another user's newer change. **Accountable:** R2; supporting R3/R1; independently reviewed by R8/R7. **Depends on:** S00 owner/race evidence, S01 source validation. Required before any S02 preview becomes persistent.

## Actual authority and existing write path

- Next.js \`useAutoSave.tsx\` and \`autoSaveDiff.ts\` compute local snapshots and send full-deck or slide PATCH through \`services/api/presentation-generation.ts\`.
- FastAPI current route is **v1** \`servers/fastapi/api/v1/ppt/endpoints/presentation.py\` (\`PATCH /update\`, \`PATCH /slide_update\`), not a speculative v2 route.
- FastAPI \`api/middlewares.py\` authenticates HTTP and populates owner context; \`services/database.py\` applies owner-scoped SQLAlchemy SELECT hooks for SlideModel. **No security vulnerability is proven solely from missing explicit owner comparison inside the PATCH handler**.
- Current \`SlideModel\` stores \`speaker_note\` and UI type carries it. Redux Undo/Redo history is local; current API payload lacks observed baseRevision and idempotency.
- \`contracts/v1/artifact-revision.schema.json\` describes revisions and idempotency, but not proof the legacy PATCH enforces them.

## Copy-first bounded donors

1. Ninerr \`packages/mcp-protocol/src/authorization.mjs\` @ \`b8229a9c9e093026e0ca967bbe65dae285c49077\` for **tool classification and write authorization patterns**; its \`@ninerr/collaboration\` and \`agent-runtime\` imports must be replaced by Gomri server auth/adapters, not copied wholesale.
2. Ninerr \`packages/history/src/index.mjs\` for typed transactions, \`createTransaction\`, \`getAffectedNodeIds\`, \`applyTransaction\` with \`enforceBaseRevision\`, and Undo/Redo. Map Ninerr graph node IDs to Gomri slide/component stable IDs via a **validated adapter**. Ninerr history alone cannot substitute for server atomic DB CAS.
3. Ninerr \`packages/studio-host/src/mcp.ts\` is a source **reference** for selection and confirmation; do not copy the full daemon/HTTP host or credentials into Gomri.

## API and transaction semantics to implement

\`\`\`text
POST /slides/{slideId}/edit-proposals (or verified existing route adapter)
  identity from session, not request body
  candidate targets = selected currently visible IDs (server recomputed)
  user prompt as untrusted text + allowlisted operation type
  baseRevision and idempotency operationId
  -> no persistent mutation; return typed patch + before/after + source checks

POST /slides/{slideId}/edit-commit
  authenticate server-side actor/workspace/tenant
  reload current canonical content and authorized target/source IDs
  verify patch schema/operationId/hash, numeric/source-preserve invariants
  atomic UPDATE .. WHERE id=slideId AND revision=baseRevision AND owner...
  if row count=1: persist content + monotonically incremented revision + journal event
  otherwise: 409 conflict, NO content mutation; return safe summary of current rev
\`\`\`

Path names **proposal only**; discover current FastAPI router conventions and DB model first. Prefer **minimal patch to actual v1 routes** and reuse current persistence. Do not introduce new transaction microservice without an ADR/proven need. Ordinary human autosave, slide reorder, speaker-note update and AI edit must all honor compatible revision/CAS rules; adding a new safe AI endpoint while leaving unsafe ordinary PATCH is not enough.

Undo creates a **new** revision with previous canonical content, never deletes/reuses an old revision; a stale client cannot undo over a newer edit. Keep a single atomic history transaction for a multi-object agent change; make human confirmation required for destructive operations.

## Negative controls (all require real disposable SQLAlchemy DB)

- ACT-01: owner A modifies A's selected text: one patch and one revision, unchanged sibling shapes.
- ACT-02: owner A attempts B's slide by valid ID: 403/404; B's source digest unchanged.
- ACT-03: forged actor/workspace in body is ignored or rejected, never elevated.
- ACT-04: simultaneous same-base-revision writers A1/A2: exactly one success, one conflict; no silent last-write-wins.
- ACT-05: full-deck reorder concurrent with selected slide edit: no orphaned slide, stable order or explicit conflict.
- ACT-06: retry same operationId: one canonical effect and one journal record; distinct hash with same operationId denied.
- ACT-07: role revoked between proposal and commit: denied and no export lease leaked.
- ACT-08: Undo from revision N+1 writes N+2 with old content; concurrent N+1 writes conflicted.
- ACT-09: model tries to rewrite a numeric figure/citation in preserve-facts mode: rejected before commit.
- ACT-10: source message contains prompt-injection or script/HTML: only data, no arbitrary network/tool calls.
- ACT-11: exporter worker/downstream queue fails after preview: canonical data remains correct; retries are safe.
- ACT-12: no external model configured: deterministic manual/fixture patch and validation path still work.

## Write boundaries

- Backend: actual \`servers/fastapi/api/v1/ppt/endpoints/presentation.py\`, \`services/database.py\`, owning SQL models and tests only as required by design review; no other ownership law changes.
- Frontend: current autosave, editor selection adapter and Redux history; preserve existing state names until migrated through tests. New \`gomri-ai-edit\` package **only if** narrow adapter is justified.
- Test homes: existing \`servers/fastapi/tests/unit/test_presentation_slide_update_api.py\` (mock tests), plus new isolated real-DB integration cases; \`servers/nextjs/tests/presentation-autosave.test.mjs\`; separate explicit agent-scoped tests.
- **Do not change global auth-disabled desktop behavior** as an accidental fix; document single-user loopback threat model separately.

**Exit:** independent R8 + Alibaba-reviewed verified code at exact head, all 12 controls PASS including real DB and client/autosave paths. **Hard stop:** any unauthorized mutation, lost claim, unbounded provider call, silent conflict, incompatible revision migration, or tests running against user DB. **Rollback:** feature flag disables agent writes; prior revisions remain readable.
