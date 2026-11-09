# VistaCreate 2026 Deep REA — 01. Product, Editor, AI and Export Surface

**Date:** 2026-11-09. **Scope:** official publicly documented VistaCreate (formerly Crello), including web, mobile and business partner API. This is an **external evidence analysis, not a live authenticated editor walkthrough**; no source deck/customer data was accessed.

## 1. What product we are actually studying

VistaCreate is a creative design suite for posters, ads, social graphics, print formats, image/video assets, motion graphics and multi-page presentations. It is not a direct equivalent of Beautiful.ai's self-reflowing Smart Slides or Gamma's research-to-deck agent, although its design editor and branded output workflows can improve Gomri.

Official pages advertise:
- Starter: 100,000+ free design templates and a large free asset set; 85 formats; one Brand Kit; social media scheduling; desktop web/mobile editing.
- Pro: 200,000+ templates, premium licensed stock, AI Writer, AI Image Generator, AI object/background removers, unlimited Brand Kits, HD export, one-click multi-size Resize, history and team features.
- Up to 100 pages per project; multi-page projects work on **web**, not current mobile app.
- Common design outputs include static/animated assets, brochures and presentations.

**Marketing numbers vary by plan, date and account** (100K free vs 200K total, 170M stock in editor vs 335M catalog in the separate B2B API suite). Do not treat these as 200K transferable, open-source templates; no private template library or stock media was copied.

Sources:
https://support.create.vista.com/hc/en-us/articles/360021367319-VistaCreate-Free-Starter-Plan
https://support.create.vista.com/hc/en-us/articles/360021367339-What-is-included-in-VistaCreate-Pro-plan
https://support.create.vista.com/hc/en-us/articles/360016728300-How-many-pages-can-a-VistaCreate-design-have

## 2. Interactive canvas/editor — observed from official documentation, not internal code

Core operations:
- create a design in a chosen format or custom dimensions, use a template or a blank artboard;
- add text, images, shapes, icons, frames, static/animated backgrounds and stickers;
- resize, move, rotate, flip, crop, align and reorder objects; adjust transparency and styling;
- replace an existing media slot by dragging new content over it;
- manage pages and copies, move between formats, keep projects in folders, autosave when signed in;
- apply global Styles to switch palettes and font pairings; Brand Kits hold logos, hex colors and uploaded fonts.

**Text details:** add/edit fonts and text boxes, image/video text masks, style presets, left/center/right align, spacing, bold/italic/underline, color picker and link embedding in PDF. There are 7 static text effects: Outline, Shadow, Text Box, Echo, Glitch, Reflection and Curved. Help says one text effect per box. It mentions Hebrew, Latin and Cyrillic in its text/font guide, but does **not establish an Arabic rendering/export benchmark**. A missing Arabic statement is not proof of non-support.

Sources:
https://support.create.vista.com/hc/en-us/articles/360026118834-How-do-I-edit-a-template-in-VistaCreate
https://support.create.vista.com/hc/en-us/articles/360021453259-How-do-I-work-with-text-in-VistaCreate
https://support.create.vista.com/hc/en-us/articles/4405990538002-How-do-I-apply-text-effects

## 3. Multi-size Resize (highest-impact competing design feature)

The official Copy & Resize UI allows:
- choose a new format from presets or enter dimensions;
- choose multiple target sizes in one request;
- copy into separate projects/tabs, retaining original;
- automatically resize the background and roughly center/scaled objects;
- inspect each result manually afterward; text and object placement may need repair;
- Pro plan needed for Resize.

**Critical verified weakness:** Vendor warns about post-resize manual adjustment. Its branded B2B editor API describes dynamic centering and background fit rather than guaranteeing semantic constraints or full auto-reflow. Gomri should implement a **content-aware reflow solver**, not merely center every original object. Preserve title hierarchy, native chart values, image crop and cite locations.

Sources:
https://support.create.vista.com/hc/en-us/articles/360033989293-How-to-resize-designs-in-VistaCreate
https://depositphotos.com/api-suite/graphic-editor.html

### Proposed Gomri resize invariants

- stable original DeckIR with target variations derived from source, never destructive;
- geometry expressed as content-role constraints, not hardcoded pixels only;
- user-invokable 16:9 -> 4:3 -> 1:1 -> 9:16 -> print format;
- preserve semantic reading order and key-chart structure;
- per-variant responsive typography/asset-crop/margins and RTL;
- restore or link the source object when variant is edited;
- detect overlap, clipped text, source claims altered, SVG crop, font fallback;
- each variant shows a quality report and undo/compare.

This is a **Gomri architecture proposal**. No actual VistaCreate algorithm has been extracted.

## 4. AI surface: separate tools, not one proven universal engine

Published features:
- AI Writer: generate, rewrite, shorten, expand, improve, translate text and change tone from a selected text box. Pro.
- AI Image Generator: prompt + style/format + image variants; Pro, documented 100 images/month per account/team; reference image transforms supported.
- AI Background Remover / Background Replacer / AI Object Remover for uploaded content.
- **AI Object Grabber**: brush or Smart Select region, optionally select multiple objects, separate object into an independently movable image layer while removing it from source image, Undo if wrong.
- Official October 2026 help says AI Assistant can create a **template from a prompt** and revise it conversationally. We did not observe this live or inspect its models; plan/availability may vary.

**Editability distinction:** Object Grabber returns an *editable image layer*, not an automatic reconstruction into native Bézier paths, text, or PPTX chart data. Never claim AI photo segmentation yields fully editable semantic objects.

Sources:
https://support.create.vista.com/hc/en-us/articles/24926528042524-How-to-write-text-with-AI-Writer
https://support.create.vista.com/hc/en-us/articles/22649408784284-How-to-generate-images-with-AI-in-VistaCreate
https://support.create.vista.com/hc/en-us/articles/29904242727068-How-to-edit-images-with-AI-Object-Grabber
https://support.create.vista.com/hc/en-us/articles/360027358213-How-do-I-create-custom-templates-in-VistaCreate

## 5. Animation and video authoring

Current help lists **eight animation effects** applied to individual elements: Move, Fade, Scale, Zoom, Wobble, Flash, Shake and Spin; **one effect per element**, with a preview. Animation effects, images, video and music combine into multi-page MP4/GIF design output. The video editor provides crop, split, trim, per-page duration, music fade, and segment timeline. The help lists MOV/MP4 uploads under 200MB, and a typical 60-second clip limit.

These are consumer authoring operations, not evidence of a reusable animation scripting API or cross-format PowerPoint animation fidelity. Lottie JSON output is not guaranteed in the VistaCreate export UI.

Sources:
https://support.create.vista.com/hc/en-us/articles/360026488234-How-do-I-animate-a-design-in-VistaCreate
https://support.create.vista.com/hc/en-us/articles/6874292482076-How-do-I-edit-videos-in-VistaCreate

## 6. Export, print and publishing boundaries

Official export menu explicitly lists JPG, PNG, transparent PNG, PDF Standard, PDF Print, MP4 and GIF. **PPTX is absent from this standard menu**, so do not assume native editable PowerPoint export is part of the current consumer offer. The product supports presentations/multi-page PDF output, but a PDF screenshot is not the same as natively editable slide content.

- "Print PDF" path and related VistaPrint print production integration are significant to a broad design product, but not the core Gomri presentation engine.
- Social scheduling and direct Facebook/Instagram/Pinterest publishing are product features, not necessarily exposed as a public free programmable API.
- History/team/HD export and unlimited Brand Kit depend on paid plan.

Sources:
https://support.create.vista.com/hc/en-us/articles/115004246593-How-do-I-save-and-download-my-finished-design
https://support.create.vista.com/hc/en-us/articles/360016027699-How-do-I-download-my-design-in-high-quality-in-VistaCreate

## 7. Competitive implications

| Feature | VistaCreate documented | Gomri strategy |
|---|---|---|
| Custom graphics and slides | strong, large template/media store | maintain editable Presenton deck + reusable graphic formats |
| Fast aspect resize | Copy & Resize, may need manual repair | semantic role-aware reflow and visual QA |
| Native PowerPoint | not in general listed export menu | Gomri keeps a tested editable PPTX path |
| Motion design | eight effects, animation/video timeline | bounded Lottie + slide animation path, export disclosures |
| Brand Kits | logo/fonts/colors, 1 on Free, unlimited Pro | versioned BrandIR with source and font licenses |
| Image segmentation | Object Grabber, selectable object extracted | evaluate local SAM/rembg and save as image layer, not fake vector |
| AI text edits | selected text rewrites via Pro AI Writer | preserve verified claims and target scope using existing NarrIR |
| Social scheduler/print | strong | **do not build for Gomri MVP** |

## 8. Unverified and negative scope

- Did **not** access a logged-in VistaCreate design or inspect authenticated editor operations.
- No private template assets, project JSON, browser profile/cookies, user-generated designs or proprietary AI model source retrieved.
- No PPTX editor/import/export superiority measurement executed.
- No paid API or model endpoint called; no credit consumed.
- All open source repositories discovered were evaluated as historical or adjacent technology; there is no source-backed proof their exact code still ships in the 2026 VistaCreate app.
- This chapter provides a behavior/specification baseline for 50 planned tests, NOT 50 actual passes.
