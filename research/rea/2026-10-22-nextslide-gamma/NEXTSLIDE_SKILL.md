# NEXTSLIDE_SKILL — the MIT donor, read line by line

**Donor:** `https://github.com/0xRafie/nextslide`
**Exact revision:** `90a46f933b3056d27460400c915ef268a9ec3f56`
**License:** MIT — `Copyright (c) 2026 Danish Rafie Ekaputra`
**Full line-by-line inventory:** `evidence/NEXTSLIDE_SKILL_SOURCE_INVENTORY.md` (484 lines)
**Probe run log:** `evidence/NEXTSLIDE_PROBE_RUNLOG.md`

---

## 1. What it actually is

A 13-file **skill** — markdown specifications plus two runnable scripts — that teaches an AI coding
agent to build self-contained HTML slide decks. It is not an application: there is no server, no
editor, no database, no build system. Its whole runtime is one HTML file with inlined CSS/JS.

```
README.md              9 877 B    entry docs
SKILL.md              15 838 B    the skill contract: how to author a deck
STYLE_PRESETS.md      21 309 B    18 presets, 19 CSS custom properties each
html-template.md      29 936 B    single-file HTML engine + JS controller + embedded JSON schema
animation-library.md  11 391 B    24 animations, easings, stagger, durations, reduced motion
typography-system.md   9 659 B    font selection criteria, preset↔font mapping
interactive-elements.md 17 162 B  10 widgets
presenter-mode.md      10 888 B    presenter window
viewport-base.css     12 583 B    13 layouts + core CSS + print styles
scripts/export-pptx.js 11 207 B   HTML → editable PPTX (PptxGenJS ^3.12.0), 414 lines
scripts/extract-pptx.py 14 688 B  PPTX → text/JSON (python-pptx + Pillow), 463 lines
LICENSE                1 078 B    MIT
```

Git history is 5 commits on `main`, oldest `f7a7220 feat: initial release — 18 style presets,
PDF/PPTX export, presenter mode, 24 animations`.

## 2. The issue's counts — reproduced, not assumed

Issue #77 §A.2 asserts "18 style presets, 13 layouts, 24 animations, a single-file HTML model,
presenter mode, PPTX import/extraction and editable PPTX export". Each was re-derived by
executable count, not by reading prose:

| Claim | Method | Result |
|---|---|---|
| 18 style presets | `grep -n '^## Preset ' STYLE_PRESETS.md` → 18 headings; corroborated by `grep -c '^:root {'` → **18** independent CSS blocks | **VERIFIED** |
| 13 layouts | `grep -o 'data-layout="[a-z-]*"' viewport-base.css \| sort -u` → **13** unique values; corroborated by 13 `### N. X Layout` headings and a 13-row table in `SKILL.md` | **VERIFIED** |
| 24 animations | `grep -n '^### [0-9]*\. animate-' animation-library.md` → **24** headings; #1–#20 under `## Entrance Animations`, #21–#24 under `## Emphasis Animations` | **VERIFIED** |
| 19 CSS custom properties per preset | `grep -o -- '--ns-[a-z0-9-]*' \| sort -u` → 19 unique | **VERIFIED** |
| Editable PPTX export | exported 4 real decks, then reopened them with `python-pptx` | **VERIFIED** — 23–28 text shapes per deck, 0–2 pictures |
| Test suite | repository inspection | **NONE** — the donor ships **no** test suite of its own |

## 3. Four real defects found by reading and running it

These are not style opinions. Each was reproduced.

### 3.1 `animate-counter-up` is permanently invisible — **the 24th animation is broken as shipped**

The donor's base rule sets `opacity: 0` on *every* `[class*="animate-"]` element. Animation #19
`animate-counter-up` has **no `@keyframes`** and is **not** in the emphasis exemption list, so no
rule ever restores its opacity. Measured in headless Chromium against a deck built from the
donor's own files:

```json
{ "animationName": "none", ... }
```

The donor's own JavaScript *does* update `textContent` from 0 → 73, but the element never becomes
visible. Visual proof: `evidence/probe/shot_midnight_counter_bug.png` — the "73%" value is simply
absent from the rendered slide.

**Gomrey's handling:** classified honestly as `engine: "controller"`, **no** keyframe block emitted,
`data-gs-count-target` documented as the controller contract, and `hidesUntilStart: false` so the
element is never hidden by a rule that nothing can undo. Guarded by a regression test.

### 3.2 The wildcard selector collides with Tailwind — a cross-product hazard

The donor's base rule is `[class*="animate-"] { opacity: 0; ... }`. Tailwind CSS v4 ships
`animate-spin`, `animate-pulse`, `animate-bounce` and `animate-ping`. Under the donor's rule, every
spinner and loading indicator in a Tailwind application is blanked to `opacity: 0`. The donor's own
`animate-pulse` emphasis animation also collides *by name* with the Tailwind utility.

The donor's `@media print` block repeats the same wildcard.

**Gomrey's handling:** `gs-anim-*` namespace, explicit enumerated selectors, no wildcard anywhere.
A regression test asserts the absence of `[class*=` and of any universal selector, and asserts that
no catalogued class collides with a Tailwind `animate-*` utility.

### 3.3 The interactive-element CSS is never inlined

`interactive-elements.md` documents 10 widgets with CSS blocks. But the documented pipeline
(`SKILL.md:126-142`) states the `<style>` block contains only 5 things: preset `:root` vars,
`viewport-base.css`, animation keyframes, `@media print` rules, and preset-specific styling. The
widget CSS is **not** among them.

**Consequence:** the donor's interactive elements do not work as shipped. Reproduced as the paired
screenshots `evidence/probe/shot_chart_UNSTYLED_per_SKILL.md.png` (per the documented pipeline) and
`evidence/probe/shot_chart_STYLED_with_interactive_CSS.png` (with the widget CSS actually applied).

### 3.4 The donor's PPTX extractor crashes on a pristine PPTX

Running `scripts/extract-pptx.py` unmodified against a PPTX produced by the donor's *own* exporter
aborts:

```
File "extract-pptx.py", line 281, in extract_presentation
    hasattr(shape, "placeholder_format")
ValueError: shape is not a placeholder
```

`python-pptx`'s `placeholder_format` property raises for non-placeholder shapes, and the donor
guards it with `hasattr`, which does not catch a property that raises. A minimally patched variant
still emits `⚠ Slide 4, shape 1: tuple index out of range`. Logs committed:
`evidence/probe/extract_pptx_PRISTINE_crash.log`, `extract_pptx_PATCHED_warnings.log`.

### 3.5 The donor's PPTX export produces **invalid chart XML**

`export-pptx.js:226` hard-codes the chart type as `'BAR'`; `pptxgenjs@3.12.0` expects `'bar'`. The
exported `ppt/charts/chart1.xml` therefore has a `plotArea` containing only `layout`, `catAx` and
`valAx` — **no `<c:barChart>`**. `python-pptx` raises `IndexError`; PowerPoint would prompt to
repair the file.

Text, shapes and speaker notes export correctly. **Charts do not.** Since charts are a first-class
Gomrey capability, this alone disqualifies the donor exporter.

### 3.6 The extractor silently loses all data

Even after the crash was patched so it could run, the extractor reported:

```
✓ Extracted 9 slides
✓ Found 0 elements        ← success exit code, zero data
```

A **silent total data loss** reported as success. It also loses all typography (paragraph-level
read vs run-level storage) and all original layouts.

### 3.7 The donor's own 18 presets fail its own contrast rule

`SKILL.md:276-341` specifies a 4.5:1 contrast requirement. **Nothing in the donor checks it.**
Measured across the 18 presets: **34 of 90 token pairs fail** in a wider matrix, and **10 of 54**
text-on-background pairs fail in the narrower subset this mission recomputed from the committed
fixture: `--ns-primary` (which drives real text) fails in **7** presets and `--ns-text-muted` in
**3**; the hard-coded KPI-change colours fail in 14 of 18 presets — 18 of 18 in the worst case.

This is simultaneously a **donor defect** and the **most valuable thing the donor contains for
Gomrey**: a ready-made, machine-checkable rule plus proof that a plausible palette set violates it
in 38 % of pairs. It lands directly on Gomrey's `F-P04` gap, where `smart_slide_layout.py` checks
overflow, clipping and overlap but **not contrast**. See wave `W4a`.

### 3.8 Additional inconsistencies (recorded, not adopted)

- `presenter-mode.md` and `html-template.md` describe **different presenter windows**.
- The `Bento Grid` preset advertises a "dashboard aesthetic" and instructs pairing with
  `data-layout="blank"` and custom grid CSS — there is **no bento layout** in the codebase.
- `STYLE_PRESETS.md` and `SKILL.md` publish **different** "use case → preset" tables (last row
  differs).
- The typography system defines **no measure (line-length) constraint** in `ch`/`em`; only
  `max-width: 75%` appears, which is viewport-relative and not typographically meaningful.
- Every preset ships a **Google Fonts `<link>`** — a hard network dependency that conflicts with
  Gomrey's offline-first default path. This is a primary reason style presets are `DEFER`, not
  adopted.

## 4. What the donor genuinely does well

- **The DOM contract is explicit.** `section.slide[data-layout="TYPE"]`, `.ns-current`,
  `.ns-total`, `slide-data` embedded JSON. A consumer can be written against it without guessing.
- **The embedded JSON schema is clean**:
  `slides: [ { layout, background: {color|image}, elements: [...], notes } ]`.
- **The JS controller is well-factored** — `goToSlide`, `triggerAnimations`, `resetAnimations`,
  `runCounterAnimations`, `updateCounter`, `syncPresenter`, `init` — with a hash-based deep link
  and a progress bar.
- **Print styles are considered** (`@page { size: landscape; margin: 0 }`, per-slide page breaks,
  `print-color-adjust: exact`).
- **Reduced motion is treated as a first-class concern**, not an afterthought.
- **Anti-patterns are documented** — max 3 animated elements per slide, consistent animation type
  per slide, no animated backgrounds, ≤800 ms durations, always stagger lists.

## 5. Disposition

| Component | Disposition | Reason |
|---|---|---|
| `animation-library.md` | **ADAPTED** (Wave 1) | Fills a verified Gomrey gap; 24 animations preserved; 7 documented adaptations; 28 tests |
| `STYLE_PRESETS.md` | DEFER | Google Fonts network dependency; the "preset" abstraction is CSS while Gomrey's is a typed token model |
| `viewport-base.css` (13 layouts) | DEFER | Gomrey has 400+ layouts across 16 templates; must be compared per-layout, not adopted wholesale |
| `html-template.md` | DEFER | Parallel-engine risk; only the *self-contained artifact* capability (`F-E06`) is worth taking |
| `interactive-elements.md` | DEFER | **Broken in the donor** (§3.3); each widget needs individual comparison |
| `presenter-mode.md` | REJECT | Gomrey already owns presenter mode |
| `typography-system.md` | DEFER | Needs a measured comparison against Gomrey's own text layout |
| `scripts/export-pptx.js` | REJECT | Parallel PPTX engine; Gomrey owns `@presenton/export-core` |
| `scripts/extract-pptx.py` | REJECT | Gomrey's importer is superior; donor's crashes (§3.4) |

**The donor is worth studying. It is not worth copying.** What Gomrey took was the *motion design*,
not the *architecture*.
