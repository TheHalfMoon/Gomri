# PROBE FIXTURES — donor generation and export probe

**Provenance (required by `docs/FIXTURE_POLICY.md`):**

| Field | Value |
|---|---|
| **Source** | Generated in this mission from the donor repository `0xRafie/nextslide` @ `90a46f933b3056d27460400c915ef268a9ec3f56` (MIT, © 2026 Danish Rafie Ekaputra), using the donor's own `SKILL.md` workflow and `scripts/export-pptx.js`. |
| **License** | MIT (donor). The generated artifacts inherit the donor's MIT terms and are committed as research evidence of the donor's runtime behaviour. |
| **Creation date (UTC)** | 2026-10-22 |
| **Generator method** | Manual execution of the donor's documented pipeline against synthetic content. The synthetic topic is *"Ocean Plastic Reduction: 2026 Strategy"*. No real user data, customer data or production content was used. |
| **Acquisition method** | Donor clone → HTML deck authored per `SKILL.md` → `node scripts/export-pptx.js <deck>.html <deck>.pptx` (PptxGenJS `^3.12.0`). |
| **Regeneration** | Scripted end-to-end by `build_deck.py` + `gen_specs.py` in this directory. `build_deck.py` concatenates the donor's own `viewport-base.css`, `STYLE_PRESETS.md` `:root` block, `animation-library.md` keyframes and `html-template.md` JS controller **verbatim**; `gen_specs.py` holds the synthetic content. Regenerate with: `python3 gen_specs.py && for v in corporate-pro midnight-pro botanical; do python3 build_deck.py spec_$v.json deck_$v.html; done`, then `node <donor>/scripts/export-pptx.js deck_<v>.html deck_<v>.pptx`. Exact commands, versions, sizes and outputs: `../NEXTSLIDE_PROBE_RUNLOG.md`. |
| **Seed** | N/A — content is authored text, not generated randomly. |
| **Size** | Each artifact < 130 KB. Whole directory < 1.3 MB. Within the committed-fixture size budget. |

## Artifacts

| File | What it is |
|---|---|
| `deck_botanical.html` | Donor single-file HTML deck, Botanical preset |
| `deck_botanical.pptx` | Same deck exported to PPTX by the donor's exporter |
| `deck_corporate-pro.html` | Donor single-file HTML deck, Corporate Pro preset |
| `deck_corporate-pro.pptx` | Same deck exported to PPTX by the donor's exporter |
| `deck_corporate-pro-fixed.html` | Corporate Pro deck **with the `interactive-elements.md` CSS inlined** — the fix for defect D4 (widget CSS is never inlined by the donor's documented pipeline). It does **not** fix `animate-counter-up`; that defect is live in every deck and is evidenced by `shot_midnight_counter_bug.png`. |
| `deck_corporate-pro-fixed.pptx` | Its PPTX export |
| `deck_midnight-pro.html` | Donor single-file HTML deck, Midnight Pro preset |
| `deck_midnight-pro.pptx` | Same deck exported to PPTX by the donor's exporter |
| `extract_corporate-pro.txt` | Output of the donor's `extract-pptx.py` (text format) |
| `extract_midnight-pro.json` | Output of the donor's `extract-pptx.py` (JSON format) |
| `extract_pptx_PRISTINE_crash.log` | **Crash log** — the donor extractor failing on a pristine donor-generated PPTX |
| `extract_pptx_PATCHED_warnings.log` | Donor extractor output after a minimal patch, showing a residual warning |
| `extracted-images/` | Images written out by the donor extractor |
| `shot_chart_STYLED_with_interactive_CSS.png` | Rendered chart with the donor's interactive-element CSS applied |
| `shot_chart_UNSTYLED_per_SKILL.md.png` | Rendered chart with only the CSS the donor's documented pipeline actually inlines |
| `shot_midnight_blank_bento.png` | Render of the donor's bento-grid preset — evidence for the "preset advertises a bento layout that the codebase does not implement" finding |
| `shot_midnight_counter_bug.png` | **Visual proof** of the donor's `animate-counter-up` defect — the counter value is absent from the rendered slide |
| `shot_midnight_title.png` | Render of the donor's `title` layout (Midnight Pro preset) |
| `shot_midnight_two-column.png` | Render of the donor's `two-column` layout |
| `shot_midnight_image-left.png` | Render of the donor's `image-left` layout with an inline data-URI SVG |
| `shot_presenter_window.png` | The donor's actual presenter window — **shows a slide number, not a slide preview** (0 iframes, 0 images) |
| `shot_timeline_STYLED.png` / `shot_timeline_UNSTYLED.png` | Timeline widget with / without the inlined interactive CSS |
| `build_deck.py`, `gen_specs.py` | The generator scripts (see *Regeneration* above) |

## Independently verified property of the donor's PPTX exporter

Re-checked in this mission with `python-pptx` (Gomrey's own dependency), not with the donor's tooling:

| Deck | Slides | Shapes | Shapes with text | Pictures |
|---|---|---|---|---|
| `deck_botanical.pptx` | 6 | 23 | 23 | 0 |
| `deck_corporate-pro.pptx` | 9 | 29 | 28 | 0 |
| `deck_corporate-pro-fixed.pptx` | 9 | 29 | 28 | 0 |
| `deck_midnight-pro.pptx` | 9 | 27 | 24 | 2 |

**Conclusion:** the donor's PPTX export produces **genuinely editable text**, not rasterised slide
images. This is a positive property of the donor — but it does **not** establish superiority over
Gomrey's existing `@presenton/export-core` path, which is why `T-101` is `REJECT`ed rather than
adopted. See `../../TRANSPLANT_MATRIX.md`.

## Policy compliance

These fixtures are **synthetic-generated** under `config/fixture-policy.json`. They contain no real
user secrets, no private health or business data, no donor credentials and no production dumps.
They pass `scripts/scan-secrets.mjs` and `scripts/check-fixtures.mjs`.
