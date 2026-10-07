# P04-G3 — Budgets, Progress, and Reconciliation

**Parent:** #26
**Issue:** #31
**Canonical base:** `d5bf717c0c78fb677ff21c39136535d7182e1a90` (P04-G2 merged)

## Goal

Resource budgets with truthful partial states on exhaustion, structured
progress events, and reconciliation of unknown outcomes that never upgrades
by assumption. Pure logic, no database, no network, no new dependencies.

## Scope

- `servers/fastapi/gomrey/budgets.py`: `ResourceBudget` with named caps and
  explicit `BudgetExhausted`; `progress_event` matching the MCP Tasks/Job
  Engine progress shape (never a correctness claim); `reconcile`, which
  resolves unknown idempotency outcomes only through an explicit re-check
  callback and returns settled outcomes without re-running side effects.
- `servers/fastapi/tests/test_gomrey_budgets.py`: 4 deterministic tests.
- Package exports extended.

## Out of scope

Worker wiring, queue admission/fairness (P16 operations), ingestion
pipeline wiring (P06).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Standalone smoke run (budget spend, progress math, reconcile honesty): PASS.
- Root Node suite and repo validators: PASS. `git diff --check`: PASS.
- pytest runs in exact-head CI; no local pytest PASS is claimed.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable
  (`PSTACK_NOT_EXECUTED`, investigated per #19 trail).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including FastAPI pytest with the new budgets
module, before a normal merge commit.
