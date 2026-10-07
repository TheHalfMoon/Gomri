# P03-G2 — Storage Seams and Presenton-State Adapters

**Parent:** #19
**Issue:** #22
**Canonical base:** `b475c631085ad479072d18f9f47e520447614750` (P03-G1 merged)

## Goal

Define narrow Gomrey-owned storage seams and prove adapters can map
imported Presenton state into Gomrey-owned contract models without
rewriting the editor and without any database migration.

## Scope

- `servers/fastapi/gomrey/contracts.py`: Pydantic v2 frozen records for the
  storage-relevant models (Workspace, SourceArtifact, SourceUnit,
  IngestionManifest, Job, StageAttempt, Artifact, ArtifactRevision, plus
  NarrativeSection). No SQLAlchemy, no engine, no network; pydantic was
  already required by FastAPI, so no new dependency surface.
- `servers/fastapi/gomrey/seams.py`: `CanonicalStore` and `BlobStore`
  protocols with the canonical-vs-rebuildable split, plus deterministic
  in-memory implementations for tests and adapter qualification.
- `servers/fastapi/gomrey/adapters.py`: pure read-only duck-typed functions
  projecting `PresentationModel`/`SlideModel` rows to Artifact,
  ArtifactRevision, and structural NarrativeIR dicts. Owner-scope rule is
  explicit (owner UUID becomes tenant and default workspace scope; unowned
  rows map to a named unowned scope, never ambient access).
- Packaging includes `gomrey*` in `pyproject.toml`.
- Deterministic pytest suites needing no database and no network.

## Out of scope

Database migrations, new tables, vector/graph servers, editor rewrites,
semantic claim extraction (later ingestion grains).

## Local qualification before commit

- `python -m py_compile` on all new files: PASS.
- Root Node suite plus secret/fixture/platform/release validators: PASS.
- pytest could not execute in this Windows environment (no `uv`; system
  Python 3.14 exceeds the backend's `<3.12` bound), so exact-head GitHub
  Actions is the authoritative pytest gate for this grain. No local pytest
  PASS is claimed.
- `git diff --check`: PASS.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable
  (`PSTACK_NOT_EXECUTED`, investigated per #19 trail).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including the FastAPI pytest suite with the
new `test_gomrey_*` modules, before a normal merge commit.
