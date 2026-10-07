"""Tests for the P06-G2 structured worker envelope and qualification."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.parser_router import BenchmarkCase, BenchmarkRun, BenchmarkScore, score_run
from gomrey.structure_worker import (
    KNOWN_WORKERS,
    LITEPARSE_BASELINE,
    QualificationProfile,
    WorkerEnvelope,
    admit_worker,
    check_qualification,
    map_structured_output,
)


def _budget(**limits) -> ResourceBudget:
    defaults = {"worker_invocations": 10.0, "worker_timeout_seconds": 3600.0}
    defaults.update(limits)
    return ResourceBudget(limits=defaults)


def _envelope(**overrides) -> WorkerEnvelope:
    base = {
        "worker_id": "docling-default",
        "parser_id": "docling-default",
        "input_digest": "d" * 64,
    }
    base.update(overrides)
    return WorkerEnvelope(**base)


def _doc() -> dict:
    return {
        "source_id": "src-1",
        "pages": [
            {"page_no": 1, "sections": [
                {"heading": "Intro", "text": "Hello world.",
                 "tables": [[["a", "b"], ["1", "2"]]],
                 "figures": [{"caption": "Fig 1"}]},
                {"heading": "Body", "text": "Second section."},
            ]},
            {"page_no": 2, "sections": [{"heading": "", "text": "Last page."}]},
        ],
    }


def test_liteparse_baseline_identity_stable() -> None:
    assert LITEPARSE_BASELINE["role"] == "baseline-comparator"
    assert "liteparse-baseline" in KNOWN_WORKERS
    assert LITEPARSE_BASELINE["service_module"] == "services.liteparse_service"


def test_worker_envelope_authorizes_bounded_capabilities() -> None:
    auth = admit_worker(_envelope(), _budget())
    assert auth.capabilities == {"network": False, "secrets": False, "quarantine_read": True}
    with pytest.raises(AdmissionError):
        admit_worker(_envelope(worker_id="mystery-box"), _budget())
    with pytest.raises(AdmissionError):
        admit_worker(_envelope(cancelled=True), _budget())
    with pytest.raises(AdmissionError):
        admit_worker(_envelope(network=True), _budget())
    with pytest.raises(AdmissionError):
        admit_worker(_envelope(secrets=True), _budget())
    with pytest.raises(AdmissionError):
        admit_worker(_envelope(timeout_seconds=0), _budget())
    with pytest.raises(AdmissionError) as exc:
        admit_worker(_envelope(), _budget(worker_invocations=0.0))
    assert exc.value.code == "resource_limit_exceeded"


def test_structured_mapping_preserves_tables_and_provenance() -> None:
    intermediate = map_structured_output(
        worker_id="docling-default", input_digest="d" * 64, document=_doc())
    assert [u["unit_id"] for u in intermediate.units] == ["p1-s0", "p1-s1", "p2-s0"]
    first = intermediate.units[0]
    assert first["tables"] == [[["a", "b"], ["1", "2"]]]
    assert first["figures"] == [{"caption": "Fig 1"}]
    assert first["page_no"] == 1
    assert intermediate.parser_id == "docling-default"
    with pytest.raises(AdmissionError):
        map_structured_output(worker_id="docling-default", input_digest="d" * 64,
                              document={"pages": []})
    with pytest.raises(AdmissionError):
        map_structured_output(worker_id="docling-default", input_digest="d" * 64,
                              document={"pages": [{"nope": True}]})
    empty_sections = map_structured_output(
        worker_id="docling-default", input_digest="d" * 64,
        document={"source_id": "s", "pages": [
            {"page_no": 1, "sections": []},
            {"page_no": 2, "sections": [{"text": "kept"}]},
        ]})
    assert [u["unit_id"] for u in empty_sections.units] == ["p2-s0"]
    assert empty_sections.warnings == ["page-1-no-sections"]


def test_qualification_requires_measurement_and_bars() -> None:
    case = BenchmarkCase(case_id="struct-001", expected_units=3, max_conflicts=0, max_uncertain=1)
    score = score_run(case, BenchmarkRun(
        case_id="struct-001", observed_units=3, conflicts=0, uncertain=0,
        baseline_coverage=1.0))
    good = QualificationProfile(seconds_per_page=4.0, mb_per_page=200.0)
    assert check_qualification(score, good) == {"qualified": True, "reasons": []}
    slow = QualificationProfile(seconds_per_page=120.0, mb_per_page=200.0)
    result = check_qualification(score, slow)
    assert result["qualified"] is False
    assert "too-slow-per-page" in result["reasons"]
    unlicensed = QualificationProfile(seconds_per_page=4.0, mb_per_page=200.0, license_ok=False)
    assert check_qualification(score, unlicensed)["qualified"] is False
    losing_score = BenchmarkScore(case_id="struct-001", coverage=0.5, conflicts=0,
                                  uncertain=0, beats_baseline=False)
    assert check_qualification(losing_score, good)["qualified"] is False
