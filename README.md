# Gomrey

Gomrey is an agent-first, evidence-grounded creation and knowledge platform for humans and AI agents.

## Product thesis

Gomrey combines source ingestion, multimodal document understanding, NotebookLM-class research/RAG, calibrated decision and verification, and artifact creation into one system. It is designed to accept large heterogeneous source collections and produce inspectable, editable, evidence-backed outputs such as presentations, documents, reports, websites, infographics, podcasts, and agent-consumable structured results.

## Engineering doctrine

- **Copy/adapt before building.** If a mature authorized or permissively licensed implementation already solves a bounded problem well, reuse it behind Gomrey-owned contracts instead of rebuilding it.
- **Agent-first parity.** A capability is not complete until it has a structured API/tool surface suitable for agents, not only a human UI.
- **Evidence before fluency.** Generated claims are never treated as true merely because a model produced them.
- **No silent source loss.** Large ingestion jobs must account for every declared source unit and expose explicit unresolved/failed states.
- **Confidence is not authority.** Jev-class decision models are advisory providers behind Gomrey-owned policy and verification contracts.
- **Local/self-hostable paths remain first-class.** Hosted providers may be optional adapters, not hidden correctness dependencies.
- **Provenance is mandatory.** Copied/adapted code, models, assets, datasets, and source content keep exact source identity, rights, notices, and modification records.

## Canonical foundation package

- [Master implementation plan](docs/MASTER_PLAN.md)
- [Canonical architecture](docs/ARCHITECTURE.md)
- [Source and donor ledger](docs/SOURCE_LEDGER.md)
- [Agent platform: MCP, A2A and plugins](docs/AGENT_PLATFORM.md)
- [Jev build and Decision Fabric policy](docs/JEV_BUILD_POLICY.md)
- [Mandatory review and evidence policy](docs/REVIEW_POLICY.md)
- [No-gaps program checklist](docs/NO_GAPS_CHECKLIST.md)

The first implementation phase imports the admitted Presenton base as a working product before replacing or extending subsystems. Gamma source is treated as an authorized selective donor only after an exact source snapshot and provenance boundary are supplied.
