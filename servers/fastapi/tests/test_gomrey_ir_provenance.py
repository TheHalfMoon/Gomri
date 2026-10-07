"""Tests for the P06-G4 IR provenance completion and coverage gate."""

import pytest

from gomrey.gateway import AdmissionError
from gomrey.ir_provenance import assemble_ir, verify_coverage


def _record(unit_id: str, **overrides) -> dict:
    base = {
        "source_id": "src-1",
        "source_unit_id": unit_id,
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "unit_kind": "page",
        "state": "accounted",
        "provenance": {"parsers": ["docling-default"], "agreement": "unchallenged"},
    }
    base.update(overrides)
    return base


def test_assembly_requires_complete_provenance() -> None:
    doc = assemble_ir(
        source_id="src-1", tenant_id="t-1", workspace_id="w-1",
        original_digest="f" * 64, records=[_record("u-1"), _record("u-2")],
    )
    assert doc["unit_count"] == 2
    assert doc["original_digest"] == "f" * 64
    with pytest.raises(AdmissionError):
        assemble_ir(source_id="src-1", tenant_id="t-1", workspace_id="w-1",
                    original_digest="f" * 64, records=[])
    with pytest.raises(AdmissionError):
        assemble_ir(source_id="src-1", tenant_id="t-1", workspace_id="w-1",
                    original_digest="f" * 64,
                    records=[_record("u-1"), _record("u-1")])


def test_cross_record_mixing_refused() -> None:
    with pytest.raises(AdmissionError) as exc:
        assemble_ir(source_id="src-1", tenant_id="t-1", workspace_id="w-1",
                    original_digest="f" * 64,
                    records=[_record("u-1"), _record("u-2", tenant_id="t-2")])
    assert exc.value.code == "unsafe_source"
    with pytest.raises(AdmissionError):
        assemble_ir(source_id="src-1", tenant_id="t-1", workspace_id="w-1",
                    original_digest="f" * 64,
                    records=[_record("u-1", provenance={"parsers": []})])
    with pytest.raises(AdmissionError):
        assemble_ir(source_id="src-1", tenant_id="t-1", workspace_id="w-1",
                    original_digest="f" * 64,
                    records=[_record("u-1", state="teleported")])


def test_coverage_complete_partial_and_silent_drops() -> None:
    verdict = verify_coverage(["u-1", "u-2"], [_record("u-1"), _record("u-2")])
    assert verdict == {"status": "complete", "declared": 2, "accounted": 2,
                       "uncertain_units": [], "failed_units": [], "silent_drops": 0}
    partial = verify_coverage(
        ["u-1", "u-2"],
        [_record("u-1"), _record("u-2", state="uncertain",
                                 provenance={"parsers": ["a", "b"], "agreement": "conflict"})],
    )
    assert partial["status"] == "partial"
    assert partial["uncertain_units"] == ["u-2"]
    with pytest.raises(AdmissionError) as exc:
        verify_coverage(["u-1", "u-2", "u-3"], [_record("u-1"), _record("u-2")])
    assert exc.value.code == "normalization_failure"
    assert "u-3" in str(exc.value)


def test_skip_and_duplicate_need_their_receipts() -> None:
    ok_skip = verify_coverage(
        ["u-1"], [_record("u-1", state="skipped", skip_reason="blank-page")])
    assert ok_skip["status"] == "complete"
    with pytest.raises(AdmissionError):
        verify_coverage(["u-1"], [_record("u-1", state="skipped")])
    ok_dup = verify_coverage(
        ["u-1"], [_record("u-1", state="duplicate", duplicate_of="u-0")])
    assert ok_dup["accounted"] == 1
    with pytest.raises(AdmissionError):
        verify_coverage(["u-1"], [_record("u-1", state="duplicate")])
