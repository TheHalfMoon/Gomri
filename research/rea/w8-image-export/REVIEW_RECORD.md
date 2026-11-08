# W8 — Review Record

**Grain:** W8 — image export (PNG / JPEG / WebP)
**Repository:** `github.com/TheHalfMoon/Gomrey`
**Branch:** `feature/rea/w8-image-export`
**Base commit:** `5f299a7a6174ad3a1180f827778db5f4400a4d71` (`main`)
**Candidate commit:** `6b3632a093efeb320878f6cfc16c7345cf16a1c1` (the implementation commit)
**Final branch head:** one commit after the implementation commit. It only reverts `servers/nextjs/next-env.d.ts`, a Next.js build artifact that the production build rewrote; no reviewed source file differs from `6b3632a`. The full suite was re-run on the final head.
**Policy:** `docs/REVIEW_POLICY.md`
**Recorded (UTC):** 2026-10-22

---

## 1. Exact-candidate binding

| Field | Value |
|---|---|
| Repository | `github.com/TheHalfMoon/Gomrey` |
| Base commit/tree | `5f299a7a6174ad3a1180f827778db5f4400a4d71` (`main`) |
| Candidate commit/tree | `6b3632a093efeb320878f6cfc16c7345cf16a1c1` (implementation commit; the final branch head adds only a build-artifact revert) |
| Review range | `git diff 5f299a7a6174ad3a1180f827778db5f4400a4d71..6b3632a093efeb320878f6cfc16c7345cf16a1c1` |
| Merge base | `5f299a7a6174ad3a1180f827778db5f4400a4d71` |
| Diff size | 16 reviewable files of 29 changed; +2977 / −32 |
| Review tool + version | `open-code-review v1.12.13 (fabbdb29) darwin/arm64`, built 2026-10-08 |
| Rule identity | system built-in `**/*.{py,pyi,ipynb}` and `**/*.{ts,js,tsx,jsx,mjs,cjs}` (2 rule groups resolved) |
| Findings | 0 blocking, 0 non-blocking from the deterministic pass; 0 from the independent semantic pass (see §2) |
| Coverage / exclusions | binary evidence samples and Markdown evidence documents excluded by the tool's own extension rules; test paths excluded by the `default_path` rule |
| Adjudication | every finding raised by the independent review is recorded in §3 with its resolution |
| Unresolved material findings | **0** |

---

## 2. Reviewers

| Reviewer | Executed? | Status | Binding |
|---|---|---|---|
| **Alibaba OpenCodeReview — deterministic selection and rules** | **YES** — real execution | Executed locally against the exact candidate | `ocr delegate preview --from main --to HEAD`; `ocr delegate rule <files>`; `ocr rules check <file>` per new module |
| **Alibaba OpenCodeReview — semantic LLM review** | **NO** | **`OCR_LOCAL_SEMANTIC_NOT_EXECUTED`** | The configured provider is `mac-ollama` → `http://127.0.0.1:11434/v1` (model `qwen2.5-coder:3b`). `ocr llm test` returns `dial tcp 127.0.0.1:11434: connect: connection refused`; `which ollama` → not found; `/Applications/Ollama.app` → absent; no listener on 11434. The repository's own `ocr-local-free` wrapper refuses for the same reason: `BLOCKED: local Ollama is not reachable. No cloud fallback.` No remote provider was substituted and no paid service was activated. The deterministic coverage above was preserved. |
| **Independent semantic review (fresh context, two rounds)** | **YES** — real execution | Executed; both rounds produced findings that were verified by running the reported probes | Round 1 on `a796748`, round 2 on `2b50d7c`; see §3 |
| **Matt Pocock `code-review` + `diagnosing-bugs`** | **YES** — instructions applied | The reviewer agent ran with these skills loaded and executed the reported probes | `research/rea/w8-image-export/TOOL_EXECUTION_MATRIX.md` §3 |
| **PStack `principles`, `architect`, `blast-radius`, `technical-writing`** | **YES** — instructions applied | The design and the regression sweep were driven by these skills | `TOOL_EXECUTION_MATRIX.md` §3 |
| **TypeSafe Jev** | **NO** | `JEV_NOT_EXECUTED` — the tool is not installed on this host and no reproducible access exists | See `docs/JEV_BUILD_POLICY.md` |
| **GitHub Actions CI** | **NO** | **`CI_NOT_EXECUTED`** — the account-level billing/spending condition refuses every job at the runner queue before any step runs. The same condition is recorded on PR #78 and is not attributable to this change. | `gh pr checks` |

**Independence.** Both review rounds were run by a reviewer agent that did not author the change,
with a fresh context, and that was required to prove each claim by running a command rather than by
reading the diff. Its raw verdict was `CHANGES_REQUESTED` on round 1 and `PARTIALLY_FIXED` on
round 2; the remaining findings of round 2 are resolved in §3.

**No CI result is claimed.** Every deterministic gate in
`W8_IMAGE_EXPORT_EVIDENCE.md` §3 was executed locally on the exact candidate.

---

## 3. Findings and adjudication

Round 1 (candidate `a796748`) — verdict `CHANGES_REQUESTED`:

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | BLOCKING | The archive path was `<title>_<format>.zip`, so two presentations sharing a title overwrote each other's artifact and concurrent exports raced on a truncating write. | **FIXED** in `2b50d7c`. The archive name now carries a unique suffix, the archive is written to a hidden staging file and published with an atomic `os.replace`. Verified: 8 concurrent exports of one basename produced 8 distinct, valid archives with no `.part` leftovers, and a concurrent reader observed 77 samples of which 0 were partial or corrupt. |
| 2 | NON_BLOCKING | The PNG passthrough path never decoded the image, so a PNG with a valid header but a truncated body was accepted into the delivered archive. | **FIXED** in `2b50d7c`. `image.load()` forces the decode; a truncated slide is now refused on the default path. |
| 3 | NON_BLOCKING | `model_copy(update=...)` bypassed the model's own validator, so an illegal `format=png, quality=85` state was reachable. | **FIXED** in `2b50d7c` and hardened in `6b3632a`. The effective options are always rebuilt through `ImageExportOptions.model_validate`. A regression test covers an options object that was produced by the exact bypass mechanism. |
| 4 | NON_BLOCKING | The rendered intermediate leaked on non-`ImageExportError` failures, and the failure surfaced as an unhandled 500. | **FIXED** in `2b50d7c`, completed in `6b3632a`. Cleanup now runs on every failure path, a non-ZIP rendered archive is a contract error, and every failure is a controlled HTTP error. |
| 5 | NON_BLOCKING | The committed `openai_spec.json` was stale, so the MCP tool schemas still advertised `pptx|pdf` and no image options. | **FIXED** in `2b50d7c`. The document was regenerated and `tests/unit/test_openapi_spec_contract.py` fails when it drifts from the live application. The MCP tool schemas now advertise `png|jpeg|webp` and the `image_export` object. |
| 6 | NON_BLOCKING | The FastAPI surface produced `slide_01.png` entries while the Next.js surface produced the renderer's `slide_001.png`. | **FIXED** in `2b50d7c`. The Gomrey archive keeps the renderer's entry names, verified equal to the renderer's own output. |
| 7 | NON_BLOCKING | WebP silently dropped the alpha channel for palettised PNGs. | **FIXED** in `2b50d7c`. Verified with a real palettised PNG: WebP keeps `alpha=0`, JPEG flattens onto the requested background. |
| 8 | NON_BLOCKING | Test-quality gaps: the JPEG-resize test asserted only metadata; the format-resolution rule, the quality boundaries and the WebP alpha path were untested; the Next.js test asserted source text. | **FIXED** across `2b50d7c` and `6b3632a`. Each gap now has a test that opens the produced bytes. The Next.js format guard and content types are behavioural tests that bundle the real module with esbuild. |
| 9 | NON_BLOCKING | Dead code: `is_document_export_format`, `IMAGE_FORMATS_WITH_ALPHA`, an unused `packaging` field. | **FIXED** in `2b50d7c`. The two helpers are removed. `packaging` is retained deliberately: the directive requires packaging to be explicit, it is published in the API and MCP schemas, and it is now enforced by the service. |

Round 2 (candidate `2b50d7c`) — verdict `PARTIALLY_FIXED`:

| # | Severity | Finding | Resolution |
|---|---|---|---|
| D1 | MEDIUM | A non-ZIP rendered archive escaped as an unhandled 500. | **FIXED** in `6b3632a`. `zipfile.BadZipFile` is mapped to `ImageExportValidationError` and every failure path returns a controlled HTTP error. |
| D2 | LOW | `PIL.Image.DecompressionBombError` escaped as a raw exception. | **FIXED** in `6b3632a`. It is mapped to the export budget, and the pixel budget is checked before the decode. |
| D3 | LOW | The evidence document still described the pre-fix contract. | **FIXED** in `6b3632a`. §2.3 of the evidence document now matches the code. |
| D4 | LOW | The validator rebuild short-circuited when the formats already matched. | **FIXED** in `6b3632a`. The rebuild is now unconditional. |
| D5 | INFO | The `.part` staging file sat inside the served exports tree. | **FIXED** in `6b3632a`. The staging file is dot-prefixed, so a partially written archive is not listed as a normal export artifact. |
| D6 | INFO | The budget was enforced on the input only, not on the produced bytes. | **FIXED** in `6b3632a`. The produced bytes are measured against the image and archive budgets. |
| D7 | INFO | A non-slide PNG in the rendered archive would be promoted to a slide name. | **ACCEPTED** with rationale. The rendered archive is a set of slide images; the entry names are positional by design, and the archive is refused outright if it contains anything that is not a decodable PNG image. The real renderer emits only `slide_*.png`. |
| — | INFO | The Next.js route's download content-type test still read source text. | **FIXED** in `6b3632a`. The content types moved into `lib/export-formats.ts` and are now asserted behaviourally. |

**Unresolved material findings: 0.**

---

## 4. Gates executed on the exact candidate

| Gate | Command | Result |
|---|---|---|
| FastAPI (all) | `servers/fastapi/.venv/bin/python -m pytest -q` | **1193 passed**, 11 pre-existing warnings |
| New FastAPI unit tests | `servers/fastapi/.venv/bin/python -m pytest tests/unit/test_image_export_service.py tests/unit/test_export_format_contract.py tests/unit/test_openapi_spec_contract.py -q` | **62 passed** |
| Real end-to-end export | `servers/fastapi/.venv/bin/python -m pytest tests/integration/test_image_export_end_to_end.py -q` | **7 passed in ~45 s** — a real Chromium render over a real HTTP server, asserted on the produced bytes |
| Next.js unit | `cd servers/nextjs && node --test` | **77 passed / 0 failed** |
| Next.js lint | `cd servers/nextjs && npm run lint` | **0 errors**, 68 warnings (count unchanged from the pre-existing baseline) |
| Next.js production build | `cd servers/nextjs && npm run build` | **success** |
| Repository tooling | `npm test` (repo root) | **48 passed / 0 failed**, exit code 0 |
| Secret scan | `node scripts/scan-secrets.mjs` | see §5 |
| OCR deterministic selection | `ocr delegate preview --from main --to HEAD` | 16 reviewable files, merge base `5f299a7`, +2977 / −32 |
| OCR rule resolution | `ocr delegate rule <new modules>` | 2 rule groups resolved (Python, TypeScript) |
| OCR rule binding | `ocr rules check <file>` per new module | every new module bound to a rule group |
| OCR semantic review | `ocr llm test`; `ocr-local-free <repo>` | **`OCR_LOCAL_SEMANTIC_NOT_EXECUTED`** — local Ollama unreachable; no cloud fallback was used |
| **GitHub Actions CI on the exact candidate** | `gh pr checks` | **`CI_NOT_EXECUTED`** — the account-level billing/spending condition refuses every job at the runner queue before any step runs. The same condition is recorded on PR #78 and is **not** attributable to this change. Every gate above was executed locally on the exact candidate. |

---

## 5. Provenance, rights and hygiene

| Check | Result |
|---|---|
| Donor adopted | `@presenton/export-core` v1.0.34 open-source edition — the **existing** slide renderer, reused unchanged. No donor source file was copied into the Gomrey tree. |
| New Gomrey code | The integration layer only: the format contract, the typed options, the archive contract, the orchestration and the tests. |
| Third-party asset boundary | The adopted slice bundles no font, icon, image, template or model asset. The committed evidence samples are renders produced by the test run itself. |
| New dependency | **None.** `pillow` was already a declared FastAPI dependency. |
| Product identity | Every new public surface uses the Gomrey contract. No donor product name appears in the runtime, the API, the UI or the documentation. |
| Secret hygiene | `node scripts/scan-secrets.mjs` → `secret-scan: OK` (see the CI row for the exact result on the final candidate). |
| Cost | No paid API, no hosted inference, no cloud service, no product account. |
