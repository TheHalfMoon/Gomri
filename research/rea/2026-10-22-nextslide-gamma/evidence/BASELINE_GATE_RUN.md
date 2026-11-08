# BASELINE GATE RUN — deterministic pre-change baseline

**Purpose:** establish the exact, reproducible green/red state of the Gomrey tree **before** any
NextSlide/Gamma-derived change, so every later claim of "existing functionality remains intact"
is anchored to a measured baseline rather than an assumption.

**Tree:** `TheHalfMoon/Gomrey` @ `5f299a7a6174ad3a1180f827778db5f4400a4d71` (main)
**Branch created for this mission:** `feature/rea/nextslide-gamma-wave1`
**Host:** macOS (darwin 25.0), arm64, Node v26.0.0, npm 11.12.1, Python 3.13.5 (system) /
Python 3.11 (project venv), uv 0.11.20
**Date (UTC):** 2026-10-22

---

## 1. Gate results

| # | Gate | Command | Result | Exit |
|---|---|---|---|---|
| G1 | Repository tooling | `npm test` (repo root) | **48 pass / 0 fail** | 0 |
| G2 | FastAPI unit+integration | `cd servers/fastapi && uv run --locked python -m pytest -q --tb=line` | **1125 passed**, 10 warnings | 0 |
| G3 | Next.js unit tests | `cd servers/nextjs && npm test` | **73 pass / 0 fail** | 0 |
| G4 | Electron typecheck | `cd electron && npm run typecheck` | **no errors** | 0 |
| G5 | Electron main compile | `cd electron && npm run build:ts` | **ok** | 0 |
| G6 | Electron main globals | `cd electron && npm run check:main-no-undef` | `No undefined names found in 39 Electron main JS files.` | 0 |
| G7 | Electron app path migration | `cd electron && npm run test:path-migration` | **11 pass / 0 fail** | 0 |
| G8 | Secret scan | `node scripts/scan-secrets.mjs` | `secret-scan: OK (no credential-like matches in repository-owned files)` | 0 |
| G9 | Platform support matrix | `node scripts/check-platform-support.mjs` | recorded below | 0 |
| G10 | Release config dry-run | `node scripts/validate-release-config.mjs` | recorded below | 0 |
| G11 | Release manifest binding | `node scripts/generate-release-manifest.mjs --check-only` | recorded below | 0 |
| G12 | Fixture policy | `node scripts/check-fixtures.mjs` | recorded below | 0 |
| G13 | Next.js ESLint | `cd servers/nextjs && npm run lint` | see `NEXTJS_LINT_BUILD.md` | — |
| G14 | Next.js production build | `cd servers/nextjs && npm run build` | see `NEXTJS_LINT_BUILD.md` | — |
| G15 | Cypress component tests | `cd servers/nextjs && npx cypress run --component --browser electron` | see `NEXTJS_LINT_BUILD.md` | — |

> G13–G15 are executed separately because they are the slowest gates; their results are recorded in
> `NEXTJS_LINT_BUILD.md` so that a re-runner can distinguish "not run" from "run and failed".

---

## 2. Environment provisioning actually performed

All provisioning was local and zero-cost; no paid API, hosted service or funded provider was used.

| Action | Command | Outcome |
|---|---|---|
| Root deps | `npm ci` (repo root) | `added 69 packages` |
| FastAPI env | `cd servers/fastapi && uv sync --locked --dev` | Python 3.11 venv resolved from `uv.lock` |
| Next.js deps | `cd servers/nextjs && npm ci` | `added 892 packages` |
| Electron deps | `cd electron && npm ci --ignore-scripts` | `added 448 packages` |

Disk after provisioning: 18 GiB free on `/` (was 19 GiB). No credential was created, requested or
written at any point.

---

## 3. Test-environment contract for FastAPI

The CI workflow pins these environment variables. Reproducing the suite locally requires them,
otherwise collection errors appear unrelated to the code under test.

```bash
APP_DATA_DIRECTORY=/tmp/presenton-tests/app-data
TEMP_DIRECTORY=/tmp/presenton-tests/temp
DATABASE_URL=sqlite+aiosqlite:////tmp/presenton-tests/test.db
DISABLE_ANONYMOUS_TRACKING=true
DISABLE_IMAGE_GENERATION=true
```

---

## 4. Baseline interpretation (why this constrains the integration)

The G2/G3 test names expose pre-existing capability that is **materially ahead of a naive
NextSlide transplant**, and therefore constrains what may be adopted:

| Existing Gomrey capability | Evidence (baseline test name) | Consequence for the mission |
|---|---|---|
| PPTX **import** already exists and is more advanced than the donor's extractor | `preserves text-list item and marker gaps when importing Template V2`, `preserves the supported PPTX JSON metadata when importing Template V2` | The donor's `extract-pptx.py` must **not** be copied. Disposition → `ALREADY_PRESENT` / `REJECT (inferior)`. |
| A Konva **canvas renderer** already exists | `allocates unsized flex children like the Konva renderer` | A second slide-rendering stack must not be introduced. Disposition → `REJECT (parallel stack)`. |
| PPTX table/vector/chart/flip/legend rendering already exists | `renders PPTX table borders, vector metadata, flips, and chart legend position` | A second PPTX engine is not justified without bounded fidelity delta. Disposition → `REFERENCE` pending a real differential test. |
| Template **theme** normalization already exists | `loads and caches normalized template themes from the theme endpoint` | Donor style presets must be proven additive, not a replacement theme source. |
| HTML **layout** output already exists | `adds text-list gap only between items in the canvas layout`, `uses marker_gap between the marker and item text in HTML layout` | A separate single-file HTML presentation engine needs a differential demonstration of a capability Gomrey lacks. |
| Editable vector arrows + SVG endpoint markers | `creates line arrows as one two-point editable vector`, `renders editable vector line arrowheads as SVG endpoint markers` | Confirms Gomrey already prioritises **editability** — the donor must be measured on the same axis. |

**Governing rule applied:** `docs/SOURCE_LEDGER.md` §1 — *"reuse mature implementation before native
rebuild, but never inherit donor architecture … by accident"* — and issue §D — *"minimize the amount
of custom code: no parallel editor stack, no duplicated PPTX engines unless bounded fidelity tests
justify them."*

---

## 5. Re-run protocol

```bash
cd /Users/abdulazizalsh/work/Gomrey
git checkout feature/rea/nextslide-gamma-wave1
npm ci
npm test                                        # G1
cd servers/fastapi && uv sync --locked --dev \
  && APP_DATA_DIRECTORY=/tmp/presenton-tests/app-data \
     TEMP_DIRECTORY=/tmp/presenton-tests/temp \
     DATABASE_URL=sqlite+aiosqlite:////tmp/presenton-tests/test.db \
     DISABLE_ANONYMOUS_TRACKING=true DISABLE_IMAGE_GENERATION=true \
     uv run --locked python -m pytest -q --tb=line   # G2
cd servers/nextjs && npm ci && npm test        # G3
cd electron && npm ci --ignore-scripts \
  && npm run typecheck && npm run build:ts \
  && npm run check:main-no-undef && npm run test:path-migration  # G4–G7
node scripts/scan-secrets.mjs                   # G8
node scripts/check-platform-support.mjs         # G9
node scripts/validate-release-config.mjs        # G10
node scripts/generate-release-manifest.mjs --check-only  # G11
node scripts/check-fixtures.mjs                 # G12
```
