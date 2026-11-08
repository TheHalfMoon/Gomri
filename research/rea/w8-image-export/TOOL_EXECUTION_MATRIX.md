# W8 — Tool Execution Matrix

Every tool that was inspected for the W8 grain, with its actual state on this machine. A
`NOT_EXECUTED` row is not a pass. Local execution and remote execution are recorded separately.

**Grain:** W8 — image export (PNG / JPEG / WebP)
**Branch:** `feature/rea/w8-image-export`
**Base:** `main@5f299a7a6174ad3a1180f827778db5f4400a4d71`
**Execution host:** macOS 14 (darwin/arm64), working directory `/Users/abdulazizalsh/work/Gomrey`
**Recorded (UTC):** 2026-10-22

---

## 1. Required stack

| # | Tool | Installed? | Version / revision | Local or remote | Executed? | Command actually run | Result |
|---|---|---|---|---|---|---|---|
| 1 | **D1 (founder-selected local model/runtime)** | **NO** | — | — | **NO** | `which d1 D1 dm1`; `ollama list`; `llama-cli --help`; `python3 -c "import llama_cpp, transformers, torch, vllm, mlx"` | **`D1_LOCAL_NOT_EXECUTED`.** No D1 binary on `PATH`, no `~/.d1`, no Ollama install, no `llama-cpp`/`transformers`/`torch`/`vllm`/`mlx` in any Python environment on this host, and no listener on any local model port (`lsof -nP -iTCP -sTCP:LISTEN` shows only Postgres, opencode, node dev servers and macOS system agents). The blocker is the **absence of the D1 runtime itself**, not a configuration error. No remote fallback was used and no other model was labelled D1. |
| 2 | **PStack** | **YES** | `finografic/pstack` via `npx skills@latest`; installed skills `principles`, `architect`, `blast-radius`, `technical-writing`, `show-me-your-work`, `how`; pinned in `skills-lock.json` with per-skill `computedHash` | local (skill instruction files, executed as instructions) | **YES** | `npx -y skills@latest add https://github.com/finografic/pstack --skill principles --skill architect --skill blast-radius --skill technical-writing --skill show-me-your-work --skill how -y` | Installed project-scoped into `.agents/skills/`. `principles` (Boundary Discipline, Type System Discipline, Laziness Protocol) and `architect` shaped the design; `blast-radius` drove the regression sweep; `technical-writing` shaped the evidence documents. Skill instructions were read and applied — PStack is an instruction library, not an inference service, so there is no separate provider or model to record. |
| 3 | **Matt Pocock engineering skills** | **YES** | `mattpocock/skills` via `npx skills@latest`; installed `tdd`, `code-review`, `diagnosing-bugs`; pinned in `skills-lock.json` | local (skill instruction files) | **YES** | `npx -y skills@latest add mattpocock/skills --skill tdd --skill code-review --skill diagnosing-bugs -y` | Installed project-scoped. `tdd` owns the red→green loop for this grain; `code-review` and `diagnosing-bugs` own the review and root-cause passes. PStack's own `tdd` skill was deliberately **not** installed, so there is exactly one TDD controller. |
| 4 | **Alibaba OpenCodeReview — deterministic selection and rules** | **YES** | `open-code-review v1.12.13 (fabbdb29) darwin/arm64`, built 2026-10-08 | local | **YES** | see `REVIEW_RECORD.md` §2 | Deterministic file selection and rule resolution executed locally and recorded. |
| 5 | **Alibaba OpenCodeReview — semantic LLM review** | **YES** (CLI) | configured provider `mac-ollama` → `http://127.0.0.1:11434/v1`, model `qwen2.5-coder:3b` | would be **local** if reachable | **NO** | `ocr llm test` → `dial tcp 127.0.0.1:11434: connect: connection refused`; `curl -s http://127.0.0.1:11434/v1/models` → empty; `lsof -nP -iTCP -sTCP:LISTEN | grep 11434` → no listener; `which ollama` → not found; `/Applications/Ollama.app` → absent | **`OCR_LOCAL_SEMANTIC_NOT_EXECUTED`.** The local Ollama provider the OCR configuration points at is not running and Ollama is not installed on this host. The repository's `ocr-local-free` wrapper independently refuses to run for the same reason (`BLOCKED: local Ollama is not reachable. No cloud fallback.`). No remote provider was substituted, no paid service was activated, and the deterministic coverage from row 4 was preserved. |
| 6 | **Real end-to-end testing** | **YES** | Chromium from the local Puppeteer cache (`~/.cache/puppeteer/chrome/mac_arm-155.0.8059.84`); Node `v26.0.0`; Python `3.11.15`; `puppeteer 25.15.0`; `@presenton/export-core 1.0.34` | local | **YES** | `servers/fastapi/.venv/bin/python -m pytest tests/integration/test_image_export_end_to_end.py -q` → `7 passed in 46.56s` | A real browser painted a real 4-slide deck (Arabic RTL and mixed script included) and the produced bytes were asserted. Not a mocked test. |
| 7 | **GitHub Actions CI** | configured | `test-all.yml` | remote | **NO** | `gh run list` / `gh pr checks` | **`CI_NOT_EXECUTED`** — the account-level billing/spending condition recorded on PR #78 refuses every job at the runner queue before any step runs. This is the same pre-existing condition; it is not attributable to W8. Every deterministic gate in `W8_IMAGE_EXPORT_EVIDENCE.md` §3 was executed locally on the exact candidate instead. **No CI result is claimed.** |

---

## 2. Supporting toolchain actually used

| Tool | Version | Use |
|---|---|---|
| `@presenton/export-core` | 1.0.34 (open-source edition) | The adopted donor renderer. PNG-per-slide ZIP output. |
| `pillow` | 12.2.0 | Image re-encoding, resizing, dimension probing, background flattening. Already a FastAPI dependency. |
| `sharp` | 0.35.3 | Transitive dependency of the donor package. Not imported by Gomrey code. |
| `jszip` | 3.10.2 | Transitive dependency of the donor package. Not imported by Gomrey code. |
| `pytest` | 9.0.3 | FastAPI unit and end-to-end suites. |
| `node --test` | Node v26.0.0 | Next.js and repository-tooling suites. |
| `shasum` | macOS 14 | Evidence manifest checksums. |

---

## 3. Skill installation footprint and audit

Both skill families were installed **project-scoped** into `.agents/skills/` (the repository
gitignores `.agents` and `skills-lock.json` by existing policy, so the install is local to this
checkout and is not committed; the pinned revisions are recorded here so the install is
reproducible).

| Family | Upstream | Pinned revision | Install command | Selected skills |
|---|---|---|---|---|
| PStack | `https://github.com/finografic/pstack` | `629dc5ea1c816031125231ca1c647afbc57d2e63` | `npx -y skills@latest add https://github.com/finografic/pstack --skill principles --skill architect --skill blast-radius --skill technical-writing --skill show-me-your-work --skill how -y` | `principles`, `architect`, `blast-radius`, `technical-writing`, `show-me-your-work`, `how` |
| Matt Pocock | `https://github.com/mattpocock/skills` | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | `npx -y skills@latest add mattpocock/skills --skill tdd --skill code-review --skill diagnosing-bugs -y` | `tdd`, `code-review`, `diagnosing-bugs` |

**Role assignment, so no two skills drive the same decision:**

| Concern | Owner |
|---|---|
| Design principles, boundary discipline, type discipline, diff sizing | PStack `principles` + `architect` |
| Change-impact sweep | PStack `blast-radius` |
| Documentation, evidence records, PR text | PStack `technical-writing` |
| Test-first loop | Matt Pocock `tdd` (PStack's own `tdd` was **not** installed) |
| Code review and root-cause passes | Matt Pocock `code-review` + `diagnosing-bugs` |

**File audit before use.** The installed trees contain 46 files. Two are executable shell scripts:

| Script | Purpose | Executed? | Finding |
|---|---|---|---|
| `.agents/skills/show-me-your-work/scripts/log.sh` | Appends a TSV decision-log row | **No** | Benign. It sanitises tabs/newlines and prefixes cells that start with `=`, `+`, `-`, `@` so attacker-controlled text cannot become spreadsheet formula execution. |
| `.agents/skills/diagnosing-bugs/scripts/hitl-loop.template.sh` | Interactive human-in-the-loop template | **No** | Benign. It only reads lines from the operator's terminal and prints `KEY=VALUE` pairs. |

Neither script was executed for this grain, and neither is referenced by the committed Gomrey
source. No skill installed a hook or an automatic execution path.

---

## 4. Cost and side effects

| Check | Result |
|---|---|
| Paid API or hosted inference used | **No** |
| Cloud service activated | **No** |
| Network access to a third-party model | **No** |
| Credentials or secrets read or recorded | **No** |
| Browser downloaded by the test | **No** — the test uses the Chromium already in the local Puppeteer cache and skips when it is absent |
| Product account created or purchased | **No** |
| Files written outside the repository | Only the local test scratch directories under the system temporary directory, removed by the fixtures |
