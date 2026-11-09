# Gomri Execution Roles, PStack Flow and Merge Authority

**Principle:** roles are fresh, bounded *assignments*, not six simultaneously writable agents on one repo. The lead assigns one ownership lane to each agent. An independent reviewer must not also approve its own implementation.

## RACI and agent prompts

| Role / persona | Accountable deliverable | Read permissions | Write ownership | Mandatory challenge |
|---|---|---|---|---|
| **R0 Technical Lead / Integrator (Opus)** | Resolve dependency graph, pin base, author ADRs, maintain status, decide GO/NO-GO for **draft PR submission** | Entire Gomri and approved donor repositories | Planning docs/branch, PR body, integration orchestration; NEVER bypass human merge review | Are all downstream claims backed by executable evidence at exact SHA? |
| **R1 Donor Auditor / Copy Curator** | Pin source SHA, exact source files, embedded dependencies/assets, permission/license/NOTICE, safe rename/transplant patch and donor comparison tests | Donor repos and source ledger | `third_party` quarantine and bounded adapter source in own PR only | Is this actual code, rightfully obtainable, needed, testable, and cheaper than existing engine? |
| **R2 Data/Authorization Engineer** | Server authority/owner, revision/CAS, idempotency, Undo write contract, accidental cross-owner test suite | FastAPI v1 routes, ORM middleware, auth, autosave, contract | Backend v1 PATCH and corresponding tests **after S00**; not editor rendering | Does a forged actor, stale edit or retry mutate anything unauthorized? |
| **R3 Editor/Layout Engineer** | Role-aware layout helper, text/chart/shape geometry, selection and smart preview | Current Template V2/Konva, Ninerr relevant slices | Slide-editor adapter/tests, no second canvas | Does transform preserve canonical IDs, exact numeric series and user overrides? |
| **R4 Narrative/Evidence Engineer** | SourceIR -> claim/citation checks -> NarrativeIR -> deterministic slide roles | PR #88 narrative and current contracts | Source/claim adapter + fixtures; no paid RAG/LLM mandatory | Are every figure/date/unit/source and unsupported claim accounted for? |
| **R5 PPTX/Export Engineer** | Editable OOXML roundtrip, charts, tables, bullets, speaker notes, loss receipt | Export-core pinned runtime, Beautiful.ai exporter fork | Export adapter and export tests; work in separate PR from R3 on shared files | Are native objects still natively editable after real PPTX import? |
| **R6 E2E & Accessibility QA** | Synthetic browser workflows, Arabic/RTL visual checks, screenshot and OOXML artifacts | Running disposable app and fixture repo | Only `cypress/e2e`, `tests/e2e`, fixture harness and QA receipts | Can actual user perform source -> design -> edit -> export offline, without clipped content or broken Undo? |
| **R7 Independent Code Reviewer** | Alibaba OCR diff/rules + independent skeptical findings, all resolved/triaged | Exact candidate diff, impacted sources, tests | Review reports/comments ONLY, no code fixes on implementation branch | Which concrete regression passes unit tests yet breaks production or security? |
| **R8 Security/Privacy Reviewer** | Owner A/B, SSRF, export revocation, auth-disabled desktop boundaries, provider/asset rights | Current source and isolated test evidence | Security test receipts/triage; no production credentials | How could a user or untrusted source access another tenant or trigger paid upload? |
| **R9 Release/CI Engineer** | Reproducible Windows build, exact-head CI, notices/SBOM, signed/un-signed UX, rollback | Build scripts and release manifests | Release/config/tests in isolated PR after S05 gates | Can users install, run offline, update/undo and un-install safely? |
| **R10 Product/Design Judge** | Independent deck preference study; objective visual rubric | Synthetic decks and blinded screenshots | Research results only | Do readable and useful slide layouts beat the current Gomri baseline? |

**Separation:** R2 (safety fix), R5 (export fix) and R7/R8 (review) must operate from separate fresh contexts or separate PRs, even when one model account is reused. Reviewer may report defects but must never silently amend candidate code before rendering findings. R0 alone decides scheduling; merge still requires the owner's authorized review policy.

## Harness responsibilities and exact PStack skill entry points

- **Discovery:** `/ps-doctor` to probe environment. Record available providers and **missing** providers; don't auto-install anything.
- **Brownfield planning:** `/ps-start` adapted to THIS packet. Read existing `docs/MASTER_PLAN.md`, `docs/ARCHITECTURE.md` and PR #93; never replace old plans or roots. Use [PRODUCT.md](PRODUCT.md) and [ROADMAP.md](ROADMAP.md) from this subfolder as pstack artifacts.
- **Architecture decision:** `/ps-adr` whenever the proposed donor import changes the canonical document model, external provider contract, asset rights or persistence.
- **Phase refinement:** `/ps-spec` edits only that phase spec + roadmap/status. No renumbering during active work; append new phases.
- **Build:** `/ps-build` on ONE approved spec. Create a test that fails for the right reason, then smallest copy/adapt/rename slice, make it pass, run all related regression tests. Source pin/donor notice must be attached to PR.
- **Review:** `/ps-review` after format/typecheck/unit/fixture gates. Invoke Alibaba OCR Delegation for independent diff/rules selection. Review must be based on exact tested commit.
- **Close:** `/ps-close` verifies requirements, PR receipts and cleanup before proposing merge. Do not claim done because a generated design preview exists.
- **Autonomy:** `/ps-dormammu` may schedule *independent* phases only after dependencies and safety gates are passing. It cannot bypass unresolved ownership/DB isolation or publish/releases automatically.

PStack installed skills observed on Windows: `~/.agents/skills/ps-start`, `ps-spec`, `ps-build`, `ps-review`, `ps-doctor`, `ps-dormammu`, `ps-adr`, `ps-close`. These are **local Markdown skills**; a successful tool installation does not itself execute them.

## Handoff protocol for each role

The lead supplies one task containing:

```yaml
project: TheHalfMoon/Gomri
base_sha: <exact SHA>
phase_id: SXX
role_id: RXX
authorized_paths: [explicit repo-relative source/test/docs paths]
donor: {repository, sha, source_files, license_notice, rename_map, approval}
inputs: [source contracts, signed fixture digests, dependency gate receipts]
expected_red_test: "<test and why it fails on baseline>"
planned_minimal_change: "<files and compatibility behavior>"
quality_gates: [format, typecheck, targeted unit, integration, RTL, E2E, export, OCR]
network_budget: none_without_explicit_approval
user_data: forbidden
storage: disposable_synthetic_only
output: {draft_pr, exact_head, tests, screenshot_hashes, provenance, rollback}
stop_on: [owner-scope failure, stale mutation, silent data loss, test isolation failure, unlicensed asset, paid egress]
```

Tasks **without** base SHA, file whitelist, a failing test or permitted donor provenance must be returned for specification correction, not implemented by guessing.

## Coordination: only these parallel groups are safe

- **Wave A (parallel, read-only):** R1 source/license map; R2 existing save/DB route trace; R5 OOXML/notes path trace; R6 E2E harness preflight.
- **Wave B (after S00):** R4 narrative source adapter in a disjoint source module; R3 non-persisting layout spike; R6 fixture writer.
- **Wave C (serialized authority):** R2 safe server writes **before** any R3/R4 user-visible AI mutation.
- **Wave D:** R5 exporter changes and R6 browser tests, with locked exporter test fixtures. R7/R8 review **after** exact-head tests.
- **Wave E:** R9 release qualification and R10 blind layout comparison; no uncontrolled concurrent merges.

Where branches overlap, pause, rebase only after the upstream PR has landed and rerun all required exact-head tests. Worktrees are isolated; do not modify the current user's active Gomri checkout.

## PStack role review and Alibaba OCR zero-cost policy

`ocr` CLI **v1.13.6** was observed installed locally on Windows. Two distinct modes:
- **Delegation Mode (NO OCR LLM key):** `ocr delegate preview --from origin/main --to HEAD --format json` selects diff, `ocr delegate rule <paths>` loads rule context. Then a separate locally installed/authorized host model (if available) must *actually* analyze the files. Delegation alone is NOT an AI review.
- **OCR-managed review:** `ocr review --from origin/main --to HEAD --format json --output <scratch>` uses configured LLM and **may contact a provider**; only run if provider is explicitly confirmed local/free and network allowed. Do not run just because OCR binary exists.

A remote provider marketed as "free" may retain data and require account linking; do not upload private source or user presentations without verified constraints. A local model is preferred. No reviewer may call its own completed review "independent" without a fresh context and clear evidence.

## Non-negotiable stopping conditions

P0b A-group 61/61 passing **does not** authorize product editing. Backend Python-3.11 dependencies, disposable owner A/B API tests and cross-client CAS remain unqualified. Actual PPTX roundtrip is known to lose speaker-note reimport and native bullet semantics. They must become accepted or explicitly receipted under S04; no release label can bypass them.

A hard requirement failing -> document, fix in own branch, test, re-review. A provider/account/OS unavailable -> status BLOCKED, not invented green.
