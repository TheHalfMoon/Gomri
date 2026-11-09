# P0a — Current Gomri Route and Symbol Map (Source-Verified)

**Date:** 2026-11-09. **Read-only inspection only.** Baseline: TheHalfMoon/Gomri main `5f299a7a6174ad3a1180f827778db5f4400a4d71`. This is a source map, not execution or proof of vulnerability. Reviewer findings were independent text critiques; this map was prepared by direct GitHub inspection.

## Verified code paths

| Layer | Source path | Symbol | Behavior | Evidence confidence / gap |
|---|---|---|---|---|
| UI auto-save | servers/nextjs/app/(presentation-generator)/presentation/hooks/useAutoSave.tsx | saveLatest -> updatePresentationContent (structural), updatePresentationSlide (individual) | Browser local fingerprint; per-hook in-flight serialization | Observed main code; no inter-client CAS in request |
| UI diff | servers/nextjs/app/(presentation-generator)/presentation/utils/autoSaveDiff.ts | getAutoSaveChanges, createAutoSaveSnapshot, fingerprintValue | Serialized JSON fingerprint; slide ID/order/index metadata | Observed main code; not server revision |
| UI transport | servers/nextjs/app/(presentation-generator)/services/api/presentation-generation.ts | updatePresentationContent, updatePresentationSlide | PATCH /api/v1/ppt/presentation/update and /slide_update; body {slide} for latter | Observed main code; no baseRevision/If-Match/idempotency in builders |
| FastAPI route | servers/fastapi/api/v1/ppt/endpoints/presentation.py | update_presentation, update_presentation_slide | UUID guard; presentation equals ID; sql_session.get then sqlmodel_update/commit | Observed; read ORM owner scope applies in logged-in context; no explicit revision CAS in handler |
| Owner context middleware | servers/fastapi/api/middlewares.py | SessionAuthMiddleware.dispatch | JWT/API key principal; set_current_owner_id; auth required for /api paths | Observed; DISABLE_AUTH bypasses principal for desktop |
| ORM owner filter | servers/fastapi/services/database.py | _scope_owned_selects, _stamp_new_owned_rows | SQLAlchemy Session do_orm_execute installs with_loader_criteria for SlideModel, PresentationModel etc on SELECTs when owner context set; new rows stamped | Observed main code; test should verify exact slide update and no bypasses |
| Slide SQL model | servers/fastapi/models/sql/slide.py | SlideModel | id, owner_id, presentation, content, ui, speaker_note, properties etc | Observed; no slide revision column in inspected model |
| Undo | servers/nextjs/store/slices/undoRedoSlice.ts | undo, redo, addToHistory | Local Redux slide snapshot history | Observed; not by itself durable server-side undo |
| ArtifactRevision v1 | contracts/v1/artifact-revision.schema.json | revision, parent_revision, content_digest, idempotency_key | Contract only | Observed; not proven wired into v1 slide endpoint |
| Native export request | servers/nextjs/app/api/export-presentation/route.ts | POST, runBundledPresentationExport, moveExportIntoOwnerDirectory | Authenticated status; formats pdf/pptx; owner export subdir for user | Observed; verify downstream ID authorization and lifecycle |
| Native export download | servers/nextjs/app/api/export-presentation/file/route.ts | GET, getSafeExportName | Requires authentication; rejects traversal; user scoped to users/{user_id}; fs.realpath containment | Observed; tests still needed for symlink/role revocation and auth-disabled desktop |
| Generation/export worker | servers/nextjs/lib/run-bundled-presentation-export.ts | runBundledPresentationExport | Runs bundled export package | Observed; actual OOXML notes preservation unverified |

## Important correction to the earlier EGM audit

The absence of an explicit owner comparison within update_presentation_slide **does not prove missing ownership protection**. Source inspection found **two actual protections**:

1. SessionAuthMiddleware at servers/fastapi/api/middlewares.py protects API routes in authenticated mode and binds a resolved principal as get_current_owner_id for the request.
2. A SQLAlchemy Session do_orm_execute hook in services/database.py adds with_loader_criteria for owned SELECTs, including **SlideModel**, if a current owner is set. Thus a normal ORM SELECT for a foreign-owned slide should be filtered, including when retrieved by ID through the ORM's SELECT path.

This is important evidence but **not a substitute for a real cross-owner PATCH test**. The authentication-disabled local desktop path intentionally runs without a principal, and the filter is skipped if owner_id is None or if an execution option bypasses it. The owner filter code alone does not establish an atomic revision check. Do not publish a security-vulnerability claim based only on handler text.

Existing tests found but NOT re-executed in this task:
- servers/fastapi/tests/unit/test_owner_isolation.py tests ORM-owned SELECT isolation for PresentationModel and TemplateV2; it does **not** directly exercise the SlideModel PATCH route.
- servers/fastapi/tests/unit/test_session_auth_middleware.py tests selected auth-gating paths and authentication-disabled proxy behavior.
- servers/fastapi/tests/unit/test_presentation_slide_update_api.py tests mutable fields including speaker_note, UUID validity, unknown slides and presentation mismatch with FakeAsyncSession; does **not** prove actual DB cross-user PATCH protection or stale concurrency handling.
- servers/nextjs/tests/presentation-autosave.test.mjs exists as a test home; coverage of cross-client concurrency is not established.

## P0a open questions to resolve with source, not guesses

1. Does SessionAuthMiddleware context reach every route, background task and SQLAlchemy get() branch as expected? Is any owner-scoping bypass legitimate in authenticated mode? The executed query and route test are P0b.
2. Do the legacy PATCH handlers serialize writes atomically with a shared document revision? No request revision fields are visible, and current SlideModel lacks an observed revision column. **CAS is NOT VERIFIED**, but race tests are still required before asserting last-write-wins.
3. Can a structural whole-deck update race a slide-level update; what does the current database transaction do?
4. Are user-scoped exports tied to the authorized presentation ID at initiation and at delivery, including after a role change? Authentication and path containment already exist; project/asset authorization requires isolated tests.
5. How are speaker_note and chart/table/native element IDs carried from SlideModel through bundled export-core and back into import? Source model contains the field, but end-to-end PPTX notes fidelity remains UNVERIFIED.
6. Does DISABLE_AUTH desktop mode have a documented trusted-local loopback boundary? Treat desktop as single-user threat model, not a substitute for multi-user auth.

## P0a exit receipts

**VERIFIED source:** Route names, UI request bodies, middleware owner context, ORM owner SELECT policy, model field names, existing relevant unit test files and export download path guards.

**UNVERIFIED execution:** Exact-owner security at PATCH, concurrent write conflicts, idempotency, export-time revocation behavior, notes OOXML fidelity, test results on current exact heads.

**Next stage:** P0b isolated synthetic tests, not production code modification. See [controlling P0 contract](../GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md) and [source audit](../GOMRI_EGM_P0_WRITE_PATH_AUDIT_2026-11-09.md).
