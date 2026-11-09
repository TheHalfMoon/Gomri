# Gomri — Source Pin and License Verification

**Checked:** 2026-11-09, through the connected owner-authorized Windows GitHub CLI, **read-only**. These are repository-level metadata checks, **not** detailed third-party asset audits or approvals to import whole repositories.

| Donor | Verified commit exists | GitHub repository license metadata | Intended admission |
|---|---|---|---|
| [TheHalfMoon/Ninerr](https://github.com/TheHalfMoon/Ninerr) | `b8229a9c9e093026e0ca967bbe65dae285c49077` | Apache-2.0 | Bounded history/agent tool authorization adapter, NOT a second editor |
| [TheHalfMoon/Skilit](https://github.com/TheHalfMoon/Skilit) | `157ace7fc57aae9e135a368b7bbe1829ae7111ae` | Apache-2.0 | Design-pattern / brand-token metadata or narrowly bounded helper |
| [beautifulai/PptxGenJS](https://github.com/beautifulai/PptxGenJS) | `1f3c948832268024833094de86687f506d59ae77` | MIT | Compare OOXML bullets/notes with bundled export-core; copy only verified better helper |
| [crello/font-metrics-sizing](https://github.com/crello/font-metrics-sizing) | `73b6cbac91d109c74a265c05e1b67da326387150` | MIT | Read-only font-metric reference, never unverified binary font edits |
| [gamma-app/n8n-nodes-gamma](https://github.com/gamma-app/n8n-nodes-gamma) | `5d0b466a9ae4be994a722577daa0a761cb28cfaf` | MIT | Reference to public API task behavior, not Gamma's proprietary editor/source |

**Verification procedure:** Five `gh api repos/<owner>/<repo>/commits/<sha>` lookups returned exact SHA matches; five `gh api repos/<owner>/<repo> --jq .license.spdx_id` calls returned the listed SPDX metadata. No repository source was downloaded during these checks. Original local Gomri checkout remained clean at `d4362c6`.

## What this proves — and does not

**Proves:** the five pinned commits are addressable through the current authorized GitHub account, and current repository metadata reports the stated license identifiers.

**Does not prove:** that the exact pinned tree's LICENSE/NOTICE has been compared, that every embedded dependency/media/model asset is compatible, or that the source files are free of transitive licensing constraints. Those must be audited by R1 at source-admission time.

**Other candidate statuses:** the Presenton base is already in Gomri and has original Apache NOTICE obligations recorded in `docs/SOURCE_LEDGER.md`; PR #88's NextSlide OSS skill has its separate attribution. Proprietary editor engines of Gamma, Beautiful.ai, GPT Slides, VistaCreate and nextslide.ai are **not** actual acquired source snapshots. Behavior REA is not a source license or code handoff.

## Import policy and precise rename

1. Check file, license, committed SHA and original attribution.
2. Identify minimal source files, their dependency graph, tests and data/assets.
3. Create a namespace / product-UI **Gomri** compatibility adapter and document upstream symbol mapping. Do not silently rename upstream copyright holders or strip notices.
4. Add a donor origin record with original repository URL, commit, path, checksum, modifications and permission basis.
5. Run existing upstream tests + Gomri adapter tests + negative-controls, then Alibaba/PStack review before merge.
6. If source bytes, permission boundary, exact SHA, file-level notices or test prerequisites are missing, mark `SOURCE_ADMISSION_BLOCKED` and do not fake a copied engine.

**Source of truth:** [donor admission CSV](SOURCE_ADMISSION.csv), [roles](ROLES.md) and the original [donor ledger](../../SOURCE_LEDGER.md).
