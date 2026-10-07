"""Deterministic tests for budgets, progress, and reconciliation (P04-G3)."""

import pytest

from gomrey.budgets import (
    BudgetExhausted,
    ResourceBudget,
    progress_event,
    reconcile,
)
from gomrey.jobs import IdempotencyLedger


def test_budget_spend_and_exhaustion() -> None:
    budget = ResourceBudget(limits={"tokens": 100.0, "pages": 10.0})
    budget.spend("tokens", 40.0)
    budget.spend("tokens", 60.0)
    assert budget.remaining("tokens") == 0.0
    assert budget.exhausted() == ["tokens"]
    with pytest.raises(BudgetExhausted) as exc:
        budget.spend("tokens", 1.0)
    assert exc.value.budget == "tokens"
    assert exc.value.limit == 100.0
    with pytest.raises(ValueError):
        budget.spend("pages", -1.0)
    assert budget.remaining("uncapped") is None


def test_progress_event_shape_and_bounds() -> None:
    event = progress_event(
        job_id="j-1", stage="index", total=1000, accounted=250,
        verified=200, uncertain=30, failed=20, warnings=["slow-ocr"],
    )
    assert event["percent"] == 25.0
    assert event["source_units_total"] == 1000
    assert event["warnings"] == ["slow-ocr"]
    empty = progress_event(job_id="j-1", stage="done", total=0, accounted=0)
    assert empty["percent"] == 100.0
    with pytest.raises(ValueError):
        progress_event(job_id="j-1", stage="x", total=10, accounted=11)


def test_reconcile_never_upgrades_unknown_by_assumption() -> None:
    ledger = IdempotencyLedger()
    assert ledger.claim("k-1") is True
    assert reconcile(ledger, "k-1", lambda: "still_unknown") == "unknown"
    assert ledger.outcome("k-1") == "unknown"
    assert reconcile(ledger, "k-1", lambda: "success") == "success"
    assert ledger.outcome("k-1") == "success"
    # Settled outcomes are returned without re-checking.
    calls: list[str] = []

    def explode() -> str:
        calls.append("ran")
        return "failed"

    assert reconcile(ledger, "k-1", explode) == "success"
    assert calls == []


def test_reconcile_records_observed_failure() -> None:
    ledger = IdempotencyLedger()
    ledger.claim("k-2")
    assert reconcile(ledger, "k-2", lambda: "failed") == "failed"
    assert ledger.outcome("k-2") == "failed"
