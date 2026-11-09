# Gamma 5 — Deep REA, Public Source Extraction and Gomri Implementation Plan

**Date:** 2026-11-09. **Status:** research and public-source snapshots on an isolated GitHub branch. **Not** a cloned Gamma product, not current Gemini/Gamma server access, not a published Gomri feature or a passing production integration.

## Executive findings

**1 — The real Gamma 5 product architecture differs substantially from classic Gamma.** Official current docs describe an agent with Plan / Express / Research and Lite / Standard / Max effort; Gamma 5 is built around **fixed 16:9 proportional Grids plus independent Freeform elements**, with a fixed vs fluid height policy. Image slides are a separate **rasterized** output mode and cannot be described as natively element-editable.

**2 — The strongest actual Gamma-authored source discovery is an internal-quality evaluation tool.** Public repository gamma-app/import-grader-annotator includes 24 named error modes (23 slide-pair, one deck), 22 image-based VLM grader mappings, a human grading interface, three import comparison variants, confusion matrices / Cohen's kappa, and trainer/validation/test rubric recalibration. It references a non-public Gamma monorepo; **the private code is not accessible**. As no clear public LICENSE was observed, this repo was inspected but **not redistributed** into Gomri.

**3 — We copied exact permitted public source code into Gomri:** 474 tracked files in three Git-subtree snapshots under third_party/gamma-public/: a Gamma-owned fork of the independent aiden0z PPTX browser renderer (381, Apache-2.0), Gamma's public n8n API node (54, MIT), and its older Fixie-AI-derived AIJSX prompt helper (39, MIT). Pinned commits, notices and boundaries are recorded. **They are source-only snapshots, not running features.**

**4 — What remains private:** Gamma's actual web editor implementation, server endpoints, generation orchestrator/model chain, internal slide data model, native export engine, paid/internal design assets and raw project data. Browser-facing JavaScript and public forks do not automatically include those systems. We cannot truthfully claim to have acquired Gamma's complete private source.

## Full evidence and implementation chapters

| Chapter | What's inside |
|---|---|
| [01 — Authorized Vivaldi UI and official current features](gamma5-rea/01-live-ui-and-official-features.md) | Direct screenshot-based Gamma Free dashboard observation; Grid/Freeform, modes, import, charts, exports, analytics and contradictions against old docs |
| [02 — Deep Grid/Agent engine behavioral reconstruction](gamma5-rea/02-grid-agent-engine-reconstruction.md) | Proportional grid vs freeform layout, candidate Deck IR, AI edit transactions, Plan/Express pipeline, editable/raster split, negative probes |
| [03 — Gamma's actual import-eval source code](gamma5-rea/03-actual-gamma-import-eval-source.md) | Exact public code modules, all 24 fault categories, grading and rubric recalibration with held-out tests, proposed independent Gomri evaluator |
| [04 — Gamma 5 API/MCP and copied client source](gamma5-rea/04-gamma-api-mcp-client-source.md) | Real operations, async lifecycle, file/page identity, single-page edit limits, 429/credits, Gamma 5 vs Classic and schema drift |
| [05 — Gomri gap matrix and copy-first roadmap](gamma5-rea/05-gomri-copy-first-gap-and-execution.md) | Concrete Presenton/Ninerr/Skilit adaptation, risk/security/license gates and a 50-test black-box competitor protocol |

## Source/code inventory

- [207 Gamma5 capability, limit, and unknown rows](../../registry/gamma5-capability-engine-matrix-2026-11-09.csv). 18 evidence domains, classified by live Free UI, official help, open-source client code, other public source, or unknown. **Not 207 confirmed end-user product features.**
- [29 public Gamma organization repos](../../registry/gamma-public-source-inventory-2026-11-09.csv). **10 original, 19 forks.** Original/fork distinction is critical.
- [24 true Gamma public import failure categories](../../registry/gamma-import-failure-modes-2026-11-09.csv), with severity, group, pair vs deck evaluation and grader names.
- [Copied Git-subtree source and exact SHA/rights register](../../third_party/gamma-public/SOURCE_REGISTER.md).
- [Three copied public source trees](../../third_party/gamma-public/): pptx-renderer, n8n-nodes-gamma, aijsx.
- [Gamma's unlicensed public import grader, NOT copied](https://github.com/gamma-app/import-grader-annotator).

## First build target

**G5-01:** establish a frozen PowerPoint import evaluator using the 24-category taxonomy as an engineering reference, actual source and output screenshots, native OOXML semantic accounting, and a reproducible failure list. Compare Gomri's own exporter/importer against the publicly imported PPTX renderer as a **read-only** evaluator; do not discard the existing Presenton editor or export engine.

**G5-02:** add canonical Grid/Freeform editing and targeted AI patches on stable objects using authorized owner source from Ninerr, with undo and exact revision checks. **G5-03:** improve native PPTX and reference style fidelity, source grounding, Arabic and visual quality. **G5-04:** run blind head-to-head comparison before declaring Gamma superiority.

## Source-admission and operational limitations

- This source research did not generate a paid Gamma deck, incur credits or call Gamma API using a key.
- Gamma Free dashboard was directly observed in Vivaldi; no personal/private Gamma content or browser screenshots are committed to public GitHub.
- Original Gamma source without a known redistribution license was not copied.
- No hidden website/API/desktop protection was bypassed or claimed.
- Do not interpret this PR as product readiness: source snapshots need dependency audits, install/build/tests, security review and measured improvement before activation.
- Earlier Gomri work [PR #88](https://github.com/TheHalfMoon/Gomri/pull/88) is still a separate open draft and not necessarily on main; don't conflate its passing local tests with this new source branch.
- Exact-head CI may be queued or blocked on account conditions; never equate queued with passing.

## Primary Gamma and source references

- https://help.gamma.app/en/articles/17572896-how-do-grids-and-freeform-editing-work-in-gamma
- https://help.gamma.app/en/articles/15002203-how-do-i-create-with-agent-in-gamma
- https://help.gamma.app/en/articles/17238075-what-are-image-slides-and-how-do-i-use-them
- https://help.gamma.app/en/articles/11047840-how-can-i-import-slides-or-content-into-gamma
- https://help.gamma.app/en/articles/8033284-how-do-i-edit-my-content-with-ai
- https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api
- https://github.com/gamma-app/n8n-nodes-gamma
- https://github.com/gamma-app/import-grader-annotator
- https://github.com/gamma-app/pptx-renderer
- https://github.com/aiden0z/pptx-renderer

**Research conclusion:** We now have actual permitted public code to build from, detailed Gamma-specific technical fault taxonomies, and a stage-gated blueprint for Gomri. We do NOT have a complete Gamma source tree. No claim of superiority before execution of the benchmark.
