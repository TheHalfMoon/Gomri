# VistaCreate Deep REA — 05. Fifty Black-Box Experiments, Source Adoption and Release Gates

Date: 2026-11-09. The scenarios below are **planned but NOT RUN** against an authenticated VistaCreate editor. Product features are source-graded from public help and marketing, not actual user workspace tests. Use synthetic non-private designs and lawful authorized access. Do not bypass trial/plan/payment requirements; do not collect login tokens, browser cookies or internal API calls.

## 1. Evidence protocol for each test

Each test record stores: scenario ID; product/surface; test date; source URL/evidence; account/plan and gated availability; synthetic input digest; before/after screenshot or video if authorized; target design format; output image/PDF/MP4/GIF; editable object count; checked claims; observed result; reviewer assessment; external credits spent (if any); confidence and limitations.

Possible statuses: PASS, FAIL, PARTIAL, NOT_RUN, BLOCKED_ACCESS, INCONCLUSIVE. No marketing screenshots or public README are test passes.

## 2. Fifty cases in 10 families

| ID | Experiment | What it should reveal |
|---|---|---|
| A01 | Start from an empty 16:9 presentation | Canvas/slide object primitives |
| A02 | Start from a social template in square aspect | Asset/template adaptation |
| A03 | Create a 4:3 presentation and add 20 slides | Multi-page editor viability |
| A04 | Create design with 100 pages | Document limits/performance |
| A05 | Try 101 pages | Limit/refusal/recovery behavior |
| B01 | Add rich text in 3 fonts | Text metrics, fallback and spacing |
| B02 | Put Arabic and Latin numerals/diacritics in one title | Script shaping and bidi |
| B03 | Use curved text and compare static export | Per-element transform fidelity |
| B04 | Apply photo/video inside text mask | Media-text composite behavior |
| B05 | Select overlapping icons/shapes and reorder | Z-order/selection model |
| C01 | Resize 16:9 -> 9:16 with chart and title | Semantic responsive reflow vs recenter |
| C02 | Resize same deck to 4:3 and square simultaneously | Multi-target identity and variations |
| C03 | Resize image-filled title frame | Crop focal point preservation |
| C04 | Resize page with dense 12-row table | Overflow/data loss |
| C05 | Resize mixed RTL header and footer | Typography, logical reading order |
| D01 | Apply Brand Kit palette to 5 pages | Global token use and local overrides |
| D02 | Upload custom permitted font and apply | Font metrics and file constraints |
| D03 | Extract palette from image with Styles | Color extraction/edit semantics |
| D04 | Create/reuse team Brand Kit | Inheritance and team policy |
| D05 | Change brand logo and check all pages | Global vs local logo refs |
| E01 | Generate image using a synthetic prompt | Prompt constraints and asset insertion |
| E02 | Use reference image to transform style | Semantic preservation and rights |
| E03 | Ask AI Writer to shorten selected headline | Text change scope |
| E04 | Ask AI Writer to translate one text box to Arabic | RTL fit and data identity |
| E05 | Ask AI Assistant to create a reusable template from prompt | New 2026 workflow and availability |
| F01 | Remove background of portrait | Edge transparency and artifacts |
| F02 | Object Grabber Smart Select one object | Object sprite and background inpaint |
| F03 | Grab two overlapping objects with multi-selection | Separate masks and layer editability |
| F04 | Grab object then Undo | True non-destructive restore |
| F05 | Grab text-bearing object | Does image layer retain editable text semantics? |
| G01 | Apply each of eight effects separately | Effects and default timing |
| G02 | Apply two effects to same object | One-effect constraint |
| G03 | Lottie vs native Move/Spin media playback | Actual editor animation format |
| G04 | Export multi-page animated design to GIF | Frames/order/duration |
| G05 | Export MP4 with video and audio | Timeline sync and output quality |
| H01 | Export one-page static design to transparent PNG | Alpha fidelity |
| H02 | Export 10-page design as PDF Standard | Page order and type |
| H03 | Export PDF Print and inspect fonts | Embedded fonts and quality |
| H04 | Try editable PPTX in consumer export menu | Availability vs documented omission |
| H05 | Export linked text as PDF and image | Hyperlink preservation vs loss |
| I01 | Share project with teammate and change one object | Attribution/sync |
| I02 | Two editors move same object | Collision resolution |
| I03 | Restore version after later edits | Non-destructive restore semantics |
| I04 | Schedule a social design to an authorized test account | Permissions and publish behavior |
| I05 | Try multi-page editor on mobile | Platform feature gap |
| J01 | Upload malformed image or font | Parser safe rejection |
| J02 | Insert remote image pointing to localhost | URL fetch/SSRF refusal |
| J03 | Put malicious instruction in template text before AI rewrite | Untrusted content as data |
| J04 | Reuse commercial template asset outside VistaCreate | Rights/transfer warning |
| J05 | Resize duplicate twice under latency/network loss | Duplicate transaction or recover |

This is exactly **50 proposed experiments**, none executed in this REA. Some are plan- or account-gated, or technically inaccessible; mark BLOCKED_ACCESS instead of guessing.

## 3. Engine-level fixtures for Gomri, entirely local and zero-cost

A real independent Gomri engineering suite can start without VistaCreate access:

- FX-01: dense Arabic/English slide with diacritics and a chart, rendered 16:9 / 4:3 / 1:1 / 9:16.
- FX-02: 8-element dashboard with true 12x12 data table and numeric source references.
- FX-03: 60-page synthetic deck for memory/performance.
- FX-04: background image with legal local stock content and focal-point boxes, 5 formats.
- FX-05: custom-font metrics test using fonts whose licenses permit testing.
- FX-06: Lottie animation with paused/mid/final frame and PDF/PPTX/MP4 outputs.
- FX-07: no-source invented figure request; reject/review.
- FX-08: object segmentation from licensed synthetic shapes (not private photo), mask and reversible asset extraction.
- FX-09: split/merge/undo text editing with revision conflicts.
- FX-10: shared source deck with variant copy-on-write (one variant edit shouldn't delete source elements).
- FX-11: malformed SVG/PDF/video/TTF/URL and SSRF attempts.
- FX-12: disabled network/account tokens; screenshot render never calls external source.
- FX-13: re-import native PPTX table/chart and compare editable objects/notes.
- FX-14: resize metadata preservation, including source citations and licensing manifest.
- FX-15: animation loss report when static PPTX export lacks a dynamic feature.

Use 30 original synthetic decks, minimum 5 aspect profiles and per-format screenshots and export audits. Every expected failure requires a negative control proving the test actually catches it.

## 4. Comparative benchmark rubric (proposed)

| Dimension | Weight | What to measure |
|---|---:|---|
| Responsive reflow and visual design | 25% | Human masked preference, clipping, layout retention |
| Native editable PPTX/semantic data fidelity | 20% | Real text/chart/table/chart data/notes after export |
| Typography and internationalization | 15% | Windows/macOS/Linux font layout, Arabic RTL and bidi |
| AI targeted edit correctness | 15% | Selected text, preserved claims, undo and revisions |
| Image extraction, background and animation | 15% | Local quality and independent object/asset accuracy |
| Security, asset rights and privacy | 10% | Zero forbidden reads/writes/uploads, explicit licenses |

Important: these weights reflect **Gomri's goal**, not VistaCreate's official scores. Report each dimension separately; do not hide a security or native-data failure inside a weighted average.

## 5. Source admission release checklist

- Four imported code trees checked against pinned SHAs; notices and authors preserved.
- Historical code does not ship unless reviewed and independently tested.
- No binary font modifications without font license and user permission.
- Electron 1.6/URL renderer marked DO NOT EXECUTE, never used in live service.
- Lottie wrapper requires React/Next.js compatibility and asset license checks.
- No external stock, hidden API key or model weights copied without rights.
- All 30×5 variant fixtures show no silent data/claim losses.
- All security/ACL/SSRF tests pass exact tested candidate.
- Windows smoke, plus macOS/Linux where supported, and release-quality screenshots.
- Independent review and exact-head CI must pass before merge.
- PR remains Draft if even one major gate is unresolved.

## 6. Where to implement, not expand

Priority in Gomri:
1. VC-G1 Adaptive Resize & cross-platform font QA in existing slide editor.
2. VC-G2 Scoped AI text patch with evidence preservation and Undo.
3. VC-G3 Optional local Object Grabber/Background Remover with asset licensing.
4. VC-G4 Animation/video frames and native PowerPoint degradation reporting.
5. VC-G5 Broader brand/template B2B API only after slides are shippable.

Do not start with a 200K-template database, social publishing scheduler, proprietary VistaCreate partner API or a second slide canvas. The goal is faster quality improvement with minimal duplicated code.

## 7. Declared limitations

No live competitor test was run, no independent numerical superiority finding exists, and no closed VistaCreate source was acquired. A Github source archive is not product implementation, and an externally documented feature is not a code-level reconstruction of the proprietary algorithms. All claims of Gomri superiority must follow measured acceptance evidence and validated export artifacts.
