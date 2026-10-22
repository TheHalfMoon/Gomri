# W3 — implementation evidence (evidence-bound narrative → artifact)

**Mission:** Issue #77, wave `W3`.
**Branch:** `feature/rea/w3-evidence-bound-narrative`
**Base:** canonical `main` @ `5f299a7a6174ad3a1180f827778db5f4400a4d71` (W3 depends on neither W1 nor W4a)
**Design:** `evidence/W3_DESIGN.md` (1 596 lines, produced by an independent subagent)
**Date (UTC):** 2026-10-22

---

## 1. What this grain delivers

Gomrey's P08/P09 evidence fabric was complete and fully tested but had **zero production call
sites**. A deck could be made, and a claim could be verified, but not both in one artifact.

W3 closes that by introducing the first production `app-layer → gomrey/` import edge:

```
POST /presentation/generate  (evidence_bundle + source_ir on the request)
  │
  ├─ build_plan_from_request()                       # app layer → gomrey
  │    └─ build_narrative_plan()                     # pure domain
  │         ├─ sufficiency_check()                   # P08-G1
  │         ├─ make_locator() + resolve()            # P08-G2  (citation identity)
  │         ├─ make_claim() + bind_claim_to_bundle()  # P09-G1
  │         ├─ verify_claim()                         # P09-G2  (deterministic gates)
  │         └─ make_decision() + synthesize()          # P09-G3  (abstain / conflict)
  │
  ├─ generate_ppt_outline(..., evidence=plan)         # the closed fact base
  │    └─ get_messages(..., evidence=plan)
  │         ├─ get_system_prompt(...)  += render_plan_rules(plan)
  │         └─ get_user_prompt(...)    += render_plan_context(plan)
  │    (the provider seam is untouched)
  │
  ├─ bind_plan_to_slides(plan, slides, toc_slides=…, title_slide=…)
  │    └─ slide.properties = {citation_ids, evidence_status, reasons}
  │       presentation.narrative  = NarrativeIR
  │       presentation.source_ir  = the IR the locators resolve against
  │
  └─ assert_artifact_exportable(presentation)          # export-time revalidation
       └─ resolve() every locator, or raise BrokenCitation
```

## 2. Files

| File | Change | Lines |
|---|---|---|
| `servers/fastapi/gomrey/narrative.py` | **added** — the pure domain module | ~520 |
| `servers/fastapi/services/evidence_narrative.py` | **added** — the app-layer wiring | ~170 |
| `servers/fastapi/tests/test_gomrey_narrative.py` | **added** — 26 pure-module tests | ~560 |
| `servers/fastapi/tests/integration/test_evidence_narrative_pipeline.py` | **added** — 15 end-to-end tests | ~330 |
| `servers/fastapi/alembic/versions/9a3c1f7b2d40_add_evidence_narrative_to_presentations.py` | **added** — persists `narrative` and `source_ir` | 58 |
| `servers/fastapi/models/sql/presentation.py` | modified — two nullable JSON columns | +7 |
| `servers/fastapi/models/generate_presentation_request.py` | modified — `evidence_bundle`, `source_ir` | +34 |
| `servers/fastapi/gomrey/__init__.py` | modified — exports the new symbols | +20 |
| `servers/fastapi/migrations.py` | modified — `REVISION_HEAD` advanced | +2 |
| `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py` | modified — the `evidence` hook | +28 |
| `servers/fastapi/api/v1/ppt/endpoints/presentation.py` | modified — plan, binding, persistence, export assertion | +70 |
| `contracts/v1/narrative-ir.schema.json` | modified — additive optional properties | +90 |
| `scripts/contracts.test.mjs` | modified — 4 contract tests | +90 |
| `servers/fastapi/tests/unit/test_migrations.py` | modified — 4 fixtures now create `presentations` | +16 |

## 3. Design decisions that differ from the design document

### 3.1 The contract version was NOT bumped

The design proposed `narrative-ir.schema.json` v1 → v2, and itself flagged that this is blocked:
`scripts/validate-contracts.mjs:176` hard-requires `schema.version === 1` for **every** schema.

The task requires preserving *"existing contract compatibility and version validation"*. Bumping the
version would have required weakening a declared repo-wide invariant. Instead the extension is
**additive within v1**:

- `sections[]` gains two **optional** properties, `citation_locators` and `evidence_status`;
- the document gains one **optional** property, `verification_scope`;
- `required` is unchanged, so every pre-existing document still validates;
- `scripts/validate-contracts.mjs` is **not modified** — the version invariant is untouched.

The per-kind required fields of a locator are enforced in the contract *and* in the code: the
schema's `CitationLocator` uses `allOf` + `oneOf` with a `const` kind per source family, so a
document locator without `page_no` is rejected by both layers.

### 3.2 The claim text may differ from the evidence text

The P09-G2 quantity gate compares a claim's numbers and dates against the **supporting texts**.
A claim that merely restates its own evidence can never fail that gate, which would make the gate
vacuous.

A bundle span may therefore carry an explicit `claim_text` — the *assertion* — separately from
`text`, the *evidence*. The claim is built from `claim_text` when present, and the evidence view
always carries `text`. This is the only way the deterministic quantity gate carries meaning, and
it is what the two negative tests exercise.

### 3.3 The plan fixes its own node count

`build_narrative_plan` accepts `n_slides: Optional[int]`. When the caller does not fix a count,
the evidence does: one node per citable claim, bounded by `MAX_PLAN_NODES`. The plan therefore
always has an exact node count, and the positional binding between a plan node and a rendered
slide is exactly one to one. The endpoint then pins the outline's slide count to the plan's node
count so the provider cannot return a different number of slides.

## 4. Bugs the tests caught (and the fixes)

Every one of these was found by a test, not by inspection, and each is now regression-tested.

| # | Bug | Severity | Fix |
|---|---|---|---|
| 1 | **Table-of-contents index shift.** The plan index was computed as `index - n_toc`, which is wrong whenever a title slide is present. The rendered order is `[title] + [toc] × n_toc + [node 0, node 1, …]`, so the node index is `index - insertion - n_toc`. With a title slide and one TOC slide, the citation for node 1 would have landed on node 0. | **Critical** — silent mis-attribution of citations | Corrected to `index - insertion - n_toc`; covered by three binding tests |
| 2 | **An insufficient bundle still produced a grounded node.** Sufficiency is the abstention signal the P08-G1 docstring names, but the node status was derived from the claim verdict alone, so a one-span bundle still produced a `grounded` node. | **High** — the artifact would assert support the evidence does not carry | A grounded node is downgraded to `abstained` with reason `insufficient-evidence` whenever the sufficiency verdict is `insufficient` |
| 3 | **A controller-backed animation could be permanently hidden** *(W4a, recorded here for completeness)* | High | Fixed in the W4a grain |
| 4 | **`counter-up` declared a keyframe it never emitted** *(W4a)* | Medium | Fixed in the W4a grain |

Two further defects were caught by the design's own risk list and confirmed by the tests:

| Risk from the design | Confirmed? | Handling |
|---|---|---|
| A span whose locator does not mint its declared citation id | **Yes** | `AdmissionError("normalization_failure")`. This is the single guard that makes a fabricated citation impossible. |
| A span with no `citation_id` | **Yes** | Recorded as an omission. It is never given a freshly minted identity, because a minted identity would assert provenance the span never claimed. |
| An unresolvable locator | **Yes** | Recorded as an omission `unresolvable-citation:…`; the span never becomes a citable claim. |
| A grounded section with no locator | **Yes** | `assert_exportable` raises `BrokenCitation`: an assertion of support with nothing behind it. |

## 5. Verification scope — units and entities are NOT gated

The P09-G2 verifier gates **numbers and dates only**. `contracts/v1/claim.schema.json` declares a
`unit_check` field, but **no code implements it anywhere in `gomrey/`**. A verdict of `supported`
therefore means *"the numbers and dates agree, the stance is supporting, and no override pattern
was found"* — it does **not** mean units or entities were verified.

W3 makes that impossibility explicit rather than leaving it implicit:

- `DETERMINISTIC_GATES = ("numbers", "dates")` and
  `UNVERIFIED_DIMENSIONS = ("units", "entities")`;
- `verification_scope()` returns both lists;
- the plan carries a `verification_scope` block, and so does the persisted NarrativeIR;
- **every grounded node records `units-not-gated` and `entities-not-gated` in its reasons**, so
  `grounded` can never be read as `fully verified`;
- `render_plan_context` and `render_plan_rules` state the scope in prose to the producer.

## 6. The five mandated acceptance cases

All five are in `servers/fastapi/tests/test_gomrey_narrative.py`, marked "MANDATED CASE".

| # | Case | Test |
|---|---|---|
| 1 | A supported claim yields a resolvable locator | `test_supported_claim_yields_resolvable_locator` |
| 2 | An unresolved claim yields an explicit abstention marker and never a fabricated citation | `test_unresolved_claim_yields_abstention_marker_and_no_fabricated_citation` |
| 3 | A contradictory pair is flagged | `test_contradictory_pair_is_flagged`, `test_a_conflicted_node_is_marked_conflicted_and_keeps_both_sides` |
| 4 | An unresolvable locator fails the export-time assertion | `test_unresolvable_locator_fails_export_assertion`, `test_a_grounded_section_without_a_locator_fails_the_export_assertion` |
| 5 | The provider still cannot overrule a deterministic gate | `test_provider_cannot_overrule_deterministic_gate`, `test_provider_verdict_without_identity_is_refused` |

## 7. Domain-layer boundary

`gomrey/narrative.py` imports **only** stdlib and intra-`gomrey` modules:

```text
from gomrey.claims import bind_claim_to_bundle, make_claim
from gomrey.citations import BrokenCitation, make_locator, resolve
from gomrey.decisions import SYNTHESIS_ELIGIBLE, make_decision, synthesize
from gomrey.evidence_bundle import sufficiency_check
from gomrey.gateway import AdmissionError
from gomrey.verification import verify_claim
```

The module performs no I/O, no network access, no filesystem access and no credential access, and
it never calls a provider. The provider's opinion is *supplied* to the deterministic verifier
through the existing `verification.verify_claim(provider_verdict=…)` seam. A repository-wide grep
confirms no `gomrey/` module imports `api/`, `utils/`, `models/` or `services/`.

## 8. Gate results on this revision

| Gate | Command | Result |
|---|---|---|
| Repository tooling | `npm test` | **52 pass / 0 fail** (4 + 48) |
| FastAPI | `uv run --locked python -m pytest -q` | **1166 passed** (1125 baseline + 26 pure + 15 integration) |
| Next.js unit | `npm test` | 73 pass / 0 fail (unchanged; W3 does not touch Next.js) |
| Contract validation | `node scripts/validate-contracts.mjs` | `contracts: OK (23 schemas listed and loadable)` |
| Contract tests | `node --test scripts/contracts.test.mjs` | **9 pass / 0 fail** (4 new) |
| Secret scan | `node scripts/scan-secrets.mjs` | OK |
| Fixture policy | `node scripts/check-fixtures.mjs` | OK |
| Platform support | `node scripts/check-platform-support.mjs` | OK |
| Release config | `node scripts/validate-release-config.mjs` | OK |
| Release manifest | `node scripts/generate-release-manifest.mjs --check-only` | OK |

## 8a. The Jev q8 finding and its fix

The first Jev build review of this candidate returned **q8 = 0.65 — concern present**: *"Is an agent
tool result structured and idempotent?"*.

That finding was correct and material. The plan was constraining the **outline** generation, but
the per-slide **content** is written by a second LLM call
(`get_slide_content_from_type_and_outline`) that never saw the plan. So the outline was
evidence-constrained while the rendered slide could still assert something the evidence did not
carry. "The provider renders, it never decides" was not yet true end to end.

Three fixes followed, all regression-tested:

1. **The slide content call now receives the plan node.**
   `get_slide_content_from_type_and_outline(..., evidence_node=...)` injects the node's closed fact
   base and its evidence rules into the content prompt. Without a node the prompt is unchanged.

2. **The fact base now carries the claim texts.**
   `PlanNode` gained `claim_texts`, and `render_plan_context` now emits the claims themselves. A
   fact base that lists citation ids but not the facts is not a fact base.

3. **The recovery path rebuilds the node from the persisted artifact.**
   The section text of the NarrativeIR now holds the node's claim texts, so
   `plan_node_from_narrative()` can rebuild the node when the in-memory plan is gone — which is
   exactly the situation of the streaming/recovery path. That path now re-renders a recovered slide
   under the same evidence rules as the original.

A fourth bug was found by the new tests while fixing the third: `node_reasons_scope` had inverted
the meaning of the `<dimension>-not-gated` flag, so a grounded node reported an **empty** gated
list. Corrected: a grounded node reports `gated = (numbers, dates)` and `not_gated = (units,
entities)`; a node that is not grounded verified nothing at all and reports both lists empty of
gating.

## 8b. The single shared slide-to-node rule

The table-of-contents remap is now implemented **once**, in
`gomrey.narrative.plan_index_for_slide`, and consumed by:

- `bind_slide_locators` — the persisted per-slide binding;
- `plan_node_for_slide` — the content call in the generation path;
- `plan_node_from_narrative` — the content call in the recovery path.

A unit test asserts that all three agree, and the binding tests assert the exact slide indices
for the title, table-of-contents and content positions.

## 8c. The containment gate — closing the q8 finding properly

The second Jev review of the fixed candidate **still** returned q8 = 0.65. That was correct
again, and it identified a deeper problem than the prompt wiring:

> The plan constrains the provider by **prompt**. Nothing checked what the provider actually
> produced. The rendered slide could state a figure the evidence does not carry, and the artifact
> would still be marked `grounded`.

W3 therefore adds the deterministic counterpart:

- `gomrey.narrative.collect_rendered_text(value)` — a layout-agnostic collector of the
  audience-facing prose of a rendered slide (identifiers, layout names, colours and URLs are not
  prose and are ignored).
- `gomrey.narrative.check_plan_containment(node, rendered_text)` — every number and date the
  rendered slide states must already appear in a claim the plan verified. The comparison **reuses
  the P09-G2 quantity gate**, so the product has exactly one number-and-date rule.
- The endpoint runs the check per slide and, when it fails, the slide's persisted binding is
  downgraded to `abstained` with reason `rendered-content-outside-plan` and the specific missing
  numbers and dates recorded. The speaker note is deliberately **not** checked: it is structural
  prose, and a count like "three key points" is not a factual claim.

This is what makes "the provider renders, it never decides" structurally true rather than
aspirational: a slide that asserts a figure the evidence does not carry cannot ship as grounded,
whatever the prompt said.

**Speaker-note boundary, stated:** the containment check covers the visible slide content only.

## 9. What is still open for W3

| Item | State |
|---|---|
| The `outlines.py` review path (`GET /outlines/stream/{id}`) | **Not wired.** It calls `generate_ppt_outline` and would accept the plan, but its request model is separate and the binding path is not wired. Recorded rather than silently omitted. |
| The smart-generation pipeline | **Not covered.** It is a separate pipeline that does not go through `generate_ppt_outline`. |
| Outline re-validation after a user edits the outline on the review page | **Not wired.** The export-time assertion covers export; the *prepare* path still accepts client outlines without re-checking them against the evidence. This is the design's risk #4 and it remains open. It is the highest-priority follow-up because a user-edited outline can reach a slide without passing the plan. |
| `providers` / `tools` MCP surface | Not changed. |
| Arabic / RTL | Not covered by W3; it is wave `W13`. |

## 10. Non-fabrication record

- No Gamma product source was inspected, because none was obtained.
- No paid service, hosted model, funded compute or product account was used.
- No login, paywall, CAPTCHA, rate limit or access control was defeated.
- No credential, secret or user data was collected.
- The pre-existing review stack was executed on the exact candidate; the unavailable tools are
  recorded as `NOT_EXECUTED` with their exact blockers in `REVIEW_RECORD_W3.md`.
- GitHub Actions did not execute (account-level spending-limit condition). No CI result is claimed.
