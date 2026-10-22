> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/get-started/authenticate-with-oauth.md).

# Authenticate with OAuth

Let Gamma users connect their own accounts to your app with the OAuth 2.0 authorization code flow.

The Gamma API accepts OAuth 2.0 Bearer tokens as an alternative to API keys. Use OAuth when your app acts on behalf of **your users** — each user connects their own Gamma account, and your requests run as that user in the workspace they choose. If you only need to act as yourself, an [API key](/get-started/understanding-the-api-options.md#authentication) is simpler.

Gamma implements the standard OAuth 2.0 authorization code flow with PKCE, plus:

* **Dynamic Client Registration** ([RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)) — register your app with a single API call, no approval process
* **Authorization Server Metadata** ([RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)) and **Protected Resource Metadata** ([RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)) — full auto-discovery, so MCP clients and OAuth libraries can configure themselves
* **Resource Indicators** ([RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707)) — tokens are audience-bound to the API they are for
* **Refresh token rotation**

{% hint style="info" %}
**Building an MCP server or assistant integration?** MCP clients handle this entire flow automatically via the discovery endpoints — see [MCP tools reference](/mcp/mcp-tools-reference.md). This page is for developers implementing the flow directly.
{% endhint %}

## Quick reference

* OAuth is an alternative to [API keys](/get-started/understanding-the-api-options.md#authentication): same endpoints, `Authorization: Bearer <token>` instead of `X-API-KEY`.
* The authorization server is `auth.gamma.app`; register your client once with dynamic client registration.
* Always send `resource=https://public-api.gamma.app` in the authorization request.
* Scopes: `generate` (full access, default) or `gamma:read` (metadata only, no credit spend).
* Access tokens last about an hour; refresh tokens rotate on each use and last up to 90 days.
* Tokens are bound to one user and one workspace; requests spend that user's credits.

## Endpoints

| Endpoint                      | URL                                                                 |
| ----------------------------- | ------------------------------------------------------------------- |
| Protected resource metadata   | `https://public-api.gamma.app/.well-known/oauth-protected-resource` |
| Authorization server metadata | `https://auth.gamma.app/.well-known/oauth-authorization-server`     |
| Client registration           | `POST https://auth.gamma.app/oauth/register`                        |
| Authorization                 | `GET https://auth.gamma.app/oauth/authorize`                        |
| Token                         | `POST https://auth.gamma.app/oauth/token`                           |
| JWKS                          | `https://auth.gamma.app/.well-known/jwks.json`                      |
| API base                      | `https://public-api.gamma.app/v1.0/...`                             |

{% hint style="warning" %}
Gamma implements OAuth 2.0, not OpenID Connect. There is no `/.well-known/openid-configuration`, no ID tokens, and no userinfo endpoint. Use the access token to call the Gamma API; do not use it as a sign-in mechanism.
{% endhint %}

## Scopes

| Scope        | Grants                                                                                                                                                                           |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `generate`   | Full API access: generations, edits, exports, themes, folders, reads. Default if no scope is requested.                                                                          |
| `gamma:read` | Read-only access to gamma metadata (title, thumbnail, author, timestamps). Intended for link-preview integrations. Does not spend credits and cannot reach generation endpoints. |

Request the minimum scope your app needs. A `gamma:read` token receives `403 insufficient_scope` on any non-read endpoint.

## Set up the flow

### Step 1: Register your client

One-time setup. No approval needed; you receive credentials immediately:

```bash
curl -X POST https://auth.gamma.app/oauth/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "My App",
    "redirect_uris": ["https://myapp.example.com/oauth/callback"],
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "none"
  }'
```

Choosing `token_endpoint_auth_method`:

* **`none`** — public client (SPA, CLI, desktop, mobile). No client secret; PKCE protects the flow.
* **`client_secret_basic`** (default) or **`client_secret_post`** — confidential client (server-side web app). You receive a `client_secret`; store it securely and never ship it to a browser.

Save the returned `client_id` (and `client_secret`, if any). Registration creates your OAuth client once per app — reuse the same `client_id` for all your users; do not re-register per user or per run.

### Step 2: Send the user to authorize

Generate a PKCE verifier/challenge and a `state` value, then redirect the user to:

```
https://auth.gamma.app/oauth/authorize
  ?client_id=YOUR_CLIENT_ID
  &redirect_uri=https://myapp.example.com/oauth/callback
  &response_type=code
  &resource=https://public-api.gamma.app
  &scope=generate
  &state=RANDOM_STATE
  &code_challenge=BASE64URL_S256_CHALLENGE
  &code_challenge_method=S256
```

{% hint style="warning" %}
**Always include `resource=https://public-api.gamma.app`.** This RFC 8707 resource indicator becomes the token's audience. Tokens minted without it are not valid for the Gamma API. Omitting it is the most common integration mistake.
{% endhint %}

The user signs in to Gamma, **selects a workspace**, and consents. Gamma then redirects back to your app:

```
https://myapp.example.com/oauth/callback?code=AUTH_CODE&state=RANDOM_STATE
```

Verify `state` matches before continuing.

### Step 3: Exchange the code for tokens

```bash
curl -X POST https://auth.gamma.app/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=https://myapp.example.com/oauth/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "code_verifier=YOUR_PKCE_VERIFIER"
```

Confidential clients also authenticate here — `client_secret` in the body for `client_secret_post`, or HTTP Basic auth for `client_secret_basic`.

{% code title="Response" %}

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "generate",
  "refresh_token": "gamma_refresh_..."
}
```

{% endcode %}

Authorization codes are single-use and short-lived — exchange them immediately.

### Step 4: Call the API

```bash
curl -X POST https://public-api.gamma.app/v1.0/generations \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "inputText": "The history of the telescope", "format": "presentation" }'
```

All API endpoints work identically with OAuth tokens and API keys — same routes, same request and response shapes. Generations and other credit-spending operations consume the **authorizing user's credits** in the workspace they selected.

### Step 5: Refresh the token

Access tokens expire after about an hour. Refresh without user interaction:

```bash
curl -X POST https://auth.gamma.app/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=CURRENT_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID"
```

{% hint style="warning" %}
**Refresh tokens rotate.** Every refresh returns a new refresh token and invalidates the old one. Persist the newly returned token atomically; if you lose it, the user must re-authorize.
{% endhint %}

Refresh tokens live up to 90 days. A user whose token has not been refreshed in 90 days must go through the authorization flow again.

## Handle errors

The API returns [RFC 6750](https://datatracker.ietf.org/doc/html/rfc6750)-compliant Bearer errors with a `WWW-Authenticate` header:

| Status                     | Error                             | Meaning                                                       | What to do                                                                |
| -------------------------- | --------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `401`                      | `invalid_token`                   | Token missing, expired, malformed, or wrong audience          | Refresh the access token; if refresh fails, re-run the authorization flow |
| `403`                      | `insufficient_scope`              | Token's scope doesn't cover this endpoint                     | Request the right scope at authorization time                             |
| `400` (at authorize/token) | `invalid_grant`, `invalid_target` | Bad or expired code, PKCE mismatch, or unsupported `resource` | Check the `resource` value and PKCE implementation                        |

Recommended client logic: on `401`, attempt one token refresh and retry; if that fails, prompt the user to reconnect.

## Best practices

{% hint style="success" %}
The two highest-impact rules: always send `resource=https://public-api.gamma.app` at authorization, and always persist the rotated refresh token before discarding the old one.
{% endhint %}

* **Always use PKCE (S256)**, even for confidential clients. Gamma supports combining PKCE with a client secret.
* **Request the minimum scope.** Link previews and metadata readers should use `gamma:read`, not `generate`.
* **Validate `state`** on the callback to prevent CSRF.
* **Store tokens securely, server-side where possible.** Access tokens are bearer credentials — anyone holding one can act as the user. Never log them or embed them in client-side code.
* **Serialize refreshes** if multiple workers share a token, so a rotation isn't lost.
* **Tokens are user and workspace scoped.** A token acts as one user in the one workspace they picked at consent. To work in a different workspace, run the authorization flow again. Design your "Connect Gamma" UX to show which workspace is connected.
* **Cache the access token** until near `expires_in` — don't refresh on every request.

## FAQ

**Can I use OAuth for "Sign in with Gamma"?**\
No — Gamma's OAuth is for API authorization only. There are no ID tokens or userinfo endpoint.

**Do OAuth requests cost credits?**\
Same credits as API-key requests; read calls cost nothing.

**Can one token access multiple workspaces?**\
No. One authorization = one user + one workspace. Repeat the flow per workspace.

## Related

* [Explore the API](/get-started/understanding-the-api-options.md) for the API key alternative and endpoint overview
* [Review access and pricing](/get-started/access-and-pricing.md) for credit costs and plan details
* [MCP tools reference](/mcp/mcp-tools-reference.md) for OAuth in the MCP context


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/get-started/authenticate-with-oauth.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
