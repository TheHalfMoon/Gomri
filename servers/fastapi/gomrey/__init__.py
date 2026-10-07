"""Gomrey-owned P03 storage contracts and seams, the P04 durable
job kernel and source-unit accounting ledger, and the P05 source
gateway admission boundary.

This package introduces Gomrey-owned domain contracts behind narrow seams
without migrating the imported database or rewriting the editor.

- contracts: Pydantic v2 records mirroring contracts/v1 for the
  storage-relevant models. No SQLAlchemy, no engine, no network.
- seams: CanonicalStore and BlobStore protocols plus deterministic
  in-memory implementations used by tests and future adapters.
- gateway: P05-G1 admission (source identity, trust lifecycle, access
  boundary, structured errors, dedup identity). Admission always lands in
  quarantined; only the explicit trust machine can reach
  trusted-for-retrieval.
- file_boundary: P05-G2 hostile file handling (path containment, MIME
  reconciliation, shared-budget enforcement, archive entry validation,
  active-content denial, temp lifecycle). Pure logic, no writes.
- remote_gateway: P05-G3 safe URL policy (scheme/credential denial,
  literal-IP SSRF classification, DNS pinning contract, redirect bounds,
  remote budgets, tainted fetch contract). Pure logic, never fetches.
- adapters: pure read-only functions projecting imported Presenton rows
  (PresentationModel/SlideModel) into Gomrey contract records.
- jobs: durable job kernel (P04-G1) with zero database and network needs.
- accounting: source-unit ledger enforcing the no-silent-loss invariant.
- budgets: resource caps, progress events, and unknown-outcome
  reconciliation that never upgrades by assumption.

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
from gomrey.budgets import (
    BudgetExhausted,
    ResourceBudget,
    progress_event,
    reconcile,
)
from gomrey.adapters import (
    owner_to_scope,
    presentation_to_artifact,
    presentation_to_revision,
    slides_to_narrative,
)
from gomrey.file_boundary import (
    TempLease,
    TempLeaseRegistry,
    check_archive_entry,
    deny_active_content,
    enforce_file_budgets,
    file_admission_report,
    normalize_path,
    reconcile_mime,
    scan_active_content,
    sniff_mime,
)
from gomrey.gateway import (
    AdmissionError,
    AdmissionReceipt,
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
from gomrey.remote_gateway import (
    UrlVerdict,
    authorize_fetch,
    classify_url,
    enforce_remote_budgets,
    normalized_fetch_result,
    validate_redirect_chain,
)
from gomrey.seams import BlobStore, CanonicalStore, MemoryBlobStore, MemoryCanonicalStore

__all__ = [
    "AdmissionError",
    "AdmissionReceipt",
    "ArtifactRecord",
    "ArtifactRevisionRecord",
    "BlobStore",
    "BudgetExhausted",
    "CanonicalStore",
    "DuplicateDeclaration",
    "DurableJob",
    "IdempotencyLedger",
    "IllegalTransition",
    "IllegalTrustTransition",
    "IngestionManifestRecord",
    "JobRecord",
    "MemoryBlobStore",
    "MemoryCanonicalStore",
    "NarrativeSection",
    "Principal",
    "ResourceBudget",
    "SourceArtifactRecord",
    "SourceUnitRecord",
    "StageAttemptRecord",
    "TempLease",
    "TempLeaseRegistry",
    "UnitLedger",
    "UnknownUnit",
    "UrlVerdict",
    "WorkspaceRecord",
    "admit_source",
    "authorize_fetch",
    "backoff_seconds",
    "can_access",
    "check_archive_entry",
    "classify_failure",
    "classify_url",
    "content_identity",
    "deny_active_content",
    "enforce_file_budgets",
    "enforce_remote_budgets",
    "file_admission_report",
    "is_duplicate",
    "is_trusted",
    "normalize_path",
    "normalized_fetch_result",
    "owner_to_scope",
    "presentation_to_artifact",
    "presentation_to_revision",
    "progress_event",
    "reconcile",
    "reconcile_mime",
    "scan_active_content",
    "select_parser",
    "should_retry",
    "slides_to_narrative",
    "sniff_mime",
    "transition",
    "transition_trust",
    "validate_redirect_chain",
]
