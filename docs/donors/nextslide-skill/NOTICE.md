# NOTICE — NextSlide OpenCode slide skill (animation contract donor)

**Adopted by:** Gomrey (`TheHalfMoon/Gomrey`)
**Adoption mode:** `ADAPT` (see `docs/SOURCE_LEDGER.md` §1)
**Scope of this record:** the slide-animation contract only.
**Date of record (UTC):** 2026-10-22

---

## 1. Source identity

| Field | Value |
|---|---|
| `source_name` | NextSlide OpenCode slide skill |
| `source_repository_or_archive` | `https://github.com/0xRafie/nextslide` |
| `exact_revision_or_digest` | `90a46f933b3056d27460400c915ef268a9ec3f56` |
| `source_paths` | `animation-library.md` (487 lines; blob `a3484b2ae4c13c7a2139e2ed2588f5e58344902c`) |
| `public_license` | MIT |
| `separate_permission_basis_if_used` | Founder attestation recorded in `research/rea/2026-10-22-nextslide-gamma/SOURCES.md` §0. Not required for this donor — the upstream license already permits reuse. |
| `embedded/transitive code/assets/models` | None in the adopted slice. The animation contract is CSS and prose only; it imports nothing and bundles no asset. |
| `model_weight_tokenizer_runtime_rights` | Not applicable — no model, tokenizer or runtime artifact is adopted. |
| `training_evaluation_dataset_rights` | Not applicable — no dataset is adopted. |
| `font_icon_media_template_brand_rights` | Not applicable — the adopted slice references no font, icon, media, template or brand asset. |
| `generated_output_redistribution_or_publication_restrictions` | None beyond the MIT terms of the adopted code. Generated decks carry no donor restriction. |
| `notices/attribution` | This file plus `docs/donors/nextslide-skill/LICENSE` (verbatim upstream MIT text) and the in-file header of each adopted source file. |

## 2. Donor copyright and license

The MIT license requires that the copyright notice and permission notice accompany
copies or substantial portions of the software. The upstream license is
reproduced verbatim at `docs/donors/nextslide-skill/LICENSE`
(sha256 `e8aa250f23393942b2c952d0c45109926b1bffc6e5e9b3d6a3f09abe691bd7a9`,
identical to the upstream file).

```
MIT License

Copyright (c) 2026 Danish Rafie Ekaputra
```

The upstream project README is preserved at
`docs/donors/nextslide-skill/UPSTREAM_README.md`.

## 3. Gomrey target modules and adoption mode

| Field | Value |
|---|---|
| `Gomrey_target_module` | `servers/nextjs/lib/slide-animations/catalog.ts`, `servers/nextjs/lib/slide-animations/stylesheet.ts`, `servers/nextjs/lib/slide-animations/index.ts` |
| `adoption_mode` | `ADAPT` — donor behaviour preserved behind a Gomrey-owned, namespaced contract |
| `why_reuse_beats_native` | The donor ships a complete, hand-tuned 24-animation catalog (20 entrance + 4 emphasis) with curated easing curves, stagger steps, duration modifiers and a reduced-motion policy. Recreating that tuning from scratch would be slower and would produce a worse result. Gomrey owns the contract and the namespace; the donor supplied the motion design. |
| `security/trust placement` | Pure data and pure string generation. No DOM access, no network access, no filesystem access, no credential access, no `eval`, no dynamic `import()`. The generated stylesheet is asserted to contain no `@import`, no `url(...)` and no URL. |
| `network/filesystem/credential capabilities` | None. |
| `tests/benchmarks` | `servers/nextjs/tests/slide-animations.test.mjs` — 28 deterministic assertions covering catalog shape, namespace isolation, Tailwind collision avoidance, stylesheet determinism, absence of wildcard selectors and external references, activation-mode behaviour, reduced-motion coverage and controller-honesty. |
| `update_strategy` | Pin the upstream revision in this file and in the source header. Re-derive the catalog when the upstream revision changes; diff the catalog in review. |
| `rollback/exit_strategy` | Delete `servers/nextjs/lib/slide-animations/` and `servers/nextjs/tests/slide-animations.test.mjs`. The module has no runtime dependency and is not yet wired into a rendering surface, so removal is a no-op for product behaviour. |
| `review evidence` | See `research/rea/2026-10-22-nextslide-gamma/STATUS.md` and the PR for the exact candidate commit, Jev record and OCR deterministic selection record. |

## 4. Modifications made to the donor material

The adopted slice was **adapted, not copied verbatim**. Every change below is
deliberate and each one exists to protect Gomrey.

### 4.1 Namespace re-binding

| Donor | Gomrey |
|---|---|
| class `animate-<id>` | class `gs-anim-<id>` |
| keyframe `ns-<id>` | keyframe `gs-keyframe-<id>` |
| easing variable `--ns-ease-<name>` | `--gs-ease-<name>` |
| path length `--ns-path-length` | `--gs-path-length` |
| delay utility `delay-<ms>` | `gs-delay-<ms>` |
| duration utility `duration-<key>` | `gs-duration-<key>` |

**Reason.** The donor's base rule is a wildcard attribute selector:

```css
[class*="animate-"] { opacity: 0; animation-duration: 500ms; ... }
```

Gomrey uses Tailwind CSS v4, which ships `animate-spin`, `animate-pulse`,
`animate-bounce` and `animate-ping` utilities. The donor's wildcard selector
matches those utilities and blanks every spinner, pulse and loading indicator in
the product to `opacity: 0`. The donor's own `animate-pulse` emphasis animation
also collides by name with the Tailwind utility of the same name. A dedicated
namespace removes both failure modes permanently.

This is a correctness fix, not a cosmetic preference.

### 4.2 Wildcard selectors removed

The donor's `[class*="animate-"]` and `.slide:not(.active) [class*="animate-"]`
rules are replaced by explicitly enumerated Gomrey class lists. Every generated
rule targets a named Gomrey class, so the animation contract cannot affect
unrelated product UI even if the stylesheet is injected globally.

### 4.3 Surface-agnostic activation

The donor gates playback on a `.slide.active` DOM contract that does not exist in
Gomrey, whose presentation surface is a Konva canvas plus a separate DOM/HTML
renderer. Gomrey exposes two explicit modes instead:

| Mode | Behaviour | Intended use |
|---|---|---|
| `auto` | animations play as soon as the element renders | self-contained HTML export |
| `gated` | animations play only inside `[data-gs-slide-active="true"]` | presenter-style surfaces that show one slide at a time |

### 4.4 Reduced motion scoped

The donor's reduced-motion block uses a universal `*` selector with
`!important`. Injected into the Gomrey application it would freeze unrelated
product chrome. Gomrey scopes the block to the enumerated Gomrey animation
classes, additionally restores `opacity: 1` for hidden elements, forces
`animation-iteration-count: 1` so looping emphasis animations stop, and resets
`stroke-dashoffset` for the SVG line-reveal animation.

### 4.5 Honest engine classification

The donor's `animate-counter-up` is **not a CSS animation**. Upstream documents
it as a marker class driven by a JavaScript controller in the donor's HTML
template. Gomrey classifies it as `engine: "controller"`, emits **no** keyframe
block for it, exposes its data-attribute contract (`data-gs-count-target`), and
never hides the element — a hidden element with no keyframe to reveal it would
be permanently invisible.

The donor's `animate-draw-line` requires a measured SVG path length. Gomrey
exposes this as a declared `requiredCustomProperty` (`--gs-path-length`) with
the donor's safe fallback value, rather than hiding the dependency.

### 4.6 Easing set extended

The donor's four named curves do not cover every animation it ships: `pulse`,
`glow` and `float` use `ease-in-out`, `shimmer` uses `linear`, and `typewriter`
uses `steps(40, end)`. Collapsing these into the four named curves would change
the donor's visual behaviour, so all three are retained as first-class easing
ids.

### 4.7 Behaviour preserved

The following are preserved exactly from the donor because they are the motion
design itself:

- all 24 keyframe bodies (`from`/`to`/`0%`/`50%`/`60%`/`70%`/`100%` steps),
  with only the keyframe *identifier* renamed;
- the four easing curves;
- the eight stagger delays (100–1000 ms) and three duration modifiers
  (300/500/800 ms);
- per-animation defaults for duration, easing, iteration count and
  `transform-origin`;
- the reduced-motion *intent* (stop movement, restore visibility, stop loops).

## 5. What was deliberately **not** adopted from this donor

| Donor artefact | Disposition | Reason |
|---|---|---|
| `scripts/export-pptx.js` (PptxGenJS) | **REJECT — not adopted** | Gomrey's export path is owned by `@presenton/export-core` v1.0.34 and already produces PPTX/PDF. Adopting a second PPTX engine would create a parallel exporter, which issue #77 §D forbids without bounded fidelity proof. |
| `scripts/extract-pptx.py` | **REJECT — already superseded** | Gomrey's `services/export_task_service.py` PPTX→JSON importer and `templates/pptx_font_utils.py` (1 668 lines) already exceed the donor's extractor. |
| `STYLE_PRESETS.md` | **DEFER** | Gomrey has 16 bundled templates with derived themes but no named style presets. This is a real gap, but presets must land inside Gomrey's template/theme model, not as a parallel preset system. Tracked as a separate grain. |
| `html-template.md` | **DEFER** | Gomrey already owns `lib/template-v2-json-to-html.ts`. A second HTML engine is a parallel stack. |
| `presenter-mode.md` | **ALREADY_PRESENT** | Gomrey owns `app/(presentation-generator)/presentation/components/PresentationMode.tsx`. |
| `typography-system.md`, `interactive-elements.md`, `viewport-base.css` | **DEFER** | Each must first be compared against Gomrey's existing typography, editor and canvas systems to avoid duplication. |

## 6. Verified upstream claim

Issue #77 §A.2 states the donor provides "18 style presets, 13 layouts, 24
animations". The **24 animations** figure is verified directly from the source
at revision `90a46f9`: 20 entrance animations (`fade-up` … `draw-line`) and 4
emphasis animations (`pulse`, `glow`, `float`, `shimmer`). The style-preset and
layout counts are not asserted by this record because they are not part of the
adopted slice; they are measured separately in
`research/rea/2026-10-22-nextslide-gamma/evidence/NEXTSLIDE_SKILL_SOURCE_INVENTORY.md`.
