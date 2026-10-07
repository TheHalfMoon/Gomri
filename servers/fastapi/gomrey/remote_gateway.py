"""Remote source gateway: URL policy, SSRF denial, redirects (P05-G3).

Pure deterministic logic with no network access. This module never fetches;
it decides what a future fetcher worker is allowed to fetch, so the
gateway cannot become an SSRF primitive:

- scheme allowlist: https by default, http only with an explicit opt-in;
  file/ftp/data/javascript and friends are never fetchable;
- credential-bearing URLs (userinfo) are denied outright;
- literal-IP targets inside loopback, RFC1918, link-local (including the
  cloud metadata address), unique-local, or unspecified ranges are
  denied; IPv4-mapped IPv6 is unwrapped before the check;
- hostnames that are not literal IPs cannot be cleared offline, so they
  return ``resolution_required``: the fetcher must resolve, pin the
  answer, and pass it to ``authorize_fetch``, which re-checks every
  resolved IP. DNS rebinding therefore fails closed at connect time;
- obviously-internal names (localhost, single labels, .internal/.local,
  metadata hostnames) are denied without resolution;
- redirects are bounded, cannot land on a denied target, and cannot
  downgrade https to http;
- remote response size and redirect count spend from the shared
  ResourceBudget;
- the normalized fetch contract carries ``untrusted_origin`` taint from
  birth so downstream stages never mistake remote bytes for instructions.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass
import ipaddress
from typing import Any
from urllib.parse import urlsplit

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError

ALLOWED_SCHEMES = frozenset({"https", "http"})
MAX_REDIRECTS = 5

_BLOCKED_NAMES = frozenset({
    "localhost",
    "metadata.google.internal",
    "instance-data",
    "instance-data-compute",
})

_BLOCKED_SUFFIXES = (".internal", ".local", ".localhost", ".invalid")


@dataclass(frozen=True)
class UrlVerdict:
    canonical_url: str
    host: str
    verdict: str  # "allow" or "resolution_required"


def _is_blocked_ip(addr: ipaddress._BaseAddress) -> bool:
    unwrapped: ipaddress._BaseAddress = addr
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        unwrapped = addr.ipv4_mapped
    return (
        unwrapped.is_loopback
        or unwrapped.is_private
        or unwrapped.is_link_local
        or unwrapped.is_reserved
        or unwrapped.is_multicast
        or unwrapped.is_unspecified
    )


def _deny(detail: str) -> AdmissionError:
    return AdmissionError("remote_fetch_denied", detail)


def _check_name(host: str) -> None:
    lowered = host.lower().rstrip(".")
    if lowered in _BLOCKED_NAMES or lowered in {"localhost"}:
        raise _deny("loopback/internal hostname refused")
    if lowered.endswith(_BLOCKED_SUFFIXES):
        raise _deny("internal network suffix refused")
    if "/" in host or " " in host or not host:
        raise AdmissionError("malformed_source", "invalid URL host")
    if "." not in lowered and ":" not in host:
        # Single-label names resolve via local search domains: internal by
        # definition. Literal IPv6 contains ':' and is handled as an IP.
        raise _deny("single-label hostname refused")


def classify_url(raw_url: str, *, require_https: bool = True) -> UrlVerdict:
    """Judge one URL without touching the network.

    Returns ``allow`` for literal-IP public targets and
    ``resolution_required`` for hostnames the fetcher must resolve and pin.
    Raises AdmissionError on anything unsafe or malformed.
    """
    if not isinstance(raw_url, str) or not raw_url or len(raw_url) > 2048:
        raise AdmissionError("malformed_source", "invalid URL")
    if any(ch.isspace() for ch in raw_url):
        raise AdmissionError("malformed_source", "URL contains whitespace")
    try:
        parts = urlsplit(raw_url)
    except ValueError as exc:
        raise AdmissionError("malformed_source", f"URL does not parse: {exc}") from exc
    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise AdmissionError("unsupported_source", f"URL scheme not fetchable: {parts.scheme or '(none)'}")
    if require_https and parts.scheme.lower() == "http":
        raise _deny("cleartext http requires an explicit opt-in")
    if parts.username is not None or parts.password is not None:
        raise _deny("credential-bearing URL refused")
    host = (parts.hostname or "").strip()
    if not host:
        raise AdmissionError("malformed_source", "URL has no host")
    try:
        addr = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        _check_name(host)
        return UrlVerdict(canonical_url=raw_url, host=host, verdict="resolution_required")
    if _is_blocked_ip(addr):
        raise _deny("private/loopback/link-local target refused")
    return UrlVerdict(canonical_url=raw_url, host=host, verdict="allow")


def authorize_fetch(
    verdict: UrlVerdict,
    resolved_ips: list[str],
    *,
    require_https: bool = True,
) -> str:
    """Pin DNS answers before connect: every resolved IP is re-checked.

    The fetcher resolves ``verdict.host``, pins the answer set, and calls
    here. Any blocked address in the set denies the whole fetch, which is
    what makes DNS rebinding fail closed. Literal-IP ``allow`` verdicts
    authorize with an empty list.
    """
    if verdict.verdict == "allow":
        if resolved_ips:
            raise AdmissionError("malformed_source", "literal-IP verdict takes no resolved IPs")
        return verdict.canonical_url
    if not resolved_ips:
        raise _deny("hostname fetch requires pinned DNS answers")
    for raw in resolved_ips:
        try:
            addr = ipaddress.ip_address(raw.strip("[]"))
        except ValueError as exc:
            raise AdmissionError("malformed_source", f"unparsable resolved IP: {raw}") from exc
        if _is_blocked_ip(addr):
            raise _deny("resolved address is private/loopback/link-local")
    if require_https and verdict.canonical_url.lower().startswith("http://"):
        raise _deny("cleartext http requires an explicit opt-in")
    return verdict.canonical_url


def validate_redirect_chain(
    urls: list[str],
    *,
    require_https: bool = True,
    budget: ResourceBudget | None = None,
) -> str:
    """Validate a redirect chain hop by hop; return the final canonical URL."""
    if not urls:
        raise AdmissionError("malformed_source", "empty redirect chain")
    if len(urls) - 1 > MAX_REDIRECTS:
        raise AdmissionError("resource_limit_exceeded", "too many redirects")
    if budget is not None:
        try:
            budget.spend("redirects", float(len(urls) - 1))
        except BudgetExhausted as exc:
            raise AdmissionError(
                "resource_limit_exceeded",
                f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
            ) from exc
    first_https = urls[0].lower().startswith("https://")
    final = urls[0]
    for hop in urls:
        verdict = classify_url(hop, require_https=require_https)
        if verdict.verdict != "allow":
            raise _deny("redirect target requires DNS pinning first")
        final = verdict.canonical_url
    if first_https and final.lower().startswith("http://"):
        raise _deny("https downgrade refused")
    return final


def enforce_remote_budgets(*, budget: ResourceBudget, response_bytes: int) -> None:
    """Bound a remote response before it enters quarantine storage."""
    if response_bytes < 0:
        raise AdmissionError("malformed_source", "negative response size")
    try:
        budget.spend("remote_response_bytes", float(response_bytes))
    except BudgetExhausted as exc:
        raise AdmissionError(
            "resource_limit_exceeded",
            f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
        ) from exc


def normalized_fetch_result(
    *,
    canonical_url: str,
    content_digest: str,
    mime: str,
    response_bytes: int,
) -> dict[str, Any]:
    """Build the fetch contract: provenance and taint travel with the bytes."""
    if len(content_digest) != 64 or any(c not in "0123456789abcdef" for c in content_digest):
        raise AdmissionError("malformed_source", "invalid content digest")
    return {
        "canonical_url": canonical_url,
        "content_digest": content_digest,
        "mime": mime,
        "response_bytes": response_bytes,
        "untrusted_origin": True,
        "treat_as": "data-not-instructions",
    }
