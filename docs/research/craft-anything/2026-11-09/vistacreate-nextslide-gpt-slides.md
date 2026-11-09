# Investigation report

**Question:** Inspect public VistaCreate, NextSlide and GPT Slides surfaces, public scripts and responsive layouts; separate marketing code and blocked pages from product engines.

**Purpose:** Evidence-grade reverse engineering for Gomri; no proprietary-code copying or paywalled access.

**Done when:** Observed evidence, honest access limitations, source/feature gap and follow-up probes are written.

## What we looked at

- https://create.vista.com/
- https://nextslide.ai/
- https://chatgpt.com/features/slides/

## What we found

### VistaCreate homepage was accessible from the private browser and captured at 1440px and 390px with 248 public outline nodes, 17 headings, 48 images, and 153 links. These are landing-page measurements, not logged-in editor behavior.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_5bc85a9bdbde76a99af1fb6cbdebdab2084c4a59c0e82a9ba49d4a0105560c92` — Opened https://create.vista.com/: "VistaCreate: AI Graphic Design Software for Online and Print". (url=https://create.vista.com/)
  - `ev_b4098ee0d65fafcce30595d4fe709325df4b519e1f9547e30dc68e664426506d` — Captured https://create.vista.com/: 2 screenshot(s), 248 outline items, 17 headings, 48 images, 153 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-vistacreate. (url=https://create.vista.com/, path=D:\Gomri-Research\CraftAnything\capture-vistacreate)

### Craft Anything static analysis of the VistaCreate homepage observed 15 loaded scripts, 12 modules, 74 apparent routes and 279 endpoint strings. The static analysis is partial and these numbers do not establish 279 working/private APIs or their availability.

- **Confidence:** Worked it out (derived)
- **Evidence:**
  - `ev_b17ab1490c385224f0468c01a992d2a0f84ecdd72be0d2e3b25c9f1aefe3ab6b` — Analysed 15 script(s) from https://create.vista.com/: 12 module(s), 279 endpoint(s), 74 route(s), bundled with tsc/webpack. (url=https://create.vista.com/)

### The public nextslide.ai site currently displays NextSlide is joining OpenAI. A 1440/390 capture shows only the announcement site, not the historic slide editor or its implementation.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_a8691cd84c27f4bef683e9217aaab827c40b75ef7957e6e34d51909a417c8a43` — Opened https://nextslide.ai/: "NextSlide is joining OpenAI". (url=https://nextslide.ai/)
  - `ev_b6808d54e33581ae69df2ecdd03b8a1a7c0ad9e4ecc0c4d3cfafb7540ee32557` — Captured https://nextslide.ai/: 2 screenshot(s), 15 outline items, 1 headings, 1 images, 0 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-nextslide. (url=https://nextslide.ai/, path=D:\Gomri-Research\CraftAnything\capture-nextslide)

### Static JavaScript analysis of the live NextSlide announcement page found 5 scripts, 3 modules and 8 endpoint strings with zero app routes; the result is not the proprietary slide engine.

- **Confidence:** Worked it out (derived)
- **Evidence:**
  - `ev_8587d0bea1e46374d578bebe6eac131db24c2e4367db911dbe1f973cbeca8f32` — Analysed 5 script(s) from https://nextslide.ai/: 3 module(s), 8 endpoint(s), 0 route(s). (url=https://nextslide.ai/)

### The public GPT Slides product URL in an unauthenticated fresh browser displayed Just a moment instead of the editor, with two failed requests, so this Craft Anything pass did not inspect the private Slides UI or engine.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_38f176144b8c364f96ac10d6f932f182143d54792449c804a610f7fd97fd8b0d` — Opened https://chatgpt.com/features/slides/: "Just a moment...". While loading: 0 error(s), 2 failed request(s). (url=https://chatgpt.com/features/slides/)

## Open questions

_None outstanding._

## How this was done

- **Mode:** Deep (the original's code and files could be read)
- **Engines:** builtin, cdp
- **Limitations:**
  - A fresh private browser: pages behind a login show their signed-out state.
  - CSS custom properties and breakpoints from cross-origin stylesheets can't be read.
  - One state of the page: menus, dialogs and content behind interactions are not opened.
  - Only the scripts this live page had loaded during the window were analysed; lazily loaded chunks may be missing.
  - Static reading only: code built at run time (eval, computed imports) is invisible.

## Evidence ledger

- `ev_5bc85a9bdbde76a99af1fb6cbdebdab2084c4a59c0e82a9ba49d4a0105560c92` **web_site_open** — Opened https://create.vista.com/: "VistaCreate: AI Graphic Design Software for Online and Print". (Seen it)
- `ev_b17ab1490c385224f0468c01a992d2a0f84ecdd72be0d2e3b25c9f1aefe3ab6b` **web_page_js_analyze** — Analysed 15 script(s) from https://create.vista.com/: 12 module(s), 279 endpoint(s), 74 route(s), bundled with tsc/webpack. (Worked it out)
- `ev_b4098ee0d65fafcce30595d4fe709325df4b519e1f9547e30dc68e664426506d` **web_site_capture** — Captured https://create.vista.com/: 2 screenshot(s), 248 outline items, 17 headings, 48 images, 153 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-vistacreate. (Seen it)
- `ev_a8691cd84c27f4bef683e9217aaab827c40b75ef7957e6e34d51909a417c8a43` **web_site_open** — Opened https://nextslide.ai/: "NextSlide is joining OpenAI". (Seen it)
- `ev_8587d0bea1e46374d578bebe6eac131db24c2e4367db911dbe1f973cbeca8f32` **web_page_js_analyze** — Analysed 5 script(s) from https://nextslide.ai/: 3 module(s), 8 endpoint(s), 0 route(s). (Worked it out)
- `ev_b6808d54e33581ae69df2ecdd03b8a1a7c0ad9e4ecc0c4d3cfafb7540ee32557` **web_site_capture** — Captured https://nextslide.ai/: 2 screenshot(s), 15 outline items, 1 headings, 1 images, 0 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-nextslide. (Seen it)
- `ev_38f176144b8c364f96ac10d6f932f182143d54792449c804a610f7fd97fd8b0d` **web_site_open** — Opened https://chatgpt.com/features/slides/: "Just a moment...". While loading: 0 error(s), 2 failed request(s). (Seen it)
- `ev_ac3b3f35c4bbf9307b65b40f5dd7b2c78d0f6ffdb1a35b4b36ec0479ecef8714` **core_evidence_browse** — Part of web_page_js_analyze evidence (all-in-view). (Worked it out)
