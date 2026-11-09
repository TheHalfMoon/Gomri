# Gamma public-source snapshots — provenance and admission register

**As of:** 2026-11-09. **Branch:** `research/gamma5-source-rea-20261109`. **Status:** source snapshots available for inspection; **not built, tested or integrated into the Gomri runtime**. This folder contains code, not a copy of Gamma's private product backend, private card editor, live LLM orchestration, private template library or customer data.

The upstream repos were imported with `git subtree add --squash`. Each commit retains its upstream source SHA in Git history; licenses/required notices remain inside the preserved folders. This is intentionally **NOT a blind product rebrand**.

| Snapshot path | Source and exact pin | Source class / license | Use in Gomri | Gate |
|---|---|---|---|---|
| `pptx-renderer/` | [gamma-app/pptx-renderer](https://github.com/gamma-app/pptx-renderer) @ `68cb570940fb28d5c4628f31d1365016c4483521` | Gamma-owned **fork** of `aiden0z/pptx-renderer`; Apache-2.0; upstream notices included; 381 files | Optional **read-only PPTX import preview** and source/layout comparator; do not confuse this package with native editable export | Verify JSZip/ECharts/PDF.js/embedded fonts and external media policy, run package tests, render real PPTX fixtures, compare against Presenton |
| `n8n-nodes-gamma/` | [gamma-app/n8n-nodes-gamma](https://github.com/gamma-app/n8n-nodes-gamma) @ `5d0b466a9ae4be994a722577daa0a761cb28cfaf` | Gamma-authored public integration; MIT; 54 files | API contract/capability reference, async job and lifecycle examples; **not** the server source; Gamma API requests need an account and can consume credits | Offline schema tests; no live API key, no paid generation, no automatic remote dependency |
| `aijsx/` | [gamma-app/aijsx](https://github.com/gamma-app/aijsx) @ `2900075d8251b7a83c6b855fcf36e6df4c5d2539` | Gamma-authored **derivative of Fixie AI's ai-jsx**; MIT; 39 files | Historic prompt composition and async rendering patterns; not evidence Gamma 5 still uses it | Review third-party notices and compare with current local tool/LLM orchestration before adoption |

**Total imported:** 474 tracked files in three separate source folders; zero application imports added.

## High-value public Gamma source intentionally NOT copied

- [gamma-app/import-grader-annotator](https://github.com/gamma-app/import-grader-annotator): original Gamma tool for grading original PowerPoint vs ideal/current/programmatic Gamma imports, 24 seeded failure modes and VLM/human agreement. **No clear public LICENSE was observed in GitHub metadata.** Inspect and document the engineering contract; do not redistribute implementation in this public repo without confirming an explicit grant covering this code and its transitive materials. Its README references a separate **private Gamma monorepo `packages/import-evals/graders`**: that code is **not** included in the public tool.
- `gamma-app/y-prosemirror`, `gamma-app/tiptap`, `gamma-app/prosemirror-view`, `gamma-app/tldraw`, `gamma-app/dnd-kit`, `gamma-app/chakra-ui`: GitHub **forks** of outside open-source projects, not Gamma's complete editor. Current production-use and private modifications are not established. Their licenses and historical date must be checked at the exact commit, especially graphic-editor assets/production licensing.
- `gamma-app/desktop-app-releases`: release metadata/binaries, **not** open Gamma application source.
- `gamma-app/tiptap-collaboration-extension`: old demo/prototype, no clear public source license.
- Unrelated original/fork repositories and experiments are enumerated in the separate 29-repo inventory.

## Security, license, and product gates

1. Keep source identity and original license text; never assert Gamma authored an upstream fork.
2. Verify exact revision, dependency notices, fixture/media rights and license before activating.
3. No untrusted external images or hyperlinks fetched automatically during PPTX import; use the renderer's `externalMedia: 'block'` and ZIP expansion limits for untrusted files.
4. Never allow library source to become the Gomri document authority. Keep Presenton editor/SourceIR/claims and `@presenton/export-core` as incumbents until tested superiority.
5. No Gamma API credential was read or used. No paid Gamma credits were consumed. Do not introduce Gamma API as a hidden production requirement.
6. Do not assert any of these sources are the internal Gamma 5 agent or grid editor implementation.
7. Run independent CI/security/bundle/export parity checks before admitting a runtime adapter; source snapshot alone is NOT a feature.

## Further evidence

- [Gamma deep REA](../../docs/research/GAMMA5_ENGINE_SOURCE_DEEP_REA_2026-11-09.md)
- [Gamma public GitHub source inventory](../../registry/gamma-public-source-inventory-2026-11-09.csv)
- [Gamma import quality failure taxonomy](../../registry/gamma-import-failure-modes-2026-11-09.csv)
- [Prior Gomri source-first implementation](https://github.com/TheHalfMoon/Gomri/pull/88) remains DRAFT.
