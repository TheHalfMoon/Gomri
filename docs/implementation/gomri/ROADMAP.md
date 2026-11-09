# Gomri — PStack ROADMAP (Copy-First)

**Status:** PLAN READY TO HAND OFF, production execution gates not yet passed. **Base:** main `5f299a7` and PR #88 `d4362c6` observed 2026-11-09; recheck before building. **Release thesis:** one trusted 8–12-slide source-grounded, editable presentation; not a clone of every competitor.

## Phase ledger

| Phase | Status | In first MVP? | Accountable role | Depends on | Spec | Measurable deliverable |
|---|---|---|---|---|---|---|
| **S00 — Proven baseline, owner/CAS and build isolation** | **START HERE — P0b partially tested, blocked groups** | Yes | R2 + R0 + R8 | No other phase | [00](specs/00-qualify-baseline.md) | Real isolated Python3.11/SQLite test, foreign-owner deny and conflict outcome; PR #88 exact-head comprehensive checks or explicit failures |
| **S01 — Grounded narrative compiler** | PLANNED | Yes | R4 | S00 safety and #88 qualification | [01](specs/01-evidence-to-deck.md) | 8 synthetic sources -> 8–12 outlines/cards, numeric+citations invariant |
| **S02 — Copy-first SmartLayout preview** | PLANNED / preview only first | Yes | R3 + R1 | S00; S01 role schema | [02](specs/02-smart-layout.md) | 4 layout families *after* single headline-helper spike; no new canvas; no overlaps/drop |
| **S03 — Scoped agent edit, server CAS, durable Undo** | PLANNED / safety-gated | Yes | R2 + R3 | S00 + S01; S02 preview may proceed in separate branch | [03](specs/03-scoped-ai-edits.md) | Real selected-element edit; conflicting writers rejected, role rechecked, Undo append-only |
| **S04 — Native export integrity & RTL** | PLANNED / current known losses | Yes | R5 + R4 | S01 + S02 + S03 | [04](specs/04-pptx-roundtrip.md) | Notes/bullets preserved or fully receipted; charts/tables native when supported; Arabic RTL checked |
| **S05 — E2E, accessibility & real UX** | PLANNED / runner not verified | Yes | R6 + R10 + R8 | S03 + S04 | [05](specs/05-e2e-browser.md) | Cypress browser jobs on synthetic account; screenshots, no external spend, no crash and data integrity |
| **S06 — Security/OCR independent review & release decision** | PLANNED | Yes | R7 + R8 + R9 | S00–S05 | [06](specs/06-release-qualification.md) | Alibaba OCR-reviewed exact-head PR, full CI, clean build, rollback, NOTICE, Windows download and install test |
| **S07 — Responsive formats and motion/image enhancements** | BACKLOG / not release blocker | No | R3 + R5 | S06 | [07](specs/07-adaptive-formats.md) | 16:9 -> 4:3/1:1/9:16 with semantic reflow; high-quality animation/frame fallback and asset rights |

**Do not split these into dozens of simultaneous uncontrolled agent sessions.** An R2 security route and an R3 slide scene writer must never mutate the same model at the same time.

## Actual delivery slices and stop/go

### S00 — root of all other work
- **What is already supported:** P0a source map and seven isolated targeted Node/PPTX groups, **61/61 pass** at #88 exact SHA. The test suite **expects** notes lost on reimport and bullets flattened, so native fidelity is not green.
- **What is blocking:** Python3.11+FastAPI/SQLModel/SQLAlchemy/aioSQLite dependencies not yet available in a disposable environment; no owner A/B real PATCH, concurrency, idempotency or export role-revocation test. Cypress binary availability not yet verified.
- **Work that CAN proceed immediately:** inspect and isolate dependency cache; produce a safe temp venv from existing local packages or explicitly documented no-cost source if approved; run tests on temporary SQLite and full PR88 FastAPI/TS/CI; preserve receipts. Do not touch existing production DB/user account.
- **Exit:** separate PASS/FAIL/BLOCKED receipts and a route-owner coverage map. If a gate fails, file a narrow repair phase with red negative test, then repeat S00. Do not assume all tests pass.

### S01 — source-to-outline
- Prefer PR #88 source/Narrative IR and current Source/Claim contracts, not new RAGFlow workers.
- Freeze 8 synthetic grounded sources (including Arabic medical-style narrative; **synthetic-only**) and citations; test exact number/unit/dated claim containment.
- No model provider required in CI. Hosted AI may be optional explicit opt-in; factual validation must be deterministic.

### S02 — accessible four-family layouts
- First a preview-only headline hero using existing `TemplateV2KonvaSlide` and `model.ts` helpers. Only after that shows value, add `stat-chart`, `comparison`, `timeline-process`.
- Use Skilit reference pattern metadata behind adapter; do not import its database or make a second scene model.
- UI preview without save triggers. After S03, add controlled apply with revision/Undo.

### S03 — safe object edits
- Map `Ninerr` history/MCP authorization into current Gomri scene and persisted FastAPI route. Source code may be bounded-copied from pinned owner SHA.
- Require server-resolved actor/workspace, slide ID and selected element IDs, allowlisted edit op, before/after proposal and source claim invariant.
- CAS/idempotency across human auto-save, AI edits and deck reorder; a local snapshot is not a database transaction.

### S04 — PowerPoint that stays editable
- Keep `@presenton/export-core` version-pinned; first fix P0b-measured notes reimport and bullet semantics or implement exact component downgrade receipts.
- Benchmark public Beautiful.ai PptxGenJS fork only with the 8 synthetic fixtures. Copy bounded code only when it proves native PPTX improvement and licenses/NOTICE are retained.
- OOXML zip and external relationship hardening; stage 30 fixtures only after first 8 pass.

### S05 — no pretend E2E
- Add real browser E2E specs under existing Next.js Cypress structure, or small documented runner adapter with pinned dependencies and local binary.
- Must run on a disposable localhost app and throwaway A/B users. Save screenshot, page trace, console, object integrity and PPTX XML.
- Do not declare E2E PASS based on document screenshots or Node unit tests. If runner missing, mark BLOCKED and document install/source/cost path.

### S06 — release gate
- Alibaba Open Code Review **Delegation Mode** is mandatory for diff/rule extraction; a reviewer model in a distinct context must *actually review* to count as AI review. No default remote OCR-managed billable provider.
- pstack `/ps-review` panel, independent security pass, negative controls, Windows binary test, licensing/NOTICE/SBOM, rollbacks, signed/unsigned user guidance, all at exact HEAD.
- Ready for user/human merge review only when no open BLOCKER/MAJOR findings and exact-head CI fully green. **No silent merge**.

### S07 — optional post-release
- Responsive reflow from single canonical deck, not three separate inconsistent artifacts.
- Motion, Object Grabber/AI background removal and social formats only after S06; no paid stock/LLM dependency and explicit asset/model license admission.

## Critical-path test order

```text
S00 temporary Python env
  -> real owner A/B denied/allowed UPDATE tests
  -> stale concurrent writer conflict proof
  -> idempotency/reorder/Undo
  -> full FastAPI/Next.js/CI exact-head qualification
S01 source/number/source claim no-loss
S02 preview layout fixtures / one existing editor
S03 controlled atomic patch and Undo
S04 OOXML native object, notes and bullet fidelity
S05 Cypress real browser & Arabic/RTL visual QA
S06 independent Alibaba OCR + PStack reviews + Windows release gate
```

A failing foreign-owner test is a **security investigation**, not proof of exploitable access until route/ORM guards are measured. Never disable global Windows Defender/firewall or run against the live user's profiles for convenience.

## Milestone tracking contract

Each phase ledger entry must record:
`state` (PLANNED/IN_PROGRESS/FAILED/BLOCKED/TESTED/REVIEWED/MERGE_READY/MERGED),
`base_sha`, `branch/pr`, `donor` and imported paths, `scope whitelist`,
`red_test`, `green_test`, `CI_url`, `e2e_screenshot`, `OCR_review_id`,
`NOTICE`, `release_blockers`, `rollback`.
No line is marked DONE without artifacts and a reviewed commit.
