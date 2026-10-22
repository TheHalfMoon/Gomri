> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/connectors/connectors-and-integrations.md).

# Connect integrations

Connect Gamma to your favorite AI tools and automation platforms.

Gamma integrates with popular AI assistants and automation platforms so you can create presentations, documents, webpages, and social posts from the tools you already use.

{% hint style="info" %}
**Looking for general Gamma help?** This page is for developers and technical setup. For general guidance on using Gamma with AI assistants and automation tools, see [How do I use Gamma with connectors and integrations?](https://help.gamma.app/en/articles/13943863-how-do-i-use-gamma-with-connectors-and-integrations) in the Help Center.
{% endhint %}

### Quick reference

* ChatGPT, Claude, Slack, Superhuman Go, and Atlassian Rovo work on all Gamma plans and do not require an API key.
* Zapier, Make, n8n, and direct API integrations require an API key.
* Use connectors when you want Gamma inside an assistant.
* Use the API or automation platforms when you want programmatic control over prompts, polling, and downstream workflows.
* Assistants powered by the Gamma MCP server (ChatGPT, Claude, Slack) can also generate from templates, read existing gammas, read their comments and analytics, and export them. ChatGPT and Claude can also edit existing gammas; the Slack app does not expose the edit tools yet.
* Building your own agent? Connect it to the same MCP server — see [Set up the MCP server](/mcp/gamma-mcp-server.md).
* Available capabilities can vary by platform. For the full MCP tool surface, see [Set up the MCP server](/mcp/gamma-mcp-server.md).

See [Access and Pricing](/get-started/access-and-pricing.md) for plan details.

{% tabs %}
{% tab title="Claude" %}

### Claude connector

Create gammas directly from Claude conversations using the Gamma Connector.

{% stepper %}
{% step %}

#### Open Claude

Go to [Claude](https://claude.ai) (web or desktop app).
{% endstep %}

{% step %}

#### Find connectors

Go to **Settings** → **Connectors**.
{% endstep %}

{% step %}

#### Add Gamma

Click **Browse Connectors** and search for "Gamma."
{% endstep %}

{% step %}

#### Connect

Click **Connect**, then click **Allow** to grant access to your Gamma account. Choose the right workspace if applicable.
{% endstep %}
{% endstepper %}

Once connected, you can ask Claude to create presentations, documents, and more — all generated in Gamma.

{% hint style="info" %}
Advanced Gamma capabilities such as browsing templates, generating from a template, and checking generation status may be available in MCP-based integrations depending on the platform. For the full MCP tool surface, see [Set up the MCP server](/mcp/gamma-mcp-server.md).
{% endhint %}

Example prompt: "Create a 10-slide marketing strategy presentation covering target audience, campaign channels, budget breakdown, and success metrics. Use a professional theme."
{% endtab %}

{% tab title="ChatGPT" %}

### ChatGPT app

Create gammas directly from ChatGPT conversations using the Gamma app.

{% stepper %}
{% step %}

#### Open the app directory

Go to **Settings** → **Apps**, or browse the [ChatGPT app directory](https://chatgpt.com/apps) directly.
{% endstep %}

{% step %}

#### Find Gamma

Search for "Gamma" — it's listed as **Gamma: Create presentations and docs**.
{% endstep %}

{% step %}

#### Connect

Click **Connect** and complete the authorization flow to grant access to your Gamma account. Choose the right workspace if applicable.
{% endstep %}
{% endstepper %}

Once connected, invoke Gamma in any conversation by:

* **@mention**: type `@Gamma` in your prompt
* **App menu**: click **+** then **More** and select Gamma

{% hint style="info" %}
Advanced Gamma capabilities such as browsing templates, generating from a template, and checking generation status may be available in MCP-based integrations depending on the platform. Some platforms also review app updates before making them available — if documented functionality is missing, the latest version of the Gamma app may still be in review. This applies to applications such as ChatGPT and Codex. For the full MCP tool surface, see [Set up the MCP server](/mcp/gamma-mcp-server.md).
{% endhint %}

Example prompt: "@Gamma Create a 10-slide sales enablement deck covering our Q3 product launches, competitive positioning, and customer success stories. Use a professional theme."
{% endtab %}

{% tab title="Slack" %}

### Slack app

Create gammas directly from Slack by messaging the Gamma app or mentioning it in a channel.

**What you can do**

* **Create gammas from a conversation**: DM the Gamma app or type `@Gamma` with your request in any channel where the app has been added, and get a presentation, document, webpage, or social post back in the thread
* **Use thread context**: when you mention Gamma in a thread, it reads the conversation and creates a gamma based on what's being discussed — turn a planning thread into a deck or a discussion into a one-pager without restating anything
* **Generate images**: ask for a standalone image and get it back in the thread
* **Use reference images**: attach up to 4 images to the message where you ask for an image, and Gamma places their subject — a person, character, or product — in the result. PNG, JPEG, GIF, WebP, HEIC, HEIF, and AVIF files work; images from earlier messages in the thread aren't used
* **Generate from templates**: browse your templates and create a new gamma from one, right from Slack
* **Check status and export**: follow up on in-progress generations and export finished gammas to PDF, PPTX, or PNG
* **Preview links**: paste a gamma link in a conversation to get a rich preview (you'll only see previews for gammas you have access to)
* **Reply to comments**: respond to Gamma comment notifications in Slack to post a reply back on the gamma

{% hint style="info" %}
The Slack app is powered by the Gamma MCP server. For the full tool surface, see [Set up the MCP server](/mcp/gamma-mcp-server.md).
{% endhint %}

Example prompts:

* "@Gamma Create a 10-slide onboarding deck for new engineers covering our tech stack, team structure, and first-week checklist."
* "@Gamma Turn this thread into a proposal doc for the leadership team."
* "@Gamma Generate a hero image of this product on a marble desk." (with a product photo attached to the same message)

**Getting started**

{% stepper %}
{% step %}

#### Add Gamma to Slack

Go to [gamma.app/slack](https://gamma.app/slack) and click **Add to Slack**.
{% endstep %}

{% step %}

#### Authorize the app

Review the requested permissions and click **Allow** to install Gamma in your Slack workspace.
{% endstep %}

{% step %}

#### Connect your Gamma account

Complete the Gamma sign-in flow to link your Gamma account. Choose the right workspace if applicable.
{% endstep %}
{% endstepper %}
{% endtab %}

{% tab title="Zapier" %}

### Zapier integration

Automate Gamma content creation as part of your Zapier workflows.

* **Integration page**: [Gamma on Zapier](https://zapier.com/apps/gamma/integrations)

#### What you can do

* Trigger a Gamma generation when a new row is added to Google Sheets
* Create a presentation whenever a deal closes in your CRM
* Generate reports from form submissions

#### Getting started

1. In your Zapier workflow, search for **Gamma** in the app directory.
2. Select the Gamma action you want to use (e.g., "Generate a Gamma").
3. Authenticate with your Gamma API key.
4. Map your trigger data to the Gamma generation parameters.

Your Gamma API key is required. Generate one from your [account settings](https://gamma.app/settings).
{% endtab %}

{% tab title="Make" %}

### Make integration

Build visual automation workflows that include Gamma content creation.

* **Integration page**: [Gamma on Make](https://www.make.com/en/integrations/gamma-app)

#### What you can do

* Generate branded presentations from CRM data
* Create documents from email content or form responses
* Build multi-step workflows combining Gamma with hundreds of other apps

#### Getting started

1. In your Make scenario, add a new module and search for **Gamma**.
2. Select the action you want (e.g., "Create a Generation").
3. Connect your Gamma account using your API key.
4. Configure the module with your desired parameters.

Your Gamma API key is required. Generate one from your [account settings](https://gamma.app/settings).
{% endtab %}

{% tab title="n8n" %}

### n8n integration

Use Gamma in your self-hosted or cloud n8n automation workflows with the official Gamma node.

* **Integration page**: [Gamma on n8n](https://n8n.io/integrations/gamma/)

#### What you can do

* Automate presentation creation from any of n8n's 400+ integrations
* Generate content from CRM data, databases, and APIs using the native Gamma node
* List your workspace themes and folders to dynamically configure generations
* Build end-to-end pipelines: data ingestion → content generation → distribution

#### Available operations

| Resource   | Operation                | Description                                                    |
| ---------- | ------------------------ | -------------------------------------------------------------- |
| Generation | **Create**               | Generate a new presentation, document, social post, or webpage |
| Generation | **Create from Template** | Remix an existing Gamma with a new prompt                      |
| Generation | **Get Status**           | Check the status of a generation                               |
| Theme      | **List**                 | Get available themes from your workspace                       |
| Folder     | **List**                 | Get workspace folders                                          |

#### Getting started

1. In the n8n editor, click **+** and search for **Gamma**.
2. Select the Gamma node and choose your operation (e.g., **Create** under Generation).
3. Create a new **Gamma credential** by entering your API key.
4. Configure your generation parameters (input text, text mode, format, theme, etc.).
5. To poll for results, add a second Gamma node with the **Get Status** operation and map the generation ID from the previous step.

Your Gamma API key is required. Generate one from your [account settings](https://gamma.app/settings).
{% endtab %}

{% tab title="Superhuman Go" %}

### Superhuman Go agent

Turn ideas, emails, and meeting notes into polished presentations directly inside Superhuman Go.

* **Agent page**: [Gamma on Superhuman](https://superhuman.com/store/agents/gamma-47462)

{% stepper %}
{% step %}

#### Open the Agent Store

In Superhuman Go, open the **Agent Store**.
{% endstep %}

{% step %}

#### Find Gamma

Search for "Gamma" and select the Gamma agent.
{% endstep %}

{% step %}

#### Add the agent

Click **Try agent** and authorize access to your Gamma account.
{% endstep %}
{% endstepper %}

Once added, ask Gamma directly in Go to generate presentations, documents, social posts, or webpages from whatever you're working on.

Example prompt: "Turn this email thread into a one-pager for the leadership audience."
{% endtab %}

{% tab title="Atlassian Rovo" %}

### Atlassian Rovo agent

Use Gamma skills inside Rovo agents to generate content from your Jira and Confluence workflows.

{% hint style="info" %}
Connecting Gamma requires an **org admin** to add the Gamma MCP server from Atlassian Administration. Once connected, all users on that site can use Gamma skills in Rovo.
{% endhint %}

{% stepper %}
{% step %}

#### Open Atlassian Administration

Go to [Atlassian Administration](https://admin.atlassian.com) and select your organization.
{% endstep %}

{% step %}

#### Navigate to Connected apps

From the sidebar, go to **Apps** → **Sites** → select your site → **Connected apps**.
{% endstep %}

{% step %}

#### Add the Gamma MCP server

Click the dropdown beside **Explore apps**, select **Add external MCP server**, and choose **Gamma** from the gallery.
{% endstep %}

{% step %}

#### Authorize and configure

Follow the installation prompts to connect your Gamma account and configure available tools.
{% endstep %}
{% endstepper %}

Once connected, users can invoke Gamma skills in any Rovo agent conversation or build custom agents in Rovo Studio that combine Gamma with other tools.

Example prompt: "Create a presentation summarizing the key decisions from this Confluence page."
{% endtab %}

{% tab title="Other Platforms" %}

### Other platforms

Gamma's REST API works with any automation platform or custom application that can make HTTP requests.

#### Getting started

All platforms follow the same pattern:

1. Make a **POST** request to `https://public-api.gamma.app/v1.0/generations` with your content and parameters.
2. Include your API key in the `X-API-KEY` header (or an [OAuth Bearer token](/get-started/authenticate-with-oauth.md) if your app acts on behalf of its users).
3. **Poll** the status endpoint until generation is complete.
4. Retrieve the Gamma URL and optional export URL from the response.

See the [Generate API parameters guide](/guides/generate-api-parameters-explained.md) for the full list of available options.

{% hint style="warning" %}
**Server-side only.** The Gamma API must be called from a backend server, not from browser-side JavaScript.
{% endhint %}
{% endtab %}
{% endtabs %}

### Which integration method is right for you?

| You want to...                                    | Use                                                                                                                                     | Plan required                                |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Create gammas with an AI assistant                | [ChatGPT](#chatgpt-app), [Claude](#claude-connector), [Superhuman Go](#superhuman-go-agent), or [Atlassian Rovo](#atlassian-rovo-agent) | Any plan                                     |
| Create gammas from your team chat                 | [Slack](#slack-app)                                                                                                                     | Any plan                                     |
| Automate with no-code workflows                   | [Zapier](#zapier-integration), [Make](#make-integration), or [n8n](#n8n-integration)                                                    | Pro+ (API key)                               |
| Connect your own AI agent or MCP client           | [MCP server](/mcp/gamma-mcp-server.md)                                                                                                  | Any plan (register your redirect URIs first) |
| Build a custom app with full programmatic control | [Gamma API](/guides/generate-api-parameters-explained.md)                                                                               | Pro+ (API key)                               |

### Related

* [Access and Pricing](/get-started/access-and-pricing.md) for plan and API key requirements
* [MCP server](/mcp/gamma-mcp-server.md) if you want an AI-tool-friendly integration layer
* [Custom MCP connectors](/connectors/custom-mcp-connectors.md) to bring your own MCP servers into Gamma
* [Generate from text](/guides/generate-api-parameters-explained.md) for the full API parameter guide


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/connectors/connectors-and-integrations.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
