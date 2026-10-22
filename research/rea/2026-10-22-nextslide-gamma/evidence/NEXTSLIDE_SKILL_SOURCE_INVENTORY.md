# NEXTSLIDE — SOURCE INVENTORY & ISSUE-CLAIM VERIFICATION

**Donor:** https://github.com/0xRafie/nextslide
**Revision (exact):** `90a46f933b3056d27460400c915ef268a9ec3f56`
**Commit message:** `README: update GitHub username to 0xRafie`
**License:** MIT, `Copyright (c) 2026 Danish Rafie Ekaputra`
**Local clone (read-only):** `/Users/abdulazizalsh/work/donor-nextslide`
**Probed:** 2026-10-22
**Method:** every file read line-by-line; counts re-derived by executable grep/python commands; runtime behaviour verified in headless Chromium 156.0.8078.4.

---

## 0. Repository shape — complete file list (14 files, entire git history)

`git log --all --diff-filter=A --name-only --pretty=format: | sort -u` returns exactly these 14 paths.
**No file has ever been added and removed.** There are no tags, no branches other than `main`, no CI config, no test file, no example deck, no HTML template *file*.

| Path | Bytes | Lines | Kind |
|---|---|---|---|
| `SKILL.md` | 15838 | 407 | Prompt/workflow spec |
| `STYLE_PRESETS.md` | 21309 | 817 | 18 preset token blocks |
| `html-template.md` | 29936 | 946 | HTML boilerplate + JS controller + JSON schema |
| `animation-library.md` | 11391 | 487 | 24 animation definitions |
| `typography-system.md` | 9659 | 255 | Font pairing rationale + size scale |
| `interactive-elements.md` | 17162 | 730 | Chart/timeline/code/KPI CSS + HTML |
| `presenter-mode.md` | 10888 | 458 | Presenter window spec |
| `viewport-base.css` | 12583 | 663 | Core CSS (the only real CSS asset) |
| `README.md` | 9877 | 243 | Docs |
| `LICENSE` | 1078 | 21 | MIT |
| `.gitignore` | 226 | 26 | — |
| `scripts/export-pptx.js` | 11207 | 414 | Node CLI: HTML → PPTX |
| `scripts/extract-pptx.py` | 14688 | 463 | Python CLI: PPTX → text/JSON |
| `scripts/package.json` | 253 | 12 | `pptxgenjs ^3.12.0` |

Git history: 5 commits, all on `main`, oldest = `f7a7220 feat: initial release — 18 style presets, PDF/PPTX export, presenter mode, 24 animations`.

**Everything except `viewport-base.css`, `scripts/export-pptx.js` and `scripts/extract-pptx.py` is Markdown prose.** The "code" of this project is 3 files: 663 lines of CSS, 414 lines of JS, 463 lines of Python.

---

## 1. `STYLE_PRESETS.md` — the 18 presets

**Count method:** `grep -n '^## Preset ' STYLE_PRESETS.md` → 18 headings (lines 40, 86, 128, 170, 212, 254, 296, 338, 382, 424, 466, 508, 550, 592, 634, 676, 718, 760). Corroborated by `grep -c '^:root {' STYLE_PRESETS.md` → **18** CSS blocks (one per preset, each independently complete), and by the Quick-Reference table at lines 17–36.

**Token set:** every preset defines exactly **19 CSS custom properties**, all prefixed `--ns-`:

```
--ns-bg  --ns-bg-alt  --ns-text  --ns-text-muted  --ns-primary  --ns-secondary  --ns-accent
--ns-font-heading  --ns-font-body  --ns-font-mono
--ns-heading-weight  --ns-body-weight
--ns-space-xs  --ns-space-sm  --ns-space-md  --ns-space-lg  --ns-space-xl  --ns-space-2xl
--ns-slide-padding  --ns-border-radius
```

Derived by `grep -o -- '--ns-[a-z0-9-]*' STYLE_PRESETS.md | sort -u` (19 unique). Note the SKILL.md "CSS Variable System" (§`SKILL.md:179-209`) documents the same 19 but its `--ns-space-*` values are illustrative; the authoritative values are per-preset.

**Spacing is identical across all 18** (8/16/24/32/48/64, `--ns-slide-padding: 48px 64px`). Only `--ns-border-radius` varies: 4px (Editorial, Classic Luxe, Photo Noir), 6px (Data Story), 8px (Minimal Clean, Corporate Pro, Pitch Deck, Bold Geometric, Asymmetric, Retro 90s, Botanical, Creative Studio, Midnight Pro), 12px (Teal Serenity, Bento Grid, Prism Glow), 16px (Soft Curves, Playful Pop).

### 1.1 Full per-preset token tables (values + source line ranges)

| # | Name | :root lines | bg | bg-alt | text | text-muted | primary | secondary | accent | heading | body | mono | h-w | b-w | radius | Category |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Minimal Clean | 47–75 | `#ffffff` | `#f8fafc` | `#1a1a2e` | `#64748b` | `#3b82f6` | `#94a3b8` | `#f59e0b` | Space Grotesk 600 | Source Sans 3 400 | JetBrains Mono | 600 | 400 | 8px | Light |
| 2 | Corporate Pro | 93–117 | `#ffffff` | `#f1f5f9` | `#1e293b` | `#475569` | `#2563eb` | `#475569` | `#dc2626` | Sora 700 | Inter 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 3 | Pitch Deck | 135–159 | `#0f172a` | `#1e293b` | `#f8fafc` | `#94a3b8` | `#22c55e` | `#64748b` | `#f97316` | Archivo Black 400 | Archivo 400 | JetBrains Mono | 400 | 400 | 8px | **Dark** |
| 4 | Bold Geometric | 177–201 | `#fafaf9` | `#f5f5f4` | `#1c1917` | `#78716c` | `#dc2626` | `#78716c` | `#ea580c` | Syne 700 | Inter 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 5 | Soft Curves | 219–243 | `#fffbf5` | `#fef3e2` | `#292524` | `#78716c` | `#f97066` | `#a8a29e` | `#fb923c` | Outfit 700 | DM Sans 400 | JetBrains Mono | 700 | 400 | **16px** | Light |
| 6 | Teal Serenity | 261–285 | `#f0fdfa` | `#ccfbf1` | `#134e4a` | `#0f766e` | `#14b8a6` | `#5eead4` | `#06b6d4` | Plus Jakarta Sans 700 | Manrope 400 | JetBrains Mono | 700 | 400 | **12px** | Light |
| 7 | Asymmetric | 303–327 | `#f5f5f4` | `#e7e5e4` | `#292524` | `#78716c` | `#6366f1` | `#a1a1aa` | `#a78bfa` | Bricolage Grotesque 700 | Source Sans 3 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 8 | Bento Grid | 347–371 | `#fafafa` | `#f4f4f5` | `#18181b` | `#71717a` | `#3b82f6` | `#a1a1aa` | `#10b981` | Plus Jakarta Sans 700 | Manrope 400 | JetBrains Mono | 700 | 400 | **12px** | Light |
| 9 | Playful Pop | 389–413 | `#ffffff` | `#f5f3ff` | `#1e1b4b` | `#6b7280` | `#7c3aed` | `#a78bfa` | `#fbbf24` | Rubik 700 | Work Sans 400 | JetBrains Mono | 700 | 400 | **16px** | Light |
| 10 | Retro 90s | 431–455 | `#fef9ef` | `#fef3c7` | `#44403c` | `#78716c` | `#ea580c` | `#0d9488` | `#ca8a04` | Chivo 700 | Lato 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 11 | Editorial | 473–497 | `#faf9f7` | `#f5f5f0` | `#1a1a1a` | `#737373` | `#991b1b` | `#a3a3a3` | `#b45309` | DM Serif Display 400 | DM Sans 400 | JetBrains Mono | 400 | 400 | **4px** | Light |
| 12 | Data Story | 515–539 | `#ffffff` | `#f1f5f9` | `#1e293b` | `#64748b` | `#1e40af` | `#64748b` | `#0891b2` | IBM Plex Serif 600 | IBM Plex Sans 400 | JetBrains Mono | 600 | 400 | **6px** | Light |
| 13 | Classic Luxe | 557–581 | `#fefce8` | `#fef9c3` | `#1c1917` | `#78716c` | `#92400e` | `#a16207` | `#166534` | Playfair Display 700 | Source Sans 3 400 | JetBrains Mono | 700 | 400 | **4px** | Light |
| 14 | Botanical | 599–623 | `#f0fdf4` | `#dcfce7` | `#14532d` | `#16a34a` | `#15803d` | `#86efac` | `#a16207` | Cormorant Garamond 700 | Source Sans 3 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 15 | Creative Studio | 641–665 | `#faf5ee` | `#f5ebe0` | `#292524` | `#78716c` | `#c2410c` | `#a8a29e` | `#65a30d` | Fraunces 700 | IBM Plex Sans 400 | JetBrains Mono | 700 | 400 | 8px | Light |
| 16 | Midnight Pro | 683–707 | `#0f172a` | `#1e293b` | `#e2e8f0` | `#94a3b8` | `#3b82f6` | `#64748b` | `#22d3ee` | Sora 700 | Inter 400 | JetBrains Mono | 700 | 400 | 8px | **Dark** |
| 17 | Prism Glow | 725–749 | `#1e1b4b` | `#312e81` | `#e0e7ff` | `#a5b4fc` | `#8b5cf6` | `#6366f1` | `#ec4899` | Bodoni Moda 700 | Manrope 400 | JetBrains Mono | 700 | 400 | **12px** | **Dark** |
| 18 | Photo Noir | 769–793 | `#111827` | `#1f2937` | `#f9fafb` | `#9ca3af` | `#e5e7eb` | `#6b7280` | `#f59e0b` | Raleway 700 | Nunito Sans 400 | JetBrains Mono | 700 | 400 | **4px** | **Dark** |

All 18 use the identical mono stack: `'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace` (6 presets omit `'Cascadia Code'` — Minimal Clean 1, Data Story 12, Editorial 11, Classic Luxe 13, Botanical 14, Creative Studio 15, Data Story uses 4 stacks; exact per-preset strings are in the file).

Each preset also carries a **Google Fonts `<link>`** (e.g. line 81: `https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600&family=Source+Sans+3:wght@400;600&display=swap`) and a "Color DNA" one-liner.

### 1.2 Discrepancies found in this file

- `STYLE_PRESETS.md:815` (Marketing/Sales row) recommends `Photo Noir` — a dark photo-centric preset — for marketing. `SKILL.md:108` gives the same row. Not a bug, but the two tables differ in the last row: `STYLE_PRESETS.md:817` has "Art / Culture → Creative Studio, Editorial, Photo Noir" which `SKILL.md` lacks.
- `STYLE_PRESETS.md:344` (Bento Grid) says to "Pair with `data-layout="blank"` and custom grid CSS" — i.e. the preset that advertises a "dashboard aesthetic" has no actual bento layout in the codebase.
- README's Light/Dark tables (lines 100–124) number presets 1,2,4..15 / 3,16,17,18 — i.e. `Pitch Deck` is #3 but listed under Dark while the quick-reference in `STYLE_PRESETS.md` lists it as #3 Dark. Consistent, but the README re-numbers in a confusing order.

---

## 2. `viewport-base.css` — the 13 layouts and the core CSS

**Count method:** `grep -o 'data-layout="[a-z-]*"' viewport-base.css | sort -u` → **13** unique values:
`blank, bullets, chart, comparison, content, image-full, image-left, image-right, quote, section, timeline, title, two-column`

Corroborated 3× independently:
- `html-template.md` `### N. X Layout` headings → **13** (lines 517, 530, 541, 559, 579, 599, 619, 631, 647, 660, 677, 697, 733)
- `SKILL.md:159-173` layout table → **13** rows
- `html-template.md` layout example `data-layout` values → **13** distinct

### 2.1 Layout definitions (source line ranges) and their DOM contract

| Layout | CSS lines | Required DOM (from `html-template.md` example) | Helper classes |
|---|---|---|---|
| `title` | 130–148 | `<div class="slide-content">` + `h1` + `p.subtitle` + `p.meta` | — |
| `section` | 152–178 | `h1` + `p.subtitle`; `::after` draws an 80×4px rule | — |
| `content` | 182–195 | `h1` + `p`/`ul`/`ol` (max-width 75%) | — |
| `two-column` | 199–217 | `div.ns-columns` > `div.ns-col` ×2 | `.ns-columns` (grid 1fr 1fr), `.ns-col` |
| `image-left` | 221–247 | `div.ns-split` > `div.ns-split-image` (img) + `div.ns-split-text` | `.ns-split`, `.ns-split-image`, `.ns-split-text` |
| `image-right` | 251–264 | same DOM; `ns-split-text` gets `order:-1` | same |
| `image-full` | 268–297 | `section[style*="background-image"]`; `::before` gradient scrim forces white text | `.ns-hero` (abs) |
| `chart` | 312–329 | `div.ns-chart-container` (80% w, max 1400px) | — |
| `quote` | 333–371 | `div.ns-quote` > `blockquote` + `p.ns-attribution` | `.ns-quote`, `.ns-attribution` |
| `bullets` | 375–411 | `ul.ns-bullets` > `li` (dot via `::before`) | `.ns-bullets` |
| `comparison` | 415–442 | `div.ns-compare` > `div.ns-compare-card` ×2 | `.ns-compare`, `.ns-compare-card` |
| `timeline` | 446–452 | `div.ns-timeline` (**CSS NOT PRESENT — see §7**) | `.ns-timeline*` missing |
| `blank` | 456–459 | freeform | — |

### 2.2 Core non-layout CSS in the same file

- **Reset** 12–33
- **Slide container** `.ns-deck` 37–45; `.slide` 47–59 (fixed **1920×1080**, `transform: scale(var(--ns-scale,1))`, `transform-origin:center center`, `opacity:0; visibility:hidden`, 400ms transition); `.slide.active` 61–64
- **`.slide-content`** 66–74 (`padding: var(--ns-slide-padding)`, flex column, z-index 1)
- **Typography** 78–126: `h1..h4` use `--ns-font-heading`/`--ns-heading-weight`, `line-height:1.15`, `letter-spacing:-0.02em`; sizes `h1 clamp(40px,4.5vw,56px)`, `h2 clamp(32px,3.5vw,44px)`, `h3 clamp(24px,2.8vw,36px)`, `h4 clamp(20px,2.2vw,28px)`; body `p,li,td,span,label` → `--ns-font-body`, `line-height:1.5`, `clamp(18px,2vw,24px)`; `.subtitle clamp(20px,2.2vw,28px)`; `.meta clamp(14px,1.5vw,18px)`; `code,pre,.mono` → `--ns-font-mono`; `strong,b {font-weight:600}`
- **Nav UI** 463–537: `.ns-progress` (fixed, 3px, top), `.ns-progress-bar` (width 0%, 300ms), `.ns-nav` (full-screen, `pointer-events:none`), `.ns-nav-prev/.ns-nav-next` (48×96, opacity 0 → 0.6 on `.ns-deck:hover`), `.ns-counter` (bottom-right, 14px, opacity .5)
- **`.notes { display:none }`** 541–543
- **Black screen** `.black-screen` 547–559
- **Utility classes** 563–593: `text-center/left/right`, `mb-*`/`mt-*`/`gap-*` (xs..2xl), `accent-text`, `muted-text`, `bg-alt`, `rounded`, `hide-in-print`
- **`@media print`** 597–663: `@page { size:landscape; margin:0 }`; `.slide` → `position:relative; width:100vw; height:100vh; opacity:1; visibility:visible; page-break-after:always`; `* { -webkit-print-color-adjust:exact }`; `* { animation:none !important; transition:none !important }`; `[class*="animate-"] { opacity:1 !important; transform:none !important; filter:none !important }`; hides `.ns-progress, .ns-nav, .ns-counter, .notes, .hide-in-print`

---

## 3. `animation-library.md` — the 24 animations

**Count method:** `grep -n '^### [0-9]*\. animate-' animation-library.md` → **24** headings (lines 90, 102, 112, 124, 136, 148, 160, 172, 188, 204, 216, 228, 240, 256, 273, 285, 297, 309, 326, 338, 364, 379, 394, 409).
README claims "20 entrance + 4 emphasis" — **confirmed**: #1–#20 are under `## Entrance Animations` (line 86), #21–#24 under `## Emphasis Animations` (line 360).

### 3.1 The exact 24

| # | Class | @keyframes | Lines | Type | Notes |
|---|---|---|---|---|---|
| 1 | `animate-fade-up` | `ns-fade-up` | 90–100 | entrance | default; translateY 30px→0 |
| 2 | `animate-fade-down` | `ns-fade-down` | 102–110 | entrance | translateY −30px→0 |
| 3 | `animate-fade-left` | `ns-fade-left` | 112–122 | entrance | enters from right (translateX 30px) |
| 4 | `animate-fade-right` | `ns-fade-right` | 124–134 | entrance | enters from left (translateX −30px) |
| 5 | `animate-fade-in` | `ns-fade-in` | 136–146 | entrance | opacity only |
| 6 | `animate-scale-up` | `ns-scale-up` | 148–158 | entrance | scale .85→1 |
| 7 | `animate-scale-down` | `ns-scale-down` | 160–170 | entrance | scale 1.15→1 |
| 8 | `animate-scale-x` | `ns-scale-x` | 172–186 | entrance | **sets `opacity:1`**, `transform-origin:left center` |
| 9 | `animate-scale-y` | `ns-scale-y` | 188–202 | entrance | **sets `opacity:1`**, `transform-origin:bottom center` |
| 10 | `animate-blur-in` | `ns-blur-in` | 204–214 | entrance | filter blur 10px→0 |
| 11 | `animate-flip-x` | `ns-flip-x` | 216–226 | entrance | perspective(800px) rotateX 90→0 |
| 12 | `animate-flip-y` | `ns-flip-y` | 228–238 | entrance | perspective(800px) rotateY 90→0 |
| 13 | `animate-zoom-in` | `ns-zoom-in` | 240–254 | entrance | scale 0→1.08→1, custom cubic-bezier |
| 14 | `animate-pop` | `ns-pop` | 256–271 | entrance | scale 0→1.12→.95→1, spring bezier |
| 15 | `animate-rotate-in` | `ns-rotate-in` | 273–283 | entrance | rotate −10deg + scale .9 |
| 16 | `animate-slide-in-left` | `ns-slide-in-left` | 285–295 | entrance | translateX −100%→0 |
| 17 | `animate-slide-in-right` | `ns-slide-in-right` | 297–307 | entrance | translateX 100%→0 |
| 18 | `animate-typewriter` | `ns-typetypewriter`→`ns-typewriter` | 309–324 | entrance | `clip-path: inset()`, `steps(40,end)`, 2s, **sets `opacity:1`** |
| 19 | `animate-counter-up` | **NONE** | 326–336 | **not a CSS animation** | marker class only; JS-driven; `data-target` |
| 20 | `animate-draw-line` | `ns-draw-line` | 338–356 | entrance | SVG `stroke-dashoffset`, **sets `opacity:1`** |
| 21 | `animate-pulse` | `ns-pulse` | 364–377 | emphasis | scale 1↔1.05, 2s infinite, `opacity:1` |
| 22 | `animate-glow` | `ns-glow` | 379–391 | emphasis | box-shadow 8px→24px, 2s infinite, `opacity:1` |
| 23 | `animate-float` | `ns-float` | 394–406 | emphasis | translateY 0↔−8px, 3s infinite, `opacity:1` |
| 24 | `animate-shimmer` | `ns-shimmer` | 409–428 | emphasis | background-position sweep, 2s linear infinite, `opacity:1` |

### 3.2 Supporting CSS

- **Base** 20–44: `[class*="animate-"] { opacity:0; animation-duration:500ms; animation-timing-function: cubic-bezier(0.16,1,0.3,1); animation-fill-mode:forwards }`; `.slide.active [class*="animate-"] { animation-play-state:running }`; `.slide:not(.active) [class*="animate-"] { animation-play-state:paused; opacity:0 }`; emphasis exemption list `.animate-pulse,.animate-glow,.animate-float,.animate-shimmer { opacity:1 }`
- **Easing** 50–57: `--ns-ease-default` (0.16,1,0.3,1), `--ns-ease-bounce` (0.34,1.56,0.64,1), `--ns-ease-smooth` (0.4,0,0.2,1), `--ns-ease-spring` (0.175,0.885,0.32,1.275)
- **Stagger** 63–72: `.delay-100 … .delay-1000` (100,200,300,400,500,600,800,1000 — **note: no 700**)
- **Duration** 78–82: `.duration-fast 300ms`, `.duration-normal 500ms`, `.duration-slow 800ms`
- **Reduced motion** 436–451: `* { animation-duration:0.01ms !important; animation-iteration-count:1 !important; transition-duration:0.01ms !important }` + `[class*="animate-"] { opacity:1 !important; transform:none !important; filter:none !important }`

### 3.3 ⚠ The 24th animation is broken as shipped

`animate-counter-up` (#19) has **no `@keyframes`** and **no `opacity:1` exemption**, while the base rule sets `opacity:0` on every `[class*="animate-"]`. Measured in headless Chromium against a deck built from the donor's own files:

```json
{ "present": true, "textContent": "73%", "dataTarget": "73",
  "computedOpacity": "0", "computedVisibility": "visible",
  "animationName": "none",
  "siblingWithoutClass": { "text": "0", "opacity": "1" } }
```

→ The counter element is **permanently invisible**. The JS in `html-template.md:231-264` does update `textContent` from 0→73, but the element never becomes visible. Visual proof: `probe/shot_midnight_counter_bug.png` — the "73%" value is absent from the rendered slide.
`interactive-elements.md:154` uses this exact class on the donut-chart label, so the donut's number is also invisible.

---

## 4. `typography-system.md` — the typography system

- **Selection criteria** (lines 9–19): high x-height, open counters, strong weight contrast, variable-font support, Google Fonts availability, screen optimisation, large-size rendering.
- **Size scale** (lines 27–36) — 8 roles, all `clamp()`:
  | Role | Range | CSS |
  |---|---|---|
  | H1 | 40–56px | `clamp(40px,4.5vw,56px)` |
  | H2 | 32–44px | `clamp(32px,3.5vw,44px)` |
  | H3 | 24–36px | `clamp(24px,2.8vw,36px)` |
  | Body | 18–24px | `clamp(18px,2vw,24px)` |
  | Subtitle | 20–28px | `clamp(20px,2.2vw,28px)` |
  | Caption | 14–18px | `clamp(14px,1.5vw,18px)` |
  | Label | 12–16px | `clamp(12px,1.2vw,16px)` |
  | Mono | 16–20px | `clamp(16px,1.6vw,20px)` |
- **Rules** (38–42): nothing below 14px; line-height 1.1–1.2 headings / 1.4–1.6 body; letter-spacing −0.02em headings, 0 body, 0.02em all-caps labels.
- **Font catalogue** (46–120): 4 display categories (Geometric Sans: Space Grotesk/Sora/Outfit/Syne; Grotesque Sans: Archivo Black/Bricolage Grotesque/Chivo/Rubik/Raleway; Display Serif: DM Serif Display/Playfair Display/Bodoni Moda; Character Serif: Fraunces/Cormorant Garamond/IBM Plex Serif/Newsreader/Spectral) + 3 body categories (Neutral Sans: Inter/Source Sans 3/DM Sans; Humanist Sans: Manrope/Work Sans/Lato/Nunito Sans/Outfit; Technical Sans: IBM Plex Sans).
- **Mono** 123–135: single stack `'JetBrains Mono','Fira Code','Cascadia Code','Consolas',monospace`.
- **Preset↔Font mapping table** 142–161 (18 rows, matches §1.1).
- **2-font rule** 174–181: emphasis via weight / size / color / case only.
- **Google Fonts loading** 185–201: `preconnect` ×2 + one combined `<link>`, `display=swap`, add `family=JetBrains+Mono:wght@400` only if code blocks present.
- **RTL / Arabic handling: NONE.** Zero occurrences of `dir=`, `rtl`, `arabic`, `hebrew`, `noto`, `bidi` in the entire repository (`grep -ric` across all files = 0). `letter-spacing:-0.02em` and `text-align:center` on headings are also RTL-unsafe. `typography-system.md:254` explicitly says "Justified text — always use left-align for body", so RTL is unaddressed, not merely unsupported.
- **Measure (line length):** NOT specified. The only constraints are `max-width: 75%` on `.ns-bullets` (viewport-base.css:386) and `[data-layout="content"] p/ul/ol { max-width:75% }` (:191-195). There is no `max-width` in `ch`/`em` anywhere.
- **CJK/Arabic font coverage:** the mono stack has no CJK fallback; heading/body stacks are Latin-only Google Fonts.

---

## 5. `html-template.md` — the single-file HTML model

### 5.1 DOM contract (what the JS depends on)

| Selector / attribute | Role | Where defined |
|---|---|---|
| `div.ns-deck` | deck root; JS `querySelector('.ns-deck')` | viewport-base.css:37 |
| `section.slide` | one per slide | viewport-base.css:47 |
| `section.slide[data-slide="N"]` | **N is the slide number**, used by `goToSlide`/`getNotesForSlide` | html-template.md:150, 400 |
| `section.slide[data-layout="TYPE"]` | one of the 13 layout names | viewport-base.css |
| `.slide.active` | the visible slide; JS adds/removes this class | html-template.md:144, 152 |
| `div.slide-content` | content wrapper, holds padding | viewport-base.css:66 |
| `aside.notes` | speaker notes; hidden via `display:none` | viewport-base.css:541 |
| `.ns-progress-bar` | progress fill, `style.width` | viewport-base.css:473 |
| `.ns-current` / `.ns-total` | counter text | html-template.md:114-115 |
| `.ns-nav-prev` / `.ns-nav-next` | nav buttons | viewport-base.css:490-525 |
| `script#slide-data[type="application/json"]` | PPTX export payload | html-template.md:78 |
| `[class*="animate-"]` | animation targets (selector-based, not a fixed class list) | animation-library.md:21 |
| `.animate-counter-up[data-target="N"]` | JS counter target | animation-library.md:333 |
| `#slide-N` URL hash | deep link | html-template.md:190-201 |

### 5.2 Inlined CSS in the generated file

Per `SKILL.md:126-142`, the `<style>` block contains 5 things: (1) preset `:root` vars, (2) `viewport-base.css` content, (3) animation keyframes, (4) `@media print` rules, (5) preset-specific styling.
**`interactive-elements.md`'s CSS is NOT in that list and is not referenced anywhere as needing to be inlined.** See §7 — this is a real defect.

### 5.3 The JavaScript controller (html-template.md:100-508, IIFE, `'use strict'`)

State: `SLIDE_WIDTH=1920`, `SLIDE_HEIGHT=1080`, `currentSlide=1`, `totalSlides`, `isBlackScreen`.

| Function | Lines | Behaviour |
|---|---|---|
| `updateScale()` | 122–127 | `min(innerW/1920, innerH/1080)` → CSS var `--ns-scale`; debounced 100ms on resize |
| `goToSlide(n)` | 137–164 | clamps 1..N; **early-returns if `n===currentSlide && .slide.active` exists**; removes `.active` + `resetAnimations(prev)`; adds `.active` + `triggerAnimations(target)` + `runCounterAnimations(target)`; updates progress/counter/hash; `syncPresenter()` |
| `nextSlide/prevSlide` | 166–172 | clamped |
| `updateProgressBar()` | 175–180 | `(currentSlide/totalSlides)*100 + '%'` |
| `updateCounter()` | 183–186 | textContent |
| `updateHash()` / `readHash()` | 189–206 | `history.replaceState` → `#slide-N`; regex `^#slide-(\d+)$` |
| `triggerAnimations(slide)` | 209–221 | for each `[class*="animate-"]`: find first class starting `animate-`, **skip `animate-counter-up`**, remove → `void el.offsetWidth` → re-add (restart) |
| `resetAnimations(slide)` | 223–228 | sets **inline** `el.style.opacity='0'` on all animated els |
| `runCounterAnimations(slide)` | 231–264 | `requestAnimationFrame` count-up over 1500ms, ease-out-cubic, preserves non-numeric prefix/suffix |
| keyboard handler | 267–324 | see §6 |
| touch handler | 330–344 | horizontal swipe > 50px and `|dx|>|dy|` |
| click nav | 347–348 | — |
| `toggleFullscreen()` | 351–357 | `documentElement.requestFullscreen()` |
| `toggleBlackScreen()` | 364–373 | toggles `body.black-screen`, posts `black-screen` message |
| BroadcastChannel setup | 376–387 | `new BroadcastChannel('nextslide-presenter')` in try/catch; listens for `type==='navigate'` |
| `syncPresenter()` | 389–397 | posts `{type:'slide-change', slide, total, notes}` |
| `getNotesForSlide(n)` | 399–404 | reads `.notes` textContent of `[data-slide="N"]` |
| `openPresenterWindow()` | 406–429 | `window.open('', 'nextslide-presenter', 'width=1200,height=800,...')`; `pw.document.write(presenterHTML)`; after 500ms posts `{type:'init',...}` |
| `generatePresenterHTML(title)` | 431–493 | returns a full HTML string (inline `<style>` + inline `<script>`) |
| `init()` | 496–500 | `readHash()`; sets `counterTotal`; `goToSlide(startSlide)` |

### 5.4 Embedded JSON schema (`slide-data`)

Documented at `html-template.md:748-946`.
```
{ meta: { title, author, date, theme, slideWidth, slideHeight },
  slides: [ { layout, background:{color|image}, elements:[...], notes } ] }
```
Element types: `text` (role: title|subtitle|body|caption|label|footnote; align: left|center|right; valign: top|middle|bottom), `image` (`src`, `alt`, `style.objectFit`, `style.borderRadius`), `shape` (`rect|circle|line`, `style.fill`), `chart` (`bar|bar-horizontal|donut|progress`, `data:[{label,value}]`).
Positions are **percentage strings**; `fontSize` is in **points** (`px*0.75`).

---

## 6. Presenter mode

### 6.1 How it opens
Press `P` (or `p`) in the main window → `openPresenterWindow()` → `window.open('', 'nextslide-presenter', 'width=1200,height=800,menubar=no,toolbar=no,location=no,status=no')` → `pw.document.write(presenterHTML)` → `pw.document.close()`. Popup-blocked → `alert('Popup blocked...')` and abort.

### 6.2 Sync
`BroadcastChannel('nextslide-presenter')`. Main→presenter: `init`, `slide-change`, `black-screen`. Presenter→main: `navigate`. Measured working in Chromium: clicking the presenter's "Next →" advanced the deck from slide 8 to slide 9.

### 6.3 Keyboard bindings (main window, `html-template.md:267-324`)
| Key | Action | Line |
|---|---|---|
| `→` `↓` `PageDown` `Space` | next slide | 272–278 |
| `←` `↑` `PageUp` | prev slide | 279–284 |
| `Home` | slide 1 | 285–288 |
| `End` | last slide | 289–292 |
| `F` / `f` | fullscreen | 293–297 |
| `P` / `p` | presenter window | 298–302 |
| `B` / `b` / `.` | black screen | 303–308 |
| `Escape` | exit fullscreen | 309–313 |
| `1`–`9` | jump to slide N | 315–322 |

Input/textarea are ignored (line 269).

### 6.4 Presenter window contents — as actually implemented
`generatePresenterHTML` (431-493) renders: current **slide number** (`#p-cur-num`), next **slide number** (`#p-next-num`, shows "End" past the last slide), speaker notes (`#p-notes`), elapsed timer (`#p-timer`, `HH:MM:SS` via `requestAnimationFrame`), wall clock (`#p-clock`), counter (`#p-counter` = "N / total"), and 3 buttons (Reset Timer / ← Prev / Next →). Its own keydown handler: `→`/`Space` next, `←` prev.

### 6.5 ⚠ `presenter-mode.md` and `html-template.md` describe DIFFERENT presenter windows
- `presenter-mode.md:97` and `:130` style `.current-slide iframe` / `.next-slide iframe` with `transform:scale(0.5)`, and `:230`/`:235` provide `#current-slide-content` / `#next-slide-content` divs. **No iframe is ever created** by the shipped controller.
- `presenter-mode.md:309` calls `getAllSlideContent()` — **this function does not exist anywhere in the repository** (verified by grep).
- `presenter-mode.md:347-388` defines a `PresenterTimer` **class**; the shipped controller uses a plain `start=Date.now()` closure.
- Class naming differs entirely: `presenter-mode.md` uses `presenter-layout / current-slide / next-slide / notes-panel / bottom-bar`; `html-template.md` uses `p-layout / p-current / p-next / p-notes / p-bar`.
- `presenter-mode.md:404` says `P` = "Toggle presenter window"; the controller only ever **opens** (never closes).

**Measured**: the real presenter window contains `iframes: 0`, `imgTags: 0`, and `.p-current` innerHTML = `<span class="p-current-label">Current Slide</span><span class="p-slide-num" id="p-cur-num">8</span>` — i.e. a big number, **not a slide preview**. Screenshot: `probe/shot_presenter_window.png`.
→ **README:18 "next-slide preview" is FALSE.** Also `presenter-mode.md` documents a `black-screen` message flow that the presenter window's `onmessage` handler ignores (it only handles `init`/`slide-change`).

---

## 7. `interactive-elements.md` — widgets, and a real integration gap

### 7.1 Widgets present (10 CSS blocks + 10 HTML snippets)
| Widget | HTML lines | CSS lines | Key classes |
|---|---|---|---|
| Horizontal bar chart | 13–43 | 45–86 | `.ns-chart.ns-chart-bar-h`, `.ns-bar-row/-label/-track/-fill/-value` |
| Vertical bar chart | 90–116 | 118–143 | `.ns-chart.ns-chart-bar-v`, `.ns-bar-col`, `.ns-bar-fill-v` |
| Donut / ring | 151–158 | 160–192 | `.ns-donut-chart`, `.ns-donut`, `.ns-donut-label`, `.ns-donut-caption` |
| Metric / KPI card | 200–218 | 220–262 | `.ns-metrics`, `.ns-metric-card`, `.ns-metric-value`, `.ns-metric-label`, `.ns-metric-change.positive/.negative/.neutral` |
| Progress bar group | 270–291 | 293–332 | `.ns-progress-group`, `.ns-progress-item/-header/-label/-value/-track/-fill` |
| Vertical timeline | 340–367 | 369–427 | `.ns-timeline`, `.ns-timeline-item/-marker(.active)/-content/-date/-title/-desc` |
| Horizontal timeline | 435–453 | 455–495 | `.ns-timeline-h`, `.ns-timeline-h-item/-dot(.active)/-date` |
| Code block | 503–516 | 518–561 | `.ns-code-block`, `.ns-code-header`, `.ns-code-lang`, `.ns-code-filename`, `.ns-code`, `.ns-code-keyword/-string/-function/-variable/-comment/-number` |
| Comparison table | 569–596 | 598–631 | `.ns-comparison`, `.ns-table`, `.ns-highlight` |
| Icon grid | 639–657 | 659–688 | `.ns-icon-grid`, `.ns-icon-card`, `.ns-icon` |

All are **pure CSS / HTML** — no JS, no chart library. Bars are driven by inline custom properties: `--ns-bar-value` (width/height), `--ns-donut-value` (0–100 → `calc(v * 3.6deg)` conic-gradient), `--ns-progress` (width), `--ns-primary-rgb` (rgba tint, **with a hardcoded fallback `59,130,246` at line 627 that does not match any preset**).

### 7.2 ⚠ CRITICAL: the widget CSS is never inlined by the documented pipeline
`grep -c '\.ns-bar-row' viewport-base.css` → **0**. `grep -c '\.ns-metric-card' viewport-base.css` → **0**. `grep -c '\.ns-timeline' viewport-base.css` → **0**. The same is true for `.ns-donut`, `.ns-code-block`, `.ns-table`, `.ns-icon-grid`, `.ns-progress-group`, `.ns-chart-bar-h/-v`.
`SKILL.md:126-142` (the Phase 4 "Output Format") lists only 5 items for the `<style>` block and **never says to inline `interactive-elements.md`'s CSS**. `SKILL.md:20` and `:123` only say to *load the file* ("Charts, timelines, code blocks").

**Consequence, measured**: a deck built strictly per SKILL.md renders charts/KPI-cards/timelines/donuts/code-blocks/tables/icon-grids **completely unstyled**.
- `probe/shot_chart_UNSTYLED_per_SKILL.md.png` — chart slide shows only a text list, no bars.
- `probe/shot_midnight_counter_bug.png` — KPI cards have no card background, no grid.
- Inlining the 10 CSS blocks fixes it: `probe/shot_chart_STYLED_with_interactive_CSS.png` and `probe/shot_timeline_STYLED.png` (46 KB / 61 KB vs 50 KB / 69 KB).

---

## 8. The two scripts

### 8.1 `scripts/export-pptx.js` — HTML → PPTX
- **Entrypoint:** `node export-pptx.js <path-to-html> [output-path]`. Shebang `#!/usr/bin/env node`. Node ≥ 14 (uses `async/await`, `Object.entries`-free). Runs on **Node v26.0.0** ✔.
- **Flags:** `--help` / `-h` (prints usage, exit 0). No other flags. No stdin support.
- **Dependency:** `pptxgenjs ^3.12.0` (declared in `scripts/package.json`, `scripts.export` npm script = `node export-pptx.js`). **Not vendored** — must `npm install` in `scripts/`. Installed cleanly (19 packages, 3s).
- **Input:** an HTML file containing `<script type="application/json" id="slide-data">…</script>`. Regex at line 28 (case-insensitive, order-sensitive: `type` before `id`).
- **Output:** `<input>.pptx` next to the input by default, or the explicit second arg. `path.resolve`d.
- **Runtime behaviour:** reads JSON → `new PptxGenJS()` → `defineLayout({name:'NEXTSLIDE', width: meta.slideWidth||13.333, height: meta.slideHeight||7.5})` → `pptx.layout='NEXTSLIDE'` → per slide: background colour / background image, then dispatches on `el.type` → `text` / `image` / `shape` / `chart`; unknown types are warned and skipped → `slide.addNotes(slideData.notes)` → `await pptx.writeFile({fileName})`.
- **Element mapping details:**
  - `text` (91–123): `pctToInches` for x/y/w/h; `fontSize` default 24; `fontFace` default `Arial`; `color` hex with `#` stripped (default `000000`); `align`/`valign` mapped with `left`/`top` fallbacks; `wrap:true`; `margin:[0,0,0,0]`; `paraSpaceAfter:4`; optional `lineSpacing`, `underline`.
  - `image` (125–168): `data:` URI → `opts.data`; `http(s)://` → `opts.path` (**← wrong: PptxGenJS `path` is a local file path, not a URL**); other → `opts.path` (local). `objectFit` → `opts.sizing={type:'cover'|'contain',w,h}`; `borderRadius>0` → `opts.rounding=true`. Failures are caught and warned, not fatal.
  - `shape` (170–202): `mapShape` → `RECTANGLE`/`OVAL`/`LINE`; `fill` hex; `shape==='line'` → `opts.line`, `fill` deleted; `borderRadius` → `rectRadius = px/72`.
  - `chart` (204–271): for `bar`/`bar-horizontal` tries a **native** `slide.addChart(type, [{name:'Data',labels,values}], {...})`; on failure falls back to `slide.addTable`.
- **⚠ Chart bug (real, reproduced):** line 226 hard-codes `const type = chartType === 'bar-horizontal' ? 'BAR' : 'BAR';` — the ternary is a no-op **and** pptxgenjs 3.12.0 expects **lowercase** `ChartType` values (`'bar'`, `'line'`, …), not `'BAR'`. Measured A/B:
  - `'BAR'` → `ppt/charts/chart1.xml` has **no `<c:barChart>` element**; `<c:plotArea>` contains only `layout, catAx, valAx` → **invalid OOXML**; `python-pptx` raises `IndexError: tuple index out of range` on `chart.chart_type`; PowerPoint would show a repair prompt.
  - `'bar'` → `<c:barChart>` present with `barDir`, `grouping`, `ser` → valid.
  All three of my exported decks carry the corrupt chart part (`INVALID_CHART=['ppt/charts/chart1.xml']`).
- **⚠ `mapShape` is dead code:** `PptxGenJS.ShapeType` is `undefined` on the class in 3.12.0 (it is an *instance* property), so `const shapes = PptxGenJS.ShapeType || {}` → `{}` → always falls back to the string `'rect'`. Output is still correct (`prstGeom prst="rect"`), but the `circle`/`line` mapping never fires.
- **Not implemented:** the JSON schema documents `chartType: "donut"` and `"progress"` — neither is handled (only `bar`/`bar-horizontal` reach the native path; `donut`/`progress` silently fall through to the table fallback because the `if` guard excludes them). `el.style.valign` is read but `role` is never used.

### 8.2 `scripts/extract-pptx.py` — PPTX → text/JSON
- **Entrypoint:** `python extract-pptx.py <path-to-pptx> [--images-dir DIR] [--format {text,json}]`. Shebang `#!/usr/bin/env python3`. argparse; default `--format text`.
- **Dependencies:** `python-pptx` (imported at module top; `ImportError` → friendly message, exit 1) and `Pillow` (declared in the docstring, **never actually imported** — python-pptx needs it for image blobs, so it's an implicit dep). **Not vendored.**
- **Runtime:** `Presentation(path)` → per-slide `guess_layout()` + per-shape `extract_shape()` → per-slide `extract_notes()` → `{"meta":…, "slides":[…]}` → `format_as_text()` or `json.dumps(indent=2, ensure_ascii=False)`. Progress/summary goes to **stderr**, payload to **stdout**. `meta` = title (from filename, overridden by slide-1 placeholder idx 0), slideWidth/Height in inches, slideCount, author, date.
- **Element output:** `type` ∈ `text|image|table|chart|shape`; `position` = `{"x":"10.0%", …}` (percent strings); `content`; `role`; `style` (fontSize pt, fontFace, bold, italic, color, align); `notes` per slide.
- **⚠ BUG 1 — hard crash on ANY pptx with a non-placeholder shape.** Lines 92, 199 and 281 use `hasattr(shape, "placeholder_format")`. In python-pptx, `placeholder_format` is a **property that raises `ValueError("shape is not a placeholder")`** for non-placeholders; `hasattr()` only swallows `AttributeError`. Reproduced:
  ```
  File ".../extract-pptx.py", line 281, in extract_presentation
      hasattr(shape, "placeholder_format")
  File ".../pptx/shapes/base.py", line 151, in placeholder_format
      raise ValueError("shape is not a placeholder")
  ValueError: shape is not a placeholder
  ```
  It crashes on the donor's own exported deck, on a plain python-pptx fixture, and therefore on essentially every real-world PPTX. Exit code 1, no output. Log: `probe/extract_pptx_PRISTINE_crash.log`.
- **⚠ BUG 2 — silent total data loss.** Line 223: `if para.font.color and para.font.color.rgb:` — `para.font.color.rgb` raises `AttributeError("no .rgb property on color type '_NoneColor'")` when the colour is not explicitly RGB. The per-shape `try/except` at 312 swallows it and **drops the whole shape**. Measured on the donor's own export: `✓ Extracted 9 slides / ✓ Found 0 elements` — **zero elements, but it reports success.** The file already contains a correct helper for this (`rgb_to_hex`, line 69) that is **never called** (dead code).
- **⚠ BUG 3 — chart shapes dropped.** `chart.chart_type` → `self.plots[0]` → `IndexError: tuple index out of range` because the exporter's uppercase `'BAR'` produced a chart part with no `<c:barChart>`. Caught and warned, shape dropped.
- **⚠ BUG 4 — typography lost on round-trip.** The exporter writes font/size/bold/colour at **run level** (`<a:rPr sz="4400" b="1">` + `<a:latin typeface="Sora">`; no `<a:defRPr>` at all). The extractor reads **paragraph level** (`para.font.size` etc., lines 215–225). Result: extracted `style` contains only `align` — `fontSize`, `fontFace`, `bold`, `color` are all lost. Verified in `probe/extract_midnight-pro.json`.
- **⚠ BUG 5 — layout is not recovered.** `guess_layout()` only recognises placeholders (`placeholder_format.idx == 0`). Because the exporter emits plain text boxes, every slide is guessed `content`/`bullets`; the original `title`/`section`/`chart`/`comparison`/`quote`/`timeline`/`two-column` is lost. Measured: `['content','bullets','content','content','image-left','image-left','bullets','content','content']` for a deck authored as `['title','two-column','section','chart','image-left','image-right','blank','counter','content']`.
- **Also note:** `role` is always `"body"` for exporter output (placeholder-only inference); `el["role"]` is `"title"` only for placeholder idx 0.

---

## 9. `LICENSE` / NOTICE obligations

`LICENSE` is the **MIT License, "Copyright (c) 2026 Danish Rafie Ekaputra"** (21 lines, verbatim MIT text).

MIT requires (verbatim from LICENSE lines 12–13):
> "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."

**Concrete obligations for a Gomrey transplant:**
1. **Retain the copyright line** `Copyright (c) 2026 Danish Rafie Ekaputra` verbatim.
2. **Retain the full MIT permission + warranty disclaimer** text (LICENSE lines 5–21), not just a pointer.
3. **Include both in all copies or substantial portions.** If any of `viewport-base.css`, the 18 preset token blocks, the 24 animation keyframes, the JS controller, or the 2 scripts are copied into Gomrey, the notice must ship with them.
4. **MIT imposes no source-disclosure, no copyleft, and no network-use restriction.** Derived works may be closed-source and commercial. No CLA/patent grant is given (MIT is silent on patents) — note that.
5. **README credits (lines 238–243) are non-binding but should be honoured**: PptxGenJS (MIT), python-pptx (MIT), Google Fonts (OFL/Apache — fonts are *not* bundled, only linked by CDN), and the PDF approach "inspired by Reveal.js" (MIT).
6. **Gomrey's own LICENSE is Apache-2.0** and `NOTICE` is a third-party-license inventory. The MIT notice must be added to the `NOTICE` inventory and/or the transplant module's own `LICENSE` file. MIT (donor) is compatible with Apache-2.0 (recipient) in both directions.
7. **No NOTICE file exists in the donor repo** — the donor's own Apache-style NOTICE obligations do not apply.
8. **Font licensing:** the presets link Google Fonts by CDN (no font binaries are redistributed), so no OFL text is required in Gomrey's NOTICE for the link form; a locally-hosted/embedded font would be.
9. **Third-party runtime deps stay outside the copyright question:** `pptxgenjs` (MIT) and `python-pptx` (MIT) have their own licences; Gomrey's `scripts/check-dependency-audit.mjs` and `scripts/generate-sbom.mjs` would need them registered if adopted.

---

## 10. TASK B — verification of the issue's claims

Issue #77 claims, each checked against the source and by execution.

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | **18 style presets** | ✅ **TRUE** | 18 `## Preset N:` headings; 18 `:root {` blocks; 18-row mapping table in `typography-system.md:142-161`; 19 distinct `--ns-*` tokens per preset. |
| 2 | **13 slide layouts** | ✅ **TRUE** | 13 unique `[data-layout=…]` selectors in `viewport-base.css`; 13 `### N. X Layout` headings in `html-template.md`; 13 rows in `SKILL.md:159-173`; 13 distinct values in the examples. |
| 3 | **24 CSS animations** | ⚠️ **TRUE COUNT, MISLEADING** | 24 headings, but only **23** `@keyframes ns-*` and only **23** `.animate-*` class rules. #19 `animate-counter-up` is explicitly "**Not a CSS animation**" (line 328) — a JS-driven marker class with **no keyframes** and **no `opacity:1` exemption**, so it renders at `opacity:0` (measured). Also "20 entrance + 4 emphasis" is accurate. |
| 4 | **Single-file HTML model** | ✅ **TRUE** | 1 `.html` with inlined `<style>`/`<script>` + `<link>` to Google Fonts + `<script type="application/json" id="slide-data">`. Built and rendered 4 working decks. |
| 5 | **Presenter mode** | ⚠️ **PARTIALLY TRUE** | It opens (`P`), syncs over BroadcastChannel, shows notes/timer/counter, and presenter→deck navigation **works** (measured). But there is **no slide preview** (`iframes:0`), and `presenter-mode.md` documents a different, non-integrated window that calls a nonexistent `getAllSlideContent()`. |
| 6 | **PPTX import / extraction** | ❌ **FALSE AS SHIPPED** | `extract-pptx.py` **crashes with `ValueError: shape is not a placeholder`** on every PPTX containing a non-placeholder shape — including the donor's own export output and a trivial python-pptx fixture. After 3 local patches it still silently drops all typography (run-level vs paragraph-level) and all original layouts. |
| 7 | **Editable PPTX export** | ✅ **TRUE (text) / ⚠️ PARTIAL (charts)** | Text is **real editable text**: 28 `<a:t>` runs in `deck_corporate-pro.pptx`, 28 non-empty text frames read back by python-pptx, **0 rasterized images**, speaker notes on every slide. **But** the chart part is corrupt (no `<c:barChart>`) because of the uppercase `'BAR'` bug. |
| 8 | **Templates** | ❌ **MISLEADING** | There is no HTML template *file*, no example deck, no starter project, no partials. `html-template.md` is **prose + code blocks**, and the "template" is a 91-line HTML skeleton (lines 11–91) plus a 409-line JS controller (lines 100–508) that a model is expected to re-type on every use. The 13 layout snippets (lines 517–744) are the closest thing to templates. |
| 9 | **Scripts** | ✅ **TRUE (2 scripts)** | `scripts/export-pptx.js` (414 lines, Node + pptxgenjs) and `scripts/extract-pptx.py` (463 lines, Python + python-pptx). Both ran (see Task C). |
| 10 | **Tests** | ❌ **FALSE** | **Zero test files have ever existed in this repository** (`git log --all --diff-filter=A --name-only` → 14 paths, none a test). No `tests/`, no `test/`, `*.test.*`, `*.spec.*`, `pytest.ini`, `tox.ini`, `jest.config.*`, `.github/workflows/`, or `Makefile`. No CI. The README's "Quality Checklist" (`SKILL.md:392-407`) is a **manual checklist for the LLM**, not automated tests. |
| 11 | **PDF export** | ✅ **TRUE** | `@media print` at `viewport-base.css:597-663`. Verified under `page.emulateMedia({media:'print'})`: slide `position:relative`, `visibility:visible`, `opacity:1`; nav/counter/notes `display:none`; `h1 opacity:1`. |
| 12 | **Editable PPTX export — "fully editable in PowerPoint/Google Slides/Keynote"** (SKILL.md:388) | ⚠️ **PARTIALLY TRUE** | Text/notes/chart-data are editable; the chart is a corrupt part; SVG images are embedded as `.svg` + `.png` fallback; and `role`-based styling and the CSS-only charts are flattened to a table, not a chart. |

### 10.1 Test-suite report
**There is no test suite.** Nothing is asserted anywhere. The only executable assertions in the repo are the implicit `throw`/`sys.exit(1)` guards in `export-pptx.js` (missing file, missing `slide-data` block, unparseable JSON) and in `extract-pptx.py` (missing `python-pptx`, missing file). The following are **untested and demonstrably broken**:
- chart export (no `<c:barChart>`),
- PPTX extraction (crash),
- `.animate-counter-up` (invisible),
- interactive-element CSS inclusion (never inlined),
- the presenter's "next-slide preview" (does not exist).

---

## 11. Additional defects found (not claimed by the issue)

| ID | Severity | Defect | Location | Proof |
|---|---|---|---|---|
| D1 | **High** | `.animate-counter-up` is permanently invisible (base rule `opacity:0`, no keyframes, no exemption) | `animation-library.md:326-336` vs `:20-44` | computed `opacity:"0"`, `animationName:"none"`; `probe/shot_midnight_counter_bug.png` |
| D2 | **High** | Exported PPTX chart part is invalid OOXML (no `<c:barChart>`) because `'BAR'` is used instead of `'bar'` | `export-pptx.js:226` | `ppt/charts/chart1.xml` plotArea has no chart-group element; `python-pptx` `IndexError`; A/B vs `'bar'` |
| D3 | **High** | `extract-pptx.py` crashes on any PPTX with a non-placeholder shape | `extract-pptx.py:92, 199, 281` | `ValueError: shape is not a placeholder` |
| D4 | **High** | `interactive-elements.md` CSS is never inlined by the documented pipeline → charts/KPI/timeline/donut/table/code/icon-grid render unstyled | `SKILL.md:126-142` | `grep -c` = 0 in `viewport-base.css`; side-by-side screenshots |
| D5 | Medium | Extractor silently drops **all** text elements when the run has no explicit RGB colour, yet reports "Found 0 elements" as success | `extract-pptx.py:223`, `:312` | `✓ Extracted 9 slides / ✓ Found 0 elements` |
| D6 | Medium | Extractor loses all typography (reads paragraph-level font, exporter writes run-level) | `extract-pptx.py:215-225` vs exporter XML | extracted `style` has only `align` |
| D7 | Medium | Extractor cannot recover the original layout (placeholder-only inference) | `extract-pptx.py:79-111` | layouts degrade to `content`/`bullets` |
| D8 | Medium | `presenter-mode.md` is not the presenter window that ships; it calls a nonexistent `getAllSlideContent()` and documents iframes that are never created | `presenter-mode.md:97,130,230,235,309` vs `html-template.md:431-493` | `iframes:0` in the live window |
| D9 | Low | Initial progress bar stays at 0% and the URL hash stays empty on load (`goToSlide(1)` early-returns because slide 1 already has `.active`) | `html-template.md:137-139`, `:496-500` | measured: `progressInlineStyle: null`, `hash: ""` |
| D10 | Low | `mapShape` is dead code — `PptxGenJS.ShapeType` is an instance property in 3.12.0, so `circle`/`line` never map | `export-pptx.js:79-87` | `typeof P.ShapeType === 'undefined'`; `instance ShapeType` is an object |
| D11 | Low | `http(s)` image `src` is passed to PptxGenJS `opts.path`, which expects a local file path → remote images always fail (warned, not fatal) | `export-pptx.js:140-141` | code read; `path` vs `data` semantics |
| D12 | Low | `chartType: "donut"` / `"progress"` (documented in the schema) are not implemented → silently fall back to a table | `export-pptx.js:222` vs `html-template.md:868` | code read |
| D13 | Low | No RTL/Arabic/CJK support anywhere; `letter-spacing:-0.02em` and `text-align:center` are RTL-unsafe | whole repo | `grep -ric 'rtl\|arabic\|bidi'` = 0 |
| D14 | Low | `.ns-highlight` uses a hard-coded `rgba(59,130,246,…)` fallback that matches no preset | `interactive-elements.md:627` | code read |
| D15 | Low | `Pillow` is declared as a dependency in the docstring but never imported; `rgb_to_hex` is defined and never called | `extract-pptx.py:12, 69` | grep |
| D16 | Info | `delay-700` is missing from the stagger set (100..600, 800, 1000) | `animation-library.md:64-71` | grep |
| D17 | **High** | The mandatory 4.5:1 contrast rule is never checked; **34 of 90** foreground/background token pairs fail it. `--ns-text` passes 18/18, but `--ns-text-muted` fails in 3 presets (Botanical 3.15:1, Asymmetric 4.40:1, Creative Studio 4.42:1) and `--ns-primary` fails in 6 (Teal Serenity 2.39:1 … Asymmetric 4.09:1) — and both drive **real text** (`.subtitle`, `.meta`, `.ns-bar-label`, `.ns-timeline-date`, `.ns-table th`, `a`, `.ns-compare-card h3`, `.ns-progress-value`). Separately the hard-coded `.ns-metric-change.positive #22c55e` fails in 14/18 presets and `.negative #ef4444` in **18/18** against each preset's own `--ns-bg-alt`. | `SKILL.md:291` (rule); `STYLE_PRESETS.md:40-800` (tokens); `interactive-elements.md:259-260` (hard-coded colours) | WCAG 2.x `(L1+0.05)/(L2+0.05)` computed over all 18 presets × 5 foreground tokens |
| D18 | Low | `.ns-highlight` uses a hard-coded `rgba(59,130,246,…)` fallback that matches no preset's `--ns-primary` | `interactive-elements.md:627` | code read |

---

## 12. Transplant-grade summary

**Genuinely reusable, low-risk (pure data / CSS, MIT):**
- 18 preset token blocks (19 tokens each) — a clean, well-structured design-token set. **Best asset in the repo.**
- `viewport-base.css` slide chrome + 13 layout styles — a coherent, minimal 1920×1080 scaled-deck runtime.
- 24 animation keyframes + stagger/duration/easing system + `prefers-reduced-motion` block.
- The 8 CSS-only widget styles in `interactive-elements.md` (bars, donut, KPI, progress, timeline, code, table, icon grid).
- The JSON `slide-data` schema — a clean, small intermediate representation that is genuinely valuable (it is the thing that makes both export directions possible).
- The 13 layout HTML snippets.

**Must be rewritten / not transplantable as-is:**
- `extract-pptx.py` — crashes; loses typography and layout; would need a full rewrite against python-pptx's run-level API.
- `export-pptx.js` chart path — `'BAR'` → `'bar'`; but more fundamentally, Gomrey already has a richer chart pipeline (`servers/nextjs/lib/chart-browser.ts`), so the chart branch should be dropped rather than fixed.
- The presenter window — a big number, not a preview. Needs a real implementation (or Gomrey's existing presentation components).
- The 5-phase prompt workflow in `SKILL.md` — a prompt, not code; useful as design *intent* (8px grid, 60-30-10, 40%+ whitespace, 1 idea/slide, max 3 animated elements/slide, 36px/18px minimums) but it overlaps Gomrey's own generation prompt and would need merging, not copying.

**Security posture of the donor code:** benign. No network calls at runtime except the Google Fonts CDN link. No `innerHTML` of untrusted data, no `eval`, no `fetch`, no cookies, no telemetry, no `localStorage`. The one dynamic-`write` is `pw.document.write(presenterHTML)` with a **static** string built from `document.title` (which is `esc()`-interpolated in the HTML template but **not** escaped when placed into the presenter window title — a minor XSS surface if a deck title contained markup; the title is attacker-controlled only if the deck is).
`export-pptx.js` writes files to a path the caller supplies; it performs no network I/O. `extract-pptx.py` writes image blobs into a caller-specified `--images-dir`; it performs no network I/O. Neither library validates or sanitises the JSON payload beyond `JSON.parse`.
