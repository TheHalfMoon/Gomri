# Gomri

**Research with evidence. Create with precision. Present beautifully.**

Gomri is an agent-first, evidence-grounded creation and knowledge platform for people and AI agents. The ambition is to combine genuinely editable, high-quality presentations with source-aware research, document understanding, citations, verification, and multi-format artifact creation.

## Current project status

- **Repository name:** Gomri (`TheHalfMoon/Gomri`).
- **Execution foundation:** an exact, documented import of [Presenton](https://github.com/presenton/presenton), with its applicable licenses and notices preserved.
- **Implemented foundation:** phased code and evidence through P09 cover contracts, resilient jobs, source-unit accounting, ingestion/worker interfaces, web/media/connector primitives, retrieval/citation contracts, and deterministic claim verification.
- **Not yet certified as complete:** deep-research/notebook product, redesigned creation compiler, collaboration, full agent platform, benchmarking, installers, and general release (P10–P16).
- **Brand migration still required:** internal application/package/runtime identifiers continue to use the historical `Gomrey` spelling. This is intentional until a tested, backward-compatible migration is qualified. Do not rename persisted state or environment variables blindly.

## Product principles

1. **Editable means editable.** Slides and their semantic objects must survive real PowerPoint round-trips; declare any rasterized fallbacks.
2. **Evidence before fluency.** Source identity, claim support, citation locators, stale/conflicting sources, and explicit abstentions are first-class.
3. **Design quality is measurable.** A deck is not complete merely because it renders. Visual, narrative, accessibility and export quality need independent tests.
4. **One product for humans and agents.** User interface, APIs, and eventually MCP/A2A tools operate through the same authorized artifact contracts.
5. **Local and self-hosted paths matter.** Optional hosted providers cannot become hidden correctness dependencies.
6. **Reuse proven sources carefully.** Pin exact revisions and preserve applicable code, model, media, data, font, and asset rights and notices.

## Project documentation

- [Competitive review and source shortlist — 9 November 2026](docs/research/GOMRI_COMPETITOR_SOURCE_AUDIT_2026-11-09.md)
- [Master implementation plan](docs/MASTER_PLAN.md)
- [Canonical architecture](docs/ARCHITECTURE.md)
- [Source and donor ledger](docs/SOURCE_LEDGER.md)
- [Agent platform](docs/AGENT_PLATFORM.md)
- [Review and evidence policy](docs/REVIEW_POLICY.md)
- [No-gaps acceptance checklist](docs/NO_GAPS_CHECKLIST.md)

**Provenance:** The original Presenton donor README remains at `docs/donors/presenton/UPSTREAM_README.md`. Historical documents and exact evidence references retain their original names. Gamma and NextSlide are competitor references; no inaccessible proprietary source is assumed to be available.
