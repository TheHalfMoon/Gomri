# ARCHITECTURE_DELTA — what must change, and why

**Mission:** Issue #77.
**Baseline:** `5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Delta date (UTC):** 2026-10-22

---

## 0. The governing conclusion

Gomrey's competitive position is **not** limited by its editor, exporter, or evidence engine — all
three are complete and qualified. It is limited by three things:

1. **Nothing is wired end to end.** P08/P09 evidence, citation and verification modules exist and
   pass their tests, but the presentation pipeline never calls them. Gomrey can *prove* a claim
   and can *make* a deck, and it cannot yet do both in one artifact.
2. **The artifact IR is flat.** `narrative-ir` models a document, not a deck of cards/pages. The
   studio surface (Presentation / Document / Website / Visual) therefore has no shared spine.
3. **Design intent is not machine-selectable.** Themes are derived from templates; there is no
   named preset layer, no brand kit, and no way to select a style by intent.

Everything below follows from those three.

---

## 1. Target architecture — one spine, six studios

```
                    ┌──────────────────────────────────────────┐
                    │        Artifact IR  (contracts/v1)        │
                    │  narrative · design · citations ·        │
                    │  provenance · slides/cards/pages         │
                    └──────────────────┬───────────────────────┘
                                       │
        ┌──────────────┬───────────────┼───────────────┬──────────────┐
        │              │               │               │              │
   ┌────▼────┐  ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐ ┌─────▼─────┐
   │Research │  │ Presentation│  │ Document  │  │   Website   │ │   Visual   │
   │ Studio  │  │   Studio    │  │  Studio   │  │   Studio    │ │   Studio   │
   └────┬────┘  └──────┬──────┘  └─────┬─────┘  └──────┬──────┘ └─────┬─────┘
        │              │               │               │              │
        └──────────────┴───────────────┴───────────────┴──────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │   Evidence / Claim / Verification     │  ← P08/P09, already built
                    │   (gomrey/retrieval, citations,        │     and currently UNWIRED
                    │    claims, verification, decisions)    │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │   Export Engine  (@presenton/export-  │
                    │   core) · Design System · AI Editing  │
                    └──────────────────────────────────────┘
```

**The point:** the six studios are *surfaces* over one IR, one design system and one evidence
authority. They are not six applications. Gamma's editor is one surface; Gomrey needs six surfaces
over a spine Gamma does not have — and Gamma's own product source is unavailable, so the spine must
be built from Gomrey's existing contracts.

## 2. Delta 1 — wire the evidence fabric into artifact production (highest value)

**Problem.** `servers/fastapi/gomrey/` contains a complete retrieval → citation → claim →
verification → decision pipeline. The presentation pipeline never calls it.

**Delta.**

| Change | File | Nature |
|---|---|---|
| New narrative producer that emits `NarrativeIR` from an `EvidenceBundle`, carrying `claim_ids`, unresolved claims, conflicts, omission state and abstention | new `servers/fastapi/gomrey/narrative.py` | new module |
| Hook the producer into the outline stage | `utils/llm_calls/generate_presentation_outlines.py` | call site |
| Add per-slide citation locators to the artifact schema | `contracts/v1/narrative-ir.schema.json` | schema extension |
| Deterministic test: an unresolved claim produces an abstention marker, never a fabricated citation | `servers/fastapi/tests/unit/` | new test |

**Invariants preserved.** `gomrey/verification.py` semantics are untouched: the provider cannot
overrule a deterministic number/date/unit/entity gate; `claims.py` binding is untouched; `ABSTAIN`
stays reachable. No artifact may contain a citation that `citations.py` cannot resolve — the
`BrokenCitation` guard becomes an export-time assertion.

**Why no donor code.** This is entirely in-repo. It is the highest-leverage change available.

## 3. Delta 2 — multi-node artifact IR

**Problem.** `narrative-ir.schema.json` `sections[]` is flat; `design-ir` `layout` is one string.
There is no way to express a deck, a paginated document, a multi-page site, or a card grid.

**Delta.** Introduce an explicit node list with a typed discriminated union:

```jsonc
{
  "nodes": [
    { "kind": "slide", "id": "s1", "layout": "title-hero",
      "elements": [ /* … */ ], "citations": [ /* locators */ ] },
    { "kind": "page",  "id": "p1", "path": "pricing",
      "blocks": [ /* … */ ] }
  ]
}
```

`layout` becomes a **per-node** property of a layout plan, not a document-level string.

**Migration discipline.** `contracts/v1/` has 23 schemas and a `manifest.json`. The change must be
additive with a schema version bump, and the existing single-document form must keep validating
until the producer migrates. `scripts/validate-contracts.mjs` and `scripts/contracts.test.mjs` are
the gates.

**Gamma signal.** Gamma's `generate_multi_page_gamma` produces 1–50 pages with a per-page `path`
slug, a deep link and its own id, in one request. That is exactly the node model above, and it is
the shape a "sales room" or "proposal site" needs.

## 4. Delta 3 — design intent becomes machine-selectable

**Problem.** A theme is derived from a template. There is no layer that answers *"give me a deck
that feels like X"*.

**Delta.** Two additions, both extending the existing token model rather than replacing it:

**(a) Named style presets.** A preset becomes a typed token set in `templates/v2/theme.py`, resolved
to the same 16 semantic colours and the same font/spacing scale the renderer already consumes.
The donor's 18 presets are a **reference**, not a source of truth: they ship Google Fonts `<link>`
network dependencies and a CSS-variable representation that does not match Gomrey's typed model.

**(b) Machine-matchable intent keywords.** Gamma's `get_themes` returns `colorKeywords[]` and
`toneKeywords[]` alongside `name`. A theme that can only be browsed by name is a gallery; a theme
that can be *selected by intent* is an API. Gamma's theme library is per-file since Gamma 5,
decoupled from the workspace — a useful separation, because theme choice is a property of the
artifact, not of the account.

**(c) Brand kit** (`F-P07`) is a separate, later delta and **requires an asset-rights decision
first**: a brand kit carries logos and fonts that are *not* covered by a code licence. The
`SOURCE_LEDGER.md` §7 rule applies — code permission ≠ asset permission.

## 5. Delta 4 — one token source across three rendering surfaces

**Problem.** Three surfaces read design values independently:
`surface/nodes.tsx` (Konva editor), `custom-template/components/EachSlide/TemplateV2LayoutPreview.tsx`
(DOM preview) and `lib/template-v2-json-to-html.ts` (HTML export).

**Delta.** A single resolved design-token object, computed once from `design-ir` + theme + preset,
consumed by all three. This is a prerequisite for W4 (presets), W7 (offline HTML artifact) and any
visual-fidelity claim, because it removes the possibility that a preset renders differently in the
editor than in the export.

## 6. Delta 5 — the animation contract reaches a surface

**Wave 1 delivered the contract. It is not yet wired.** Delta 5 is small:

| Change | File |
|---|---|
| Add an `animation` field to the slide/node element schema | `servers/fastapi/templates/v2/models/elements.py`, `contracts/v1/` |
| Emit the animation class attribute in the HTML renderer | `servers/nextjs/lib/template-v2-json-to-html.ts` |
| Inline the generated stylesheet in the exported artifact | same |
| Surface the animation control in the editor | `servers/nextjs/components/slide-editor/` |
| Map the DOM activation attribute for presenter surfaces | `PresentationMode.tsx` |

**Konva note.** The editor is a canvas, so CSS animation classes do not apply there. The editor
needs a Konva-side equivalent (Konva `Tween`), driven by the **same catalog** so the two surfaces
cannot drift. The catalog is the contract; each surface renders it natively.

## 7. Delta 6 — export fidelity as a first-class, tested property

**Problem.** No export→import round-trip suite exists. Gamma — which ships an internal
`import-grader-annotator` with a 24-mode failure taxonomy — treats import fidelity as a graded
engineering problem. Gamma's own docs admit that exported tables lose rounded corners, and that
fonts are substituted on import.

**Delta.** A versioned fidelity harness:

| Component | Purpose |
|---|---|
| `fidelity/cases/*.json` | synthetic decks exercising tables, vectors, charts, RTL, mixed script, media, overflow |
| `fidelity/expectations/*.json` | per-case expected properties (text present, vector type, table cell count, no rasterisation) |
| `fidelity/runner` | export → reopen → assert → report JSON+CSV |
| `fidelity/taxonomy` | versioned failure-mode taxonomy (mirrors the `import-grader-annotator` *pattern*, not its code — that repository is Gamma-internal QA tooling, not a permissively licensed product dependency) |

This is the closest available substitute for Gamma's internal QA tooling and it closes
`F-E09`, `F-I02` and the issue §F acceptance gate for export fidelity.

## 8. Delta 7 — Arabic, RTL and mixed-script qualification

**Problem.** No measured Arabic/RTL qualification exists in Gomrey **or** in either donor. The
donor's typography system defines no measure in `ch`/`em`; Gamma's language list includes `ar` and
`ar-sa` but its layout behaviour for RTL is not documented and its editor source is unavailable.

**Delta.** A qualification suite first — measure before building. Cases: pure Arabic, pure English,
mixed Arabic/English in one paragraph, Arabic with Latin numerals, Arabic inside a table, Arabic
inside a chart label, Arabic in a vector shape, and Arabic in an exported PPTX. Each case asserts:
logical-direction correctness, correct font fallback, no glyph loss, no overflow, and correct
export.

**Design signal from Gamma:** its output-language identifiers pair a base locale with a **register**
(`ar` / `ar-sa`, `ja` / `ja-da`, `en` / `en-gb` / `en-in`). A language+register model is more useful
than a bare ISO-639 list, and it maps directly onto an Arabic-first product.

## 9. What is explicitly *not* changing

| Not changing | Why |
|---|---|
| The Konva canvas editor | Complete and qualified; a second renderer is a parallel stack |
| `@presenton/export-core` | Canonical export path |
| `utils/llm_provider.py` | Canonical provider seam |
| `gomrey/verification.py` semantics | P09 semantics are preserved, not rewritten |
| `PRESENTATION_GENERATION_MODE` | Canonical switch; not an authz control |
| The 16 bundled templates | Preserve; extend with a preset layer above them |
| `contracts/v1/artifact_type` enum | Preserve; the seven types are correct, only their runtime producers are missing |

## 10. Delta-to-gap map

| Delta | Closes / advances |
|---|---|
| 1 — evidence wired into artifacts | `F-R07`, `F-R08`, `F-R09` |
| 2 — multi-node IR | `F-C01`, `F-C02`, `F-S04` |
| 3 — machine-selectable design intent | `F-P06`, `F-P07` |
| 4 — single token source | `F-C07`, `F-C08` |
| 5 — animation reaches a surface | `F-P08`, `F-P09`, `F-P10` |
| 6 — export fidelity harness | `F-E05`, `F-E09`, `F-I02` |
| 7 — Arabic/RTL qualification | `F-C09`, `F-E10` |

Every delta either extends an existing canonical module or adds one clearly-named new module.
None introduces a parallel stack, a second authority, or a second identity.
