"""Deterministic tests for the CanonicalStore/BlobStore seams (P03-G2)."""

from gomrey.seams import (
    CanonicalStore,
    BlobStore,
    MemoryBlobStore,
    MemoryCanonicalStore,
)


def test_memory_canonical_store_round_trip() -> None:
    store: CanonicalStore = MemoryCanonicalStore()
    assert store.get("artifact", "a-1") is None
    store.put("artifact", "a-1", {"artifact_id": "a-1", "revision": 1})
    assert store.get("artifact", "a-1") == {"artifact_id": "a-1", "revision": 1}
    assert store.delete("artifact", "a-1") is True
    assert store.get("artifact", "a-1") is None
    assert store.delete("artifact", "a-1") is False


def test_memory_canonical_store_returns_copies() -> None:
    store = MemoryCanonicalStore()
    store.put("job", "j-1", {"status": "running"})
    record = store.get("job", "j-1")
    assert record is not None
    record["status"] = "mutated"
    assert store.get("job", "j-1") == {"status": "running"}


def test_memory_blob_store_is_content_addressed() -> None:
    store: BlobStore = MemoryBlobStore()
    digest = store.put_bytes(b"hello gomrey")
    assert store.put_bytes(b"hello gomrey") == digest
    assert store.get_bytes(digest) == b"hello gomrey"
    assert store.get_bytes("0" * 64) is None


def test_memory_blob_store_is_immutable() -> None:
    store = MemoryBlobStore()
    digest = store.put_bytes(b"bytes")
    blob = store.get_bytes(digest)
    assert blob is not None
    assert bytes(blob) == b"bytes"
