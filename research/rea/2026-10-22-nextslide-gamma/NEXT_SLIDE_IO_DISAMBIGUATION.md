# NEXT_SLIDE.IO — Disambiguation Proof (Unrelated Product)

**Claim under test:** `nextslide.io` is a presentation *clicker / remote-control* product and is **NOT** a donor for, or related to, `nextslide.ai` (the AI-presentation product acquired by OpenAI) or to Gamma.
**Verdict: CONFIRMED UNRELATED.** The two share only a brand string. Different category, different product, different business model, different audience, no shared code, no shared branding, no cross-links, no shared company.

---

## 1. Primary evidence

| # | Evidence | Source | Tag |
|---|----------|--------|-----|
| E1 | **Page title:** `NextSlide - Turn your phone into a powerpoint clicker` | `https://www.nextslide.io/` @ 2026-10-22T03:39:50Z | API_RESPONSE |
| E2 | **Meta description:** `"Upload your PowerPoint, share a link, and anyone can control the slides from their own phone, anywhere - nothing to install."` | same | API_RESPONSE |
| E3 | **Hero headline (rendered):** `THE INTERNET CLICKER` / `Turn your phone into a powerpoint clicker` | `https://www.nextslide.io/` browser render @ 2026-10-22T03:40:30Z | OBSERVED_UI |
| E4 | **Value prop (rendered):** `See your notes and slides, in sync, on any screen.` / `Your presentation — runs in any browser.` / `Any screen shows slides or notes.` | same | OBSERVED_UI |
| E5 | **3-step flow (rendered):** `01 Upload your presentation` → `02 Send the links` → `03 Present in sync`; "Presenter links to control the presentation. **Content links to see your current slide, next slide, and notes.**" | same | OBSERVED_UI |
| E6 | **Feature headings (rendered):** `Shared presentation control` · `Turn your tablet into a confidence monitor` · `Audience Views` · `Hybrid Events` · `…And more!` | same | OBSERVED_UI |
| E7 | **Navigation (rendered):** `Next Slide | Features | FAQ | Use cases | Teams and Zoom | Presenter view on Zoom | Confidence monitors | OBS, vMix, and Wirecast | Stream Deck and API control` | same | OBSERVED_UI |
| E8 | **Live demo (rendered):** a demo deck titled `Trail Forward: FY2026 Growth Review` with `ON SCREEN / ACTIVE SLIDE / UP NEXT / CONTROL / 2/5 / 00:00 / NOTES` and a `Sharing your screen` panel showing avatars `AK, MR, JT, +2` — i.e. it **displays a deck someone else uploaded** | same | OBSERVED_UI |
| E9 | **Pricing model (rendered):** `Pay for the event, or pay for the year.` — event-based or annual pricing for *presenting*, not for creating content | same | OBSERVED_UI |
| E10 | **Testimonial (rendered):** `"My team got up to speed in a couple minutes. All three presenters were able to drive their own slides seamlessly."` — about *presenting*, not generating | same | OBSERVED_UI |
| E11 | **Platform claim (rendered):** `iPhone, Android, iPad, Windows, Mac - any browser.` — runs in a browser, no install | same | OBSERVED_UI |
| E12 | **Redirect:** `nextslide.io` → `https://www.nextslide.io/` (HTTP 200, 1 redirect) | curl @ 2026-10-22T03:39:50Z | API_RESPONSE |

---

## 2. Category contrast

| Dimension | `nextslide.ai` | `nextslide.io` | Same? |
|---|---|---|---|
| Category | AI **content generation** (prompt → presentation) | **Presentation remote control / clicker** (a browser companion for a deck you already have) | **NO** |
| Direction of data flow | user input → generated deck | existing deck → presenters' phones → audience screens | **NO** |
| AI at all | Yes — "turn prompts, notes, documents, or research into a polished, editable presentation" | No AI mentioned anywhere on the marketing surface | **NO** |
| Lifecycle | 2026-08-06 sunset page; team now at OpenAI | Live, selling event/annual plans | **NO** |
| Audience | Anyone creating decks | Event presenters, hybrid-event teams, confidence monitors, OBS/vMix/Wirecast, Stream Deck | **NO** |
| Monetization | Software subscription (product shut down) | Per-event or per-year plan for *presenting* | **NO** |
| Deliverable | A generated `.pptx` / PDF / web page | A **link** that lets phones drive slides + notes | **NO** |
| Brand assets | `og-image-logos-v3.png`, `brand/nextslide-x.png`, HK Grotesk Wide fonts, OpenAI co-branding | "Next / Slide" wordmark, plain Astro site (`data-astro-cid-*` attributes) | **NO** |
| Hosting | Cloudflare + Cloudflare Rocket Loader | Astro static build | **NO** |

---

## 3. Negative-evidence checks (things that would indicate a relationship — all absent)

| Check | Result | Tag |
|---|---|---|
| Does `nextslide.io` link to `nextslide.ai` (or vice-versa)? | **No.** No cross-domain link found in the `nextslide.io` HTML or the `nextslide.ai` HTML/JS bundle | OBSERVED_UI |
| Does `nextslide.io` mention AI, GPT, LLM, or generation anywhere on the marketing surface? | **No.** Rendered text contains zero AI-generation language | OBSERVED_UI |
| Does `nextslide.ai` mention presenting, remotes, clickers, or event control? | **No.** Its only body text is the OpenAI acquisition note | OBSERVED_UI |
| Do they share a founder/company? | **No public signal.** `nextslide.ai` names **Ahmed Beshry** (founder). `nextslide.io` names no founder and shows "Built by people who run real events." | OBSERVED_UI |
| Shared npm package / shared GitHub org? | No shared package or org found for either (`nextslide.io` publishes no SDK; the only relevant npm/GitHub hits for "nextslide" are unrelated — see §4) | API_RESPONSE |
| Shared codebase? | Not applicable — `nextslide.io` is a closed commercial product with no public source; `nextslide.ai` has no public source either | OBSERVED_UI |

---

## 4. Why this is not a donor source

- **`nextslide.io` has no AI generation surface.** Its entire capability set is *presenting* (upload → link → presenters drive slides/notes → audience views). It generates nothing. There is no generation, no templates, no themes, no documents, no web pages, no AI images, no export engine, no API for content creation.
- **It is not open source.** No public repo for `nextslide.io` exists; the site is a closed Astro build with no SDK published. Even setting aside the category mismatch, there is nothing to draw from.
- **Its relevant engineering surface is generic and well-trodden**: browser-based slide presentation, presenter-device sync over a shared link, screen-sharing, Stream Deck / OBS / vMix integration, confidence-monitor view. None of that is a differentiator for an AI creation platform.
- **Potential name collision risk is real and must be guarded**: any search for "NextSlide" will surface `nextslide.io` heavily and `nextslide.ai` barely. Treat `nextslide.io` as a **false-positive filter** in any future competitive scan.

### `nextslide` GitHub hits — none are `nextslide.io`'s source

`GET api.github.com/search/repositories?q=nextslide` → **31 repos, 0 stars on every relevant one.** Inspected: `onebone/nextslide-editor` (2★), `mattkula/nextslide` (1★, "NextSlide online powerpoint viewer"), `timmywheels/nextslide` (1★), `0xRafie/nextslide` (1★, **an OpenCode HTML-slide skill — excluded by the brief**), `NextSlide-AI/Nextslide.AI` (0★, **empty repo, and belongs to the *other* target**), `ammarjmahmood/nextslide` (0★, voice slide changer), `yasiru2003/nextslide` (0★, voice-activated slide controller), `A-NextSlide/nextslide`, `brianneidhardtclz/nextslide`, `eperez28/nextslide`, `Coconusu/nextslide26`, `mephistorine/nextslide`. **None is `nextslide.io`.**

---

## 5. One-page conclusion

> **`nextslide.io` is "THE INTERNET CLICKER" — a browser-based presentation remote that lets multiple presenters drive an uploaded PowerPoint from their own phones/tablets while audiences see slides and notes on any screen.** It is aimed at event presenters and hybrid events (confidence monitors, OBS/vMix/Wirecast, Stream Deck), priced per-event or per-year, and is marketed with a live multi-presenter demo.
>
> It is **categorically, commercially, and technically distinct** from `nextslide.ai` (a now-sunset AI prompt-to-presentation product whose team joined OpenAI) and from Gamma (an AI visual-communication platform with a documented REST API and a 21-tool hosted MCP server).
>
> **It contributes no donor capability, no source code, and no architectural insight to this research. It is logged solely as an excluded false positive.** Anyone repeating this scan should hard-exclude the domain `nextslide.io` and the string "nextslide clicker" from all queries, and must not treat `NextSlide-AI/Nextslide.AI` (an *empty* repo) as evidence of `nextslide.ai` source either.

**Evidence base:** `https://www.nextslide.io/` fetched via curl (HTTP 200, 85,599 B, 1 redirect from apex) and via headless Chromium (`document.body.innerText` captured verbatim), 2026-10-22T03:39:50Z – 2026-10-22T03:45:03Z. Screenshots: `raw/nextslide_io_rendered.png`. Raw HTML: `raw/nextslide_io.html`.
