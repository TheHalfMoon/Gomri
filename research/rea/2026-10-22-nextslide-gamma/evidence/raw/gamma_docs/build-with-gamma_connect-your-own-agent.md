> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/build-with-gamma/connect-your-own-agent.md).

# Connect your own agent

Connect your own AI agent or MCP client to Gamma: what access requires, how OAuth and DCR work, and how to verify the setup.

Gamma's hosted MCP server at `https://mcp.gamma.app/mcp` gives any MCP client the same tools that power the Gamma connectors in ChatGPT and Claude: generate presentations, documents, and social posts from a brief or from a workspace template, read and search gammas the user can access, edit them with a natural-language instruction, export to PDF, PPTX, or PNG, and read comments and engagement analytics. This guide is for a custom harness, an internal agent, or a developer tool that lets users add MCP servers by URL. For the tool-by-tool contract, see the [MCP tools reference](/mcp/mcp-tools-reference.md).

## Quick reference

* Server URL: `https://mcp.gamma.app/mcp`; works with any Gamma plan, including Free.
* Auth is OAuth 2.0 with PKCE and Dynamic Client Registration; every redirect URI must match Gamma's allowlist, so a new client [requests access](#request-access-for-a-new-client) first.
* The connected user's workspace and permissions apply to every tool call; `get_themes` is a free end-to-end check.
* Generations and edits consume credits; reads, searches, and exports do not.
* `read_gamma` is MCP-only; archive/delete are REST-only. Webpages and multi-page gammas use Classic generation on both sides (`generate_multi_page_gamma`, or `POST /generations` with `pages`).

## What access requires

|               |                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gamma account | Any plan, including Free. Generations, edits, and images charge the connected user's credits; reading, searching, and exporting are free.                                                                                                                                                                                                                                                                     |
| OAuth         | OAuth 2.0 with PKCE, discovered the standard MCP way from the server URL. There are no static client IDs: your client registers itself through Dynamic Client Registration (DCR), so the client or framework you use must support it.                                                                                                                                                                         |
| Redirect URIs | Registration succeeds only when every redirect URI your client sends matches a pattern Gamma has allowlisted. Hosted clients use an HTTPS callback on their own hostname; a few desktop tools we have onboarded (such as Cursor and Gemini CLI) use allowlisted loopback patterns. New clients [request access](#request-access-for-a-new-client) with their exact redirect URIs before the first connection. |
| Permissions   | On first connection the user picks a workspace and approves the permissions on the consent screen. Every tool call runs as that user in that workspace.                                                                                                                                                                                                                                                       |

**Already-registered clients** (the connectors, and the developer tools and agent platforms we have onboarded) connect with no setup: add the server URL and sign in. If registration fails with a redirect URI error, the client is not onboarded yet.

### Request access for a new client

<a href="https://docs.google.com/forms/d/1y5EJFP8pbl2-0PfTQexcs5vsvWpnPj3Q9bKOaH_4wuE/viewform" class="button primary">Request MCP Access</a>

The form asks for your name, email, company, use case, the OAuth redirect URIs your client will use, and a logo for the consent page (SVG, PNG, or JPEG, 256x256 px). The Gamma team reviews requests and registers the redirect URIs. Include the exact local and production redirect URIs you need. While you wait, you can prototype with the [REST API](/get-started/understanding-the-api-options.md) if your plan includes API keys (Pro and above); every workflow below has a REST equivalent except reading a gamma's content.

## Connect and verify

1. Add `https://mcp.gamma.app/mcp` to your client as a remote (streamable HTTP) MCP server. The client discovers the OAuth metadata, registers through DCR, and opens Gamma's sign-in page.
2. Sign in, pick the workspace, and approve the consent screen.
3. List the server's tools. You should see `generate`, `generate_from_template`, `read_gamma`, `search_gammas`, `search_templates`, `edit_gamma`, `export_gamma`, `get_gamma_comments`, the analytics tools, `get_themes`, and `get_folders`.
4. Call `get_themes` or `get_folders` for a free end-to-end check. Both return quickly and charge nothing.

{% hint style="info" %}
Reading and exporting need view access to the gamma in the connected workspace; editing needs edit access. A tool that returns a permission error is working correctly: the connected user cannot see or change that gamma.
{% endhint %}

## A first workflow

Every job that creates, edits, or exports runs asynchronously: a tool returns an ID, and a matching `get_*_status` tool reports `pending`, `completed`, or `failed`. Have your agent poll every few seconds.

| Step                       | Tool                        | What to pass                                                                                  | What comes back                                                                                |
| -------------------------- | --------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Find the approved template | `search_templates` with `q` | A phrase from the template's title                                                            | `workspaceTemplates[].id` for templates in the user's workspace                                |
| Generate on brand          | `generate_from_template`    | `gammaId` of a workspace template, `prompt` with the brief, optional `exportAs`               | `generationId`; poll `get_generation_status` until `completed` or `failed` for the gamma's URL |
| Check the result           | `read_gamma`                | The `generationId` or the gamma URL                                                           | The gamma's content as text                                                                    |
| Revise one thing           | `edit_gamma`                | The gamma URL and an instruction such as "Replace the pricing table with the three new tiers" | `editId`; poll `get_edit_status` for a summary of the change                                   |
| Hand off                   | `export_gamma`              | The gamma URL and `exportAs: "pdf"`                                                           | `exportId`; poll `get_export_status` for a download URL (valid about a week)                   |

Generating from a brief with no template works the same way through `generate`; pass `themeId` from `get_themes` to apply your workspace theme. `generate_from_template` is the MCP form of `POST /agent/generations` with `templateId`: the template you pass as `gammaId` is pinned as the starting point and the prompt supplies the content; any [template instructions](/build-with-gamma/brand-template-editing-controls.md#template-instructions) saved in the template, including locked slides, apply too. The full walkthrough, including failure cases and example output, is [Generate branded content from approved templates](/build-with-gamma/branded-template-workflow.md). Which of a template's properties survive generation and editing, and which the prompt can change, is in [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md).

## REST API or MCP?

|                                                                                     | MCP server                  | REST API                                                     |
| ----------------------------------------------------------------------------------- | --------------------------- | ------------------------------------------------------------ |
| Who decides what to call                                                            | The agent, at runtime       | Your code                                                    |
| Auth                                                                                | OAuth with DCR, any plan    | API key (Pro and above) or OAuth on behalf of your users     |
| Generate, generate from template, edit, export, search, comments, analytics, images | Yes                         | Yes                                                          |
| Read a gamma's content                                                              | `read_gamma`                | Not available                                                |
| Archive or delete a gamma                                                           | Not available               | `POST /gammas/{gammaId}/archive`, `DELETE /gammas/{gammaId}` |
| Webpages and multi-page gammas                                                      | `generate_multi_page_gamma` | Classic `POST /generations` with `pages`                     |

Use MCP when an agent should pick tools and parameters itself. Use the [REST API](/get-started/understanding-the-api-options.md) when your own code controls the requests or runs on an automation platform. Credits are charged the same way on both.

## Troubleshooting

| Symptom                                              | Cause                                                                                                                             | Fix                                                                                                                                                      |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Registration rejected with a redirect URI error      | The client's redirect URIs are not allowlisted                                                                                    | [Request access](#request-access-for-a-new-client) with the exact URIs                                                                                   |
| Sign-in loops or the client reports no OAuth support | The client does not support DCR or PKCE                                                                                           | Use a client or framework that does, or call the REST API                                                                                                |
| `generate_from_template` rejects the ID              | The gamma is not a workspace template, has more than one page, is part of a site, is archived, or is an official Explore template | Pick a `workspaceTemplates` hit from `search_templates`; see [template eligibility](/build-with-gamma/branded-template-workflow.md#which-templates-work) |
| Tool returns a permission error                      | The connected user cannot view or edit that gamma                                                                                 | Share the gamma with that user, or connect as a user who has access                                                                                      |
| Generation `failed` with `insufficient_credits`      | The connected workspace is out of credits                                                                                         | Add credits or enable auto-recharge in Settings > Billing                                                                                                |

## Related

* [Set up the MCP server](/mcp/gamma-mcp-server.md): connection details and the full FAQ
* [Generate branded content from approved templates](/build-with-gamma/branded-template-workflow.md): the template loop this guide's first workflow follows
* [MCP tools reference](/mcp/mcp-tools-reference.md): every tool's parameters and output
* [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md): what generation and editing preserve or change


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/build-with-gamma/connect-your-own-agent.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
