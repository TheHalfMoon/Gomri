"""Deterministic tests for the P05-G1 source gateway admission boundary."""

import pytest

from gomrey.gateway import (
    AdmissionError,
    IllegalTrustTransition,
    Principal,
    admit_source,
    can_access,
    content_identity,
    is_duplicate,
    is_trusted,
    select_parser,
    transition_trust,
)


def _principal(**overrides) -> Principal:
    base = {
        "principal_id": "u-1",
        "tenant_id": "t-1",
        "workspace_ids": ["w-1"],
        "scopes": ["source:write", "source:read"],
    }
    base.update(overrides)
    return Principal(**base)


def _request(**overrides):
    base = {
        "source_id": "src-1",
        "tenant_id": "t-1",
        "workspace_id": "w-1",
        "source_type": "pdf",
        "origin": "local",
        "original_digest": "a" * 64,
        "provenance": {"acquired_by": "u-1"},
    }
    base.update(overrides)
    return base


def test_valid_admission_lands_quarantined_never_trusted() -> None:
    receipt = admit_source(_request(), _principal())
    assert receipt.trust_state == "quarantined"
    assert is_trusted(receipt.trust_state) is False
    assert receipt.parser_id == "docling-default"
    assert receipt.duplicate_of is None


def test_trust_machine_forbids_silent_promotion() -> None:
    with pytest.raises(IllegalTrustTransition):
        transition_trust("src-1", "quarantined", "trusted-for-retrieval")
    with pytest.raises(IllegalTrustTransition):
        transition_trust("src-1", "received", "trusted-for-retrieval")
    assert transition_trust("src-1", "quarantined", "validated") == "validated"
    assert is_trusted("trusted-for-retrieval") is True
    assert is_trusted("normalized") is False


def test_unsupported_type_and_origin_fail_closed() -> None:
    with pytest.raises(AdmissionError) as exc:
        admit_source(_request(source_type="holodeck"), _principal())
    assert exc.value.code == "unsupported_source"
    with pytest.raises(AdmissionError) as exc2:
        admit_source(_request(origin="telepathy"), _principal())
    assert exc2.value.code == "unsupported_source"
    with pytest.raises(AdmissionError):
        select_parser("holodeck")


def test_malformed_digest_and_provenance_rejected() -> None:
    with pytest.raises(AdmissionError) as exc:
        admit_source(_request(original_digest="not-a-digest"), _principal())
    assert exc.value.code == "malformed_source"
    with pytest.raises(AdmissionError) as exc2:
        admit_source(_request(provenance={}), _principal())
    assert exc2.value.code == "malformed_source"


def test_access_boundary_deny_by_default() -> None:
    # Cross-tenant admission is denied.
    with pytest.raises(AdmissionError) as exc:
        admit_source(_request(), _principal(tenant_id="t-2"))
    assert exc.value.code == "access_denied"
    # Workspace the principal does not belong to is denied.
    with pytest.raises(AdmissionError):
        admit_source(_request(workspace_id="w-9"), _principal())
    # Missing write scope is denied.
    with pytest.raises(AdmissionError):
        admit_source(_request(), _principal(scopes=["source:read"]))
    # Unknown actions are denied; cross-workspace reads are denied.
    assert can_access(_principal(), source_tenant="t-1", source_workspace="w-1", action="read") is True
    assert can_access(_principal(), source_tenant="t-1", source_workspace="w-1", action="drop-table") is False
    assert can_access(_principal(), source_tenant="t-1", source_workspace="w-9", action="read") is False
    assert can_access(_principal(), source_tenant="t-2", source_workspace="w-1", action="read") is False


def test_duplicate_content_identity_is_deterministic() -> None:
    digest = content_identity(b"same bytes")
    assert digest == content_identity(b"same bytes")
    assert digest != content_identity(b"other bytes")
    assert is_duplicate(digest, {digest}) is True
    assert is_duplicate(digest, set()) is False
    receipt = admit_source(_request(original_digest=digest), _principal(), known_digests={digest})
    assert receipt.duplicate_of == digest
    assert receipt.trust_state == "quarantined"


def test_error_codes_reject_unknown_codes() -> None:
    with pytest.raises(ValueError):
        AdmissionError("not-a-code", "x")
    assert AdmissionError("access_denied", "x").code == "access_denied"
