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
- parser_boundary: P05-G4 quarantine exit (parser adapter contract,
  normalization gate, trusted IR release, taint markers, sensitivity
  hooks, revocation receipts). Pure logic, no trusted mutation.
- parser_router: P06-G1 ensemble contracts (deterministic preflight and
  workload classification, bounded second-parser routing, explicit
  disagreement reconciliation, Source IR emission, benchmark scoring).
  Pure logic, no models, no network.
- structure_worker: P06-G2 worker envelope (capability-bounded
  admission-to-execution), LiteParse baseline identity, Docling-shaped
  output mapping, measurement-only qualification gates. Pure logic, no
  subprocess, no weights, no lockfile change.
- ocr_worker: P06-G3 OCR region contracts (bbox/rotation/confidence
  provenance), Unicode script/direction analysis, frozen Arabic P0
  suite, honest escalation observations. Pure logic, no models.
- ir_provenance: P06-G4 IR assembly with unbroken provenance chains and
  the P04-ledger coverage gate (silent drops fail loudly, partials carry
  coordinates). Pure logic.
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
from gomrey.parser_boundary import (
    ParserAdapter,
    ParserIntermediate,
    QuarantinedView,
    RevocationReceipt,
    TrustedRelease,
    classify_sensitivity,
    promote_to_trusted,
    revoke_source,
    run_parser,
    taint_content,
    validate_intermediate,
)
from gomrey.structure_worker import (
    KNOWN_WORKERS,
    LITEPARSE_BASELINE,
    QualificationProfile,
    WorkerAuthorization,
    WorkerEnvelope,
    admit_worker,
    check_qualification,
    map_structured_output,
)
from gomrey.ocr_worker import (
    ARABIC_P0_CASES,
    OCRRegion,
    check_arabic_case,
    map_ocr_regions,
    quality_observations,
    script_profile,
)
from gomrey.ir_provenance import assemble_ir, verify_coverage
from gomrey.parser_router import (
    BenchmarkCase,
    BenchmarkRun,
    BenchmarkScore,
    Preflight,
    Reconciliation,
    Route,
    check_second_parser_budget,
    classify_workload,
    preflight,
    reconcile_units,
    route,
    score_run,
    to_source_ir,
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
    "BenchmarkCase",
    "BenchmarkRun",
    "BenchmarkScore",
    "AdmissionError",
    "AdmissionReceipt",
    "ARABIC_P0_CASES",
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
    "KNOWN_WORKERS",
    "LITEPARSE_BASELINE",
    "MemoryBlobStore",
    "MemoryCanonicalStore",
    "NarrativeSection",
    "OCRRegion",
    "ParserAdapter",
    "ParserIntermediate",
    "Preflight",
    "Principal",
    "QuarantinedView",
    "QualificationProfile",
    "Reconciliation",
    "ResourceBudget",
    "RevocationReceipt",
    "Route",
    "SourceArtifactRecord",
    "SourceUnitRecord",
    "StageAttemptRecord",
    "TempLease",
    "TempLeaseRegistry",
    "TrustedRelease",
    "UnitLedger",
    "UnknownUnit",
    "UrlVerdict",
    "WorkerAuthorization",
    "WorkerEnvelope",
    "WorkspaceRecord",
    "admit_source",
    "admit_worker",
    "authorize_fetch",
    "assemble_ir",
    "backoff_seconds",
    "can_access",
    "check_arabic_case",
    "check_archive_entry",
    "check_qualification",
    "check_second_parser_budget",
    "classify_failure",
    "classify_sensitivity",
    "classify_url",
    "classify_workload",
    "content_identity",
    "deny_active_content",
    "enforce_file_budgets",
    "enforce_remote_budgets",
    "file_admission_report",
    "is_duplicate",
    "is_trusted",
    "map_ocr_regions",
    "map_structured_output",
    "normalize_path",
    "normalized_fetch_result",
    "owner_to_scope",
    "preflight",
    "presentation_to_artifact",
    "presentation_to_revision",
    "progress_event",
    "promote_to_trusted",
    "quality_observations",
    "reconcile",
    "reconcile_mime",
    "reconcile_units",
    "revoke_source",
    "route",
    "run_parser",
    "scan_active_content",
    "score_run",
    "script_profile",
    "select_parser",
    "should_retry",
    "slides_to_narrative",
    "sniff_mime",
    "taint_content",
    "to_source_ir",
    "transition",
    "transition_trust",
    "validate_intermediate",
    "validate_redirect_chain",
    "verify_coverage",
]
