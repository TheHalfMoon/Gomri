> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/mcp/gamma-mcp-server.md).

# Set up the MCP server

Connect your own AI agent or MCP client to Gamma's hosted MCP server to generate, read, edit, and export gammas. Also powers the Gamma connectors in ChatGPT, Claude, and Slack.

Gamma MCP is a hosted server at `https://mcp.gamma.app/mcp` that gives any MCP client tools to create branded presentations, documents, webpages, and social posts; generate from workspace templates; read, search, and edit existing gammas; export to PDF, PPTX, or PNG; and read comments and engagement analytics. The Gamma connectors in ChatGPT and Claude and the Gamma app for Slack run on this server, and you can connect your own agent to it. [Access requirements and connection steps](#connect-your-own-agent-or-mcp-client) are below.

{% hint style="info" %}
**Looking for general Gamma help?** This page covers MCP server setup for developers. For general guidance on using Gamma with AI assistants, see [How do I use Gamma with connectors and integrations?](https://help.gamma.app/en/articles/13943863-how-do-i-use-gamma-with-connectors-and-integrations) in the Help Center.
{% endhint %}

### Quick reference

* Server URL: `https://mcp.gamma.app/mcp`. Works with any AI tool that supports the Model Context Protocol and OAuth with Dynamic Client Registration.
* Available on all Gamma plans. Generations, edits, and images charge credits the same way as the API; reading, searching, and exporting do not.
* Gamma MCP supports generating from scratch, generating multi-page Gammas, generating from templates, checking generation status, generating standalone images, editing existing gammas, exporting existing gammas, browsing existing gammas, searching gammas by content, searching templates, reading gammas, reading comments, viewing engagement analytics, browsing themes, and browsing folders.
* Reading and exporting require view access to the Gamma in the connected workspace.
* Once a generation completes, its generation ID can be used to read, edit, or export the new Gamma straight away, without looking up the Gamma's file ID.
* Editing requires at least edit access to the Gamma. Edits change the gamma you point at and cannot add new pages. One edit runs on a gamma at a time.
* Custom clients authenticate with OAuth and Dynamic Client Registration. Redirect URIs must be registered with Gamma before the first connection; see [Connect your own agent or MCP client](#connect-your-own-agent-or-mcp-client).
* See [MCP tools reference](/mcp/mcp-tools-reference.md) for full tool details, parameter tables, and authentication guidance.

### Capabilities

{% hint style="info" %}
Some platforms review app updates before making them available to users. If functionality listed here is not available in your AI tool, the latest version of the Gamma app may still be in review. This applies to applications such as ChatGPT and Codex, where OpenAI reviews each update.
{% endhint %}

**Generate from scratch** -- create presentations, documents, webpages, or social posts with control over text density, tone, audience, language, images, themes, layout, headers/footers, export format, and sharing permissions.

**Generate a multi-page Gamma** -- create one Gamma with several distinct pages under a single URL in one request, with per-page content and settings. Ideal for sales rooms, proposal sites, and microsites.

**Generate from a template** -- create a new gamma from an existing template gamma. By default, Gamma preserves the template's structure while adapting the content to a new audience, topic, or use case.

**Check generation status** -- poll long-running generation jobs until they complete or fail.

**Generate standalone images** -- create a single image from a text prompt as an illustration, scene, photo, or abstract graphic, with a choice of aspect ratio and optional theme branding. The image generates in the background; check its status to get the image URL. Generated images are saved to your workspace media library, and the status result can include a link to them there.

**View engagement analytics** -- see how a gamma is performing: total views, unique viewers, per-card engagement, and who viewed it.

**Read comments** -- list the comment threads and replies on an existing gamma.

**Browse existing gammas** -- search or list gammas and templates that already exist in the connected workspace, and search workspace templates alongside the official Gamma explore templates.

**Search gammas by content** -- run a full-text search over the titles and body text of gammas the user can access, with filters for creator and last-updated time. Each hit can come back with a text snippet, usually centered on the match, and the creator's name or email.

**Read existing gammas** -- retrieve the full content of a presentation or document when you provide a Gamma file ID or URL. This tool is read-only and cannot modify the Gamma.

**Edit existing gammas** -- change the content of a gamma you already have from a natural-language instruction: reword, restructure, add, or remove content. The edit runs in the background; check its status to get a summary of the changes. Edits apply to a gamma's existing pages and cannot add new pages.

**Export existing gammas** -- export a gamma you already have to PDF, PPTX, or PNG (PNG returns a `.zip` with one PNG per card). The export runs in the background; check its status to get the download link.

**Browse themes** -- search Gamma's theme library by name. Each theme includes tone and color keywords to help match your style.

**Organize to folders** -- browse or search your Gamma folders and save generated content to specific locations.

### Getting started

There are two ways to use the server:

* **Use an existing connector.** ChatGPT, Claude, Slack, Superhuman Go, and Atlassian Rovo ship with Gamma in their libraries. You need a Gamma account on any plan; setup varies by platform -- see [Connect integrations](/connectors/connectors-and-integrations.md).
* **Connect your own agent or MCP client.** Point your client at `https://mcp.gamma.app/mcp` and complete the OAuth flow. See [Connect your own agent or MCP client](#connect-your-own-agent-or-mcp-client) for what access requires.

### Tips for best results

* Be specific about structure: "create a 10-slide marketing strategy covering target audience, channels, budget, and metrics" works better than "make a presentation about marketing."
* Describe your style upfront: "professional and minimal," "colorful and creative," "corporate and clean."
* Specify the format: presentation, document, webpage, or social post.
* Control text density: "keep slides brief with bullet points" or "include detailed explanations."
* Mention folder names if you want content organized: "save to my Marketing folder."
* Request exports when needed: "export as PowerPoint" or "generate a PDF."
* Name the change you want when editing an existing gamma: "make the tone more formal throughout" or "replace the pricing card with our new tiers."

### Connect your own agent or MCP client

This is the path for a custom harness, an internal agent, or a developer tool that lets you add MCP servers by URL. The step-by-step version, with a first workflow and troubleshooting, is [Connect your own agent](/build-with-gamma/connect-your-own-agent.md).

**What you need**

|                |                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Server URL     | `https://mcp.gamma.app/mcp`                                                                                                                                                                                                                                                                                                                                                                                                                |
| Gamma account  | Any plan. Credits are charged to the connected user's workspace.                                                                                                                                                                                                                                                                                                                                                                           |
| Authentication | OAuth 2.0 with PKCE, discovered the standard MCP way. Clients register through Dynamic Client Registration (DCR); your client or framework must support DCR, as there are no static client IDs.                                                                                                                                                                                                                                            |
| Redirect URIs  | Registration succeeds only if every redirect URI your client sends matches a pattern Gamma has allowlisted for it, so register your URIs with Gamma before the first connection. Allowlisted patterns are mostly HTTPS callbacks on the client's own hostname; a few app deep-link and loopback (`http://localhost:<port>`) patterns exist for onboarded desktop tools such as Cursor and Gemini CLI, and loopback redirects require PKCE. |
| Permissions    | On first connection the user picks a workspace and grants the client the permissions listed on the consent screen. Credits and access checks follow that user.                                                                                                                                                                                                                                                                             |

**Does your client already work?**

Clients whose redirect URIs are already registered (the connectors above, and a number of developer tools and agent platforms we have onboarded) connect without any setup: add the server URL and sign in. If your client's registration is rejected with a redirect URI error, it has not been onboarded yet -- request access below.

**Request access for a new client**

<a href="https://docs.google.com/forms/d/1y5EJFP8pbl2-0PfTQexcs5vsvWpnPj3Q9bKOaH_4wuE/viewform" class="button primary">Request MCP Access</a>

The form asks for your name, email, company, use case, the OAuth redirect URIs your client will use, and a logo for the consent page (SVG, PNG, or JPEG, 256x256 px). The Gamma team reviews requests and registers the redirect URIs. While you wait, you can prototype with the [REST API](/get-started/understanding-the-api-options.md) if your plan includes API keys (Pro and above); most MCP tools have a REST equivalent, but reading a gamma's full content (`read_gamma`) is MCP-only.

{% hint style="warning" %}
**Local development:** loopback redirect URIs are rejected unless your client's loopback pattern has been allowlisted. Include the exact local and production redirect URIs you need in the access request.
{% endhint %}

**Verify the connection**

After authorizing, list the server's tools. You should see `generate`, `generate_from_template`, `read_gamma`, `edit_gamma`, `export_gamma`, and the rest of the set in the [MCP tools reference](/mcp/mcp-tools-reference.md). Call `get_themes` or `get_folders` for a cheap end-to-end check that does not charge credits.

### Troubleshooting

<details>

<summary>Authentication errors</summary>

Your connection to Gamma may have expired or been revoked. Disconnect and reconnect the Gamma connector in your AI assistant to refresh authentication.

</details>

<details>

<summary>Connection problems</summary>

Make sure you're logged into both your AI assistant and your Gamma account before connecting. If issues persist, check your network connection.

</details>

<details>

<summary>Insufficient credits</summary>

Your account doesn't have enough credits. Purchase more at [Settings > Billing](https://gamma.app/settings/billing) or upgrade your plan.

</details>

<details>

<summary>Plan limits</summary>

The maximum card count, available image models, and credits come from your workspace's current Gamma plan. When a request exceeds one of these limits, your AI assistant tells you which limit applies and links to [Settings > Billing](https://gamma.app/settings/billing), where you can compare plans. If you upgrade, ask the assistant to retry; Gamma checks each request against your live plan.

</details>

<details>

<summary>Invalid parameters</summary>

Your AI assistant will typically retry with corrected values. If the issue persists, try rephrasing your request with simpler options.

</details>

### FAQ

<details>

<summary>Connectors, MCP, and API -- which should I use?</summary>

**No-code users:** Use Gamma connectors in Claude or ChatGPT, or the Gamma app for Slack, for conversational creation — or Zapier/Make/n8n for automated workflows.

**Developers:** Use Gamma MCP when an AI agent should decide what to create, read, edit, or export at runtime -- the agent picks tools and parameters itself. Use the [Gamma API](/get-started/understanding-the-api-options.md) when your own code controls the requests, needs API-key auth for a backend job, or runs on an automation platform. Both cover the core generate, read, edit, and export workflows; a few operations, such as archiving or deleting a gamma, are API-only.

</details>

<details>

<summary>Can I edit a gamma using MCP?</summary>

When `edit_gamma` and `get_edit_status` appear in your tool list, use `edit_gamma` with a Gamma file ID or URL and a natural-language instruction, then poll `get_edit_status` for the summary of changes. Edits change the existing gamma and cannot add new pages, and only one edit runs on a gamma at a time. For anything the tool cannot do, edit in the [Gamma app](https://gamma.app).

</details>

<details>

<summary>What can I request through Gamma MCP?</summary>

You can create new content with `generate`, browse existing gammas and templates with `get_gammas`, find gammas by their content with `search_gammas`, find workspace and explore templates with `search_templates`, create new content from a template with `generate_from_template`, check status with `get_generation_status`, generate a standalone image with `generate_image` (and retrieve it with `get_image_generation_status`), export an existing gamma to PDF, PPTX, or PNG with `export_gamma` (and retrieve the link with `get_export_status`), edit an existing gamma with `edit_gamma` (and check it with `get_edit_status`), browse themes and folders, and read existing Gamma presentations or documents with `read_gamma`. See the [MCP tools reference](/mcp/mcp-tools-reference.md) for the full tool list and parameter details.

</details>

<details>

<summary>Where can I learn more about MCP?</summary>

Visit the [Model Context Protocol website](https://modelcontextprotocol.io/) for technical details.

</details>

### Related

* [MCP tools reference](/mcp/mcp-tools-reference.md) for authentication, parameter tables, and error handling
* [Connect integrations](/connectors/connectors-and-integrations.md) for platform-specific setup instructions
* [Generate from text](/guides/generate-api-parameters-explained.md) for the full parameter reference
* [Access and pricing](/get-started/access-and-pricing.md) for credit costs and plan details
* [Connect your own agent](/build-with-gamma/connect-your-own-agent.md): step-by-step guide for a custom MCP client, with a first workflow and troubleshooting
* [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md): what generation and editing preserve


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/mcp/gamma-mcp-server.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
