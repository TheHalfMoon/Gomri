# W3 — Evidence-bound narrative → artifact producer: implementation design

**Mission:** issue #77, wave W3.
**Scope:** wire the existing, tested P08/P09 evidence fabric under `servers/fastapi/gomrey/`
into the presentation pipeline so that (a) a deck is built from an `EvidenceBundle`,
(b) every claim carries a resolvable citation locator, (c) unresolved claims and
conflicts surface as explicit markers, (d) no artifact can contain a citation that
`servers/fastapi/gomrey/citations.py` cannot resolve.

**Status:** READ-ONLY design. No source file was modified by this document. The only
file created by this work is this document.

**Authority note.** The W3 row in
`research/rea/2026-10-22-nextslide-gamma/IMPLEMENTATION_GRAPH.md:90-99` already fixes
the intended shape: *"new `servers/fastapi/gomrey/narrative.py`; hook in
`utils/llm_calls/generate_presentation_outlines.py`; `contracts/v1/narrative-ir.schema.json`
(per-slide citation locators)"*. This document refines that row to an executable level
and records where the recorded plan was under-specified (see §F.6).

Every factual claim below cites `file:line` in the repository at commit
`2a8e482`. Anything not verified by reading the file is marked **UNCERTAIN**.

---

## A. Current-state facts

### A.0 The two facts that shape the whole design

**(A.0.1) The `gomrey/` package has zero production call sites.**
A repository-wide grep for imports of `gomrey` outside the package
(`servers/fastapi/**`, excluding `.venv/`) returns **only** files under
`servers/fastapi/tests/`. No file under `api/`, `utils/`, `models/`, `services/`
imports `gomrey`. The package is a pure, fully-tested island. This is precisely the
gap W3 closes, and it means W3 introduces the **first** production import edge
`app-layer → gomrey/`.

**(A.0.2) The `gomrey/` package is a pure domain layer and must stay one.**
`grep -rn "^from \|^import " servers/fastapi/gomrey/*.py` shows the only non-stdlib
imports are `pydantic` (`gomrey/contracts.py:12`) and stdlib (`uuid` `gomrey/adapters.py:19`,
`posixpath` `gomrey/file_boundary.py:26`, `ipaddress` `gomrey/remote_gateway.py:30`).
No `gomrey/` module imports `models/`, `utils/`, `api/` or `services/`. Every module
docstring repeats the rule: *"Pure deterministic logic with no … model calls"*.
**Therefore `gomrey/narrative.py` must not import from the app layer and must not
call a provider.** The LLM-calling half of W3 must live in `utils/llm_calls/`.

### A.1 `servers/fastapi/gomrey/citations.py` (130 lines)

Public surface:

| Symbol | Line | Signature / shape |
|---|---|---|
| `LOCATOR_KINDS` | 29 | `frozenset({"document","web","video","spreadsheet","image"})` — the 5 locator kinds |
| `BrokenCitation` | 34–37 | `@dataclass class BrokenCitation(Exception)` with fields `citation_id: str`, `reason: str` |
| `citation_id` | 40 | `citation_id(locator: dict[str, Any]) -> str` — `"cite-" + sha256(canonical_json)[:16]` |
| `make_locator` | 46 | `make_locator(kind: str, **fields: Any) -> dict[str, Any]` |
| `resolve` | 89 | `resolve(locator: dict[str, Any], ir_document: dict[str, Any]) -> dict[str, Any]` |
| `_find_unit` | 82 | private: `unit.get("source_unit_id") == unit_id and unit.get("source_id") == source_id`, else `BrokenCitation("", f"unit not in IR: …")` |

`make_locator` required fields per kind (lines 51–57):

```
document   : source_id, unit_id, page_no
web        : source_id, unit_id, canonical_url, retrieved_at
video      : source_id, unit_id, video_id, start, end
spreadsheet: source_id, unit_id, workbook, sheet, cell
image      : source_id, unit_id, bbox
```

Optional fields copied when present (62–64): `paragraph`, `table_cell`, `region_bbox`,
`section`, `transcript_segment_id`, `scene_id`, `keyframe_id`, `unit_id`, `range`, `table`.

Shape guards (67–77): `document.page_no` must be `int`; `video` must satisfy
`0 <= start < end`; `spreadsheet.cell` must match `^[A-Z]{1,3}[1-9][0-9]*$`
(`_CELL_RE`, line 31); `image.bbox` must be a 4-sequence with `bbox[0] < bbox[2]` and
`bbox[1] < bbox[3]`.

`make_locator` sets `locator["citation_id"] = citation_id(locator_without_citation_id)`
(line 78). **The ID is content-addressed over the canonical JSON of the locator
(with `kind` included, `citation_id` excluded).** Calling `citation_id(locator)` on a
locator that already carries a `citation_id` yields a *different* hash — callers must
mint IDs with `make_locator`, never with `citation_id` on a pre-stamped dict.

`resolve` semantics (89–130), per kind:
- `document` (99–104): if `unit["page_no"]` is present and differs from the locator's
  `page_no` → `BrokenCitation(citation, "locator page disagrees with IR unit")`.
- `web` (105–110): if `unit["provenance"]["retrieval_snapshot"]["retrieved_at"]`
  exists and differs → `BrokenCitation(citation, "locator snapshot is not the cited retrieval")`.
- `video` (111–116): if `unit["provenance"]["timestamp"]` exists and the locator range
  is not contained in it → `BrokenCitation(citation, "locator timestamp outside cited span")`.
- `spreadsheet` (117–119): no coordinate check — resolves on unit existence alone.
- `image` (120–123): if `unit["bbox"]` exists and differs → `BrokenCitation(citation, "locator bbox disagrees with IR unit")`.

Returns (124–130):
```python
{"citation_id": …, "kind": …, "position": {…}, "source_revision": ir_document.get("original_digest", ""), "resolved": True}
```

**`resolve` requires an `ir_document` shaped like `gomrey.ir_provenance.assemble_ir`
output**: `{"source_id", "tenant_id", "workspace_id", "original_digest", "unit_count",
"units": [...]}` (`gomrey/ir_provenance.py:67-74`), where each unit carries
`source_id`, `source_unit_id`, optional `page_no`, optional `bbox`, and a `provenance`
dict with `parsers`, `agreement`, optional `retrieval_snapshot`, optional `timestamp`.

### A.2 `servers/fastapi/gomrey/evidence_bundle.py` (132 lines)

| Symbol | Line | Signature |
|---|---|---|
| `SUFFICIENCY_VERDICTS` | 31 | `frozenset({"sufficient","insufficient","needs_review"})` |
| `EvidenceBundle` | 34–45 | dataclass: `bundle_id, query, tenant_id, workspace_id, source_revisions: list[dict[str,str]], spans: list[dict], retrieval_identities: list[str], contradictions: list[dict], omissions: list[dict[str,str]], verification_state: str = "unverified"` |
| `build_bundle` | 48 | `build_bundle(*, bundle_id, query, tenant_id, workspace_id, source_revisions, spans, retrieval_identities, contradictions=None, omissions=None, dropped_without_reason=0) -> EvidenceBundle` |
| `bundle_digest` | 94 | `bundle_digest(bundle) -> str` (sha256 over the 11 canonical fields, 96–107) |
| `sufficiency_check` | 111 | `sufficiency_check(bundle, *, min_spans: int = 2, require_fresh: bool = True) -> dict` |

`build_bundle` refusals (62–80): missing identity → `AdmissionError("malformed_source")`;
`dropped_without_reason > 0` → `AdmissionError("normalization_failure")`; a
`source_revision` without `source_id`/`digest` → `malformed_source`; a span without
`citation_id` **or** `span_id` → `normalization_failure`; a contradiction whose
`span_ids` reference an unknown span → `normalization_failure`.

`sufficiency_check` returns `{"verdict", "reasons", "stale_spans"}`:
- `too-few-spans` when `len(bundle.spans) < min_spans` (**default `min_spans=2`, so a
  one-span bundle is `insufficient`** — verified by execution),
- `stale-spans-present` when a span carries `stale_labeled` and `require_fresh`,
- `contradictions-open` → verdict `needs_review` **always wins** (128–129),
- else `insufficient` if any reason, else `sufficient` (131–132).

**Sufficiency is the abstention signal** (docstring lines 16–19: *"the abstention
signal downstream generation must obey"*).

### A.3 `servers/fastapi/gomrey/claims.py` (357 lines)

| Symbol | Line | Notes |
|---|---|---|
| `VERIFICATION_STATES` | 41 | `unverified, verifying, supported, partially_supported, contradicted, does_not_establish, unresolved, blocked` |
| `CLAIM_STATUSES` | 52 | `draft, candidate, accepted, downgraded, blocked, withdrawn` |
| `UNCERTAINTY_LEVELS` | 61 | `low, medium, high, unknown` |
| `DERIVATION_KINDS` | 63 | `human, imported, derived, generated` |
| `normalize_claim` | 110 | `normalize_claim(text) -> dict` → `{"text_normalized", "tokens"}` |
| `detect_policy_override_attempt` | 122 | `detect_policy_override_attempt(text) -> bool` — deterministic tripwire; `_OVERRIDE_PATTERNS` at 67–74 |
| `Claim` | 133–150 | dataclass: `claim_id, text, normalized, tenant_id, workspace_id, evidence_refs, supports, contradicts, uncertainty, status, verification_state, version, created_at, updated_at, derivation, source_provenance` |
| `make_claim` | 153 | keyword-only; **required**: `claim_id, text, tenant_id, workspace_id, created_at, updated_at, derivation` |
| `claim_digest` | 224 | `claim_digest(claim) -> str` |
| `bind_claim_to_bundle` | 247 | `bind_claim_to_bundle(claim, bundle, *, require_fresh: bool = True) -> dict` |
| `ClaimStore` | 308 | `Protocol` — `put`, `get`, `delete` |
| `MemoryClaimStore` | 325 | dict-backed implementation |

`make_claim` refusals: bad id format (`_ID_RE` line 65), duplicate id in a list
(`_check_id_list`, 83–97), self-reference (181–183), unknown enum (184–189),
`version < 1` (190–191), bad timestamp (100–107), `derivation.kind` not in
`DERIVATION_KINDS` (194–195), a `source_provenance` entry without `source_id` (197–200).

`bind_claim_to_bundle` returns:
```python
{"claim_id", "bundle_id", "bound_spans", "stale_spans", "contradictions_open",
 "omissions", "override_flag", "reasons", "bindable_for_verification"}
```
Refusals: cross-project → `AdmissionError("access_denied")` (259–260); a claim
reference that is not a span ID → `AdmissionError("normalization_failure")` (265–267).

`reasons` may contain (278–293): `no-evidence-refs`, `bundle-empty`,
`stale-spans-present`, `contradictions-open`, `policy-override-flagged`,
`span-without-citation-id`.

**Critical invariant:** a span is identified by `span.get("citation_id") or
span.get("span_id","")` (262–264). A bound span that has **no `citation_id`** yields
reason `span-without-citation-id` (289–293) → not bindable. So the bundle's spans
must carry `citation_id` (not merely `span_id`) for a claim to reach verification.

**There is no `ClaimContract` type in the repo.** The claim *contract* is
`contracts/v1/claim.schema.json` (a flat, storage-shaped record) plus the
`gomrey.claims.Claim` dataclass. A distinct `ClaimContract` class **does not exist**.

### A.4 `servers/fastapi/gomrey/verification.py` (213 lines)

| Symbol | Line | Notes |
|---|---|---|
| `VERDICTS` | 39 | `supported, partially_supported, contradicted, does_not_establish, unresolved, blocked` — the 6 verdicts |
| `STANCES` | 48 | `supports, contradicts, context` |
| `_NUMBER_RE` | 50 | `\d+(?:\.\d+)?` |
| `_DATE_RE` | 51 | ISO date, `d/d/yyyy`, or a bare 4-digit year 19xx/20xx |
| `check_quantity_agreement` | 64 | `check_quantity_agreement(claim_text: str, supporting_texts: list[str]) -> dict` → `{"ok", "missing_numbers", "missing_dates"}` |
| `verify_claim` | 83 | `verify_claim(claim, binding_report, bundle, *, evidence_views=None, provider_verdict=None, provider_identity=None) -> dict` |
| `_verdict` | 189 | assembles the record + sha256 `digest` |

**Deterministic gates that exist (and only these):**
1. **Numbers** — `_numbers` (56) / `check_quantity_agreement` (64–80): every number
   token in the claim text must appear in the pooled supporting text, else
   `missing_numbers`. Applied at 157–164.
2. **Dates** — `_dates` (60) / `check_quantity_agreement`: same rule → `missing_dates`.
   Applied at 163–164.
3. **Binding inheritance** (107–117): if `bindable_for_verification` is False the
   verdict is inherited verbatim from the binder; `binding:contradictions-open` →
   `contradicted`, otherwise `unresolved`; an override flag forces `unresolved`.
4. **Stance tally** (148–170): contradicting-only → `contradicted`; contradicting +
   supporting → `partially_supported`; supporting only → quantity gate → `supported`
   or `does_not_establish`; no supporting stance → `does_not_establish`.
5. **Override tripwire** (135–146): an override pattern in any evidence view or in
   the claim forces `unresolved`.
6. **Evidence-view presence** (119–129): a bound ref with no view →
   `does_not_establish` with reason `no-evidence-view:{ref}`.

**There is no separate unit gate and no separate entity gate.** The task brief asks
about "numbers/dates/units/entities"; the repo implements **numbers and dates only**
(`check_quantity_agreement`). `contracts/v1/claim.schema.json` declares
`numeric_check`, `date_check`, `unit_check` — but `unit_check` has **no code
implementation anywhere in `gomrey/`**. Units and entities are **not** deterministically
gated. This must be stated, not glossed.

**The provider-cannot-overrule rule (172–180):**
```python
overruled = False
if provider_verdict is not None:
    if verdict in ("contradicted", "does_not_establish", "unresolved", "blocked"):
        if provider_verdict in ("supported", "partially_supported"):
            overruled = True
            reasons.append("provider-overruled-by-policy")
    if verdict == "partially_supported" and provider_verdict == "supported":
        overruled = True
        reasons.append("provider-overruled-by-policy")
```
A provider verdict also requires `provider_identity` with both `provider` and
`model_revision` (99–102), else `AdmissionError("malformed_source")`.

The verdict record (200–212):
```python
{"claim_id","bundle_id","verdict","reasons","checks","provider_verdict",
 "provider_identity","provider_overruled","digest"}
```
`checks` is always `["binding-inherited","stance-tally","quantity-agreement","override-tripwire"]` (105).

### A.5 `servers/fastapi/gomrey/decisions.py` (359 lines)

| Symbol | Line | Notes |
|---|---|---|
| `NODE_KINDS` | 38 | `claim, evidence, source, citation, decision` |
| `EDGE_RELATIONS` | 40 | `supports, contradicts, cites, derives, context` |
| `DECISION_STATUSES` | 42 | `proposed, accepted, abstained, blocked, superseded` |
| `SYNTHESIS_ELIGIBLE` | 44 | `frozenset({"supported","partially_supported"})` |
| `build_graph` | 78 | `build_graph(*, tenant_id, workspace_id, nodes, edges) -> SupportGraph`; orphan citation → `AdmissionError("normalization_failure")` (111–115) |
| `graph_digest` | 119 | `graph_digest(graph) -> str` |
| `Decision` | 131–145 | dataclass: `decision_id, question, tenant_id, workspace_id, claim_ids, evidence_ids, constraints, assumptions, uncertainty, alternatives, conclusion, status, version` |
| `make_decision` | 148 | keyword-only; **required**: `decision_id, question, tenant_id, workspace_id`; each alternative must have a non-empty `option` (180–182) |
| `synthesize` | 193 | `synthesize(decision, verdicts, *, require_alternative_when_conflict: bool = True) -> dict` |
| `CalibrationProfile` | 249–255 | dataclass: `provider, workload, benchmark, samples, abstention_rate` |
| `register_profile` | 258 | `register_profile(registry, *, provider, workload, benchmark, samples, abstention_rate) -> dict` — refuses `samples < 50` (270–271), `abstention_rate` outside [0,1] (272–273) |
| `route_workload` | 281 | `route_workload(registry, workload, candidates) -> dict` → `{"provider","mode":"calibrated"\|"deterministic-only","benchmark","reason"}` |
| `adjudicate` | 296 | `adjudicate(deterministic_verdict, challenger_verdict=None, challenger_independent=False) -> dict` |
| `DecisionStore` / `MemoryDecisionStore` | 316 / 333 | protocol + dict-backed impl |

**`synthesize` (193–246) is the ABSTAIN mechanism:**
- Only `supported` / `partially_supported` claims are **included** (213).
- Everything else is **omitted** with its verdict and first two reasons (218–220).
- `partially_supported` → `conflicts += {"kind": "partial-support"}` (215–217).
- `contradicted` → `omissions` **and** `conflicts += {"kind": "contradiction"}` (221–223).
- **If any conflict exists and `decision.alternatives` is empty and
  `require_alternative_when_conflict` is True → the whole synthesis is
  `status="abstained"`, `included_claims=[]`, `conclusion=""`,
  `reasons=["conflict-requires-alternative"]`, and every included claim is
  additionally withheld (224–235).**
- Otherwise `status = "accepted" if included else "abstained"` (236);
  `reasons = ["synthesis-complete"]` or `["no-eligible-claims"]` (245).

`adjudicate` (296–313): deterministic wins; a challenger that disagrees and is
**not** independent → `mode="deterministic-wins"`; an independent challenger that
disagrees → `verdict="unresolved"`, `abstained=True`,
`reason="challenger-divergence-needs-evidence"`.

### A.6 `servers/fastapi/gomrey/retrieval_pipeline.py` (160 lines)

| Symbol | Line | Signature |
|---|---|---|
| `CHANNELS` | 30 | `("exact", "lexical", "dense", "visual", "graph")` |
| `acl_filter` | 33 | `acl_filter(candidates, *, tenant_id, workspace_id) -> {"kept","denied"}` |
| `lexical_overlap` | 51 | `lexical_overlap(query: str, text: str) -> float` (query terms > 2 chars) |
| `exact_boost` | 60 | `exact_boost(candidates, *, identifiers: list[str]) -> list[dict]` — matches on `unit_id` |
| `fuse` | 76 | `fuse(candidates, *, weights: dict[str,float]) -> list[dict]` — adds `fused_score`, `channels_present`; unknown channel → `AdmissionError`; zero-sum weights → `AdmissionError` |
| `apply_constraints` | 101 | `apply_constraints(ranked, *, max_per_source=3, include_stale=False, limit=10) -> {"results","excluded_stale"}` — stale excluded by default and **labelled** `stale_labeled` when included |
| `retrieve` | 131 | `retrieve(*, query, candidates, tenant_id, workspace_id, identifiers=None, weights=None, max_per_source=3, include_stale=False, limit=10) -> dict` |

**What does it need to search?** There is **no index server, no embedding model, no
vector store** in this module. `retrieve` consumes a **candidate list of plain dicts**
supplied by the caller. A candidate dict is expected to carry (by field access in
the code): `tenant_id`, `workspace_id`, `unit_id`, `source_id`, `text`, optional
`scores` (a dict keyed by channel names from `CHANNELS`), optional `is_fresh`.

**No indexes exist anywhere in the repo for this pipeline.** `grep` over
`servers/fastapi/` finds no Qdrant/pgvector/FAISS/Lucene client wired to
`retrieval_pipeline.retrieve`. The `fastembed-vectorstore` dependency is listed in
`pyproject.toml` but is not used by `gomrey/`.

`retrieve` returns `{"results", "denied_by_acl", "excluded_stale", "candidates_seen"}`
(155–160). Default weights `{"exact": 3.0, "lexical": 2.0, "dense": 1.0}` (152).

### A.7 Other `gomrey/` modules relevant to W3

- `gomrey/gateway.py`: `AdmissionError(code, detail)` at 96–103; `ERROR_CODES` at 59
  (`unsupported_source, unsafe_source, malformed_source, resource_limit_exceeded,
  access_denied, remote_fetch_denied, parser_failure, normalization_failure,
  duplicate_source`). `Principal` (113), `AdmissionReceipt` (123), `is_trusted` (136),
  `transition_trust` (141), `content_identity` (151), `select_parser` (161),
  `can_access` (181), `admit_source` (204).
- `gomrey/adapters.py`: `owner_to_scope(owner_id)` (25) → `(f"tenant:{id}", f"tenant:{id}:default")`,
  `UNOWNED_TENANT = "tenant:unowned"`, `UNOWNED_WORKSPACE = "workspace:default"` (21–22);
  `canonical_digest` (33); `presentation_to_artifact` (39);
  `presentation_to_revision` (54); **`slides_to_narrative(presentation, slides)` (82)** —
  already produces a NarrativeIR-shaped dict with one section per slide,
  `heading="Slide N"`, `text=speaker_note`, `claim_ids=[]` (91–97), and
  `narrative_id=f"{presentation.id}:narrative:1"` (100). It is **structural only** —
  its own docstring says *"No semantic extraction or claim mining happens here;
  evidence binding is a later ingestion grain"* (86–87). **W3 is that grain.**
- `gomrey/ir_provenance.py`: `assemble_ir(*, source_id, tenant_id, workspace_id,
  original_digest, records) -> dict` (36) — produces the `ir_document` that
  `citations.resolve` consumes; `verify_coverage(declared_unit_ids, records)` (88).
- `gomrey/contracts.py`: `NarrativeSection(FrozenRecord)` at 124–127 —
  `heading`, `text`, `claim_ids`. `FrozenRecord` = `ConfigDict(extra="forbid", frozen=True)` (15–16).
- `gomrey/__init__.py`: re-exports **every** public symbol of every module and lists
  them in `__all__` (e.g. `from gomrey.citations import BrokenCitation, citation_id,
  make_locator, resolve` at the `citations` import block; `"resolve"`, `"make_locator"`,
  `"sufficiency_check"`, `"synthesize"`, `"slides_to_narrative"` appear in `__all__`).
  **W3 must follow this convention.**

### A.8 The presentation pipeline — exact call sequence

#### A.8.1 `utils/llm_calls/generate_presentation_outlines.py` (404 lines)

| Symbol | Line |
|---|---|
| `OutlineGenerationStatus` (frozen dataclass, `message: str`) | 50–52 |
| `get_system_prompt(verbosity=None, include_title_slide=True, include_table_of_contents=False)` | 66 |
| `get_user_prompt(content, n_slides, language, additional_context=None, tone=None, instructions=None, include_title_slide=True, include_table_of_contents=False)` | 186 |
| `get_messages(content, n_slides, language, additional_context=None, tone=None, verbosity=None, instructions=None, include_title_slide=True, include_table_of_contents=False) -> list[Message]` | 217 |
| `async generate_ppt_outline(content, n_slides, language=None, additional_context=None, tone=None, verbosity=None, instructions=None, include_title_slide=True, web_search=False, include_table_of_contents=False, emit_statuses=False, disconnect_checker=None)` | 251 |

`generate_ppt_outline` is an **async generator** that yields text chunks. Inside it:
- `model = get_model()` (265), `response_model = get_presentation_outline_model_with_n_slides(n_slides)` (266–270),
- `client = get_client(config=get_llm_config(use_openai_responses_api=use_search_tool))` (274–276),
- web-search routing (272–352) — the only network branch,
- `outline_schema = prepare_schema_for_validation(response_model.model_json_schema(), strict=False)` (361–364),
- `response_format = JSONSchemaResponse(name="response", json_schema=outline_schema, strict=False)` (365–369),
- **the provider seam**: `async for event in stream_generate_events(client, disconnect_checker=…, **get_generate_kwargs(model=model, messages=get_messages(…), response_format=response_format, tools=…, stream=True))` (371–390),
- content chunks are yielded verbatim (392–396); a non-content final chunk is
  serialised with `serialize_structured_content` (400–402),
- `except Exception as e: yield handle_llm_client_exceptions(e)` (403–404).

**The provider seam is `get_client` + `get_model` + `stream_generate_events` /
`generate_structured_with_schema_retries`, and the prompt is assembled purely by
`get_messages`.** That is the seam W3 must not change.

`get_user_prompt` (186–214) builds a flat text block with the labelled lines
`Generation Settings (authoritative):`, `Today's Date:`, `Content:`, `Instructions …`,
`Context:`. `get_system_prompt` (66–166) is a long rules string; line 158 is
*"Do not include URLs, hyperlinks, citations, footnotes, references, or source lists in
slide outlines."* and line 163 is *"…do not invent citations."* — **these two lines
are the natural home for the evidence rules**, but note line 158 currently forbids
citations in the outline. W3 must not contradict itself: the *model* must not write
citations (they are attached deterministically), so line 158 stays valid and is
*reinforced*, not relaxed.

#### A.8.2 `utils/llm_calls/generate_slide_content.py` (275 lines)

- `SLIDE_CONTENT_SYSTEM_PROMPT` (20–67), `SLIDE_CONTENT_USER_PROMPT` (70–84).
- `_prepare_response_schema(json_schema)` (203–226) — strips `__image_url__` /
  `__icon_url__` (86), injects a required `__speaker_note__` (214–225), forces
  `ensure_array_schemas_have_items` (226).
- `async get_slide_content_from_type_and_outline(slide_layout: SlideLayoutModel,
  outline: SlideOutlineModel, language: Optional[str], tone=None, verbosity=None,
  instructions=None, *, slide_number=None, disconnect_checker=None)` (229–275).
  Returns a **dict** — the slide's content JSON — via
  `generate_structured_with_schema_retries(client, model, messages=…, response_format=…,
  json_schema=…, strict=False, validate_schema=True, disconnect_checker=…)` (263–272).
  The response schema is the **slide layout's** JSON schema, i.e. the model is
  constrained by the layout, not by the outline.

#### A.8.3 `utils/llm_calls/generate_presentation_structure.py` (211 lines)

- `get_messages(presentation_layout, n_slides, data, instructions=None, source_content=None)` (108).
- `get_messages_for_slides_markdown(...)` (137).
- `async generate_presentation_structure(presentation_outline: PresentationOutlineModel,
  presentation_layout: PresentationLayoutModel, instructions=None,
  using_slides_markdown=False, source_content=None, disconnect_checker=None)
  -> PresentationStructureModel` (157–211).
  **Data structure in/out: `PresentationOutlineModel` → `PresentationStructureModel`,
  whose only field is `slides: List[int]` (layout indices)** —
  `models/presentation_structure_model.py:4-6`. Layout selection carries **no prose
  and no evidence**; it is not a narrative stage.

#### A.8.4 `api/v1/ppt/endpoints/presentation.py` (3334 lines)

`create_presentation` — `POST /presentation/create` at **1634–1733**. Body params
(1636–1648): `content`, `n_slides`, `language`, `file_paths`, `tone`, `verbosity`,
`instructions`, `include_table_of_contents`, `include_title_slide`, `web_search`,
`generation_mode` (`"standard"|"smart"`), `community_design_ids`. Response model
`PresentationModel`. **It persists a `PresentationModel` row only (1698–1716) and
returns it (1733). It does NOT invoke the outline stage.** So `create` is the
"intent capture" step, not a deck build.

`prepare_presentation` — `POST /presentation/prepare` at **1783–1871**. Body:
`presentation_id`, `outlines: List[SlideOutlineModel]`, `layout: str`,
`title: Optional[str]`. Response model `PresentationPrepareResponse`
(162–165, `presentation_id`). Flow: fetch the presentation (1799–1801) →
`PresentationOutlineModel(slides=outlines)` (1803) → `_resolve_prepare_layout`
(1805–1807) → `generate_presentation_structure(...)` (1819–1826) **unless the layout
is `ordered`** → `_normalize_presentation_structure` (1828) → TOC insertion
(1834–1852) → persist `presentation.outlines`, `title`, `layout`, `fonts`,
`structure` (1854–1864) → mem0 store (1866–1869). **The outlines arrive from the
client** — the user reviewed/edited them on the outline page.

`export_existing_presentation` — `POST /presentation/{id}/export` at **1595–1631**;
calls `export_presentation(...)` at **1621**. It loads only the `PresentationModel`
(1617), not the slides.

`generate_presentation_handler` — 2627–3109, the one-shot `/generate` path:
- documents loaded → `additional_context` (2675–2683),
- `outline_messages = get_outline_messages(...)` (2696–2706),
- **`async for chunk in generate_ppt_outline(...)` at 2725–2742** — the outline stage,
- `dirtyjson.loads` → `normalize_outline_payload(...)` → `PresentationOutlineModel(**…)`
  at 2744–2759,
- `generate_presentation_structure(...)` at 2837–2846,
- TOC insertion at 2860–2878,
- `PresentationModel(...)` built with `outlines=presentation_outlines.model_dump()` at 2885–2902,
- **`get_slide_content_from_type_and_outline(...)` in batches of 10 at 2936–2949**,
- **`SlideModel(... content=slide_content ...)` at 2956–2964**,
- `export_presentation(...)` at **3042–3047**.

`stream_presentation` — `GET /presentation/stream/{id}` at 2224–2467:
- requires `presentation.structure` (2233–2237) and `presentation.outlines` (2238–2242),
- **`get_slide_content_from_type_and_outline(...)` at 2313–2321**,
- **`SlideModel(...)` at 2326–2334**, slides deleted and re-inserted at 2433–2444.
  **This path does not export** — it only persists slides.

`utils/export_utils.py:43` — `async export_presentation(presentation_id, title,
export_as, cookie_header=None) -> PresentationAndPath`. **It has no DB session and
no slides**; it builds a URL to the Next.js `/pdf-maker` service
(`_build_presentation_export_url`, line 27) and delegates
(`EXPORT_TASK_SERVICE.export_from_url`, line 59).

`api/v1/ppt/endpoints/outlines.py` — the second outline call site:
`stream_outlines` at 84–276, **`async for chunk in generate_ppt_outline(...)` at
170–183**, `normalize_outline_payload(...)` at 219, `presentation.outlines = …` at 248.

#### A.8.5 Models

- `models/presentation_outline_model.py`: `SlideOutlineModel` at 8–22 (**one field:
  `content: str`**, with a `field_validator` that trims to
  `MAX_OUTLINE_CONTENT_WORDS`); `PresentationOutlineModel` at 24–31
  (`slides: List[SlideOutlineModel]`, `max_length=MAX_NUMBER_OF_SLIDES`); `to_string`
  at 30–35 emits `## Slide {i+1}:\n  - Content: {slide}`.
- `models/presentation_structure_model.py`: `PresentationStructureModel` at 4–6 —
  `slides: List[int]`.
- `models/generate_presentation_request.py`: `GeneratePresentationRequest` at 8–46;
  `GenerateSmartPresentationRequest` at 49–70.
- `models/sql/presentation.py`: `PresentationModel` at 21; `outlines: Optional[dict]`
  (JSON) at 51; also `layout`, `structure`, `theme`, `fonts` JSON columns.
- `models/sql/slide.py`: `SlideModel` at 9; `content: dict` (JSON) at 26;
  **`properties: Optional[dict]` (JSON) at 29 — currently unused everywhere except a
  `copy.deepcopy` in `get_new_slide` (line 43). It is a free, already-migrated
  per-slide JSON slot.**
- `constants/presentation.py`: `MAX_NUMBER_OF_SLIDES = 50`;
  `MAX_OUTLINE_CONTENT_WORDS` default 100 (env-overridable).

#### A.8.6 The four-stage sequence, summarised

```
POST /presentation/create                     → persist intent (no outline)
GET  /presentation/outlines/stream/{id}       → generate_ppt_outline → persist outlines
PUT  /presentation/outlines/{id}              → user edits outlines
POST /presentation/prepare                   → layouts + structure + persist
GET  /presentation/stream/{id}                → slide content → SlideModel rows
POST /presentation/{id}/export                → export_presentation (HTTP to nextjs)

one-shot alternative:
POST /presentation/generate                   → generate_presentation_handler does
                                                 outlines → structure → slides → export
```

**Both the outline stage and the slide-content stage are duplicated across the
one-shot path and the review path.** Any W3 change must cover both.

### A.9 Contracts

`contracts/v1/manifest.json` — `"schema_version": 1` (line 2) and a `schemas` array of
23 entries (lines 5–29). `scripts/contracts.test.mjs:95` asserts
`manifest.schemas.length === 23`.

`contracts/v1/narrative-ir.schema.json` — `"$id": "gomrey:v1:NarrativeIR"`,
`"version": 1` (line 4), `additionalProperties: false` (line 7), required
`["narrative_id","artifact_id","revision","tenant_id","workspace_id","sections"]` (line 6).
`sections` items (lines 17–27): `required: ["heading","text"]`,
`additionalProperties: false`, properties `heading` (maxLength 500), `text`
(maxLength 20000), `claim_ids` (`array` of `string` maxLength 128).

`contracts/v1/design-ir.schema.json` — `components[].citation_ids` already exists
(`array` of `string` maxLength 128). **The DesignIR already has a per-node citation
id list; the NarrativeIR does not.** That asymmetry is the gap W3 closes.

`contracts/v1/artifact.schema.json` — the artifact record
(`artifact_id, tenant_id, workspace_id, artifact_type, title, current_revision,
created_at, status`); `status` enum includes `verifying`, `needs_repair`, `ready`.

`contracts/v1/citation.schema.json` — **shape MISMATCH with `gomrey/citations.py`.**
The contract's `locator` is a flat field namespace
(`page, paragraph, table, cell, region, url, dom_section, timestamp_ms,
transcript_span, workbook, sheet, range`) with **no `kind` discriminator**, while
`citations.make_locator` produces a **kind-tagged** dict
(`kind, source_id, unit_id, …, citation_id`). The two are not the same shape and
`citations.resolve` cannot consume the contract's `Citation` record.
**W3 must use the `citations.py` shape in the artifact, and this divergence is a
named risk (see §F.4).**

`contracts/v1/claim.schema.json` — flat record with `support_state` enum
(`SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED, DOES_NOT_ESTABLISH, UNRESOLVED,
SOURCE_UNAVAILABLE`) and `numeric_check` / `date_check` / `unit_check` enums.
**Also a shape mismatch with `gomrey/claims.Claim`** (which uses lowercase
`verification_state` values and has no `unit_check`).

### A.10 Test conventions

Gomrey tests live in `servers/fastapi/tests/test_gomrey_*.py` (flat, **not** in
`tests/unit/`; only `tests/unit/test_gomrey_compatibility.py` is in `tests/unit/`).
There are 26 `test_gomrey_*.py` files. Conventions, from
`tests/test_gomrey_citations.py`, `tests/test_gomrey_verification.py`,
`tests/test_gomrey_evidence_bundle.py`:

```python
"""Tests for the P08-G2 citation locators and resolver."""      # module docstring naming the grain

import pytest

from gomrey.citations import BrokenCitation, citation_id, make_locator, resolve


def _doc() -> dict:                     # module-level helper factories, no fixtures
    return { … }


def test_all_five_families_resolve() -> None:      # plain functions, -> None annotated
    doc = _doc()
    …
    assert resolved["resolved"] is True
    with pytest.raises(BrokenCitation):             # failure cases use pytest.raises
        …
```

- No classes, no `unittest`, no `monkeypatch` in the gomrey unit tests.
- Helpers are `_`-prefixed module functions returning fresh dicts per call
  (`_span`, `_bundle`, `_claim`, `_views` in `test_gomrey_verification.py:11-50`).
- Assertions are on exact values or membership (`assert result["verdict"] == "supported"`,
  `assert any(reason.startswith("quantity-mismatch") for reason in result["reasons"])`).
- `servers/fastapi/tests/conftest.py` provides `fake_async_session`, `snapshots_dir`,
  `load_snapshot` — **not used by the gomrey unit tests**.
- The Node-side contract tests live in `scripts/contracts.test.mjs`
  (`node --test`), with a `VALID` fixture map keyed by schema name
  (`scripts/contracts.test.mjs:11-101`) and `assert.equal(manifest.schemas.length, 23)`
  at line 95.

### A.11 What does **not** exist

| Asked-about thing | Reality |
|---|---|
| `ClaimContract` class | **Does not exist.** The claim contract is `contracts/v1/claim.schema.json` + `gomrey.claims.Claim`. |
| A deterministic unit gate | **Does not exist.** Only numbers + dates. `unit_check` exists only as a contract enum value. |
| A deterministic entity gate | **Does not exist.** |
| Any index / vector store feeding `retrieval_pipeline.retrieve` | **Does not exist.** `retrieve` takes caller-supplied candidate dicts. |
| Any production caller of `build_bundle` / `retrieve` / `make_locator` / `verify_claim` / `synthesize` | **Does not exist.** Only tests call them. |
| A `narrative` column on `presentations` | **Does not exist.** |
| Any persisted NarrativeIR | **Does not exist.** `gomrey.adapters.slides_to_narrative` computes one in memory but nothing calls it in production. |
| An ingest path that turns uploaded files into a Source IR | **Does not exist.** `DocumentsLoader` produces plain text (`additional_context`), not IR. |
| `DecisionRequest` / `DecisionResult` in `gomrey/decisions.py` | **Does not exist** in the code. They exist only as contract schemas `contracts/v1/decision-request.schema.json` and `decision-result.schema.json`. The code-level equivalents are `make_decision` / `synthesize`. |

---

## B. The narrowest correct integration point

### B.1 The point

**`servers/fastapi/utils/llm_calls/generate_presentation_outlines.py::generate_ppt_outline`
(line 251), at the message-construction seam `get_messages(...)` (line 376).**

Surrounding code, verbatim (lines 371–391):

```python
        emitted_content = False
        async for event in stream_generate_events(
            client,
            disconnect_checker=disconnect_checker,
            **get_generate_kwargs(
                model=model,
                messages=get_messages(
                    content,
                    n_slides,
                    language,
                    additional_context,
                    tone,
                    verbosity,
                    instructions,
                    include_title_slide,
                    include_table_of_contents,
                ),
                response_format=response_format,
                tools=([WebSearchTool()] if use_search_tool else None),
                stream=True,
            ),
        ):
```

Proposed new signature (keyword-only addition at the end; **every existing
positional call site keeps working unchanged**):

```python
async def generate_ppt_outline(
    content: str,
    n_slides: Optional[int],
    language: Optional[str] = None,
    additional_context: Optional[str] = None,
    tone: Optional[str] = None,
    verbosity: Optional[str] = None,
    instructions: Optional[str] = None,
    include_title_slide: bool = True,
    web_search: bool = False,
    include_table_of_contents: bool = False,
    emit_statuses: bool = False,
    disconnect_checker: Optional[DisconnectChecker] = None,
    *,
    evidence: Optional["NarrativePlan"] = None,   # NEW
):
```

`evidence` is a `gomrey.narrative.NarrativePlan` (a pure, deterministic plan built
by the caller from an `EvidenceBundle` + an assembled IR document). When `evidence`
is `None` the function behaves **exactly as today** — no prompt change, no schema
change, no behavioural change.

What you must pass in:

| Argument | Type | Where it comes from |
|---|---|---|
| `bundle` | `gomrey.evidence_bundle.EvidenceBundle` | the caller (endpoint); built by `gomrey.evidence_bundle.build_bundle(**bundle_payload)` from the request |
| `ir_document` | `dict[str, Any]` | the assembled Source IR (`gomrey.ir_provenance.assemble_ir` output shape); needed by `citations.resolve` |
| `tenant_id`, `workspace_id` | `str` | `gomrey.adapters.owner_to_scope(presentation.owner_id)` → `("tenant:<uuid>", "tenant:<uuid>:default")` |
| `n_slides` | `int` | resolved count; **must be an int when `evidence` is present** (see B.5) |

### B.2 Why this point and not another

**Rejected alternative 1 — the slide-content stage
(`generate_slide_content.py::get_slide_content_from_type_and_outline`, line 229).**
Rejected: (i) the response schema there is the **slide layout's** schema
(`_prepare_response_schema(slide_layout.json_schema)`, line 240), so the model is
not free to emit evidence fields without fighting the layout contract; (ii) it runs
**per slide, in parallel batches of 10** (`presentation.py:2929-2949`), so a
cross-slide conflict could never be detected — conflict detection is inherently a
whole-deck property; (iii) it runs *after* the narrative is already fixed, so an
unsupported claim would already be on the slide.

**Rejected alternative 2 — `generate_presentation_structure`
(line 157).** Rejected: it returns `PresentationStructureModel` = `List[int]` layout
indices (`models/presentation_structure_model.py:4-6`). It carries no prose and no
claims; there is nothing to bind.

**Rejected alternative 3 — `prepare_presentation` (`presentation.py:1784`).**
Rejected as the *producer* point: it receives `outlines: List[SlideOutlineModel]`
**from the client** (line 1786) — the user may have edited them on the outline
page. The narrative is already fixed by then. It is however the right place for a
*re-validation* (the outline the user edited may no longer match the evidence).

**Rejected alternative 4 — `create_presentation` (`presentation.py:1635`).**
Rejected: it only persists intent; no outline, no prose, no slides.

**Rejected alternative 5 — `stream_presentation` / `generate_presentation_handler`
slide creation.** Rejected as the producer point for the same reason as (1), plus:
the `stream_presentation` path reads the outline back from the DB
(`presentation.get_presentation_outline()`, `presentation.py:2247`), so the evidence
binding must have been persisted to survive.

**Why `generate_ppt_outline` is the narrowest correct point:**

1. **It is the single funnel.** Both outline call sites
   (`presentation.py:2725` and `outlines.py:170`) go through it. One hook covers
   the one-shot path and the review path.
2. **It is upstream of everything that matters.** Structure selection, slide content,
   slide persistence and export all descend from the outline. A claim that never
   entered the outline cannot reach a slide.
3. **It sits below the provider seam.** The seam is
   `get_client`/`get_model`/`stream_generate_events` (lines 265, 274, 371) and the
   message assembly `get_messages` (line 376). Adding an `evidence` parameter changes
   *what the model is told*, not *who the model is*. The provider seam is untouched.
4. **It respects `gomrey/decisions.py:16`** — *"Generated prose stays downstream of
   this structured record."* The deterministic plan is built first; the model only
   renders it.
5. **It is the smallest diff.** One new keyword parameter, plus two optional
   keyword parameters on `get_messages` / `get_user_prompt` / `get_system_prompt`.
   No change to the provider-facing response schema, no change to
   `SlideOutlineModel`, no change to `PresentationOutlineModel`.

### B.3 The two consequences that must accompany the hook

The hook alone is not sufficient. Two deterministic steps are required, and they
are the *same* on both the outline path and the export path:

**(B.3.1) Binding — plan node ↔ rendered slide.**
`gomrey.narrative.bind_slide_locators(plan, slides, *, toc_slides=0,
title_slide=True) -> list[dict]`. Positional by construction (see §C.5 for the
TOC remap). The output is written to the **already-existing, currently-unused**
`SlideModel.properties` JSON column (`models/sql/slide.py:29`) as
`{"citation_ids": [...], "evidence_status": "...", "reasons": [...]}`.
**No migration is needed for the per-slide binding.**

**(B.3.2) Assertion — export-time resolvability check.**
`gomrey.narrative.assert_exportable(narrative_ir, ir_document) -> None`, raising
`gomrey.citations.BrokenCitation` on the first unresolvable locator. Called
immediately before `export_presentation(...)`:
- `presentation.py:3042` (one-shot generate path),
- `presentation.py:1621` (`POST /presentation/{id}/export`).

For the export path to have an IR document to resolve against, the **IR resolution
context** must be persisted with the artifact. See §C.7 and §G.

### B.4 The call sequence with W3 enabled

```
POST /presentation/generate  (or  GET /outlines/stream/{id})
  │
  ├─ [NEW] evidence_bundle + source_ir supplied on the request
  │     └─ bundle = build_bundle(**request.evidence_bundle)          # gomrey.evidence_bundle
  │     └─ plan   = build_narrative_plan(bundle, request.source_ir, # gomrey.narrative  [NEW]
  │                                       plan_id=…, n_slides=…,
  │                                       tenant_id=…, workspace_id=…)
  │     └─ narrative_ir = build_narrative_ir(plan, artifact_id=…, revision=…)   # gomrey.narrative [NEW]
  │     └─ assert_exportable(narrative_ir, request.source_ir)      # gomrey.narrative [NEW] — FAILS FAST
  │
  ├─ generate_ppt_outline(…, evidence=plan)                          # [MODIFIED] hook
  │     └─ get_messages(…, evidence=plan) → get_user_prompt(…, evidence=plan)
  │           → the plan's closed fact base is injected
  │     └─ get_system_prompt(…, evidence=plan) → the evidence rules are added
  │     └─ provider seam unchanged: get_client / get_model / stream_generate_events
  │
  ├─ PresentationOutlineModel(**normalize_outline_payload(json, MAX_NUMBER_OF_SLIDES))
  │
  ├─ [NEW] bindings = bind_slide_locators(plan, presentation_outlines.slides,
  │                                         toc_slides=…, title_slide=…)
  │     └─ narrative_ir["sections"] ← bindings (positional, TOC-remapped)
  │     └─ assert_exportable(narrative_ir, ir_document)  # re-check after TOC remap
  │
  ├─ generate_presentation_structure(...)                            # unchanged
  ├─ get_slide_content_from_type_and_outline(...)                    # unchanged
  ├─ SlideModel(..., properties=bindings[i])                          # [MODIFIED] per-slide locators
  └─ export_presentation(...)                                        # unchanged
```

### B.5 The `n_slides` problem

`n_slides` may be `None` (auto-detect). With an evidence bundle the plan must know
how many slides it is describing, otherwise positional binding is undefined.
**Rule:** when `evidence` is present and `n_slides is None`,
`build_narrative_plan` derives the count deterministically as
`min(len(eligible_claims), MAX_NUMBER_OF_SLIDES)` (at least 1), and the plan
**fixes** that count. The prompt then states the exact slide count, and the
provider-facing schema is built with `get_presentation_outline_model_with_n_slides(n)`
(already the mechanism used at `generate_presentation_outlines.py:266-270`), so the
model cannot return a different number of slides.

---

## C. Proposed new module — `servers/fastapi/gomrey/narrative.py`

### C.1 Module contract

- **Pure.** No model calls, no network, no I/O, no app-layer imports. Imports only
  stdlib + intra-`gomrey` modules. (Matches every other `gomrey/` module.)
- **No provider.** The provider's opinion may be *supplied* to the deterministic
  verifier through the existing `verification.verify_claim(provider_verdict=…)`
  seam; `narrative.py` never obtains one itself.
- **Never fabricates a citation ID.** Every `citation_id` in the output originates
  from `citations.make_locator` over a locator supplied by a bundle span, and every
  such locator is proven resolvable by `citations.resolve` before it is emitted.
- **Fails closed.** An unresolvable locator, a span without a locator, a
  cross-project bundle, an insufficient bundle, or a conflict without an
  alternative all degrade to an explicit marker — never to a silent drop and never
  to an invented citation.

### C.2 Module docstring (proposed, verbatim)

```python
"""Evidence-bound narrative producer (W3).

Pure deterministic logic with no model calls, no network, and no app-layer
imports. This module turns an EvidenceBundle into a structured narrative
plan whose nodes carry resolvable citation locators, and it produces the
NarrativeIR that the artifact carries.

- evidence first: a plan is built from the bundle's spans, bound to
  claims, and classified by the P09-G2 verifier before any prose exists;
- the provider renders, it never decides: a plan node states its claims,
  their verdict, and its locators; the model may only phrase them;
- citation identity is minted by citations.make_locator and proven by
  citations.resolve; a locator that cannot be resolved degrades the node
  to an abstention, it is never replaced by a plausible one;
- conflicts are first-class: a node whose claims disagree is marked
  conflicted and carries both sides, it is never averaged into one;
- sufficiency is obeyed: an insufficient bundle produces a plan whose
  nodes may only say what is not known.

Failures raise the shared AdmissionError taxonomy from gateway.py;
unresolvable citations raise BrokenCitation from citations.py.
"""
```

### C.3 Public API

```python
# servers/fastapi/gomrey/narrative.py

NODE_STATUSES: frozenset[str]
# frozenset({"grounded", "abstained", "conflicted"})

ABSTENTION_MARKER: str
# "abstained"  — the literal value of evidence_status for a node with no
# assertable claim.

CONFLICT_MARKER: str
# "conflicted"


@dataclass(frozen=True)
class PlanNode:
    node_id: str                 # "n-1", "n-2", … (positional, deterministic)
    heading: str                 # audience-facing heading intent for the slide
    claim_ids: list[str]         # gomrey.claims.Claim.claim_id values, ordered
    citation_ids: list[str]      # gomrey.citations.citation_id values, ordered
    locators: list[dict[str, Any]]  # gomrey.citations.make_locator output, ordered
    status: str                  # NODE_STATUSES
    reasons: list[str]           # machine-readable reasons, e.g. "no-eligible-claim"


@dataclass(frozen=True)
class NarrativePlan:
    plan_id: str
    bundle_id: str
    tenant_id: str
    workspace_id: str
    nodes: list[PlanNode]
    conflicts: list[dict[str, Any]]     # from decisions.synthesize + bundle.contradictions
    omissions: list[dict[str, str]]     # from decisions.synthesize
    sufficiency: dict[str, Any]         # from evidence_bundle.sufficiency_check
    synthesis: dict[str, Any]           # from decisions.synthesize
    verdicts: dict[str, dict[str, Any]] # claim_id -> verification record
    digest: str                         # sha256 over the canonical plan


def build_narrative_plan(
    bundle: Any,
    ir_document: dict[str, Any],
    *,
    plan_id: str,
    tenant_id: str,
    workspace_id: str,
    n_slides: int,
    min_spans: int = 2,
    require_fresh: bool = True,
    provider_verdict: Optional[str] = None,
    provider_identity: Optional[dict[str, str]] = None,
) -> NarrativePlan:
    """Build the deterministic evidence→narrative plan.

    `bundle` is a gomrey.evidence_bundle.EvidenceBundle.
    `ir_document` is an assembled Source IR (gomrey.ir_provenance.assemble_ir
    shape) used to prove every locator resolvable.
    `provider_verdict`/`provider_identity` are forwarded verbatim to
    gomrey.verification.verify_claim; a provider may never upgrade a
    deterministic failure (P09-G2 semantics, unchanged).
    """


def render_plan_context(plan: NarrativePlan) -> str:
    """Render the closed fact base injected into the provider prompt.

    Contains, per node, the node heading, the verified claim texts, the
    citation IDs, and the node status. Contains NO number or date that is
    not present in a verified claim text.
    """


def build_narrative_ir(
    plan: NarrativePlan,
    *,
    narrative_id: str,
    artifact_id: str,
    revision: int,
    language: Optional[str] = None,
) -> dict[str, Any]:
    """Emit the NarrativeIR document (contracts/v1/narrative-ir.schema.json v2).

    Each section is one plan node and carries `citation_locators` and
    `evidence_status` in addition to heading/text/claim_ids.
    """


def bind_slide_locators(
    plan: NarrativePlan,
    slides: list[Any],
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> list[dict[str, Any]]:
    """Bind plan nodes to rendered slides; returns one dict per slide.

    Each dict: {"citation_ids": [...], "evidence_status": str, "reasons": [...]}.
    Positional: slide i ↔ plan node i, after the deterministic TOC remap
    (TOC slides are inserted at index 1 when a title slide is present,
    index 0 otherwise — see utils/outline_utils.get_presentation_outline_model_with_toc
    and api/v1/ppt/endpoints/presentation.py::_insert_toc_layouts).
    A slide with no corresponding node (TOC, or a slide beyond the plan)
    gets status "abstained" and no citation IDs.
    """


def assert_exportable(
    narrative_ir: dict[str, Any],
    ir_document: dict[str, Any],
) -> None:
    """Export-time assertion: every locator in the artifact must resolve.

    Raises gomrey.citations.BrokenCitation on the first unresolvable
    locator, naming the citation ID and the defect. Returns None otherwise.
    """


def narrative_digest(narrative_ir: dict[str, Any]) -> str:
    """Reproducible sha256 digest over the canonical NarrativeIR."""
```

### C.4 `build_narrative_plan` — step by step

```
1.  sufficiency = evidence_bundle.sufficiency_check(bundle, min_spans=min_spans,
                                                      require_fresh=require_fresh)
2.  For each span in bundle.spans (keyed by span["citation_id"]):
      a. locator_input = span.get("locator")
         if locator_input is None → the span is not citable; skip it and record
             omission {"span_id": …, "reason": "span-without-locator"}.
      b. locator = citations.make_locator(locator_input["kind"],
                                          **{k: v for k, v in locator_input.items()
                                             if k != "kind"})
         → any BrokenCitation here means the SPAN is malformed; it is recorded as
           an omission with the defect name, never repaired.
      c. INVARIANT CHECK: locator["citation_id"] == span["citation_id"]
         → mismatch ⇒ AdmissionError("normalization_failure", …).
           This is the single guard that makes a fabricated citation impossible.
      d. citations.resolve(locator, ir_document)
         → BrokenCitation ⇒ omission {"span_id": …, "reason": "unresolvable-citation:…"};
           the span never becomes a citable claim.
3.  claim = claims.make_claim(claim_id=f"cl-{span_id}", text=span_text,
                               tenant_id=bundle.tenant_id, workspace_id=bundle.workspace_id,
                               evidence_refs=[span_id],
                               created_at=…, updated_at=…,
                               derivation={"kind": "derived", "source": "evidence-span"})
      → claim_id derivation must be deterministic: "cl-" + span_id.
4.  binding = claims.bind_claim_to_bundle(claim, bundle, require_fresh=require_fresh)
5.  evidence_views = {span_id: {"stance": span.get("stance", "supports"),
                                "text": span_text}}
6.  verdict = verification.verify_claim(claim, binding, bundle,
                                        evidence_views=evidence_views,
                                        provider_verdict=provider_verdict,
                                        provider_identity=provider_identity)
      → the P09-G2 record, unmodified.
7.  decision = decisions.make_decision(decision_id=f"dec-{bundle.bundle_id}",
                                        question=bundle.query,
                                        tenant_id=…, workspace_id=…,
                                        claim_ids=[c.claim_id for c in claims],
                                        evidence_ids=[span ids],
                                        alternatives=[…derived from contradictions…])
8.  synthesis = decisions.synthesize(decision, verdicts)
9.  Node assignment: node i receives claims[i::n_slides] (stride, order-stable).
      A node whose claim list is empty → status "abstained",
      reasons ["no-eligible-claim"] (+ any synthesis reason).
      A node whose claims include a "partially_supported" or "contradicted" claim
      → status "conflicted", and the conflicting claim IDs are recorded.
      Otherwise → status "grounded".
10. Locators per node: the locators of its claims' spans, in claim order, with
    duplicates removed by citation_id. A node can only be "grounded" if every
    one of its locators resolved in step 2d.
11. digest = sha256 over the canonical JSON of the plan (same convention as
    claims.claim_digest / evidence_bundle.bundle_digest).
```

**`alternatives` derivation (step 7).** `decisions.make_decision` requires each
alternative to have a non-empty `"option"` (decisions.py:180–182), and
`decisions.synthesize` withholds everything when a conflict exists and no
alternative is supplied (224–235). To *surface* a conflict rather than collapse
the whole deck into abstention, the plan derives one alternative per
`bundle.contradictions` entry:
`{"option": <contradiction description>, "span_ids": [...]}`. The conflict then
appears in `synthesis["conflicts"]` **and** in the affected node's
`status = "conflicted"`, and the node's prompt block instructs the producer to
present both sides.

### C.5 `bind_slide_locators` — the TOC remap

`get_presentation_outline_model_with_toc` (`utils/outline_utils.py:84`) inserts TOC
outlines at `insertion_index = 1 if title_slide else 0` (line 94);
`_insert_toc_layouts` (`api/v1/ppt/endpoints/presentation.py:349`) inserts the TOC
**layouts** at the same index (line 358). So the final slide list is:

```
index:        0            1 .. 1+n_toc-1            1+n_toc .. end
content:      title slide  TOC slides                plan nodes 0 .. n-1
```

Mapping (deterministic, no model involvement):

```python
def _plan_index_for_slide(i, *, n_toc, title_slide):
    insertion = 1 if title_slide else 0
    if i < insertion:
        return i - 0 if not title_slide else 0   # title slide carries no plan node
    if i < insertion + n_toc:
        return None                              # TOC slide: no node
    return i - n_toc
```

**A title slide carries no plan node** (the current outline contract makes slide 0
the title: `generate_presentation_outlines.py:100`, *"First slide title must be the
same as the presentation title"*). So when `include_title_slide` is true, plan
node 0 maps to slide 1, not slide 0. The exact rule must be implemented once, in
`bind_slide_locators`, and unit-tested against the TOC insertion helper.

### C.6 `render_plan_context` — the closed fact base

```
[EVIDENCE PLAN 1/4] status=grounded
Heading: Revenue growth
- CLAIM: Revenue grew 12 percent in 2024.
- CITATION: cite-e6d4be86e625ce6e
[EVIDENCE PLAN 2/4] status=abstained
Heading: Cost structure
- NO ASSERTABLE CLAIM. State what is not known. Do not assert.
[EVIDENCE PLAN 3/4] status=conflicted
Heading: Headcount
- CLAIM: Headcount grew 8 percent in 2024. (cite-e6d4be86e625ce6e)
- CLAIM: Headcount fell 3 percent in 2024. (cite-9a11c0d2ee4477b1)
- CONFLICT: present both figures; do not pick one.
```

The matching system-prompt rules (to be added to `get_system_prompt` only when
`evidence` is present):

```
Evidence rules:
- Every factual sentence must come from a CLAIM line in the evidence plan.
- Never write a number or date that is not in a CLAIM line.
- A plan block marked "abstained" has no claim: say what is not known.
- A plan block marked "conflicted": present both sides, do not pick one.
- Never write a citation, footnote, source list, URL or locator; the system
  attaches citations deterministically.
```

**Note the interaction with existing rules:** `generate_presentation_outlines.py:158`
already says *"Do not include URLs, hyperlinks, citations, footnotes, references, or
source lists in slide outlines."* and line 163 says *"do not invent citations."*
The evidence rules **reinforce** both; they do not relax them. The citation IDs in
the fact base are an internal handle for the producer's grounding, not an instruction
to print them.

**The provider-facing response schema is NOT changed.** The model is not asked to
emit `citation_ids`, `evidence_node_id`, or any other field. `SlideOutlineModel`
keeps its single `content: str` field (`models/presentation_outline_model.py:8-22`).
This is what keeps the provider seam and the outline contract untouched.

### C.7 `build_narrative_ir` and persistence

`build_narrative_ir` emits:

```json
{
  "narrative_id": "…",
  "artifact_id": "…",
  "revision": 1,
  "tenant_id": "…",
  "workspace_id": "…",
  "language": "en",
  "sections": [
    {
      "heading": "Revenue growth",
      "text": "…",
      "claim_ids": ["cl-cite-e6d4be86e625ce6e"],
      "citation_locators": [
        {"kind": "document", "citation_id": "cite-e6d4be86e625ce6e",
         "source_id": "s-1", "unit_id": "u-1", "page_no": 4}
      ],
      "evidence_status": "grounded"
    },
    {
      "heading": "Cost structure",
      "text": "…",
      "claim_ids": [],
      "citation_locators": [],
      "evidence_status": "abstained"
    }
  ]
}
```

**Persistence.** `SlideModel.properties` (`models/sql/slide.py:29`) is a free,
already-migrated per-slide JSON slot and carries the per-slide binding. The
**whole** NarrativeIR and the IR resolution context must live somewhere the
export path can read. Two options:

- **B.7-a (recommended, no migration):** the NarrativeIR + a **bounded IR
  resolution context** (only the units referenced by the plan's locators, plus
  `original_digest`) are stored on the presentation. The only free JSON columns
  are `PresentationModel.outlines` (taken by the outline model), `.layout`,
  `.structure`, `.theme`, `.fonts` — all taken. **So a new column is required**:
  `PresentationModel.narrative: Optional[dict]` (JSON, nullable), added by an
  **additive** alembic revision whose `down_revision` is the current head
  `026c0ba8b35c` (`alembic/versions/026c0ba8b35c_add_async_task_payload_and_unified_api_.py`).
  Precedent: `alembic/versions/f42ad4074449_add_theme_column_to_presentations.py`
  adds a JSON column to `presentations` in exactly this way. The repo's migration
  discipline (`tests/test_gomrey_migration_discipline.py`) forbids only
  `drop_table`/`drop_column` in `upgrade()`, so an added nullable column is legal.
- **B.7-b (out of scope for W3):** store the NarrativeIR in the `gomrey.seams`
  `CanonicalStore` (a Protocol with `MemoryCanonicalStore`, `gomrey/seams.py:19`).
  This keeps the DB untouched but adds a second persistence substrate and a second
  authority for artifact state — a direct violation of "the artifact IR's
  authority" must not change.

**W3 chooses B.7-a.** The persisted column carries:

```json
{
  "narrative_ir": { …NarrativeIR v2… },
  "ir_context": {
    "original_digest": "…",
    "units": [ …only the units referenced by the plan's locators… ]
  },
  "plan_digest": "…"
}
```

`ir_context.units` is **bounded by the plan's locator count**, not by the size of
the corpus — the export assertion only ever needs the units it must resolve
against.

### C.8 `assert_exportable` — the export-time assertion

```python
def assert_exportable(narrative_ir, ir_document):
    for section in narrative_ir.get("sections", []):
        for locator in section.get("citation_locators", []):
            citations.resolve(locator, ir_document)   # raises BrokenCitation
    # also: every citation_id must be one the plan minted
    return None
```

`citations.resolve` already performs every check W3 needs: unit existence, source
match, page agreement, retrieval-snapshot agreement, timestamp containment, bbox
agreement. **W3 does not re-implement any of it** — it only calls it, which is
exactly why the guarantee "no artifact can contain a citation that `citations.py`
cannot resolve" is true by construction.

**Second check (in addition to resolvability):** the union of every
`citation_ids` in the narrative IR must be a subset of the bundle's span
`citation_id`s. This catches a citation ID that resolves against the IR but was
never minted from a bundle span (e.g. injected by a caller). It raises
`AdmissionError("normalization_failure", …)` rather than `BrokenCitation`, because
it is a normalisation defect, not a resolution defect.

---

## D. Contract extension

### D.1 The additive change to `contracts/v1/narrative-ir.schema.json`

`version` 1 → **2**; two new **optional** properties on the `sections[]` item;
one new root `$defs` entry.

```json
{
  "$id": "gomrey:v1:NarrativeIR",
  "title": "NarrativeIR",
  "version": 2,
  "type": "object",
  "required": ["narrative_id", "artifact_id", "revision", "tenant_id", "workspace_id", "sections"],
  "additionalProperties": false,
  "properties": {
    "narrative_id": { "type": "string", "minLength": 1, "maxLength": 128 },
    "artifact_id": { "type": "string", "minLength": 1, "maxLength": 128 },
    "revision": { "type": "integer", "minimum": 1 },
    "tenant_id": { "type": "string", "minLength": 1, "maxLength": 128 },
    "workspace_id": { "type": "string", "minLength": 1, "maxLength": 128 },
    "language": { "type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$" },
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["heading", "text"],
        "additionalProperties": false,
        "properties": {
          "heading": { "type": "string", "maxLength": 500 },
          "text": { "type": "string", "maxLength": 20000 },
          "claim_ids": { "type": "array", "items": { "type": "string", "maxLength": 128 } },
          "citation_locators": {
            "type": "array",
            "items": { "$ref": "#/$defs/CitationLocator" }
          },
          "evidence_status": {
            "type": "string",
            "enum": ["grounded", "abstained", "conflicted"]
          }
        }
      }
    }
  },
  "$defs": {
    "CitationLocator": {
      "type": "object",
      "required": ["kind", "citation_id"],
      "additionalProperties": false,
      "oneOf": [
        { "required": ["source_id", "unit_id", "page_no"],
          "properties": { "kind": { "const": "document" }, "page_no": { "type": "integer", "minimum": 1 } } },
        { "required": ["source_id", "unit_id", "canonical_url", "retrieved_at"],
          "properties": { "kind": { "const": "web" } } },
        { "required": ["source_id", "unit_id", "video_id", "start", "end"],
          "properties": { "kind": { "const": "video" },
                          "start": { "type": "number", "minimum": 0 },
                          "end": { "type": "number", "minimum": 0 } } },
        { "required": ["source_id", "unit_id", "workbook", "sheet", "cell"],
          "properties": { "kind": { "const": "spreadsheet" } } },
        { "required": ["source_id", "unit_id", "bbox"],
          "properties": { "kind": { "const": "image" },
                          "bbox": { "type": "array", "items": { "type": "number" } } } }
      ],
      "properties": {
        "kind": { "type": "string", "enum": ["document", "web", "video", "spreadsheet", "image"] },
        "citation_id": { "type": "string", "minLength": 1, "maxLength": 128 },
        "source_id": { "type": "string", "maxLength": 128 },
        "unit_id": { "type": "string", "maxLength": 128 },
        "page_no": { "type": "integer", "minimum": 1 },
        "canonical_url": { "type": "string", "maxLength": 2000 },
        "retrieved_at": { "type": "string", "maxLength": 64 },
        "video_id": { "type": "string", "maxLength": 128 },
        "start": { "type": "number", "minimum": 0 },
        "end": { "type": "number", "minimum": 0 },
        "workbook": { "type": "string", "maxLength": 200 },
        "sheet": { "type": "string", "maxLength": 200 },
        "cell": { "type": "string", "maxLength": 64 },
        "bbox": { "type": "array", "items": { "type": "number" } },
        "paragraph": { "type": "integer", "minimum": 1 },
        "table_cell": { "type": "string", "maxLength": 64 },
        "region_bbox": { "type": "string", "maxLength": 200 },
        "section": { "type": "string", "maxLength": 500 },
        "transcript_segment_id": { "type": "string", "maxLength": 128 },
        "scene_id": { "type": "string", "maxLength": 128 },
        "keyframe_id": { "type": "string", "maxLength": 128 },
        "range": { "type": "string", "maxLength": 100 },
        "table": { "type": "string", "maxLength": 200 }
      }
    }
  }
}
```

### D.2 Why this shape

- The `oneOf` branches mirror `citations.make_locator`'s per-kind required sets
  (`gomrey/citations.py:51-57`) **exactly**, so a locator that the contract
  accepts is a locator the code can build, and vice versa.
- `oneOf` with `const` on `kind` matches **exactly one** branch — which is what
  `validate-contracts.mjs:139-142` requires (`count === 1`).
- `$defs` + `$ref` is supported: `SUPPORTED_KEYWORDS` includes `$defs` and `$ref`
  (`scripts/validate-contracts.mjs:11-35`), and only local `#/$defs/...` refs are
  permitted (`validate-contracts.mjs:69-74`).
- **`minItems` / `maxItems` are NOT in `SUPPORTED_KEYWORDS`** — they must not be
  used. The 4-element `bbox` shape is therefore enforced only in code
  (`citations.py:75-77`), not by the contract. This is a known, recorded gap.
- The optional fields mirror `make_locator`'s optional tuple
  (`citations.py:62-64`) exactly.
- `citation_id` is `minLength 1, maxLength 128`; the minted form is
  `"cite-" + 16 hex` = 21 characters (`citations.py:43`).

### D.3 The schema-version bump — and the hard constraint it hits

**Two version numbers exist and they are different things:**

| Version | Where | Current | Bump? |
|---|---|---|---|
| contract-set version | `contracts/v1/manifest.json:2` `"schema_version"` | `1` | **→ `2`** |
| per-schema version | `contracts/v1/narrative-ir.schema.json:4` `"version"` | `1` | **→ `2`, but this breaks a validator** |

`scripts/validate-contracts.mjs:176`:
```js
if (schema.version !== 1) errors.push(`contracts: ${entry.name} version must be 1`);
```
`scripts/contracts.test.mjs:146` asserts `checkContracts()` returns `[]`.
**Bumping the NarrativeIR's own `version` to 2 without touching the validator makes
`checkContracts` fail and therefore breaks `npm test`.**

Two acceptable resolutions — **both must be chosen explicitly; there is no
zero-change option**:

- **D.3-a (recommended).** Relax the pin to a supported set:
  `if (![1, 2].includes(schema.version)) errors.push(...)` — a **one-line** change
  in `scripts/validate-contracts.mjs:176`, plus `narrative-ir.schema.json`
  `"version": 2` and `manifest.json` `"schema_version": 2`. The validator then
  permits exactly one v2 schema and continues to reject anything else.
- **D.3-b.** Leave `narrative-ir.schema.json`'s `"version"` at `1` and bump only
  `manifest.json`'s `"schema_version"` to `2`. Zero validator risk, but the
  per-schema version no longer distinguishes the extended shape from the original.

**W3 chooses D.3-a.** Whatever is chosen, `manifest.schemas.length` stays **23**
(the schema *count* does not change — only one file is edited), so
`scripts/contracts.test.mjs:95` needs no change.

### D.4 How the existing single-document form stays valid

1. **`sections[]` `required` stays `["heading","text"]`.** `citation_locators` and
   `evidence_status` are **not** added to `required`. A pre-W3 NarrativeIR
   document therefore still validates unchanged.
2. **`additionalProperties: false` still holds.** The two new keys are now
   *known* properties, so a document carrying them validates; a document carrying
   an *unknown* key still fails. This is what makes the extension additive rather
   than a relaxation.
3. **The existing fixture stays valid.** `scripts/contracts.test.mjs:76-78`:
   ```js
   NarrativeIR: {
     narrative_id: "r-1", artifact_id: "a-1", revision: 3, tenant_id: TENANT, workspace_id: WORKSPACE,
     sections: [{ heading: "Summary", text: "Growth continued.", claim_ids: ["c-1"] }],
   },
   ```
   has no `citation_locators` and no `evidence_status` → still valid under v2.
4. **`gomrey.adapters.slides_to_narrative` output stays valid.** `adapters.py:91-98`
   emits sections with only `heading`, `text`, `claim_ids` → still valid under v2.
5. **`gomrey.contracts.NarrativeSection`** (`contracts.py:124-127`) is a Pydantic
   record with `extra="forbid"` (`contracts.py:16`). It mirrors the *old* shape and
   is **not** changed by W3; the new fields live in the JSON contract only. If
   W3 later wants a Pydantic mirror, it must be a **new** record type (e.g.
   `NarrativeSectionV2`) rather than a mutation of `NarrativeSection`, so existing
   Pydantic consumers are unaffected.

---

## E. Test plan

### E.1 New file: `servers/fastapi/tests/test_gomrey_narrative.py`

Conventions copied from `tests/test_gomrey_citations.py` and
`tests/test_gomrey_verification.py`: module docstring naming the grain, plain
`def test_…() -> None` functions, `_`-prefixed module-level helper factories
returning fresh dicts, `pytest.raises` for failure cases, no classes, no
fixtures, no `monkeypatch`.

Helpers (proposed):

```python
def _ir_document() -> dict: …          # one unit per locator kind, like test_gomrey_citations._doc()
def _locator(kind: str = "document") -> dict: …   # citations.make_locator(...)
def _bundle(**overrides) -> EvidenceBundle: …     # evidence_bundle.build_bundle(**…)
def _plan(bundle, ir, **overrides) -> NarrativePlan: …  # narrative.build_narrative_plan(…)
```

### E.2 The five mandated test cases

| # | Test name | Arrangement | Assertions |
|---|---|---|---|
| 1 | `test_supported_claim_yields_resolvable_locator` | A bundle with two spans, each carrying a `document` locator over a unit that exists in the IR document; each span's `citation_id` equals `citations.make_locator(...)["citation_id"]`; the span text contains the claim's number and date. `build_narrative_plan(...)` with `n_slides=1`. | `plan.nodes[0].status == "grounded"`; `plan.nodes[0].citation_ids` is non-empty; every locator in `plan.nodes[0].locators` satisfies `citations.resolve(locator, ir)["resolved"] is True`; `plan.nodes[0].citation_ids == [locator["citation_id"] for locator in …]`; `plan.verdicts[claim_id]["verdict"] == "supported"`; the emitted `narrative_ir["sections"][0]["evidence_status"] == "grounded"`. |
| 2 | `test_unresolved_claim_yields_abstention_marker_and_no_fabricated_citation` | A claim that cannot be verified: a bundle whose only span has `evidence_refs == []` on the claim (i.e. the span is not bound) **or** the span's evidence view is absent — so the P09 verdict is `unresolved` / `does_not_establish`. Simplest deterministic construction: a bundle with **one** span (so `sufficiency_check` → `insufficient` with `too-few-spans`) **and** a claim bound to a span whose supporting text does not contain the claim's number. | `plan.nodes[0].status == "abstained"`; `plan.nodes[0].status == narrative.ABSTENTION_MARKER`; `plan.nodes[0].citation_ids == []`; `plan.nodes[0].locators == []`; `plan.nodes[0].claim_ids == []`; `"no-eligible-claim" in plan.nodes[0].reasons`; **the union of every `citation_ids` across the whole plan is a subset of the bundle's span citation IDs**; the emitted `narrative_ir` contains **no** `citation_locators` entry whose `citation_id` is not in the bundle's span ID set; and `assert_exportable(narrative_ir, ir)` does not raise. |
| 3 | `test_contradictory_pair_is_flagged` | Two spans over two different units, both with `stance` values `"supports"` and `"contradicts"` against the same claim text; the bundle also carries one `contradictions` entry whose `span_ids` name both spans (so `build_bundle` accepts it — `evidence_bundle.py:75-80`). | `plan.conflicts` is non-empty; `plan.nodes[0].status == "conflicted"` (`narrative.CONFLICT_MARKER`); the node's `reasons` name the conflict; `plan.nodes[0].citation_ids` contains **both** citation IDs (both sides are surfaced, neither is dropped); the emitted `narrative_ir["sections"][0]["evidence_status"] == "conflicted"`; `plan.synthesis["conflicts"]` is non-empty. |
| 4 | `test_unresolvable_locator_fails_export_assertion` | Build a valid plan, then **tamper** with the emitted `narrative_ir`: point a section's `citation_locators[0]["unit_id"]` at a unit that is not in the IR document (or change `page_no` so it disagrees with the unit's `page_no`). | `with pytest.raises(BrokenCitation): narrative.assert_exportable(tampered_ir, ir)`; the exception's `citation_id` is the tampered locator's ID; and the **untampered** `narrative_ir` passes `assert_exportable` without raising. Also assert that `assert_exportable` returns `None` on the good document. |
| 5 | `test_provider_cannot_overrule_deterministic_gate` | Same arrangement as (1) but the supporting span text does **not** contain the claim's number, and `build_narrative_plan(..., provider_verdict="supported", provider_identity={"provider": "challenger-x", "model_revision": "r1"})`. | `plan.verdicts[claim_id]["verdict"] == "does_not_establish"`; `plan.verdicts[claim_id]["provider_overruled"] is True`; `"provider-overruled-by-policy" in plan.verdicts[claim_id]["reasons"]`; the claim is **not** included in the synthesis (`claim_id not in plan.synthesis["included_claims"]`); the node carrying it is **not** `"grounded"` — it is `"abstained"`; **and no locator for that claim is emitted**. Additionally assert that the P09 fabric is untouched: `verify_claim(..., provider_verdict="supported", provider_identity={"provider":"x"})` (missing `model_revision`) still raises `AdmissionError`. |

### E.3 Supporting tests (same file)

| # | Test name | Assertion |
|---|---|---|
| 6 | `test_insufficient_bundle_makes_every_node_abstained` | `sufficiency_check` → `insufficient` ⇒ every `plan.nodes[*].status == "abstained"`, every `citation_ids == []`. |
| 7 | `test_plan_context_exposes_only_verified_claim_quantities` | Every number/date token in `render_plan_context(plan)` appears in some verified claim text. Uses the same regexes as `gomrey.verification` (`_NUMBER_RE`/`_DATE_RE` are private; the test re-declares them locally, as `test_gomrey_verification.py:85-87` already does with `check_quantity_agreement`). |
| 8 | `test_slide_binding_is_positional_and_toc_aware` | With `toc_slides=1, title_slide=True`, `bind_slide_locators(plan, slides)` returns, for slide 0 → no plan node (`"abstained"`), slide 1 → TOC (`"abstained"`), slide 2 → plan node 0 (`"grounded"`). With `toc_slides=0, title_slide=True`, slide 1 → plan node 0. |
| 9 | `test_narrative_ir_validates_against_contract_v2` | Load `contracts/v1/narrative-ir.schema.json` (path: `Path(__file__).resolve().parents[3] / "contracts" / "v1" / "narrative-ir.schema.json"` — `jsonschema` 4.26.0 is already a dependency in `pyproject.toml` and is installed in `.venv`) and validate the emitted `narrative_ir` with `jsonschema.Draft202012Validator`. Assert no errors. Also assert the **pre-W3** form (sections with only `heading`/`text`/`claim_ids`) still validates under v2. |
| 10 | `test_conflict_without_alternative_abstains_the_decision` | A plan built from a bundle whose contradictions cannot be expressed as alternatives ⇒ `plan.synthesis["status"] == "abstained"` and `plan.synthesis["reasons"] == ["conflict-requires-alternative"]` (mirrors `decisions.py:224-235`). |
| 11 | `test_span_without_locator_is_omitted_never_invented` | A span with no `locator` ⇒ it is recorded as an omission (`"span-without-locator"`) and produces **no** claim, **no** citation ID and **no** locator. |
| 12 | `test_span_citation_id_mismatch_is_refused` | A span whose `citation_id` differs from `make_locator(...)["citation_id"]` ⇒ `AdmissionError` with code `normalization_failure`. **This is the anti-fabrication test.** |
| 13 | `test_plan_is_deterministic` | Two identical calls produce byte-identical `plan.digest` and identical `narrative_digest`. |

### E.4 Contract-side tests: `scripts/contracts.test.mjs`

Two new `node --test` cases:

```js
test("narrative ir accepts per-node citation locators", async () => {
  const { schemas } = await loadSchemas();
  const ir = {
    narrative_id: "r-2", artifact_id: "a-1", revision: 1, tenant_id: TENANT, workspace_id: WORKSPACE,
    sections: [{
      heading: "Revenue", text: "Growth continued.", claim_ids: ["c-1"],
      citation_locators: [{ kind: "document", citation_id: "cite-abc", source_id: "s-1", unit_id: "u-1", page_no: 4 }],
      evidence_status: "grounded",
    }],
  };
  assert.deepEqual(validateValue(structuredClone(ir), schemas.NarrativeIR, schemas.NarrativeIR), []);
});

test("narrative ir single-document form stays valid after the v2 extension", async () => {
  const { schemas } = await loadSchemas();
  assert.deepEqual(validateValue(structuredClone(VALID.NarrativeIR), schemas.NarrativeIR, schemas.NarrativeIR), []);
  // a locator with the wrong per-kind required set is rejected
  const bad = structuredClone(VALID.NarrativeIR);
  bad.sections[0].citation_locators = [{ kind: "document", citation_id: "cite-x", source_id: "s-1" }];
  assert.ok(validateValue(bad, schemas.NarrativeIR, schemas.NarrativeIR).length > 0);
});
```

`scripts/contracts.test.mjs:95`'s `manifest.schemas.length === 23` assertion is
**unchanged** (no schema is added or removed).

### E.5 Regression gates

| Gate | Command |
|---|---|
| Gomrey-scoped pytest | `pytest servers/fastapi/tests/test_gomrey_*.py` |
| FastAPI suite | `pytest servers/fastapi/tests` |
| Node contract suite | `node --test scripts/contracts.test.mjs` |
| Contract validator | `node scripts/validate-contracts.mjs` |
| Migration discipline | `pytest servers/fastapi/tests/test_gomrey_migration_discipline.py` |
| Import hygiene | `python -c "import ast,pathlib; …"` — assert `gomrey/narrative.py` imports nothing from `models`/`utils`/`api`/`services` |

---

## F. Risks and non-goals

### F.1 What could break

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **The per-schema `version` pin.** `scripts/validate-contracts.mjs:176` hard-requires `version === 1`; `contracts.test.mjs:146` asserts `checkContracts()` is clean. Bumping NarrativeIR to v2 without relaxing the pin breaks `npm test`. | **High** (breaks CI) | §D.3: choose D.3-a (one-line relaxation) explicitly and add a `contracts.test.mjs` case that a v2 schema is accepted and a v3 schema is not. |
| R2 | **The `contracts/v1/citation.schema.json` shape mismatch.** The contract's flat `locator` namespace has no `kind` discriminator and is not consumable by `citations.resolve`. If the artifact is ever validated against `Citation` rather than `NarrativeIR`, the locators fail. | **High** (silent corruption) | W3's extension uses the **`gomrey/citations.py` shape**, not the `Citation` contract shape, and §C.8 adds the "citation ID ⊆ bundle span IDs" check. The two shapes must be reconciled in a separate grain. |
| R3 | **TOC insertion shifts slide indices.** `get_presentation_outline_model_with_toc` (`utils/outline_utils.py:84-94`) and `_insert_toc_layouts` (`presentation.py:349-360`) insert at index 1 (or 0). Positional binding silently mis-attributes citations if the remap is not applied. | **High** (wrong citation on the wrong slide — worse than no citation) | `bind_slide_locators` owns the remap in one place; test 8 pins it against the real insertion helper. |
| R4 | **A user edits the outline on the review page.** `PUT /outlines/{id}` (`outlines.py:59`) lets the client replace the outline wholesale; `prepare` (`presentation.py:1783`) accepts `outlines: List[SlideOutlineModel]` from the client. The evidence binding computed at generation time no longer describes the deck. | **High** | Re-run `assert_exportable` and the quantity gate at **export** time, not only at generation time. The export assertion must re-derive the binding from the persisted plan and the persisted outline, and fail (or mark the deck `needs_repair`) if the outline no longer matches. **W3 must specify this explicitly; it is not optional.** |
| R5 | **Provider drift.** The model may write a number or date that is not in any verified claim. The quantity gate (`check_quantity_agreement`) only fires on *claims*, not on the final prose. | Medium | `render_plan_context` exposes only verified claim texts; the evidence rules forbid other quantities; and a post-render check re-runs `check_quantity_agreement` per slide against the node's claim texts. |
| R6 | **Schema drift between the Pydantic and JSON contracts.** `gomrey.contracts.NarrativeSection` (`contracts.py:124`) uses `extra="forbid"` and mirrors the v1 shape. If someone extends it in place, the v1 JSON contract and the Pydantic record diverge. | Medium | §D.4 item 5: extend with a **new** record type, never mutate `NarrativeSection`. |
| R7 | **The bundle's `citation_id` is not the locator's `citation_id`.** `build_bundle` accepts any span ID; `bind_claim_to_bundle` matches on `citation_id or span_id`. A bundle built elsewhere could carry IDs that no locator hashes to, and the binding would silently reference nothing. | Medium | The explicit equality check in `build_narrative_plan` step 2c (test 12). |
| R8 | **The first production import edge `app → gomrey`.** `gomrey/` has zero production callers today. An accidental import of `models/` or `utils/` into `gomrey/narrative.py` would invert the layering permanently. | Medium | An import-hygiene test (§E.5) plus the module's own docstring rule. |
| R9 | **Additive alembic migration.** Adding `presentations.narrative` needs a revision on top of head `026c0ba8b35c`, and the migration-discipline test forbids `drop_table`/`drop_column` in `upgrade()`. | Medium | The migration is additive-only by construction; copy `f42ad4074449_add_theme_column_to_presentations.py` verbatim in shape. |
| R10 | **A bundle with fewer than 2 spans is `insufficient` by default** (`sufficiency_check` default `min_spans=2`, `evidence_bundle.py:114`). A realistic single-document deck would therefore be all-abstained. | Medium | W3 must expose `min_spans` as a parameter on `build_narrative_plan` and let the caller choose; the default stays at the P08-G3 default. Document it. |
| R11 | **`stream_presentation` rebuilds slides from the persisted outline** (`presentation.py:2247, 2313`). If the plan is not persisted, the streamed deck loses its citations. | Medium | The persisted `presentations.narrative` column carries the plan; the streamed slides re-read it. |
| R12 | **The smart mode has its own pipeline.** `stream_smart_presentation` (`presentation.py:1874`) and `generate_smart_presentation.py` do **not** call `generate_ppt_outline`. A hook in `generate_presentation_outlines.py` does not cover smart mode. | Medium | Out of W3's scope (§F.3), but it must be an explicit, recorded gap — not an oversight. |

### F.2 What must NOT change

1. **The P09 semantics.** `gomrey/verification.py` is untouched. `verify_claim`
   keeps its 6 verdicts, its `checks` list, its `provider_overruled` flag and its
   digest. `check_quantity_agreement` keeps its exact contract. `narrative.py`
   *calls* the verifier; it never re-implements a verdict. Test 5 is the regression
   lock.
2. **The provider seam.** `get_client` / `get_model` / `stream_generate_events` /
   `generate_structured_with_schema_retries` and the `JSONSchemaResponse` /
   `prepare_schema_for_validation` contract are untouched. The provider-facing
   response schema is **not** extended — the model is never asked to emit a
   citation ID, a locator, or a claim ID.
3. **The artifact IR's authority.** The NarrativeIR remains the canonical
   narrative record (already true: `gomrey/adapters.py:82` produces one, and
   `contracts/v1/narrative-ir.schema.json` is its contract). W3 adds fields to it;
   it does not create a parallel record, a second export format, or a second
   persistence substrate.
4. **The outline contract.** `SlideOutlineModel` keeps exactly one field,
   `content: str` (`models/presentation_outline_model.py:8-22`).
   `PresentationOutlineModel` is unchanged. `normalize_outline_payload`
   (`utils/outline_limits.py:37`) is unchanged. The `/outlines` API response shape
   is unchanged.
5. **The `gomrey/` purity rule.** No `models`/`utils`/`api`/`services` imports in
   `gomrey/narrative.py`; no model calls; no network.
6. **The migration discipline.** Additive only; no `drop_table`/`drop_column` in
   any `upgrade()`.
7. **The existing contract set.** `manifest.schemas.length` stays 23. The 22 other
   schemas are byte-identical.

### F.3 Explicitly out of scope

1. **Ingestion.** Nothing in W3 turns uploaded files into a Source IR or a bundle.
   `DocumentsLoader` still produces plain `additional_context`. The bundle and the
   IR document are **inputs** to W3, supplied on the request. Wiring the P05–P07
   fabric is a separate grain.
2. **`retrieval_pipeline` call sites.** `retrieve` is not called by W3. The bundle
   arrives already built. (W3 consumes the bundle, not the retriever.)
3. **Smart mode.** `generate_smart_presentation.py` / `stream_smart_presentation`
   (`presentation.py:1874`) keep their own pipeline. W3 covers the standard mode.
   Recorded as gap R12.
4. **The editor surface.** No change to `servers/nextjs/`. Citations are carried
   in the FastAPI-side IR and the per-slide `properties` slot; they are not yet
   rendered on the slide canvas.
5. **Citation rendering.** No footnote, no on-slide marker, no reference list.
   The outline prompt still forbids citations in slide content
   (`generate_presentation_outlines.py:158`).
6. **Unit and entity gates.** `check_quantity_agreement` covers numbers and dates
   only. Adding unit/entity gates is a P09-G2 amendment, not W3.
7. **`contracts/v1/citation.schema.json` / `claim.schema.json` reconciliation.**
   The shape mismatches (R2) are recorded, not fixed.
8. **Persisting the bundle.** The bundle is a request-scoped input. Persisting it
   (so a later export can re-verify) is a follow-on; the persisted
   `ir_context.units` subset in §C.7 is sufficient for the export assertion.
9. **The `decisions.py` calibration registry.** `register_profile` / `route_workload`
   are exercised only if a provider is actually consulted; W3 ships with
   deterministic-only routing (`route_workload` → `mode="deterministic-only"`,
   `reason="no-valid-profile"`).
10. **`decisions.build_graph` / `SupportGraph`.** The support graph is a P09-G3
    facility for multi-source decision provenance. W3's plan is a linear
    claim→node structure and does not need it. Not used.

### F.4 Named gaps the design does not close

- The `Citation` and `Claim` **contract** schemas are not the shapes the code
  uses (R2). W3 uses the code shapes.
- **No unit or entity gate** exists (§A.4).
- **`ir_provenance.verify_coverage` is not called by W3.** The plan builder assumes
  the IR document it receives was already coverage-verified. It should be, by the
  ingestion grain.
- **The `ir_document` must be supplied.** W3 cannot verify a locator it cannot
  resolve, and resolution needs the IR. If a caller supplies an IR that does not
  contain the locator's unit, the plan degrades to abstention — which is correct,
  but means a misconfigured caller produces an all-abstained deck rather than an
  error. **W3 should log a hard warning when `sufficiency` is `insufficient`
  *because* no locator resolved**, distinct from "not enough spans".

---

## G. Effort estimate per file

Effort in engineer-hours, one engineer, no provider available for live runs
(deterministic fixtures only). "Modify" = edit an existing file; "Create" = a new
file.

### G.1 Create

| File | Est. | Notes |
|---|---|---|
| `servers/fastapi/gomrey/narrative.py` | **6–8 h** | ~420 lines. `PlanNode`/`NarrativePlan` dataclasses, `build_narrative_plan` (the 11-step algorithm), `render_plan_context`, `build_narrative_ir`, `bind_slide_locators` (+ TOC remap), `assert_exportable`, `narrative_digest`. No app imports. |
| `servers/fastapi/tests/test_gomrey_narrative.py` | **3–4 h** | 13 tests (E.2 + E.3), following `test_gomrey_verification.py` conventions. |
| `servers/fastapi/alembic/versions/<rev>_add_narrative_to_presentations.py` | **0.5–1 h** | Additive nullable JSON column on `presentations`; `down_revision = "026c0ba8b35c"`. |

### G.2 Modify

| File | Est. | Change |
|---|---|---|
| `servers/fastapi/utils/llm_calls/generate_presentation_outlines.py` | **1.5–2 h** | `evidence` kwarg on `generate_ppt_outline` (251), `get_messages` (217), `get_user_prompt` (186), `get_system_prompt` (66); the evidence rules block; `render_plan_context` injection. **No change to the provider-facing schema.** |
| `servers/fastapi/api/v1/ppt/endpoints/presentation.py` | **3–4 h** | Plan construction + `assert_exportable` before generation (≈2724) and before export (≈3042, ≈1621); `bind_slide_locators` after the TOC remap; `SlideModel(properties=bindings[i])` (≈2956, ≈2326); persist `presentation.narrative`. |
| `servers/fastapi/models/sql/presentation.py` | **0.5 h** | `narrative: Optional[dict] = Field(sa_column=Column(JSON), default=None)`; add to `get_new_presentation`'s deepcopy list (models/sql/presentation.py:81-107). |
| `servers/fastapi/models/generate_presentation_request.py` | **0.5–1 h** | Optional `evidence_bundle: Optional[dict]` and `source_ir: Optional[dict]` on `GeneratePresentationRequest` (8) and `GenerateSmartPresentationRequest` (49). Both optional → every existing request stays valid. |
| `servers/fastapi/gomrey/__init__.py` | **0.5 h** | Re-export the 8 new public symbols and add them to `__all__` (the file's existing convention). |
| `contracts/v1/narrative-ir.schema.json` | **1–1.5 h** | The full §D.1 document: `$defs.CitationLocator` with the 5-branch `oneOf`, two new optional section properties, `version: 2`. |
| `contracts/v1/manifest.json` | **0.25 h** | `"schema_version": 2`. **`schemas` array unchanged (23).** |
| `scripts/validate-contracts.mjs` | **0.25 h** | One-line relaxation of the version pin at line 176. |
| `scripts/contracts.test.mjs` | **0.5–1 h** | Two new `node --test` cases (E.4). The `VALID` fixture and the `manifest.schemas.length === 23` assertion stay unchanged. |

### G.3 Totals

| | Files | Effort |
|---|---|---|
| Create | 3 | 9.5–13 h |
| Modify | 9 | 8.5–12 h |
| **Total** | **12** | **18–25 h (≈3–4 engineer-days)** |

The recorded W3 row in `IMPLEMENTATION_GRAPH.md:95` names 3 files; this design
needs 12. The gap is entirely in three places the recorded row did not anticipate:
(i) the export-time assertion needs the IR and the NarrativeIR to be **persisted**
(migration + model + column), (ii) the per-schema version pin in the shared
validator must be relaxed, and (iii) the bundle and the IR document have to
enter the pipeline as request inputs, because nothing in the repo produces them.

### G.4 Suggested commit split (each independently green)

1. `gomrey/narrative.py` + `tests/test_gomrey_narrative.py` + `gomrey/__init__.py`
   — the pure domain module and its tests. **No production call site yet.**
2. `contracts/v1/narrative-ir.schema.json` + `manifest.json` +
   `validate-contracts.mjs` + `contracts.test.mjs` — the contract extension.
3. `generate_presentation_outlines.py` + `models/generate_presentation_request.py`
   — the hook, still inert (no caller passes `evidence`).
4. `models/sql/presentation.py` + the alembic revision — persistence.
5. `api/v1/ppt/endpoints/presentation.py` — the call site + the export assertion.
   **This is the commit that makes W3 real.**

---

## Appendix — quick reference of every file touched

```
servers/fastapi/gomrey/narrative.py                          CREATE   pure domain module
servers/fastapi/tests/test_gomrey_narrative.py              CREATE   13 tests
servers/fastapi/alembic/versions/<rev>_add_narrative_to_presentations.py  CREATE  additive migration
servers/fastapi/gomrey/__init__.py                           MODIFY   exports
servers/fastapi/utils/llm_calls/generate_presentation_outlines.py  MODIFY  the hook (line 251 / 376)
servers/fastapi/api/v1/ppt/endpoints/presentation.py         MODIFY   call site + export assertion
servers/fastapi/models/sql/presentation.py                  MODIFY   presentations.narrative
servers/fastapi/models/generate_presentation_request.py     MODIFY   optional bundle/IR inputs
contracts/v1/narrative-ir.schema.json                       MODIFY   v2, per-node locators
contracts/v1/manifest.json                                  MODIFY   schema_version 2
scripts/validate-contracts.mjs                              MODIFY   version pin relaxation
scripts/contracts.test.mjs                                  MODIFY   2 new contract tests
```
