# VistaCreate Deep REA — 02: Actual Public Source and Engineering Boundaries

Research date: 2026-11-09. The public source linked here was inspected through official GitHub repositories. The material in the Gomri research branch is **a pinned source snapshot**, not installed or integrated running code. No proprietary VistaCreate editor source was obtained.

## 1. GitHub survey

The public GitHub organizations surveyed comprise 61 repositories: depositphotos 14, crello 17, VistaPrint 30. An inventory categorizes forks vs originally authored modules, licenses, priority and specific potential use in registry/vistacreate-public-github-inventory-2026-11-09.csv. Most repositories are unrelated build/infra tools or old forks; **a corporate repo name is not proof that it runs in VistaCreate in 2026.**

Four sources were selected, copied at exact SHAs and preserved under third_party/vistacreate-public/ for inspection. Their original rights and limitations are documented in SOURCE_REGISTER.md.

## 2. Crello font-metrics-sizing: the most relevant original donor

Repo: https://github.com/crello/font-metrics-sizing
Commit: 73b6cbac91d109c74a265c05e1b67da326387150. MIT, original Crello utility, seven files, last active 2018.

**Actual code in index.js:** a Node utility to normalize TrueType/OpenType font metrics across Windows vs Unix-like systems. It reads ascender, descender, lineGap and unitsPerEm from TrueType OS/2 and hhea tables, calculates line-spacing based on UPM and a requested factor, and writes recomputed vertical values before compiling the font again using fonttools and xml2js. It takes a buffer and rejects invalid factors.

The mechanism addresses a real Gomri risk: browser preview text wrapping may differ from native PowerPoint or Electron on Windows/macOS/Linux. This utility is **not a browser renderer**, and changing font binaries does NOT guarantee correct Arabic shaping, word wrapping or line breaks.

**Hazards:** the package's npm test script explicitly has no tests; a native fonttools dependency points to an old Crello fork, xml2js is pinned to 0.4.19. Font redistribution/editing may be license-restricted; never patch someone else's original font file automatically. Proposed action: adapt **read-only font metrics analysis** and systematic native export/RTL fixtures; keep vendor code snapshot quarantine.

## 3. Crello react-lottie: animation adapter (fork, not engine)

Repo: https://github.com/crello/react-lottie
Commit: 4b44b884089a7412b1abd5b57bf8549e7e217c6f. MIT, 45 files. Historical Crello fork of chenqingspring/react-lottie (wrapper around Airbnb's lottie-web), version 0.0.11, last pushed 2020.

**Actual package:** typed React component with SVG/Canvas/HTML animation renderer choices; playing/paused/stopped state, speed, direction, segments, loops, autoplay, event listeners, and example code.

**Hazards:** React 16 and TypeScript 3-era peer dependencies; generated JSON/media assets may have different rights. Browser animation does not imply native PowerPoint animations nor deterministic PNG/PDF frame output. Proposed Gomri action: inspect Lottie binding/preview handling but prefer current maintained upstream and current Gomri animation infra rather than install another legacy React runtime.

## 4. Crello electron-render-service: do not execute

Repo: https://github.com/crello/electron-render-service
Commit: 23eb21131587f8bc6ed51d680e14042286f636c5. 32 files. Historical fork of msokk/electron-render-service, not Crello-authored core renderer. Package/repository metadata says MIT; a root license file was not found during direct inspection, so full notices must be resolved before binary distribution.

Source README/package defines HTML or URL -> PDF/PNG/JPEG endpoints, clipping rectangles, renderer pool, delayed capture, waitForText, and a credential passed as an accessKey query parameter. Actual dependency is Electron ~1.6.2 from 2017.

**Hard no-go:** obsolete browser engine and user-submitted URLs risk SSRF, internal network exposure, remote code/security issues and token leakage. This 2017 service was copied only as non-running history; **never run, expose, bundle or use it for production Gomri**. A safe alternative is a modern disposable renderer with no network, input sanitization, bounded resources, URL allowlists and sandboxing.

## 5. VistaPrint ArteJS: an adjacent historical editor

Repo: https://github.com/VistaPrint/ArteJS
Commit: 429042fe6b23435afc02e6c6cee3518249c7ebf9. Apache-2.0, 133 files. Original VistaPrint project from 2015, version 0.3.0, rich text WYSIWYG editor. Uses jQuery ~1.9, Grunt and postinstall commands. It is **NOT demonstrated to be the modern VistaCreate text engine**.

Potential research value: structured rich text format/normalization and cross-browser formatting. Production recommendation: retain Gomri's tested modern text editor and avoid installing this obsolete stack. Any reusable idea needs independent modern implementation/test.

## 6. Private-code discovery: depositphotos/vcr-kit

Repo: https://github.com/depositphotos/vcr-kit
Public SHA: 1ceb6d9fc37a398a8a1c8f1b4c8b332ac56e159a. README explains an onboarding bootstrap that checks for macOS, installs tools, prompts GitLab organizational login, then downloads the actual engineering kit from a **private GitLab repository**. No complete current VistaCreate product source is included. No clear public redistribution license was found for this kit. We **did not execute it**, obtain credentials or access private sources.

A public bootstrap pointing to private source is not permission to retrieve that private repository. It also is not evidence of the internal editor's exact database, rendering library, product API or model weights.

## 7. Other repos considered but not copied

- https://github.com/depositphotos/api-sdk-php — MIT PHP Depositphotos *stock-image API client*, requires API key and stock-license terms. Not a free media library or VistaCreate editor.
- https://github.com/crello/gopdf — fork of third-party PDF generator; not necessarily current.
- https://github.com/crello/node-fonttools — old native dependency, license status needs confirmation.
- https://github.com/crello/exif-js and go-jpeg-image-structure — metadata/EXIF forks.
- https://github.com/crello/react-lottie is not the native designer; the underlying animation implementation is upstream lottie-web.

## 8. Competitive source-led architectural inference (our design, NOT vendor internals)

The official VistaCreate product demonstrably needs typed movable elements, design/page geometry, brand references, animation settings, crop/transparency, media assets and variants across artboard sizes. This **does not prove** it uses Fabric, Konva, WebGL, custom ProseMirror, or any particular library.

Proposed Gomri representation:

    DesignDocument:
       documentId, revision, locale, brandKitRef
       designVariants: [ { format, width, height, pageIds[] } ]
       page: { pageId, nodes[], timeline?, sourceRefs[] }
       node: { elementId, kind, geometry, constraints, styleRef,
               assetRef?, animation?, sourceClaimRefs[] }

The same canonical source graph should yield 16:9 slides, 4:3, 1:1 social cards, 9:16, PDF and images. PowerPoint native object export should use typed semantic nodes; video/GIF animation export uses a separately qualified timeline/render path. No graphics image should be falsely called an editable chart/table.

## 9. Source-status conclusion

YES: 217 public files were copied, exact source and rights recorded. YES: font/animation/render/rich-text code and vendor current product behavior were inspected. NO: this is not the VistaCreate private editor source. NO: any source was implemented/tested in Gomri runtime. NO: old source should be shipped solely because it is publicly readable.

See third_party/vistacreate-public/SOURCE_REGISTER.md, plus the 61-repo inventory.
