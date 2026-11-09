# VistaCreate Deep REA — 03. Partner API, Design Pipeline, Asset Rights and Product Boundaries

Date: 2026-11-09. Evidence based on current VistaCreate/Depositphotos first-party partner marketing/documentation and public GitHub source. A **licensed partner API is not source code** and its existence does not mean an ordinary VistaCreate user can programmatically edit designs through a free public endpoint.

## 1. Product layers that must remain separate

**A — Consumer VistaCreate editor:** authenticated web/mobile design app, templates, manual editing, multi-page creation, optional AI, Pro features, exports and social posting.

**B — VistaCreate / Depositphotos Creative Suite API:** bespoke B2B editor/creative API. Its official overview offers an **advanced iframe**, white-label co-branding, configurable sidebar, embedded libraries, customizable design templates/formats, automatic replacement of text/images/videos in templates, preview/render output, and stock/AI services. Pricing is partnership-oriented, not an open no-cost local developer toolkit.

**C — Depositphotos Stock API:** separate media catalog/license system. Its old MIT PHP SDK exposes how authenticated accounts request assets; it does not include copyrighted stock files for unlimited redistribution.

**D — Private VistaCreate engineering kit:** public depositphotos/vcr-kit is an installer bootstrap; the real kit resides in private GitLab and requires organizational permission. Its private code was neither available nor accessed.

**Never conflate** these products and repositories into a single public VistaCreate source release.

Sources:
https://depositphotos.com/api-suite/graphic-editor.html
https://support.create.vista.com/hc/en-us/articles/29216091266972-What-is-a-Design-API
https://github.com/depositphotos/vcr-kit
https://github.com/depositphotos/api-sdk-php

## 2. B2B design API — real, grounded behavior, unknown implementation

Public partner page explicitly describes:
1. embed designer through an advanced iframe/API integration;
2. select rebrand/white-label UI;
3. allow customer-specific template formats, category collections and media libraries;
4. use template variable replacement with **text, image, video** data;
5. auto-render finished design or send it to editor for further customer changes;
6. display watermarked stock previews and connect a licensed stock library;
7. configure which editor sidebar tools are available.

### Architecture inferred for independent Gomri — NOT vendor proprietary source

    Partner app data and tokens
         -> Template identity and parameter schema
         -> Bound variable substitution
         -> Project/deck revision
         -> Renderer / screenshot / export adapter
         -> User edit (optional)
         -> Final deliverable and provenance receipt

This is a logical product contract any comparable API must solve. We did NOT recover VistaCreate's actual server JSON schema, its permission model, private template rendering implementation, partner billing rules, or private asset URLs.

### Proposed Gomri API contract

- POST design/generate: layout role, template ID, approved sources, requested output formats and Brand Kit.
- POST design/render-variants: one base deck, many target aspect ratios and their deterministic quality reports.
- POST design/patch: typed element mutation, base revision, allowed source refs, idempotency, scope.
- GET design/render-status and export-status: jobs with bounded retries.
- GET design/report: flattened native object audit + asset copyright/license provenance + clipping failures.
- GET template/parameters and POST template/render: typed template variables, escaped text, approved assets.
- NO upload to a remote vendor by default, no hidden fee or cloud credential.

P0 architecture should stay independent from the VistaCreate partner API; using it would cost money and would not give the full source code.

## 3. Responsive marketing variants: bigger opportunity than duplicating generic templates

VistaCreate's B2B page says Advanced Resize centers elements and scales background; the consumer help warns designers may need to manually reposition text/elements. A genuinely superior Gomri engine can:

- keep one semantically meaningful design system for title, chart, source quote, footer and hero media;
- derive 16:9 slide, 4:3 slide, 1:1 image, 9:16 carousel story and print PDF in one operation;
- preserve exact source figures and layout roles;
- use automatic smart reflow, cropping and object grouping;
- identify variants requiring manual review; never claim impossible one-click perfect results;
- generate design variants without accidentally turning native charts/tables into rasterized screenshots.

This is strategically stronger for Gomri than a brute force 200K-template reproduction; a reusable template component engine can produce families with better consistency.

## 4. AI Object Grabber / Object Remover: editing semantics

The official help says a user selects an object within an image using Smart Select or brush, optionally multiple objects, then clicks Grab. The object is removed from the original image and becomes a separate layer that can be moved/resized and copied between designs. Undo exists.

Potential independent decomposition (a **Gomri** design, not vendor internals):
- decode image and preserve source digest;
- compute one or multiple object-selection masks;
- anti-alias/feather masks and extract RGBA sprites into asset records;
- perform an image-inpainting fill on the remaining background, with visible quality/confidence;
- preserve a reversible composite transaction with original image, extracted masks and pixels;
- insert a new independent image layer on the scene graph (not pretend a text/vector/PowerPoint table);
- run privacy and size/format policy; no third-party upload by default.

**Not established:** exact VistaCreate model names, weights, inference stack, image-inpainting algorithm, commercial training licenses or latency. We do not have its object-grabber source.

Suggested candidates **not copied**: facebookresearch/segment-anything (Apache-2.0 source/model) for masks and danielgatis/rembg (MIT code) for background removal. rembg model weights can carry separate commercial restrictions; audit before download/use. For larger workflow, review local CPU/ONNX/VRAM cost on Windows. Avoid paid cloud by default.

Sources:
https://support.create.vista.com/hc/en-us/articles/29904242727068-How-to-edit-images-with-AI-Object-Grabber
https://github.com/facebookresearch/segment-anything
https://github.com/danielgatis/rembg

## 5. Animation and export design-contract

Current VistaCreate consumer docs define eight element effects and GIF/MP4 export, plus video timeline editing. The old crello/react-lottie fork is **real MIT source**, but it is a wrapper over Airbnb's Lottie renderer. It is not the full VistaCreate 2026 animation engine.

Gomri must represent a time-varying animation or clip explicitly:
- elementId, duration, start/end, easing, transforms/opacity, sequence, media and loop;
- a deterministic static frame for PDF/PNG;
- timeline and frame renderer for MP4/GIF;
- independently editable OOXML output where the target PPTX supports effects;
- error/report for effects that will rasterize or be omitted.

Do not claim CSS animation in editor = native PPTX animation. Support source IDs and voice/speaker notes unaffected by media timing.

## 6. Content library and asset rights — non-negotiable

VistaCreate's official Legal FAQ says its platform assets can be used **in designs in the platform under its conditions**, but animations/fonts/media may need separate licenses for external use, and raw creative assets cannot simply be downloaded as original reusable stock. This is a critical distinction:

- source code MIT/Apache vs fonts/images/videos/icons with independent rights;
- branded stock purchased/accessible in VistaCreate vs royalty-free outside the app;
- a finished commercial design vs a redistributed source asset/template pack;
- single-subscriber access vs transfer and sublicensing.

Never copy private VistaCreate templates or stock into a public Gomri repo merely because they are visible online. A user-claimed legal permission may be valid but it must cover **the exact assets/code and redistribution rights** before shipment.

Official:
https://support.create.vista.com/hc/en-us/articles/13402817714844-Legal-FAQ

## 7. API/source and security threat model

**Source import:** untrusted fonts, SVG, video and PDFs; bounds, parsing and decompression safety. Never execute executable parts of a copied app/template.

**Remote image acquisition:** URL SSRF (localhost/private networks), redirect rewriting and credentials leaks. No arbitrary browser capture service exposed.

**Template variable binding:** HTML/script injection through inserted copy; use escaped typed text, rights-safe media and allowed element types.

**Agent AI modifications:** untrusted source text is not system instruction; scoped patch operations and write-time ACL; preserve original visual and user edits with undo.

**Plugin/third-party code:** old Crello Electron 1.6/React16/jQuery stacks are unsafe deployment candidates. Keep them source-only until independent modern rebuild and transitive rights audit.

**Privacy:** no account login, vendor API calls, generated user media upload, billing actions, or access to private GitLab conducted by this research.

## 8. Gomri's actual competitive wedge

The user wants Gomri to beat Gamma/Beautiful.ai in **presentations**, not reimplement all of VistaCreate's social scheduling, massive stock procurement, e-commerce, or cloud operations.

Priority:
- P0: adaptive slide-to-multi-aspect responsive editing and cross-OS font fidelity.
- P1: object grabber and smart background removal as optional **asset tools**.
- P1: animation/video asset export with correct PPTX and PDF downgrade reports.
- P2: embedded editor/API and marketing production formats when flagship slides work.
- P3: scheduling and print-on-demand (separate potential future product).

No market-superiority claim is supported without independent benchmark. Source snapshots by themselves ship zero user-visible capabilities.
