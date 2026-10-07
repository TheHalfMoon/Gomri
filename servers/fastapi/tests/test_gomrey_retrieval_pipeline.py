"""Tests for the P08-G1 layered retrieval pipeline (no indexes)."""

import pytest

from gomrey.gateway import AdmissionError
from gomrey.retrieval_pipeline import (
    acl_filter,
    apply_constraints,
    exact_boost,
    fuse,
    lexical_overlap,
    retrieve,
)


def _candidate(unit_id: str, source: str, text: str, **overrides) -> dict:
    base = {
        "unit_id": unit_id,
        "source_id": source,
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "text": text,
        "scores": {"dense": 0.9},
        "is_fresh": True,
    }
    base.update(overrides)
    return base


def test_acl_first_denied_counted_never_leaked() -> None:
    pool = [
        _candidate("u-1", "s-1", "revenue grew strongly"),
        _candidate("u-2", "s-2", "revenue figures", tenant_id="t-2"),
        _candidate("u-3", "s-3", "revenue notes", workspace_id="w-9"),
    ]
    result = retrieve(query="revenue growth", candidates=pool,
                      tenant_id="t-1", workspace_id="w-1")
    assert result["denied_by_acl"] == 2
    assert [r["unit_id"] for r in result["results"]] == ["u-1"]
    assert result["candidates_seen"] == 3


def test_exact_surfaces_first_lexical_computed() -> None:
    assert lexical_overlap("revenue growth figures", "quarterly revenue figures") == 0.6667
    assert lexical_overlap("", "anything") == 0.0
    pool = [
        _candidate("u-1", "s-1", "unrelated weather report", scores={"dense": 0.99}),
        _candidate("u-2", "s-1", "revenue growth figures"),
    ]
    ordered = exact_boost(pool, identifiers=["u-2"])
    assert [c["unit_id"] for c in ordered] == ["u-2", "u-1"]
    assert ordered[0]["scores"]["exact"] == 1.0


def test_fusion_explicit_and_channel_presence_recorded() -> None:
    pool = [_candidate("u-1", "s-1", "x", scores={"lexical": 0.5})]
    fused = fuse(pool, weights={"lexical": 1.0, "dense": 1.0})
    assert fused[0]["fused_score"] == 0.25
    assert fused[0]["channels_present"] == ["lexical"]
    with pytest.raises(AdmissionError):
        fuse(pool, weights={"telepathy": 1.0})
    with pytest.raises(AdmissionError):
        fuse(pool, weights={"lexical": 0.0, "dense": 0.0})


def test_freshness_and_diversity_constraints() -> None:
    pool = [
        _candidate("u-1", "s-1", "alpha", is_fresh=False),
        _candidate("u-2", "s-1", "beta"),
        _candidate("u-3", "s-1", "gamma"),
        _candidate("u-4", "s-1", "delta"),
        _candidate("u-5", "s-2", "epsilon"),
    ]
    ranked = sorted(pool, key=lambda c: c["unit_id"])
    capped = apply_constraints(ranked, max_per_source=2)
    assert [r["unit_id"] for r in capped["results"]] == ["u-2", "u-3", "u-5"]
    assert capped["excluded_stale"] == 1
    labeled = apply_constraints(ranked, max_per_source=10, include_stale=True)
    stale = next(r for r in labeled["results"] if r["unit_id"] == "u-1")
    assert stale["stale_labeled"] is True
    with pytest.raises(AdmissionError):
        retrieve(query="", candidates=pool, tenant_id="t-1", workspace_id="w-1")


def test_no_vector_models_still_retrieves_lexically() -> None:
    pool = [
        _candidate("u-1", "s-1", "revenue growth figures", scores={}),
        _candidate("u-2", "s-1", "weather report", scores={}),
    ]
    result = retrieve(query="revenue growth", candidates=pool,
                      tenant_id="t-1", workspace_id="w-1",
                      weights={"exact": 1.0, "lexical": 1.0})
    assert [r["unit_id"] for r in result["results"]] == ["u-1", "u-2"]
    assert result["results"][0]["channels_present"] == ["lexical"]
