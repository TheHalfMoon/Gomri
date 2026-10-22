> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/get-started/understanding-the-api-options.md).

# Explore the API

How the Gamma API works — generate, edit, read, search, export, and analytics endpoints — and when to use the REST API versus the MCP server.

The Gamma API generates polished presentations, documents, social posts, and (on the Classic endpoints) webpages from text or from a workspace template, edits existing gammas, reads and searches your workspace, exports to PDF, PPTX, or PNG, and reports engagement analytics. Every job that generates, edits, or exports runs asynchronously: you create it, poll for status, and retrieve the result.

Most of these capabilities are also available to AI agents as MCP tools; archiving and deleting a gamma are REST-only. See [Set up the MCP server](/mcp/gamma-mcp-server.md). For the exact request schema, field types, and response contract, see the individual endpoint reference pages.

### How it works

{% stepper %}
{% step %}

#### Create a generation

`POST /v1.0/agent/generations` with a `prompt` and, optionally, a `templateId`, `format`, `numCards`, and `exportAs`. You get back a `gen_`-prefixed `generationId`.
{% endstep %}

{% step %}

#### Poll for status

`GET /v1.0/agent/generations/{generationId}` every 5 seconds until `status` is `completed` or `failed`. While still `pending`, optional `progress` reports card counts and an estimated `percent` once building starts.
{% endstep %}

{% step %}

#### Get your result

The completed response includes `gamma.gammaUrl` (view it in Gamma), `gamma.gammaId` for later edits, exports, archive, or delete, `result.summary`, and `exportUrl` when you asked for an export (PDF, PPTX, or a PNG `.zip` with one image per card).
{% endstep %}

{% step %}

#### Edit, export, or archive later

`POST /v1.0/agent/gammas/{gammaId}/edits` edits your gamma from a natural-language instruction. `POST /v1.0/gammas/{gammaId}/export` exports any gamma in your workspace that you can view. `POST /v1.0/gammas/{gammaId}/archive` removes it from the active workspace; `DELETE /v1.0/gammas/{gammaId}` deletes it (workspace admin).
{% endstep %}
{% endstepper %}

See [Poll for results](/guides/async-patterns-and-polling.md) for full implementation examples in Python, JavaScript, and cURL.

### Quick reference

* **Gamma 5 (recommended):** use `POST /v1.0/agent/generations` to have the Gamma agent create a gamma from a prompt, optionally starting from a template or existing gamma (`templateId`), and `POST /v1.0/agent/gammas/{gammaId}/edits` to edit an existing gamma from a natural-language instruction. Poll `GET /v1.0/agent/generations/{generationId}` and `GET /v1.0/agent/edits/{editId}`.
* **Classic:** `POST /v1.0/generations` and `POST /v1.0/generations/from-template` run the older Classic engine. They keep working for existing integrations; start new integrations on the agent endpoints.
* Both Classic endpoints accept an optional `title` when you want to set the Gamma name explicitly; poll `GET /v1.0/generations/{generationId}`.
* Use `GET /v1.0/themes` and `GET /v1.0/folders` to look up IDs before generation.
* Use `POST /v1.0/gammas/{gammaId}/archive` to remove a Gamma from the active workspace. Pass the file ID from the poll response, not the web app URL slug.
* Use `DELETE /v1.0/gammas/{gammaId}` when you need to remove a Gamma entirely. This requires a workspace admin role.
* Use `GET /v1.0/gammas/search`, `GET /v1.0/templates/search`, `GET /v1.0/gammas/{gammaId}`, and `GET /v1.0/gammas/{gammaId}/comments` to find and inspect existing gammas, and `POST /v1.0/gammas/{gammaId}/export` to export any gamma in your workspace that you can view.

### Gamma 5 agent endpoints and Classic endpoints

The agent endpoints run Gamma 5, Gamma's agent engine, and are the recommended path for new integrations. The Classic endpoints run the previous engine and remain available for integrations already built on them.

|                     | Agent generation (Gamma 5)                                                                                                                                                                     | Agent edit (Gamma 5)                                                                                              | Generate (Classic)                                                                                                                                                               | Create from template (Classic)                                                                                                                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Endpoint**        | `POST /v1.0/agent/generations`                                                                                                                                                                 | `POST /v1.0/agent/gammas/{gammaId}/edits`                                                                         | `POST /v1.0/generations`                                                                                                                                                         | `POST /v1.0/generations/from-template`                                                                                                                                                                           |
| **When to use**     | Describing the outcome and letting the Gamma agent plan and build the gamma, optionally starting from a workspace template, an existing gamma, or an official Explore template (`templateId`). | Editing an existing gamma from a natural-language instruction, like "update the pricing card with the new tiers." | Creating from scratch with explicit parameters — you control format, tone, audience, images, layout, and more. The only way to generate webpages and multi-page gammas or sites. | Adapting a gamma saved as a template in your workspace — swap content, retarget the audience, transform the subject, replace images, or restructure cards. Design once in the Gamma app, reuse programmatically. |
| **Required fields** | `prompt`                                                                                                                                                                                       | `prompt`                                                                                                          | `inputText` or `pages`                                                                                                                                                           | `prompt` + `gammaId`                                                                                                                                                                                             |
| **Structure**       | The agent decides, or follows the `templateId` source.                                                                                                                                         | The gamma is revised in place.                                                                                    | Gamma determines the layout from your parameters.                                                                                                                                | The template's structure is preserved by default; your prompt can also change content, audience, card count, or order.                                                                                           |
| **Pricing**         | By the work the agent does                                                                                                                                                                     | By the work the agent does                                                                                        | Per card and per image                                                                                                                                                           | Per card and per image                                                                                                                                                                                           |

`POST /agent/generations` accepts `format` (`presentation`, `document`, or `social`; for a webpage use the Classic `POST /generations`), `numCards`, `quality`, `themeId` or `templateId`, `sourceUrls`, `additionalInstructions`, `exportAs`, `sharingOptions`, `folderId`, and `disableConnectors`. The Classic endpoints support `title`, `themeId`, `exportAs`, `sharingOptions`, and `folderId`. On the Classic endpoints, omitting `themeId` keeps the template's theme (`from-template`) or applies the workspace default (`generations`). On `POST /agent/generations` there is no default theme: pass `themeId` or `templateId` to get your branding. See the full reference for each:

* [POST /agent/generations](/agent-gamma-5/create-agent-generation.md) and [POST /agent/gammas/{gammaId}/edits](/agent-gamma-5/edit-gamma.md)
* [Generate API Parameters](/guides/generate-api-parameters-explained.md) (Classic)
* [Create from Template Parameters](/guides/create-from-template-api-parameters-explained.md) (Classic)

### Key parameters at a glance

| Parameter                  | What it controls                   | Example values                                                                                     |
| -------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------- |
| `title`                    | Explicit Gamma title               | `"Q3 Board Update"`                                                                                |
| `format`                   | Output type                        | `presentation`, `document`, `webpage`, `social`                                                    |
| `textMode`                 | How input text is interpreted      | `generate` (topic → content), `condense` (summarize), `preserve` (keep as-is)                      |
| `themeId`                  | Brand theme (colors, fonts, logo)  | Get IDs from `GET /v1.0/themes`                                                                    |
| `numCards`                 | Number of slides/sections          | `1`–`75`                                                                                           |
| `exportAs`                 | Auto-export on completion          | `pdf`, `pptx`, `png`                                                                               |
| `imageOptions.source`      | Where images come from             | `aiGenerated`, `webFreeToUseCommercially`, `noImages`                                              |
| `textOptions.tone`         | Writing style                      | Any string: `"professional"`, `"casual"`, `"academic"`                                             |
| `textOptions.audience`     | Who the content is for             | Any string: `"executives"`, `"new hires"`, `"students"`                                            |
| `cardOptions.headerFooter` | Logo, page numbers, text           | 6 positions per card — see [Header and Footer Formatting](/guides/header-and-footer-formatting.md) |
| `sharingOptions`           | Permissions on the generated gamma | Workspace, external link, and email access levels                                                  |

### Read, search, export, and manage

| Endpoint                                                                                                                    | Purpose                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /v1.0/gammas/{gammaId}`                                                                                                | Get a gamma's metadata, such as title, theme, and URLs.                                                                                                                                                                           |
| `GET /v1.0/gammas/search`                                                                                                   | Full-text search over the titles and body text of gammas the caller can access.                                                                                                                                                   |
| `GET /v1.0/templates/search`                                                                                                | Search workspace templates (usable as `gammaId` for Classic template generation or `templateId` for agent generation) and official Explore templates (usable as `templateId` for agent generation).                               |
| `GET /v1.0/gammas/{gammaId}/comments`                                                                                       | List comment threads and replies on a gamma.                                                                                                                                                                                      |
| `POST /v1.0/gammas/{gammaId}/export`                                                                                        | Export a gamma in your workspace to PDF, PPTX, or PNG. You need view access, and archived gammas can't be exported. Poll `GET /v1.0/exports/{id}` for the download URL.                                                           |
| `POST /v1.0/images`                                                                                                         | Generate a standalone on-brand image. Poll `GET /v1.0/images/{id}`.                                                                                                                                                               |
| `POST /v1.0/images/media/{savedMediaId}/archive`                                                                            | Remove an image you created from your workspace media library. The file is not deleted, and existing image URLs keep working.                                                                                                     |
| `GET /v1.0/themes`                                                                                                          | List available themes (standard + custom workspace themes). Use the `id` as `themeId`.                                                                                                                                            |
| `GET /v1.0/folders`                                                                                                         | List workspace folders. Use a folder `id` as `folderId`.                                                                                                                                                                          |
| `POST /v1.0/gammas/{gammaId}/archive`                                                                                       | Archive a Gamma. Uses the `gammaId` returned by a completed generation.                                                                                                                                                           |
| `DELETE /v1.0/gammas/{gammaId}`                                                                                             | Delete a Gamma. Requires a workspace admin role.                                                                                                                                                                                  |
| `GET /v1.0/gammas/{gammaId}/analytics` and `.../analytics/cards`, `.../analytics/viewers`, `.../analytics/viewers/{userId}` | Engagement analytics: views, unique viewers, per-card time, and per-viewer detail. Requires edit access to the gamma; with manage access, results cover all viewers, otherwise only your own activity. Data updates about hourly. |

Theme, folder, comment, and viewer listings use cursor-based pagination: check `hasMore` and pass `nextCursor` as `after`. Viewer analytics returns at most 500 viewers in total. Gamma and template searches don't use cursors: each returns up to `limit` hits (maximum 25; for template search, per list). With `q`, gamma results are ranked by relevance and workspace templates on a best-effort basis (`workspaceDegraded` is `true` when they fall back to last-edited order). Without `q`, gamma search needs at least one of `createdBy`, `updatedAfter`, or `updatedBefore` and returns the most recently updated gammas first; use those filters to reach older gammas.

### REST API or MCP server?

|                              | REST API                                                                                                                                                                                         | MCP server                                                                                                                                                                                                                                                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Who decides what to call** | Your code                                                                                                                                                                                        | An AI agent, at runtime                                                                                                                                                                                                                                                                                            |
| **Auth**                     | API key (Pro, Ultra, Teams, Business, Enterprise) or OAuth on behalf of your users                                                                                                               | OAuth with Dynamic Client Registration, on any plan. Custom clients need their redirect URIs registered with Gamma first ([request access](/mcp/gamma-mcp-server.md#connect-your-own-agent-or-mcp-client)).                                                                                                        |
| **Typical use**              | Backend jobs, automation platforms, apps with their own UI                                                                                                                                       | Custom agents, assistants, developer tools that load MCP servers                                                                                                                                                                                                                                                   |
| **Capabilities**             | Gamma 5 agent generation and edits, Classic generation (including multi-page gammas with `pages`) and template generation, read, search, comments, export, images, analytics, archive and delete | The same core set as tools (`generate`, `generate_multi_page_gamma`, `generate_from_template`, `edit_gamma`, `search_gammas`, `search_templates`, `get_gamma_comments`, `export_gamma`, `generate_image`, analytics tools), plus `read_gamma` for a gamma's content. Archiving and deleting a gamma are REST-only. |

See [Set up the MCP server](/mcp/gamma-mcp-server.md) for connection requirements.

### Authentication

REST requests use an API key in the `X-API-KEY` header. Generate your key from [Account Settings > API Keys](https://gamma.app/settings/api-keys).

```bash
curl https://public-api.gamma.app/v1.0/themes \
  -H "X-API-KEY: $GAMMA_API_KEY"
```

If your app acts on behalf of its own users, the API also accepts OAuth 2.0 Bearer tokens on the same endpoints — see [Authenticate with OAuth](/get-started/authenticate-with-oauth.md).

API access requires a Pro, Ultra, Teams, Business, or Enterprise plan. See [Access and Pricing](/get-started/access-and-pricing.md) for credit costs and plan details.

{% hint style="info" %}
**Not a developer?** You can also use Gamma through [connectors and integrations](/connectors/connectors-and-integrations.md) — no code required.
{% endhint %}

### Related

* [Generate from text](/guides/generate-api-parameters-explained.md) for a parameter-by-parameter walkthrough of `POST /v1.0/generations`
* [Generate from a template](/guides/create-from-template-api-parameters-explained.md) for the template-based remix workflow
* [Poll for results](/guides/async-patterns-and-polling.md) for complete polling implementations
* [Connect your own agent](/build-with-gamma/connect-your-own-agent.md): hosted MCP server for a custom agent or client
* [Generate from approved templates](/build-with-gamma/branded-template-workflow.md): end-to-end branded workflow
* [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md): what is preserved, what can change


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/get-started/understanding-the-api-options.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
