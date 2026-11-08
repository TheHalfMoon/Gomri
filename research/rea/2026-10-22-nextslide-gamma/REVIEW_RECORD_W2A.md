# REVIEW_RECORD — W2a (animation field on the slide model + HTML renderer wiring)

**Mission:** Issue #77, wave `W2a`.
**Binding required by:** `docs/REVIEW_POLICY.md` §3, `docs/JEV_BUILD_POLICY.md` §2.
**Date (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

```text
repository              TheHalfMoon/Gomrey
branch                  feature/rea/w2a-animation-wiring
base branch             feature/rea/nextslide-gamma-wave1   (PR #78)
base commit             6dde5b4a8faea32c64811ee818f053d5fc12dbe3
candidate commit        f5881ea
reviewed range          feature/rea/nextslide-gamma-wave1..HEAD  (range mode)
```

W2a is **stacked on wave 1**, because the animation catalog, the stylesheet generator and the
class-name contract all live in `servers/nextjs/lib/slide-animations/`, which wave 1 introduced.
It therefore inherits wave 1's blocked state and cannot merge before PR #78 does.

## 2. Reviewed file/range set (deterministic selection)

Source: `ocr delegate preview --from feature/rea/nextslide-gamma-wave1 --to HEAD`

```text
# Files (4 reviewable / 7 total)
- mode: range
- from: feature/rea/nextslide-gamma-wave1
- to: HEAD
- merge_base: 6dde5b4a8faea32c64811ee818f053d5fc12dbe3
- total_insertions: 714
- total_deletions: 5
```

**Implementation surface under review:**

```text
servers/fastapi/templates/v2/models/elements.py
servers/fastapi/templates/v2/models/layouts.py
servers/nextjs/lib/template-v2-json-to-html.ts
servers/nextjs/tests/slide-animations-rendering.test.mjs
```

**Exclusions, as reported by the tool itself:**

| Exclusion | Reason |
|---|---|
| `evidence/W2A_ANIMATION_WIRING.md` | `excluded: unsupported_ext` — markdown |
| `servers/fastapi/tests/test_slide_animation_model.py` | `excluded: default_path` — the tool's path policy for test roots |
| `servers/nextjs/tsconfig.tsbuildinfo` | `excluded: unsupported_ext` — build artifact; also **reverted** so it is not in the commit |

The two test files were verified by running them (20 tests), not by the OCR selector.

**Rule identity resolved for the adopted modules** (`ocr delegate rule`): rule group
`system / **/*.{py,pyi,ipynb}`, whose content includes *Favor precision over recall*, *Dead Code*,
*Obvious Typos or Spelling Errors*, and the instruction that security and correctness findings are
blocking while style suggestions are not.

## 3. Reviewer 1 — Alibaba OpenCodeReview (deterministic selection + rules)

```text
review_tool             ocr (Alibaba OpenCodeReview)
version                 1.13.2
mode                    delegate — deterministic file/rule selection, NO LLM required
commands executed       ocr delegate preview --from feature/rea/nextslide-gamma-wave1 --to HEAD
                        ocr delegate rule servers/fastapi/templates/v2/models/elements.py \
                                           servers/nextjs/lib/template-v2-json-to-html.ts
provider / model        none — LLM-free by design
findings                none from the deterministic selector
coverage                4 reviewable files / 7 changed files
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
candidate commit        f5881ea
latency_ms              717
usage                   input_tokens 1334, output_tokens 175
calibration semantics   "noul" — the probability that the stated concern IS present.
                        true = concern present, false = concern not present.
abstentions / warnings  none reported (ok: true)
```

### 4.1 Decisions — the 10 mandatory questions from `docs/JEV_BUILD_POLICY.md` §2

| # | Question (abbreviated) | `noul` | Concern present? |
|---|---|---|---|
| q1 | Violates a declared invariant? | **0.10** | no |
| q2 | Donor code copied beyond the admitted slice? | **0.04** | no |
| q3 | A deterministic check replaced by a model call? | **0.05** | no |
| q4 | Failure/retry/idempotency incomplete? | **0.28** | no |
| q5 | Any source/page/chunk/artifact silently dropped? | **0.21** | no |
| q6 | Weakens provenance or citation precision? | **0.04** | no |
| q7 | Adds ambient network/filesystem/secret authority? | **0.03** | no |
| q8 | Agent tool result non-structured / non-idempotent? | **0.13** | no |
| q9 | Claimed test/evidence applicable to the exact candidate? | **0.33** | no |
| q10 | A simpler already-admitted implementation should be reused? | **0.10** | no |

**All ten below the 0.5 threshold. Zero concerns present, on the first round.**

### 4.2 Note on the review state

The W3 review established that a state description which *answers* the question abstractly, rather
than describing the change, produces a false signal — the W3 candidate scored 0.65–0.71 on q8 for
two rounds before a diagnostic showed the same code scored 0.37 when described accurately.

The W2a state description was therefore written to **describe** the change and to state the
scoping facts explicitly:

- *which agent tools it adds or modifies: none*;
- *no language-model call is added or modified*;
- *why the field is declared on the element model* (pydantic would otherwise drop it silently);
- *the canvas and export limitation* (animations run in the HTML preview only).

The state states these facts; it does not argue a conclusion. The zero-concern result is therefore
read together with the fact that the state was accurate, not because it was argued.

## 5. Human / host adjudication

| Finding state | Count | Notes |
|---|---|---|
| `FIXED` | **3** | All found before the candidate was frozen, all regression-tested:<br>1. A root element that already carried a `class` attribute would have received a **second** `class` attribute. Browsers silently ignore the second one, so the animation would have vanished with no error. The class is now merged, and a test asserts that no element carries two `class` attributes.<br>2. `remove_fields_from_schema` removed the `animation` property but left the `ElementAnimation` `$defs` entry and its description behind. `_prune_unreferenced_defs` now drops definitions nothing references, because an unreferenced definition invites the belief that the field is still reachable.<br>3. A tracked build artifact, `servers/nextjs/tsconfig.tsbuildinfo`, was regenerated by the typecheck and would have been committed. It was reverted and the commit amended. |
| `NOT_APPLICABLE` | **1** | "Failure/retry/idempotency complete?" — the change adds a model field and a pure renderer branch. An unknown animation id is ignored rather than rendered broken, and a deck without animations carries no animation CSS, so there is no state to be non-idempotent about. |
| `ACCEPTED_RISK` | **0** | — |
| `BLOCKING` | **0** | — |
| **Unresolved material findings** | **0** | — |

## 6. Deterministic gate results on the exact candidate `f5881ea`

| Gate | Command | Result |
|---|---|---|
| FastAPI | `uv run --locked python -m pytest -q` | **1135 passed** (1125 baseline + 10 new) |
| Repository tooling | `npm test` | **48 pass / 0 fail** |
| Next.js unit | `npm test` | **111 pass / 0 fail** (101 wave-1 baseline + 10 new) |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |

The counts differ from the W3 branch because this branch is stacked on wave 1, which does not carry
W3's four contract tests.

## 7. Authority boundary

```text
JEV_PASS != MERGE_AUTHORITY
```

Merge authority rests with the deterministic gates in §6 and with CI on the exact candidate.

## 8. CI status on this candidate

```text
CI_NOT_EXECUTED
blocker : BLOCKED_COST — GitHub Actions account spending limit / payment failure.
detail  : the same account-level condition that blocks PR #78 and PR #79. It is an
          account property, not a property of any candidate.
owner   : resolve the account's "Billing & plans" spending limit, then re-run.
```

No CI result is claimed for this candidate.
