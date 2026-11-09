# S06 — Local Alibaba OCR + PStack Review + Windows Release Qualification

**Goal:** Release candidate whose tested commit, source provenance, security and native artifact fidelity are independently reviewable. **Owners:** R7 OCR reviewer, R8 security, R9 release, R0 integration. **Depends on:** S00–S05 passing and P1/P2 runtime scopes separately authorized.

## Zero-cost tools actually observed

- Alibaba \`ocr\` CLI version **1.13.6** (Windows/amd64), installed as \`@alibaba-group/open-code-review\`; local binary supports \`delegate preview\` and \`delegate rule\` with **no OCR-managed LLM key**.
- The local Gomri feature branch is a Git repository with an existing \`origin/main\` reference and PR #88 candidate; using OCR on the git diff does not write product code.
- \`ps-review\` and \`ps-close\` are already installed as PStack skills.
- Full OpenCode free-labelled model availability/network/account permissions are **not guaranteed**; an agent model may be remote even when free. Do not call an expensive hosted OCR model by default; user asked free **locally**.

## Exact OCR process (review happens only after machine gate)

Run from an isolated checked-out feature worktree that contains the actual candidate SHA:

\`\`\`powershell
# First test diffs/formats/TS/backend suite/E2E and ensure head is exact.
$base = 'origin/main'
$head = 'HEAD'
ocr --version
ocr delegate preview --from $base --to $head --format json > .review\ocr-selection.json
ocr delegate rule 'servers/fastapi/api/v1/ppt/endpoints/presentation.py' 'servers/nextjs/components/slide-editor/model/model.ts' --format json > .review\ocr-rules.json
\`\`\`

The reviewable file inventory and resolved rules can run locally **without a model**; it is **not by itself a code review**. To satisfy the actual reviewer gate:
1. Feed exact diff, relevant full files, ORM/auth and source/OOXML negative-control tests, resolved rules and branch commit to a fresh independent local review model.
2. If a local model is not installed, either (a) use an explicit zero-price, authorized remote model through OpenCode with network/provider disclosure, or (b) keep **AI_REVIEW_BLOCKED** and perform a documented manual source reviewer. Never claim fully offline when using a free hosted route.
3. Require **line-specific bug findings**, priority BLOCKER/MAJOR/MINOR, reproduction/negative control, fix proof and reviewer disposition, not generic praise.
4. Open a new review context after each material fix; re-run deterministic tests at the new exact head. Do not rely on a prior model run.
5. PStack \`/ps-review\` must independently test correctness, parsimony and security; \`/ps-close\` is allowed only after the code/tests/rights gates pass.

For advanced \`ocr review\` (OCR-managed LLM) do not run until the configured provider is proven local or approved zero-charge. OCR Delegation is the default.

## Full technical gate

- **Static mechanical:** package formatting/TypeScript, FastAPI mypy/pytest as configured, root tests, Next.js unit tests, dependency audit; test counts/paths all reported.
- **Backend safety:** authenticated two-owner query/PATCH, cross-workspace denial, concurrent stale CAS, multi-client autosave, idempotent retry and Undo revocation (real disposable DB).
- **Visual/E2E:** Cypress run with isolated real browser, full source->deck->edit->PPTX, RTL and accessibility. No skipped critical case.
- **PPTX:** OOXML native text/table/chart/notes/bullets; complete non-silent loss receipt. Export package SHA and source exact commit recorded.
- **Security:** untrusted file/URL/HTML, parser limits, SSRF, package scripts, credential redaction, export role at start/download, trial auth vs desktop auth-disabled.
- **Donor:** SHA, exact paths, original LICENSE/NOTICE, fork lineage/permission scope, rename map, transitive assets/model weights; no hidden premium stock.
- **Windows build:** signed/unsigned Windows installer if part of product scope, direct download and SmartScreen warning accurate, real smoke; no user profile cleanup except owned scratch.
- **Privacy/cost:** zero unintended network/paid providers; synthetic fixture data only in all CI/baseline tests.

## Branch and merge protocol

One feature or donor transplant per draft PR with:
\`phase_id, base_sha, donor_commit, modified_paths, tests_red_then_green,
 CI_URL, E2E_video/hash, OCR selection/rules + review report, reviewer dispositions,
 license/NOTICE, rollback, user-visible known limitations.\`

Do not merge without independent reviewer and exact-head checks; **do not auto-publish**. Reviewers may be separate agent contexts, but a model that implemented the patch may not count as independent review without a new context and source evidence. No open BLOCKER/MAJOR in the release scope.

## Release acceptance

**S06-GO:** one 8–12-slide source-grounded editable deck journey in the real Windows app with tested source claims, safe save/Undo, editable native PowerPoint where advertised, full E2E and no unapproved charges, all at same commit and documented known limitations. A feature that is declared unsupported must not be marketed as native editable.

**S06-NO-GO:** safety test blocked/failed, missing browser runner, inability to reproduce PPTX notes, no source/asset rights, OCR model or reviewer absent without manual fallback, CI red/skipped, unclean or untracked generated user data, or unapproved billable inference.

**Rollback:** preserve previous exact working export/runtime; disable new feature flags and revert narrow PRs. No external app marketplace necessary for initial Windows release.
