# Quality, E2E and Free-Local Alibaba Review — Executable Policy

**Target:** Gomri, Windows, PStack phase S00–S07. **Proof standard:** actual command log + exact source SHA + fixture hash + negative control + independent reviewer, not "the model said done." This is a **plan**, not a claim all gates have already passed.

## A. Observed tool and source evidence (2026-11-09)

| Tool / code | Verified now | Not yet verified |
|---|---|---|
| PStack skills | `ps-start`, `ps-spec`, `ps-build`, `ps-review`, `ps-doctor`, `ps-adr`, `ps-close`, `ps-dormammu` under Windows `~/.agents/skills/` | Actual agent invocation and availability of fresh subagent model contexts |
| Alibaba OCR | `ocr v1.13.6` installed; **`ocr delegate preview` executed successfully** on Gomri PR #88 diff | Full independent LLM review and fix verification; OCR Delegation alone does not review code |
| OCR preview result | From `origin/main` to PR #88 `HEAD d4362c6`: **223 changed files, 96 reviewable, 127 excluded**, 41,132 insertions/125 deletions reported by CLI | Why all excluded files may or may not matter for license/source/NOTICE; inspect manually, never claim the tool reviewed all 223 |
| OCR rules | **`ocr delegate rule` executed successfully** for FastAPI update route and Konva slide model: two rule groups, schema v1 | Whether the rules detected any actual bug (they are configuration, not findings) |
| Cypress | Local Cypress npm package ^15.18.1, CLI present, existing component-only `cypress.config.ts` | Browser binary cache and actual local E2E run; no `cypress/e2e` suite verified |
| Python | Windows Python 3.11.15 present | No isolated backend wheelhouse/venv with SQLModel/FastAPI/etc; owner A/B integration still blocked |
| Native PowerPoint | `@presenton/export-core@1.0.34` existing; 15 real export/reimport tests from PR #88 green | Speaker-note reimport and native bullet semantics specifically **fail semantic preservation** under current expected behavior; real Windows editor E2E not qualified |
| D: free space | About 6 GB available during this planning inspection | Full build/Chrome/Cypress binary/install requirement; remeasure before dependency admission |

## B. Local-review-first execution (no OCR API key)

Review runs only after source/test gates are green at the *same SHA*. Run in the feature worktree; do not change original active Gomri checkout.

```powershell
# Exact SHA and cleanliness before review:
git rev-parse HEAD
git status --porcelain
ocr --version

# Alibaba's local delegation: scope and rules, no OCR-managed LLM key
ocr delegate preview --from origin/main --to HEAD --format json > .review/ocr-selection.json
ocr delegate rule 'servers/fastapi/api/v1/ppt/endpoints/presentation.py' 'servers/nextjs/components/slide-editor/model/model.ts' --format json > .review/ocr-rules.json

# IMPORTANT: manually inspect excluded_files for source/license/NOTICE/security.
# Pass the selected diff, rule groups and relevant full files to a distinct reviewer.
# Only a returned finding report with exact file/line evidence counts as a review.
```

The CLI was actually tested on the currently checked-out Gomri source, but it **did not** run a model. The large PR #88 diff includes code, docs, research JSON and source history; triage exclusions. A default selector may exclude Markdown documentation like SOURCE_LEDGER and a donor NOTICE, which are **mandatory manual provenance review** even if not selected by the code-review CLI.

### Two allowed review paths

**Path 1 — fully local/private, $0** (preferred): on the Windows PC, confirm a locally installed, reachable code-capable model in a model runtime using `ocr` supported provider configuration or a host agent with OCI Delegation. Test a tiny fixture with no secrets, freeze model/revision, record actual endpoint restricted to loopback, verify no egress, then run independent review.

**Path 2 — free-labelled hosted model, explicitly consented:** host OpenCode uses its own no-charge model to inspect delegated diff/rules, with source egress/policy accounted for. This is **not "offline/local inference"**, even when the CLI runs locally. Never auto-upload a private repository or real health-related data simply because a provider is advertised free.

**If neither path is verified:** OCR Delegation produces only deterministic file/rule selection; use a human/authorized separate source auditor and mark `AI_REVIEW_NOT_RUN`. Do not call it a completed AI review.

A review finding is actionable only with severity, repo-relative file/line or exact diff hunk, reproduction, tests that detect it, proposed smallest repair, and acceptance disposition. Tool reports alone cannot approve their own code.

## C. E2E runner procedure

1. `cd servers/nextjs`, verify installed Cypress CLI and version. **Verify actual binary** only against a user-authorized isolated test cache; current Cypress binary cache was absent when inspected.
2. Before any binary download, run disk preflight and verify official license/checksum/source. No Cypress Cloud recording or paid integration.
3. Start Next.js + FastAPI on two temporary loopback ports, temporary SQLite/user storage, two test accounts and no API keys. If impossible due missing backend dependencies, mark `E2E_BLOCKED`; do not use the logged-in Vivaldi browser.
4. Add `cypress.config.e2e.ts` and `cypress/e2e/` test files behind an isolated feature PR. Preserve existing component config. Use data-testid, role/name selectors, stable test fixtures, and deterministic mock provider data.
5. Run [12 E2E journeys](specs/05-e2e-browser.md), including concurrent editing and revoked export access; retain screenshot/video logs and a separate native OOXML audit.
6. After testing, remove only temp-owned fixture database, user profile and ports; verify original checkout unmodified.

A Node unit test that checks `aria-label` attribute or a screenshot of a marketing page is not a real browser end-to-end pass.

## D. No-silent-loss and unit/integration negative controls

| Gate | Minimal negative control that MUST fail old/unsafe behavior |
|---|---|
| Source facts | Wrong unit/value or citation ID in slide fails `assert_exportable` |
| Layout | Remove source component or move text beyond canvas -> test catches it, not just screenshot diff |
| Access | A with valid B slide UUID -> 403/404 and B DB digest identical |
| Concurrency | Two same-base-revision writers -> stale conflict, no last-write-wins |
| Idempotency | Replay same operation ID with changed patch -> denied; unchanged -> one effect |
| Agent scope | Unselected chart/text modified -> reject patch before commit |
| Native notes | Export and reimport distinct notes -> exact match; current importer fails and must be addressed |
| Bullet hierarchy | Plain bullet characters no longer accepted as native bullet preservation |
| Charts | A PNG screenshot instead of native chart OOXML -> explicitly flagged non-native |
| RTL | Mixed Arabic numbers and diacritics beyond frame -> visual/geometry test fails |
| Export role | Revoked user downloads previously queued file -> deny in isolated auth mode |
| SSRF | URL import points to loopback/private service -> blocked/explicit user-approved local-only fixture |
| Offline | Any unapproved external socket/API call -> fail, not silent fallback |
| Donor | Missing upstream NOTICE/License/transitive asset right -> block import PR |

## E. Mechanical + independent gate order

1. **Donor:** pinned source SHA, exact files, license/NOTICE, rename map, original author lineage, no unlicensed media/models.
2. **RED:** write failing test for named feature or acknowledged loss. Demonstrate failure catches the intended bug, not environment setup alone.
3. **GREEN:** smallest working bounded source copy/adapt/rename; no second canonical model.
4. **Mechanical:** formatter, static typing, root/Next.js/FastAPI tests, deterministic narrative/RTL, OOXML native object tests; all exact head.
5. **E2E:** real browser on synthetic/local data, full flow and screenshot plus semantic inventory.
6. **Alibaba OCR:** local Delegation diff/rules and distinct actual model/human review; must manually inspect excluded license/NOTICE docs.
7. **PStack:** ps-review correctness, parsimony and product review; resolve findings, rerun exact-head tests.
8. **Release:** Windows smoke, no unapproved spending, SBOM/license/provenance, rollback, human merge/release approval.

**Any one hard failure resets the candidate to BLOCKED/FAILED.** Quality score improvements cannot compensate for an ownership breach, silent note/chart loss or unlicensed source. Keep a per-feature evidence table, not a vague universal "all green" statement.

## F. Reproducibility receipt

```json
{
  "phase": "S03",
  "candidate_sha": "<actual HEAD>",
  "donor_repo": "TheHalfMoon/Ninerr",
  "donor_sha": "<fixed SHA>",
  "test_command": "<exact command with secret fields redacted>",
  "test_exit": "PASS|FAIL|BLOCKED",
  "negative_control": "<how regression fails>",
  "e2e_test_ids": ["E02", "E05", "E08"],
  "native_pptx_inventory": "<artifact digest + object types>",
  "review_mode": "OCR_DELEGATE_ONLY|LOCAL_LLM|AUTHORIZED_FREE_REMOTE|HUMAN",
  "reviewer_context_id": "<fresh review session or reviewer>",
  "findings": ["<file:line>"],
  "notice_license_check": "PASS|FAIL",
  "no_paid_network": "VERIFIED|UNVERIFIED",
  "rollback": "<feature flag or commit>"
}
```

**Stop if any artifact is missing for the claimed PASS**. Reports under PR #93 are design/test evidence; updating them does not itself change app functionality.
