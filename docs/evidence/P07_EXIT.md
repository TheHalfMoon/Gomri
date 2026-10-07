# P07 Exit — Web, Media and Connectors

**Epic:** #53
**Canonical head at exit:** `2102a2302475bbf45889fb322fb5b0c880a418b5`
plus the exit-gap closure below (parity bridge + this record).

## Exit criterion (MASTER_PLAN)

> At least one file, one web, one video and one synced connector
> source all normalize into the same Source IR/citation model.

**Met at contract level, with the boundary stated plainly below.**
The parity proof (`gomrey/source_parity.py`,
`tests/test_gomrey_source_parity.py`) composes all four families —
file page, two web pages with namespaced IDs, video grounded segment
plus uncertain uncovered scene, connector upsert plus
tombstone-to-revocation — through one record shape, one assembly gate
(mixed-tenant union refused), and one coverage verdict (partial with
exact coordinate, zero silent drops). 96 gomrey + 48 root tests green;
every grain exact-head 9/9 CI.

## Grain mapping

- G1 bounded web acquisition (#54): explicit scope, depth/page
  budgets, snapshots, robots/terms decisions.
- G2 media pipeline (#55): validated timelines, gap-explicit
  alignment, timestamp spans, degraded labels.
- G3 connector sync (#56): cursors+revisions, tombstones, stale-marked
  partials, secret-less handles, ACL mapping, freshness flags.
- Exit parity bridge (this PR): the four families into one model,
  mechanically tested.

## The recorded boundary (read before citing this exit)

TypeSafe Jev exit probes scored 0.55 → 0.43 → 0.42 across two genuine
proof-strengthenings (mixed-tenant refusal, multi-page namespacing).
The residual is not noise to shop away: it marks a true scope fact.
This exit proves **contract composition over synthetic fixtures**, not
runtime ingestion of live web/video/connector sources — no worker
exists yet to exercise these paths, which is correct per the program
ladder (workers qualify later *through* these gates), but it bounds
what "normalize" means here. The P05 exit set this precedent (0.40
recorded with disposition); same treatment applies.

 binding downstream obligations (not optional):

1. Worker qualification must run REAL web, video, and connector
   sources through these contracts before any default/GA claim.
2. P15 torture must include multi-page crawl accounting, connector
   tombstone propagation, and video gap accounting on live-shaped
   inputs.
3. P08 retrieval must filter `is_fresh=False` and partial-stale
   receipts rather than assume freshness.

## Standing review record for the program

- TypeSafe Jev `jev-1.13.0` really executed on every grain, driving
  fixes each time (G1 spend-order/revisit 0.27→0.09; G3 three
  hardenings converging 0.14). Exit probes above recorded verbatim.
- PStack: no canonical install throughout P07; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; delegation review
  per grain, never a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.
- Issue #14 stays open as the externally blocked signing dependency.
- Open PRs: none at exit; merged remote branches retained per governance.
