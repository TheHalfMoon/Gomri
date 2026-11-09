# ADR-0001 — One canonical editor, bounded source transplants

**Status:** Accepted as design direction, **runtime implementation conditioned on S00 safety qualification**. **Date:** 2026-11-09.

## Context

Gomri already has a Presenton-derived editor, slide model and export engine. Competitor REAs suggest strong layout/agent/collaboration capabilities, while owner-controlled Ninerr and Skilit contain reusable source. Importing a full alternative editor would create duplicate scene state, migrations, parity bugs and untestable source provenance.

## Decision

Preserve **existing Template V2/Konva** as the interactive scene authority and FastAPI as persisted authority. Reuse the current exporter first. Admit each donor as `COPY_BOUNDED`, `ADAPT`, `REFERENCE` or `DEFER` with exact SHA, file list, license/NOTICE, asset boundary, renaming map, tests and owner. Copy code only where same-fixture comparison proves value.

Ninerr history/authorization is a strong candidate for **typed operations and selection control**, but its graph IDs and collaboration runtime cannot simply replace Gomri's DB/session. The adapter must be explicit. Skilit design intelligence informs layout pattern selection; its database and billing layer are out of scope. The public Beautiful.ai PptxGenJS fork is a comparison/export helper, not a private Smart Slides engine. NextSlide animation skill isn't nextslide.ai proprietary source.

## Consequences

Positive: one editor, fewer migrations, testable scoped imports, real source provenance, lower local disk and dependency pressure.

Negative: incremental adapters need careful ID/semantic mapping and may be slower to reach every competitor marketing capability. Accept this to preserve correctness.

## Rejected alternatives

Full fork of another editor; bulk replacing export runtime; assuming competitor public JavaScript exposes private AI source; copying licensed fonts/templates with code rights only; second persisted scene graph.

## Verification

S02 fixture adapter and S03 real DB authorization/CAS tests; S04 OOXML no-loss and E2E identity tests; independent source/NOTICE review before merge.
