# VistaCreate / Crello public-source archive — provenance and admission gates

Date: 2026-11-09. Gomri branch: research/vistacreate-source-rea-20261109.

**Source snapshot only:** 217 public files preserved under third_party/vistacreate-public/. No code has been imported into the running Gomri app, installed, built, deployed, or tested as a VistaCreate feature. The private VistaCreate editor, design model, rendering engine, AI object grabber and media corpus are **NOT** in these repositories.

## Pinned sources actually copied

| Folder | Real original source and commit pin | License / attribution | Files | Admission verdict |
|---|---|---|---:|---|
| crello-font-metrics-sizing/ | https://github.com/crello/font-metrics-sizing @ 73b6cbac91d109c74a265c05e1b67da326387150 | MIT, original historical Crello utility, 2018 | 7 | **P0 analysis** of Windows/macOS/Linux font-metric drift; source uses older native fonttools and unmaintained dependencies, do not install untouched |
| crello-react-lottie/ | https://github.com/crello/react-lottie @ 4b44b884089a7412b1abd5b57bf8549e7e217c6f | MIT, Crello **fork** of chenqingspring/react-lottie, which wraps Airbnb lottie-web; 2020 | 45 | **P1 reference** for SVG/Canvas Lottie playback and event hooks; React 16 / lottie-web 5.7 legacy, compare modern library first |
| crello-electron-render-service/ | https://github.com/crello/electron-render-service @ 23eb21131587f8bc6ed51d680e14042286f636c5 | MIT per package/repo metadata, fork of **msokk/electron-render-service**; 2017; root LICENSE not confirmed during inspection | 32 | **DO NOT RUN**: obsolete Electron ~1.6.2, user-specified URL-to-PDF/PNG/JPEG, query credential, risk of SSRF/unsafe network fetch. Historical architecture reference only, license text must be resolved before redistribution |
| vistaprint-ArteJS/ | https://github.com/VistaPrint/ArteJS @ 429042fe6b23435afc02e6c6cee3518249c7ebf9 | Apache-2.0, **VistaPrint-origin**, 2015; it is an adjacent Vista family source, NOT demonstrated VistaCreate code | 133 | **LOW / reference only**: jQuery 1.9 and obsolete Grunt/postinstall, not appropriate as modern Gomri rich text editor |

Total 217 committed files in four separate directories; 217 source files **does not mean 217 features**. Each folder preserves original source paths and any repository-provided notices. The study has not run dependency installation or code compilation.

## First-party repos reviewed but NOT copied

- https://github.com/depositphotos/vcr-kit @ 1ceb6d9fc37a398a8a1c8f1b4c8b332ac56e159a: public **bootstrap**, no clear redistribution license; documentation explicitly says the actual engineering kit is obtained from a **private GitLab repo** requiring a VistaCreate account and permission. It does **not** expose private production source. Never run its installer or try to access private GitLab assets without authorized access.
- https://github.com/depositphotos/api-sdk-php @ f18136a5b2103fdd89d6249a8d8baa4880584745: MIT, Depositphotos **stock API client** only, not VistaCreate editor/AI code. Requires credentials, stock content/license/payments may apply; not useful as zero-cost local Gomri core.
- Other Crello/depositphotos/VistaPrint GitHub repositories are inventoried in registry/vistacreate-public-github-inventory-2026-11-09.csv. A public upstream fork is not a vendor-authored proprietary module and 2015–2022 commits do not establish current use in 2026.

## New independent donor candidates, NOT copied in this source phase

| Capability | Candidate | Reported upstream license | Gate |
|---|---|---|---|
| Vector 2D editor | fabricjs/fabric.js | MIT | Compare against existing Presenton/Canvas for object identity, performance and RTL, avoid second source of truth |
| Canvas drag/resize scene graph | konvajs/konva | MIT | Use existing editor's renderer if already integrated; avoid duplicate frontends |
| Resizing/snapping/group transforms | daybrush/moveable | MIT | Compare bounded transform logic, keyboard/accessibility |
| Lottie playback | airbnb/lottie-web | MIT | Prefer maintained upstream vs Crello's old React 16 fork, check animation export parity |
| Background removal | danielgatis/rembg | MIT code | **Model weights licensed separately**; some models have commercial restriction; local memory/performance tests |
| Object selection/masking | facebookresearch/segment-anything | Apache-2.0 | Check model/weights rights, VRAM and image privacy; it does not automatically recreate an editable vector object |
| Native slides | gitbrent/PptxGenJS | MIT | Already in Gomri source evaluation; don't import twice |

The user prefers zero-cost and local privacy. All donor upgrades require exact code SHA, license+assets/weights check, local tests, rollback and measured benefit; no automatic paid VistaCreate, Depositphotos or third-party API use.

## Strong security and runtime boundaries

1. **Never execute the old Electron render service as found.** A network renderer that accepts arbitrary URLs and an accessKey query parameter can create SSRF and token-leak hazards. Use a sandboxed, no-network modern renderer with URL and resource policy enforcement if needed.
2. Font metrics must be **measured, not patched blindly**; modifying TTF/OTF OS/2 and hhea tables has distribution/fidelity/licensing implications. Validate the original font licenses and test cross-OS layout without rewriting user fonts in place.
3. Avoid production use of archived jQuery/Grunt/React 16 packages; modern dependencies already in Gomri are the incumbent.
4. Keep copied third-party notices and upstream/fork identities. DO NOT remove author attribution as part of a rebrand.
5. Do not copy VistaCreate private template media, music, customer files, browser profile storage, or license-gated images as though they were MIT source.
6. Never automatically send user files to a cloud API; no API account/credits were used for this study.
7. This source archive remains isolated in a DRAFT PR. The application and main branch remain unchanged.

## Quick comparison table for Gomri

| Donor | Technology actually relevant | Immediate outcome |
|---|---|---|
| Crello font tool | Cross-OS font ascender/descender/line gap | Add font-fidelity fixtures + safe metric analysis |
| Crello Lottie wrapper | Playback events, speed, segments, renderer choice | Extend animation QA and export degradation inventory |
| Crello render service | PDF/JPEG/PNG capture workflow | **Architecture reference only**; rebuild sandboxed, never ship 2017 runtime |
| VistaPrint ArteJS | Rich-text editing API design history | Low priority; use Gomri current rich text |
| Depositphotos API SDK | Stock image catalog + authentication | Not a no-cost local media library |
| VistaCreate private editor | Proprietary full engine | **Source not available** |

Additional research:
- docs/research/VISTACREATE_SOURCE_ENGINE_REA_2026-11-09.md
- docs/research/vistacreate-rea/01-current-product-behavior.md
- docs/research/vistacreate-rea/02-code-source-and-engine-inference.md
