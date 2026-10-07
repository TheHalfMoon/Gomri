# P08-G2 — Citation Locators and Resolver

**Parent:** #61
**Issue:** #63
**Canonical base:** `f224d222f0136523775d6fa3e627a68b004d7ab7` (P08-G1 merged)

## Goal

Pointers that resolve or fail loudly: per-source-family locators with
deterministic IDs, resolved against the assembled IR with coordinate
agreement — never rendered as support when broken.

## Scope

- `servers/fastapi/gomrey/citations.py`: five disjoint locator kinds
  (document, web, video, spreadsheet, image) with per-kind required
  fields and shape validation; `citation_id` from canonical JSON
  encoding; `BrokenCitation` typed error; `resolve` checking unit
  existence, source match, and page/snapshot/timestamp/bbox agreement.
  Pure logic, no rendering, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_citations.py`: 2 dense tests
  (all five families resolve with stable IDs; nine breakage shapes
  fail loudly).
- Package exports extended.

## Out of scope

Evidence bundles and sufficiency (G3); claim-support classification
(P09); renderer integration (P11).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (21 modules incl. new citations): 103 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over ir_provenance/source_parity.
- TypeSafe Jev `jev-1.13.0` (real): unresolved-support 0.07,
  unstable/ambiguous 0.06. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review (including the
  pre-commit simplification of resolve fallbacks into uniform IR-key
  lookups); no BLOCKING findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Pre-commit simplification (uniform source_id+unit_id keys on all
  kinds instead of per-kind fallback chains) — applied before tests.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
citations module, before a normal merge commit.
