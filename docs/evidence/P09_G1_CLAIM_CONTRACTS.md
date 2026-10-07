# P09-G1 — Claim Contracts + Evidence Binding

**Parent:** #69
**Issue:** #70
**Canonical base:** `933656c2390914e47c3972b62bd7053f31b38f50` (P08 exit merged, post-merge CI 9/9 green)

## Goal

Durable claim records that either bind to exact evidence or are
explicitly unsupported. The binder reports; the P09-G2 verifier
decides. Insufficient evidence is never re-widened into support
(P08 exit obligation 3).

## Scope

- `servers/fastapi/gomrey/claims.py`: `Claim` (identity, text,
  deterministic normalized view, tenant/workspace isolation, evidence
  refs, support/contradiction links, uncertainty, status, verification
  state, version, timestamps, derivation, source provenance);
  `VERIFICATION_STATES` (unverified/verifying/supported/
  partially_supported/contradicted/does_not_establish/unresolved/
  blocked, matching JEV_BUILD_POLICY families); `CLAIM_STATUSES`,
  `UNCERTAINTY_LEVELS`, `DERIVATION_KINDS`; `make_claim`
  (self-refs, duplicates, bad enums, version 0, bad derivation,
  sourceless provenance refused); `normalize_claim` (stable, not
  semantic); `detect_policy_override_attempt` (narrow tripwire,
  never authority); `claim_digest` (canonical JSON sha256);
  `bind_claim_to_bundle` (cross-project refused; missing refs
  refused; stale/contradictions/omissions/override flags reported,
  never upgraded; span-without-citation-id blocks binding);
  `ClaimStore` protocol + `MemoryClaimStore` (copy-on-put/get,
  tenant-isolated keys). Pure logic, no models, no network, no new
  deps.
- `servers/fastapi/tests/test_gomrey_claims.py`: 12 tests (direct
  support binds; empty refs never bind; contradictions block;
  missing/deleted refused; duplicates/self refused; malformed
  refused; cross-project refused; stale surfaced with strict/relaxed;
  injection flagged and blocked; digest stable/sensitive; store
  roundtrip with isolation).
- `servers/fastapi/gomrey/__init__.py`: additive exports only.

## Out of scope

Verification verdicts and provider/challenger routing (P09-G2),
decision graph/synthesis/calibration (P09-G3), store backends beyond
memory (later grains behind the same protocol).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (23 modules incl. new claims): 117 PASS
  (105 prior + 12 new).
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap:
  unrelated collection errors for non-Gomrey tests locally).
- Graft: initial `check` STALE (expected: new module); `ask`
  confirms additive leaf (bind calls override-tripwire +
  AdmissionError only; no existing callers touched); graph refreshed
  locally, cache not committed.
- TypeSafe Jev (real, CLI 2026.919.0 / model jev-1.13.0):
  invariant-preservation 0.11, provenance/no-drop 0.09. No blocking
  signal. Store-hardening applied pre-commit (copy-on-put/get).
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review (new pure-logic
  module + 12 tests + export additions; found and fixed store
  aliasing pre-commit); no BLOCKING findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow before a normal merge commit. Merge closes #70.
