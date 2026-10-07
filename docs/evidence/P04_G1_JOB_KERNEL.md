# P04-G1 — Durable Job Kernel

**Parent:** #26
**Issue:** #27
**Canonical base:** `c07105b2fc730472f7eb065383770789003e3255` (P03 complete)

## Goal

Pure deterministic job kernel: closed state machine, idempotency memoization,
checkpoint/resume tokens, transient/permanent classification, deterministic
bounded backoff, cancellation, and deadline checks. No database, no network,
no new dependencies.

## Scope

- `servers/fastapi/gomrey/jobs.py`: `transition` over an explicit legal map
  with `IllegalTransition` on any other edge; `IdempotencyLedger` where the
  first claim wins and replays observe the stored outcome (`unknown` is never
  silently upgraded); `DurableJob` with ordered stage checkpoints, opaque
  resume tokens that reject unknown stages, and ISO-8601 deadline checks;
  `classify_failure`/`should_retry`/`backoff_seconds` with a bounded,
  jitter-free schedule.
- `servers/fastapi/tests/test_gomrey_jobs.py`: 8 deterministic tests.
- Package exports extended in `gomrey/__init__.py`.

## Out of scope

Persistence backends, unit-manifest accounting (G2), budgets/progress
reconciliation (G3), worker wiring.

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Standalone stdlib smoke run of the kernel (transitions, checkpoint resume,
  backoff, retry): PASS.
- Root Node suite and repo validators: PASS. `git diff --check`: PASS.
- pytest runs in exact-head CI (backend bound prevents local execution); no
  local pytest PASS is claimed.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable
  (`PSTACK_NOT_EXECUTED`, investigated per #19 trail).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including FastAPI pytest with the new job
module, before a normal merge commit.
