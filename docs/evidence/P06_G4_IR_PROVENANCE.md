# P06-G4 — Coverage Verification and IR Provenance

**Parent:** #43
**Issue:** #47
**Canonical base:** `dc0906f71431357360a53ecd7f4477704e7aa8ff` (P06-G3 merged, post-merge CI green)

## Goal

Finish the P06 ingestion contract: assembled Source IR carries an
unbroken provenance chain on every unit, and declared units reconcile
against emitted records through the P04 ledger — silent drops fail
loudly, partials carry exact coordinates.

## Scope

- `servers/fastapi/gomrey/ir_provenance.py`: `assemble_ir`
  (cross-record source/tenant/workspace equality, per-unit parser and
  agreement provenance, legal states, digest check — source mixing
  refused as unsafe); `verify_coverage` (P04 UnitLedger declare/mark
  reconciliation, duplicate-emission and unresolvable-record refusal,
  silent-drop exception with coordinates, complete/partial verdicts with
  exact unresolved units; skip/duplicate receipts enforced by the
  ledger, with a caught-and-removed draft wart that would have invented
  fallback reasons). Pure logic, no new deps.
- `servers/fastapi/tests/test_gomrey_ir_provenance.py`: 4 tests
  (assembly completeness, mixing refusal, complete/partial/drops,
  receipt enforcement).
- Package exports extended.

## Out of scope

Worker processes and model weights (later qualification), retrieval
(P08), fetcher/connector wiring (P07).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (15 modules incl. new ir_provenance): 83 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over router/structure/ocr/accounting.
- TypeSafe Jev `jev-1.13.0` (real): mixing/gaps 0.06, drops-hidden
  0.12. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Self-review caught a fallback-reason invention wart pre-commit
  (would have masked malformed skip/duplicate records) — removed so
  the ledger enforces receipts; covered by test.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
ir_provenance module, before a normal merge commit. Merge closes #47.
