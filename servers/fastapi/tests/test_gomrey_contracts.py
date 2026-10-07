"""Deterministic tests for Gomrey Pydantic storage contracts (P03-G2)."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from gomrey.contracts import (
    ArtifactRecord,
    ArtifactRevisionRecord,
    IngestionManifestRecord,
    JobRecord,
    SourceArtifactRecord,
    SourceUnitRecord,
    StageAttemptRecord,
    WorkspaceRecord,
)

WHEN = datetime(2026, 10, 7, tzinfo=timezone.utc)
HEX = "ab" * 32


def test_workspace_record_accepts_valid() -> None:
    record = WorkspaceRecord(
        workspace_id="w-1",
        tenant_id="t-1",
        name="Research",
        created_at=WHEN,
        revision=1,
        status="active",
    )
    assert record.revision == 1


def test_records_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        WorkspaceRecord(
            workspace_id="w-1",
            tenant_id="t-1",
            name="Research",
            created_at=WHEN,
            revision=1,
            status="active",
            vector_index="must-not-exist",
        )


def test_source_artifact_requires_sha256_digest() -> None:
    with pytest.raises(ValidationError):
        SourceArtifactRecord(
            source_id="s-1",
            tenant_id="t-1",
            workspace_id="w-1",
            source_type="pdf",
            original_digest="not-a-digest",
            revision=1,
            created_at=WHEN,
        )


def test_source_unit_state_is_closed_vocabulary() -> None:
    with pytest.raises(ValidationError):
        SourceUnitRecord(
            source_id="s-1",
            source_unit_id="u-1",
            tenant_id="t-1",
            workspace_id="w-1",
            unit_kind="page",
            state="vaporized",
        )


def test_manifest_forbids_silent_drops_at_type_level() -> None:
    with pytest.raises(ValidationError):
        IngestionManifestRecord(
            manifest_id="m-1",
            source_id="s-1",
            tenant_id="t-1",
            workspace_id="w-1",
            declared_units=10,
            accounted_units=9,
            silent_drop_count=1,
            status="complete",
        )


def test_job_and_stage_attempt_validate() -> None:
    job = JobRecord(
        job_id="j-1",
        tenant_id="t-1",
        workspace_id="w-1",
        kind="ingest",
        input_baseline="s-1@2",
        idempotency_key="k-1",
        status="running",
        created_at=WHEN,
    )
    stage = StageAttemptRecord(
        job_id=job.job_id,
        stage="parse",
        attempt=1,
        tenant_id="t-1",
        workspace_id="w-1",
        status="checkpointed",
        started_at=WHEN,
    )
    assert stage.attempt == 1


def test_artifact_revision_requires_digest_and_state() -> None:
    record = ArtifactRevisionRecord(
        artifact_id="a-1",
        revision=1,
        tenant_id="t-1",
        workspace_id="w-1",
        content_digest=HEX,
        verification_state="unverified",
        created_at=WHEN,
    )
    assert record.content_digest == HEX
    with pytest.raises(ValidationError):
        ArtifactRecord(
            artifact_id="a-1",
            tenant_id="t-1",
            workspace_id="w-1",
            artifact_type="hologram",
            title="Nope",
            current_revision=1,
            created_at=WHEN,
            status="draft",
        )
