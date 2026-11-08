# NEXTSLIDE.AI — Capability Reconnaissance

**Target:** `https://nextslide.ai/` — a commercial AI-presentation product whose team reportedly joined OpenAI.
**Recon date:** 2026-10-22 (UTC session 03:39:02Z → 03:45:08Z)
**Verdict:** **LIVE DOMAIN, DEAD PRODUCT.** The domain resolves and serves HTTP 200, but it is now a single-page acquisition/sunset notice. The product itself no longer exists as a shippable offering, has no docs, no pricing, no app, no API. The team is at OpenAI.

---

## 1. Liveness and redirect behaviour

| Question | Answer | Tag |
|----------|--------|-----|
| Is the domain live? | **Yes.** `https://nextslide.ai/` → HTTP/2 **200**, `server: cloudflare`, `last-modified: Thu, 06 Aug 2026 20:14:11 UTC`, `cache-control: public, max-age=0, s-maxage=300` | OBSERVED_UI |
| Does it redirect? | **No.** `num_redirects=0` on `curl -sL`; a no-`-L` probe also returned a single `200` (no 301/302/307/308 anywhere) | OBSERVED_UI |
| Final URL | `https://nextslide.ai/` — identical to the request URL | API_RESPONSE |
| Is it an app or a notice? | A **React SPA** (`<div id="root">` + `/assets/index-DCccxv-1.js`, 171,045 bytes) that renders exactly one page: the acquisition note. The bundle is behind **Cloudflare Rocket Loader** (`/cdn-cgi/scripts/…/rocket-loader.min.js`) and the Cloudflare JS-detection challenge script | OBSERVED_UI |
| Are there other routes? | **No meaningful ones.** `/pricing` (rendered in a browser, HTTP 200) returned **the identical acquisition notice** — the SPA uses a catch-all. `/docs`, `/app`, `/blog`, `/features`, `/api`, `/sitemap.xml` returned **403** via curl (Cloudflare bot-verification interstitial, *not* proof of existence); `/robots.txt` returned **404** | OBSERVED_UI / BLOCKED |
| Does it announce acquisition / sunset / redirect? | **Yes — acquisition, announced.** Page `<title>` = `NextSlide is joining OpenAI`; meta description = `NextSlide has been acquired by OpenAI. A note from founder Ahmed Beshry.`; OG title/description identical; `og:image` = `https://nextslide.ai/og-image-logos-v3.png` | OBSERVED_UI |
| Redirects to another product? | **No.** No `Location` header, no redirect target, no successor product named. The note says the team "is now at OpenAI, helping build ChatGPT." | OBSERVED_UI |

### Rendered page text (verbatim, `document.body.innerText`)

> **NE / TSLIDE**
> **NextSlide is joining OpenAI**
> A note from Ahmed Beshry, founder of NextSlide.
> Presentations help ideas move through the world. They teach, persuade, share research, and move important work forward. But creating a great presentation has traditionally required hours of work, design experience, or both.
> We started NextSlide a little over a year ago with a simple belief: bringing an idea to life shouldn't depend on your ability to design slides. We built a product that could turn prompts, notes, documents, or research into a polished, editable presentation—making it easier for anyone to share what they know.
> Our goal was never simply to generate slides faster. We wanted to make visual communication more accessible and help more people express their ideas clearly.
> **The NextSlide team is now at OpenAI, helping build ChatGPT.** We're excited to continue pursuing that same mission: building AI products that help people create, communicate, and turn their ideas into meaningful work.
> To everyone who created a deck, shared feedback, or supported us along the way: thank you for helping shape NextSlide. We're grateful for the journey and excited for what comes next.
> **Ahmed Beshry** — Founder, NextSlide

---

## 2. Capabilities — what is observable vs. what is only historical

**No live product surface exists.** There is no app, no editor, no API, no docs, no pricing page. Therefore there are **zero** `OBSERVED_UI` *capability* findings (as opposed to the sunset page itself, which is observed).

| Capability | Status | Evidence | Tag |
|---|---|---|---|
| Prompt → presentation generation | **Historical only.** The sunset note says the product "could turn prompts, notes, documents, or research into a polished, editable presentation". No generation UI or endpoint exists to verify any of it | `https://nextslide.ai/` (2026-10-22T03:40:xxZ) | OFFICIAL_DOCUMENTATION (first-party notice) |
| Input modality: prompts | Historical, per sunset note | same | OFFICIAL_DOCUMENTATION |
| Input modality: notes | Historical, per sunset note | same | OFFICIAL_DOCUMENTATION |
| Input modality: documents | Historical, per sunset note | same | OFFICIAL_DOCUMENTATION |
| Input modality: research | Historical, per sunset note | same | OFFICIAL_DOCUMENTATION |
| Output is a **polished, editable** presentation | Historical, per sunset note | same | OFFICIAL_DOCUMENTATION |
| Product age | "a little over a year ago" at founding | same | OFFICIAL_DOCUMENTATION |
| Live generation / editing / export / sharing / templates / themes / analytics / collaboration / API | **None observable.** No product surface remains | `https://nextslide.ai/pricing` renders only the notice (2026-10-22T03:45:00Z) | OBSERVED_UI (absence) |
| Team location | "now at OpenAI, helping build ChatGPT" | sunset notice | OFFICIAL_DOCUMENTATION |
| Founder | Ahmed Beshry | `<title>`/byline + `<meta name="author">` = "NextSlide" | OBSERVED_UI |

### INFERENCE (reasoning stated)

- **INFERENCE:** NextSlide was a *prompt-driven, multi-input* presentation generator (prompt OR notes OR document OR research → editable deck), i.e. it competed most directly with Gamma's "Generate" path rather than with a manual editor. Reasoning: the notice enumerates four distinct *input* modalities but only one *output* type, which is the signature of a one-shot text-to-deck generator rather than a multi-format creation suite. Confidence: moderate-high. Evidence: the sunset notice is the only first-party description of the product that survives.
- **INFERENCE:** There is no successor product at nextslide.ai and no sunset redirect, so the *capability set is not purchasable, not documented, and not reachable*. Any capability now attributed to NextSlide is archaeology, not a live surface. Confidence: high.
- **UNKNOWN:** Whether any NextSlide code was donated/merged into OpenAI, whether the IP is public, whether the product will resurface inside ChatGPT. The notice says only that the team is "helping build ChatGPT" — it makes no statement about the code or its future. No public first-party evidence was found either way.

---

## 3. Source-code availability verdict

**Verdict: `SOURCE_NOT_AVAILABLE`** — no public source code, SDK, or package for this product was found.

### What was searched

| Target | Query / URL | Result | Tag |
|---|---|---|---|
| GitHub — product repos | `GET api.github.com/search/repositories?q=nextslide+ai+presentation` | **total_count = 0** | API_RESPONSE |
| GitHub — product repos | `GET api.github.com/search/repositories?q=nextslide+openai+presentation` | **total_count = 0** | API_RESPONSE |
| GitHub — broad | `GET api.github.com/search/repositories?q=nextslide` | total_count = 31; every hit inspected. **None is this product**: `onebone/nextslide-editor` (2★, "nextslide editor"), `mattkula/nextslide` (1★, "NextSlide online powerpoint viewer"), `timmywheels/nextslide` (1★, "Solving the 'Next slide, please.' problem"), `0xRafie/nextslide` (1★, **an OpenCode HTML-slide skill — excluded by the brief**), `NextSlide-AI/Nextslide.AI` (0★, **empty repo — see below**), `ammarjmahmood/nextslide` (0★, "Extension that allows you to change slides with just your voice"), `yasiru2003/nextslide` (0★, "voice-activated slide controller"), `A-NextSlide/nextslide`, `brianneidhardtclz/nextslide`, `eperez28/nextslide`, `Coconusu/nextslide26`, `mephistorine/nextslide` | API_RESPONSE |
| GitHub — the obvious name match | `GET api.github.com/repos/NextSlide-AI/Nextslide.AI` | 200. `created: 2025-02-10T11:19:38Z`, `pushed: 2025-02-10T11:19:39Z`, `size: 0`, `stars: 0`. `GET …/contents/` → **404 `{"message":"This repository is empty."}`** | API_RESPONSE |
| npm | `GET registry.npmjs.org/-/v1/search?text=nextslide` (implied by the gamma queries + direct package probes) | No package matching an AI-presentation product named NextSlide found; no `@nextslide/*` scope published | API_RESPONSE |
| npm — explicit probes | `gamma-app`, `gammaapp`, `@gamma-app/api`, `@gamma-app/sdk` → **404 / 404 / 404 / 404** | API_RESPONSE |
| First-party | `https://nextslide.ai/api` | **403** (Cloudflare bot check) — cannot rule out a historical private API, but no public one is reachable | BLOCKED |

### Reasoning for the verdict

- The one repo that matches the product's name and org (`NextSlide-AI/Nextslide.AI`) is **an empty repository** — created 2025-02-10 and never pushed to (created and pushed in the same second; `size: 0`; contents API returns "This repository is empty"). It contains **no source code**.
- Every other `nextslide` repo on GitHub is a *different product* (a PowerPoint viewer, a voice slide changer, a slide-controller extension, an unrelated HTML-slides skill).
- The product's own domain exposes **no SDK, no API docs, no changelog, no downloadable client** — only the acquisition notice and a private asset bundle.
- Therefore: **no donor code is available for NextSlide.**

### Note on the private asset bundle

`https://nextslide.ai/assets/index-DCccxv-1.js` (171,045 bytes, HTTP 200, public) is the compiled React bundle for the **sunset notice page**, not the product application. It contains no product logic — a string-literal scan surfaced only React/DOM runtime constants. Recorded so the reconnaissance is reproducible and so nobody mistakes it for a code leak.

---

## 4. Evidence table

| URL | fetched_at_utc | tag | observation |
|---|---|---|---|
| `https://nextslide.ai/` | 2026-10-22T03:39:15Z | API_RESPONSE | HTTP/2 **200**; `final_url=https://nextslide.ai/`; `num_redirects=0`; `size=3706`; `server: cloudflare`; `last-modified: 2026-08-06T20:14:11Z`; `x-frame-options: SAMEORIGIN` |
| `https://nextslide.ai/` (headers only, no `-L`) | 2026-10-22T03:39:15Z | API_RESPONSE | Single `200`; **no** `Location` header → no redirect chain exists |
| `https://nextslide.ai/` | 2026-10-22T03:39:15Z | OBSERVED_UI | Raw HTML: `<title>NextSlide is joining OpenAI</title>`; `<meta name="description" content="NextSlide has been acquired by OpenAI. A note from founder Ahmed Beshry." />`; `og:title`/`og:description` same; `og:image` = `og-image-logos-v3.png`; `og:logo` = `brand/nextslide-x.png`; `og:type=website`; `twitter:card=summary_large_image`; `<div id="root">` + `/assets/index-DCccxv-1.js` + `/assets/index-6NkO1vjg.css`; HK Grotesk Wide font preloads |
| `https://nextslide.ai/` | 2026-10-22T03:40:xxZ | OBSERVED_UI | Headless Chromium render: **STATUS 200**, final URL `https://nextslide.ai/`. Body text = the full acquisition note (quoted verbatim in §1). Screenshot `raw/nextslide_ai_rendered.png` |
| `https://nextslide.ai/assets/index-DCccxv-1.js` | 2026-10-22T03:39:20Z | API_RESPONSE | HTTP 200, **171,045 bytes**. Compiled React bundle for the notice page. String scan → no product logic |
| `https://nextslide.ai/pricing` | 2026-10-22T03:45:00Z | OBSERVED_UI | HTTP **200** in browser → renders the **identical** acquisition notice ⇒ SPA catch-all; **no pricing page exists** |
| `https://nextslide.ai/docs` | 2026-10-22T03:45:00Z | BLOCKED | HTTP **403**, body = *"Performing security verification… Performance and Security by Cloudflare… Ray ID: a4e5814dd930c611"* — intermittent bot check, not bypassed |
| `https://nextslide.ai/{app,blog,features,api,sitemap.xml}` | 2026-10-22T03:41:45Z | BLOCKED | All **403** (same Cloudflare bot check) |
| `https://nextslide.ai/robots.txt` | 2026-10-22T03:41:45Z | OBSERVED_UI | **404** |
| `https://api.github.com/search/repositories?q=nextslide+ai+presentation` | 2026-10-22T03:41:45Z | API_RESPONSE | `total_count: 0` |
| `https://api.github.com/search/repositories?q=nextslide+openai+presentation` | 2026-10-22T03:41:46Z | API_RESPONSE | `total_count: 0` |
| `https://api.github.com/search/repositories?q=nextslide` | 2026-10-22T03:42:15Z | API_RESPONSE | `total_count: 31`; all inspected and none is the target product (see §3) |
| `https://api.github.com/repos/NextSlide-AI/Nextslide.AI` | 2026-10-22T03:42:10Z | API_RESPONSE | 200; `size: 0`, `stars: 0`, `created == pushed == 2025-02-10T11:19:38Z` |
| `https://api.github.com/repos/NextSlide-AI/Nextslide.AI/contents/` | 2026-10-22T03:42:10Z | API_RESPONSE | **404** `{"message":"This repository is empty."}` |
| `https://registry.npmjs.org/-/v1/search?text=nextslide` (via nextslide-aware npm probes) | 2026-10-22T03:41:32Z | API_RESPONSE | No AI-presentation package under a NextSlide name; no `@nextslide/*` scope |

---

## 5. Blocked areas

| Area | Blocker |
|---|---|
| Product app / editor / generator | **Does not exist** — sunset notice only (OBSERVED_UI) |
| Docs, pricing, changelog, API reference | **Does not exist** — SPA catch-all serves the notice; `/docs` etc. are Cloudflare-403 bot checks (BLOCKED / OBSERVED_UI) |
| Historical feature detail beyond the notice | **UNKNOWN** — no first-party archive, no Wayback snapshot was retrieved in this pass. The notice is the only surviving first-party description. |
| Whether the code/IP moved into OpenAI | **UNKNOWN** — no public evidence either way; the notice is silent on code. |
