> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/mcp/mcp-tools-reference.md).

# MCP tools reference

Authentication, tools, parameters, and error handling for the Gamma MCP server.

To connect a custom client, start with [Connect your own agent](/build-with-gamma/connect-your-own-agent.md); for what generation and editing preserve, see [Brand, template, and editing controls](/build-with-gamma/brand-template-editing-controls.md).

Complete reference for the Gamma MCP server's authentication, available tools, input parameters, and error handling.

## Quick reference

* All requests require an OAuth 2.0 Bearer token.
* Available tools: `generate`, `generate_multi_page_gamma`, `generate_from_template`, `get_generation_status`, `generate_image`, `get_image_generation_status`, `export_gamma`, `get_export_status`, `edit_gamma`, `get_edit_status`, `get_gammas`, `search_gammas`, `search_templates`, `read_gamma`, `get_gamma_comments`, `get_gamma_analytics`, `get_gamma_card_analytics`, `get_gamma_viewer_analytics`, `get_gamma_viewer_detail_analytics`, `get_themes`, and `get_folders`.
* `generate`, `generate_multi_page_gamma`, and `generate_from_template` are asynchronous. They return a `generationId`; call `get_generation_status` until `status` is `completed` or `failed`. Once completed, the `generationId` can be passed to `read_gamma`, `edit_gamma`, or `export_gamma` in place of the Gamma ID; see [Using a generation ID in place of a Gamma ID](#using-a-generation-id-in-place-of-a-gamma-id).
* `export_gamma` is asynchronous. It returns an `exportId`; call `get_export_status` until `status` is `completed` or `failed`.
* `generate_image` creates a standalone image and is asynchronous. It returns an `imageGenerationId`; call `get_image_generation_status` until `status` is `completed` or `failed`. Both tools can return a `mediaLibraryUrl` for the workspace media library, and the completed image can carry a `savedMediaId` for a link to that one image.
* `edit_gamma` changes the content of an existing gamma and is asynchronous. It returns an `editId`; call `get_edit_status` until `status` is `completed` or `failed`.
* `edit_gamma` and `get_edit_status` appear in the tool list when editing is available for the connected account. Check the tool list before offering MCP editing.
* Use `get_gammas` to browse existing gammas and templates (pass `createdByMe: true` to limit results to gammas the user created), `search_gammas` to find gammas by their content, `search_templates` to find workspace templates and official Gamma explore templates, and `read_gamma` (read-only, accepts a file ID or full URL) to read one.
* Analytics tools (`get_gamma_analytics`, `get_gamma_card_analytics`, `get_gamma_viewer_analytics`, `get_gamma_viewer_detail_analytics`) report engagement for an existing gamma; data is eventually consistent and can lag by about an hour.
* OAuth discovery is available at `/.well-known/oauth-protected-resource`.
* Errors return `{ "error": "...", "isError": true }`. Failures caused by a plan or credit limit also carry `planLimitExceeded: true` and the workspace's live limits; see [Plan limit failures](#plan-limit-failures).
* `tools/list` responses carry the cache hints `ttlMs: 60000` and `cacheScope: "private"`. Hosts that support SEP-2549 may cache the per-user tool list for up to 60 seconds.

## Authentication

The Gamma MCP server uses OAuth 2.0. Every request must include a valid Bearer token. For a walkthrough of the same OAuth flow against the REST API, see [Authenticate with OAuth](/get-started/authenticate-with-oauth.md).

### Authorization header

Include your token with each request:

```
Authorization: Bearer <your-oauth-token>
```

### OAuth discovery

The server implements [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728) (OAuth Protected Resource Metadata). Clients retrieve OAuth configuration at:

```
GET /.well-known/oauth-protected-resource
```

### Dynamic client registration

The authorization server supports [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591) Dynamic Client Registration. Discover the registration endpoint URL from the authorization server metadata obtained via the OAuth discovery endpoint above.

### OAuth consent permissions

When a user connects your app, Gamma asks them to approve these permissions:

* Create gammas in your workspace
* Read gammas in your workspace
* List folders from your workspace
* List themes from your workspace

### Authentication errors

A failed authentication -- including a token whose Gamma access has been revoked -- returns `401 Unauthorized` with a `WWW-Authenticate` header:

```
WWW-Authenticate: Bearer resource_metadata="https://<server>/.well-known/oauth-protected-resource"
```

Use the `resource_metadata` URI to discover the authorization server and initiate the OAuth flow. Completing a fresh authorization resolves the error.

## Tools overview

| Tool                                | Description                                                                                    | Read-only | Destructive | Idempotent |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- | --------- | ----------- | ---------- |
| `generate`                          | Create presentations, documents, webpages, or social posts from scratch                        | No        | No          | No         |
| `generate_multi_page_gamma`         | Create one multi-page Gamma (several pages under one URL) in a single request                  | No        | No          | No         |
| `generate_from_template`            | Create a new gamma from an existing template gamma                                             | No        | No          | No         |
| `get_generation_status`             | Check the status of a `generate`, `generate_multi_page_gamma`, or `generate_from_template` job | Yes       | No          | Yes        |
| `generate_image`                    | Generate one standalone image from a text prompt                                               | No        | No          | No         |
| `get_image_generation_status`       | Check the status of a `generate_image` job and get the image URL                               | Yes       | No          | Yes        |
| `export_gamma`                      | Export an existing gamma to PDF, PPTX, or PNG                                                  | No        | No          | No         |
| `get_export_status`                 | Check the status of an export and get the download link                                        | Yes       | No          | Yes        |
| `edit_gamma`                        | Edit the content of an existing gamma from a natural-language instruction                      | No        | Yes         | No         |
| `get_edit_status`                   | Check the status of an `edit_gamma` job and get the summary of changes                         | Yes       | No          | Yes        |
| `get_gammas`                        | Browse or search existing gammas and templates                                                 | Yes       | No          | Yes        |
| `search_gammas`                     | Full-text search over gamma titles and body text                                               | Yes       | No          | Yes        |
| `search_templates`                  | Search workspace templates and official Gamma explore templates                                | Yes       | No          | Yes        |
| `read_gamma`                        | Read the full content of an existing Gamma                                                     | Yes       | No          | Yes        |
| `get_gamma_comments`                | List comment threads (and replies) on an existing Gamma                                        | Yes       | No          | Yes        |
| `get_gamma_analytics`               | Get engagement summary analytics for a Gamma                                                   | Yes       | No          | Yes        |
| `get_gamma_card_analytics`          | Get card-by-card engagement for a Gamma                                                        | Yes       | No          | Yes        |
| `get_gamma_viewer_analytics`        | List the people who viewed a Gamma                                                             | Yes       | No          | Yes        |
| `get_gamma_viewer_detail_analytics` | Get one viewer's detailed engagement with a Gamma                                              | Yes       | No          | Yes        |
| `get_themes`                        | Browse or search the Gamma theme library                                                       | Yes       | No          | Yes        |
| `get_folders`                       | Browse or search your Gamma folders                                                            | Yes       | No          | Yes        |

## generate

Create a new presentation, document, webpage, or social post from scratch. Each call creates new content and returns a generation job.

### Input parameters

| Parameter                | Type            | Required | Description                                                                                              |
| ------------------------ | --------------- | -------- | -------------------------------------------------------------------------------------------------------- |
| `inputText`              | `string`        | Yes      | Content to generate from: a brief prompt, outline, or full draft                                         |
| `title`                  | `string`        | No       | Title for the generated Gamma (1–500 characters); inferred from content if omitted                       |
| `textMode`               | `enum`          | No       | How to handle the input text: `generate`, `condense`, or `preserve`                                      |
| `format`                 | `enum`          | No       | Output type: `presentation`, `document`, `social`, or `webpage`                                          |
| `numCards`               | `int`           | No       | Number of slides, cards, or pages to generate                                                            |
| `cardSplit`              | `enum`          | No       | How content is divided into cards: `auto` or `inputTextBreaks`                                           |
| `themeId`                | `string`        | No       | Theme ID from `get_themes`, applied to the generated gamma. See [Unknown theme IDs](#unknown-theme-ids)  |
| `folderId`               | `string`        | No       | Folder ID from `get_folders` to save the generated content in                                            |
| `folderIds`              | `array[string]` | No       | Deprecated. Use `folderId`. At most one entry, treated as `folderId`; `folderId` wins when both are sent |
| `additionalInstructions` | `string`        | No       | Extra guidance for the generator                                                                         |
| `exportAs`               | `enum`          | No       | Export format: `pptx`, `pdf`, or `png`. `png` returns a `.zip` with one PNG per card                     |

### Text options

Optional `textOptions` object for controlling text generation.

| Parameter  | Type     | Description                                                                   |
| ---------- | -------- | ----------------------------------------------------------------------------- |
| `amount`   | `enum`   | Text density per slide or section: `brief`, `medium`, `detailed`, `extensive` |
| `tone`     | `string` | Writing tone, such as `professional` or `casual`                              |
| `audience` | `string` | Target audience, such as `executives` or `students`                           |
| `language` | `string` | Language code, such as `en`, `es`, or `fr`                                    |

### Image options

Optional `imageOptions` object for controlling image sourcing.

| Parameter     | Type     | Description                                                                                                                                                             |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `source`      | `enum`   | Image source: `aiGenerated`, `webAllImages`, `webFreeToUse`, `webFreeToUseCommercially`, `pictographic`, `giphy`, `pexels`, `themeAccent`, `placeholder`, or `noImages` |
| `model`       | `string` | AI image model to use when `source` is `aiGenerated`. Accepts the same model IDs as the REST API — see [Image models](/reference/image-model-accepted-values.md)        |
| `stylePreset` | `enum`   | Art style preset: `photorealistic`, `illustration`, `abstract`, `3D`, `lineArt`, or `custom`                                                                            |
| `style`       | `string` | Custom style description for AI images when `stylePreset` is `custom` or omitted                                                                                        |

### Card options

Optional `cardOptions` object for layout and header/footer configuration.

| Parameter      | Type     | Description                                                                                         |
| -------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `dimensions`   | `enum`   | Aspect ratio or page size: `16x9`, `4x3`, `fluid`, `letter`, `a4`, `pageless`, `1x1`, `4x5`, `9x16` |
| `headerFooter` | `object` | Header and footer configuration                                                                     |

The `headerFooter` object contains six slot positions and two visibility flags. All properties are optional.

| Parameter           | Type      | Description                            |
| ------------------- | --------- | -------------------------------------- |
| `topLeft`           | `object`  | Top-left header slot                   |
| `topCenter`         | `object`  | Top-center header slot                 |
| `topRight`          | `object`  | Top-right header slot                  |
| `bottomLeft`        | `object`  | Bottom-left footer slot                |
| `bottomCenter`      | `object`  | Bottom-center footer slot              |
| `bottomRight`       | `object`  | Bottom-right footer slot               |
| `hideFromFirstCard` | `boolean` | Hide header/footer from the first card |
| `hideFromLastCard`  | `boolean` | Hide header/footer from the last card  |

Each slot object accepts:

| Parameter | Type     | Required | Description                                                  |
| --------- | -------- | -------- | ------------------------------------------------------------ |
| `type`    | `enum`   | Yes      | Content type: `cardNumber`, `image`, or `text`               |
| `source`  | `enum`   | No       | Image source when `type` is `image`: `themeLogo` or `custom` |
| `src`     | `string` | No       | Image URL when `type` is `image` and `source` is `custom`    |
| `value`   | `string` | No       | Text content when `type` is `text`                           |
| `size`    | `enum`   | No       | Image size: `sm`, `md`, `lg`, `xl`                           |

### Sharing options

Optional `sharingOptions` object for controlling access after generation.

| Parameter         | Type     | Description                                                                  |
| ----------------- | -------- | ---------------------------------------------------------------------------- |
| `workspaceAccess` | `enum`   | Workspace member access: `edit`, `comment`, `view`, `noAccess`, `fullAccess` |
| `externalAccess`  | `enum`   | External user access: `edit`, `comment`, `view`, `noAccess`                  |
| `emailOptions`    | `object` | Share via email to specific recipients                                       |

`emailOptions` accepts:

| Parameter    | Type            | Required | Description                                                     |
| ------------ | --------------- | -------- | --------------------------------------------------------------- |
| `recipients` | `array[string]` | Yes      | Email addresses to share with                                   |
| `access`     | `enum`          | Yes      | Recipient access level: `edit`, `comment`, `view`, `fullAccess` |

### Output

| Field          | Type     | Description                                    |
| -------------- | -------- | ---------------------------------------------- |
| `generationId` | `string` | Unique ID for the generation                   |
| `status`       | `enum`   | Initial status is `pending`                    |
| `gammaUrl`     | `string` | Link to the generation in Gamma when available |

Call `get_generation_status` with the returned `generationId` until the job reaches `completed` or `failed`.

## generate\_from\_template

Create a new gamma by adapting, remixing, or transforming an existing template gamma. Use `get_gammas` with `type: template` or the `workspaceTemplates` list from `search_templates` if you need to find the right template ID first.

### Input parameters

| Parameter        | Type            | Required | Description                                                                                                                                                                                                                                                              |
| ---------------- | --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `gammaId`        | `string`        | Yes      | File ID of a template gamma in the user's workspace: the `id` of a `get_gammas` result with type `template`, the `id` of a `search_templates` `workspaceTemplates` hit, or a user-provided template ID. IDs from `search_templates` `exploreTemplates` are not supported |
| `prompt`         | `string`        | Yes      | Instructions and/or content for the new gamma                                                                                                                                                                                                                            |
| `title`          | `string`        | No       | Title for the generated Gamma (1–500 characters); inferred from content if omitted                                                                                                                                                                                       |
| `themeId`        | `string`        | No       | Theme ID from `get_themes`. Not supported for agent generations: the call fails before generating with an error asking you to retry without `themeId`. See [Unknown theme IDs](#unknown-theme-ids)                                                                       |
| `imageOptions`   | `object`        | No       | Optional AI image overrides for templates that use AI-generated images                                                                                                                                                                                                   |
| `sharingOptions` | `object`        | No       | Sharing and permissions options                                                                                                                                                                                                                                          |
| `folderId`       | `string`        | No       | Folder ID from `get_folders` to save the generated content in                                                                                                                                                                                                            |
| `folderIds`      | `array[string]` | No       | Deprecated. Use `folderId`. At most one entry, treated as `folderId`; `folderId` wins when both are sent                                                                                                                                                                 |
| `exportAs`       | `enum`          | No       | Export format: `pptx`, `pdf`, or `png`. `png` returns a `.zip` with one PNG per card                                                                                                                                                                                     |

`imageOptions` accepts:

| Parameter | Type     | Description                                                                                                                       |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `model`   | `string` | AI image model to use. Accepts the same model IDs as the REST API — see [Image models](/reference/image-model-accepted-values.md) |
| `style`   | `string` | Custom style description for AI-generated images                                                                                  |

### Output

| Field          | Type     | Description                                                                                                 |
| -------------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `generationId` | `string` | Unique ID for the generation                                                                                |
| `status`       | `enum`   | Initial status is `pending`                                                                                 |
| `gammaUrl`     | `string` | Link to the generation in Gamma when available                                                              |
| `warnings`     | `string` | File-level warnings about ignored or adjusted options (for example, sharing, folder, or dimension settings) |

Call `get_generation_status` with the returned `generationId` until the job reaches `completed` or `failed`.

## generate\_multi\_page\_gamma

Create a single Gamma containing several distinct pages under one URL in one request — ideal for sales rooms, proposal sites, onboarding portals, and microsites. Prefer `generate` for a single presentation, document, webpage, or social post; use this only when the user wants several distinct pages within one Gamma. This tool creates new content and cannot edit an existing Gamma.

### Input parameters

Provide `pages[]` in the order the pages should appear. Per-page settings live on each entry; file-wide settings (theme, folders, dimensions, sharing, export, overall title) apply to all pages.

| Parameter        | Type            | Required | Description                                                                                                     |
| ---------------- | --------------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| `pages`          | `array[object]` | Yes      | Ordered list of pages to generate (1–50). Each entry becomes a distinct page with its own deep link             |
| `title`          | `string`        | No       | Title for the overall Gamma (1–500 characters); inferred if omitted                                             |
| `publish`        | `boolean`       | No       | When `true`, publish the result as a live multi-page site on a Gamma-generated subdomain once all pages succeed |
| `themeId`        | `string`        | No       | Theme ID from `get_themes`                                                                                      |
| `folderId`       | `string`        | No       | Folder ID from `get_folders` to save the generated content in                                                   |
| `folderIds`      | `array[string]` | No       | Deprecated. Use `folderId`. At most one entry, treated as `folderId`; `folderId` wins when both are sent        |
| `cardOptions`    | `object`        | No       | Layout and header/footer configuration — same shape as the [`generate`](#generate) tool's card options          |
| `sharingOptions` | `object`        | No       | Access after generation — same shape as the [`generate`](#generate) tool's sharing options                      |
| `exportAs`       | `enum`          | No       | Export format: `pptx`, `pdf`, or `png`. `png` returns a `.zip` with one PNG per card                            |

Each `pages[]` entry accepts:

| Parameter                | Type     | Required | Description                                                                                                                          |
| ------------------------ | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `inputText`              | `string` | Yes      | Content to generate this page from                                                                                                   |
| `title`                  | `string` | No       | Title for this page (1–500 characters)                                                                                               |
| `path`                   | `string` | No       | URL slug for this page, e.g. `/pricing` (1–500 characters). Honored only for pages after the first; omitted → derived from the title |
| `additionalInstructions` | `string` | No       | Extra guidance for the generator                                                                                                     |
| `textMode`               | `enum`   | No       | How to handle the input text: `generate` (default), `condense`, or `preserve`                                                        |
| `format`                 | `enum`   | No       | Output type: `presentation`, `document`, `social`, or `webpage`                                                                      |
| `numCards`               | `int`    | No       | Number of cards to generate for this page                                                                                            |
| `cardSplit`              | `enum`   | No       | How content is divided into cards: `auto` or `inputTextBreaks`                                                                       |
| `textOptions`            | `object` | No       | Text controls — same shape as the [`generate`](#generate) tool's text options                                                        |
| `imageOptions`           | `object` | No       | Image sourcing — same shape as the [`generate`](#generate) tool's image options                                                      |

### Output

| Field          | Type            | Description                                                                                  |
| -------------- | --------------- | -------------------------------------------------------------------------------------------- |
| `generationId` | `string`        | Unique ID for the generation                                                                 |
| `status`       | `enum`          | Initial status is `pending`                                                                  |
| `gammaUrl`     | `string`        | Link to the generation in Gamma when available                                               |
| `pages`        | `array[object]` | Per-page results: `gammaId`, `gammaUrl`, `status`, and `error` / `exportUrl` when applicable |
| `warnings`     | `string`        | File-level warnings about ignored or adjusted options                                        |

Call `get_generation_status` with the returned `generationId` until the job reaches `completed` or `failed`.

## get\_generation\_status

Check the status of a generation started with `generate`, `generate_multi_page_gamma`, or `generate_from_template`.

### Input

| Parameter      | Type     | Required | Description                                                                                                                                                       |
| -------------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `generationId` | `string` | Yes      | Generation ID returned by the create tool, or the `/generations/` URL it returned. IDs prefixed `gen_` identify agent generations and are accepted in either form |

### Output

| Field               | Type     | Description                                                                                                                                                           |
| ------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `generationId`      | `string` | Unique ID for the generation                                                                                                                                          |
| `status`            | `enum`   | `pending`, `completed`, or `failed`                                                                                                                                   |
| `progress`          | `object` | While `pending`, may include `done`, `total`, `percent` (0–99), and per-stage counts in `stages` once card building starts. Only `completed` is 100%                  |
| `gammaUrl`          | `string` | URL to the created Gamma when the job is completed                                                                                                                    |
| `exportUrl`         | `string` | Download URL for the export file when available. For `exportAs: png`, this is a `.zip` with one PNG per card. Expires after about one week; treat the URL as a secret |
| `credits.deducted`  | `int`    | Credits deducted for the generation. Omitted for agent generations (`gen_` IDs)                                                                                       |
| `credits.remaining` | `int`    | Remaining credits after the generation. Omitted for agent generations (`gen_` IDs)                                                                                    |
| `warnings`          | `string` | Non-fatal warnings about ignored or adjusted options, one per line, when the generation reports any                                                                   |
| `error`             | `string` | Error message when the generation fails                                                                                                                               |

### Using a generation ID in place of a Gamma ID

Once a generation completes, you can read, edit, or export the Gamma it created without looking up its file ID: pass the `generationId`, or the `/generations/<generationId>` URL, as the `gammaIdOrUrl` of `read_gamma`, `edit_gamma`, or `export_gamma`. The comment and analytics tools do not accept generation IDs.

A generation ID resolves only once the generation has finished. Until then, and in a few other cases, the tool returns an error instead of acting:

| Case                                                           | What the tool returns                                                                                                                                         |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Generation still `pending`                                     | An error telling you to check `get_generation_status` (a few seconds between checks, not a tight loop) and retry the same call once the status is `completed` |
| Generation `failed`                                            | An error with the generation's failure message — there is no completed Gamma to act on through this generation ID                                             |
| Generation created several pages (`generate_multi_page_gamma`) | An error listing each page's `gammaId` and `gammaUrl`; call the tool again with the specific page's `gammaId`                                                 |

A plain token prefixed `gen_` is an agent generation ID and is looked up as a generation directly. Any other plain token is tried as a Gamma file ID first and looked up as a generation only if no Gamma with that ID is accessible. If it is neither, you get the original `404 Not found`.

## generate\_image

Generate one standalone image from a text prompt — an illustration, scene, photo, or abstract graphic on its own, not a gamma.

This tool is asynchronous: it returns immediately with an `imageGenerationId` and `status: pending`. Call `get_image_generation_status` with that ID until the image is ready — do not call `generate_image` again to check progress, as that starts a new, separately billed generation.

### Input

| Parameter         | Type            | Required | Description                                                                                                                                                                                            |
| ----------------- | --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `prompt`          | `string`        | Yes      | Description of the image to generate (1–5,000 characters). Include background treatments here too, such as "on a white background"                                                                     |
| `type`            | `enum`          | No       | Visual style: `illustration` (default), `scene` (narrative illustration), `photo` (photorealistic), or `abstract`                                                                                      |
| `sizePreset`      | `enum`          | No       | Aspect ratio: `social-square` (1:1, default), `social-portrait` (4:5), `story` (9:16), `banner` (16:9), or `slide` (16:9). Exact pixel dimensions are chosen by the model                              |
| `themeId`         | `string`        | No       | Theme ID from `get_themes` to brand the image; omit for the workspace default theme                                                                                                                    |
| `referenceImages` | `array[object]` | No       | Up to 4 reference images whose subject (a character or product) should appear in the generated image. Each entry accepts `url` (required, must be `https://`) and `role` (only `subject` is supported) |

When `referenceImages` are provided, the references drive the look and `type` and `themeId` are ignored.

### Output

| Field               | Type            | Description                                                                |
| ------------------- | --------------- | -------------------------------------------------------------------------- |
| `imageGenerationId` | `string`        | Unique ID for the image generation                                         |
| `status`            | `enum`          | Initial status is `pending`                                                |
| `warnings`          | `array[object]` | Warnings about ignored or adjusted options, each with `code` and `message` |
| `generatedTime`     | `string`        | ISO 8601 timestamp of when the generation was queued, when available       |
| `mediaLibraryUrl`   | `string`        | Link to your workspace media library in Gamma, when available              |

Image generations charge credits. Call `get_image_generation_status` with the returned `imageGenerationId` until the job reaches `completed` or `failed`.

## get\_image\_generation\_status

Check the status of an image generation started with `generate_image`, and retrieve the image URL once it is ready. Each call returns the current status; poll it every few seconds rather than in a tight loop.

### Input

| Parameter           | Type     | Required | Description                                      |
| ------------------- | -------- | -------- | ------------------------------------------------ |
| `imageGenerationId` | `string` | Yes      | Image generation ID returned by `generate_image` |

### Output

| Field               | Type            | Description                                                                                                                                                         |
| ------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `imageGenerationId` | `string`        | Unique ID for the image generation                                                                                                                                  |
| `status`            | `enum`          | `pending`, `completed`, or `failed`                                                                                                                                 |
| `image`             | `object`        | The generated image when completed: `url`, `width`, `height`, `aspectRatioUsed`, and `savedMediaId` when available                                                  |
| `warnings`          | `array[object]` | Warnings about ignored or adjusted options, each with `code` and `message`                                                                                          |
| `error`             | `string`        | Error message when the generation fails                                                                                                                             |
| `retryable`         | `boolean`       | Present on failure: whether retrying the same request could succeed. Invalid input, such as an unknown `themeId` or a blocked reference image URL, is not retryable |
| `errorStatusCode`   | `int`           | Present on failure when the API reported one: the HTTP status behind the failure                                                                                    |
| `credits.deducted`  | `int`           | Credits deducted for the generation                                                                                                                                 |
| `credits.remaining` | `int`           | Remaining credits after the generation                                                                                                                              |
| `mediaLibraryUrl`   | `string`        | Link to your workspace media library in Gamma, returned for every status when available                                                                             |

Generated images are saved to your workspace media library. When the result carries both `mediaLibraryUrl` and `image.savedMediaId`, append the ID to the URL — `{mediaLibraryUrl}/{savedMediaId}` — to link straight to that one image. The media library entry stays available after the generation job itself ages out of the status endpoint, so it is the durable link to share with a user.

## export\_gamma

Export an existing gamma to a downloadable file. This starts the export and returns immediately with an `exportId`; the export runs in the background. Call `get_export_status` with that `exportId` to get the download link once it is ready — do not call `export_gamma` again to check progress, as that starts a new export.

### Input

| Parameter      | Type     | Required | Description                                                                                                                                                                                                                                        |
| -------------- | -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gammaIdOrUrl` | `string` | Yes      | Gamma file ID, full Gamma URL, or the `generationId` or `/generations/` URL from a completed generation ([details](#using-a-generation-id-in-place-of-a-gamma-id)). Example: `g5aykcic8ujm71s` or `https://gamma.app/docs/My-Deck-g5aykcic8ujm71s` |
| `exportAs`     | `enum`   | Yes      | Export format: `pdf`, `pptx`, or `png`. `png` returns a `.zip` with one PNG per card                                                                                                                                                               |

### Output

| Field      | Type     | Description                         |
| ---------- | -------- | ----------------------------------- |
| `exportId` | `string` | Unique ID for the export job        |
| `status`   | `enum`   | Initial status is `pending`         |
| `gammaId`  | `string` | File ID of the gamma being exported |
| `exportAs` | `enum`   | The requested export format         |

The connected user must have view access to the gamma in the selected workspace. Archived gammas cannot be exported. Call `get_export_status` with the returned `exportId` until the job reaches `completed` or `failed`.

## get\_export\_status

Check the status of an export started with `export_gamma`, and retrieve the download link once it is ready.

### Input

| Parameter  | Type     | Required | Description                          |
| ---------- | -------- | -------- | ------------------------------------ |
| `exportId` | `string` | Yes      | Export ID returned by `export_gamma` |

### Output

| Field       | Type     | Description                                                                                                                                                                                                                                                 |
| ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `exportId`  | `string` | Unique ID for the export job                                                                                                                                                                                                                                |
| `status`    | `enum`   | `pending`, `completed`, or `failed`                                                                                                                                                                                                                         |
| `gammaId`   | `string` | File ID of the exported gamma                                                                                                                                                                                                                               |
| `exportAs`  | `enum`   | The requested export format                                                                                                                                                                                                                                 |
| `exportUrl` | `string` | Download URL when the export is completed. For `exportAs: png`, this is a `.zip` with one PNG per card. Anyone with this URL can download the file until it expires (about one week), and access is not tied to your API key, so treat the link as a secret |
| `error`     | `string` | Customer-safe error message when the export fails                                                                                                                                                                                                           |
| `reason`    | `enum`   | Machine-readable failure reason when the export fails: `render_timeout`, `deck_too_large`, `no_content`, or `export_failed`                                                                                                                                 |

## edit\_gamma

Edit an existing gamma from a natural-language instruction — reword, restructure, add, or remove content. Use `generate` instead when the user wants new content rather than a change to a gamma they already have.

This tool is asynchronous: it returns immediately with an `editId` and `status: pending`. Call `get_edit_status` with that ID until the edit is done — do not call `edit_gamma` again to check progress, as that starts a brand-new edit.

### Input

| Parameter           | Type      | Required | Description                                                                                                                                                                                                                                        |
| ------------------- | --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gammaIdOrUrl`      | `string`  | Yes      | Gamma file ID, full Gamma URL, or the `generationId` or `/generations/` URL from a completed generation ([details](#using-a-generation-id-in-place-of-a-gamma-id)). Example: `g5aykcic8ujm71s` or `https://gamma.app/docs/My-Deck-g5aykcic8ujm71s` |
| `prompt`            | `string`  | Yes      | Natural-language instruction describing the edit (1–10,000 characters). Example: "Change the title of the first card to Q3 Review"                                                                                                                 |
| `disableConnectors` | `boolean` | No       | Set to `true` to keep this edit from using workspace connectors such as Notion or Slack. Omit it for normal behavior                                                                                                                               |

### Output

| Field      | Type     | Description                    |
| ---------- | -------- | ------------------------------ |
| `editId`   | `string` | Unique ID for the edit job     |
| `status`   | `enum`   | Initial status is `pending`    |
| `gammaUrl` | `string` | Link to the gamma being edited |

The connected user must have at least edit access to the gamma in the selected workspace. Archived gammas cannot be edited. Each edit changes one page — the page in the URL, or the gamma's main page. It cannot add pages. Only one edit can run on a page at a time, so wait for the current edit to reach `completed` or `failed` before starting another. Call `get_edit_status` with the returned `editId` until the job reaches `completed` or `failed`.

## get\_edit\_status

Check the status of an edit started with `edit_gamma`, and retrieve the summary of changes once it is done. Poll it every few seconds rather than in a tight loop.

### Input

| Parameter | Type     | Required | Description                      |
| --------- | -------- | -------- | -------------------------------- |
| `editId`  | `string` | Yes      | Edit ID returned by `edit_gamma` |

### Output

| Field      | Type     | Description                                                                                                                                                                         |
| ---------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `editId`   | `string` | Unique ID for the edit job                                                                                                                                                          |
| `status`   | `enum`   | `pending`, `completed`, or `failed`                                                                                                                                                 |
| `gammaUrl` | `string` | Link to the edited gamma                                                                                                                                                            |
| `summary`  | `string` | Summary of the applied changes when the edit is completed                                                                                                                           |
| `error`    | `string` | Customer-safe error message when the edit fails                                                                                                                                     |
| `reason`   | `enum`   | Machine-readable failure reason when the edit fails: `target_not_found`, `unsupported_target`, `access_revoked`, `insufficient_credits`, `timeout`, `unavailable`, or `edit_failed` |

## get\_gammas

Browse or search the user's existing gammas, including templates.

### Input parameters

| Parameter     | Type      | Description                                                                                                            |
| ------------- | --------- | ---------------------------------------------------------------------------------------------------------------------- |
| `query`       | `string`  | Search gammas by title; minimum 3 characters                                                                           |
| `type`        | `enum`    | Filter by gamma type: `template`, `regular`, or `all`                                                                  |
| `limit`       | `int`     | Maximum number of results to return; default `25`, max `50`                                                            |
| `createdByMe` | `boolean` | When `true`, return only gammas the connected user created; default `false`, which returns every gamma they can access |
| `after`       | `string`  | Cursor from a previous response for pagination                                                                         |

When paginating, keep `query` and `type` the same between calls and only advance the `after` cursor.

Use `createdByMe: true` when the user asks for gammas they created — gammas they only have access to, such as shared or collaborated-on gammas, are excluded.

### Output

| Field                   | Type             | Description                                      |
| ----------------------- | ---------------- | ------------------------------------------------ |
| `gammas`                | `array[object]`  | Array of matching gammas                         |
| `gammas[].id`           | `string`         | Unique gamma identifier                          |
| `gammas[].title`        | `string`         | Gamma title                                      |
| `gammas[].type`         | `enum`           | `template` or `regular`                          |
| `gammas[].url`          | `string`         | URL to open the gamma                            |
| `gammas[].thumbnailUrl` | `string \| null` | Thumbnail image URL when available               |
| `gammas[].themeId`      | `string \| null` | Theme ID when available                          |
| `gammas[].createdTime`  | `string`         | ISO-8601 timestamp of creation time              |
| `gammas[].updatedTime`  | `string`         | ISO-8601 timestamp of last modification          |
| `hasMore`               | `boolean`        | Whether additional results are available         |
| `nextCursor`            | `string`         | Cursor for the next page when more results exist |

## search\_gammas

Full-text search over the gammas the user can access, matched against titles and body text. Use it when the user is looking for gammas by topic, phrase, or content; use `get_gammas` for title-based browsing and template discovery.

Maps to `GET /gammas/search`. If document search is temporarily unavailable, the call may fail with a service-unavailable error; retry later.

### Input parameters

| Parameter         | Type      | Required | Description                                                                        |
| ----------------- | --------- | -------- | ---------------------------------------------------------------------------------- |
| `q`               | `string`  | No       | Full-text query matched against titles and body text; results are relevance-ranked |
| `createdBy`       | `string`  | No       | Restrict to gammas created by a user: `me`, an email address, or a user ID         |
| `updatedAfter`    | `string`  | No       | ISO-8601 date; only gammas last updated at or after this time                      |
| `updatedBefore`   | `string`  | No       | ISO-8601 date; only gammas last updated at or before this time                     |
| `includeArchived` | `boolean` | No       | Also search archived gammas; default `false`                                       |
| `limit`           | `int`     | No       | Maximum number of hits; default `10`, max `25`                                     |

Omit `q` and set at least one of `createdBy`, `updatedAfter`, or `updatedBefore` to browse matching gammas ordered by last-updated descending.

### Output

| Field                | Type             | Description                                                                                                     |
| -------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
| `hits`               | `array[object]`  | Relevance-ranked search hits                                                                                    |
| `hits[].id`          | `string`         | Unique gamma identifier                                                                                         |
| `hits[].title`       | `string \| null` | Gamma title                                                                                                     |
| `hits[].url`         | `string`         | URL to view the gamma                                                                                           |
| `hits[].highlight`   | `string \| null` | Snippet from the gamma text, usually centered on the match; can start at the beginning of the text or be `null` |
| `hits[].createdBy`   | `string \| null` | Display name of the creator, or their email when there is no display name                                       |
| `hits[].updatedTime` | `string \| null` | ISO-8601 timestamp of the last update                                                                           |
| `hits[].archived`    | `boolean`        | Whether the gamma is archived                                                                                   |

## search\_templates

Search templates in the user's workspace and the official Gamma explore templates. The response contains two separate lists because they differ in what they can be used for: `workspaceTemplates` hits can be passed to `generate_from_template`; `exploreTemplates` hits are for browsing and preview only.

### Input parameters

| Parameter | Type     | Required | Description                                                                                                                                      |
| --------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `q`       | `string` | No       | Search query, up to 2,000 characters. Both workspace and explore templates are relevance-ranked against the query. Omit `q` to browse both lists |
| `limit`   | `int`    | No       | Maximum number of hits per list; default `10`, max `25`                                                                                          |

### Output

| Field                             | Type             | Description                                                                                                                                      |
| --------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `workspaceTemplates`              | `array[object]`  | Templates from the user's workspace: relevance-ranked when `q` is given, otherwise ordered by last edited, most recent first                     |
| `workspaceTemplates[].id`         | `string`         | Template identifier; pass it through unchanged as the `gammaId` input to `generate_from_template`                                                |
| `workspaceTemplates[].title`      | `string \| null` | Template title                                                                                                                                   |
| `workspaceTemplates[].url`        | `string`         | URL to view the template                                                                                                                         |
| `workspaceTemplates[].previewUrl` | `string \| null` | Preview image URL when available                                                                                                                 |
| `exploreTemplates`                | `array[object]`  | Official Gamma explore templates, relevance-ranked when `q` is given                                                                             |
| `exploreTemplates[].id`           | `string`         | Explore template identifier; not accepted by `generate_from_template`, but usable as `templateId` on the REST `POST /agent/generations` endpoint |
| `exploreTemplates[].title`        | `string \| null` | Template title                                                                                                                                   |
| `exploreTemplates[].url`          | `string`         | URL to view the template                                                                                                                         |
| `exploreTemplates[].thumbnailUrl` | `string \| null` | Thumbnail image URL when available                                                                                                               |
| `exploreTemplates[].previewUrl`   | `string \| null` | Preview image URL when available                                                                                                                 |

{% hint style="warning" %}
Only `workspaceTemplates` hits are valid `gammaId` inputs to `generate_from_template`; passing an `exploreTemplates` id is rejected by that tool. To generate from an Explore template, use its id as `templateId` on the REST `POST /agent/generations` endpoint, or link it by `url`.
{% endhint %}

`generate_from_template` checks a workspace template's eligibility at generation time and can reject some templates (for example multi-page or site-bound templates). When a hit is rejected, try another `workspaceTemplates` hit.

## read\_gamma

Read the content of an existing Gamma presentation or document. Use this when you want to inspect, reference, or learn from a Gamma that already exists.

This tool is read-only and idempotent. It cannot edit the Gamma.

### Input

| Parameter      | Type     | Required | Description                                                                                                                                                                                                                                        |
| -------------- | -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gammaIdOrUrl` | `string` | Yes      | Gamma file ID, full Gamma URL, or the `generationId` or `/generations/` URL from a completed generation ([details](#using-a-generation-id-in-place-of-a-gamma-id)). Example: `g5aykcic8ujm71s` or `https://gamma.app/docs/My-Deck-g5aykcic8ujm71s` |

### Response format

Returns formatted text that includes the Gamma title and the full content of every page in order. The tool is designed to surface human-readable content, not raw HTML or JSON.

* `Title: <gamma title>` identifies the Gamma title.
* `=== Page N: <title> ===` marks each page or card in original order.
* Each page body contains the full human-readable content for that page, including text, images, videos, embeds, charts, tables, diagrams, and other visuals.

The connected user must have view access to the Gamma in the selected workspace. Archived gammas cannot be read.

## get\_themes

Browse or search the Gamma theme library. Use the returned `id` in the `generate` or `generate_from_template` tool's `themeId` parameter.

If the user references a theme by name, search by name. Otherwise, fetch the full list and choose based on tone and color keywords.

### Input parameters

| Parameter | Type     | Description                     |
| --------- | -------- | ------------------------------- |
| `name`    | `string` | Optional. Search themes by name |

### Output

| Field                    | Type            | Description                           |
| ------------------------ | --------------- | ------------------------------------- |
| `themes`                 | `array[object]` | Array of theme objects                |
| `themes[].id`            | `string`        | Theme ID to pass to a generation tool |
| `themes[].name`          | `string`        | Display name                          |
| `themes[].type`          | `enum`          | `standard` or `custom`                |
| `themes[].colorKeywords` | `array[string]` | Color keywords describing the palette |
| `themes[].toneKeywords`  | `array[string]` | Tone keywords describing the style    |
| `count`                  | `int`           | Total themes returned                 |

## get\_folders

Browse or search your Gamma folders. Use the returned `id` in a generation tool's `folderId` parameter.

### Input parameters

| Parameter | Type     | Description                      |
| --------- | -------- | -------------------------------- |
| `name`    | `string` | Optional. Search folders by name |

### Output

| Field            | Type            | Description                            |
| ---------------- | --------------- | -------------------------------------- |
| `folders`        | `array[object]` | Array of folder objects                |
| `folders[].id`   | `string`        | Folder ID to pass to a generation tool |
| `folders[].name` | `string`        | Display name                           |
| `count`          | `int`           | Total folders returned                 |

## get\_gamma\_comments

List comment threads (and their replies) on an existing Gamma. Use this to read, review, or summarize feedback on a Gamma. Read-only. Results are paginated, oldest activity first.

### Input parameters

| Parameter         | Type      | Required | Description                                                                               |
| ----------------- | --------- | -------- | ----------------------------------------------------------------------------------------- |
| `gammaIdOrUrl`    | `string`  | Yes      | Gamma file ID or full Gamma URL                                                           |
| `limit`           | `int`     | No       | Max threads per page; default `50`, max `50`                                              |
| `after`           | `string`  | No       | Cursor from a previous response for pagination                                            |
| `updatedSince`    | `string`  | No       | ISO-8601 timestamp; return only threads with activity after this time                     |
| `includeArchived` | `boolean` | No       | Include archived (deleted) comments and replies, each flagged `archived`. Default `false` |

### Output

| Field                    | Type             | Description                                                                                    |
| ------------------------ | ---------------- | ---------------------------------------------------------------------------------------------- |
| `comments`               | `array[object]`  | Comment threads, oldest activity first                                                         |
| `comments[].id`          | `string`         | Thread ID                                                                                      |
| `comments[].cardId`      | `string \| null` | Card the comment is on; `null` for page-level comments                                         |
| `comments[].author`      | `object`         | `{ id, name }` (name may be `null`)                                                            |
| `comments[].contentText` | `string`         | Plain-text comment body                                                                        |
| `comments[].status`      | `enum`           | `open` or `closed`                                                                             |
| `comments[].replies`     | `array[object]`  | Replies, each with `id`, `author`, `contentText`, `createdTime`, `updatedTime`, and `archived` |
| `comments[].createdTime` | `string`         | ISO-8601 creation time                                                                         |
| `comments[].updatedTime` | `string`         | ISO-8601 last-activity time                                                                    |
| `hasMore`                | `boolean`        | Whether more threads are available                                                             |
| `nextCursor`             | `string`         | Cursor for the next page when more results exist                                               |

## get\_gamma\_analytics

Get an engagement summary for an existing Gamma: total views, unique viewers and editors, card count, when it was last opened, and a 30-day daily viewer trend. Use this as the default when a user asks how a gamma is performing. In clients that support MCP apps, this renders an interactive widget; it also returns structured data and a formatted text summary. Analytics data is eventually consistent and can lag by about an hour.

### Input

| Parameter      | Type     | Required | Description                     |
| -------------- | -------- | -------- | ------------------------------- |
| `gammaIdOrUrl` | `string` | Yes      | Gamma file ID or full Gamma URL |

### Output

| Field           | Type             | Description                                                                      |
| --------------- | ---------------- | -------------------------------------------------------------------------------- |
| `gammaId`       | `string`         | Canonical file ID                                                                |
| `totalViews`    | `int`            | Total view events, including repeat opens                                        |
| `uniqueViewers` | `int`            | Unique viewers (authenticated and anonymous)                                     |
| `uniqueEditors` | `int`            | Unique editors                                                                   |
| `cardCount`     | `int`            | Number of cards                                                                  |
| `lastOpened`    | `string \| null` | ISO-8601 of the most recent view; `null` if never opened                         |
| `dailyViews`    | `object`         | 30-day rolling window: `{ dayCount, timezone, days: [{ date, uniqueViewers }] }` |

## get\_gamma\_card\_analytics

Get card-by-card engagement for an existing Gamma: total time viewers spent on each card and the percentage of viewers who reached it. Every card is included in deck order. Use this when a user asks which cards performed best or where viewers dropped off. Analytics data can lag by about an hour.

### Input

| Parameter      | Type     | Required | Description                     |
| -------------- | -------- | -------- | ------------------------------- |
| `gammaIdOrUrl` | `string` | Yes      | Gamma file ID or full Gamma URL |

### Output

| Field           | Type            | Description                                                                                                                                                        |
| --------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `gammaId`       | `string`        | Canonical file ID                                                                                                                                                  |
| `uniqueViewers` | `int`           | Unique viewers                                                                                                                                                     |
| `uniqueEditors` | `int`           | Unique editors                                                                                                                                                     |
| `cardCount`     | `int`           | Number of cards                                                                                                                                                    |
| `cards`         | `array[object]` | Ordered by position, each: `cardId`, `cardName` (`null` if untitled), `cardPosition` (1-based), `viewTimeSeconds` (total across viewers), `viewersPercent` (0–100) |

## get\_gamma\_viewer\_analytics

List the people who viewed an existing Gamma: display name and email for signed-in viewers (`null` for anonymous), when they last opened it, and how many cards they viewed. Use this to find who has seen a gamma, or to locate a specific viewer. Requires at least edit permission on the gamma (manage permission shows all viewers; edit-only shows just the API user's own activity — a `403` otherwise). Results are paginated.

### Input parameters

| Parameter       | Type     | Required | Description                                              |
| --------------- | -------- | -------- | -------------------------------------------------------- |
| `gammaIdOrUrl`  | `string` | Yes      | Gamma file ID or full Gamma URL                          |
| `limit`         | `int`    | No       | Max viewers; default `25`, max `50`                      |
| `after`         | `string` | No       | Cursor from a previous response for pagination           |
| `sortDirection` | `enum`   | No       | Sort by most recent open time: `desc` (default) or `asc` |

### Output

| Field        | Type            | Description                                                                                                                            |
| ------------ | --------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `gammaId`    | `string`        | Canonical file ID                                                                                                                      |
| `viewers`    | `array[object]` | Each: `viewerId`, `displayName` (`null` if anonymous), `email` (`null` if anonymous), `lastOpened` (ISO-8601 or `null`), `cardsViewed` |
| `hasMore`    | `boolean`       | Whether more viewers are available                                                                                                     |
| `nextCursor` | `string`        | Cursor for the next page when more results exist                                                                                       |

To find a specific person, scan each page for their name or email, paginating with `after` until found or pages run out. Pass the matching `viewerId` as `userId` to `get_gamma_viewer_detail_analytics`.

## get\_gamma\_viewer\_detail\_analytics

Get one viewer's detailed engagement with an existing Gamma: their name and email, when they last opened it, how many cards they viewed, and the share of their total view time spent on each card. Use this when a user asks how a specific person engaged with a gamma.

### Input

| Parameter      | Type     | Required | Description                                                                                                                    |
| -------------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `gammaIdOrUrl` | `string` | Yes      | Gamma file ID or full Gamma URL                                                                                                |
| `userId`       | `string` | Yes      | The viewer's user ID — the `viewerId` from `get_gamma_viewer_analytics`. Anonymous viewers are not addressable (returns `404`) |

### Output

| Field              | Type             | Description                                                                                                                                           |
| ------------------ | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gammaId`          | `string`         | Canonical file ID                                                                                                                                     |
| `scope`            | `enum`           | `all` (manage permission) or `self` (edit permission — own activity only)                                                                             |
| `userId`           | `string`         | The viewer's user ID                                                                                                                                  |
| `displayName`      | `string \| null` | Viewer display name                                                                                                                                   |
| `email`            | `string \| null` | Viewer email                                                                                                                                          |
| `lastOpened`       | `string \| null` | ISO-8601 of the most recent view                                                                                                                      |
| `cardsViewed`      | `int`            | Cards this viewer viewed                                                                                                                              |
| `cardCount`        | `int`            | Total cards (denominator for `cardsViewed`)                                                                                                           |
| `perCardTimeSpent` | `array[object]`  | Ordered by position, each: `cardId`, `cardName` (`null` if untitled), `cardPosition` (1-based), `viewTimePercent` (0–100; `0` for cards never viewed) |

## Error handling

All tools return errors in a consistent format:

{% code title="Error response" %}

```json
{
  "error": "Error message describing what went wrong",
  "isError": true
}
```

{% endcode %}

| Error                  | Description                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `401 Unauthorized`     | Missing, expired, or revoked OAuth Bearer token. Re-authorize to continue                       |
| `403 Forbidden`        | The connected user does not have permission to access the requested Gamma or workspace resource |
| `404 Not found`        | The requested Gamma, generation, or resource could not be found                                 |
| `400 Bad request`      | One or more parameters are invalid for the requested tool                                       |
| `Rate limit exceeded`  | Too many requests in a given time period                                                        |
| `Network connectivity` | Unable to establish connection to the server                                                    |
| `Insufficient credits` | The account does not have enough credits to complete the generation                             |

### Plan limit failures

When `generate`, `generate_from_template`, `generate_multi_page_gamma`, `generate_image`, `get_image_generation_status`, `edit_gamma`, or `export_gamma` fails because the request exceeded a limit of the workspace's Gamma plan, the failed result carries the workspace's live limits alongside the error. Plan limit failures include insufficient credits, `numCards` above the plan maximum, more `inputTextBreaks` than the plan allows, and image models or reference images that the plan does not include.

{% code title="Plan limit failure" %}

```json
{
  "status": "failed",
  "error": "numCards must not be greater than 10",
  "planLimitExceeded": true,
  "currentPlanLimits": {
    "workspace": "Acme",
    "planTier": "free",
    "creditsRemaining": 400,
    "maxGenerateCards": 10,
    "availableImageModels": ["flux-1-quick", "flux-2-klein"]
  },
  "upgradeUrl": "https://gamma.app/settings/billing?source=mcp",
  "guidance": "..."
}
```

{% endcode %}

| Field               | Type      | Description                                                                                                                                                                                                                                                                                                                                    |
| ------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `planLimitExceeded` | `boolean` | `true` when the failure is a plan or credit limit                                                                                                                                                                                                                                                                                              |
| `currentPlanLimits` | `object`  | The workspace's limits fetched at the moment of failure: `workspace`, `planTier`, `creditsRemaining`, `maxGenerateCards`, and `availableImageModels`; `creditsRemaining` can be absent. `planTier` is `free` or the workspace's highest paid plan (`plus`, `pro`, `ultra`, `team`, `business`, or `enterprise`). Omitted when the lookup fails |
| `upgradeUrl`        | `string`  | Link to the workspace billing settings, where the user can compare plans, upgrade, or buy credits                                                                                                                                                                                                                                              |
| `guidance`          | `string`  | Instructions for the model: report the limit that was hit, offer to retry at `maxGenerateCards` for card-count failures, and retry after the user upgrades because the API validates against the live plan                                                                                                                                     |

A `get_image_generation_status` poll whose generation failed on a plan limit carries the same fields on its `failed` result.

### Unknown theme IDs

When a tool fails because the `themeId` does not exist in the workspace, the failed result carries `themeNotFound: true`, `guidance`, and `validThemes`: up to 100 workspace themes as `{ "id", "name" }` pairs. `validThemes` is omitted when the theme lookup fails. Pick the closest match from `validThemes`, use `get_themes` to search for a theme, or omit `themeId`. Without a `themeId`, `generate_from_template` keeps the template's theme and the other tools use the workspace default theme. Only pass theme IDs returned by the API.

`generate_from_template` does not support `themeId` when it runs as an agent generation: the template keeps its own theme, and the error says to retry without `themeId` (use `generate` with `themeId` to apply a saved theme on Gamma's standard design). Some generations do not support `format: "webpage"` in `generate`. These failures carry no `themeNotFound` or `validThemes`; the error says to retry without `themeId`, or with a different `format`.

## Related

* [Set up the MCP server](/mcp/gamma-mcp-server.md) for getting started and troubleshooting
* [Connect integrations](/connectors/connectors-and-integrations.md) for platform-specific setup
* [Generate from text](/guides/generate-api-parameters-explained.md) for the equivalent REST API parameters
* [Access and pricing](/get-started/access-and-pricing.md) for credit costs and plan details


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/mcp/mcp-tools-reference.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
