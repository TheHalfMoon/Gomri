# Gomri EGM Planning and Review Index

**Updated:** 2026-11-09. **Base:** main 5f299a7. **State:** CONDITIONAL. Planning/source-inspection artifacts only; no Gomri product feature code changed, no P0b application tests executed, and no user data touched.

| Resource | Current evidence / approval |
|---|---|
| [Converged design v4](GOMRI_EGM_CONVERGED_EDITOR_2026-11-09.md) | Plan for one source-to-native-editable-PPTX experience; P0a/P0b permitted under bounds, P1/P2 NO-GO |
| [Authoritative P0a/P0b execution contract](GOMRI_EGM_P0_EXECUTION_CONTRACT_2026-11-09.md) | Source tracing versus disposable testing clearly separated |
| [Mandatory P0b test isolation and phase permissions](GOMRI_EGM_P0B_ISOLATION_CONTRACT_2026-11-09.md) | Ephemeral source checkout/DB/accounts/storage, offline/provider controls, cleanup receipts; preflight NOT RUN |
| [Original P0 source audit with corrected protection finding](GOMRI_EGM_P0_WRITE_PATH_AUDIT_2026-11-09.md) | Source inspection of v1 PATCH, local autosave; ORM owner filters and middleware are present; no vulnerability claimed |
| [P0a route, owner and symbol matrix](evidence/P0A_ROUTE_SYMBOL_MATRIX.md) | **SOURCE REVIEW DONE**, actual routes and existing auth/ORM policies identified; tests NOT RUN |
| [P0a PPTX, speaker notes and export map](evidence/P0A_EXPORT_NOTES_MAP.md) | speaker_note exists; PPTX notes/reimport and permission-at-delivery test NOT RUN |
| [P0a PR exact-head ledger](evidence/P0A_PR_BASELINE.md) | PRs #88–#92 all open/Draft with pinned SHAs; CI not assumed passed |
| [Goldfish Zoom Out](reviews/2026-11-09/goldfish-zoom-out.md) | Independent early review CONDITIONAL |
| [Goldfish Design Critic](reviews/2026-11-09/goldfish-design-critic.md) | Independent early review CONDITIONAL |
| [Post-fix Goldfish Zoom Out](reviews/2026-11-09/goldfish-postfix-zoom-out.md) | Independent second pass CONDITIONAL; drove explicit P0 split |
| [Implementation Readiness v3](reviews/2026-11-09/goldfish-implementation-readiness-v3.md) | Independent review: P0a GO; P0b CONDITIONAL; P1/P2 NO-GO; did not review v4 or execute tests |

## Decision ledger

**Allowed now:** P0a read-only source/contract refinement. **Conditionally allowed next:** P0b scratch-only suite execution **only after every test-group isolation preflight passes**. **Not allowed:** production feature-source writes, new agent save endpoints, SmartLayout persistence, user-data mutation, merges, releases, or announcing competitor superiority.

All role reviews used isolated OpenCode sessions with a free-labelled provider, **not Google's complete official five-stage EGM subagent orchestrator**. The reports are independent design critiques, not executed test receipts. The official EGM build-readiness process and human approval remain incomplete.

Legacy original plan: docs/MASTER_PLAN.md and docs/ARCHITECTURE.md on main. Integration PR #88 is unmerged; research PRs #89–#92 are unmerged. This PR (#93) remains Draft.
