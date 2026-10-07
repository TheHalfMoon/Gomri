"""Adversarial tests for the P05-G3 remote source gateway (no network)."""

import pytest

from gomrey.budgets import ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.remote_gateway import (
    authorize_fetch,
    classify_url,
    enforce_remote_budgets,
    normalized_fetch_result,
    validate_redirect_chain,
)


def _budget(**limits) -> ResourceBudget:
    defaults = {"remote_response_bytes": 5_000_000.0, "redirects": 5.0}
    defaults.update(limits)
    return ResourceBudget(limits=defaults)


def test_valid_https_passes_with_taint() -> None:
    verdict = classify_url("https://example.com/research/paper")
    # Hostnames always need DNS pinning: literal allow is for public IPs only.
    assert verdict.verdict == "resolution_required"
    authorized = authorize_fetch(verdict, ["93.184.216.34"])
    assert authorized == "https://example.com/research/paper"
    literal = classify_url("https://93.184.216.34/paper")
    assert literal.verdict == "allow"
    assert authorize_fetch(literal, []) == "https://93.184.216.34/paper"
    result = normalized_fetch_result(
        canonical_url=authorized, content_digest="b" * 64,
        mime="text/html", response_bytes=1024,
    )
    assert result["untrusted_origin"] is True
    assert result["treat_as"] == "data-not-instructions"


def test_ssrf_literal_ips_denied() -> None:
    for hostile in (
        "http://localhost/admin",
        "https://localhost/admin",
        "https://127.0.0.1/",
        "https://127.1.2.3/",
        "https://10.0.0.5/",
        "https://172.16.9.9/",
        "https://172.31.255.1/",
        "https://192.168.1.1/",
        "https://169.254.169.254/latest/meta-data/",
        "https://169.254.10.20/",
        "https://0.0.0.0/",
        "https://[::1]/",
        "https://[::ffff:127.0.0.1]/",
        "https://[fc00::1]/",
        "https://[fe80::1]/",
    ):
        with pytest.raises(AdmissionError):
            classify_url(hostile, require_https=False)


def test_internal_names_and_schemes_denied() -> None:
    for hostile in (
        "https://intranet/",
        "https://db.internal/",
        "https://printer.local/",
        "https://metadata.google.internal/",
        "ftp://example.com/x",
        "file:///etc/passwd",
        "data:text/plain,hi",
        "javascript:alert(1)",
    ):
        with pytest.raises(AdmissionError):
            classify_url(hostile)
    with pytest.raises(AdmissionError):
        classify_url("https://user:pass@example.com/")


def test_https_required_by_default_with_explicit_opt_in() -> None:
    with pytest.raises(AdmissionError) as exc:
        classify_url("http://example.com/page")
    assert exc.value.code == "remote_fetch_denied"
    verdict = classify_url("http://example.com/page", require_https=False)
    assert verdict.verdict == "resolution_required"


def test_dns_rebinding_fails_closed_at_pin_time() -> None:
    verdict = classify_url("https://example.com/data")
    with pytest.raises(AdmissionError):
        authorize_fetch(verdict, [])
    with pytest.raises(AdmissionError):
        authorize_fetch(verdict, ["93.184.216.34", "127.0.0.1"])
    with pytest.raises(AdmissionError):
        authorize_fetch(verdict, ["10.1.2.3"])
    with pytest.raises(AdmissionError):
        authorize_fetch(verdict, ["not-an-ip"])


def test_redirect_chain_bounded_and_safe() -> None:
    final = validate_redirect_chain(
        ["https://93.184.216.34/a", "https://93.184.216.34/b"],
        budget=_budget(),
    )
    assert final == "https://93.184.216.34/b"
    with pytest.raises(AdmissionError):
        validate_redirect_chain(["https://93.184.216.34/a"] * 8)
    # Redirect to a private target is denied.
    with pytest.raises(AdmissionError):
        validate_redirect_chain(["https://93.184.216.34/a", "https://10.0.0.1/b"])
    # https downgrade refused.
    with pytest.raises(AdmissionError):
        validate_redirect_chain(["https://93.184.216.34/a", "http://93.184.216.34/b"])
    # Hostname hops need pinning before the chain is trusted.
    with pytest.raises(AdmissionError):
        validate_redirect_chain(["https://example.com/a", "https://example.com/b"])
    # Redirect budget exhaustion is explicit.
    with pytest.raises(AdmissionError) as exc:
        validate_redirect_chain(
            ["https://93.184.216.34/a", "https://93.184.216.34/b"],
            budget=_budget(redirects=0.0),
        )
    assert exc.value.code == "resource_limit_exceeded"


def test_remote_response_budget_and_result_validation() -> None:
    enforce_remote_budgets(budget=_budget(), response_bytes=100)
    with pytest.raises(AdmissionError) as exc:
        enforce_remote_budgets(budget=_budget(remote_response_bytes=10.0), response_bytes=11)
    assert exc.value.code == "resource_limit_exceeded"
    with pytest.raises(AdmissionError):
        normalized_fetch_result(
            canonical_url="https://example.com/", content_digest="zzz",
            mime="text/html", response_bytes=1,
        )
