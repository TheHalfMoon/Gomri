# P01 Presenton Import Evidence

**Phase:** P01 — Presenton full-base import  
**Status:** IMPORT_BASELINE_CANDIDATE  
**Date:** 2026-10-05

## Canonical Gomrey base

- Base branch: `main`
- Base commit: `204cebee93d3b75ae610ac2ddeb784adcf8f02b9`
- P01 branch: `p01/presenton-base-import`

## Admitted donor identity

- Repository: `presenton/presenton`
- Commit: `e158a014cc1e29da0a27fe539db08dcbcea5c69d`
- Tree: `dbf6834b8519e25f4dfd936dc8c099ce17b9e96e`
- Commit timestamp: `2026-10-02T18:49:27Z`
- LICENSE blob: `5566576249c0c99a84455b2fc8454e03a9b18e20` (11,340 bytes)
- NOTICE blob: `ba5df534c4549ed7459a34667a506baa5cbd5fea` (1,274,338 bytes)

The donor `main` revision was reverified immediately before import and still resolved to the exact admitted commit above.

## Import method

The donor was fetched into the existing Gomrey Git repository as a single exact commit using a temporary `presenton-upstream` remote and a shallow fetch. The donor tree was then checked out into the P01 branch.

This avoids a second full-history clone while retaining exact donor Git objects and blob identities.

The only path collision between the pre-import Gomrey tree and the donor tree was root `README.md`.

Resolution:

- Gomrey keeps its canonical root `README.md`.
- The exact donor root README is preserved at `docs/donors/presenton/UPSTREAM_README.md`.
- No Presenton executable source file was rewritten or rebranded during this import grain.

## Byte-level import verification

A deterministic Git-object comparison checked donor tree entries against the Gomrey index.

```text
donor_files                    = 11469
exact_matched_non_readme       = 11468
mismatches                     = 0
donor_readme_sha               = c710b98c44e7f4c22b3e83a26c0d8e12f25dcaca
preserved_readme_sha           = c710b98c44e7f4c22b3e83a26c0d8e12f25dcaca
donor_readme_preserved_exactly = true
```

Therefore every donor path except the intentional root README collision is staged with the exact donor blob/mode, and the displaced donor README is preserved byte-for-byte at the provenance path.

## Inherited donor baseline observations

`git diff --check` reports pre-existing whitespace and conflict-marker-like text in the imported donor snapshot, including the generated NOTICE corpus and some source files. These bytes are inherited from the exact donor snapshot and are intentionally not rewritten in the import baseline. The exact blob comparison above is the authority for import integrity.

Any later cleanup must be a separate reviewed change and must not silently mutate NOTICE/license material.

## Graft evidence

`graft v0.21.1` built and checked the imported code graph:

```text
code files = 787
nodes      = 8971
edges      = 23544
languages  = javascript, python, tsx, typescript
graph check = OK
```

The graph identified the key P01 parity surfaces, including:

- `servers/fastapi/tests/test_presentation_generation_api.py`
- `servers/fastapi/tests/integration/test_presentation_generation_flow.py`
- `servers/fastapi/tests/unit/test_mcp_server_auth.py`
- `servers/fastapi/tests/unit/test_mcp_files_api.py`
- `servers/fastapi/tests/integration/test_auth_endpoints.py`
- `servers/nextjs/tests/presentation-autosave.test.mjs`
- `scripts/sync-presentation-export.test.mjs`
- `electron/build.js`

Graft deep semantic summaries were not required for this import grain; the wiring graph is current and sufficient for targeted P01 parity work.

## Required P01 parity still open

The import baseline alone does **not** prove runtime parity. The following remain required before P01 can close:

- reproducible dependency installation/build path;
- presentation generation tests;
- existing editor/autosave/editing tests;
- PPTX export tests;
- PDF/export runtime tests;
- REST/auth tests;
- MCP auth/tool tests;
- local/self-hosted startup behavior where practical on the qualification device;
- Alibaba Open Code Review on the exact code candidate;
- TypeSafe Jev review bound to the exact code candidate;
- exact-head CI and post-merge verification.

## Current nonclaims

- No Gomrey rebrand is claimed in P01 import baseline.
- No Gamma source is imported.
- No OCR/RAG architecture replacement is performed.
- No runtime/build/test parity is claimed yet.
- No inherited donor finding is represented as fixed merely by importing it.
