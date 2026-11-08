> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/readme.md).

# Gamma Developer Docs

Gamma API and MCP for AI agents and apps: generate branded presentations, documents, webpages, and social posts, then read, edit, and export them.

{% columns %}
{% column valign="middle" %}
Give your AI agent or app the tools to create, edit, and export on-brand gammas, through the hosted MCP server or the REST API.

<a href="/mcp/gamma-mcp-server.md" class="button primary">Connect your agent</a><a href="/get-started/understanding-the-api-options.md" class="button secondary">Use the REST API</a>
{% endcolumn %}

{% column %}

<figure><img src="https://2814591912-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FupsTVd2JbSOFZRBjfqED%2Fuploads%2Fgit-blob-f7bdadae6305295a8fb9abfcaa79bcc56c80a778%2Flandscape-developer-clouds.png?alt=media" alt="" width="300"><figcaption></figcaption></figure>
{% endcolumn %}
{% endcolumns %}

Three ways to build with Gamma:

* **Connect your AI agent.** MCP clients that support OAuth with Dynamic Client Registration can use the hosted server at `https://mcp.gamma.app/mcp` on any plan. Popular clients already work; for a custom client, [register its redirect URIs first](/mcp/gamma-mcp-server.md#connect-your-own-agent-or-mcp-client). Guide: [Connect your own agent](/build-with-gamma/connect-your-own-agent.md).
* **Build a branded template workflow.** A human approves a template; your code or agent generates on-brand variants from it ([`POST /agent/generations`](/agent-gamma-5/create-agent-generation.md) with `templateId`, or `generate_from_template` over MCP), then inspects, edits, and exports them. Guide: [Generate from approved templates](/build-with-gamma/branded-template-workflow.md); what is preserved and what can change: [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md).
* **Call the REST API directly.** Gamma 5 agent generation and editing, plus read, search, export, and analytics endpoints, with an [API key](https://gamma.app/settings/api-keys) (Pro, Ultra, Teams, Business, Enterprise) or OAuth.

## Authentication

The Gamma API supports two authentication methods. Pick based on whose Gamma account your requests act as:

|                     | API key                                                                    | OAuth 2.0                                                                      |
| ------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Best for            | Scripts, internal tools, automation platforms (Zapier, Make, n8n)          | Apps acting on behalf of **your users**, MCP servers, marketplace integrations |
| Setup               | Copy a key from [Settings > API Keys](https://gamma.app/settings/api-keys) | Register a client, run an authorization flow                                   |
| Header              | `X-API-KEY: sk-gamma-...`                                                  | `Authorization: Bearer <access_token>`                                         |
| Whose account       | Yours                                                                      | The user who authorized your app                                               |
| Credential lifetime | Until revoked                                                              | Access token \~1 hour; refresh token up to 90 days (rotated)                   |

Every request must include exactly one of the two headers, plus `Content-Type: application/json`. See [Authenticate with OAuth](/get-started/authenticate-with-oauth.md) for the full OAuth setup guide.

API key access requires a Pro, Ultra, Teams, Business, or Enterprise plan. [Some connectors](/connectors/connectors-and-integrations.md) work on all plans and do not require an API key.

{% hint style="info" %}
**Machine-readable docs** are available at [developers.gamma.app/llms.txt](https://developers.gamma.app/llms.txt) and [developers.gamma.app/llms-full.txt](https://developers.gamma.app/llms-full.txt). Every page is also available as markdown by appending `.md` to the URL.
{% endhint %}

## Quickstart

### 1. Start a generation

Generation runs on the Gamma 5 agent. Describe what you want; the agent plans and builds the gamma.

{% tabs %}
{% tab title="cURL" %}

```bash
curl -X POST https://public-api.gamma.app/v1.0/agent/generations \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $GAMMA_API_KEY" \
  -d '{
    "prompt": "A 10-slide Q3 product launch strategy for the sales team",
    "format": "presentation",
    "numCards": 10,
    "exportAs": "pdf"
  }'
```

{% endtab %}

{% tab title="Python" %}

```python
import requests, os

response = requests.post(
    "https://public-api.gamma.app/v1.0/agent/generations",
    headers={
        "X-API-KEY": os.environ["GAMMA_API_KEY"],
        "Content-Type": "application/json",
    },
    json={
        "prompt": "A 10-slide Q3 product launch strategy for the sales team",
        "format": "presentation",
        "numCards": 10,
        "exportAs": "pdf",
    },
)
response.raise_for_status()  # surfaces 403 insufficient_credits, 429 concurrency limits, etc.
generation_id = response.json()["generationId"]
```

{% endtab %}

{% tab title="JavaScript" %}

```javascript
const response = await fetch(
  "https://public-api.gamma.app/v1.0/agent/generations",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": process.env.GAMMA_API_KEY,
    },
    body: JSON.stringify({
      prompt: "A 10-slide Q3 product launch strategy for the sales team",
      format: "presentation",
      numCards: 10,
      exportAs: "pdf",
    }),
  }
);
if (!response.ok) throw new Error(await response.text());
const { generationId } = await response.json();
```

{% endtab %}
{% endtabs %}

{% code title="Response" %}

```json
{
  "generationId": "gen_V1StGXR8Z5jdHi6B",
  "status": "pending",
  "warnings": []
}
```

{% endcode %}

To generate from an approved template instead, add `"templateId": "<workspace template, gamma, or Explore template id>"` and leave out `themeId`.

### 2. Poll for the result

Poll `GET /v1.0/agent/generations/{generationId}` every 5 seconds until `status` is `completed` or `failed`, then read `gamma.gammaUrl` from the completed response. While still `pending`, the response may include `progress` with `done`, `total`, and `percent` (0–99) once card building starts; only `completed` means the job is finished. Completed and failed responses also report `credits.deducted` (what this job charged) and `credits.remaining` (your balance when the status was served); either may be omitted if the lookup fails. See [Poll for results](/guides/async-patterns-and-polling.md) for pacing, rate-limit headers, and how agent polling differs from Classic.

```python
import time

deadline = time.time() + 25 * 60  # agent jobs usually finish in minutes but may run up to 20
while time.time() < deadline:
    resp = requests.get(
        f"https://public-api.gamma.app/v1.0/agent/generations/{generation_id}",
        headers={"X-API-KEY": os.environ["GAMMA_API_KEY"]},
    )
    resp.raise_for_status()  # a 401, 404, or 429 is shown instead of failing on a missing "status"
    result = resp.json()
    if result["status"] == "completed":
        print(result["gamma"]["gammaUrl"])
        break
    if result["status"] == "failed":
        print("Generation failed:", result.get("error"))
        break
    time.sleep(5)
else:
    print("Still running after 25 minutes. Don't resubmit; check", generation_id, "again later.")
```

{% code title="Response (completed)" %}

```json
{
  "generationId": "gen_V1StGXR8Z5jdHi6B",
  "status": "completed",
  "gamma": {
    "gammaId": "g_l0mf2jvf1fpmi1v",
    "gammaUrl": "https://gamma.app/docs/abc123"
  },
  "result": { "summary": "Created a 10-card launch deck covering goals, timeline, and metrics." },
  "exportUrl": "https://exports.gamma.app/.../deck.pdf",
  "warnings": [],
  "updatedTime": "2026-08-25T17:03:04.000Z",
  "credits": { "deducted": 15, "remaining": 485 }
}
```

{% endcode %}

### 3. Use your Gamma

Your presentation is live at `gamma.gammaUrl`. If you specified `exportAs` and the export succeeded, the file is at `exportUrl`; an `export_failed` entry in `warnings` means the gamma was created without the file, and you can export it with [`POST /v1.0/gammas/{gammaId}/export`](/management/export-gamma.md). To edit your gamma, call [`POST /v1.0/agent/gammas/{gammaId}/edits`](/agent-gamma-5/edit-gamma.md) with a natural-language instruction.

{% hint style="info" %}
Getting a 401? Gamma uses `X-API-KEY` as a custom header — not `Authorization: Bearer`. See [Error codes](/reference/error-codes.md) for other common issues.
{% endhint %}

## Endpoints

| Endpoint                                                                                        | Method | Description                                                                |
| ----------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------- |
| [/agent/generations](/agent-gamma-5/create-agent-generation.md)                                 | POST   | Gamma 5: generate from a prompt, optionally from a template (`templateId`) |
| [/agent/generations/{generationId}](/agent-gamma-5/get-agent-generation-status.md)              | GET    | Poll agent generation status                                               |
| [/agent/gammas/{gammaId}/edits](/agent-gamma-5/edit-gamma.md)                                   | POST   | Gamma 5: edit your gamma                                                   |
| [/agent/edits/{editId}](/agent-gamma-5/get-edit-status.md)                                      | GET    | Poll agent edit status                                                     |
| [/generations](/generations-classic/create-generation.md)                                       | POST   | Classic: generate from text                                                |
| [/generations/from-template](/generations-classic/create-from-template.md)                      | POST   | Classic: generate from template                                            |
| [/generations/{id}](/generations-classic/get-generation-status.md)                              | GET    | Poll Classic generation status                                             |
| [/images](/images/create-image-generation.md)                                                   | POST   | Generate a standalone image                                                |
| [/images/{id}](/images/get-image-generation-status.md)                                          | GET    | Poll image generation status                                               |
| [/images/media/{savedMediaId}/archive](/images/archive-image.md)                                | POST   | Archive a media library item                                               |
| [/themes](/workspace/list-themes.md)                                                            | GET    | List workspace themes                                                      |
| [/folders](/workspace/list-folders.md)                                                          | GET    | List workspace folders                                                     |
| [/gammas/search](/management/search-gammas.md)                                                  | GET    | Search workspace gammas                                                    |
| [/templates/search](/management/search-templates.md)                                            | GET    | Search workspace and explore templates                                     |
| [/gammas/{gammaId}](/management/get-gamma.md)                                                   | GET    | Get gamma metadata                                                         |
| [/gammas/{gammaId}/comments](/management/get-gamma-comments.md)                                 | GET    | List comment threads                                                       |
| [/gammas/{gammaId}/archive](/management/archive-gamma.md)                                       | POST   | Archive a Gamma                                                            |
| [/gammas/{gammaId}/export](/management/export-gamma.md)                                         | POST   | Export an existing Gamma                                                   |
| [/exports/{id}](/management/get-export-status.md)                                               | GET    | Poll export status                                                         |
| [/gammas/{gammaId}](/management/delete-gamma.md)                                                | DELETE | Delete a Gamma                                                             |
| [/gammas/{gammaId}/analytics](/analytics/get-gamma-analytics.md)                                | GET    | Doc-level engagement metrics                                               |
| [/gammas/{gammaId}/analytics/cards](/analytics/get-gamma-card-analytics.md)                     | GET    | Per-card engagement stats                                                  |
| [/gammas/{gammaId}/analytics/viewers](/analytics/get-gamma-viewer-analytics.md)                 | GET    | Per-viewer engagement (paginated)                                          |
| [/gammas/{gammaId}/analytics/viewers/{userId}](/analytics/get-gamma-viewer-detail-analytics.md) | GET    | Single-viewer per-card engagement                                          |

{% hint style="success" %}
**Building an AI agent?** Generation, template generation, editing, reading, search, export, and analytics are also available as MCP tools. The [MCP server](/mcp/gamma-mcp-server.md) lets your agent generate gammas from text or templates, read and search existing ones, edit them, export, and read comments and analytics, authenticated with OAuth and Dynamic Client Registration. See the [MCP tools reference](/mcp/mcp-tools-reference.md).
{% endhint %}

## Next steps

<table data-view="cards"><thead><tr><th></th><th></th><th data-hidden data-card-target data-type="content-ref"></th></tr></thead><tbody><tr><td><strong>Generate with the Gamma 5 agent</strong></td><td>One prompt, optional template, quality presets, source URLs, and export — the recommended endpoint.</td><td><a href="/agent-gamma-5/create-agent-generation.md">POST /agent/generations</a></td></tr><tr><td><strong>Edit an existing gamma</strong></td><td>Describe the change you want and Gamma applies it to your gamma.</td><td><a href="/agent-gamma-5/edit-gamma.md">POST /agent/gammas/{gammaId}/edits</a></td></tr><tr><td><strong>Classic generation</strong></td><td>The previous engine: parameter-driven generation and template remixing. Use it for webpages and multi-page gammas, which the Gamma 5 agent does not support, or if your integration is already built on it.</td><td><a href="/guides/generate-api-parameters-explained.md">Generate from text</a></td></tr><tr><td><strong>Connect integrations</strong></td><td>Use Gamma with AI assistants and automation platforms — some require no API key.</td><td><a href="/connectors/connectors-and-integrations.md">Connect integrations</a></td></tr><tr><td><strong>Set up the MCP server</strong></td><td>Give your AI agent tools to generate, read, edit, and export gammas via OAuth.</td><td><a href="/mcp/gamma-mcp-server.md">Set up the MCP server</a></td></tr></tbody></table>


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/readme.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
