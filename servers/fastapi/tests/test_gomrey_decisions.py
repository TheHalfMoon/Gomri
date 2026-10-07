"""Tests for the P09-G3 decision graph, synthesis, and calibration."""

import pytest

from gomrey.decisions import (
    MemoryDecisionStore,
    adjudicate,
    build_graph,
    graph_digest,
    make_decision,
    register_profile,
    route_workload,
    synthesize,
)
from gomrey.gateway import AdmissionError


def _graph(**overrides):
    base = {
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "nodes": [
            {"node_id": "claim-1", "kind": "claim", "ref": "claim-1"},
            {"node_id": "ev-1", "kind": "evidence", "ref": "c-1"},
            {"node_id": "cite-1", "kind": "citation", "ref": "c-1"},
        ],
        "edges": [
            {"from_id": "claim-1", "to_id": "ev-1", "relation": "supports"},
            {"from_id": "cite-1", "to_id": "ev-1", "relation": "cites"},
        ],
    }
    base.update(overrides)
    return build_graph(**base)


def _decision(**overrides):
    base = {
        "decision_id": "d-1",
        "question": "Did revenue grow?",
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "claim_ids": ["claim-1", "claim-2"],
        "evidence_ids": ["c-1"],
        "conclusion": "Revenue grew on supporting evidence.",
        "alternatives": [{"option": "hold", "note": "conflict fallback"}],
    }
    base.update(overrides)
    return make_decision(**base)


def test_graph_rejects_dangling_and_orphans():
    graph = _graph()
    assert graph_digest(graph) == graph_digest(_graph())
    with pytest.raises(AdmissionError):
        _graph(edges=[{"from_id": "claim-1", "to_id": "ghost", "relation": "supports"}])
    with pytest.raises(AdmissionError):
        build_graph(tenant_id="t-1", workspace_id="w-1",
                    nodes=[{"node_id": "claim-1", "kind": "claim", "ref": "claim-1"},
                           {"node_id": "cite-9", "kind": "citation", "ref": "c-9"}],
                    edges=[{"from_id": "cite-9", "to_id": "claim-1", "relation": "cites"}])
    with pytest.raises(AdmissionError):
        _graph(nodes=[{"node_id": "x", "kind": "oracle", "ref": "x"}])


def test_synthesis_includes_only_verified_conflicts_exposed():
    decision = _decision()
    result = synthesize(decision, {
        "claim-1": {"verdict": "supported", "reasons": ["supporting-evidence-agrees"]},
        "claim-2": {"verdict": "contradicted", "reasons": ["contradicting-evidence-only"]},
    })
    assert result["status"] == "accepted"
    assert result["included_claims"] == ["claim-1"]
    assert any(o["claim_id"] == "claim-2" for o in result["omissions"])
    assert any(c["kind"] == "contradiction" for c in result["conflicts"])


def test_conflict_without_alternative_abstains():
    decision = _decision(alternatives=[])
    result = synthesize(decision, {
        "claim-1": {"verdict": "partially_supported", "reasons": ["conflicting-evidence"]},
        "claim-2": {"verdict": "does_not_establish", "reasons": ["no-supporting-stance"]},
    })
    assert result["status"] == "abstained"
    assert result["included_claims"] == []
    assert "conflict-requires-alternative" in result["reasons"]


def test_empty_synthesis_abstains_with_omissions():
    decision = _decision()
    result = synthesize(decision, {
        "claim-1": {"verdict": "unresolved", "reasons": ["binding:no-evidence-refs"]},
        "claim-2": {"verdict": "does_not_establish", "reasons": ["quantity-mismatch:12"]},
    })
    assert result["status"] == "abstained"
    assert result["conclusion"] == ""
    assert len(result["omissions"]) == 2


def test_calibration_routing_prefers_measured_profiles():
    registry = register_profile({}, provider="decider-x", workload="retrieval-relevance",
                                benchmark="gomrey-frozen-001", samples=200, abstention_rate=0.1)
    routed = route_workload(registry, "retrieval-relevance", ["decider-x", "laya-y"])
    assert routed["mode"] == "calibrated"
    assert routed["provider"] == "decider-x"
    fallback = route_workload(registry, "artifact-quality", ["decider-x"])
    assert fallback == {"provider": "deterministic", "mode": "deterministic-only",
                        "benchmark": "", "reason": "no-valid-profile"}
    with pytest.raises(AdmissionError):
        register_profile({}, provider="decider-x", workload="w", benchmark="b",
                         samples=12, abstention_rate=0.1)


def test_disagreement_policy_abstains_on_independent_divergence():
    assert adjudicate("supported")["mode"] == "deterministic-only"
    assert adjudicate("supported", "supported")["mode"] == "agreement"
    split = adjudicate("supported", "contradicted", challenger_independent=True)
    assert split["abstained"] is True
    assert split["verdict"] == "unresolved"
    weak = adjudicate("supported", "contradicted", challenger_independent=False)
    assert weak["verdict"] == "supported"
    assert weak["mode"] == "deterministic-wins"


def test_decision_store_roundtrip_with_isolation():
    store = MemoryDecisionStore()
    store.put(_decision())
    loaded = store.get("d-1", "t-1", "w-1")
    assert loaded is not None
    assert loaded.question == "Did revenue grow?"
    assert store.get("d-1", "t-2", "w-1") is None
    assert store.delete("d-1", "t-1", "w-1") is True
    assert store.get("d-1", "t-1", "w-1") is None
