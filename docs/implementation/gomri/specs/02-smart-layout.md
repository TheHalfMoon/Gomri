# S02 — Four SmartLayout Families, Without a Second Editor

**Goal:** Ship polished, responsive-internal 16:9 slide layouts that stay genuinely editable. **Owners:** R3 Editor/Layout, R1 Donor Auditor, R10 Product Judge. **Depends on:** S00 safety evidence and S01 role data for production use. **Initial slice is preview-only**, no persisted slide changes until S03 transaction safety.

## Why copy-first

Use existing Template V2/Konva and layout functions already present in:
- \`servers/nextjs/components/slide-editor/model/model.ts\` — \`updateComponentInUi\`, \`updateElementInUi\`, \`setComponentPositionsInUi\`, \`layoutChildren\`, \`resizeComponent\`. Inspect exact symbols and call signatures at checked-out SHA before changes.
- \`servers/nextjs/components/slide-editor/surface/TemplateV2KonvaSlide.tsx\`, \`componentFrameBounds.ts\`, \`alignmentGuides.ts\`.
- \`servers/nextjs/components/slide-editor/text/template-v2-text.ts\`, \`text-line-height.ts\`.
- Copy a **bounded, pinned reference/data utility** from TheHalfMoon/Skilit only if the existing editor cannot implement the design token/pattern role cheaply. Do not import Skilit PostgreSQL, worker, billing, entire component collection or app.
- Historical Crello \`font-metrics-sizing/index.js\` is read-only font arithmetic reference; do not edit third-party font binaries.
- Beautiful.ai 12×12 grid is **behavioral inspiration documented publicly**, not private implementation available for copying.

## Exact design contract

\`\`\`ts
type LayoutRole = 'headline-hero' | 'stat-chart' | 'comparison' | 'timeline-process';
type LayoutInput = {
  slideId: string; baseRevision: number; role: LayoutRole;
  components: ReadonlyArray<{componentId: string; kind: string;
    contentDigest: string; citationIds: readonly string[];
    semanticRole: string; isUserPositionOverride?: boolean}>;
  frame: {width: number; height: number};
  locale: 'ar' | 'en' | 'mixed';
};
type PreviewResult = {candidate: unknown; diagnostics: ReadonlyArray<{
  componentId?: string; severity: 'error'|'warning'; code: string
}>; preservedIds: readonly string[]; sourceDigest: string};
\`\`\`

This is an **illustrative interface to refine from live source types**, not a new persisted schema or claim the functions exist. All candidate layouts are pure derived projections; do not mutate input or change source/citation/chart facts.

## Implementation slices

1. **S02-a (no save):** one \`headline-hero\` 16:9 preview in an independent UI fixture. Compare direct composition of existing \`layoutChildren\` and frame bounds with a tiny adapter; do not build a generic constraint solver before proving necessity.
2. **S02-b:** \`stat-chart\` with native chart data/titles/labels, \`comparison\` with 2–4 balanced semantic cells and \`timeline-process\` with order/connector continuity.
3. **S02-c:** design tokens/brand references from Skilit after proven need; keep asset rights and user override policy.
4. **S02-d (requires S03):** transactionally apply selected layout preview, produce exact before/after diff, single Undo step, revision compare and explicit confirmation if intentional user positions change.

## Eight synthetic visual fixtures / acceptance

- Layout bounds: every semantic component remains present, anchored, inside slide safe area; no silent clipping or item loss.
- Mixed Arabic/English long title and diacritics: correct bidi, Unicode shaping, no overlapping chart or footer, no font patching.
- Dense data chart and multi-row table: content and underlying series/cells preserved exactly; if cannot fit, result is \`error:overflow\` with no mutation.
- Source/citation IDs and numeric values unchanged before/after every preview.
- Background image crop: preserve known focal point and photo license metadata; if unsupported, show manual review.
- Stable identity/digest no duplicates or cross-slide leakage.
- Undo/persist only enabled after S03 CAS tests pass; pre-S03 preview must not make network PATCH or auto-save calls.
- Visual comparison against **current Gomri baseline** on same 8 decks; R10 must explain composition choice without claiming Beautiful.ai superiority.

**Test homes:** existing \`servers/nextjs/tests/template-v2-component-bounds.test.mjs\`, text sizing/Arabic tests and separate \`tests/gomri-smart-layout.test.mjs\` only if justified by source. Cypress visual snapshot tests come under S05.

**Hard stop:** duplicate Konva editor or parallel canonical store, excessive new dependency, citation/number loss, unlicensed template, unknown license source, or ability to persist without S03 guard.

**Rollback:** feature flag off -> exactly original Template V2; no data migration before measured need. **Out of scope:** 85 formats, freeform full Canva editor, commercial stock, automatic SVG recreation.
