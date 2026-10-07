# P07-G2 — Media Pipeline Contracts

**Parent:** #53
**Issue:** #55
**Canonical base:** `62e2f75ebe55ae40088c70e6177467963f53f71f` (P07-G1 merged)

## Goal

Multimodal video/audio sources by contract: transcript, scenes,
keyframes, and chapters align by timestamp with every absence an
explicit degraded label. Transcript-only is a declared mode, never
the silent default.

## Scope

- `servers/fastapi/gomrey/media_pipeline.py`: `TranscriptSegment` /
  `SceneSegment` / `MediaTimeline` models; `validate_timeline`
  (range, order, monotonic per-track, no overlap); `align_transcript_visual`
  (overlap attachment, uncovered scenes and ungrounded spans reported,
  segment-count budgets); `media_span` timestamp evidence spans with
  data-not-instructions treatment; `degraded_modes` explicit labels.
  Pure logic, no media I/O, no network, no new deps.
- `servers/fastapi/tests/test_gomrey_media_pipeline.py`: 3 tests
  (alignment + gaps, timestamp refusal + budget, span shape + degraded
  matrix).
- Package exports extended.

## Out of scope

Media fetching, subtitle acquisition, transcription, scene detection,
and keyframe workers (later qualification); connector sync (G3).

## Local qualification before commit

- `py_compile` on new/changed files: PASS.
- Gomrey-scoped pytest (17 modules incl. new media_pipeline): 90 PASS.
- Root Node suite: 48 PASS. `git diff --check`: PASS.
- Full FastAPI suite runs in exact-head CI (pre-existing env gap).
- Graft standing: additive over web_acquisition/ir_provenance.
- TypeSafe Jev `jev-1.13.0` (real): gaps-hidden 0.15,
  degraded-as-full 0.09. No blocking signal.
- PStack: still no canonical install; `PSTACK_NOT_EXECUTED`.
- Alibaba OCR: no OCR workflow in this repository; hosted OCR not
  executable. Delegation: exact-diff manual review; no BLOCKING
  findings; not a hosted PASS.
- Dependabot disabled (403); code scanning no analysis (404). Recorded.

## Review findings

- One malformed `__all__` edit drafted during export wiring was caught
  by the edit tool (target text absent) before touching the file; the
  applied exports were then verified complete by import audit
  (MISSING: none). No file corruption; NOT_APPLICABLE as a defect but
  recorded for process honesty.
- Unresolved material findings: 0.

## Exact-head requirement

Do not merge on local evidence alone. The committed candidate must pass
the full GitHub Actions workflow, including FastAPI pytest with the new
media_pipeline module, before a normal merge commit.
