# SXX — Phase name

**Goal:** Observable user or safety outcome, not a technology wish list.

**Owner role:** RXX. **Depends on:** SXX or none. **Status:** PLANNED / BLOCKED / IN_PROGRESS / TESTED / REVIEWED / MERGE_READY / MERGED.

## Coordination

- **Surface:** explicit file/contract ownership; no overlapping canonical writes.
- **Base:** exact tested commit SHA, PR and donor pin.
- **Isolation:** temp source/db/profile, no real user data, no unapproved paid/cloud calls.

## Requirements

- Reuse/adapt or copy the smallest qualified donor source. Record source SHA/file paths/license/NOTICE and rename map.
- Keep one canonical scene editor, source/claim fidelity, native PPTX integrity.
- Reject unauthorized edits, silent overwrites and data loss.

## Acceptance criteria

- **AC-01 (RED):** a named negative control fails for a meaningful defect on baseline; not a missing dependency.
- **AC-02 (GREEN):** bounded implementation makes the same test and relevant regression suite pass.
- **AC-03 (E2E):** real browser screenshot + semantic inspection if phase is user-visible.
- **AC-04 (Review):** independent Alibaba OCR file/rules selection and actual fresh source reviewer, including excluded notices.
- **AC-05 (Receipt):** current commit, command, exit, skips, fixture hash, artifacts, rollback and explicit limitations.

## Performance budget

Measure the current baseline before setting numeric targets. Never invent throughput/latency scores.

## Hardstop

No safe isolation, rights/NOTICE gap, owner authorization failure, silent revision overwrites, hidden object loss, unexpected paid egress, unreviewed deployment.

## Open questions

List only decision-blocking unknowns; prefer a deterministic tiny source/test spike. Preserve unresolved issues in STATE.md.

## Out of scope

Everything not necessary for this phase's acceptance. Dependent features remain on ROADMAP.
