# P06-G3 — OCR Workers and Arabic P0 Suite

**Parent:** #43
**Issue:** #46
**Canonical base:** `5a432f2c23c92e1e7fefd92c76b6ff715049d75d` (P06-G2 merged)

## Goal

Define what OCR workers must produce and freeze the nine canonical
Arabic P0 expectations as deterministic checks — worker processes
(PaddleOCR-class and challengers) qualify through these contracts,
never around them.

## Scope

- `servers/fastapi/gomrey/ocr_worker.py`: `OCRRegion` model (bbox,
  rotation, confidence observation, degraded flags); `script_profile`
  Unicode analysis (Arabic/Latin, both numeral systems, rtl/mixed/ltr);
  `validate_region`; `map_ocr_regions` (bbox/script provenance into
  units); `quality_observations` (low-confidence/rotated/degraded
  escalation signals, never a certificate); `check_arabic_case` for all
  nine MASTER_PLAN cases with empty-input rejection, decimal/date shape
  evidence, and certain-claim-over-visual rejection. Pure logic, no
  models, no weights, no lockfile change.
- `servers/fastapi/tests/test_gomrey_ocr_worker.py`: 4 tests
  (script/numeral profiles, provenance mapping + malformed shapes,
  escalation honesty, all nine P0 cases with negatives).
- Package exports extended.

## Out of scope

PaddleOCR DEPEND packaging and weights, worker processes, real scan
fixtures, cell-order table qualification with measured tables (worker
qualification + G4 coverage), IR provenance completion (G4).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (14 modules incl. new ocr_worker): 79 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over structure_worker/parser_router.
- TypeSafe Jev `jev-1.13.0` (real): overclaim/provenance-loss 0.20;
  suite-triviality first probe 0.48. Investigation found a real
  triviality bug — `all()` over an empty region list vacuously passes
  any universal case — plus two weaker-than-named checks. Fixed: empty
  input raises, decimals need shape evidence, charts reject
  certain-claims-over-visual; re-probe 0.16. No blocking findings.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Jev-driven fixes above (vacuous pass, decimal shapes, visual-certainty
  rejection) — FIXED, re-probed 0.16.
- RTL table cell-order qualification needs measured tables and belongs
  to worker qualification; the P0 case here pins direction presence, not
  order — recorded, not claimed.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
ocr_worker module, before a normal merge commit.
