"""Tests for the P07-G1 bounded web acquisition contracts (no network)."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.web_acquisition import (
    CrawlScope,
    acquisition_policy,
    admit_child,
    page_snapshot,
    plan_crawl,
)


def _budget() -> ResourceBudget:
    return ResourceBudget(limits={"crawl_pages": 10.0})


def _plan(**overrides) -> object:
    base = {"seed_url": "https://93.184.216.34/docs/"}
    base.update(overrides)
    return plan_crawl(CrawlScope(**base))


def test_valid_plan_and_same_origin_child() -> None:
    plan = _plan()
    assert plan.status()["pages_visited"] == 0
    admitted = admit_child(plan, "https://93.184.216.34/docs/", "https://93.184.216.34/docs/a",
                           depth=1, budget=_budget())
    assert admitted == "https://93.184.216.34/docs/a"
    assert plan.status()["pages_visited"] == 1
    # Revisits are idempotent: same URL, no double spend or count.
    budget = _budget()
    repeat = admit_child(plan, "https://93.184.216.34/docs/", "https://93.184.216.34/docs/a",
                         depth=1, budget=budget)
    assert repeat == admitted
    assert plan.status()["pages_visited"] == 1
    assert budget.consumed.get("crawl_pages", 0.0) == 0.0


def test_cross_origin_child_denied_not_followed() -> None:
    plan = _plan()
    with pytest.raises(AdmissionError) as exc:
        admit_child(plan, "https://93.184.216.34/docs/", "https://93.184.216.35/evil",
                    depth=1, budget=_budget())
    assert exc.value.code == "remote_fetch_denied"
    assert plan.status()["pages_visited"] == 0
    # Explicit expansion allows a named domain (literal-IP form here).
    wide = _plan(allowed_domains=("93.184.216.35",))
    assert admit_child(wide, "https://93.184.216.34/", "https://93.184.216.35/x",
                       depth=1, budget=_budget())
    # Hostname children need DNS pinning before admission.
    named = plan_crawl(CrawlScope(seed_url="https://example.com/"))
    with pytest.raises(AdmissionError):
        admit_child(named, "https://example.com/", "https://example.com/p",
                    depth=1, budget=_budget())
    assert admit_child(named, "https://example.com/", "https://example.com/p",
                       depth=1, budget=_budget(), resolved_ips=["93.184.216.34"])


def test_depth_and_page_bounds() -> None:
    shallow = _plan(max_depth=0)
    with pytest.raises(AdmissionError) as exc:
        admit_child(shallow, "https://93.184.216.34/", "https://93.184.216.34/x",
                    depth=1, budget=_budget())
    assert exc.value.code == "resource_limit_exceeded"
    with pytest.raises(AdmissionError):
        plan_crawl(CrawlScope(seed_url="https://93.184.216.34/", max_pages=0))
    with pytest.raises(AdmissionError):
        plan_crawl(CrawlScope(seed_url="https://93.184.216.34/", max_depth=99))
    tiny = _plan(max_pages=1)
    admit_child(tiny, "https://93.184.216.34/", "https://93.184.216.34/a",
                depth=0, budget=_budget())
    with pytest.raises(AdmissionError):
        admit_child(tiny, "https://93.184.216.34/", "https://93.184.216.34/b",
                    depth=0, budget=_budget())
    with pytest.raises(AdmissionError):
        plan_crawl(CrawlScope(seed_url="https://10.0.0.1/"))


def test_snapshot_taint_and_policy_matrix() -> None:
    snap = page_snapshot(
        canonical_url="https://93.184.216.34/a", content_digest="a" * 64,
        mime="text/html", response_bytes=512, retrieved_at="2026-10-07T00:00:00Z",
    )
    assert snap["untrusted_origin"] is True
    assert snap["origin"] == "https://93.184.216.34"
    with pytest.raises(AdmissionError):
        page_snapshot(canonical_url="https://93.184.216.34/a", content_digest="bad",
                      mime="text/html", response_bytes=1, retrieved_at="t")
    open_policy = acquisition_policy(robots_allowed=True, terms_redistribution_allowed=True)
    assert open_policy == {"fetch_permitted": True, "redistribution_permitted": True, "reasons": []}
    blocked = acquisition_policy(robots_allowed=False, terms_redistribution_allowed=False)
    assert blocked["fetch_permitted"] is False
    assert blocked["redistribution_permitted"] is False
    unknown = acquisition_policy(robots_allowed=None, terms_redistribution_allowed=False)
    assert unknown["fetch_permitted"] is True
    assert "robots-unknown-flagged" in unknown["reasons"]
    assert "redistribution-denied-by-default" in unknown["reasons"]
