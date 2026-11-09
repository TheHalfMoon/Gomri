# Beautiful.ai Deep REA — 01: Current Product and Smart Slides Behavioral Contract

**As of 2026-11-09.** The goal is to design an independent Gomri engine that reproduces or improves Beautiful.ai's user-visible workflow, not to pretend the proprietary renderer is available. Evidence levels: **OFFICIAL_DOC** vendor help/changelog; **FIRST_PARTY_PUBLIC_SOURCE** vendor-authored Apache/MIT package/skill; **UNKNOWN** no verified implementation; **NOT_RUN** no live user-authorized editor test.

## 1. What Beautiful.ai truly competes on

Unlike a simple prompt-to-PPTX generator, the core product is a **self-designing slide system**. Beautiful.ai calls these **Smart Slides**: a template-specific component/layout engine realigns, resizes, styles and animates structured content as it changes. The user manipulates the content and the slide template while the layout tries to keep readable and on-brand. This is a stronger UX problem than just producing a static screenshot.

Official: https://www.beautiful.ai/ ; https://www.beautiful.ai/slide-templates

Main competitive lesson for Gomri: **Smart Layout is an invariant of every edit, not a one-time design prompt**. A perfect first draft is insufficient if the title subsequently overflows or the chart changes values.

## 2. 2026-09-29 product evolution: template -> AI presentation

Beautiful.ai now supports a beta which takes a chosen designer-authored presentation template and uses AI to adapt it to the user's subject. This means template *identity and structure* can survive content substitution rather than being treated as a generic style prompt.

Official changelog: https://www.beautiful.ai/product-updates (2026-09-29).

### 2026-09-28 outline and input workflow

- Starting with only a topic: ask targeted clarifying questions.
- Starting with a complete outline: generate immediately or refine first.
- Provide a text-only low-fidelity outline, edit/reorder/remove/insert slides before design.
- Choose Brand Kit, image source/style and language earlier in generation.
- Produce fully designed slides from approved outline.

This distinguishes **Narrative IR** from slide visuals. Copy-first Gomri should preserve each slide's approved message and evidence before layout selection, not ask the model to invent both together.

Official: https://support.beautiful.ai/hc/en-us/articles/12885226948109-Creating-a-presentation-with-AI

## 3. Slide AI: targeted regeneration, not necessarily arbitrary patch

Beautiful.ai's Slide AI supports: use the current slide as a starting point; change its content, structure, design or imagery; propose multiple Smart Slide alternative layouts; switch to a selected template; choose slide type and language; use full deck context; attach source; enable web search; toggle **Preserve Exact Text**; optionally regenerate image **without rewriting the text**.

This is **slide-scoped** AI with explicit content preservation controls. It does **not** prove arbitrary isolated editing of any internal ProseMirror text run, or perfect guarantee that all native object IDs survive every layout conversion.

Source: https://support.beautiful.ai/hc/en-us/articles/43350069148557-Create-and-Edit-your-Slides-with-Slide-AI

Gomri test: two consecutive slide rewrites with Preserve Exact Text on must produce semantically identical input text, numbers, units, citations and source references, while allowing layout changes; report any unsupported movement of chart data.

## 4. Smart Slide taxonomy

The official public template catalog groups layouts into **eight use-case collections**: Impact; Structural; Data & Charts; Comparison; Diagrams & Timeline; Essential; Product & Customer; People. Some templates are not static: chart/dashboard, sequence/flow chart, org chart, Gantt/timeline, image carousel, ROI calculator and map.

- Interactive **ROI**: variables and formulas with sliders that recalculate metrics during presentation playback. This is *application interactivity*, not static picture export.
- Interactive **map**: region zoom, animated geographic view, labels/markers, pan/zoom in playback.
- Data slides: charts and editable series; import/paste files and choose ranges.
- Diagrams: auto-layout of steps, connectors, labels and shapes.
- Embedded video/web views, countdowns, animation, image carousels.
- Smart templates can switch layout but source structure and numbers must remain stable.

Sources:
https://www.beautiful.ai/slide-templates
https://www.beautiful.ai/product-updates (2026-04-25; 2026-08-21).

In Gomri, distinguish:
(1) **native PPTX-editable** objects (text, charts, tables, shapes);
(2) **live app-only interactive** objects (ROI slider, pan/zoom maps, webview);
(3) **raster/fallback** objects.
Every export must disclose which capability was flattened or lost.

## 5. Editor and interaction design

October 2025 and 2026 changelogs describe:
- slide navigation on the left, thumbnails and reorder;
- inline contextual controls plus a right-hand Properties Panel;
- six properties categories: Edit, Add, Ideas, Style, Playback, Options;
- slide-wise switching between Smart template types and Classic freeform;
- layered object organization in Classic;
- guides/alignment/distribution, multiselection, style controls;
- chart series and cell editing, icon/image frames, captions;
- find/replace across deck;
- presenter notes and feedback.

Source: https://www.beautiful.ai/product-updates (2025-01-07 and 2025-10-07).

These are visible workflows; no first-party internal rendering/DOM algorithms were disclosed through those announcements.

## 6. Brand Kits: generation constraints are now part of the brand

September 2026 renamed Themes to **Brand Kits**. They include colors, type, decoration, footers, default slides, load screen, image sourcing/style, writing voice, language and reusable instructions. Teams can choose a Shared Brand Kit and share assets. There is a live preview and an import-from-PPT extraction workflow; source help warns the PPT extraction may miss some original brand details.

Gomri should model:
- versioned BrandKit (colors, fonts, logo, spacing, shape/callout palettes, background modes, default slide roles);
- content constraints (language, brand voice, do-not-claim and evidence policy);
- asset rights and source selection per workspace;
- style preview without mutating the canonical deck;
- carefully delimited template inheritance vs user overrides.

Sources:
https://support.beautiful.ai/hc/en-us/articles/48232447962637-Creating-Your-New-Brand-Kit
https://www.beautiful.ai/product-updates (2026-09-11).

## 7. Import/export product truth (critical competitive opening)

Current help documents:
- PPTX slide import with slide picking and source font recognition; imported PPT-based **Classic Slides** do not automatically become Smart Slides. Thus "we import PowerPoint" does not imply preserving automatic Smart constraints.
- Editable PPTX full deck/individual slide is a Pro/Team/Enterprise paid export feature; PowerPoint Image export is raster slides. Native editability should be tested by inspecting actual OOXML.
- Google Slides export is offered on paid plans; audio, animations, embedded videos and transitions may be lost.
- PDF/compressed PDF, print and an offline player exist.
- Export may show font/layout differences on systems without source fonts.

Sources:
https://support.beautiful.ai/hc/en-us/articles/360059654532-How-can-I-import-my-PowerPoint
https://support.beautiful.ai/hc/en-us/articles/48233231049741-Creating-a-Team-Template-from-Scratch
https://support.beautiful.ai/hc/en-us/articles/30629528652685-Exporting-your-slides-and-presentations
https://support.beautiful.ai/hc/en-us/articles/360035562031-How-do-I-export-as-an-editable-PowerPoint

Gomri's opportunity: preserve more imported PPT object semantics and add Smart layout constraints **without destroying imported text, chart values, speaker notes or Arabic RTL**.

## 8. Collaboration, sharing and analytics

Beautiful.ai supports shared templates/slides, user groups, shared/private folders, assignments, export restrictions, comments/threaded replies, sharing links, viewer analytics and slide version history (depending on tier). Some slides may be references to shared library content and require explicit copy-on-edit semantics.

Source: https://www.beautiful.ai/product-updates ; https://support.beautiful.ai/hc/en-us/articles/360004996892-Version-History

Gomri must NOT assume current app has all of these on Free. Separate web page claims, plan tiers, actual role permissions and API/MCP availability.

## 9. Official API and MCP boundaries

OpenAPI publication has **10 operations**, principally generation, search/list/get, template creation, and export; the public OAuth MCP FAQ describes similar operations and expressly says the old connector doesn't support arbitrary editing of existing slides.

However, as of 2026-11-06 the officially published **Beautiful.ai Claude and Grok plugins** describe a different, newer agent toolset including get_slide, create_slide, update_slide, render_slide and lock_slides. These may belong to a distinct/new version. This is not proof every user in every tier can access the newer operations. See chapters 03 and 04.

Sources:
https://github.com/beautifulai/beautifulai-docs/blob/main/openapi.yaml
https://support.beautiful.ai/hc/en-us/articles/44246954338829-Beautiful-ai-MCP-Quick-Setup-FAQ
https://github.com/beautifulai/claude-plugin

## 10. What this study did not do

- No authenticated Beautiful.ai editor session was opened or exercised.
- No presentation was generated or user credits spent.
- No live API or MCP call to a Beautiful.ai account.
- No proprietary server code, design templates, customer assets, model prompts or internal database acquired.
- No measured output fidelity/visual score was established; all comparative benchmark numbers remain unknown.

The following chapters use public Apache/MIT vendor-authored source snapshots plus separate unlicensed **reference-only** API docs. Their exact SHA and license are maintained in third_party/beautiful-ai-public/SOURCE_REGISTER.md.
