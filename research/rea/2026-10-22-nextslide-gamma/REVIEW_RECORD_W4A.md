# REVIEW_RECORD — Wave 4a (deterministic WCAG AA theme legibility linter)

**Mission:** Issue #77, wave `W4a`.
**Binding required by:** `docs/REVIEW_POLICY.md` §3, `docs/JEV_BUILD_POLICY.md` §2.
**Date (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

```text
repository              TheHalfMoon/Gomrey
branch                  feature/rea/w4a-contrast-linter
base branch             feature/rea/nextslide-gamma-wave1  (PR #78)
base commit             6dde5b4a8faea32c64811ee818f053d5fc12dbe3
main                    5f299a7a6174ad3a1180f827778db5f4400a4d71
candidate commit        f0fbf523ac2cabdf81cd91e94c84d31e19def648
merge_base (vs main)   5f299a7a6174ad3a1180f827778db5f4400a4d71
reviewed range          main..HEAD  (range mode)
```

This is a **stacked PR**: it is based on PR #78 so that the shared research record
(`research/rea/2026-10-22-nextslide-gamma/`) evolves in one place rather than
forking into two divergent copies.

### 1.1 Files changed by this wave

| File | Change |
|---|---|
| `servers/fastapi/templates/v2/quality.py` | **added** — the linter |
| `servers/fastapi/templates/v2/theme.py` | modified — additive `legibility` key on the theme payload |
| `servers/fastapi/tests/unit/test_template_quality.py` | **added** — 19 tests |
| `servers/fastapi/tests/fixtures/donor_nextslide_presets.json` | **added** — donor colour-token fixture |
| `servers/fastapi/tests/fixtures/generate_donor_nextslide_presets.py` | **added** — deterministic regenerator |
| `servers/fastapi/tests/fixtures/README.md` | **added** — fixture provenance |
| `servers/fastapi/tests/integration/test_presentation_generation_flow.py` | modified — the pre-existing exact-payload assertion now also covers the additive key |
| `research/rea/2026-10-22-nextslide-gamma/*` | modified — the contrast measurement is corrected and its scope made explicit; `W4a` is marked shipped; `evidence/W3_DESIGN.md` added |

### 1.2 Reviewed file/range set (deterministic selection)

Source: `ocr delegate preview --from main --to HEAD`

```text
# Files (41 reviewable / 120 total)
- mode: range
- from: main
- to: HEAD
- merge_base: 5f299a7a6174ad3a1180f827778db5f4400a4d71
- total_insertions: 26459
- total_deletions: 1
```

**Implementation surface under review:**

```text
servers/fastapi/templates/v2/quality.py
servers/fastapi/templates/v2/theme.py
servers/fastapi/tests/unit/test_template_quality.py
servers/fastapi/tests/fixtures/generate_donor_nextslide_presets.py
servers/fastapi/tests/integration/test_presentation_generation_flow.py
```

**Rule identity resolved for the adopted module** (`ocr delegate rule`): rule group
`system / **/*.{py,pyi,ipynb}`, whose content includes *Obvious Typos or Spelling Errors*,
*Favor precision over recall*, and the instruction that security and correctness findings are
blocking while style suggestions are not.

**Coverage / exclusions.** The remaining files in the range are the shared research record
(`.md`), the fixture JSON, and binary evidence. OCR reports `.md` as `unsupported_ext` and
binaries as `binary`; those were verified structurally instead — the fixture is
regenerated and diffed for determinism, and the binary evidence was inspected with
`unzip -t`, OOXML parsing and `python-pptx`.

## 2. Reviewer 1 — Alibaba OpenCodeReview (deterministic selection + rules)

```text
review_tool             ocr (Alibaba OpenCodeReview)
version                 1.13.2
mode                    delegate — deterministic file/rule selection, NO LLM required
commands executed       ocr delegate preview --from main --to HEAD
                        ocr delegate rule servers/fastapi/templates/v2/quality.py \
                                           servers/fastapi/tests/unit/test_template_quality.py
provider / model        none — LLM-free by design
findings                none from the deterministic selector
coverage                41 reviewable files / 120 changed files
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
request                 research/rea/2026-10-22-nextslide-gamma/evidence/jev-review-w4a-request.json
output                  research/rea/2026-10-22-nextslide-gamma/evidence/jev-review-w4a-output.json
candidate commit        f0fbf523ac2cabdf81cd91e94c84d31e19def648
latency_ms              800
calibration semantics   "noul" — the probability that the stated concern IS present.
                        true = concern present, false = concern not present.
abstentions / warnings  none reported (ok: true)
```

### 3.1 Decisions

| # | Question (abbreviated) | `noul` | Concern present? |
|---|---|---|---|
| q1 | Violates a declared invariant? | **0.11** | no |
| q2 | Donor code copied beyond the admitted slice? | **0.11** | no |
| q3 | A deterministic check replaced by a model call? | **0.02** | no |
| q4 | Failure/retry/idempotency incomplete? | **0.11** | no |
| q5 | Any source/page/chunk/artifact silently dropped? | **0.12** | no |
| q6 | Weakens provenance or citation precision? | **0.06** | no |
| q7 | Adds ambient network/filesystem/secret authority? | **0.02** | no |
| q8 | Agent tool result non-structured / non-idempotent? | **0.18** | no |
| q9 | Claimed test/evidence applicable to the exact candidate? | **0.47** | no |
| q10 | A simpler already-admitted implementation should be reused? | **0.12** | no |

All ten below the 0.5 threshold. As in wave 1, q9 (evidence applicability) is the highest.

## 4. Human / host adjudication

| Finding state | Count | Notes |
|---|---|---|
| `FIXED` | **3** | All found before the candidate was frozen, all regression-tested:<br>1. The first cut applied the 4.5:1 **text** threshold to the brand fill colour `primary`, which produced a false positive on Gomrey's own standard pairing `#2563EB` on `#F8FAFC` (4.4:1). Corrected: `primary` is judged as a graphical object at 3:1 (WCAG 1.4.11).<br>2. The first cut also checked decorative borders (`stroke`), which WCAG 1.4.11 excludes. Removed.<br>3. The pre-existing integration test asserted the exact theme payload and broke on the additive key. Updated to assert the original five keys by equality **and** the new key explicitly. |
| `NOT_APPLICABLE` | **1** | "Failure/retry/idempotency complete?" — the linter is a pure arithmetic function with no persistence, no jobs and no side effects. |
| `ACCEPTED_RISK` | **0** | — |
| `BLOCKING` | **0** | — |
| **Unresolved material findings** | **0** | — |

## 5. Deterministic gate results on the exact candidate `f0fbf52`

| Gate | Command | Result |
|---|---|---|
| Repository tooling | `npm test` | 48 pass / 0 fail |
| FastAPI | `uv run --locked python -m pytest -q` | **1144 passed** (1125 baseline + 19 new) |
| Next.js unit | `npm test` | 101 pass / 0 fail |
| Next.js lint | `npm run lint` | 0 errors |
| Next.js build | `npm run build` | success |
| Electron | typecheck / build:ts / check:main-no-undef / test:path-migration | all pass |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Export runtime | `npm run sync:presentation-export && npm run check:presentation-export` | OK (1.0.34) |
| Fixture determinism | regenerate + `diff` | byte-identical |

## 6. Independent review

The W3 design was produced by a fresh-context subagent that did not author any of this code, and
whose findings are recorded in `evidence/W3_DESIGN.md` — including five real hazards it found that
would otherwise have been discovered during implementation (a hard `version === 1` pin in
`scripts/validate-contracts.mjs`, a `citation.schema.json` shape mismatch, TOC index shifting that
would silently mis-attribute citations, user-edited outlines invalidating a generation-time
binding, and a layering inversion risk).

## 7. Authority boundary

```text
JEV_PASS != MERGE_AUTHORITY
```

Merge authority rests with the deterministic gates in §5 and with CI on the exact candidate.

## 8. CI status on this candidate

```text
CI_NOT_EXECUTED
blocker : BLOCKED_COST — GitHub Actions account spending limit / payment failure.
detail  : the same condition that blocked PR #78 applies to this branch; it is an
          account-level condition, not a property of any candidate.
owner   : resolve the account's "Billing & plans" spending limit, then re-run.
```
