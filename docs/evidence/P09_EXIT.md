# P09 Exit — Decision Fabric and Claim Verification

**Epic:** #69
**Canonical head at exit:** `1a186641fb96035e1d8ef40e102f9021f28f652e`
(post-merge CI pending at write time; verified below before close)

## Exit criterion (MASTER_PLAN)

> Default provider for each workload is justified by measured
> quality/calibration/resource evidence; unsupported claims are
> repaired, downgraded, or blocked.

**Half met by construction, half by contract — stated exactly.**
Unsupported claims blocked/downgraded is proven deterministically
(G1 binding refusals, G2 verdict gates with provider-overrule
recording, G3 verified-only synthesis with abstention). The
measured-challenger half is NOT yet run: no Decider/SemIf/Laya-class
adapter has been benchmarked, so no challenger holds a default
anywhere. What exists is the framework the measurement will run
through (calibration registry with sample/benchmark floors, routing
with deterministic fallback, disagreement adjudication) plus a
deterministic default whose justification is explicit in every
verdict record. Claiming a measured provider default now would be
fabrication; the measurement belongs to P15 by canonical plan.

## Grain mapping

- G1 claim contracts (#70): durable claim records, verification
  states, evidence binding that never widens insufficiency, override
  tripwire, tenant-isolated store.
- G2 verification engine (#71): deterministic verdicts, quantity/date
  agreement gates, stance tally, identity-carrying provider seam
  that cannot overrule policy, claim and evidence injection both
  forcing unresolved.
- G3 decision graph (#72): support graph with dangling/orphan
  refusal, verified-only synthesis with exposed conflicts and
  conflict-without-alternative abstention, calibration registry +
  routing, disagreement adjudication, decision store.

## Binding downstream obligations

1. P15 arena must benchmark challenger providers through frozen
   workloads (with calibration profiles) before any becomes a
   default — routing must keep returning deterministic-only until then.
2. P10 research UX must surface verification states, conflicts, and
   omissions; it must never render unbound, unverified, or
   override-flagged claims as support.
3. P11 creation compiler must consume synthesis records (not raw
   bundles) and preserve conflict representation into artifacts.

## Standing review record for the program

- TypeSafe Jev `jev-1.13.0` really executed on every grain
  (G1 0.11/0.09, G2 0.07, G3 0.08, none blocking). Exit-honesty
  probe on this document: 0.13.
- PStack: no canonical install throughout P09; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; delegation review
  per grain, never a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.
- Issue #14 stays open as the externally blocked signing dependency.
- Open PRs: none at exit; merged remote branches retained per governance.
