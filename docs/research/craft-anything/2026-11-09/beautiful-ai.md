# Investigation report

**Question:** Inspect the public Beautiful.ai homepage visually at desktop/mobile sizes, record CSS/layout evidence and limit claims to signed-out public surface.

**Purpose:** Evidence-grade reverse engineering for Gomri; no proprietary-code copying or paywalled access.

**Done when:** Observed evidence, honest access limitations, source/feature gap and follow-up probes are written.

## What we looked at

- beautiful-pptx (js-app)
- https://www.beautiful.ai/

## What we found

### Beautiful.ai public homepage was inspected and captured at 1440px and 390px; evidence includes design tokens, 64 headings, 113 images, 194 links and 483 outline nodes. This is the marketing site, not the logged-in Smart Slides editor.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_a49a5304103e6e0a194991ac801dc725d66c77ea3c2d45679a8297274260dc3c` — Opened https://www.beautiful.ai/: "AI Presentation Software for Teams". While loading: 3 error(s), 3 failed request(s). (url=https://www.beautiful.ai/)
  - `ev_d1321a73b310037049aecf9eef8c5c10832c37e3a43d37a79ab741411263c398` — Captured https://www.beautiful.ai/: 2 screenshot(s), 483 outline items, 64 headings, 113 images, 194 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-beautiful-ai. (url=https://www.beautiful.ai/, path=D:\Gomri-Research\CraftAnything\capture-beautiful-ai)

### Craft Anything statically examined beautifulai/PptxGenJS at 1f3c948, identifying PptxGenJS 3.13.0-bai.5 and 55 source modules; its bundled browser code includes JSZip. This modified exporter library is not Beautiful.ai private Smart Slide layout engine; analysis has a node cap.

- **Confidence:** Worked it out (derived)
- **Evidence:**
  - `ev_f43d9ee5e85cd56ca9f28084cce9ec67638cfe8ed392bca33273fd1a4915cf71` — Web app beautiful-pptx 3.13.0-bai.5: 55 source files, 0 IPC channel(s) (0 paired), 0 window(s), 0 endpoint(s), 2 route(s), bundled with babel/browserify. (path=D:\Gomri-Research\CraftAnything\sources\beautiful-pptx, module=dist/pptxgen.cjs.js (main))

## Open questions

_None outstanding._

## How this was done

- **Mode:** Deep (the original's code and files could be read)
- **Engines:** builtin, cdp
- **Limitations:**
  - 2915 graph nodes were dropped at the 1300-node cap; raise max_nodes to keep them.
  - A fresh private browser: pages behind a login show their signed-out state.
  - CSS custom properties and breakpoints from cross-origin stylesheets can't be read.
  - One state of the page: menus, dialogs and content behind interactions are not opened.
  - Only one page of module summaries is included; tools that take this evidence need every module, so pass the input path to them or use offset=0 with a limit above modules_total.
  - Static reading only: code built at run time (eval, computed requires, remote content) is invisible; IPC pairs need literal channel names.

## Evidence ledger

- `ev_a49a5304103e6e0a194991ac801dc725d66c77ea3c2d45679a8297274260dc3c` **web_site_open** — Opened https://www.beautiful.ai/: "AI Presentation Software for Teams". While loading: 3 error(s), 3 failed request(s). (Seen it)
- `ev_d1321a73b310037049aecf9eef8c5c10832c37e3a43d37a79ab741411263c398` **web_site_capture** — Captured https://www.beautiful.ai/: 2 screenshot(s), 483 outline items, 64 headings, 113 images, 194 links, 0 forms → D:\Gomri-Research\CraftAnything\capture-beautiful-ai. (Seen it)
- `ev_f43d9ee5e85cd56ca9f28084cce9ec67638cfe8ed392bca33273fd1a4915cf71` **js_app_map** — Web app beautiful-pptx 3.13.0-bai.5: 55 source files, 0 IPC channel(s) (0 paired), 0 window(s), 0 endpoint(s), 2 route(s), bundled with babel/browserify. (Worked it out)
