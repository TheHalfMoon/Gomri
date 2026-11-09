# Independent Goldfish review — Design Critic

**Run:** new OpenCode plan session, model `opencode/deepseek-v4.1-flash-free`, fresh context, attached Elephant draft, no source code opened. **Actual independent model response; not the complete official EGM plugin orchestrator.**

## Goldfish Design Critique — Gomri EGM Draft (2026-11-09)

Reviewed as text only; no source opened. Findings cite plan sections.

**F1 — §5 Concurrency: compare-and-swap is named, not specified (blocking).**
"Compares `baseRevision`, `proposalHash` … at commit time" describes a check, not an atomic write. Nothing says the hash is recomputed server-side from the stored proposal (a client-supplied `proposalHash` is worthless), that `targetElementIds` is derived rather than trusted, or that revision check and mutation are one conditional write. *Smallest test:* two commits on the same `baseRevision` apply exactly one and return 409 for the other; a commit with a tampered `proposalHash` returns 400 and writes nothing. *Fix:* one sentence: server recomputes hash and target set, then performs a single conditional update keyed on `(artifact_id, revision)`.

**F2 — §5/§9 Authorization: `actor` is compared, never authenticated (blocking).**
The contract lists `actor` and `workspaceId` as comparison inputs but never binds them to the server session; ArtifactRevision v1's `author_principal_id`/`tenant_id` can be spoofed if taken from the request. §9 revalidates "at commit and export," but export is asynchronous (`export_task_service.py`), so membership can be revoked between enqueue and delivery. *Smallest test:* commit with a forged `author_principal_id` → 403 and no revision row; revoke role after export enqueue → task fails closed, no artifact served.

**F3 — §7 Phase 2 + §10 Q2 Autosave silently bypasses the commit gate (blocking).**
The plan admits autosave's conflict behavior is unverified but still asserts §5 conflict safety. `useAutoSave.tsx` is a second write path; if it writes canonical state directly, last-write-wins returns through the back door that §9 forbids. *Smallest test:* hold a proposal open, let autosave fire with stale `baseRevision` → write rejected or explicitly merged, never silently overwriting. *Fix:* route autosave through the same CAS, or freeze autosave while a proposal is pending.

**F4 — §7 Phase 2 Gate: "Undo restores exact previous canonical revision" contradicts append-only revision semantics.**
ArtifactRevision appears immutable and monotonic (§2). Undo cannot restore revision *N* without rewriting history; if it appends rev *N+2*, the digest equals *N* but clients holding `baseRevision N+1` must conflict. The plan never chooses. *Smallest test:* edit → rev *N+1*; undo → assert new rev *N+2* with `content_digest` equal to rev *N*, and a stale `baseRevision N+1` client receives 409, not silent overwrite.

**F5 — §7 Phase 1 precedes the safety machinery it depends on (major).**
G3 requires no silent loss during layout swaps, but Phase 1 lands SmartLayout before Phase 2's commit/authorization service. Phase 1 swaps therefore run through the existing editor/autosave path, unprotected. *Smallest test:* with Phase 2 disabled, apply a layout that drops a citation — must fail closed with prior state retained; if it cannot pass, Gate P1 is invalid as written. *Fix:* make Phase 1 apply its `{candidate, diagnostics, lossReceipt}` through proposal→commit from day one, even if the commit is local-only.

**F6 — §3 G3/G5 vs §7 Phase 3: the 95% retention target licenses the exact loss G3 forbids (major).**
"At least 95% supported native elements retained" permits 5% silent loss. Loss is only acceptable if individually receipted against G1's frozen per-fixture loss inventory, but `lossReceipt` has no schema, version, or completeness check. *Smallest test:* a 100-element deck that drops 3 must fail even at 97%, unless each dropped element ID appears in the receipt.

**F7 — §7 Phase 3: "safe zip reader" and OOXML identity roundtrip are unspecified (major).**
No limits (zip-slip, zip-bomb, entity expansion), and chart/table identity across export→reimport depends on shape IDs the exporter may regenerate, so "reimport" may prove nothing without a declared ID mapping. *Smallest test:* hostile archive rejected with typed error; a chart reimported maps to the same canonical `component_id`/series, not merely similar pixels.

**Verdict: CONDITIONAL.** Phase 0 evidence work and the doc artifacts may proceed. Block Phase 1+ writes until F1–F3 and F5 are resolved in the plan text; F4, F6, F7 before Gate P3. No API is claimed here beyond what the draft itself states as proposed.
