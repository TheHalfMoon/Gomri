# Gomrey Review and Evidence Policy

**Status:** FOUNDATION PLAN  
**Purpose:** define which review tools and evidence can satisfy Gomrey acceptance gates.

## 1. Mandatory review stack for implementation work

For non-trivial code changes, Gomrey requires both of the following when the relevant execution environment is available:

1. **Alibaba Open Code Review (OCR)** — deterministic file/rule selection plus semantic review under the project review configuration.
2. **Jev / Jev-class build review** — typed decision review following `JEV_BUILD_POLICY.md`, with TypeSafe Jev used when reproducible access is available and explicitly identified.

Neither tool alone grants merge authority. Deterministic tests, security/provenance review, exact-candidate CI, and unresolved-finding reconciliation remain required.

## 2. Non-evidence integrations

Automated GitHub integrations such as CodeRabbit, Cubic, Qodo, or similar tools may post summaries/statuses if installed on the repository, but **they do not satisfy Gomrey's mandatory review evidence** unless a later canonical policy amendment explicitly adopts one.

Their presence or green status must not be cited as proof that an implementation grain passed the required review stack.

## 3. Exact-candidate binding

Every accepted review record must identify:

```text
repository
base commit/tree
candidate commit/tree
reviewed file/range set
review tool + exact version/model/provider
configuration/rule identity
findings
coverage/exclusions
adjudication
unresolved material findings count
```

If HEAD moves materially, candidate-bound review evidence becomes stale and must be rerun or explicitly requalified for the new exact candidate.

## 4. Jev non-fabrication rule

If TypeSafe Jev is unavailable:

```text
JEV_NOT_EXECUTED
```

must be recorded. An open Jev-class system may be used as an additional comparator, but its output must not be labeled or represented as TypeSafe Jev.

## 5. Alibaba OCR non-fabrication rule

If Alibaba OCR cannot execute in the current environment, record the exact blocker. Do not substitute a different reviewer and call it OCR. A host semantic review may be documented separately only when the actual Alibaba OCR execution mode used supports that workflow and the tool's deterministic selection/rule evidence is real.

## 6. Review independence

Where the risk of a change warrants it, require an independent substantive reviewer/model/human beyond the authoring agent. The same model that generated a change cannot be treated as independent merely because it was prompted again.

## 7. Review finding states

Findings resolve to one of:

```text
FIXED
NOT_APPLICABLE
ACCEPTED_RISK (requires explicit authority and rationale)
BLOCKING
```

A material `BLOCKING` finding prevents merge. Silence is not PASS.

## 8. Evidence hierarchy

Preferred proof order:

1. deterministic test/runtime observation;
2. exact static/security/provenance check;
3. Alibaba OCR finding/coverage record;
4. Jev typed decision review;
5. independent semantic review;
6. human/governance decision where required.

Probabilistic review cannot override a deterministic failing test or policy violation.

## 9. Planning-only changes

Planning/document-only changes may record `JEV_NOT_EXECUTED` and/or `OCR_NOT_EXECUTED` when those tools are unavailable, but they must not use that exception to authorize implementation that the canonical plan says requires the mandatory review stack.

## 10. Merge evidence

Before merge, the acceptance packet must state whether each required reviewer actually executed on the exact final candidate. After merge, post-merge verification binds the canonical merge commit/tree and any actually-triggered required workflows.
