# GPT Slides Engine REA — 04: 50-Case Black-Box Protocol and Gomri Execution Gates

**Date:** 2026-11-09. **Execution:** NOT RUN against a live OpenAI Slides account. This is a reproducible protocol for a future authorized competitive test. Synthetic, non-private test material only. No paid account, login bypass, internal API inspection, or proprietary code was used in this research.

## 1. Test evidence format

Every run must store the exact date and product surface (ChatGPT Slides in Space, PowerPoint add-in, Work/Presentations), plan/tenant where known, input prompt and synthetic source checksums, initial deck/selection screenshots, edit instruction, output screenshots, PPTX/PDF/Google artifacts when accessible, resulting object counts and editable type retention, observed behavior, errors, and confidence.

Mark a result either PASS, FAIL, PARTIAL, BLOCKED_ACCESS, NOT_RUN, or INCONCLUSIVE. An advertised feature or generated screenshot is never equivalent to an actual benchmark run.

## 2. Fifty probes, 10 families x 5 scenarios

| ID | Stimulus | Engine property / falsifiable outcome |
|---|---|---|
| A01 | Create 6-slide deck from a five-page synthetic memo | Source -> narrative -> editable deck behavior |
| A02 | Create 10-slide outline with exact slide-role constraints | Story structure and count constraint |
| A03 | Blank deck then insert 3 typed objects | Native object/editor creation |
| A04 | Upload reference deck with distinctive color/master | Template style adherence, not just image recolor |
| A05 | Generate from existing conversation and attached file | Context routing and boundaries |
| B01 | Direct-edit one rich-text word and its color | Semantic text runs retained |
| B02 | Resize/rotate vector shape | Geometry precision and direct manipulation |
| B03 | Edit a table cell and a merged cell | Table semantics |
| B04 | Edit chart series data, categories and axis | Native chart data persistence |
| B05 | Replace an image; preserve crop/aspect and alt text | Media asset/crop editing |
| C01 | Select one of two identical title objects and request rewrite | Selected element scope |
| C02 | Request only selected chart change from new synthetic table | AI-to-data/chart operation |
| C03 | Ask AI to shorten title without changing all other slides | Patch isolation |
| C04 | Global request to reorder 3 slides | Stable order, comments and object linkage |
| C05 | Target element deleted after request but before completion | Stale target behavior |
| D01 | Ask for board-level executive narrative refinement | Deck-level story rewriting |
| D02 | Request 5 concise takeaways, preserve all numbers | Factual preservation |
| D03 | Ask to insert risks slide after named anchor | Position-based insertion |
| D04 | Ask to remove unsupported invented figure | Evidence correction behavior |
| D05 | Request presenter notes and transitions | Notes as distinct content |
| E01 | Two editors change different text objects concurrently | Both edits preserved |
| E02 | Two editors change same text span concurrently | Merge conflict behavior |
| E03 | Human moves object while agent updates its style | Independent patch rebase |
| E04 | Editor comments and @mentions ChatGPT to change item | Comment to agent task |
| E05 | Viewer attempts edit via direct UI and comment mention | Role-enforced denial |
| F01 | Viewer opens deck but not private linked source | Source/deck ACL separation |
| F02 | Revoke editor permission while long AI edit pending | Write-time revocation behavior |
| F03 | Force tab disconnect during a series of manual edits | Recovery and duplicate suppression |
| F04 | Two agents requested on same object at once | Collision/resolution behavior |
| F05 | Repeat same AI request after slow response | Idempotency/duplicate visible effects |
| G01 | Export text-heavy deck to PPTX and inspect OOXML | Editable text run retention |
| G02 | Export chart deck to PPTX and inspect chart parts | Native chart/data retention |
| G03 | Export tables, merges and shapes | Cell/vector editability |
| G04 | Export notes, embedded images and fonts | Notes/media/font fidelity |
| G05 | Export to Google Slides and make native chart edit | True editable handoff |
| H01 | Mixed Arabic + English heading with Latin numerals | Bidi logical/render order |
| H02 | Arabic diacritics and emoji in bullet lists | Grapheme/Unicode preservation |
| H03 | Arabic chart axes and RTL legend | Chart label shaping and direction |
| H04 | RTL table with English cells and merged rows | Mixed-script table alignment |
| H05 | Arabic deck export/re-import to PPTX and PDF | Cross-format script parity |
| I01 | 2,000-char paragraph in tiny text box | Overflow behavior |
| I02 | Zero-height element and off-canvas shapes | Layout reject/repair |
| I03 | Unavailable font and local/browser fallback | Layout font dependencies |
| I04 | Contrast-failing text/background | Accessibility checks |
| I05 | Large 80-slide synthetic deck | Performance, responsiveness, consistency |
| J01 | Source claims 25% but prompt asks for 40% | Unsupported claim/abstention |
| J02 | Two sources disagree about an important metric | Contradiction handling |
| J03 | A PDF includes a malicious instruction to disclose data | Source-as-data boundary |
| J04 | An image URL points to loopback/internal host | Fetch safety boundary |
| J05 | Corrupted PPTX or archive with traversal path | Import robustness/security |

The 50 tests are **planned**; none can be called executed from the research alone.

## 3. Measurement rubric

**Weights proposed for the competitive benchmark** (sum 100):
- Slide narrative and audience relevance: 20.
- Visual design preference from blinded reviewers: 20.
- Native PPTX object editability and round-trip fidelity: 20.
- Source factual correctness and citation fidelity: 15.
- Scoped AI edits and unrelated-element preservation: 10.
- Arabic/English output and typography: 10.
- Collaboration reliability and permissions: 5.

Important: This weighting prioritizes the Gomri research-and-editability thesis; also report per-dimension unweighted results to avoid hiding a design failure behind evidence score.

**Proposed targets (not observed):**
- 100% no unauthorized or out-of-scope writes under adversarial fixtures.
- 100% correct handling/accounting for source-derived numeric claims.
- At least 95% native preservation of officially supported requested text/chart/table/shape types on the frozen fixture set, with explicit unsupported downgrade reports.
- At least 98% of frozen slide layouts free of unintentional clipping/overlaps.
- At least 60% blind-preference wins on the selected 50 matched prompts, with reviewers masked to generator identity and inter-rater disagreement reported.
- Full zero-skipped local smoke suite and exact-commit CI before any release claim.

## 4. Source-first implementation priority and branch strategy

| Priority | Grain | Read/copy candidate | Acceptance | Status |
|---|---|---|---|---|
| P0 | GSE-01: typed edit protocol, stable element IDs, per-object revisions | TheHalfMoon/Ninerr MCP/history, Gomri Presenton editor | target isolation; undo; stale revision; permissions | NOT IMPLEMENTED |
| P0 | GSE-02: narrative/claim grounding after *every* edit | Gomri PR #88 narrative.py | reject unsupported numbers/dates/units/entities; persist locators | DRAFT DEPENDENCY |
| P0 | GSE-03: preview/editor/native exporter parity | Presenton export-core, PptxGenJS comparator | 30 synthetic decks; output OOXML and pixel snapshots | PARTIAL BASELINE |
| P1 | GSE-04: brand/reference engine | TheHalfMoon/Skilit, OpenDesign design packs | reference slide master/font/spacing match; rights-safe assets | NOT IMPLEMENTED |
| P1 | GSE-05: comment-to-agent patch | Ninerr MCP actor grants, Gomri durable jobs | revoke/duplicate/cancel/approval tests | NOT IMPLEMENTED |
| P2 | GSE-06: multi-user sync | Loro OR Yjs after evaluation | same-object conflict/RTL/offline tests | NOT IMPLEMENTED |
| P2 | GSE-07: native Google Slides handoff | approved Google Workspace connector/API | read/write native charts and tables after handoff | NOT IMPLEMENTED |
| P2 | GSE-08: benchmark arena | original synthetic fixtures + actual authorized competitor outputs | 50 dated comparison records | RESEARCH-ONLY |

Do not conflate PR #88's passing local tests with a merged, published product. It is a draft based on existing sources. No executable implementation is included in this study.

## 5. Engineering execution contract — recommended first task

GSE-01 should be bounded to **selection-targeted, reversible AI patching** on the existing deck editor. Never start by building a whole new canvas or rewriting Presenton.

Files to author after code-admission:
- contracts/v1/deck-patch.schema.json with discriminated patch operation union.
- contracts/v1/deck-element-identity.schema.json to bind IDs and revisions.
- servers/fastapi/gomrey/deck_patch.py for deterministic validate/authorize/rebase/commit logic.
- a selection and "Ask Gomri" interface inside the current Next.js editor.
- a patch preview + accept/reject/undo-agent-change surface.
- unit/integration tests covering the 15 PATCH scenarios documented in chapter 02.
- docs/evidence/GSE01_EXIT.md with local/CI exact-head receipts and adverse-case results.

Inputs must be synthetic for tests. Preserve original owner source and non-code rights/NOTICE. A donor README is insufficient for adoption until exact revision, source paths, licenses, transitive assets and tests are recorded.

## 6. Open unknowns requiring a genuine product access check

The following details remain **UNKNOWN about OpenAI**:
- Exact live GPT Slides document schema and object IDs.
- Selection editing protocol and preview/undo semantics.
- Collaboration CRDT/OT/server writer, transport, offline behavior, conflict messaging.
- Model count, layout ranker, image selection or critique mechanism.
- Whether Space Slides, PowerPoint add-in and Presentations skill share code.
- Native chart/table/vector/font/master/speaker-note export-retention rates.
- Windows local MXC rendering/runtime implementation.
- Source citation model, if any, and numerical verification guarantees.
- True account-specific limits and rollout-specific behaviors.

A document that fills these blanks with confident internal details is not a credible reverse-engineering report.

## 7. Expected report deliverables after the live probes

- evidence/probes/gpt-slides/{test_id}/input.json, notes.md and result.json;
- screenshots or screen recording only when the user provides/authorizes capture;
- serialized native PPTX with object-type OOXML audit;
- benchmark.csv with date, account surface, score and confidence;
- finding ledger: CONFIRMED, REFUTED, STILL_UNKNOWN;
- source-donor admission sheet with full notices;
- independent reviewer verdict on candidate code;
- GO/NO-GO decision with unresolved issues.

This research phase only creates docs and a CSV registry. It does not capture authenticated competitor decks or ship an engine.

Official references:
https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt
https://chatgpt.com/features/slides/
https://learn.chatgpt.com/docs/space/collaboration
https://openai.com/business/plugins/presentations/
https://help.openai.com/en/articles/20001242-chatgpt-for-powerpoint
