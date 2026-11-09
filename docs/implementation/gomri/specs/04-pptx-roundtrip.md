# S04 — Native Editable PowerPoint, Speaker Notes, Bullets and RTL

**Goal:** Native PPTX slides stay meaningfully editable, with explicit fallbacks for unsupported features. **Owner:** R5; R4 citations; R6 E2E; R7 independent review. **Depends:** S01/S02/S03. Do not equate green screenshot tests with editable PowerPoint.

## What source already exists

- Keep existing \`servers/nextjs/lib/run-bundled-presentation-export.ts\`, \`servers/nextjs/lib/template-v2-json-to-html.ts\` and \`@presenton/export-core@1.0.34\` baseline (verify actual pin at build HEAD).
- In PR #88 \`servers/nextjs/tests/export-fidelity.test.mjs\`, 15/15 true JSON -> PPTX -> JSON tests passed on Windows. The tests **expect speaker notes written to PPTX but not reimported**, and bullets preserved only as flattened plain text. They are documented P3 defects/limitations, **not zero-loss passes**.
- SlideModel and UI already carry \`speaker_note\`; do not add a second notes database.
- Beautiful.ai public fork of PptxGenJS at \`1f3c948832268024833094de86687f506d59ae77\` is a compare-first bounded source candidate, not the private Smart Slides renderer. Preserve upstream Brent Ely MIT notices and review any actual fork changes before borrowing.

## Implementation sequence

1. Freeze eight synthetic canonical decks including: rich bullets, bilingual/RTL, native chart+units, table, complex shape, brand image, distinct speaker notes, adversarial malformed source.
2. Trace speaker note from SQL Slide -> UI DTO -> bundled export -> \`ppt/notesSlides\` and relationships -> import -> canonical Slide. Fix the minimal missing parser/export path.
3. Recreate **native paragraph bullet semantics** in OOXML, including indentation/levels, numbering and RTL. Literal bullet characters in normal text are not equivalent.
4. Inspect actual chart, table, shape and data part types, not only screenshot pixels; reimport with stable component mapping and unchanged figures.
5. Build explicit per-object loss receipt for unsupported CSS/Lottie animation, raster fallback, inaccessible font or vector.
6. Add bounded ZIP/XML import hardening: max file count, max decompressed size/ratio, safe relationship allowlist and no external entity expansion; prior fixture ZIP helper is not a hardened arbitrary PPTX parser.
7. Test export access and ownership at request, execution and download after role revocation. Auth and realpath guards already exist; test the full flow before declaring a vulnerability or success.
8. Test real Windows editable PPTX open in an authorized native viewer; if viewer unavailable mark **BLOCKED**.

## Output contract

Each export records: exact input digest, exporter SHA/version, native text IDs, chart series data and units, table cell inventory, speaker-note content/relationships, fonts used/fallbacks, explicit loss receipts per slideId/componentId/format, tested output hash, and assertion results. A flattened PNG can be a valid stated fallback **only if not falsely advertised as a native editable chart/table**.

## Acceptance (all required or explicitly scoped out by owner)

- **S04-NOTE:** notes for two slides survive reimport and native edit, or release blocks with a truthful loss report.
- **S04-BULLET:** nested bullets/numbering survive as native semantics; no silent flattened text.
- **S04-CHART:** native OOXML chart and workbook values/labels/units match source exactly.
- **S04-TABLE:** source table cells and typed data reimport natively.
- **S04-ID:** persistent mapping source component -> OOXML element -> reimport identity.
- **S04-RTL:** mixed Arabic and English, digits, diacritics, typography and logical reading order checked in HTML and output.
- **S04-SAFETY:** malicious ZIP/relationship tests rejected, no filesystem/network leak.
- **S04-PRIV:** owner-scoped export/start/download and revocation tests pass in isolated backend.
- **S04-NATIVE:** Windows viewer proves actual text/chart/table editable, with screenshot and data inspection.
- **S04-LOSS:** every unsupported visual dynamic feature explicitly receipted; zero **silent** supported-data loss.

**Tests:** existing \`tests/export-fidelity.test.mjs\` and fixture helpers in PR #88, supplemented by exact negative controls. Fail first for notes/bullets before fixing; no rewriting expectations to make a defect disappear. No wholesale exporter replacement or paid services. **Stop:** any unsupported loss, unreviewed license, invalid native object claim or unsafe import. **Rollback:** adapter off, previous exporter exact pin and honest feature downgrade status.
