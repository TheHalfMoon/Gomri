# P06-G1 — Parser Router and Ensemble Contracts

**Parent:** #43
**Issue:** #44
**Canonical base:** `6d126e634b93cba9638188c749380ce696b09905` (P05 exit merged, post-merge CI green)

## Goal

Deterministic routing and disagreement discipline before worker
qualification: cheap preflight signals, explicit workload classes,
bounded second-parser triggers, conflict-marked reconciliation, and a
benchmark harness where challengers win only by measurement.

## Scope

- `servers/fastapi/gomrey/parser_router.py`: `preflight` byte signals;
  `classify_workload` explicit rules; `route` with bounded escalation
  (unknown workloads never run unchallenged); `check_second_parser_budget`;
  `reconcile_units` (agree/conflict/uncertain, challenger text preserved,
  never averaged); `to_source_ir` (one record per unit, dual-parser
  provenance, non-agreeing states marked uncertain); `BenchmarkCase` /
  `score_run` with mandatory incumbent measurement. Pure logic, no
  models, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_parser_router.py`: 6 tests
  (native/scanned/table/unknown routing, budget cap, reconciliation
  honesty, IR provenance, benchmark promotion rules).
- Package exports extended.

## Out of scope

Docling/PaddleOCR worker qualification (G2/G3), IR provenance
completion (G4), fetcher workers (P07).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (12 modules incl. new parser_router): 71 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft ask confirms the grain extends the P05 parser boundary
  additively.
- TypeSafe Jev `jev-1.13.0` (real): first promotion-integrity probe
  scored an elevated 0.42. Investigation found a real defect:
  `BenchmarkRun.baseline_coverage` defaulted to 0.0, so a caller that
  forgot the incumbent measurement got `beats_baseline=True` for free.
  Fixed by making the baseline mandatory (pinned by test); re-probe
  scored 0.11. Silent-loss/ambient probe: 0.18. No blocking findings.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Jev-driven fix above (baseline mandatory) — FIXED, re-probed 0.11.
- `to_source_ir` marks "unchallenged" single-parser units as
  `accounted` (tracked, not lost) rather than `verified`: consistent
  with the P03 contract state semantics; NOT_APPLICABLE as a defect.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
parser_router module, before a normal merge commit.
