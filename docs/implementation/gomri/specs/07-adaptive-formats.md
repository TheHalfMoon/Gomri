# S07 — Adaptive Design Formats and Optional Media (Post-MVP)

**Goal:** Extend a proven source-grounded deck engine into 4:3, 1:1 and 9:16 **without duplicating canonical source facts or silently flattening editable objects**. **Owners:** R3 Layout, R5 Export, R10 Design Judge. **Depends:** fully qualified S06; **not required for initial MVP**.

## Why this phase is deferred

VistaCreate's published Copy & Resize documentation acknowledges manual layout repair is sometimes needed. Gomri can exceed simple center-and-scale by using semantic roles from S01/S02, but this should not delay source-to-editable-PPTX. It is explicitly unsafe to promise 85 marketing design formats, video workflows or a stock catalog before a single native slide works.

## Copy-first boundaries

Keep existing Template V2/Konva geometry, role layouts and native exporter; do not transplant a full alternative editor. Crello font metrics arithmetic is read-only reference, modern Lottie adapter only after dependency/assets review, the PR #88 NextSlide OSS animation skill only as bounded source (it is **not** the proprietary NextSlide.ai engine), and Skilit brand tokens behind Gomri-owned adapters. Any Object Grabber model/code needs separate weight/asset rights, RAM/VRAM and privacy gate, so it is an independent later decision.

## Future requirements

- One canonical source deck, stable source/slide/component IDs, derived variants with versioned override pointers.
- Format profiles 16:9, 4:3, 1:1, 9:16 with semantic title/chart/table/image zones, focal crop and logical RTL anchors.
- Per-variant status: regenerated, user override, requires review, or unsupported; no forced rewriting of manually positioned slides.
- Typed animation timeline and frame-specific export: deterministic static PDF/PPTX frame, honest GIF/MP4/HTML semantics when later supported.
- No unsupported stock/font/media redistribution, and no cloud model required for simple layout reflow.
- Native data and source citations preserved across all variants, with downgrade receipt for each exception.

## Acceptance

Start with eight synthetic decks × four formats, then expand to 30 only if the first wave passes. Verify no unlabelled loss of chart series values, citations, text order or notes; check clipping, Arabic line breaks, min font size and crop. Browser screenshot comparisons are coupled with canonical data and native PPTX object inspections. Blind reviewer compares against current Gomri baseline, not unverified competitor screenshots.

**Hard stop:** source edits modifying only one aspect variant overwrite canonical content or other variants; user overrides silently erased; altered numerical values; model weight licenses unknown; excessive binary dependencies on Windows. **Out of scope:** social scheduling, white-label paid API, print on demand, massive asset library, full live collaboration.

**Delivery:** separate draft PR after S06 with exact-head tests and independent review. No automatic release.
