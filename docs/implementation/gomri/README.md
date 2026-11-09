# Gomri — Copy-First Implementation Packet

**Status:** IMPLEMENTATION-SPECIFIED / **execution gates outstanding**. Authored 2026-11-09 on planning PR #93. This packet is an execution addendum to [EGM v4](../../designs/GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md), not a claim that Gomri's full backend/security/export implementation is qualified.

**Product:** Gomri is an agent-native, evidence-grounded, editable slide authoring product. The milestone is **one excellent source -> outline -> native editable 8–12-slide deck -> selected AI edit -> native PPTX workflow**. Do not expand into a generic design/marketing suite before that journey works.

**PStack working-directory rule:** The PStack artifact root for these skills is this folder, `docs/implementation/gomri/`. When invoking skills that look for `PRODUCT.md`, `ROADMAP.md`, `CLAUDE.md` or `specs/`, launch the PStack planning session **with this folder as cwd** (or explicitly point it at these files). The Git repository root remains `TheHalfMoon/Gomri`, and all source edits happen on a separate git worktree at that root. Do **not** run `/ps-start` from the repo root if it would overwrite the existing root product instructions.

## The three governing files

1. [ROADMAP.md](ROADMAP.md) — dependency ordered phases, owner role, success test, no-go and delivery artifact.
2. [ROLES.md](ROLES.md) — actual engineer/agent permissions, PStack skill assignments, review separation, execution protocol.
3. [SOURCE_ADMISSION.csv](SOURCE_ADMISSION.csv) — copy-first donor pin, exact source path, entry mode, rename target, test and rights gate.

The [QA and zero-cost review contract](QUALITY_AND_LOCAL_REVIEW.md) includes Cypress E2E, actual Alibaba OCR Delegation, free/local model boundaries, render/OOXML and isolated test requirements. The [implementation handoff prompt](OPUS_HANDOFF.md) gives Opus/OpenCode an autonomous but bounded execution contract. Every phase has its own spec in [specs/](specs/).

## Definitions

- **COPY_FIRST:** prefer a physically inspectable, version-pinned, permission-qualified donor implementation to rewriting a proven function. Never equate *public competitor UI* with a right or ability to obtain its private backend.
- **RENAME:** user-facing names, active namespaces, interfaces and tests use Gomri where applicable. **Do not erase original copyright notices, LICENSE/NOTICE, source-attribution digests, license-bearing media metadata or import provenance**. Rename is a transformation, not concealment of source history.
- **NO_DUPLICATE_ENGINE:** keep existing Presenton-derived FastAPI, Next.js Template V2/Konva editor and bundled native export-core. Transplant the *smallest* required slice; do not copy a whole alternate editor or state management system.
- **NO_COST:** no billable hosted model/API and no surprise credits. A free-labelled remote model may be zero-price but is **not offline/private**; default to deterministic tests and local model inference if an actual local model is installed, otherwise review must explicitly declare the network/provider dependency or use OCR delegation without an LLM.
- **GATE:** a test or source inspection must return an explicit verified outcome; an unrun test, a skipped test, a model opinion or a prior-commit badge is not PASS.
- **PSTACK:** use already-installed local `ps-start`, `ps-spec`, `ps-build`, `ps-review`, `ps-doctor`, `ps-adr`, `ps-close` and `ps-dormammu` skills. Source instructions live under the user's `~/.agents/skills/ps-*`. Adapt output locations to this packet, **do not overwrite Gomri's existing root `CLAUDE.md` or original `docs/MASTER_PLAN.md`**.
- **E2E:** genuine headed or headless browser test using an isolated test account and synthetic deck; not just Node contract tests or desktop screenshots. The repo already has Cypress dev dependency and component config, but its E2E runner/binary has **not been verified as available**, so actual browser tests are a separate gate.

## Authority and build-state hierarchy

1. Actual main or exact PR #88 code; **main** was observed as `5f299a7`; PR #88 candidate `d4362c6` (both must be freshly checked).
2. [EGM authoritative P0 execution contract](../../designs/GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md) and [mandatory isolated preflight](../../designs/GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md).
3. This implementation packet's phases and per-file boundaries, **only for the phase whose gate has been passed**.
4. Donor source register and actual code content at SHA; research docs cannot override live source.
5. PStack reviewer outputs and Alibaba OCR findings **must reference exact changed source, test and file line**, with dispositions.
6. Human/owner PR approval before production merge/release, even if the implementation agent may autonomously prepare its draft PRs.

If these conflict, choose the narrower/safest interpretation, create a small ADR, and do not edit the main/product state until clarified through source-based evidence.

## First concrete action for a builder

Read [specs/00-qualify-baseline.md](specs/00-qualify-baseline.md). It gives the exact source and write boundaries, a safe offline Python-3.11 environment admission procedure, the next cross-owner and concurrent-save negative tests and what to do if the environment remains blocked. The prior measured [P0b execution ledger](../../designs/evidence/P0B_EXECUTION_LEDGER_2026-11-09.md) records 61/61 targeted Node tests, but **speaker notes lost on PPTX reimport and bullets flattened to text**; don't mark these parity gates green.

Only after S00's safety gates may agents start S01+ as constrained feature PRs.

## Milestones that are *not* release blockers

Massive stock catalogs, paid B2B white-label APIs, full social scheduling, unlimited fonts, collab CRDT, AI image inpainting/Object Grabber, real-time video export, native macOS/Linux packages, all 85 VistaCreate design formats, and blindly reproducing all third-party competitor private source. Preserve as optional future backlog.

## Expected artifact sequence

`S00 baseline/permissions -> S01 evidence compiler -> S02 four smart layouts -> S03 scoped edit -> S04 native PPTX/RTL/notes -> S05 isolated E2E/accessibility -> S06 hardening and draft release decision -> S07 optional multi-aspect/adaptive media.`

Parallel source audits/design experiments may run, but **only one agent may author canonical scene model, persisted slide write route or export-core in a single dependency wave**.

**Decision: the *specification* can now be handed to implementation agents; the *production feature writes* remain subject to safety gates and exact-head test evidence.**
