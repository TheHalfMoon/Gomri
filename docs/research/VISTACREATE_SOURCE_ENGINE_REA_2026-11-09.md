# VistaCreate / Crello — Deep REA, Real Public Source and Gomri Execution Plan

**Research completed 2026-11-09.** Project: TheHalfMoon/Gomri. Status: isolated DRAFT research branch with source snapshots and technical evidence. **No feature has been merged, deployed, run on a production account, or benchmarked as superior.**

## Executive findings

1. **VistaCreate is an all-purpose creative design editor, not simply an AI presentation maker.** It has 85 advertised formats, multi-page documents up to 100 pages (web), animations/video timeline, AI Writer, AI Image Generator, Object Grabber, Brand Kits/Styles, one-click multi-format resize, export PDF/PNG/JPG/MP4/GIF, scheduling and a bespoke white-label B2B editor API. These capabilities vary by plan and platform; source and credit restrictions apply.
2. **The highest-impact competitive wedge for Gomri is responsive format adaptation.** VistaCreate's official Resize docs say designers may need manual text/object repairs after Copy & Resize. We should implement semantic/layout-aware reflow on one canonical deck graph across 16:9/4:3/1:1/9:16 with zero silent chart/citation loss.
3. **Actual source discovery:** public Crello code includes a **font vertical-metrics normalizer** that directly addresses cross-OS typography drift and a historical React Lottie wrapper, plus a 2017 Electron PDF/PNG renderer fork. The adjacent VistaPrint org exposes 2015 ArteJS rich-text code. Four public packages totalling **217 files** were copied to third_party/vistacreate-public at immutable original SHAs, with original licenses and attribution, as **quarantined source snapshots only**.
4. **Strong source boundary:** the modern VistaCreate editor, current design schema, AI Assistant, background/image Object Grabber and server renderer source are NOT public in these repos. The public depositphotos/vcr-kit installer retrieves its actual engineering suite from an **organization-private GitLab repository**, requiring corporate authorization. We did not execute it or access private source.
5. **Strategic non-goal:** do not turn Gomri into a generic Canva clone or a social scheduling/print marketplace. Build excellent slides and derived reusable design variants, local media handling and native PowerPoint quality first.

## Detailed research chapters

| Chapter | What's inside |
|---|---|
| [01 — VistaCreate current features and behavioral contracts](vistacreate-rea/01-current-product-behavior.md) | Editor, 85 formats, Brand Kits, AI Writer/Generator/Object Grabber, responsive resize, animation/video, export, limitations |
| [02 — Actual public Crello/VistaPrint code and private-source boundary](vistacreate-rea/02-code-source-and-engine-inference.md) | Font OS/2/hhea source math, Lottie fork, obsolete Electron rendering security, ArteJS, private GitLab kit |
| [03 — Partner API and proposed independent design-engine architecture](vistacreate-rea/03-api-image-and-format-engine.md) | White-label iframe/API vs paid stock API vs public code; template variables; image mask/inpainting; asset rights |
| [04 — Source-first Gomri implementation waves](vistacreate-rea/04-gomri-copy-first-build-plan.md) | Current Presenton/Ninerr/Skilit alignment, adaptive formats, native PPTX, no-cost local image tools and conditional source admission |
| [05 — 50 black-box benchmark scenarios and go/no-go](vistacreate-rea/05-blackbox-50-and-adoption.md) | 50 named NOT RUN probes; 15 local engine fixtures, human visual scoring, rights/security/export criteria |

## Structured audit materials

- [61 public repos inventoried](../../registry/vistacreate-public-github-inventory-2026-11-09.csv) from three related orgs: crello 17, depositphotos 14 and VistaPrint 30. Many unrelated or ancient; do not claim all are current editor dependencies.
- [288 source-graded capability/limit/unknown rows](../../registry/vistacreate-capability-source-matrix-2026-11-09.csv) in 22 evidence domains. These are **NOT 288 independently benchmarked product features**. Breakdown: 177 general help, 37 2026 AI help, 15 B2B API marketing, 45 actual public source observations, 14 unknowns.
- [Pinned 217 source files](../../third_party/vistacreate-public/) from four MIT/Apache/metadata-labelled repositories, **not active Gomri code**.
- [Source admission and license register](../../third_party/vistacreate-public/SOURCE_REGISTER.md) with security and known old dependency warnings.

## Source inventory — important provenance caveats

| Source | Files | Actual code / purpose | Decision |
|---|---:|---|---|
| crello/font-metrics-sizing | 7 | MIT, original Crello vertical OS/2/hhea font metrics transformation | P0 font quality reference only; never patch fonts by default |
| crello/react-lottie | 45 | MIT, fork of chenqingspring/react-lottie over Airbnb lottie-web | P1 animation ideas; React16 historical, test maintained upstream |
| crello/electron-render-service | 32 | MIT package metadata, fork of msokk renderer | DO NOT EXECUTE: obsolete Electron 1.6, unsafe URL capture potential, query accessKey |
| VistaPrint/ArteJS | 133 | Apache-2.0, VistaPrint 2015 jQuery WYSIWYG | historical only; not modern VistaCreate engine |

The first-party 2026 vcr-kit repo is a GitLab setup **bootstrap**, not the private code it downloads; it has no clear public redistribution license and is **not copied**. A claim of legal permission does not itself authenticate external GitLab account access, third-party media licenses or backend source presence.

## Fastest product implementation order

| Wave | Build | Grounded reason |
|---|---|---|
| VC-G1 P0 | One-deck multi-aspect Adaptive Resize + cross-OS font quality | better than naive center-and-rescale for slides/social/print; measurable |
| VC-G2 P0 | Scoped, source-grounded AI text changes + history/Undo | AI Writer behavior plus Gomri's evidence thesis |
| VC-G3 P1 | Optional local Object Grabber, background removal, asset layer transactions | true editing of images with no remote upload; masks aren't vector objects |
| VC-G4 P1 | Typed animation and MP4/GIF/PDF/PPTX fidelity | consistent playback and honest raster/export downgrades |
| VC-G5 P2 | Brand/reference kit and typed template/MCP API | only after core deck quality and permissions |
| DEFER P3 | Social scheduling, licensed commercial stock, print fulfillment | distract from Gomri's flagship slides |

**Admission gates:** code licenses, notices, fonts/media/model weight rights, source identity, local zero-cost behavior, tested object preservation and export, render parity and old source security. Source discovery is not a reason to replace Presenton editor or install an old jQuery/React16/Electron stack.

## Specific verified limitations worth beating

- VistaCreate help documents Copy & Resize can require manual adjustments to text and image positions.
- Standard consumer export menu lists JPG/PNG/PDF/MP4/GIF and does **not list editable PPTX**. This is a documentation-level finding, not a proof no plan/private API ever supports a PPTX workflow.
- Old 2017 public Crello renderer takes user-provided URL and query credential: unacceptable as a Gomri service.
- AI Object Grabber creates an independent **raster image layer** after segmentation/inpaint; it does not inherently create native editable PowerPoint tables/charts/text.
- Public font guide does not establish measured Arabic bidi quality; Gomri can qualify it independently.
- Many VistaCreate stock fonts, images, animations and videos have restricted standalone redistribution. Even if an end-user can design with them, source assets cannot simply be copied to Gomri.

## Actual work vs not done

**DONE:** source search across public orgs and current official docs, code inspection, 217 pinned public-source files committed to a separate research branch, 61 repo ledger, 288-row capability ledger, five detailed chapters, 50-case black-box test protocol, independent implementation roadmap and rights/security gates.

**NOT DONE:** live authenticated competitor editor tests, obtaining the private modern VistaCreate source/AI models or licensed stock assets, source dependency installation, runtime feature integration in Gomri, actual PPTX/MP4 benchmark passes, exact-HEAD production CI qualification, launch or release.

No paid API, token/account, model weight, unauthorized source, or user private design was accessed.

## Primary sources

- https://create.vista.com/
- https://support.create.vista.com/hc/en-us/articles/360033989293-How-to-resize-designs-in-VistaCreate
- https://support.create.vista.com/hc/en-us/articles/29904242727068-How-to-edit-images-with-AI-Object-Grabber
- https://support.create.vista.com/hc/en-us/articles/24926528042524-How-to-write-text-with-AI-Writer
- https://support.create.vista.com/hc/en-us/articles/360026488234-How-do-I-animate-a-design-in-VistaCreate
- https://support.create.vista.com/hc/en-us/articles/115004246593-How-do-I-save-and-download-my-finished-design
- https://support.create.vista.com/hc/en-us/articles/13402817714844-Legal-FAQ
- https://depositphotos.com/api-suite/graphic-editor.html
- https://github.com/depositphotos/vcr-kit
- https://github.com/crello/font-metrics-sizing
- https://github.com/crello/react-lottie
- https://github.com/crello/electron-render-service
- https://github.com/VistaPrint/ArteJS

**Research verdict:** public code and product behavior have been mapped to concrete Gomri engineering and testing opportunities. The private current VistaCreate engine was **not** obtained; winning requires independent tested implementation.
