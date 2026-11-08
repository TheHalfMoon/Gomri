# REVIEW_RECORD — W13 (Arabic / RTL / mixed-script qualification)

**Mission:** Issue #77, wave `W13`.
**Binding required by:** `docs/REVIEW_POLICY.md` §3, `docs/JEV_BUILD_POLICY.md` §2.
**Date (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

```text
repository              TheHalfMoon/Gomrey
branch                  feature/rea/w13-arabic-rtl
base branch             main   (canonical)
base commit             5f299a7a6174ad3a1180f827778db5f4400a4d71
candidate commit        a0d28fe0a2132e7f0011d18bfca34ae1ca30306f
merge_base (vs main)    5f299a7a6174ad3a1180f827778db5f4400a4d71
reviewed range          main..HEAD  (range mode)
```

W13 depends on nothing. It branches from canonical `main` and can be qualified and merged
independently of the blocked PR #78 / #79 chain.

## 2. Reviewed file/range set (deterministic selection)

Source: `ocr delegate preview --from main --to HEAD`

```text
# Files (10 reviewable / 13 total)
- mode: range
- from: main
- to: HEAD
- merge_base: 5f299a7a6174ad3a1180f827778db5f4400a4d71
- total_insertions: 1857
- total_deletions: 51
```

**Implementation surface under review:**

```text
servers/fastapi/gomrey/ocr_worker.py
servers/fastapi/gomrey/text_direction.py
servers/fastapi/tests/qualification/__init__.py
servers/fastapi/tests/qualification/arabic_rtl_contract.json
servers/nextjs/components/slide-editor/text/css-text.ts
servers/nextjs/components/slide-editor/text/html-text-attrs.ts
servers/nextjs/components/slide-editor/text/text-direction.ts
servers/nextjs/lib/template-v2-json-to-html.ts
```

**Exclusions, as reported by the tool itself:**

| Exclusion | Reason |
|---|---|
| `evidence/W13_ARABIC_RTL_DESIGN.md`, `evidence/W13_IMPLEMENTATION_EVIDENCE.md` | `excluded: unsupported_ext` — markdown |
| `servers/fastapi/tests/qualification/test_arabic_rtl_qualification.py` | `excluded: default_path` — the tool's path policy for test roots |
| `servers/nextjs/tests/arabic-rtl-qualification.test.mjs`, `servers/nextjs/tests/template-v2-renderer-fields.test.mjs` | `excluded: default_path` |

Those files were verified by running them (43 tests) and by the full gate sweep, not by the OCR
selector.

## 3. Reviewer 1 — Alibaba OpenCodeReview (deterministic selection + rules)

```text
review_tool             ocr (Alibaba OpenCodeReview)
version                 1.13.2
mode                    delegate — deterministic file/rule selection, NO LLM required
commands executed       ocr delegate preview --from main --to HEAD
provider / model        none — LLM-free by design
findings                none from the deterministic selector
coverage                10 reviewable files / 13 changed files
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
candidate commit        a0d28fe0a2132e7f0011d18bfca34ae1ca30306f
latency_ms              475
calibration semantics   "noul" — the probability that the stated concern IS present.
                        true = concern present, false = concern not present.
abstentions / warnings  none reported (ok: true)
```

### 4.1 Decisions — the 10 mandatory questions from `docs/JEV_BUILD_POLICY.md` §2

| # | Question (abbreviated) | `noul` | Concern present? |
|---|---|---|---|
| q1 | Violates a declared invariant? | **0.14** | no |
| q2 | Donor code copied beyond the admitted slice? | **0.03** | no |
| q3 | A deterministic check replaced by a model call? | **0.02** | no |
| q4 | Failure/retry/idempotency incomplete? | **0.14** | no |
| q5 | Any source/page/chunk/artifact silently dropped? | **0.18** | no |
| q6 | Weakens provenance or citation precision? | **0.05** | no |
| q7 | Adds ambient network/filesystem/secret authority? | **0.02** | no |
| q8 | Agent tool result non-structured / non-idempotent? | **0.12** | no |
| q9 | Claimed test/evidence applicable to the exact candidate? | **0.15** | no |
| q10 | A simpler already-admitted implementation should be reused? | **0.13** | no |

**All ten below the 0.5 threshold. Zero concerns present.**

### 4.2 A candidate-contamination finding, and what it cost

The **first** W13 review run returned **q9 = 0.50 — concern present**: *"Is the claimed test and
evidence applicable to the exact candidate revision?"*

That was correct, and the cause was not the code. While the W13 review was running, a second
concurrent design survey (wave **W12**) wrote its 1 281-line design document into the working
tree, and a `git add -A` swept it into the W13 candidate. The candidate therefore contained a
1 281-line artifact belonging to a different wave, which is exactly what q9 asks about.

The fix was to remove it from the candidate (`git rm --cached` + amend). The W12 document was
preserved on disk for the W12 branch and was not modified.

Re-reviewing the same code on the cleaned candidate:

| Run | Candidate | q9 | Cause |
|---|---|---|---|
| 1 | `0373850` | **0.50** | the candidate contained wave W12's design document |
| 2 | `a0d28fe` | **0.15** | the candidate contains only W13's own implementation and evidence |

**A candidate must contain nothing but what it claims.** That is recorded here rather than hidden,
because the first run was right.

### 4.3 Note on the review state

The W3 review established that a state description which *answers* the question abstractly, rather
than describing the change, produces a false signal. Every W13 state description therefore
**describes** the change and states the scoping facts explicitly:

- *which agent tools it adds or modifies: none*;
- *no language-model call is added or modified*;
- *the scope of the claim*, including the explicit statement that there is no headless browser and
  that the suite cannot prove rendered pixel order;
- *the surfaces the change does not fix*, listed;
- *asset rights*: no font binary is vendored, downloaded or relicensed.

The state states these facts; it does not argue a conclusion.

## 5. Human / host adjudication

| Finding state | Count | Notes |
|---|---|---|
| `FIXED` | **4** | All found before the candidate was frozen, all regression-tested:<br>1. A separate wave's design document was swept into the W13 candidate by a concurrent write. It was removed and the commit amended.<br>2. An existing renderer test's regex (`<li style="margin-top:11px;`) predated the new `dir` attribute. It was updated to `<li dir="auto" style="margin-top:11px;`; the gap behaviour it asserts is unchanged.<br>3. The vector-text qualification case assumed the HTML export surface renders a vector's text. It does not — the vector renderer emits geometry only, and the vector's text is laid out by an LTR segment engine in the canvas. The test now asserts what is true and **states the pre-existing surface gap explicitly**.<br>4. The speaker-note qualification case assumed the HTML surface emits the speaker note. It does not — a note is a separate slide field. Same treatment. |
| `NOT_APPLICABLE` | **1** | "Failure/retry/idempotency complete?" — the change adds a pure classifier, a shared font stack and renderer attributes. The classifier is deterministic, has no state and no I/O, so there is nothing to be non-idempotent about. |
| `ACCEPTED_RISK` | **0** | — |
| `BLOCKING` | **0** | — |
| **Unresolved material findings** | **0** | — |

Findings 3 and 4 are the reason the qualification fixture declares an **evidence class** on every
case: a case that looks like it should assert markup but cannot is visible in the fixture instead
of hiding behind a test that quietly measures something else.

## 6. Deterministic gate results on the exact candidate `a0d28fe`

| Gate | Command | Result |
|---|---|---|
| FastAPI | `uv run --locked python -m pytest -q` | **1150 passed** (1125 baseline + 25 qualification) |
| Repository tooling | `npm test` | **48 pass / 0 fail** |
| Next.js unit | `npm test` | **91 pass / 0 fail** (73 baseline + 18 qualification) |
| TypeScript | `npx tsc --noEmit` | clean |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |

## 7. Independent review

The W13 design was produced by a fresh-context subagent that did not author any of this code, and
whose findings are recorded in `evidence/W13_ARABIC_RTL_DESIGN.md` — including the fact that the
export path *is* the DOM path (which is why the renderer is the highest-value edit), and its own
risk statement: **the "supported" claim must not outrun the evidence**.

That risk statement is carried into the implementation: the evidence file's §5 states what W13
does and does not claim, the fixture declares an evidence class per case, and the wave does not
close on unit tests alone — a manual generate → export → reopen check on one Arabic deck is
required.

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
