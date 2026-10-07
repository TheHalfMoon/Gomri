# P08 Exit — Retrieval Fabric and Citation Resolver

**Epic:** #61
**Canonical head at exit:** `5bddfd2d1bc7761466aa08033e4d272975620ad1`
(post-merge CI pending at write time; verified below before close)

## Exit criterion (MASTER_PLAN)

> Frozen benchmark beats the Presenton/imported baseline and proves
> citation locators resolve to exact source positions.

**Half met by measurement, half by contract — stated exactly.**
Citation locators resolving to exact positions is proven
deterministically (G2: five families resolve, nine breakage shapes fail
loudly). The frozen-benchmark-beats-baseline half is NOT yet measured:
no dense/visual index exists to beat anything with, and no frozen
retrieval benchmark has run. What exists is the harness the measurement
will run through (P06-G1 scoring with mandatory baselines, P06-G2
qualification bars) plus a pipeline whose ordering, freshness, and
degraded behavior are proven. Claiming a beaten baseline now would be
fabrication; the measurement belongs to P15 by canonical plan.

## Grain mapping

- G1 layered pipeline (#62): ACL-first with counts, exact boost,
  lexical channel, explicit fusion, freshness/diversity constraints,
  no-vector retrieval proven.
- G2 citations (#63): five locator kinds, deterministic IDs, resolver
  with coordinate agreement, BrokenCitation failures.
- G3 evidence bundle (#64): bounded bundles with digests, marked
  contradictions with escalation, accounted omissions, sufficiency
  verdicts with abstention.

## Binding downstream obligations

1. P15 arena must run the frozen retrieval benchmark vs the imported
   baseline through the P06 harness before any superiority claim.
2. Dense/visual/graph index qualification must preserve the G1
   guarantees (ACL-first, freshness filtering, lexical fallback) —
   re-qualify, don't assume.
3. P09 verification consumes bundles and sufficiency verdicts; it must
   not re-widen insufficient evidence into support.

## Standing review record for the program

- TypeSafe Jev `jev-1.13.0` really executed on every grain
  (0.06–0.15, none blocking). Exit-honesty probe: 0.12.
- PStack: no canonical install throughout P08; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; delegation review
  per grain, never a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.
- Issue #14 stays open as the externally blocked signing dependency.
- Open PRs: none at exit; merged remote branches retained per governance.
