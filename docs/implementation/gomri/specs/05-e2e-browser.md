# S05 — Browser E2E, Accessibility and Visual Quality

**Goal:** Prove the complete authoring flow in a **real browser**, using synthetic accounts and a disposable backend. **Owner:** R6, supported by R8 (security), R10 (visual quality). **Depends on:** S03 and S04. Contract/unit tests are not a substitute for E2E.

## Local runner admission (observed 2026-11-09)

- Gomri's Next.js \`package.json\` has \`cypress ^15.18.1\`. Windows \`servers/nextjs/node_modules/cypress/package.json\` and \`.bin/cypress.cmd\` exist.
- Existing \`servers/nextjs/cypress.config.ts\` configures component tests (Next/Webpack) only; an E2E suite directory was **not found** at the inspected commit.
- \`%LOCALAPPDATA%/Cypress/Cache\` was absent. This means the Cypress **CLI exists** but a runnable browser binary is **not verified**.
- A Playwright browser cache exists, but \`@playwright/test\`/\`playwright\` were absent in the inspected Next.js dependency tree. Do not claim ready Playwright E2E.
- Existing FastAPI integration and Next.js Node tests are useful regression checks, but not UI E2E.

## First builder task: qualify the existing Cypress runner, $0

Verify \`cypress.cmd --version\`, binary cache and test browser availability in a temporary environment. Prefer adding Cypress E2E test configuration to the **already installed Cypress** instead of installing a second full test platform. If the official free Cypress binary needs downloading, verify its source/checksum, require adequate disk and use test-only cache; free software download is not a paid inference API. Do not auto-contact Cypress Cloud or send recordings without explicit approval.

Create a new \`servers/nextjs/cypress.config.e2e.ts\` or equivalent scoped config, and \`servers/nextjs/cypress/e2e/*.cy.ts\` with test-only fixtures. Keep the component config unchanged. Use explicit localhost target ports, isolated browser profile and synthetic owners A/B. Do not use the user's signed-in Vivaldi session.

## Mandatory real-browser user journeys

| Case | Journey | Observable PASS requirements |
|---|---|---|
| E01 | Synthetic source -> outline -> 8–12 slides | All sources/citations visible, no missing figures, no external paid provider |
| E02 | Select title -> proposed AI text patch -> accept -> Undo | Only selected element changes, revision increments once, Undo restores prior content |
| E03 | Drag/resize a grouped chart, quote and shape | Stable IDs, data values and source references; no accidental sibling changes |
| E04 | Arabic headline with mixed English numbers/diacritics | Correct bidi and keyboard edit; no clipping at 1440×900 and 390×844 viewports |
| E05 | Save/reload and same deck open again | Same canonical digest, notes, order and IDs |
| E06 | Export native PPTX and inspect/import | Notes, bullet hierarchy, editable chart and table, explicit loss receipt |
| E07 | Owner A attempts to load/edit/export B deck | UI denial **plus database unchanged**, no leaked export file |
| E08 | Concurrent browser autosave and agent patch | Conflict or approved merge, no silent lost updates |
| E09 | Export canceled halfway through | No corrupt canonical slide, bounded retries and visible error |
| E10 | Offline / missing model provider | Deterministic test path, no attempt to send user content to vendor |
| E11 | Image/PDF fallback and animation static frame | No blank/overlap, correct explicit native downgrade |
| E12 | Windows desktop binary smoke (release phase) | App opens locally, export works, rollback and unsigned download warning truthful |

E12 may be a separate last-mile release gate. These tests do not require authorized Gamma or Beautiful.ai competitor accounts.

## Quality artifacts and accessibility

Each run records test ID, source SHA, frozen synthetic input SHA256, browser and Cypress versions, isolation manifest, console error summary, screenshot/video trace if available, export file SHA, OOXML inventory, exact pass/fail/skip, and cleanup receipt.

- Use role/name/data-testid selectors; avoid brittle pixel-coordinate clicks.
- Keyboard navigation and focus visible for source chooser, slide list, selected object, undo, export, dialogs; accessible names and contrast checks.
- Real screenshot diff and semantic/no-loss assertion are BOTH required: rasterized chart may look good but no longer be editable.
- Check unsupported native objects through structured loss receipt, not vague warnings.
- Test deliberately malformed source text and blocked network requests as negative controls.

**Acceptance:** E01–E11 run and pass on a test-only local backend; no authorization failure, silent data loss, missing source, unapproved network or broken actual native object. Missing browser binary/isolated DB => BLOCKED with exact dependency; never claim E2E passed based on the source plan alone.

**Hard stop:** real user session or file accessed, real account credentials reused, paid Cypress Cloud enabled without approval, testing on production database, skipped browser assertions, or screenshot-only object fidelity. **Rollback:** delete only the new E2E suite/config and test-owned scratch.
