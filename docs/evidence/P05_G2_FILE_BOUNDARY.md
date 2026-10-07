# P05-G2 — Hostile File Boundary

**Parent:** #33
**Issue:** #35
**Canonical base:** `8d59c5e9d0740fe717c237c0e86aeeeb8b760338` (P05-G1 merged, post-merge CI green)

## Goal

Safe local-file handling on the G1 admission path: traversal-proof
paths, MIME truth over extension claims, shared-budget enforcement, and
active-content denial — with legitimate files passing untouched.

## Scope

- `servers/fastapi/gomrey/file_boundary.py`: `normalize_path`
  containment; `sniff_mime` magic-byte identification;
  `reconcile_mime` extension/content/declaration agreement (spoof,
  executable, and raw-SVG-at-this-boundary refused);
  `enforce_file_budgets` spending six hostile-input dimensions from one
  shared ResourceBudget; `check_archive_entry` containment per member;
  `scan_active_content`/`deny_active_content` (script, event handlers,
  javascript: URIs, foreignObject, XXE entities, server-side code);
  `TempLeaseRegistry` temp lifecycle; composed `file_admission_report`.
  Pure logic, no FS writes, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_file_boundary.py`: 6 adversarial
  tests (traversal battery, spoof/executable, active-content battery,
  budget exhaustion incl. bomb shapes, temp lifecycle, legit pass-through).
- Package exports extended.

## Out of scope

URL policy (G3), parser normalization/quarantine exit (G4), actual
worker sandboxing, SVG sanitizer path (later grain).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (9 modules incl. new file_boundary): 52 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (system python lacks the
  uv-locked deps; pre-existing env gap, not caused by this change).
- Adversarial self-test caught 2 real defects pre-commit: `foreignobject`
  and `<!entity` regexes written in camel/upper case never matched the
  lowercased scan text, so 2 of 5 hostile payloads passed silently. Fixed
  to lowercase, battery re-green. This is the boundary working as
  designed: the tests demonstrate hostile inputs fail, not just that
  valid ones pass.
- Graft wiring rebuilt (3 files replayed, rest cached); ask confirms the
  grain is additive over gateway/budgets with no downstream dependents.
- TypeSafe Jev `jev-1.13.0` (real): fail-closed-weakened 0.08,
  legit-blocked 0.09. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review of the 3 reviewable
  files; findings adjudicated below, not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- Delegation review: `sniff_mime` returns `text/plain` for undecodable
  UTF-8 failures as None — callers treat None as unknown, not trusted;
  NOT_APPLICABLE.
- Delegation review: SVG refused at this boundary rather than
  sanitized — intentional routing to the later sanitizer path, documented
  in out-of-scope; NOT_APPLICABLE.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
file_boundary module, before a normal merge commit.
