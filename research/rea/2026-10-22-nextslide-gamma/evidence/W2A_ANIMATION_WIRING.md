# W2a — animation field on the slide model + HTML renderer wiring

**Mission:** Issue #77, wave `W2a`.
**Branch:** `feature/rea/w2a-animation-wiring`
**Base:** `feature/rea/nextslide-gamma-wave1` (PR #78) — **W2a depends on wave 1**, because the
animation catalog, the stylesheet generator and the class-name contract all live in
`servers/nextjs/lib/slide-animations/`, which wave 1 introduced.
**Date (UTC):** 2026-10-22

---

## 1. What this grain delivers

Wave 1 delivered the **animation contract** (a surface-agnostic catalog plus deterministic
stylesheet generation) with 28 tests, but nothing could *use* it: no slide could declare an
animation, and no renderer emitted one. W2a closes that loop.

| Layer | Change |
|---|---|
| Slide element model | `ElementAnimation` on the animatable element types |
| Template | a template declares the animation per element; it survives template parsing |
| LLM | the layout-generating and content-generating models never see the field |
| HTML renderer | the animation class is emitted and the stylesheet is inlined |

## 2. Files

| File | Change | Lines |
|---|---|---|
| `servers/fastapi/templates/v2/models/elements.py` | **modified** — `ElementAnimation` model; `animation` field on Text, TextList, Table, Vector, Chart, Infographic, Image | +30 |
| `servers/fastapi/templates/v2/models/layouts.py` | **modified** — strip `animation` from the LLM layout schema; prune the orphaned `$defs` entry | +50 |
| `servers/nextjs/lib/template-v2-json-to-html.ts` | **modified** — emit the animation class; inline the animation stylesheet | +110 |
| `servers/fastapi/tests/test_slide_animation_model.py` | **added** — 10 tests | +175 |
| `servers/nextjs/tests/slide-animations-rendering.test.mjs` | **added** — 10 tests | +220 |

## 3. Design decisions

### 3.1 The animation is a template-authoring decision, never a model decision

Three independent mechanisms enforce that, because each one fails silently on its own:

1. **The content schema is built from a per-type whitelist.** `templates/v2/schema.py::_content_schema_for_element`
   returns a *fixed* schema per element type (text → a string, image → `image_prompt`, table → a
   matrix of strings). It never copies element fields. A template element carrying `animation`
   therefore cannot leak it into the content schema.
2. **The layout-generation schema is stripped explicitly.** `slide_layout_llm_json_schema()` now
   removes `animation` with the existing `remove_fields_from_schema` helper, and prunes the
   `$defs` entry that removal orphans.
3. **The template application keeps the template's value.** `_apply_template_content_to_ui`
   deep-copies the template element and replaces only the content fields, so a model-supplied
   animation could never win — and could never be applied in the first place, because of (1).

### 3.2 The field is declared on the element model, or it is silently dropped

`RawSlideLayout` / `Component` parse the template's elements as `SlideElement`, and pydantic's
default is to **ignore** extra fields. Had the animation been added only to the renderer, the
template's animation would have been dropped at parse time with no error. Declaring
`ElementAnimation` on the element model is what makes the field survive. There is a regression
test for exactly this.

### 3.3 Structural containers are not animatable

`container`, `flex`, `grid` and `group` are deliberately excluded. The donor's own guidance is
that a container is never the animated element — only its contents are. Animating a container
would also move every child at once and defeat the per-element stagger.

### 3.4 The catalog is not duplicated in Python

`ElementAnimation.name` is a free string, not an enum. The catalog lives in exactly one place —
`servers/nextjs/lib/slide-animations/catalog.ts` — and the renderer ignores an unknown id
rather than emitting a broken animation. A second copy of the id list in Python would be a
second source of truth that could drift.

## 4. What the renderer does

- `renderItem` now dispatches through `renderItemByType` and then applies the animation class to
  the **root element** of the rendered fragment. Because `renderItem` is also the recursion point
  for children, nested elements carry their own animation.
- If the root element already has a `class` attribute, the animation class is **merged** into it.
  A second `class` attribute would be silently dropped by the browser, which would have made the
  animation disappear without any error.
- The stylesheet is inlined **only when the deck actually uses an animation**, so a deck without
  animations carries no animation CSS.
- `mode: "auto"` is used: the animation runs on load rather than waiting for a
  `data-gs-slide-active` gate. The gated mode belongs to an interactive player, not to a rendered
  slide.

## 5. Honest limitation — the canvas and the export do not run animations

The HTML renderer is the **preview** surface. The editor surface and the PPTX/PDF export path
render through the **Konva canvas** (`TemplateV2KonvaSlide.tsx`, reached from
`app/(export)/pdf-maker`), where a CSS class has no effect.

So the capability delivered by W2a is:

| Surface | Animations |
|---|---|
| Template preview (HTML renderer) | **run** |
| Editor surface (Konva canvas) | **do not run** |
| PPTX export | **do not run** |
| PDF export | **do not run** |

This is stated rather than hidden. A canvas animation needs a **controller** that drives the
Konva node properties over time — the wave-1 catalog already anticipates this with
`SlideAnimationEngine = "css" | "controller"`, and the `controller`-engine animations
(`typewriter`, `counter-up`, `draw-line`) need exactly that controller. The controller is **not**
part of W2a and is not claimed to be.

The HTML renderer is also the natural place for the CSS engine's animations to land first,
because the stylesheet is already surface-agnostic by construction.

## 6. The `controller` engine is not claimed

Three catalog animations are `engine: "controller"`: `typewriter`, `counter-up` and `draw-line`.
The wave-1 stylesheet emits their supporting declarations, but the driving behaviour is not part
of the module and is never claimed to be. W2a does not change that: those ids produce their class
and their declarations, and the behaviour that would actually animate them is still absent.

## 7. Bugs the tests caught

| Bug | Severity | Fix |
|---|---|---|
| The template's `runs` were not being replaced in the first draft of the test — the content lookup is `content[component_id][element_name]`, not `content[element_name]`. | Test defect | The test now uses the shape the repo's own `tests/unit/test_template_image_targets.py` uses. |
| `remove_fields_from_schema` removed the `animation` **property** but left the `ElementAnimation` `$defs` entry and its description behind. | Low — harmless, but an unreferenced definition invites the belief that the field is still reachable | `_prune_unreferenced_defs` drops definitions nothing references any more. |
| A root element that already had a `class` attribute would have received a **second** `class` attribute, which browsers silently ignore — the animation would vanish with no error. | **High** — silent failure | The class is merged into the existing attribute, and a test asserts that no element carries two `class` attributes. |

## 8. Gate results on this revision

| Gate | Command | Result |
|---|---|---|
| FastAPI | `uv run --locked python -m pytest -q` | **1135 passed** (1125 baseline + 10 new) |
| Repository tooling | `npm test` | **48 pass / 0 fail** |
| Next.js unit | `npm test` | **111 pass / 0 fail** (101 wave-1 baseline + 10 new) |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |

Note: the counts differ from the W3 branch because this branch is stacked on wave 1, which does
not carry W3's four contract tests.

## 9. Open items

| Item | State |
|---|---|
| The Konva canvas controller | **Not delivered.** Required for the editor surface, the PPTX export and the PDF export. |
| The `controller`-engine animations (`typewriter`, `counter-up`, `draw-line`) | **Not delivered.** They need a runtime controller. |
| Per-slide animation ordering / a timeline | **Not delivered.** The model carries a per-element delay only; there is no slide-level sequence. |
| A template that actually uses an animation | **Not delivered.** The capability is proven by tests, not by a shipped template. |
| Arabic / RTL | Not covered — wave `W13`. |
