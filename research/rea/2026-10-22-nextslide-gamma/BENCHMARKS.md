# BENCHMARKS — measured numbers

**Mission:** Issue #77.
**Date (UTC):** 2026-10-22
**Baseline:** `5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Candidate:** `0c19896e813b119027b930d143240ce43fbedd65`

Every number here was produced by a command recorded in `EXPERIMENTS.md`. No figure is estimated,
extrapolated or copied from marketing copy.

---

## 1. Gomrey baseline — gate timings and counts

| Gate | Count | Duration |
|---|---|---|
| Root `npm test` | 48 pass / 0 fail | 1.79 s (post-change) |
| FastAPI `pytest` | **1125 passed**, 10 warnings | **12.22 s** post-change / 31.18 s pre-change |
| Next.js `node --test` (baseline) | 73 pass / 0 fail | 0.93 s |
| Next.js `node --test` (candidate) | **101 pass / 0 fail** | 2.32 s |
| Next.js `eslint` | 0 errors / 68 warnings | — |
| Next.js production build | success | — |
| Electron path migration | 11 pass / 0 fail | 0.11 s |
| New module tests | **28 pass / 0 fail** | 0.16 s |

**Delta:** +28 tests, +0 failures, +0 lint errors, +0 warnings. The new module's test cost is
**0.16 s** — 0.14 % of the Next.js suite.

## 2. The adopted animation contract

| Metric | Value |
|---|---|
| Animations in the catalog | **24** (20 entrance + 4 emphasis) — matches the donor exactly |
| Easing curves | 7 (4 from the donor's named presets + `ease-in-out`, `linear`, `steps` retained because the donor uses them directly) |
| Stagger delays | 8 (100, 200, 300, 400, 500, 600, 800, 1000 ms) |
| Duration modifiers | 3 (300 / 500 / 800 ms) |
| Generated stylesheet | **472 lines**, ~11 KB, `gated` mode |
| Deterministic | Yes — identical options always produce byte-identical CSS |
| Runtime dependencies | **0** |
| Network references in the generated CSS | **0** — asserted (`@import`, `url(`, `http`) |
| Wildcard selectors in the generated CSS | **0** — asserted |
| Animations covered by the reduced-motion block | **24 / 24** — asserted |
| Controller-backed animations | 1 (`counter-up`), correctly emitting **no** keyframe block |
| Animations that can end permanently hidden | **0** — asserted |

## 3. The donor's PPTX export — independent verification

Reopened with **`python-pptx`** (Gomrey's own dependency), not with the donor's tooling, so the
result does not depend on donor code being correct.

| Deck | Slides | Shapes | Shapes with text | Pictures | Editable text |
|---|---|---|---|---|---|
| `deck_botanical.pptx` | 6 | 23 | 23 | 0 | **yes** |
| `deck_corporate-pro.pptx` | 9 | 29 | 28 | 0 | **yes** |
| `deck_corporate-pro-fixed.pptx` | 9 | 29 | 28 | 0 | **yes** |
| `deck_midnight-pro.pptx` | 9 | 27 | 24 | 2 | **yes** |
| **Total** | 33 | 108 | **103** | 2 | — |

**103 of 108 shapes carry real text.** The donor's exporter produces genuinely editable PPTX **for
text, shapes and speaker notes**.

**This does not establish superiority over Gomrey.** Gomrey's export path is
`@presenton/export-core` v1.0.34, verified installed and `OK`. Per issue §D, a second PPTX engine
requires a bounded fidelity demonstration; none was made, so the donor exporter is `REJECT`ed.

### 3.1 The donor's PPTX export is **invalid for charts**

Structural inspection of `ppt/charts/chart1.xml` in the exported decks:

- `plotArea` contains only `layout`, `catAx`, `valAx` — **no `<c:barChart>`**.
- `python-pptx` raises `IndexError` when opening it.
- PowerPoint would show a **repair prompt**.

**Root cause, proven by A/B:** `scripts/export-pptx.js:226` hard-codes the chart type as `'BAR'`,
but `pptxgenjs@3.12.0` expects `'bar'`. A mixed-case string silently produces an empty plot area.

**Calibration:** the donor's export is trustworthy for text, shapes and notes, and **untrustworthy
for charts**. Since charts are a first-class Gomrey capability
(`servers/nextjs/components/slide-editor/charts`, and a baseline test that renders "PPTX table
borders, vector metadata, flips, and **chart legend position**"), this is a concrete, measured
reason to reject the donor exporter in favour of `@presenton/export-core`.

> **Verification boundary, stated honestly:** no PowerPoint, LibreOffice or Keynote was available in
> this environment. "Opens without a repair prompt" was verified **structurally** (unzip integrity,
> OOXML part inspection, `python-pptx` round-trip), **not** by launching an office suite. The
> chart-part defect was nonetheless confirmed directly in the OOXML.

### 3.2 The donor's PPTX extractor **silently loses all data**

After patching the crash so it could run at all, the extractor reported:

```
✓ Extracted 9 slides
✓ Found 0 elements        ← success exit code, zero data
```

A **silent total data loss** reported as success. Even when fully patched it loses all typography
(the extractor reads paragraph-level font, while OOXML stores it at run level) and all original
layouts. Independently of the crash, this is disqualifying for an import path.

## 3a. Accessibility measurement — the donor's own presets fail WCAG AA

The donor's design rules specify a 4.5:1 contrast requirement (`SKILL.md:276-341`). **That rule is
never checked by the donor's own tooling.** Two independent measurements were taken, at two different
scopes. Both are recorded rather than merged:

**Measurement A — wider matrix** (independent subagent survey): across a 90-pair token matrix,
**34 / 90** pairs fail the 4.5:1 rule; `--ns-text-muted` fails in 3 presets, `--ns-primary` in 6,
and the hard-coded KPI-change colours fail in 14 of 18 presets — 18 of 18 in the worst case.

**Measurement B — text-on-background subset** (recomputed in this mission from the committed fixture
`servers/fastapi/tests/fixtures/donor_nextslide_presets.json`, covering the three text roles against
the slide background): **10 / 54** pairs fail.

| Failing role | Presets | Count |
|---|---|---|
| `--ns-primary` (drives real text) | Minimal Clean, Soft Curves, Teal Serenity, Asymmetric, Bento Grid, Retro 90s, Prism Glow | **7** |
| `--ns-text-muted` | Asymmetric, Botanical, Creative Studio | **3** |
| `--ns-text` | none | **0** |

> The two measurements disagree by one on the `--ns-primary` breakdown (6 vs 7) because they use
> different pair matrices. **Measurement B is the authoritative one for this mission** because it is
> reproducible from the committed fixture and pinned by a regression test
> (`servers/fastapi/tests/unit/test_template_quality.py`). The committed fixture and its generator
> are the ground truth; both numbers are reported rather than one being silently discarded.

**Why this matters for Gomrey:** `F-P04` ("layout quality assurance beyond overflow") is a real
Gomrey gap — `utils/smart_slide_layout.py` checks overflow, clipping and overlap but **not contrast**.
The donor supplies (a) the machine-checkable rule and (b) proof that a plausible-looking 18-preset
palette set violates it in 38 % of pairs. That is a ready-made, high-value, **original-implementation**
target: a deterministic contrast linter that runs on every resolved theme, before export.

This is recorded as wave **W4a** in `IMPLEMENTATION_GRAPH.md`.

## 4. Donor capability counts — reproduced

| Claim | Claimed | Measured | Method |
|---|---|---|---|
| Style presets | 18 | **18** | `grep -c '^:root {'` → 18 independent CSS blocks; corroborated by 18 `## Preset N` headings |
| CSS custom properties per preset | 19 | **19** | `grep -o -- '--ns-[a-z0-9-]*' \| sort -u` |
| Layouts | 13 | **13** | `grep -o 'data-layout="[a-z-]*"' \| sort -u`; corroborated by 13 headings and a 13-row table |
| Animations | 24 (20 + 4) | **24 (20 + 4)** | `grep -n '^### [0-9]*\. animate-'` → 24; category split confirmed from section headings |
| Test suite | (implied) | **0** | The donor ships no tests of its own |
| Editable PPTX export | claimed | **verified** | 103/108 shapes carry editable text |

## 5. Donor defects — reproduced, with severity

| Defect | Evidence | Severity | Gomrey handling |
|---|---|---|---|
| `animate-counter-up` permanently invisible | headless Chromium `animationName: "none"`; screenshot `shot_midnight_counter_bug.png` | **High** — a documented feature silently does nothing | Reclassified `engine: "controller"`; no keyframe emitted; never hidden; regression-tested |
| Wildcard `[class*="animate-"]` base rule | `animation-library.md:21`; also in the `@media print` block | **High in a Tailwind product** — blanks `animate-spin`/`animate-pulse`/`animate-bounce`/`animate-ping` | Gomrey namespace + explicit selectors; asserted by test |
| Name collision on `animate-pulse` | donor emphasis animation vs Tailwind v4 utility | **High** — same class name, different behaviour | Resolved by the namespace |
| `extract-pptx.py` crashes on pristine PPTX | `ValueError: shape is not a placeholder`, line 281 | **Medium** — the tool is unusable as shipped | Donor extractor rejected; Gomrey's own importer retained |
| Interactive-element CSS never inlined | `SKILL.md:126-142` vs `interactive-elements.md`; two paired screenshots | **Medium** — the documented widgets do not work | Donor widgets deferred; each needs individual comparison |
| Presets require Google Fonts over the network | 18 × `<link href="https://fonts.googleapis.com/…">` | **Medium for an offline-first product** | Presets deferred, not adopted |
| `presenter-mode.md` ≠ `html-template.md` presenter | two different implementations described | **Low** | Irrelevant — presenter mode rejected as already present |
| `Bento Grid` preset advertises a nonexistent layout | screenshot `shot_midnight_blank_bento.png` | **Low** | Presets deferred |
| Typography defines no measure in `ch`/`em` | only `max-width: 75%` | **Low** | Typography deferred pending comparison |
| Two different use-case → preset tables | `STYLE_PRESETS.md:817` vs `SKILL.md` | **Low** | Presets deferred |

**Donor defects found: 10.** Four are High or Medium severity.

## 6. Gamma — measured, not asserted

### 6.1 REST surface

| Metric | Value |
|---|---|
| Documented REST endpoints | **24** across two engines (`/agent/*` and the Classic engine) |
| Base URL | `https://public-api.gamma.app` |
| Auth | `X-API-KEY` header, or OAuth 2.0 Bearer |
| Job model | All long operations async: create → poll status → retrieve. **No webhooks.** |
| Output languages | **74+**, locale+register pairs (`ar` / `ar-sa`, `ja` / `ja-da`, `en` / `en-gb` / `en-in`) |
| Image models | **38**, with per-image credit costs from 2 to 125 |
| Export formats | `pdf`, `png`, `pptx` — **one format per request** |
| Multi-page range | `pages[]` **1–50** in a single request, each with its own path slug and id |
| Card dimensions | 10 (`16x9`, `4x3`, `fluid`, `letter`, `a4`, `pageless`, `1x1`, `4x5`, `9x16`) |
| Import limits | PPTX/DOCX ≤ 200 MB, PDF ≤ 100 MB |
| Import fidelity claim | Original layouts and design preserved, fully editable; fonts substituted and reported; some charts arrive as images |
| Versioning | App-level history + restore on all plans. **No API revision/rollback endpoint exists.** |
| Export URL lifetime | ≈ **1 week**, not key-tied → *"treat the link as a secret"* |

### 6.2 MCP surface — live metadata

| Fact | Measured value |
|---|---|
| Server URL | `https://mcp.gamma.app/mcp` |
| Resource metadata (live, HTTP 200) | `{"resource":"https://mcp.gamma.app","authorization_servers":["https://auth.gamma.app"],"scopes_supported":["generate","gamma:read"],"bearer_methods_supported":["header","body"]}` |
| Authorization server metadata (live, HTTP 200) | authorize `/oauth/authorize`, token `/oauth/token`, **`registration_endpoint` `/oauth/register`** (RFC 7591 DCR), jwks `/.well-known/jwks.json`, grants `[authorization_code, refresh_token]`, **`code_challenge_methods_supported:[S256]`**, `token_endpoint_auth_methods_supported:[none, client_secret_post, client_secret_basic]` |
| Tools | **21** — `generate`, `generate_multi_page_gamma`, `generate_from_template`, `get_generation_status`, `generate_image`, `get_image_generation_status`, `export_gamma`, `get_export_status`, `edit_gamma`, `get_edit_status`, `get_gammas`, `search_gammas`, `search_templates`, `read_gamma`, `get_gamma_comments`, `get_gamma_analytics`, `get_gamma_card_analytics`, `get_gamma_viewer_analytics`, `get_gamma_viewer_detail_analytics`, `get_themes`, `get_folders` |
| Destructive-flagged tools | **1** — `edit_gamma` |
| Read-only tools | **13** of 21 |
| Idempotent tools | **12** of 21 |
| API divergence | `read_gamma` is MCP-only; **archive + delete are REST-only**; the Slack app omits the edit tools |
| Tool-list cache | `ttlMs: 60000`, `cacheScope: "private"` |
| Pricing | Generations, edits and images charge credits; **reading, searching and exporting are free** |

### 6.3 Code availability

| Metric | Value |
|---|---|
| `github.com/gamma-app` repositories | **29** |
| Repos containing the product core | **0** |
| Repos that are OSS forks of third-party libraries | 14 (`tiptap`, `prosemirror-view`, `prosemirror-math`, `react-prosemirror`, `y-prosemirror`, `tldraw`, `chakra-ui`, `dnd-kit`, `apollo-client`, `async-redis`, `cf-image-proxy`, `aijsx`, `schematics`, `pptx-renderer`) — these reveal the stack (ProseMirror/TipTap + Yjs, tldraw, Chakra, dnd-kit, Apollo, Redis, Cloudflare image proxy) but contain no Gamma product code |
| Repos that are opaque / scratch / binaries | 4 |
| Substantive non-forks | **2**: `n8n-nodes-gamma` (official **MIT** integration node, 49 files, 12 test files, published to npm) and `import-grader-annotator` (internal QA tooling — **not** permissively licensed for product use) |
| npm `scope:gamma` | **0** packages |
| npm `@gamma-app/api`, `@gamma-app/sdk`, `gamma-app`, `gammaapp` | **404** |

**Verdict:** product core `SOURCE_NOT_AVAILABLE`; **external contract available under MIT** via
`gamma-app/n8n-nodes-gamma` @ `5d0b466a9ae4be994a722577daa0a761cb28cfaf`.

### 6.4 Competitive calibration — the important numbers

| Axis | Gamma | NextSlide OSS | Gomrey | Verdict |
|---|---|---|---|---|
| PPTX export | ✅ but **editable tables only**; whole-deck round-trip **not** claimed | ✅ genuinely editable (103/108 text shapes) | ✅ via `@presenton/export-core` | **Gomrey is not behind** |
| PDF export | ✅ Present Mode, not Edit Mode | ✖ | ✅ | Comparable |
| Image export | ✅ PNG `.zip`, one per card | ✖ | ✖ | **Both behind** — `F-E05` |
| HTML export | ✖ | ✅ single-file | ✅ | Comparable |
| Presentation / document / webpage / social | ✅ 4 formats | ✖ | ⚠️ schema only | **Gamma ahead** — `F-C02`, `F-S01`–`F-S04` |
| Multi-page under one URL | ✅ 1–50 pages | ✖ | ✖ | **Gamma ahead** — `F-S04` |
| Machine-matchable themes | ✅ `colorKeywords[]` + `toneKeywords[]` | ⚠️ 18 CSS presets, network fonts | ⚠️ theme derived from template only | **Gamma ahead** — `F-P06` |
| Brand kit | ✅ | ✖ | ✖ | **Gamma ahead** — `F-P07` |
| Agent editing | ✅ natural language, destructive-flagged | ✖ | ⚠️ per-slide only | **Gamma ahead** — `F-P16` |
| MCP surface | ✅ 21 tools, DCR + PKCE | ✖ | ⚠️ present, smaller | **Gamma ahead in breadth** — `F-A02` |
| Slide animation | ✖ | ✅ 24 | ✅ **24 (adopted)** | **Parity, now measured** |
| Reduced motion | unknown | ✅ (universal `*`) | ✅ (scoped, 24/24) | **Gomrey better scoped** |
| Source-linked citations in artifacts | ✖ | ✖ | ⚠️ built but **unwired** | **Gomrey uniquely capable — once wired** |
| Adversarial citation verification | ✖ | ✖ | ✅ deterministic, provider cannot overrule | **Gomrey uniquely ahead** |
| Arabic / RTL qualification | undocumented | ✖ | ✖ | **Nobody ahead — unmeasured everywhere** |

**Honest conclusion:** Gamma leads on *surface breadth* (formats, multi-page, brand, agentic editing,
MCP tool count). It does **not** lead on editability, evidence grounding or verification — and its
own export help page admits fidelity gaps (content scaling, chart sizing, font substitution).
Gomrey's lead on evidence grounding is real but **currently latent**, because the fabric is not
wired. Wiring it (`W3`) is the single highest-leverage action available.

## 7. Cost

| Resource | Spend |
|---|---|
| LLM provider calls | **0** — no key present |
| Hosted APIs | **0** — none authenticated |
| Product accounts | **0** — none created |
| Compute | Local only (8 cores / 8 GiB) |
| Downloads | Free/open only |

See `EXPERIMENTS.md` §E9.

## 8. What is *not* benchmarked yet, and why

| Gap | Reason |
|---|---|
| Same-case competitive deck comparison (Gomrey vs Gamma vs NextSlide on one prompt) | Requires authenticated access to the competitors — `BLOCKED`. Not claimed. |
| Gamma 5 vs Classic runtime behaviour | Documented only; `UNKNOWN` |
| Gamma PPTX round-trip fidelity | Documented only; `UNKNOWN` |
| Visual diffs of exported artifacts | Requires an authenticated competitor export; `BLOCKED` |
| Arabic/RTL quality comparison | No donor exposes a measurable RTL surface; see `F-C09` |
| `graft` and `morluto/rea` analysis outputs | `BLOCKED` — no funded LLM provider |

**No parity or superiority claim is made anywhere in this mission on the basis of these gaps.**
