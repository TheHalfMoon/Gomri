# P05-G1 — Source Gateway Contracts and Admission

**Parent:** #33
**Issue:** #34
**Canonical base:** `1ae7adb47403f5977e6906e204befbc5a706ed47` (P04-G3 merged, 9/9 green)

## Goal

Admission boundary: no source silently enters trusted state. Every
admission lands in `quarantined`; only the explicit trust machine can
reach `trusted-for-retrieval`. Access is deny-by-default with
tenant/workspace scope and least privilege.

## Scope

- `servers/fastapi/gomrey/gateway.py`: trust lifecycle
  (`discovered/received/quarantined/validated/parsed/normalized/rejected/trusted-for-retrieval`)
  with legal transitions; `admit_source` validation (identity, type,
  origin, digest, provenance, access context, parser routing);
  `can_access` deny-by-default boundary; `AdmissionError` taxonomy
  (`unsupported/unsafe/malformed/limit/access-denied/remote-fetch-denied/parser/normalization/duplicate`);
  `content_identity`/`is_duplicate` deterministic dedup; `select_parser`
  deterministic routing. Pure logic, no DB, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_gateway.py`: 7 deterministic tests.
- Package exports extended.

## Out of scope

File-byte checks (G2), URL policy (G3), parser normalization and
quarantine exit (G4), worker wiring, connector sync (P07).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (8 modules incl. new gateway): 46 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (system python lacks the
  uv-locked deps; same pre-existing env gap as prior grains, not caused
  by this change).
- Graft wiring rebuilt (9191 nodes); dependency ask confirms the grain
  is additive over contracts/seams/budgets/jobs with no downstream
  dependents to break.
- TypeSafe Jev `jev-1.13.0` (real, not impersonated):
  invariant-violation 0.13, silent-loss 0.06, ambient-authority 0.05.
  No blocking signal; findings below adjudicated.
- PStack: no canonical install found (`pstack` not recognized);
  `PSTACK_NOT_EXECUTED`, does not halt this grain.
- Alibaba OCR: no OCR workflow installed in this repository
  (workflows are Docker Release, Electron Linux, R2 sync, Test All);
  hosted OCR not executable here. Delegation: exact-diff manual review
  of the 3 reviewable files against the security/provenance checklist;
  findings adjudicated below. Not represented as a hosted PASS.
- Dependabot alerts: disabled for this repository (403). Code scanning:
  no analysis found (404). Recorded, not claimed as green.

## Review findings

- Delegation review: admission entry at `quarantined` skips
  `discovered/received` — by design (fail-closed entry; those states
  serve pre-admission acquisition in G2/G3), NOT_APPLICABLE as a defect.
- Delegation review: redundant cross-tenant check after `can_access`
  — defense-in-depth, NOT_APPLICABLE.
- Jev probabilities all low-risk; no BLOCKING findings.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
gateway module, before a normal merge commit.
