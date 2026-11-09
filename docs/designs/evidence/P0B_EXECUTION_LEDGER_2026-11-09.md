# P0b Actual Execution Ledger — Gomri Windows

**Date:** 2026-11-09. **Status:** PARTIAL P0b qualification. **Candidate exact SHA:** d4362c6d968d2746d499630d8498d3111c98c90b (Draft PR #88). **Main baseline:** 5f299a7a6174ad3a1180f827778db5f4400a4d71.

## Real isolated run

An independent detached Git clone was created under D:\Gomri-Research\EGM\P0B-20261109\source-pr88; the active user checkout C:\Users\Shehr\Gomrey remained clean, same source SHA. Source data was about 0.3 GB tracked, D: free space changed from ~7.39 GB to ~6.87 GB. Runtime was local Node on Windows; no package manager install, paid provider or remote API call performed.

A process-specific child-environment allowlist used disposable TEMP/TMP/HOME/APPDATA/APP_DATA_DIRECTORY and an unused SQLite DATABASE_URL pointing to the isolated runtime directory. No model API keys were inherited. A Node process-level outbound guard rejected remote net.Socket.connect and fetch, plus a dummy localhost HTTP(S) proxy. **This was a best-effort guard, not a Windows firewall or full OS egress sandbox.** It is suitable for the selected reviewed tests only; full FastAPI/E2E groups require stronger isolation.

Each command was run through node --test from the isolated source, with per-file SHA256, exit and elapsed time. **Seven sanitized receipt records are now committed in [the evidence JSON](P0B_RECEIPTS_SANITIZED_2026-11-09.json)**; they include per-test outputs and digest fields. The raw disposable scratch files were removed after upload, so the original full raw logs are no longer stored on the Windows PC.

| Case | Actual test file(s) | Tests | Exit | Result |
|---|---|---:|---:|---|
| P0B-A01-contracts | scripts/contracts.test.mjs | 9 | 0 | PASS |
| P0B-A02-template-converters | scripts/convert-template.test.mjs; scripts/convert-presentation-template.test.mjs | 4 | 0 | PASS |
| P0B-A03-main-metadata | scripts/package-metadata.test.mjs; scripts/product-identity.test.mjs; scripts/compatibility-aliases.test.mjs | 9 | 0 | PASS |
| P0B-A04-nextjs-autosave | servers/nextjs/tests/presentation-autosave.test.mjs | 3 | 0 | PASS |
| P0B-A05-template-v2-geometry | servers/nextjs/tests/template-v2-component-bounds.test.mjs | 3 | 0 | PASS |
| P0B-A06-arabic-rtl-contract | servers/nextjs/tests/arabic-rtl-qualification.test.mjs | 18 | 0 on retry | PASS |
| P0B-A07-native-pptx-roundtrip | servers/nextjs/tests/export-fidelity.test.mjs | 15 | 0 | PASS — measured known losses |

**Grand total: 61/61 passing tests in seven groups**, including real JSON-to-PPTX-to-JSON export-fidelity tests. This is not a complete UI, cross-user security or perfect PowerPoint editability qualification.

### Initial setup failure, then repaired without modifying the original checkout

The first A06 Arabic/RTL run produced **18 failures at setup time** because its esbuild bundle could not resolve the KaTeX dependency. This was a missing scratch dependency, not a verified product failure. Only already-installed local copies of esbuild, @esbuild/win32-x64 and katex (about 14 MB total) were copied into the separate scratch checkout. A04, A05 and A06 were rerun at the exact same SHA, returning 3/3, 3/3 and 18/18 passes. **Receipt retention correction:** the first failure was observed in the terminal output but the same A06 JSON receipt path was **overwritten by the green rerun**. The initial full raw failure JSON is NOT retained; its key error, exit status and test count are accurately summarized here from the observed initial terminal output. Future runners must use distinct attempt IDs rather than overwrite receipts.

## Measured PPTX export/reimport qualification — P0B-A07

Copied the already-installed, pinned **@presenton/export-core 1.0.34** runtime (~78 MB) into the isolated clone; no npm installation, network fetch, user profile or production data access. Ran system Node with the previously established scratch environment and process-level outbound guard from scratch Next.js:

`node --test tests/export-fidelity.test.mjs`

Actual result at **d4362c6**: **exit 0, 15 tests, 15 PASS, 0 FAIL, 0 SKIP, approximately 69 seconds**. Sanitized stdout excerpts, exits and source file SHA256 are recorded in committed evidence JSON `P0B-A07-native-pptx-roundtrip.json`.

Fixture cases cover text fonts, alignment and bullets, tables, vectors, charts, backgrounds, speaker notes, adversarial content and RTL/emoji; the harness performs actual PPTX generation and re-import rather than screenshots.

**Critical interpretation of passing tests:** the observed expected behaviors explicitly include (1) a speaker note being **written into PPTX but not restored by PPTX→JSON reimport**, and (2) bullet content surviving only as **literal text instead of native bullet structures**. This is an acknowledged P3 roundtrip-fidelity limitation, not a native semantic preservation pass. A passing expectations harness is not an end-user-quality guarantee.

The bundled test's ZIP reader is a narrow central-directory inspection utility and is not established as a safe, complete parser for untrusted Office files. Pixel-level render, PowerPoint desktop editing and the cross-owner export authorization test are still pending.

**Updated totals:** 9+4+9+3+3+18+15 = **61/61 passing tests across seven targeted groups**. The green retry has a sanitized repository JSON receipt; the initial setup failure is summarized from observed console output because the original receipt was overwritten. This is an audit-trail limitation, not an additional passing test.

## Unrun/blocked cases — do not count as passes

| Work | State | Why |
|---|---|---|
| Entire root npm test | NOT RUN | Selected scripts only; remaining scripts require their own isolation review |
| Entire Next.js suite and production build | NOT RUN | Only three targeted tests; full dependency tree not installed in scratch |
| Full FastAPI pytest | BLOCKED | Disposable Python dependencies, backend environment, isolated DB and auth not yet qualified |
| Owner A/B real slide PATCH negative tests | BLOCKED | Need synthetic session/DB and full API test isolation |
| Stale two-client CAS, reorder, retry and Undo | BLOCKED | Need controlled concurrent database test and revision oracle |
| Native PPTX deterministic roundtrip | **15/15 PASS** in P0B-A07 | Current measured expectations explicitly show speaker notes **not re-imported** and bullet semantics **flattened to text**; live editor and untrusted PPTX parser untested |
| Windows real browser/E2E | NOT RUN | Needs disposable browser/profile/storage |
| GitHub exact-head CI and independent code review | NOT VERIFIED | Do not use historical CI claims as this run |
| Full official Google EGM orchestration | NOT RUN | Prior independent reviewer sessions are not the official complete orchestrator |

Source inspection already confirmed actual FastAPI SessionAuthMiddleware and SQLAlchemy owner-filtering SELECT hook, as documented in P0a route map. This is a **real existing protection**; no foreign-owner vulnerability has been proven. Browser auto-save tests passing do not prove server atomic CAS. SlideModel and the UI have speaker_note fields, but native editable PPTX notes remain unqualified.

## Backend environment admission check — P0B-B1 remains BLOCKED

Additional **read-only** Windows toolchain inspection found: the source backend pyproject requires **Python >=3.11,<3.12** with FastAPI, SQLModel, SQLAlchemy, aiosqlite, pytest and other packages. There is a locally installed bare Python **3.11.15**, but it has **none of pytest, fastapi, sqlmodel, sqlalchemy, aiosqlite or uvicorn** available. The Windows Python 3.14.7 has pytest but lacks FastAPI/SQLModel/SQLAlchemy/aiosqlite and is outside the declared backend version range. No isolated backend virtual environment was present. A local uv cache directory exists, but its top-level layout does not demonstrate a complete compatible offline dependency set.

**Decision:** no dependency install, network download, live DB attachment or improper Python 3.14 substitution. Real SessionAuthMiddleware + AsyncSession owner-scoped test **cannot safely run yet** under the specified isolated backend configuration. P0B-B1 is **BLOCKED ENVIRONMENT**, not a passing test and not evidence of a security vulnerability.

Next admitted action requires building a disposable Python 3.11 test environment exclusively from audited local offline wheels or a user-approved no-cost dependency path, verifying temporary SQLite/database and account isolation, then executing the single B1 query. Do not install into the normal user's Python or mutate the existing desktop data.

## Cleanup and evidence preservation

After [the seven sanitized receipts](P0B_RECEIPTS_SANITIZED_2026-11-09.json) were committed, the specifically created directory `D:\Gomri-Research\EGM\P0B-20261109` was deleted, with no test-owned Node/git/Python process running. D: free space rose from **5.10 GB** to **5.73 GB** (approximately 0.63 GB recovered). The existing user checkout was verified **clean, 0 modified paths**, still at `d4362c6d968d2746d499630d8498d3111c98c90b`. Only the intentionally created test scratch was deleted; user project files were not touched.

The repository now retains a sanitized, inspectable evidence bundle rather than the full original console logs. The first missing-KaTeX failure's original complete JSON receipt was overwritten before upload and cannot be recovered from the remaining evidence. This is transparently recorded, not described as two preserved raw receipts.

## Verdict

**GO for the seven isolated P0b-A targeted Node groups only. P0b overall remains CONDITIONAL/INCOMPLETE, P1 and P2 are still NO-GO.** Next safe step is an isolated backend test sandbox, with two synthetic owners, no shared database/queue/storage, test egress protection and cleanup receipts. A separate fresh Goldfish implementation-readiness review of actual P0b evidence is needed before permitting product code changes.

**No main merge, deployment, feature source edit, paid service or user data mutation occurred.**

Links: [P0 isolation contract](../GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md), [P0 route map](P0A_ROUTE_SYMBOL_MATRIX.md), [PR #88](https://github.com/TheHalfMoon/Gomri/pull/88), [PR #93](https://github.com/TheHalfMoon/Gomri/pull/93).
