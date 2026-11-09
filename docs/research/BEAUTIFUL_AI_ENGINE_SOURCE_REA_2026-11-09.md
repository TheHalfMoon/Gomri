# Beautiful.ai — Deep Engine REA and Copy-First Source Register

**Research date:** 2026-11-09. **Project:** TheHalfMoon/Gomri. **Status:** public-source acquisition + first-party engineering contract analysis; **not a production feature or a live authenticated Beautiful.ai benchmark**.

## Key findings

1. **Smart Slides is the product's engineering moat.** Template-specific elements automatically distribute, scale, align, animate and choose visual arrangements as content changes. New Beautiful.ai AI creation flow separates prompt, editable outline, Brand Kit and design. We should make SmartLayout a permanent editable engine layer in Gomri, not a one-shot image generator.
2. **We found unusually deep publicly released Beautiful.ai model documentation.** The official Nov 6, 2026 Claude/Grok plugin source includes 103 element reference documents; explicit per-slide schema `template_id`, `layout`, `states[0]`, version/migration, theme, text blocks, native charts/tables, freeform and 12x12 grids; render-before-save and per-slide MCP editing tool descriptions. We parsed 73 named template IDs referencing 59 root element documents. **These are real public Apache-licensed source documents, not the proprietary executable renderer.**
3. **We copied four licensed public source repositories into an isolated Gomri Git branch:** 388 tracked source files, pinned upstream commits, preserved MIT/Apache licenses. The copied code includes Beautiful.ai's modified version of PptxGenJS (3.13.0-bai.5) with the original Brent Ely attribution and its 2026 bullet/security changes.
4. **The Beautiful.ai public API and newer agent plugins are different generations of capability.** Published OpenAPI has **10 operations** and a structured outline containing **32 slide-content types**; the older MCP FAQ says its connector lacks arbitrary slide editing, whereas the new official Claude/Grok plugins refer to get_slide, update_slide, create_slide and render_slide. Account/rollout-dependent availability requires live verification.
5. **Critical gaps in the public source:** no actual SmartLayout algorithm, renderer implementation, private MCP backend, AI model routing/training weights, private templates and assets. Neither the public plugin nor PptxGenJS derivative yields Beautiful.ai's full product code.

## Detailed technical chapters

| Document | What it verifies / designs |
|---|---|
| [01 — Product, Smart Slides, 2026 releases](beautiful-ai-rea/01-product-smartslides-2026.md) | Prompt/outline/Slide AI/Preserve Exact Text, Smart Slides, Brand Kits, ROI, maps, export, plans |
| [02 — Actual slide model, element tree and layout](beautiful-ai-rea/02-source-slide-model-layout.md) | Explicit public JSON model, 12x12 grid geometry, freeform, migrations, computed caches, fit and data-loss failure modes |
| [03 — Agent tools, MCP and render-verify-save](beautiful-ai-rea/03-agent-tools-mcp-render-loop.md) | Published full agent workflow, placeholders, selection/slide updates, render errors, edit markers vs concurrency |
| [04 — Public API and PptxGenJS code](beautiful-ai-rea/04-openapi-pptx-source-provenance.md) | Six vendor-org public repos, 10 OpenAPI paths, 32 enum slide types, PptxGenJS derivative and license checks |
| [05 — Gomri fast implementation and 50 tests](beautiful-ai-rea/05-gomri-copy-first-build-and-arena.md) | Native SmartLayout + AI transaction integration waves, 12 priority template families, 50 planned competitor probes |

## Structured source inventories

- [Beautiful.ai 6 public repos, origin/rights/commit decision](../../registry/beautiful-ai-public-source-inventory-2026-11-09.csv).
- [388 source files: exact pins, ownership and admission gates](../../third_party/beautiful-ai-public/SOURCE_REGISTER.md).
- [Copied source trees: Claude, Grok, PptxGenJS and React state](../../third_party/beautiful-ai-public/).
- [73 named public template IDs and 59 root-element mappings](../../registry/beautiful-ai-template-model-map-2026-11-09.csv).
- [10 public API operations and 32 structured-outline slide types](../../registry/beautiful-ai-openapi-contract-2026-11-09.csv).
- [305 source-graded rows in 20 subject areas](../../registry/beautiful-ai-capability-source-matrix-2026-11-09.csv): public feature descriptions, exposed schema and tool semantics, API operations, **and unknowns**. This is **NOT** a claim of 305 working/confirmed end-user features.

## How it changes Gomri's plan

**BAI-01 (P0):** native SmartLayout constraints mapped onto Presenton's existing editor/Template V2, with non-destructive handling of invalid/missing cells, text-fit and chart/table data.

**BAI-02 (P0):** tool-driven AI edits modeled as typed patches with per-object permissions, revision conflicts, visual preview, render QA and undo. Reuse bounded Ninerr authorization/history code and existing Gomri source-bound narrative.

**BAI-03 (P0):** compare Beautiful.ai's source PptxGenJS derivative vs original upstream and Presenton export core; adopt only measured fixes to editable notes/chart/table/bullet/RTL fidelity.

**BAI-04 (P1):** 12 excellent editable Smart Slide families first, plus Skilit Brand Kit/reference pattern intelligence and agent plan→outline→design workflow.

**BAI-05 (P2):** collaboration and product integrations after flagship UX; 50 synthetic live benchmark cases, blind design scoring and exact-head CI gates.

Do **not** rewrite the whole app, double-import derivative source, replace a qualified exporter without tests, or assume a public vendor MCP URL is a free product engine.

## What actually happened in this session

**Completed:** researched current 2026 official features; inspected source in six public Beautiful.ai org repos; copied Apache/MIT source snapshots; analyzed current slide-schema/fit/migration and AI/MCP workflow; created indexed research reports, template/API/source and capability registries.

**Not completed:** authenticated black-box product testing; paid AI slide generation; runtime feature integration; new Windows/macOS/Linux builds; proving visual superiority. All 50 live benchmark scenarios are future **proposed tests**, not measured.

**No changes to Gomri main**, no deployment, no paid Beautiful.ai/Anthropic access, no source from private APIs.

## Primary official references

- [Beautiful.ai 2026 Product Updates](https://www.beautiful.ai/product-updates)
- [Create presentation with AI](https://support.beautiful.ai/hc/en-us/articles/12885226948109-Creating-a-presentation-with-AI)
- [Edit with Slide AI](https://support.beautiful.ai/hc/en-us/articles/43350069148557-Create-and-Edit-your-Slides-with-Slide-AI)
- [Beautiful.ai Smart Slides](https://www.beautiful.ai/slide-templates)
- [Beautiful.ai slide model source](https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-elements/elements/Slide.md)
- [Beautiful.ai new MCP plugin](https://github.com/beautifulai/claude-plugin)
- [Beautiful.ai public OpenAPI](https://github.com/beautifulai/beautifulai-docs/blob/main/openapi.yaml)
- [Beautiful.ai PptxGenJS](https://github.com/beautifulai/PptxGenJS)

**Research verdict:** We have reproducible public source and specific integration targets. Gomri can reproduce and improve observable Smart Slides behavior through independent implementation. We do **not** possess Beautiful.ai's private layout engine, source-of-truth database, server, or complete model pipeline.
