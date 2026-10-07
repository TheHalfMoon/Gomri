"""Structured worker envelope and baseline qualification (P06-G2).

Pure deterministic logic with no subprocess, no models, and no network.
This grain binds the two structured paths named by the donor ledger
without vendoring weights or touching the lockfile:

- worker envelope: every structured-worker invocation is admitted
  through an explicit record (worker identity, input digest, capability
  grants defaulting to nothing, timeout, cancellation). The envelope
  authorizes execution; the worker process itself stays outside this
  module, behind the P05 parser boundary;
- LiteParse baseline: the imported Presenton path is recorded as the
  frozen comparator with a stable identity, so any challenger must beat
  a named incumbent rather than a moving target;
- structured mapping: Docling-shaped output (pages, sections, tables,
  figures with provenance) maps to ParserIntermediate through a pure
  function tested with synthetic fixtures — no model required to prove
  the mapping preserves structure and provenance;
- qualification gates: the Docling DEPEND/WORKER adoption states its
  license, resource envelope, and acceptance bars as data, and
  `check_qualification` decides by measurement only.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
from typing import Any

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError
from gomrey.parser_boundary import ParserIntermediate
from gomrey.parser_router import BenchmarkScore

LITEPARSE_BASELINE = {
    "worker_id": "liteparse-baseline",
    "parser_id": "liteparse",
    "role": "baseline-comparator",
    "service_module": "services.liteparse_service",
    "source_ledger_anchor": "docling-project/docling planning anchor eda5b5fc86d10b2b79a900ff3e69fc159d5f6014",
}

KNOWN_WORKERS = frozenset({
    "liteparse-baseline",
    "docling-default",
    "ocr-visual-worker",
    "fallback-second-parser",
})

DOCLING_ADOPTION = {
    "donor": "docling-project/docling",
    "mode": "DEPEND / WORKER with COPY_BOUNDED adapters",
    "license_observed": "permissive-open-source (verify exact LICENSE blob at DEPEND time)",
    "role": "default structured path challenger; default status only by benchmark",
    "forbidden": "no model weights vendored; no lockfile change in this grain",
}

DOCLING_QUALIFICATION_BARS = {
    "min_coverage": 1.0,
    "max_conflicts": 0,
    "max_uncertain": 1,
    "max_seconds_per_page": 30.0,
    "max_mb_per_page": 512.0,
}


@dataclass(frozen=True)
class WorkerEnvelope:
    """Admission-to-execution: what a worker may touch, for how long."""

    worker_id: str
    parser_id: str
    input_digest: str
    timeout_seconds: float = 300.0
    network: bool = False
    secrets: bool = False
    cancelled: bool = False


@dataclass(frozen=True)
class WorkerAuthorization:
    worker_id: str
    input_digest: str
    capabilities: dict[str, bool]


def admit_worker(envelope: WorkerEnvelope, budget: ResourceBudget) -> WorkerAuthorization:
    """Authorize one worker invocation, or fail closed with a typed error."""
    if envelope.worker_id not in KNOWN_WORKERS:
        raise AdmissionError("unsupported_source", f"unknown worker: {envelope.worker_id}")
    if envelope.cancelled:
        raise AdmissionError("parser_failure", "worker invocation cancelled")
    if envelope.timeout_seconds <= 0:
        raise AdmissionError("malformed_source", "non-positive worker timeout")
    if len(envelope.input_digest) != 64:
        raise AdmissionError("malformed_source", "invalid input digest")
    if envelope.network or envelope.secrets:
        raise AdmissionError("unsafe_source", "workers hold no network or secret authority")
    try:
        budget.spend("worker_invocations", 1.0)
        budget.spend("worker_timeout_seconds", float(envelope.timeout_seconds))
    except BudgetExhausted as exc:
        raise AdmissionError(
            "resource_limit_exceeded",
            f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
        ) from exc
    return WorkerAuthorization(
        worker_id=envelope.worker_id,
        input_digest=envelope.input_digest,
        capabilities={"network": False, "secrets": False, "quarantine_read": True},
    )


def map_structured_output(
    *,
    worker_id: str,
    input_digest: str,
    document: dict[str, Any],
) -> ParserIntermediate:
    """Map Docling-shaped structure to ParserIntermediate, preserving provenance.

    Expected shape (synthetic in tests, Docling-faithful in workers):
    {"pages": [{"page_no": int, "sections": [{"heading": str, "text": str,
    "tables": [[...]], "figures": [{"caption": str}]}]}]}.
    """
    if worker_id not in KNOWN_WORKERS:
        raise AdmissionError("unsupported_source", f"unknown worker: {worker_id}")
    pages = document.get("pages")
    if not isinstance(pages, list) or not pages:
        raise AdmissionError("normalization_failure", "structured output has no pages")
    units: list[dict[str, Any]] = []
    warnings: list[str] = []
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("page_no"), int):
            raise AdmissionError("normalization_failure", "page without page_no")
        page_no = page["page_no"]
        sections = page.get("sections", [])
        if not isinstance(sections, list) or not sections:
            warnings.append(f"page-{page_no}-no-sections")
            continue
        for index, section in enumerate(sections):
            if not isinstance(section, dict) or not isinstance(section.get("text"), str):
                raise AdmissionError("normalization_failure", f"page {page_no} section without text")
            unit_id = f"p{page_no}-s{index}"
            units.append({
                "unit_id": unit_id,
                "kind": "page",
                "text": section["text"],
                "heading": str(section.get("heading", "")),
                "tables": section.get("tables", []),
                "figures": section.get("figures", []),
                "page_no": page_no,
            })
    if not units:
        raise AdmissionError("normalization_failure", "structured output yielded no units")
    return ParserIntermediate(
        source_id=document.get("source_id", ""),
        parser_id=worker_id,
        input_digest=input_digest,
        units=units,
        warnings=warnings,
    )


@dataclass
class QualificationProfile:
    seconds_per_page: float
    mb_per_page: float
    license_ok: bool = True
    resource_ok: bool = True


def check_qualification(
    score: BenchmarkScore,
    profile: QualificationProfile,
) -> dict[str, Any]:
    """Decide Docling default status by measurement against frozen bars."""
    bars = DOCLING_QUALIFICATION_BARS
    reasons: list[str] = []
    if score.coverage < bars["min_coverage"]:
        reasons.append("coverage-below-bar")
    if score.conflicts > bars["max_conflicts"]:
        reasons.append("conflicts-above-bar")
    if score.uncertain > bars["max_uncertain"]:
        reasons.append("uncertain-above-bar")
    if profile.seconds_per_page > bars["max_seconds_per_page"]:
        reasons.append("too-slow-per-page")
    if profile.mb_per_page > bars["max_mb_per_page"]:
        reasons.append("too-heavy-per-page")
    if not profile.license_ok:
        reasons.append("license-unverified")
    if not profile.resource_ok:
        reasons.append("resource-gate-failed")
    qualified = not reasons and score.beats_baseline
    if score.beats_baseline and reasons:
        reasons.append("beats-baseline-but-bars-unmet")
    return {"qualified": qualified, "reasons": reasons}
