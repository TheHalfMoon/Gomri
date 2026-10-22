# GAMMA — Capability Reconnaissance

**Target:** `https://gamma.app/` (product) + `https://developers.gamma.app/` (developer docs)
**Recon date:** 2026-10-22 (UTC session 03:39:02Z → 03:45:08Z)
**Company:** Gamma Tech, Inc. (per `api-evangelist/gammaapp` repo description). SOC 2 Type II compliant (stated on the pricing page).
**Headline:** Gamma exposes the **most completely documented public API + MCP server of any AI-presentation product**, with **21 MCP tools** and **18 REST endpoints** across two engine generations ("Gamma 5" agent endpoints and "Classic" endpoints). Its internal product source is **NOT** open — only peripheral integrations and one internal QA tool leak into the public GitHub org.

---

## 1. Top-line capability inventory by area

Every row is evidence-tagged. `OD` = OFFICIAL_DOCUMENTATION, `OU` = OBSERVED_UI, `AR` = API_RESPONSE, `INF` = INFERENCE, `UNK` = UNKNOWN, `BLK` = BLOCKED.

### 1.1 Generation — formats

| Capability | Evidence | Tag |
|---|---|---|
| **Presentation** format | `format: "presentation"` in the OpenAPI `Generation.format` enum (`document, presentation, social, webpage`). Marketing tab "PRESENTATIONS — Decks that wow the room." | OD + OU |
| **Document** format | same enum; marketing tab "DOCUMENTS — Docs that draw you in. One-pagers to white papers." | OD + OU |
| **Social** (carousel/visual) format | same enum; marketing tab "SOCIAL MEDIA VISUALS — Carousels and graphics sized for every platform, in your brand." | OD + OU |
| **Webpage** format | same enum, but **Classic endpoints only** — "`webpage` is not supported by the agent engine and is rejected" (`POST /v1.0/agent/generations`). Marketing tab "WEBSITES — A live site in minutes. Prompt it, publish it, share the link." | OD + OU |
| **AI-generated image** as a standalone artifact | `POST /v1.0/images` → `POST /v1.0/images` + `GET /v1.0/images/{id}`; MCP `generate_image` + `get_image_generation_status`. Marketing tab "AI-GENERATED IMAGES — The best image models, built in." | OD + OU |
| **Multi-page Gamma / microsite** (several pages under one URL, one request) | `pages[]` array on `POST /v1.0/generations` — "Up to 50 pages per request", each with its own `gammaId`, `gammaUrl`, `path` slug, deep link; `publish: true` publishes it as a live site on a Gamma-generated subdomain. MCP tool `generate_multi_page_gamma` (1–50 pages). Doc use-case: "sales rooms, proposal sites, onboarding portals, and microsites" | OD |
| **Card-based unit of content** | The whole model is "cards" — `numCards`, `cardSplit` (`auto` \| `inputTextBreaks`), `cardOptions.dimensions` (10 values: `16x9, 4x3, fluid, letter, a4, pageless, 1x1, 4x5, 9x16`). Per-format defaults differ: presentation/document/webpage = `fluid`, social = `1x1` | OD |
| **Text density control** | `textOptions.amount` ∈ `brief, medium, detailed, extensive`; plus `tone`, `audience`, `language` | OD |
| **Text handling mode** | `textMode` ∈ `generate` \| `condense` \| `preserve`. UI equivalents documented as "Generate / Condense / Preserve" on the Classic outline page, with a lock icon on Preserve | OD |
| **Card count cap** | `numCards` — "capped at the plan's maximum (**10 on free plans, 100 on paid plans**); a higher value is rejected with 400. Within the cap it is a soft target: the agent may deviate by a card or two, and the result is not validated against it." Marketing/pricing confirms Free = 10 slides/prompt, Plus+ = 100 | OD + OU |
| **74 output languages** | Full BCP-47-ish list from the OpenAPI `TextOptions.language` enum (af, ar-sa, en-gb, en-in, es-419, es-mx, es-es, ja, ja-da, pt-br, pt-pt, zh-cn, zh-tw, …) — independently corroborated by `apiEnums.ts` `LANGUAGE_OPTIONS` | OD |

### 1.2 AI editing / conversational iteration

| Capability | Evidence | Tag |
|---|---|---|
| **Agent-first creation ("Gamma 5")** | `POST /v1.0/agent/generations` — "`prompt` is the only required field." Marketing: "Starts with a conversation / Outlines first, so you shape the story / Iterates in chat, right beside your deck" | OD + OU |
| **Natural-language edit of an existing gamma** | `POST /v1.0/agent/gammas/{gammaId}/edits` with `prompt` (1–10,000 chars); MCP `edit_gamma` + `get_edit_status` returns a `summary` of changes | OD |
| **Edit semantics** | "Everything the edit instruction does not mention" is preserved — theme, untouched-card layout, sharing settings, and the gamma's URL stay the same. Edits do not change the gamma's format. "one edit runs on a gamma at a time" (a second concurrent request is rejected) | OD |
| **Edit limits** | "Edits apply to the gamma you point at and **cannot add new pages**"; "**There is no object-level API for addressing a specific slide element**"; archived gammas can't be edited; needs edit access; costs credits | OD |
| **Edit failure taxonomy** | `get_edit_status.reason` ∈ `target_not_found, unsupported_target, access_revoked, insufficient_credits, timeout, unavailable, edit_failed` | OD |
| **Three creation modes in the Classic UI** | "Generate – AI drafts an initial version based on your topic. **Paste** – AI formats and refines pre-written content. **Import** – AI converts existing files, decks, or web pages into a structured format." | OD |
| **Freeform editing mode** | Marketing "REFINE" section: "Ask Gamma's agent for changes, drop in smart layouts, or move anything anywhere with **freeform editing**. Move between them whenever you want. You never have to pick one." → "Ask, drag, or drop in a smart layout / Break out into full freeform design mode" | OU |
| **Studio mode** (image-per-slide) | Classic generator only, Pro+ only, presentations & social only. Each slide = one AI image with built-in text; "You can't move, resize, or restyle individual elements, change layouts, or swap out images on a Studio slide." "Edit text" extracts text into editable boxes over the image. Not in Gamma 5 | OD |
| **"Imagine" design tool** | Help article `13928852-what-is-imagine-and-how-do-i-design-with-it` (fetched 200) — dedicated design surface | OD |
| **AI editing of content in-app** | Help article `8033284-how-do-i-edit-my-content-with-ai` (fetched 200); marketing: "We rebuilt how Gamma thinks, designs, and edits." | OD + OU |
| **Transform content & layouts** | Help article `11029130-what-s-the-fastest-way-to-transform-content-and-layouts` (fetched 200) | OD |
| **Effort picker** | Help article `16951195-what-is-the-effort-picker-and-how-do-i-use-it` (fetched 200) — user-facing compute/taste control; API analogue is `quality` (`lite`/`standard`/`max`) | OD |

### 1.3 Themes, brand kits, templates

| Capability | Evidence | Tag |
|---|---|---|
| **Theme library** (standard + custom workspace themes) | `GET /v1.0/themes`; MCP `get_themes` → `themes[].id, name, type (standard\|custom), colorKeywords[], toneKeywords[], count`. "Each theme includes tone and color keywords to help match your style." | OD |
| **Custom themes / brand kits** | Help `11029150`: "A custom theme in Gamma defines the overall visual style of your content, including **colors, fonts, slide styles and accent images**." Pro tier = "Custom branding". Enterprise = custom domains + workspace branding | OD + OU |
| **Themes are per-file in Gamma 5** | "Themes now live on each file, so you can fine-tune the look of one gamma without affecting any others. Previously, updating a theme updated every gamma that used it" — file themes vs. shareable workspace themes | OD |
| **Theme vs template separation** | Explicit doc: theme = styling only (agent still decides structure); template = structure + styling (content rewritten). `themeId` and `templateId` are **mutually exclusive** on the agent endpoint — "passing both is rejected" | OD |
| **Template gallery — 46 pages, 20 categories** | `https://gamma.app/templates` rendered: "**100+ templates for any style or project**", 20 categories (Brochure, Business planning, Ebook, Event, Infographic, Just for fun, Lesson, Marketing materials, Meeting, Pitch deck, Portfolio, Project management, Proposal, Report, Research, Resume, School project, Social media, Training), pagination `1 2 … 46` | OU |
| **Template search API** | `GET /v1.0/templates/search`; MCP `search_templates` returns **two separate lists**: `workspaceTemplates[]` (usable as `gammaId`) and `exploreTemplates[]` (official Gamma templates — **not** accepted by `generate_from_template`; usable as `templateId` on REST `POST /agent/generations`) | OD |
| **Explore taxonomy** | `https://gamma.app/explore` rendered: AI graphics (Logos, Art, Drawings, Posters, Backgrounds, Thumbnails), Presentations, Websites, Documents, Social media, API; plus Menus (Conference websites, Sales proposals, Product launches, Keynotes, Pitch decks, Lead magnets, Portfolio websites, Business websites, Personal Websites, White papers, Ebooks, Training manuals, Case studies, Business plans, Onboarding, Social posts, Profile pictures, Infographics, Stories, Banners) and Solutions (Educators, …) | OU |
| **Template-level instructions + slide locks** | "a template owner can add **template-level instructions** (overall guidance such as tone, audience, or 'always fill in the pricing table'), **slide-level instructions** (a note on each slide saying what belongs there), and **lock** any slide that generation must leave untouched, such as a cover, legal disclaimer, or pricing slide. The instructions are stored invisibly in the template… **There is no API parameter for any of this; it is set in the template.**" Locks are honored by generation, not by human editors | OD |
| **Templates as reusable workspace objects** | Import a PPTX → "Save as a workspace template". Classic `POST /generations/from-template` requires the template to be **single-page**, marked as a template, within the plan's card limit; Explore/multi-page/archived/site-bound templates are rejected | OD |

### 1.4 Charts, tables, structured content, diagrams

| Capability | Evidence | Tag |
|---|---|---|
| **Smart Charts** (spreadsheet-backed chart block) | Help `11029098`: Insert → "Charts & Diagrams" → "Smart Charts", or `/chart` slash command. Chart editor with a data grid: add/remove/retype columns, delete columns, data labeling, axes, colors/text size, change chart type, annotate on the chart, show/hide series, drag to reposition, corner-handle resize | OD |
| **Google Sheets sync (one-directional)** | "You can connect a Smart Chart to a tab in a Google Sheet… click **Sync**… **Syncing is one-directional.** Changes you make in the Google Sheet flow into Gamma, but edits to the chart in Gamma do not write back to your sheet." | OD |
| **Smart Diagrams** (vector canvas) | Help `11029098`: Insert → "Smart Diagrams", or `/diagram`. Zoom, grid toggle, undo, text alignment/colour/placement, line thickness, **arrow direction**, insert lines/arrows/shapes/text/images, drag images, **background removal** tool | OD |
| **Tables as first-class blocks** | `read_gamma` output includes "text, images, videos, embeds, charts, tables, diagrams, and other visuals". Export to PPTX exports **tables as real, editable tables** (see §1.8) | OD |
| **API-level charting constraint** | "Charts, tables, and infographics can be prompted for, but **there are no parameters that control chart type, styling, or data formatting**, and results vary across runs. For predictable layouts, build them into a template." → the deterministic path is template-baked charts | OD |
| **Infographics** | Help `13920805-how-do-i-add-infographics-in-gamma` (fetched 200) | OD |
| **Shapes** | Help `16951068-what-are-shapes-and-how-do-i-use-them` (fetched 200) | OD |
| **Animations** | Help `13920980-how-do-i-add-animations-in-gamma` (fetched 200) | OD |
| **Videos** | Help `17168766-how-do-i-add-videos-to-gamma` (fetched 200); AI image-model enum even includes **video** models (`veo-3.1`, `veo-3.1-fast`, `luma-ray-2`, `luma-ray-2-flash`, `leonardo-motion-2`, `leonardo-motion-2-fast`) usable in `imageOptions.model` | OD |
| **Forms** | Help `17237438-how-do-i-add-a-form-to-my-gamma` (fetched 200) — "Add a form to my Gamma" | OD |
| **Toggles / nested slides / footnotes** | Help `11016428-how-do-i-use-toggles-nested-slides-and-footnotes-effectively` (fetched 200) | OD |

### 1.5 Images & image models

| Capability | Evidence | Tag |
|---|---|---|
| **38 AI image models** selectable via `imageOptions.model` | OpenAPI `ImageModel` enum + `apiEnums.ts` `IMAGE_MODEL_OPTIONS` (independent corroboration, incl. credit cost per model). Families: **DALL·E 3**, **Flux 1** (pro/quick/ultra), **Flux 2** (klein/flex/max/pro), **Flux Kontext** (fast/max/pro), **GPT Image** (1-medium, 2, 2-hd, 2-mini, 1-high, 1-mini-high/low/medium), **Ideogram 3** (+quality/turbo), **Leonardo Phoenix/Motion**, **Luma Photon/Ray**, **Nano Banana 2 / Flash / Pro** (Gemini 2.5 Flash / 3 Pro / 3.1 Flash Image), **Recraft V3/V4** (+vector/SVG) | OD |
| **10 non-AI image sources** | `imageOptions.source` ∈ `aiGenerated, webAllImages, webFreeToUse, webFreeToUseCommercially, pictographic, giphy, pexels, themeAccent, placeholder, noImages` — note the **commercial-use-safety ladder** (`webAllImages` vs `webFreeToUse` vs `webFreeToUseCommercially`) | OD |
| **AI style presets** | MCP `imageOptions.stylePreset` ∈ `photorealistic, illustration, abstract, 3D, lineArt, custom` + free-text `style` (≤5,000 chars). REST uses `style` string | OD |
| **Style-reference images** | `generate_image` accepts up to 4 `referenceImages[]` (`url` required, HTTPS only; `role` currently only `subject`). "When `referenceImages` are provided, the references drive the look and `type` and `themeId` are ignored." | OD |
| **Standalone image types & aspect presets** | `type` ∈ `illustration` (default), `scene`, `photo`, `abstract`; `sizePreset` ∈ `social-square` (1:1), `social-portrait` (4:5), `story` (9:16), `banner` (16:9), `slide` (16:9) | OD |
| **Media library** | Generated images are saved to the workspace media library; `mediaLibraryUrl` + `image.savedMediaId` → `{mediaLibraryUrl}/{savedMediaId}`. "The media library entry stays available after the generation job itself ages out… so it is the **durable link** to share." Archive a media item: `POST /v1.0/images/media/{savedMediaId}/archive` (idempotent; file not deleted, existing URLs keep working) | OD |
| **In-app image editing** | Help `11100214-how-do-i-edit-my-ai-generated-images` + `16154694-how-do-i-edit-images-with-gamma-imagine` (both fetched 200) | OD |
| **Your own images** | Include image URLs in `inputText` / `prompt`; "Gamma fetches and re-hosts them." Image URLs must be publicly accessible. `POST /v1.0/agent/generations` "doesn't guarantee that URLs in `prompt` are fetched and re-hosted." Import limits: images capped at **50 megapixels** (~8000×6250); media uploads 200 MB; AI style-ref images 10 MB | OD |
| **Image generation via API** | `POST /v1.0/images` → `imageGenerationId`; `GET /v1.0/images/{id}` → `image.url, width, height, aspectRatioUsed, savedMediaId`; failures carry `retryable` + `errorStatusCode` | OD |

### 1.6 Import

| Capability | Evidence | Tag |
|---|---|---|
| **PPTX import** (layout-faithful in Gamma 5) | Help `11047840`: "In Gamma 5, PowerPoint and PDF imports **keep your original layouts, design, and structure**. Everything stays fully editable." Marketing CONNECT: "Import PowerPoints and PDFs and they arrive the way you built them." | OD + OU |
| **PPTX / DOCX import** | "PowerPoint (.pptx) and Word (.docx) files: up to **200 MB** per file." | OD |
| **PDF import** | "PDFs: up to **100 MB** per file." | OD |
| **Webpage import** | "Webpages: paste a link." | OD |
| **Google Drive import** | "connect Google Drive through Connectors first" | OD |
| **Public Notion doc import** | "paste a link, or copy and paste the content directly" | OD |
| **Excel (.xlsx)** | **Not supported directly.** Workarounds: save as `.csv` and upload, or move to Google Sheets and read via the Drive connector | OD |
| **Keynote (.key)** | **Not supported directly.** Export to `.pptx` first | OD |
| **Import fidelity caveats** | Fonts not available are substituted and Gamma names the replacement (upload fonts manually via the font dropdown). "some charts arrive as static images" — recreate via the chart block to make editable | OD |
| **Save-as-template** | Import → "Save as a workspace template"; or "Import a template" under More options. Also "Reuse only your fonts, colors, and logo → create a custom theme instead" | OD |
| **Classic vs Gamma 5 import** | "Gamma's classic generator imports **only the text** from your file, not its design or layouts. To keep your original design, import from the Gamma 5 home screen instead." | OD |
| **Import via LLM / connector** | Help `15715171-how-can-i-get-my-data-into-gamma-decks-using-an-llm` (fetched 200) | OD |

### 1.7 Export formats

| Format | Where | Exact behaviour | Tag |
|---|---|---|---|
| **PDF** | API + UI | Direct download. Exported content reflects **Present Mode**, not Edit Mode | OD |
| **PPTX (PowerPoint)** | API + UI | Direct download. **Tables export as real, editable PowerPoint tables** (on by default, all plans; toggleable off). "PowerPoint does not support rounded corners on tables, so editable tables export with **sharp corners** even though Gamma's default styling shows rounded ones. All other table styling is preserved." | OD |
| **PNG** | API + UI | "Returns a **`.zip` with one PNG per card**" — not a single PNG file | OD |
| **Google Slides** | UI only | "Google Slides (**via PPTX upload**)" — not a native export target in the API; the export enum is exactly `pdf, png, pptx` | OD |
| **LinkedIn post** | UI only | "Post directly to LinkedIn" from the export menu | OD |
| **Single-card export** | UI only | "You can export the full gamma or individual slides" — dropdown to choose All cards vs current card | OD |
| **Image quality slider** | UI only | Controls resolution of images in the export; higher = sharper + larger file | OD |
| **Email copy** | UI only | "You'll also receive an email copy of the export" | OD |
| **Zoom-to-fit** | UI | Export scaling controlled by a "Zoom to fit" setting in Share → Export; explains most export-vs-editor mismatches | OD |
| **API export mechanics** | — | `POST /v1.0/gammas/{gammaId}/export` → `exportId`; `GET /v1.0/exports/{id}` → `exportUrl`. **One format per request**; "If you need multiple formats, make separate generation requests or export additional formats manually from the Gamma app." Export URLs **expire after ~1 week**, are **not tied to the API key**, and "anyone with this URL can download… **treat the link as a secret**" | OD |
| **Export failure taxonomy** | — | `reason` ∈ `render_timeout` and `export_failed` (transient, safe to retry); `deck_too_large` and `no_content` (require changing input) | OD |
| **"Editable PPTX" claim — precise reading** | — | Gamma claims editable **tables** inside the PPTX, and claims **layout/design fidelity on import**. It does **NOT** claim that the whole exported PPTX round-trips as a fully editable Gamma-like deck. Help `15939201` explicitly says exports "reflect **Present Mode**, not Edit Mode, so some visual differences are expected." A full-fidelity PPTX export is **not** claimed | OD |

### 1.8 Publishing, web output, embedding, responsiveness

| Capability | Evidence | Tag |
|---|---|---|
| **Publish as a live site** | `publish: true` on `POST /v1.0/generations` publishes a multi-page Gamma "as a live site on a Gamma-generated subdomain once all pages succeed" | OD |
| **Staged publishing** | "When you make updates to your gamma site, those changes won't go live immediately… preview your edits and publish only when you're ready." "Publish all site changes" vs. "Publish current page" (page-only; site theme/navigation unchanged) | OD |
| **Disable / unpublish without deleting** | Site Settings → toggle "Site Enabled" off: "remove public access without deleting your content"; re-enable any time | OD |
| **Responsive preview** | "Select **Preview** to view your site in **desktop, tablet, or mobile** mode" | OD |
| **Custom domains** | Pro = "Publish up to **10 custom domains**"; Ultra = "up to **100 custom domains**" | OU |
| **Per-page URL slugs + deep links** | `pages[].path` (1–500 chars, e.g. `/pricing`); honored for pages after the first; "Each entry becomes a distinct page with its own deep link"; collisions auto-disambiguated from the title | OD |
| **Embed via iframe** | Share → Embed → generate iframe code; works in Shopify (HTML block), Wix ("Embed a Site" widget), Squarespace (code block). **Only Gamma docs and presentations can be embedded — "Currently, Gamma sites cannot be embedded into other websites."** Public access must be enabled. Updates propagate automatically. Available on **all plans** | OD |
| **QR codes** | Help `11047829-how-do-i-create-and-embed-a-qr-code-in-gamma` (fetched 200) | OD |
| **Search-engine indexing toggle** | `enableSearchEngineIndexing` in the official n8n node's request mapping | OD |
| **Cookie/tracking on published site** | Help `17357900-does-gamma-set-cookies-or-run-tracking-on-my-published-site` (fetched 200) | OD |

### 1.9 Collaboration, sharing, workspaces

| Capability | Evidence | Tag |
|---|---|---|
| **Access levels** | `noAccess` \| `view` \| `comment` \| `edit`; workspace members additionally get `fullAccess`. Per-gamma share link + email share with per-recipient access | OD + OU |
| **Workspace permission override** | "Workspace settings override individual sharing settings. If your workspace is set to *Members can edit*, they will always have editing access — even if your gamma is set to *Anyone with the link can view*." | OD |
| **Request access** | "If someone sends you a link to a gamma you cannot open… you can request access directly from the gamma." Owner gets email; approve/deny from the share panel. (Folder access requests "coming soon") | OD |
| **Password protection** | "Require a password to view a Gamma" — Free/Plus/Pro/Ultra matrix; **does not apply to Gamma sites, only Gamma docs** | OD |
| **"Made with Gamma" badge** | Free-plan presentations carry the badge, and it "remains tied to the presentation even after upgrading to a paid plan"; removable via Share → Advanced Settings on paid plans. Plus tier = "Remove Gamma branding" | OD + OU |
| **Web discoverability** | "Make your Gamma discoverable on the web" — plan-gated | OD |
| **Comments** | `GET /v1.0/gammas/{gammaId}/comments`; MCP `get_gamma_comments`. Threads with `cardId` (null = page-level), `author{id,name}`, `contentText`, `status` (`open`\|`closed`), `replies[]`, `createdTime`, `updatedTime`; cursor pagination + `updatedSince` delta polling + `includeArchived` | OD |
| **Groups** | Help `17455788-what-are-groups-in-gamma-and-how-do-i-use-them` (fetched 200) | OD |
| **Folders & permissions** | `GET /v1.0/folders`; Help `15715069-how-do-folders-permissions-and-sharing-work` (fetched 200) | OD |
| **Workspace members** | Help `11047939-how-can-i-add-users-to-my-workspace` (fetched 200) | OD |
| **Audit logs** | Help `16950938-how-do-audit-logs-work-in-gamma` (fetched 200) | OD |
| **Admin controls (Enterprise)** | Help `16951270-what-admin-controls-are-available-on-enterprise` (fetched 200) | OD |
| **Slack app** | Help `15546622-can-i-use-gamma-with-slack` (fetched 200); the Slack app runs on the same MCP server but "does not expose the edit tools" | OD |

### 1.10 Versioning / history

| Capability | Evidence | Tag |
|---|---|---|
| **Undo** | `Cmd/Ctrl+Z`, repeatable | OD |
| **Version history** | "Gamma's version history feature lets you track changes over time and restore earlier versions of your gamma." Three-dot menu → Version History → pick a version → confirm. "This feature is available to **all users, including those on the free plan**" | OD |
| **Restore semantics** | "Restoring a version **replaces** your current gamma content with the selected version." Recommend duplicating first | OD |
| **API-level versioning** | **None.** There is no version-history endpoint, no revision list, no rollback endpoint, and no diff. The API surface has create/read/edit/export/archive/delete only. Editing is destructive-in-place; the only recovery path is the app's version history | OD (absence, explicit) |
| **Admin audit log vs. content version** | Audit logs (help `16950938`) are a workspace admin feature — distinct from end-user content version history | OD |

### 1.11 Analytics

| Capability | Evidence | Tag |
|---|---|---|
| **Doc-level engagement** | `GET /v1.0/gammas/{gammaId}/analytics` → `totalViews`, `uniqueViewers`, `uniqueEditors`, `cardCount`, `lastOpened`, `dailyViews{dayCount, timezone, days[{date, uniqueViewers}]}` (30-day rolling window) | OD |
| **Per-card engagement** | `GET …/analytics/cards` → `cards[]{cardId, cardName, cardPosition(1-based), viewTimeSeconds, viewersPercent(0-100)}` in deck order | OD |
| **Per-viewer list** | `GET …/analytics/viewers` → `viewers[]{viewerId, displayName, email, lastOpened, cardsViewed}`; paginated; `sortDirection` desc/asc. Requires edit permission; **manage** → all viewers, **edit-only** → only the API user's own row (403 otherwise) | OD |
| **Per-viewer detail** | `GET …/analytics/viewers/{userId}` → `scope` (`all`\|`self`), `cardsViewed`, `cardCount`, `perCardTimeSpent[]{cardId, cardName, cardPosition, viewTimePercent}` | OD |
| **Eventual consistency** | "Analytics data is eventually consistent and can lag by about an hour." | OD |
| **Interactive widget in MCP apps** | "In clients that support MCP apps, this renders an interactive widget; it also returns structured data and a formatted text summary." | OD |
| **Pro tier gating** | Pro = "Detailed analytics & advanced sharing" | OU |
| **Help article** | `11047329-how-do-i-track-my-gamma-s-performance-using-analytics` (fetched 200) | OD |

### 1.12 Connectors / integrations

| Capability | Evidence | Tag |
|---|---|---|
| **25+ connectors** | Marketing CONNECT: "Pull real content from **Slack, Notion, Dropbox, and 25+ tools**." Help `15715171`; the API has a `disableConnectors` flag on both generation and edit to opt out of Notion/Slack-style connectors | OU + OD |
| **AI-assistant connectors** | ChatGPT, Claude, Slack, **Superhuman Go**, and **Atlassian Rovo** — "work on all Gamma plans and do not require an API key." Also Zapier, Make, n8n (require an API key) | OD |
| **Custom MCP connectors into Gamma** | `connectors/custom-mcp-connectors.md` — "Bring your own MCP servers into Gamma so workspace members can use your team's tools and data with Gamma Agent." | OD |
| **OpenAI review caveat** | "Some platforms review app updates before making them available to users… This applies to applications such as **ChatGPT and Codex**, where OpenAI reviews each update." | OD |
| **Google Drive / Google Sheets** | Connectors for Drive import; one-directional Sheets→Smart Chart sync | OD |
| **Notion** | Public Notion docs importable; Notion is also a connector target | OD |
| **Dropbox** | Named in the marketing connector list | OU |
| **n8n official node** | `gamma-app/n8n-nodes-gamma` — MIT, JavaScript/TypeScript, published to npm, actively pushed (2026-10-13) | OD + API_RESPONSE |

### 1.13 Enterprise / business

| Capability | Evidence | Tag |
|---|---|---|
| **Pricing tiers** | **Free $0** (400 credits at signup; 10 slides/prompt; import PDF & PPTX; export PDF/PPTX/PNG/Google Slides) · **Plus $9/seat/mo** ($108 annual; 1,000 credits; 100 slides/prompt; remove branding; advanced AI image models) · **Pro $18/seat/mo** ($216 annual; 4,000 credits; premium image models; custom branding; detailed analytics & advanced sharing; 10 custom domains; **API access**) · **Ultra $90/seat/mo** ($1,080 annual; 20,000 credits; most advanced AI models incl. text/image/**video**; 100 custom domains; early access) | OU |
| **Billing** | "Save up to 28% with annual billing"; "No credit card required" (Free) | OU |
| **Credits** | 1–3 credits/card (varies by the text model Gamma picks internally). AI images: Standard 2–15, Advanced 20–33, Premium 34–75, Ultra 30–125 credits/image. Template generations "may cost slightly more per card". Illustrative: 10-card deck + 5 basic images ≈ 20–60 credits; 20-card doc + 15 premium images ≈ 320–1,070; 30-card social set + 30 ultra images ≈ 930–3,900 | OD |
| **Agent job pricing** | Agent generations/edits are "priced by the work the agent does" — writing, research, images — **not** per card/image. "The same prompt can cost a different amount from run to run." `quality` ∈ `lite` \| `standard` \| `max`; `max` = Pro+ only (else **403 `agent_premium_models_restricted`**) | OD |
| **Credit pooling** | Help `16894266-how-does-credit-pooling-work-for-business-and-enterprise` (fetched 200) | OD |
| **Auto-recharge** | "Auto-recharge is the safest way to prevent failed generations due to exhausted credits." | OD |
| **SOC 2 Type II** | Stated on the pricing page | OU |
| **Enterprise admin controls** | Help `16951270` (fetched 200) | OD |
| **Business options** | Help `11594955-what-options-does-gamma-offer-for-business` (fetched 200) | OD |

---

## 2. REST API — endpoint table

**Base URL:** `https://public-api.gamma.app` (path prefix `/v1.0`)
**Auth (REST):** API key in header `X-API-KEY` — OpenAPI `securitySchemes: { api-key: { type: apiKey, in: header, name: "X-API-KEY" } }`, `servers: [{ url: "https://public-api.gamma.app", description: "Production" }]`
**Auth (REST, alternative):** OAuth 2.0 Bearer token on the same endpoints (acts on behalf of the user; spends the authorizing user's credits)
**All jobs are asynchronous:** create → poll → retrieve. **There are no webhooks.**

| # | Method | Path | Auth | Req (key fields) | Resp (key fields) | Tier / limit | Tag |
|---|--------|------|------|-----------------|------------------|-------------|-----|
| 1 | POST | `/v1.0/agent/generations` | `X-API-KEY` or OAuth Bearer | `prompt` (required, ≤400,000 chars); `templateId`, `themeId`, `format` ∈ {document,presentation,social}, `numCards` (1–100; **10 free / 100 paid**), `quality` ∈ {lite,standard,max}, `sourceUrls[]` (≤10), `additionalInstructions` (≤5,000), `exportAs` ∈ {pdf,png,pptx}, `folderId`, `sharingOptions`, `disableConnectors` | `generationId` (`^gen_[A-Za-z0-9]+$`), `status:"pending"`, `warnings[]` | Pro+ (API keys); `max` quality Pro+ else **403**; 429 `workspace_concurrency_limit_exceeded` + `Retry-After`; 503 = busy | OD |
| 2 | GET | `/v1.0/agent/generations/{generationId}` | same | path `generationId` | `status` ∈ {pending,completed,failed}, `progress{done,total,percent(0–99),stages}`, `gamma.gammaUrl`, `gamma.gammaId`, `result.summary`, `exportUrl`, `credits{deducted,remaining}` | poll ≈ every 5 s | OD |
| 3 | POST | `/v1.0/agent/gammas/{gammaId}/edits` | same | `prompt` (1–10,000 chars), `disableConnectors` | `editId`, `status:"pending"` | one edit per gamma at a time; credits charged; archived gammas rejected | OD |
| 4 | GET | `/v1.0/agent/edits/{editId}` | same | path `editId` | `status`, `gammaUrl`, `summary`, `credits{deducted,remaining}`, `error`, `error.reason` | — | OD |
| 5 | POST | `/v1.0/generations` (Classic) | same | `inputText` (≤400,000) **or** `pages[]` (1–50); `textMode`, `format` ∈ {document,presentation,social,webpage}, `cardSplit`, `numCards`, `title` (1–500), `additionalInstructions` (≤5,000), `textOptions`, `imageOptions`, `cardOptions`, `sharingOptions`, `themeId`, `folderId`, `exportAs`, `publish` | `generationId`, `warnings`, `pageWarnings[]` | 402 insufficient credits | OD |
| 6 | POST | `/v1.0/generations/from-template` (Classic) | same | `gammaId` (required — single-page workspace template), `prompt` (≤400,000), `title`, `themeId` (**replaces** the template theme — Classic exception), `imageOptions`, `sharingOptions`, `folderId`, `exportAs` | `generationId`, `warnings` | template must be single-page + marked template + within card limit | OD |
| 7 | GET | `/v1.0/generations/{id}` | same | path `id` | `generationId`, `status`, `gammaId`, `gammaUrl`, `exportUrl`, `credits{deducted,remaining}`, `pages[]{gammaId,gammaUrl,status,error,exportUrl}`, `error{message,statusCode}` | poll | OD |
| 8 | POST | `/v1.0/images` | same | `prompt` (1–5,000), `type` ∈ {illustration,scene,photo,abstract}, `sizePreset` ∈ {social-square,social-portrait,story,banner,slide}, `themeId`, `referenceImages[]{url,role}` (≤4) | `imageGenerationId`, `status:"pending"`, `warnings[]`, `generatedTime`, `mediaLibraryUrl` | credits charged | OD |
| 9 | GET | `/v1.0/images/{id}` | same | path `id` | `status`, `image{url,width,height,aspectRatioUsed,savedMediaId}`, `warnings[]`, `error`, `retryable`, `errorStatusCode`, `credits{}`, `mediaLibraryUrl` | poll every few seconds | OD |
| 10 | POST | `/v1.0/images/media/{savedMediaId}/archive` | same | path `savedMediaId` | (success) | idempotent; file not deleted, existing image URLs keep working | OD |
| 11 | GET | `/v1.0/themes` | same | — | list of themes: `id`, `name`, `type` (standard\|custom), `colorKeywords[]`, `toneKeywords[]` | — | OD |
| 12 | GET | `/v1.0/folders` | same | — | list of folders: `id`, `name` | — | OD |
| 13 | GET | `/v1.0/gammas/search` | same | `q`, `createdBy`, `updatedAfter`, `updatedBefore`, `includeArchived`, `limit` (default 10, max 25) | `hits[]{id,title,url,highlight,createdBy,updatedTime,archived}` | full-text over titles + body | OD |
| 14 | GET | `/v1.0/templates/search` | same | `q` (≤2,000 chars), `limit` (default 10, max 25) | `workspaceTemplates[]`, `exploreTemplates[]` (with `previewUrl`, `thumbnailUrl`) | explore ids **rejected** by `generate_from_template` | OD |
| 15 | GET | `/v1.0/gammas/{gammaId}` | same | path: file ID **or** the doc ID from a `gamma.app/docs/...` URL | metadata: title, theme, card count, URLs, timestamps | — | OD |
| 16 | GET | `/v1.0/gammas/{gammaId}/comments` | same | `limit` (default 50, max 50), `after`, `updatedSince`, `includeArchived` | `comments[]{id,cardId,author{id,name},contentText,status,replies[],createdTime,updatedTime}`, `hasMore`, `nextCursor` | — | OD |
| 17 | POST | `/v1.0/gammas/{gammaId}/export` | same | body `{ exportAs: pdf\|png\|pptx }` | `exportId` | view access; archived gammas can't be exported; one format per request | OD |
| 18 | GET | `/v1.0/exports/{id}` | same | path `id` | `exportId`, `status`, `gammaId`, `exportAs`, `exportUrl` (≈1-week TTL, secret), `error{reason,message,statusCode}` | poll | OD |
| 19 | POST | `/v1.0/gammas/{gammaId}/archive` | same | path `gammaId` | (success) | idempotent; does **not** deduct credits | OD |
| 20 | DELETE | `/v1.0/gammas/{gammaId}` | same | path `gammaId` | (deleted) | **requires workspace admin role** | OD |
| 21 | GET | `/v1.0/gammas/{gammaId}/analytics` | same | path | `totalViews`, `uniqueViewers`, `uniqueEditors`, `cardCount`, `lastOpened`, `dailyViews{...}` | edit access; ~1 h lag | OD |
| 22 | GET | `/v1.0/gammas/{gammaId}/analytics/cards` | same | path | `cards[]{cardId,cardName,cardPosition,viewTimeSeconds,viewersPercent}` | edit access | OD |
| 23 | GET | `/v1.0/gammas/{gammaId}/analytics/viewers` | same | `limit` (default 25, max 50), `after`, `sortDirection` | `viewers[]{viewerId,displayName,email,lastOpened,cardsViewed}` | edit access (manage = all) | OD |
| 24 | GET | `/v1.0/gammas/{gammaId}/analytics/viewers/{userId}` | same | path `userId` (from #23) | `scope`, `cardsViewed`, `cardCount`, `perCardTimeSpent[]{...}` | anonymous viewers → 404 | OD |

*Endpoints #21–#24 are counted in the doc's own summary table; #20 and #19 are **REST-only** (no MCP equivalent).*

### API-response evidence (live, unauthenticated)

```
$ curl -s https://public-api.gamma.app/v1.0/themes
HTTP 401  application/json
{"message":"Invalid API key","statusCode":401}

$ curl -s https://public-api.gamma.app/v1.0/folders
HTTP 401  {"message":"Invalid API key","statusCode":401}

$ curl -s https://public-api.gamma.app/v1.0/gammas/search
HTTP 401  {"message":"Invalid API key","statusCode":401}
```
(Tag: API_RESPONSE — base URL, path shape, and auth scheme confirmed. No key obtained; no bypass attempted.)

---

## 3. Gamma MCP server — the facts

| Fact | Value | Evidence | Tag |
|---|---|---|---|
| **Server URL** | `https://mcp.gamma.app/mcp` | `developers.gamma.app/mcp/gamma-mcp-server.md` — "Gamma MCP is a hosted server at `https://mcp.gamma.app/mcp`" | OD |
| **Transport** | HTTP MCP endpoint (Streamable-HTTP style) at `/mcp`; OAuth discovery via RFC 9728 at `/.well-known/oauth-protected-resource` | doc + live metadata | OD + AR |
| **Live resource metadata** | `{"resource":"https://mcp.gamma.app","authorization_servers":["https://auth.gamma.app"],"scopes_supported":["generate","gamma:read"],"bearer_methods_supported":["header","body"]}` — fetched from `https://mcp.gamma.app/.well-known/oauth-protected-resource`, **HTTP 200** | `https://mcp.gamma.app/.well-known/oauth-protected-resource` @ 2026-10-22T03:41:08Z | API_RESPONSE |
| **Authorization server** | `https://auth.gamma.app` | live metadata + `developers.gamma.app/get-started/authenticate-with-oauth.md` | AR + OD |
| **Live AS metadata** | `authorization_endpoint: https://auth.gamma.app/oauth/authorize`, `token_endpoint: https://auth.gamma.app/oauth/token`, **`registration_endpoint: https://auth.gamma.app/oauth/register`** (RFC 7591 DCR), `jwks_uri: …/.well-known/jwks.json`, `response_types_supported:[code]`, `grant_types_supported:[authorization_code, refresh_token]`, `code_challenge_methods_supported:[S256]` (PKCE), `token_endpoint_auth_methods_supported:[none, client_secret_post, client_secret_basic]`, `scopes_supported:[generate, gamma:read]`, `claims_supported:[sub,aud,exp,iat,iss]`, `authorization_response_iss_parameter_supported:true` | `https://auth.gamma.app/.well-known/oauth-authorization-server` @ 2026-10-22T03:41:10Z | API_RESPONSE |
| **Auth scheme** | OAuth 2.0 Bearer token on every request (`Authorization: Bearer <token>`). **No static client IDs** — clients must support **Dynamic Client Registration (RFC 7591)**. Loopback (`http://localhost:<port>`) redirects require PKCE | doc + live metadata | OD + AR |
| **Redirect URI gating** | "Registration succeeds only if every redirect URI your client sends matches a pattern Gamma has **allowlisted** for it, so register your URIs with Gamma before the first connection." Onboarded desktop tools (Cursor, Gemini CLI) have loopback patterns. New clients must submit a request form (name, email, company, use case, redirect URIs, 256×256 logo SVG/PNG/JPEG) | `mcp/gamma-mcp-server.md` | OD |
| **Consent scopes (UI strings)** | "Create gammas in your workspace" · "Read gammas in your workspace" · "List folders from your workspace" · "List themes from your workspace" | `mcp/mcp-tools-reference.md` | OD |
| **401 behaviour** | `WWW-Authenticate: Bearer resource_metadata="https://<server>/.well-known/oauth-protected-resource"` | `mcp/mcp-tools-reference.md` | OD |
| **Tool count** | **21 tools** | `mcp/mcp-tools-reference.md` quick reference | OD |
| **Availability** | "Available on **all Gamma plans**" (incl. Free and Plus). **No API key required.** Generations/edits/images charge credits; **reading, searching, and exporting do not** | `get-started/access-and-pricing.md` | OD |
| **Powers first-party connectors** | "The Gamma connectors in ChatGPT and Claude and the Gamma app for Slack **run on this server**" | `mcp/gamma-mcp-server.md` | OD |
| **Error shape** | `{ "error": "...", "isError": true }`; plan/credit failures add `planLimitExceeded: true` + live workspace limits | `mcp/mcp-tools-reference.md` | OD |
| **Cache hints** | `tools/list` responses carry `ttlMs: 60000`, `cacheScope: "private"`; SEP-2549 hosts may cache the per-user tool list up to 60 s | `mcp/mcp-tools-reference.md` | OD |
| **Async model** | `generate`, `generate_multi_page_gamma`, `generate_from_template` → `generationId`; `generate_image` → `imageGenerationId`; `export_gamma` → `exportId`; `edit_gamma` → `editId`. Poll the matching `get_*_status` tool. "Once completed, the `generationId` can be passed to `read_gamma`, `edit_gamma`, or `export_gamma` in place of the Gamma ID" | `mcp/mcp-tools-reference.md` | OD |
| **MCP-only capability** | `read_gamma` (read a gamma's **full content**) is **MCP-only** — no REST equivalent. Conversely, **archive** and **delete** are **REST-only** | `mcp/gamma-mcp-server.md` FAQ + `reference/common-feature-requests.md` | OD |
| **Cheap end-to-end check** | "Call `get_themes` or `get_folders` for a cheap end-to-end check that does not charge credits." | `mcp/gamma-mcp-server.md` | OD |
| **Custom MCP callback endpoint** | `https://api.gamma.app/mcp/custom/callback` appears in the docs corpus | `raw/gamma_llms-full.txt` | OD |

### The 21 MCP tools (verbatim names, with read-only / destructive / idempotent flags from the doc's table)

| # | Tool | Description | Read-only | Destructive | Idempotent |
|---|------|-------------|-----------|------------|------------|
| 1 | `generate` | Create presentations, documents, webpages, or social posts from scratch | No | No | No |
| 2 | `generate_multi_page_gamma` | Create one multi-page Gamma (several pages under one URL) in a single request | No | No | No |
| 3 | `generate_from_template` | Create a new gamma from an existing template gamma | No | No | No |
| 4 | `get_generation_status` | Check the status of a `generate`, `generate_multi_page_gamma`, or `generate_from_template` job | Yes | No | Yes |
| 5 | `generate_image` | Generate one standalone image from a text prompt | No | No | No |
| 6 | `get_image_generation_status` | Check the status of a `generate_image` job and get the image URL | Yes | No | Yes |
| 7 | `export_gamma` | Export an existing gamma to PDF, PPTX, or PNG | No | No | No |
| 8 | `get_export_status` | Check the status of an export and get the download link | Yes | No | Yes |
| 9 | `edit_gamma` | Edit the content of an existing gamma from a natural-language instruction | No | **Yes** | No |
| 10 | `get_edit_status` | Check the status of an `edit_gamma` job and get the summary of changes | Yes | No | Yes |
| 11 | `get_gammas` | Browse or search existing gammas and templates | Yes | No | Yes |
| 12 | `search_gammas` | Full-text search over gamma titles and body text | Yes | No | Yes |
| 13 | `search_templates` | Search workspace templates and official Gamma explore templates | Yes | No | Yes |
| 14 | `read_gamma` | Read the full content of an existing Gamma | Yes | No | Yes |
| 15 | `get_gamma_comments` | List comment threads (and replies) on an existing Gamma | Yes | No | Yes |
| 16 | `get_gamma_analytics` | Get engagement summary analytics for a Gamma | Yes | No | Yes |
| 17 | `get_gamma_card_analytics` | Get card-by-card engagement for a Gamma | Yes | No | Yes |
| 18 | `get_gamma_viewer_analytics` | List the people who viewed a Gamma | Yes | No | Yes |
| 19 | `get_gamma_viewer_detail_analytics` | Get one viewer's detailed engagement with a Gamma | Yes | No | Yes |
| 20 | `get_themes` | Browse or search the Gamma theme library | Yes | No | Yes |
| 21 | `get_folders` | Browse or search your Gamma folders | Yes | No | Yes |

**Notable MCP-only semantics:**
- `read_gamma` response format: `Title: <gamma title>`, then `=== Page N: <title> ===` per page, "Each page body contains the full human-readable content for that page, including text, images, videos, embeds, charts, tables, diagrams, and other visuals." Deliberately human-readable, "not raw HTML or JSON."
- `get_gammas` pagination: `query` (min 3 chars, title search), `type` ∈ {template, regular, all}, `limit` (default 25, max 50), `createdByMe`, `after` cursor. "When paginating, keep `query` and `type` the same between calls and only advance the `after` cursor."
- `search_gammas` output includes a `highlight` snippet "usually centered on the match".
- `search_templates` splits `workspaceTemplates` vs `exploreTemplates` because they have different usable parameters — a hard constraint worth copying.
- `get_themes` returns `colorKeywords[]` and `toneKeywords[]` — i.e. the theme library is **machine-matchable**, not just human-browsable.

---

## 4. Code-availability verdict

### Verdict: **`SOURCE_NOT_AVAILABLE` for the product core; partially available only for peripheral integrations + one internal QA tool.**

**Gamma's internal product source (the editor, the agent engine, the card model, the PPTX exporter, the web renderer) is not public.** The `gamma-app` GitHub org exists and has 29 repos, but they are overwhelmingly **forks of third-party open-source libraries** and **peripheral integrations** — not the product.

### All 29 repos in `github.com/gamma-app` (fetched `GET api.github.com/users/gamma-app/repos?per_page=100`, 2026-10-22T03:41:48Z)

| Repo | fork? | Language | Description | Relevance |
|---|---|---|---|---|
| `gamma-app/pptx-renderer` | **yes** | — | "Browser-native high-fidelity PPTX renderer: parses Office Open XML, renders slides as HTML/SVG (187+ shapes, 134+ SmartArt, 36+ style variants, 100+ python-pptx cases)" — Apache-2.0, 0★, pushed 2026-08-20 | **NOT** Gamma's exporter. `fork: true` → a fork of a third-party OSS project. Same content as the upstream it forks. **Excluded.** The genuinely interesting detail is the *capability* (browser-native OOXML→HTML/SVG PPTX rendering with visual regression vs. PowerPoint), not the ownership |
| `gamma-app/n8n-nodes-gamma` | **no** | JavaScript | "**Official** Gamma community node for n8n - Create AI-powered presentations and documents" — **MIT**, 2★, pushed 2026-10-13 | **Genuinely Gamma-authored and published.** 49 files: `nodes/Gamma/api.ts`, `apiEnums.ts`, `actions/generation/create.operation.ts` (24 KB), `actions/{analytics,comment,export,folder,gamma,image,theme,user}`, `credentials/GammaApi.credentials.ts`, `docs/n8n-integration-plan.md` (25 KB), `docs/n8n-readiness-audit.md` (19 KB), `test/*.js` (10 test files incl. `live.test.js`) | **PARTIAL** — integration only, not the product |
| `gamma-app/import-grader-annotator` | **no** | Python | desc `null`, no license, pushed 2026-06-29. Files: `README.md`, `AGENTS.md`, `backend/`, `frontend/`, `docs/`, `scripts/`, `setup.sh`, `run.sh`, `.env.example` | **Genuinely Gamma-internal code.** README: "A local tool for manually annotating **PPTX→Gamma import quality**… **Import Evals Taxonomy (PSSL)** — a built-in set of **24** [failure modes]"; three output variants ("Deck Doctor" = hand-crafted ideal Gamma, "Current Import", "Programmatic Import"); grades Pass/Borderline/Fail per slide pair; autosave + Google-Drive-shared folder; exports consolidated JSON + tidy CSV. Setup instructions reference a Google account `…@gamma.app` | **PARTIAL** — internal QA/eval tooling, not the product. Strong signal that Gamma runs a formal **import-fidelity eval harness** with a 24-mode failure taxonomy |
| `gamma-app/ai-coding-interview` | no | TypeScript | desc `null`, 1★, pushed 2026-07-14 | **Hiring artifact** — Gamma's AI-coding interview exercise. Not product source, but a direct signal of their AI-engineering culture |
| `gamma-app/desktop-app-releases` | no | — | desc `null`, pushed 2024-08-17 | Release binaries only — no source |
| `gamma-app/schematics` | **yes** | — | "Nest architecture element generation based on Angular schematics" | Fork of `schematics` — **Excluded** |
| `gamma-app/tiptap`, `tiptap-collaboration-extension`, `tiptap-react19-bug` | yes | — | — | Forks of TipTap. **Excluded.** *Suggestive:* Gamma's editor is built on ProseMirror/TipTap + Yjs collaboration (`y-prosemirror`, `prosemirror-view`, `prosemirror-math`, `react-prosemirror` also forked) |
| `gamma-app/prosemirror-view`, `prosemirror-math`, `react-prosemirror`, `y-prosemirror` | yes | — | — | Forks. **Excluded** |
| `gamma-app/tldraw` | yes | — | — | Fork of tldraw. **Excluded.** *Suggestive:* tldraw is in Gamma's stack (freeform canvas / diagram surfaces) |
| `gamma-app/chakra-ui` | yes | — | — | Fork. **Excluded.** *Suggestive:* Chakra UI in the Gamma stack |
| `gamma-app/dnd-kit` | yes | — | — | Fork. **Excluded.** *Suggestive:* dnd-kit in the Gamma stack (drag-and-drop layout editing) |
| `gamma-app/apollo-client` | yes | — | — | Fork. **Excluded.** *Suggestive:* Apollo GraphQL client in the Gamma stack |
| `gamma-app/async-redis` | yes | — | — | Fork. **Excluded.** *Suggestive:* Redis in the Gamma stack |
| `gamma-app/cf-image-proxy` | yes | — | — | Fork. **Excluded.** *Suggestive:* a Cloudflare image-proxy service in the Gamma stack |
| `gamma-app/aijsx` | yes | — | — | Fork. **Excluded** |
| `gamma-app/raycast-ext-gamma-color-picker` | yes | — | — | Fork. **Excluded** |
| `gamma-app/chrome-extension-webpack-boilerplate` | yes | — | — | Fork. **Excluded** |
| `gamma-app/react-19-chakra-bug` | yes | — | — | Fork. **Excluded** |
| `gamma-app/PhishingArmyCore`, `fruity-dolphin-23`, `id128`, `HungryDog`, `HungryDog2` | — | — | — | Fork/scratch repos with no descriptive metadata. **Excluded** |
| `gamma-app/lokalise-push-action` | yes | — | — | Fork. **Excluded** |

### Non-Gamma repos checked and explicitly excluded

| Repo | Why excluded | Tag |
|---|---|---|
| `api-evangelist/gammaapp` | "Gamma.app — **independent third-party** profile of a public API surface, **by API Evangelist**". 0★, no code, topics only. Not Gamma-authored | API_RESPONSE |
| `presenton/presenton` (11,259★) | "Open-Source AI Presentation Generator and API (Gamma, Canva, Beautiful AI, Deckt…" — a **Gamma competitor**, not Gamma | API_RESPONSE |
| `allweonedev/presentation-ai` (3,055★) | "**Gamma Alternative**" — a competitor | API_RESPONSE |
| `ishandutta2007/open-gamma` (3★) | "open-source equivalent of gamma" — a clone | API_RESPONSE |
| `atharva9167j/preso`, `misbahsy/zentable`, `SurgePix/ai-ppt-prompts`, `mindlesseye/Gamma-Desktop---Gamma-AI-Presentation-2026` | Competitors / clones / prompt libraries | API_RESPONSE |
| `DedInc/gamma-ai-watermark-remover` (173★) | A third-party tool that strips the "Made with Gamma" badge — anti-Gamma, not Gamma | API_RESPONSE |
| `OpenGammaProject/Gamma-MCA`, `KrasnovM/Gamma-Manager`, `0skater0/NvColorProfiles` | Unrelated uses of the word "gamma" (spectroscopy, display gamma ramp, color profiles) | API_RESPONSE |

### npm

- `GET registry.npmjs.org/-/v1/search?text=scope:gamma` → **0 results** (no `@gamma/*` scope published).
- `GET registry.npmjs.org/gamma-app` → **404**; `…/gammaapp` → **404**; `…/@gamma-app/api` → **404**; `…/@gamma-app/sdk` → **404**.
- `GET registry.npmjs.org/-/v1/search?text=gamma%20presentation` → 20 results, **all** `@stdlib/*` gamma-distribution math packages plus `gamma` (the math function). **No Gamma-the-product package.**
- **Exception:** `n8n-nodes-gamma` is published to npm (MIT) — an official Gamma community node.

### Reasoning

1. There is **no** repository containing the Gamma editor, agent engine, card renderer, or exporter.
2. The `gamma-app` org's forks reveal Gamma's **technology stack** (ProseMirror/TipTap + Yjs, tldraw, Chakra UI, dnd-kit, Apollo, Redis, a Cloudflare image proxy) but **contain no Gamma-original product code** — a fork's contents are the upstream's.
3. The only two non-fork repos of substance are an **integration** (n8n node) and an **internal QA tool** (`import-grader-annotator`).
4. Therefore a competitor cannot legally or practically reconstruct Gamma's core from public sources; the public surface that matters is the **documented API + MCP contract**, which is unusually complete.

---

## 5. Export format table (consolidated)

| Format | API `exportAs`? | MCP `export_gamma`? | UI | Editable? | Fidelity notes | Tag |
|---|---|---|---|---|---|---|
| **PDF** | ✅ `pdf` | ✅ | ✅ | No (static) | Reflects **Present Mode**, not Edit Mode; Zoom-to-fit controls scaling | OD |
| **PPTX (PowerPoint)** | ✅ `pptx` | ✅ | ✅ | **Tables only** — "exported as **real, editable tables**… You can edit the text and restyle the table directly in PowerPoint — or in Google Slides after uploading the PPTX file. This is on by default for all users on all plans… toggleable off." PowerPoint can't do rounded table corners → exported tables get **sharp corners**; all other table styling preserved. **The deck as a whole is not claimed to round-trip as a Gamma-editable file** | OD |
| **PNG** | ✅ `png` | ✅ | ✅ | No | "**a `.zip` with one PNG per card** (not a single PNG file)" | OD |
| **Google Slides** | ❌ (not in the enum) | ❌ | ✅ (via PPTX upload) | Tables only, after a PPTX round-trip | Not a first-class API export target | OD |
| **LinkedIn post** | ❌ | ❌ | ✅ | — | Direct post from the export menu | OD |
| **Single card** | ❌ | ❌ | ✅ | — | Dropdown: All cards vs current card | OD |
| **Email copy of export** | ❌ | ❌ | ✅ | — | Automatic email delivery | OD |
| **Export URL lifetime** | — | — | — | — | ≈**1 week**; not tied to the API key; **"treat the link as a secret"** | OD |

**"Editable PPTX" verdict:** Gamma claims **editable tables inside** the PPTX export and **layout-faithful PPTX/PDF import**. It does **not** claim a fully editable PPTX round-trip of the whole deck. The doc explicitly warns exports reflect Present Mode, and its own export-fidelity help article exists to explain the gaps (content scaling, chart sizing, font substitution). Tag: OD.

---

## 6. Evidence table (condensed)

| URL | fetched_at_utc | tag | observation |
|---|---|---|---|
| `https://developers.gamma.app/` | 2026-10-22T03:39:52Z | API_RESPONSE | **200**, 889,855 bytes (GitBook) |
| `https://developers.gamma.app/llms.txt` | 2026-10-22T03:40:05Z | API_RESPONSE | **200**, 10,515 B — 47-page doc index. Also documents a GitBook "ask" endpoint: `GET https://developers.gamma.app/index.md?ask=<q>&goal=<goal>` |
| `https://developers.gamma.app/llms-full.txt` | 2026-10-22T03:40:06Z | API_RESPONSE | **200**, 491,973 B — full docs corpus incl. **embedded OpenAPI 3.0.0 JSON specs** for the REST API (base URL, `X-API-KEY` scheme, full request/response schemas) |
| `https://developers.gamma.app/readme.md` | 2026-10-22T03:40:07Z | API_RESPONSE | **200**, 17,262 B |
| `https://developers.gamma.app/mcp/gamma-mcp-server.md` | 2026-10-22T03:40:30Z | OFFICIAL_DOCUMENTATION | **200**, 18,079 B — server URL, transport, capabilities, OAuth+DCR, redirect-URI allowlist, troubleshooting |
| `https://developers.gamma.app/mcp/mcp-tools-reference.md` | 2026-10-22T03:40:31Z | OFFICIAL_DOCUMENTATION | **200**, 83,971 B — the 21-tool table + per-tool parameter/output schemas + error handling |
| `https://developers.gamma.app/get-started/access-and-pricing.md` | 2026-10-22T03:40:32Z | OFFICIAL_DOCUMENTATION | **200**, 9,549 B — plan gating, credit model, `quality` tiers |
| `https://developers.gamma.app/get-started/authenticate-with-oauth.md` | 2026-10-22T03:40:33Z | OFFICIAL_DOCUMENTATION | **200**, 13,106 B |
| `https://developers.gamma.app/get-started/understanding-the-api-options.md` | 2026-10-22T03:40:34Z | OFFICIAL_DOCUMENTATION | **200**, 24,470 B — endpoint table + Gamma 5 vs Classic comparison |
| `https://developers.gamma.app/build-with-gamma/brand-template-editing-controls.md` | 2026-10-22T03:40:35Z | OFFICIAL_DOCUMENTATION | **200**, 23,073 B — enforced/default/prompt-directed matrix; template instructions + slide locks; "Verified against the Gamma 5 and Classic endpoints on **2026-10-20**" |
| `https://developers.gamma.app/build-with-gamma/branded-template-workflow.md` | 2026-10-22T03:40:36Z | OFFICIAL_DOCUMENTATION | **200**, 16,513 B |
| `https://developers.gamma.app/reference/common-feature-requests.md` | 2026-10-22T03:40:37Z | OFFICIAL_DOCUMENTATION | **200**, 21,038 B — "one-screen map of that surface and the limits to design around" |
| `https://developers.gamma.app/reference/changelog.md` | 2026-10-22T03:40:38Z | OFFICIAL_DOCUMENTATION | **200**, 7,973 B |
| `https://developers.gamma.app/reference/error-codes.md` | 2026-10-22T03:40:39Z | OFFICIAL_DOCUMENTATION | **200**, 9,848 B |
| `https://developers.gamma.app/reference/image-model-accepted-values.md` | 2026-10-22T03:40:40Z | OFFICIAL_DOCUMENTATION | **200**, 9,486 B |
| `https://developers.gamma.app/reference/output-language-accepted-values.md` | 2026-10-22T03:40:41Z | OFFICIAL_DOCUMENTATION | **200**, 5,275 B |
| `https://developers.gamma.app/connectors/connectors-and-integrations.md` | 2026-10-22T03:40:42Z | OFFICIAL_DOCUMENTATION | **200**, 17,190 B — ChatGPT, Claude, Slack, Superhuman Go, Atlassian Rovo, Zapier, Make, n8n |
| `https://developers.gamma.app/connectors/custom-mcp-connectors.md` | 2026-10-22T03:40:43Z | OFFICIAL_DOCUMENTATION | **200**, 6,891 B — bring-your-own-MCP into Gamma |
| `https://developers.gamma.app/guides/charts-and-structured-content.md` | 2026-10-22T03:40:44Z | OFFICIAL_DOCUMENTATION | **200**, 4,841 B |
| `https://developers.gamma.app/guides/header-and-footer-formatting.md` | 2026-10-22T03:40:45Z | OFFICIAL_DOCUMENTATION | **200**, 8,209 B |
| `https://developers.gamma.app/guides/async-patterns-and-polling.md` | 2026-10-22T03:40:46Z | OFFICIAL_DOCUMENTATION | **200**, 18,019 B — Python/JS/cURL polling examples |
| `https://public-api.gamma.app/v1.0/themes` | 2026-10-22T03:41:05Z | API_RESPONSE | **401** `{"message":"Invalid API key","statusCode":401}` |
| `https://public-api.gamma.app/v1.0/folders` | 2026-10-22T03:41:05Z | API_RESPONSE | **401** same body |
| `https://public-api.gamma.app/v1.0/gammas/search` | 2026-10-22T03:41:06Z | API_RESPONSE | **401** same body |
| `https://mcp.gamma.app/.well-known/oauth-protected-resource` | 2026-10-22T03:41:08Z | API_RESPONSE | **200** `{"resource":"https://mcp.gamma.app","authorization_servers":["https://auth.gamma.app"],"scopes_supported":["generate","gamma:read"],"bearer_methods_supported":["header","body"]}` |
| `https://mcp.gamma.app/.well-known/oauth-authorization-server` | 2026-10-22T03:41:09Z | API_RESPONSE | **404** — metadata is on the AS host, not the RS host |
| `https://auth.gamma.app/.well-known/oauth-authorization-server` | 2026-10-22T03:41:10Z | API_RESPONSE | **200** — full RFC 8414 metadata (authorize/token/register/jwks endpoints, S256 PKCE, `none` token auth, scopes, claims) |
| `https://gamma.app/` | 2026-10-22T03:42:30Z | BLOCKED | curl → **403** (Cloudflare challenge) |
| `https://gamma.app/` | 2026-10-22T03:42:35Z | OBSERVED_UI | browser → **STATUS 200**. Sections BRAINSTORM / DESIGN / REFINE / CONNECT + 6 format tabs (PRESENTATIONS, DOCUMENTS, SOCIAL MEDIA VISUALS, WEBSITES, API, AI-GENERATED IMAGES). "Import PowerPoints and PDFs and they arrive the way you built them. Pull real content from Slack, Notion, Dropbox, and 25+ tools. Start in Claude, ChatGPT, or Slack. Export with high fidelity." Enterprise customer logos incl. IBM, Mastercard, Novartis, Northeastern, NYT, HSF Kramer, Cigna. Screenshot `raw/gamma_home_full.png` |
| `https://gamma.app/templates` | 2026-10-22T03:43:00Z | OBSERVED_UI | **STATUS 200** — "100+ templates"; 20 categories; pagination `1 2 … 46`; ~250 template names enumerated (Rounds, The Quiet Deck, Polder, Isotype, …). Screenshot `raw/gamma_templates.png` |
| `https://gamma.app/explore` | 2026-10-22T03:45:08Z | OBSERVED_UI | **STATUS 200** — explore taxonomy (AI graphics / Presentations / Websites / Documents / Social media / API + Menus + Solutions). Screenshot `raw/gamma_explore.png` |
| `https://gamma.app/pricing` | 2026-10-22T03:43:05Z | OBSERVED_UI | **STATUS 200** — Free/Plus $9/Pro $18/Ultra $90 per seat per month; SOC 2 Type II. Screenshot `raw/gamma_pricing.png` |
| `help.gamma.app` search ×10 queries | 2026-10-22T03:43:30Z | API_RESPONSE | **200 ×10** — article IDs enumerated per query |
| 18 individual `help.gamma.app/en/articles/…` pages | 2026-10-22T03:44:00Z | OFFICIAL_DOCUMENTATION | **200 ×18** — see LIVE_PROBE_LOG §4 for the full ID list |
| `https://api.github.com/users/gamma-app/repos?per_page=100` | 2026-10-22T03:41:48Z | API_RESPONSE | **200**, 29 repos |
| `https://api.github.com/repos/gamma-app/n8n-nodes-gamma/git/trees/HEAD?recursive=1` | 2026-10-22T03:41:20Z | API_RESPONSE | **200** — 49 files; official MIT integration |
| `raw.githubusercontent.com/.../n8n-nodes-gamma/main/nodes/Gamma/api.ts` | 2026-10-22T03:41:22Z | API_RESPONSE | **200** — `export const BASE_URL = 'https://public-api.gamma.app';` |
| `raw.githubusercontent.com/.../apiEnums.ts` | 2026-10-22T03:41:24Z | API_RESPONSE | **200**, 8,186 B — 38 image models + credit costs, 74 languages, `EXPORT_AS_VALUES = ["pdf","png","pptx"]`, per-format `CARD_DIMENSION_OPTIONS` |
| `raw.githubusercontent.com/.../create.operation.ts` | 2026-10-22T03:41:26Z | API_RESPONSE | **200**, 24,021 B — real request-shape source incl. `enableSearchEngineIndexing` |
| `raw.githubusercontent.com/.../import-grader-annotator/main/README.md` | 2026-10-22T03:41:30Z | API_RESPONSE | **200** — Gamma-internal import-eval harness; 24-mode taxonomy; `@gamma.app` Google account |
| `https://registry.npmjs.org/-/v1/search?text=scope:gamma` | 2026-10-22T03:41:30Z | API_RESPONSE | **200**, 0 results |
| `https://registry.npmjs.org/{gamma-app,gammaapp,@gamma-app/api,@gamma-app/sdk}` | 2026-10-22T03:41:32Z | API_RESPONSE | **404 / 404 / 404 / 404** |
| `https://api.github.com/search/repositories?q=gamma+presentation+ai` | 2026-10-22T03:41:44Z | API_RESPONSE | 65 results, all competitors/clones |

---

## 7. Blocked areas (precise)

| Area | Blocker | Tag |
|---|---|---|
| Gamma authenticated app (editor, Gamma 5 chat UI, template editor, dashboard, folders, analytics UI) | Requires sign-in. Not attempted — no accounts created | BLOCKED (login required) |
| Live REST responses with data | `X-API-KEY` required; all probes 401. No key obtained, no bypass attempted | BLOCKED (auth required) |
| Live MCP tool calls | OAuth Bearer + DCR-registered client with a Gamma-allowlisted redirect URI. Only the public metadata endpoints are reachable | BLOCKED (OAuth + DCR allowlist) |
| "Editable PPTX" round-trip fidelity | Would require exporting a real deck and inspecting the OOXML. Not attempted (needs an account + credits) | UNKNOWN |
| Gamma 5 vs Classic behavioural difference in practice | Only the documented contract is reported; no live generations were run | UNKNOWN (documented-only) |
| Full per-item Explore template catalogue | `gamma.app/explore` exposes the category taxonomy; enumerating every template ID needs paginated JS fetches beyond this pass | PARTIAL |
| `gamma-app/pptx-renderer` provenance | It is a `fork: true`; the upstream owner was not identified in this pass | UNKNOWN |
