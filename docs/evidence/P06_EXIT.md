# P06 Exit — Document/OCR Intelligence

**Epic:** #43
**Canonical head at exit:** `3e56a327015b6d29b4d0d7972fc68b1254eccbe1`
(post-merge CI pending at write time; verified below before close)

## Exit criterion (MASTER_PLAN)

> Gomrey Source IR preserves structural/page/region provenance and
> benchmarked parser quality. No "100% OCR accuracy" claim; 100% unit
> accounting remains the reliability contract.

**Met at the contract-and-gate layer.** Routing, ensemble discipline,
worker envelopes, the frozen LiteParse comparator, measurement-only
qualification gates, the Arabic P0 suite, IR assembly checks, and the
ledger coverage gate are implemented, tested (83 gomrey + 48 root),
and exact-head qualified per grain. No accuracy percentage is asserted
anywhere; observations stay observations.

## Grain mapping

- G1 router + ensemble contracts (#44): preflight, workload rules,
  bounded escalation, explicit reconciliation, IR emission, benchmark
  scoring with mandatory baseline.
- G2 structured worker + baseline (#45): capability-bounded envelope,
  LiteParse frozen identity, Docling-shaped mapping, qualification bars.
- G3 OCR workers + Arabic P0 (#46): region contracts, script analysis,
  nine frozen cases, escalation honesty.
- G4 IR provenance + coverage (#47): chain checks, source-mixing
  refusal, ledger reconciliation with loud drops and coordinates.

## Honest scoping notes (owned by later qualification, not P06 gaps)

- Docling DEPEND packaging, PaddleOCR worker processes, and model
  weights are intentionally not vendored here; they land through the G2
  gates with exact LICENSE blobs, resource profiles, and winning
  benchmark runs. The gates exist so those landings are measured.
- Per-format measured qualification (PDF/DOCX/PPTX/XLSX/HTML/TXT/images)
  runs through the frozen harness as workers land; the mapping already
  preserves pages/sections/tables/figures generically.
- MinerU stays optional per the canonical plan (gates must pass first).
- RTL table cell-order with measured tables belongs to worker
  qualification alongside real table fixtures.

## Standing review record for the program

- TypeSafe Jev `jev-1.13.0` really executed on every grain, including
  two elevated probes that each found and fixed a real defect
  (zero-default baseline 0.42→0.11; vacuous-pass suite 0.48→0.16).
  Exit-honesty probe: 0.10.
- PStack: no canonical install throughout P06; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; delegation review per
  grain, never a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.
- Issue #14 stays open as the externally blocked signing dependency.
- Open PRs: none at exit; merged remote branches retained per governance.
