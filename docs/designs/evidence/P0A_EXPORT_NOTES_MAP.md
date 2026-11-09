# P0a — PowerPoint, Speaker Notes and Export Access Map

**Date:** 2026-11-09. **Main:** `5f299a7`. Status: **source inspection, no export execution**. Scope is the current Gomri/Presenton application; code from pending PR #88 is not assumed in main.

## Known code ownership

| Stage | Verified source location | What is present | What remains unverified |
|---|---|---|---|
| Slide canonical data | servers/fastapi/models/sql/slide.py, SlideModel | `speaker_note: Optional[str]`, content, ui, layout, properties, owner_id and presentation UUID | Per-element stable identity across export and reimport |
| Next.js UI model | servers/nextjs/app/(presentation-generator)/types/slide.ts | `speaker_note?: string`; slide ID, index, content, layout, UI | Validation of notes under simultaneous edits |
| Notes editing | servers/nextjs/app/(presentation-generator)/presentation/components/SlideActionBar.tsx; presentation/components/PresentationMode.tsx | Speaker notes UI elements exist | Exact UI write path, autosave integration and any Markdown loss |
| Slide update API | servers/nextjs/app/(presentation-generator)/services/api/presentation-generation.ts | Sends full slide to PATCH /api/v1/ppt/presentation/slide_update | Revision conflict semantics for concurrent notes edits |
| Server update | servers/fastapi/api/v1/ppt/endpoints/presentation.py | `slide.model_dump(exclude={id,presentation,index})` merged into stored SlideModel; speaker_note included as mutable content | User/owner route check in a real authenticated DB test; no atomic CAS demonstrated |
| Existing unit test | servers/fastapi/tests/unit/test_presentation_slide_update_api.py | Test source explicitly updates and asserts `speaker_note == "Updated note"` | Test was NOT executed here; fake DB test cannot establish exported PPTX fidelity |
| Bundled native export | servers/nextjs/lib/run-bundled-presentation-export.ts; app/api/export-presentation/route.ts | PDF and PPTX requested via bundled export runner | Does export-core serialize notes slides, native chart/table objects or shape IDs? UNKNOWN |
| Export request role | servers/nextjs/app/api/export-presentation/route.ts | `authStatusForRequest` checks authenticated, requires id/format, runs exporter with cookie, moves output under user directory | Upstream presentation ID validation in export worker; concurrent revocation |
| Download role/path | servers/nextjs/app/api/export-presentation/file/route.ts | Authenticates request; `getSafeExportName` confines ordinary users to `users/{user_id}/...`; `realpath` prevents path traversal/symlink outside exports | Auth-disabled desktop behavior, revoked user's effect, stale cached files in unusual runtime modes |
| Import after export | Prior PR #88 includes a draft editable PPTX -> JSON fidelity harness | Existing prior evidence described notes loss in some fixtures | NOT on main; do not claim round-trip notes support |

## Explicit nonclaims and necessary test

**Do not write "speaker notes missing from Gomri".** They exist in the SlideModel, browser Slide type and UI, and the slide update unit test covers changing them. The **unknown is native PPTX notes OOXML, after export and reimport**, not whether the in-app concept exists.

**Do not write "export endpoint has no auth".** It authenticates before initiating and downloading, and scopes exported file paths to the current user. The remaining question is whether authorization for the requested *presentation itself* is consistently checked through the exporter/underlying API, especially under role changes, disabled-auth mode and concurrent requests.

Minimum **P0b** synthetic fixtures:
1. Two slides containing distinct notes strings; edit one, save, reload, native PPTX export; inspect `ppt/notesSlides/*.xml` and rels; compare exact text, attribution and mappings.
2. Verify a chart, table and note all remain independent native structures when claimed; if flattened or lost, issue explicit feature-status and loss receipt.
3. Download an owned export; try an unauthorized other-owner export file path, traversal and symlink in isolated test directory. Verify denial/containment.
4. Revoke access between generation and retrieval; check the recipient's ability to download by current session and any background artifact ownership.
5. Use a synthetic owner A/B setup to check presentation ID ownership at export **start** and output read, not only file name path.
6. When P0b certifies exporter behavior, compare exact exported native object identity to initial SlideModel IDs and record any mapping failure; tests cannot assert a notes guarantee if the upstream bundled package lacks support.

These tests have **not** been run. The existence of a notes field, auth check and path guard is source-verified but not the same as complete runtime protection or PowerPoint fidelity.

**Next:** P0b isolated test receipts, then P3 design/implementation gate. See [P0 contract](../GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md).
