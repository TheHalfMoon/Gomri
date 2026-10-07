"""Tests for the P07-G3 connector sync contracts (no providers)."""

import pytest

from gomrey.connector_sync import (
    SyncCursor,
    apply_sync,
    check_handle,
    freshness,
    issue_handle,
    map_acl,
    refresh_handle,
    sync_backoff_seconds,
)
from gomrey.gateway import AdmissionError


def _handle(**overrides):
    base = {
        "handle_id": "cred-1",
        "provider": "drive",
        "owner_principal": "u-1",
        "scopes": ["source:read", "source:write"],
        "expires_at": "2027-01-01T00:00:00Z",
    }
    base.update(overrides)
    return issue_handle(**base)


def _cursor() -> SyncCursor:
    return SyncCursor(provider="drive", cursor_token="cur-1", last_revision="r-1")


def test_credential_lifecycle_is_handle_only() -> None:
    handle = _handle()
    assert handle.revoked is False
    check_handle(handle, now_iso="2026-10-07T00:00:00Z", required_scope="source:read")
    with pytest.raises(AdmissionError):
        check_handle(handle, now_iso="2026-10-07T00:00:00Z", required_scope="admin:all")
    with pytest.raises(AdmissionError):
        check_handle(handle, now_iso="2028-01-01T00:00:00Z", required_scope="source:read")
    refreshed = refresh_handle(handle, new_expiry="2028-01-01T00:00:00Z")
    assert refreshed.expires_at > handle.expires_at
    with pytest.raises(AdmissionError):
        refresh_handle(handle, new_expiry="2020-01-01T00:00:00Z")
    with pytest.raises(AdmissionError):
        _handle(scopes=[])
    # The handle type cannot express raw secrets: no such field exists.
    assert not hasattr(handle, "secret") and not hasattr(handle, "token")


def test_sync_applies_upserts_and_tombstones() -> None:
    receipt = apply_sync(
        sync_id="s-1", provider="drive", cursor=_cursor(),
        changes=[{"item_id": "a", "revision": "r-2"}, {"item_id": "b", "revision": "r-2"}],
        deletions=["c"], new_cursor_token="cur-2", new_revision="r-2",
        known_item_ids=frozenset({"a", "b", "c"}),
    )
    assert receipt.status == "complete"
    assert receipt.is_fresh is True
    assert receipt.tombstones == ("c",)
    assert receipt.cursor_after == "cur-2"
    assert (receipt.revision_before, receipt.revision_after) == ("r-1", "r-2")
    with pytest.raises(AdmissionError):
        apply_sync(sync_id="s", provider="drive", cursor=_cursor(),
                   changes=[{"item_id": "", "revision": "r"}], deletions=[],
                   new_cursor_token="cur-2", new_revision="r-2",
                   known_item_ids=frozenset())
    with pytest.raises(AdmissionError):
        apply_sync(sync_id="s", provider="github", cursor=_cursor(),
                   changes=[], deletions=[],
                   new_cursor_token="cur-2", new_revision="r-2",
                   known_item_ids=frozenset())
    with pytest.raises(AdmissionError):
        apply_sync(sync_id="s", provider="drive", cursor=_cursor(),
                   changes=[], deletions=["ghost"],
                   new_cursor_token="cur-2", new_revision="r-2",
                   known_item_ids=frozenset({"a"}))
    with pytest.raises(AdmissionError):
        apply_sync(sync_id="s", provider="drive", cursor=_cursor(),
                   changes=[{"item_id": "a", "revision": "r-2"},
                            {"item_id": "a", "revision": "r-3"}],
                   deletions=[], new_cursor_token="cur-2", new_revision="r-3",
                   known_item_ids=frozenset({"a"}))
    with pytest.raises(AdmissionError):
        apply_sync(sync_id="s", provider="drive", cursor=_cursor(),
                   changes=[], deletions=[],
                   new_cursor_token="cur-2", new_revision="",
                   known_item_ids=frozenset())


def test_interrupted_sync_is_stale_with_coordinates() -> None:
    receipt = apply_sync(
        sync_id="s-9", provider="drive", cursor=_cursor(),
        changes=[{"item_id": "a", "revision": "r-2"}],
        deletions=["b"], new_cursor_token="cur-2", new_revision="r-2",
        known_item_ids=frozenset({"a", "b"}),
        interrupted=True,
    )
    assert receipt.status == "partial-stale"
    assert receipt.is_fresh is False
    assert set(receipt.pending) == {"a", "b"}
    # Neither cursor nor revision advances past unapplied work.
    assert receipt.cursor_after == "cur-1"
    assert receipt.revision_after == "r-1"


def test_backoff_acl_and_freshness() -> None:
    assert sync_backoff_seconds(1) == 1.0
    assert sync_backoff_seconds(3) == 4.0
    grants = map_acl([
        {"principal": "u-1", "effect": "allow", "scopes": ["source:read"]},
        {"principal": "u-9", "effect": "deny", "scopes": ["source:read"]},
    ])
    assert grants[1]["effect"] == "deny"
    with pytest.raises(AdmissionError):
        map_acl([{"principal": "u-1", "effect": "maybe", "scopes": []}])
    with pytest.raises(AdmissionError):
        map_acl([{"principal": "", "effect": "allow", "scopes": []}])
    assert freshness(10.0, 60.0) == {"is_fresh": True, "stale": False}
    assert freshness(3600.0, 60.0) == {"is_fresh": False, "stale": True}
    with pytest.raises(AdmissionError):
        freshness(-1.0, 60.0)
