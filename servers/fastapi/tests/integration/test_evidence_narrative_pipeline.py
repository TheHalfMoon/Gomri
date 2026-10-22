"""End-to-end tests for the W3 evidence-bound narrative pipeline.

These exercise the wiring, not only the pure module:

- a request carrying evidence produces a deterministic plan;
- the plan's closed fact base and the evidence rules actually reach the
  provider prompt, and the provider seam is otherwise untouched;
- the plan binds to rendered slides through the deterministic
  table-of-contents remap;
- the persisted NarrativeIR conforms to ``contracts/v1/narrative-ir.schema.json``;
- the export-time assertion refuses an artifact whose citation no longer
  resolves.
"""

import json
import pathlib

import pytest

from gomrey.citations import BrokenCitation, make_locator
from gomrey.narrative import ABSTENTION_MARKER, GROUNDED_MARKER
from models.generate_presentation_request import (
    EvidenceBundleInput,
    GeneratePresentationRequest,
)
from services.evidence_narrative import (
    assert_artifact_exportable,
    bind_plan_to_slides,
    build_plan_from_request,
    narrative_for_presentation,
)
from utils.llm_calls.generate_presentation_outlines import get_messages

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
NARRATIVE_SCHEMA = (
    REPO_ROOT / "contracts" / "v1" / "narrative-ir.schema.json"
)

SOURCE = "src-1"
TENANT = "tenant:owner-1"
WORKSPACE = "tenant:owner-1:default"


def _source_ir() -> dict:
    return {
        "source_id": SOURCE,
        "original_digest": "d" * 64,
        "units": [
            {
                "source_id": SOURCE,
                "source_unit_id": "p1-s0",
                "page_no": 1,
                "provenance": {"parsers": ["docling-default"], "agreement": "agree"},
            },
            {
                "source_id": SOURCE,
                "source_unit_id": "p1-s1",
                "page_no": 1,
                "provenance": {"parsers": ["docling-default"], "agreement": "agree"},
            },
        ],
    }


def _locator(unit_id: str) -> dict:
    return make_locator("document", source_id=SOURCE, unit_id=unit_id, page_no=1)


def _bundle_input() -> EvidenceBundleInput:
    first = _locator("p1-s0")
    second = _locator("p1-s1")
    return EvidenceBundleInput(
        bundle_id="bundle-1",
        query="What happened to retention in 2026?",
        source_revisions=[{"source_id": SOURCE, "digest": "d" * 64}],
        spans=[
            {
                "span_id": first["citation_id"],
                "citation_id": first["citation_id"],
                "text": "Retention rose to 91 percent in 2026.",
                "stance": "supports",
                "locator": {
                    "kind": "document",
                    "source_id": SOURCE,
                    "unit_id": "p1-s0",
                    "page_no": 1,
                },
            },
            {
                "span_id": second["citation_id"],
                "citation_id": second["citation_id"],
                "text": "The sample covered 4000 accounts.",
                "stance": "supports",
                "locator": {
                    "kind": "document",
                    "source_id": SOURCE,
                    "unit_id": "p1-s1",
                    "page_no": 1,
                },
            },
        ],
        retrieval_identities=["retrieval-1"],
    )


def _plan(**kwargs):
    return build_plan_from_request(
        evidence_bundle=_bundle_input(),
        source_ir=_source_ir(),
        owner_id="owner-1",
        n_slides=kwargs.pop("n_slides", None),
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# Request surface
# --------------------------------------------------------------------------- #


def test_a_request_carries_optional_evidence() -> None:
    request = GeneratePresentationRequest(content="Tell me about retention.")
    assert request.evidence_bundle is None
    assert request.source_ir is None

    with_evidence = GeneratePresentationRequest(
        content="Tell me about retention.",
        evidence_bundle=_bundle_input(),
        source_ir=_source_ir(),
    )
    assert with_evidence.evidence_bundle is not None
    assert with_evidence.source_ir is not None


def test_a_bundle_without_a_source_ir_is_refused() -> None:
    with pytest.raises(ValueError):
        build_plan_from_request(
            evidence_bundle=_bundle_input(),
            source_ir=None,
            owner_id="owner-1",
            n_slides=None,
        )


def test_no_evidence_means_no_plan() -> None:
    plan = build_plan_from_request(
        evidence_bundle=None,
        source_ir=None,
        owner_id="owner-1",
        n_slides=None,
    )
    assert plan is None


# --------------------------------------------------------------------------- #
# The plan
# --------------------------------------------------------------------------- #


def test_a_request_with_evidence_produces_a_plan_bound_to_the_owner_scope() -> None:
    plan = _plan()

    assert plan is not None
    assert plan.tenant_id == TENANT
    assert plan.workspace_id == WORKSPACE
    assert plan.bundle_id == "bundle-1"
    assert plan.node_count == 2
    assert all(node.status == GROUNDED_MARKER for node in plan.nodes)


def test_the_plan_is_deterministic() -> None:
    assert _plan().digest == _plan().digest


def test_the_plan_fixes_its_own_slide_count_when_the_caller_does_not() -> None:
    plan = _plan(n_slides=None)
    assert plan.node_count == 2

    pinned = _plan(n_slides=5)
    assert pinned.node_count == 5


# --------------------------------------------------------------------------- #
# The provider sees the evidence, and only the evidence
# --------------------------------------------------------------------------- #


def test_the_outline_prompt_carries_the_evidence_rules_and_the_closed_fact_base() -> None:
    plan = _plan()

    messages = get_messages(
        "Tell me about retention.",
        plan.node_count,
        "en",
        None,
        None,
        None,
        None,
        True,
        False,
        plan,
    )

    system = messages[0].content
    user = messages[1].content

    # The rules are present and authoritative.
    assert "EVIDENCE RULES" in system
    assert "Never fill the gap with a plausible statement" in system
    # The scope is stated, so units and entities are never claimed as verified.
    assert "did not check" in system
    assert "units" in system
    assert "entities" in system
    # The fact base is present and carries the plan's citation ids.
    assert "EVIDENCE PLAN" in user
    assert plan.nodes[0].citation_ids[0] in user
    assert "EVIDENCE SUFFICIENCY" in user


def test_without_evidence_the_prompt_is_unchanged() -> None:
    messages = get_messages(
        "Tell me about retention.",
        4,
        "en",
        None,
        None,
        None,
        None,
        True,
        False,
    )

    system = messages[0].content
    user = messages[1].content

    assert "EVIDENCE RULES" not in system
    assert "EVIDENCE PLAN" not in user


def test_the_evidence_rules_tell_the_model_not_to_write_citations_into_slides() -> None:
    plan = _plan()
    messages = get_messages("x", plan.node_count, "en", None, None, None, None, True, False, plan)
    system = messages[0].content
    assert "Never write a citation id" in system


# --------------------------------------------------------------------------- #
# Binding
# --------------------------------------------------------------------------- #


def test_the_plan_binds_to_slides_through_the_table_of_contents_remap() -> None:
    plan = _plan()
    slides = [object(), object(), object(), object()]

    bindings = bind_plan_to_slides(
        plan, slides, toc_slides=1, title_slide=True
    )

    assert len(bindings) == 4
    # The title slide and the table-of-contents slide carry no plan node.
    assert bindings[0]["evidence_status"] == ABSTENTION_MARKER
    assert bindings[1]["evidence_status"] == ABSTENTION_MARKER
    # The two content slides carry the two plan nodes, in order.
    assert bindings[2]["citation_ids"] == plan.nodes[0].citation_ids
    assert bindings[3]["citation_ids"] == plan.nodes[1].citation_ids


def test_a_slide_beyond_the_plan_is_explicitly_abstained() -> None:
    plan = _plan()
    bindings = bind_plan_to_slides(plan, [object(), object(), object()], title_slide=False)
    assert bindings[2]["evidence_status"] == ABSTENTION_MARKER
    assert bindings[2]["reasons"] == ["no-plan-node"]


def test_without_a_plan_every_slide_is_explicitly_abstained() -> None:
    bindings = bind_plan_to_slides(None, [object(), object()])
    assert len(bindings) == 2
    for binding in bindings:
        assert binding["evidence_status"] == ABSTENTION_MARKER
        assert binding["reasons"] == ["no-evidence-plan"]


# --------------------------------------------------------------------------- #
# The persisted artifact
# --------------------------------------------------------------------------- #


def test_the_narrative_ir_conforms_to_the_contract() -> None:
    schema = json.loads(NARRATIVE_SCHEMA.read_text(encoding="utf-8"))
    plan = _plan()

    document = narrative_for_presentation(
        plan, artifact_id="a-1", revision=1, language="en"
    )

    # Top level: only declared properties, and every required one present.
    assert set(document) <= set(schema["properties"])
    for key in schema["required"]:
        assert key in document

    section_schema = schema["properties"]["sections"]["items"]
    for section in document["sections"]:
        assert set(section) <= set(section_schema["properties"])
        for key in section_schema["required"]:
            assert key in section
        assert section["evidence_status"] in section_schema["properties"][
            "evidence_status"
        ]["enum"]
        for locator in section["citation_locators"]:
            assert locator["kind"] in {"document", "web", "video", "spreadsheet", "image"}
            assert locator["citation_id"].startswith("cite-")
            assert locator["source_id"] == SOURCE

    # The verification scope travels with the artifact.
    assert document["verification_scope"]["not_gated"] == ["units", "entities"]


def test_the_artifact_refuses_to_export_when_a_citation_stops_resolving() -> None:
    plan = _plan()
    document = narrative_for_presentation(
        plan, artifact_id="a-1", revision=1, language="en"
    )

    class _Presentation:
        narrative = document
        source_ir = _source_ir()

    # A healthy artifact passes.
    assert_artifact_exportable(_Presentation())

    # A tampered artifact does not.
    tampered = json.loads(json.dumps(document))
    tampered["sections"][0]["citation_locators"][0]["unit_id"] = "p9-s9"
    _Presentation.narrative = tampered

    with pytest.raises(BrokenCitation) as excinfo:
        assert_artifact_exportable(_Presentation())
    assert "export-time citation revalidation failed" in excinfo.value.reason


def test_an_artifact_without_a_narrative_is_not_checked() -> None:
    class _Presentation:
        narrative = None
        source_ir = None

    assert_artifact_exportable(_Presentation())
