# GPT Slides Engine REA — 01: Behavioral Reconstruction

**Date:** 2026-11-09. **Level:** documented behavior -> architectural requirements. This is NOT leaked or recovered OpenAI source.

## 1. Product surfaces that must not be conflated

| Surface | Runtime/user context | What is verifiable |
|---|---|---|
| ChatGPT Slides in Space | Shared, persistent visual deck | Editable elements, selected-object AI, deck prompt AI, concurrent users, comments, exports |
| ChatGPT for PowerPoint | Sidebar inside Microsoft PowerPoint | Native slide creation/editing; existing deck context; template and advanced-editor limitations |
| ChatGPT Work | Task-based artifact production | Attached sources, master/reference decks, saved templates, direct Google Slides where connector is enabled |
| OpenAI Presentations plugin | Tool-backed durable artifact creation | Create, inspect, render, verify and export local decks |

These workflows may cooperate but **shared internal code is not established**.

Sources: O1 https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt
O2 https://chatgpt.com/features/slides/
O3 https://help.openai.com/en/articles/20001242-chatgpt-for-powerpoint
O4 https://help.openai.com/en/articles/20001278-creating-and-editing-documents-spreadsheets-and-presentations-with-chatgpt-work
O5 https://openai.com/business/plugins/presentations/

## 2. Independently documentable public operations

**Create:** start blank or template in Space, ask Work to create a presentation from chat or attachments, reference an example deck. This proves inputs and an editable output, not an implementation order or named planner.

**Edit:** select an element and choose Request edits; a global prompt bar can change the deck. Text, images, shapes, tables and charts are editable directly. This proves element-scoped and deck-scoped operations, not which rendering library is used.

**Collaborate:** editors concurrently update the same deck, use shared comments and mention ChatGPT/dots. View and edit roles are available. Docs explicitly say separate comment-only permission is unavailable at launch, despite broader marketing phrasing.

**Export:** Present, PPTX, PDF, Google Slides, with caution to inspect output. No published 100% semantic object fidelity guarantee.

## 3. Essential engine invariants deduced from behavior

The editor must have a usable identity for the target element, a way to distinguish user edits from AI edits, a way to synchronize updates, and persistent enough state to export. It does NOT necessarily require Yjs, Loro, React, Konva, WebGL, a vector database, an agent swarm, OOXML as canonical storage, or any other specific implementation.

The minimum conceptual architecture for a competing system:

    Inputs -> Source/evidence registry -> Narrative intent
       -> Style and design constraints -> Typed editable Deck IR
       -> Renderer/editor -> Authoritative mutation/transaction log
       -> PPTX/PDF/Google adapters
    Comments and agents -> Permission check -> Scoped patch -> Mutation log

The boxes describe **our proposed Gomri engine**, not a claim about ChatGPT Slides internals.

## 4. Critical hypotheses to falsify in the real product

H1: GPT Slides may keep a semantic object graph instead of only rendered bitmaps. Evidence: direct chart/table edits and editable exports; contrary implementation could reconstruct objects on demand. Test by exporting and inspecting native OOXML chart/table objects.

H2: Selection-based agent edits likely address a bounded region of the document. Evidence: selected-element Request edits. Test by making two nearby objects nearly identical, requesting an edit on one, and comparing all object properties.

H3: Collaboration requires some conflict policy. There is **no evidence** whether OpenAI uses CRDT, operational transformation, locks or server-serialized writes. Test simultaneous same-object edits, deletion during AI run, reconnection, and revoked permissions.

H4: Reference-deck guidance likely extracts design attributes. Alternative: prompting directly over sampled slide images. Test unusual master layouts, limited fonts, inaccessible image assets and high density.

H5: There may be a rendering or verification loop. The product is visually polished and a separate Presentations plugin advertises rendering/verification, but **there is no evidence** they use the same engine. Test intentionally overlong text, chart axis overlap, small font substitution, then inspect whether the engine repairs or leaves defects.

## 5. Documented negative constraints

- Publicly available product pages do **not** disclose engine source code.
- NextSlide founder says the team joined OpenAI; that is organizational lineage only.
- No official source establishes a particular LLM/model chain, training data or proprietary renderer.
- Marketing screenshots are UI evidence, not correctness/benchmark evidence.
- PowerPoint help expressly notes that advanced editing and precise template matching may be limited.
- Screenshots alone cannot prove native editability, layout preservation or claim grounding.

Additional sources:
https://learn.chatgpt.com/docs/space/collaboration
https://nextslide.ai/

## 6. Proposed system acceptance gates

G1: an edit to selected element A never silently changes unrelated B.
G2: every accepted edit is undoable and attributed to human/agent.
G3: a stale or deleted target is refused or safely resolved, never blindly overwritten.
G4: active viewer never gains mutation privilege by mentioning an agent.
G5: every exported file is inspected for native editable objects and loss taxonomy.
G6: references remain tied to allowed source revisions and cannot be fabricated.
G7: Arabic/English RTL, fonts, tables and charts retain semantic correctness.
G8: current Gomri editor and export cannot be replaced without measured improvement.

Companion inventory: registry/chatgpt-slides-capability-matrix-2026-11-09.csv.
