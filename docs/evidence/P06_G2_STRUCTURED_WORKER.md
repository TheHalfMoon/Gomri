# P06-G2 — Structured Worker and Baseline Qualification

**Parent:** #43
**Issue:** #45
**Canonical base:** `9471836fb137a5362ce0971e8b34d01894e0f701` (P06-G1 merged)

## Goal

Bind the structured paths without vendoring weights: a
capability-bounded worker envelope, the LiteParse baseline as a frozen
comparator, a pure Docling-shaped output mapping, and
measurement-only qualification gates.

## Scope

- `servers/fastapi/gomrey/structure_worker.py`: `WorkerEnvelope` /
  `admit_worker` (known workers only, cancellation/timeout/digest
  checks, network/secrets refused, invocation/timeout budgets);
  `LITEPARSE_BASELINE` frozen comparator identity; `KNOWN_WORKERS`;
  `map_structured_output` (pages/sections/tables/figures to
  ParserIntermediate with provenance, synthetic fixtures in tests);
  `DOCLING_ADOPTION` + `DOCLING_QUALIFICATION_BARS` as data;
  `check_qualification` (coverage, conflicts, uncertain, time, weight,
  license, resource bars plus beats_baseline). Pure logic, no
  subprocess, no models, no network, no lockfile change.
- `servers/fastapi/tests/test_gomrey_structure_worker.py`: 4 tests
  (baseline identity, envelope allow/deny battery, mapping incl.
  tables/figures and malformed shapes, qualification pass/fail).
- Package exports extended.

## Out of scope

Adding the Docling DEPEND package, model weights, worker processes,
OCR workers (G3), IR provenance completion (G4). The DEPEND step lands
only with its exact LICENSE blob, resource profile, and a winning
benchmark run through these gates.

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (13 modules incl. new structure_worker): 75 PASS
  (one first-run NameError — missing `score_run` import in the new test
  — fixed immediately, re-green).
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over parser_router/parser_boundary/gateway.
- TypeSafe Jev `jev-1.13.0` (real): authority-leak 0.03,
  default-without-merit 0.17. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Delegation review: `LITEPARSE_BASELINE` carries a ledger anchor string
  rather than a live version probe — intentional (frozen comparator, no
  import-time coupling to the subprocess service); NOT_APPLICABLE.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
structure_worker module, before a normal merge commit.
