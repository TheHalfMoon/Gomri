> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/connectors/custom-mcp-connectors.md).

# Add custom MCP connectors

Bring your own MCP servers into Gamma so workspace members can use your team's tools and data with Gamma Agent.

Custom connectors bring your own MCP servers into Gamma. A workspace admin adds the server once, each member signs in with their own account, and Gamma Agent can then use your team's internal tools and data to create gammas.

{% hint style="info" %}
**Looking to use Gamma inside another AI tool?** This page covers bringing your MCP server into Gamma. To use Gamma from tools like Claude or ChatGPT, see [Connect integrations](/connectors/connectors-and-integrations.md).
{% endhint %}

## Quick reference

* Available on the Enterprise plan.
* Workspace admins add and manage custom connectors. Each member connects their own account.
* Your server must be a remote MCP server with an HTTPS URL and support OAuth sign-in.
* Gamma aims to only use your read-only tools.

## Why use custom connectors

Gamma Agent works best when it can see the information your team relies on. Custom connectors let it reach your team's own systems, like databases, CRMs, wikis, or analytics tools, through a hosted MCP server.

* **Ground gammas in real data**: build decks and docs from the records, metrics, and documents in your own systems
* **Keep access personal**: each member signs in with their own account, so Gamma only sees what that member can already see
* **Use them alongside other connectors**: combine a custom connector with built-in connectors like Google Drive or Notion in the same request

Example prompts:

* "Pull this quarter's top 10 accounts by ARR from our CRM and turn them into a QBR deck."
* "Find last week's incident report and create a one-page postmortem summary for leadership."

## Before you start

Check that your MCP server:

* Uses Streamable HTTP and has a public HTTPS URL for its MCP endpoint, for example `https://mcp.example.com/mcp`
* Supports OAuth sign-in with Dynamic Client Registration or Client ID Metadata Documents

If your OAuth provider requires an allow-list of redirect URLs, add `https://api.gamma.app/mcp/custom/callback`.

## Add a custom connector

Workspace admins add the connector once for the whole workspace.

{% stepper %}
{% step %}

### Open workspace settings

In Gamma, go to **Settings** → **Sharing & access** and make sure **Workspace connectors** is turned on.
{% endstep %}

{% step %}

### Add the connector

Under **Custom connectors**, click **Add connector**.
{% endstep %}

{% step %}

### Enter the server details

Enter a **Name** that members will recognize and your server's **Server URL**, then click **Add**.
{% endstep %}
{% endstepper %}

The connector now appears in your workspace's list, and members can connect to it.

## Connect your account

Each member connects their own account before Gamma Agent can use the connector.

{% stepper %}
{% step %}

### Open My connectors

Go to **Settings** → **My connectors** and find the connector under **Custom connectors**.
{% endstep %}

{% step %}

### Sign in

Click **Connect** and sign in to your account in the popup window.
{% endstep %}

{% step %}

### Ask Gamma Agent to use it

Once you see **Connector connected**, mention the connector or its data in your next request to Gamma Agent.

Pick which connectors Gamma Agent can use with a toggle in the chat box.
{% endstep %}
{% endstepper %}

## Manage custom connectors

* **Pause a connector**: admins turn the connector's toggle off in **Sharing & access**. Turn it back on to restore access.
* **Change the name or URL**: delete the connector and add it again with the new details.
* **Delete a connector**: deleting a connector disconnects every member who connected to it.
* **Disconnect your account**: members click **Disconnect** in **My connectors**.

## Troubleshooting

| Problem                                         | What to try                                                                                                                 |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| The connector can't be added                    | Check that the URL uses HTTPS, points to the MCP endpoint, and that your server supports OAuth sign-in.                     |
| Sign-in fails                                   | Add `https://api.gamma.app/mcp/custom/callback` to your OAuth provider's allowed redirect URLs, and allow popups for Gamma. |
| A tool doesn't show up                          | Make sure the tool is marked as read-only on your server.                                                                   |
| **Add connector** is greyed out or shows a lock | Requires the Enterprise plan and **Workspace connectors** turned on in **Sharing & access**.                                |

## Related

* [Connect integrations](/connectors/connectors-and-integrations.md) to use Gamma from other AI tools
* [Access and pricing](/get-started/access-and-pricing.md) for plan details
* [Model Context Protocol](https://modelcontextprotocol.io/) to learn more about MCP


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/connectors/custom-mcp-connectors.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
