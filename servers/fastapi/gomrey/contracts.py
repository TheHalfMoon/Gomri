"""Pydantic v2 records mirroring contracts/v1 for storage-relevant models.

Dependency-free apart from pydantic (already required by FastAPI).
These records are canonical state: tenant/workspace identity is mandatory
(except the documented global definitions), and the no-silent-loss
invariant is a type constraint (Literal[0]), not a comment.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class FrozenRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkspaceRecord(FrozenRecord):
    workspace_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=200)
    created_at: datetime
    revision: int = Field(ge=1)
    status: Literal["active", "suspended", "deleted"]


class SourceArtifactRecord(FrozenRecord):
    source_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    source_type: Literal[
        "pdf", "document", "web", "video", "audio",
        "spreadsheet", "image", "presentation", "connector", "other",
    ]
    original_uri: Optional[str] = Field(default=None, max_length=2048)
    original_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    revision: int = Field(ge=1)
    created_at: datetime


class SourceUnitRecord(FrozenRecord):
    source_id: str = Field(min_length=1, max_length=128)
    source_unit_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    unit_kind: Literal[
        "page", "section", "slide", "sheet", "segment",
        "scene", "range", "region", "item",
    ]
    state: Literal[
        "declared", "accounted", "verified",
        "uncertain", "failed", "skipped", "duplicate",
    ]


class IngestionManifestRecord(FrozenRecord):
    manifest_id: str = Field(min_length=1, max_length=128)
    source_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    declared_units: int = Field(ge=0)
    accounted_units: int = Field(ge=0)
    silent_drop_count: Literal[0] = 0
    status: Literal["complete", "partial", "failed"]


class JobRecord(FrozenRecord):
    job_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    kind: str = Field(min_length=1, max_length=128)
    input_baseline: str = Field(min_length=1, max_length=256)
    idempotency_key: str = Field(min_length=1, max_length=256)
    status: Literal[
        "queued", "running", "suspended", "complete",
        "partial", "failed", "cancelled",
    ]
    created_at: datetime


class StageAttemptRecord(FrozenRecord):
    job_id: str = Field(min_length=1, max_length=128)
    stage: str = Field(min_length=1, max_length=128)
    attempt: int = Field(ge=1)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    status: Literal[
        "running", "checkpointed", "complete",
        "transient_failure", "permanent_failure", "cancelled",
    ]
    started_at: datetime


class ArtifactRecord(FrozenRecord):
    artifact_id: str = Field(min_length=1, max_length=128)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    artifact_type: Literal[
        "presentation", "document", "site",
        "infographic", "social", "image", "other",
    ]
    title: str = Field(min_length=1, max_length=500)
    current_revision: int = Field(ge=1)
    created_at: datetime
    status: Literal[
        "draft", "verifying", "needs_repair",
        "ready", "published", "archived",
    ]


class ArtifactRevisionRecord(FrozenRecord):
    artifact_id: str = Field(min_length=1, max_length=128)
    revision: int = Field(ge=1)
    tenant_id: str = Field(min_length=1, max_length=128)
    workspace_id: str = Field(min_length=1, max_length=128)
    content_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    verification_state: Literal[
        "unverified", "verifying", "verified", "needs_repair", "blocked"
    ]
    created_at: datetime


class NarrativeSection(FrozenRecord):
    heading: str = Field(max_length=500)
    text: str = Field(max_length=20000)
    claim_ids: list[str] = Field(default_factory=list)
