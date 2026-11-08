# EXPERIMENTS — every command that was run

**Mission:** Issue #77.
**Date (UTC):** 2026-10-22
**Host:** macOS 25.0 (darwin), arm64, 8 cores, 8 GiB RAM. Node v26.0.0, npm 11.12.1, Python 3.13.5
(system) / Python 3.11 (project venv), uv 0.11.20, curl 8.7.1, ripgrep 15.2.0.

This file is the operator-level index. Two deeper run logs exist and are referenced rather than
duplicated:

- `evidence/LIVE_PROBE_LOG.md` — every live network fetch, HTTP status, raw snippet and failure.
- `evidence/NEXTSLIDE_PROBE_RUNLOG.md` — every donor probe command, artifact path and sha256.

---

## E0 — Source acquisition

| # | Command | Result |
|---|---|---|
| E0.1 | `gh issue view 77 --repo TheHalfMoon/Gomrey` | Retrieved the canonical mission (issue body supersedes the operator brief in detail). |
| E0.2 | `gh repo clone TheHalfMoon/Gomrey Gomrey` | `main@5f299a7a6174ad3a1180f827778db5f4400a4d71`, 552 MB working tree. |
| E0.3 | `gh repo clone 0xRafie/nextslide donor-nextslide` | `90a46f933b3056d27460400c915ef268a9ec3f56`, MIT, 13 tracked files. |
| E0.4 | `gh repo clone morluto/rea rea-tool` | `4a4bbab3c337701febeb6b532ace49041c4876e0` (`rea-agents` v6.7.0). |
| E0.5 | `gh repo clone gamma-app/n8n-nodes-gamma donor-gamma-n8n` | `5d0b466a9ae4be994a722577daa0a761cb28cfaf`, **MIT, © 2025 Gamma**, 49 files incl. a 12-file test suite. |
| E0.6 | `git ls-tree -r HEAD` on the donor | Recorded every blob id for the provenance record. |

## E1 — Tooling availability probes

| # | Command | Result |
|---|---|---|
| E1.1 | `gh auth status` | 3 accounts; `TheHalfMoon` active, scopes `repo`, `workflow`, `admin:ssh_signing_key`. |
| E1.2 | `command -v rea graft pstack opencodereview jev` | `graft` ✔ 0.21.1, `jev` ✔ 2026.919.0, `rea` ✘, `pstack` ✘, `opencodereview` ✘ (package present instead). |
| E1.3 | `env | grep -oiE "…(API_KEY\|TOKEN\|ANTHROPIC\|OPENAI\|GEMINI\|…)"` | **No LLM provider key present.** This is the blocker for `rea`'s and `graft`'s LLM-backed paths. |
| E1.4 | `node …/open-code-review/bin/ocr.js auth status` | `Not signed in, run ocr auth login --provider chatgpt.` → **OCR semantic pass blocked.** |
| E1.5 | `node …/ocr.js delegate preview` | **Works without an LLM.** Reports the exact reviewable file/range set → satisfies the deterministic half of `REVIEW_POLICY.md` §1.1. |
| E1.6 | `node …/ocr.js delegate rule <path>` / `ocr rules check <path>` | **Works without an LLM.** Resolved rule identity per file. |
| E1.7 | `jev noul --state "…" "Is 2+2=4?"` | **Real execution:** `{"noul":0.98,"type":"noul"}`, `model: jev-1.14.0`, `latency_ms:495`. |
| E1.8 | `jev choice --opt copy=… --opt adapt=… --opt reference=… "What adoption mode fits?"` | **Real execution:** `{"choice":"adapt","confidence":0.38,"probabilities":{"adapt":0.59,"copy":0.25,"reference":0.16}}`. |
| E1.9 | `jev --version` | `jev 2026.919.0`. |

> **Correction recorded:** an earlier working assumption was that TypeSafe Jev was unavailable because
> no key was visible in the environment. Probing proved the opposite — the CLI executes and returns
> calibrated typed output. The assumption was wrong and was replaced with the measured result.

## E2 — Baseline gate runs (pre-change)

| # | Command | Result |
|---|---|---|
| E2.1 | `npm ci` (root) | `added 69 packages` |
| E2.2 | `npm test` | **48 pass / 0 fail** |
| E2.3 | `cd servers/fastapi && uv sync --locked --dev` | Python 3.11 venv resolved from `uv.lock` |
| E2.4 | `uv run --locked python -m pytest -q --tb=line` | **1125 passed**, 10 warnings, 31.18 s |
| E2.5 | `cd servers/nextjs && npm ci` | `added 892 packages` |
| E2.6 | `npm test` | **73 pass / 0 fail** |
| E2.7 | `npm run lint` | **0 errors**, 68 warnings (pre-existing) |
| E2.8 | `npm run build` | success |
| E2.9 | `cd electron && npm ci --ignore-scripts` | `added 448 packages` |
| E2.10 | `npm run typecheck` / `build:ts` / `check:main-no-undef` / `test:path-migration` | all pass; `No undefined names found in 39 Electron main JS files.`; 11/11 |
| E2.11 | `node scripts/scan-secrets.mjs` | `secret-scan: OK` |
| E2.12 | `node scripts/check-platform-support.mjs` | `platform-support: OK (linux full-integration; windows/macos bounded)` |
| E2.13 | `node scripts/validate-release-config.mjs` | `release-config: OK` |
| E2.14 | `node scripts/generate-release-manifest.mjs --check-only` | `release-manifest: OK (Gomrey 0.1.0 @ 5f299a7)` |
| E2.15 | `node scripts/check-fixtures.mjs` | `fixture-policy: OK` |
| E2.16 | `npm run sync:presentation-export && npm run check:presentation-export` | `[presentation-export] Installed export-core 1.0.34` → `OK (1.0.34)` |

## E3 — Gap probes

| # | Command | Result |
|---|---|---|
| E3.1 | `rg -ci "slideTransition\|entranceAnimation\|transitionName\|animationPreset" app components lib utils` | **0 files** → no slide animation model |
| E3.2 | `rg -c "prefers-reduced-motion" app components lib utils` | 2 files → reduced motion only partially present |
| E3.3 | `rg -c "@keyframes" app/globals.css` | 12 — all product chrome, none slide-level |
| E3.4 | `rg -ci "brand_?kit" app components lib utils models` | **0 files** → no brand kit |
| E3.5 | `rg -l "presenter" app components lib` | `PresentationMode.tsx` → presenter mode already present |
| E3.6 | `find . -type d -name "*export*"` | `app/(export)/pdf-maker`, `app/api/export-presentation{,/data}` → export exists |
| E3.7 | `rg -n "Literal\[\"pptx\",\"pdf\"\]" servers/fastapi/utils/export_utils.py` | export enum is PPTX/PDF only → no image export |
| E3.8 | `find . -name "*.test.*"` in `servers/nextjs` | 19 pre-existing `.test.mjs` files → conventions known |

> E3.1 and E3.4 initially returned polluted hits from a minified Tailwind bundle in
> `public/vendor/`; the search was re-scoped to source directories only and the polluted run is
> recorded here rather than hidden.

## E4 — Donor inspection

| # | Command | Result |
|---|---|---|
| E4.1 | `grep -n '^## Preset ' STYLE_PRESETS.md` | 18 headings |
| E4.2 | `grep -c '^:root {' STYLE_PRESETS.md` | **18** independent CSS blocks — corroborates E4.1 |
| E4.3 | `grep -o -- '--ns-[a-z0-9-]*' STYLE_PRESETS.md \| sort -u` | **19** unique custom properties |
| E4.4 | `grep -o 'data-layout="[a-z-]*"' viewport-base.css \| sort -u` | **13** unique layout values |
| E4.5 | `grep -n '^### [0-9]*\. animate-' animation-library.md` | **24** headings |
| E4.6 | `grep -n '^## Entrance Animations' / '^## Emphasis Animations'` | #1–#20 / #21–#24 → **20 + 4** confirmed |
| E4.7 | `sed -n` on `animation-library.md` base/easing/delay/duration/reduced-motion blocks | Wildcard `[class*="animate-"]` base rule confirmed; reduced-motion block uses a universal `*` selector |
| E4.8 | Full read of all 24 animation definitions | Keyframe bodies captured verbatim for adaptation; `animate-counter-up` has **no** `@keyframes` |
| E4.9 | `cat scripts/package.json` | `pptxgenjs ^3.12.0` — the donor's only new runtime dependency |
| E4.10 | `shasum -a 256 LICENSE` | `e8aa250f23393942b2c952d0c45109926b1bffc6e5e9b3d6a3f09abe691bd7a9` — copied verbatim to `docs/donors/nextslide-skill/LICENSE` and verified byte-identical |
| E4.11 | Repository test-suite search | **The donor ships no test suite.** |

## E5 — Donor runtime probe (real artifacts)

Full command-by-command detail: `evidence/NEXTSLIDE_PROBE_RUNLOG.md`.

| # | Experiment | Result |
|---|---|---|
| E5.1 | Author a deck from `SKILL.md` for the synthetic topic *"Ocean Plastic Reduction: 2026 Strategy"* | 4 single-file HTML decks produced (Botanical, Corporate Pro, Corporate Pro fixed, Midnight Pro) |
| E5.2 | `node scripts/export-pptx.js <deck>.html <deck>.pptx` | 4 real `.pptx` produced, 88–130 KB each |
| E5.3 | Reopen each `.pptx` with **`python-pptx`** (Gomrey's own dependency, not the donor's tooling) | slides 6–9; shapes 23–29; **text shapes 23–28**; pictures 0–2 → **the donor's PPTX output is genuinely editable text** |
| E5.4 | Run the donor's `extract-pptx.py` unmodified on a pristine donor-generated PPTX | **CRASH** — `ValueError: shape is not a placeholder` at line 281 (`hasattr(shape,"placeholder_format")` → the property raises). Log committed. |
| E5.5 | Re-run after a minimal patch | `⚠ Slide 4, shape 1: tuple index out of range`; 9 slides, 26 elements, 2 images extracted. Log committed. |
| E5.6 | Render the `animate-counter-up` element in headless Chromium | `animationName: "none"` → the element is **permanently invisible** despite the JS updating its text to `73`. Screenshot committed. |
| E5.7 | Render a chart with only the CSS the documented pipeline inlines, then with the widget CSS applied | Two screenshots proving the donor's interactive-element CSS is **never inlined** by its own documented pipeline |
| E5.8 | Render the `Bento Grid` preset | Screenshot proving the preset advertises a bento layout that does not exist in the codebase |
| E5.9 | Apply 2+ style presets and 3+ layouts to the same content | 4 distinct decks, each with its own `.html` and `.pptx` |

## E6 — Live product reconnaissance

Full detail: `evidence/LIVE_PROBE_LOG.md`.

| # | Target | Result |
|---|---|---|
| E6.1 | `curl -sL -A "$UA" https://nextslide.ai/` | HTTP/2 **200**, 3 706 B, `num_redirects=0`, `server: cloudflare` |
| E6.2 | Inspect the rendered page | Title `NextSlide is joining OpenAI`; *"The NextSlide team is now at OpenAI, helping build ChatGPT."* — signed **Ahmed Beshry, Founder** |
| E6.3 | `/pricing` in a headless browser | **200 with the identical notice** → SPA catch-all; no pricing, docs, app or API exist |
| E6.4 | `/docs`, `/app`, `/blog`, `/features`, `/api`, `/sitemap.xml` | **403** — Cloudflare *"Performing security verification"* interstitial (Ray ID `a4e5814dd930c611`). **Not bypassed.** Not evidence that these paths exist. |
| E6.5 | `/robots.txt` | 404 |
| E6.6 | `GET https://api.github.com/search/repositories?q=nextslide+ai+presentation` | `total_count: 0` |
| E6.7 | `GET …/repos/NextSlide-AI/Nextslide.AI` | 200 but `size: 0`, `stars: 0`; `/contents/` → **404 "This repository is empty."** |
| E6.8 | `GET …/search/repositories?q=nextslide` | 31 hits — all different products (PPT viewer, voice controller, editor, etc.) plus 6 empty repos |
| E6.9 | npm `nextslide*` and `@nextslide/*` | No AI-presentation package, no scope |
| E6.10 | `curl -sL https://www.nextslide.io/` | 200; title *"Turn your phone into a powerpoint clicker"* → **unrelated product, not a donor** |
| E6.11 | `GET https://developers.gamma.app/llms.txt` + all 21 linked doc pages | Full official documentation set captured under `evidence/raw/gamma_docs/` |
| E6.12 | `GET https://mcp.gamma.app/mcp` (metadata) | `{"resource":"https://mcp.gamma.app","authorization_servers":["https://auth.gamma.app"],"scopes_supported":["generate","gamma:read"],"bearer_methods_supported":["header","body"]}` |
| E6.13 | `GET https://auth.gamma.app/.well-known/oauth-authorization-server` | authorize/token/**`registration_endpoint` `/oauth/register`** (RFC 7591 DCR), jwks, grants `[authorization_code, refresh_token]`, **`code_challenge_methods_supported:[S256]`**, `token_endpoint_auth_methods_supported:[none, client_secret_post, client_secret_basic]` |
| E6.14 | `GET https://public-api.gamma.app/...` (data endpoints) | **401 `{"message":"Invalid API key","statusCode":401}`** — no key, no bypass attempted |
| E6.15 | `GET https://api.github.com/users/gamma-app/repos?per_page=100` | 29 repos enumerated and classified (see E6.18) |
| E6.16 | `npm view @gamma-app/api @gamma-app/sdk gamma-app gammaapp` | `scope:gamma` → **0 results**; the three package names → **404** |
| E6.17 | n8n node package metadata | `gamma-app/n8n-nodes-gamma` — official, MIT, published to npm, pushed 2026-10-13 |
| E6.18 | Classify all 29 `gamma-app` repos | All are OSS forks of third-party libraries, integration nodes, QA tooling, opaque scratch, or binaries. **No product core.** Two substantive non-forks: `n8n-nodes-gamma` (MIT integration) and `import-grader-annotator` (internal QA tooling, not permissively licensed for product use). |

## E7 — Implementation and qualification

| # | Experiment | Result |
|---|---|---|
| E7.1 | Write `catalog.ts` + `stylesheet.ts` + `index.ts` | 24-animation catalog, namespaced, 2 activation modes, scoped reduced motion |
| E7.2 | `node --test tests/slide-animations.test.mjs` (first run) | **3 failures** — real defects found by the tests, not by inspection |
| E7.3 | Defect A — `counter-up` declared a keyframe name it never emitted | Fixed: `keyframeName` is `null` for controller-backed animations |
| E7.4 | Defect B — the stylesheet's declaration scanner flagged keyframe `from { … }` steps | Fixed the **test** (the stylesheet was valid); the scanner now strips `@keyframes` blocks before checking |
| E7.5 | Defect C (found by **reading the generated CSS**, not by a test) — `.gs-anim-counter-up { opacity: 0 }` with no keyframe to reveal it → **permanently invisible** | Fixed: controller-backed animations never hide; regression test added |
| E7.6 | Defect D — `--gs-ease-ease-in-out` naming stutter | Fixed by stripping the `ease-` prefix; regression test added |
| E7.7 | `node --test tests/slide-animations.test.mjs` | **28 pass / 0 fail** |
| E7.8 | Generate and visually inspect the stylesheet (472 lines) | Keyframes, element rules, gated activation block and reduced-motion block all correct |
| E7.9 | Full re-run of every gate on the candidate | All green: 48 / 1125 / 101, lint 0 errors, build OK, Electron OK, security/release/fixture gates OK |

## E8 — Failed and blocked experiments (recorded, not hidden)

| # | Experiment | Outcome |
|---|---|---|
| E8.1 | `webfetch https://api.github.com/repos/TheHalfMoon/Gomrey/issues/77` | **404** — the repository is private and `webfetch` is unauthenticated. Re-issued through `gh`, which is authenticated. |
| E8.2 | `timeout 60 <cmd>` | `timeout` is not present on macOS. Re-issued without it. |
| E8.3 | `OCR="node …/ocr.js"; $OCR …` | Shell quoting error — the variable expanded as a single word. Re-issued with `node "$OCR"`. |
| E8.4 | `jev ask --stdin` | `unexpected argument '--stdin'`; the correct form is `jev ask <path>` with a JSON object of questions. |
| E8.5 | `jev ask` with `"questions": [ … ]` (array) | `'questions' must be a non-empty JSON object of question id to question`. Corrected to an object. |
| E8.6 | Run `morluto/rea`'s analysis path | **Blocked** — no LLM provider key in the environment. Recorded as `REA_NOT_EXECUTED`; the framework was cloned and read, and REA was performed by direct source reading, executed runtime probes and live observation. |
| E8.7 | Run `graft build` | **Blocked** — same cause. Recorded as `GRAFT_NOT_EXECUTED`. |
| E8.8 | OCR semantic review | **Blocked** — `ocr auth status` → not signed in. Recorded as `OCR_NOT_EXECUTED`; **no substitute reviewer was used**, per `REVIEW_POLICY.md` §5. |
| E8.9 | Invoke Gamma MCP tools | **Blocked** — OAuth Bearer + RFC 7591 DCR, and redirect URIs must be pre-allowlisted by Gamma. |
| E8.10 | Call Gamma REST data endpoints | **Blocked** — 401, no API key. Not obtained; would exceed the zero-founder-cost rule. |
| E8.11 | Reach `nextslide.ai/{docs,app,…}` | **Blocked** — Cloudflare bot challenge. Not bypassed. |
| E8.12 | Playwright first launch | **Failed** — `Executable doesn't exist at …/ms-playwright/chromium_headless_shell-1248/…` (playwright 1.64.1 expects rev 1248, cache had 1243). Resolved with `npx playwright install chromium-headless-shell` (free download, no account). |
| E8.13 | Run the donor's `extract-pptx.py` on a pristine PPTX | **Failed** — `ValueError: shape is not a placeholder`. Log committed. |
| E8.14 | Commit the raw evidence directory | **Rejected by policy** — it contained 18 MB of `node_modules` and a 4 MB PNG. `node_modules` is gitignored; the PNG was dropped and the large captures were gzipped; a sha256 manifest (`evidence/RAW_ARTIFACT_MANIFEST.txt`) preserves provenance for every artifact, including the dropped one. |

## E9 — Zero-cost guarantee

| Resource | Spend |
|---|---|
| LLM provider calls (OpenAI / Anthropic / Gemini / Groq / DeepSeek / Minimax) | **0** — no key present in the environment |
| Hosted APIs (Gamma REST, Gamma MCP, OCR's ChatGPT backend) | **0** — none authenticated; none purchased |
| Product accounts (gamma.app, nextslide.ai, Gamma Cloud) | **0** — none created |
| Compute | Local only: 8 cores, 8 GiB RAM |
| Downloads | Free/open: donor repositories, Playwright's chromium-headless-shell from the public Microsoft CDN, `uv.lock`-pinned Python packages, `npm`-locked Node packages |

No funded resource was consumed at any point.
