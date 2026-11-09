# P0b Actual Execution Ledger — Gomri Windows

**Date:** 2026-11-09. **Status:** PARTIAL P0b qualification. **Candidate exact SHA:** d4362c6d968d2746d499630d8498d3111c98c90b (Draft PR #88). **Main baseline:** 5f299a7a6174ad3a1180f827778db5f4400a4d71.

## Real isolated run

An independent detached Git clone was created under D:\Gomri-Research\EGM\P0B-20261109\source-pr88; the active user checkout C:\Users\Shehr\Gomrey remained clean, same source SHA. Source data was about 0.3 GB tracked, D: free space changed from ~7.39 GB to ~6.87 GB. Runtime was local Node on Windows; no package manager install, paid provider or remote API call performed.

A process-specific child-environment allowlist used disposable TEMP/TMP/HOME/APPDATA/APP_DATA_DIRECTORY and an unused SQLite DATABASE_URL pointing to the isolated runtime directory. No model API keys were inherited. A Node process-level outbound guard rejected remote net.Socket.connect and fetch, plus a dummy localhost HTTP(S) proxy. **This was a best-effort guard, not a Windows firewall or full OS egress sandbox.** It is suitable for the selected reviewed tests only; full FastAPI/E2E groups require stronger isolation.

Each command was run through node --test from the isolated source, with per-file SHA256, exit, elapsed, stdout/stderr in locally saved JSON receipts.

| Case | Actual test file(s) | Tests | Exit | Result |
|---|---|---:|---:|---|
| P0B-A01-contracts | scripts/contracts.test.mjs | 9 | 0 | PASS |
| P0B-A02-template-converters | scripts/convert-template.test.mjs; scripts/convert-presentation-template.test.mjs | 4 | 0 | PASS |
| P0B-A03-main-metadata | scripts/package-metadata.test.mjs; scripts/product-identity.test.mjs; scripts/compatibility-aliases.test.mjs | 9 | 0 | PASS |
| P0B-A04-nextjs-autosave | servers/nextjs/tests/presentation-autosave.test.mjs | 3 | 0 | PASS |
| P0B-A05-template-v2-geometry | servers/nextjs/tests/template-v2-component-bounds.test.mjs | 3 | 0 | PASS |
| P0B-A06-arabic-rtl-contract | servers/nextjs/tests/arabic-rtl-qualification.test.mjs | 18 | 0 on retry | PASS |

**Grand total: 46/46 passing tests in six groups.** These are selected deterministic unit/contract/markup tests, not full suites and not UI or native PowerPoint proof.

### Initial setup failure, then repaired without modifying the original checkout

The first A06 Arabic/RTL run produced **18 failures at setup time** because its esbuild bundle could not resolve the KaTeX dependency. This was a missing scratch dependency, not a verified product failure. Only already-installed local copies of esbuild, @esbuild/win32-x64 and katex (about 14 MB total) were copied into the separate scratch checkout. A04, A05 and A06 were rerun at the exact same SHA, returning 3/3, 3/3 and 18/18 passes. The original failed receipt and passing rerun should both be retained in scratch for audit.

## Unrun/blocked cases — do not count as passes

| Work | State | Why |
|---|---|---|
| Entire root npm test | NOT RUN | Selected scripts only; remaining scripts require their own isolation review |
| Entire Next.js suite and production build | NOT RUN | Only three targeted tests; full dependency tree not installed in scratch |
| Full FastAPI pytest | BLOCKED | Disposable Python dependencies, backend environment, isolated DB and auth not yet qualified |
| Owner A/B real slide PATCH negative tests | BLOCKED | Need synthetic session/DB and full API test isolation |
| Stale two-client CAS, reorder, retry and Undo | BLOCKED | Need controlled concurrent database test and revision oracle |
| Native PPTX and speaker note OOXML/reimport | BLOCKED | Need isolated bundled export runtime, notes fixture, secure XML parsing |
| Windows real browser/E2E | NOT RUN | Needs disposable browser/profile/storage |
| GitHub exact-head CI and independent code review | NOT VERIFIED | Do not use historical CI claims as this run |
| Full official Google EGM orchestration | NOT RUN | Prior independent reviewer sessions are not the official complete orchestrator |

Source inspection already confirmed actual FastAPI SessionAuthMiddleware and SQLAlchemy owner-filtering SELECT hook, as documented in P0a route map. This is a **real existing protection**; no foreign-owner vulnerability has been proven. Browser auto-save tests passing do not prove server atomic CAS. SlideModel and the UI have speaker_note fields, but native editable PPTX notes remain unqualified.

## Verdict

**GO for the six isolated P0b-A local Node groups only. P0b overall remains CONDITIONAL/INCOMPLETE, P1 and P2 are still NO-GO.** Next safe step is an isolated backend test sandbox, with two synthetic owners, no shared database/queue/storage, test egress protection and cleanup receipts. A separate fresh Goldfish implementation-readiness review of actual P0b evidence is needed before permitting product code changes.

**No main merge, deployment, feature source edit, paid service or user data mutation occurred.**

Links: [P0 isolation contract](../GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md), [P0 route map](P0A_ROUTE_SYMBOL_MATRIX.md), [PR #88](https://github.com/TheHalfMoon/Gomri/pull/88), [PR #93](https://github.com/TheHalfMoon/Gomri/pull/93).
