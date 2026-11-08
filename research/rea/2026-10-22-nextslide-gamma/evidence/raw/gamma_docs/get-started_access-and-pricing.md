> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/get-started/access-and-pricing.md).

# Review access and pricing

API access requirements, credit-based pricing, and plan details.

{% hint style="info" %}
**Looking for general Gamma help?** This page is for developers using the API. For general guidance on credits and billing, see [How do credits work in Gamma?](https://help.gamma.app/en/articles/7834324-how-do-credits-work-in-gamma) in the Help Center.
{% endhint %}

### Quick reference

* The MCP server and the ChatGPT, Claude, and Slack connectors work on all plans.
* API keys are available on Pro, Ultra, Teams, Business, and Enterprise plans.
* Generations (`POST /v1.0/generations`) are priced per card and per image. Agent generations and edits are priced by the work the agent does.
* Credit usage is returned in the `credits` field on the completed or failed status response for every generation and edit.
* Auto-recharge is the safest way to prevent failed generations due to exhausted credits.

### Access

#### API keys (Zapier, Make, n8n, direct integration)

API key access is available on Pro, Ultra, Teams, Business, and Enterprise plans. Workspace admins can restrict or turn off API key access for their workspace; if you can't create a key on an eligible plan, ask your admin. Generate an API key from [Settings > API Keys](https://gamma.app/settings/api-keys). View [pricing plans here](https://gamma.app/pricing).

<figure><img src="https://2814591912-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FupsTVd2JbSOFZRBjfqED%2Fuploads%2Fgit-blob-70e8895ffa6a5ace27d1f7bd1aff1e8b714ec314%2Fapi-key-settings.png?alt=media" alt="API key settings in Gamma" width="75%"><figcaption><p>Settings > API Keys</p></figcaption></figure>

**OAuth apps (acting on behalf of your users)**

Apps can also authenticate users via [OAuth](/get-started/authenticate-with-oauth.md) instead of an API key. Requests made with an OAuth token consume the authorizing user's credits in the workspace they connected.

#### MCP server and connectors (ChatGPT, Claude, Slack, your own MCP client)

The [MCP server](/mcp/gamma-mcp-server.md) and the connectors built on it are available on all plans, including Free and Plus. No API key required — connect from [ChatGPT, Claude, or Slack](/connectors/connectors-and-integrations.md) and sign in with your Gamma account. Your own MCP client can connect too once Gamma has registered its redirect URIs; see [Connect your own agent or MCP client](/mcp/gamma-mcp-server.md#connect-your-own-agent-or-mcp-client). Generations, edits, and images via MCP charge credits the same way as API calls; reading, searching, and exporting do not.

### Usage and pricing

* API billing uses a credit-based system. Higher tier subscribers receive more monthly credits.
* API usage draws from the same credit balance as AI features in the Gamma app and is priced by the same rules. Requests made with an API key consume the key owner's credits in that workspace, so teammates sharing a key draw down the owner's balance.
* If you run out of credits, you can upgrade to a higher subscription tier, purchase credits ad hoc, or enable auto-recharge (*recommended*) at [Settings > Billing](https://gamma.app/settings/billing).

<figure><img src="https://2814591912-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FupsTVd2JbSOFZRBjfqED%2Fuploads%2Fgit-blob-ec88f20b135d9a7fc7b5ce1af26bbbfbfcd96e61%2Fbilling-credits.png?alt=media" alt="Credit management in Gamma" width="75%"><figcaption><p>Settings > Billing</p></figcaption></figure>

### How credits work

The Gamma API has two pricing models: generations are priced per card and per image, and agent generations and edits are priced by the work the agent does.

**Generations (`POST /generations` and `POST /generations/from-template`)**

Credit charges are determined based on several factors and are returned in the GET response.

| Feature         | API parameter        | Credits Charged\*                                                                                                       |
| --------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Number of cards | `numCards`           | 1-3 credits/card (varies by the text generation model Gamma selects internally)                                         |
| AI image model  | `imageOptions.model` | Standard: 2-15 credits/image. Advanced: 20-33 credits/image. Premium: 34-75 credits/image. Ultra: 30-125 credits/image. |

\* **Credit consumption rates and the actions that consume credits are subject to change.**

Template-based generations (`POST /generations/from-template`) may cost slightly more per card than standard generations.

**Illustrative scenarios for generations**

* Deck with 10 cards + 5 images using a basic image model = \~20-60 credits
* Doc with 20 cards + 15 images using a premium image model = \~320-1070 credits
* Socials with 30 cards + 30 images using an ultra image model = \~930-3900 credits

Both standard generations (`POST /generations`) and template-based generations (`POST /generations/from-template`) consume credits. Credit usage details are returned in the `credits` field of the `GET /generations/{generationId}` response, showing `deducted` and `remaining` values.

**Agent generations and edits (`POST /agent/generations` and `POST /agent/gammas/{gammaId}/edits`)**

Agent jobs are charged for the AI work the agent does while it runs, including writing, research, and the images it creates. Pricing follows the `quality` preset on the request, and the agent chooses its own image models, so the per-card and per-image prices above do not apply. The same prompt can cost a different amount from run to run because the agent does a different amount of work each time.

| `quality`  | Plans                                       |
| ---------- | ------------------------------------------- |
| `lite`     | All plans with API access                   |
| `standard` | All plans with API access                   |
| `max`      | Pro, Ultra, Teams, Business, and Enterprise |

Higher presets use more capable models and generally cost more per run. `max` requires a plan that includes it and can use more credits. Omitting `quality` uses the API default, capped at what your plan includes. Requesting `max` on a plan that does not include it returns `403` with code `agent_premium_models_restricted`.

The completed or failed response from `GET /agent/generations/{generationId}` or `GET /agent/edits/{editId}` returns `credits.deducted` (the credits removed for that job) and `credits.remaining` (your balance when the status was served). Either field is omitted when its lookup fails, so treat them as informational rather than as a billing record. To estimate costs for your use case, run a few representative prompts at the quality you plan to use and compare their `credits.deducted` values.

A job needs at least one available credit to start. If the balance is empty, the request returns `403` with code `insufficient_credits`, or the job fails with `error.reason` set to `insufficient_credits`.

To learn more about credits, visit our [Help Center](https://help.gamma.app/en/articles/7834324-how-do-ai-credits-work-in-gamma).

### Related

* [Connect integrations](/connectors/connectors-and-integrations.md) for setup instructions by platform
* [Poll for results](/guides/async-patterns-and-polling.md) for where `credits.deducted` and `credits.remaining` appear in the generation flow
* [POST /agent/generations](/agent-gamma-5/create-agent-generation.md) and [POST /agent/gammas/{gammaId}/edits](/agent-gamma-5/edit-gamma.md) for the `quality` parameter on agent requests and edits
* [Get Help](/reference/get-help.md) if you need support with pricing or API access


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/get-started/access-and-pricing.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
