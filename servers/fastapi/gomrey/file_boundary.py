"""Hostile file boundary: paths, MIME truth, budgets, archives (P05-G2).

Pure deterministic logic with no filesystem writes and no network, layered
on P05-G1 admission and the P04 ResourceBudget:

- paths: user-selected names are normalized and contained inside an
  explicit root; traversal, absolute escape, drive prefixes, null bytes,
  and unsafe-symlink markers are denied, never sanitized into access;
- MIME truth: the declared type must reconcile with sniffed magic bytes;
  extension spoofing (e.g. a script named ``.pdf``) fails closed;
- budgets: file size, decompressed size, archive entry count, nesting
  depth, page count, and extracted characters spend from a shared
  ResourceBudget, so hostile inputs surface as explicit exhaustion, not
  silent truncation or resource collapse;
- archives: entry paths obey the same containment rule; entry-count and
  depth caps bound decompression-bomb shapes before any worker expands
  them;
- active content: script, hostile HTML/SVG, XXE entity declarations, and
  executable headers are reported as findings and denied by default.

Failures raise the shared AdmissionError taxonomy from gateway.py so the
whole gateway speaks one error language.
"""

from dataclasses import dataclass, field
import posixpath
import re
from typing import Any

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError

ALLOWED_MIME = frozenset({
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/html",
    "text/csv",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/tiff",
    "image/bmp",
    "image/webp",
    "application/zip",
    "application/gzip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
})

EXTENSION_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
    ".csv": "text/csv",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".zip": "application/zip",
    ".gz": "application/gzip",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

_MAGIC: list[tuple[bytes, str]] = [
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"II*\x00", "image/tiff"),
    (b"MM\x00*", "image/tiff"),
    (b"BM", "image/bmp"),
    (b"PK\x03\x04", "application/zip"),
    (b"\x1f\x8b", "application/gzip"),
    (b"MZ", "application/x-dos-executable"),
]

_SCRIPT_PATTERNS: list[tuple[str, str]] = [
    ("script-element", r"<\s*script[\s>]"),
    ("event-handler", r"on(?:click|load|error|mouseover|focus|submit)\s*="),
    ("javascript-uri", r"javascript\s*:"),
    ("svg-foreign-object", r"<\s*foreignobject[\s>]"),
    ("svg-script-href", r"<\s*(?:animate|set)[\s>][^>]*href\s*="),
    ("xxe-entity", r"<!entity[\s>]"),
    ("server-side-code", r"<\?(?:php|=)"),
    ("html-import", r"<\s*link[^>]*rel\s*=\s*[\"']import[\"']"),
]

_UNSAFE_NAME_RE = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)")


@dataclass
class TempLease:
    """Opaque temp-file lifecycle token: issue, track, release, verify."""

    token: str
    source_id: str
    released: bool = False


@dataclass
class TempLeaseRegistry:
    """In-memory temp lifecycle for tests and future worker adapters."""

    _active: dict[str, str] = field(default_factory=dict)

    def issue(self, token: str, source_id: str) -> TempLease:
        if token in self._active:
            raise AdmissionError("malformed_source", "temp token already issued")
        self._active[token] = source_id
        return TempLease(token=token, source_id=source_id)

    def release(self, token: str) -> None:
        if token not in self._active:
            raise AdmissionError("malformed_source", "unknown temp token")
        del self._active[token]

    def outstanding(self) -> int:
        return len(self._active)


def normalize_path(user_path: str) -> str:
    """Contain a user-selected name inside the staging root.

    Returns the canonical ``root/<name>`` path. Denies traversal,
    absolute escape, drive prefixes, null bytes, and symlink-escape
    markers instead of rewriting them into something reachable.
    """
    if not isinstance(user_path, str) or not user_path or "\x00" in user_path:
        raise AdmissionError("malformed_source", "invalid source path")
    candidate = user_path.replace("\\", "/").strip()
    if (
        not candidate
        or candidate.startswith("/")
        or _UNSAFE_NAME_RE.search(candidate)
        or re.match(r"^[A-Za-z]:", candidate)
        or candidate.startswith("~")
    ):
        raise AdmissionError("unsafe_source", "path escapes the staging root")
    normalized = posixpath.normpath(candidate)
    if normalized in {".", ".."} or normalized.startswith("../") or normalized.startswith("/"):
        raise AdmissionError("unsafe_source", "path escapes the staging root")
    for part in normalized.split("/"):
        if not part or part in {".", ".."}:
            raise AdmissionError("unsafe_source", "path escapes the staging root")
        if part.startswith(".symlink:"):
            raise AdmissionError("unsafe_source", "unsafe symlink marker refused")
    return "root/" + normalized


def sniff_mime(data: bytes) -> str | None:
    """Identify bytes by magic header; text and images sniffed structurally."""
    for magic, mime in _MAGIC:
        if data.startswith(magic):
            return mime
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return "image/webp"
    if b"\x00" not in data:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        stripped = data.lstrip()[:2048].lower()
        if stripped.startswith((b"<html", b"<!doctype html", b"<svg")):
            return "text/html" if b"<svg" not in stripped[:5] else "image/svg+xml"
        return "text/plain"
    return None


def reconcile_mime(filename: str, data: bytes, declared_mime: str) -> str:
    """Require filename, magic bytes, and declaration to agree.

    Returns the canonical MIME. Extension spoofing and magic mismatches
    fail closed; SVG is unsupported at this boundary (served only through
    the G4 sanitizer path later).
    """
    if declared_mime not in ALLOWED_MIME:
        raise AdmissionError("unsupported_source", f"unsupported MIME: {declared_mime}")
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    expected = EXTENSION_MIME.get(ext)
    if expected is not None and expected != declared_mime:
        raise AdmissionError("unsafe_source", "extension/MIME mismatch (spoofing)")
    sniffed = sniff_mime(data)
    if sniffed == "application/x-dos-executable":
        raise AdmissionError("unsafe_source", "executable payload refused")
    if sniffed == "image/svg+xml":
        raise AdmissionError("unsafe_source", "SVG requires the sanitizer path")
    if sniffed is not None:
        if declared_mime in {"text/plain", "text/markdown", "text/csv"} and sniffed == "text/plain":
            return declared_mime
        if sniffed != declared_mime:
            raise AdmissionError("unsafe_source", "content/MIME mismatch (spoofing)")
    return declared_mime


def enforce_file_budgets(
    *,
    budget: ResourceBudget,
    file_bytes: int,
    decompressed_bytes: int = 0,
    archive_entries: int = 0,
    nesting_depth: int = 0,
    page_count: int = 0,
    extracted_chars: int = 0,
) -> None:
    """Spend hostile-input dimensions from one shared budget.

    Raises AdmissionError(resource_limit_exceeded) on exhaustion so the
    caller reports an explicit partial/blocked state, never silent loss.
    """
    spends = {
        "file_bytes": file_bytes,
        "decompressed_bytes": decompressed_bytes,
        "archive_entries": archive_entries,
        "nesting_depth": nesting_depth,
        "page_count": page_count,
        "extracted_chars": extracted_chars,
    }
    for resource, amount in spends.items():
        if amount < 0:
            raise AdmissionError("malformed_source", f"negative {resource}")
        try:
            budget.spend(resource, float(amount))
        except BudgetExhausted as exc:
            raise AdmissionError(
                "resource_limit_exceeded",
                f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
            ) from exc


def check_archive_entry(entry_path: str, *, entry_index: int) -> str:
    """Validate one archive member path before any worker expands it."""
    if entry_index < 0:
        raise AdmissionError("malformed_source", "negative archive entry index")
    return normalize_path(entry_path)


def scan_active_content(data: bytes) -> list[str]:
    """Report script/hostile-markup/executable signals in decoded content."""
    try:
        text = data[:65536].decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return []
    lowered = text.lower()
    return [name for name, pattern in _SCRIPT_PATTERNS if re.search(pattern, lowered)]


def deny_active_content(data: bytes) -> None:
    """Fail closed when active content is present; pass silently otherwise."""
    findings = scan_active_content(data)
    if findings:
        raise AdmissionError(
            "unsafe_source",
            f"active content refused: {','.join(sorted(findings))}",
        )


def file_admission_report(
    *,
    filename: str,
    data: bytes,
    declared_mime: str,
    budget: ResourceBudget,
    page_count: int = 0,
    extracted_chars: int = 0,
) -> dict[str, Any]:
    """One composed boundary: path, MIME, active content, budgets.

    Returns the safe-handle record on success; raises AdmissionError
    otherwise. Legitimate files pass untouched.
    """
    safe_path = normalize_path(filename)
    mime = reconcile_mime(filename, data, declared_mime)
    deny_active_content(data)
    enforce_file_budgets(
        budget=budget,
        file_bytes=len(data),
        page_count=page_count,
        extracted_chars=extracted_chars,
    )
    return {"safe_path": safe_path, "mime": mime, "bytes": len(data)}
