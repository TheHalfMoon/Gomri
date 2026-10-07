# P02-G4 — CI, SBOM, Security, Fixtures, and Release Baseline

**Parent:** #6
**Issue:** #17
**Canonical base:** `049b872da23d9e6c4c0c36401179f831e53e9a1f` (P02-G3c merge)

## Goal

Close the remaining P02 engineering-baseline requirements without redesigning
product architecture and without requiring Store, signing, or paid-service
credentials for ordinary CI.

## Scope

1. **Cross-platform CI baseline** — Linux stays the full integration path.
   `config/platform-support.json` is the machine-readable matrix. Windows and
   macOS run bounded source and package-configuration qualification only
   (`qualify-windows`, `qualify-macos` in `test-all.yml`).
2. **Dependency / SBOM baseline** — `scripts/generate-sbom.mjs` emits
   deterministic CycloneDX 1.6 documents for all four shipped surfaces (root,
   electron, nextjs, fastapi) from their lockfiles. Missing lockfiles or empty
   parses fail instead of silently omitting a surface. Tool identity and
   lockfile hashes are recorded. Generated artifacts are gitignored and
   uploaded by the `sbom-baseline` CI job.
3. **Security baseline** — `config/security-policy.json` defines deterministic
   public-CI gates with no hidden SaaS correctness dependency:
   `scripts/scan-secrets.mjs` (credential-leak guard),
   `scripts/validate-release-config.mjs` (donor-publish guard),
   lockfile pinning, and `npm audit` per JS surface gated by
   `config/security-allowlist.json` with rationale, expiry, and owner.
   Python is pinned with `uv sync --locked` and audited with `pip-audit`.
4. **Fixture and test-data policy** — `docs/FIXTURE_POLICY.md` and
   `config/fixture-policy.json` allow synthetic, public-redistributable, or
   explicitly licensed fixtures only, with provenance and regeneration
   requirements. `scripts/check-fixtures.mjs` fails visibly on denied material.
5. **Release artifact baseline** — `config/release-baseline.json` freezes the
   Gomrey-owned 0.1.0 version, app IDs, artifact templates, platforms, SBOM
   references, and donor-publish prohibitions. `scripts/validate-release-config.mjs`
   is the credential-free dry-run; `scripts/generate-release-manifest.mjs`
   binds the exact source commit and lockfile hashes. `docker-release.yml` now
   targets `ghcr.io/thehalfmoon/gomrey`, and the R2 sync workflow rejects donor
   `Presenton-*` artifacts and the `presenton-desktop` bucket.

## Version reset

P02-G4 resets the inherited `0.9.11-beta` donor-family version to Gomrey-owned
`0.1.0` across `package.json`, `electron/package.json`, lockfiles, and
`electron/version.json` (with Gomrey release URLs). The desktop uses a separate
appId, so this is a fresh application identity rather than a semver downgrade.
P16 owns GA versioning.

## Local qualification before commit

- Root repository suite: **43/43 PASS** (30 pre-existing + 13 new G4 contract tests).
- `node scripts/check-platform-support.mjs`: PASS (linux full-integration; windows/macos bounded).
- `node scripts/scan-secrets.mjs`: PASS (no credential-like matches in repository-owned files).
- `node scripts/check-fixtures.mjs`: PASS.
- `node scripts/validate-release-config.mjs`: PASS (versions aligned at 0.1.0; no donor publish target).
- `node scripts/generate-release-manifest.mjs --check-only`: PASS.
- `node scripts/generate-sbom.mjs`: PASS (root 93, electron 456, nextjs 879, fastapi 204 components; no surface omitted).
- Per-surface `check-dependency-audit.mjs` against live `npm audit` JSON: PASS on all three JS surfaces (145 GHSA allowlisted to 2027-04-05).
- `git diff --check`: PASS.
- Graft v0.21.1 worktree build: **9,059 nodes / 23,813 edges / 811 parsed files**. Blast over version, release, and workflow symbols stays inside the changed files plus known export-runtime version consumers that track `presentationExportVersion`, not the app version.
- Alibaba Open Code Review v1.12.12 delegation preview: **27 reviewable / 31 total** (lockfiles and prose evidence outside semantic coverage). JS/workflow review rules supplied; no hosted OCR-model PASS is claimed. Host review under those rules removed one dead-code block in the release validator.
- TypeSafe Jev `jev-1.13.0`: material-blocker signal **0.24**; risk triage selects `SECURITY` (0.88, confidence 0.84) for the allowlisted highs with P15 remediation, so exact-head CI remains the mandatory merge gate.
- PStack: no PStack skill or command is installed in this execution environment; `PSTACK_NOT_EXECUTED` is recorded and all other safe work continues.

## Exact-head requirement

- Root repository suite: new G4 contract tests included in `npm test`.
- `git diff --check`: must pass.
- Graft exact-range analysis on the final candidate.
- Alibaba Open Code Review delegation/host review, accurately labeled; no
  hosted PASS claimed unless the tool executes it.
- TypeSafe Jev exact-candidate review; `JEV_NOT_EXECUTED` if unavailable.
- Exact-head GitHub Actions green, including the new `g4-baseline`,
  `security-baseline`, `sbom-baseline`, `qualify-windows`, and
  `qualify-macos` jobs.
- Normal merge commit only; no squash/rebase/force-push.

## Exclusions

No Source IR/RAG/NotebookLM work, no new binary artwork, no Store credential
setup, and no end-user release. P16 owns GA release and operations.
