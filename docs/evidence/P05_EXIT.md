# P05 Exit — Source Gateway, Hostile-Input Boundary, Access Control

**Epic:** #33
**Canonical head at exit:** `6da46f2937d01af7f1c8e0895f4d57f871435904`
(post-merge CI green on the G4 merge)

## Exit criterion (MASTER_PLAN)

> Adversarial fixtures prove forbidden paths fail closed without
> contaminating trusted storage/indexes.

**Met.** 26 gateway adversarial tests plus the 39 pre-existing Gomrey
contract/job/budget tests (65 total) and the 48-test root suite — which
includes the fixture-policy and secret-scanner guards — pass on the exit
head, and every grain qualified with exact-head 9/9 CI.

## Work-item mapping

| MASTER_PLAN P05 work | Evidence |
|---|---|
| MIME/content classification | G2 `sniff_mime`/`reconcile_mime` |
| Archive/decompression/page/size limits | G2 six-dimension budgets + entry checks; G4 char/unit budgets |
| Parser isolation | G4 adapter protocol (no store/ledger/network surface) |
| SSRF/DNS/redirect controls | G3 classification, pinning contract, redirect bounds |
| Active-content denial | G2 scan/deny battery |
| Source ACL model | G1 deny-by-default tenant/workspace/scope boundary |
| Data classification hooks | G4 secret/credential/PII patterns |
| Prompt-injection/taint metadata | G3 tainted fetch contract; G4 markers (no completeness claim) |
| Source rights/access metadata | G1 provenance + export/share scopes |
| Revocation/deletion vs derived projections | G4 tombstone receipts, audit preserved |
| Quarantine and explicit rejection states | G1 trust machine; structured error taxonomy |

## Honest scoping notes (owned by later programs, not P05 gaps)

- Connector credential handles, OAuth/token refresh, and incremental-sync
  revocation belong to P07, which builds the connectors; P05 denies
  credential-bearing URLs and records connector provenance today.
- Plugin/worker capability enforcement beyond gateway purity (no ambient
  handles by construction) belongs to the P13 plugin runtime.
- Acquisition robots/terms policy and redistribution/export workflow
  enforcement belong to P07 web acquisition; P05 carries the rights
  metadata and export-scope checks they will consume.
- SVG sanitizer path and fetcher/browser workers are explicitly later
  grains, routed — not dropped — by G2/G3 denials.

## Standing review record for the program

- TypeSafe Jev `jev-1.13.0` executed really on every grain (9 questions,
  all low-risk 0.05–0.13, none blocking); never impersonated.
- Exit-honesty Jev on this file scored 0.4 (elevated, non-blocking).
  Disposition: the score reflects genuine program-summary uncertainty,
  not a located defect — every deferred item above names its canonical
  owning program (P07 connectors own credential handles/sync/robots;
  P13 owns the plugin runtime), and the P05 exit criterion itself (the
  adversarial-fixtures sentence) is fully demonstrated. The deferrals
  are plan-ordered, not hidden; P06+ must consume the P05 hooks
  (provenance, ACL, URL policy, taint) rather than re-bypass them.
  Future grains that widen connectors/plugins must re-qualify these
  boundaries instead of assuming them.
- PStack: no canonical install in this environment throughout P05;
  `PSTACK_NOT_EXECUTED` every grain.
- Alibaba OCR: no OCR workflow installed in this repository; hosted OCR
  never executable here. Every grain carries exact-diff delegation
  review with adjudicated findings — never represented as hosted PASS.
- Dependabot alerts disabled (403); code scanning no analysis (404);
  recorded each grain.
- Issue #14 stays open as the externally blocked signing dependency.
- Merged remote feature branches remain per governance (no casual
  deletion); open PRs: none at exit.
