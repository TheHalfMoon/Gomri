# GPT Slides Engine REA — 02: Editable Deck Model and Agent Patch Runtime

**Purpose:** engineer a reusable Gomri engine to reproduce verified GPT Slides user-facing behavior. This is a proposed independent implementation, **not** OpenAI's private protocol.

## 1. Source compilation and content control

Gomri already has a canonical source/evidence foundation in servers/fastapi/gomrey. On the draft integration PR #88, servers/fastapi/gomrey/narrative.py contains real functions: build_narrative_plan, render_plan_context, build_narrative_ir, check_plan_containment, bind_slide_locators and assert_exportable. The file explicitly records a limit: numbers and dates are gated but entity/units coverage is incomplete.

We should preserve these source revisions and claim verifications through every slide mutation. Never let an AI edit bypass verification simply because the first generation was verified.

Proposed phases:

1. Normalize chat/files/spreadsheets/pages into SourceIR with revision, ACL and exact page/cell locator.
2. Compile intent: objective, target audience, locale, content scope, deck length, target export, preserve constraints.
3. Assemble NarrativeIR: slide objectives, takeaway, evidence claim IDs, uncertainty/abstention, optional notes.
4. Compile DesignIR: theme, layout roles, reference deck, editable shapes, charts, tables, media with provenance.
5. Assemble a versioned DeckIR, render, inspect layout, apply controlled auto-repairs, persist.

The five phases are an architectural recommendation, **not** a disclosed GPT Slides pipeline.

## 2. Canonical Deck IR

Recommended discriminated element types:

| Element type | Native semantics | Export risk |
|---|---|---|
| text | rich runs, font, logical Unicode, direction, bounding geometry | flattened runs; font substitution; RTL reorder |
| image | asset digest, crop and focal point, alt text, permissions | replaced media, broken link, unexpected crop |
| shape | primitive/vector path, stroke/fill/transform, grouping | rasterization or unsupported path |
| table | rows/cells, text runs, style, merge spans, column widths | flattened text or merged-cell loss |
| chart | categories, editable series data, labels, axes, orientation | chart becomes a picture |
| group | child IDs, z-order, nested transforms | flattening and hierarchy loss |
| diagram | nodes/edges/labels semantic graph | native editability may be unavailable |
| notes | rich speaker notes per slide | loss on PPTX reimport |

Mandatory fields:
- deckId, schemaVersion, deckRevision, locale, slideId/order.
- elementId and objectRevision for each element, stable even after reordering.
- styleRef to theme token, geometry in canonical units, preserved sourceRef/claimIds.
- dedicated source registry; no private full source text embedded in exported artifacts by accident.
- generic imported unknown object retained read-only with unsupported status until supported.

Prevent duplicate IDs, unbounded recursion, invalid float geometry, external remote script injection, and malformed relationship graphs.

## 3. Typed patch protocol

AI should produce operations, not authority-bearing program code. Example Gomri request:

    {
      "deckId":"deck_42",
      "baseRevision":118,
      "actorId":"agent_review_01",
      "selection":{"slideIds":["slide_02"],"elementIds":["el_chart_7"]},
      "intent":"Update this chart from approved Q2 data",
      "preserve":["other_elements","existing_claim_ids","deck_theme"],
      "operations":[
        {
          "op":"set_chart_data",
          "elementId":"el_chart_7",
          "expectedObjectRevision":9,
          "sourceRef":"sheet_v12#Sheet1!B2:F8"
        }
      ],
      "idempotencyKey":"task_19:attempt_1"
    }

Proposed explicit op types:
- set_text_runs, set_style, set_geometry, replace_image, set_table_cells, set_chart_data.
- add_slide, move_slide, delete_slide, clone_element, group_elements.
- attach_evidence, resolve_comment, set_notes.
- No arbitrary JavaScript evaluation, filesystem/network authority or untrusted HTML rendering in patch payload.

Each operation has a typed inverse for undo, a fixed affected-elements set, a before/after semantic diff and a human-readable explanation.

## 4. Transaction validation

A safe write should run in this order:

1. Authenticate actor and resolve editor/session identity.
2. Check deck ACL and source ACL separately; require agent's previous read context to match this deck.
3. Validate JSON schema, target scope, current element IDs and protected fields.
4. Reject negative or enormous dimensions, NaN, runaway recursion, missing assets, unauthorized source references.
5. Validate intended semantics: numbers, dates, units, named entities, citations, embedded chart data.
6. Run layout/contrast/bidi checks on isolated proposed state.
7. Compare base revision with current revision. Rebase only independent disjoint edits; refuse same-object conflict or deleted target.
8. Ask a human for consequential/destructive changes.
9. Commit once with an idempotency key, actor attribution and append-only receipt.
10. Keep a reversible inverse mutation; publish a change event and export invalidation.

Typed errors: INVALID_OPERATION, OUT_OF_SCOPE, NOT_AUTHORIZED, SOURCE_FORBIDDEN, TARGET_GONE, STALE_REVISION, LOSSY_EXPORT, EVIDENCE_MISMATCH, UNSUPPORTED_ELEMENT, REVIEW_REQUIRED.

## 5. Concrete owner-controlled source: Ninerr

Inspected TheHalfMoon/Ninerr docs/MCP.md and README. Unlike the unknown internal GPT Slides engine, this is code we can actually reuse:
- packages/mcp-protocol/src/tools.mjs — enumerated 18 read/write tools and tool classifications.
- packages/mcp-protocol/src/authorization.mjs — authorization with scoped tools, actor/document, policy revision.
- packages/studio-host/src/mcp.ts — runtime MCP gate before write, per-agent project identity.
- packages/history, packages/document-model, packages/persistence — journal/history/undo components.
- User can choose an element via selection, agent writes are history transactions, Undo agent change is explicitly implemented.
- Destructive delete calls require person confirmation. The mechanism checks exact tool, document, actor and argument digest.

**Copy strategy:** copy the smallest tested protocol/transaction slice into a Gomri adapter; do NOT replace Presenton's Canvas/Template V2 node representation with Ninerr's HTML/CSS authoritative document.

## 6. Required tests (concrete)

| Test | Input | Expected |
|---|---|---|
| PATCH-01 | Select title, ask shorten | Only selected text runs altered |
| PATCH-02 | Ask to edit slide count out of scope | OUT_OF_SCOPE, no mutation |
| PATCH-03 | Target element deleted before commit | TARGET_GONE, no resurrection |
| PATCH-04 | Concurrent human+AI different elements | Both survive |
| PATCH-05 | Concurrent human+AI same chart | Explicit conflict, no lost data |
| PATCH-06 | Replay exact request twice | One visible committed effect |
| PATCH-07 | Agent tries to edit unread deck | NOT_AUTHORIZED |
| PATCH-08 | Viewer requests edit via comment | NOT_AUTHORIZED |
| PATCH-09 | Agent deletes slide without approval | REVIEW_REQUIRED |
| PATCH-10 | Update verified 25% to invented 40% | EVIDENCE_MISMATCH |
| PATCH-11 | Undo agent change after later user edit | Only agent's compatible patch undone |
| PATCH-12 | Restore after crash during commit | Exactly-once effect / replay-safe receipt |
| PATCH-13 | Arabic and Latin Unicode text edit | Correct direction and content |
| PATCH-14 | Reorder slides with citations/comments | Stable element/anchor/source identities |
| PATCH-15 | Export after patch | Verified/unsupported facts surfaced, not silently hidden |

## 7. Exit criteria

- One canonical editable Deck IR, not parallel JSON stores.
- Stable element selection with targeted AI edits and explicit diff preview.
- Human/agent tools share one permission and transaction layer.
- True undo-agent-edit and crash-safe idempotency.
- No first-party original source replaced without regression tests.
- Both FastAPI and Next.js negative controls pass at exact tested candidate; GitHub CI passes before merge.

This is **GSE-01**, the highest-leverage first engineering grain. Existing W3 in PR #88 is a dependency, not proof this new patch runtime exists.

Sources: https://github.com/TheHalfMoon/Gomri/pull/88 ; https://github.com/TheHalfMoon/Ninerr/blob/main/docs/MCP.md ; https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt
