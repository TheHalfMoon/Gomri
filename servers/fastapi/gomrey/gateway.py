"""Source gateway admission: identity, trust lifecycle, access boundary (P05-G1).

Pure deterministic logic with no database and no network. Persistence
arrives behind the CanonicalStore seam; this module defines the rules any
backend must enforce:

- a source never enters trusted state silently: admission always lands in
  ``quarantined`` and promotion follows an explicit trust state machine;
- unvalidated external material is never indistinguishable from trusted
  normalized Source IR: only ``trusted-for-retrieval`` is retrievable, and
  only ``validated``/``parsed``/``normalized`` predecessors can reach it;
- access is deny-by-default with tenant/workspace scope and least
  privilege: no implicit global read, no cross-project access without an
  explicit grant;
- failures are structured AdmissionError codes shared by later grains
  (G2 file boundary, G3 remote gateway, G4 parser boundary);
- content identity is deterministic (sha256): exact duplicates, renames,
  and same-remote-bytes-twice collapse to one digest.
"""

from dataclasses import dataclass, field
from hashlib import sha256
import re
from typing import Any, Literal

TRUST_STATES = frozenset({
    "discovered",
    "received",
    "quarantined",
    "validated",
    "parsed",
    "normalized",
    "rejected",
    "trusted-for-retrieval",
})

TRUSTED_STATES = frozenset({"trusted-for-retrieval"})

LEGAL_TRUST_TRANSITIONS: dict[str, frozenset[str]] = {
    "discovered": frozenset({"received", "rejected"}),
    "received": frozenset({"quarantined", "rejected"}),
    "quarantined": frozenset({"validated", "rejected"}),
    "validated": frozenset({"parsed", "rejected"}),
    "parsed": frozenset({"normalized", "rejected"}),
    "normalized": frozenset({"trusted-for-retrieval", "rejected"}),
    "trusted-for-retrieval": frozenset(),
    "rejected": frozenset(),
}

ADMITTED_SOURCE_TYPES = frozenset({
    "pdf", "document", "web", "video", "audio",
    "spreadsheet", "image", "presentation", "connector", "other",
})

ADMITTED_ORIGINS = frozenset({
    "local", "web", "connector", "agent",
})

ERROR_CODES = frozenset({
    "unsupported_source",
    "unsafe_source",
    "malformed_source",
    "resource_limit_exceeded",
    "access_denied",
    "remote_fetch_denied",
    "parser_failure",
    "normalization_failure",
    "duplicate_source",
})

_READ_SCOPE: dict[str, str] = {
    "read": "source:read",
    "write": "source:write",
    "delete": "source:delete",
    "export": "source:export",
    "share": "source:share",
}

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")

_PARSER_BY_TYPE: dict[str, str] = {
    "pdf": "docling-default",
    "document": "docling-default",
    "presentation": "docling-default",
    "spreadsheet": "docling-default",
    "web": "crawl4ai-bounded",
    "video": "transcript-scene-worker",
    "audio": "asr-segment-worker",
    "image": "ocr-visual-worker",
    "connector": "connector-normalizer",
    "other": "fallback-second-parser",
}


@dataclass
class AdmissionError(Exception):
    code: str
    detail: str

    def __post_init__(self) -> None:
        if self.code not in ERROR_CODES:
            raise ValueError(f"unknown admission error code: {self.code}")


@dataclass
class IllegalTrustTransition(Exception):
    source_id: str
    from_state: str
    to_state: str


@dataclass
class Principal:
    """Who is acting: user, agent, service, or plugin worker."""

    principal_id: str
    tenant_id: str
    workspace_ids: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)


@dataclass
class AdmissionReceipt:
    source_id: str
    tenant_id: str
    workspace_id: str
    source_type: str
    origin: str
    original_digest: str
    trust_state: str
    parser_id: str
    duplicate_of: str | None = None


def is_trusted(state: str) -> bool:
    """Only trusted-for-retrieval counts as trusted; everything else is not."""
    return state in TRUSTED_STATES


def transition_trust(source_id: str, from_state: str, to_state: str) -> str:
    """Return to_state when the trust move is legal, else raise."""
    allowed = LEGAL_TRUST_TRANSITIONS.get(from_state)
    if allowed is None:
        raise IllegalTrustTransition(source_id, from_state, to_state)
    if to_state not in allowed:
        raise IllegalTrustTransition(source_id, from_state, to_state)
    return to_state


def content_identity(data: bytes) -> str:
    """Deterministic content identity for exact-duplicate detection."""
    return sha256(data).hexdigest()


def is_duplicate(digest: str, known_digests: set[str]) -> bool:
    """True when these exact bytes were already admitted."""
    return digest in known_digests


def select_parser(source_type: str) -> str:
    """Deterministic parser routing; unknown types are unsupported, not guessed."""
    parser = _PARSER_BY_TYPE.get(source_type)
    if parser is None:
        raise AdmissionError("unsupported_source", f"unknown source_type: {source_type}")
    return parser


def _require_id(field_name: str, value: Any) -> str:
    if not isinstance(value, str) or not _ID_RE.match(value):
        raise AdmissionError("malformed_source", f"invalid {field_name}")
    return value


def _require_tenant_scope(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise AdmissionError("malformed_source", "invalid tenant_id")
    return value


def can_access(
    principal: Principal,
    *,
    source_tenant: str,
    source_workspace: str,
    action: str,
) -> bool:
    """Deny-by-default access check with tenant isolation and least privilege.

    A principal may act only within its own tenant, only in a workspace it
    belongs to, and only with the scope the action requires. Unknown actions
    are denied. No global read exists.
    """
    scope = _READ_SCOPE.get(action)
    if scope is None:
        return False
    if principal.tenant_id != source_tenant:
        return False
    if source_workspace not in principal.workspace_ids:
        return False
    return scope in principal.scopes


def admit_source(
    request: dict[str, Any],
    principal: Principal,
    *,
    known_digests: set[str] | None = None,
) -> AdmissionReceipt:
    """Validate an admission request and land the source in quarantined.

    Raises AdmissionError with a structured code on any failure. Never
    returns a trusted state: callers must drive the trust machine through
    validation, parsing, and normalization (later grains) first.
    """
    source_id = _require_id("source_id", request.get("source_id"))
    tenant_id = _require_tenant_scope(request.get("tenant_id"))
    raw_workspace = request.get("workspace_id")
    if not isinstance(raw_workspace, str) or not _ID_RE.match(raw_workspace):
        raise AdmissionError("malformed_source", "invalid workspace_id")
    workspace_id = raw_workspace
    source_type = request.get("source_type")
    if source_type not in ADMITTED_SOURCE_TYPES:
        raise AdmissionError("unsupported_source", f"unsupported source_type: {source_type}")
    origin = request.get("origin")
    if origin not in ADMITTED_ORIGINS:
        raise AdmissionError("unsupported_source", f"unsupported origin: {origin}")
    digest = request.get("original_digest")
    if not isinstance(digest, str) or not _DIGEST_RE.match(digest):
        raise AdmissionError("malformed_source", "invalid original_digest")
    provenance = request.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("acquired_by"):
        raise AdmissionError("malformed_source", "provenance.acquired_by is required")
    if not can_access(
        principal,
        source_tenant=tenant_id,
        source_workspace=workspace_id,
        action="write",
    ):
        raise AdmissionError("access_denied", "principal may not admit into this workspace")
    if principal.tenant_id != tenant_id:
        raise AdmissionError("access_denied", "cross-tenant admission is denied")
    duplicate_of: str | None = None
    if known_digests is not None and digest in known_digests:
        duplicate_of = digest
    return AdmissionReceipt(
        source_id=source_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        source_type=str(source_type),
        origin=str(origin),
        original_digest=digest,
        trust_state="quarantined",
        parser_id=select_parser(str(source_type)),
        duplicate_of=duplicate_of,
    )
