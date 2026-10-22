# GOMREY BASELINE SURVEY — what already exists

**Repository:** `/Users/abdulazizalsh/work/Gomrey`
**Branch:** `feature/rea/nextslide-gamma-wave1`
**Base SHA:** `5f299a7a6174ad3a1180f827778db5f4400a4d71` (main, `Merge pull request #76 from TheHalfMoon/p09/exit-closeout`)
**Survey date (UTC):** 2026-10-22
**Survey mode:** READ-ONLY. No repository file was modified by this survey except this document.
**Purpose:** exact inventory of existing Gomrey capability so that the NextSlide OSS-skill and Gamma-inspired waves do not duplicate, fork, or break working systems.

**Status legend:** `COMPLETE` · `PARTIAL` · `STUB` · `MISSING`

---

## 0. Executive summary

Gomrey is **not** a greenfield project. It is a fork of **Presenton** (`presenton/presenton`, Apache-2.0, `COPY_FULL_BASE` per `docs/SOURCE_LEDGER.md:23-41`) that already carries:

- a complete **presentation** product: generation (2 modes), 16 bundled templates, Konva-based slide editor, PPTX/PDF export, AI chat editing, MCP server, Electron desktop shell;
- a complete **evidence/retrieval/decision** substrate (P08/P09) that is pure-deterministic, tested, and *not connected to the presentation pipeline yet*.

The single most important structural fact for this mission: **the presentation pipeline (Presenton lineage) and the evidence/decision fabric (Gomrey P03–P09 lineage) are two separate systems that currently meet only at the contract/schema layer, not at runtime.** `docs/ARCHITECTURE.md:353-371` specifies the intended join (`EvidenceBundle → Narrative IR → Design IR → renderer`), but no such runtime path exists today.

Implication for the donor waves: the NextSlide skill's *HTML/CSS slide engine* and *PPTXGenJS exporter* would be **parallel stacks** for subsystems Gomrey already implements (Konva editor, `@presenton/export-core` exporter, python-pptx import). The Gamma-inspired work should target the **missing** join — Narrative IR / Design IR / layout QA / evidence-bound artifacts — rather than re-implement rendering.

---

## 1. PRESENTATION GENERATION PIPELINE

### 1.1 Where deck generation is orchestrated — COMPLETE

| Concern | File | Lines |
|---|---|---|
| v1 route composition (all 18 routers) | `servers/fastapi/api/v1/ppt/router.py` | 1-48 |
| v2 route composition | `servers/fastapi/api/v2/ppt/router.py`, `api/v2/router.py` | 1-9, 1-5 |
| App wiring | `servers/fastapi/api/main.py` | 64-83 (`app.include_router(...)` 67-73) |
| **Main orchestration** (create / prepare / stream / update / export) | `servers/fastapi/api/v1/ppt/endpoints/presentation.py` | 3334 lines total; key handlers below |
| Outline read/update/stream | `servers/fastapi/api/v1/ppt/endpoints/outlines.py` | 44-45, 59-60, 84-85 (276 lines) |
| Slide AI edit (`/edit`, `/edit-html`) | `servers/fastapi/api/v1/ppt/endpoints/slide.py` | 36-37, 127-128 (172 lines) |
| Template CRUD + PPTX→Template-V2 import | `servers/fastapi/api/v1/ppt/endpoints/template.py` | 2165 lines; routes at 1106, 1182, 1208, 1265, 1562, 1611, 1686, 1775, 1860, 1915, 1965, 2078, 2112, 2147 |
| Async task router | `servers/fastapi/api/v1/async_tasks/router.py` | — |
| Webhooks | `servers/fastapi/api/v1/webhook/router.py` | — |
| MCP server | `servers/fastapi/mcp_server.py` | 18 424 bytes; `main()` at 417, `get_mcp_instructions()` 143-287 |

**Orchestration entry points in `presentation.py`:**

- `POST /create` → `create_presentation` (L1634-1735)
- `POST /prepare` → `prepare_presentation` (L1783-1873)
- `POST /stream` (smart) → `stream_smart_presentation` (L1874-2223)
- `GET /stream/{id}` (standard) → `stream_presentation` (L2224-2469)
- `PATCH /update` → `update_presentation` (L2470-2527)
- `PATCH /slide_update` → `update_presentation_slide` (L2528-2562)
- `POST /{id}/export` → `export_existing_presentation` (L1595-1633)
- Layout resolution helpers: `_resolve_requested_template` (210), `_resolve_generation_layout` (260), `_build_template_layout_model` (398), `_template_slide_ui` (478), `_apply_template_content_to_ui` (563) and per-element appliers (614-1420)

**Storage models** (`servers/fastapi/models/sql/`):
- `presentation.py` — `PresentationModel`, `PresentationVersion` enum = `v1-standard` | `v2-standard` (L14-17)
- `slide.py` — `SlideModel` with `layout_group`, `layout`, `content` (JSON), `html_content`, `speaker_note`, `properties`, `ui` (JSON) — L10-31
- `template_v2.py` — `TemplateV2`

### 1.2 LLM provider seam — COMPLETE

**The seam is `servers/fastapi/utils/llm_provider.py`:**

- `get_llm_provider()` (L47-59) → `LLMProvider(get_llm_provider_env())`, HTTP 500 on invalid.
- `get_model()` (L126-174) → per-provider model resolution with env override + `DEFAULT_*` fallback.
- 15 provider predicates (L62-124): `is_openai_selected`, `is_deepseek_selected`, `is_google_selected`, `is_anthropic_selected`, `is_vertex_selected`, `is_azure_selected`, `is_bedrock_selected`, `is_ollama_selected`, `is_custom_llm_selected`, `is_cerebras_selected`, `is_openrouter_selected`, `is_fireworks_selected`, `is_together_selected`, `is_codex_selected`, `is_litellm_selected`, `is_lmstudio_selected`.
- Supported provider list (from the error message, L54-58): `openai, deepseek, google, vertex, azure, bedrock, openrouter, fireworks, together, cerebras, anthropic, litellm, lmstudio, ollama, custom, codex`.

**Client construction:** `servers/fastapi/utils/llm_config.py` (524 lines) — `get_llm_config()` builds typed `llmai.shared.*ClientConfig` objects per provider; web-grounding toggle (`enable_web_grounding`, L~100), thinking disable, Codex OAuth refresh path (`_get_codex_access_token`, L~108).

**LLM client library:** `llmai==0.3.15` (pinned in `servers/fastapi/pyproject.toml:31`). Provider configs come from `llmai.shared`.

**Provider disable/config:** all env-driven through `servers/fastapi/utils/get_env.py`; per-user overrides persist via `servers/fastapi/services/provider_settings.py` (191 lines) and `models/sql/provider_settings.py`. Frontend provider UI: `servers/nextjs/components/LLMSelection.tsx`, `components/*Config.tsx` (Anthropic, OpenAI, Google, Vertex, Bedrock, Codex, Ollama, Custom), `servers/nextjs/utils/providerConstants.ts`, `utils/providerUtils.ts`.

**Generation token defaults** (`POST /api/v1/ppt/generation/defaults`): `servers/fastapi/api/v1/ppt/endpoints/generation.py:54-58` + `resolve_generation_token_defaults` (L26-51).

### 1.3 Outline / content planning — COMPLETE

| Stage | File | Lines |
|---|---|---|
| Outline generation (title + slide markdown outline), streaming, web-search augmented | `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py` | 404 lines; `get_system_prompt` L71-…; `DIRECT_CONTENT_VOICE_RULES` L39-52 |
| **Layout selection** (per-slide layout index) | `servers/fastapi/utils/llm_calls/generate_presentation_structure.py` | 211 lines; `STRUCTURE_FROM_SLIDES_MARKDOWN_SYSTEM_PROMPT` L18-60 (selection rules for table/chart/metrics layouts) |
| Slide content generation against a JSON schema | `servers/fastapi/utils/llm_calls/generate_slide_content.py` | 275 lines; `SLIDE_CONTENT_SYSTEM_PROMPT` L21-69 |
| Smart (HTML) deck generation | `servers/fastapi/utils/llm_calls/generate_smart_presentation.py` | 936 lines; `get_smart_messages` L308, `normalize_smart_slide_html` L417, `_validate_smart_slide_layout_safety` L438, `SmartSlideStreamParser` L556, `generate_smart_presentation` L733 |
| Web-search query synthesis | `servers/fastapi/utils/llm_calls/generate_web_search_query.py` | 74 lines |
| AI edit of a slide (schema-constrained) | `servers/fastapi/utils/llm_calls/edit_slide.py` | 167 lines |
| AI edit of slide HTML | `servers/fastapi/utils/llm_calls/edit_slide_html.py` | 95 lines |
| AI re-layout of a slide on edit | `servers/fastapi/utils/llm_calls/select_slide_type_on_edit.py` | 92 lines |
| Structured-output plumbing | `servers/fastapi/utils/llm_utils.py` (535), `utils/schema_utils.py`, `utils/get_dynamic_models.py` | — |
| Web-search providers (SearXNG/Tavily/Exa/Brave/Serper/model-native) | `servers/fastapi/utils/web_search.py` | — |

### 1.4 `docs/presentation-generation-modes.md` — COMPLETE

Defines two workflows selected by the `PRESENTATION_GENERATION_MODE` env var (default `both`; values `both` | `standard` | `smart`; case-insensitive; unrecognised → `both`):

| Mode | Web UI | MCP tools |
|---|---|---|
| `standard` | Fixed, predefined layouts; includes outline review step; supports built-in + custom templates | Standard + template-generation tools |
| `smart` | Adaptive layouts that respond to generated content; streams directly into the editor; **no** template workflow | Only the Smart generation workflow |
| `both` | Mode selector shown, Standard preselected; template pages remain available | Standard, Smart, and template-generation tools |

The doc explicitly notes the setting is **not** an authorization control for the REST API (L26-28). Implementation:
- Backend mode gate: `servers/fastapi/mcp_server.py:143` `get_mcp_instructions(generation_mode)`; mode value read via `get_env`.
- Frontend: `servers/nextjs/utils/presentationGenerationMode.ts` (`normalizePresentationGenerationMode`, `isGenerationModeAvailable`, `getInitialGenerationMode`), `servers/nextjs/app/(presentation-generator)/(dashboard)/layout.tsx:7-15` (`showTemplates={presentationGenerationMode !== "smart"}`), `app/(presentation-generator)/upload/components/GenerationModeDialog.tsx`.
- Docker: `docker-compose.yml` forwards `PRESENTATION_GENERATION_MODE` to every profile.

---

## 2. TEMPLATES / LAYOUTS / THEMES

### 2.1 Template inventory — COMPLETE

**Repo-root `templates/` — 16 bundled templates**, each `<id>/template.json` + `<id>/static/` (images, thumbnail):

`civic` (29 layouts / 38 merged), `dynamic` (32/40), `editorial` (24/9), `executive` (32/47), `general` (12/15), `horizon` (28/29), `landmark` (27/17), `modern` (10/19), `momentum` (28/27), `mosaic` (34/67), `nova` (28/26), `pulse` (28/20), `signal` (24/20), `standard` (11/19), `swift` (9/20), `verdant` (27/31).

**Template JSON schema** (top-level keys enforced by `scripts/convert-template.mjs:15-23`):
```
id, name, description, thumbnail, merged_components[], layouts[], fonts{}, theme{}
```
- `merged_components[]` → `{id, description, variants[]}`; each variant `{id, description, position{x,y}, elements[]}`
- `layouts[]` → `{id, description, components[]}`
- `theme` → `{colors{primary, background, card, stroke, primary_text, background_text, graph_0..graph_9}, fonts{textFont{name,url}}}`
- Elements are 1280×720-px typed objects: `vector` (polygon/points/fill), `text`, `text-list`, `image`, `rectangle`, `ellipse`, `line`, `container`, `flex`, `grid`, `table`, `chart`, `infographic`.

**Import path:** `servers/fastapi/templates/default_templates.py` — `import_default_templates_on_startup()` (L21-59) scans `templates/`, upserts `TemplateV2` rows, copies static assets, removes stale defaults. Root resolution `_default_templates_root()` (L60-61).

**Template model (DB):** `servers/fastapi/models/sql/template_v2.py`.

### 2.2 Root `layouts.json` — ORPHAN ARTIFACT (note)

`/layouts.json` (252 637 bytes) at repo root holds `{layouts:{layouts:[14 layouts]}}` in the same Template-V2 layout shape but **is not referenced by any code path** (grep for the literal `"layouts.json"` returns zero hits outside variable names). Treat it as a stale export, **not** a source of truth.

### 2.3 `servers/fastapi/templates/` — COMPLETE

| File | Lines | Role |
|---|---|---|
| `presentation_layout.py` | 62 | `PresentationLayoutModel`, `SlideLayoutModel` (re-exported by `models/presentation_layout.py`) |
| `preview.py` | 62 | Slide preview rendering |
| `fonts_and_slides_preview.py` | 1 922 | PPTX font + slide preview pipeline (python-pptx based) |
| `pptx_font_utils.py` | 1 668 | **python-pptx** font replacement / PPTX inspection (L13 `from pptx import Presentation`; L1075 "Replace fonts in a PPTX file using python-pptx") |
| `default_templates.py` | 315 | Bundled-template bootstrap |
| `v2/schema.py` | 1 548 | Template-V2 JSON schema + `slide_layout_llm_json_schema` |
| `v2/models/layouts.py` | 977 | `SlideLayout`, `SlideLayouts`, `Component`, `MergedComponent`, `MergedComponents`, `LayoutGenerationOptions`, `SimilarComponentsList` |
| `v2/models/elements.py` | 694 | Element models incl. `Image`, `ImageFit` |
| `v2/generation.py` | 1 371 | Template-V2 layout generation (LLM), `DEFAULT_VALIDATION_RETRIES = 5` (L48), `MAX_PARALLEL_SLIDE_LAYOUTS = 10` (L49), preview-slide tool loop (L50) |
| `v2/certified_generation.py` | 4 621 | "Certified" Template-V2 generation: vision passes, component merging, text-capacity planning, semantic manifests, duplicate detection |
| `v2/theme.py` | 806 | Theme derivation (see 2.5) |
| `v2/content.py` | 87 | Content hydration into Template-V2 element trees |
| `v2/tools.py` | 123 | `PreviewSlideTool` (`PREVIEW_SLIDE_TOOL_NAME`) |

### 2.4 `servers/nextjs/` template surfaces — COMPLETE

- `app/(presentation-generator)/(dashboard)/templates/` — template gallery page + `TemplatePanel.tsx`, `CreateCustomTemplate.tsx`
- `app/(presentation-generator)/custom-template/` — custom template creation flow (`CustomTemplatePage.tsx`, `hooks/useTemplateCreation.ts`, `hooks/useFileUpload.ts`)
- `app/(presentation-generator)/template-preview/` — template preview + **layout editor** (`components/editor/LayoutsPanel.tsx`, `ThumbnailStrip.tsx`, `ResponsiveSlideFrame.tsx`, `templatePreviewAnalytics.ts`)
- `lib/template-v2-json-to-html.ts` (4 145 lines) — canonical Template-V2 → HTML renderer
- `lib/template-theme.ts` — theme normalisation + `TEMPLATE_THEME_COLOR_KEYS` (16 keys), `DEFAULT_TEMPLATE_THEME`
- `app/(presentation-generator)/components/TemplatePreviewComponents.tsx`, `TemplateV2HtmlSlidePreview.tsx`

### 2.5 Layout selection / auto-layout — PARTIAL (two distinct mechanisms)

**(a) Standard mode — LLM-chosen layout index (deterministic schema, probabilistic choice).**
`utils/llm_calls/generate_presentation_structure.py:18-60` returns `PresentationStructureModel` = `{slides: List[int]}` (`models/presentation_structure_model.py`). The LLM picks one layout index per slide under written rules (table→table/graph layout, chart requires numeric table, image layouts only when imagery requested, etc.). There is **no** scoring/fitting objective, no overflow pre-check, and no deterministic tie-break — the selection is a single LLM call.

**(b) Smart mode — LLM emits free-form HTML + deterministic safety inspection.**
`utils/llm_calls/generate_smart_presentation.py` streams HTML per slide; `_validate_smart_slide_layout_safety` (L438) calls `utils/smart_slide_layout.py` (≈300 lines) — a pure HTML/Tailwind-aware geometry inspector that detects: negative margins/translations, `overflow-hidden` on text-bearing containers, absolutely-positioned content without a complete pixel box, off-canvas/zero-size geometry, container-boundary overflow, and overlapping absolutely-positioned siblings. Canvas constants `SLIDE_WIDTH = 1280.0`, `SLIDE_HEIGHT = 720.0` (L8-9).

**(c) Template-V2 certified generation — deterministic text-capacity + geometry planning.**
`templates/v2/certified_generation.py` contains `_validate_text_capacity_plan` (L1783), `_apply_text_capacity_plan` (L1961), `_estimated_text_capacity` (L2375), `_estimated_text_character_width` (L2449), `_validate_flexible_plan` (L2512), `_infer_repeat_geometry` (L2692), `_validate_regular_repeat_geometry` (L2814), `_compile_semantic_layout` (L2895). This is the **closest thing to a layout-QA engine in the repo**.

**(d) Frontend layout algorithms — COMPLETE for *editing*, not for *auto-placement*.**
`servers/nextjs/components/slide-editor/layout/flowLayout.ts` (flex + grid child placement), `wrappedFlexLayout.ts`, `layoutResize.ts`, `layoutItems.ts`; `model/model.ts` (2 336 lines) `layoutChildren` / `layoutContainerChildren`; `selection/` transformers.

### 2.6 Theme / color / brand — PARTIAL

- **Theme derivation from a template:** `servers/fastapi/templates/v2/theme.py` — `build_theme_profile` (L145), `select_theme_roles_with_llm` (L261), `select_theme_roles_deterministically` (L305), `materialize_theme` (L357), `template_theme_for_presentation` (L405), `contrast_ratio` (L423). Constants: `MAX_PROFILE_COLORS = 14`, `MAX_PROFILE_PAIRS = 8`, `MAX_PROFILE_FONTS = 5` (L26-28).
- **Theme data model:** `servers/fastapi/models/theme_data.py` — `PresentationThemeColors`, `PresentationThemeTextFont`, `PresentationThemeFonts`, `PresentationThemeData`.
- **Theme apply to DOM:** `servers/nextjs/app/(presentation-generator)/presentation/utils/applyPresentationThemeDom.ts`.
- **16-color semantic scale:** `primary, background, card, stroke, primary_text, background_text, graph_0..graph_9` — mirrored in `servers/nextjs/lib/template-theme.ts` (`TEMPLATE_THEME_COLOR_KEYS`).
- **Fonts:** bundled local catalog at `servers/nextjs/public/vendor/fonts/` (families: sans_serif, serif, slab_serif, script, handwritten, display — ~50+ families). Loader: `servers/nextjs/components/slide-editor/text/local-fonts.ts`, `surface/fontLoading.ts`; `app/(presentation-generator)/hooks/useFontLoad.tsx`, `useFontLoader.tsx`. Upload endpoint: `servers/fastapi/api/v1/ppt/endpoints/fonts.py` (172 lines) + `models/sql/font_upload.py`.
- **Brand kits:** **MISSING.** No `brand` concept beyond `DesignIR.brand_skill_id` in the contract (`contracts/v1/design-ir.schema.json`) and the `brand_skill_id` field. No brand-kit entity, no logo ingestion, no brand extraction skill. `docs/NO_GAPS_CHECKLIST.md:82` lists "Brand system" as a **P11/P13** row — still open.
- **Theme presets (named, curated style sets):** **MISSING.** There is no "preset" catalogue; themes are only derived from an existing template's own content. (`STYLE_PRESETS.md` is a *NextSlide donor* artifact — see `research/rea/2026-10-22-nextslide-gamma/SOURCES.md:69`.)
- **Infographic catalogue (closest existing "visual preset" system):** `servers/fastapi/utils/infographic_catalog.py` (639 lines) — `INFOGRAPHIC_CATALOG` (L45-478) with **27 infographic types** (`progress_bar, gauge, gantt, timeline, roadmap, milestone_timeline, staircase, supply_chain, stair_step_blocks, maturity_model, pillar_framework, transformation_hub, diagonal_circles, risk_matrix, chevron_process, radial_cycle, conversion_funnel, vertical_funnel, pyramid, segmented_wheel, customer_journey, before_after, impact_effort_matrix, comparison_matrix, org_chart, decision_tree, mind_map`). Mirrored in `servers/fastapi/services/chat/infographic_catalog.py`.

### 2.7 `scripts/convert-template.mjs` / `scripts/convert-presentation-template.mjs` — COMPLETE

| Script | Purpose |
|---|---|
| `scripts/convert-template.mjs` | Converts an **exported template JSON** into the **bundled default-template shape**. Exports `convertTemplateData` / `convertTemplate`. Enforces `TOP_LEVEL_KEYS` (L15-23) = `id, name, description, thumbnail, merged_components, layouts, fonts`. Replaces editable image/icon URLs with `/static/images/replaceable_template_image.png` and `/static/icons/placeholder.svg` (L25-26); copies referenced assets into `<template>/static/` and the app-data `images/` + `fonts/` dirs. |
| `scripts/convert-presentation-template.mjs` | Converts an **edited presentation JSON** (the template editor's output) into a template: bundles per-layout UI edits into `layouts[]` and into `merged_components[].variants[]`, with `--id/--name/--description/--thumbnail` overrides. Imports `convertTemplateData` from `convert-template.mjs`. |

**Source-of-truth schema:** the bundled `templates/<id>/template.json` shape (enforced by `scripts/convert-template.mjs` `TOP_LEVEL_KEYS` and validated by `scripts/convert-template.test.mjs`, `scripts/convert-presentation-template.test.mjs`).

Root npm scripts: `npm run convert:template`, `npm run convert:presentation-template`, `npm run test:template-converter`.

---

## 3. TYPOGRAPHY / STYLING / DESIGN TOKENS

### 3.1 App-shell design tokens — PARTIAL

- `servers/nextjs/app/globals.css` — `@font-face` for Manrope + Syne (L1-15); CSS custom properties in `:root` / `.dark` (L38-100+): `--background, --foreground, --card, --popover, --primary, --secondary, --muted, --accent, --destructive, --border, --input, --ring, --chart-1..5, --radius`. This is the **shadcn/ui** token set — it governs the **application chrome**, not slide content.
- `servers/nextjs/tailwind.config.ts` — maps those CSS vars to Tailwind tokens; `fontFamily: {syne, manrope}`; `darkMode: ["class"]`.
- `servers/nextjs/components.json` — shadcn/ui config.

### 3.2 Slide-level typography — PARTIAL (functional, not a design system)

- Text model: `servers/nextjs/components/slide-editor/text/text-runs.ts`, `text/template-v2-text.ts` (rich-run layout engine: alignment, vertical alignment, line height, wrapping, bold/italic/underline, color, letter spacing, list markers), `text/text-line-height.ts`, `text/markdown-text.ts`.
- Rich-text editing: `text/TiptapInlineTextEditor.tsx`, `text/TemplateV2InlineEditor.tsx` (Tiptap overlay over Konva text).
- Toolbars: `text/TextToolbar.tsx`, `text/BulletsToolbar.tsx` — font family, size, styles, color, alignment, opacity, letter spacing, line height.
- Fonts: `text/local-fonts.ts` + `public/vendor/fonts/**`; `surface/fontLoading.ts` gates the Konva layer on font readiness.
- **Gap:** there is **no** typographic scale, baseline grid, spacing scale, or modular type ramp applied to slide content. Sizes are raw pixel values on a 1280×720 canvas.

### 3.3 Rendering surfaces

| Surface | Path |
|---|---|
| Next.js App Router pages | `servers/nextjs/app/**` (12 route groups listed in §7) |
| React components | `servers/nextjs/components/**` (27 dirs incl. `slide-editor/`, `ui/`, `Auth/`, `runtime/`) |
| Shared lib | `servers/nextjs/lib/**` (15 files: `template-v2-json-to-html.ts`, `template-theme.ts`, `math.ts`, `chart-browser.ts`, `svg-color.ts`, `runtime-limits.ts`, `user-config-store.ts`, …) |
| Next.js route handlers | `servers/nextjs/app/api/**` (`export-presentation`, `export-presentation-data/[id]`, `export-presentation/file`, `upload-image`, `user-config`, `runtime-config`, `update-svg`, `read-file`, `has-required-key`, `can-change-keys`, `github-stars`, `telemetry-status`) |
| FastAPI static assets | `servers/fastapi/static/` (icons: fill/duotone/thin/bold/light/regular; images; vendor) |
| Electron renderer assets | `electron/resources/ui/assets/{css,fonts}` |

---

## 4. EDITOR (UI editing)

### 4.1 Is there a slide editor UI — YES, COMPLETE for Template-V2 slides

**Routes (Next.js App Router):**

| Route | Purpose |
|---|---|
| `/upload` | Create: prompt, files, slide count, language, tone, verbosity, mode |
| `/outline` | Outline review + template selection (Standard mode) |
| `/presentation` | **The editor** |
| `/custom-template` | Custom template creation |
| `/template-preview` | Template preview + layout editor |
| `/documents-preview` | Source-document preview/edit (input side) |
| `/dashboard`, `/templates`, `/community`, `/settings`, `/admin` | Dashboard surfaces |
| `/pdf-maker` (route group `(export)`) | Headless export renderer |

**Editor core:** `servers/nextjs/components/slide-editor/` — 73 files across 16 subfolders (`surface, model, selection, toolbar, text, tables, charts, images, shapes, layout, clipboard, events, math, importing, infographics, insert, shortcuts, state, types.ts, utils`).

**Authoritative map:** `servers/nextjs/components/slide-editor/README.md` (1 385 lines) — the single most complete technical document in the repo. It enumerates every feature and its owning file.

**What can be edited:**

| Capability | Owner |
|---|---|
| Component drag / multi-select | `surface/TemplateV2KonvaSlide.tsx` (3 400 lines) — `handleComponentDragStart/Move/End` |
| Resize / transform | `selection/SelectionTransformers.tsx` |
| Rich text (Tiptap overlay) | `text/TiptapInlineTextEditor.tsx`, `text/TemplateV2InlineEditor.tsx` |
| Tables (cell select + inline edit) | `tables/TemplateV2TableElement.tsx`, `tables/TableInlineEditor.tsx`, `tables/useTableCellSelection.ts` |
| Charts (type, data, colors, axes) | `charts/TemplateV2ChartJsElement.tsx`, `charts/ChartToolbar.tsx`, `charts/ChartEditorContent.tsx`, `charts/chart-data.ts` |
| Images (replace, crop focus, flip, opacity, radius) | `images/ImageToolbar.tsx` |
| Icons (search, replace, weight, recolor) | `images/IconsEditor.tsx` + `lib/svg-color.ts` |
| Shapes / lines / shadows | `shapes/ShapeToolbar.tsx`, `shapes/LineToolbar.tsx`, `model/render-style.ts` |
| Flex / grid layout + items | `layout/flowLayout.ts`, `layout/layoutItems.ts`, `layout/layoutResize.ts`, `layout/LayoutToolbar.tsx` |
| Ungroup, layer order | `model/template-v2-ungroup.ts`, `selection/layering.ts` |
| Copy / paste / duplicate | `clipboard/clipboard.ts`, `clipboard/useClipboard.ts` (custom MIME `application/x-gomrey-template-v2`) |
| Design variables | `toolbar/DesignVariablesToolbar.tsx`, `model/design-variables.ts` |
| Insert blocks/elements | `insert/insert-elements.ts`, `model/inserted-content.ts` |
| Smart-mode HTML editing | `app/(presentation-generator)/components/SmartHtmlEditor.tsx`, `SmartHtmlSelectionOverlay.tsx`, `SmartHtmlSlide.tsx` |

**What is NOT editable (gaps):** no slide-level "re-layout to a different template layout" UI for Standard mode; no cross-slide master/grid; no accessibility (alt-text authoring, contrast check) UI; no RTL/Arabic authoring; no i18n of UI strings in the editor.

### 4.2 Undo/redo — COMPLETE (two independent implementations)

1. **Surface-local (Template-V2 canvas):** `components/slide-editor/surface/TemplateV2KonvaSlide.tsx` — `undoStackRef` / `redoStackRef` (L423-424), `commitUi(nextUi, pushHistory)` (L1250), `undo()` (L1282), `redo()` (L1290), `MAX_HISTORY_ENTRIES` (imported L151). Keyboard Cmd/Ctrl+Z / Cmd/Ctrl+Y, active-surface scoped, editable-target aware.
2. **Deck-level (Redux):** `servers/nextjs/store/slices/undoRedoSlice.ts` (142 lines) + `app/(presentation-generator)/presentation/hooks/PresentationUndoRedo.ts` (99 lines).

### 4.3 Autosave — COMPLETE

`app/(presentation-generator)/presentation/hooks/useAutoSave.tsx` (212 lines) — debounced (default 1 000 ms), diff-based (not blind write), paused while `isStreaming || isLoading || isLayoutLoading`, coalesces concurrent saves via `pendingSaveRef`, snapshots via `app/(presentation-generator)/presentation/utils/autoSaveDiff.ts`. Test: `servers/nextjs/tests/presentation-autosave.test.mjs`.

### 4.4 Versioning / history — MISSING (no persistent revision history)

- No `ArtifactRevision` rows, no revision timeline, no named versions, no diff viewer.
- `contracts/v1/artifact-revision.schema.json` **exists** (schema-only) and `contracts/v1/artifact.schema.json` requires `current_revision` — but no runtime implementation.
- `docs/ARCHITECTURE.md:372-382` specifies the target model (stable identities, optimistic expected-revision checks, idempotent mutation keys, structured diffs, undo/history, branch/merge) — **unimplemented**.
- `docs/NO_GAPS_CHECKLIST.md` has no explicit revision-history row; `docs/MASTER_PLAN.md` P11 does not cover it either. **Unclaimed gap.**

### 4.5 State management — COMPLETE

- Redux Toolkit + React-Redux: `servers/nextjs/store/store.ts` (18 lines), slices `presentationGeneration.ts`, `presentationGenUpload.ts`, `undoRedoSlice.ts`, `userConfig.ts`.
- Local component state for canvas interaction (see README "Editor Surface State").
- Zustand is **not** used; the `zustand-store-ts` skill in the environment is not relevant here.
- `servers/nextjs/models/` contains only `models/errors.ts` — there is **no** shared TypeScript domain model for artifacts. The contract layer is JSON Schema only (`contracts/v1/*.json`), with no generated TS types and no runtime validator wired into the Next.js app.

---

## 5. EXPORT ENGINE

### 5.1 PPTX export — COMPLETE, but **not owned by this repo**

**Chain:**

```
FastAPI POST /api/v1/ppt/presentation/{id}/export
  → utils/export_utils.py:43-75  export_presentation()
  → services/export_task_service.py:425 export_from_url()
  → builds URL  <NEXT_PUBLIC_URL>/pdf-maker?id=…&fastapiUrl=…
Next.js /pdf-maker  (route group "(export)")
  → app/(export)/pdf-maker/page.tsx → PdfMakerPage.tsx  (renders slides to HTML/Chromium)
Next.js POST /api/api/export-presentation
  → lib/run-bundled-presentation-export.ts  runBundledPresentationExport()
  → spawns  presentation-export/runner.mjs  (external package)
  → @presenton/export-core  runTask({type:"export", format:"pptx"|"pdf"})
  → writes <APP_DATA_DIRECTORY>/exports/…
```

- **External runtime:** repo-root `presentation-export/` — installed by `scripts/sync-presentation-export.cjs` from `https://github.com/presenton/presenton-export/releases/download` (see `sync-presentation-export.cjs:26-29`), pinned to `presentationExportVersion: "v1.0.34"` in root `package.json:4`. The directory is **gitignored** (`.gitignore:29-30`) and **not present** in this checkout — `npm run sync:presentation-export` must run before export works.
- `scripts/sync-presentation-export.cjs` CLI: `--force`, `--check-only`, `--allow-version-override`; validates `sharp` native runtime for the platform; writes `presenton-export-version.json`.
- `scripts/run-presentation-export.mjs` — task runner: builds `runTask()` options (output dir, temp dir, Puppeteer executable path/cache, cookie `urlConfigs`, `modifyWindow` injecting `NEXT_PUBLIC_FAST_API` / `ASSETS_BASE_URL` into the page), normalises the response shape (`path` / `file_path`), writes `<task>.response.json`.
- **Fidelity:** the export is *DOM-based*. The PDF-maker page renders slides at exactly 1280×720 with an explicit print stylesheet (see `PdfMakerPage.tsx:26-70`, including the comment that "export-core measures PPTX elements in a 3000px-wide viewport"). Text/shape/table/chart fidelity therefore depends on `lib/template-v2-json-to-html.ts` (4 145 lines) being complete relative to the Konva renderer. **The donor's PptxGenJS exporter would be a parallel stack, not a drop-in.**
- **Editability:** the design intent (ARCHITECTURE.md:369-371) is editable text/charts, and the Konva/HTML pipeline does emit real text runs and Chart.js canvases. Whether the resulting PPTX is *text-editable* vs *image-flattened* is determined inside the external `@presenton/export-core` package — **not verifiable from this repository**.

### 5.2 PPTX import / extraction — COMPLETE, and already stronger than the donor

- `servers/fastapi/services/export_task_service.py:690-731` `convert_pptx_to_json(pptx_path)` → `PptxToJsonDocument`; also `convert_pptx_to_html` (L460). Artifacts land under `app_data/pptx-to-json/` and `app_data/pptx-to-html/` (`api/v1/auth/assets.py:9-10`; `api/v1/admin/router.py:267-268`).
- `servers/fastapi/templates/pptx_font_utils.py` (1 668 lines) — python-pptx based font replacement and PPTX inspection.
- `servers/fastapi/templates/fonts_and_slides_preview.py` (1 922 lines) — PPTX→rendered-slide-images + font mapping.
- `servers/fastapi/api/v1/ppt/endpoints/template.py:924-1000` — the PPTX→Template-V2 certified-creation flow (validates one preview image per raw slide, rejects otherwise).
- **No donor `extract-pptx.py` should be copied** (already recorded in `evidence/BASELINE_GATE_RUN.md:78`).

### 5.3 PDF / HTML / image export — COMPLETE

- **PDF:** same export chain, `format: "pdf"`.
- **HTML:** `servers/nextjs/lib/template-v2-json-to-html.ts` — Template-V2 → HTML string; also `app/(presentation-generator)/components/TemplateV2HtmlSlidePreview.tsx` and `app/(presentation-generator)/custom-template/components/EachSlide/TemplateV2LayoutPreview.tsx` (DOM preview path).
- **Image:** `services/export_task_service.py` — `render_html_to_image` (L524), `render_json_to_image` (L551), `render_jsons_to_images` (L583), `render_htmls_to_images` (L629); result models `HtmlToImageTaskResult` (L110), `HtmlToImagesTaskResult` (L114), `JsonToImageTaskResult` (L118).
- **Formats accepted by the API:** only `Literal["pptx","pdf"]` (`utils/export_utils.py:46`; `models/generate_presentation_request.py:41,64`; `models/presentation_from_template.py:14`). **PNG/JPEG/WebP export is internal-only** — there is **no user-facing image export endpoint**.

### 5.4 `scripts/run-presentation-export.mjs` + `scripts/sync-presentation-export.cjs` — relation to FastAPI

- `sync-presentation-export.cjs` = **installer** (network fetch → `presentation-export/`).
- `run-presentation-export.mjs` = **task runner entrypoint** copied into `presentation-export/runner.mjs`; the *server-side* FastAPI does **not** call it directly — it calls `EXPORT_TASK_SERVICE.export_from_url()` (Python) → Next.js `/api/export-presentation` → `runBundledPresentationExport()` → spawns `presentation-export/runner.mjs` in an isolated child process.
- Next.js side: `lib/run-bundled-presentation-export.ts` — `getExportPackageRoot()` (L12-19), `bundledExportPackageAvailable()` (L47-57), `runBundledPresentationExport()` (L137-), isolated child process, bounded stdout/stderr buffers, temp workdir cleanup, output-path normalisation relative to `APP_DATA_DIRECTORY`, `0o755/0o644` permission normalisation.

### 5.5 Export tests / fixtures — PARTIAL

- `servers/nextjs/tests/pdf-maker-export-layout.test.mjs` — export layout assertions.
- `servers/fastapi/tests/unit/test_export_cookie_header.py` — export cookie header.
- `servers/fastapi/tests/test_pptx_font_utils.py` — python-pptx font utils.
- `scripts/sync-presentation-export.test.mjs` — installer.
- **MISSING:** no golden/fixture-based PPTX or PDF output comparison test; no export fidelity regression suite; no round-trip test (export → re-import → compare).

---

## 6. RESEARCH / SOURCE / EVIDENCE / VERIFICATION (P08 / P09)

### 6.1 Retrieval pipeline (P08-G1) — COMPLETE, pure-deterministic, NOT wired to production

`servers/fastapi/gomrey/retrieval_pipeline.py` (160 lines). Channels: `("exact", "lexical", "dense", "visual", "graph")` (L30).
- `acl_filter` (L37-52) — ACL first; denied candidates counted, never leaked.
- exact identifier/location boost → lexical overlap → dense/visual/graph as *inputs only*.
- explicit weighted fusion with recorded per-candidate channel presence (missing channel = absent evidence, not zero).
- freshness as a filter; diversity caps per source; **rebuildable**: with dense/visual/graph absent, exact+lexical still retrieve ("never nothing").
- Failures raise `AdmissionError` from `gomrey/gateway.py`.

**Status:** the module has **no index server and no embeddings** — it is an *ordering discipline* over candidate records that future index stages produce. There is **no** dense index, **no** BM25/FTS implementation, **no** reranker, **no** embedding model pack, and **no** call site in the presentation pipeline. `docs/evidence/P08_EXIT.md:11-22` states this explicitly ("the frozen-benchmark-beats-baseline half is NOT yet measured").

### 6.2 Citation resolver (P08-G2) — COMPLETE, not wired

`servers/fastapi/gomrey/citations.py` (130 lines). `LOCATOR_KINDS = {"document","web","video","spreadsheet","image"}` (L29).
- `citation_id(locator)` — deterministic sha256 of canonical JSON → `cite-<16 hex>` (L39-42).
- `make_locator(kind, **fields)` — validated shapes; unknown kinds refused (L45-50).
- Resolver requires: unit exists, source matches, coordinates agree (page, timestamp containment, cell-in-range, bbox sanity). Otherwise raises `BrokenCitation` with the exact defect named. **A broken citation is a typed error at resolve time, never a rendered footnote.**

### 6.3 Evidence bundle (P08-G3) — COMPLETE, not wired

`servers/fastapi/gomrey/evidence_bundle.py` (132 lines). `SUFFICIENCY_VERDICTS = {"sufficient","insufficient","needs_review"}` (L32).
- Bundle binds: source revisions, resolved spans, retrieval identities, contradictions, omissions/truncation, freshness, scope, digest, verification state — **all together**; missing any ⇒ malformed, not partial.
- Contradictions escalate to `needs_review`; never averaged away.
- Omissions must carry recorded reasons.
- Sufficiency gate decides *whether there is anything to classify*; classification itself belongs to P09.

### 6.4 Claim contracts + verification engine (P09-G1/G2) — COMPLETE, not wired

`servers/fastapi/gomrey/claims.py` (357 lines) — durable claim records, evidence binding that never widens insufficiency, override tripwire (`detect_policy_override_attempt`), tenant-isolated store.

`servers/fastapi/gomrey/verification.py` (213 lines):
- `VERDICTS = {supported, partially_supported, contradicted, does_not_establish, unresolved, blocked}` (L47-55)
- `STANCES = {supports, contradicts, context}` (L57)
- Unbindable claims (missing refs, cross-project, stale, open contradictions, override flags) **never** verify as supported — the binder's refusal is inherited, not re-judged.
- Missing evidence views ⇒ `does_not_establish`, not support by assumption.
- Deterministic number/date checks run **before** any provider opinion; mismatch ⇒ `does_not_establish` with the defect named.
- Provider seam: `provider_verdict` carries provider + model revision; a provider **cannot** upgrade a deterministically failed claim, suppress a contradiction, or clear an override flag — overreach recorded as `provider-overruled`.
- Source/model/tool text is treated as **data**: override tripwires in the claim or any evidence view force `unresolved`.
- Every verdict carries reasons, applied deterministic checks, and a reproducible digest.

### 6.5 Decision graph (P09-G3) — COMPLETE, not wired

`servers/fastapi/gomrey/decisions.py` (359 lines).
- `NODE_KINDS = {claim, evidence, source, citation, decision}`; `EDGE_RELATIONS = {supports, contradicts, cites, derives, context}`; `DECISION_STATUSES = {proposed, accepted, abstained, blocked, superseded}`; `SYNTHESIS_ELIGIBLE = {supported, partially_supported}` (L39-47).
- `build_graph` refuses dangling references and orphan citations; `graph_digest` = canonical sha256.
- `make_decision` — question, claims, evidence, constraints, assumptions, uncertainty, alternatives, conclusion, status, version.
- `synthesize` — only supported/partially_supported enter; contradicted / does_not_establish / unresolved / blocked excluded **with explicit omissions**; conflicts (contradicting evidence, mixed stances, open disagreements) travel with the synthesis; conflict-without-alternative ⇒ **abstain** with eligible claims withheld.
- `register_profile` — calibration registry: 50+ samples, named benchmark, bounded abstention rate required.
- `route_workload` — prefers a valid calibrated profile, else deterministic-only with the reason named.
- `adjudicate` — deterministic first, independently diverse challenger else `ABSTAIN`/`UNRESOLVED`; incompatible probabilities never averaged.
- `DecisionStore` protocol + `MemoryDecisionStore` (copy-on-put/get, tenant-isolated).

**Runtime Decision Fabric contract** (per `docs/JEV_BUILD_POLICY.md:63-125`): `DecisionRequest → deterministic eligibility/policy → provider router → LocalDecisionProvider candidates → calibration/disagreement/abstention → DecisionResult → deterministic downstream policy`. Decision families required: `BOOLEAN, CHOICE, ORDINAL_SCORE, RANK, MULTI_LABEL, ABSTAIN/NO_FIT`.

**Known honest gap** (`docs/evidence/P09_EXIT.md:13-25`): the *measured* challenger half is **not** done — no Decider/SemIf/Laya-class adapter has been benchmarked, so **no challenger holds a default anywhere**. The framework exists; the measurement belongs to P15.

### 6.6 Authoritative artifact / document / slide data schemas — PARTIAL

**Three schema locations, three different things:**

| Layer | Location | Content |
|---|---|---|
| Contract schemas (JSON Schema, authoritative) | `contracts/v1/*.json` (23 schemas) + `contracts/v1/manifest.json` | Workspace, Principal, CapabilityGrant, SourceArtifact, SourceUnit, EvidenceSpan, SourceSnapshot, IngestionManifest, EvidenceBundle, Claim, Citation, Job, StageAttempt, ArtifactBaseline, DecisionRequest, DecisionResult, **Artifact**, **ArtifactRevision**, **NarrativeIR**, **DesignIR**, Plugin, Skill, ConnectorIdentity |
| Python runtime records | `servers/fastapi/gomrey/contracts.py` (127 lines) | Pydantic v2 mirrors of the contracts (`FrozenRecord` base, `extra="forbid"`, `frozen=True`; `Literal[0]`-style no-silent-loss invariants) |
| Presentation persistence | `servers/fastapi/models/sql/presentation.py`, `slide.py`, `template_v2.py` | Presenton-era tables (`PresentationModel`, `SlideModel`) — **not** contract-aligned; `SlideModel.ui`/`content`/`html_content` are unstructured JSON columns |

**Validation:** `scripts/validate-contracts.mjs` + `scripts/contracts.test.mjs` (root `npm test`).

**Canonical artifact IR — what it supports today:**

`contracts/v1/artifact.schema.json`:
```
artifact_id, tenant_id, workspace_id, artifact_type, title, current_revision, created_at, status
artifact_type ∈ {presentation, document, site, infographic, social, image, other}
status ∈ {draft, verifying, needs_repair, ready, published, archived}
```

`contracts/v1/narrative-ir.schema.json`:
```
narrative_id, artifact_id, revision, tenant_id, workspace_id, language, sections[]
section = {heading, text, claim_ids[]}          // additionalProperties:false
language pattern ^[a-z]{2}(-[A-Z]{2})?$
```

`contracts/v1/design-ir.schema.json`:
```
design_id, artifact_id, revision, tenant_id, workspace_id, layout (string), tokens{string→string}, components[], brand_skill_id
component = {component_id, component_type, citation_ids[]}   // additionalProperties:false
```

**Answers to the IR questions:**

- **Does the IR already support slides/cards/pages?** `Artifact.artifact_type` **enum already contains** `presentation, document, site, infographic, social, image, other` — i.e. the *vocabulary* exists. **But** `NarrativeIR.sections[]` is a flat list of `{heading, text, claim_ids}` — there is **no** nested slide/card/page node type, no per-section layout binding, no per-section media/asset references, and no ordering/index. `DesignIR.layout` is a **single string**, not a per-section layout plan. **So the IR does NOT yet support multi-slide/card/page structure.**
- **Citations?** Yes: `Citation` schema (`citation_id, tenant_id, workspace_id, source_id, source_unit_id, bundle_id, locator, retrieval_snapshot`), `NarrativeIR.section.claim_ids[]`, `DesignIR.component.citation_ids[]`.
- **Provenance?** Partially: `Artifact`/`ArtifactRevision` carry tenant/workspace/revision; `SourceArtifact`/`SourceUnit`/`EvidenceSpan`/`SourceSnapshot`/`IngestionManifest` carry full provenance. `gomrey/ir_provenance.py` (130 lines) implements the provenance-completeness + 100%-unit-coverage gate.

**Gaps in the IR:** no `ArtifactRevision` runtime; no artifact↔slide binding (PresentationModel/SlideModel are not contract records); no `design_ir` runtime producer; no `narrative_ir` runtime producer; no bridge from `EvidenceBundle` → `NarrativeIR` (the seam specified in `docs/ARCHITECTURE.md:357-362`).

---

## 7. DOCS / WEBSITE / VISUAL OUTPUT

Presenton was presentations + docs. **Current state:**

| Mode | Status | Evidence |
|---|---|---|
| **Presentation** | COMPLETE | §1, §2, §4, §5 above |
| **Document / report** | **PARTIAL — input-side only** | `servers/fastapi/services/documents_loader.py` (357 lines), `services/document_conversion_service.py` (89), `services/office_document_service.py` (171, DOCX/PPTX/XLSX/ODF text extraction), `services/liteparse_service.py` (469). These are **source ingestion** (document → text → deck prompt), not document authoring. |
| | | Frontend `app/(presentation-generator)/documents-preview/` (DocumentPreviewPage.tsx, MarkdownRenderer.tsx) — previews/edits *uploaded* documents as inputs. |
| | | **No document authoring/creation pipeline, no document artifact model, no DOCX export.** `Artifact.artifact_type` includes `document` but nothing produces one. |
| **Website / site** | **MISSING** | No route, no builder, no renderer, no `site` artifact producer. `Artifact.artifact_type` includes `site`; `docs/NO_GAPS_CHECKLIST.md:78` ("Website creation", P11/P14) is open. |
| **Social / visual cards** | **PARTIAL** | 27 infographic types (`utils/infographic_catalog.py:45-478`) usable **inside** slides; `insert/insert-elements.ts` + `InsertPalettePreview.tsx` insert them. **No standalone social-card artifact, no 1:1/9:16 story formats, no social export.** `Artifact.artifact_type` includes `social`; NO_GAPS row "Social/graphics" (L79) is open. |
| **Infographic** | PARTIAL | Slide-level infographics exist; no standalone infographic artifact or export path. |
| **Podcast / audio** | **MISSING** | MASTER_PLAN P10 lists it; no implementation. `services/mem0_*` are memory, not media. |
| **Mind map / timeline / quiz** | PARTIAL | Mind map + timeline exist as *infographic types*; no standalone artifact. |

**Next.js `/documents-preview` is an input surface, not an output studio.** This is the single largest divergence between what Presenton upstream advertises ("presentations and documents") and what this tree actually ships.

---

## 8. ENGINEERING CONTRACTS — exact gates

### 8.1 `docs/REVIEW_POLICY.md` — MANDATORY REVIEW STACK

**§1 — both required for non-trivial code changes (when the environment allows):**
1. **Alibaba Open Code Review (OCR)** — deterministic file/rule selection **plus** semantic review under the project review configuration.
2. **Jev / Jev-class build review** — typed decision review per `JEV_BUILD_POLICY.md`, TypeSafe Jev used when reproducible access is available and **explicitly identified**.

> "Neither tool alone grants merge authority. Deterministic tests, security/provenance review, exact-candidate CI, and unresolved-finding reconciliation remain required." (L13)

**§2 — non-evidence integrations.** CodeRabbit / Cubic / Qodo "do not satisfy Gomrey's mandatory review evidence"; their green status must not be cited as proof (L17-19).

**§3 — exact-candidate binding.** Every accepted review record must identify:
```
repository, base commit/tree, candidate commit/tree, reviewed file/range set,
review tool + exact version/model/provider, configuration/rule identity, findings,
coverage/exclusions, adjudication, unresolved material findings count
```
> "If HEAD moves materially, candidate-bound review evidence becomes stale and must be rerun or explicitly requalified." (L38)

**§4 — Jev non-fabrication.** If TypeSafe Jev is unavailable, record exactly:
```
JEV_NOT_EXECUTED
```
An open Jev-class system may be an extra comparator but must not be labeled TypeSafe Jev (L42-48).

**§5 — OCR non-fabrication.** If Alibaba OCR cannot execute, **record the exact blocker**. Do not substitute a different reviewer and call it OCR (L50-52).

**§6 — review independence.** Where risk warrants, require an independent substantive reviewer/model/human beyond the authoring agent. "The same model that generated a change cannot be treated as independent merely because it was prompted again." (L54-56)

**§7 — finding states.** Exactly one of:
```
FIXED
NOT_APPLICABLE
ACCEPTED_RISK (requires explicit authority and rationale)
BLOCKING
```
> "A material `BLOCKING` finding prevents merge. Silence is not PASS." (L69)

**§8 — evidence hierarchy (preferred proof order):**
1. deterministic test/runtime observation
2. exact static/security/provenance check
3. Alibaba OCR finding/coverage record
4. Jev typed decision review
5. independent semantic review
6. human/governance decision where required

> "Probabilistic review cannot override a deterministic failing test or policy violation." (L82)

**§9 — planning-only changes** may record `JEV_NOT_EXECUTED` / `OCR_NOT_EXECUTED`, but must not use that exception to authorize implementation the plan says requires the mandatory stack (L86).

**§10 — merge evidence.** Before merge the acceptance packet must state whether each required reviewer **actually executed on the exact final candidate**. After merge, post-merge verification binds the canonical merge commit/tree and any actually-triggered required workflows.

### 8.2 `docs/JEV_BUILD_POLICY.md` — TYPED DECISION CONTRACT

**§2 — build-time Jev requirement.** For non-trivial implementation grains the acceptance packet must include a Jev-class review when reproducible access exists. **Minimum build-time review questions (L21-30):**
- Does the change violate a declared invariant?
- Is donor code copied beyond the authorized/admitted slice?
- Is a deterministic check being replaced by an unnecessary model call?
- Is failure/retry/idempotency behavior complete?
- Is any source/page/chunk/artifact silently dropped?
- Does the change weaken provenance or citation precision?
- Does it add ambient network/filesystem/secret authority?
- Is an agent tool result structured and idempotent?
- Is the claimed test/evidence applicable to the exact candidate revision?
- Is there a simpler already-admitted implementation that should be reused instead?

**§2 — evidence requirement (L36-46).** Do not write "Jev passed" without recording:
```
review_tool
provider/model/tool version
request/schema digest
candidate commit/tree
reviewed file/range identity
decision outputs/probabilities
calibration semantics if exposed
abstentions/warnings
human/host adjudication
```
If TypeSafe Jev is unavailable → record `JEV_NOT_EXECUTED`; may use Decider/SemIf as an admitted comparator but must not impersonate TypeSafe Jev (L48).

**§3 — Jev does not replace other review.** Build acceptance requires, **in addition** to Jev-class output:
- deterministic tests and static checks;
- security/provenance review;
- exact diff/range review;
- CI on the exact candidate;
- where required, Alibaba Open Code Review and the project's other mandated review tools;
- benchmark evidence for performance/retrieval/model changes.

> "`JEV_PASS != MERGE_AUTHORITY`." (L61)

**§4 — runtime Decision Fabric (permanent product boundary):**
```
DecisionRequest -> deterministic eligibility/policy -> provider router
  -> one or more LocalDecisionProvider candidates
  -> calibration/disagreement/abstention handling
  -> DecisionResult -> deterministic downstream policy
```
> "Gomrey owns the contract. Providers are replaceable." (L77)

**§5 — DecisionRequest minimum fields (L90-106):** `request_id, workload_kind, state/context digest, bounded context, question, answer family, options/rubric, source/evidence refs, language, latency budget, memory/resource budget, privacy mode, provider allow/deny set, required calibration profile, consequence class, deadline/cancellation`.

**§6 — DecisionResult minimum fields (L111-124):** `provider identity, model identity and immutable revision, artifact/tokenizer/config digests, runtime identity, quantization/precision, request/schema digest, selected value, probability distribution or documented score semantics, calibration profile/revision, abstention/OOD signal, latency/device/resource metadata, truncation/degraded warnings, local/remote data-boundary assertion`.

**§7 — runtime provider hierarchy:** 1. deterministic rules (always available); 2. compact local Jev-class candidate (e.g. Laya-class); 3. Mapika Decider-class typed provider; 4. SemIf/direct-option-logit adapter over admitted local models; 5. larger challenger providers only where benchmarked gain justifies cost. "No single model is declared globally best." (L129-137)

**§8 — high-value workloads:** ingestion routing; retrieval; evidence verification (`SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED, DOES_NOT_ESTABLISH, UNRESOLVED`); artifact quality (slide crowded/not crowded, narrative redundancy, **layout candidate choice**, chart-type choice, brand-fit scoring, whether an artifact requires repair) (L139-183).

**§9 — authority boundary.** A DecisionResult **cannot** grant a permission, approve its own side effect, lower a deterministic privacy/security classification, mark evidence verified without supporting checks, mark tests/CI passed, declare a donor license/permission satisfied, publish externally, or silently convert unknown into known. Hard policy wins over model confidence (L186-203).

**§10 — calibration.** Every production provider/workload pair requires a measured calibration profile with benchmark identity, language/domain scope, sample size, Brier/ECE/NLL, risk/coverage curve, abstention precision/recall, unsafe-commit rate, distribution-shift limits, model/runtime/quantization identity. Without one, output may be used only as an uncalibrated ranking signal (L207-219).

**§11 — disagreement policy.** Deterministic checks first → inspect evidence sufficiency/truncation → optionally invoke an independently trained/provider-diverse challenger → else `ABSTAIN`, `UNRESOLVED`, or request more evidence. "Do not average incompatible probability semantics." (L221-230)

**§12 — local-first packaging.** Decision models are separate signed/content-addressed packs; not baked into the core binary; not silently downloaded during inference. Baseline correctness must not require a GPU or hosted endpoint (L232-238).

**§13 — promotion gate.** A provider becomes default for a workload only if it beats or matches the incumbent on Gomrey's frozen benchmark across task quality, calibration, abstention behaviour, latency/resource budget, language coverage, privacy/offline requirements, reproducibility (L240-252).

### 8.3 `docs/SOURCE_LEDGER.md` — obligations for imported third-party code

**§1 — adoption modes (L9-17):** `COPY_FULL_BASE`, `COPY_BOUNDED`, `ADAPT`, `DEPEND`, `WORKER`, `MODEL_PACK`, `REFERENCE`, `BENCHMARK_ONLY`, `DEFER`.

> "Before copied/adapted material lands, record exact revision, exact paths, controlling terms or separate permission basis, embedded/transitive material, notices, modifications, tests, security placement, update strategy, and exit strategy." (L19)

**§2 — Presenton is the primary executable foundation** (`COPY_FULL_BASE`, L23-41). Rule: *"import first, prove parity, then replace weak subsystems incrementally. Do not rewrite working presentation/editor/export paths simply to make them 'Gomrey native.'"* (L41)

**§2 — Gamma gate (L43-54):**
> "**no Gamma code is copied until an exact source snapshot, permission scope, third-party/asset boundary, and provenance record exist.** A public `gamma.app` URL is not a source archive."

**§7 — assets are separate identities from code (L194-207).** Code permission does **not** grant rights to fonts, icons, illustrations, photos, audio, video, templates, themes, stock assets, logos, trademarks, brand kits, or user-supplied source material. "A copied donor module may land while its bundled asset/model remains excluded." Model-pack admission requires exact artifact digests + separate code/runtime/weight/tokenizer/model-data/license identities. "Benchmark datasets are never assumed redistributable because their loader code is open source."

**§9 — the source admission record (L224-251) — every adopted slice must record:**
```
source_name
source_repository_or_archive
exact_revision_or_digest
source_paths
public_license
separate_permission_basis_if used
embedded/transitive code/assets/models
model_weight_tokenizer_runtime_rights
training_evaluation_dataset_rights
font_icon_media_template_brand_rights
generated_output_redistribution_or_publication_restrictions
notices/attribution
Gomrey_target_module
adoption_mode
why_reuse_beats_native
security/trust placement
network/filesystem/credential capabilities
tests/benchmarks
modifications
update strategy
rollback/exit strategy
review evidence
```
> "Permission expands what is possible; it does not remove provenance, third-party rights, security, benchmark, or exit requirements." (L253)

**§8 — founder-owned sibling donors (L209-222):** `TheHalfMoon/MedOrigin, Morize, Winds, Inercative, Orcel, kernux, Ascout, SpecGrain, Diffcipline`.

### 8.4 `docs/FIXTURE_POLICY.md` + `config/fixture-policy.json` — fixture rules

- Machine-readable contract: `config/fixture-policy.json`. Enforcement: `scripts/check-fixtures.mjs` (deterministic, **no network**).
- **Allowed:** synthetic fixtures generated by a checked-in script with a recorded seed; public benchmark inputs explicitly redistributable; explicitly licensed data with attribution preserved.
- **Prohibited:** real user secrets/API keys/tokens; private health or business data; donor credentials or production dumps; unlicensed scraped personal data.
- **Provenance:** each fixture directory documents source, license, creation date, and generator/acquisition method. Generated fixtures record the **exact generator script and seed**. Large corpora are referenced, not committed.
- **Scan roots:** `servers/fastapi/tests`, `servers/nextjs/tests`, `scripts`, `sbom`. **Excluded:** `docs/donors/`, `docs/evidence/`. One allowlisted path: `scripts/scan-secrets.test.mjs` (intentional synthetic strings).
- Companion guard: `scripts/scan-secrets.mjs` (repository-wide credential scan).
- `scripts/rebuild_notice_all.py` — NOTICE rebuild helper (presenton NOTICE blob is 1 274 338 bytes, must be preserved).

### 8.5 `docs/NO_GAPS_CHECKLIST.md` — the program coverage ledger

156 rows; every row must resolve to `NOT_APPLICABLE | PLANNED | IMPLEMENTED | QUALIFIED | BLOCKED` **with evidence**. "A missing row is not allowed to become an implicit assumption." (L6) Rows directly relevant to this mission:

| Row | Line | Phase | State in this tree |
|---|---|---|---|
| Presentation generation | 73 | P01/P11 | IMPLEMENTED (Presenton) |
| Presentation editing (text/media/chart/layout, undo/history) | 74 | P01/P11 | PARTIAL (undo ✅, history ❌) |
| PPTX export (editable output, fonts/assets, fidelity) | 75 | P01/P11 | IMPLEMENTED but owned by external package |
| PDF/image export | 76 | P01/P11 | PARTIAL (no user-facing image export) |
| Document/report creation (editable semantic content, citations) | 77 | P11 | NOT STARTED |
| Website creation (responsive output, assets, publish path) | 78 | P11/P14 | NOT STARTED |
| Social/graphics (reusable artifact compiler, export formats) | 79 | P11 | NOT STARTED (infographics only) |
| Narrative IR | 80 | P11 | CONTRACT ONLY |
| Design IR | 81 | P11 | CONTRACT ONLY |
| Brand system (logos/fonts/colors/themes, rights, brand extraction/skills) | 82 | P11/P13 | NOT STARTED |
| Layout QA (overflow, clipping, contrast, density, missing fonts/assets) | 83 | P11/P15 | PARTIAL (overflow only, `smart_slide_layout.py`) |
| Accessibility (alt text, contrast, reading order, keyboard/UI) | 84 | P11/P14/P15 | NOT STARTED |
| Localization/i18n (locale-safe formatting, RTL, Arabic first-class) | 85 | P02/P10/P15 | NOT STARTED (en only) |
| Studio outputs (report, deck, doc, infographic, audio/podcast…) | 72 | P10/P11 | deck only |
| Gamma donor (exact authorized archive, selective module admission, third-party boundary) | 13 | P11 | OPEN — **SOURCE NOT OBTAINED** |
| Benchmark framework / RAG quality / competitive evaluation | 121-126 | P15 | NOT STARTED |

### 8.6 `docs/MASTER_PLAN.md` — phase ladder and exit rules

Ladder (L38-56): `P00 → P01 → P02 → P03 → P04 → P05 → P06 → P07 → P08 → P09 → P10 → P11 → P12 → P13 → P14 → P15 → P16`.

**§2 governing execution rules (L25-36):**
1. Reuse before rebuild (native code requires a reason when an equivalent mature donor implementation exists).
2. Do not blindly concatenate repositories — donor code admitted behind Gomrey contracts.
3. Exact provenance.
4. **No fabricated evidence.**
5. **Jev in the build loop.**
6. Agent-first parity (idempotency, typed results, permissions).
7. **No silent loss.**
8. **Confidence is not authority.**
9. Local/self-hostable is first-class.
10. **Promotion by benchmark.**

**P11 — Creation compiler and Gamma selective absorption (L406-441):** work = Narrative IR; Design IR; evidence-to-claim binding; skill/brand-driven generation; editable charts/tables/text/images; **layout/overflow verifier**; artifact transform between presentation/document/site/social/infographic; selective Gamma module absorption **only after exact authorized source admission and direct superiority test**.

> **Gamma rule (L423-436):** "Do not perform a blind Gamma transplant. For each candidate module compare: quality; dependencies; architectural fit; security; maintenance cost; embedded third-party assets/rights; migration risk; Presenton/Gomrey incumbent. **Copy the better implementation, not the more famous one.**"

**Final merge rule (L615-619 area):** security/provenance review passes; Jev-class review evidence recorded when required/available; no unresolved material review findings.

### 8.7 `docs/ARCHITECTURE.md` — the target IR join

§16 (L353-371) is the specification the mission should target:
```
EvidenceBundle -> Narrative IR -> Artifact intent -> Design IR / layout plan -> Renderer/exporter
  -> presentation | document/report | website | infographic/social | images/PDF/PPTX/etc.
```
> "Generated visual artifacts retain editable semantic elements where the target format allows it. The system must not flatten editable charts/text to images merely for implementation convenience unless the user explicitly chooses a rasterized export." (L369-371)

§17 (L372-382) — artifact revision model: stable identities, optimistic expected-revision checks, idempotent mutation keys, structured diffs, undo/history, branch/merge, citations versioned with the content they support.

### 8.8 Branch naming convention — OBSERVED, NOT DOCUMENTED

`CONTRIBUTING.md` is **stale Presenton text** (L1-14 still says "Contributing to Presenton"; L51-58 suggests `feature/…`, `fix/…`, `docs/…`; L129 says "Changes are **inside `electron/`**" — all wrong for this repo). **Do not follow it.**

The **actual, observed** convention across 60+ remote branches is:
```
p<NN>/g<M>-<kebab-case-slug>
```
Examples: `p03/g1-core-contracts`, `p03/g2-storage-seams`, `p04/g3-budgets-reconciliation`, `p05/g4-parser-boundary`, `p06/g3-ocr-workers`, `p07/g2-media-pipeline`, `p08/g1-retrieval-pipeline`, `p09/g3-decision-graph`, `p09/exit-closeout`, `p01/presenton-base-import`, `p02/g4-engineering-baseline`.

Per-issue work branches in the current mission use: `feature/rea/nextslide-gamma-wave1`.

**Recommendation:** for this mission use `p11/g<n>-<slug>` (or `p11/rea-nextslide-gamma-wave1`) — but this is **not documented anywhere**, so it should be confirmed with the owner, not inferred silently.

### 8.9 How docs are updated — OBSERVED

Per-grain evidence files live in `docs/evidence/` (36 files), named `<PHASE>_<GRAIN>_<SLUG>.md`, each recording: parent issue, canonical base SHA, goal, scope (file-by-file with line ranges), out-of-scope, local qualification (exact commands + pass counts), review findings, unresolved material findings count, and an "exact-head requirement" stating that local evidence alone is insufficient and the committed candidate must pass full GitHub Actions before merge. Phase exit files: `P05_EXIT.md`, `P06_EXIT.md`, `P07_EXIT.md`, `P08_EXIT.md`, `P09_EXIT.md`.

Contract/doc policy changes are expected to also touch `docs/MASTER_PLAN.md`, `docs/NO_GAPS_CHECKLIST.md`, `docs/ARCHITECTURE.md`, `docs/SOURCE_LEDGER.md`, and `contracts/v1/` (with `manifest.json` updated and `scripts/validate-contracts.mjs` passing).

---

## 9. TEST LANDSCAPE

### 9.1 Root repository tooling — COMPLETE

`npm test` (root) = `npm run test:template-converter && node --test` over **16** files:
```
scripts/package-metadata.test.mjs
scripts/product-identity.test.mjs
scripts/desktop-release-identity.test.mjs
scripts/desktop-store-artwork.test.mjs
scripts/compatibility-aliases.test.mjs
scripts/start-config-permissions.test.mjs
scripts/sync-presentation-export.test.mjs
scripts/user-config-env.test.mjs
scripts/platform-support.test.mjs
scripts/scan-secrets.test.mjs
scripts/generate-sbom.test.mjs
scripts/check-dependency-audit.test.mjs
scripts/check-fixtures.test.mjs
scripts/release-baseline.test.mjs
scripts/contracts.test.mjs
(+ scripts/convert-template.test.mjs, scripts/convert-presentation-template.test.mjs via test:template-converter)
```
Other root scripts: `npm run convert:template`, `npm run convert:presentation-template`, `npm run sync:presentation-export`, `npm run sync:presentation-export:force`, `npm run check:presentation-export`.

### 9.2 FastAPI — COMPLETE

- **125** test files under `servers/fastapi/tests/` (`unit/`, `integration/`, `edge_cases/`, `regression/`, `mocks/`, plus 40 top-level `test_gomrey_*.py`).
- Runner: **pytest** via **uv** (dev group: `pytest>=9.0.3`, `pytest-cov>=7.1.0`; `pyproject.toml [tool.pytest.ini_options] testpaths = ["tests"]`).
- Command (CI-identical, `.github/workflows/test-all.yml:74-75`, `test-local.sh:40-50`):
```bash
cd servers/fastapi
uv sync --locked --dev
mkdir -p /tmp/presenton-tests/app-data /tmp/presenton-tests/temp
APP_DATA_DIRECTORY=/tmp/presenton-tests/app-data \
TEMP_DIRECTORY=/tmp/presenton-tests/temp \
DATABASE_URL=sqlite+aiosqlite:////tmp/presenton-tests/test.db \
DISABLE_ANONYMOUS_TRACKING=true \
DISABLE_IMAGE_GENERATION=true \
uv run --locked python -m pytest --verbose --tb=short
```
- **Baseline measurement** (`evidence/BASELINE_GATE_RUN.md:20`): **1 125 passed**, 10 warnings, exit 0.
- Notable suites for this mission: `tests/test_gomrey_{retrieval_pipeline,citations,evidence_bundle,claims,verification,decisions,ir_provenance,contracts,seams}.py`; `tests/unit/test_generate_{presentation_outlines,presentation_structure,slide_content,web_search_query}.py`; `tests/unit/test_template_api.py`, `test_template_theme.py`, `test_default_templates.py`; `tests/unit/test_chat_service_template_v2.py`, `test_chat_llm_tools.py`; `tests/integration/test_presentation_generation_flow.py`; `tests/regression/test_outline_generation_snapshots.py`; `tests/test_pptx_font_utils.py`.

### 9.3 Next.js — COMPLETE

- `npm test` = `node --test` over `servers/nextjs/tests/**` (**20** files): `backend-connectivity`, `clipboard`, `community-config`, `community-error-handling`, `flow-layout-text-sizing`, `gomrey-internal-identity`, `gomrey-persisted-protocol`, `infographic-rendering`, `latex-html-text-rendering`, `pdf-maker-export-layout`, `presentation-autosave`, `runtime-provider-config`, `template-preview-density`, `template-theme-infographics`, `template-v2-canonical-model-compatibility.ts`, `template-v2-component-bounds`, `template-v2-json-to-html-metadata`, `template-v2-renderer-fields`, `vector-arrow-rendering`, plus root `local-font-loading-validation.test.mjs`.
- **Baseline:** **73 pass / 0 fail** (`evidence/BASELINE_GATE_RUN.md:21`).
- Lint: `npm run lint` (ESLint 9, `eslint.config.mjs`).
- Typecheck (editor): `./node_modules/.bin/tsc --noEmit --incremental false` (per `components/slide-editor/README.md` "Testing and Verification Commands").
- Production build: `NEXT_PUBLIC_FAST_API=http://localhost:8000 NEXT_PUBLIC_URL=http://localhost:3000 npm run build`.
- **Cypress component tests:** `npx cypress run --component --browser electron` — `cypress.config.ts` (Next/webpack), specs: `components/ui/switch.cy.tsx`, `components/ui/dialog.cy.tsx`, `components/SmartHtmlSelectionOverlay.cy.tsx`. **No committed Playwright specs** — `servers/nextjs/.playwright-cli/` is local scratch only.

### 9.4 Electron — COMPLETE

`cd electron && npm ci --ignore-scripts && npm run typecheck && npm run build:ts && npm run check:main-no-undef && npm run test:path-migration` (`.github/workflows/test-all.yml:113-145`; baseline 11 pass).

### 9.5 CI gates — `.github/workflows/test-all.yml` (triggers: push to `main`, PR to `main`, manual)

| Job | Gates |
|---|---|
| `test-repository-tools` | `npm ci` → `npm test` → `npm run sync:presentation-export` → `npm run check:presentation-export` |
| `test-fastapi` | `uv sync --locked --dev` → `uv run --locked python -m pytest --verbose --tb=short` |
| `test-nextjs` | `npm ci` → `npm test` → `npm run lint` → `npm run build` → `npx cypress run --component --browser electron` |
| `test-electron` | `npm run typecheck`, `npm run build:ts`, `npm run check:main-no-def`, `npm run test:path-migration` |
| `g4-baseline` | `npm test` → `node scripts/check-platform-support.mjs` → `node scripts/validate-release-config.mjs` → `node scripts/generate-release-manifest.mjs --check-only` → `node scripts/check-fixtures.mjs` → `node scripts/generate-sbom.mjs` |
| `security-baseline` | `node scripts/scan-secrets.mjs` → `npm audit` (root/electron/nextjs) via `scripts/check-dependency-audit.mjs` → `uv sync --locked --dev` → `pip-audit --desc --local` |
| `sbom-baseline` | `node scripts/generate-sbom.mjs` → `node scripts/generate-release-manifest.mjs > dist/release-manifest.json` → `--check-only` |
| `qualify-windows` / `qualify-macos` | `npm test` → `node scripts/check-platform-support.mjs` → `node scripts/validate-release-config.mjs` |

> `.github/workflows/README.md`: "No test step is allowed to fail silently."

### 9.6 Which tests are the acceptance gates for a new module

| New module surface | Gate(s) |
|---|---|
| Any FastAPI module | `uv run --locked python -m pytest --verbose --tb=short` (full suite) |
| Any Next.js module | `npm test` + `npm run lint` + `npm run build` + Cypress component run |
| New contract schema | `npm test` (`scripts/contracts.test.mjs`) + `node scripts/validate-contracts.mjs` + `scripts/validate-contracts.mjs` keyword subset |
| New donor code | `node scripts/scan-secrets.mjs` + `node scripts/check-fixtures.mjs` + `npm run generate-sbom` + `npm run check:presentation-export` (if export paths touched) |
| New template / template JSON | `npm run test:template-converter` + `scripts/convert-template.test.mjs` + FastAPI `test_template_api.py` |
| New editor component | `npm test` (node --test) + `tsc --noEmit --incremental false` + Cypress component spec |
| New export path | `servers/nextjs/tests/pdf-maker-export-layout.test.mjs` + FastAPI export tests |

---

## 10. GAPS FOR THE MISSION

### 10.1 What already exists (do NOT rebuild)

| Capability | Owner |
|---|---|
| LLM provider abstraction (15 providers) | `servers/fastapi/utils/llm_provider.py` |
| Outline → structure → slide-content planning | `servers/fastapi/utils/llm_calls/*` |
| Smart HTML deck generation + streaming | `servers/fastapi/utils/llm_calls/generate_smart_presentation.py` |
| 16 bundled templates / 400+ layouts | `templates/*/template.json` |
| Template-V2 schema + certified generation | `servers/fastapi/templates/v2/**` |
| Konva slide editor (text/table/chart/image/icon/shape/line/flex/grid) | `servers/nextjs/components/slide-editor/**` |
| Undo/redo, autosave, clipboard, layer order, ungroup | same |
| PPTX import (python-pptx), PPTX font utils | `servers/fastapi/templates/pptx_font_utils.py`, `services/export_task_service.py:690` |
| PPTX/PDF export chain | `scripts/sync-presentation-export.cjs` → `presentation-export/` → `@presenton/export-core` |
| HTML/JSON→image rendering | `services/export_task_service.py:524-689` |
| 27 infographic types | `servers/fastapi/utils/infographic_catalog.py` |
| AI chat editing with 25+ tools | `servers/fastapi/services/chat/tools.py` |
| MCP server (REST + MCP parity) | `servers/fastapi/mcp_server.py` |
| Deterministic retrieval/citation/evidence/claim/verification/decision fabric | `servers/fastapi/gomrey/{retrieval_pipeline,citations,evidence_bundle,claims,verification,decisions}.py` |
| Contract schemas (23) + Pydantic mirrors | `contracts/v1/`, `servers/fastapi/gomrey/contracts.py` |
| Source IR provenance + unit accounting | `servers/fastapi/gomrey/{ir_provenance,accounting}.py` |
| Hostile-input gateway, file boundary, remote gateway | `servers/fastapi/gomrey/{gateway,file_boundary,remote_gateway,parser_boundary}.py` |
| Job kernel + budgets + idempotency | `servers/fastapi/gomrey/{jobs,budgets}.py` |

### 10.2 Gaps a Presentation / Document / Website / AI-Editing / Export / Design-System studio would need

**Presentation Studio**
1. **Evidence-bound generation** — `EvidenceBundle → NarrativeIR → slide content`. No runtime producer of `NarrativeIR` exists. *File:* new `servers/fastapi/gomrey/narrative.py` + hook in `utils/llm_calls/generate_presentation_outlines.py`.
2. **Multi-slide IR structure** — `NarrativeIR.sections[]` has no slide/node nesting, no per-section layout binding, no asset refs. *File:* `contracts/v1/narrative-ir.schema.json`.
3. **Layout QA beyond overflow** — contrast, density, missing-font/asset checks, reading order. Only overflow exists (`utils/smart_slide_layout.py`). *File:* `servers/fastapi/utils/smart_slide_layout.py` + new `layout_qa.py`.
4. **Deterministic layout selection with fallback** — currently a single LLM call returning indices. *File:* `servers/fastapi/utils/llm_calls/generate_presentation_structure.py`.
5. **Artifact/revision runtime** — `Artifact`, `ArtifactRevision`, `ArtifactBaseline` have no runtime store. *File:* `servers/fastapi/gomrey/contracts.py` + new artifact service.

**Document Studio**
6. **Document authoring pipeline** — none. Only source ingestion. *File:* new `servers/fastapi/services/document_generation_service.py` + new route.
7. **Document artifact producer + DOCX export** — `Artifact.artifact_type="document"` is unenumerated in code. *File:* new service + `servers/fastapi/utils/export_utils.py` (currently `Literal["pptx","pdf"]`).
8. **Markdown/document renderer with citation anchors** — `MarkdownRenderer.tsx` exists only as an input preview. *File:* `servers/nextjs/app/(presentation-generator)/documents-preview/components/MarkdownRenderer.tsx`.

**Website Studio**
9. **No website builder at all** — no route, no IR, no renderer, no responsive layout engine, no publish path. *File:* entire new area under `servers/nextjs/app/(presentation-generator)/website/` + `servers/fastapi/gomrey/site.py`.
10. **Publish path** — NO_GAPS row "Publishing" (L105) is P14, unstarted. *File:* new.

**AI Editing**
11. **AI editing of Standard-mode decks is template-scoped** — `services/chat/tools.py` tools operate on template V2 slides; no AI edit that operates on the *deck* (reorder, retitle, restyle, regenerate a slide with a different layout). *File:* `servers/fastapi/services/chat/tools.py`.
12. **No conversational artifact-level AI** — `Chat.tsx` is per-presentation; no notebook/research chat. *File:* `servers/nextjs/app/(presentation-generator)/presentation/components/Chat.tsx`.
13. **Editability verification after AI edit** — no post-edit repair loop. `docs/NO_GAPS_CHECKLIST.md:83` "Layout QA" + ARCHITECTURE §24 "Verification and repair loop". *File:* new.
14. **Design decisions via the Decision Fabric** — `JEV_BUILD_POLICY.md:173-182` lists "slide crowded/not crowded, layout candidate choice, chart-type choice, brand-fit scoring" as decision workloads. None implemented. *File:* new provider adapters under `servers/fastapi/gomrey/`.

**Export Engine**
15. **Export fidelity regression suite** — no golden PPTX/PDF comparison, no export→re-import round trip. *File:* new `servers/fastapi/tests/` + `servers/nextjs/tests/`.
16. **Image export endpoint** — internal only; `Literal["pptx","pdf"]` blocks PNG/JPEG/WebP. *File:* `servers/fastapi/utils/export_utils.py:46`, `models/generate_presentation_request.py:41`.
17. **PPTX import fidelity is exercised but not export round-tripped.** *File:* `servers/fastapi/services/export_task_service.py`.
18. **Accessibility in export** — alt text, reading order, contrast. *File:* `servers/nextjs/lib/template-v2-json-to-html.ts` + export-core configuration.

**Design System**
19. **Brand kit system** — logos, brand fonts, brand colors, brand extraction skill, rights metadata. Only `DesignIR.brand_skill_id` (a string) exists. *File:* new `servers/fastapi/gomrey/brand.py` + `contracts/v1/design-ir.schema.json`.
20. **Theme/style presets** — only per-template derived themes; no curated named presets, no design-token scale. *File:* `servers/fastapi/templates/v2/theme.py` (extend) + `servers/nextjs/lib/template-theme.ts`.
21. **Typographic scale / spacing scale / baseline grid for slide content** — raw pixel values only. *File:* `servers/nextjs/components/slide-editor/model/design-variables.ts` + `text/text-line-height.ts`.
22. **Token-driven theming across renderers** — Konva renderer, DOM preview renderer and HTML export renderer each read colours independently; a token change must be applied three times. *File:* `servers/nextjs/components/slide-editor/surface/nodes.tsx`, `app/(presentation-generator)/custom-template/components/EachSlide/TemplateV2LayoutPreview.tsx`, `servers/nextjs/lib/template-v2-json-to-html.ts`.
23. **Localization / RTL / Arabic-first authoring** — NO_GAPS row L85 (P02/P10/P15). *File:* new.

**Cross-cutting**
24. **Dense/lexical/visual retrieval is a framework with no index.** *File:* `servers/fastapi/gomrey/retrieval_pipeline.py` (provider side missing).
25. **No challenger decision provider has been benchmarked** — `docs/evidence/P09_EXIT.md:13-25`. *File:* new provider adapters.
26. **No artifact versioning/history runtime.** *File:* `servers/fastapi/gomrey/contracts.py`.
27. **Root `layouts.json` is an orphan 252 KB artifact** — should be moved or removed; do not treat as source of truth.

---

## GAP TABLE FOR MISSION STUDIOS

| # | Required capability | State | Primary file(s) that must change | Notes |
|---|---|---|---|---|
| 1 | Evidence-bound narrative planning (`EvidenceBundle → NarrativeIR`) | **MISSING** | new `servers/fastapi/gomrey/narrative.py`; hook `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py` | P08/P09 fabric exists but is unwired |
| 2 | Multi-slide/card/page IR nodes | **MISSING** | `contracts/v1/narrative-ir.schema.json`, `contracts/v1/design-ir.schema.json` | Current `sections[]` is flat |
| 3 | Design IR runtime producer + per-section layout plan | **MISSING** | new `servers/fastapi/gomrey/design.py`; `contracts/v1/design-ir.schema.json` (`layout` is a single string) | |
| 4 | Artifact + ArtifactRevision runtime store (history, diffs, idempotency) | **MISSING** | `servers/fastapi/gomrey/contracts.py`; new store impl | Schema exists, runtime does not |
| 5 | Layout QA (contrast, density, reading order, missing assets/fonts) | **PARTIAL** | `servers/fastapi/utils/smart_slide_layout.py` (+ new module) | Overflow/clipping only |
| 6 | Deterministic layout selection + confidence fallback | **PARTIAL** | `servers/fastapi/utils/llm_calls/generate_presentation_structure.py` | Single LLM index pick |
| 7 | Brand-kit system (logos, brand fonts/colors, extraction, rights) | **MISSING** | new `servers/fastapi/gomrey/brand.py`; `contracts/v1/design-ir.schema.json` | Only `brand_skill_id` string |
| 8 | Named theme/style presets | **MISSING** | `servers/fastapi/templates/v2/theme.py`; `servers/nextjs/lib/template-theme.ts` | Templates derive own themes only |
| 9 | Slide typographic/spacing scale + baseline grid | **MISSING** | `servers/nextjs/components/slide-editor/text/*`, `model/design-variables.ts` | Raw pixels only |
| 10 | Single token source across Konva / DOM preview / HTML export | **PARTIAL** | `components/slide-editor/surface/nodes.tsx`; `custom-template/components/EachSlide/TemplateV2LayoutPreview.tsx`; `lib/template-v2-json-to-html.ts` | 3 parallel readers |
| 11 | Document authoring pipeline + DOCX export | **MISSING** | new `servers/fastapi/services/document_generation_service.py`; `servers/fastapi/utils/export_utils.py:46` | Ingestion only today |
| 12 | Website builder (routes, IR, responsive renderer, publish) | **MISSING** | new `servers/nextjs/app/(presentation-generator)/website/`; new backend service | Nothing exists |
| 13 | Standalone social/visual-card artifact + formats | **PARTIAL** | `servers/fastapi/utils/infographic_catalog.py`; `servers/nextjs/components/slide-editor/insert/insert-elements.ts` | Infographics are slide-internal |
| 14 | Deck-level AI editing (reorder, retitle, restyle, regenerate slide) | **PARTIAL** | `servers/fastapi/services/chat/tools.py` | Per-slide only |
| 15 | AI edit post-repair / layout verification loop | **MISSING** | new repair service; `docs/ARCHITECTURE.md` §24 | |
| 16 | Decision-fabric providers for artifact quality (crowding, layout, chart-type, brand-fit) | **MISSING** | new adapters under `servers/fastapi/gomrey/`; `docs/JEV_BUILD_POLICY.md` §8 | |
| 17 | Dense / lexical / visual retrieval index | **MISSING** (framework only) | `servers/fastapi/gomrey/retrieval_pipeline.py` provider side | |
| 18 | Benchmarked challenger decision provider | **MISSING** | `docs/evidence/P09_EXIT.md` TODO | Deferred to P15 by canonical plan |
| 19 | Export fidelity regression suite + export→import round trip | **MISSING** | new `servers/fastapi/tests/`, `servers/nextjs/tests/` | |
| 20 | User-facing image export (PNG/JPEG/WebP) | **MISSING** | `servers/fastapi/utils/export_utils.py:46`; `models/generate_presentation_request.py:41,64` | `Literal["pptx","pdf"]` |
| 21 | Accessibility in authoring + export (alt text, contrast, reading order, keyboard) | **MISSING** | `servers/nextjs/lib/template-v2-json-to-html.ts`; editor toolbars | NO_GAPS L84 |
| 22 | Localization / RTL / Arabic-first authoring | **MISSING** | new i18n layer | NO_GAPS L85 |
| 23 | Benchmark framework for studio outputs (P15 arena) | **MISSING** | new under `tests/` | NO_GAPS L121-126 |
| 24 | Document→website / site artifact transform | **MISSING** | new | ARCHITECTURE §16 |
| 25 | Orphan root `layouts.json` cleanup | **MISSING** (hygiene) | `/layouts.json` | Not referenced by any code |
| 26 | LLM provider seam | **EXISTING** | `servers/fastapi/utils/llm_provider.py:47-193` | Do not add a parallel provider registry |
| 27 | Template + layout corpus | **EXISTING** | `templates/*/template.json` (16 templates) | |
| 28 | Konva slide editor | **EXISTING** | `servers/nextjs/components/slide-editor/**` (73 files) | |
| 29 | PPTX import (python-pptx) | **EXISTING** | `servers/fastapi/templates/pptx_font_utils.py`; `services/export_task_service.py:690` | Stronger than donor extractor |
| 30 | PPTX/PDF export chain | **EXISTING** (external pkg) | `scripts/sync-presentation-export.cjs`; `servers/nextjs/lib/run-bundled-presentation-export.ts` | `presentation-export/` not committed |
| 31 | Citation / evidence / claim / verification fabric | **EXISTING** | `servers/fastapi/gomrey/{citations,evidence_bundle,claims,verification,decisions}.py` | Deterministic, tested, unwired |
| 32 | Contract schemas + validators | **EXISTING** | `contracts/v1/*.json` (23) + `scripts/validate-contracts.mjs` | |
| 33 | Theme derivation from template | **EXISTING** | `servers/fastapi/templates/v2/theme.py` | |
| 34 | Infographic catalogue (27 types) | **EXISTING** | `servers/fastapi/utils/infographic_catalog.py:45-478` | |
| 35 | MCP server + REST parity | **EXISTING** | `servers/fastapi/mcp_server.py` | |
| 36 | Undo/redo + autosave | **EXISTING** | `components/slide-editor/surface/TemplateV2KonvaSlide.tsx:423-1290`; `store/slices/undoRedoSlice.ts`; `presentation/hooks/useAutoSave.tsx` | |
| 37 | Layout selection for smart HTML deck + safety QA | **EXISTING** | `utils/llm_calls/generate_smart_presentation.py`; `utils/smart_slide_layout.py` | |

---

## 11. INTEGRATION WARNINGS FOR THE DONOR WAVES

1. **No parallel slide-rendering stack.** Gomrey has a Konva editor + a DOM preview renderer + an HTML export renderer, all fed by Template-V2 JSON. A donor single-file HTML deck engine is a *fourth* path unless it demonstrates a capability gap (e.g. animations, presenter mode) — and even then it must emit Template-V2 JSON or the export chain will not pick it up.
2. **No second PPTX exporter without a bounded differential.** `@presenton/export-core` is the only supported exporter; the donor's PptxGenJS script would need a measurable fidelity/editable-text delta against it.
3. **No donor `extract-pptx.py`.** `services/export_task_service.py:690` + `templates/pptx_font_utils.py` already exceed it.
4. **Do not invent a second provider registry.** Extend `utils/llm_provider.py` / `utils/llm_config.py`; `services/provider_settings.py` already persists per-user provider config.
5. **Preserve the Presenton NOTICE blob** (`ba5df534c4549ed7459a34667a506baa5cbd5fea`, 1 274 338 bytes) per `docs/SOURCE_LEDGER.md:30`; `scripts/rebuild_notice_all.py` is the rebuild helper.
6. **Gamma code is still gated.** `docs/SOURCE_LEDGER.md:54` — no Gamma code may be copied until an exact source snapshot, permission scope, third-party/asset boundary and provenance record exist. `research/rea/2026-10-22-nextslide-gamma/SOURCES.md:117-126` records Gamma as `SOURCE_NOT_AVAILABLE`; the wave proceeds as **qualified equivalent implementation**, never parity.
7. **NextSlide MIT notice obligation.** Per `SOURCES.md:48-79`, `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56` is MIT © 2026 Danish Rafie Ekaputra; any copied/adapted file needs a §9 admission record and a NOTICE/attribution entry.
8. **Every copied/adapted slice needs the §9 admission record** (`docs/SOURCE_LEDGER.md:224-251`) — 23 fields.
9. **Fixtures must satisfy `config/fixture-policy.json`** — synthetic-with-seed only, provenance header per directory, `scripts/check-fixtures.mjs` + `scripts/scan-secrets.mjs` must stay green.
10. **Watch the three-way renderer drift.** Any new element type must be added in *three* places (Konva surface, DOM preview, HTML export) or export parity silently breaks — this is the single most common failure mode documented in `components/slide-editor/README.md` ("Preview/export differs from editor").
11. **The evidence fabric is not connected.** Highest-leverage P11 work is the `EvidenceBundle → NarrativeIR → DesignIR` join, not new renderers.
12. **`PRESENTATION_GENERATION_MODE` already gates two UX paths.** Any new studio mode needs an explicit decision about whether it is a third mode, a template variant, or a post-processing stage — and must be reflected in `docs/presentation-generation-modes.md` and `servers/nextjs/utils/presentationGenerationMode.ts`.

---

## 12. METHOD NOTE

Every claim in this survey is anchored to a file path (and, where meaningful, a line range) inside `/Users/abdulazizalsh/work/Gomrey` at SHA `5f299a7a6174ad3a1180f827778db5f4400a4d71`. No source file was modified. Test counts are quoted from the measured baseline in `research/rea/2026-10-22-nextslide-gamma/evidence/BASELINE_GATE_RUN.md` (run 2026-10-22 on the same branch) rather than re-run during this survey.
