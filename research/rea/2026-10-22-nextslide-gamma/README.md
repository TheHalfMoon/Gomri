# REA — NextSlide & Gamma → Gomrey

**Mission:** [Issue #77](https://github.com/TheHalfMoon/Gomrey/issues/77) — deep NextSlide + Gamma
reverse engineering and source-first capability migration into Gomrey.
**Gomrey target:** `TheHalfMoon/Gomrey` @ `main@5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Branch:** `feature/rea/nextslide-gamma-wave1`
**Date (UTC):** 2026-10-22

This directory is the durable, auditable record of the mission: what was observed, what was actually
obtained, what was integrated, what was rejected and why, and what remains.

---

## 1. Read this first

| If you want to know… | Read |
|---|---|
| What was authorized, and what that does **not** mean | `SOURCES.md` §0 |
| Which files were actually obtained | `SOURCES.md` §1–§3a |
| Which review tools genuinely ran | `SOURCES.md` §6, `STATUS.md` §2.2, `REVIEW_RECORD.md` |
| What Gomrey already had, measured | `GOMREY_CURRENT_BASELINE.md` |
| Every capability, across all five products, with a mandatory state | `FEATURE_MATRIX.md` |
| Every transplant: source → target → tests → rollback | `TRANSPLANT_MATRIX.md` |
| What the donor's code actually is | `NEXTSLIDE_SKILL.md` |
| What the dead product and the live platform actually do | `NEXTSLIDE_AI.md`, `GAMMA.md` |
| Every command that was run | `EXPERIMENTS.md` |
| What the architecture should become, and why | `ARCHITECTURE_DELTA.md` |
| What to build next, in what order | `IMPLEMENTATION_GRAPH.md`, `STATUS.md` §5 |
| Measured numbers | `BENCHMARKS.md` |

## 2. The three short answers

**1. NextSlide.ai is a live domain with a dead product.** It returns HTTP 200 with a single
React SPA whose only page is an acquisition notice — *"The NextSlide team is now at OpenAI"* —
signed by founder Ahmed Beshry. `/pricing` renders the same page (catch-all route); `/docs` returns
a Cloudflare bot-verification interstitial, which is *not* evidence that `/docs` exists. Its GitHub
organisation `NextSlide-AI/Nextslide.AI` exists but the repository is **empty**. Verdict:
`SOURCE_NOT_AVAILABLE`.

**2. The open-source `0xRafie/nextslide` is a different product, and it is real.** A 13-file MIT
skill — 18 style presets, 13 layouts, 24 animations, a single-file HTML presentation engine, a
presenter mode, a PPTX importer and a PptxGenJS exporter. **All of the issue's counts were
reproduced**, not assumed. It also ships with four genuine defects that we found by reading and
running it, one of which (a permanently invisible counter element) is independently visible in the
committed probe screenshots.

**3. Gamma's product source is not available, but its *external contract* is.** 29 repos under
`github.com/gamma-app` were enumerated: all are OSS forks of third-party libraries, integration
nodes, QA tooling, opaque scratch projects or binaries. The editor, card model, theme system and
export renderer are not published. However, **`gamma-app/n8n-nodes-gamma` is an official,
MIT-licensed, Gamma-owned repository** that encodes Gamma's public REST contract and ships a
12-file test suite. That converts the Gamma wave from "entirely blocked" to "contract transplant
available, core still blocked".

## 3. What has actually shipped

**One qualified transplant, in this branch:**

| Deliverable | Path | Qualification |
|---|---|---|
| Slide animation contract — 24 animations, easings, stagger, durations, reduced motion | `servers/nextjs/lib/slide-animations/` | 28 deterministic tests, all gates green |
| Donor license + adaptation record | `docs/donors/nextslide-skill/` | MIT text byte-identical to upstream; 23-field admission record |
| Ledger admission | `docs/SOURCE_LEDGER.md` §2 | new donor subsection |

The interesting part is *how* it was adapted. The donor's base rule is
`[class*="animate-"] { opacity: 0; ... }`. Gomrey uses Tailwind CSS v4, whose `animate-spin`,
`animate-pulse`, `animate-bounce` and `animate-ping` utilities that wildcard would match — silently
blanking every spinner and loading indicator in the product. Adopting the donor verbatim would have
shipped a visual bug across the whole application. The adopted contract re-namespaces to
`gs-anim-*`, enumerates every selector explicitly, replaces the donor's `.slide.active` DOM
contract with two surface-agnostic activation modes, scopes the reduced-motion block, and
re-classifies the donor's broken `animate-counter-up` as honestly controller-backed.

Three donor components were **rejected on measured evidence**, not taste:

| Rejected | Measured reason |
|---|---|
| `scripts/export-pptx.js` | Gomrey already owns `@presenton/export-core` v1.0.34; a second PPTX engine is a parallel stack. (The donor's output *is* genuinely editable — verified with `python-pptx` — but that does not establish superiority.) |
| `scripts/extract-pptx.py` | Gomrey's importer is already superior **and** the donor's extractor **crashes** on a pristine donor-generated PPTX (`ValueError: shape is not a placeholder`). Crash log committed. |
| `presenter-mode.md` | Gomrey already owns a 610-line `PresentationMode.tsx`. |

## 4. Directory map

```
research/rea/2026-10-22-nextslide-gamma/
├── README.md                     this file
├── SOURCES.md                    source registry, authorization, tooling execution matrix
├── NEXTSLIDE_AI.md               the dead commercial product
├── NEXTSLIDE_SKILL.md            the MIT donor, read line by line
├── GAMMA.md                      live platform capability + API/MCP reconnaissance
├── NEXT_SLIDE_IO_DISAMBIGUATION.md  proof that the clicker is not a donor
├── EXPERIMENTS.md                every command that was run
├── FEATURE_MATRIX.md             68 capabilities × 5 products, mandatory states
├── TRANSPLANT_MATRIX.md          source → target → tests → rollback
├── GOMREY_CURRENT_BASELINE.md    what Gomrey already had, measured
├── ARCHITECTURE_DELTA.md         what must change, and why
├── IMPLEMENTATION_GRAPH.md       dependency-ordered execution plan
├── BENCHMARKS.md                 measured numbers
├── STATUS.md                     the operational ledger
├── REVIEW_RECORD.md              exact-candidate review binding
└── evidence/
    ├── BASELINE_GATE_RUN.md      pre-change green/red baseline
    ├── GOMREY_BASELINE_SURVEY.md full baseline survey (941 lines)
    ├── NEXTSLIDE_SKILL_SOURCE_INVENTORY.md  donor inventory (484 lines)
    ├── NEXTSLIDE_PROBE_RUNLOG.md every probe command and output
    ├── LIVE_PROBE_LOG.md         every live fetch, status and failure
    ├── RAW_ARTIFACT_MANIFEST.txt sha256 of every captured artifact
    ├── raw/                      gzipped page captures + 21 official Gamma doc pages
    ├── probe/                    4 real HTML decks, 4 PPTX exports, crash log, screenshots
    └── scripts/                  the headless-browser capture scripts
```

## 5. The one-sentence version

> Gomrey's **editing, export, evidence and verification** foundations are already strong and are not
> the bottleneck; its **studio surface**, **theme/brand layer**, **multi-node artifact IR** and
> **evidence-to-artifact wiring** are the real gaps — and the single highest-value fix,
> wiring the already-complete P08/P09 evidence fabric into the presentation pipeline, needs no donor
> code at all.
