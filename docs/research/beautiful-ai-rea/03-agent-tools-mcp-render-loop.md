# Beautiful.ai Deep REA — 03: New Agent/MCP Source, Slide Editing and Render-Verify-Save

Date: 2026-11-09. Inspected vendor-authored Apache-2.0 Beautiful.ai Claude and Grok plugins, exact source pins recorded in third_party/beautiful-ai-public/SOURCE_REGISTER.md. These are public Markdown instructions, element documentation, plugin manifests and MCP connection declarations. **They do not include or run the private renderer, backend or proprietary models.**

## A. Two different generations of MCP connector

The public Beautiful.ai support page for its older MCP connector describes OAuth-connected creation, lookup, templates, folders, themes, exports and explicitly denies arbitrary slide-by-slide modification. The published **new Beautiful.ai Claude plugin** (version 0.8.4, updated November 6, 2026) points to a newer agent MCP server and describes tools named get_slide, create_slide, update_slide, render_slide and lock_slides. The Grok plugin follows a similar new flow.

This is a time/versioned capability difference. It is incorrect to claim "Beautiful.ai MCP cannot edit slides" categorically, and equally incorrect to claim the newer tool set is universally available on all workspaces or in the old connector. No live account or OAuth was used in this study.

Sources:
https://support.beautiful.ai/hc/en-us/articles/44246954338829-Beautiful-ai-MCP-Quick-Setup-FAQ
https://github.com/beautifulai/claude-plugin
https://github.com/beautifulai/grok-plugin

## B. Published tool names and responsibilities (actual public source)

**User/workspace/context:** get_context, list_workspaces, list_themes, list_shared_themes, list_user_notes, read_user_note, write_user_note, list_shared_knowledge_notes, read_shared_knowledge_note, write_shared_knowledge_note.

**Presentation operations:** find_presentations, get_presentation, get_presentation_theme, get_presentation_links, create_presentation, update_presentation, export_presentation, open_presentation.

**Slide operations:** get_slide, create_slide, update_slide, lock_slides.

**Template operations:** list_slide_templates, get_slide_examples.

**Images/icons:** generate_image_asset, create_upload_url, save_image_asset, list_icons.

**Render/preview:** render_slide.

**Sharing:** create_public_link, create_password_protected_link, share_presentation_with_user.

These names describe client-visible tools in the publicly published skill; they are not copies of the private server's implementations.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-editing/SKILL.md

## C. Exact published agent editing algorithm

The published Beautiful.ai slide-editing source prescribes:

1. Inspect user/workspace context, preferences and Brand Kit.
2. Resolve target presentation/slide and read its current model; mark edited slides through lock_slides.
3. Inspect template defaultData/real examples, and the element reference.
4. Modify the **smallest** model fields necessary and preserve unrelated content/IDs.
5. Render the proposed model using render_slide with its theme; check returned visual image, renderErrors and pageErrors. Scale 0.5 offers cheaper preview; larger final scale for small text.
6. Repair visual defects and retry a bounded number of times (the public skill says at most three repair attempts).
7. Save via update_slide for existing slide or create_slide for new slide; render:true can reject unsuccessful render before save.
8. Release editor marking, report changed slides and any conversion of shared slides into owned copies.

**Critical limitation in public source:** lock_slides is described as a spinner/editor visual feedback device that blocks local editor manipulation but **does not provide authoritative concurrency control**. It would be dangerous for Gomri to substitute it for revision checking, lock ownership or optimistic concurrency control.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-editing/SKILL.md

### The real "AI agent edits" moat

The correct abstraction is not "one prompt rewrites all JSON". It is:

    target resolution
       -> context and evidence
       -> template/schema choice
       -> minimal typed modification
       -> render + evaluate
       -> explicit revision/permission validation
       -> commit and receipt
       -> optional user confirmation/undo

This is Gomri's recommended engine, NOT proof Beautiful.ai itself validates exact revisions or uses this sequence in every product path.

## D. Deck generation: show the skeleton early, fill slides progressively

The public presentation-building source advises an outline of roughly 6–12 slides for ordinary requests, selects Brand Kit and source images, and uses create_presentation with one placeholder per slide. A placeholder uses template_id = ai-generation and metadata isGenerating=true, with slidePrompt as a short description. The user can open the deck while the agent fills slides one at a time, rendering and verifying each before save.

**Design meaning:** perceived product speed depends on instant creation of a useful durable artifact and visible per-slide progress, not only total backend job latency. A placeholder model and resume-safe per-slide jobs can produce a better user experience even when actual generation is slow.

**Risk:** if a retry creates a second presentation instead of resuming the same presentationId and slideIds, it causes duplicate decks or reordered output. Implement exact job IDs, idempotency keys, and a durable stage receipt.

Source: https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-presentation-building/SKILL.md

## E. Template and visual critique behaviors

A separate public design skill calls for:
- visually interesting slides, not text-only default outputs where a meaningful picture/icon belongs;
- no wasted area, good use of the canvas, few well-proportioned dashboard cells;
- legible contrast, consistent type and source-aligned imagery;
- systematic variation in slide templates across the deck;
- inspect **rendered** slides, not just JSON validity, before saving.

The template-choice skill maps specific content types to presentation structures; more than 1/3 of slides on the same template is discouraged for design variety. Content may need to be shortened or split to stay within template's item limits.

Gomri must separate deterministic hard gates (data correctness, clipping, chart editability, ACL) from subjective visual preference (aesthetics), and evaluate both.

Sources:
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-design/SKILL.md
https://github.com/beautifulai/claude-plugin/blob/main/skills/beautiful-ai-slide-templates/SKILL.md

## F. Versioned model and template capability route

The public skill says:
- list_slide_templates returns IDs and template defaultData/capability flags;
- get_slide_examples provides real slide models of a template;
- get_slide returns existing object model; only modify intended fields;
- update_slide may require the full changed field (e.g. all of states), so **unrelated sibling content can be accidentally overwritten without a canonical transaction layer**;
- old version fields may invoke destructive model migration;
- libraryItemId can tie a slide to a shared library source and must be detached with a user-visible explanation before modifying the copy.

The newer agent tooling is powerful but still needs strict orchestration; public instructions themselves warn against blind source/model copying.

## G. Proposed independent Gomri Agent Tool Runtime

Use existing Presenton editor and W3 Narrative IR, then adopt:
- one canonical Deck IR with stable deck/slide/element IDs and per-element revisions;
- a typed per-object patch protocol instead of entire loose model snapshots;
- three-phase state: proposed patch -> preview and hard validation -> commit;
- idempotent create_presentation and per-slide retry/resume;
- render-before-save with typed failures (fit, visibility, numeric claim, accessible contrast, RTL, missing media);
- source ACL and workspace permissions checked **again at commit**, not just initial read;
- revision-based conflict detection independent of decorative lock_spinners;
- immutable undo journal / human-approved destructive operations;
- source + license receipts, local/offline provider option, no default paid Beautiful.ai dependency.

**Concrete owner source:** TheHalfMoon/Ninerr packages/mcp-protocol and studio-host/history already implement per-tool authorization, document scope and an Undo agent change journal. Adapt the smallest bounded slice, then test with Gomri's specific PPTX editable graph.

## H. 20 negative and positive acceptance probes

| Case | Required result |
|---|---|
| AG-01: select title and shorten only it | untouched slide/text/chart identical |
| AG-02: template switch with existing native table | no table cell lost |
| AG-03: duplicate create request | same deck returned, not duplicate |
| AG-04: one placeholder generated twice | exactly one finished slide |
| AG-05: render before save finds overflow | no destructive save |
| AG-06: renderErrors non-empty but image returned | reject model; image != success |
| AG-07: lock_slides mark set by agent | UI shown, not treated as exclusive authoritative lock |
| AG-08: human edits while agent composes | base revision conflict surfaced |
| AG-09: user revokes role during queued agent job | deny write at commit |
| AG-10: agent imports source with malicious instructions | source remains untrusted data |
| AG-11: same object changed by two agents | explicit resolution, no last-writer loss |
| AG-12: chart series update from a new source | exact data, units and citations checked |
| AG-13: Arabic with diacritics on chart and table | correct editor/preview/PPTX glyph order |
| AG-14: missing version fields in new slide | reject/migrate with no data loss |
| AG-15: style update to Brand Kit | explicit preview, preserve user overrides |
| AG-16: edit linked shared slide | user understands copy/detach |
| AG-17: generated visual with unlicensed remote image | block or show rights gate |
| AG-18: three failed layout repairs | keep prior good slide, return honest failure |
| AG-19: user cancels while image upload pending | release marks, no orphan/secret |
| AG-20: undo AI edit after later unrelated human edit | only compatible AI change undone |

**Current status:** code/skill snapshots obtained; no external MCP account connected, no executable agent integration into Gomri in this PR.
