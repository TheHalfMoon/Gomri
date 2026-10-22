# W8 — Image Export (PNG / JPEG / WebP)

**Grain:** W8 from `research/rea/2026-10-22-nextslide-gamma/IMPLEMENTATION_GRAPH.md`
**Branch:** `feature/rea/w8-image-export`
**Base:** `main@5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Mission:** Issue #77
**Advances:** `F-E05`

---

## 1. Copy-first source transplant

### 1.1 What was adopted

| Field | Value |
|---|---|
| Donor package | `@presenton/export-core` v1.0.34 (open-source edition) |
| Donor artifact | `presenton-export-core-opensource-1.0.34.tgz` |
| Artifact sha256 | `17c5aef592721d996a4f658de03282764d0ba900ab01beb7ca10a0404d595079` |
| Upstream release | `github.com/presenton/presenton-export` |
| Adoption method | **COPY** — the donor's `export` and `html-to-any` task types already render one PNG per slide into a ZIP archive. That renderer is reused unchanged. |
| Donor task types used | `export` (production, URL-driven) and `html-to-any` (verification probe) |
| Donor format support | `"pdf" \| "pptx" \| "png"` — PNG was already implemented and never exposed by Gomrey |
| Licensing | The donor package is an external dependency, not first-party Gomrey source. Its terms remain with the package. No donor source file was copied into the Gomrey tree. |

### 1.2 What Gomrey wrote

Only the integration layer and the parts the donor does not provide:

| Gomrey file | Responsibility | Why it is new |
|---|---|---|
| `servers/fastapi/enums/export_format.py` | One authoritative export-format contract | The format was previously an inline `Literal["pptx","pdf"]` duplicated across six sites |
| `servers/fastapi/models/image_export_options.py` | Typed image export options (format, packaging, width, quality, background) | The donor has no image-options concept |
| `servers/fastapi/services/image_export_service.py` | Archive contract: entry names, slide order, format conversion, budget, hostile-input rejection | The donor emits a ZIP with its own naming and no conversion, budget or validation layer |
| `servers/fastapi/utils/export_utils.py` | Routes image exports to the renderer, then repackages; removes the intermediate | The donor has no Gomrey export orchestration |
| `servers/fastapi/services/export_task_service.py` | Accepts `"png"` in the runtime task payload | One-word widening of an existing literal |
| `servers/fastapi/api/{v1,v2}/ppt/endpoints/presentation.py` | Accepts the widened format and the image options | Boundary wiring |
| `servers/nextjs/lib/run-bundled-presentation-export.ts` | Declares `"png"` as a bundled runtime format | One-word widening of an existing type |
| `servers/nextjs/app/api/export-presentation/route.ts` | Accepts `"png"` at the export route | Boundary wiring |

**No new renderer was written.** The slide pixels come from the donor's Chromium renderer.

### 1.3 Dependency boundary

| Dependency | Version | Why |
|---|---|---|
| `pillow` | 12.2.0 | Already a declared FastAPI dependency (`pyproject.toml`: `pillow>=12.2.0`). Used for image re-encoding, resizing, and dimension probing. No dependency was added. |
| `sharp` / `jszip` | 0.35.3 / 3.10.2 | Transitive dependencies of the vendored donor package. The Gomrey side does not import them; it consumes the donor's PNG output through the ZIP contract. |

---

## 2. Behaviour

### 2.1 Public contract

`export_as` now accepts `pptx`, `pdf`, `png`, `jpeg`, `webp` on:

- `POST /api/v1/ppt/presentation/{id}/export`
- `POST /api/v1/ppt/presentation/generate`
- `POST /api/v1/ppt/presentation/edit`
- `POST /api/v1/ppt/presentation/derive`
- `POST /api/v2/ppt/presentation/generate/smart` (sync and async)
- `POST /api/nextjs/export-presentation`

Image exports accept an optional `image_export` object:

```json
{
  "format": "png | jpeg | webp",
  "packaging": "zip",
  "width": 320..7680,
  "quality": 1..100,
  "background": "#ffffff"
}
```

### 2.2 Rules that are enforced, not assumed

| Rule | Enforcement | Result on violation |
|---|---|---|
| `quality` is meaningless for PNG | Pydantic `model_validator` on `ImageExportOptions` | `422` — deterministic refusal |
| `packaging` other than `zip` | Pydantic `Literal["zip"]` | `422` |
| `width` outside 320..7680 | Pydantic `Field(ge, le)` | `422` |
| `background` not a hex colour | Pydantic `field_validator` | `422` |
| Target width changes the aspect ratio | Height is derived from the source aspect ratio; it is never independent | Aspect is preserved by construction |
| Archive entry escapes the archive | `ImageExportService._validate_entry_name` | `ImageExportValidationError` → HTTP 500 with a specific detail |
| Archive entry is nested or absolute | same guard | same |
| Archive entry is not a rendered PNG slide | PNG signature check | same |
| Slide is unreadable or empty | Pillow open + size check | same |
| Too many slides, or an oversized archive/image | budget constants in `image_export_service.py` | `ImageExportBudgetError` |
| The rendered archive is missing | explicit check | `ImageExportValidationError` |
| The rendered archive is not a readable ZIP | `zipfile.BadZipFile` is mapped to a contract error | `ImageExportValidationError` |
| The slide is a decompression bomb | the pixel budget is checked before the decode; Pillow's own bomb error is mapped too | `ImageExportBudgetError` |
| The exported bytes exceed the budget | the produced bytes are measured, not just the input | `ImageExportBudgetError` |

### 2.3 Output contract

- The deliverable is a **ZIP** (`application/zip`) with one image per slide.
- Entry names are `slide_001.<ext>`, `slide_002.<ext>`, … — the renderer's own convention, so the
  FastAPI surface and the Next.js surface describe the same slides the same way.
- Entry order is the **numeric slide index**, not the lexical order of the donor's file names.
- The archive file name is `<title>_<format>_<unique>.zip`. The unique suffix matters: a title is
  not unique (two presentations can share one, and one presentation can be exported twice at the
  same time), and without it the second export silently overwrote the first one's artifact.
- The archive is written to a hidden staging file and published with an atomic rename, so a
  downloader never observes a half-written ZIP and a concurrent export never truncates another.
- PNG output is **byte-identical** to what the renderer produced (no re-encode), so PNG export
  adds zero lossy steps.
- JPEG and WebP are re-encoded from the rendered PNG. JPEG flattens transparency onto the
  requested background colour; PNG and WebP keep the alpha channel, including for palettised
  PNGs.
- Every rendered slide is **decoded** before it is accepted, so a truncated or corrupt slide is
  refused rather than written into the delivered archive.
- The rendered intermediate archive is deleted after the Gomrey archive is written — on the success
  path and on every failure path — so exactly one downloadable artifact survives.
- The budget is enforced on the input **and** on the produced bytes.

---

## 3. Test evidence

### 3.1 Deterministic unit tests

```text
servers/fastapi/.venv/bin/python -m pytest tests/unit/test_image_export_service.py tests/unit/test_export_format_contract.py -q
40 passed in 2.53s
```

| Area | Coverage |
|---|---|
| Format contract | The six formats split into disjoint document/image sets; unknown formats refused; the effective options are always rebuilt through the model, so an object that bypassed validation cannot reach the encoder |
| Options model | Unknown format, unsupported packaging, quality-on-PNG, bad background, out-of-range width and quality all refused |
| Archive layout | Deterministic entry names, numeric slide ordering, per-slide dimensions reported |
| Fidelity | PNG output is byte-identical to the rendered slide; rendered pixel colour survives the JPEG path |
| Alpha | Transparent PNG flattens onto the requested JPEG background |
| Resolution | `width=640` on a 1280×720 slide yields 640×360; `width=1920` yields 1920×1080 |
| Hostile input | Path traversal, absolute names, nested names, non-image entries, corrupt PNG, truncated PNG, empty archive, over-budget slide count, a rendered archive that is not a ZIP, a decompression-bomb slide, a missing archive |
| Output budget | The produced bytes are measured against the image and archive budgets |
| Concurrency | Two exports of one title produce two archives; a failed export leaves no staging file and no partial archive |
| Distinctness | Exporting one deck as PNG and as JPEG yields two archives, not one overwritten |

### 3.2 Real end-to-end tests

```text
servers/fastapi/.venv/bin/python -m pytest tests/integration/test_image_export_end_to_end.py -q
7 passed in 46.56s
```

These are **not** mocked. The test:

1. serves a real 4-slide HTML deck over a real local HTTP server;
2. drives the **real** vendored `@presenton/export-core` runtime, which launches a real Chromium
   and paints every slide at 1280×720;
3. runs the **real** `export_presentation` → `build_image_archive` path over the produced bytes;
4. asserts on the produced bytes: PNG signature, exact canvas size, one distinct rendered image
   per slide, ordering, the absence of the intermediate archive, and the JPEG and WebP
   conversions.

The deck includes an Arabic RTL slide (`مرحبا بالعالم`) and a mixed-script slide, so the rendered
output covers RTL shaping as well as Latin.

If the local environment cannot run the renderer (no Node runtime, no export package, or no
Chromium in the Puppeteer cache), the test **skips with the precise reason** and records
`E2E_NOT_EXECUTED`. It never reports a skip as a pass.

### 3.3 Regression runs on the same tree

| Suite | Command | Result |
|---|---|---|
| FastAPI (all) | `servers/fastapi/.venv/bin/python -m pytest -q` | **1172 passed**, 10 pre-existing warnings |
| Next.js (all) | `cd servers/nextjs && node --test` | **76 passed / 0 failed** |
| Repository tooling | `npm test` (repo root) | **48 passed / 0 failed** |

### 3.4 Visual evidence

`RENDER_SAMPLES/` holds one rendered slide per format, taken from the real render described
above, plus `MANIFEST.sha256`. The Arabic RTL sample was inspected visually: the glyphs are
correctly shaped and right-to-left, and the canvas is exactly 1280×720.

---

## 4. Known limits, recorded not hidden

- **The render quality preset is the donor's low-quality preset.** The vendored package is the
  open-source edition, which forces `quality: "low"` for the `export` and `html-to-any` task
  types. W8 does not change that; adopting the full edition would change the donor's licensing
  surface and is a separate decision.
- **The image export reuses the PPTX/PPTX render path.** The donor renders at the fixed
  1280×720 slide canvas. A `width` larger than 1280 upscales the rendered pixels; it does not
  re-render at a higher device scale factor.
- **Presentation notes are not part of an image export.** Images carry no speaker notes, and
  there is no per-slide metadata sidecar in the archive. The archive is exactly the images.
- **The archive contains images only.** If a future donor revision adds a manifest to the PNG
  ZIP, the current service refuses that archive rather than silently dropping the entry. The
  guard is a deliberate, deterministic refusal.
- **The Next.js export route accepts `pdf`, `pptx` and `png` only.** JPEG and WebP need the
  re-encode step, which lives in the FastAPI service, so the Next.js route is the renderer
  surface and the FastAPI surface is the image-export surface. Both use the same slide entry
  names, so the two surfaces describe the same slides the same way.
- **`D1_LOCAL_NOT_EXECUTED`.** See `TOOL_EXECUTION_MATRIX.md`.

---

## 5. Rollback

Every change is additive:

- Delete `servers/fastapi/enums/export_format.py`, `servers/fastapi/models/image_export_options.py`
  and `servers/fastapi/services/image_export_service.py`.
- Restore the `Literal["pptx", "pdf"]` annotations in
  `servers/fastapi/models/generate_presentation_request.py`,
  `servers/fastapi/models/presentation_from_template.py`,
  `servers/fastapi/api/v1/ppt/endpoints/presentation.py` and
  `servers/fastapi/api/v2/ppt/endpoints/presentation.py`, and remove the `image_options` /
  `image_export` parameters.
- Restore `Literal["pdf", "pptx"]` in
  `servers/fastapi/services/export_task_service.py::export_from_url` and
  `"pdf" | "pptx"` in `servers/nextjs/lib/run-bundled-presentation-export.ts` and
  `servers/nextjs/app/api/export-presentation/route.ts`.

No persisted data, migration, protocol, or public import path changes, so the rollback is a
revert with no migration.
