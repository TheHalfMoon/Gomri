# P09-G3 — Decision Graph / Synthesis + Calibration

**Parent:** #69
**Issue:** #72
**Canonical base:** `7f5ba652df5b19c5002b21dfa19e0300406e6fa8` (P09-G2 merged)

## Goal

Traceable decisions over verified claims: a support graph that is
never flattened into an answer string, synthesis that includes only
verified claims with conflicts exposed, calibration that is earned by
measurement, and disagreement that abstains instead of averaging.

## Scope

- `servers/fastapi/gomrey/decisions.py`: `build_graph`
  (dangling refs and orphan citations refused); `graph_digest`
  (canonical sha256); `make_decision` (question, claims, evidence,
  constraints, assumptions, uncertainty, alternatives, conclusion,
  status, version — all validated); `synthesize` (only
  supported/partially_supported enter; others omitted with verdicts;
  partial support and contradictions listed as conflicts; conflict
  without an alternative abstains with eligible claims withheld);
  `register_profile` (50+ samples, named benchmark, bounded
  abstention rate); `route_workload` (calibrated preference, else
  deterministic-only with reason); `adjudicate` (deterministic
  first, independent challenger else ABSTAIN/UNRESOLVED, never
  averaged); `DecisionStore` protocol + `MemoryDecisionStore`
  (copy-on-put/get, tenant-isolated). Pure logic, no generation,
  no model calls, no new deps.
- `servers/fastapi/tests/test_gomrey_decisions.py`: 7 tests
  (dangling/orphan/unknown-kind refused; verified-only synthesis
  with exposed contradiction; conflict-without-alternative
  abstains; empty synthesis abstains with omissions; calibrated
  routing vs deterministic fallback + sample floor; disagreement
  abstains on independent divergence; store roundtrip isolated).
- `servers/fastapi/gomrey/__init__.py`: additive exports only.

## Out of scope

Generated prose (downstream of this record); challenger-model
adapters; benchmark datasets (P15 arena); UI surfaces (P10).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (25 modules incl. new decisions): 131 PASS
  (124 prior + 7 new).
- Root Node suite: 48 PASS (re-verified at push time).
- `git diff --check`: PASS.
- Graft: `ask` confirms additive leaf, no existing callers; graph
  refreshed locally, cache not committed.
- TypeSafe Jev (real, CLI 2026.919.0 / model jev-1.13.0):
  conflict-hiding/autonomy probe 0.08. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review (graph +
  synthesis + calibration + 7 tests + exports; no hidden conflict
  path, no averaging); no BLOCKING findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow before a normal merge commit. Merge closes #72.
