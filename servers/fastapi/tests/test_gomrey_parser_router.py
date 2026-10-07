"""Tests for the P06-G1 parser router and ensemble contracts."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.parser_router import (
    BenchmarkCase,
    BenchmarkRun,
    check_second_parser_budget,
    classify_workload,
    preflight,
    reconcile_units,
    route,
    score_run,
    to_source_ir,
)


def _native_pdf() -> bytes:
    body = b"%PDF-1.7\n" + b" ".join(
        b"The quick brown fox jumps over the lazy dog" for _ in range(30)
    )
    return body + b" /Font /Helvetica endstream"


def test_preflight_and_native_routing() -> None:
    signals = preflight(_native_pdf(), "application/pdf")
    assert "text-runs-present" in signals.signals
    workload = classify_workload(signals.signals, "application/pdf")
    assert workload == "native_text"
    decision = route("pdf", workload)
    assert decision.primary_parser == "docling-default"
    assert decision.second_parser is None


def test_scanned_and_table_routing_trigger_second_parser() -> None:
    scanned = classify_workload(("embedded-images", "text-sparse"), "application/pdf")
    assert scanned == "scanned"
    decision = route("pdf", scanned)
    assert decision.primary_parser == "ocr-visual-worker"
    assert decision.second_parser == "docling-default"
    table = classify_workload(("text-runs-present", "table-markers"), "application/pdf")
    assert table == "table_heavy"
    assert route("document", table).second_parser == "ocr-visual-worker"
    unknown = route("pdf", "unknown")
    assert unknown.second_parser is not None
    with pytest.raises(AdmissionError):
        route("pdf", "telepathic")
    with pytest.raises(AdmissionError):
        preflight(b"", "application/pdf")
    with pytest.raises(AdmissionError):
        preflight(b"not a pdf at all here", "application/pdf")


def test_second_parser_budget_is_bounded() -> None:
    budget = ResourceBudget(limits={"second_parser_triggers": 1.0})
    check_second_parser_budget(budget)
    with pytest.raises(AdmissionError) as exc:
        check_second_parser_budget(budget)
    assert exc.value.code == "resource_limit_exceeded"


def test_reconciliation_never_averages_silently() -> None:
    primary = [
        {"unit_id": "u-1", "kind": "page", "text": "same"},
        {"unit_id": "u-2", "kind": "page", "text": "mine"},
        {"unit_id": "u-3", "kind": "page", "text": "only-left"},
    ]
    secondary = [
        {"unit_id": "u-1", "kind": "page", "text": "same"},
        {"unit_id": "u-2", "kind": "page", "text": "theirs"},
    ]
    result = reconcile_units(primary, secondary)
    assert result.verdict == "conflict"
    assert result.conflicts == ("u-2",)
    assert result.uncertain_unit_ids == ("u-3",)
    conflict_unit = next(u for u in result.units if u["unit_id"] == "u-2")
    assert conflict_unit["challenger_text"] == "theirs"
    assert conflict_unit["text"] == "mine"
    # Unchallenged runs are marked, not trusted by default.
    solo = reconcile_units(primary, None)
    assert solo.verdict == "agree"
    assert all(u["agreement"] == "unchallenged" for u in solo.units)


def test_ir_provenance_and_accounting() -> None:
    primary = [{"unit_id": "u-1", "kind": "page", "text": "same"}]
    secondary = [{"unit_id": "u-1", "kind": "page", "text": "same"}]
    records = to_source_ir(
        reconcile_units(primary, secondary),
        source_id="src-1", tenant_id="t-1", workspace_id="w-1",
    )
    assert len(records) == 1
    assert records[0]["state"] == "accounted"
    assert records[0]["provenance"]["parsers"] == ["primary", "secondary"]
    assert records[0]["tenant_id"] == "t-1"


def test_benchmark_promotion_by_measurement_only() -> None:
    case = BenchmarkCase(case_id="ar-mixed-001", expected_units=10, max_conflicts=1, max_uncertain=1)
    winner = score_run(case, BenchmarkRun(
        case_id="ar-mixed-001", observed_units=10, conflicts=0, uncertain=1,
        baseline_coverage=0.9,
    ))
    assert winner.coverage == 1.0
    assert winner.beats_baseline is True
    loser = score_run(case, BenchmarkRun(
        case_id="ar-mixed-001", observed_units=9, conflicts=0, uncertain=0,
        baseline_coverage=0.9,
    ))
    assert loser.beats_baseline is False
    with pytest.raises(AdmissionError):
        score_run(case, BenchmarkRun(
            case_id="other", observed_units=10, conflicts=0, uncertain=0,
            baseline_coverage=0.9))
    # The incumbent measurement is mandatory: no silent zero baseline.
    with pytest.raises(TypeError):
        BenchmarkRun(case_id="ar-mixed-001", observed_units=10, conflicts=0, uncertain=0)  # type: ignore[call-arg]
