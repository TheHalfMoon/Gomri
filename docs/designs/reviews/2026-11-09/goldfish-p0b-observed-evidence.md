# Evidence record: independent Goldfish on ACTUAL P0b results

**Method:** Fresh OpenCode plan session using free-labelled opencode/deepseek-v4.1-flash-free, reviewing only the three attached source/evidence files. No tool/code execution by reviewer, not official complete EGM orchestrator. Input: P0b test ledger, P0b isolation contract and P0a route map. Reviewer did not inspect raw test process logs; its verdict is bounded to supplied evidence.

# Independent Goldfish Review — Gomri P0b Actual Evidence

**Scope:** only the three supplied artifacts (execution ledger, isolation contract, P0a route map). No private code access, no tools, no external sources, no test execution. This is a readiness judgment on the evidence as written, not an official EGM certification.

## 1. Seven targeted Node/PPTX groups — **GO (bounded)**

The ledger records 61/61 passing tests at exact candidate SHA `d4362c6…`, run from a detached clone, with per-file SHA256, exit codes and receipts:

| Group | Tests |
|---|---:|
| A01 contracts | 9 |
| A02 template converters | 4 |
| A03 main metadata | 9 |
| A04 nextjs autosave | 3 |
| A05 template-v2 geometry | 3 |
| A06 Arabic/RTL | 18 (green on retry) |
| A07 native PPTX roundtrip | 15 |
| **Total** | **61** |

GO applies **only** to these seven groups. Two qualifications are part of the verdict, not footnotes:

- A06 first ran 18 setup failures from an unresolved KaTeX bundle dependency, then passed after ad-hoc copying of pre-installed esbuild/@esbuild/win32-x64/katex. That is a scratch-environment defect, not a product failure — but it shows dependency completeness was not preflight-proven. Both receipts must be retained.
- The egress guard was a Node-level `net.Socket.connect`/`fetch` hook plus dummy proxy, explicitly **not** an OS firewall. It is adequate only for these reviewed tests.

## 2. The 61 passes vs. the measured losses

A07's 15/15 PASS is a **passing-expectations harness**, not native semantic preservation. The ledger states the expected behaviors include:

1. Speaker notes are **written into PPTX but not restored by PPTX→JSON reimport**.
2. Bullets survive only as **literal text, not native bullet structures**.

So "15/15" measures that the pipeline reproduces its own documented losses; it does not measure editable-PowerPoint fidelity. The bundled ZIP reader is a narrow central-directory inspector, not an established safe parser for untrusted Office files. Pixel render, PowerPoint desktop editing and cross-owner export authorization remain unrun. These are P3-scoped limitations and must not be reclassified as a pass or a waived "known issue" for canonical writes.

## 3. Overall P0b completion — **CONDITIONAL / INCOMPLETE**

Group A is partial (selected scripts only; root `npm test`, full Next.js suite and production build NOT RUN). Group B (FastAPI pytest), Group C (safety negatives) and Group D (Windows browser/E2E) are BLOCKED or NOT RUN. Exact-head CI and independent code review are NOT VERIFIED. No P0b overall GO exists, and no full-orchestrator EGM run has occurred.

## 4. P1 SmartLayout preview — **NO-GO**

The contract makes P1 contingent on P0b approval and on a separate scoped preview approval, with "no layout commits until P2 write-safety passes." Neither condition is met. Notes/bullet fidelity also remains unqualified, which directly affects preview-to-export trust.

## 5. P2 production agent writes — **NO-GO**

CAS is **not verified**: no request revision field and no observed slide revision column; concurrency tests are blocked. The P0a map confirms real middleware and ORM owner-SELECT protections exist, but the owner filter is skipped when `owner_id` is None or when execution options bypass it, and `DISABLE_AUTH` desktop mode is single-user only. No foreign-owner PATCH has been executed. No production write is authorized.

## Blocking requirements (six)

1. **Isolated backend sandbox:** disposable DB/schema, two synthetic owners (A/B), isolated storage/queue/ports, auth enabled, test-scoped egress block, teardown receipts.
2. **Real cross-owner PATCH negative:** A PATCHes B's slide through actual `SessionAuthMiddleware` + real `AsyncSession` (not `FakeAsyncSession`); forged actor/tenant. Expect rejection with unchanged DB digest.
3. **Revision/CAS oracle:** same-revision concurrent writes, whole-deck vs slide-level race, reorder vs slide update, duplicate operation, Undo/autosave interleaving — deterministic rejection or defined serialization; no assumed last-write-wins.
4. **Export authorization lifecycle:** export after role revocation, delivery-time re-check, symlink/traversal, auth-disabled desktop boundary; plus malformed/untrusted PPTX parser safety.
5. **Notes/native-bullet acceptance:** explicit measurable criteria for `speaker_note` roundtrip and native bullet structure; current losses are failing criteria, not passes.
6. **Toolchain/exact-head preflight:** pin and pre-stage esbuild, win32-x64, katex, export-core 1.0.34 with a receipt; verify exact-head CI and independent code review.

## Next safest grain

One case, read-only: **P0b-B1** — a single owner-scoped `SlideModel` SELECT through real middleware and `AsyncSession` on a throwaway two-owner DB, with isolation manifest and DB digest. Only after that passes: **P0b-C1**, one cross-owner PATCH negative. No batch runs, no product source edits, no merge.
