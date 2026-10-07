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
- web_acquisition: P07-G1 bounded crawl contracts (explicit scope,
  depth/page budgets, snapshot records, robots/terms decisions). Pure
  logic, never fetches.
- media_pipeline: P07-G2 media contracts (validated timelines,
  transcript/visual alignment with explicit gaps, timestamp spans,
  degraded-mode labels). Pure logic, no media I/O.
- connector_sync: P07-G3 sync contracts (opaque cursors, tombstones,
  stale-marked partials, secret-less credential handles, ACL mapping,
  freshness labels). Pure logic, no providers.
- source_parity: P07 exit proof (web/media/connector families into the
  single IR record shape, one assembly gate, one coverage gate). Pure
  logic.
- retrieval_pipeline: P08-G1 layered retrieval (ACL-first filter, exact
  boost, lexical channel, explicit fusion, freshness and diversity
  constraints). Pure logic, no index servers.
- citations: P08-G2 locators per source family plus a resolver that
  fails loudly on unresolvable IDs. Pure logic.
- evidence_bundle: P08-G3 bounded bundles with digests, marked
  contradictions, accounted omissions, and sufficiency verdicts. Pure
  logic, no generation.
- claims: P09-G1 durable claim records with verification states,
  evidence binding that never widens insufficiency into support, and
  a policy-override tripwire. Pure logic, no models.
- verification: P09-G2 deterministic verdicts with quantity/date
  agreement checks and a provider seam that can never overrule hard
  policy. Pure logic, no model calls.
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
from gomrey.web_acquisition import (
    CrawlPlan,
    CrawlScope,
    acquisition_policy,
    admit_child,
    page_snapshot,
    plan_crawl,
)
from gomrey.media_pipeline import (
    MediaTimeline,
    SceneSegment,
    TranscriptSegment,
    align_transcript_visual,
    degraded_modes,
    media_span,
    validate_timeline,
)
from gomrey.connector_sync import (
    CredentialHandle,
    SyncCursor,
    SyncReceipt,
    apply_sync,
    check_handle,
    freshness,
    issue_handle,
    map_acl,
    refresh_handle,
    sync_backoff_seconds,
)
from gomrey.source_parity import (
    media_aligned_to_units,
    parity_assemble,
    sync_changes_to_units,
    web_page_to_units,
)
from gomrey.retrieval_pipeline import (
    acl_filter,
    apply_constraints,
    exact_boost,
    fuse,
    lexical_overlap,
    retrieve,
)
from gomrey.citations import BrokenCitation, citation_id, make_locator, resolve
from gomrey.evidence_bundle import (
    EvidenceBundle,
    build_bundle,
    bundle_digest,
    sufficiency_check,
)
from gomrey.claims import (
    CLAIM_STATUSES,
    DERIVATION_KINDS,
    UNCERTAINTY_LEVELS,
    VERIFICATION_STATES,
    Claim,
    ClaimStore,
    MemoryClaimStore,
    bind_claim_to_bundle,
    claim_digest,
    detect_policy_override_attempt,
    make_claim,
    normalize_claim,
)
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
from gomrey.verification import STANCES, VERDICTS, check_quantity_agreement, verify_claim
from gomrey.seams import BlobStore, CanonicalStore, MemoryBlobStore, MemoryCanonicalStore

__all__ = [
    "BenchmarkCase",
    "BenchmarkRun",
    "BenchmarkScore",
    "BrokenCitation",
    "AdmissionError",
    "AdmissionReceipt",
    "ARABIC_P0_CASES",
    "ArtifactRecord",
    "ArtifactRevisionRecord",
    "BlobStore",
    "BudgetExhausted",
    "CLAIM_STATUSES",
    "CanonicalStore",
    "Claim",
    "ClaimStore",
    "CrawlPlan",
    "CrawlScope",
    "CredentialHandle",
    "DERIVATION_KINDS",
    "DuplicateDeclaration",
    "DurableJob",
    "EvidenceBundle",
    "IdempotencyLedger",
    "IllegalTransition",
    "IllegalTrustTransition",
    "IngestionManifestRecord",
    "JobRecord",
    "KNOWN_WORKERS",
    "LITEPARSE_BASELINE",
    "MediaTimeline",
    "MemoryBlobStore",
    "MemoryCanonicalStore",
    "MemoryClaimStore",
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
    "SceneSegment",
    "STANCES",
    "SourceArtifactRecord",
    "SourceUnitRecord",
    "StageAttemptRecord",
    "SyncCursor",
    "SyncReceipt",
    "TempLease",
    "TempLeaseRegistry",
    "TranscriptSegment",
    "TrustedRelease",
    "UnitLedger",
    "UNCERTAINTY_LEVELS",
    "UnknownUnit",
    "UrlVerdict",
    "VERDICTS",
    "VERIFICATION_STATES",
    "WorkerAuthorization",
    "WorkerEnvelope",
    "WorkspaceRecord",
    "acl_filter",
    "align_transcript_visual",
    "acquisition_policy",
    "admit_child",
    "admit_source",
    "admit_worker",
    "apply_constraints",
    "apply_sync",
    "authorize_fetch",
    "assemble_ir",
    "backoff_seconds",
    "bind_claim_to_bundle",
    "build_bundle",
    "bundle_digest",
    "can_access",
    "check_arabic_case",
    "check_archive_entry",
    "check_quantity_agreement",
    "check_qualification",
    "check_second_parser_budget",
    "citation_id",
    "classify_failure",
    "classify_sensitivity",
    "classify_url",
    "classify_workload",
    "content_identity",
    "check_handle",
    "claim_digest",
    "deny_active_content",
    "degraded_modes",
    "detect_policy_override_attempt",
    "enforce_file_budgets",
    "enforce_remote_budgets",
    "exact_boost",
    "file_admission_report",
    "freshness",
    "fuse",
    "is_duplicate",
    "is_trusted",
    "issue_handle",
    "lexical_overlap",
    "map_acl",
    "map_ocr_regions",
    "make_claim",
    "map_structured_output",
    "make_locator",
    "media_aligned_to_units",
    "media_span",
    "normalize_claim",
    "normalize_path",
    "normalized_fetch_result",
    "owner_to_scope",
    "page_snapshot",
    "parity_assemble",
    "plan_crawl",
    "preflight",
    "presentation_to_artifact",
    "presentation_to_revision",
    "progress_event",
    "promote_to_trusted",
    "quality_observations",
    "reconcile",
    "reconcile_mime",
    "reconcile_units",
    "refresh_handle",
    "resolve",
    "revoke_source",
    "retrieve",
    "route",
    "run_parser",
    "scan_active_content",
    "score_run",
    "script_profile",
    "select_parser",
    "should_retry",
    "slides_to_narrative",
    "sniff_mime",
    "sufficiency_check",
    "sync_backoff_seconds",
    "sync_changes_to_units",
    "taint_content",
    "to_source_ir",
    "transition",
    "transition_trust",
    "validate_intermediate",
    "validate_redirect_chain",
    "validate_timeline",
    "verify_claim",
    "verify_coverage",
    "web_page_to_units",
]
