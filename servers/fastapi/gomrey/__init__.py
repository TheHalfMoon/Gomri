"""Gomrey-owned P03 storage contracts and seams.

This package introduces Gomrey-owned domain contracts behind narrow seams
without migrating the imported database or rewriting the editor.

- contracts: Pydantic v2 records mirroring contracts/v1 for the
  storage-relevant models. No SQLAlchemy, no engine, no network.
- seams: CanonicalStore and BlobStore protocols plus deterministic
  in-memory implementations used by tests and future adapters.
- adapters: pure read-only functions projecting imported Presenton rows
  (PresentationModel/SlideModel) into Gomrey contract records.

Canonical vs rebuildable rule: records validated here are canonical state.
Embeddings, thumbnails, search facets, and rendered previews derived from
them are rebuildable projections and must never be stored through these
seams as truth.
"""

from gomrey.adapters import (
    owner_to_scope,
    presentation_to_artifact,
    presentation_to_revision,
    slides_to_narrative,
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
    "IngestionManifestRecord",
    "JobRecord",
    "MemoryBlobStore",
    "MemoryCanonicalStore",
    "NarrativeSection",
    "SourceArtifactRecord",
    "SourceUnitRecord",
    "StageAttemptRecord",
    "WorkspaceRecord",
    "owner_to_scope",
    "presentation_to_artifact",
    "presentation_to_revision",
    "slides_to_narrative",
]
