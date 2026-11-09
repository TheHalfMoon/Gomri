# P0a — Exact PR Source Baseline Before Isolated P0b Qualification

**Inspected:** 2026-11-09. **Baseline main:** 5f299a7a6174ad3a1180f827778db5f4400a4d71.

| PR | Scope | Verified head SHA | Status | Changed files |
|---|---|---|---|---:|
| [#88](https://github.com/TheHalfMoon/Gomri/pull/88) | Integration: citations, RTL, PPTX, image export, animations | d4362c6d968d2746d499630d8498d3111c98c90b | OPEN/DRAFT | 223 |
| [#89](https://github.com/TheHalfMoon/Gomri/pull/89) | GPT Slides REA | 10d9deb857d1aa8190f27634a63d2445a1a478fa | OPEN/DRAFT | 6 |
| [#90](https://github.com/TheHalfMoon/Gomri/pull/90) | Beautiful.ai source REA | 5e8ebe0b31b3282f2d0c071d627e40cad5636050 | OPEN/DRAFT | 399 |
| [#91](https://github.com/TheHalfMoon/Gomri/pull/91) | VistaCreate REA | b4d08c40bc8f6235bab2a02a58060c52f3d98999 | OPEN/DRAFT | 226 |
| [#92](https://github.com/TheHalfMoon/Gomri/pull/92) | Craft Anything public REA | 4fc9ba32a35b5847a3b3c2c2fe935b0bff609abf | OPEN/DRAFT | 6 |
| [#93](https://github.com/TheHalfMoon/Gomri/pull/93) | This EGM plan and review | Moving as evidence added | OPEN/DRAFT | — |

**Interpretation:** PR #88 is an unmerged engineering candidate. #89–#92 are research and copied public source, not verified product functions. None constitutes an accepted current-main feature or a claimed release.

## P0b tasks — not executed in this P0a report

1. Re-fetch each exact head at execution time and record the actual checkout; do not rely solely on these snapshots.
2. On isolated Windows test environment, run root Node tests, Next.js tests, TypeScript, production build, fixed export-core and native PPTX fidelity. Record exact command, exit, elapsed, skips, output artifact and checksum.
3. Run the complete FastAPI suite on disposable storage; owner A/B slide PATCH, stale concurrent writes, deck reorder race and retry/Undo scenarios.
4. Inspect CI exact head for queued, failed, skipped or passed; previous candidate evidence reported root 55 pass, Next.js 148 pass, native PPTX harness 15 pass and production build, but **this is historical local evidence, NOT 2026-11-09 exact-head CI approval**.
5. Run Windows UI synthetic source -> outline -> slide -> scoped edit -> editable PowerPoint journey, with screenshots, speaker notes and per-component identity checks. Record all losses.
6. Audit legal source notices, licenses and third-party model/media assets; never run quarantined old Crello Electron renderer or silently trigger paid APIs.

**Exit:** a per-test PASS/FAIL/BLOCKED ledger and explicit GO/CONDITIONAL/NO-GO to advance one grain. A failing or unverified PR #88 may be kept Draft while current main is tested separately; it does not automatically authorize P1.

See [controlling execution contract](../GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md).
