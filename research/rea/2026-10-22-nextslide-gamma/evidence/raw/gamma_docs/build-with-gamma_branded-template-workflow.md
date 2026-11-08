> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/build-with-gamma/branded-template-workflow.md).

# Generate from approved templates

Turn one brief into an on-brand presentation, document, and social post from approved templates, then check, revise, and export.

A team approves a handful of templates once; every agent or script then produces content that uses their layout and theme without re-describing the brand each time. This page walks that loop for one brief with Gamma 5 (`POST /agent/generations` with `templateId`, or the `generate_from_template` MCP tool), with the REST call and the MCP tool for each step. You can read it without running anything; the calls are small enough to paste into a client.

## Quick reference

* Generate with [`POST /agent/generations`](/agent-gamma-5/create-agent-generation.md) and `templateId` (REST) or `generate_from_template` with a workspace template as `gammaId` (MCP); do not send `themeId` with a template.
* Tell the prompt how closely to follow the template; rules that should apply every time belong in the template's [instructions and locks](/build-with-gamma/brand-template-editing-controls.md#template-instructions).
* Poll until `status` is `completed` or `failed`; the completed response carries `gamma.gammaId`, `gamma.gammaUrl`, `credits`, and the export URL if you asked for `exportAs` and the export succeeded.
* Edit the generated gamma (`gamma.gammaId`), not the template; one edit runs on a gamma at a time, and edits need edit access.
* Reads and exports are free; generations and edits consume credits.

## The brief

> Launch update for the Atlas analytics add-on: what shipped (three features), who it is for, pricing for the two tiers, and next quarter's roadmap. Audience: existing customers.

Three outputs, three approved templates in the workspace:

| Output                                 | Template                                                                            | Format         |
| -------------------------------------- | ----------------------------------------------------------------------------------- | -------------- |
| Launch deck for the customer webinar   | "Product launch deck" (title, three feature cards, pricing table, roadmap, closing) | `presentation` |
| Release notes page for the help center | "Release notes" (summary, what's new, pricing, FAQ)                                 | `document`     |
| Announcement post                      | "Launch announcement" (one visual card with headline and three bullets)             | `social`       |

## Which templates work

Use [`POST /agent/generations`](/agent-gamma-5/create-agent-generation.md) with `templateId`. It runs Gamma 5 and accepts three kinds of starting point: a template saved in your workspace, any gamma in your workspace, or an official Gamma template from Explore. Your prompt decides how closely the result follows it, so say so: "Follow this template's structure and style exactly; only replace the content." Do not send `themeId` with `templateId` (the request fails with `400`); the template's look is the brand.

For finer control over how the template is applied, put the rules in the template itself with **template instructions**: overall guidance in the template's settings (tone, audience, what must always be filled in), a note on each slide saying what belongs there, and a **lock** on any slide the generation must leave untouched, such as the cover, a legal disclaimer, or the pricing table. Gamma reads them on every generation from that template, so your prompt only needs to carry the brief. See [What are template instructions and how can I use them?](https://help.gamma.app/en/articles/16056626-what-are-template-instructions-and-how-can-i-use-them) in the Help Center.

Find the IDs with [`GET /templates/search`](/management/search-templates.md): `workspaceTemplates[].id` for your own, `exploreTemplates[].id` for official ones. Over MCP, the `generate_from_template` tool is the same call: it starts a Gamma 5 generation with the template you pass as `gammaId` pinned as its `templateId`; use a `workspaceTemplates` hit from `search_templates`.

{% hint style="info" %}
The Classic REST endpoint `POST /generations/from-template` keeps the template's structure automatically but only accepts single-page workspace templates within your plan's card limit, and rejects Explore templates, non-template gammas, archived gammas, and gammas that are part of a site. Keep using it in existing integrations; start new ones on `POST /agent/generations`.
{% endhint %}

## Step 1: Generate from the template

One call per output. The template carries the layout and theme; the brief carries the content.

{% tabs %}
{% tab title="REST" %}

```bash
curl -X POST https://public-api.gamma.app/v1.0/agent/generations \
  -H "X-API-KEY: $GAMMA_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "templateId": "g_launchdeck1a2b3c",
    "format": "presentation",
    "prompt": "Follow this template's structure and style exactly; only replace the content. Launch update for the Atlas analytics add-on. Features: scheduled reports, anomaly alerts, Snowflake sync. For existing customers. Pricing: Team $49/mo, Business $149/mo. Roadmap next quarter: custom dashboards, SSO.",
    "exportAs": "pdf"
  }'
```

Repeat with the "Release notes" template (`"format": "document"`) and the "Launch announcement" template (`"format": "social"`). Each call returns a `gen_`-prefixed `generationId`; poll [`GET /v1.0/agent/generations/{generationId}`](/agent-gamma-5/get-agent-generation-status.md) until `status` is `completed` or `failed`. The response carries `gamma.gammaUrl`, `exportUrl` when `exportAs` was set, and the `credits` charged. See [Poll for results](/guides/async-patterns-and-polling.md).
{% endtab %}

{% tab title="MCP" %}
`generate_from_template` with:

```json
{
  "gammaId": "g_launchdeck1a2b3c",
  "prompt": "Launch update for the Atlas analytics add-on. Features: scheduled reports, anomaly alerts, Snowflake sync. For existing customers. Pricing: Team $49/mo, Business $149/mo. Roadmap next quarter: custom dashboards, SSO.",
  "exportAs": "pdf"
}
```

`gammaId` is a template saved in the user's workspace (a `workspaceTemplates` hit from `search_templates`); the tool runs `POST /agent/generations` with it as `templateId`, so the format follows the template and `themeId` is not accepted. Repeat with the other two template IDs; poll `get_generation_status` with the returned `gen_` id until `status` is `completed` or `failed`.
{% endtab %}
{% endtabs %}

What came back for the deck: eight cards in the template's order, the three feature cards filled from the brief, the pricing table with the two tiers, roadmap and closing cards; the template's theme throughout. The document used the "Release notes" sections and wrote an FAQ from the brief; the social post is one card with the headline and three feature bullets. If a result drifts from the template, tighten the prompt ("keep every card, same order, same layouts") and regenerate; the structure is prompt-directed on the agent endpoint, so check it the first time you use a template.

## Step 2: Check the result

{% tabs %}
{% tab title="MCP" %}
`read_gamma` with `gammaIdOrUrl` set to the generation ID or gamma URL returns the content as text, so the agent can confirm the pricing tiers and feature names before anyone opens the deck.
{% endtab %}

{% tab title="REST" %}
`GET /v1.0/gammas/{gammaId}` returns metadata (title, card count, URL, timestamps), not content; the completed agent status also includes `result.summary`, the agent's own description of what it built. To check content, open `gamma.gammaUrl` or inspect the exported file.
{% endtab %}
{% endtabs %}

## Step 3: Revise one thing

The brief's pricing changed after generation: Business is $129, not $149. Edit the existing gamma rather than regenerating.

{% tabs %}
{% tab title="MCP" %}
`edit_gamma` with the gamma URL and `prompt: "In the pricing table, change the Business tier price to $129/mo."` Poll `get_edit_status` until `completed` or `failed`; `result.summary` describes what changed.
{% endtab %}

{% tab title="REST" %}

```bash
DECK_ID=g_atlaslaunch7k8m9n   # gamma.gammaId from the completed generation in Step 1
curl -X POST https://public-api.gamma.app/v1.0/agent/gammas/$DECK_ID/edits \
  -H "X-API-KEY: $GAMMA_API_KEY" -H "Content-Type: application/json" \
  -d '{ "prompt": "In the pricing table, change the Business tier price to $129/mo." }'
```

Use the generated deck's id, not the template's; editing the template would change the template itself.

Poll `GET /v1.0/agent/edits/{editId}`. The completed response includes `result.summary` and the `credits` charged.
{% endtab %}
{% endtabs %}

Edits change only what the instruction asks for; the rest of the gamma, including its theme and layout, stays as it was. Only one edit runs on a gamma at a time, so wait for `completed` before sending the next instruction. Edits need edit access to the gamma and are charged credits like generations.

## Step 4: Export

{% tabs %}
{% tab title="MCP" %}
`export_gamma` with the gamma URL and `exportAs: "pptx"` (or `pdf`, or `png` for a zip of card images). Poll `get_export_status` for the download URL.
{% endtab %}

{% tab title="REST" %}
`POST /v1.0/gammas/{gammaId}/export` with `{ "exportAs": "pptx" }`, then `GET /v1.0/exports/{exportId}`.
{% endtab %}
{% endtabs %}

Exports are free and work for any non-archived gamma in the connected workspace that the user can view. The deck went out as PPTX for the webinar, the release notes as PDF, and the social post as PNG.

## When it fails

| What you see                                                                                                                                              | Why                                                                                                                 | What to do                                                                                                                                                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `400` on `POST /agent/generations` with both `themeId` and `templateId`                                                                                   | They cannot be combined                                                                                             | Drop `themeId`; the template supplies the look                                                                                                                                                                                                           |
| `400` or not found for `templateId`                                                                                                                       | The ID is not a workspace template, a gamma in this workspace, or an Explore template, or the user cannot access it | Pick an id from `GET /templates/search` or `GET /gammas/search`                                                                                                                                                                                          |
| Result does not follow the template                                                                                                                       | The agent treats the template as a reference and your prompt did not ask it to keep the structure                   | Say "follow this template's structure exactly; only replace the content", and lock the slides that must never change in the template's [instructions](https://help.gamma.app/en/articles/16056626-what-are-template-instructions-and-how-can-i-use-them) |
| `failed` with `insufficient_credits`                                                                                                                      | The workspace is out of credits                                                                                     | Add credits; reads and exports still work                                                                                                                                                                                                                |
| Edit returns a permission error                                                                                                                           | The user has view access only                                                                                       | Ask the owner for edit access                                                                                                                                                                                                                            |
| Classic `POST /generations/from-template` rejects `gammaId`: not a template, multiple pages, part of a site, archived, Explore id, or over the card limit | Classic template eligibility                                                                                        | Use `POST /agent/generations` with `templateId`, or mark a single-page gamma as a template                                                                                                                                                               |

## What this gives you

* Brand consistency without prompt engineering: the template carries layout and theme; the brief carries only the content.
* A verifiable loop: generate, read, edit, export, each with a status you can poll and a credit charge you can see.
* One pattern for three formats; `format` and the template decide whether the result is a deck, a document, or a post.

## Related

* [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md): which properties are preserved, which can change, and whether each is enforced, a default, or up to your prompt
* [Connect your own agent to Gamma](/build-with-gamma/connect-your-own-agent.md): connecting an agent to run this loop
* [`POST /agent/generations`](/agent-gamma-5/create-agent-generation.md): parameter details for Gamma 5 generation
* [Generate from template (Classic)](/guides/create-from-template-api-parameters-explained.md): the Classic REST route for existing integrations


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/build-with-gamma/branded-template-workflow.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
