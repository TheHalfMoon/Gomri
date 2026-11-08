# SOURCES — Source Registry

**Mission:** Issue #77 — deep NextSlide + Gamma REA and source-first capability migration into Gomrey.
**Registry date (UTC):** 2026-10-22
**Gomrey target revision:** `5f299a7a6174ad3a1180f827778db5f4400a4d71` (main, `Merge pull request #76 from TheHalfMoon/p09/exit-closeout`)
**Registry owner:** MiniMax (autonomous REA + integration lead)

---

## 0. Authorization record (founder attestation)

The founder states that the owners of NextSlide and Gamma have granted permission for deep reverse
engineering and source reuse for Gomrey. This is recorded as a **founder attestation**, not as
independent inspection of the private agreements. The permission documents are held privately by
the founder and are not reproduced here.

```
FOUNDER_REA_AUTHORIZATION=YES_CONFIRMED_BY_FOUNDER
FOUNDER_SOURCE_COPY_ADAPT_REBRAND_AUTHORIZATION=YES_CONFIRMED_BY_FOUNDER
CONFIDENTIAL_PERMISSION_DOCUMENTS=HELD_PRIVATELY_BY_FOUNDER
FOUNDER_IMPOSED_REA_DEPTH_LIMIT=NONE
FOUNDER_IMPOSED_AUTHORIZED_SOURCE_TRANSPLANT_SCOPE_LIMIT=NONE
```

**Availability is a separate technical fact.** An authorization does not itself provide a
repository URL, archive, credentials, binaries, or source bytes. This registry records, for each
donor, what was *actually obtained* and what was *not*. Nothing in this mission claims inspection
of, or transplantation from, any file that was not actually retrieved.

### Standing boundaries actually applied in this mission

| Boundary | Status | Evidence |
|---|---|---|
| Source bytes actually obtained | tracked per donor below | `git rev-parse HEAD` + blob ids |
| Third-party assets inside a donor | assessed separately from code | §5 asset-rights audit |
| Gamma internal source | **NOT OBTAINED** — no archive/repository/credentials supplied | §3 |
| Login/paywall/access-control circumvention | **not attempted** | `LIVE_PROBE_LOG.md` |
| Secrets / user data | **not collected** | `scripts/scan-secrets.mjs` → OK |
| Funded/external services | **none purchased** | §6 tooling matrix |

---

## 1. Donor registry — NextSlide identities (kept strictly separate)

Issue #77 §A requires that these three be distinguished. `nextslide.io` is an **unrelated
presentation clicker** and is not a donor.

### 1.1 `0xRafie/nextslide` — the MIT OpenCode slide skill — **PRIMARY CODE DONOR**

| Field | Value |
|---|---|
| Repository | `https://github.com/0xRafie/nextslide` |
| Exact revision | `90a46f933b3056d27460400c915ef268a9ec3f56` |
| Commit subject | `README: update GitHub username to 0xRafie` |
| Public license | **MIT** |
| Copyright | `Copyright (c) 2026 Danish Rafie Ekaputra` |
| LICENSE blob id | `1f0239b87b6b390ade2cb7f8c4180e6c02f457d4` |
| LICENSE sha256 | `e8aa250f23393942b2c952d0c45109926b1bffc6e5e9b3d6a3f09abe691bd7a9` |
| Access method | `gh repo clone 0xRafie/nextslide` (public) |
| Availability | **FULL SOURCE OBTAINED** |
| Adoption mode (planned) | `COPY_BOUNDED` / `ADAPT` behind Gomrey-owned interfaces |

**Exact file inventory at `90a46f9` (git blob ids):**

| Blob id | Path | Role |
|---|---|---|
| `bc2f582421cd82470f78f8e16665fdc2f16a10eb` | `README.md` | skill entrypoint docs |
| `0c3bcc2f5bbb9ab7bd0114a792944c0e4b0f98d1` | `SKILL.md` | the skill contract / generation workflow |
| `0e18484ae76bc983654255ce053a8bf1334c044c` | `STYLE_PRESETS.md` | style preset definitions |
| `a3484b2ae4c13c7a2139e2ed2588f5e58344902c` | `animation-library.md` | animation library |
| `89cf7f907668a441fad8102d6a4984fa7b013b45` | `html-template.md` | single-file HTML engine spec |
| `505ae09f37e576b2ee9667d476c93a0a3c07b595` | `typography-system.md` | typography rules |
| `688ec8211dbf5838275de71df1e040919ac570b3` | `interactive-elements.md` | interactive widgets |
| `5905fdf4f764e87792953059d227ca76aa083969` | `presenter-mode.md` | presenter mode |
| `dce13d8d52a637a074bb33ba232e26c2690253fe` | `viewport-base.css` | base stylesheet |
| `81062d4268656d0502ef59e89f9b02dae75abf73` | `scripts/export-pptx.js` | HTML → editable PPTX (PptxGenJS) |
| `e3d97b1139dfbff6db905dced2c81154aa889ce8` | `scripts/extract-pptx.py` | PPTX → structured extraction (python-pptx) |
| `57cd574dd00be549c78ad2a70631e6ff89cc50df` | `scripts/package.json` | script deps (`pptxgenjs ^3.12.0`) |
| `e6346adca04353eea36ae16a06de08f21e0dea76` | `.gitignore` | — |

**Transitive/embedded dependencies of the donor scripts:**

| Dependency | Version | License | Notes |
|---|---|---|---|
| `pptxgenjs` | `^3.12.0` | MIT | external npm dep — **not** vendored into the donor tree; a Go/Node runtime dep |
| `python-pptx` | unpinned in script header | MIT | external pip dep; **already a Gomrey FastAPI dependency** (`python-pptx>=1.0.2`) |
| `Pillow` | unpinned in script header | MIT-CMU | external pip dep; **already a Gomrey FastAPI dependency** (`pillow>=12.2.0`) |

> **Note on overlap:** `python-pptx` and `Pillow` are already admitted Gomrey dependencies. Only
> `pptxgenjs` would be a *new* runtime dependency, and only if the donor's exporter is adopted.

### 1.2 NextSlide.ai — commercial product — **OBSERVATION-ONLY DONOR**

| Field | Value |
|---|---|
| Product | `https://nextslide.ai/` |
| Nature | Commercial AI-presentation product; team reportedly joined OpenAI |
| Public source | **none found** (no repo, SDK or npm package attributable to this product) |
| Availability | **SOURCE_NOT_AVAILABLE** — no archive, repository, credentials or binaries supplied |
| Evidence class | `OBSERVED_UI` / `OFFICIAL_DOCUMENTATION` only |
| Adoption mode | `REFERENCE` (architecture/UX) — no code to copy |

### 1.3 nextslide.io — **NOT A DONOR** (disambiguation control)

Unrelated commercial presentation *clicker / remote*. Verified and recorded in
`NEXT_SLIDE_IO_DISAMBIGUATION.md` purely so it is never confused with 1.1 or 1.2.

---

## 2. Donor registry — Gamma

| Field | Value |
|---|---|
| Product | `https://gamma.app/` |
| Developer docs | `https://developers.gamma.app/` |
| Nature | Commercial creation platform (presentations, documents, websites, images, social) |
| Internal source | **NOT OBTAINED** |
| Availability | **SOURCE_NOT_AVAILABLE** |
| Reason | No authorized source snapshot, repository, archive or credentials were supplied to this repository. A public `gamma.app` URL is **not** a source archive (`docs/SOURCE_LEDGER.md` §2, Gamma gate). |
| Adoption mode | `EQUIVALENT_IMPLEMENTED_AND_QUALIFIED` via permitted donors or original Gomrey code |
| Evidence class | `OFFICIAL_DOCUMENTATION` + `API_RESPONSE` + `OBSERVED_UI` |

> The founder's authorization for Gamma source reuse **remains live and unconsumed**. If an exact
> authorized Gamma snapshot is later supplied, `COPY_BOUNDED`/`ADAPT` becomes available under
> `docs/SOURCE_LEDGER.md` §2 and §9 without re-litigating authorization. Until then, the Gamma wave
> proceeds as **qualified equivalent implementation** and never claims parity.

---

## 3. Supporting tool sources (analysis instruments, not donors)

| Tool | Revision / version | License | Use |
|---|---|---|---|
| `morluto/rea` | `4a4bbab3c337701febeb6b532ace49041c4876e0` (`rea-agents` v6.7.0) | MIT | REA framework; **cloned and inspected**; see §6 for why its LLM-backed analysis path was not executed |
| `graft` | 0.21.1 | — | codebase context graph (Gomrey) |
| `jev` (TypeSafe Jev) | 2026.919.0, model `jev-1.14.0` | — | mandatory build review (§6) |
| `@alibaba-group/open-code-review` | 1.13.2 | — | mandatory build review (§6) |

## 3a. Gamma-adjacent code donor — `gamma-app/n8n-nodes-gamma` (MIT, official)

A Gamma-owned public repository was found during the code-availability audit. It is **not** the
Gamma product core, but it is an *official, MIT-licensed* artifact that encodes Gamma's **public
REST contract** and ships a **working test suite**.

| Field | Value |
|---|---|
| Repository | `https://github.com/gamma-app/n8n-nodes-gamma` |
| Exact revision | `5d0b466a9ae4be994a722577daa0a761cb28cfaf` (`fix: n8n review fixes, release 0.6.1 (#16)`) |
| Public license | **MIT** — `Copyright (c) 2025 Gamma` |
| Access method | `gh repo clone gamma-app/n8n-nodes-gamma` (public) |
| Availability | **FULL SOURCE OBTAINED** |
| Adoption mode (planned) | `COPY_BOUNDED` / `ADAPT` — Gamma REST contract only |

**What it contains (verified by direct read):**

| Path | Content |
|---|---|
| `nodes/Gamma/api.ts` (23 lines) | `BASE_URL = 'https://public-api.gamma.app'`; the required `User-Agent` policy and why it is set |
| `nodes/Gamma/apiEnums.ts` (155 lines) | **38 image models with per-image credit costs**; **74+ output languages** including `ar`, `ar-sa`, `ja`, `ja-da`; `EXPORT_AS_VALUES = ["pdf","png","pptx"]` |
| `nodes/Gamma/actions/**` | Concrete request shapes for generation, edit, export, folders, comments, user and list/search |
| `test/` (12 files) | A real test suite: `enums.test.js`, `multipage.test.js`, `routing.test.js`, `structure.test.js`, `presend.test.js`, `user-agent.test.js`, `gamma-lifecycle.test.js` and others |

**Why this materially changes the Gamma wave:** until this repository was found, the Gamma
capability wave had **zero** admissible Gamma code and every Gamma capability would have been
`BLOCKED_SOURCE`. This artifact is an official, permissively-licensed statement of Gamma's
*external* contract. It does **not** contain the editor, the card model, the theme system, the
import grader or the export renderer — those remain `SOURCE_NOT_AVAILABLE`. It makes a
**Gamma-compatible API adapter** possible, and it supplies exact, testable enum/credit data.

**Design signal carried forward:** Gamma's output-language identifiers pair a base locale with an
optional **register** (`ar` / `ar-sa`, `ja` / `ja-da`, `en` / `en-gb` / `en-in`). This is a
language+register model rather than a bare ISO-639 list, and it is directly relevant to Gomrey's
Arabic-first requirement.

> **Asset-rights note.** This donor bundles a `gamma.svg` / `gamma.dark.svg` icon pair. Gamma
> trademarks are **not** covered by the MIT grant. Only the **API contract** may be adopted; the
> artwork and the Gamma name may not be reused.

---

## 4. Existing Gomrey donor context (unchanged by this mission)

Recorded from `docs/SOURCE_LEDGER.md` §2 and preserved verbatim — P00–P09 are **preserved, not
redone**.

| Donor | Revision | Mode | Note |
|---|---|---|---|
| `presenton/presenton` | `e158a014cc1e29da0a27fe539db08dcbcea5c69d` | `COPY_FULL_BASE` | working foundation; NOTICE blob `ba5df534c4549ed7459a34667a506baa5cbd5fea` (1,274,338 bytes) must be preserved |
| RAGFlow / Open Notebook / SurfSense / Onyx CE | see ledger §3 | `COPY_BOUNDED`/`ADAPT`/`REFERENCE` | not touched by this mission |
| Docling / PaddleOCR / MinerU / Crawl4AI | see ledger §4 | `DEPEND`/`WORKER` | not touched by this mission |

---

## 5. Asset-rights audit (independent of code permission)

`docs/SOURCE_LEDGER.md` §7 requires that code permission **not** be read as asset permission.

| Asset class | In `0xRafie/nextslide` | Verdict |
|---|---|---|
| Source code | MIT, © 2026 Danish Rafie Ekaputra | **Admissible** with notice preservation |
| Fonts | **none bundled** — the donor specifies system/web font stacks by name | Admissible as *references*; no font binaries to redistribute |
| Images / icons / illustrations | none bundled | No asset rights issue |
| Templates | none bundled (templates are described as CSS/style presets) | No asset rights issue |
| Brand kits / trademarks | none | No asset rights issue |
| Model weights / datasets | none | No model-pack admission needed |

**Consequence:** admitting donor *code* creates a MIT attribution obligation but **no** asset
redistribution obligation. This is materially simpler than a donor that ships fonts or stock
imagery, and it removes the main hidden-rights risk from the code wave.

---

## 6. Tooling execution matrix (evidence-backed, non-fabricated)

`docs/REVIEW_POLICY.md` §4/§5 mandate honest `NOT_EXECUTED` recording rather than substitution.

| Tool | Executed? | Evidence | Verdict |
|---|---|---|---|
| **TypeSafe Jev** | **YES — real execution** | `jev 2026.919.0`, model `jev-1.14.0`; live `noul` → `{"noul":0.85,"type":"noul"}`; live `choice` → `{"choice":"adapt","confidence":0.38,"probabilities":{"adapt":0.59,"copy":0.25,"reference":0.16}}` | **AVAILABLE** — satisfies `REVIEW_POLICY` §1.2 |
| **Alibaba OCR — deterministic selection/rules** | **YES — real execution** | `ocr delegate preview` (workspace mode, exact file/range set), `ocr delegate rule <path>`, `ocr rules check <path>`; all LLM-free by design | **AVAILABLE** — satisfies `REVIEW_POLICY` §1.1 deterministic half |
| **Alibaba OCR — semantic LLM review** | **NO** | `ocr auth status` → `Not signed in, run ocr auth login --provider chatgpt.` | **`OCR_NOT_EXECUTED`** — exact blocker recorded; no substitute reviewer used (policy §5) |
| **Graft** | binary present (0.21.1) | LLM-backed graph build | **`GRAFT_NOT_EXECUTED`** — no funded provider configured in this environment |
| **morluto/rea** | source cloned @ `4a4bbab` | REA framework; requires an LLM provider for its analysis path | **`REA_NOT_EXECUTED`** — no funded LLM provider; source-level + live-observation REA performed instead (see `EXPERIMENTS.md`) |
| **PStack** | not present on PATH, no repository identified | — | **`PSTACK_NOT_EXECUTED`** — unavailable; not fabricated |
| **Alibaba OCR via ChatGPT sign-in** | not attempted | Requires an external account | Not used — external account would exceed the zero-founder-cost rule |

> **Provenance / integrity note:** a grant to a product owner does not extend to independently owned
> third-party code inside that product. Only the MIT-licensed `0xRafie/nextslide` tree above is
> code-admissible. Gamma and NextSlide.ai contribute **behavior and architecture only**.

---

## 7. Reproducibility

| Artifact | How to reproduce |
|---|---|
| Donor source | `gh repo clone 0xRafie/nextslide && cd nextslide && git checkout 90a46f933b3056d27460400c915ef268a9ec3f56` |
| REA framework | `gh repo clone morluto/rea && cd rea && git checkout 4a4bbab3c337701febeb6b532ace49041c4876e0` |
| Gomrey baseline | `gh repo clone TheHalfMoon/Gomrey && cd Gomrey && git checkout 5f299a7a6174ad3a1180f827778db5f4400a4d71` |
| Baseline test runs | `npm test` (root) · `cd servers/fastapi && uv sync --locked --dev && uv run --locked python -m pytest -q` |
