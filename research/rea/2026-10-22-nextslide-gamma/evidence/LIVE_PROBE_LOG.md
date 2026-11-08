# LIVE_PROBE_LOG — nextslide.ai / Gamma / nextslide.io

Reproducibility record. Every command run, every URL fetched, HTTP status, raw-response snippets, and every failure with its reason.

- Operator: subagent (authorized by product owner for competitive analysis + engineering research)
- Working dir: `/Users/abdulazizalsh/work/Gomrey/research/rea/2026-10-22-nextslide-gamma/evidence/`
- Raw artifacts: `./raw/` (HTML, JS, screenshots, doc markdown), `./raw/gamma_docs/`, `./raw/gamma_hc/`, `./raw/gamma_gh/`
- Session window (UTC): 2026-10-22T03:39:02Z → 2026-10-22T03:45:08Z

## 0. Tooling determination

| # | Command | Result | Tag |
|---|---------|--------|-----|
| T1 | `date -u "+%Y-%m-%dT%H:%M:%SZ"` | `2026-10-22T03:39:02Z` | API_RESPONSE |
| T2 | `command -v curl` | `/usr/bin/curl` (curl 8.7.1, x86_64-apple-darwin25.0, SecureTransport/LibreSSL 3.3.6, nghttp2/1.68.1) | API_RESPONSE |
| T3 | `command -v playwright playwright-cli chromium google-chrome` | **no output** — none on PATH | API_RESPONSE |
| T4 | `ls -d /Users/abdulazizalsh/work/Gomrey/servers/nextjs/.playwright-cli` | **exists** — but contains only prior run logs/yml/png, no browser binary | API_RESPONSE |
| T5 | `npx playwright --version` | `1.64.1` (npm-installed on demand) | API_RESPONSE |
| T6 | `ls ~/Library/Caches/ms-playwright` | `chromium_headless_shell-1194`, `chromium_headless_shell-1243`, `chromium-1194`, `ffmpeg-1011` | API_RESPONSE |
| T7 | `ls /Applications/` | only `Safari.app` — **no Google Chrome installed** | API_RESPONSE |
| T8 | `npm install --prefix . playwright@1.64.1` | `added 2 packages in 691ms` (zero-cost, no paid service) | API_RESPONSE |
| T9 | `node scripts/render.mjs https://nextslide.ai/` | **FAILED**: `Executable doesn't exist at .../ms-playwright/chromium_headless_shell-1248/...` — playwright 1.64.1 expects chromium rev 1248, cache had 1243 | BLOCKED (resolved at T10) | BLOCKED |
| T10 | `npx playwright install chromium-headless-shell` | `FFmpeg (playwright ffmpeg v1013) downloaded` + chromium-headless-shell 1248 installed (free download, no account) | API_RESPONSE |
| T11 | `node scripts/render.mjs …` (after T10) | all renders succeeded | OBSERVED_UI |

**Tooling used:** (1) `curl -sL -A "<realistic UA>"` for all HTML/API — **used**; (2) Playwright 1.64.1 headless Chromium (installed free from Microsoft CDN into the standard `~/Library/Caches/ms-playwright` cache) for JS-rendered pages — **used**; (3) `cua` MCP server — **not used** (not required; curl + local headless Chromium fully covered the surface, and `cua` would only have been needed for GUI interaction with a logged-in app, which is out of scope).

**No logins, paywalls, CAPTCHAs, rate limits, or access controls were defeated. No accounts created. No purchases. No paid tiers used.**

## 1. nextslide.ai

| # | UTC | Command / URL | Status | Notes |
|---|-----|---------------|--------|-------|
| N1 | 03:39:15 | `curl -sL -A "$UA" https://nextslide.ai/` | **HTTP/2 200** | `final_url=https://nextslide.ai/`, `num_redirects=0`, `size=3706` bytes. No redirect. Headers: `server: cloudflare`, `last-modified: Thu, 06 Aug 2026 20:14:11 UTC`, `cache-control: public, max-age=0, s-maxage=300` | API_RESPONSE |
| N2 | 03:39:15 | `curl -s -D - https://nextslide.ai/` (no `-L`) | **200** | Confirms no 301/302; single 200 response, no redirect chain | API_RESPONSE |
| N3 | 03:39:20 | `curl -sL https://nextslide.ai/assets/index-DCccxv-1.js` | **200**, 171,045 bytes | React SPA bundle referenced from N1's HTML | API_RESPONSE |
| N4 | 03:39:25 | `node` string-extraction over N3 bundle | — | **Partial failure**: naive string-literal extraction returned only React/runtime noise, no product prose (content is JSX-compiled). Superseded by N8. | API_RESPONSE |
| N5 | 03:41:xx | `curl` for `https://nextslide.ai/{docs,pricing,app,blog,features,api,sitemap.xml,robots.txt}` | **403** for docs/pricing/app/blog/features/api/sitemap.xml; **404** for robots.txt | 403 is a Cloudflare bot challenge, not an app response (see N7) | API_RESPONSE |
| N6 | 03:45:03 | `curl -sL https://www.nextslide.io/` | **200** (1 redirect: `nextslide.io` → `www.nextslide.io`), 85,599 bytes | see §3 | API_RESPONSE |
| N7 | 03:45:00 | `node scripts/render2.mjs '[["https://nextslide.ai/pricing",…],["https://nextslide.ai/docs",…]]'` | `/pricing` → **200**; `/docs` → **403** | **Key result**: `/pricing` renders *the identical sunset page* as `/` → the SPA has a catch-all route; `/docs` returned a literal Cloudflare "Performing security verification" interstitial (Ray ID `a4e5814dd930c611`) — i.e. an intermittent bot check, NOT evidence that `/docs` exists | OBSERVED_UI |
| N8 | 03:40:xx | `node scripts/render.mjs https://nextslide.ai/` (headless Chromium) | **STATUS 200**, `FINAL_URL https://nextslide.ai/` | Rendered `document.body.innerText` captured in full — see NEXTSLIDE_AI.md. Screenshot: `raw/nextslide_ai_rendered.png` | OBSERVED_UI |

N8 raw innerText (verbatim, full):

```
NE
TSLIDE
NextSlide is joining OpenAI

A note from Ahmed Beshry, founder of NextSlide.

Presentations help ideas move through the world. They teach, persuade, share research, and move important work forward. But creating a great presentation has traditionally required hours of work, design experience, or both.

We started NextSlide a little over a year ago with a simple belief: bringing an idea to life shouldn’t depend on your ability to design slides. We built a product that could turn prompts, notes, documents, or research into a polished, editable presentation—making it easier for anyone to share what they know.

Our goal was never simply to generate slides faster. We wanted to make visual communication more accessible and help more people express their ideas clearly.

The NextSlide team is now at OpenAI, helping build ChatGPT. We're excited to continue pursuing that same mission: building AI products that help people create, communicate, and turn their ideas into meaningful work.

To everyone who created a deck, shared feedback, or supported us along the way: thank you for helping shape NextSlide. We're grateful for the journey and excited for what comes next.

Ahmed Beshry
Founder, NextSlide
```

N1 raw HTML head (verbatim excerpt, from `raw/nextslide_ai.html`):

```html
<title>NextSlide is joining OpenAI</title>
<meta name="description" content="NextSlide has been acquired by OpenAI. A note from founder Ahmed Beshry." />
<meta name="author" content="NextSlide" />
<meta property="og:title" content="NextSlide is joining OpenAI" />
<meta property="og:description" content="NextSlide has been acquired by OpenAI. A note from founder Ahmed Beshry." />
<meta property="og:image" content="https://nextslide.ai/og-image-logos-v3.png" />
```

## 2. Source-code availability searches

| # | UTC | Command | Result | Notes |
|---|-----|---------|--------|-------|
| S1 | 03:41:30 | `curl https://registry.npmjs.org/-/v1/search?text=gamma%20presentation&size=20` | 200 | 20 results, **all** `@stdlib/*` gamma-distribution packages + `gamma` (the math function). **No Gamma-the-product package.** | API_RESPONSE |
| S2 | 03:41:30 | `curl https://registry.npmjs.org/-/v1/search?text=scope:gamma&size=20` | 200 | **0 results** — no `@gamma/*` scope published | API_RESPONSE |
| S3 | 03:41:32 | `curl` each of `gamma-app`, `gammaapp`, `@gamma-app/api`, `@gamma-app/sdk` on registry.npmjs.org | **404 / 404 / 404 / 404** | None published | API_RESPONSE |
| S4 | 03:41:40 | `curl https://api.github.com/search/repositories?q=gamma-app` | 200, total_count=780 | Top hits all unrelated (`LUTCalc`, `gamma-ai-watermark-remover`, `OpenGammaProject/Gamma-MCA` — gamma spectroscopy, `KrasnovM/Gamma-Manager` — display gamma ramp) | API_RESPONSE |
| S5 | 03:41:42 | `curl https://api.github.com/search/repositories?q=gammaapp` | 200, total_count=11 | 11 repos, none related. `api-evangelist/gammaapp` = *"Gamma.app — independent third-party profile of a public API surface, by API Evangelist"* (third-party, 0 stars) | API_RESPONSE |
| S6 | 03:41:44 | `curl https://api.github.com/search/repositories?q=gamma+presentation+ai` | 200, total_count=65 | All are **Gamma competitors / clones**, not Gamma: `presenton/presenton` (11,259★, "Open-Source AI Presentation Generator and API (Gamma, Canva, Beautiful AI, Deckt…"), `allweonedev/presentation-ai` (3,055★, "Gamma Alternative"), `atharva9167j/preso`, `misbahsy/zentable`, `ishandutta2007/open-gamma` | API_RESPONSE |
| S7 | 03:41:45 | `curl https://api.github.com/search/repositories?q=nextslide+ai+presentation` | 200, **total_count=0** | No match | API_RESPONSE |
| S8 | 03:41:46 | `curl https://api.github.com/search/repositories?q=nextslide+openai+presentation` | 200, **total_count=0** | No match | API_RESPONSE |
| S9 | 03:41:47 | `curl https://api.github.com/orgs/{gamma-app,gammaapp,gamma-app-inc,gammaappinc}` | `gamma-app` → **200**; `gammaapp` → 200; `gamma-app-inc` → 404; `gammaappinc` → 404 | `gamma-app` is a **real GitHub org** | API_RESPONSE |
| S10 | 03:41:48 | `curl https://api.github.com/users/gamma-app/repos?per_page=100` | 200, **count=29** | Full list captured in GAMMA.md §6 | API_RESPONSE |
| S11 | 03:41:55 | `curl https://api.github.com/repos/gamma-app/{pptx-renderer,n8n-nodes-gamma,schematics,import-grader-annotator,desktop-app-releases,ai-coding-interview}` | 200 each | Per-repo metadata captured — see GAMMA.md §6 | API_RESPONSE |
| S12 | 03:41:56 | `curl .../contents/` for pptx-renderer, schematics, import-grader-annotator | 200 each | Directory listings captured | API_RESPONSE |
| S13 | 03:42:10 | `curl https://api.github.com/repos/NextSlide-AI/Nextslide.AI` | 200 | `created: 2025-02-10T11:19:38Z`, `pushed: 2025-02-10T11:19:39Z`, `stars: 0`, `size: 0` | API_RESPONSE |
| S14 | 03:42:10 | `curl .../NextSlide.AI/contents/` | **404** `{"message":"This repository is empty."}` | **Not source code** | API_RESPONSE |
| S15 | 03:42:15 | `curl https://api.github.com/search/repositories?q=nextslide` | 200, total_count=31 | All unrelated: `onebone/nextslide-editor`, `mattkula/nextslide` (PowerPoint viewer), `timmywheels/nextslide`, **`0xRafie/nextslide`** (an OpenCode HTML-slide skill — explicitly excluded by the brief), `NextSlide-AI/Nextslide.AI` (empty), `ammarjmahmood/nextslide` (voice slide control), `yasiru2003/nextslide` (voice-activated slide controller) | API_RESPONSE |

## 3. nextslide.io (disambiguation)

| # | UTC | Command / URL | Status | Notes |
|---|-----|---------------|--------|-------|
| X1 | 03:39:50 | `curl -sL -A "$UA" https://nextslide.io/` | **200**, 1 redirect → `https://www.nextslide.io/`, 85,599 bytes |  | API_RESPONSE |
| X2 | 03:39:50 | `grep -o '<title>…'` on X1 | — | `<title>NextSlide - Turn your phone into a powerpoint clicker</title>` | API_RESPONSE |
| X3 | 03:39:50 | `grep -o '<meta name="description"…'` on X1 | — | `"Upload your PowerPoint, share a link, and anyone can control the slides from their own phone, anywhere - nothing to install."` | API_RESPONSE |
| X4 | 03:40:30 | `node scripts/render.mjs https://www.nextslide.io/` | **STATUS 200** | Full innerText captured; screenshot `raw/nextslide_io_rendered.png` | OBSERVED_UI |
| X5 | 03:45:03 | heading extraction on X1 | — | Headings: *"Share a presentation in 3 easy steps"*, *"Upload your presentation"*, *"Send the links"*, *"Present in sync"*, *"See your notes and slides, in sync, on any screen."*, *"Everything you can do with one link."*, *"Shared presentation control"*, *"Turn your tablet into a confidence monitor"*, *"Audience Views"*, *"Hybrid Events"*, *"…And more!"* | API_RESPONSE |
| X6 | 03:45:03 | body-text grep on X1 | — | Nav: *"Next Slide Features FAQ Use cases Teams and Zoom Presenter view on Zoom Confidence monitors OBS, vMix, and Wirecast Stream Deck and API control"*; steps: *"01 Upload your presentation"*, *"Presenter links to control the presentation. Content links to see your current slide, next slide, and notes."*, *"03 Present in sync"*; testimonial: *"My team got up to speed in a couple minutes. All three presenters were able to drive their own slides seamlessly."* | API_RESPONSE |

## 4. Gamma — docs and API

| # | UTC | Command / URL | Status | Notes |
|---|-----|---------------|--------|-------|
| G1 | 03:39:52 | `curl -sL https://developers.gamma.app/` | **200**, 889,855 bytes | GitBook site; HTML contains links to `llms.txt`, `llms-full.txt`, `readme.md` | OFFICIAL_DOCUMENTATION |
| G2 | 03:40:05 | `curl https://developers.gamma.app/llms.txt` | **200**, 10,515 bytes | Full docs index — 47 doc pages enumerated. Saved `raw/gamma_llms.txt` | OFFICIAL_DOCUMENTATION |
| G3 | 03:40:06 | `curl https://developers.gamma.app/llms-full.txt` | **200**, 491,973 bytes | Complete docs corpus incl. embedded OpenAPI 3.0.0 JSON specs. Saved `raw/gamma_llms-full.txt` | OFFICIAL_DOCUMENTATION |
| G4 | 03:40:07 | `curl https://developers.gamma.app/readme.md` | **200**, 17,262 bytes | README | OFFICIAL_DOCUMENTATION |
| G5 | 03:40:30 | `curl` 18 individual doc pages as `.md` | **200 ×18** | `raw/gamma_docs/` — mcp server, mcp tools ref, api-options, access-and-pricing, oauth, connect-your-own-agent, brand/template/editing-controls, branded-template-workflow, scope-and-limits, changelog, error-codes, image-models, output-languages, connectors, custom-mcp-connectors, charts, header-footer, async-polling | OFFICIAL_DOCUMENTATION |
| G6 | 03:41:00 | `grep -oE '(GET\ | POST\ | DELETE) /[a-zA-Z0-9_{}/.-]+' raw/gamma_llms-full.txt` | — | 62 path tokens extracted (both bare and `/v1.0`-prefixed forms) | API_RESPONSE |
| G7 | 03:41:05 | `curl https://public-api.gamma.app/v1.0/themes` | **401** | `{"message":"Invalid API key","statusCode":401}` | API_RESPONSE |
| G8 | 03:41:05 | `curl https://public-api.gamma.app/v1.0/folders` | **401** | `{"message":"Invalid API key","statusCode":401}` | API_RESPONSE |
| G9 | 03:41:06 | `curl https://public-api.gamma.app/v1.0/gammas/search` | **401** | `{"message":"Invalid API key","statusCode":401}` — base URL + auth scheme confirmed; no auth bypass attempted | API_RESPONSE |
| G10 | 03:41:08 | `curl https://mcp.gamma.app/.well-known/oauth-protected-resource` | **200** | `{"resource":"https://mcp.gamma.app","authorization_servers":["https://auth.gamma.app"],"scopes_supported":["generate","gamma:read"],"bearer_methods_supported":["header","body"]}` | API_RESPONSE |
| G11 | 03:41:09 | `curl https://mcp.gamma.app/.well-known/oauth-authorization-server` | **404** | `Cannot GET /.well-known/oauth-authorization-server` — expected: metadata lives on the *authorization server* host, not the resource host | API_RESPONSE |
| G12 | 03:41:10 | `curl https://auth.gamma.app/.well-known/oauth-authorization-server` | **200** | Full RFC 8414 metadata: `authorization_endpoint: https://auth.gamma.app/oauth/authorize`, `token_endpoint: https://auth.gamma.app/oauth/token`, `registration_endpoint: https://auth.gamma.app/oauth/register`, `jwks_uri: …/.well-known/jwks.json`, `grant_types_supported: [authorization_code, refresh_token]`, `code_challenge_methods_supported: [S256]`, `token_endpoint_auth_methods_supported: [none, client_secret_post, client_secret_basic]`, `scopes_supported: [generate, gamma:read]`, `claims_supported: [sub,aud,exp,iat,iss]` | API_RESPONSE |
| G13 | 03:41:20 | `curl https://api.github.com/repos/gamma-app/n8n-nodes-gamma/git/trees/HEAD?recursive=1` | 200 | 49 files; **official Gamma-published MIT integration code** — `nodes/Gamma/api.ts`, `apiEnums.ts`, `create.operation.ts`, `credentials/GammaApi.credentials.ts`, `docs/*.md`, `test/*.js` | API_RESPONSE |
| G14 | 03:41:22 | `curl` raw `nodes/Gamma/api.ts` | 200 | `export const BASE_URL = 'https://public-api.gamma.app';` and `USER_AGENT = 'n8n-nodes-gamma/0.6.1'` | API_RESPONSE |
| G15 | 03:41:24 | `curl` raw `nodes/Gamma/apiEnums.ts` | 200, 8,186 bytes | 38 AI image model IDs + credit costs; 74 language codes; `IMAGE_SOURCE_VALUES`; `EXPORT_AS_VALUES = ["pdf","png","pptx"]`; `CARD_DIMENSION_OPTIONS` per format | API_RESPONSE |
| G16 | 03:41:26 | `curl` raw `nodes/Gamma/actions/generation/create.operation.ts` | 200, 24,021 bytes | Real request-shape source: `inputText`, `textMode`, `format`, `additionalInstructions`, `imageModel`, `audience`, `cardDimensions{Presentation,Document,Social,Webpage}`, `cardSplit`, `emailAccess`, `emailRecipients`, `enableSearchEngineIndexing`, `exportAs`, `externalAccess`, `workspaceAccess` | API_RESPONSE |
| G17 | 03:41:30 | `curl` raw `gamma-app/import-grader-annotator/README.md` | 200 | **Genuinely Gamma-internal code.** README references a Google account `…@gamma.app`, describes "PPTX→Gamma import quality" grading, a 24-mode "Import Evals Taxonomy (PSSL)", three output variants ("Deck Doctor" / "Current Import" / "Programmatic Import") | OFFICIAL_DOCUMENTATION |
| G18 | 03:42:30 | `curl -sL https://gamma.app/` (plain curl) | **403**, 679,279 bytes | Cloudflare challenge on the marketing page for raw curl; body still contained valid `<meta name="description">` | API_RESPONSE |
| G19 | 03:42:35 | `node scripts/render2.mjs https://gamma.app/` | **STATUS 200** | Real browser passes the check. innerText captured — 4 sections (BRAINSTORM/DESIGN/REFINE/CONNECT) + 6 format tabs. Screenshot `raw/gamma_home_full.png` | OBSERVED_UI |
| G20 | 03:43:00 | `node scripts/render2.mjs https://gamma.app/templates` | **STATUS 200** | 20 categories; template pagination "1 2 … 46". Screenshot `raw/gamma_templates.png` | OBSERVED_UI |
| G21 | 03:43:02 | `node scripts/render2.mjs https://gamma.app/explore` | **STATUS 200** | Explore taxonomy: AI graphics (Logos/Art/Drawings/Posters/Backgrounds/Thumbnails), Presentations, Websites, Documents, Social media, API, plus Menus/Solutions. Screenshot `raw/gamma_explore.png` | OBSERVED_UI |
| G22 | 03:43:05 | `node scripts/render2.mjs https://gamma.app/pricing` | **STATUS 200** | Full tier table captured. Screenshot `raw/gamma_pricing.png` | OBSERVED_UI |
| G23 | 03:43:30 | `curl -sL 'https://help.gamma.app/en/?q=<term>'` × 8 queries (export, import, powerpoint, editable, theme brand, chart infographic, embed, version history, comment collaboration, credit) | **200 ×10** | Help-center article IDs extracted per query → `raw/gamma_hc/` | OFFICIAL_DOCUMENTATION |
| G24 | 03:44:00 | `curl` 18 individual help-center articles | **200 ×18** | Saved `raw/gamma_hc/*.html`; text extracted | API_RESPONSE |
| G25 | 03:44:30 | `node scripts/render2.mjs https://help.gamma.app/en/articles/7834324-…` | 200 | Redirects to `/7834324-how-do-credits-work-in-gamma` (URL slug drift) | OFFICIAL_DOCUMENTATION |

### Gamma help-center article IDs fetched (all HTTP 200)

`8022861-what-s-the-easiest-way-to-export-my-gamma` · `11047840-how-can-i-import-slides-or-content-into-gamma` · `15939201-why-doesn-t-my-exported-pdf-or-powerpoint-match-what-i-see-in-gamma` · `7838093-how-do-i-create-a-new-presentation-document-or-webpage-in-gamma` · `17238075-what-is-studio-mode-and-how-do-i-use-it` · `11016385-where-do-i-start-when-adding-content-in-gamma` · `16951068-what-are-shapes-and-how-do-i-use-them` · `11047576-can-i-publish-or-disable-my-gamma-site` · `11047806-can-i-embed-gamma-into-another-site` · `11048579-can-i-undo-a-change-or-restore-a-previous-version-in-gamma` · `11029098-how-can-i-generate-charts-and-diagrams-in-gamma` · `11029150-how-do-i-customize-themes-colors-and-fonts-in-gamma` · `11047226-how-do-collaboration-and-sharing-settings-work-in-gamma` · `10262646-how-do-i-change-my-gamma-theme` · `11016428-how-do-i-use-toggles-nested-slides-and-footnotes-effectively` · `17168766-how-do-i-add-videos-to-gamma` · `17237438-how-do-i-add-a-form-to-my-gamma` · `13928852-what-is-imagine-and-how-do-i-design-with-it`

## 5. Failures and blocks — complete list

| # | Item | Precise blocker | Tag |
|---|------|----------------|-----|
| F1 | `npx playwright` browser launch (first attempt) | playwright 1.64.1 requires chromium rev **1248**; local cache only had **1243** and **1194**. `Executable doesn't exist at …/chromium_headless_shell-1248/…`. **Resolved** by `npx playwright install chromium-headless-shell` (free Microsoft CDN download, no account). | BLOCKED → resolved |
| F2 | `nextslide.ai` product documentation / pricing / app | **Does not exist.** The domain now serves a single-page OpenAI-acquisition notice with an SPA catch-all. `/pricing` (browser, 200) renders the *same* notice. No docs, no pricing, no app, no API. The product is **sunset**; the team is at OpenAI. | OBSERVED_UI |
| F3 | `https://nextslide.ai/docs` via curl | **403** — Cloudflare bot-verification interstitial ("Performing security verification… Ray ID: a4e5814dd930c611"). Not bypassed. Not evidence of a page's existence. | BLOCKED (Cloudflare bot check) |
| F4 | `https://nextslide.ai/{app,blog,features,api,sitemap.xml}` via curl | **403** — same Cloudflare bot check as F3 | BLOCKED (Cloudflare bot check) |
| F5 | `https://nextslide.ai/robots.txt` | **404** | OBSERVED_UI |
| F6 | Gamma authenticated app (editor, dashboard, template editor, Gamma 5 agent UI) | Requires sign-in. Not attempted — no accounts created. Editor internals (card model, freeform canvas, agent chat UI) characterised only from **official documentation + help center + marketing surface**. | BLOCKED (login required) |
| F7 | Gamma REST API data-returning endpoints | Require `X-API-KEY`; all probes returned **401 `{"message":"Invalid API key","statusCode":401}`**. No key obtained, no bypass attempted. | BLOCKED (auth required) |
| F8 | Gamma MCP tool invocation | Requires OAuth 2.0 Bearer token + DCR-registered client with Gamma-allowlisted redirect URIs. Only metadata endpoints (G10, G12) are public. | BLOCKED (OAuth + DCR allowlist) |
| F9 | Gamma API "Classic" vs "Gamma 5" agent engine behavioural comparison | Both engines documented; only the *documented* contract is reported. No live generations were run (would consume credits + need a key). | UNKNOWN (documented-only) |
| F10 | `api-evangelist/gammaapp` (GitHub) | 3rd-party API profile, **not** Gamma-authored. Excluded from the code-availability verdict. | OBSERVED_UI |
| F11 | `gamma-app/pptx-renderer` | GitHub `fork: true` → a fork of a third-party Apache-2.0 project, **not** Gamma's export engine. Excluded. | OBSERVED_UI |
| F12 | `0xRafie/nextslide` (GitHub) | An OpenCode HTML-slide skill — **explicitly excluded by the brief** as not the target product. | OBSERVED_UI |
| F13 | `presenton/presenton`, `allweonedev/presentation-ai`, `ishandutta2007/open-gamma` etc. | Gamma *competitors / clones*, not Gamma's own source. Excluded. | OBSERVED_UI |
| F14 | n8n node `test/live.test.js` (14,689 bytes) | Exists but requires a real `GAMMA_API_KEY` to run. Not executed. | BLOCKED (needs paid-tier key) |
| F15 | Gamma Explore template gallery full item list | `gamma.app/explore` exposes taxonomy/categories only; the per-item grid requires JS + pagination beyond one render. 46 template pages on `/templates` and 12+ category taxonomies on `/explore` were captured; individual template IDs were not enumerated. | PARTIAL |

## 6. Evidence-tag legend used throughout all deliverables

| Tag | Meaning |
|-----|---------|
| `OBSERVED_UI` | Page rendered or inspected by me in headless Chromium; `document.body.innerText` captured verbatim |
| `OFFICIAL_DOCUMENTATION` | Fetched from `developers.gamma.app` or `help.gamma.app` (Gamma-operated) — quoted/paraphrased with URL |
| `API_RESPONSE` | I called a public endpoint and the literal response is recorded here |
| `INFERENCE` | Reasoned from cited evidence — the reasoning is stated inline |
| `UNKNOWN` | Could not determine with the available public surface |
| `BLOCKED` | Precise blocker stated in §5 above |
