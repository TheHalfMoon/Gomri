# P01 Presenton Import and Qualification Evidence

**Phase:** P01 — Presenton full-base import
**Status:** P01_QUALIFIED_CANDIDATE
**Date:** 2026-10-05

## Canonical Gomrey base

- Base branch: `main`
- Base commit: `204cebee93d3b75ae610ac2ddeb784adcf8f02b9`
- P01 branch: `p01/presenton-base-import`
- Pull request: `#4`
- Qualified code/CI head: `7b7c6144c9e8fca7384474eab8450ecdd688f2d3`

## Admitted donor identity

- Repository: `presenton/presenton`
- Commit: `e158a014cc1e29da0a27fe539db08dcbcea5c69d`
- Tree: `dbf6834b8519e25f4dfd936dc8c099ce17b9e96e`
- Commit timestamp: `2026-10-02T18:49:27Z`
- LICENSE blob: `5566576249c0c99a84455b2fc8454e03a9b18e20` (11,340 bytes)
- NOTICE blob: `ba5df534c4549ed7459a34667a506baa5cbd5fea` (1,274,338 bytes)

The donor `main` revision was reverified immediately before import and still resolved to the exact admitted commit above.

## Import method and integrity

The donor was fetched into the existing Gomrey Git repository as a single exact commit using a temporary `presenton-upstream` remote and a shallow fetch. The donor tree was then checked out into the P01 branch. This avoids a second full-history clone while retaining exact donor Git objects and blob identities.

The only path collision between the pre-import Gomrey tree and the donor tree was root `README.md`.

Resolution:

- Gomrey keeps its canonical root `README.md`.
- The exact donor root README is preserved at `docs/donors/presenton/UPSTREAM_README.md`.
- No Presenton executable source file was rebranded during the import baseline grain.

Deterministic Git-object comparison result:

```text
donor_files                    = 11469
exact_matched_non_readme       = 11468
mismatches                     = 0
donor_readme_sha               = c710b98c44e7f4c22b3e83a26c0d8e12f25dcaca
preserved_readme_sha           = c710b98c44e7f4c22b3e83a26c0d8e12f25dcaca
donor_readme_preserved_exactly = true
```

Import baseline commit: `6a3bd8ab9f17185ae51a67b9d2350a3f0f3abd69`.

## Inherited donor baseline observations

`git diff --check` reports pre-existing whitespace and conflict-marker-like text in the imported donor snapshot, including the generated NOTICE corpus and some source files. These bytes are inherited from the exact donor snapshot and were intentionally not rewritten in the import baseline. The exact blob comparison above is the authority for import integrity.

The donor also contains a prebuilt ONNX blob of approximately 86.20 MB under `servers/fastapi/fastembed_cache/...`. It is below GitHub's hard object-size rejection threshold but above GitHub's recommended 50 MB size. P01 preserves it as donor baseline; later model/artifact lifecycle work may move such material behind Gomrey model-pack boundaries.

## Graft evidence

Graft `v0.21.1` built the imported code graph.

Initial import graph:

```text
code files = 787
nodes      = 8971
edges      = 23544
languages  = javascript, python, tsx, typescript
```

After the P01 credential-permission regression test was added:

```text
code files = 788
nodes      = 8972
edges      = 23548
languages  = javascript, python, tsx, typescript
```

Graft identified the principal P01 parity surfaces:

- `servers/fastapi/tests/test_presentation_generation_api.py`
- `servers/fastapi/tests/integration/test_presentation_generation_flow.py`
- `servers/fastapi/tests/unit/test_mcp_server_auth.py`
- `servers/fastapi/tests/unit/test_mcp_files_api.py`
- `servers/fastapi/tests/integration/test_auth_endpoints.py`
- `servers/nextjs/tests/presentation-autosave.test.mjs`
- `scripts/sync-presentation-export.test.mjs`
- `electron/build.js`

For the credential-permission repair, `graft blast` reported one changed area and no indexed dependents outside the diff at depth 2. The static source-contract regression test is intentionally not represented as a call-graph edge.

A later `graft check` invocation hung without producing a terminal verdict and was terminated. It is **not** represented as a PASS. Successful Graft build and blast evidence remain valid.

## P01 parity coverage

Existing test inventory used by the imported suites includes approximately:

```text
presentation generation API                         12 tests
presentation generation/export integration flow    28 tests
MCP auth/tool routing                               20 tests
MCP file API                                         4 tests
REST/auth integration                                6 tests
Next.js presentation autosave                        3 tests
repository presentation-export runtime               4 tests
```

The exact baseline import commit `6a3bd8ab9f17185ae51a67b9d2350a3f0f3abd69` passed GitHub Actions run `37244909334`:

- `Test FastAPI` — SUCCESS, including all pytest tests;
- `Test repository tooling` — SUCCESS, including repository tests and presentation-export runtime install/verification;
- `Test Next.js` — SUCCESS, including Node tests, ESLint, production build, and Cypress component tests.

The exact credential-hardening commit `3b5761958982ce560147bd00b77accef6c78fa00` passed GitHub Actions run `37248872673` with the same three jobs SUCCESS.

The current P01 candidate adds a lightweight Electron source qualification job: locked dependency install with packaging hooks disabled, TypeScript typecheck, Electron main-process compilation, and undefined-global checking. It intentionally does not package, sign, publish, or contact the donor release repository.

The same Electron source checks were also exercised locally on the authorized Windows qualification device using `npm ci --ignore-scripts --no-audit --no-fund`:

```text
npm run typecheck           = PASS (exit 0)
npm run build:ts            = PASS (exit 0)
check-main-no-undef         = PASS before cleanup; 37 Electron main JS files had no undefined names
```

The temporary `electron/node_modules` and `electron/app_dist` directories were then removed to reclaim disk. A later direct checker invocation after cleanup failed only because the deliberately removed `typescript` dependency was no longer present; that post-cleanup invocation is not a product test result and does not supersede the successful pre-cleanup qualification.

Final four-job exact-head run `37249330913` on `7b7c6144c9e8fca7384474eab8450ecdd688f2d3` completed **SUCCESS**:

- `Test FastAPI` — SUCCESS;
- `Test repository tooling` — SUCCESS;
- `Test Electron` — SUCCESS (locked install without packaging hooks, typecheck, compile, main-global check);
- `Test Next.js` — SUCCESS (tests, ESLint, production build, Cypress component tests).

## Self-hosted/startup qualification

On the authorized Windows qualification device:

```text
docker compose config --quiet = PASS
node --check start.js          = PASS
```

This proves the imported self-hosted configuration parses and the top-level startup script is syntactically valid. Full production deployment certification and bundled desktop installer qualification are later release responsibilities, not P01 claims.

## Security finding and repair

Alibaba Open Code Review delegation rules led the host semantic review to an inherited credential-file permissions issue in `start.js`: the Node startup path persisted `userConfig.json` and its backup with `0644`, while the configuration can contain provider API keys, cloud credentials, search keys, and access/refresh tokens. The Python user-config store already used owner-only `0600` semantics.

Repair commit: `3b5761958982ce560147bd00b77accef6c78fa00` (`fix: secure persisted provider configuration`).

The bounded repair:

- hardens an existing primary config to `0600` before backup copy;
- stores the backup with `0600`;
- creates temporary config files with exclusive `wx` creation and `0600` mode;
- stores the final primary config with `0600`;
- adds `scripts/start-config-permissions.test.mjs` and includes it in the root test command.

Local qualification:

```text
targeted permission tests = 2/2 PASS
root repository tests      = 14/14 PASS
git diff --check           = PASS
```

## Alibaba Open Code Review evidence

Tool: `open-code-review v1.12.11 (a758d9c)`.

The hosted OCR LLM scan could not execute because the configured Anthropic provider had no usable API credential in the current OCR runtime. No hosted-OCR PASS is claimed.

Official OCR delegation mode was executed instead.

For the security repair exact range `6a3bd8ab9f17185ae51a67b9d2350a3f0f3abd69..3b5761958982ce560147bd00b77accef6c78fa00`, OCR selected all 3/3 changed files:

- `package.json`
- `scripts/start-config-permissions.test.mjs`
- `start.js`

The tool supplied its JavaScript/package security and correctness rules; host semantic review under those rules found the inherited credential-file permission issue and verified the bounded repair. No material unresolved finding remains in that patch.

For the Electron CI workflow change, OCR selected `.github/workflows/test-all.yml` and supplied workflow-specific security/reliability rules. The final job uses repository-level `contents: read`, no secrets, no `pull_request_target`, no publishing, cached locked dependencies, and an explicit 20-minute timeout.

Evidence state:

```text
OCR_DELEGATION_COMPLETE
HOST_SEMANTIC_REVIEW_COMPLETE
HOSTED_LLM_SCAN_NOT_EXECUTED
HOSTED_SCAN_BLOCKER = configured provider credential unavailable
```

## TypeSafe Jev evidence

CLI: `jev v2026.919.0`
Model: `jev-1.13.0`

Exact repair commit `3b5761958982ce560147bd00b77accef6c78fa00`:

```text
material security/correctness regression probability = 0.27
suitable for exact-candidate CI probability           = 0.70
```

Final Electron CI patch after timeout hardening:

```text
material security/supply-chain/correctness risk probability = 0.21
appropriate for P01 Electron source qualification probability = 0.73
```

P01 phase-boundary check:

```text
probability that P01 requires fully packaged/signed Electron installers before closure = 0.08
```

This supports the canonical phase split: P01 qualifies the imported working source/runtime surfaces; installer packaging/signing remains a later release qualification responsibility.

Jev is a typed probabilistic reviewer, not merge authority. Deterministic tests and exact-head CI remain authoritative.

## Existing MCP/API baseline

The imported MCP server is built from the OpenAPI surface with explicit route maps/tool names and origin protection. Existing MCP auth/tool/file tests and REST auth tests are included in the FastAPI suite that passed on the exact code candidate.

P01 preserves this working MCP/API baseline; Gomrey's broader MCP Tasks, A2A, plugin, permission, and agent-first architecture begins in later planned phases behind Gomrey-owned contracts.

## Known donor limitations / nonclaims

The imported `DocumentsLoader` is a baseline, **not** Gomrey's target deep-ingestion engine. Verified donor behavior includes:

- `DECOMPOSE_TIMEOUT_SECONDS = 600`;
- sequential iteration over `self._file_paths`;
- scanned-PDF classification based on a sample of the first 5 pages with a text threshold;
- 300 DPI LiteParse OCR path for scanned PDFs;
- fallback parser after primary LiteParse failure.

Therefore P01 makes no claim that Presenton's imported ingestion path satisfies Gomrey's future 1,000+/10,000-page, no-silent-loss, multimodal, resumable source-accounting contract. That replacement is deliberately deferred to P04-P08.

Additional nonclaims:

- no Gomrey product-wide rebrand is claimed in P01;
- no Gamma source is imported;
- no NotebookLM-class RAG replacement is performed;
- no Docling/PaddleOCR/MinerU/Crawl4AI donor absorption is performed;
- no full Electron installer/package/signing qualification is claimed;
- no inherited donor defect is represented as fixed merely by importing the donor.

## P01 close rule

P01 is qualified for merge after this evidence closeout commit receives successful exact-head CI. Merge must use an ordinary merge commit with an exact-head guard. Post-merge verification must then bind canonical `main` and its triggered workflow run.
