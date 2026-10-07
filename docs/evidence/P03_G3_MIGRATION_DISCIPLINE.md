# P03-G3 — Migration Discipline and P03 Exit Evidence

**Parent:** #19
**Issue:** #24
**Canonical base:** `cc3354863221a1ed9a6c41b48b2729e45755d9b0` (P03-G2 merged)

## Goal

Lock migration discipline with a deterministic DB-free test and record
P03 exit evidence. No migration files are modified in this grain.

## Scope

`servers/fastapi/tests/test_gomrey_migration_discipline.py` parses the 24
alembic files with `ast` (never executes them) and enforces:

- every file declares `revision` and `down_revision` (plain or annotated);
- exactly one root and one head with a continuous chain;
- no `drop_table`/`drop_column` inside any `upgrade()` except two exact
  grandfathered donor revisions (`026c0ba8b35c` token-table consolidation,
  `d0a2b4c6e8f1` username-only settings rebuild), each with a staleness
  guard so the exception map cannot silently rot.

`downgrade()` reversals are standard alembic practice and out of scope.
Legacy-database stamping remains covered by `tests/unit/test_migrations.py`.
Destructive storage changes require a new governed migration grain that
extends the exception map explicitly.

## P03 exit evidence

- G1 (issue #20, PR #21): 23 versioned JSON contract schemas plus a
  dependency-free validator; tenant/workspace identity and no-silent-loss
  enforced by schema and test.
- G2 (issue #22, PR #23): Pydantic storage contracts, CanonicalStore/BlobStore
  seams with in-memory implementations, and read-only Presenton-state
  adapters proven by deterministic pytest with no database and no network.
- G3 (this grain): migration chain locked as above.
- P03 exit (MASTER_PLAN): contracts have serialization/schema tests, and
  adapters map the imported Presenton state into Gomrey-owned models without
  rewriting the editor. Satisfied on the G1+G2+G3 evidence.

## Local qualification before commit

- New discipline tests: **4/4 PASS** via direct stdlib execution
  (identical code to what pytest collects; full pytest runs in CI).
- `python -m py_compile` on the new test: PASS.
- Root Node suite and repo validators: PASS. `git diff --check`: PASS.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable
  (`PSTACK_NOT_EXECUTED`, investigated per #19 trail).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including FastAPI pytest with the new
discipline module, before a normal merge commit.
