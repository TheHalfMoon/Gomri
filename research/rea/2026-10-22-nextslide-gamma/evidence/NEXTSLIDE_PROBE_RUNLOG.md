# NEXTSLIDE — GENERATION / EXPORT PROBE RUNLOG

**Donor:** `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56` (MIT, © 2026 Danish Rafie Ekaputra)
**Run date:** 2026-10-22
**Scratch dir:** `/private/var/folders/zj/kby34wq12tq0vy4clz9spsgm0000gn/T/opencode/nextslide-probe`
**Artifact dir:** `/Users/abdulazizalsh/work/Gomrey/research/rea/2026-10-22-nextslide-gamma/evidence/probe/`
**Synthetic topic:** "Ocean Plastic Reduction: 2026 Strategy"

> The donor clone at `/Users/abdulazizalsh/work/donor-nextslide` was **never modified**. A copy was made to the scratch dir; the only edits are explicitly marked `[PATCHED — scratch only]`.

---

## 0. Environment (exact versions)

```
$ node --version
v26.0.0
$ npm --version
11.12.1
$ python3 --version
Python 3.13.5            (/opt/homebrew/bin/python3)
$ python3 -m pip --version
pip 25.1.1 from /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/pip
$ git -C /Users/abdulazizalsh/work/donor-nextslide log -1 --format="%H %s"
90a46f933b3056d27460400c915ef268a9ec3f56 README: update GitHub username to 0xRafie
```

### 0.1 Dependencies installed (zero-cost, local, scratch/user-scope only)

```
$ cd "$SC/donor/scripts" && npm install --no-audit --no-fund
added 19 packages in 3s
$ node -e "console.log(require('pptxgenjs/package.json').version)"
3.12.0

$ python3 -m pip install --user --quiet python-pptx Pillow
$ python3 -c "import pptx, PIL; print('python-pptx', pptx.__version__); print('Pillow', PIL.__version__)"
python-pptx 1.0.2
Pillow 13.0.0
```

### 0.2 Headless browser installed (for runtime verification)

```
$ cd "$SC/pw" && npm install --no-audit --no-fund playwright-core@latest
$ npx --yes playwright@latest install chromium
Downloading Chrome for Testing 156.0.8078.4 (playwright chromium v1248) ... 185.8 MiB
Chrome for Testing 156.0.8078.4 (playwright chromium v1248) downloaded to
  /Users/abdulazizalsh/Library/Caches/ms-playwright/chromium-1248
```
UA observed: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) … HeadlessChrome/156.0.8078.4 Safari/537.36`

**LibreOffice / Keynote / PowerPoint: NOT AVAILABLE** (`which soffice libreoffice` → not found; `/Applications/LibreOffice.app` absent). Consequence: the "does it open in PowerPoint without a repair prompt" question is answered by **OOXML structure inspection + python-pptx + a second independent parse**, not by a real PowerPoint launch. See §6.3 — the chart defect *was* still provable without PowerPoint.

---

## 1. Generation method (uses the donor's own files verbatim)

Two scratch scripts were written (`build_deck.py`, `gen_specs.py`). They **do not re-implement** anything — they parse and concatenate the donor's assets:

| Asset consumed | Donor source | How |
|---|---|---|
| Core CSS | `donor/viewport-base.css` | embedded **verbatim** (verified: `v.strip() in h` → `True`) |
| Design tokens | `donor/STYLE_PRESETS.md` | the selected preset's `:root { … }` block, **verbatim** (verified for preset 2: `True`) |
| Font `<link>` | `donor/STYLE_PRESETS.md` | the preset's Google Fonts `<link>`, verbatim |
| Animations | `donor/animation-library.md` | base + easing + delays + durations + the 23 `@keyframes`/`.animate-*` blocks, verbatim |
| Reduced-motion | `donor/animation-library.md` | verbatim |
| JS controller | `donor/html-template.md` | the `## JavaScript Slide Controller` code block, **verbatim** (verified: `js in h` → `True`) |
| Slide markup | `donor/html-template.md` | the 13 layout snippets (lines 517–744) as the DOM contract |
| JSON schema | `donor/html-template.md` | `slide-data` schema (lines 748–946) |

Verification that the built HTML really contains the donor's bytes:

```
viewport-base.css embedded verbatim: True
STYLE_PRESETS.md preset2 :root embedded verbatim: True
html-template.md controller JS embedded verbatim: True
```

### 1.1 Probe harness bug found and fixed (NOT a donor defect)
My first build passed the animation **class names without the `animate-` prefix** (`"fade-up"`) while the parser keyed blocks by the full class name (`"animate-fade-up"`), so 23/24 animation CSS blocks were silently omitted → every slide rendered blank. Detected because the first screenshot was 7.4 KB (a solid colour). Fixed by (a) using full class names and (b) making the builder **hard-fail** if a requested animation block is missing:
```
if missing: raise SystemExit(f"FATAL: requested animation blocks not found in animation-library.md: {missing}")
```
All results below are from the **fixed** build. After the fix: 23 `.animate-*` rules and 23 `@keyframes ns-*` in the output; screenshots 26–66 KB.

---

## 2. Decks generated (3 presets × ≥3 layouts, same content)

```
$ python3 gen_specs.py
wrote spec_corporate-pro.json  slides=9  layouts=['title','content','section','bullets','chart','comparison','quote','timeline','content']
wrote spec_midnight-pro.json  slides=9  layouts=['title','two-column','section','chart','image-left','image-right','blank','counter','content']
wrote spec_botanical.json     slides=6  layouts=['title','bullets','two-column','comparison','quote','content']

$ python3 build_deck.py spec_corporate-pro.json deck_corporate-pro.html
wrote deck_corporate-pro.html  preset=2 'Corporate Pro'  slides=9  bytes=61285
$ python3 build_deck.py spec_midnight-pro.json deck_midnight-pro.html
wrote deck_midnight-pro.html  preset=16 'Midnight Pro'  slides=9  bytes=61119
$ python3 build_deck.py spec_botanical.json deck_botanical.html
wrote deck_botanical.html  preset=14 'Botanical'  slides=6  bytes=52848
```

**Variants:**
- **A** `deck_corporate-pro.html` — preset 2 *Corporate Pro* (light, Sora+Inter), 9 slides, 9 distinct layout types
- **B** `deck_midnight-pro.html` — preset 16 *Midnight Pro* (dark, Sora+Inter), 9 slides, 9 distinct layout types
- **C** `deck_botanical.html` — preset 14 *Botanical* (light, Cormorant Garamond+Source Sans 3), 6 slides, 6 distinct layout types
- **D** `deck_corporate-pro-fixed.html` — variant A **plus** the 10 CSS blocks from `interactive-elements.md` inlined (the fix for defect D4)

**Layout coverage across variants:** title, content, section, bullets, chart, comparison, quote, timeline, two-column, image-left, image-right, blank = **12 of 13** layouts exercised. (`image-full` not used — it requires a real photo URL, which would have introduced a remote fetch into the probe.)

### 2.1 Structural validation of the generated HTML

```
deck_corporate-pro.html: html_sections=9 json_slides=9 layouts=['title','content','section','bullets','chart','comparison','quote','timeline','content']
   theme=corporate-pro slideW=13.333 elems/slide=[3,2,2,6,2,5,2,5,2]
   controller_js=True  googlefonts_link=True
   has_notes=9  counter_marker=True
deck_midnight-pro.html: html_sections=9 json_slides=9 layouts=['title','two-column','section','chart','image-left','image-right','blank','counter','content']
   theme=midnight-pro elems/slide=[3,5,2,2,3,3,4,3,2]  has_notes=9
deck_botanical.html:    html_sections=6 json_slides=6 layouts=['title','bullets','two-column','comparison','quote','content']
   theme=botanical elems/slide=[3,6,5,5,2,2]  has_notes=6
```

---

## 3. PPTX export — the donor's own script

```
$ cd "$SC/donor/scripts" && node export-pptx.js --help

NextSlide PPTX Export
━━━━━━━━━━━━━━━━━━━━
Usage:
  node export-pptx.js <path-to-html> [output-path]
Arguments:
  path-to-html   Path to a NextSlide HTML presentation file
  output-path    (Optional) Output .pptx path. Defaults to same name as input with .pptx extension
Requirements:
  npm install pptxgenjs
Example:
  node export-pptx.js presentation.html
  node export-pptx.js deck.html my-deck.pptx

$ node export-pptx.js "$SC/deck_corporate-pro.html" "$SC/deck_corporate-pro.pptx"

📊 NextSlide PPTX Export
━━━━━━━━━━━━━━━━━━━━━━
  Input:  …/deck_corporate-pro.html
  Output: …/deck_corporate-pro.pptx

  Processing 9 slides...

  Slide 1 [title] — 3 element(s)
  Slide 2 [content] — 2 element(s)
  Slide 3 [section] — 2 element(s)
  Slide 4 [bullets] — 6 element(s)
  Slide 5 [chart] — 2 element(s)
  Slide 6 [comparison] — 5 element(s)
  Slide 7 [quote] — 2 element(s)
  Slide 8 [timeline] — 5 element(s)
  Slide 9 [content] — 2 element(s)

  ✓ Exported 9 slides to:
    …/deck_corporate-pro.pptx
EXIT=0
```

All four exports exited **0**:
```
corporate-pro export EXIT=0
midnight-pro export EXIT=0
botanical export EXIT=0
fixed export EXIT=0
```

### 3.1 Artifact sizes + sha256

| File | Bytes | sha256 |
|---|---|---|
| `deck_corporate-pro.html` | 61285 | `00227567bde9ad0c1dd60f7915e2e17bfea6e4664409e6a80c6887bfc3b1beba` |
| `deck_midnight-pro.html` | 61119 | `ca53254c556da6261e5bee20401d985a5367095076041f9ba741f150e8506b66` |
| `deck_botanical.html` | 52848 | `4fce2d030ad6074bf89a57e949c06e96120bf966fe7302bfaba7cd551da1fdf8` |
| `deck_corporate-pro-fixed.html` | 68931 | `b441f57caa3f1402e15952665c6828ace7aabdc8a2def83c84e7179cb659b691` |
| `deck_corporate-pro.pptx` | 127562 | `3eefd0aa31fb890ab8b1b3507a1c9ceeb0ca88f179b3a2688cb6c6ea5a3b27c1` |
| `deck_midnight-pro.pptx` | 129939 | `bc42cf693205660248485fc2f2308bd21495e44c055ae6648f7dab62507ec8e1` |
| `deck_botanical.pptx` | 88577 | `6842c166eb8e3c3ffe710fad77091fbff10b6237e7372b15b91acdd845c0cc38` |
| `deck_corporate-pro-fixed.pptx` | 127562 | `e25e6c6657f2b29116d1c8a755a9420b87a00e7bb7e62d34c44dc28efd088d5d` |

---

## 4. PPTX validation — is the text REAL editable text?

### 4.1 `unzip -l` / `unzip -t`

```
$ unzip -l deck_corporate-pro.pptx
Archive:  deck_corporate-pro.pptx
  Length      Date    Time    Name
---------  ---------- -----   ----
     5972  10-22-2026 03:42   [Content_Types].xml
      801  10-22-2026 03:42   docProps/core.xml
     1586  10-22-2026 03:42   docProps/app.xml
     8397  10-22-2026 03:42   ppt/theme/theme1.xml
     3515  10-22-2026 03:42   ppt/presentation.xml
     3338  10-22-2026 03:42   ppt/slides/slide1.xml
     2733  10-22-2026 03:42   ppt/slides/slide2.xml
     2436  10-22-2026 03:42   ppt/slides/slide3.xml
     6127  10-22-2026 03:42   ppt/slides/slide4.xml
     2102  10-22-2026 03:42   ppt/slides/slide5.xml
     5273  10-22-2026 03:42   ppt/slides/slide6.xml
     2474  10-22-2026 03:42   ppt/slides/slide7.xml
     5297  10-22-2026 03:42   ppt/slides/slide8.xml
     2648  10-22-2026 03:42   ppt/slides/slide9.xml
     1766  10-22-2026 03:42   ppt/notesSlides/notesSlide1.xml
     … (notesSlide2..9)
    16987  10-22-2026 03:42   ppt/embeddings/Microsoft_Excel_Worksheet1.xlsx
     318  10-22-2026 03:42   ppt/charts/_rels/chart1.xml.rels
     2549  10-22-2026 03:42   ppt/charts/chart1.xml
---------                     -------
    118058                     74 files

$ unzip -t deck_corporate-pro.pptx | tail -3
    testing: ppt/charts/chart1.xml    OK
No errors detected in compressed data of deck_corporate-pro.pptx.
```

### 4.2 python-pptx read-back

```
deck_corporate-pro.pptx  slide_count = 9  size = 12191695 x 6858000 (13.333in x 7.500in)
  slide1: shapes=3 textframes=3 nonempty_text=3 notes_len=86 notes='Speaker note for slide 1 (title). Expand with re'
  slide2: shapes=2 textframes=2 nonempty_text=2 notes_len=88 …
  slide3: shapes=2 textframes=2 nonempty_text=2 notes_len=88 …
  slide4: shapes=6 textframes=6 nonempty_text=6 notes_len=88 …
  slide5: shapes=2 textframes=1 nonempty_text=1 notes_len=86 …      ← chart slide: 1 text + 1 CHART
  slide6: shapes=5 textframes=5 nonempty_text=5 notes_len=91 …
  slide7: shapes=2 textframes=2 nonempty_text=2 notes_len=86 …
  slide8: shapes=5 textframes=5 nonempty_text=5 notes_len=89 …
  slide9: shapes=2 textframes=2 nonempty_text=2 notes_len=88 …
  TOTAL text frames=28  with text=28  shape kinds={'AUTO_SHAPE (1)': 28, 'CHART (3)': 1}
  XML <a:t> text runs = 28   <p:pic> images = 0   chart parts = 1   media files = ['ppt/media/']

deck_midnight-pro.pptx  slide_count = 9
  TOTAL text frames=24  with text=24  shape kinds={'AUTO_SHAPE (1)': 24, 'CHART (3)': 1, 'PICTURE (13)': 2}
  XML <a:t> text runs = 24   <p:pic> images = 2   chart parts = 1
  media files = ['ppt/media/image-5-1.png','ppt/media/image-5-2.svg','ppt/media/image-6-1.png','ppt/media/image-6-2.svg']

deck_botanical.pptx     slide_count = 6
  TOTAL text frames=23  with text=23  shape kinds={'AUTO_SHAPE (1)': 23}
  XML <a:t> text runs = 23   <p:pic> images = 0   chart parts = 0
```

### 4.3 Raw XML evidence of real text runs

```
$ python3 -c "…re.findall(r'<a:t>([^<]*)</a:t>', slide1.xml)"
['Ocean Plastic Reduction', '2026 Strategy', 'Global Marine Resilience Initiative · October 2026']
```
Full run properties of the title run (proof it is a live, styled text run — not a picture):
```xml
<a:r><a:rPr lang="en-US" sz="4400" b="1" dirty="0">
  <a:solidFill><a:srgbClr val="1E293B"/></a:solidFill>
  <a:latin typeface="Sora" pitchFamily="34" charset="0"/>…
</a:rPr><a:t>Ocean Plastic Reduction</a:t></a:r>
```
Shape geometry on slide 6: `<a:prstGeom prst="rect">` × 5, `<p:sp>` count 5 — native autoshapes, not images.

### 4.4 ✅ VERDICT: **PPTX text is REAL, editable text — YES.**
- 28 / 24 / 23 `<a:t>` text runs across the three decks; **every** python-pptx text frame is non-empty.
- **Zero** rasterised slide images (`<p:pic>` = 0 on the text decks; = 2 on the deck that legitimately contains 2 inline SVG illustrations).
- Fonts, sizes, weights and colours are written as run properties (`sz`, `b`, `<a:srgbClr>`, `<a:latin typeface>`) → editable in PowerPoint/Sheets/Keynote.
- Speaker notes are real PPTX notes slides (`ppt/notesSlides/notesSlideN.xml`), one per slide.
- Slide size is exactly 13.333in × 7.5in (16:9), matching `meta.slideWidth/Height`.

### 4.5 ❌ BUT the CHART part is invalid OOXML (defect D2)

```
$ python3 …  # scan every chart part for a chart-group element
deck_botanical.pptx            slides= 6 a:t_runs= 23 pics=0 charts=0 INVALID_CHART=[]                   notesSlides=6 size=88577B
deck_corporate-pro.pptx        slides= 9 a:t_runs= 28 pics=0 charts=1 INVALID_CHART=['ppt/charts/chart1.xml'] notesSlides=9 size=127562B
deck_corporate-pro-fixed.pptx  slides= 9 a:t_runs= 28 pics=0 charts=1 INVALID_CHART=['ppt/charts/chart1.xml'] notesSlides=9 size=127562B
deck_midnight-pro.pptx         slides= 9 a:t_runs= 24 pics=2 charts=1 INVALID_CHART=['ppt/charts/chart1.xml'] notesSlides=9 size=129939B
```

The offending XML (`ppt/charts/chart1.xml`):
```
<c:chartSpace …><c:chart><c:autoTitleDeleted val="1"/><c:plotArea>
  <c:layout/><c:catAx>…</c:catAx><c:valAx>…</c:valAx>
</c:plotArea>
```
`has <c:barChart>: False` — a `<c:plotArea>` with **no chart-group element** is invalid per ECMA-376; PowerPoint will show a repair prompt and python-pptx cannot even read it:
```
File ".../pptx/chart/chart.py", line 86, in chart_type
    first_plot = self.plots[0]
File ".../pptx/chart/chart.py", line 276, in __getitem__
    xChart = xCharts[index]
IndexError: tuple index out of range
```

**Root cause, proven by A/B test.** `export-pptx.js:226`:
```js
const type = chartType === 'bar-horizontal' ? 'BAR' : 'BAR';   // ← no-op ternary, and 'BAR' is wrong
```
pptxgenjs 3.12.0 `ChartType` constants are **lowercase**:
```
$ node -e "const P=require('pptxgenjs'); console.log(JSON.stringify(P.ChartType))"
{ "area": "area", "area3d": "area3d", "bar": "bar", … }
```
A/B with the same installed library:
```
t_bar_upper.pptx  ('BAR') -> has <c:barChart>: False | plotArea first tags: ['layout','catAx','axId','scaling','orientation','delete']
t_bar_lower.pptx  ('bar') -> has <c:barChart>: True  | plotArea first tags: ['layout','barChart','barDir','grouping','varyColors','ser']
```
→ `'BAR'` writes a corrupt chart part; `'bar'` writes a valid one.

**Also:** `export-pptx.js:79-87` `mapShape()` reads `PptxGenJS.ShapeType`, which is `undefined` on the class in 3.12.0 (it is an instance property) → the `rect`/`circle`/`line` mapping is dead code and always falls back to `'rect'`:
```
static ShapeType: undefined      instance ShapeType: object
static ChartType: undefined      instance ChartType: object bar
```

---

## 5. Runtime verification of the HTML in headless Chromium

```
$ node verify.js
=== ENVIRONMENT ===
UA: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) … HeadlessChrome/156.0.8078.4 Safari/537.36
BroadcastChannel available: true

=== INITIAL STATE ===
{ slides: 9, activeIdx: 0, hash: '', counter: '1 / 9',
  scaleVar: '0.8333333333333334', slidePx: [1600, 900] }

=== KEYBOARD NAVIGATION (ArrowRight) ===
{ activeSlide: '2', activeLayout: 'two-column', hash: '#slide-2',
  progressWidth: '22.2222%', counter: '2 / 9' }
after End -> 9
after Home -> 1
after ArrowLeft (clamped to 1) -> 1

=== PRINT MEDIA (emulate print) ===
{ slideCount: 9, slide0_position: 'relative', slide0_visibility: 'visible', slide0_opacity: '1',
  navHidden: 'none', counterHidden: 'none', notesHidden: 'none', h1Opacity: '1' }

=== PAGE ERRORS ===
(none)
```
✅ Navigation, hash routing, progress bar, counter, 1920×1080 letterbox scaling and the `@media print` rules all work as documented.

### 5.1 ❌ DEFECT D1 — `.animate-counter-up` is permanently invisible (measured)
```
=== ANIMATE-COUNTER-UP SLIDE (slide 8, layout=counter) ===
{ present: true, textContent: '73%', dataTarget: '73',
  computedOpacity: '0', computedVisibility: 'visible',
  animationName: 'none', inlineStyleOpacity: '(none)',
  siblingWithoutClass: { text: '0', opacity: '1' },
  slideActive: '8' }
```
The element with the class is at `opacity:0`; its sibling **without** the class is at `opacity:1`. The `73%` value is **absent from the rendered slide** (`probe/shot_midnight_counter_bug.png`).
Cause: `animation-library.md:21-26` sets `opacity:0` on every `[class*="animate-"]`; `animate-counter-up` has **no `@keyframes`** and is **not in the emphasis exemption list** (`:38-43`).
The JS *does* update the text (0→73), so the number is correct but invisible.

### 5.2 ⚠ DEFECT D8 — the presenter window has NO slide preview (measured)
```
=== PRESENTER MODE (P) ===
{ title: 'Presenter — Ocean Plastic Reduction: 2026 Strategy — Midnight Pro',
  hasCurrentNum: true, hasNextNum: true,
  currentNumText: '8', nextNumText: '9',
  notesText: 'Speaker note for slide 8 (counter). Expand with regional detail and cite the 2026 audit.',
  counter: '8 / 9', timer: '00:00:00',
  iframes: 0, imgTags: 0,
  pCurrentHTML: '<span class="p-current-label">Current Slide</span><span class="p-slide-num" id="p-cur-num">8</span>',
  pNextHTML:    '<span class="p-next-label">Next</span><span class="p-slide-num" id="p-next-num">9</span>' }
after presenter Next -> deck active slide = 9
```
- ✅ The popup opens, notes + timer + counter work, and **presenter→deck navigation over BroadcastChannel works** (deck advanced 8→9).
- ❌ `iframes: 0`, `imgTags: 0` — the "current slide" and "next slide" panes contain **only a large slide number**, no visual preview. `README.md:18`'s "next-slide preview" is false for the shipped code.
- `presenter-mode.md` documents a *different* window (iframes, `#current-slide-content`, and a call to `getAllSlideContent()` which **does not exist anywhere in the repo**).

### 5.3 ❌ DEFECT D4 — interactive-element CSS is never inlined (measured)
Per `SKILL.md:126-142`, the `<style>` block should contain: preset vars, `viewport-base.css`, animation keyframes, `@media print`, preset-specific styling. **`interactive-elements.md`'s CSS is not in that list, and `viewport-base.css` contains none of it:**
```
$ for c in ns-chart-bar-h ns-bar-row ns-bar-track ns-bar-fill ns-metrics ns-metric-card \
           ns-metric-value ns-timeline ns-timeline-item ns-code-block ns-table ns-icon-grid \
           ns-donut ns-progress-group; do … grep -c "\.$c" viewport-base.css; done
ns-chart-bar-h      viewport-base.css=0  interactive-elements.md=1
ns-bar-row          viewport-base.css=0  interactive-elements.md=1
ns-bar-track        viewport-base.css=0  interactive-elements.md=1
ns-bar-fill         viewport-base.css=0  interactive-elements.md=2
ns-metrics          viewport-base.css=0  interactive-elements.md=1
ns-metric-card      viewport-base.css=0  interactive-elements.md=1
ns-metric-value     viewport-base.css=0  interactive-elements.md=1
ns-timeline         viewport-base.css=0  interactive-elements.md=13
ns-timeline-item    viewport-base.css=0  interactive-elements.md=1
ns-code-block       viewport-base.css=0  interactive-elements.md=1
ns-table            viewport-base.css=0  interactive-elements.md=5
ns-icon-grid        viewport-base.css=0  interactive-elements.md=1
ns-donut            viewport-base.css=0  interactive-elements.md=3
ns-progress-group   viewport-base.css=0  interactive-elements.md=1
```
**A/B proof** (same content, same preset; only difference = the 10 CSS blocks inlined):

| Variant | Chart slide screenshot | Bytes | Timeline slide | Bytes |
|---|---|---|---|---|
| A — per `SKILL.md` | `probe/shot_chart_UNSTYLED_per_SKILL.md.png` — text list, **no bars** | 50209 | `probe/shot_timeline_UNSTYLED.png` | 68845 |
| D — CSS inlined | `probe/shot_chart_STYLED_with_interactive_CSS.png` — **bars, tracks, labels** | 46360 | `probe/shot_timeline_STYLED.png` | 61278 |

The KPI-card slide (`probe/shot_midnight_counter_bug.png`) shows the same defect: no card background, no grid.

**Fix (verified):** inline the 10 `interactive-elements.md` CSS blocks (7,646 bytes) into the deck's `<style>`.

---

## 6. PPTX import / extraction — **FAILS as shipped**

### 6.1 As-shipped script → hard crash
```
$ cp /Users/abdulazizalsh/work/donor-nextslide/scripts/extract-pptx.py ./extract-pptx.py.PRISTINE
$ python3 extract-pptx.py.PRISTINE deck_corporate-pro.pptx > pristine_text.out 2> pristine_text.err
EXIT=1
--- stdout (first 5 lines) ---
(empty)
--- stderr (tail) ---
Traceback (most recent call last):
  File ".../extract-pptx.py.PRISTINE", line 463, in <module>
    main()
  File ".../extract-pptx.py.PRISTINE", line 443, in main
    data = extract_presentation(pptx_path, images_dir)
  File ".../extract-pptx.py.PRISTINE", line 281, in extract_presentation
    hasattr(shape, "placeholder_format")
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../pptx/shapes/base.py", line 151, in placeholder_format
    raise ValueError("shape is not a placeholder")
ValueError: shape is not a placeholder
```
Full log: `probe/extract_pptx_PRISTINE_crash.log`.

**Minimal reproducer:**
```python
>>> sh = prs.slides[0].shapes[0]
>>> sh.is_placeholder
False
>>> hasattr(sh, "placeholder_format")
ValueError: shape is not a placeholder      # hasattr only swallows AttributeError
```
Offending sites: `extract-pptx.py:92`, `:199`, `:281`.
**It crashes on the donor's own export output, on a trivial python-pptx fixture, and therefore on essentially every real-world PPTX:**
```
$ python3 extract-pptx.py fixture_pythonpptx.pptx
ValueError: shape is not a placeholder
```

### 6.2 `[PATCHED — scratch only]` — 3 local edits to reach the intended behaviour
1. `hasattr(x, "placeholder_format")` → `getattr(x, "is_placeholder", False)` (3 sites)
2. `para.font.color.rgb` → wrapped in `try/except AttributeError` (line 223)

### 6.3 Result after patching — still broken, in three more ways
```
$ python3 donor/scripts/extract-pptx.py deck_corporate-pro.pptx
  ⚠ Slide 1, shape 0: no .rgb property on color type '_NoneColor'
  ⚠ Slide 1, shape 1: no .rgb property on color type '_NoneColor'
  … (32 warnings) …
  ⚠ Slide 5, shape 1: tuple index out of range
  ✓ Extracted 9 slides
  ✓ Found 0 elements          ←← ZERO. Reported as success.
```
With patch #1 only (before patch #2): `✓ Found 0 elements` — **every element silently dropped** because `para.font.color.rgb` raises `AttributeError` for `_NoneColor`, the per-shape `try/except` (line 312) swallows it, and the whole shape is discarded. The script still prints "✓ Extracted 9 slides".

With both patches:
```
$ python3 donor/scripts/extract-pptx.py deck_midnight-pro.pptx --format json --images-dir ./extracted-images > extract_midnight.json
  ⚠ Slide 4, shape 1: tuple index out of range
  ✓ Extracted 9 slides
  ✓ Found 26 elements
  ✓ Saved 2 images to ./extracted-images
EXIT=0
```

**Extraction output format** (the intended shape):
```json
{
  "meta": { "title": "deck_midnight-pro", "slideWidth": 13.333, "slideHeight": 7.5,
            "slideCount": 9, "author": "Gomrey Research Probe", "date": "2026-10-22" },
  "slides": [
    { "slideNumber": 1, "layout": "content",
      "elements": [
        { "type": "text",
          "position": { "x": "10.0%", "y": "28.0%", "w": "80.0%", "h": "22.0%" },
          "content": "Ocean Plastic Reduction", "role": "body",
          "style": { "align": "center" } } ] } ] }
```
- `position` = percent strings; `role` ∈ title/subtitle/body/caption/label/footnote; `style` = fontSize(pt)/fontFace/bold/italic/color/align.
- `--format text` (default) prints a human-readable markdown-ish digest to stdout (`# Title`, `## Slide N [layout]`, `[role] (style): content`, `Notes: …`); `--format json` prints the JSON above. Diagnostics always go to **stderr**.
- `--images-dir` writes image blobs as `slide{N}_img{idx}.{ext}` (verified: `extracted-images/slide5_img0.png`, `slide6_img2.png`, 1594 B each).

**Three remaining defects, all measured:**
1. **Typography is lost.** Exported runs carry properties at *run* level (`<a:rPr sz="4400" b="1">` + `<a:latin typeface="Sora">`, and **no `<a:defRPr>` at all**), but the extractor reads *paragraph* level (`para.font.size`, `para.font.name`, `para.font.bold`, `para.font.color.rgb`, lines 215–225). Result: the extracted `style` contains **only `align`** — `fontSize`, `fontFace`, `bold`, `color` are all gone.
2. **Layout is not recovered.** `guess_layout()` (lines 79–111) only recognises placeholders. Exported text boxes have no placeholders, so the original layouts are lost:
   ```
   authored:  ['title','two-column','section','chart','image-left','image-right','blank','counter','content']
   extracted: ['content','bullets','content','content','image-left','image-left','bullets','content','content']
   ```
3. **Chart shapes are dropped** (`IndexError` from the corrupt `'BAR'` chart part, §4.5).
4. **`role` is always `"body"`** for exporter output (placeholder-only inference).

**Round-trip verdict:** `export-pptx.js` → `extract-pptx.py` is **not** a working round-trip. Geometry survives; typography, layout, role and charts do not.

---

## 7. Other commands run / failures encountered

| Command | Result |
|---|---|
| `git clone` / `git log` (donor) | OK — 5 commits, 14 files ever, no tests |
| `npm install` in `scripts/` | OK — 19 packages, 3s, pptxgenjs 3.12.0 |
| `pip install --user python-pptx Pillow` | OK — python-pptx 1.0.2, Pillow 13.0.0 |
| `npx playwright install chromium` | OK — Chrome for Testing 156.0.8078.4, 185.8 MiB |
| `node export-pptx.js <html> <pptx>` ×4 | OK, exit 0 |
| `python3 extract-pptx.py <pptx>` (as shipped) | ❌ **FAILED** — `ValueError: shape is not a placeholder`, exit 1 |
| `python3 extract-pptx.py <pptx>` (2 local patches) | ⚠ exit 0 but **0 elements** (before patch 2) / 26 elements with lost typography + lost layouts (after) |
| `unzip -t` on all 4 pptx | OK — no CRC errors |
| python-pptx read-back on all 4 pptx | OK — 9/9/6/9 slides, all text frames non-empty |
| LibreOffice / PowerPoint / Keynote | ❌ **NOT AVAILABLE** — chart-validity proven structurally instead |
| `soffice`/`libreoffice` on PATH | not found; `/Applications/LibreOffice.app` absent; no brew cask installed |
| Remote network during rendering | Google Fonts `<link>` is present; headless Chromium had no font network access, so screenshots use fallback sans. **This does not affect any conclusion** (all defects are DOM/CSS/JS/OOXML-level, not font-dependent). |

---

## 8. Staged artifacts (`evidence/probe/`) — all < 2 MB

```
     52848  ./deck_botanical.html
     88577  ./deck_botanical.pptx
     68931  ./deck_corporate-pro-fixed.html
    127562  ./deck_corporate-pro-fixed.pptx
     61285  ./deck_corporate-pro.html
    127562  ./deck_corporate-pro.pptx
     61119  ./deck_midnight-pro.html
    129939  ./deck_midnight-pro.pptx
      3331  ./extract_corporate-pro.txt
     11238  ./extract_midnight-pro.json
       571  ./extract_pptx_PATCHED_warnings.log
      1078  ./extract_pptx_PRISTINE_crash.log
      1594  ./extracted-images/slide5_img0.png
      1594  ./extracted-images/slide6_img2.png
     46360  ./shot_chart_STYLED_with_interactive_CSS.png
     50209  ./shot_chart_UNSTYLED_per_SKILL.md.png
     49235  ./shot_midnight_blank_bento.png
     26547  ./shot_midnight_counter_bug.png
     66068  ./shot_midnight_image-left.png
     32836  ./shot_midnight_title.png
     57569  ./shot_midnight_two-column.png
     32812  ./shot_presenter_window.png
     61278  ./shot_timeline_STYLED.png
     68845  ./shot_timeline_UNSTYLED.png
$ find . -type f -size +2M -print
(no output — nothing oversized)
```

### 8.1 sha256 of every staged file
```
4fce2d030ad6074bf89a57e949c06e96120bf966fe7302bfaba7cd551da1fdf8  ./deck_botanical.html
6842c166eb8e3c3ffe710fad77091fbff10b6237e7372b15b91acdd845c0cc38  ./deck_botanical.pptx
b441f57caa3f1402e15952665c6828ace7aabdc8a2def83c84e7179cb659b691  ./deck_corporate-pro-fixed.html
e25e6c6657f2b29116d1c8a755a9420b87a00e7bb7e62d34c44dc28efd088d5d  ./deck_corporate-pro-fixed.pptx
00227567bde9ad0c1dd60f7915e2e17bfea6e4664409e6a80c6887bfc3b1beba  ./deck_corporate-pro.html
3eefd0aa31fb890ab8b1b3507a1c9ceeb0ca88f179b3a2688cb6c6ea5a3b27c1  ./deck_corporate-pro.pptx
ca53254c556da6261e5bee20401d985a5367095076041f9ba741f150e8506b66  ./deck_midnight-pro.html
bc42cf693205660248485fc2f2308bd21495e44c055ae6648f7dab62507ec8e1  ./deck_midnight-pro.pptx
06a1c321e51f361643461493abdd2bff2e8a5f2d0d42fb2bb14108d3e0cebdac  ./extract_corporate-pro.txt
56d236f3680a8c3ae551afb0010c5f02ec253deaea275cb0bfc4e6e100d7345d  ./extract_midnight-pro.json
96511ee5d8c68da4598dabfbf911914b54daf87d603018d83366da7af34ef6eb  ./extract_pptx_PATCHED_warnings.log
405a0575c8ce2d7c8f3cabc724f72d5d6734c3a5104c0a4dca27cd6d7e4e3e09  ./extract_pptx_PRISTINE_crash.log
0db2447fffb75ae48f57c711c26783f619591d48b1713f997a7bc34626c95ff1  ./extracted-images/slide5_img0.png
0db2447fffb75ae48f57c711c26783f619591d48b1713f997a7bc34626c95ff1  ./extracted-images/slide6_img2.png
e5337ea74713837f167638138f98a5d7a62d3eeb88d659185756f9d0e67328e2  ./shot_chart_STYLED_with_interactive_CSS.png
a3cf3cae1ab7bd10e7886bcf1cd40c3f96da08bd278e716f45ccade83bca2de1  ./shot_chart_UNSTYLED_per_SKILL.md.png
322d0b49f8fa87b300965c4d156043998347f60c5eb3773d62665160d1168b74  ./shot_midnight_blank_bento.png
a8b720fab731bdc0b92838a790605421ccacf5c9f9da86b9074930e94b724502  ./shot_midnight_counter_bug.png
33fce89ae8d9bc305d56c0ed7b3c6e8b3d69b470ea27a1c8fc182933361d8ce9  ./shot_midnight_image-left.png
8ccd2eeecae0b329356470c617123faf80e1ca5b32d366780ddc56db186adac2  ./shot_midnight_title.png
84b7e59a5f5e757cdce552a2c1393d951a321770c28721f8a82754743cde1f51  ./shot_midnight_two-column.png
16e29f5c562b87910b85729b0611eb5c3517545162b409cdd46fc4d597eb7d78  ./shot_presenter_window.png
1b7420fada2da88cb63f95b912dbeb8b1687d0e3cbd7b4757d39f11d8ce5a81a  ./shot_timeline_STYLED.png
5a0628d04aba4672f0ac7a90a8ad7f60d942883a7cfb7c7b7d1032841d2cc59e  ./shot_timeline_UNSTYLED.png
```

---

## 9. Summary of probe outcomes

| # | Probe | Outcome |
|---|---|---|
| C1 | Generate a single-file HTML deck for a synthetic topic using the donor's own instructions/scripts | ✅ **PASS** — 4 decks built from the donor's verbatim CSS/JS/presets, all render in Chromium, no console errors |
| C2 | Run the PPTX export script → real .pptx; verify it opens/validates; report slide count, text frames, editable-vs-raster | ✅ **PASS (text)** — 4 real .pptx, 28/24/23 `<a:t>` runs, 0 rasterised slides, 9/9/6/9 slides, notes on every slide. ⚠ **chart part invalid** (`'BAR'` bug, proven by A/B) |
| C3 | Run the PPTX import/extraction on a PPTX; report the output format | ❌ **FAIL (as shipped)** — `ValueError: shape is not a placeholder` on every PPTX. With 2 local patches it runs but drops all typography, all original layouts and the chart, and silently reported "0 elements" as success. Format documented in §6.3. |
| C4 | ≥2 style presets and ≥3 layouts applied to the same content, saved separately | ✅ **PASS** — 3 presets (Corporate Pro / Midnight Pro / Botanical) + 1 CSS-fixed variant; 12 of the 13 layouts exercised; 4 separate artifacts |
| C5 | Report exact commands, versions, sizes, outputs, failures | ✅ this document |
| C6 | Install only zero-cost local packages; mark paid/unavailable inputs as BLOCKED | ✅ pptxgenjs, python-pptx, Pillow, playwright-core + chromium all installed free. ⚠ **BLOCKED: no PowerPoint/LibreOffice/Keynote available** → "opens without repair prompt" could not be tested by launching a real office suite; verified structurally instead. ⚠ Google Fonts CDN not reachable in the headless browser → screenshots use fallback sans (does not affect any conclusion). |
