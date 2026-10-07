# P08-G3 — Evidence Bundle and Sufficiency

**Parent:** #61
**Issue:** #64
**Canonical base:** `e4ce61cc3da884a7eae164861b9f478287914461` (P08-G2 merged)

## Goal

The bounded evidence set generation may consume, and the verdict that
tells generation to stop: sufficiency with abstention, contradictions
marked and escalated, omissions accounted.

## Scope

- `servers/fastapi/gomrey/evidence_bundle.py`: `EvidenceBundle` with
  all load-bearing fields (revisions, spans, retrieval identities,
  contradictions, omissions, scope, verification state);
  `build_bundle` (identity required, unaccounted drops and dangling
  contradiction refs refused); `bundle_digest` (canonical JSON sha256);
  `sufficiency_check` (sufficient/insufficient/needs_review with named
  reasons; stale handling; min_spans validation). Claim-support
  classification explicitly belongs to P09. Pure logic, no generation,
  no new deps.
- `servers/fastapi/tests/test_gomrey_evidence_bundle.py`: 2 dense
  tests (digest stability, build refusals, abstention/escalation
  matrix, stale allow/deny, min_spans validation).
- Package exports extended.

## Out of scope

Claim-support classification and verification loop (P09), renderer
integration (P11), index servers (later qualification).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (22 modules incl. new evidence_bundle):
  105 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over citations/retrieval_pipeline.
- TypeSafe Jev `jev-1.13.0` (real): weak-evidence 0.08,
  digest/fields 0.12. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review (including removal
  of a dead no-op branch pre-commit); no BLOCKING findings; not a
  hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
evidence_bundle module, before a normal merge commit. Merge closes #64.
