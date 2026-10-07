# P04-G2 — Source-Unit Accounting

**Parent:** #26
**Issue:** #29
**Canonical base:** `89b244d11d591ce63b892d53e05dcd361bf291e1` (P04-G1 merged)

## Goal

Deterministic unit ledger enforcing accounted == declared with
silent_drop_count == 0, proven by a seeded 1,000-unit kill/restart torture
test. Pure logic, no database, no network, no new dependencies.

## Scope

- `servers/fastapi/gomrey/accounting.py`: `UnitLedger` with duplicate
  declaration rejection, unknown-unit rejection, terminal-state validation
  (skipped needs a reason, duplicate needs a canonical id), counts with
  computed silent drops, incomplete/partial/complete status, and
  snapshot/restore that refuses marks for undeclared units.
- `servers/fastapi/tests/test_gomrey_accounting.py`: 6 tests including a
  seeded torture run that snapshots and restores after every chunk and
  finishes 1,000/1,000 accounted with zero silent drops.
- Package exports extended.

## Out of scope

Persistence backends, budgets/progress reconciliation (G3), ingestion
pipeline wiring (P06).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Standalone seeded 1,000-unit smoke run: PASS (903 verified in sample).
- Root Node suite and repo validators: PASS. `git diff --check`: PASS.
- pytest runs in exact-head CI; no local pytest PASS is claimed.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable
  (`PSTACK_NOT_EXECUTED`, investigated per #19 trail).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including FastAPI pytest with the new
accounting module, before a normal merge commit.
