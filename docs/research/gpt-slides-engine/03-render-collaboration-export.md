# GPT Slides Engine REA — 03: Rendering, Collaboration, Export, and Security

**Evidence boundary:** ChatGPT Slides public documentation proves what users can do, NOT the internal implementation. Everything labeled "Gomri design" below is an independent proposed approach.

## 1. Rendering stack: what can and cannot be inferred

Observed via OpenAI:
- Native *categories* of element editing: text, images, shapes, tables, charts.
- Direct and AI-driven layout modifications.
- Browser font picker and desktop system font behavior.
- Present and export flows.
These do NOT reveal use of HTML, SVG, Konva, Canvas, WebGL, native PowerPoint XML, or a proprietary WASM engine.

Gomri actually has a Presenton-derived scene editor and HTML preview. Concrete code in draft PR #88:
- servers/nextjs/components/slide-editor/** — interactive element editor;
- servers/nextjs/lib/template-v2-json-to-html.ts — typed/render-by-element HTML renderer for text, image, chart, table, SVG, infographic, flex/grid;
- servers/nextjs/components/slide-editor/text/text-direction.ts — Arabic/RTL handling added on draft branch;
- servers/nextjs/lib/slide-animations/** — animations from a bounded MIT NextSlide skill donor;
- @presenton/export-core v1.0.34 — PowerPoint/export runtime.

**Failure mode:** HTML preview may display an animation that the Konva editor and native PowerPoint exporter do not reproduce. Arabic shaping in a normal text element does not prove RTL chart axes/table cells are correct. Typography may reflow when system fonts are missing. These are distinct QA targets.

## 2. Render parity as a hard engine property

Keep exactly ONE semantic deck representation, and construct projections from it:

    Deck IR
      |-> Interactive editor renderer
      |-> HTML/presentation preview renderer
      |-> PPTX semantic export adapter
      |-> PDF pixel/document export adapter
      |-> Google Slides adapter

Every projection must preserve identical slide/object identity and semantic content where supported. Geometry may be adapted, but differences must be accounted for.

Measure:
- number of slides and typed elements rendered;
- text character/rich-run retention, paragraph alignment and Unicode logical order;
- chart series values/categories, axis labels and legend;
- table cell text, merged cells, row/column geometry;
- image crop, alpha, transform and asset linkage;
- object overlap, clipped text, invisible text, unused margins and density;
- speaker notes, chart objects, master/layout inheritance;
- rasterized object inventory with why it happened.

Proposed strict gates:
- 0 missing elements silently;
- 0 unsupported numeric claims without evidence state;
- 0 incorrect Arabic text order in frozen test fixtures;
- >=95% *supported target object types* retained as native editable PPTX objects (TARGET, not measured);
- >=98% frozen slides without unintended clipping (TARGET, not measured);
- every unsupported export downgrade logged.

## 3. Existing real export evidence and its limitations

The previous Gomri integration branch PR #88 passed real local Windows tests:
- 55 root tests;
- 148 Next.js tests with 0 skips;
- 15 PPTX export -> reimport fidelity tests;
- a Next.js production build.
These statements are about THAT draft branch at the tested head and do not establish final product quality or a merged release.

The fidelity harness intentionally exposes limitations:
- speaker notes can exist in generated PPTX but be absent in reimported JSON;
- some bullets are converted to literal text;
- unsupported object properties can degrade on round trip.
Consequently the phrase "editable PPTX" is not a blanket promise of losslessness.

Use gitbrent/PptxGenJS (MIT) for a controlled 8-fixture trial against Presenton. It supports native OOXML charts/tables/shapes/slide masters and RTL, but needs source/asset and actual parity qualification. Do not replace a working exporter based on README claims.

## 4. Collaboration: official behavior, unknown algorithm

OpenAI docs confirm:
- editors can simultaneously edit one deck;
- shared comments, @teammate, @ChatGPT and @dot;
- view and edit permissions;
- permission inheritance from Space and parent page;
- separate source permissions;
- no dedicated comment-only Slides role at launch.

**Not public:** CRDT vs OT vs server-side sequencing, actual transport, storage engine, merge strategy, diff granularity, presence protocol or latency.

Independent Gomri solution options:
(A) a single authoritative server sequencer with per-object revisions + transaction log, initially simpler and easier to secure;
(B) a single CRDT provider such as Loro or Yjs, added only if concurrent/offline targets justify it and its output remains canonical.

Do NOT install two competing replicated document authorities. Keep ephemeral collaborator cursors separate from content history and access control.

### Concurrent test scenarios

- Editor A changes title, B changes chart -> both survive.
- A edits Arabic word; B inserts punctuation in same string -> valid Unicode sequence, no damaged glyph ordering.
- A deletes object while agent tries to alter it -> agent receives TARGET_GONE.
- A reorders slide while B comments on an anchored element -> comment remains on correct element.
- Two agents edit same chart from different versions -> conflict explicit; do not last-write-wins silently.
- Disconnect after local edit, reconnect -> no duplicates or hidden loss.
- User loses edit access during long generation -> commit refused at application time.
- Viewer forges agent mention -> no unauthorized mutation.
- Repeated comment delivery -> one job/one effect, one receipt.

## 5. Comment -> AI task pipeline (Gomri recommendation)

    comment created
      -> detect authorized @agent mention
      -> resolve anchored slide/element IDs and comment ID
      -> inspect actor/deck/source permissions
      -> snapshot deck revision
      -> create durable idempotent task
      -> propose typed patch
      -> scope, policy, evidence, layout checks
      -> preview / approval if consequential
      -> commit or conflict with audit receipt
      -> reply to originating comment

Do not trust raw comment text as a tool instruction with elevated priority; it is user data. A comment may request a legitimate action, but tool authority is independently verified on each call.

TheHalfMoon/Ninerr exposes a bounded, inspectable MCP call authorization system and attributed edit-history transactions. It is a better immediate code donor than guessing what the ChatGPT Slides backend uses.

## 6. Brand, templates, and design quality

Official behavior: style from example deck; use templates and uploaded images; create visuals; Work may preserve master and section order. Accurate template matching is NOT guaranteed even in the PowerPoint add-in.

Proposed pipeline:
1. Parse reference deck into master/layout inventory.
2. Extract theme tokens (fonts, colors, spacing, grids, media treatment, logo).
3. Match narrative roles to layout candidates.
4. Construct editable shapes instead of a single generated slide image.
5. Render and critique multiple candidates against a normalized source fixture.
6. Repair clipping/overlap/contrast in a deterministic pass.
7. Report unmatchable fonts and paid/third-party asset restrictions.

Candidates:
- TheHalfMoon/Skilit for design evidence, pattern and reusable brand knowledge.
- nexu-io/open-design for portable design-system and agent patterns under its advertised Apache-2.0, but its screenshot-backed slide outputs may not satisfy native PPTX editability.
- Presenton for the existing editor and template/layout production code.

## 7. Security and privacy constraints

Access to a shared deck does not automatically mean access to linked private sources. This is explicit in Space collaboration documentation.

Gomri must deny:
- viewer or revoked user writing via agent, comment, direct API or cached socket;
- cross-workspace source retrieval or inline secret display;
- malicious prompt instructions embedded in user-provided PPTX/PDF/web text;
- remote image URL accessing localhost or internal networks;
- zip traversal/bomb during PowerPoint import;
- script injection via SVG/HTML/markdown;
- unsanctioned model-provider network calls;
- hidden creation of paid cloud dependencies.

Write-time policy is essential: permissions may change while an AI job runs. Every job stores requester, task origin, allowed source IDs, scope, and revision; commit reevaluates authorization.

## 8. Platform branches: don't combine unrelated surfaces

OpenAI Slides web/Space, Windows desktop local fallback, native PowerPoint add-in and Work-generated artifacts have distinct availability and behavior. A successful sample created via Presentations plugin does NOT prove that the Space editor uses the same rendering engine or object schema.

For Gomri, qualify each surface separately: Windows desktop UI, macOS desktop UI, Linux self-hosted, web editor, exporter, agent MCP interface. Store exact hashes and environment evidence per run.

## 9. Observed vs proposed / unknown decisions

| Question | Official observation | Gomri decision | Still unknown about GPT Slides |
|---|---|---|---|
| Can user select and change chart? | Yes, category directly editable | Native typed chart element | Actual chart renderer |
| Does AI edit one selected element? | Selection-scoped Request edits | Stable IDs + typed patch | Internal patch representation |
| Can multiple people edit same deck? | Yes | Server sequencer first; CRDT after proof | Merge algorithm |
| Are comments agent prompts? | @ChatGPT/dot supported | Comment-triggered scoped job with ACL | Tool/task scheduling internals |
| Is export editable? | PowerPoint workflow advertised | Native object fidelity report | OpenAI loss rate |
| Is comment-only permission supported? | Not at Slides launch | View/edit first; independent comments later | Future rollout |
| Does GPT Slides use NextSlide code? | No verified disclosure | Independent donor sources only | Code provenance not public |

Sources:
https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt
https://learn.chatgpt.com/docs/space/collaboration
https://help.openai.com/en/articles/20001242-chatgpt-for-powerpoint
https://github.com/TheHalfMoon/Gomri/pull/88
https://github.com/TheHalfMoon/Ninerr/blob/main/docs/MCP.md
https://github.com/gitbrent/PptxGenJS/
https://github.com/loro-dev/loro
https://github.com/nexu-io/open-design
