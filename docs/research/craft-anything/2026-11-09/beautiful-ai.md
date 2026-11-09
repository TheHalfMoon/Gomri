# Investigation report

**Question:** Inspect the public Beautiful.ai homepage visually at desktop/mobile sizes, record CSS/layout evidence and limit claims to signed-out public surface.

**Purpose:** Evidence-grade reverse engineering for Gomri; no proprietary-code copying or paywalled access.

**Done when:** Observed evidence, honest access limitations, source/feature gap and follow-up probes are written.

## What we looked at

- https://www.beautiful.ai/

## What we found

### Beautiful.ai public homepage was inspected and captured at 1440px and 390px; evidence includes design tokens, 64 headings, 113 images, 194 links and 483 outline nodes. This is the marketing site, not the logged-in Smart Slides editor.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_a49a5304103e6e0a194991ac801dc725d66c77ea3c2d45679a8297274260dc3c` — Opened https://www.beautiful.ai/: "AI Presentation Software for Teams". While loading: 3 error(s), 3 failed request(s). (url=https://www.beautiful.ai/)
  - `ev_d1321a73b310037049aecf9eef8c5c10832c37e3a43d37a79ab741411263c398` — Captured https://www.beautiful.ai/: 2 screenshot(s), 483 outline items, 64 headings, 113 images, 194 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-beautiful-ai. (url=https://www.beautiful.ai/, path=D:\Gomri-Research\CraftAnything\capture-beautiful-ai)

## Open questions

_None outstanding._

## How this was done

- **Mode:** Deep (the original's code and files could be read)
- **Engines:** cdp
- **Limitations:**
  - A fresh private browser: pages behind a login show their signed-out state.
  - CSS custom properties and breakpoints from cross-origin stylesheets can't be read.
  - One state of the page: menus, dialogs and content behind interactions are not opened.

## Evidence ledger

- `ev_a49a5304103e6e0a194991ac801dc725d66c77ea3c2d45679a8297274260dc3c` **web_site_open** — Opened https://www.beautiful.ai/: "AI Presentation Software for Teams". While loading: 3 error(s), 3 failed request(s). (Seen it)
- `ev_d1321a73b310037049aecf9eef8c5c10832c37e3a43d37a79ab741411263c398` **web_site_capture** — Captured https://www.beautiful.ai/: 2 screenshot(s), 483 outline items, 64 headings, 113 images, 194 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-beautiful-ai. (Seen it)
