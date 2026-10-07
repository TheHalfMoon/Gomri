# P08-G1 — Layered Retrieval Pipeline

**Parent:** #61
**Issue:** #62
**Canonical base:** `7fbaf62c54df2d18f3230d766c841dede4d7c520` (P07 exit merged)

## Goal

Ordering discipline for retrieval: ACL before ranking, cheap signals
before expensive ones, explicit fusion, freshness filtering, diversity
caps — holding even when dense/visual/graph stages are absent.

## Scope

- `servers/fastapi/gomrey/retrieval_pipeline.py`: `acl_filter`
  (tenant/workspace first, denied counted); `lexical_overlap`
  deterministic channel; `exact_boost` (reorders kept records only);
  `fuse` (weighted combination, channel presence recorded, unknown or
  zero-sum weights refused); `apply_constraints` (stale excluded by
  default with count, labeled when included, per-source caps, limit);
  composed `retrieve`. Pure logic, no index servers, no embeddings, no
  new deps.
- `servers/fastapi/tests/test_gomrey_retrieval_pipeline.py`: 5 tests
  (ACL-first with counts, exact ordering, fusion explicitness,
  freshness/diversity, no-vector lexical retrieval).
- Package exports extended.

## Out of scope

Citation locators/resolver (G2), evidence bundle/sufficiency (G3),
index servers and embedding packs (later qualification).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (20 modules incl. new retrieval_pipeline):
  101 PASS (one first-run expectation arithmetic error in the new test
  itself — 2/3 vs 1/2 — fixed, re-green).
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over gateway/ir_provenance/connector_sync.
- TypeSafe Jev `jev-1.13.0` (real): ACL-bypass 0.06,
  silent-staleness 0.15. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
retrieval_pipeline module, before a normal merge commit.
