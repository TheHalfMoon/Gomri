# GPT Slides Engine — Deep REA and Source-First Gomri Blueprint

**As of 2026-11-09.** Research-only. Based on official product documentation, public UI evidence, and actual inspected owner-controlled code. No ChatGPT Slides private implementation, reverse-engineered internal endpoint, or authenticated competitor session was accessed.

## Read the full report

1. **[01 — Behavioral reconstruction and technical unknowns](gpt-slides-engine/01-behavior-and-architecture.md)** — What the GPT Slides engine demonstrably does; which architecture claims would be fabricated; falsifiable hypotheses.
2. **[02 — Editable Deck IR and agent patch protocol](gpt-slides-engine/02-deck-ir-agent-patches.md)** — Proposed typed element graph, source-to-narrative path, scoped AI transactions, rollback, exact access and negative tests; real Ninerr code bridge.
3. **[03 — Rendering, collaboration, export and security](gpt-slides-engine/03-render-collaboration-export.md)** — Canvas/HTML/PPTX parity, RTL, charts, comments/@agents, version conflicts, role/security boundaries, bounded donors.
4. **[04 — 50-case black-box protocol and implementation gates](gpt-slides-engine/04-blackbox-50-and-execution.md)** — Fifty named hypothetical tests with expected observations, benchmark rubric, risks, donor-source waves and exact completion gates.
5. **[175-row capability / gaps / uncertainty registry](../../registry/chatgpt-slides-capability-matrix-2026-11-09.csv)** — Twelve domains; documented vs marketed vs unknown, proposed Gomri owner and acceptance test per row.

**Important:** 175 records are NOT 175 independent GPT Slides capabilities. They represent operations, unknowns, product boundaries and proposed tests. The registry has 100 documentation-cited rows, 30 marketing/example-cited rows and 45 unknown/engineering-goal rows; count repeated documentation statements once when reporting external feature claims.

## Technical conclusion

The hard part to reproduce is **not a prompt-to-image slide generator**. The visible first-party product connects: conversational/file/template creation, an editable scene with typed text/images/shapes/tables/charts, selection-scoped AI edits, deck-wide revisions, human/team comments, concurrent collaborative editing, and native export.

These observed behaviors do NOT disclose OpenAI's internal schema, LLM topology, editor framework, renderer, collaboration algorithm or export implementation. The NextSlide team's move to OpenAI likewise is NOT proof of source availability.

## How to build a superior independent Gomri engine

**Keep:** the qualified Presenton-derived editor, layouts, FastAPI/Next.js/Electron, and native export path.

**Copy bounded real owner source:** Ninerr's MCP selection, authorization, agent/human history transactions and undo agent change; align to Gomri Deck IR rather than importing a second design-document authority.

**Reuse existing draft work:** PR [#88](https://github.com/TheHalfMoon/Gomri/pull/88) contains evidence-linked narrative, Arabic/RTL, animation and real PPTX export-fidelity tests with local Windows passes. PR #88 is an **OPEN DRAFT**, not on main; the exact combined code needs remaining FastAPI + CI qualification.

**Add:** scoped typed AI patches; stable object IDs/revisions and per-action receipts; independent claim verification after edits; consistent HTML/editor/PPTX render checks; reference-deck style transfer from Skilit; then comment-triggered agents and multi-user collaboration.

**Do not claim:** OpenAI's internal engine was copied, perfect PPTX fidelity, ChatGPT Slides access in this study, or a completed Gomri product.

## Recommended build order

| Wave | Capability | Acceptance |
|---|---|---|
| GSE-01 | Selected object -> AI typed patch, approval/undo, conflict detection | 15 negative/positive cases, no unrelated changes |
| GSE-02 | Source/narrative integrity after every edit | Numbers, units, entities and citations trace to permitted evidence |
| GSE-03 | HTML/editor/native export parity | Semantic text/chart/table/shape retention, Arabic, overflow, notes |
| GSE-04 | Brand/reference style intelligence | Render-based style grading, source and asset notices |
| GSE-05 | Comment -> agent action | ACL, task receipts, cancellation, retries, exact-scope edits |
| GSE-06 | Real-time coedit | One server authority or one evaluated CRDT; concurrency evidence |
| GSE-07 | Google Slides native handoff | Editable data survives round trip |
| GSE-08 | Head-to-head competitive evidence | 50 matched synthetic cases, masked human scoring |

## Core official evidence

- [ChatGPT Slides help](https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt)
- [ChatGPT Slides product](https://chatgpt.com/features/slides/)
- [Space collaboration](https://learn.chatgpt.com/docs/space/collaboration)
- [ChatGPT for PowerPoint](https://help.openai.com/en/articles/20001242-chatgpt-for-powerpoint)
- [ChatGPT Work artifact workflow](https://help.openai.com/en/articles/20001278-creating-and-editing-documents-spreadsheets-and-presentations-with-chatgpt-work)
- [OpenAI Presentations plugin](https://openai.com/business/plugins/presentations/)
- [NextSlide founder announcement](https://nextslide.ai/)

## Actual inspected owner code

- [Gomri current integration candidate](https://github.com/TheHalfMoon/Gomri/pull/88)
- [Gomri draft narrative engine](https://github.com/TheHalfMoon/Gomri/blob/feat/gomri-source-fasttrack-20261109/servers/fastapi/gomrey/narrative.py)
- [Gomri draft HTML slide renderer](https://github.com/TheHalfMoon/Gomri/blob/feat/gomri-source-fasttrack-20261109/servers/nextjs/lib/template-v2-json-to-html.ts)
- [Ninerr agent/MCP selection and transaction rules](https://github.com/TheHalfMoon/Ninerr/blob/main/docs/MCP.md)
- [Skilit architecture](https://github.com/TheHalfMoon/Skilit/blob/main/ARCHITECTURE.md)

**Disposition:** research complete at the public-evidence level; actual authenticated black-box REA remains NOT RUN; proposed product code remains NOT IMPLEMENTED by this research PR.
