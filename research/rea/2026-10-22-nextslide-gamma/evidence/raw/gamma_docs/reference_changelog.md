> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/reference/changelog.md).

# Changelog

New updates and improvements to the Gamma API, MCP Server, and integrations.

Release history for the Gamma Public API, MCP Server, and integrations.

{% updates format="full" %}
{% update date="2026-10-05" tags="launch" %}

## Gamma 5 agent: generate and edit through the API

`POST /agent/generations` has the Gamma agent plan and build a gamma from a prompt, optionally starting from a workspace template, an existing gamma, or an official Explore template (`templateId`). `POST /agent/gammas/{gammaId}/edits` edits an existing gamma from a natural-language instruction; poll `GET /agent/edits/{editId}`. Both are priced by the work the agent does. The MCP server exposes editing as `edit_gamma` and `get_edit_status`, and the ChatGPT and Claude connectors can now edit existing gammas.
{% endupdate %}

{% update date="2026-10-05" tags="launch" %}

## Custom MCP connectors

Admins of Enterprise workspaces can add their own MCP servers as connectors, so the Gamma agent can look up information from internal tools while it works. See [Add custom MCP connectors](/connectors/custom-mcp-connectors.md).
{% endupdate %}

{% update date="2026-08-31" tags="feature" %}

## MCP: search templates

The MCP server gained `search_templates`, which returns workspace templates and official Explore templates in one call.
{% endupdate %}

{% update date="2026-08-28" tags="feature" %}

## Search gammas and templates

`GET /gammas/search` runs a full-text search over the titles and body text of gammas the caller can access. `GET /templates/search` returns workspace templates (usable as `gammaId` for `POST /generations/from-template`) and official Explore templates (usable as `templateId` for `POST /agent/generations`) in one request. The MCP server gained `search_gammas`.
{% endupdate %}

{% update date="2026-08-04" tags="feature" %}

## Standalone image generation

`POST /images` generates a single on-brand image from a prompt, with optional reference images; poll `GET /images/{id}`. Images are saved to the workspace media library and can be archived with `POST /images/media/{savedMediaId}/archive`. MCP: `generate_image` and `get_image_generation_status`.
{% endupdate %}

{% update date="2026-07-30" tags="launch" %}

## Gamma app for Slack

Create gammas from a DM or an `@Gamma` mention, use thread context, generate from templates, export, and reply to comments without leaving Slack. Powered by the MCP server. See the [Slack app](/connectors/connectors-and-integrations.md#slack-app) guide.
{% endupdate %}

{% update date="2026-07-20" tags="feature" %}

## Multi-page gammas from MCP

`generate_multi_page_gamma` creates one gamma with several pages under a single URL in one request, with per-page content and settings, and can publish the result as a site.
{% endupdate %}

{% update date="2026-07-16" tags="feature" %}

## Analytics card metadata and complete card lists

Card analytics responses now include `cardName` and `cardPosition` on each row. `GET /gammas/{gammaId}/analytics/cards` returns every card in the Gamma; cards with no recorded activity have zeroed stats. `GET /gammas/{gammaId}/analytics/viewers/{userId}` `perCardTimeSpent` covers every card; unviewed cards have `viewTimePercent` of 0.
{% endupdate %}

{% update date="2026-07-13" tags="feature" %}

## Read, export, and analyze existing gammas

New endpoints for gammas the API did not create: `GET /gammas/{gammaId}` for metadata, `GET /gammas/{gammaId}/comments` for comment threads, `POST /gammas/{gammaId}/export` with `GET /exports/{id}` for PDF, PPTX, and PNG exports, and the `GET /gammas/{gammaId}/analytics` family for engagement data. New MCP tools: `get_gamma_comments`, `export_gamma`, and the analytics tools. `read_gamma` continues to return a gamma's content.
{% endupdate %}

{% update date="2026-03-06" tags="launch" %}

## ChatGPT App live

Gamma is now available as an app in ChatGPT. Create presentations, documents, and social posts directly from ChatGPT conversations.
{% endupdate %}

{% update date="2026-03-06" tags="launch" %}

## All three automation platforms

Gamma now has native integrations on Zapier, Make, and n8n. Full `v1.0` API parity across all three platforms.
{% endupdate %}

{% update date="2026-02-27" tags="feature" %}

## Create from template GA, new models, and more

Create from Template is now generally available. New `stylePreset` parameter. Export as PNG now supported. `GET /generations/{id}` returns `gammaId`. New image models: `recraft-v4`, `recraft-v4-svg`, `recraft-v4-pro`, `gemini-3.1-flash-image-mini`, `gemini-3.1-flash-image`, `gemini-3.1-flash-image-hd`, `flux-2-max`, `flux-2-klein`.
{% endupdate %}

{% update date="2026-01-23" tags="launch" %}

## Claude connector

Create gammas directly from Claude conversations using the Gamma Connector.
{% endupdate %}

{% update date="2026-01-16" tags="deprecation" %}

## v0.2 API removed

`v0.2` endpoints have been disabled. All integrations must use `v1.0`.
{% endupdate %}

{% update date="2025-11-05" tags="feature" %}

## Generate API GA, create from template, and more

Generate API moves from beta to `v1.0`. Create from Template API in beta. Webpage generation. Headers and footers. Image URLs in input. Folder assignment and email sharing. List Themes and List Folders endpoints. Official Make.com integration. Removed hard generation limits.
{% endupdate %}

{% update date="2025-09-15" tags="feature" %}

## Credits-based pricing, new models, and Zapier

Introduction of credits-based pricing. Ultra tier unlocks more powerful models and up to 75 cards. Zapier integration available.
{% endupdate %}

{% update date="2025-07-28" tags="launch" %}

## Beta release of Gamma Generate endpoints

Two new endpoints that allow the creation and retrieval of gammas via API have been released in beta.

* [Explore the API](/get-started/understanding-the-api-options.md) for an overview of how the API works
* [Review access and pricing](/get-started/access-and-pricing.md) for plan requirements and credit details
* [Generate from text](/guides/generate-api-parameters-explained.md) for parameter-by-parameter guidance
* [POST /generations](/generations-classic/create-generation.md) for the endpoint reference
  {% endupdate %}
  {% endupdates %}


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/reference/changelog.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
