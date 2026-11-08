# Export-fidelity fixtures

Synthetic decks and measured expectations for the export round trip.

```
decks/            eight synthetic decks, one per fidelity concern
expectations/     the MEASURED facts, one entry per deck
generator.mjs     regenerates the decks (deterministic)
measure.mjs       re-measures the expectations against the real export core
roundtrip.mjs     the round trip itself, plus the ZIP reader
```

## The round trip

```text
deck JSON → pptx-from-json → PPTX → pptx-to-json → JSON
```

It is **browser-free**: no Chromium, no ImageMagick, no LibreOffice. That is what lets it run on
CI. The production export path is browser-bound; this harness is the deterministic tier beneath
it.

## What is pinned, and what is not

| Pinned | Not pinned |
|---|---|
| the re-imported JSON (element types, run text, font attributes, geometry, alignment) | the PPTX bytes — two runs differ by a UUID file name and wall-clock ZIP timestamps |
| the PPTX package part list (notes slides, charts, media, slide count) | rendered pixels — that is a browser tier |

## Running it

```bash
npm run sync:presentation-export   # free, public release tarball; not committed
node --test servers/nextjs/tests/export-fidelity.test.mjs
```

The export runtime is gitignored, so a checkout without it reports an **explicit skip with a
reason** (`EF-RUNTIME-ABSENT`). A skip is never reported as a pass.

The export core requires Node >= 22.12.0. On an older Node the harness reports
`EF-NODE-VERSION` rather than failing in a confusing way.
