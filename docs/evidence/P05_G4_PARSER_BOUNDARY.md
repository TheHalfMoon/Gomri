# P05-G4 — Parser Boundary and Quarantine Exit

**Parent:** #33
**Issue:** #37
**Canonical base:** `002b35169c63049795ee1d2a3ee9c2dff4b8bdbc` (P05-G3 merged, post-merge CI green)

## Goal

Close the gateway: parsers cannot mutate trusted state; only the
normalization gate releases trusted Source IR, and only from the
`normalized` trust state — with taint, classification, provenance, and
revocation semantics intact.

## Scope

- `servers/fastapi/gomrey/parser_boundary.py`: `ParserAdapter` protocol
  (quarantined view in, intermediate out, no store/ledger/network
  parameters); `run_parser` (identity binding, typed crash wrapping that
  keeps the exception shape but drops raw messages); `validate_intermediate`
  gate (digest binding, unique IDs, legal kinds, text checks, char/unit
  budgets); `taint_content` (data-not-instructions wrapper with
  instruction-pattern markers, text preserved exactly, no safety claims);
  `classify_sensitivity` (secret/credential/PII hooks); `promote_to_trusted`
  (normalized-state only, emits TrustedRelease with evidence spans);
  `revoke_source` (projection invalidation with audit-preserving
  tombstone). Pure logic, no new deps.
- `servers/fastapi/tests/test_gomrey_parser_boundary.py`: 6 tests
  (isolation surface, typed crash, gate rejections, normalized-only
  promotion, taint honesty, sensitivity + revocation).
- Package exports extended.

## Out of scope

Format-specific parser quality (P06), fetcher worker (P07), retrieval
(P08), SVG sanitizer path (later grain).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (11 modules incl. new parser_boundary): 65 PASS.
- Root Node suite: 48 PASS, including the fixture-policy guard that
  caught a real violation in this grain's first draft: committed
  credential-shaped test literals (`AKIA…`, private-key header) were
  flagged by `check-fixtures`. Fixed by runtime-assembling the shapes so
  no scannable credential literal is committed; guard re-green. Raw
  crash-message leakage was likewise caught by test and fixed to
  shape-only. Both are the boundary working as designed.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft rebuilt; ask confirms gateway.py owns the trust machine this
  grain extends, additive with no downstream breakage.
- TypeSafe Jev `jev-1.13.0` (real): quarantine-bypass 0.09,
  overclaim/provenance-loss 0.08. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Delegation review: crash message dropped but exception type name kept
  — intentional bounded operator signal, documented and pinned by test;
  NOT_APPLICABLE as a leak.
- Delegation review: taint markers are heuristic metadata, explicitly
  not a completeness claim; matches MASTER_PLAN ("do not claim prompt
  injection can be perfectly solved"); NOT_APPLICABLE.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
parser_boundary module, before a normal merge commit. Merge closes #37
and completes P05 pending the exit check.
