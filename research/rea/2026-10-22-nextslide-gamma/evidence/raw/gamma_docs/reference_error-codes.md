> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/reference/error-codes.md).

# Error codes

Detailed descriptions of API error codes.

### Quick reference

* `400` means the request shape or values are invalid.
* `401` usually means the API key is missing or invalid.
* `402` with `"Insufficient credits remaining"` means the workspace is out of credits.
* `403` on `/archive` usually means the `gammaId` is a web app URL slug instead of the API file ID.
* `403` on `DELETE /gammas/{gammaId}` means the API key owner is not a workspace admin.
* `403` on `GET /gammas/{gammaId}/analytics`, `/analytics/cards`, or `/analytics/viewers` means the API key owner lacks at least edit permission on the Gamma.
* `404` on generation polling usually means the `generationId` is wrong or unavailable.
* `409` on `POST /agent/gammas/{gammaId}/edits` means an edit is already in progress on that page (`code: edit_in_progress`).
* `429` means you should slow down and retry later. Agent endpoints may return `code: workspace_concurrency_limit_exceeded` when the workspace has too many in-flight agent jobs.
* `503` on agent endpoints or `GET /gammas/search` means the service is busy or document search is temporarily unavailable; retry the request.

### Example error response

```json
{
  "message": "Invalid API key.",
  "statusCode": 401
}
```

### Error Code Reference

| Status Code | Message                                                             | Description                                                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400         | Input validation errors                                             | Invalid parameters detected. Check the error details for specific parameter requirements.                                                                                                       |
| 401         | Invalid API key                                                     | The provided API key is invalid or not associated with an eligible account.                                                                                                                     |
| 402         | Insufficient credits remaining                                      | Your workspace does not have enough credits. Purchase more at [gamma.app/settings/billing](https://gamma.app/settings/billing) or enable auto-recharge.                                         |
| 403         | Forbidden                                                           | Access denied. You do not have permission for this resource, or the requested feature is not available on your plan.                                                                            |
| 403         | Access denied. You must have edit permission to archive this gamma. | The `gammaId` is wrong (web app URL slug instead of API file ID), the Gamma is not in the API key's workspace, or the key owner lacks edit permission.                                          |
| 403         | Access denied - workspace admin role required                       | `DELETE /gammas/{gammaId}` requires a workspace admin role on the API key's workspace.                                                                                                          |
| 404         | Generation ID not found. generationId: xxxxxx                       | The specified generation ID could not be located. Check and correct your generation ID.                                                                                                         |
| 409         | Edit already in progress                                            | `POST /agent/gammas/{gammaId}/edits` — another edit is running on this page. Response includes `code: edit_in_progress` and may include the running `editId` when it belongs to your workspace. |
| 429         | Too many requests                                                   | Too many requests have been made. Retry after the rate limit period. Agent create/edit endpoints may instead return `code: workspace_concurrency_limit_exceeded` with a `Retry-After` header.   |
| 503         | Service unavailable                                                 | Agent endpoints may return this when the service is busy. `GET /gammas/search` may return this when document search is temporarily unavailable. Retry the request.                              |
| 500         | An error occurred while generating the gamma.                       | An unexpected error occurred while generating the gamma. Contact support with the `x-request-id` header for troubleshooting assistance.                                                         |
| 502         | Bad gateway                                                         | The request could not be processed due to a temporary gateway issue. Try again.                                                                                                                 |

### Troubleshooting Tips

<details>

<summary>400 - Input validation errors</summary>

* Check that all required fields are present (`inputText` or `pages` for `POST /generations`; `prompt` and `gammaId` for `POST /generations/from-template`; `prompt` for `POST /agent/generations`; `exportAs` for `POST /gammas/{gammaId}/export`)
* On `POST /agent/generations`, use a `themeId` from `GET /v1.0/themes`, do not combine `themeId` with `templateId`, and confirm the theme exists in your workspace
* Verify enum values match exactly (e.g., `presentation` not `Presentation`)
* Ensure `inputText` is between 1 and 400,000 characters
* Check that `numCards` is within your plan’s limits

</details>

### Related

* [Warnings](/reference/warnings.md) for non-fatal response warnings
* [Poll for results](/guides/async-patterns-and-polling.md) if your error happens during generation status checks
* [Get Help](/reference/get-help.md) if you need support escalation

<details>

<summary>401 - Invalid API key</summary>

* Verify your API key starts with `sk-gamma-`
* Check that the key hasn’t been revoked
* Ensure the header is `X-API-KEY` (case-sensitive)

</details>

<details>

<summary>503 - Document search unavailable</summary>

* `GET /gammas/search` may return `503` when document search is temporarily unavailable.
* Retry after a short delay with exponential backoff.

</details>

<details>

<summary>403 - Archive access denied</summary>

* Verify you are using the `gammaId` from the generation poll response, not the slug from the web app URL.
* The API file ID typically starts with `g_`. The URL slug (e.g. `bc7s74ruzod20f4`) will not work.
* Confirm the Gamma belongs to the same workspace as the API key.
* Check that the API key owner has edit permission on the Gamma.

</details>

<details>

<summary>402 - Insufficient credits</summary>

* Check `credits.remaining` on `completed` and `failed` poll responses to monitor your balance
* Enable [auto-recharge](https://gamma.app/settings/billing) to avoid interruptions
* In automated workflows, check the remaining balance after each completed generation before starting another

</details>

<details>

<summary>429 - Rate limit exceeded</summary>

* Wait before retrying (check `Retry-After` header if present)
* Implement exponential backoff in your integration
* Consider upgrading your plan for higher limits
* On agent create or edit endpoints, a `workspace_concurrency_limit_exceeded` code means too many agent jobs are in flight for the workspace — wait for jobs to finish or poll existing ids before starting more

</details>

<details>

<summary>409 - Edit already in progress</summary>

* Only one agent edit runs on a page at a time
* Poll the running job with `GET /agent/edits/{editId}` instead of starting a duplicate edit
* When the response includes an `editId` for the in-progress job, use that id if it belongs to your workspace

</details>


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/reference/error-codes.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
