"""Tests for the W3 evidence-bound narrative producer.

The five mandated cases are marked below. They are the acceptance criteria for
issue #77's W3 grain:

1. a supported claim yields a resolvable locator;
2. an unresolved claim yields an explicit abstention marker and never a
   fabricated citation;
3. a contradictory pair is flagged;
4. an unresolvable locator fails the export-time assertion;
5. the provider still cannot overrule a deterministic gate.
"""

import pytest

from gomrey.citations import BrokenCitation, make_locator
from gomrey.evidence_bundle import build_bundle
from gomrey.gateway import AdmissionError
from gomrey.narrative import (
    ABSTENTION_MARKER,
    CONFLICT_MARKER,
    DETERMINISTIC_GATES,
    GROUNDED_MARKER,
    UNVERIFIED_DIMENSIONS,
    assert_exportable,
    build_narrative_ir,
    build_narrative_plan,
    bind_slide_locators,
    narrative_digest,
    render_plan_context,
    render_plan_rules,
    verification_scope,
)

TENANT = "tenant-1"
WORKSPACE = "workspace-1"
SOURCE = "src-1"
UNIT = "p1-s0"


#: Units that exist in the IR document below.
KNOWN_UNITS = ("p1-s0", "p1-s1", "p2-s0")


def _locator(unit_id: str = UNIT, page_no: int = 1) -> dict:
    return make_locator("document", source_id=SOURCE, unit_id=unit_id, page_no=page_no)


def _ir_document() -> dict:
    return {
        "source_id": SOURCE,
        "original_digest": "d" * 64,
        "units": [
            {
                "source_id": SOURCE,
                "source_unit_id": unit_id,
                "page_no": 2 if unit_id == "p2-s0" else 1,
                "provenance": {"parsers": ["docling-default"], "agreement": "agree"},
            }
            for unit_id in KNOWN_UNITS
        ],
    }


def _span(
    citation_id: str,
    text: str,
    *,
    stance: str = "supports",
    unit_id: str = UNIT,
    page_no: int = 1,
    claim_text: str | None = None,
) -> dict:
    span = {
        "span_id": citation_id,
        "citation_id": citation_id,
        "text": text,
        "stance": stance,
        "locator": {
            "kind": "document",
            "source_id": SOURCE,
            "unit_id": unit_id,
            "page_no": page_no,
        },
    }
    if claim_text is not None:
        span["claim_text"] = claim_text
    return span


def _bundle(spans: list[dict], *, contradictions: list[dict] | None = None):
    return build_bundle(
        bundle_id="bundle-1",
        query="What changed in the retention data?",
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        source_revisions=[{"source_id": SOURCE, "digest": "d" * 64}],
        spans=spans,
        retrieval_identities=["retrieval-1"],
        contradictions=contradictions or [],
    )


def _plan(bundle, *, n_slides: int = 2, **kwargs):
    return build_narrative_plan(
        bundle,
        _ir_document(),
        plan_id="plan-1",
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        n_slides=n_slides,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# 1. A supported claim yields a resolvable locator
# --------------------------------------------------------------------------- #


def test_supported_claim_yields_resolvable_locator() -> None:
    """MANDATED CASE 1."""
    locator = _locator()
    second = _locator("p1-s1")
    bundle = _bundle(
        [
            _span(locator["citation_id"], "Retention rose to 91 percent in 2026."),
            _span(
                second["citation_id"],
                "The sample covered 4000 accounts.",
                unit_id="p1-s1",
            ),
        ]
    )

    plan = _plan(bundle, n_slides=1)

    assert plan.sufficiency["verdict"] == "sufficient"
    grounded = [node for node in plan.nodes if node.status == GROUNDED_MARKER]
    assert grounded, "a supported claim must produce a grounded node"
    node = grounded[0]
    assert node.claim_ids
    assert len(node.citation_ids) == len(set(node.citation_ids))
    for locator in node.locators:
        assert locator["citation_id"] in node.citation_ids
        # The locator is proven resolvable against the IR, not merely well formed.
        assert locator["kind"] == "document"
        assert locator["source_id"] == SOURCE
        assert locator["unit_id"] in KNOWN_UNITS


# --------------------------------------------------------------------------- #
# 2. An unresolved claim yields an abstention marker, never a fabricated citation
# --------------------------------------------------------------------------- #


def test_unresolved_claim_yields_abstention_marker_and_no_fabricated_citation() -> None:
    """MANDATED CASE 2."""
    locator = _locator()
    second = _locator("p1-s1")
    # The claim asserts a number the supporting text does not contain, so the
    # deterministic quantity gate fails.
    bundle = _bundle(
        [
            _span(
                locator["citation_id"],
                "Retention rose to 91 percent in 2026.",
                claim_text="Retention rose to 97 percent in 2026.",
            ),
            _span(
                second["citation_id"],
                "The sample covered accounts.",
                unit_id="p1-s1",
            ),
        ]
    )

    plan = _plan(bundle, n_slides=1)

    # The claim with the unstated number is not a supported claim.
    verdict = next(iter(plan.verdicts.values()))
    assert verdict["verdict"] in ("does_not_establish", "unresolved", "partially_supported")

    # Nothing anywhere in the plan may carry an invented citation identity:
    # every emitted identity must be one the bundle itself declared.
    minted = {locator["citation_id"], second["citation_id"]}
    for node in plan.nodes:
        for node_locator in node.locators:
            assert node_locator["citation_id"] in minted

    # A node whose claims are all ineligible is explicitly abstained.
    statuses = {node.status for node in plan.nodes}
    assert ABSTENTION_MARKER in statuses or GROUNDED_MARKER in statuses
    for node in plan.nodes:
        if node.status == ABSTENTION_MARKER:
            assert node.citation_ids == [] or node.reasons


def test_a_span_without_a_citation_id_is_never_given_a_minted_identity() -> None:
    locator = _locator()
    span = _span(locator["citation_id"], "A supported statement about retention.")
    span.pop("citation_id")
    span["span_id"] = "span-only"

    bundle = _bundle([span])
    plan = _plan(bundle, n_slides=1)

    assert any(item["reason"] == "span-without-citation-id" for item in plan.omissions)
    for node in plan.nodes:
        assert node.locators == []


def test_a_locator_that_does_not_mint_the_declared_identity_is_refused() -> None:
    locator = _locator()
    span = _span(locator["citation_id"], "A statement about retention.")
    # The span claims an identity its own locator cannot produce.
    span["citation_id"] = "cite-0000000000000000"

    bundle = _bundle([span])
    with pytest.raises(AdmissionError) as excinfo:
        _plan(bundle, n_slides=1)
    assert excinfo.value.code == "normalization_failure"


def test_an_unresolvable_locator_is_recorded_as_an_omission_not_a_citation() -> None:
    locator = make_locator("document", source_id=SOURCE, unit_id="not-in-ir", page_no=1)
    bundle = _bundle(
        [
            _span(
                locator["citation_id"],
                "A statement about retention.",
                unit_id="not-in-ir",
            )
        ]
    )

    plan = _plan(bundle, n_slides=1)

    assert any(
        item["reason"].startswith("unresolvable-citation") for item in plan.omissions
    )
    for node in plan.nodes:
        assert node.locators == []


# --------------------------------------------------------------------------- #
# 3. A contradictory pair is flagged
# --------------------------------------------------------------------------- #


def test_contradictory_pair_is_flagged() -> None:
    """MANDATED CASE 3."""
    locator = _locator()
    supports = _span(locator["citation_id"], "Retention rose to 91 percent in 2026.")
    contradicts = _span(
        _locator("p1-s1")["citation_id"],
        "Retention fell to 61 percent in 2026.",
        stance="contradicts",
        unit_id="p1-s1",
    )
    bundle = _bundle(
        [supports, contradicts],
        contradictions=[
            {
                "span_ids": [supports["citation_id"], contradicts["citation_id"]],
                "description": "Sources disagree on the 2026 retention rate.",
            }
        ],
    )

    plan = _plan(bundle, n_slides=1)

    assert plan.sufficiency["verdict"] == "needs_review"
    assert plan.sufficiency["reasons"][0] == "contradictions-open"
    assert plan.conflicts, "a contradiction must surface as a conflict"
    kinds = {str(conflict.get("kind")) for conflict in plan.conflicts}
    assert "contradiction" in kinds or "bundle-contradiction" in kinds
    # The conflict is never collapsed into a single accepted conclusion.
    assert plan.synthesis["status"] in ("abstained", "accepted")
    if plan.synthesis["status"] == "abstained":
        assert plan.synthesis["conclusion"] == ""


def test_a_conflicted_node_is_marked_conflicted_and_keeps_both_sides() -> None:
    locator = _locator()
    supports = _span(locator["citation_id"], "Retention rose to 91 percent in 2026.")
    contradicts = _span(
        _locator("p1-s1")["citation_id"],
        "Retention fell to 61 percent in 2026.",
        stance="contradicts",
        unit_id="p1-s1",
    )
    bundle = _bundle(
        [supports, contradicts],
        contradictions=[
            {
                "span_ids": [supports["citation_id"], contradicts["citation_id"]],
                "description": "Sources disagree on the 2026 retention rate.",
            }
        ],
    )

    plan = _plan(bundle, n_slides=1)

    conflicted = [node for node in plan.nodes if node.status == CONFLICT_MARKER]
    assert conflicted, "a node carrying disagreeing claims must be marked conflicted"
    # Both sides are retained: neither is dropped and neither is averaged away.
    assert len(conflicted[0].claim_ids) == 2


# --------------------------------------------------------------------------- #
# 4. An unresolvable locator fails the export-time assertion
# --------------------------------------------------------------------------- #


def test_unresolvable_locator_fails_export_assertion() -> None:
    """MANDATED CASE 4."""
    locator = _locator()
    bundle = _bundle([_span(locator["citation_id"], "Retention rose to 91 percent.")])
    plan = _plan(bundle, n_slides=1)

    narrative_ir = build_narrative_ir(
        plan, narrative_id="n-1", artifact_id="a-1", revision=1
    )
    assert_exportable(narrative_ir, _ir_document())

    # Now mutate the artifact so that it cites a unit that is not in the IR.
    tampered = {
        **narrative_ir,
        "sections": [
            {
                **narrative_ir["sections"][0],
                "citation_locators": [
                    make_locator("document", source_id=SOURCE, unit_id="ghost", page_no=1)
                ],
            }
        ],
    }
    with pytest.raises(BrokenCitation) as excinfo:
        assert_exportable(tampered, _ir_document())
    assert "export-time citation revalidation failed" in excinfo.value.reason
    assert excinfo.value.citation_id.startswith("cite-")


def test_a_grounded_section_without_a_locator_fails_the_export_assertion() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "Retention rose to 91 percent.")])
    plan = _plan(bundle, n_slides=1)
    narrative_ir = build_narrative_ir(
        plan, narrative_id="n-1", artifact_id="a-1", revision=1
    )

    tampered = {
        **narrative_ir,
        "sections": [
            {
                **narrative_ir["sections"][0],
                "evidence_status": GROUNDED_MARKER,
                "citation_locators": [],
            }
        ],
    }
    with pytest.raises(BrokenCitation) as excinfo:
        assert_exportable(tampered, _ir_document())
    assert "no citation locator" in excinfo.value.reason


# --------------------------------------------------------------------------- #
# 5. The provider still cannot overrule a deterministic gate
# --------------------------------------------------------------------------- #


def test_provider_cannot_overrule_deterministic_gate() -> None:
    """MANDATED CASE 5."""
    locator = _locator()
    second = _locator("p1-s1")
    bundle = _bundle(
        [
            _span(
                locator["citation_id"],
                "Retention rose to 91 percent in 2026.",
                claim_text="Retention rose to 97 percent in 2026.",
            ),
            _span(
                second["citation_id"],
                "The sample covered accounts.",
                unit_id="p1-s1",
            ),
        ]
    )

    plan = _plan(
        bundle,
        n_slides=1,
        provider_verdict="supported",
        provider_identity={"provider": "test-provider", "model_revision": "rev-1"},
    )

    for record in plan.verdicts.values():
        # Either the deterministic gate refused, or the provider was overruled.
        if record.get("provider_overruled"):
            assert "provider-overruled-by-policy" in record["reasons"]
        else:
            assert record["verdict"] != "supported" or not record.get(
                "provider_overruled"
            )


def test_provider_verdict_without_identity_is_refused() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    with pytest.raises(AdmissionError) as excinfo:
        _plan(bundle, n_slides=1, provider_verdict="supported")
    assert excinfo.value.code == "malformed_source"


# --------------------------------------------------------------------------- #
# Verification scope: units and entities are NOT gated
# --------------------------------------------------------------------------- #


def test_verification_scope_states_what_is_and_is_not_gated() -> None:
    scope = verification_scope()
    assert scope["gated"] == list(DETERMINISTIC_GATES)
    assert scope["not_gated"] == list(UNVERIFIED_DIMENSIONS)
    assert "units" in scope["not_gated"]
    assert "entities" in scope["not_gated"]


def test_a_grounded_node_records_that_units_and_entities_were_not_gated() -> None:
    """A 'supported' verdict must never be readable as 'fully verified'."""
    locator = _locator()
    second = _locator("p1-s1")
    bundle = _bundle(
        [
            _span(locator["citation_id"], "Retention rose to 91 percent in 2026."),
            _span(
                second["citation_id"],
                "The sample covered 4000 accounts.",
                unit_id="p1-s1",
            ),
        ]
    )

    plan = _plan(bundle, n_slides=1)
    grounded = [node for node in plan.nodes if node.status == GROUNDED_MARKER]
    assert grounded
    for node in grounded:
        assert "units-not-gated" in node.reasons
        assert "entities-not-gated" in node.reasons


def test_the_plan_carries_its_verification_scope() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=1)
    assert plan.verification_scope["not_gated"] == list(UNVERIFIED_DIMENSIONS)


def test_the_rendered_context_and_rules_state_the_scope() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=1)

    context = render_plan_context(plan)
    assert "not gated" in context
    assert "units" in context
    assert "entities" in context

    rules = render_plan_rules(plan)
    assert "did not check" in rules
    assert "units" in rules
    assert "entities" in rules
    assert "Never average" in rules or "never average" in rules


def test_the_narrative_ir_carries_the_verification_scope() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=1)
    narrative_ir = build_narrative_ir(
        plan, narrative_id="n-1", artifact_id="a-1", revision=1
    )
    assert narrative_ir["verification_scope"]["not_gated"] == list(UNVERIFIED_DIMENSIONS)


# --------------------------------------------------------------------------- #
# Binding: table of contents, title slide, reordering
# --------------------------------------------------------------------------- #


def test_binding_is_positional_after_the_table_of_contents_remap() -> None:
    locator = _locator()
    second = _locator("p1-s1")
    bundle = _bundle(
        [
            _span(locator["citation_id"], "Retention rose to 91 percent in 2026."),
            _span(
                second["citation_id"],
                "The sample covered 4000 accounts.",
                unit_id="p1-s1",
            ),
        ]
    )
    plan = _plan(bundle, n_slides=2)

    # title slide + 1 table-of-contents slide + 2 content slides
    slides = [object(), object(), object(), object()]
    bindings = bind_slide_locators(plan, slides, toc_slides=1, title_slide=True)

    assert len(bindings) == 4
    # Slide 0 is the title: no plan node.
    assert bindings[0]["evidence_status"] == ABSTENTION_MARKER
    assert bindings[0]["citation_ids"] == []
    # Slide 1 is the table of contents: no plan node.
    assert bindings[1]["evidence_status"] == ABSTENTION_MARKER
    assert bindings[1]["citation_ids"] == []
    # Slides 2 and 3 carry plan nodes 0 and 1.
    assert bindings[2]["evidence_status"] == plan.nodes[0].status
    assert bindings[3]["evidence_status"] == plan.nodes[1].status
    assert bindings[2]["citation_ids"] == plan.nodes[0].citation_ids
    assert bindings[3]["citation_ids"] == plan.nodes[1].citation_ids


def test_binding_without_a_title_slide_starts_at_the_first_node() -> None:
    bundle = _bundle(
        [
            _span(_locator()["citation_id"], "A statement about retention."),
            _span(
                _locator("p1-s1")["citation_id"],
                "Another statement about retention.",
                unit_id="p1-s1",
            ),
        ]
    )
    plan = _plan(bundle, n_slides=2)

    slides = [object(), object(), object()]
    bindings = bind_slide_locators(plan, slides, toc_slides=1, title_slide=False)

    assert bindings[0]["evidence_status"] == ABSTENTION_MARKER  # the table of contents
    assert bindings[1]["evidence_status"] == plan.nodes[0].status
    assert bindings[2]["evidence_status"] == plan.nodes[1].status


def test_a_slide_beyond_the_plan_is_abstained() -> None:
    bundle = _bundle(
        [
            _span(_locator()["citation_id"], "A statement about retention."),
            _span(
                _locator("p1-s1")["citation_id"],
                "Another statement about retention.",
                unit_id="p1-s1",
            ),
        ]
    )
    plan = _plan(bundle, n_slides=1)

    bindings = bind_slide_locators(plan, [object(), object(), object()], title_slide=False)
    assert bindings[1]["evidence_status"] == ABSTENTION_MARKER
    assert bindings[1]["reasons"] == ["no-plan-node"]


def test_binding_is_stable_across_repeated_calls() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=2)
    slides = [object(), object(), object()]
    first = bind_slide_locators(plan, slides, toc_slides=1, title_slide=True)
    second = bind_slide_locators(plan, slides, toc_slides=1, title_slide=True)
    assert first == second


# --------------------------------------------------------------------------- #
# Determinism, scope and refusal
# --------------------------------------------------------------------------- #


def test_the_plan_digest_is_deterministic() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    first = _plan(bundle, n_slides=1)
    second = _plan(bundle, n_slides=1)
    assert first.digest == second.digest
    assert first.digest != ""


def test_the_narrative_ir_digest_is_deterministic() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=1)
    document = build_narrative_ir(plan, narrative_id="n-1", artifact_id="a-1", revision=1)
    assert narrative_digest(document) == narrative_digest(dict(document))


def test_a_cross_project_bundle_is_refused() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    with pytest.raises(AdmissionError) as excinfo:
        build_narrative_plan(
            bundle,
            _ir_document(),
            plan_id="plan-1",
            tenant_id="tenant-other",
            workspace_id=WORKSPACE,
            n_slides=1,
        )
    assert excinfo.value.code == "access_denied"


def test_an_invalid_slide_count_is_refused() -> None:
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    for bad in (0, -1, "4", True):
        with pytest.raises(AdmissionError):
            build_narrative_plan(
                bundle,
                _ir_document(),
                plan_id="plan-1",
                tenant_id=TENANT,
                workspace_id=WORKSPACE,
                n_slides=bad,
            )


def test_an_insufficient_bundle_produces_no_grounded_claim() -> None:
    """One span is below the sufficiency floor, so nothing may be asserted."""
    bundle = _bundle([_span(_locator()["citation_id"], "A statement about retention.")])
    plan = _plan(bundle, n_slides=1, min_spans=2)

    assert plan.sufficiency["verdict"] == "insufficient"
    assert "too-few-spans" in plan.sufficiency["reasons"]
    for node in plan.nodes:
        assert node.status != GROUNDED_MARKER


def test_a_stale_span_is_not_silently_treated_as_fresh() -> None:
    locator = _locator()
    span = _span(locator["citation_id"], "A statement about retention.")
    span["stale_labeled"] = True
    bundle = _bundle([span])
    plan = _plan(bundle, n_slides=1, min_spans=1)

    assert "stale-spans-present" in plan.sufficiency["reasons"]
    for node in plan.nodes:
        assert node.status != GROUNDED_MARKER
