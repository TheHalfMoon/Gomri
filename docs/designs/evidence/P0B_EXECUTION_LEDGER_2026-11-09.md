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
| P0B-A07-native-pptx-roundtrip | servers/nextjs/tests/export-fidelity.test.mjs | 15 | 0 | PASS — measured known losses |

**Grand total: 61/61 passing tests in seven groups**, including real JSON-to-PPTX-to-JSON export-fidelity tests. This is not a complete UI, cross-user security or perfect PowerPoint editability qualification.

### Initial setup failure, then repaired without modifying the original checkout

The first A06 Arabic/RTL run produced **18 failures at setup time** because its esbuild bundle could not resolve the KaTeX dependency. This was a missing scratch dependency, not a verified product failure. Only already-installed local copies of esbuild, @esbuild/win32-x64 and katex (about 14 MB total) were copied into the separate scratch checkout. A04, A05 and A06 were rerun at the exact same SHA, returning 3/3, 3/3 and 18/18 passes. The original failed receipt and passing rerun should both be retained in scratch for audit.

## Measured PPTX export/reimport qualification — P0B-A07

Copied the already-installed, pinned **@presenton/export-core 1.0.34** runtime (~78 MB) into the isolated clone; no npm installation, network fetch, user profile or production data access. Ran system Node with the previously established scratch environment and process-level outbound guard from scratch Next.js:

`node --test tests/export-fidelity.test.mjs`

Actual result at **d4362c6**: **exit 0, 15 tests, 15 PASS, 0 FAIL, 0 SKIP, approximately 69 seconds**. Full stdout and source test SHA256 are recorded in local JSON receipt `P0B-A07-native-pptx-roundtrip.json`.

Fixture cases cover text fonts, alignment and bullets, tables, vectors, charts, backgrounds, speaker notes, adversarial content and RTL/emoji; the harness performs actual PPTX generation and re-import rather than screenshots.

**Critical interpretation of passing tests:** the observed expected behaviors explicitly include (1) a speaker note being **written into PPTX but not restored by PPTX→JSON reimport**, and (2) bullet content surviving only as **literal text instead of native bullet structures**. This is an acknowledged P3 roundtrip-fidelity limitation, not a native semantic preservation pass. A passing expectations harness is not an end-user-quality guarantee.

The bundled test's ZIP reader is a narrow central-directory inspection utility and is not established as a safe, complete parser for untrusted Office files. Pixel-level render, PowerPoint desktop editing and the cross-owner export authorization test are still pending.

**Updated totals:** 9+4+9+3+3+18+15 = **61/61 passing tests across seven targeted groups**. The first missing-KaTeX setup failure and green retry are both represented in scratch evidence.

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

## Verdict

**GO for the seven isolated P0b-A targeted Node groups only. P0b overall remains CONDITIONAL/INCOMPLETE, P1 and P2 are still NO-GO.** Next safe step is an isolated backend test sandbox, with two synthetic owners, no shared database/queue/storage, test egress protection and cleanup receipts. A separate fresh Goldfish implementation-readiness review of actual P0b evidence is needed before permitting product code changes.

**No main merge, deployment, feature source edit, paid service or user data mutation occurred.**

Links: [P0 isolation contract](../GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md), [P0 route map](P0A_ROUTE_SYMBOL_MATRIX.md), [PR #88](https://github.com/TheHalfMoon/Gomri/pull/88), [PR #93](https://github.com/TheHalfMoon/Gomri/pull/93).
