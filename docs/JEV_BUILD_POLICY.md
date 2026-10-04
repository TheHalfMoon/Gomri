# Gomrey Jev Build and Decision-Fabric Policy

**Status:** FOUNDATION PLAN  
**Purpose:** make calibrated typed decisions a first-class engineering primitive while preventing probabilistic confidence from becoming authority.

## 1. Two separate uses of Jev-class systems

Gomrey uses Jev-class decision systems in two different roles:

1. **Building Gomrey** — review, classification, routing, bounded design/test decisions, and independent challenge of implementation work.
2. **Inside Gomrey** — runtime typed decisions for ingestion routing, retrieval relevance, evidence support, artifact verification, and abstention.

These roles must never be conflated. A build reviewer does not become product authority, and a runtime provider does not approve its own code or release.

## 2. Build-time Jev requirement

For non-trivial implementation grains, the acceptance packet must include a Jev-class review when reproducible Jev access is available.

Minimum build-time review questions include:

- Does the change violate a declared invariant?
- Is donor code copied beyond the authorized/admitted slice?
- Is a deterministic check being replaced by an unnecessary model call?
- Is failure/retry/idempotency behavior complete?
- Is any source/page/chunk/artifact silently dropped?
- Does the change weaken provenance or citation precision?
- Does it add ambient network/filesystem/secret authority?
- Is an agent tool result structured and idempotent?
- Is the claimed test/evidence applicable to the exact candidate revision?
- Is there a simpler already-admitted implementation that should be reused instead?

### Evidence requirement

Do not write “Jev passed” without recording:

```text
review_tool
provider/model/tool version
request/schema digest
candidate commit/tree
reviewed file/range identity
decision outputs/probabilities
calibration semantics if exposed
abstentions/warnings
human/host adjudication
```

If TypeSafe Jev is unavailable in the execution environment, the task does **not** fabricate Jev output. It must record `JEV_NOT_EXECUTED` and may use an admitted open Jev-class comparator such as Decider/SemIf for additional review, but that does not impersonate TypeSafe Jev.

## 3. Jev does not replace other review

Build acceptance requires independent evidence in addition to Jev-class output:

- deterministic tests and static checks;
- security/provenance review;
- exact diff/range review;
- CI on the exact candidate;
- where required, Alibaba Open Code Review and the project’s other mandated review tools;
- benchmark evidence for performance/retrieval/model changes.

`JEV_PASS != MERGE_AUTHORITY`.

## 4. Runtime Decision Fabric

Permanent product boundary:

```text
DecisionRequest
  -> deterministic eligibility/policy
  -> provider router
  -> one or more LocalDecisionProvider candidates
  -> calibration/disagreement/abstention handling
  -> DecisionResult
  -> deterministic downstream policy
```

Gomrey owns the contract. Providers are replaceable.

Supported decision families should include at least:

- `BOOLEAN`
- `CHOICE`
- `ORDINAL_SCORE`
- `RANK`
- `MULTI_LABEL`
- `ABSTAIN / NO_FIT`

## 5. DecisionRequest minimum fields

```text
request_id
workload_kind
state/context digest
bounded context
question
answer family
options/rubric
source/evidence refs
language
latency budget
memory/resource budget
privacy mode
provider allow/deny set
required calibration profile
consequence class
deadline/cancellation
```

## 6. DecisionResult minimum fields

```text
provider identity
model identity and immutable revision
artifact/tokenizer/config digests
runtime identity
quantization/precision
request/schema digest
selected value
probability distribution or documented score semantics
calibration profile/revision
abstention/OOD signal
latency/device/resource metadata
truncation/degraded warnings
local/remote data-boundary assertion
```

## 7. Runtime provider hierarchy

The initial provider pool is intentionally plural:

1. deterministic rules — always available;
2. compact local Jev-class provider candidate (e.g. Laya-class);
3. Mapika Decider-class typed provider;
4. SemIf/direct-option-logit adapter over admitted local models;
5. larger challenger providers only where benchmarked gain justifies cost.

Routing is workload-specific. No single model is declared globally best.

## 8. High-value Gomrey workloads

### Ingestion routing

Examples:

- native text vs scanned vs mixed page;
- table/formula/chart-heavy page;
- parser selection;
- whether a second parser is required;
- retry/degrade/abstain after parser disagreement.

### Retrieval

Examples:

- candidate relevance classification;
- source-family routing;
- rerank shortlisting;
- contradiction/duplicate classification;
- whether retrieval is sufficient or must continue.

### Evidence verification

Examples:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `CONTRADICTED`
- `DOES_NOT_ESTABLISH`
- `UNRESOLVED`

Probabilistic support classification must be combined with deterministic checks for numbers, dates, units, entities, page/table/cell references, and citation integrity where applicable.

### Artifact quality

Examples:

- slide crowded/not crowded;
- narrative redundancy;
- layout candidate choice;
- chart-type choice from an allowed set;
- brand-fit scoring;
- whether a generated artifact requires repair.

## 9. Authority boundary

A DecisionResult cannot:

- grant a permission or capability;
- approve its own side effect;
- lower a deterministic privacy/security classification;
- mark evidence verified without applicable supporting checks;
- mark tests/CI passed;
- declare a donor license/permission satisfied;
- publish externally without the required policy/approval;
- silently convert an unknown into a known state.

Hard policy wins over model confidence.

```text
CONFIDENCE != AUTHORITY
MODEL_OUTPUT != PERMISSION
MODEL_OUTPUT != VERIFICATION
```

## 10. Calibration and abstention

Raw softmax/logit scores are not user-facing truth. Every production provider/workload pair requires a measured calibration profile with:

- benchmark/dataset identity;
- language/domain scope;
- sample size;
- Brier/ECE/NLL where meaningful;
- risk/coverage curve;
- abstention precision/recall;
- unsafe-commit rate;
- distribution-shift limits;
- model/runtime/quantization identity.

If no valid calibration profile exists for the workload, the provider may still be used as an uncalibrated ranking signal only when explicitly allowed, and its output must not be represented as calibrated probability.

## 11. Disagreement policy

When high-consequence providers disagree:

1. run deterministic checks first;
2. inspect evidence sufficiency and input truncation;
3. optionally invoke an independently trained/provider-diverse challenger;
4. if disagreement remains material, return `ABSTAIN`, `UNRESOLVED`, or request more evidence.

Do not average incompatible probability semantics.

## 12. Local-first runtime packaging

Decision models should be separate signed/content-addressed packs, not baked into the Gomrey core binary or silently downloaded during inference.

A pack records model/tokenizer/config/calibration/runtime identities, licenses/permissions, digests, resource profile, and qualification evidence.

Baseline correctness must not require a GPU or hosted Jev endpoint.

## 13. Promotion gate

A decision provider becomes default for a workload only if it beats or matches the incumbent under Gomrey’s frozen benchmark on:

- task quality;
- calibration;
- abstention behavior;
- latency/resource budget;
- language coverage;
- privacy/offline requirements;
- reproducibility.

A provider may win one workload and lose another. Routing may preserve both.
