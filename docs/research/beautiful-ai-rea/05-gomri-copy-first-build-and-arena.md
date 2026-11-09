# Beautiful.ai Deep REA — 05: Gomri Copy-First Integration, Priority Order and 50-Probe Arena

**As-of:** 2026-11-09. **Status:** research and source preservation; no source package is wired into the Gomri production runtime. All targets below are proposed acceptance criteria, NOT measured scores or results. Do not conflate this branch with open Draft PR #88 or its pending CI qualification.

## 1. Baseline: do not throw away a functioning editor

What is known about TheHalfMoon/Gomri:
- Presenton-derived Next.js slide editor with actual templates, text/image/chart/table components, layout/HTML preview and native PPTX/PDF export through an existing export runtime.
- FastAPI source accounting, parser/worker contracts, lexical retrieval, citations, evidence/claim verification and durable job foundations on main.
- Open draft [PR #88](https://github.com/TheHalfMoon/Gomri/pull/88) integrates source-linked Narrative IR and presentation generation, 24 animations, font/color contrast lint, Arabic/RTL flows and PPTX export/reimport fidelity; local Windows checks were reported successful but full FastAPI + exact-head CI remain outstanding. This branch does NOT depend on unmerged source as if it shipped.
- TheHalfMoon/Ninerr has actual selection-aware MCP, permission gating, history/undo transactions and a design canvas. TheHalfMoon/Skilit has reference/style/brand-oriented research and design-system patterns. Reuse narrowly.

The goal is not to create a separate Beautiful.ai clone next to Presenton. It is to introduce one **native, source-grounded, responsive SmartLayout layer** into the existing editor with superior authoring invariants.

## 2. Engine proposed for Gomri

    User and agent instructions + source files
        -> Intent and verified Narrative IR
        -> SmartSlide candidate chooser (role, content count, evidence, template)
        -> Shared typed Deck IR and source links
           -> SmartLayout grid/constraint adapter
           -> Classic freeform/Canvas adapter
        -> Deterministic geometry/text/chart/RTL fit solver
        -> Render preview + structured/pixel QA
        -> Typed revisioned human/AI patch transaction
        -> PPTX native export / PDF / image / presentation mode
        -> Per-slide fidelity and evidence audit

This is a **Gomri engineering proposal**, not the private Beautiful.ai engine diagram. The published skill says a model is rendered by an element class and uses 12x12 grids, computed text caches, fit constraints and migrations. It does not reveal full code, algorithms, or model weights.

## 3. Six implementation waves

### BAI-00 — source admission (P0, no new runtime dependency)

- Preserve exact MIT/Apache source attribution and pins for the four imported repos.
- Treat Claude/Grok skills as **vendor documentation and possible template-design donors**, not as production imperative instructions and not as a need for paid Beautiful.ai accounts.
- Inspect only known-good source packages: PptxGenJS derivative, rich model docs, React state utility. Avoid unlicensed source.
- Compare older public REST API with new MCP v2 and retain both statuses in a versioned capability ledger.
- Run source package typecheck/build/tests when needed; record exact SHA + dependency safety, offline behavior, asset rights.

### BAI-01 — SmartLayout compiler with actual constraints (P0)

Implement a Gomri-owned typed layer with elements:
- RichText, Image, Icon, Shape, Line, Group, Table, Chart, Timeline, SmartDiagram, Media, Notes, GridCell and FreeformGroup.
- Reusable TemplateRole and BrandKit, with target layout constraints (grid, fixed, preserve-aspect, editable).
- FitResult: isFit, clipping, overlap, minFontSizeReached, invalidCellGeometry, missingAsset, dataMismatch, readingOrder, notes, sourceLinks.
- No hidden mutation: preserve chart source data and claim locators through template switches.
- No silently dropped items: reject invalid cells or offer a visible proposed reflow.
- RTL and font fallback as hard tests, not late QA.

**First 12 template families:** headline/title, textlist, rich image+text, dashboard/chart, table, comparison, flowchart/process, timeline/Gantt, org/team, quote/testimonial, photo gallery, summary/closing. Map the 73 public template IDs to these families rather than writing 73 separate engines.

**Acceptance:** 30 synthetic slide fixtures, render/preview/PPTX native object type accounting; zero lost cell items, numbers, chart series and source citations under supported types.

### BAI-02 — AI authoring and slide-wise verification (P0)

- Start with verified Narrative IR and an approved outline.
- Create one durable deck once and visible placeholders; never spawn duplicates on retry.
- Choose diverse templates across the deck using semantic content, Brand Kit, readability and source evidence.
- Build each slide as typed Deck IR; render before save; only commit after fit/data/ACL checks.
- Cap visual repair attempts and report failures; always preserve previously valid slide and show partial progress.
- Retain exact source values under Preserve Text mode and selectively regenerate only visual/media nodes.
- Per-element AI patches and history/Undo via bounded Ninerr code, not direct overwrites of entire JSON blobs.
- Treat a UI lock/spinner as **non-authoritative**: enforce revisions and permissions at the backend commit.

**Acceptance:** one targeted edit cannot change unselected sibling slides/objects; duplicate request -> exactly one effect; overlapping writes -> conflict; undo correct.

### BAI-03 — Brand Kit and reference quality (P1)

- Reuse Skilit brand token and reference pattern work where it is actually implemented/qualified.
- Import reference PPTX fonts/colors/layout as proposed tokens, but preserve source style and disclose misses.
- Apply Brand Kit voice, language, logo, images, footer and style to every generated slide via deterministic theme resolver.
- Version Brand Kits and make shared-library detachment explicit.
- Compare 2–4 well-designed editable candidates per slide and use screenshot QA + blinded human review, not AI self-praise.

**Acceptance:** a brand-provided 10-slide fixture has no missing logo, wrong brand color or unwanted font substitution; blind reviewers prefer the new path more often than old baseline on a frozen set.

### BAI-04 — native PowerPoint fidelity and interactivity (P0/P1)

- Compare **Beautiful.ai/PptxGenJS 3.13.0-bai.5** with upstream gitbrent and Presenton export-core on the exact same 30 authored Deck IR fixtures.
- Inspect OOXML for native chart data, table cells, paragraph/bullet formatting, shapes, speaker notes, slides and masters.
- Pin source/licensing/dep fixes and avoid regressions; copy only the validated improvements.
- Separate native editable elements from browser-only live ROI/map/webview widgets and fallback images; report each lossy export.
- Continue Arabic/English typography tests, including diacritics, list bullets, table cells, chart axes and mixed-script runs.
- Test bad PPTX ZIP, external images, font resources and missing theme against hard import security limits.

**Acceptance:** every requested export contains all supported semantic objects and numbers, with explicit typed loss reasons for unsupported objects; measured screenshot fidelity.

### BAI-05 — collaboration, MCP, security and quality moat (P1/P2)

- One canonical Deck IR, source ACLs, authenticated workspace-scoped actions.
- API/MCP/desktop agent share the **same typed command semantics** for create/read/patch/render/export.
- Comment-to-agent tasks are bounded by permissions and source access, with durable receipts.
- Version history, copy-on-write shared slides, viewer restrictions, data retention and revocation checks.
- Zero-cost-first mode using local deterministic generation/provider adapters; no automatic paid Beautiful.ai/Anthropic API calls.
- User privacy: no upload of private source decks to unknown vendors during QA or source extraction.

## 4. Fifty live black-box probes, NOT RUN

**Prerequisites:** authorized account with access to the relevant features, synthetic content, no purchased plan or credits without explicit user request; record exact surface/plan/date and screenshots/artifacts. We did not exercise a logged-in Beautiful.ai editor here.

| ID | Test stimulus | Expected evidence |
|---|---|---|
| A01 | Prompt only -> outline | low-fidelity editable outline |
| A02 | Complete 10-slide outline -> direct generation | no unrequested rewrites |
| A03 | Insert/remove/reorder outline slides | order and content persistence |
| A04 | Voice prompt | correct content or explicit feature unavailability |
| A05 | Attach synthetic PDF and restrict facts | no numbers invented |
| B01 | Smart text list + 12 items | readable fit or clear overflow |
| B02 | Dashboard grid add/remove cells | no content lost |
| B03 | Freeform slide out-of-frame object | warning/clipping behavior |
| B04 | Switch Smart template preserving exact data | text/table/chart parity |
| B05 | Multi-column graph with too-long labels | render quality and axis integrity |
| C01 | Slide AI current slide rewrite | target only |
| C02 | Preserve Exact Text on | text byte/semantic identical |
| C03 | Regenerate Image toggle | text unaffected |
| C04 | Use Presentation Context toggle | story consistency |
| C05 | Slide-specific web search/source | citations and numeric accuracy |
| D01 | Brand Kit color change | consistent colors across deck |
| D02 | Brand Kit imported from reference PPT | font/logo/spacing agreement |
| D03 | Brand voice applied to AI text | acceptable human edit |
| D04 | Team assets as image source | authorized assets only |
| D05 | Shared slide template edited | copy-on-write and link behavior |
| E01 | Smart pie chart data update | native series preserved |
| E02 | ROI calculator slider during playback | values recalculate |
| E03 | Map zoom/markers during playback | interactive behavior |
| E04 | Gantt timeline dates/labels | correct schedule and positions |
| E05 | Flowchart add decision node | connectors and layout remain valid |
| F01 | PPTX slide import preserves font | compare source/raster/editable object |
| F02 | PPTX slides imported into Smart mode? | verify Classic limitation |
| F03 | Editable PPTX export with table | native table cells |
| F04 | PPTX export with speaker notes | notes retained |
| F05 | Google Slides export with animation | explicit degradation |
| G01 | 2 people change different slides | no lost edits |
| G02 | 2 people change same element | conflict/merge behavior |
| G03 | Member edits shared slide | attribution/version |
| G04 | Viewer tries forbidden export | permission denied |
| G05 | Revoke access during agent work | commit denied or policy behavior |
| H01 | New MCP v2 get/render/edit slide | tool available with authorized account |
| H02 | Older MCP creation/export tool | distinguish connector version |
| H03 | REST structured outline with imageSource | validate contract/plan |
| H04 | MCP template variable interpolation | template replacement correctness |
| H05 | Unauthorized MCP tool request | no privilege escalation |
| I01 | Arabic/English direction + numerals | correct glyph and logical order |
| I02 | Arabic table with Latin values | table RTL and export fidelity |
| I03 | Repeated template types in long deck | design monotony / layout candidates |
| I04 | Image carousel multiple items | animation/preview/export |
| I05 | Long-form slide with constraints | no silent text loss |
| J01 | Missing image source asset | repair/fail, no spinner indefinitely |
| J02 | Stale migration version on valid slide | preservation and explicit conversion |
| J03 | Duplicate deferred agent write | one effect |
| J04 | Inject instruction in source PDF | source treated as untrusted data |
| J05 | Malicious PPTX relationship/ZIP bomb | import safe refusal |

There are **10 groups x 5 = 50 planned tests**, not 50 executed results. A source description and successful API schema compilation are not substitutes for these live tests.

## 5. Measurable competition rubric

Scoring recommendation (not yet validated):
- visual design/readability and style consistency: 25%;
- semantic native editability and PowerPoint fidelity: 20%;
- plan/outline and audience-specific storytelling: 15%;
- source integrity and factual/numeric correctness: 15%;
- targeted AI revision correctness, conflicts and undo: 15%;
- Arabic/RTL, accessibility, privacy and permissions: 10%.

High-priority **hard gates** independent of weighted score:
- 0 unauthorized writes or source leaks;
- 0 unsupported chart values silently invented or lost;
- 0 accidentally dropped Grid items/notes without a reason;
- 100% scoped patches do not modify unrelated objects in frozen fixtures;
- 100% render failure surfaced and not silently saved;
- browser-only widget exports have explicit loss inventory.

Provisional non-hard quantitative aims (not measurements): ≥95% native retention of supported PPTX object types; ≥98% benchmark slides without clipping/overlaps; ≥60% blinded designer preference wins on 50 matching prompts. Report confidence intervals, disagreements and separate per-family breakdown.

## 6. Priority decision for Gomri to ship sooner

**Do first:** only four engine slices:
1. Smart grid/constraint layout that takes current Presenton elements.
2. Targeted AI editing with render-before-save, revisioned patches and undo.
3. A set of 12 excellent template families based on the public 73-type taxonomy.
4. Native PPTX fidelity and source/RTL QA.

**Do not first:** building every Beautiful.ai Smart Slide, importing every source repo, a full new desktop app, complex collaboration backend, ROI/map animation system or arbitrary unverified AI provider contracts. These can follow after flagship deck quality passes.

The cloned source is a reference and donor candidate, not an instant product replacement. Keep PR #88 separate and qualify/merge it under existing gates before basing product work on it.

## 7. Final source-status contract

YES — four source packages and 388 files have been committed to a protected research branch with pinned SHA and rights metadata.

YES — current vendor Apache skill source exposes detailed slide JSON model, actual template family names, render/repair/save protocol, and a 12x12 grid contract.

NO — the private Beautiful.ai server, the internal SmartLayout implementation, hidden design model algorithms, production training data, and all private template assets were **not** obtained.

NO — these copied files do not yet make Gomri behave like Beautiful.ai; no runtime adapter was built in this research branch.

GO for source-backed implementation experiments. NO-GO for claims of parity/superiority or a public release until tests pass.
