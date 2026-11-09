# Beautiful.ai public-source snapshots — audit and admission register

**Date:** 2026-11-09. **Scope:** Source preserved in Gomri's isolated research branch at immutable upstream commit hashes; **not built, tested, activated, or integrated into runtime**. The source repositories are public and carry the indicated repository licenses. The original vendor's product engine, private services, private datasets and customer presentations remain inaccessible.

| Directory | Original source | Pinned SHA | Files | Rights / provenance | Decision |
|---|---|---|---:|---|---|
| `claude-plugin/` | https://github.com/beautifulai/claude-plugin | `a3f771432c0d2c43f13c56a92d34ee9fa932855a` | 113 | Apache-2.0, Beautiful.ai original plugin, includes 103 **Markdown descriptions** of slide element contracts and 5 plugin skills. Not a stand-alone slide renderer and has **no executable design engine**. | **HIGH**: adopt bounded slide-model and design/evaluation architecture, not remote vendor dependency |
| `grok-plugin/` | https://github.com/beautifulai/grok-plugin | `e0b625790c05f7ff3fe4d5813057a4f0b0d74c81` | 116 | Apache-2.0, original plugin with broadly overlapping skill contracts adapted to Grok. | **MEDIUM**: diff against Claude plugin; do not duplicate document authorities or packages |
| `react-global-state/` | https://github.com/beautifulai/react-global-state | `519d6b0c891da2835f0b890f4fb66afebbc6ae43` | 19 | MIT, first-party small React state helper `bai-react-global-state` 0.7.0, published for legacy React 16+; not a presentation layout engine. | **LOW**: inspect only if existing Gomri state/history design needs it |
| `PptxGenJS/` | https://github.com/beautifulai/PptxGenJS | `1f3c948832268024833094de86687f506d59ae77` | 140 | MIT, vendor-maintained **derivative of Brent Ely/gitbrent/PptxGenJS**. GitHub `fork=false` doesn't make Beautiful.ai the original author. Package version `3.13.0-bai.5` with own bullet improvements and dependency hardening; original MIT notice preserved. | **HIGH**: compare vendor edits and native PPTX/RTL/notes/chart fidelity against Gomri export-core; adopt only measured improvements |

**Total:** 388 source files, preserved in four isolated source subtrees, pinned to original commits in the git commit message and this register. **Zero production imports or Gamma/Beautiful.ai paid calls.**

## Public Beautiful.ai repositories intentionally not copied

- https://github.com/beautifulai/beautifulai-docs — public hosted OpenAPI specification for a 9-operation generation/list/template/export API. No clear repository LICENSE was detected; inspect the published contract but do not bulk copy unlicensed implementation/source.
- https://github.com/beautifulai/qa-eng-interview — public 2025 test exercise (Cypress). README mentions Anthropic use for an example slide-generation test; no explicit public license detected. This is **not evidence** the whole Beautiful.ai 3.0 generator uses Anthropic exclusively.
- OpenAI/Claude/Beautiful.ai MCP servers: publicly documented endpoints require authorized OAuth or API keys. A public endpoint is **not the backend's source code** and cannot be silently substituted into Gomri's no-cost local engine.

## Source ownership and implementation caveats

1. `claude-plugin` and `grok-plugin` contain **public, vendor-authored instructions and model-interface documentation**. They describe a JSON slide document and elements at unusually high resolution, plus calls such as `render_slide`, `create_slide` and `update_slide`. They do **not** implement Beautiful.ai's renderer, layout solver, AI model stack, private MCP server or persistence backend.
2. Plugin documents describe `template_id`, `states[0]`, `layout`, `version: 10`, `migrationVersion: 10.03`, `textStylesVersion: 2`. These are source-verified **public schema conventions**, not a promise all private live accounts accept every field.
3. The newer 2026-11-06 Claude/Grok plugins advertise slide-level edit/add/render tools and a newer MCP server route; an older MCP FAQ says the earlier connector cannot perform arbitrary slide-level edits. **Do not conflate connector versions.** Verify the exact client/server/tier in authenticated tests.
4. `PptxGenJS` is third-party origin. Retain Brent Ely's copyright/MIT license; upstream version 3.13.0-bai.5 and 2026 Nov security fix removes unused `image-size` dependency.
5. Current Gomri uses Presenton editor and `@presenton/export-core`. Its IR and renderer remain canonical until side-by-side tests prove benefit.
6. Assets/fonts/graphics and transitive packages must pass independent redistribution/security review before inclusion in a binary release.
7. Source snapshots can be read and tested in a sandbox without credentials. **Never call Beautiful.ai production MCP, create files, or spend user credits automatically** to qualify locally reproducible code.

## Proposed source-first admission waves

- **BAI-01**: parse vendor Markdown element/template taxonomy into independent Gomri schema test fixtures; deep-copy only with Apache NOTICE/provenance.
- **BAI-02**: implement a deterministic `SmartLayout` component that maps existing Gomri Design IR to grid/constraint nodes and returns typed `isFit`/overflow reasons.
- **BAI-03**: render-before-commit contract with preview, error repair budget and typed patch/undo, borrowing selected history/authorization code from user's `TheHalfMoon/Ninerr`.
- **BAI-04**: compare vendor PptxGenJS 3.13.0-bai.5 against upstream and existing export-core for bullet retention, font handling, notes, native charts and editable shapes.
- **BAI-05**: benchmark 50 synthetic cases against Beautiful.ai with designer-blind quality scoring, plus Arabic/RTL and native PPTX object fidelity.

## Companion documents

- [Deep competitive engine REA](../../docs/research/BEAUTIFUL_AI_ENGINE_SOURCE_REA_2026-11-09.md)
- [Engine architecture and exported model details](../../docs/research/beautiful-ai-rea/02-source-slide-model-layout.md)
- [Capability and source registry](../../registry/beautiful-ai-capability-source-matrix-2026-11-09.csv)
