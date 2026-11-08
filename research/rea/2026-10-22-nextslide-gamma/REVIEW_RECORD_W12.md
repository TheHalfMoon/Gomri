# REVIEW_RECORD — W12 (export fidelity harness)

**Mission:** Issue #77, wave `W12`.
**Binding required by:** `docs/REVIEW_POLICY.md` §3, `docs/JEV_BUILD_POLICY.md` §2.
**Date (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

```text
repository              TheHalfMoon/Gomrey
branch                  feature/rea/w12-export-fidelity
base branch             main   (canonical)
base commit             5f299a7a6174ad3a1180f827778db5f4400a4d71
candidate commit        690513e928c0546be6df415b5e834df667502ee3
merge_base (vs main)    5f299a7a6174ad3a1180f827778db5f4400a4d71
reviewed range          main..HEAD  (range mode)
```

W12 depends on nothing. It branches from canonical `main` and can be qualified and merged
independently of the blocked PR #78 / #79 chain.

## 2. Reviewed file/range set (deterministic selection)

Source: `ocr delegate preview --from main --to HEAD`

```text
# Files (3 reviewable / 19 total)
- mode: range
- from: main
- to: HEAD
- merge_base: 5f299a7a6174ad3a1180f827778db5f4400a4d71
- total_insertions: 3359
- total_deletions: 0
```

**Implementation surface under review:**

```text
.github/workflows/test-all.yml
package.json
servers/nextjs/tests/export-fidelity.test.mjs
```

**Exclusions, as reported by the tool itself:**

| Exclusion | Reason |
|---|---|
| `evidence/W12_EXPORT_FIDELITY_DESIGN.md`, `evidence/W12_IMPLEMENTATION_EVIDENCE.md`, `fixtures/export-fidelity/PROVENANCE.md`, `fixtures/export-fidelity/README.md` | `excluded: unsupported_ext` — markdown |
| `fixtures/export-fidelity/decks/*.json`, `fixtures/export-fidelity/expectations/v1.json`, `fixtures/export-fidelity/*.mjs` | `excluded: default_path` — the tool's path policy for fixture and test roots |

Those files were verified by running the harness (15 tests), by the fixture-policy gate, and by
re-running the measurement against the real export runtime — not by the OCR selector.

**Rule identity resolved for the adopted modules** (`ocr delegate rule`): rule group
`system / **/*.{py,pyi,ipynb}` / the JavaScript equivalent, whose content includes *Favor precision
over recall*, *Dead Code* and *Obvious Typos or Spelling Errors*, and the instruction that security
and correctness findings are blocking while style suggestions are not.

## 3. Reviewer 1 — Alibaba OpenCodeReview (deterministic selection + rules)

```text
review_tool             ocr (Alibaba OpenCodeReview)
version                 1.13.2
mode                    delegate — deterministic file/rule selection, NO LLM required
commands executed       ocr delegate preview --from main --to HEAD
provider / model        none — LLM-free by design
findings                none from the deterministic selector
coverage                3 reviewable files / 19 changed files
```

**Semantic review:** `OCR_NOT_EXECUTED` — blocker: `ocr auth status` → *"Not signed in, run ocr
auth login --provider chatgpt."* No substitute reviewer was used or labelled as OCR
(`REVIEW_POLICY.md` §5).

## 4. Reviewer 2 — TypeSafe Jev (typed build-time decision review)

```text
review_tool             jev
tool version            jev 2026.919.0
provider / model        jev-1.14.0
mode                    ask (state + the 10 mandatory questions)
candidate commit        690513e928c0546be6df415b5e834df667502ee3
latency_ms              545
calibration semantics   "noul" — the probability that the stated concern IS present.
                        true = concern present, false = concern not present.
abstentions / warnings  none reported (ok: true)
```

### 4.1 Decisions — the 10 mandatory questions from `docs/JEV_BUILD_POLICY.md` §2

| # | Question (abbreviated) | `noul` | Concern present? |
|---|---|---|---|
| q1 | Violates a declared invariant? | **0.11** | no |
| q2 | Donor code copied beyond the admitted slice? | **0.03** | no |
| q3 | A deterministic check replaced by a model call? | **0.02** | no |
| q4 | Failure/retry/idempotency incomplete? | **0.22** | no |
| q5 | Any source/page/chunk/artifact silently dropped? | **0.22** | no |
| q6 | Weakens provenance or citation precision? | **0.04** | no |
| q7 | Adds ambient network/filesystem/secret authority? | **0.08** | no |
| q8 | Agent tool result non-structured / non-idempotent? | **0.15** | no |
| q9 | Claimed test/evidence applicable to the exact candidate? | **0.42** | no |
| q10 | A simpler already-admitted implementation should be reused? | **0.07** | no |

**All ten below the 0.5 threshold. Zero concerns present.**

q9 is the highest score at 0.42. The state described the one nuance that could justify it: the
harness exercises an **external** runtime that is not committed, so its evidence depends on a
runtime being materialised. That is a real caveat and it is why the harness reports an explicit
skip rather than a pass when the runtime is absent, and why a dedicated CI job was added that
materialises it. It remains below the threshold.

### 4.2 Note on the review state

Every W12 state description **describes** the change and states the scoping facts explicitly:

- *which agent tools it adds or modifies: none*;
- *no language-model call is added or modified*;
- *what the harness pins and, precisely, what it does not pin* (not the PPTX bytes, not rendered
  pixels, not a compatibility with Gomrey's own model that does not exist);
- *the behaviour that is currently dropped*, listed, so the drops are recorded facts rather than
  silent losses;
- *that the expectations are measured, not guessed*;
- *that a skip is never reported as a pass*;
- *that no existing CI gate was removed or weakened*.

The state states these facts; it does not argue a conclusion.

## 5. Human / host adjudication

| Finding state | Count | Notes |
|---|---|---|
| `FIXED` | **3** | All found before the candidate was frozen, all regression-tested:<br>1. The harness's skip was implemented as an early `return`, which `node:test` counts as a **pass**. A skip must never be reported as a pass, so it now uses the test context's `t.skip(reason)`. Verified by hiding the export runtime: 12 skipped, 3 passed, 0 failed.<br>2. The design proposed a **picture** fixture. The picture shape's model is not documented in the export-core type declarations, and all three plausible constructions throw `Cannot read properties of undefined (reading 'path')`. Pinning that failure would have encoded our own misuse of an undocumented shape as a fact about the product. The fixture was replaced with one covering the constructs that are constructible, and the gap is recorded as an open item.<br>3. The measurement script could not find the export runtime because the repository-root path was resolved four levels up instead of five. The export core also declares `engines.node >= 22.12.0` while every existing CI job pins Node 20, where the export tasks cannot run — so a dedicated Node 22 CI job was added, and the harness reports `EF-NODE-VERSION` rather than failing confusingly. |
| `NOT_APPLICABLE` | **1** | "Failure/retry/idempotency complete?" — the harness runs a pure measurement and compares facts; it writes nothing into the product. The fixtures and the expectations are regenerated deterministically, and the new CI job is additive. |
| `ACCEPTED_RISK` | **0** | — |
| `BLOCKING` | **0** | — |
| **Unresolved material findings** | **0** | — |

## 6. Deterministic gate results on the exact candidate `690513e`

| Gate | Command | Result |
|---|---|---|
| Next.js unit | `npm test` | **88 pass / 0 fail** (73 baseline + 15 harness) |
| Export-fidelity harness | `node --test tests/export-fidelity.test.mjs` | **15 pass / 0 fail** |
| Repository tooling | `npm test` (root) | **48 pass / 0 fail** |
| FastAPI | `uv run --locked python -m pytest -q` | **1125 passed** (unchanged) |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |
| Workflow parse | `yaml.safe_load` | OK — `test-export-fidelity` registered |

## 7. Independent review

The W12 design was produced by a fresh-context subagent that did not author any of this code. Its
findings are recorded in `evidence/W12_EXPORT_FIDELITY_DESIGN.md`, including the single most
important risk it identified: **the harness would pin a third-party version's behaviour while CI
runs an unsupported Node.** That risk is real and it is handled — the expectations are pinned to
`export_core_version`, the harness reports `EF-NODE-VERSION`, and a dedicated Node 22 CI job
exists.

The design also identified the two highest-value expectations, and both are implemented: the
text-runs and font contract on fixture 01, and the **two-sided** speaker-note assertion on fixture
07 — the note is present in the PPTX package *and* absent from the re-imported JSON.

## 8. Authority boundary

```text
JEV_PASS != MERGE_AUTHORITY
```

Merge authority rests with the deterministic gates in §6 and with CI on the exact candidate.

## 9. CI status on this candidate

```text
CI_NOT_EXECUTED
blocker : BLOCKED_COST — GitHub Actions account spending limit / payment failure.
detail  : the same account-level condition that blocks PR #78 and PR #79. It is an
          account property, not a property of any candidate.
owner   : resolve the account's "Billing & plans" spending limit, then re-run.
```

No CI result is claimed for this candidate.
