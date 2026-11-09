# ADR-0002 — Server-authoritative edits, auditable local-first execution

**Status:** Design decision pending S00 negative-test results. **Date:** 2026-11-09.

## Context

The present browser auto-save uses per-hook serialization and JSON fingerprints. These are not inter-client conflict detectors. FastAPI's authentication middleware and owner-scoped SQLAlchemy SELECT hooks are real source protections, but live two-owner PATCH behavior and atomic revision control have not been tested. User requests zero unapproved cost, privacy and autonomous engineering without unsafe cloud calls.

## Decision

Before persistent AI edits, require a server-resolved principal/workspace/target selection, verified proposal hash and an atomic compare-and-swap of content plus increasing revision. Apply one compatible revision policy to *all* writes: human auto-save, selected edits, speaker-note updates, slide reorder, export lifecycle and Undo. Duplicate operation IDs are idempotent; stale writes return 409/412; Undo appends a new revision. Maintain safe migration behavior for old clients with explicit cut-over tests.

Default deterministic local/free test path and no provider secrets. Alibaba Open Code Review Delegation may run offline for diff/rule selection; it is *not* model review. A verified local model is preferable; free-labelled hosted inference is remote and must be explicitly disclosed/allowed.

## Consequences

Benefits: no silent lost updates, stronger testable security, selected AI edit safety, predictable costs.

Trade-offs: migration/compatibility and cross-client tests required; not justified to invent microservices before examining actual v1 FastAPI routes.

## Acceptance

S00 owner A/B and race baseline; S03 atomic operation integration with data digest; S05 real browser concurrency; S06 independent Code Review and cost/egress receipts.

**Hard stop:** cross-owner mutation, stale write accepted silently, unreviewed provider uploading private decks, or unsupported Undo persistence.
