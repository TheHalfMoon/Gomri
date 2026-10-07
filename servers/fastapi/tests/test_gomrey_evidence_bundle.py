"""Tests for the P08-G3 evidence bundle and sufficiency gate."""

import pytest

from gomrey.evidence_bundle import (
    build_bundle,
    bundle_digest,
    sufficiency_check,
)
from gomrey.gateway import AdmissionError


def _span(span_id: str, **overrides) -> dict:
    base = {"citation_id": span_id, "position": {"unit_id": "u-1"}}
    base.update(overrides)
    return base


def _bundle(**overrides) -> object:
    base = {
        "bundle_id": "b-1",
        "query": "What grew revenue?",
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "source_revisions": [{"source_id": "s-1", "digest": "d" * 64}],
        "spans": [_span("c-1"), _span("c-2")],
        "retrieval_identities": ["exact+lexical"],
    }
    base.update(overrides)
    return build_bundle(**base)


def test_bundle_digest_stable_and_bound() -> None:
    first = bundle_digest(_bundle())
    assert first == bundle_digest(_bundle())
    assert len(first) == 64
    changed = bundle_digest(_bundle(query="Something else?"))
    assert changed != first
    with pytest.raises(AdmissionError):
        build_bundle(bundle_id="", query="q", tenant_id="t", workspace_id="w",
                     source_revisions=[], spans=[], retrieval_identities=[])
    with pytest.raises(AdmissionError):
        build_bundle(bundle_id="b", query="q", tenant_id="t", workspace_id="w",
                     source_revisions=[], spans=[_span("c-1")],
                     retrieval_identities=[], dropped_without_reason=2)
    with pytest.raises(AdmissionError):
        build_bundle(bundle_id="b", query="q", tenant_id="t", workspace_id="w",
                     source_revisions=[], spans=[_span("c-1")],
                     retrieval_identities=[],
                     contradictions=[{"span_ids": ["ghost"]}])


def test_sufficiency_abstains_and_escalates() -> None:
    assert sufficiency_check(_bundle())["verdict"] == "sufficient"
    thin = sufficiency_check(_bundle(spans=[_span("c-1")]))
    assert thin["verdict"] == "insufficient"
    assert thin["reasons"] == ["too-few-spans"]
    conflicted = sufficiency_check(_bundle(
        contradictions=[{"span_ids": ["c-1", "c-2"], "note": "growth vs decline"}]))
    assert conflicted["verdict"] == "needs_review"
    assert "contradictions-open" in conflicted["reasons"]
    stale_bundle = _bundle(spans=[_span("c-1"), _span("c-2", stale_labeled=True)])
    stale_strict = sufficiency_check(stale_bundle)
    assert stale_strict["verdict"] == "insufficient"
    assert stale_strict["stale_spans"] == ["c-2"]
    stale_allowed = sufficiency_check(stale_bundle, require_fresh=False)
    assert stale_allowed["verdict"] == "sufficient"
    assert stale_allowed["stale_spans"] == ["c-2"]
    with pytest.raises(AdmissionError):
        sufficiency_check(_bundle(), min_spans=0)
