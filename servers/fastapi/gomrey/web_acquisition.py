"""Bounded web acquisition contracts (P07-G1).

Pure deterministic logic with no fetching, no rendering, and no network,
layered on the P05 remote gateway: a crawl plan is an explicit,
budgeted, auditable permission to visit a bounded set of pages — never
an open-ended license to follow the web.

- scope: seed URL plus an explicit expansion set (allowed domains,
  subdomain rule, sitemap URLs). Same-origin is the default; anything
  else must be named. Out-of-scope URLs are denied, never followed;
- bounds: depth and page caps spend from the shared ResourceBudget, so
  a page can never silently expand into an unbounded crawl;
- snapshots: every admitted page yields a retrieval record (canonical
  URL, digest, MIME, size, retrieval timestamp marker, taint) that later
  pipeline stages consume instead of re-deriving provenance;
- robots/terms: acquisition decisions are recorded data. Fetch is
  allowed unless robots disallow (flagged when unknown, since robots.txt
  is voluntary); redistribution is denied unless source terms allow it.
  Neither decision is silent.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
from urllib.parse import urlsplit

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.remote_gateway import UrlVerdict, authorize_fetch, classify_url


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme.lower()}://{(parts.hostname or '').lower()}"


@dataclass(frozen=True)
class CrawlScope:
    seed_url: str
    allowed_domains: tuple[str, ...] = ()
    allow_subdomains: bool = False
    sitemap_urls: tuple[str, ...] = ()
    max_depth: int = 2
    max_pages: int = 50
    respect_robots: bool = True


@dataclass
class CrawlPlan:
    scope: CrawlScope
    seed_verdict: UrlVerdict
    visited: list[str] = field(default_factory=list)

    def status(self) -> dict[str, object]:
        return {
            "seed": self.scope.seed_url,
            "pages_visited": len(self.visited),
            "pages_remaining": max(0, self.scope.max_pages - len(self.visited)),
        }


def plan_crawl(scope: CrawlScope) -> CrawlPlan:
    """Validate a crawl scope without visiting anything."""
    if scope.max_depth < 0 or scope.max_pages <= 0:
        raise AdmissionError("malformed_source", "crawl bounds must be positive")
    if scope.max_depth > 5 or scope.max_pages > 10000:
        raise AdmissionError("resource_limit_exceeded", "crawl bounds exceed planner caps")
    verdict = classify_url(scope.seed_url)
    # Both "allow" (literal public IP) and "resolution_required" (hostname)
    # seeds are plannable; the fetcher must still pin DNS before visiting.
    for domain in scope.allowed_domains:
        if not domain or "." not in domain or " " in domain or "/" in domain:
            raise AdmissionError("malformed_source", f"bad allowed domain: {domain}")
    for sitemap in scope.sitemap_urls:
        sitemap_verdict = classify_url(sitemap)
        if sitemap_verdict.verdict != "allow":
            raise AdmissionError("remote_fetch_denied", "sitemap requires DNS pinning first")
    return CrawlPlan(scope=scope, seed_verdict=verdict)


def _domain_allowed(host: str, scope: CrawlScope, seed_host: str) -> bool:
    lowered = host.lower()
    if lowered == seed_host:
        return True
    for domain in scope.allowed_domains:
        candidate = domain.lower()
        if lowered == candidate:
            return True
        if scope.allow_subdomains and lowered.endswith("." + candidate):
            return True
    return False


def admit_child(
    plan: CrawlPlan,
    parent_url: str,
    child_url: str,
    depth: int,
    budget: ResourceBudget,
    resolved_ips: list[str] | None = None,
) -> str:
    """Admit one child page under the plan, or fail closed with a reason."""
    if depth < 0 or depth > plan.scope.max_depth:
        raise AdmissionError("resource_limit_exceeded", "crawl depth exceeded")
    verdict = classify_url(child_url)
    host = (urlsplit(child_url).hostname or "")
    seed_host = (urlsplit(plan.scope.seed_url).hostname or "").lower()
    if not _domain_allowed(host, plan.scope, seed_host):
        raise AdmissionError("remote_fetch_denied", "out-of-scope URL never followed")
    if verdict.verdict == "resolution_required":
        if not resolved_ips:
            raise AdmissionError("remote_fetch_denied", "child requires DNS pinning first")
        authorize_fetch(verdict, resolved_ips)
    if verdict.canonical_url in plan.visited:
        # Revisits are idempotent: no double spend, no double count.
        return verdict.canonical_url
    if len(plan.visited) >= plan.scope.max_pages:
        raise AdmissionError("resource_limit_exceeded", "crawl page cap reached")
    try:
        budget.spend("crawl_pages", 1.0)
    except BudgetExhausted as exc:
        raise AdmissionError(
            "resource_limit_exceeded",
            f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
        ) from exc
    plan.visited.append(verdict.canonical_url)
    return verdict.canonical_url


def page_snapshot(
    *,
    canonical_url: str,
    content_digest: str,
    mime: str,
    response_bytes: int,
    retrieved_at: str,
) -> dict[str, object]:
    """Build the per-page retrieval record later stages consume as truth."""
    if len(content_digest) != 64:
        raise AdmissionError("malformed_source", "invalid content digest")
    if not retrieved_at:
        raise AdmissionError("malformed_source", "retrieval timestamp required")
    return {
        "canonical_url": canonical_url,
        "origin": _origin(canonical_url),
        "content_digest": content_digest,
        "mime": mime,
        "response_bytes": response_bytes,
        "retrieved_at": retrieved_at,
        "untrusted_origin": True,
        "treat_as": "data-not-instructions",
    }


def acquisition_policy(
    *,
    robots_allowed: bool | None,
    terms_redistribution_allowed: bool,
) -> dict[str, object]:
    """Record the robots/terms decision explicitly; nothing is silent."""
    reasons: list[str] = []
    fetch = True
    if robots_allowed is False:
        fetch = False
        reasons.append("robots-disallow")
    elif robots_allowed is None:
        reasons.append("robots-unknown-flagged")
    redistribute = bool(terms_redistribution_allowed)
    if not redistribute:
        reasons.append("redistribution-denied-by-default")
    return {
        "fetch_permitted": fetch,
        "redistribution_permitted": redistribute,
        "reasons": reasons,
    }
