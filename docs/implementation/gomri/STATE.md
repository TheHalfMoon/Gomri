# Gomri — PStack Session State

**Updated:** 2026-11-09. **Planning branch:** `plan/egm-converged-gomri-20261109` (Draft PR #93). **Execution phase:** **S00 — partially qualified / environment BLOCKED**. This is a planning handoff, not an automated job or a verified running builder.

## Where we are

Gomri already has a Presenton-derived Next.js/Template V2/Konva editor, FastAPI backend and native export-core. PR #88 is **DRAFT, unmerged** candidate integration at the previously observed `d4362c6d968d2746d499630d8498d3111c98c90b`. All current SHA and CI states must be refreshed at execution.

P0a route/owner/export audit is documented in PR #93. Seven targeted Windows groups at PR #88 exact commit passed **61/61 tests**. The 15 PPTX tests **document native limitations**: notes written to export but not reimported; bullet semantics flattened to text. This is NOT complete native fidelity or security QA.

Actual backend A/B owner PATCH and stale-write/CAS tests remain **BLOCKED** because no suitable isolated Python 3.11 FastAPI/SQLModel/SQLAlchemy/aioSQLite test environment was qualified. Cypress package is locally installed but full E2E browser binary and suite are not verified. A full official Google EGM review orchestrator was not completed.

## In flight

Only **S00 read-only preflight, offline environment qualification and disposable synthetic tests** can start under the controlling EGM contract. New product code and persistence changes require safety test evidence and separate phase approval. Do not invoke PStack skills from repository root if they might overwrite root files: run PStack documentation steps with this folder as cwd.

## Next steps

1. Run `/ps-resume` and `/ps-doctor` from this directory; map verified local providers and missing capabilities.
2. Recheck active source Git SHA / PR #88 head, existing active worktrees and free disk without mutating user files.
3. Create a **new disposable test checkout** and Python 3.11 test-only venv from audited offline dependencies if present; if not, use the S00 bounded official-PyPI wheel admission with explicit allowlist, hashes and disk cap; if unqualified, list the missing wheels and BLOCKED cause.
4. Create real authenticated owner A/B SQLAlchemy negative tests on isolated SQLite; trace cross-client autosave/CAS, Undo, export revocation; preserve unique attempt receipts.
5. Qualify Cypress binary and test runner in a separate scratch environment without Cypress Cloud or real profiles.
6. Run a **fresh independent /ps-review** on evidence and blocker resolutions. If GO, open narrowly scoped S01/S02 draft feature PRs and retain S03 persisted writes behind S00 safety gate.

## Decisions and blockers

- **D001:** Keep one editor/canonical slide store; bounded copy-first adapters only; source/NOTICE retained.
- **D002:** One atomic server CAS authorization boundary for **all** writers before AI persistence. Existing owner middleware/ORM select filters are real; a cross-owner exploit is NOT proven.
- **D003:** Windows and local-first, zero unapproved paid provider calls, synthetic test data.
- **B001:** Python 3.11 isolated backend dependencies absent at previous check — S00 blocker.
- **B002:** Real two-owner route, stale writer and redo/Undo tests unrun — S03 write blocker.
- **B003:** Speaker notes reimport and bullet semantics lost — S04 release blocker.
- **B004:** Cypress browser binary and full user E2E unqualified — S05 release blocker.
- **B005:** Independent Alibaba AI review not done; local Delegation file/rules selection succeeded — S06 review blocker.

## Last safely completed work

Created `docs/implementation/gomri/` packet with PRODUCT/ROADMAP/CLAUDE/AGENTS/ROLES, donor admission registry, eight phase specs, E2E/OCR contract and Opus handoff. A read-only Git check of earlier donor SHAs confirmed five named source commits exist. The committed Python validator was rerun after handoff additions: 23 packet Markdown files, 27 total documents, 74 internal references and 15 donor rows at planning head d0e20e9b, **PASS/zero structural errors**. Runtime security/E2E is still a separate gate. No product source files changed, no merge or deployment. **The user has approved preparing the plan for implementation, not bypassing untested production write gates.**
