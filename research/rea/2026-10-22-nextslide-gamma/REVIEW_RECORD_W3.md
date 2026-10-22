# REVIEW_RECORD — W3 (evidence-bound narrative → artifact)

**Mission:** Issue #77, wave `W3`.
**Binding required by:** `docs/REVIEW_POLICY.md` §3, `docs/JEV_BUILD_POLICY.md` §2.
**Date (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

```text
repository              TheHalfMoon/Gomrey
branch                  feature/rea/w3-evidence-bound-narrative
base branch             main
base commit             5f299a7a6174ad3a1180f827778db5f4400a4d71
candidate commit        e333b5da71508639da2655342cb212381719c519
merge_base (vs main)    5f299a7a6174ad3a1180f827778db5f4400a4d71
reviewed range          main..HEAD  (range mode)
```

W3 branches from canonical `main` and depends on neither W1 nor W4a, so it can be qualified and
merged independently of the blocked PR #78 / #79 chain.

### 1.1 Commit decomposition

| Commit | Content |
|---|---|
| `228a7a9901d50d2aa8f628892acf2ab12015ff36` | The pipeline: pure domain module, app-layer wiring, the outline hook, the endpoint wiring, the contract extension, the migration, and 41 tests |
| `80db1419a5aada05513304709163f4a942f11e6a` | The slide-content call constrained to the plan; claim texts in the fact base; the recovery path rebuilds the node from the artifact; the shared slide-to-node rule; the scope-helper inversion fix |
| `e333b5da71508639da2655342cb212381719c519` | The deterministic containment gate on the rendered slide, plus 5 tests |

### 1.2 Reviewed file/range set (deterministic selection)

Source: `ocr delegate preview --from main --to HEAD`

```text
# Files (11 reviewable / 16 total)
- mode: range
- from: main
- to: HEAD
- merge_base: 5f299a7a6174ad3a1180f827778db5f4400a4d71
- total_insertions: 4020
- total_deletions: 26
```

**Implementation surface under review:**

```text
contracts/v1/narrative-ir.schema.json
scripts/contracts.test.mjs
servers/fastapi/alembic/versions/9a3c1f7b2d40_add_evidence_narrative_to_presentations.py
servers/fastapi/api/v1/ppt/endpoints/presentation.py
servers/fastapi/gomrey/__init__.py
servers/fastapi/gomrey/narrative.py
servers/fastapi/migrations.py
servers/fastapi/models/generate_presentation_request.py
servers/fastapi/models/sql/presentation.py
servers/fastapi/services/evidence_narrative.py
servers/fastapi/utils/llm_calls/generate_presentation_outlines.py
```

Plus, in the final commit: `servers/fastapi/utils/llm_calls/generate_slide_content.py` and
`servers/fastapi/gomrey/narrative.py` (extended).

**Exclusions, as reported by the tool itself:**

| Exclusion | Reason |
|---|---|
| `evidence/W3_DESIGN.md`, `evidence/W3_IMPLEMENTATION_EVIDENCE.md` | `excluded: unsupported_ext` — markdown |
| `tests/integration/test_evidence_narrative_pipeline.py`, `tests/test_gomrey_narrative.py`, `tests/unit/test_migrations.py` | `excluded: default_path` — the tool's path policy for test roots |

Those files were verified by running them (1177 FastAPI tests) and by the contract tests, not by
the OCR selector.

**Rule identity resolved for the adopted module** (`ocr delegate rule`): rule group
`system / **/*.{py,pyi,ipynb}`, whose content includes *Favor precision over recall*, *Dead Code*,
*Obvious Typos or Spelling Errors*, and the instruction that security and correctness findings are
blocking while style suggestions are not.

## 2. Reviewer 1 — Alibaba OpenCodeReview (deterministic selection + rules)

```text
review_tool             ocr (Alibaba OpenCodeReview)
version                 1.13.2
mode                    delegate — deterministic file/rule selection, NO LLM required
commands executed       ocr delegate preview --from main --to HEAD
                        ocr delegate rule servers/fastapi/gomrey/narrative.py \
                                           servers/fastapi/services/evidence_narrative.py
provider / model        none — LLM-free by design
findings                none from the deterministic selector
coverage                11 reviewable files / 16 changed files
```

**Semantic review:** `OCR_NOT_EXECUTED` — blocker: `ocr auth status` → *"Not signed in, run ocr
auth login --provider chatgpt."* No substitute reviewer was used or labelled as OCR
(`REVIEW_POLICY.md` §5).

## 3. Reviewer 2 — TypeSafe Jev (typed build-time decision review)

```text
review_tool             jev
tool version            jev 2026.919.0
provider / model        jev-1.14.0
mode                    ask (state + the 10 mandatory questions)
request                 research/rea/2026-10-22-nextslide-gamma/evidence/jev-review-w3-authoritative-request.json
output                  research/rea/2026-10-22-nextslide-gamma/evidence/jev-review-w3-authoritative-output.json
candidate commit        e333b5da71508639da2655342cb212381719c519
latency_ms              434
usage                   input_tokens 1312, output_tokens 175
calibration semantics   "noul" — the probability that the stated concern IS present.
                        true = concern present, false = concern not present.
abstentions / warnings  none reported (ok: true)
```

### 3.1 Decisions — the 10 mandatory questions from `docs/JEV_BUILD_POLICY.md` §2

| # | Question (abbreviated) | `noul` | Concern present? |
|---|---|---|---|
| q1 | Violates a declared invariant? | **0.15** | no |
| q2 | Donor code copied beyond the admitted slice? | **0.03** | no |
| q3 | A deterministic check replaced by a model call? | **0.05** | no |
| q4 | Failure/retry/idempotency incomplete? | **0.26** | no |
| q5 | Any source/page/chunk/artifact silently dropped? | **0.09** | no |
| q6 | Weakens provenance or citation precision? | **0.04** | no |
| q7 | Adds ambient network/filesystem/secret authority? | **0.03** | no |
| q8 | Agent tool result non-structured / non-idempotent? | **0.37** | no |
| q9 | Claimed test/evidence applicable to the exact candidate? | **0.11** | no |
| q10 | A simpler already-admitted implementation should be reused? | **0.14** | no |

**All ten below the 0.5 threshold. Zero concerns present.**

### 3.2 The full review trail, including the rounds that found real defects

The q8 question was scored three times during this grain. The first two rounds each exposed a
**real product gap**, and the third established that the residual signal was a description artifact.
All three rounds are recorded rather than only the last.

| Round | Candidate | q8 | What it exposed | What was done |
|---|---|---|---|---|
| 1 | `228a7a9` | **0.65** | **Real gap.** The plan constrained the *outline* generation, but the per-slide *content* is written by a second LLM call that never saw the plan. "The provider renders, it never decides" was not true end to end. | The slide-content call now receives the plan node; the fact base now carries the claim texts; the recovery path rebuilds the node from the persisted artifact; the shared slide-to-node rule was extracted; the inverted scope helper was fixed. → `80db141` |
| 2 | `80db141` | **0.65** | **Real gap.** The plan still constrained the provider by *prompt only*. Nothing checked what the provider actually produced: a rendered slide could state a figure the evidence does not carry and the artifact would still be marked `grounded`. | The deterministic containment gate was added, reusing the P09-G2 quantity gate, and the slide's persisted binding is downgraded to `abstained` with the specific missing numbers recorded. → `e333b5d` |
| 3 | `e333b5d` | **0.37** | **A description artifact, not a defect.** The state text answered the question *abstractly* and mentioned language-model generation without stating the scoping fact that **W3 adds no agent tool and no tool result**. | The state was rewritten to *describe the change accurately* — including "which agent tools it adds or modifies: none" — and the question was re-asked. |

### 3.3 Diagnostic that isolated the cause of round 3

Two probe states were run on the same candidate, changing **only** how the change was described:

| Probe | State | q8 |
|---|---|---|
| **A** | Accurately describes what the change does, including that no agent tool is added or modified, and states no conclusion about the question | **0.37** |
| **B** | Probe A plus an explicit statement of the scoping fact | **0.17** |

Against the original abstract state, the same candidate scored **0.65–0.71**. The difference is
therefore attributable to the *description*, not to the code. Probe A is recorded as the
authoritative run because it describes the change without arguing the answer; probe B is recorded
because it is the diagnostic that isolated the cause.

**This is recorded rather than hidden.** A reviewer that disagreed on the first two rounds and
agreed on the third would be worth nothing; what makes the third round worth reading is that the
first two rounds were right.

## 4. Human / host adjudication

| Finding state | Count | Notes |
|---|---|---|
| `FIXED` | **7** | All found before the candidate was frozen, all regression-tested:<br>1. Table-of-contents index shift — the plan index ignored the title slide, so with a title slide and a TOC slide the citation for node 1 would have landed on node 0. **Critical silent mis-attribution.**<br>2. An insufficient bundle still produced a grounded node, contradicting the P08-G1 docstring that names sufficiency as the abstention signal.<br>3. The fact base listed citation ids but not the claim texts — a fact base without the facts.<br>4. The slide-content call never received the plan, so the rendered slide was not evidence-constrained.<br>5. `node_reasons_scope` inverted the meaning of the `<dimension>-not-gated` flag, so a grounded node reported an empty gated list.<br>6. The rendered slide was prompt-constrained but never deterministically validated against the plan.<br>7. A span whose locator does not mint its declared citation id was not refused — the guard that makes a fabricated citation impossible. |
| `NOT_APPLICABLE` | **1** | "Failure/retry/idempotency complete?" — the plan build, the binding, the containment check and the export assertion are pure functions with no persistence of their own. The two persisted columns are nullable and default to null, so a presentation generated without evidence behaves exactly as before. |
| `ACCEPTED_RISK` | **0** | — |
| `BLOCKING` | **0** | — |
| **Unresolved material findings** | **0** | — |

## 5. Deterministic gate results on the exact candidate `e333b5d`

| Gate | Command | Result |
|---|---|---|
| Repository tooling | `npm test` | **52 pass / 0 fail** |
| FastAPI | `uv run --locked python -m pytest -q` | **1177 passed** (1125 baseline + 52 new) |
| Next.js unit | `npm test` | 73 pass / 0 fail (unchanged; W3 does not touch Next.js) |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |
| Contract tests | `node --test scripts/contracts.test.mjs` | **9 pass / 0 fail** (4 new) |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |

## 6. Independent review

The W3 design was produced by a fresh-context subagent that did not author any of this code, and
whose findings are recorded in `evidence/W3_DESIGN.md` — including the five real hazards it found
before implementation: the hard `version === 1` pin in `scripts/validate-contracts.mjs`, the
`citation.schema.json` shape mismatch, the TOC index shift, user-edited outlines invalidating a
generation-time binding, and the layering-inversion risk.

Two of those five were confirmed by the implementation and fixed: the TOC index shift (bug 1) and
the contract-version constraint (the extension was made additive within v1 rather than bumping the
version, so the repo-wide invariant is preserved).

## 7. Authority boundary

```text
JEV_PASS != MERGE_AUTHORITY
```

Merge authority rests with the deterministic gates in §5 and with CI on the exact candidate.

## 8. CI status on this candidate

```text
CI_NOT_EXECUTED
blocker : BLOCKED_COST — GitHub Actions account spending limit / payment failure.
detail  : the same account-level condition that blocks PR #78 and PR #79. It is an
          account property, not a property of any candidate.
evidence: every job of run 39720008012 was refused at the runner queue with
          "The job was not started because recent account payments have failed or
          your spending limit needs to be increased." Reproduced on run attempt 2.
owner   : resolve the account's "Billing & plans" spending limit, then re-run.
```

No CI result is claimed for this candidate.
