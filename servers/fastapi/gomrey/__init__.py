"""Gomrey-owned P03 storage contracts and seams, plus the P04 durable
job kernel and source-unit accounting ledger.

This package introduces Gomrey-owned domain contracts behind narrow seams
without migrating the imported database or rewriting the editor.

- contracts: Pydantic v2 records mirroring contracts/v1 for the
  storage-relevant models. No SQLAlchemy, no engine, no network.
- seams: CanonicalStore and BlobStore protocols plus deterministic
  in-memory implementations used by tests and future adapters.
- adapters: pure read-only functions projecting imported Presenton rows
  (PresentationModel/SlideModel) into Gomrey contract records.
- jobs: durable job kernel (P04-G1) with zero database and network needs.
- accounting: source-unit ledger enforcing the no-silent-loss invariant.

Canonical vs rebuildable rule: records validated here are canonical state.
Embeddings, thumbnails, search facets, and rendered previews derived from
them are rebuildable projections and must never be stored through these
seams as truth.
"""

from gomrey.accounting import (
    DuplicateDeclaration,
    UnitLedger,
    UnknownUnit,
)
from gomrey.adapters import (
    owner_to_scope,
    presentation_to_artifact,
    presentation_to_revision,
    slides_to_narrative,
)
from gomrey.jobs import (
    DurableJob,
    IdempotencyLedger,
    IllegalTransition,
    backoff_seconds,
    classify_failure,
    should_retry,
    transition,
)
from gomrey.contracts import (
    ArtifactRecord,
    ArtifactRevisionRecord,
    IngestionManifestRecord,
    JobRecord,
    NarrativeSection,
    SourceArtifactRecord,
    SourceUnitRecord,
    StageAttemptRecord,
    WorkspaceRecord,
)
from gomrey.seams import BlobStore, CanonicalStore, MemoryBlobStore, MemoryCanonicalStore

__all__ = [
    "ArtifactRecord",
    "ArtifactRevisionRecord",
    "BlobStore",
    "CanonicalStore",
    "DuplicateDeclaration",
    "DurableJob",
    "IdempotencyLedger",
    "IllegalTransition",
    "IngestionManifestRecord",
    "JobRecord",
    "MemoryBlobStore",
    "MemoryCanonicalStore",
    "NarrativeSection",
    "SourceArtifactRecord",
    "SourceUnitRecord",
    "StageAttemptRecord",
    "UnitLedger",
    "UnknownUnit",
    "WorkspaceRecord",
    "backoff_seconds",
    "classify_failure",
    "owner_to_scope",
    "presentation_to_artifact",
    "presentation_to_revision",
    "should_retry",
    "slides_to_narrative",
    "transition",
]
