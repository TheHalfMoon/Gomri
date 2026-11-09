# Gamma 5 REA — 01. Live Vivaldi Surface and Official Capability Verification

**As of 2026-11-09.** Source levels: `SESSION_UI` (actual authorized Vivaldi screenshot, private and NOT committed); `OFFICIAL_HELP` (current Gamma docs); `SOURCE_CODE` (readable public Gamma repositories); `HYPOTHESIS` (Gomri engineering inference); `UNKNOWN` (not verified). These terms must not be collapsed into a single "confirmed" grade.

## A. What was actually inspected in the user's Vivaldi session

- Browser: Vivaldi on authorized Windows desktop, website `gamma.app`, signed-in **Free** workspace.
- Initial screen: Gamma 5 welcome / "More visual variety" onboarding overlay. It was dismissed without generating anything.
- Home navigation visible: **Home**, **Media**, **Templates**, **Customize**, **Settings**, plus Recent chats, Recent gammas, Search, All, Shared with you, Sites, API Generated, workspace folders.
- Main composition: prompt box with attachment `+`, generation-options icon, image control and **Standard** effort selector. Product shortcuts visible: **Presentation**, **Document**, **Carousel**, **Image**; additional shortcuts extend beyond the cropped window.
- Direct access to **Use classic generator** also visible in this Gamma 5 home page.
- Prompt placeholder/creation hints and a carousel of suggested templates are visible.
- No private gamma was opened; no AI generation, import, collaboration, export, API token generation, billing action, or credit-consuming operation was performed.
- Screenshot and browser profile/private workspace material have **not** been committed to this public repository. Do not publish user/private session information.

**Limit:** this authenticates the CURRENT free-account home experience, not the behavior of editor operations, Gamma Pro Research, Gamma native import fidelity, server technology or private code. The remainder is evidence from public docs and source.

## B. Current Gamma 5 creation engine contract

Gamma currently presents a conversational agent with:
1. **Plan** mode: asks goal/audience questions, displays a plan/story before proceeding, waits for approval.
2. **Express** mode: skips up-front clarification/review to make a first draft, then permits chat refinement.
3. **Research** option: deeper web source gathering before generation; available Pro+ with Plan, not Express. Even without Research, Gamma says its agent may do a quick web search.
4. **Effort** Lite / Standard / Max: progressively stronger/slower/more credit-consuming generation; Max advertises deeper research and better visual models. Exact model chain is private; marketing must not be treated as model disclosure.
5. Source inputs: text, pasted notes, uploaded images, presentations, document files, spreadsheets, links, and supported integrations; can request that only attached material be used, but this is a prompt instruction rather than a formally proven hard web-access policy.

Official:
- https://help.gamma.app/en/articles/15002203-how-do-i-create-with-agent-in-gamma
- https://help.gamma.app/en/articles/16951195-what-is-the-effort-picker-and-how-do-i-use-it

## C. Gamma 5 layout model (important technical fact, not just a marketing sentence)

The official Gamma 5 help center explicitly defines:
- presentations have a **fixed 16:9 canvas**;
- a **grid** with proportional rows/columns/cells is the primary structural layout primitive, replacing classic columns, smart layouts and card layouts;
- grids allow relative cell resizing, ordering, cell backgrounds/fills, padding, borders, image backgrounds, and conversion between preset layouts;
- **freeform boxes** can be positioned independently, resized and rotated, including overlapping callouts and shapes;
- **conversion from grid content to freeform is one-way** (Undo available immediately);
- per-gamma layout choice: **fixed** content scales down to fit subject to a minimum, while **fluid** keeps size and can grow vertically;
- Gamma 5 and classic documents continue to coexist; legacy decks preserve previous behavior.

These are external design semantics. The docs do NOT reveal the private editor's exact Grid IR schema or renderer. Gomri should not assert Gamma uses CSS Grid, ProseMirror, Yjs or Canvas merely from this description.

Official: https://help.gamma.app/en/articles/17572896-how-do-grids-and-freeform-editing-work-in-gamma

## D. Gamma editing and revision semantics

- Manual editing and **Agent** mode in the same editor; direct per-slide edits via `Edit with Agent`.
- Gamma says the agent keeps previous goal/context and reports slides it touched, preserving other slides for targeted requests.
- **Original / Modified** toggle allows user to compare changes, with a restore option.
- **Undo** via Ctrl/Cmd+Z, plus Version History available even on the free plan. Restore replaces current content; duplicate first to retain both states.
- **Agent may research and add citations**, and may change structure, styling, writing, visuals.
- API/connector edits have a stronger explicit technical limit: one **page** per edit; cannot add pages; only one edit can run on a page at a time. Do not generalize this API limitation to every internal UI editor operation without testing.

Official:
- https://help.gamma.app/en/articles/8033284-how-do-i-edit-my-content-with-ai
- https://help.gamma.app/en/articles/11016385-where-do-i-start-when-adding-content-in-gamma
- https://help.gamma.app/en/articles/11048579-can-i-undo-a-change-or-restore-a-previous-version-in-gamma
- https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api

## E. Import, native editability, image-slide exception

Gamma 5 claims improved PPTX/PDF import with original layout, design and structure preserved; offers "preserve" vs redesign/condense approaches. Supports PPTX/POTX (not old PPT), DOCX, PDF, XLSX, CSV, public Google Slides/Notion URLs and web pages. Public docs state 50 files / 250 MB per message, up to 1 GB per chat, and no fixed slide count.

**Critical exception:** Gamma's **Image slides** (formerly Studio mode, Pro web) produce one generated image per slide with text embedded in the pixels. The full slide's elements/layouts are NOT individually editable; a tool can extract text into overlay text boxes. Each regeneration/edit creates another image and consumes credits. It is incorrect to describe ALL Gamma slides as natively editable semantic elements.

Official:
- https://help.gamma.app/en/articles/11047840-how-can-i-import-slides-or-content-into-gamma
- https://help.gamma.app/en/articles/17238075-what-are-image-slides-and-how-do-i-use-them

## F. Styles, components, and export limitations

- Theme is workspace-reusable, **Styles** is the gamma-specific copy in Gamma 5; can edit global fonts/colors/logo without replacing shared theme.
- Shape/image/fill controls per slide, logos/headers/footer on supported paid plans.
- Smart Charts allow editing data; older chart feature being deprecated.
- Gamma exports PPTX/PDF and image formats. Tables export as native editable tables by default, at the expense of unsupported rounded corners; user can disable the table editability toggle.
- Gamma's own help documents real differences in export geometry, font substitution, zoom-to-fit, chart/diagram dimensions; published outputs reflect Present mode, not Edit mode. Thus "pixel-perfect, lossless" would be an exaggeration.
- Gamma sites can be published on gamma.site free and custom domains Pro+; Gamma 5 Agent cannot directly generate or publish webpage-format sites from home, though the resulting gamma can later be published via editor.
- Full presentation analytics such as unique viewers, view depth and relative time per slide are Pro+; site analytics is separate and generally requires Google Analytics/Tag Manager.

Official:
- https://help.gamma.app/en/articles/11029150-how-do-i-customize-themes-colors-and-fonts-in-gamma
- https://help.gamma.app/en/articles/11029098-how-can-i-generate-charts-and-diagrams-in-gamma
- https://help.gamma.app/en/articles/8022861-what-s-the-easiest-way-to-export-my-gamma
- https://help.gamma.app/en/articles/15939201-why-doesn-t-my-exported-pdf-or-powerpoint-match-what-i-see-in-gamma
- https://help.gamma.app/en/articles/8429268-how-do-i-create-publish-a-site-in-gamma
- https://help.gamma.app/en/articles/11047329-how-do-i-track-my-gamma-s-performance-using-analytics

## G. Contradictions and stale documents to prevent in the REA

1. Some older Gamma developer docs say the API **cannot edit existing gammas**. Newer 2026 help and the official `n8n-nodes-gamma` source document `/v1.0/agent/gammas/{gammaId}/edits`. Date-grade sources; don't repeat the old limitation.
2. Gamma markets a "redesigned freeform editor" while current docs specify a structured proportional **grid as default** and freeform boxes only where desired. It is a hybrid editor, not unconstrained coordinates everywhere.
3. "Fully editable" cannot be applied to Image slides, which are raster images by design.
4. Gamma advertises import/export fidelity, while its own troubleshooting guides enumerate font/layout differences; performance must be measured, not inferred.
5. Gamma lists various integrations, but an integration's ability to read/create/edit depends on plan, API type, role and credits. Do not imply every connector has all permissions.
6. The gamma-app GitHub organization contains forks. A fork is **not** evidence its upstream code was written by Gamma or is used in current product.

## H. Unverified live product operations

Actual Gamma 5 Pro/Max generation, source-grounded web research, true editable PPTX import, element-level revisions, concurrent collaboration, native chart export, AI agent hidden prompt/model cascade and private JavaScript source maps were **not exercised or accessed** in Vivaldi during this study. Preserve this limit in any final product parity statement.
