"""Connector sync contracts: cursors, tombstones, credentials, ACLs (P07-G3).

Pure deterministic logic with no provider SDKs and no network. Sync is
how outside systems enter Gomrey over time, so the contract makes time
itself explicit:

- cursors: opaque resume tokens with revision identity; unknown cursors
  are malformed, never guessed forward;
- changes: upserts carry provider-native revisions; deletions arrive as
  tombstones that propagate — removal is an event, never an absence;
- partial sync: interruption yields exact pending coordinates and a
  stale marker. Stale data is labeled stale; nothing upgrades it to
  fresh by assumption, and consumers must read the flag;
- credentials: handles are opaque references with scopes, expiry, and
  revocation. The handle type has no secret field by construction — raw
  secrets cannot be expressed, let alone stored. Refresh rotates,
  revocation kills, expiry denies;
- backoff: rate-limit discipline reuses the P04 job backoff, not a
  second invented curve;
- ACL resync: provider access entries map to Gomrey scope grants with
  explicit denies preserved; unknown shapes fail closed.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
from typing import Any

from gomrey.gateway import AdmissionError
from gomrey.jobs import backoff_seconds


@dataclass(frozen=True)
class CredentialHandle:
    handle_id: str
    provider: str
    owner_principal: str
    scopes: tuple[str, ...]
    expires_at: str
    revoked: bool = False


@dataclass(frozen=True)
class SyncCursor:
    provider: str
    cursor_token: str
    last_revision: str


@dataclass(frozen=True)
class SyncReceipt:
    sync_id: str
    provider: str
    cursor_before: str
    cursor_after: str
    revision_before: str
    revision_after: str
    upserts: tuple[dict[str, Any], ...]
    tombstones: tuple[str, ...]
    pending: tuple[str, ...]
    status: str
    is_fresh: bool


def issue_handle(
    *,
    handle_id: str,
    provider: str,
    owner_principal: str,
    scopes: list[str],
    expires_at: str,
) -> CredentialHandle:
    """Create a credential handle. There is no parameter for raw secrets."""
    if not handle_id or not provider or not owner_principal or not expires_at:
        raise AdmissionError("malformed_source", "incomplete credential handle")
    if not scopes:
        raise AdmissionError("access_denied", "credential without scopes refused")
    return CredentialHandle(
        handle_id=handle_id,
        provider=provider,
        owner_principal=owner_principal,
        scopes=tuple(scopes),
        expires_at=expires_at,
    )


def refresh_handle(handle: CredentialHandle, *, new_expiry: str) -> CredentialHandle:
    """Rotate a handle forward; the old record stays revoked in history."""
    if handle.revoked:
        raise AdmissionError("access_denied", "revoked credential cannot refresh")
    if not new_expiry or new_expiry <= handle.expires_at:
        raise AdmissionError("malformed_source", "refresh must extend expiry")
    return CredentialHandle(
        handle_id=handle.handle_id,
        provider=handle.provider,
        owner_principal=handle.owner_principal,
        scopes=handle.scopes,
        expires_at=new_expiry,
    )


def check_handle(handle: CredentialHandle, *, now_iso: str, required_scope: str) -> None:
    """Authorize one connector action, or deny with a typed error."""
    if handle.revoked:
        raise AdmissionError("access_denied", "revoked credential refused")
    if now_iso >= handle.expires_at:
        raise AdmissionError("access_denied", "expired credential refused")
    if required_scope not in handle.scopes:
        raise AdmissionError("access_denied", "credential lacks required scope")


def sync_backoff_seconds(attempt: int) -> float:
    """Rate-limit discipline reuses the P04 deterministic backoff."""
    return backoff_seconds(attempt)


def apply_sync(
    *,
    sync_id: str,
    provider: str,
    cursor: SyncCursor,
    changes: list[dict[str, Any]],
    deletions: list[str],
    new_cursor_token: str,
    new_revision: str,
    known_item_ids: frozenset[str],
    interrupted: bool = False,
) -> SyncReceipt:
    """Apply one sync batch: upserts, tombstones, and honest partial states.

    The caller states its full item inventory every time — tombstones for
    unknown items fail instead of silently deleting nothing.
    """
    if cursor.provider != provider:
        raise AdmissionError("malformed_source", "cursor belongs to another provider")
    if not cursor.cursor_token or not new_cursor_token:
        raise AdmissionError("malformed_source", "sync cursors must be opaque and non-empty")
    if not new_revision or not cursor.last_revision:
        raise AdmissionError("malformed_source", "sync revisions must be non-empty")
    upserts: list[dict[str, Any]] = []
    for change in changes:
        item_id = change.get("item_id")
        revision = change.get("revision")
        if not isinstance(item_id, str) or not item_id or not isinstance(revision, str) or not revision:
            raise AdmissionError("normalization_failure", "change without item identity")
        upserts.append({"item_id": item_id, "revision": revision})
    if len({u["item_id"] for u in upserts}) != len(upserts):
        raise AdmissionError("normalization_failure", "batch revises one item twice ambiguously")
    tombstones = [d for d in deletions if isinstance(d, str) and d]
    if len(tombstones) != len(deletions):
        raise AdmissionError("normalization_failure", "deletion without item identity")
    ghosts = [d for d in tombstones if d not in known_item_ids]
    if ghosts:
        raise AdmissionError("normalization_failure", f"tombstone for unknown items: {ghosts[0]}")
    pending: tuple[str, ...] = ()
    if interrupted:
        pending = tuple(u["item_id"] for u in upserts) + tuple(tombstones)
    advanced = not interrupted
    return SyncReceipt(
        sync_id=sync_id,
        provider=provider,
        cursor_before=cursor.cursor_token,
        cursor_after=new_cursor_token if advanced else cursor.cursor_token,
        revision_before=cursor.last_revision,
        revision_after=new_revision if advanced else cursor.last_revision,
        upserts=tuple(upserts),
        tombstones=tuple(tombstones),
        pending=pending,
        status="partial-stale" if interrupted else "complete",
        is_fresh=advanced,
    )


def map_acl(provider_aces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map provider access entries to Gomrey scope grants, denies preserved."""
    grants: list[dict[str, Any]] = []
    for ace in provider_aces:
        principal = ace.get("principal")
        effect = ace.get("effect", "allow")
        scopes = ace.get("scopes", [])
        if not isinstance(principal, str) or not principal:
            raise AdmissionError("normalization_failure", "ACE without principal")
        if effect not in {"allow", "deny"}:
            raise AdmissionError("normalization_failure", "ACE with unknown effect")
        if not isinstance(scopes, list) or not all(isinstance(s, str) for s in scopes):
            raise AdmissionError("normalization_failure", "ACE with malformed scopes")
        grants.append({"principal": principal, "effect": effect, "scopes": list(scopes)})
    return grants


def freshness(last_success_age_s: float, max_age_s: float) -> dict[str, Any]:
    """Decide fresh vs stale from ages; stale is a label, never fresh."""
    if last_success_age_s < 0 or max_age_s <= 0:
        raise AdmissionError("malformed_source", "invalid freshness ages")
    fresh = last_success_age_s <= max_age_s
    return {"is_fresh": fresh, "stale": not fresh}
