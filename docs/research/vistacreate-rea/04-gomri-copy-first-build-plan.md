# VistaCreate Deep REA — 04. Gomri Fast Copy-First Implementation and Competitive Gap Map

Date: 2026-11-09. This is a production-oriented engineering plan, **NOT executed implementation**. Keep existing Gomri Presenton-derived visual slide editor, Next.js/FastAPI, structured source/claim verification, @presenton/export-core and Electron desktop. Open draft PR #88 has source narrative/animations/RTL/PPTX fidelity but is not assumed merged. No code from VistaCreate's private server is available.

## 1. Compare actual capabilities to current Gomri

| VistaCreate capability | Verified vendor behavior | Gomri existing or pending | Copy/build decision |
|---|---|---|---|
| Many design target formats | 85 total claimed including slides, social and print | predominantly presentations, images, PDF | P0: add responsive design variant schema, not 85 hard-coded editors |
| Resize to multiple formats | Copy & Resize; target-specific manual fixes possible | geometric copy/resize, not fully evaluated semantic reflow | P0: build adaptive layout compiler that remeasures text/chart/asset |
| Cross-platform text typography | public Crello vertical font metric source | HTML/native PPTX font differences known | P0: font fidelity report and side-by-side benchmarks |
| Text and media animation | eight effects; MP4/GIF | Presenton and PR #88 animations (not same) | P1: bounded modern Lottie/animation support and export QA |
| AI Writer scoped text | rewrite, tone, shorten, translate in Pro | typed source-grounded narrative and future patch engine | P0: use Ninerr permissioned edit journal and source facts |
| Background removal | official AI tools | image/media pipeline scaffold | P1: optional rembg with independently licensed local weights |
| Object Grabber | segmentation into separate image layer and image fill | not implemented or verified | P1: SAM masks, RGBA sprites, inpaint background, reversible transaction |
| Brand Kit/Styles | logo, type, palette; 1 Free, unlimited Pro | template theme foundation, Skilit potential | P1: versioned BrandIR, reference-derived and portable |
| Asset search library | premium 170M and B2B stock 335M marketing | no equivalent licensed corpus | Don't copy vendor assets; own free/open library with asset rights |
| Visual effects | seven text effects, many image filters | partial text/asset styles | P1: text effects with native PPTX degradation warnings |
| AI template prompt | October 2026 docs says available | source-to-slide work underway | P1: source-approved prompt -> design template candidate |
| Multi-page docs | 100 pages max | slide deck and doc claims | P2: test large deck; no reason to impose arbitrary 100 |
| Partner API white-label | paid iframe and template substitution | REST/MCP agent foundations | P2: own local REST/MCP adapters |
| Social scheduling/print | integrated marketing workflows | outside Gomri slide thesis | P3: defer, avoid scope creep |
| General export | images, PDF, MP4, GIF; no PPTX in standard list | native editable PPTX path available | KEEP/editability moat; run fidelity benchmarks |

## 2. Candidate sources and what to actually copy

**Always protect source origin, original licenses and component boundaries.**

| Candidate | Provenance | Direct integration priority | Why or why not |
|---|---|---|---|
| Existing Gomri editor + export-core | owner repo Presenton base | KEEP P0 | strongest already-running investment; don't create a second canvas |
| Crello font-metrics-sizing | MIT original Crello 2018 | P0 **read-only math** | real cross-OS text-fidelity mechanism; outdated native dependencies, no tests |
| TheHalfMoon/Ninerr MCP/history | owner code | P0 **bounded copy** | selection, authorization, undo and agent transactions |
| TheHalfMoon/Skilit | owner code | P1 **bounded copy** | patterns, reference/brand design intelligence |
| TheHalfMoon/Gomri PR #88 | owner draft | P0 qualify before depending | narrative integrity, RTL, native PPTX QA, animation |
| daybrush/moveable | MIT independent OSS | P1 compare | group resize/rotate/snap; avoid duplicate editor state |
| konvajs/konva | MIT independent OSS | inspect existing integration | scene graph; no reason to import twice |
| fabricjs/fabric.js | MIT independent OSS | compare only | another full canvas could conflict with Presenton |
| airbnb/lottie-web | MIT independent OSS | P1 preferred | maintained upstream vs old Crello fork |
| crello/react-lottie | MIT Crello fork | ARCHIVE/test only | React16 peer version; don't use as production |
| crello/electron-render-service | MIT metadata msokk fork | **NO-GO runtime** | obsolete Electron, URL SSRF/security |
| VistaPrint/ArteJS | Apache-2.0 VistaPrint 2015 | ARCHIVE only | legacy jQuery/Grunt, not VistaCreate editor |
| facebookresearch/segment-anything | Apache-2.0 model/code | P1 gated | masks for Object Grabber; local model VRAM test |
| danielgatis/rembg | MIT package | P1 gated | **weights can have separate restrictive license** |
| gitbrent/PptxGenJS | MIT independent OSS | already considered P0 | source-level native OOXML export comparison |
| Depositphotos Stock SDK | MIT PHP | no | remote paid stock, not zero-cost |
| VistaCreate private engine/templates | no accessible code | unavailable | do not claim copy or assume rights |

## 3. Build waves for maximum speed

### VC-G1 — Responsive slide variants and safe font diagnostics (P0)

1. Define a single canonical Gomri DesignIR / DeckIR: slide nodes have stable IDs, semantic roles (title, chart, quote, logo, caption), crop priority, aspect constraints and source claims.
2. Add FormatProfile for 16:9, 4:3, 1:1, 9:16, PDF A4 and custom pixels, each with safe margins and breakpoint rules.
3. Derived variants are *references* to one source layout and contain only validated overrides; no duplicated claims or missing chart series.
4. Implement constraint reflow: font measurement, safe grid layout, image crop focus, collision checks, chart/table min legibility, RTL right/left anchors.
5. Compare against naive centered/scaled output, prove fewer manual repairs.
6. Use Crello font source as a metric-analysis reference; no font binary mutation, no old fonttools native dependency in production.
7. Record exact output diff and allow user to restore original format unchanged.

**Required evidence:** at least 30 diverse synthetic page fixtures and 5 formats each, with 0 missing semantic elements or silent numerical changes; visual geometry and RTL checks.

### VC-G2 — Source-grounded AI text edits (P0)

- In existing editor, select text/element and ask AI for rewrite/shorten/tone/translate.
- Model returns typed patch, not arbitrary HTML or full deck replacement.
- Keep approved figures/dates/units/citations under a preserve-facts mode.
- Verify actor/deck/source ACL at read and write times, stale revision conflict, and explicit Undo agent change.
- Render before commit; respect text width, min font, contrast, no unselected sibling changes.
- Reuse Ninerr protocol/history and Gomri source/Narrative IR once draft PR #88 is qualified.

### VC-G3 — Image operations (P1)

- Use optional local background removal with explicit model licenses and memory budgets.
- For Object Grabber, selection mask -> RGBA crop -> background inpainting -> two distinct non-destructive layers; preserve original pixels.
- Store vector/semantic editability truth: extracted object remains a raster sprite unless separately vectorized.
- Undo/redo must reverse every layer and asset addition.
- No API calls/private source uploads by default.

### VC-G4 — Motion/design and export (P1)

- Use modern lottie-web (or verified existing animation path), not Crello's obsolete wrapper.
- Eight common visual effects implemented as typed transitions with per-element timing.
- Render consistent MP4/GIF frames locally and choose deterministic static frame for PDF/PNG; explicit loss/downgrade in native PPTX.
- Add text effects: outline, shadow, background box, echo, glitch, reflection, curved; check format support.
- Native PowerPoint remains first-class editable output, not one large screenshot.

### VC-G5 — Brand, templates and API (P2)

- BrandIR tokens for fonts/rights, logo, palette, default visual styles, citation/footer placement and export metadata.
- Create own licensed template variants and per-format rendering, not 200K vendor stock templates.
- Local MCP/API for template variable substitution, multi-target rendering, export status and quality receipts.
- Defer print provider, scheduling and paid B2B API unless Gomri itself needs them later.

## 4. Avoid false "more code is better" metrics

The cloned 217 public files are historic/adjacent sources. Do not score progress by copied file count. A source file is useful only if it:
- solves a measurable component of flagship product;
- is legally and technically admissible with notices/assets;
- passes automated tests and synthetic visual render checks;
- has a rollback path and does not duplicate existing source authority;
- maintains no-cloud/zero-cost default;
- survives Windows/macOS/Linux and RTL where promised.

Do not install a 2017 renderer or 2015 WYSIWYG as an expedient shortcut.

## 5. Explicitly separate "Gomri" vs "Ninerr" scope

Ninerr is a broader design intelligence/editor project in the owner's GitHub; Gomri is a deck/presentation/story product. Copy a bounded source component from Ninerr to Gomri where useful. Do not turn Gomri into an all-purpose Photoshop/Canva clone until the core editable slide product is ready.

A 9:16 social variant of a source-backed presentation is in scope; a full social scheduling platform or print marketplace is not.

## 6. Quality gates and proposed targets (NOT measured)

Hard:
- 0 unauthorized AI/source writes in adversarial fixtures.
- 0 lost or silently changed native chart numeric values, units or source claims.
- 0 lost elements during responsive-format conversion without explicit downgrade.
- 0 credentials/private API calls by copied renderers in offline tests.
- all imported third-party licenses/assets reviewed.

Proposed performance and preference targets:
- 95%+ native editable objects retained for supported PPTX element classes in benchmark.
- 98%+ of format variants free of unintended text clipping/overlap.
- majority blind designer preference on matched deck/format tasks vs old baseline, with reviewers blinded.
- all 30 source decks × 5 formats reproducible under local screenshot QA; compare on original Windows PC and at least one other OS before cross-platform claims.
- exact-HEAD CI and independent review before any merge or release.

These are **Gomri goals**, not measured VistaCreate or Gomri results. Black-box plan details are in 05-blackbox-50-and-adoption.md.

## 7. Implementation order to enter engineering immediately

VC-G1 is first. It can use existing Scene/Template V2 and fast deterministic algorithms, with immediate visible value. Next VC-G2 typed selection AI and no-loss patch history. Image segmentation and scheduling follow only after flagship slide UX and exports are reliable.

Do not merge any source archive into main on its own; a feature PR should include only bounded code under active paths, matching original author/notice and test evidence.
