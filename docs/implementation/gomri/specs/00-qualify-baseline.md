# S00 — Qualify Baseline and Restore a Safe Isolated Backend Test Lane

**Goal:** Replace the conditional P0b state with trustworthy actual FastAPI/Next.js/PowerPoint and two-owner security receipts. This **is the only phase authorized to begin immediately** under the controlling EGM contract.

**Owners:** R2 (backend safety), R0 (integrator), R8 (independent security verifier). **Depends on:** none. **Surface:** disposable test source, environment/fixtures and planning branch evidence. **Prohibited:** real user DB/files, changes to production source, auto-merge.

## Existing baseline / constraints

- PR #88 pinned \`d4362c6\` contains narrative, animation, Arabic/RTL and PPTX work, but is unmerged.
- Exact-head historical P0b: 61/61 seven selected Node tests passed (unit/contracts and 15 native PPTX roundtrip tests); **the test intentionally expects speaker-note import loss and bullet flattening**.
- Source has \`SessionAuthMiddleware\` and SQLAlchemy \`with_loader_criteria\` filtering owned \`SlideModel\` SELECTs. No confirmed cross-owner vulnerability. Current browser \`PATCH /api/v1/ppt/presentation/slide_update\` request has no observed \`baseRevision\`/idempotency key; actual concurrent write protection untested.
- Bare Python 3.11.15 exists on Windows, but requisite \`fastapi\`, \`sqlmodel\`, \`sqlalchemy\`, \`aiosqlite\`, \`pytest\` were not in that interpreter. Python 3.14 is outside the project's Python >=3.11,<3.12 range. \`uv\` not on the observed PATH. D: recently ~6 GB free; check again before install.
- Scratch tree for the previous run was **deleted after preserving sanitized receipts**; do not reuse imaginary paths from that run.

## Write boundary and test isolation

- New branch/working tree under a **fresh temporary directory**, independent from C:\Users\Shehr\Gomrey. Pin exact commit by \`git rev-parse HEAD\` after checkout.
- Temporary Python 3.11 venv and SQLite DB under that scratch folder; per-run randomly generated synthetic tenant A/B, APP_DATA_DIRECTORY, exports, queues, browser profile and ports.
- Do not inherit provider keys, real cookies, DB credentials or user media. Set/no-telemetry and egress guards per [EGM isolation contract](../../../designs/GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md). Process-level Node hooks are **not** a full OS sandbox. Test the egress rule with a negative control.
- Do NOT connect to user's existing PostgreSQL/MySQL/desktop database. Python wheelhouse must be pinned/checksummed and free; prefer local cache. If unavailable, explicitly arrange a separate dependency-admission PR; no surprise pip install or paid compute.

## Executable sequence

1. \`/ps-doctor\`: record actual Python executable, node, git, disk free, Cypress/Playwright binary, Alibaba OCR and available local model. Capture **versions**, not secrets.
2. \`git clone --no-hardlinks --no-checkout <owner repo> <scratch>\` or equivalent isolated worktree with independent build paths; detach exact #88 SHA. Assert original checkout \`git status --porcelain\` unchanged.
3. \`py -3.11 -m venv <scratch>\.venv\` if interpreter available. Audit complete lock/resolution and install only checksum-pinned wheels into that venv using \`--no-index --find-links <audited_wheelhouse>\`. If the wheelhouse is missing, record BLOCKED and pause only backend group; do **not** use Python 3.14.
4. Run EGM P0b preflight and write manifest: dependency SHA, temp storage locations (redacted), random two owners, auth enabled, separate DB basename, loopback ports, provider egress and teardown guarantee. Negative control must prove host egress blocked where required; don't change global firewall or Windows Defender.
5. Existing selected unit/contract suites and native PPTX tests at current head: rerun only if source head changed or environment newly qualified. Record all errors, no overwritten retry artifacts; receipt filenames carry \`attempt-N\`.
6. Real backend tests with SQLAlchemy/SQLite, not fake session: A reads/writes own slide (success); A tries B's slide with known valid UUID (403/404, no B content mutation); forged actor/workspace rejected; auth-disabled desktop documented separately.
7. Two **concurrent writers**, same slide/revision; reorder vs slide update; duplicate operation; Undo/autosave interleaving. **If existing code overwrites silently, record failing test then produce a tiny S03 dependency/repair spec**. Do not silently modify production handler inside S00.
8. Qualify PR #88 exact-head FastAPI, TS, Next.js and root suites, export-core and existing CI statuses. Each grouped test has exact SHA, exit, skip, fixture digest and negative-control proof.
9. Clean only test-owned paths, preserve sanitized receipts in PR #93 docs, verify original worktree still clean.

## Acceptance and stop conditions

- **S00-A01:** A complete Python 3.11 temp dependency manifest with non-user DB and independent credentials; or explicitly BLOCKED with exact missing wheel names and no unintended installation.
- **S00-A02:** Authenticated owner A/B tests record actual status and DB digest before/after. If foreign-write succeeds: hard BLOCKER, report privately and stop features, do not claim release security.
- **S00-A03:** Conflict, reorder, idempotency and Undo tests reproduce the current semantics; fails may remain as **documented S03 blocking tests** but must never be called green.
- **S00-A04:** Exact #88 CI/test matrix has no hidden skipped/failed cases and named blockers. No "green" from a prior commit.
- **S00-A05:** Zero paid compute/model calls; original checkout unchanged; scratch teardown verified.
- **S00-A06:** R8 independently reviews the route-level evidence and identifies whether deeper ORM checks actually deny foreign owner.

**Exit decision:** GO for P1 **preview only** may be granted based on source/geometry/test safety even if S03 CAS requires repair, but **no persisted user/agent writes** until successful S03 safety gate. A missing A/B test is BLOCKED, not authorization to implement. New dependency downloads or security failures require separate scoped approval/repair.

## Out of scope

No full RAG rebuild, no SmartLayout persistence, no new API endpoint, no model inference, no user presentation import and no release. **Rollback:** delete only scratch and restore no source state; keep receipt and issue link.
