# W12 — Export Fidelity Regression Harness: Implementation Design

> **Scope.** Gomrey exports PPTX/PDF through an external pinned package
> (`@presenton/export-core` v1.0.34) and imports PPTX back to JSON in Python.
> A round trip exists in code but is untested. W12 builds a deterministic
> fidelity harness that exports a synthetic deck, re-imports it, and asserts on
> what survived.
>
> **Status.** Design only. No source file was modified. All "measured" facts
> below were produced by executing the pinned runtime in this checkout
> (`presentation-export/node_modules/@presenton/export-core@1.0.34`).
>
> **Repo state caveat.** The task named branch
> `feature/rea/w3-evidence-bound-narrative` @ `87b6bf9`. At analysis time the
> working tree had been switched by a concurrent session to
> `feature/rea/w13-arabic-rtl` @ `5f299a7`, and `research/` did not exist on
> that branch. Every source file this design cites was verified byte-identical
> between `87b6bf9` and the working tree
> (`git diff --quiet 87b6bf9 -- <file>` → SAME for all ten files listed in
> §A.1). The deliverable was written to the absolute path requested;
> it is therefore **untracked** on whatever branch is currently checked out.
> Whoever lands W12 must `git checkout feature/rea/w3-evidence-bound-narrative`
> (or the wave branch) before adding it.
>
> **Concurrent-edit caveat.** A parallel W13 wave (Arabic/RTL) is editing
> `servers/nextjs/lib/template-v2-json-to-html.ts` in the same checkout.
> Every line anchor in this document for that file
> (`template-v2-json-to-html.ts:159-160`, `:162-192`, `:194-221`) is a
> **`87b6bf9` anchor** and will drift once W13 lands. All other cited files
> were unmodified at analysis time.

---

## A. Current-state facts

### A.1 Files that must not drift

All of the following are byte-identical between `87b6bf9` and the checkout
used for analysis (verified with `git diff --quiet`):

| Path | Role |
|---|---|
| `servers/nextjs/lib/run-bundled-presentation-export.ts` | Node export launcher |
| `scripts/sync-presentation-export.cjs` | Runtime installer / `--check-only` |
| `scripts/run-presentation-export.mjs` | `runTask` bridge (becomes `runner.mjs`) |
| `servers/nextjs/lib/template-v2-json-to-html.ts` | Slide JSON → HTML renderer |
| `servers/fastapi/services/export_task_service.py` | Python import/export service |
| `servers/fastapi/templates/pptx_font_utils.py` | PPTX font utilities (see §A.6) |
| `config/fixture-policy.json` | Fixture policy |
| `scripts/check-fixtures.mjs` | Fixture policy enforcement |
| `servers/fastapi/templates/v2/models/elements.py` | `SlideElement` union |
| `servers/fastapi/templates/v2/models/layouts.py` | `RawSlideLayouts` model |

### A.2 The export runtime (Node side)

**`servers/nextjs/lib/run-bundled-presentation-export.ts`**

| Fact | Citation |
|---|---|
| Runtime root = `EXPORT_PACKAGE_ROOT` env, else `<cwd>/../../presentation-export` | `:12-17` |
| App root = `GOMREY_APP_ROOT`/`PRESENTON_APP_ROOT` env, else `<cwd>/../..` | `:19-24` |
| Entrypoint resolved as `<exportRoot>/runner.mjs`; `fs.access` throws if missing | `:39-43` |
| `bundledExportPackageAvailable()` = runner.mjs **and** `node_modules/@presenton/export-core/dist/index.js` both exist | `:45-56` |
| `BundledPresentationExportFormat = "pdf" \| "pptx"` | `:58` |
| `BundledPresentationExportResult = { path: string }` | `:60` |
| Output dir mode `0o755`, file mode `0o644` | `:62-63`, `:124-132` |
| Relative output paths require `APP_DATA_DIRECTORY`; `/app_data/…` is stripped | `:75-122` |
| **Public entry**: `runBundledPresentationExport({presentationId, title, format, cookieHeader?}) → {path}` | `:137-144` |
| Builds URL `${NEXT_PUBLIC_URL||"http://127.0.0.1"}/pdf-maker?id=…&format=…` (+`exportSession`, +`fastapiUrl`) | `:157-168` |
| Appends `#exportCookie=<urlencoded cookieHeader>` when a cookie is present | `:169-171` |
| Task file written to `mkdtemp(TEMP_DIRECTORY||tmpdir()/presenton, "export-")` | `:173-177` |
| Task payload = `{type:"export", url, format, title: sanitizeFilename(...), fastapiUrl?, cookieHeader?}` | `:179-186` |
| Spawns `process.execPath [runner.mjs, taskPath]`, `cwd=appRoot`, `env=process.env` | `:199-203` |
| Reads `<task>.response.json` → `{path?, url?}` → `normalizeExportOutputPath` | `:191`, `:251-257` |
| Returns `{path: outPath}`; work dir removed in `finally` | `:266-269` |
| Despite the name, there is **no lock** — `:143` delegates straight through | `:143` |

**Interface summary.** `runBundledPresentationExport` takes a *presentation id*,
not a deck. It is a **URL-driven** exporter: it does not accept deck JSON and
does not accept a template. The deck reaches the renderer through the HTTP
page `/pdf-maker`.

**`scripts/sync-presentation-export.cjs`**

| Fact | Citation |
|---|---|
| Target = `<repo>/presentation-export`; runner = `presentation-export/runner.mjs` | `:15-17` |
| Version manifest = `presentation-export/presenton-export-version.json` | `:26` |
| Download base = `https://github.com/presenton/presenton-export/releases/download` | `:29-30` |
| CLI flags: `--force`, `--check-only`, `--allow-version-override` | `:32-35` |
| Version pin read from root `package.json` → `presentationExportVersion` (= `"v1.0.34"`) | `:115-122`, `package.json:5` |
| `EXPORT_RUNTIME_VERSION` honored **only** with `--allow-version-override` | `:124-128` |
| Asset name = `presenton-export-core-opensource-<v>.tgz` | `:130-132` |
| `--check-only` re-validates: runner present, package present, manifest present, version match, manifest name match, sharp runtime valid | `:213-246`, `:300-304` |
| Sharp runtime = `sharp` + `@img/sharp-<platformArch>` (+ optional `@img/sharp-libvips-<platformArch>`) at the **exact same version** | `:58-108` |
| Platform arch: `linux-x64` (glibc) / `linuxmusl-x64` (musl) / `${platform}-${arch}` | `:37-48` |
| Install = copy `scripts/run-presentation-export.mjs` → `runner.mjs`, write a `package.json` pinning the tarball, `npm install --omit=dev --ignore-scripts --no-package-lock --no-fund --no-audit --cache <cache>/npm` | `:255-295` |
| `EXPORT_CORE_ARCHIVE` env → use a local tarball instead of downloading | `:314-320` |
| Exports `clearDirectoryContents`, `getRuntimePlatformArch`, `validateSharpRuntime` for unit testing | `:339-343` |

**`scripts/run-presentation-export.mjs`**

| Fact | Citation |
|---|---|
| `import { runTask } from "@presenton/export-core"` — the only runtime export | `:3` |
| `buildRunOptions`: `outputDirectory = APP_DATA_DIRECTORY/exports` for `export`/`html-to-any`, else `APP_DATA_DIRECTORY` | `:41-45` |
| `browserLaunchOptions.executablePath` from `PUPPETEER_EXECUTABLE_PATH`; `puppeteerCacheDirectory` from `PUPPETEER_CACHE_DIR` | `:36-37`, `:55-56` |
| `urlConfigs = [{url, match:"origin", cookies}]` when cookies exist | `:47-50` |
| `modifyWindow` injects `window.env = {NEXT_PUBLIC_FAST_API, ASSETS_BASE_URL}` | `:19-31` |
| Response normalisation: `files` → `{paths, file_paths}`; else `{path, file_path}` from `response.filePath` | `:64-80` |
| Writes `<task>.response.json` next to the task file | `:101-102` |

**Route wrapper.** `servers/nextjs/app/api/export-presentation/route.ts:92-162`:
requires auth (`:93-96`), body `{format, id, title}` (`:115`), rejects unless
`bundledExportPackageAvailable()` (`:133-137`), calls
`runBundledPresentationExport` (`:139-144`), moves the artifact to
`<APP_DATA_DIRECTORY>/exports/users/<userId>/` (`:53-90`, `:145-148`), and
returns `{success:true, path:"/api/export-presentation/file?name=…"}` (`:150-153`).

**Is the runtime present in a fresh checkout?** No.

- `presentation-export/` is gitignored — `.gitignore:31` (`presentation-export/`),
  confirmed by `git check-ignore -v presentation-export/` →
  `.gitignore:31:presentation-export/	presentation-export/`, and
  `git ls-files presentation-export` returns **nothing**.
- CI installs it explicitly: `.github/workflows/test-all.yml:34-38`
  (`npm run sync:presentation-export` then `npm run check:presentation-export`).
- Docker installs it at build time: `Dockerfile:67`
  (`node /app/scripts/sync-presentation-export.cjs --force`) and verifies it at
  `Dockerfile:136`.

**Zero-cost install.**

```sh
npm run sync:presentation-export     # == node scripts/sync-presentation-export.cjs
```

This is free and credential-free: the tarball is a **public GitHub Release
asset** (`scripts/sync-presentation-export.cjs:29-30`, `:310-323`), and the only
npm dependency pulled is `sharp` + its platform-native prebuilt
(`@img/sharp-<platformArch>`) from the public npm registry. `npm install` runs
with `--ignore-scripts`, so nothing is built locally. `EXPORT_CORE_ARCHIVE`
(`:314-320`) allows an offline/air-gapped install from a pre-fetched tarball.

**Runtime prerequisites (measured).**

| Requirement | Evidence |
|---|---|
| Node **≥ 22.12.0** | `presentation-export/node_modules/@presenton/export-core/package.json` → `engines: {"node":">=22.12.0"}` |
| Chromium **only** for browser-backed tasks (`export`, `html-to-any`, `*to-image*`) | export-core `README.md:47-49`; measured: `html-to-any` printed `[browser] Puppeteer browser is missing; downloading it` |
| **No** ImageMagick, no LibreOffice, no Office | Measured: `pptx-from-json` and `pptx-to-json` completed with only `node` + `sharp` present |
| `sharp` native binary for the platform | `scripts/sync-presentation-export.cjs:58-108` |

> **CI blocker (important).** Every job in `.github/workflows/test-all.yml`
> pins Node **20** (`:25`, `:91`, `:128`, `:157`, `:191`, `:244`, `:279`,
> `:304`), and `electron-linux-ubuntu22.yml:30` also pins 20. Docker uses
> `node:22-bookworm-slim` (`Dockerfile:33`, `:48`, `:111-112`). Installing the
> runtime under Node 20 works (the `engines` field is not enforced because
> `--ignore-scripts` and no `engine-strict`), but **running** export-core
> tasks under Node 20 is unsupported. W12's CI plan must add Node ≥ 22.12.

### A.3 The production export path is browser-driven

`servers/nextjs/app/(export)/pdf-maker/PdfMakerPage.tsx` is the page the
export runtime renders:

- `<div id="presentation-slides-wrapper" …>` — `:257-260`
- one `<div class="main-slide" … data-speaker-note={slide.speaker_note ?? ""}>` per slide — `:284-286`
- inner `<div class="slide-export-inner group font-syne" data-layout data-group>` — `:287-291`
- slides come from `DashboardApi.getPresentation` or
  `/api/export-presentation-data/<id>` with an `x-export-cookie` header — `:175-222`
- three render branches: `TemplateV2HtmlSlidePreview` (template-v2 HTML),
  `SmartHtmlPdfSlide` (`slide.html_content`), `SlideScale` (classic) — `:292-308`

Measured consequence: the export-core's HTML→PPTX extractor **requires** that
DOM. A bare slide HTML fails with `Presentation slides wrapper not found`;
wrapping it in `#presentation-slides-wrapper` + `.main-slide` succeeds.

### A.4 The external package's own contract

`presentation-export/node_modules/@presenton/export-core/README.md`:

- "The package exposes one task API" — `runTask` is the only runtime export (`:72-73`).
- Task table (`:219-230`): `export`, `html-to-any`, `pptx-from-json`,
  `pptx-to-html`, `pptx-to-json`, `html-to-image`, `html-to-images`,
  `json-to-html`, `json-to-image`, `json-to-images`.
- `RunTaskOptions` (`:78-89`): `outputDirectory`, `tempDirectory`,
  `cleanupTempDirectory`, `browserLaunchOptions`, `puppeteerCacheDirectory`,
  `getBrowser`, `urlConfigs`, `modifyWindow`.
- Open-source edition = low-quality only; `export`/`html-to-any` do not accept
  `quality` (`:19-21`).
- `pptx-from-json` input (`:56-61`):

  ```ts
  const task: ExportPptxFromJsonTask = {
    type: "pptx-from-json",
    data: { name: "Quarterly report", slides: [{ shapes: [] }] },
  };
  ```

- Response shapes (`:250-267`): `ExportFileResponse {type:"file", filePath, url, mimeType}`.

`dist/index.d.ts` (the type surface W12 will code against):

| Model | Lines | Shape |
|---|---|---|
| `PptxPresentationModel` | `:265-269` | `{name?, shapes?, slides: PptxSlideModel[]}` |
| `PptxSlideModel` | `:259-263` | `{background?: PptxFillModel, shapes: PptxShapeModel[], note?: string}` |
| `PptxPositionModel` | `:24-29` | `{left, top, width, height}` — **pixels**, 1280×720 canvas |
| `PptxFontModel` | `:31-41` | `{name, size, font_weight, italic, color, opacity?, underline?, underline_color?, strike?}` |
| `PptxFillModel` | `:43-46` | `{color, opacity}` |
| `PptxStrokeModel` | `:48-53` | `{color, thickness, opacity, dash?}` |
| `PptxShadowModel` | `:55-61` | `{radius, offset, color, opacity, angle}` |
| `PptxTextBoxModel` | `:102-113` | `{shape_type, margin?, fill?, stroke?, shadow?, position, rotation?, text_wrap, vertical_alignment?, paragraphs}` |
| `PptxAutoShapeBoxModel` | `:115-127` | `{shape_type, type?, …, text_wrap, border_radius?, paragraphs?}` |
| `PptxPictureModel` | `:93-98` | `{is_network, path, svg_fallback_path?, svg_color?}` |
| `PptxPictureBoxModel` | `:115-148` | `{shape_type, position, …, clip, picture, clip_path?}` |
| `PptxConnectorModel` | `:150-158` | `{shape_type, type?, position, rotation?, thickness, color, opacity}` |
| `PptxTableModel` | `:185-194` | `{shape_type, position, rotation?, rows, cols, row_heights?, col_widths?, cells}` |
| `PptxTableCellModel` | `:173-183` | `{row, col, row_span, col_span, margin?, fill?, borders?, vertical_alignment?, paragraphs}` |
| `PptxChartModel` | `:225-257` | chart type, categories, datasets, title, axes, legend… |
| `PptxParagraphModel` | `:75-85` | `{spacing?, alignment?, font?, line_height?, letter_spacing?, level?, bullet?, text?, text_runs?}` |
| `PptxParagraphBulletModel` | `:68-73` | `{type: "default"\|"number", color?, format?, char?}` |
| `PptxFromJsonTask` | `:289-294` | `{type:"pptx-from-json", data: PptxPresentationModel, …}` |
| `PptxToJsonTask` | `:303-308` | `{type:"pptx-to-json", pptx_path, title?, get_fonts?}` |
| `SlideElement` union | `:903-915` | `Text\|Container\|Image\|TextList\|Table\|Vector\|Chart\|Infographic\|Flex\|Grid\|Group` — doc comment: *"Discriminated union matching FastAPI's template-v2 SlideElement contract."* |
| `runTask` | `:1120` | `runTask<T extends ExportCoreTask>(task, options?): Promise<TaskResponse<T>>` |

### A.5 The deck JSON that goes in — two distinct vocabularies

This is the single most important structural fact for W12: **there are two
unrelated JSON dialects**, and only one of them can drive a browser-free export.

**Dialect 1 — Gomrey slide model (`RawSlideLayouts`).**
`servers/fastapi/templates/v2/models/layouts.py:45-52`:

```python
class RawSlideLayout(BaseModel):
    id: str
    description: str
    elements: list[SlideElement]

class RawSlideLayouts(BaseModel):
    layouts: list[RawSlideLayout]
```

`SlideElement` is defined in
`servers/fastapi/templates/v2/models/elements.py` — `Text` `:217-236`,
`Image` `:255-278`, `TextList` `:281-301`, `Table` `:319-…`, `Vector` `:360-…`,
`Chart` `:380-…`, `Container` `:239-252`. Positions are **pixels**
(`Position` `:104-107`, `Size` `:109-112`); text is `runs: list[TextRunValue]`
(`TextRun` `:195-204`, `LatexTextRun` `:207-211`).

This is the dialect the **importer** produces and the **renderer** consumes:

- `servers/nextjs/lib/template-v2-json-to-html.ts:162-192` —
  `templateV2UiToHtml(ui, options)` / `templateV2UiToHtmlFragment(ui, options)`
  accept `{elements, components, background, fonts}` (`:194-221`) and emit HTML
  at 1280×720 (`:159-160`).
- `servers/fastapi/api/v1/ppt/endpoints/template.py:955-959` —
  `pptx_json = await EXPORT_TASK_SERVICE.convert_pptx_to_json(pptx_path)` then
  `RawSlideLayouts.model_validate(pptx_json.model_dump(mode="json"))`.

**Dialect 2 — export-core PPTX model (`PptxPresentationModel`).**
The `pptx-from-json` input. This is *not* the Gomrey slide model and is not
produced anywhere in the Gomrey codebase.

**Consequence.** A slide-model deck cannot be fed to `pptx-from-json`. The
bridge is `json-to-html` → `html-to-any` — and `html-to-any` is a **browser**
task. So:

- The **production** export path is browser-only and non-deterministic (§C).
- The **deterministic** path is `pptx-from-json` → `pptx-to-json`, which
  exercises the same PPTX writer and the same PPTX reader that the production
  path uses, but with a synthetic dialect-2 deck.

W12 must therefore ship **both**: a deterministic dialect-2 harness (CI), and
an opt-in dialect-1 browser harness (local / dedicated job).

### A.6 The Python import path

**`servers/fastapi/services/export_task_service.py`**

| Fact | Citation |
|---|---|
| `class PptxToHtmlDocument(BaseModel): slides, font_css, width, height, images_dir, fonts_dir` | `:93-95` |
| `class PptxToJsonDocument(BaseModel): layouts: list[dict[str, Any]]` | `:102-103` |
| `class PresentationExportTaskResult(BaseModel): path: str` | `:106-107` |
| `ExportTaskService.__init__(timeout_seconds=300)`; `node_binary` from `LITEPARSE_NODE_BINARY` (default `"node"`) | `:122-127` |
| `_resolve_export_dir()` — `EXPORT_PACKAGE_ROOT` env, else 4 candidate paths probed for `runner.mjs` | `:129-149` |
| `_build_node_env()` — **requires** `APP_DATA_DIRECTORY`; sets `TEMP_DIRECTORY`, `PUPPETEER_TMP_DIR`, `PUPPETEER_CACHE_DIR`, `ASSETS_BASE_URL="/app_data"`; refuses to download a browser in Electron mode | `:154-206` |
| `_ensure_runtime_ready()` — requires `runner.mjs` **and** `node_modules/@presenton/export-core/dist/index.js` | `:208-227` |
| `_create_task_paths()` — `mkdtemp(prefix="export-task-")` under `TEMP_DIRECTORY` (+ owner id) | `:285-297` |
| `_run_task_locked` — writes task json, spawns `node runner.mjs <task>`, `cwd=export_dir`, reads `<task>.response.json`; HTTP 500 with returncode/stderr/stdout on failure | `:302-357` |
| `_run_bounded_child` — asyncio subprocess with bounded stdout/stderr tails | `:359-423` |
| **`async def convert_pptx_to_json(self, pptx_path: str) -> PptxToJsonDocument`** | **`:690-729`** |
| ↳ 400 if the file is missing | `:691-692` |
| ↳ task payload = `{"type":"pptx-to-json","pptx_path": pptx_path}` | `:694-697` |
| ↳ reads the produced JSON file | `:705-707` |
| ↳ `_absolutize_conversion_asset_urls` + `_scope_conversion_artifacts` | `:708-717` |
| ↳ **`return PptxToJsonDocument(**output_data)`** | `:719` |
| ↳ 500 on `JSONDecodeError` / `ValidationError` | `:720-729` |
| `async def convert_pptx_to_html(self, pptx_path, get_fonts=False) -> PptxToHtmlDocument` | `:460-522` |
| `async def export_from_url(url, title, export_as, fastapi_url=None, cookie_header=None)` | `:425-458` |
| `_absolutize_conversion_asset_urls` — rewrites `images/…`, `fonts/…` → `/app_data/pptx-to-json/<session>/…` | `:731-773` |
| `_move_export_to_owner` — relocates into the owner exports dir | `:775-807` |

> **Model narrowing (silent loss).** `PptxToJsonDocument` declares **only**
> `layouts` (`:102-103`). The raw converter file also contains `font_css`,
> `fonts`, `fonts_dir`, `images_dir` (measured — see §B.2). `Pydantic` drops
> them at `:719` because they are not declared fields. A harness that asserts
> on `PptxToJsonDocument` will never see the font manifest. This is a
> **documented, asserted drop**, not a bug in the harness.

**Callers of `convert_pptx_to_json` (only two):**

- `servers/fastapi/api/v1/ppt/endpoints/template.py:955` → `:957-959`
  `RawSlideLayouts.model_validate(pptx_json.model_dump(mode="json"))`,
  HTTP 500 `"PPTX-to-JSON export produced invalid slide layout JSON"` on
  `ValidationError` (`:960-970`).
- `servers/fastapi/templates/fonts_and_slides_preview.py:779`
  (`await EXPORT_TASK_SERVICE.convert_pptx_to_json(modified_pptx_path)`) then
  `:814` `await EXPORT_TASK_SERVICE.render_jsons_to_images(...)`. **This is
  the closest thing to a round trip in the product** (PPTX → JSON → PNGs) and
  it is not covered by any test.

**`servers/fastapi/templates/pptx_font_utils.py` is NOT on the import path.**
It is a standalone PPTX *font* utility (extract fonts from OOXML, build alias
configs, rewrite the PPTX). It is not called by `convert_pptx_to_json`. Public
surface, for reference only:

`FontDetail` `:39-73`; `normalize_font_family_name` `:130`;
`get_static_font_catalog` `:162`; `get_static_font_url` `:176`;
`build_google_fonts_stylesheet_url` `:183`; `extract_fonts_from_oxml` `:246`;
`extract_raw_fonts_and_embedded_details` `:271`; `normalize_font_variants` `:310`;
`extract_used_font_variants_from_pptx` `:365`;
`extract_used_fonts_from_pptx` `:807`; `create_font_alias_config` `:887`;
`replace_fonts_in_pptx` `:1068`; `extract_font_from_eot` `:1134`;
`get_font_details` `:1167`; `convert_eot_to_ttf` `:1294`.

W12 should **not** try to fold font substitution into the fidelity loop: it
mutates the PPTX before import, which would confound "what survived export"
with "what the font aliaser changed". If W12 later wants to cover it, it
belongs in a separate, opt-in test.

### A.7 Existing round-trip evidence

**There is none.** Searches for `round.trip|roundtrip|round_trip` outside
`.venv`/`node_modules` return only unrelated unit tests:

- `servers/fastapi/tests/unit/test_latex_text.py:42`
- `servers/fastapi/tests/unit/test_dict_utils.py:102`
- `servers/fastapi/tests/test_gomrey_decisions.py:124`
- `servers/fastapi/tests/test_gomrey_claims.py:162`
- `servers/fastapi/tests/test_gomrey_seams.py:11`
- `servers/fastapi/tests/test_gomrey_accounting.py:56`

`pptx-to-json` is exercised **only through mocks**:

- `servers/fastapi/tests/unit/test_template_api.py:356-357`, `:438-439`,
  `:485-486`, `:523-524`, `:815-816`, `:874-875` — all patch
  `"api.v1.ppt.endpoints.template.EXPORT_TASK_SERVICE.convert_pptx_to_json"`
  with `AsyncMock(return_value=PptxToJsonDocument(**RAW_LAYOUTS))`.
- `servers/fastapi/tests/unit/test_runtime_limits.py:131-164` —
  `test_convert_pptx_to_html_resolves_relative_asset_directories` runs a **real**
  subprocess against a hand-built PPTX.
- `servers/fastapi/tests/test_pptx_font_utils.py:1031`, `:1092`, `:1136` —
  a stub service with a fake `convert_pptx_to_json`.

**No test exports a deck and re-imports it. W12 is greenfield.**

### A.8 Test conventions

**(a) FastAPI / pytest**

| Convention | Citation |
|---|---|
| `[tool.pytest.ini_options] testpaths = ["tests"]` | `servers/fastapi/pyproject.toml:66-67` |
| Python `>=3.11,<3.12`; dev deps `pytest>=9.0.3`, `pytest-cov>=7.1.0` (no `pytest-asyncio`) | `pyproject.toml:11`, `:60-64` |
| Async is driven with `asyncio.run(...)` (not `@pytest.mark.asyncio`) | `tests/unit/test_runtime_limits.py:44`, `:164` |
| Fixtures: `fake_async_session` (`:54-56`), `snapshots_dir` → `tests/regression/snapshots` (`:59-61`), `load_snapshot` (`:64-70`) | `tests/conftest.py` |
| `tmp_path` builtin for file artifacts | `tests/unit/test_runtime_limits.py:41`, `:62`, `:92`, `:131` |
| In-memory PPTX zips are built with `zipfile` | `tests/test_pptx_font_utils.py:55-100` |
| Runnable via `uv run --locked python -m pytest --verbose --tb=short` | `.github/workflows/test-all.yml:75` |

**(b) Next.js / `node:test`**

| Convention | Citation |
|---|---|
| `"test": "node --test"`, `"lint": "eslint ."` | `servers/nextjs/package.json` |
| `import assert from "node:assert/strict"; import test from "node:test";` | `servers/nextjs/tests/template-v2-json-to-html-metadata.test.mjs:1-4` |
| TypeScript modules are bundled with **esbuild** in `test.before`, then dynamically imported with a cache-busting query | `…metadata.test.mjs:11-33`, `vector-arrow-rendering.test.mjs:14-48` |
| CWD-relative entrypoints: `path.resolve("lib/template-v2-json-to-html.ts")` → **tests must run from `servers/nextjs`** | `…metadata.test.mjs:13` |
| `mkdtemp(path.join(tmpdir(), "presenton-…-"))` in `test.before`; `rm(…, {recursive:true, force:true})` in `test.after` | `…metadata.test.mjs:13-34` |

**(c) Tests that assert on file artifacts**

- `servers/fastapi/tests/unit/test_runtime_limits.py:131-164` — the only
  existing test that drives the real export runtime and asserts on produced
  files. Closest precedent for W12's Python side.
- `servers/nextjs/tests/pdf-maker-export-layout.test.mjs:10-19` — asserts on
  *source text* via regex, not artifacts.
- `scripts/check-fixtures.test.mjs` — calls the exported `checkFixtures()`.

**(d) Fixture policy — where a fixture must live, and what it must carry**

`config/fixture-policy.json` (34 lines) — requirements **verbatim**:

- `:3` policy — *"Committed fixtures must be synthetic, public, or explicitly
  licensed. No real user secrets, private health or business data, donor
  credentials, or production dumps. Every fixture carries provenance and
  regeneration instructions."*
- `:4-8` `allowed_kinds` — `synthetic-generated`,
  `public-benchmark-redistributable`, `explicitly-licensed-with-attribution`
- `:9-16` `prohibited` — real user secrets or tokens / private health data /
  private business data / donor credentials / production database dumps /
  unlicensed scraped personal data
- `:18` `provenance_header` — *"Each fixture directory must document source,
  license, creation date, and generator or acquisition method."*
- `:19` `regeneration` — *"Generated fixtures must record the exact generator
  script and seed so they can be reproduced."*
- `:20` `no_secrets` — *"Fixtures must pass scripts/scan-secrets.mjs and must
  not contain credential-like material."*
- `:21` `size_budget` — *"Fixtures stay small and bounded; large corpora live
  outside the repository and are referenced, not committed."*
- `:23-33` `scan` — script `scripts/check-fixtures.mjs`; roots
  `["servers/fastapi/tests","servers/nextjs/tests","scripts","sbom"]`;
  `exclude_prefixes` `["docs/donors/","docs/evidence/"]`;
  `allowlisted_paths` `["scripts/scan-secrets.test.mjs"]`

**What `scripts/check-fixtures.mjs` actually enforces** (it is *not* the whole
policy):

- `:20-24` the policy file must define `allowed_kinds`, `prohibited`,
  `requirements`
- `:7` denied **filenames**: `/\.pem$/`, `/\.key$/`, `/id_rsa/`,
  `/credentials\.json$/`, `/production.*dump/i`, `/\.dump$/`
- `:8-12` denied **content**: `/\bAKIA[0-9A-Z]{16}\b/`,
  `/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/`,
  `/\bgh[pousr]_[A-Za-z0-9]{36,}\b/`
- `:49` files > 1 MiB are skipped entirely
- `:57` lines containing `EXAMPLE` or `placeholder` are skipped
- `:68-70` only the four `scan.roots` are walked

⇒ The `provenance_header`, `regeneration` and `size_budget` requirements are
**policy, not machine-enforced**. W12 must satisfy them by convention: a
`PROVENANCE.md` in the fixture directory + a committed generator script + a
recorded seed.

`scripts/scan-secrets.mjs` additionally denies `aws_secret_access_key=…` (`:12`),
`sk-[A-Za-z0-9]{20,}` (`:14`) and `password|passwd|secret = "…"` (`:15`); it
scans **only `git ls-files`** (`:78`) — i.e. tracked files only — and skips
binary image extensions (`:57`). A committed PNG fixture is therefore not
scanned, but a committed `.json` fixture **is**.

**Recommended fixture home:** `servers/nextjs/tests/fixtures/export-fidelity/`
— it is inside a `scan.roots` entry (so `check-fixtures.mjs` and
`scan-secrets.mjs` cover it), it is the side that already owns the export
runtime, and it keeps binary artifacts out of the Python tree.

---

## B. The round trip, step by step

### B.1 Tier A — deterministic (browser-free), the CI tier

```
deck.json (dialect 2, PptxPresentationModel)
   │  runTask({type:"pptx-from-json", data: deck})
   ▼
<name>_<uuid>.pptx                      ← bytes NOT reproducible
   │  runTask({type:"pptx-to-json", pptx_path})
   ▼
presentation.json  {font_css, fonts, fonts_dir, images_dir, layouts:[…]}
```

Measured timings on this machine: `pptx-from-json` **59 ms**, `pptx-to-json`
**15 ms**. No Chromium, no ImageMagick, no LibreOffice.

`layouts[]` entries are exactly Gomrey's `RawSlideLayout`:
`{id: "slide_<n>", description: "Full slide layout converted from PPTX slide <n>.",
elements: [SlideElement]}`.

### B.2 Tier A output shape (measured, fixture 03)

```json
{
  "font_css": "",
  "fonts": [],
  "fonts_dir": "fonts",
  "images_dir": "images",
  "layouts": [
    { "id": "slide_1",
      "description": "Full slide layout converted from PPTX slide 1.",
      "elements": [ { "type": "table", "position": {…}, "size": {…},
                      "columns": [ {…}, {…} ], "rows": [ [ {…}, {…} ], [ {…}, {…} ] ],
                      "decorative": true, "name": "Table 1024",
                      "min_columns": 2, "max_columns": 2,
                      "min_rows": 3, "max_rows": 3 } ] }
  ]
}
```

`fonts` is the sorted, de-duplicated set of font families used. `fonts_dir` is
empty unless `get_fonts` is requested. `font_css` is always `""`.

### B.3 Tier B — production path (browser), the opt-in tier

```
Gomrey slide JSON (dialect 1, RawSlideLayouts)
   │  templateV2UiToHtml(ui)              ← pure TS, deterministic, 3 ms
   ▼
HTML  (Gomrey's own renderer)
   │  runTask({type:"html-to-any", html, format:"pptx"|"pdf"})
   │    ← requires the #presentation-slides-wrapper / .main-slide DOM
   ▼
.pptx / .pdf
   │  runTask({type:"pptx-to-json", pptx_path})
   ▼
presentation.json
```

Measured: `html-to-any` pptx = **5.2 s** (and it downloaded Chromium on first
use: `[browser] Puppeteer browser is missing; downloading it`);
`html-to-any` pdf = **4.6 s**; `json-to-html` = **3 ms** and
**byte-identical across runs**.

**Tier B is not reproducible.** Two runs of the same HTML produced two
different re-imported JSONs. The reason is structural: the browser path
*measures* the DOM. A declared text box of `{width: 600, height: 80}` came
back as `{width: 602, height: 44}` — the measured glyph box, not the declared
box. Tier A returns the declared values exactly (`123.5`, `45.25`, `640.5`,
`90.75` all round-tripped bit-for-bit).

### B.4 Preserved vs dropped — measured, per construct

Measured on export-core v1.0.34, Tier A.

| Construct | Preserved | Dropped / altered (measured) |
|---|---|---|
| **Text content** | run text verbatim (`"RunA "`, `"RunB"`) | — |
| **Text font** | `family`, `size`, `color`, `bold` (weight≥600→true), `italic`, `underline`, `letter_spacing` | `opacity` not surfaced; `font_weight` becomes a boolean `bold` |
| **Text geometry** | `position.x/y`, `size.width/height` **exactly** (px) | `rotation` dropped |
| **Paragraph structure** | — | N paragraphs collapse into **one** text element with one run per paragraph, joined by `"\n"` |
| **Paragraph `alignment`** | — | always `{horizontal:"left", vertical:"top"}` — `center` is lost |
| **`vertical_alignment`** | — | `"middle"` → `"top"` |
| **`line_height`** | — | `1.2` → `0.04` (a different unit) |
| **`level`** (outline level) | — | dropped |
| **`bullet`** | — | inlined as literal text: `{type:"number",char:"1."}` → `"1. Numbered item"`; `{type:"default"}` → `"• Bulleted item"` |
| **Text box fill** | colour + opacity, but as a **separate sibling `vector` polygon**, not on the text element | text element has no `fill` |
| **Autoshape geometry** | — | `type` is **ignored**: `"ellipse"` comes back as a **rectangle** polygon with no `shape` key |
| **Autoshape fill** | `color`, `opacity` | — |
| **Autoshape stroke** | `color`, `width` (from `thickness`) | `opacity` dropped; `dash` dropped |
| **Shadow** | `color`, `opacity`, `blur` (from `radius`) | `offset`+`angle` → `offset_x`/`offset_y` (angle 45 → 1.41/1.41) |
| **Autoshape text** | — | becomes a **separate sibling `text` element**; the shape and its text no longer co-locate in one object |
| **Table** | cell text, header-row cell fill, `alignment` | header row → `columns`; body rows → `rows`; `row_span`/`col_span` dropped; `borders` dropped; `row_heights`/`col_widths` dropped; `min_rows`/`max_rows` count the header |
| **Chart** | `chart_type`, `title`, `colors`, `categories`, `series[{name,values}]`, `legend`, `legend_position`, `x_axis`/`y_axis` flags, `x_axis_grid`/`y_axis_grid`, `axis_color` | `x_axis_title`/`y_axis_title` dropped; `axis_color` falls back to the default `"#475569"` when unset; `point_colors`/`data_label_*` dropped |
| **Image** | embedded at `ppt/media/Presenton_Native_Image_1.png`; re-import `data: "images/Presenton_Native_Image_1-<hash>.png"`, `fit:"fill"`, `is_icon:false`, `position`, `size` | `svg_fallback_path`, `svg_color`, `border_radius`, `clip_path`, `opacity`, `invert`, `brightness` dropped |
| **Connector** | `stroke.color`, `stroke.width`, `points`, `closed:false` | `rotation` dropped; the `type` is not surfaced |
| **Background** | synthesised as a full-slide `vector` polygon `{0,0}-{1280,720}` with the fill colour | only present when the deck sets `background` |
| **Speaker notes** | written to `ppt/notesSlides/notesSlide1.xml` as `<a:t>…</a:t>` | **not re-imported** — no `notes` key exists anywhere in the output JSON |
| **Element `name`** | — | auto-generated and *positional*: `"Shape 2"`, `"Shape 3"`, `"Shape 5"`, `"Presenton Shadow Shape 1"`, `"Table 1024"`, `"Chart 2048"`, `"Connector 2"`, `"Presenton Native Image 1"`. Brittle; treat as **soft**. |
| **`decorative`** | — | always `true`, regardless of input |
| **`min_length`/`max_length`** | recomputed from the text | input values ignored |
| **`font_css`** | — | always `""` |
| **`fonts`** | sorted set of families used | — |
| **`fonts_dir`** | retained directory path | empty (no `get_fonts`) |
| **Slide count** | preserved | — |

### B.5 The `shape_type` discriminator (undocumented, discovered empirically)

`PptxShapeModel` is typed as an empty interface (`dist/index.d.ts:100`) and
every subclass types `shape_type` as a bare `string` (`:106`, `:116`, `:131`,
`:151`, `:186`, `:226`). The accepted values are therefore **not** in the type
surface. Measured:

| `shape_type` | Behaviour |
|---|---|
| `textbox` | ✅ text element |
| `autoshape` | ✅ vector + text |
| `connector` | ✅ vector |
| `table` | ✅ table (needs `cells`) |
| `chart` | ✅ chart (needs `datasets`) |
| `picture` | ✅ image (needs `picture.path`) |
| `textBox`, `text`, `autoShape`, `shape`, `rect`, `pictureBox`, `image`, `group`, `textlist`, `text_box`, `TEXT_BOX`, `autoshapeBox`, `box` | ⚠️ **silently produce nothing** — no error, no element, no media part |

Error shapes worth guarding against:
`shape_type:"table"` with no `cells` → `cells is not iterable`;
`shape_type:"chart"` with no `datasets` → `Cannot read properties of undefined
(reading 'filter')`.

Image source handling (`shape_type:"picture"`): `picture.path` accepts an
**absolute local path**, a **`data:` URI**, a **`file://` URI**, or an HTTP(S)
URL; `is_network` was observed to be **ignored** for local sources (all five
variants produced identical `ppt/media/Presenton_Native_Image_1.png` and an
identical re-imported `data` path). For CI, use a **data URI** so no binary
file is needed.

### B.6 Tier A vs the FastAPI service boundary

`ExportTaskService.convert_pptx_to_json` (`:690-729`) adds two things the
raw task does not:

1. `_absolutize_conversion_asset_urls` (`:731-773`) rewrites `images/…` and
   `fonts/…` into `/app_data/pptx-to-json/<session>/…` — **but only** when the
   artifact directory's parent is exactly `<APP_DATA_DIRECTORY>/pptx-to-json`
   (`:747-749`). Otherwise the relative paths pass through unchanged.
2. `PptxToJsonDocument(**output_data)` (`:719`) narrows the payload to
   `layouts` only — `font_css`, `fonts`, `fonts_dir`, `images_dir` are **not**
   declared fields and are dropped by Pydantic.

Therefore the Python-side harness must assert on `document.layouts` (and can
additionally assert that `fonts` is *not* exposed, which is itself a
documented fidelity fact about the service boundary).

---

## C. What the harness may assert deterministically

### C.1 Deterministic — safe to assert on CI

| # | Assertion | Why it is safe | Evidence |
|---|---|---|---|
| 1 | The re-imported JSON **content** of a fixed input PPTX | `pptx-to-json` is byte-identical across runs for a fixed PPTX | measured: `sha256(json1) === sha256(json2)` → `true` |
| 2 | `json-to-html` output string is byte-identical across runs | pure function, no browser | measured: `sha256` equal, 3 ms |
| 3 | Element `type` sequence per slide | derived from the PPTX structure | measured for all 8 fixtures |
| 4 | Text run content, per-run font family/size/colour/bold/italic/underline/letter_spacing | 1:1 through the OOXML run properties | measured, fixture 01 |
| 5 | Element `position` / `size` in px, exactly | position/size map 1:1 to EMU | measured: `123.5 / 45.25 / 640.5 / 90.75` exact |
| 6 | Fill colour + opacity, stroke colour + width | 1:1 through `spPr` | measured, fixture 04 |
| 7 | Chart type, categories, series names/values, title, legend flag/position | 1:1 through `chart1.xml` | measured, fixture 05 |
| 8 | Table cell text; header row → `columns`, body rows → `rows` | 1:1 through `a:tbl` | measured, fixture 03 |
| 9 | The PPTX **package part list** (`ppt/media/…`, `ppt/charts/chart1.xml`, `ppt/notesSlides/notesSlide1.xml`, `ppt/embeddings/*.xlsx`) | ZIP entry names are stable | measured with `unzip -l` |
| 10 | Speaker-note **text is present in the PPTX XML** | notesSlide is written | measured: `<a:t>W12_SPEAKER_NOTE_MARKER</a:t>` |
| 11 | Speaker-note text is **absent from the re-imported JSON** | documented drop | measured: `NOTE-PRESENT: false` |
| 12 | The re-imported JSON validates as Gomrey's `RawSlideLayouts` | the converter and the model are the same contract | `template.py:957-959` |

### C.2 Non-deterministic — must NOT be asserted on CI

| Thing | Why not | Evidence |
|---|---|---|
| **PPTX bytes** | the output filename embeds a UUID and the generated ZIP entries carry wall-clock timestamps (`ppt/slides/slide1.xml` at `10-22-2026 05:00` vs static parts at `11-30-2107 00:00`) | measured: two `pptx-from-json` runs of the same deck → different sha256 |
| **PDF bytes** | same class of nondeterminism | measured: two `html-to-any` pdf runs → same size (11783) but different bytes |
| **Tier B re-imported JSON** | the browser path measures the DOM; declared `{600×80}` came back as `{602×44}` | measured: `TIER B reimport deterministic: false` |
| **Any pixel/visual comparison** | requires a renderer, a font stack, and a display profile; CI has none | — |
| **Export-core's own `eval:*` suites** | they live in the vendored tarball (`README.md:288-298`) and are not shipped (`package.json` `files: ["dist","README.md"]`) | `package.json:17-20` |

### C.3 CI feasibility — the concrete plan

1. **Node version.** export-core requires `node >=22.12.0`
   (`package.json` → `engines`). All CI jobs pin Node 20
   (`test-all.yml:25,91,128,157,191,244,279,304`). A W12 CI job must use
   Node 22 (or the `test-nextjs` job must be bumped).
2. **Runtime install.** `npm run sync:presentation-export` +
   `npm run check:presentation-export` — already done in the
   `test-repository-tools` job (`test-all.yml:34-38`), **not** in
   `test-nextjs` (`:77-111`) or `test-fastapi` (`:40-75`). One added step is
   required in whichever job runs the harness.
3. **Network egress.** `sync:presentation-export` downloads a GitHub Release
   asset (`:310-323`). `EXPORT_CORE_ARCHIVE` (`:314-320`) allows an offline
   install from a pre-fetched tarball if egress is blocked.
4. **Chromium.** Only the Tier B harness needs it. Puppeteer downloads on
   demand (export-core `README.md:47-49`) — a ~150 MB network fetch inside
   the test. Tier A needs **no** browser, so **Tier A is the CI tier**.
5. **Failure mode.** If `presentation-export/` is absent, the harness must
   **skip with an explicit message**, not fail — mirroring
   `bundledExportPackageAvailable()` (`:45-56`) rather than inventing a
   second availability check.

---

## D. The synthetic deck fixtures

**Home.** `servers/nextjs/tests/fixtures/export-fidelity/`

```
servers/nextjs/tests/fixtures/export-fidelity/
├── PROVENANCE.md                 # policy: source, license, creation date, generator
├── README.md                     # what each fixture covers + expected drops
├── generator.mjs                 # the single generator script (policy: regeneration)
├── expectations/
│   └── v1.json                   # the machine-readable expectation file (§E)
└── decks/
    ├── 01-text-runs-fonts.json
    ├── 02-alignment-bullets.json
    ├── 03-table.json
    ├── 04-vectors.json
    ├── 05-chart.json
    ├── 06-image-media.json
    ├── 07-speaker-notes.json
    └── 08-adversarial.json
```

Every deck is **`synthetic-generated`** (`config/fixture-policy.json:4-8`).
`generator.mjs` writes the eight deck files from a single in-file spec with a
fixed seed, so `regeneration` (`:19`) is satisfied by construction. `PROVENANCE.md`
satisfies `provenance_header` (`:18`). Total committed size is well under the
1 MiB skip threshold in `scripts/check-fixtures.mjs:49`; the image fixture uses
a **data URI**, so **no binary file is committed** (which also keeps
`scripts/scan-secrets.mjs` out of the picture, since it skips image extensions
at `:57`).

### D.1 Coverage matrix

| # | Fixture | Covers | Deliberately exercises |
|---|---|---|---|
| 01 | `text-runs-fonts` | text runs + font family/size/colour/bold/italic/underline/letter_spacing; background | the **preserve** path |
| 02 | `alignment-bullets` | paragraph alignment, vertical alignment, bullet (number + default), outline `level`, `line_height` | four documented **drops** in one element |
| 03 | `table` | 3×2 table, header fill, cell text, spans | header→`columns` split, span/border drops |
| 04 | `vectors` | autoshape (ellipse), stroke, shadow, in-shape text, connector | **geometry flattening** (ellipse→rectangle) |
| 05 | `chart` | bar chart, 2 series, categories, title, legend, axis titles | axis-title drop, `axis_color` default |
| 06 | `image-media` | picture from a `data:` URI | media part + retained-asset path |
| 07 | `speaker-notes` | slide-level `note` | notes **written but not re-imported** |
| 08 | `adversarial` | 2000-char run in a 40×20 box, missing font family, zero-size shape, RTL + emoji text, empty slide | robustness: must not throw, must not hang |

### D.2 The exact JSON for the simplest one

`servers/nextjs/tests/fixtures/export-fidelity/decks/01-text-runs-fonts.json`
— **verified to round-trip** (see §B.4):

```json
{
  "name": "W12 01 text runs and fonts",
  "slides": [
    {
      "background": { "color": "#FFFFFF", "opacity": 1 },
      "shapes": [
        {
          "shape_type": "textbox",
          "position": { "left": 100, "top": 100, "width": 800, "height": 120 },
          "text_wrap": true,
          "paragraphs": [
            {
              "text_runs": [
                {
                  "text": "RunA ",
                  "font": {
                    "name": "Arial",
                    "size": 18,
                    "font_weight": 400,
                    "italic": false,
                    "color": "#0000FF"
                  }
                },
                {
                  "text": "RunB",
                  "font": {
                    "name": "Georgia",
                    "size": 22,
                    "font_weight": 700,
                    "italic": true,
                    "color": "#00AA00",
                    "underline": true
                  }
                }
              ],
              "alignment": "left",
              "letter_spacing": 2
            }
          ]
        }
      ]
    }
  ]
}
```

Measured re-import for this deck:

- `fonts` → `["Arial","Georgia"]`
- `layouts[0].elements` → `["vector","text"]` (the first `vector` is the
  synthesised background)
- the `text` element carries `position {x:100,y:100}`, `size {width:800,height:120}`,
  `font {size:18,family:"Arial",color:"#0000FF",bold:false,italic:false,letter_spacing:2}`,
  and two runs — `RunA ` (Arial 18 `#0000FF`) and `RunB` (Georgia 22 `#00AA00`
  `bold:true italic:true underline:true`)
- `min_length: 4`, `max_length: 9` (recomputed)

### D.3 Notes on the other seven decks

- **02** — three paragraphs in one text box. Measured result: **one** `text`
  element, **one** run, text
  `"Centred paragraph\n1. Numbered item\n• Bulleted item"`. Assert exactly
  that string, and assert that `alignment.horizontal === "left"` and
  `alignment.vertical === "top"`.
- **03** — measured result: `columns` = the two header cells (each with
  `color: {color:"#DDDDDD"}`), `rows` = two body rows,
  `min_columns/max_columns = 2`, `min_rows/max_rows = 3`.
- **04** — measured result: `["vector","text","vector"]`. The first `vector` is
  the **rectangle** that replaced the ellipse (points `100,100 → 300,220`,
  `fill {color:"#123456", opacity:0.8}`, `stroke {color:"#654321", width:3}`,
  `shadow {offset_x:1.41, offset_y:1.41, blur:4, color:"#000000", opacity:0.25}`).
  The `text` element carries `"Inside shape"` in `Calibri` (the default —
  the shape's paragraphs carried no font). The second `vector` is the
  connector: `points [{100,400},{400,400}]`, `closed:false`,
  `stroke {color:"#FF00FF", width:2}`.
- **05** — measured result: `chart_type:"bar"`, `title:"Quarterly Throughput"`,
  `colors:["#FF0000","#0000FF"]`, `categories:["Alpha","Beta","Gamma"]`,
  `series:[{name:"Series One",values:[10,20,30]},{name:"Series Two",values:[5,15,25]}]`,
  `legend:true`, `legend_position:"bottom"`, `x_axis:true`, `y_axis:true`,
  `x_axis_grid:false`, `y_axis_grid:false`, `axis_color:"#475569"`.
  **No** `x_axis_title`/`y_axis_title` keys. The PPTX also contains
  `ppt/charts/chart1.xml` **and** `ppt/embeddings/Microsoft_Excel_Chart1.xlsx`.
- **06** — measured result: one `image` element,
  `data:"images/Presenton_Native_Image_1-b2bbe763c7e1.png"`, `fit:"fill"`,
  `is_icon:false`, `position {100,100}`, `size {128,128}`. The PPTX contains
  `ppt/media/Presenton_Native_Image_1.png` (70 bytes). The `data` path
  contains a **content hash** (`-b2bbe763c7e1`) — assert with a **regex**
  (`^images/Presenton_Native_Image_1-[0-9a-f]{12}\.png$`), not a literal.
- **07** — the deck sets `note: "W12_SPEAKER_NOTE_MARKER"`. The PPTX contains
  `ppt/notesSlides/notesSlide1.xml` containing that string. The re-imported
  JSON contains **no** trace of it. Assert both facts.
- **08** — measured result: `fonts: ["Calibri","NoSuchFontXYZ"]` (the missing
  family is preserved **by name**), `layouts` has 2 entries, the second with
  `elements: []`. The overflowing run survives verbatim (2000 chars) with
  `family:"NoSuchFontXYZ"`, `size:96`. The zero-size autoshape becomes a
  degenerate 4-point polygon all at `(0,0)`. The RTL+emoji string
  `"مرحبا עולם 🎉"` survives byte-for-byte. Nothing throws.

---

## E. The expectation model

### E.1 Design principles

1. **Every observable is declared.** The expectation file enumerates what the
   harness checks. An assertion that is not in the file is not run; an
   observable that changes and is not in the file is not a failure. This makes
   the harness's coverage auditable.
2. **Every expectation is classified** as `preserved`, `transformed`, or
   `dropped`. Only a broken `preserved` expectation is a **failure**. A
   `transformed`/`dropped` expectation that changes is a **change report**,
   not a red build — because export-core's fidelity is a moving target and a
   *documented* drop is knowledge, not a defect.
3. **Expectations are versioned independently of the code.** A version bump of
   the export runtime requires an explicit, reviewed expectations bump.
4. **Nothing unstable is asserted.** Element `name` values are positional and
   brittle (§B.4); asset filenames contain a content hash; PPTX bytes contain
   UUIDs and timestamps.

### E.2 File format (proposed)

`servers/nextjs/tests/fixtures/export-fidelity/expectations/v1.json`

```json
{
  "schema_version": 1,
  "export_core_version": "1.0.34",
  "fixtures": [
    {
      "id": "01-text-runs-fonts",
      "deck": "decks/01-text-runs-fonts.json",
      "class": "preserved",
      "expectations": [
        { "kind": "fonts_set", "value": ["Arial", "Georgia"] },
        { "kind": "element_types", "slide": 1, "value": ["vector", "text"] },
        { "kind": "text_runs", "slide": 1, "element": 1,
          "value": [
            { "text": "RunA ", "font.family": "Arial", "font.size": 18,
              "font.color": "#0000FF", "font.bold": false, "font.italic": false },
            { "text": "RunB", "font.family": "Georgia", "font.size": 22,
              "font.color": "#00AA00", "font.bold": true, "font.italic": true,
              "font.underline": true }
          ] },
        { "kind": "field_equals", "slide": 1, "element": 1,
          "field": "position.x", "value": 100 },
        { "kind": "field_equals", "slide": 1, "element": 1,
          "field": "size.height", "value": 120 },
        { "kind": "field_equals", "slide": 1, "element": 1,
          "field": "font.letter_spacing", "value": 2 }
      ]
    },
    {
      "id": "04-vectors",
      "deck": "decks/04-vectors.json",
      "class": "transformed",
      "expectations": [
        { "kind": "element_types", "slide": 1, "value": ["vector", "text", "vector"] },
        { "kind": "field_equals", "slide": 1, "element": 0, "field": "fill.color",
          "value": "#123456" },
        { "kind": "field_equals", "slide": 1, "element": 0, "field": "fill.opacity",
          "value": 0.8 },
        { "kind": "field_equals", "slide": 1, "element": 0, "field": "stroke.width",
          "value": 3 },
        { "kind": "field_equals", "slide": 1, "element": 2, "field": "stroke.color",
          "value": "#FF00FF" },
        { "kind": "field_equals", "slide": 1, "element": 2, "field": "closed",
          "value": false },
        { "kind": "field_absent", "slide": 1, "element": 0, "field": "shape",
          "reason": "autoshape geometry type is flattened to a rectangle polygon" },
        { "kind": "field_absent", "slide": 1, "element": 0, "field": "rotation",
          "reason": "rotation is not surfaced by the converter" }
      ]
    },
    {
      "id": "06-image-media",
      "deck": "decks/06-image-media.json",
      "class": "preserved",
      "expectations": [
        { "kind": "element_types", "slide": 1, "value": ["image"] },
        { "kind": "field_matches", "slide": 1, "element": 0, "field": "data",
          "pattern": "^images/Presenton_Native_Image_1-[0-9a-f]{12}\\.png$" },
        { "kind": "field_equals", "slide": 1, "element": 0, "field": "fit",
          "value": "fill" },
        { "kind": "field_equals", "slide": 1, "element": 0, "field": "is_icon",
          "value": false },
        { "kind": "pptx_part_matches", "pattern": "^ppt/media/Presenton_Native_Image_1\\.png$" },
        { "kind": "retained_asset_exists", "pattern": "^images/Presenton_Native_Image_1-[0-9a-f]{12}\\.png$" }
      ]
    },
    {
      "id": "07-speaker-notes",
      "deck": "decks/07-speaker-notes.json",
      "class": "dropped",
      "expectations": [
        { "kind": "pptx_part_exists", "path": "ppt/notesSlides/notesSlide1.xml" },
        { "kind": "pptx_xml_contains", "path": "ppt/notesSlides/notesSlide1.xml",
          "contains": "W12_SPEAKER_NOTE_MARKER" },
        { "kind": "json_absent_text", "value": "W12_SPEAKER_NOTE_MARKER",
          "reason": "pptx-to-json does not surface notes; the note survives only in the PPTX" }
      ]
    }
  ]
}
```

### E.3 Assertion kinds

| `kind` | Meaning | Deterministic |
|---|---|---|
| `fonts_set` | the re-imported `fonts` array equals the set | yes |
| `element_types` | the `type` sequence of `layouts[i].elements` | yes |
| `text_runs` | per-run text + font attribute map | yes |
| `field_equals` | a dotted field equals a value (numbers compared with a 0.01 tolerance) | yes |
| `field_approx` | a numeric field within a tolerance | yes |
| `field_matches` | a field matches a regex (for content-hashed paths) | yes |
| `field_absent` | a field must **not** exist (a declared drop) | yes |
| `field_present` | a field must exist | yes |
| `json_absent_text` | a string must not occur anywhere in the re-imported JSON | yes |
| `json_contains_text` | a string must occur in the re-imported JSON | yes |
| `pptx_part_exists` | a ZIP entry exists (exact path) | yes |
| `pptx_part_matches` | a ZIP entry matches a regex | yes |
| `pptx_xml_contains` | a ZIP entry's XML contains a string | yes |
| `retained_asset_exists` | a file exists under the converter's retained asset dir | yes |
| `raw_slide_layouts_validate` | the re-imported JSON validates as Gomrey `RawSlideLayouts` | yes (Python tier) |

### E.4 Versioning and reporting

- `expectations/v1.json` — the file name carries the schema version.
  `schema_version` and `export_core_version` are inside the file, so a
  mismatch between the expectations and the installed runtime is a **hard
  error**, not a silent pass.
- **Version bump procedure.** When `package.json:presentationExportVersion`
  changes, the maintainer must (a) re-run the harness in `--update` mode to
  produce a candidate expectations file, (b) diff it against the committed
  file, (c) review every changed line, (d) commit the new expectations
  **and** a note in `PROVENANCE.md` recording what changed and why. A bare
  `--update` commit is a review failure.
- **Failure report.** A failing expectation must report, in this order:
  1. the failing expectation's `id`, `kind`, `field`, expected vs actual;
  2. the **taxonomy code** (§F);
  3. the **class** of the expectation (`preserved` / `transformed` / `dropped`)
     — a `preserved` failure is a regression; a `transformed`/`dropped`
     change is a behaviour-change notice;
  4. the fixture id and the deck file, so the run is reproducible;
  5. a pointer to the sibling evidence — the re-imported JSON and the PPTX
     part list — written to a run directory so a human can diff them.
- **Output format.** A human-readable table on stdout (pass/fail per
  expectation) plus one machine-readable JSON report
  (`w12-export-fidelity-report.json`) with `{schema_version, export_core_version,
  node_version, fixtures:[{id, status, failures:[{code, kind, field, expected,
  actual, reason}]}]}`. The report is the artefact the orchestrator and the
  REA evidence directory consume.

### E.5 Where the file lives and why it satisfies the policy

- The expectations file and the decks live under
  `servers/nextjs/tests/fixtures/export-fidelity/`, which is inside
  `config/fixture-policy.json:25` `scan.roots` → both
  `scripts/check-fixtures.mjs` and `scripts/scan-secrets.mjs` cover them.
- `PROVENANCE.md` in the fixture directory satisfies `:18`
  (`provenance_header`).
- `generator.mjs` + the recorded seed satisfies `:19` (`regeneration`).
- Total size is a few KiB — far below the 1 MiB skip threshold in
  `scripts/check-fixtures.mjs:49` and consistent with `:21` (`size_budget`).
- No deck contains a credential-like string, so `scripts/scan-secrets.mjs`
  passes. The image fixture is a `data:` URI inside a `.json` file — it is
  scanned as text, and a base64 PNG contains no secret pattern.

---

## F. The taxonomy

**Versioned failure-mode codes.** `taxonomy_version: 1`. Codes are stable
identifiers; the human text may be reworded without a version bump, but
adding/removing/re-purposing a code requires a bump.

Each code carries: `class` (see below), `severity`, and a one-line meaning.

- `class: regression` — a previously-preserved observable broke. **Blocking.**
- `class: behaviour-change` — a documented transform/drop changed shape.
  **Non-blocking**, but must be reviewed and the expectations file updated.
- `class: harness-error` — the harness itself failed (missing runtime, bad
  fixture, timeout). **Blocking**, but the diagnosis is "the harness", not
  "the product".
- `class: runtime-missing` — the export runtime is not installed. **Skip**
  with an explicit message.

| Code | Class | Severity | Meaning |
|---|---|---|---|
| `EF-RUNTIME-MISSING` | runtime-missing | skip | `presentation-export/` or `export-core/dist/index.js` absent |
| `EF-NODE-VERSION` | harness-error | blocker | Node < 22.12.0 (export-core `engines`) |
| `EF-DECK-UNREADABLE` | harness-error | blocker | fixture deck missing or not valid JSON |
| `EF-DECK-SCHEMA-INVALID` | harness-error | blocker | deck is not a valid `PptxPresentationModel` (e.g. `table` without `cells`) |
| `EF-EXPORT-TASK-FAILED` | regression | blocker | `pptx-from-json` threw or exited non-zero |
| `EF-EXPORT-TIMEOUT` | harness-error | blocker | export exceeded the per-fixture timeout |
| `EF-REIMPORT-TASK-FAILED` | regression | blocker | `pptx-to-json` threw or exited non-zero |
| `EF-REIMPORT-SCHEMA-INVALID` | regression | blocker | re-imported JSON failed `RawSlideLayouts` validation |
| `EF-ELEMENT-MISSING` | regression | blocker | an expected element is absent |
| `EF-ELEMENT-UNEXPECTED` | behaviour-change | minor | an extra element appeared |
| `EF-ELEMENT-TYPE-CHANGED` | regression | blocker | an element's `type` changed |
| `EF-ELEMENT-COUNT` | behaviour-change | major | the element count for a slide changed |
| `EF-FIELD-MISMATCH` | regression | blocker | a preserved field's value differs |
| `EF-FIELD-NUMERIC-DRIFT` | behaviour-change | major | a numeric field drifted beyond tolerance |
| `EF-FIELD-UNEXPECTEDLY-ABSENT` | regression | blocker | a preserved field disappeared |
| `EF-FIELD-UNEXPECTEDLY-PRESENT` | behaviour-change | minor | a documented-drop field reappeared |
| `EF-TEXT-CONTENT-MISMATCH` | regression | blocker | run text differs |
| `EF-TEXT-RUN-SPLIT-CHANGED` | behaviour-change | major | paragraphs merged/split differently |
| `EF-FONT-FAMILY-MISMATCH` | regression | blocker | font family differs |
| `EF-FONT-SET-CHANGED` | behaviour-change | minor | the `fonts` set differs |
| `EF-GEOMETRY-DRIFT` | behaviour-change | major | position/size differs beyond tolerance |
| `EF-GEOMETRY-FLATTENED` | behaviour-change | major | a shape's geometry was flattened (e.g. ellipse → rectangle) |
| `EF-FILL-MISMATCH` | regression | blocker | fill colour/opacity differs |
| `EF-STROKE-MISMATCH` | regression | blocker | stroke colour/width differs |
| `EF-SHADOW-MISMATCH` | behaviour-change | minor | shadow offset/angle conversion differs |
| `EF-TABLE-STRUCTURE-CHANGED` | behaviour-change | major | header/body split or cell count changed |
| `EF-CHART-SERIES-MISMATCH` | regression | blocker | chart categories/series/values differ |
| `EF-CHART-AXIS-TITLE-LOST` | behaviour-change | minor | an axis title stopped being emitted |
| `EF-ASSET-MISSING` | regression | blocker | a retained asset (image/font) is absent |
| `EF-ASSET-PATH-UNSTABLE` | behaviour-change | minor | a retained-asset path no longer matches its expected pattern |
| `EF-PPTX-PART-MISSING` | regression | blocker | a ZIP part (media/chart/notes) is absent |
| `EF-PPTX-PART-UNEXPECTED` | behaviour-change | minor | a new ZIP part appeared |
| `EF-NOTE-NOT-WRITTEN` | regression | blocker | the speaker note is missing from the PPTX |
| `EF-NOTE-NOT-ROUNDTRIPPED` | behaviour-change | minor | a note that used to be dropped is now imported (or vice versa) |
| `EF-NONDETERMINISTIC-ARTIFACT` | regression | blocker | two runs of the same fixture produced different re-imported JSON |
| `EF-SILENT-SKIP` | regression | blocker | a shape produced no output and no error (an invalid `shape_type`) |
| `EF-DECL-DROP-UNDECLARED` | harness-error | blocker | a previously-dropped field is neither declared nor preserved — expectations need a review |
| `EF-ADVERSARIAL-CRASH` | regression | blocker | the adversarial fixture made the runtime throw instead of degrading |
| `EF-ADVERSARIAL-HANG` | harness-error | blocker | the adversarial fixture exceeded the timeout |

**Reporting rule.** A `regression`-class failure is a red build. A
`behaviour-change`-class finding is printed as a **notice** and written into
the JSON report under `changes`, not `failures` — with the explicit note that
the expectations file must be reviewed and bumped. `harness-error` and
`runtime-missing` never masquerade as product regressions: they abort the
fixture with a message that says so.

### F.1 Provenance of the taxonomy

The Gamma `import-grader-annotator` was named as a **pattern reference** for
"a versioned, machine-readable grader rubric attached to an import pipeline".
It is **internal Gamma QA tooling and is not permissively licensed**. It is
not present anywhere in this repository (searched: no `*grader*` file under
`research/`), and **no code, text, taxonomy, label, or structure from it has
been copied here**. Everything in §F was written from scratch against the
measured behaviour of the pinned export runtime, using the repository's own
conventions (`config/fixture-policy.json` `schema_version: 1`,
`scripts/validate-contracts.mjs`, `config/`-scoped policy files). If a future
wave wants to align taxonomies, that is a fresh, separately-reviewed task
with its own licence clearance.

---

## G. Test plan

### G.1 Node harness — `servers/nextjs/tests/export-fidelity.test.mjs` (CI tier)

Follows the established `node:test` conventions
(`servers/nextjs/tests/template-v2-json-to-html-metadata.test.mjs:1-34`):
`node:assert/strict`, `node:test`, `mkdtemp` in `test.before`, `rm` in
`test.after`.

Arrangement:

1. `test.before` — resolve the export package root
   (`EXPORT_PACKAGE_ROOT` or `<repo>/presentation-export`), import
   `@presenton/export-core` from `<root>/node_modules/@presenton/export-core/dist/index.js`,
   create the temp output dir.
2. `test.before` — read `expectations/v1.json`, read the eight deck files.
3. Per fixture: `pptx-from-json` → `pptx-to-json` → evaluate the expectations.
4. `test.after` — remove the temp dir.

Concrete test names:

| Test | Fixture | Asserts |
|---|---|---|
| `export fidelity: runtime is installed and runnable` | — | `export-core/dist/index.js` exists; `engines.node` satisfied; else `EF-RUNTIME-MISSING` / `EF-NODE-VERSION` |
| `export fidelity: 01 preserves text runs and font attributes` | 01 | `fonts_set`, `element_types`, `text_runs`, `field_equals` on `position`/`size`/`letter_spacing` |
| `export fidelity: 02 flattens paragraph alignment, bullets and levels` | 02 | the joined run text is exactly `"Centred paragraph\n1. Numbered item\n• Bulleted item"`; `alignment.horizontal === "left"`; `alignment.vertical === "top"`; no `level` key |
| `export fidelity: 03 preserves table cell text and the header/body split` | 03 | `columns` = 2 header cells with `color #DDDDDD`; `rows` = 2 body rows; `min_rows === 3` |
| `export fidelity: 04 flattens autoshape geometry and preserves fill/stroke` | 04 | element types `["vector","text","vector"]`; `fill.color/opacity`; `stroke.width`; connector `stroke.color`; `shape` field absent; the shape's text is a sibling `text` element |
| `export fidelity: 05 preserves chart type, categories, series and legend` | 05 | `chart_type`, `title`, `categories`, `series` names/values, `legend`, `legend_position`; `x_axis_title` absent; PPTX contains `ppt/charts/chart1.xml` and `ppt/embeddings/*.xlsx` |
| `export fidelity: 06 embeds image media and exposes a retained asset path` | 06 | `element_types === ["image"]`; `data` matches the content-hash regex; `fit === "fill"`; `is_icon === false`; PPTX contains `ppt/media/Presenton_Native_Image_1.png`; the retained file exists on disk |
| `export fidelity: 07 writes speaker notes into the PPTX but does not re-import them` | 07 | `ppt/notesSlides/notesSlide1.xml` exists and contains the marker; the marker does **not** occur in the re-imported JSON |
| `export fidelity: 08 survives adversarial content without throwing or hanging` | 08 | both tasks succeed; 2 layouts; the second has `elements: []`; the 2000-char run and the RTL+emoji string survive verbatim; `NoSuchFontXYZ` is present in `fonts` |
| `export fidelity: re-imported JSON is byte-stable for a fixed input PPTX` | 01 | two `pptx-to-json` runs of the same PPTX produce identical bytes |
| `export fidelity: the export runtime rejects an invalid shape_type loudly or not at all` | — | a deck with `shape_type:"pictureBox"` produces no element and no media part — recorded as `EF-SILENT-SKIP` so a future change to loud failure is detected |
| `export fidelity: deck fixtures are byte-stable` | all | `sha256` of each committed deck file matches a value recorded in `expectations/v1.json` (`decks` section) |
| `export fidelity: every fixture has at least one preserved and one dropped expectation` | all | a meta-test over the expectations file, so a fixture cannot silently become vacuous |

**Command:**

```sh
cd servers/nextjs && node --test tests/export-fidelity.test.mjs
```

**Skip behaviour.** If `presentation-export/` is absent, the harness must
`t.skip()` with the message
`"presentation-export runtime not installed — run `npm run sync:presentation-export`"`,
mirroring `bundledExportPackageAvailable()`
(`servers/nextjs/lib/run-bundled-presentation-export.ts:45-56`). It must
**not** fail, and it must not silently pass.

### G.2 Python harness — `servers/fastapi/tests/test_export_fidelity.py` (opt-in)

Exercises the **real Gomrey import boundary**
(`ExportTaskService.convert_pptx_to_json`, `export_task_service.py:690-729`),
which the Node harness bypasses.

| Test | Asserts |
|---|---|
| `test_convert_pptx_to_json_returns_raw_slide_layouts` | the service's `layouts` validate as `RawSlideLayouts` (`templates/v2/models/layouts.py:51-52`) — the same call the template endpoint makes (`template.py:957-959`) |
| `test_convert_pptx_to_json_narrows_the_document_to_layouts_only` | `PptxToJsonDocument` exposes **only** `layouts`; `font_css` / `fonts` / `images_dir` are **not** attributes — a documented drop at `export_task_service.py:102-103` + `:719` |
| `test_convert_pptx_to_json_rejects_a_missing_pptx` | HTTP 400, `"PPTX not found: …"` (`:691-692`) |
| `test_export_fidelity_service_matches_the_node_expectations` | the service's re-imported `layouts` equal the same `expectations/v1.json` expectations the Node harness checks (the two tiers must not drift) |

Conventions: plain `def test_*(tmp_path, monkeypatch)`, `asyncio.run(...)` for the
async service calls (no `pytest-asyncio` in the dev deps —
`servers/fastapi/pyproject.toml:60-64`), `monkeypatch.setenv("APP_DATA_DIRECTORY", …)`
and `monkeypatch.setenv("EXPORT_PACKAGE_ROOT", …)` (`_resolve_export_dir`,
`:129-149`; `_build_node_env`, `:154-206`).

**Command:**

```sh
cd servers/fastapi && uv run --locked python -m pytest tests/test_export_fidelity.py -v
```

**Guard.** The Python harness spawns `node runner.mjs` and needs the runtime
(`_ensure_runtime_ready`, `:208-227`). Gate it on an env var
(`GOMREY_EXPORT_FIDELITY=1`) so the default `pytest` run
(`.github/workflows/test-all.yml:75`) is unaffected, and add a dedicated CI
job that sets it.

### G.3 Optional Tier B harness — browser

`servers/nextjs/tests/export-fidelity-browser.test.mjs`, gated on
`GOMREY_EXPORT_FIDELITY_BROWSER=1` **and** a resolvable Chromium. It renders a
Gomrey slide-model deck through `templateV2UiToHtml` and
`runTask({type:"html-to-any", format:"pptx"})`, then re-imports. Assertions
must be **tolerant** (element types and text content only) because the browser
path measures the DOM (§C.2). It must **not** assert on PPTX or PDF bytes, and
must not assert on exact geometry.

This is the only tier that covers the production export path, and it is
explicitly *not* a CI gate.

### G.4 CI wiring

1. Add a Node 22 job (or bump `test-nextjs` to Node 22 — `test-all.yml:91`).
2. In that job: `npm run sync:presentation-export` and
   `npm run check:presentation-export` (mirroring `test-all.yml:34-38`).
3. Run `node --test tests/export-fidelity.test.mjs` (or `npm test`, which
   already runs `node --test` over the whole `tests/` directory —
   `servers/nextjs/package.json`).
4. Optionally add a Python job with `GOMREY_EXPORT_FIDELITY=1`.
5. `node scripts/check-fixtures.mjs` (already in `test-all.yml:176`) will
   automatically cover the new fixture directory because it is under
   `servers/nextjs/tests` (`config/fixture-policy.json:25`).

### G.5 Full local run

```sh
# 1. one-time, free, no credentials
npm run sync:presentation-export
npm run check:presentation-export

# 2. Node harness (deterministic, no browser)
cd servers/nextjs && node --test tests/export-fidelity.test.mjs

# 3. Python harness (needs the runtime; opt-in)
cd servers/fastapi && \
  APP_DATA_DIRECTORY=/tmp/gomrey-app-data \
  TEMP_DIRECTORY=/tmp/gomrey-temp \
  EXPORT_PACKAGE_ROOT="$PWD/../../presentation-export" \
  GOMREY_EXPORT_FIDELITY=1 \
  uv run --locked python -m pytest tests/test_export_fidelity.py -v
```

---

## H. Risks and non-goals

### H.1 What a fidelity harness must NOT claim

1. **Not pixel equality.** Nothing in this harness compares rendered pixels.
   There is no renderer in CI, no font stack parity, no display profile.
2. **Not PowerPoint correctness.** The harness reads OOXML. It never opens
   PowerPoint, Keynote, or Google Slides. A file can satisfy every
   expectation here and still render differently in PowerPoint.
3. **Not coverage of the production export path.** Tier A exercises the
   export-core PPTX writer and reader, **not** the browser pipeline that
   production uses (`PdfMakerPage.tsx`). Tier B covers the browser pipeline
   but is not a CI gate. The harness must not be described as "the export
   regression suite" without that caveat.
4. **Not a proof of determinism for the shipped artifact.** The PPTX bytes are
   not reproducible (UUID filenames, wall-clock ZIP timestamps). The harness
   asserts on the **re-imported content**, which is reproducible.
5. **Not a defect list.** Many "losses" in §B.4 are the converter's *design*,
   not bugs. The harness records them as `transformed`/`dropped`, and a change
   in a dropped field is a notice, not a red build.
6. **Not a substitute for a visual diff.** Visual regressions (overlap,
   clipping, wrong colours) remain uncovered. A pixel-diff tier would need a
   pinned browser, a pinned font set, and a golden-image store — out of
   scope for W12 and expensive to keep honest.
7. **Not a licence to copy Gamma.** See §F.1.
8. **Not a validator of `pptx_font_utils`.** Font aliasing mutates the PPTX
   before import and would confound the measurement. It is out of scope.

### H.2 Risks

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | **`shape_type` is undocumented** — the d.ts types it as bare `string` (`dist/index.d.ts:106,116,131,151,186,226`); the accepted values were discovered empirically (§B.5). A future export-core could rename them. | medium | The harness pins `export_core_version` in the expectations file and hard-fails on a version mismatch; a rename surfaces as `EF-SILENT-SKIP` / `EF-ELEMENT-MISSING` immediately, not silently |
| R2 | **The expectations file encodes a third-party version's behaviour.** Bumping `package.json:presentationExportVersion` changes fidelity | high (by design) | Version is pinned in `expectations/v1.json`; a mismatch is a hard error; a bump requires a reviewed expectations update (§E.4) |
| R3 | **CI runs Node 20; export-core needs ≥ 22.12.0.** A new job is required | certain | §G.4; the harness itself checks `engines` and reports `EF-NODE-VERSION` |
| R4 | **`sync:presentation-export` needs GitHub Releases egress.** CI or a restricted network may block it | medium | `EXPORT_CORE_ARCHIVE` (`sync-presentation-export.cjs:314-320`) allows an offline tarball; the harness skips cleanly when the runtime is absent |
| R5 | **A browser task could be triggered accidentally**, pulling ~150 MB of Chromium into CI | medium | Tier A fixtures contain no image/HTML tasks; the browser harness is behind an env gate; add a CI assertion that `PUPPETEER_CACHE_DIR` stays empty in the Tier A job |
| R6 | **The adversarial fixture could hang or crash export-core** | low | Per-fixture timeout (`EF-EXPORT-TIMEOUT`); the expectation is "degrades, does not throw"; a throw is `EF-ADVERSARIAL-CRASH` |
| R7 | **Fixture drift between the Node and Python tiers** — two harnesses, two expectations | medium | The Python test asserts against the *same* `expectations/v1.json`; the fixture decks live in one directory, not two |
| R8 | **The fixture directory is inside `scan.roots`, so a future deck could trip the secret scanner** | low | Decks are synthetic; no credential-like strings; `check-fixtures.mjs` and `scan-secrets.mjs` run in CI and will block a bad commit |
| R9 | **The browser path measures the DOM, so a Tier B regression would look like a Tier A regression if the tiers were mixed** | medium | Separate test files and separate expectations classes; Tier B expectations are tolerant by construction (§G.3) |
| R10 | **`PptxToJsonDocument` silently narrows the payload** (`:102-103`, `:719`), so a Python-side harness cannot see `fonts` | certain | Assert the narrowing as a documented fact (`test_convert_pptx_to_json_narrows_the_document_to_layouts_only`); do not treat it as a harness bug |
| R11 | **The repo's branch state moved during analysis** (w3 → w13) and `research/` was absent on the working branch | certain | The deliverable is untracked; §"Repo state caveat" records it; the landing engineer must check out the wave branch before `git add` |

### H.3 Non-goals for W12

- No changes to `run-bundled-presentation-export.ts`, `sync-presentation-export.cjs`,
  `run-presentation-export.mjs`, or `export_task_service.py`. W12 is
  **additive**: new test files, new fixture directory, one expectations file,
  and a CI job.
- No change to the export runtime version.
- No pixel/visual regression tier.
- No font-aliasing coverage.
- No benchmark or performance budget for the export path.
- No attempt to make the PPTX byte-reproducible (that is an export-core
  concern, not a harness concern).

---

## Appendix — provenance of the measured facts

Every "measured" claim in this document came from executing the pinned runtime
present in this checkout:

```
presentation-export/node_modules/@presenton/export-core@1.0.34
  dist/index.js   (obfuscated bundle)
  dist/index.d.ts (1120 lines — the type surface cited throughout)
  README.md       (329 lines)
```

Probes were run from a scratch directory outside the repository
(`$TMPDIR/opencode/w12-probe/`). No repository file was created, modified, or
deleted. Probe scripts covered: `pptx-from-json` / `pptx-to-json` /
`json-to-html` / `html-to-any` round trips; a 12-value `shape_type` sweep;
5 image-source variants; the 8 final fixture decks; byte-stability of the
PPTX artifact, the re-imported JSON, and the HTML string; and the
browser-vs-browser path.

Node version used for measurement: **v26.0.0** (the CI jobs use Node 20 —
see R3).
