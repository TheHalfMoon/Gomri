# P07-G3 — Connector Sync Contracts

**Parent:** #53
**Issue:** #56
**Canonical base:** `cbe772bc79fbe79e09f87f84239299ded64c4cff` (P07-G2 merged)

## Goal

Sync over time without silent truth-upgrades: opaque cursors with
revision identity, tombstone deletions, stale-marked partials,
secret-less credential handles, preserved ACL denies, and explicit
freshness.

## Scope

- `servers/fastapi/gomrey/connector_sync.py`: `CredentialHandle`
  (no secret field by construction, scoped issue, forward-only
  refresh, revocation/expiry/scope denial); `SyncCursor`;
  `apply_sync` (mandatory per-sync inventory, ghost-tombstone refusal,
  empty-revision and double-revision refusal, cursor+revision pinned
  before/after with no advance on interruption, partial-stale status
  with pending coordinates); `map_acl` (denies preserved, unknown
  shapes refused); `freshness` flags; backoff reusing P04
  `backoff_seconds`. Pure logic, no providers, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_connector_sync.py`: 4 tests
  (credential lifecycle + field-absence pin, upserts/tombstones/failure
  battery, interruption coordinates, backoff/ACL/freshness).
- Package exports extended.

## Out of scope

Provider adapters, OAuth flows, worker processes (later
qualification); retrieval consumption of freshness flags (P08 must
filter `is_fresh=False` rather than assume it).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (18 modules incl. new connector_sync): 94 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over jobs/gateway (backoff reuse verified).
- TypeSafe Jev `jev-1.13.0` (real): handles-clean 0.08;
  stale-as-fresh trajectory 0.23 → 0.34 → 0.25 → 0.14 across three
  genuine fixes: (1) `new_revision` accepted-but-dropped, now pinned in
  receipts with no advance on interruption; (2) empty revisions and
  intra-batch double-revisions refused; (3) inventory made mandatory,
  closing the ghost-tombstone path. Residual: provider-opaque revision
  strings cannot be monotonicity-checked generically, and consumers must
  read the freshness flag — contract boundaries owned by the adapter
  layer and P08, recorded in out-of-scope.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Three Jev-driven hardenings above — all FIXED and re-probed.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
connector_sync module, before a normal merge commit. Merge closes #56.
