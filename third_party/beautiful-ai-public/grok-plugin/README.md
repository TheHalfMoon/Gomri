# Beautiful.ai

The Beautiful.ai plugin builds presentations and edits them with you, right from the chat. Describe what you need and get a designed deck in your Beautiful.ai workspace, on your Brand Kit. Then keep going, on that deck or any you already have: rewrite a slide, add or redesign slides, switch layouts, add pictures, restructure the deck. Grok renders each slide it builds or changes, checks how it looks and fixes what doesn't look right. When the deck is ready, export it to PDF or PowerPoint, share it, or open it in the Beautiful.ai editor.

You need a Beautiful.ai account. Some features, such as AI-generated pictures, depend on your workspace's plan.

## Use it

1. Install the plugin. On first use, Grok opens the Beautiful.ai sign-in in your browser: sign in with your Beautiful.ai account, or sign up there.
2. Ask for what you need, for example:
   - "Make me a 10-slide pitch deck about our new product"
   - "Tighten the text on slide 3 of my latest presentation"
   - "Add a stock photo of a commuter on an electric bike to slide 2"
   - "Export my Q3 review to PowerPoint"
   - "Give me a public link to my pitch deck"

Grok may ask once where your pictures should come from and which Brand Kit to use, and can remember your answer for next time.

## What the plugin contains

- Skills that teach Grok how to build a presentation, edit and review slides, pick templates and lay out slide content. They are Markdown only: the plugin has no scripts, hooks or agents, and runs nothing on your computer.
- `.mcp.json`, which points at the Beautiful.ai MCP server (`https://` URL, OAuth sign-in). All work on your presentations goes through that server.

## Data

- Your requests and the slide content Grok writes are sent to the Beautiful.ai MCP server, which reads and changes presentations, slides, themes, assets and notes in the Beautiful.ai workspaces you belong to, with the permissions your account has.
- When you ask for pictures, the server finds them in stock libraries, on the web or among your Team Assets, or generates them with AI, depending on your workspace's plan and permissions, and saves them as assets of your workspace.
- To put a picture of your own on a slide, Grok uploads the file to Beautiful.ai's storage on Google Cloud Storage (`storage.googleapis.com`), through a short-lived upload URL the server issues for that one file, or sends it to the server directly. Either way the picture becomes an asset of your workspace. Nothing else is sent anywhere but the Beautiful.ai MCP server.
- Grok can save your preferences, such as where your pictures should come from, as notes in your Beautiful.ai account.
- Sharing tools create links to your presentation or share it with people you name. A public link makes the presentation viewable by anyone who has it.
- The plugin does not delete presentations and does not change your plan or billing; do that in the Beautiful.ai app.
- The plugin itself stores nothing and needs no credentials of its own: the only credential is the OAuth token Grok obtains when you sign in. How Beautiful.ai handles your data is described in its [privacy policy](https://www.beautiful.ai/privacy-policy) and [terms of service](https://www.beautiful.ai/terms-of-service).

## Support

[support.beautiful.ai](https://support.beautiful.ai)
