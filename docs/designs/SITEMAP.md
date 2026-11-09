# Gomri EGM Design Index

**Updated:** 2026-11-09. **Base:** main `5f299a7`. All files on this EGM planning branch are **design/review only**, not production integration.

| Document | Status | Purpose |
|---|---|---|
| [Converged editor plan](GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md) | **v2, CONDITIONAL / P0 ONLY** | One source-to-editable-PPTX journey, staged SmartLayout and agent edit gates |
| [Current v1 save-path audit](GOMRI_EGM_P0_WRITE_PATH_AUDIT_2026-11-09.md) | Code inspection complete; negative tests **NOT RUN** | Observed autosave, PATCH endpoint and transaction/authorization gaps to verify |
| [Goldfish Zoom Out](reviews/2026-11-09/goldfish-zoom-out.md) | Independent model response, **CONDITIONAL** | Reuse and scope stress test |
| [Goldfish Design Critic](reviews/2026-11-09/goldfish-design-critic.md) | Independent model response, **CONDITIONAL** | CAS, ownership, Undo and export/OOXML integrity risks |
| Post-fix Zoom Out / Implementation Readiness | Pending | Must check the revised design before production writes |

**Important:** The EGM official five-stage review orchestrator was not executed end-to-end. Fresh independent OpenCode reviewer sessions implement selected reviewer perspectives; empty/time-out responses are not passes. The actual codebase source audit is separate from the independent reviewers.

Legacy references are `docs/MASTER_PLAN.md` and `docs/ARCHITECTURE.md` on main; unmerged PR #88 contains candidate features and #89–#92 contain separate research. These are **not assumed shipped**. Only the read-only P0 audit and proposed negative tests may proceed while EGM approval remains conditional.
