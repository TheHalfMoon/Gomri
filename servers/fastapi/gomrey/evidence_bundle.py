"""Evidence bundle and sufficiency checks (P08-G3).

Pure deterministic logic with no generation and no model calls. The
bundle is the bounded, inspectable evidence set that generation may
consume — and the sufficiency verdict is what tells generation to stop:

- binding: exact source revisions, resolved spans, retrieval
  identities, contradictions, omissions/truncation, freshness, scope,
  digest, and verification state travel together. A bundle missing any
  of these is malformed, not partial;
- contradictions are marked and escalate to needs_review. They are
  never averaged away or silently dropped;
- omissions are accounted: dropped candidates without recorded reasons
  are malformed input, not acceptable loss;
- sufficiency: too few spans, stale spans where fresh is required, or
  open contradictions yield insufficient/needs_review — the abstention
  signal downstream generation must obey. Claim-support classification
  itself belongs to the P09 decision fabric; this gate decides whether
  there is anything to classify with.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

from gomrey.gateway import AdmissionError

SUFFICIENCY_VERDICTS = frozenset({"sufficient", "insufficient", "needs_review"})


@dataclass
class EvidenceBundle:
    bundle_id: str
    query: str
    tenant_id: str
    workspace_id: str
    source_revisions: list[dict[str, str]] = field(default_factory=list)
    spans: list[dict[str, Any]] = field(default_factory=list)
    retrieval_identities: list[str] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    omissions: list[dict[str, str]] = field(default_factory=list)
    verification_state: str = "unverified"


def build_bundle(
    *,
    bundle_id: str,
    query: str,
    tenant_id: str,
    workspace_id: str,
    source_revisions: list[dict[str, str]],
    spans: list[dict[str, Any]],
    retrieval_identities: list[str],
    contradictions: list[dict[str, Any]] | None = None,
    omissions: list[dict[str, str]] | None = None,
    dropped_without_reason: int = 0,
) -> EvidenceBundle:
    """Assemble a bundle; unaccounted drops and dangling refs refused."""
    if not bundle_id or not query or not tenant_id or not workspace_id:
        raise AdmissionError("malformed_source", "bundle missing identity")
    if dropped_without_reason > 0:
        raise AdmissionError("normalization_failure", "dropped candidates lack omission reasons")
    for revision in source_revisions:
        if not revision.get("source_id") or not revision.get("digest"):
            raise AdmissionError("malformed_source", "source revision without identity")
    known_spans = set()
    for span in spans:
        span_id = span.get("citation_id") or span.get("span_id")
        if not span_id:
            raise AdmissionError("normalization_failure", "span without identity")
        known_spans.add(str(span_id))
    for contradiction in contradictions or []:
        refs = [str(r) for r in contradiction.get("span_ids", [])]
        dangling = [r for r in refs if r not in known_spans]
        if dangling:
            raise AdmissionError("normalization_failure",
                                 f"contradiction references unknown spans: {dangling[0]}")
    return EvidenceBundle(
        bundle_id=bundle_id,
        query=query,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        source_revisions=list(source_revisions),
        spans=list(spans),
        retrieval_identities=list(retrieval_identities),
        contradictions=list(contradictions or []),
        omissions=list(omissions or []),
    )


def bundle_digest(bundle: EvidenceBundle) -> str:
    """Reproducible digest for audit and regeneration checks."""
    canonical = json.dumps({
        "bundle_id": bundle.bundle_id,
        "query": bundle.query,
        "tenant_id": bundle.tenant_id,
        "workspace_id": bundle.workspace_id,
        "source_revisions": bundle.source_revisions,
        "spans": bundle.spans,
        "retrieval_identities": bundle.retrieval_identities,
        "contradictions": bundle.contradictions,
        "omissions": bundle.omissions,
        "verification_state": bundle.verification_state,
    }, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def sufficiency_check(
    bundle: EvidenceBundle,
    *,
    min_spans: int = 2,
    require_fresh: bool = True,
) -> dict[str, Any]:
    """Decide sufficient / insufficient / needs_review with named reasons."""
    if min_spans < 1:
        raise AdmissionError("malformed_source", "min_spans must be positive")
    reasons: list[str] = []
    if len(bundle.spans) < min_spans:
        reasons.append("too-few-spans")
    stale = sorted(str(s.get("citation_id") or s.get("span_id", ""))
                   for s in bundle.spans if s.get("stale_labeled"))
    if stale and require_fresh:
        reasons.append("stale-spans-present")
    if bundle.contradictions:
        return {"verdict": "needs_review", "reasons": ["contradictions-open"] + reasons,
                "stale_spans": stale}
    if reasons:
        return {"verdict": "insufficient", "reasons": reasons, "stale_spans": stale}
    return {"verdict": "sufficient", "reasons": [], "stale_spans": stale}
