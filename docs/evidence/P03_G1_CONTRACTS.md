# P03-G1 — Versioned Core Contract Schemas and Validators

**Parent:** #19
**Issue:** #20
**Canonical base:** `7b669011ed4822532b05dd3ee3a2814aaf412e26` (P02 complete)

## Goal

Ship Gomrey-owned versioned JSON Schemas plus deterministic validators for
the P03 core models. No storage or product-behavior changes.

## Scope

`contracts/v1/` holds 23 self-contained schemas (local `$defs` only) listed
exactly once in `manifest.json`: Workspace, Principal, CapabilityGrant,
SourceArtifact, SourceUnit, EvidenceSpan, SourceSnapshot, IngestionManifest,
EvidenceBundle, Claim, Citation, Job, StageAttempt, ArtifactBaseline,
DecisionRequest, DecisionResult, Artifact, ArtifactRevision, NarrativeIR,
DesignIR, Plugin, Skill, ConnectorIdentity.

`scripts/validate-contracts.mjs` is a dependency-free deterministic validator
for the documented keyword subset (type, enum, const, required, properties,
additionalProperties, items, lengths, minimum/maximum, pattern, format
date-time/uri/uuid, anyOf/oneOf/allOf, local `$defs` refs). Anything outside
the subset fails loudly instead of silently passing. A new runtime dependency
such as ajv was deliberately deferred: it would expand the shipped root SBOM
and security surface for a need covered by auditable dependency-free code.

Architecture invariants enforced by schema or test:

- Every durable record carries `tenant_id`; all but the documented
  tenant-level/global definitions (Workspace, Principal, Plugin) and the
  tenant-global Skill definition also require `workspace_id`.
- `IngestionManifest.silent_drop_count` has `maximum: 0`: the no-silent-loss
  invariant is a schema constraint, not a comment.
- Claim support states, citation locators, decision answer families, and
  abstention signals match `ARCHITECTURE.md`.
- No schema requires vector/graph index fields; projections stay rebuildable.
- `ConnectorIdentity.credential_handle` is an opaque server-side reference;
  raw secrets are prohibited by schema description, fixture policy, and
  secret scanning.

## Local qualification before commit

- Root repository suite: **48/48 PASS** (43 pre-existing + 5 contract tests).
- `node scripts/validate-contracts.mjs`: PASS (23 schemas listed and loadable).
- Secret scan, fixture check, platform-support, and release-config validators: PASS.
- `git diff --check`: PASS.
- Graft, Alibaba Open Code Review delegation, and TypeSafe Jev evidence are
  bound to the exact candidate below; PStack remains unavailable in this
  environment (`PSTACK_NOT_EXECUTED` with the §6 investigation recorded on
  #19's trail: no repo docs, binary, or package define a canonical install).

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass the
full GitHub Actions workflow, including the new contract suite on all three
platform jobs, before a normal merge commit.
