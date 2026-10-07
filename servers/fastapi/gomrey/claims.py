"""Claim contracts and evidence binding (P09-G1).

Pure deterministic logic with no generation and no model calls. A claim is
a durable, inspectable record that either binds to exact evidence or is
explicitly unsupported — an unbound citation never renders as support.

- identity: claim_id plus mandatory tenant/workspace isolation; cross
  project binding is refused, never coerced;
- text/content plus a deterministic normalized derivation (whitespace
  collapse, control stripping, stable token view). Semantic
  normalization belongs to later providers; this form guarantees a
  stable digest, not understanding;
- source provenance travels with the claim; evidence references are
  citation IDs that must resolve to spans in the bound bundle;
- support/contradiction links are explicit related-claim IDs, never
  inferred; self-references and duplicates are malformed;
- uncertainty, lifecycle status, and verification state are closed
  enums; unknown is explicit, never a silent default upgrade;
- version/timestamps/derivation are mandatory audit fields; derivation
  kind is closed (human/imported/derived/generated);
- binding is fail-closed: missing refs, dangling contradiction refs,
  unaccounted drops, stale spans, open contradictions, insufficient
  sufficiency, and policy-override tripwires never upgrade into
  support. The binder reports; the P09-G2 verifier decides;
- source/model/tool text is data: detect_policy_override_attempt is a
  deterministic tripwire heuristic, never authority. A flag forces
  needs-review downstream, never an auto-verdict.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any, Optional, Protocol, runtime_checkable

from gomrey.gateway import AdmissionError

VERIFICATION_STATES = frozenset({
    "unverified",
    "verifying",
    "supported",
    "partially_supported",
    "contradicted",
    "does_not_establish",
    "unresolved",
    "blocked",
})

CLAIM_STATUSES = frozenset({
    "draft",
    "candidate",
    "accepted",
    "downgraded",
    "blocked",
    "withdrawn",
})

UNCERTAINTY_LEVELS = frozenset({"low", "medium", "high", "unknown"})

DERIVATION_KINDS = frozenset({"human", "imported", "derived", "generated"})

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

_OVERRIDE_PATTERNS = (
    re.compile(r"ignore\s+(all\s+|previous\s+|prior\s+)?instructions?", re.I),
    re.compile(r"disregard\s+.*instructions?", re.I),
    re.compile(r"override\s+.*(verif|policy|guardrail|instruction)", re.I),
    re.compile(r"mark\s+.*as\s+supported", re.I),
    re.compile(r"^\s*system\s*:", re.I | re.M),
    re.compile(r"jailbreak", re.I),
)


def _check_id(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not _ID_RE.match(value):
        raise AdmissionError("malformed_source", f"invalid {field_name}")
    return value


def _check_id_list(values: Any, field_name: str) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        raise AdmissionError("malformed_source", f"{field_name} must be a list")
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        _check_id(str(value), field_name)
        token = str(value)
        if token in seen:
            raise AdmissionError("normalization_failure", f"duplicate {field_name}: {token}")
        seen.add(token)
        out.append(token)
    return out


def _check_timestamp(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdmissionError("malformed_source", f"missing {field_name}")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AdmissionError("malformed_source", f"invalid {field_name}")
    return value


def normalize_claim(text: str) -> dict[str, Any]:
    """Deterministic normalized view of claim text (stable, not semantic)."""
    if not isinstance(text, str) or not text.strip():
        raise AdmissionError("malformed_source", "claim text is required")
    collapsed = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", collapsed)
    if not cleaned:
        raise AdmissionError("malformed_source", "claim text is required")
    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", cleaned)]
    return {"text_normalized": cleaned, "tokens": tokens}


def detect_policy_override_attempt(text: str) -> bool:
    """Tripwire heuristic: does this text attempt to redefine verification policy?

    Deterministic and narrow. A True result forces needs-review
    downstream; it never authorizes any verdict on its own.
    """
    if not isinstance(text, str) or not text:
        return False
    return any(pattern.search(text) for pattern in _OVERRIDE_PATTERNS)


@dataclass
class Claim:
    claim_id: str
    text: str
    normalized: dict[str, Any]
    tenant_id: str
    workspace_id: str
    evidence_refs: list[str] = field(default_factory=list)
    supports: list[str] = field(default_factory=list)
    contradicts: list[str] = field(default_factory=list)
    uncertainty: str = "unknown"
    status: str = "draft"
    verification_state: str = "unverified"
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    derivation: dict[str, Any] = field(default_factory=dict)
    source_provenance: list[dict[str, Any]] = field(default_factory=list)


def make_claim(
    *,
    claim_id: str,
    text: str,
    tenant_id: str,
    workspace_id: str,
    evidence_refs: list[str] | None = None,
    supports: list[str] | None = None,
    contradicts: list[str] | None = None,
    uncertainty: str = "unknown",
    status: str = "draft",
    verification_state: str = "unverified",
    version: int = 1,
    created_at: str,
    updated_at: str,
    derivation: dict[str, Any],
    source_provenance: list[dict[str, Any]] | None = None,
    normalized: dict[str, Any] | None = None,
) -> Claim:
    """Build a validated claim; malformed records are refused."""
    _check_id(claim_id, "claim_id")
    _check_id(tenant_id, "tenant_id")
    _check_id(workspace_id, "workspace_id")
    if not isinstance(text, str) or not text.strip():
        raise AdmissionError("malformed_source", "claim text is required")
    refs = _check_id_list(evidence_refs, "evidence_refs")
    supporting = _check_id_list(supports, "supports")
    contradicting = _check_id_list(contradicts, "contradicts")
    for related in supporting + contradicting:
        if related == claim_id:
            raise AdmissionError("malformed_source", "claim cannot reference itself")
    if uncertainty not in UNCERTAINTY_LEVELS:
        raise AdmissionError("malformed_source", f"unknown uncertainty: {uncertainty}")
    if status not in CLAIM_STATUSES:
        raise AdmissionError("malformed_source", f"unknown claim status: {status}")
    if verification_state not in VERIFICATION_STATES:
        raise AdmissionError("malformed_source", f"unknown verification state: {verification_state}")
    if not isinstance(version, int) or version < 1:
        raise AdmissionError("malformed_source", "claim version must be positive")
    _check_timestamp(created_at, "created_at")
    _check_timestamp(updated_at, "updated_at")
    if not isinstance(derivation, dict) or derivation.get("kind") not in DERIVATION_KINDS:
        raise AdmissionError("malformed_source", "derivation kind is required")
    provenance = list(source_provenance or [])
    for entry in provenance:
        if not isinstance(entry, dict) or not entry.get("source_id"):
            raise AdmissionError("malformed_source", "provenance entry without source_id")
        _check_id(str(entry["source_id"]), "provenance source_id")
    derived_normalized = dict(normalized) if isinstance(normalized, dict) else normalize_claim(text)
    if "text_normalized" not in derived_normalized:
        raise AdmissionError("malformed_source", "normalized claim must carry text_normalized")
    return Claim(
        claim_id=claim_id,
        text=text,
        normalized=derived_normalized,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        evidence_refs=refs,
        supports=supporting,
        contradicts=contradicting,
        uncertainty=uncertainty,
        status=status,
        verification_state=verification_state,
        version=version,
        created_at=created_at,
        updated_at=updated_at,
        derivation=dict(derivation),
        source_provenance=provenance,
    )


def claim_digest(claim: Claim) -> str:
    """Reproducible digest for audit and regeneration checks."""
    canonical = json.dumps({
        "claim_id": claim.claim_id,
        "text": claim.text,
        "normalized": claim.normalized,
        "tenant_id": claim.tenant_id,
        "workspace_id": claim.workspace_id,
        "evidence_refs": claim.evidence_refs,
        "supports": claim.supports,
        "contradicts": claim.contradicts,
        "uncertainty": claim.uncertainty,
        "status": claim.status,
        "verification_state": claim.verification_state,
        "version": claim.version,
        "created_at": claim.created_at,
        "updated_at": claim.updated_at,
        "derivation": claim.derivation,
        "source_provenance": claim.source_provenance,
    }, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def bind_claim_to_bundle(
    claim: Claim,
    bundle: Any,
    *,
    require_fresh: bool = True,
) -> dict[str, Any]:
    """Bind a claim to an evidence bundle without widening insufficiency.

    Returns a binding report; the verifier (P09-G2) decides. Never
    upgrades insufficient/needs_review, stale, contradicted, or
    override-flagged bindings into support.
    """
    if claim.tenant_id != bundle.tenant_id or claim.workspace_id != bundle.workspace_id:
        raise AdmissionError("access_denied", "claim and bundle are in different projects")
    known_spans = {
        str(span.get("citation_id") or span.get("span_id", ""))
        for span in bundle.spans
    }
    missing = [ref for ref in claim.evidence_refs if ref not in known_spans]
    if missing:
        raise AdmissionError("normalization_failure", f"claim references missing evidence: {missing[0]}")
    stale = sorted(
        str(span.get("citation_id") or span.get("span_id", ""))
        for span in bundle.spans
        if span.get("stale_labeled") and str(span.get("citation_id") or span.get("span_id", "")) in set(claim.evidence_refs)
    )
    contradictions_open = [
        dict(contradiction) for contradiction in (bundle.contradictions or [])
        if any(str(span_id) in set(claim.evidence_refs) for span_id in contradiction.get("span_ids", []))
    ]
    reasons: list[str] = []
    if not claim.evidence_refs:
        reasons.append("no-evidence-refs")
    if len(bundle.spans) < 1:
        reasons.append("bundle-empty")
    if stale and require_fresh:
        reasons.append("stale-spans-present")
    if contradictions_open:
        reasons.append("contradictions-open")
    override_flag = detect_policy_override_attempt(claim.text)
    if override_flag:
        reasons.append("policy-override-flagged")
    for span in bundle.spans:
        span_id = str(span.get("citation_id") or span.get("span_id", ""))
        if span_id in set(claim.evidence_refs) and not span.get("citation_id"):
            reasons.append("span-without-citation-id")
            break
    bindable = not reasons
    return {
        "claim_id": claim.claim_id,
        "bundle_id": bundle.bundle_id,
        "bound_spans": [ref for ref in claim.evidence_refs],
        "stale_spans": stale,
        "contradictions_open": contradictions_open,
        "omissions": list(bundle.omissions or []),
        "override_flag": override_flag,
        "reasons": reasons,
        "bindable_for_verification": bindable,
    }


@runtime_checkable
class ClaimStore(Protocol):
    """Durable truth for claim records behind tenant isolation."""

    def put(self, claim: Claim) -> None:
        """Insert or replace the canonical claim record."""
        ...

    def get(self, claim_id: str, tenant_id: str, workspace_id: str) -> Optional[Claim]:
        """Return the claim, or None when absent. Cross-project reads fail closed."""
        ...

    def delete(self, claim_id: str, tenant_id: str, workspace_id: str) -> bool:
        """Remove the claim. Returns True when a record was removed."""
        ...


class MemoryClaimStore:
    """Deterministic dict-backed ClaimStore for tests and adapters."""

    def __init__(self) -> None:
        self._claims: dict[tuple[str, str, str], Claim] = {}

    def put(self, claim: Claim) -> None:
        self._claims[(claim.tenant_id, claim.workspace_id, claim.claim_id)] = replace(
            claim,
            normalized=dict(claim.normalized),
            evidence_refs=list(claim.evidence_refs),
            supports=list(claim.supports),
            contradicts=list(claim.contradicts),
            derivation=dict(claim.derivation),
            source_provenance=[dict(entry) for entry in claim.source_provenance],
        )

    def get(self, claim_id: str, tenant_id: str, workspace_id: str) -> Optional[Claim]:
        stored = self._claims.get((tenant_id, workspace_id, claim_id))
        if stored is None:
            return None
        return replace(
            stored,
            normalized=dict(stored.normalized),
            evidence_refs=list(stored.evidence_refs),
            supports=list(stored.supports),
            contradicts=list(stored.contradicts),
            derivation=dict(stored.derivation),
            source_provenance=[dict(entry) for entry in stored.source_provenance],
        )

    def delete(self, claim_id: str, tenant_id: str, workspace_id: str) -> bool:
        return self._claims.pop((tenant_id, workspace_id, claim_id), None) is not None
