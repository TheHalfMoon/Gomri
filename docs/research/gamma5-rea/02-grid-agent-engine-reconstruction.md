# Gamma 5 Deep REA — 02: Grid Editor and Agent Engine

**As-of:** 2026-11-09. This document distinguishes directly documented Gamma 5 behavior (OFFICIAL), actually inspected user-session controls (LIVE-UI), public Gamma repository contents (GITHUB-SOURCE), and independent proposed Gomri implementation (HYPOTHESIS). None of the proposed internal Gamma schemas or orchestration pipelines below is a claim of leaked Gamma code.

## 1. Observed editor architecture: grid plus freeform

Gamma 5 official help explicitly says the default composition is a proportional **grid of rows/columns/cells** on a fixed 16:9 slide. The grid replaces former classic concepts such as smart layouts and classic columns. Cells can be resized and rearranged; backgrounds, borders, padding, image fills, ordering and presets can be changed. The same editor supports independent **freeform boxes** positioned by coordinates, with overlap, resize and rotation. Grid-to-freeform conversion is described as one-way except immediate Undo. Gamma can use fixed content-to-frame behavior or fluid vertical growth.

**Evidence:** https://help.gamma.app/en/articles/17572896-how-do-grids-and-freeform-editing-work-in-gamma

This does **not** establish Gamma's internal storage schema, renderer, use of CSS Grid, ProseMirror, canvas, Yjs or any other library. A fork in its GitHub organization is weak historical architectural evidence, not production-current code evidence.

### Functional data structures any rival must represent

**Proposed Gomri Deck IR:**

    Deck:
      size=(1280,720), layoutPolicy="fixed|fluid", revision, themeRef
      slides:
        - slideId, notes, claimIds, role
          root:
            Grid(rows:[proportional], columns:[proportional], cells:[nodes])
            FreeformLayer(nodes:[Node])
          Node:
            stable elementId, type, styleRef, geometry, dataRef,
            sourceRev, editableKind, zIndex, accessibility

Where Grid is a semantic layout *constraint* and FreeformLayer is an independent z-order plane. This is a candidate Gomri design, **not Gamma's internal schema**.

### Layout invariants

- Width/height and grid fractions are canonical and must remain positive/finite.
- A grid cell's layout is recomputed on sibling resizing; direct freeform geometry remains stable.
- Grid-to-freeform conversion requires an explicit transformation and a reversible transaction.
- Text fitting and fluid-height behavior are distinct policies; no silent truncation.
- Changes propagate to editor, presenter preview, native PPTX geometry and PDF render consistently.
- Imported charts/tables remain typed objects rather than bitmaps where supported.
- RTL text direction is a logical property, not a negative-x transform. Arabic shaping must be tested separately in chart labels, table cells and designer canvas.

### Failure modes to probe

1. Long text in narrow grid cell: shrink to a minimum, clip, reflow or overflow?
2. Drag a freeform chart over two grid cells: is its z-order stable after resize?
3. Convert grid to freeform then undo: are element identity and semantics preserved?
4. Resize one row: are neighboring chart axis labels and table contents still legible?
5. Change fixed to fluid and export to PPTX: how is card height converted to fixed slide height?
6. Switch theme: are manual overrides replaced or retained?
7. Multi-slide import with mixed portrait/square sources: how are intrinsic ratios reconciled?
8. Arabic labels in mixed-script RTL charts: do native exports preserve Unicode order?

None of these probes has been executed against a live authored Gamma deck in this study.

## 2. Gamma 5 conversational generation state machine

**OFFICIAL:** Gamma 5 uses a conversational agent. Users choose **Plan** or **Express**. Plan asks about objectives/audience and presents an outline or plan for review; Express skips that checkpoint. **Research** is a Pro+ option associated with Plan; the agent may still perform lightweight search without it. Effort levels **Lite / Standard / Max** affect response effort, time and credit consumption. In the user's actual Free-workspace Vivaldi dashboard, the prompt composer showed Standard and a switch to Classic.

**Sources:**
- https://help.gamma.app/en/articles/15002203-how-do-i-create-with-agent-in-gamma
- https://help.gamma.app/en/articles/16951195-what-is-the-effort-picker-and-how-do-i-use-it
- Live Vivaldi dashboard screenshot inspected during this research, kept private on PC, not committed.

### Behavioral model to reconstruct (HYPOTHESIS)

    REQUEST_RECEIVED
      -> MODE_PLAN? -> REQUIREMENTS_GATHERING -> OUTLINE_REVIEW -> APPROVED
      -> SOURCE_ACQUISITION? -> SOURCE_NORMALIZATION
      -> NARRATIVE_PLANNING
      -> DESIGN_CANDIDATES
      -> SLIDE_GRAPH_COMPILATION
      -> LAYOUT_VERIFICATION
      -> PERSISTED_DECK -> OPTIONAL_EXPORT

This is one viable implementation for Gomri, not Gamma's disclosed pipeline. We do not know whether Gamma actually uses a fixed stage order, multiple models, image-driven renderer, iterative critic, or specialized planning model.

**Design challenge:** "Plan" is not just a user-visible form. It needs typed fields for audience, goal, style, narrative constraints, source scope and review state. "Express" uses sensible defaults but cannot invent facts. An effort picker should have a predictable resource/cost budget and the same semantic correctness floor.

**Gomri implementation:** reuse existing Source IR and W3 evidence-linked Narrative IR (candidate PR #88), add a durable generation job with stages and checkpoints, and pass a typed intent to Presenton's scene compiler; allow local zero-cost model adapters or deterministic offline fallbacks. Do not insert a paid Gamma API call as a hidden backend dependency.

## 3. Editable objects vs image-slide pipeline

**OFFICIAL:** Gamma 5's typical deck allows direct editing of structured elements. Separately, Gamma's **Image slides** (formerly Studio) can generate a slide as one composed raster image, so individual components are **not independently editable**. It may offer extracted text overlaid as editable text boxes, but changes to the visual often require regeneration and credits.

Source: https://help.gamma.app/en/articles/17238075-what-are-image-slides-and-how-do-i-use-them

**Critical product truth:** native editability and image-slide aesthetics are two distinct output modes. It is invalid to label every Gamma slide editable in the PowerPoint object sense. Gomri should make the mode explicit: "Native editable" versus "Image composition" with an audit showing what is flattened, and should prefer native text/table/chart objects by default.

**To beat Gamma:** combine powerful visual style generation with a deterministic reconstruction/semantic object retention step. SlidePoise is an independent donor candidate, not a Gamma repo and not imported here.

## 4. Editing loop: AI changes, diff, undo and history

**OFFICIAL:** Gamma supports manual editing and a conversational Agent that can target a slide or broader artifact. There are **Original / Modified** comparison controls and restoration. Ctrl/Cmd+Z and Version History permit recovery; history is available even on Free. These are visible user behaviors, not a disclosed storage or transaction implementation.

Sources:
- https://help.gamma.app/en/articles/8033284-how-do-i-edit-my-content-with-ai
- https://help.gamma.app/en/articles/11048579-can-i-undo-a-change-or-restore-a-previous-version-in-gamma

**Separate confirmed API contract:** Gamma's public REST editing operation targets **one page at a time**, cannot add pages via that edit endpoint, and allows at most **one active edit per page**. Do not assume the UI uses that API endpoint or shares those limits.

Source: https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api

### Proposed Gomri typed patch transaction

    AIEditRequest:
      deckId, baseRevision, targetSlideIds, targetElementIds,
      actorId, intent, allowedSources, expectedObjectRevisions,
      preserveOtherElements, idempotencyKey

    ProposedChange:
      typedOps[], beforeState, afterState, scopeDiff,
      confidence, evidenceStatus, layoutChecks, importLossWarnings

    MutationCoordinator:
      authorize -> plan -> stage -> render -> validate
        -> show diff -> accept -> compare current revision
        -> commit once or conflict -> reversible history

Required negative tests:
- Two users edit different objects: no lost updates.
- Agent edits object A and sibling B is identical: B must remain unchanged.
- Agent updates source-dependent number with unsupported data: reject or mark unresolved.
- Agent tries to edit stale/deleted element: explicit conflict.
- Repeated edit job after network timeout: no duplicate mutation.
- Restore old version: exactly which collaboration changes are lost is disclosed.
- Agent uses a comment to request write after access revoked: write-time ACL denies.

**Concrete donor:** TheHalfMoon/Ninerr has a scoped MCP tool catalog, per-document authorization, attributed history transactions and Undo agent change. This is a much stronger code donor for Gomri than guessing Gamma's internal mutation log.

## 5. Design and media: reconstructable behavior vs unknown internals

Gamma can take prompts, upload example slides, import research/data and choose themes; Gamma 5 offers per-gamma Styles in addition to workspace themes. Smart Charts can carry editable data, while older chart implementation is being phased out. There are Media, Templates and Customize top-level surfaces in the actual Free dashboard.

Sources:
- https://help.gamma.app/en/articles/11029150-how-do-i-customize-themes-colors-and-fonts-in-gamma
- https://help.gamma.app/en/articles/11029098-how-can-i-generate-charts-and-diagrams-in-gamma

**Unknown:** exact style token schema, brand intelligence implementation, image-generation prompts/providers, quality-scoring ranker, renderer layout engine, template assignment algorithms. Do not fabricate. Forks of Tiptap, Chakra and tldraw show public interest in those technologies historically, not a map of current private systems.

**Proposed Gomri design engine:** narrative slide objectives -> theme/brand token constraints -> several candidate typed layouts -> screenshot/raster + semantic-object checker -> repair overflow/contrast/RTL -> select. Source content and design instructions must be separately constrained, with media rights tracked. The first visual quality claim must be backed by blinded head-to-head review.

## 6. Release-critical engine boundaries

A competitor-level engine must survive:
- missing fonts, big tables, charts with many labels, RTL, animations;
- downloaded media, malformed SVG/PPTX files, zip decompression limits;
- same-object concurrent edits and disconnect/retry;
- export to editable PPTX without silently flattening;
- source-citation integrity after text generation, subsequent AI edits and export;
- browser-only production without dependence on online paid models by default.

The Product "Grid/Freeform" behavioral model is transferable as a **requirements contract**. The actual Gamma editor/agent implementation remains private and has NOT been copied. The Gamma forked PPTX renderer source copied into the Gomri branch is a **browser viewer/import comparator**, not the editor or image-generation engine.

## 7. Next code grain (Gomri)

Phase GG-01: introduce Grid/Flexible layout schema and deterministic migration layer around existing Template V2; no complete editor rewrite.
Phase GG-02: add the AI selection-aware patch transaction protocol (borrow Ninerr) with Original/Modified diff.
Phase GG-03: integrate render-parity, native PPTX object-fidelity and contrast/RTL QA.
Phase GG-04: add style/brand pattern matching from Skilit and local design candidates.
Phase GG-05: add 50-case matched competitive arena with design-blind reviewers.

**No such runtime code was implemented in this REA.** This document makes an actionable design but is not itself a passing product patch.
