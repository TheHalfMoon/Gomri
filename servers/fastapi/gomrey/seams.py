"""Narrow storage seams: CanonicalStore and BlobStore protocols.

The seam is the architecture: domain code depends on these protocols,
never on an engine, a driver, or a vendor SDK. Canonical records
(contracts.py) are the truth; anything derived from them — embeddings,
thumbnails, facets, previews — is a rebuildable projection and must be
recomputable after deletion.

MemoryCanonicalStore and MemoryBlobStore are deterministic implementations
for tests and for adapter qualification. Production backends arrive in
later grains behind the same protocols with migration discipline.
"""

from hashlib import sha256
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class CanonicalStore(Protocol):
    """Durable truth for Gomrey contract records."""

    def put(self, kind: str, record_id: str, record: dict[str, Any]) -> None:
        """Insert or replace the canonical record for (kind, record_id)."""
        ...

    def get(self, kind: str, record_id: str) -> Optional[dict[str, Any]]:
        """Return the canonical record, or None when absent."""
        ...

    def delete(self, kind: str, record_id: str) -> bool:
        """Remove the canonical record. Tombstone policy is set by the caller."""
        ...


@runtime_checkable
class BlobStore(Protocol):
    """Content-addressed immutable bytes for inputs and assets."""

    def put_bytes(self, data: bytes) -> str:
        """Store bytes and return their sha256 hex digest."""
        ...

    def get_bytes(self, digest: str) -> Optional[bytes]:
        """Return the bytes for a digest, or None when absent."""
        ...


class MemoryCanonicalStore:
    """Deterministic dict-backed CanonicalStore for tests."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], dict[str, Any]] = {}

    def put(self, kind: str, record_id: str, record: dict[str, Any]) -> None:
        self._records[(kind, record_id)] = dict(record)

    def get(self, kind: str, record_id: str) -> Optional[dict[str, Any]]:
        record = self._records.get((kind, record_id))
        return dict(record) if record is not None else None

    def delete(self, kind: str, record_id: str) -> bool:
        return self._records.pop((kind, record_id), None) is not None


class MemoryBlobStore:
    """Deterministic content-addressed BlobStore for tests."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def put_bytes(self, data: bytes) -> str:
        digest = sha256(data).hexdigest()
        self._blobs.setdefault(digest, bytes(data))
        return digest

    def get_bytes(self, digest: str) -> Optional[bytes]:
        blob = self._blobs.get(digest)
        return bytes(blob) if blob is not None else None
