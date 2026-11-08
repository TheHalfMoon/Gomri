> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/build-with-gamma/brand-template-editing-controls.md).

# Brand, template, and editing controls

What the Gamma API and MCP preserve, what they can change, and which operation controls brand, template, content, and revisions.

This page answers one question for each part of a gamma: when you generate or edit through the API or MCP, is it kept, can you change it, and what controls it. Each row says whether the behavior is **enforced** (cannot be overridden by a request), a **default** (applies unless you pass a parameter), or **prompt-directed** (the model decides from your instruction, so results vary). [Theme vs template](#theme-vs-template) defines the two terms the rows use. Link to a row directly with its anchor.

Verified against the Gamma 5 and Classic endpoints on 2026-10-20. Endpoint behavior is in the [OpenAPI reference](/agent-gamma-5/create-agent-generation.md); MCP tool behavior is in the [MCP tools reference](/mcp/mcp-tools-reference.md).

## Theme vs template <a href="#theme-vs-template" id="theme-vs-template"></a>

Two different things carry your branding, and a request uses one or the other:

|                  | Theme                                                                                                                                                                         | Template                                                                                                                                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What it is       | The look: colors, fonts, backgrounds, and card styling. Themes are created in the Gamma app and listed by [`GET /themes`](/workspace/list-themes.md) or `get_themes`.         | A gamma used as a starting point: its cards, layouts, and example content, plus the theme it was built with. Found with [`GET /templates/search`](/management/search-templates.md) or `search_templates`. |
| What it controls | Styling only. The agent still decides the structure and writes the content.                                                                                                   | Structure and styling. The content is rewritten from your prompt.                                                                                                                                         |
| Parameter        | `themeId`                                                                                                                                                                     | `templateId` on `POST /agent/generations` (also used by MCP `generate_from_template`); `gammaId` on Classic `POST /generations/from-template`                                                             |
| Together?        | No. A template brings its own theme, so `themeId` is rejected when a template is set (Classic from-template is the exception: there `themeId` replaces the template's theme). |                                                                                                                                                                                                           |

Pick a theme when you want on-brand styling and are happy for Gamma to design the structure; pick a template when the structure matters too.

## Brand styling <a href="#brand-styling" id="brand-styling"></a>

|            |                                                                                                                                                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Preserved  | Generating from a template keeps the template's theme. Edits never change the theme.                                                                                                                               |
| Can change | `themeId` restyles a generation that is not based on a template (`POST /agent/generations`, Classic `POST /generations`, MCP `generate`). On Classic from-template calls, `themeId` replaces the template's theme. |
| Controls   | `themeId`; the template's own theme; workspace default theme                                                                                                                                                       |
| API vs MCP | Same. `generate_from_template` rejects `themeId`, like `templateId` on the agent endpoint.                                                                                                                         |
| Defaults   | Classic `POST /generations` without `themeId` uses the workspace default theme. `POST /agent/generations` has no default theme: pass `themeId` or `templateId` to get your branding; passing both is rejected.     |
| Type       | **Default** (theme choice), **enforced** (edits cannot restyle)                                                                                                                                                    |

## Template structure <a href="#template-structure" id="template-structure"></a>

|            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preserved  | With `templateId` on `POST /agent/generations` (recommended), the template's structure is kept to the degree your prompt asks: "follow this template exactly; only replace the content" keeps card order and layouts, while a loose prompt lets the agent add, drop, or reorder cards. Rules saved in the template itself ([template instructions](#template-instructions), including locked slides) apply on every generation without being repeated in the prompt. Accepts workspace templates, any gamma in the workspace, and official Explore templates. |
| Can change | Anything the prompt allows. On the Classic REST route (`POST /generations/from-template`) structure is kept automatically, but only single-page workspace templates within the plan's card limit are accepted; Explore, non-template, archived, and site-bound gammas are rejected.                                                                                                                                                                                                                                                                           |
| Controls   | `templateId` and the prompt (`POST /agent/generations`; MCP `generate_from_template` pins `gammaId` as `templateId`); `gammaId` on Classic `POST /generations/from-template`                                                                                                                                                                                                                                                                                                                                                                                  |
| API vs MCP | `generate_from_template` is the MCP form of `POST /agent/generations` with `templateId`, but it takes a template saved in the user's workspace as `gammaId`; for any gamma in the workspace or an Explore template, call the REST endpoint.                                                                                                                                                                                                                                                                                                                   |
| Defaults   | Prompt-directed on the agent endpoint (state what to keep); preserved automatically on Classic from-template calls.                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Type       | **Prompt-directed** (agent `templateId`, MCP `generate_from_template`), **default** (Classic REST from-template)                                                                                                                                                                                                                                                                                                                                                                                                                                              |

### Template instructions and locked slides <a href="#template-instructions" id="template-instructions"></a>

For fine-grained control over how a template is applied, put the rules in the template rather than in every request. In the Gamma app, a template owner can add **template-level instructions** (overall guidance such as tone, audience, or "always fill in the pricing table"; Template settings → Instructions), **slide-level instructions** (a note on each slide saying what belongs there), and **lock** any slide that generation must leave untouched, such as a cover, legal disclaimer, or pricing slide. The instructions are stored invisibly in the template, never appear in the generated gamma, and are read every time Gamma generates from that template, so an API or MCP prompt only needs to carry the brief. Locks are honored by generation, not by human editors: anyone with edit access can still change a locked slide afterwards. There is no API parameter for any of this; it is set in the template. See [What are template instructions and how can I use them?](https://help.gamma.app/en/articles/16056626-what-are-template-instructions-and-how-can-i-use-them) in the Help Center.

## Content and placeholders <a href="#content-and-placeholders" id="content-and-placeholders"></a>

|            |                                                                                                                                                                                                                                                                                                                                                                |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preserved  | Slides locked in the template's [instructions](#template-instructions) are carried over unchanged. Everything else is guidance for what each card should contain; the model rewrites it from your prompt.                                                                                                                                                      |
| Can change | All text, images, and layouts within a card. Charts and tables are produced from the prompt and from `additionalInstructions` / `textOptions` on Classic calls; there are no chart-specific parameters. Images follow `imageOptions` (`source`, `model`, `style`) or image URLs in your text.                                                                  |
| Controls   | The prompt or `inputText`; `textOptions` and `imageOptions` (Classic); `cardOptions.dimensions` and `cardSplit` (Classic); `format` and `numCards` where supported                                                                                                                                                                                             |
| API vs MCP | Same parameters where the tool exposes them; see each tool's table.                                                                                                                                                                                                                                                                                            |
| Defaults   | Placeholder text that your prompt does not cover is filled by the model, not left as-is. There is no request parameter to lock an element; locking is done per slide in the template's instructions. To keep a block verbatim when you are not generating from a template, include it in the prompt and say so; this is prompt-directed and should be checked. |
| Type       | **Prompt-directed**                                                                                                                                                                                                                                                                                                                                            |

## Revisions <a href="#revisions" id="revisions"></a>

|            |                                                                                                                                                                                                                            |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preserved  | Everything the edit instruction does not mention. Theme, layout of untouched cards, sharing settings, and the gamma's URL stay the same.                                                                                   |
| Can change | Text, images, charts, and layout of the cards the instruction targets; adding or removing cards when asked. Edits do not change the gamma's format.                                                                        |
| Controls   | `POST /agent/gammas/{gammaId}/edits` / `edit_gamma` with a `prompt` (1–10,000 characters); `disableConnectors` to keep workspace connectors out of the edit                                                                |
| API vs MCP | Same job and same `editId` / `get_edit_status` lifecycle. The Slack app does not expose the edit tools.                                                                                                                    |
| Defaults   | One edit runs on a gamma at a time; a second request while one is pending is rejected. Edits require edit access to the gamma and charge credits; the completed status reports `credits.deducted` and `credits.remaining`. |
| Type       | **Prompt-directed** (what changes), **enforced** (one edit at a time, edit access)                                                                                                                                         |

## Verification <a href="#verification" id="verification"></a>

|                     |                                                                                                                                                                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| What you can read   | `read_gamma` (MCP only) returns the gamma's content as text. `GET /gammas/{gammaId}` returns metadata: title, card count, URL, timestamps. `GET /gammas/{gammaId}/comments` / `get_gamma_comments` return comments. Analytics endpoints and tools return views, time on card, and viewers for gammas you can edit. |
| What you can export | PDF, PPTX, or PNG for any non-archived gamma in the workspace you can view, via `POST /gammas/{gammaId}/export` / `export_gamma`; download URLs expire after about one week.                                                                                                                                       |
| Controls            | Status polling: `GET /agent/generations/{id}`, `GET /agent/edits/{id}`, `GET /generations/{id}`, `GET /exports/{id}` and their MCP `get_*_status` tools                                                                                                                                                            |
| API vs MCP          | Content reading is MCP-only; archive and delete are REST-only.                                                                                                                                                                                                                                                     |
| Defaults            | Generation and edit results are not validated against the template or prompt by Gamma. Check the result (read it, export it, or open it) before relying on it.                                                                                                                                                     |
| Type                | **Enforced** (access scoping), **not provided** (automatic validation)                                                                                                                                                                                                                                             |

## Summary

|                     | Controls                                                                                                                                                                                                                                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Enforced**        | Access: edit access for edits, view access for reads and exports. One edit runs on a gamma at a time.                                                                                                                                                                                                                                            |
| **Default**         | Theme: Classic from-template keeps the template's theme unless `themeId` replaces it; agent generation has none, so pass `themeId` or `templateId`. Template instructions and locked slides: set in the template, applied on every generation (no per-element lock in a request). Structure is kept automatically on Classic REST from-template. |
| **Prompt-directed** | Template structure with agent `templateId` and MCP `generate_from_template` (ask for it in the prompt). Text, images, and charts. The scope of an edit.                                                                                                                                                                                          |

## Related

* [Generate branded content from approved templates](/build-with-gamma/branded-template-workflow.md): the template loop end to end
* [Connect your own agent to Gamma](/build-with-gamma/connect-your-own-agent.md): running it from your own MCP client
* [Generate from template (Classic)](/guides/create-from-template-api-parameters-explained.md): Classic REST from-template parameters
* [API scope and limits](/reference/common-feature-requests.md): what the API and MCP can and cannot do


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/build-with-gamma/brand-template-editing-controls.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
