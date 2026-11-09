# Investigation report

**Question:** Inspect public historical Crello font metrics code and its relevance to Gomri

**Purpose:** Source provenance and font-fidelity research

**Done when:** Source graph evidence recorded

## What we looked at

- crello-font (js-app)
- https://github.com/crello/font-metrics-sizing

## What we found

### Craft Anything statically analyzed crello/font-metrics-sizing 1.0.5 at SHA 73b6cba: one JavaScript source module and six functions with zero network endpoints. It is an old public font-metric normalization utility, not current VistaCreate editor code.

- **Confidence:** Worked it out (derived)
- **Evidence:**
  - `ev_31795adfb81bdfd8d0d462afd8c9e844be492064f4eedd8e3167ea49deba5406` — Node package crello-font 1.0.5: 1 source files, 0 IPC channel(s) (0 paired), 0 window(s), 0 endpoint(s), 0 route(s). (path=D:\Gomri-Research\CraftAnything\sources\crello-font, module=index.js (main))

## Open questions

_None outstanding._

## How this was done

- **Mode:** Deep (the original's code and files could be read)
- **Engines:** builtin
- **Limitations:**
  - Static reading only: code built at run time (eval, computed requires, remote content) is invisible; IPC pairs need literal channel names.

## Evidence ledger

- `ev_31795adfb81bdfd8d0d462afd8c9e844be492064f4eedd8e3167ea49deba5406` **js_app_map** — Node package crello-font 1.0.5: 1 source files, 0 IPC channel(s) (0 paired), 0 window(s), 0 endpoint(s), 0 route(s). (Worked it out)
