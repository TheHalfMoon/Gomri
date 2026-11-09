# Gomri EGM — P0b Isolated Test Environment and Permission Matrix

**Status: PROPOSED / P0b CONDITIONAL, NOT STARTED.** Date: 2026-11-09. This is the mandatory preflight before any baseline test against main or draft PR #88. No source changes, system firewall changes, installations or test-data writes were performed to create this document.

## 1. Explicit permissions by phase

| Phase | Read repository | Write evidence docs | Build/test in disposable workspace | Modify product source | Modify canonical user content | Merge/release |
|---|---|---|---|---|---|---|
| P0a (source audit) | YES | YES (planning branch) | NO | NO | NO | NO |
| P0b (qualification) | YES | YES (planning branch) | YES **after isolation preflight**, disposable files/DB only | NO; isolated stand-alone test harness may be authored without application changes | NO | NO |
| P1 (preview concept) | After P0b approval | YES | YES, isolated | Only bounded preview code on a separate PR after fresh approval | NO; no autosave/persist | NO until CI/review |
| P2 (revision/ACL) | After gate | YES | YES | Narrow, separately reviewed feature PR | Only in synthetic tests until exact-head acceptance and explicit release decision | NO automatic merge |
| P3 (OOXML fidelity) | After gate | YES | YES | Narrow, separately reviewed feature PR | NO until release gate | NO automatic merge |
| P4/P5 | Separately scoped later | YES | As allowed | Not yet authorized | Not yet authorized | Not yet authorized |

**Production write** means writing product code, persistent application data, user-owned artifacts or a live deployment. A test that mutates only a throwaway database is a **test write**, not an authorization to mutate a real deck.

## 2. Mandatory P0b preflight — all must be PASS

1. **Exact source:** record current main SHA and #88 candidate SHA, branch URL and commit. Prepare an independent *detached, temporary* source copy for each run; do NOT checkout branches in C:\Users\Shehr\Gomrey, change that working tree or merge/cherry-pick.
2. **Disk and cleanup:** measure C:/D: free space and expected dependencies/build output *before* installing anything. If insufficient, mark large builds BLOCKED; do not delete unrelated caches, agents or project assets, and do not use the user's normal profile as scratch.
3. **Database isolation:** create a newly initialized throwaway SQLite database or dedicated ephemeral DB schema. Assert the connection URL points to the temporary path and contains **no existing customer tenant/account IDs**. Do not reuse the current desktop app's production database or existing user account.
4. **Identity isolation:** generate two new synthetic user IDs (owner A/B), one fresh synthetic workspace per user, test-only JWT/session cookies and test-local configuration. Refuse tests if current auth data or external identity provider is selected. Set auth enabled for multi-user tests; separately document disabled-auth desktop as a *single-user mode*, never equivalent to multi-tenant authorization.
5. **Storage isolation:** set APP_DATA_DIRECTORY, uploads, exports, browser profiles, screenshot outputs and task/job queues to unique disposable paths. If the code cannot switch any of these from real storage, mark that test BLOCKED rather than guessing it is safe.
6. **Network/provider isolation:** launch with external model, image/stock, Sentry/telemetry and remote provider credentials **unset** from child process (do not print or commit secrets); use deterministic local synthetic data. A hard egress block, when available, must be scoped only to disposable test processes/containers; **never change global Windows firewall rules**. If isolation cannot be established and an operation may call a billable service, do not run it.
7. **Process isolation:** use dedicated loopback ports and disposable browsers. Verify there is no already-running server on those ports. No test should attach to the user's live browser, app session, Docker volume, shared Redis or ordinary database.
8. **Preflight proof:** emit a machine-readable manifest recording exact repo SHA, temporary paths (non-secret), database basename, two synthetic owner IDs (for testing only), allowed loopback ports, expected processes, provider flags redacted, and isolation checks. Any FAIL aborts that case.
9. **Teardown:** stop only test-owned processes; delete only enumerated test-owned temporary directories/DB/queues and scratch browser profiles; verify no process or file lock remains. Keep checksum/test receipts in the research branch, never secrets, cookies or real personal data.

## 3. Runnable groups, separately approved

- **P0b group A — static reproducibility:** root Node tests, Next.js node tests, TypeScript; exact-head, no cloud credentials, temp cache. Skip any script requiring package installation until dependency/admission and disk preflight.
- **P0b group B — isolated backend:** existing FastAPI pytest with temp DB and temp assets. Tests for ORM owner-scope must use middleware and actual AsyncSession, not only FakeAsyncSession. Explicitly compare authenticated multi-user with intentionally disabled-auth single-user mode.
- **P0b group C — safety negatives:** owner A PATCHes B's slide; forged actor/tenant; same-revision concurrent writes; reorder versus slide update; duplicate operation; Undo/autosave interleaving; export after access revoked. Record expected rejection, actual status/content and DB digest.
- **P0b group D — export/Windows:** synthetic 8–12 slides including notes, chart, table, Arabic/English; open/export/reimport actual PPTX; capture screenshots and native OOXML types. Do not conflate a visually similar PNG with editable PPTX.

**Do not use empty test output, exit=0 for a setup command, or a prior-commit CI badge as evidence a case passed.** A failed or blocked test is an expected possible finding.

## 4. Evidence receipt template (one per command/scenario)

| Field | Requirement |
|---|---|
| receipt_id, case_id, phase | Unique and linked to this contract |
| source_sha, branch, tool versions | Exact immutable identity |
| command / fixture_hash | Reproducible, secrets redacted |
| environment/isolation_manifest_hash | Temp DB/ports/egress status |
| expectation and negative control | How an unsafe result would fail |
| actual output, exit code, elapsed, skips | No invented results |
| result | PASS / FAIL / BLOCKED / INCONCLUSIVE |
| affected paths, artifacts, cleanup receipt | Verify no user data changed |
| reviewer and disposition | GO / CONDITIONAL / NO-GO for **that** grain |

A failing security negative test is not silently reclassified as PASS or approved as a known issue for canonical AI writes.

## 5. Exact go/no-go split

**P0a GO:** route/owner map, speaker-notes/export map, PR baseline and named unknowns exist and are reviewable. The code inspection alone does not approve runtime writes.

**P0b CONDITIONAL:** start only after all isolation preflight fields are satisfied per test group. Unavailable disk, credentials, disposable queues or offline inference routes yield BLOCKED for the affected group.

**P1/P2 NO-GO at present:** the first headline-hero preview must first get a separate scoped approval; no layout commits until P2 write-safety passes. The feature paths listed in the v3 master plan are proposals, not permission to edit them.

All original EGM review reports and this contract remain Draft. The full official EGM Goldfish orchestration has not been demonstrated.
