# Gamma 5 Deep REA — 03: Actual Gamma Import Evaluation Source

**As-of:** 2026-11-09. **Primary source:** https://github.com/gamma-app/import-grader-annotator. This is an actual **Gamma-authored PUBLIC source repository**, not a hypothetical source of the editor or full generation model. **No clear public repository LICENSE was identified** as of the research. Its source was read and analyzed, **not copied into Gomri's public repo**. A separate grant may be possible but must be documented before redistribution.

## 1. Why this is the most valuable find

Gamma's public repo exposes a **quality-measurement workflow** for imported presentation slides: human-rated input/output slide pairs, a detailed failure taxonomy, image-based VLM graders, agreement reports and explicit grader calibration. This is a stronger practical target for Gomri than speculative reverse engineering of Gamma's closed-source visual generation internals.

Import-quality optimization is not one homogeneous "looks good" score. It separates layout, typography, images, branding, components and data fidelity. The repo contains real source modules and developer notes documenting this evaluator. This is **internal engineering tooling published publicly**, NOT proof that these exact tests gate the production Gamma 5 release.

## 2. Three comparison variants — source-backed

README and storage code describe **three independent output variants** per imported deck:

| Variant | Input | Comparator | Intended insight |
|---|---|---|---|
| Deck Doctor | original slide PDF | manually crafted ideal Gamma PDF | Design target / ideal import |
| Current Import | original slide PDF | actual Gamma current-import PDF | End-user import behavior |
| Programmatic Import | original slide PDF | programmatically generated Gamma output PDF | Separate automated import path |

The local app pairs pages 1:1 and keeps variants' annotations separate. It warns if page counts differ; aligning an output with excess pages requires explicitly dropping selected output pages, with a once-only backup. A shorter output cannot be naively repaired by alignment.

UI capabilities in public README:
- side-by-side matched slides with linked zoom/pan;
- manual grades Pass/Borderline/Fail/NA plus notes;
- per-mode filter and progressive annotation;
- autosave/resume and local render cache;
- editable failure-mode directory with soft disable, delete guards, grading notes;
- consolidated JSON and tidy long CSV exports, across variants.

The app is **FastAPI + React/Vite/Tailwind**, with PDF rendering through PyMuPDF; does not need the private Gamma monorepo for core manual workflow.

## 3. Source inventory: exact inspected modules

| Source file | Evidence actually read | Major functions or behavior |
|---|---|---|
| backend/app/modes.py | 409 lines, SHA 2c699cf... | 24 built-in evaluation dimensions; dynamic modes.json registry, severity P0/P1/P2; 23 pair-level, 1 deck-level; 22 configured image-graders |
| backend/app/ai_grader.py | 757 lines, SHA d1da8b67... | resolves input/output images, prompt.md and grader.yml; AI model call; verdict parsing; prompt hash cache and persistent per-cell results |
| backend/app/llm.py | code search/README | Anthropic vision client, sends two local PNGs with rubric, returns rawResponse/error/latencyMs; separate external model expense |
| backend/app/reports.py | 142 lines, SHA 1760d595... | confusion matrix, human vs AI grade distributions, observed agreement, chance-adjusted Cohen's kappa |
| backend/app/recalibrate.py | 931 lines, SHA cce9d157... | seeded train/validation/test split, candidate rubric generation, rank by validation kappa, measure held-out test, explicit human approval to adopt |
| backend/app/storage.py | source code references | persistent per-deck grades and atomic writes; RLock; preserves disabled-mode historical grades |
| backend/app/grader_author.py | code search | creates new vision-grader rubric from human failure-mode description |
| backend/app/config.py | source code references | model / grader paths, split and candidate configuration |
| frontend (React/Vite) | README/AGENTS.md | matched slide viewer, mode inspector, reports, recalibration controls |

Important: Some file locations and hashes above were validated by direct GitHub fetch. Others are referenced by docs/source searches. They are distinct evidence tiers.

## 4. The actual 24-category taxonomy

The 24 records have been transcribed into an auditable companion CSV:
[registry/gamma-import-failure-modes-2026-11-09.csv](../../registry/gamma-import-failure-modes-2026-11-09.csv)

| ID | Source failure category | Severity | Scope |
|---|---|---|---|
| 1 | Logo dropped | P1 | slide pair |
| 2 | Headers & footers dropped | P0 | slide pair |
| 3 | Text sizing & spacing | P1 | slide pair |
| 4 | Divider mishandling | P2 | slide pair |
| 5 | Decorations dropped | P2 | slide pair |
| 6 | Diagrams flattened to primitives | P1 | slide pair |
| 7 | Color zones / fills misassigned | P1 | slide pair |
| 8 | Layout direction changed | P1 | slide pair |
| 9 | Icons dropped or swapped | P2 | slide pair |
| 10 | Background / hero images dropped | P1 | slide pair |
| 11 | Heading alignment | P2 | slide pair |
| 12 | Slide too tall / 16:9 broken | P1 | slide pair |
| 13 | Forced into accent treatment | P1 | slide pair |
| 14 | Table styling / size | P1 | slide pair |
| 15 | Labels / pills | P2 | slide pair |
| 17 | Chart conversion and data loss | P0 | slide pair |
| 18 | Brand color remapping | P1 | entire deck |
| 19 | Text color / emphasis drift | P2 | slide pair |
| 20 | Forced component substitution | P2 | slide pair |
| 21 | Flaky/inconsistent handling | P2 | slide pair |
| 22 | Bullet size / shape / color | P2 | slide pair |
| 23 | Icons / emoji / images oversized | P2 | slide pair |
| 24 | Card frames / borders | P2 | slide pair |
| 25 | Text highlight lost | P2 | slide pair |

The IDs are intentionally non-contiguous: **#16 was merged into #7**. #18 is evaluated once per deck, not per slide. #21 requires across-slide judgment and has no direct single-pair grader. Therefore 24 categories, **22 mapped vision graders**, 23 pair-level categories and one deck-level category, not 24 grader implementations.

The source lists severity P0 for just #2 dropped headers/footers and #17 chart data loss. It is tempting to promote data loss to P0+ for Gomri, but that would be Gomri's own choice, not a faithful transcription.

## 5. How the published VLM grader operates

The source's vision evaluation path:

    pair: original.png / output.png
       -> choose failure mode
       -> lookup grader.yml and prompt.md
       -> resolve configured vision model
       -> compute prompt hash(model + prompt)
       -> cached previous grade? use when fresh
       -> otherwise call Anthropic Messages API on both PNGs
       -> parse verdict pass/borderline/fail/na/skip + reason
       -> persist result keyed by deck, variant, pair, mode
       -> compare with human grade when available

**No Gamma backend source is obtained by this.** The grader client is an evaluation tool, not the production Gamma5 slide creation agent.

The README mentions private Gamma monorepo directory packages/import-evals/graders and an earlier eval-server run-grader route. Those **paths exist as references in public code, not accessible source trees**. Do not manufacture the proprietary rubric prompts.

Potential issue: default Anthropic API is not zero cost. Gomri must make hosted VLM optional and use a deterministic screenshot/structural checker or a qualified local free VLM by default. Never accidentally connect the user to a paid provider.

## 6. Human-model agreement mathematics and calibration

Published reports.py computes **Cohen's kappa**:

    observed_agreement = agreements / comparable_pairs
    expected_agreement = sum(class_frequency_human * class_frequency_model)
    kappa = (observed_agreement - expected_agreement) /
            (1 - expected_agreement)

Classes include pass, borderline, fail and na. An undefined kappa (only one class) is represented as undefined/null, not invented as 1.

The recalibration source explicitly:
1. combines human-labelled pairs across decks and output variants for one failure mode;
2. splits train / validation / test with a reproducible seed;
3. scores current rubric as baseline;
4. diagnoses train disagreements and samples representative paired images;
5. proposes multiple candidate grading instructions using a model;
6. scores candidate rubrics against validation, selects highest kappa;
7. scores winner once on a held-out test set;
8. records before/after and requires explicit adoption to change canonical prompt.

This is **a real implemented optimization method**, not an imagined agent loop. A concern for Gomri: a purely random per-pair split may leak near-identical slides from the same deck across train/validation/test, inflating apparent generalization. Prefer a **deck-grouped split** and a separate out-of-domain corpus; compare kappa, class-specific precision/recall and severe false-negative counts, not kappa alone.

## 7. Proposed Gomri import QA subsystem (not yet implemented)

**Authority:** keep the current Presenton editor and its canonical slide/element representation. Add a new **Evaluator** sidecar instead of a second production importer.

Proposed pipeline:

    Imported PPTX
       -> risk-controlled ZIP/XML/asset parser
       -> native source-render PNG + OOXML typed element summary
       -> Gomri import to Deck IR
       -> Gomri rendered PNG and native export audit
       -> deterministic geometry/text/chart/shape/source-data diff
       -> human slide-pair grading UI
       -> optional VLM grader if local/authorized
       -> issue taxonomy + evidence report + CI acceptance gate

Core facts to compute without any LLM:
- counts of source and target slides, shapes, text runs, table cells, chart data points, media assets;
- file/media integrity and zip limits;
- lost/flattened chart series and table cell values;
- changed numbers, unit labels, text content, notes and citations;
- font substitution log and Arabic Unicode logical correctness;
- geometry overlap/clipping, effective color contrast and aspect-ratio fidelity;
- pixel similarity with explicit uncertainty from render font differences.

All 24 Gamma taxonomy categories can serve as **independent engineering reference**. Do not ship unlicensed source or private grader prompts. Use a new Gomri-owned, meaningfully generalized implementation and its own synthetic fixtures/labels.

## 8. Why this matters competitively

Current Gomri PR #88 already carries a real PPTX-from-json -> PPTX-to-json fidelity fixture suite, and local tests passed at the draft head. But that suite measures selected **semantic import/export properties**, not the full visual fidelity of imported PPTX or grade agreement against expert human judgments.

This source discovery provides the missing methodology:
- a multi-path baseline (ideal vs current vs programmatic),
- a reproducible per-slide failure taxonomy,
- a human/AI adjudication system with metrics,
- a held-out calibration process,
- a clear error-driven engineering feedback loop.

A team can improve native fidelity using this architecture without knowing Gamma's proprietary editor source. Gomri should benchmark its own importer against **independently generated originals**, not copy Gamma's user/customer decks.

## 9. Acceptance test contract for Gomri

**Required**:
1. A purely local baseline grading workflow works without any model key.
2. Every imported slide is accounted for exactly once; missing/extra slides are visible.
3. Chart data/text loss are detected structurally, regardless of screenshot resemblance.
4. Misaligned slides cannot be silently paired to inflate scores.
5. Original source file never gets destructively modified during alignment.
6. Human annotation writes are atomic and concurrency-safe.
7. Disabled modes retain past grades.
8. Recalibration uses deck-grouped train/val/test; report coverage and kappa confidence.
9. Held-out tests are never used to select a winner.
10. An AI grader is optional, cost-bounded, traceable and permission-limited.
11. Every issue includes source slide, output slide, rule ID, source digests and a reproducible artifact.
12. Exact-head unit/integration/render QA and independent review pass before runtime adoption.

**Status:** documented design + faithful 24-row CSV only. No actual import-grader original code copied, no local VLM model run, no quality improvement yet measured.

## 10. Primary source links

- https://github.com/gamma-app/import-grader-annotator
- https://github.com/gamma-app/import-grader-annotator/blob/main/backend/app/modes.py
- https://github.com/gamma-app/import-grader-annotator/blob/main/backend/app/ai_grader.py
- https://github.com/gamma-app/import-grader-annotator/blob/main/backend/app/llm.py
- https://github.com/gamma-app/import-grader-annotator/blob/main/backend/app/reports.py
- https://github.com/gamma-app/import-grader-annotator/blob/main/backend/app/recalibrate.py
- https://github.com/gamma-app/import-grader-annotator/blob/main/AGENTS.md
- https://github.com/gamma-app/import-grader-annotator/blob/main/README.md
