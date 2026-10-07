"""Adversarial tests for the P05-G2 hostile file boundary."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.file_boundary import (
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
from gomrey.gateway import AdmissionError


def _budget(**limits) -> ResourceBudget:
    defaults = {
        "file_bytes": 1_000_000.0,
        "decompressed_bytes": 10_000_000.0,
        "archive_entries": 1000.0,
        "nesting_depth": 5.0,
        "page_count": 5000.0,
        "extracted_chars": 5_000_000.0,
    }
    defaults.update(limits)
    return ResourceBudget(limits=defaults)


def test_legit_files_pass_untouched() -> None:
    pdf = b"%PDF-1.7 legit body"
    report = file_admission_report(
        filename="report.pdf", data=pdf, declared_mime="application/pdf",
        budget=_budget(), page_count=3, extracted_chars=500,
    )
    assert report == {"safe_path": "root/report.pdf", "mime": "application/pdf", "bytes": len(pdf)}
    assert normalize_path("a/b/c.txt") == "root/a/b/c.txt"
    assert sniff_mime(b"\x89PNG\r\n\x1a\nrest") == "image/png"
    assert reconcile_mime("n.txt", b"hello world", "text/plain") == "text/plain"


def test_traversal_and_escape_fail_closed() -> None:
    for hostile in (
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\secrets\\k.txt",
        "a/../../b",
        "..",
        "",
        "evil\x00.pdf",
        "~/.ssh/id_rsa",
        ".symlink:/etc/passwd",
    ):
        with pytest.raises(AdmissionError):
            normalize_path(hostile)
    # Archive members obey the same containment.
    with pytest.raises(AdmissionError):
        check_archive_entry("../../evil.sh", entry_index=0)
    assert check_archive_entry("docs/ok.txt", entry_index=0) == "root/docs/ok.txt"


def test_extension_spoof_and_executable_refused() -> None:
    html_as_pdf = b"<html><body>not a pdf</body></html>"
    with pytest.raises(AdmissionError) as exc:
        reconcile_mime("evil.pdf", html_as_pdf, "application/pdf")
    assert exc.value.code == "unsafe_source"
    with pytest.raises(AdmissionError):
        reconcile_mime("run.pdf", b"MZ\x90\x00evil", "application/pdf")
    with pytest.raises(AdmissionError):
        reconcile_mime("pic.svg", b"<svg></svg>", "image/png")
    with pytest.raises(AdmissionError) as exc2:
        reconcile_mime("x.bin", b"data", "application/x-sh")
    assert exc2.value.code == "unsupported_source"


def test_active_content_denied_legit_text_allowed() -> None:
    assert scan_active_content(b"plain notes, nothing active") == []
    deny_active_content(b"plain notes, nothing active")
    for payload, _ in [
        (b"<script>alert(1)</script>", "script-element"),
        (b'<img src=x onerror="evil()">', "event-handler"),
        (b"<a href='javascript:evil()'>x</a>", "javascript-uri"),
        (b"<svg><foreignObject>x</foreignObject></svg>", "svg-foreign-object"),
        (b"<!ENTITY xxe SYSTEM 'file:///etc/passwd'>", "xxe-entity"),
    ]:
        assert scan_active_content(payload) != []
        with pytest.raises(AdmissionError) as exc:
            deny_active_content(payload)
        assert exc.value.code == "unsafe_source"


def test_budgets_exhaust_explicitly_never_silently() -> None:
    tiny = _budget(file_bytes=10.0)
    with pytest.raises(AdmissionError) as exc:
        enforce_file_budgets(budget=tiny, file_bytes=11)
    assert exc.value.code == "resource_limit_exceeded"
    bomb = _budget(decompressed_bytes=100.0, archive_entries=5.0)
    with pytest.raises(AdmissionError):
        enforce_file_budgets(budget=bomb, file_bytes=10, decompressed_bytes=10_000_000)
    with pytest.raises(AdmissionError):
        enforce_file_budgets(budget=bomb, file_bytes=10, archive_entries=6)
    with pytest.raises(AdmissionError):
        enforce_file_budgets(budget=_budget(), file_bytes=-1)
    # Oversized file fails at the composed boundary too.
    with pytest.raises(AdmissionError):
        file_admission_report(
            filename="big.pdf", data=b"%PDF-" + b"x" * 50,
            declared_mime="application/pdf", budget=_budget(file_bytes=10.0),
        )


def test_temp_lease_lifecycle() -> None:
    registry = TempLeaseRegistry()
    lease = registry.issue("tok-1", "src-1")
    assert lease.released is False
    assert registry.outstanding() == 1
    with pytest.raises(AdmissionError):
        registry.issue("tok-1", "src-2")
    registry.release("tok-1")
    assert registry.outstanding() == 0
    with pytest.raises(AdmissionError):
        registry.release("tok-1")
