# P09-G2 — Verification Engine (Deterministic + Provider Seam)

**Parent:** #69
**Issue:** #71
**Canonical base:** `7b8b720c9f562eccf87bae5df5c3bcd6475d803b` (P09-G1 merged)

## Goal

Classify whether a bound claim is supported, partially supported,
contradicted, unsupported, or unverifiable — deterministically first,
with providers as opinions that can never overrule hard policy.

## Scope

- `servers/fastapi/gomrey/verification.py`: `VERDICTS`
  (supported/partially_supported/contradicted/does_not_establish/
  unresolved/blocked); `STANCES` (supports/contradicts/context);
  `check_quantity_agreement` (claim numbers/dates must appear in
  supporting views; mismatches named); `verify_claim` (binding
  refusal inherited; missing views mean does_not_establish;
  stance tally; quantity/date gates; override tripwires in claim or
  any view force unresolved; provider verdicts require
  provider+model_revision identity and are recorded with
  provider-overruled-by-policy whenever they reach past a
  deterministic failure); verdict digests (canonical JSON sha256).
  Pure logic, no model calls, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_verification.py`: 7 tests
  (supported with quantity agreement + digest stability;
  contradicted-only vs mixed partial; quantity mismatch downgrade;
  unbindable abstains; missing views judge nothing; provider
  overreach recorded and refused, identity required; claim and
  evidence injection both force unresolved).
- `servers/fastapi/gomrey/__init__.py`: additive exports only.

## Out of scope

Decision graph/synthesis/calibration (P09-G3); challenger-model
adapters beyond the identity-carrying seam; semantic entailment
beyond deterministic agreement (provider-backed, still non-authoritative).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (24 modules incl. new verification): 124 PASS
  (117 prior + 7 new).
- Root Node suite: 48 PASS (re-verified at push time).
- `git diff --check`: PASS.
- Graft: `check` STALE (expected: new module); `ask` confirms
  additive leaf, no existing callers; graph refreshed locally,
  cache not committed.
- TypeSafe Jev (real, CLI 2026.919.0 / model jev-1.13.0):
  model-authority probe 0.07. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review (deterministic
  gate + seam + 7 tests + exports; no ambient authority, no silent
  upgrade path); no BLOCKING findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow before a normal merge commit. Merge closes #71.
