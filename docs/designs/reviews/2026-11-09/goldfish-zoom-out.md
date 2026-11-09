# Independent Goldfish review — Zoom Out

**Run:** isolated OpenCode plan session, model `opencode/deepseek-v4.1-flash-free`, fresh context, attached Elephant draft only. **Status:** actual model response; not the official EGM plugin orchestrator. Reviewer did not access code and explicitly requests source verification.

**Zoom-Out / Skeptical Architect — Gomri EGM Design Draft**

**1. §7 Phase 2 + §5 "Concurrency" + §10 Q2 — overengineered commit service on an uninspected substrate.**
The plan specifies a new `slide_edit_transaction.py` carrying `baseRevision`, `operationId`, `proposalHash`, `targetElementIds`, actor revalidation and idempotency, while §5 concedes "actual endpoint paths and handler signatures must be discovered" and Q2 admits auto-save conflict semantics are unknown. The single hardest component is designed before its foundation is observed. *Fix:* make Phase 0 deliver a one-page write-path trace of `useAutoSave.tsx`/`autoSaveDiff.ts` and the existing ArtifactRevision flow; Phase 2 must reuse document-grain revision CAS, adding slide-grain transactions only against a failing test.

**2. §7 Phase 1, §2 DesignIR bullet, §10 Q1 — compiler pre-decided ahead of seam proof.**
Four new files (`types.ts`, `constraints.ts`, `compile.ts`, fixture suite) assume a "versioned, small typed metadata envelope" can carry semantic roles, but no envelope schema, v1 field mapping, or `additionalProperties:false` migration behavior is given. §10 Q1 explicitly leaves open whether one helper would suffice — an open question should not be answered by shipping a library. *Fix:* run a single `headline-hero` spike inside an existing file behind a flag; publish the envelope schema and v1 mapping, then choose compiler vs helper.

**3. §3 G1, §7 Phase 4, Gate P4 — test and format breadth before a proven slice.**
30 fixtures, 30 prompts, and 4 aspect ratios (120 variants) are committed before one end-to-end journey passes, and Phase 4 already specs new files, tests and a gate for a post-P3 feature. This is scope inflation disguised as rigor. *Fix:* 8 fixtures (one each: Arabic, chart, table, citation-heavy, long title, etc.) and 16:9 only to close P3; demote P4 to an unspecced backlog.

**4. §2 evidence bullets vs §10 Q7; PR #88 dependency.**
"Existing code paths checked on main" is file-path existence, not behavior; Q7 concedes reviewers may be certifying interfaces "only guessed from filenames." PR #88 is declared a blocking baseline yet its CI/E2E are "not verified," and Phases 1–3 repeatedly reference files that live only in that PR — with no Branch B if it fails. *Fix:* Phase 0 must publish a read-only export/symbol inventory (signatures, props, test names) and state the fallback: build on main 5f299a7 with reduced P1 scope.

**5. §3 benchmark block + §6 exporter row + Phase 3 — uncalibrated targets and a rights-dependent gate.**
"60% blind designer preference," "98% no clipping," "95% native retention" have no baseline measurement, panel size, sampling method or power calculation. Phase 3 also benchmarks against Beautiful.ai's PptxGenJS fork while §2 states legal use "still requires exact accessible source and third-party notices/assets checks" — a release gate resting on an unresolved rights question. *Fix:* record current Gomri output metrics first, derive thresholds as baseline-plus-margin, defer preference to a documented pilot, and make upstream PptxGenJS plus license review a prerequisite rather than a comparison target.

**Verdict: CONDITIONAL.** The authority model (one Konva canvas), no-loss receipts and fail-closed semantics are sound. But Phases 1–2 authorize implementation grain against seams the document itself admits are unseen, and the fixture/format scope exceeds the stated north-star journey. Authorize Phase 0 only; re-review after the write-path trace, symbol inventory and envelope schema exist.
