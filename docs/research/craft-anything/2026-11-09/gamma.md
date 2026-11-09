# Investigation report

**Question:** Examine public Gamma site and its accessible code with Craft Anything; distinguish access blocks from product findings.

**Purpose:** Evidence-grade reverse engineering for Gomri; no proprietary-code copying or paywalled access.

**Done when:** Observed evidence, honest access limitations, source/feature gap and follow-up probes are written.

## What we looked at

- gamma-n8n (js-app)
- https://gamma.app/

## What we found

### In a fresh private browser on November 9, 2026, gamma.app returned a Just a moment page with HTTP 403, so the live Gamma editor was not inspected and no source code was recovered by this pass.

- **Confidence:** Seen it (observed)
- **Evidence:**
  - `ev_db9fb2f06f7a925aeaa5fdee9c13c949b237931188b527e42d8166caf1c9cd5b` — Opened https://gamma.app/: "Just a moment...". While loading: 1 error(s), 4 failed request(s). (url=https://gamma.app/)

### Craft Anything inspected the source checkout of gamma-app/n8n-nodes-gamma at 5d0b466: 32 JavaScript/TypeScript modules and 83 detected functions, with no IPC channels. This is a public n8n API client, not Gamma private generation server or editor source.

- **Confidence:** Worked it out (derived)
- **Evidence:**
  - `ev_6f0c4cb0385538c28b61826f54547042211c0d83e34f0e2c0ee38cba49c4a0fb` — Node package gamma-n8n 0.6.1: 32 source files, 0 IPC channel(s) (0 paired), 0 window(s), 5 endpoint(s), 0 route(s). (path=D:\Gomri-Research\CraftAnything\sources\gamma-n8n)

## Open questions

_None outstanding._

## How this was done

- **Mode:** Deep (the original's code and files could be read)
- **Engines:** builtin, cdp
- **Limitations:**
  - A fresh private browser: pages behind a login show their signed-out state.
  - Only one page of module summaries is included; tools that take this evidence need every module, so pass the input path to them or use offset=0 with a limit above modules_total.
  - Static reading only: code built at run time (eval, computed requires, remote content) is invisible; IPC pairs need literal channel names.

## Evidence ledger

- `ev_db9fb2f06f7a925aeaa5fdee9c13c949b237931188b527e42d8166caf1c9cd5b` **web_site_open** — Opened https://gamma.app/: "Just a moment...". While loading: 1 error(s), 4 failed request(s). (Seen it)
- `ev_6f0c4cb0385538c28b61826f54547042211c0d83e34f0e2c0ee38cba49c4a0fb` **js_app_map** — Node package gamma-n8n 0.6.1: 32 source files, 0 IPC channel(s) (0 paired), 0 window(s), 5 endpoint(s), 0 route(s). (Worked it out)
