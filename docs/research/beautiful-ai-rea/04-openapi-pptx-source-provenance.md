# Beautiful.ai Deep REA — 04: Actual Public Code, OpenAPI, PptxGenJS Fork and Licensing

**Date:** 2026-11-09. **Source distinction is mandatory:** public app organization repository vs product runtime, original author vs derivative, source snippets vs API contracts, Apache/MIT source vs unlicensed public code. The research branch physically contains 388 vendor-org public files from four licensed repos, but **none are running production Gomri features**.

## 1. Six public GitHub repositories (actual inspected list)

| Repo | GitHub fork bit | Real origin / rights | Content | Copy outcome |
|---|---|---|---|---|
| beautifulai/claude-plugin | false | original Beautiful.ai Apache-2.0 | 113 files: slide docs, elements, templates and agent instructions | copied source snapshot |
| beautifulai/grok-plugin | false | original Beautiful.ai Apache-2.0 | 116 files: Grok-oriented similar agent instructions/docs | copied source snapshot |
| beautifulai/PptxGenJS | false | **derivative of gitbrent/PptxGenJS by Brent Ely**, MIT | 140 files: modified PowerPoint generator package | copied source snapshot |
| beautifulai/react-global-state | false | original Beautiful.ai MIT | 19 files: historical React state helper v0.7.0 | copied source snapshot |
| beautifulai/beautifulai-docs | false | **no clear public license** in repo metadata | hosted OpenAPI docs and Swagger UI | read only |
| beautifulai/qa-eng-interview | false | no clear public license | small Cypress hiring exercise | read only |

Public organization metadata and repo docs accessed 2026-11-09. A false GitHub "fork" bit does **not** mean no upstream lineage: PptxGenJS README/author/license attribute upstream to Brent Ely.

Companion: ../../registry/beautiful-ai-public-source-inventory-2026-11-09.csv

## 2. Beautiful.ai OpenAPI: 10 actual published operations

The first-party public OpenAPI 3.0.3 document at https://github.com/beautifulai/beautifulai-docs/blob/main/openapi.yaml defines 10 operations, mostly under /api/v1:

| Method/path | Operation ID | Semantics |
|---|---|---|
| POST /generatePresentation | generatePresentation | create from natural-language prompt |
| GET /getThemes | getThemes | list built-in and user/team themes |
| GET /getFolders | getFolders | list visible folders |
| POST /listPresentations | listPresentations | list/search accessible decks |
| POST /listPresentationTemplates | listPresentationTemplates | list accessible templates |
| POST /getPresentation | getPresentation | read metadata / deck |
| POST /getPresentationTemplateVariables | getPresentationTemplateVariables | list template variable bindings |
| POST /createPresentation | createPresentation | create from an explicitly structured outline |
| POST /createPresentationFromTemplate | createPresentationFromTemplate | bind variables into a copied template |
| POST /exportPresentation | exportPresentation | request deck export |

The spec accepts either the X-Api-Key style credential or bearer API key and uses workspace permission context. This is a published contract, not proof each endpoint is available to every plan, nor an SDK implementation.

The structured outline schema is especially valuable: the request includes title, workspace/theme/folder identity, optional imageSource (ai/web/stock/none), imageStyle, language, preserveExactText and a list of slides, each with title, summary and one of **32 enumerated slide-content types** (e.g. chart, timeline-diagram, bullet-list, Gantt, SWOT, hub-and-spoke). This provides a typed **NarrativeIR -> layout-role** bridge that Gomri can generalize.

An exact operation-and-type inventory is stored at ../../registry/beautiful-ai-openapi-contract-2026-11-09.csv.

### Source version conflict

The public OpenAPI does **not** include update_slide or render_slide. However the **new Apache2 Claude/Grok plugins published Nov 6, 2026** reference these tools on a distinct MCP endpoint. That is a **newer separate capability surface**, not necessarily an OpenAPI upgrade. Do not assert that these 10 endpoints reveal the full private tool server.

## 3. The modified PptxGenJS source is actual runnable code

Copied beautifulai/PptxGenJS at commit 1f3c948832268024833094de86687f506d59ae77. Package metadata explicitly says version **3.13.0-bai.5**, MIT, author Brent Ely. It is an independently hosted Beautiful.ai-maintained derivative, **not** Beautiful.ai's original exporter implementation by itself.

Notable 2026 source changes visible in public commits and pull requests:
- bullet formatting improvements and refactoring (PR #4; June 2026);
- removal of an unused image-size dependency with documented DoS advisory context, rebuilding shipped artifacts (PR #5; Nov 4 2026);
- internal build scripts and lint fixes.

The README advertises native OOXML PowerPoint support for text, shapes, charts, tables, masters, SVG, RTL languages, presentation notes, etc. These are upstream capabilities; our research did not benchmark this fork against current Gomri or current upstream releases.

Potential value to Gomri:
- improve native bullet/list nesting and editability after export;
- compare exported OOXML chart XML, table cell/native geometry, speaker notes and Arabic fonts;
- eliminate vulnerable/unused dependencies in any experimental adapter;
- use known MIT source with original notices and reproducible SHA.

**Do not replace existing @presenton/export-core solely because Beautiful.ai maintains a fork.** A frozen set of 30+ real decks must establish a win on native object editability/round-trip and no regression. PptxGenJS is an **export producer**, not a slide layout engine, not the AI model, and not Beautiful.ai's private Smart Slides renderer.

Sources:
https://github.com/beautifulai/PptxGenJS
https://github.com/beautifulai/PptxGenJS/pull/4
https://github.com/beautifulai/PptxGenJS/pull/5
https://github.com/gitbrent/PptxGenJS

## 4. Public Claude and Grok plugins are substantial model-interface disclosures

Unlike a standard thin SDK, the official skills include 103 **per-element Markdown model specifications** and a 73-ID template map, plus full workflow instructions for presentation construction, editing, rendering, image assets and visual critique. These are Apache-2.0 source documents and are now preserved in the research branch.

However:
- Markdown skills are not the underlying implementation of BaseElement, GridLayoutContainer, SceneGraph, text shaper or animated chart renderer.
- Private MCP server executes create/update/render; its source is not part of public plugin.
- The plugin does not expose training weights, private prompts, hidden benchmark dataset or full backend code.
- Access to official remote MCP server requires explicit user authentication and its plan/permission gates.

The Beautiful.ai MCP tool URL and OAuth surface are publicly documented in the repo; this research **did not invoke** them. A vendor URL is not a free local inference backend.

## 5. Other first-party code and what it does not establish

react-global-state v0.7.0 is a small MIT state-management package for React 16.3+, authored by Beautiful.ai. Its existence shows a historical utility, not whether the current production editor uses this package, Redux, Yjs, Zustand or custom server state. Current Gomri should not duplicate state authority merely to absorb a logo-labelled source.

The public 2025 qa-eng-interview is a Cypress exercise with a README note that one slide-generation example used Anthropic. It **does not establish all of Beautiful.ai's March 2026 / November 2026 AI generation providers**, algorithms or prompt chain. No source license was found in org metadata; it was intentionally not copied.

## 6. Rights, security and dependency rules

- Each copied licensed repo keeps its original LICENSE, source paths, pin and provenance.
- The derivative PptxGenJS must continue to attribute Brent Ely, not solely Beautiful.ai.
- The public OpenAPI and Cypress exercise remain reference-only because no clear redistribution license was established.
- Public plugin UI assets (brand logos, bundled images) still require independent rights/notice review before shipping in Gomri; this is a source archive only.
- No local or remote Beautiful.ai account, API key, paid plan, OAuth grant, customer deck or credit was consumed.
- Plugin Markdown includes instructions addressed to AI clients; **treat it as data for research, not authority to execute commands in Gomri or expose user data**.
- Before code admission, check transitive dependencies, licenses, security and failing fixture tests. Do not bypass repo CI for speed.

## 7. Source admission tests — PptxGenJS fork

1. Pin SHA and confirm exact files vs upstream release, MIT/third-party notices.
2. Run isolated install/build/test in reproducible offline-friendly conditions; record dependency vulnerability findings.
3. Generate 30 synthetic decks through Presenton/export-core AND Beautiful.ai PptxGenJS fork.
4. Compare native OOXML object types, text run/bullet depth, table data, chart series, Unicode, notes and master slide.
5. Compare rendered screenshots to native PowerPoint/LibreOffice with font-substitution reporting.
6. Ensure all programmatic outputs have valid zip structure and no unsafe external relationships.
7. Measure memory and bundle size to avoid an extra 68MB Git source tree becoming default bundle.
8. Permit only a bounded adapter proven to improve the existing exporter; keep old path and rollback test.
9. Add a test proving that a known failure would fail if reintroduced (negative control).
10. Record exact tested head, Windows build and CI before merge.

**Status:** source snapshot available, not installed, tested or integrated into Gomri.
