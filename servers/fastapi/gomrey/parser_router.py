"""Parser router and ensemble contracts (P06-G1).

Pure deterministic logic with no models, no weights, and no network,
sitting between the P05 quarantine boundary and the format workers:

- preflight: cheap byte-level signals (native-text likelihood,
  image-dominance, structural markers) that route work but never assert
  quality;
- classification: page signals map to workload classes (native, scanned,
  mixed, table-heavy, visual) through explicit rules, not confidence;
- routing: the default structured path with bounded second-parser
  triggers for disagreement-prone and high-risk regions;
- disagreement: two parser outputs reconcile through explicit rules —
  agreement, conflict-marked union, or declared uncertainty. Outputs are
  never silently averaged, and unknown never upgrades to known;
- reconciliation: parser units become Source IR shapes carrying both
  parser identities and provenance, with every declared unit accounted;
- benchmark harness: frozen cases with recorded expectations score runs
  deterministically, so a challenger becomes default only by measured
  superiority over the LiteParse baseline.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
import re
from typing import Any

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError, select_parser

WORKLOAD_CLASSES = frozenset({
    "native_text",
    "scanned",
    "mixed",
    "table_heavy",
    "formula_chart",
    "visual_only",
    "unknown",
})

ENSEMBLE_VERDICTS = frozenset({"agree", "conflict", "uncertain"})


@dataclass(frozen=True)
class Preflight:
    mime: str
    byte_size: int
    signals: tuple[str, ...]


@dataclass(frozen=True)
class Route:
    workload: str
    primary_parser: str
    second_parser: str | None
    reason: str


@dataclass(frozen=True)
class Reconciliation:
    verdict: str
    units: tuple[dict[str, Any], ...]
    conflicts: tuple[str, ...]
    uncertain_unit_ids: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkScore:
    case_id: str
    coverage: float
    conflicts: int
    uncertain: int
    beats_baseline: bool


def preflight(data: bytes, mime: str) -> Preflight:
    """Cheap deterministic signals for routing; signals are hints, not truth."""
    if not data:
        raise AdmissionError("malformed_source", "empty parser input")
    signals: list[str] = []
    head = data[:65536]
    text_runs = len(re.findall(rb"[A-Za-z]{3,}", head))
    if text_runs > 20:
        signals.append("text-runs-present")
    if re.search(rb"/(Image|XObject).{0,64}/Subtype\s*/Image", data[:131072]):
        signals.append("embedded-images")
    if re.search(rb"/(Table|TR|TD)\b", head):
        signals.append("table-markers")
    if re.search(rb"<table[\s>]", head.lower()):
        signals.append("table-markers")
    if text_runs <= 3 and len(data) > 4096:
        signals.append("text-sparse")
    if mime == "application/pdf" and b"%PDF-" not in data[:8]:
        raise AdmissionError("malformed_source", "PDF magic missing")
    return Preflight(mime=mime, byte_size=len(data), signals=tuple(signals))


def classify_workload(signals: tuple[str, ...], mime: str) -> str:
    """Map preflight signals to a workload class through explicit rules."""
    has_text = "text-runs-present" in signals
    has_images = "embedded-images" in signals
    has_tables = "table-markers" in signals
    sparse = "text-sparse" in signals
    if mime.startswith("image/"):
        return "scanned" if sparse or not has_text else "mixed"
    if has_tables and (has_text or not sparse):
        return "table_heavy"
    if has_text and not has_images and not sparse:
        return "native_text"
    if has_images and not has_text:
        return "scanned"
    if has_text and has_images:
        return "mixed"
    return "unknown"


def route(source_type: str, workload: str) -> Route:
    """Deterministic parser routing with bounded second-parser triggers."""
    if workload not in WORKLOAD_CLASSES:
        raise AdmissionError("malformed_source", f"unknown workload: {workload}")
    primary = select_parser(source_type)
    if workload in {"scanned", "visual_only"}:
        return Route(workload, "ocr-visual-worker", "docling-default",
                     "image-dominant input needs OCR first, structure second")
    if workload == "table_heavy":
        return Route(workload, primary, "ocr-visual-worker",
                     "table regions need a visual challenger")
    if workload in {"mixed", "formula_chart"}:
        return Route(workload, primary, "fallback-second-parser",
                     "mixed content needs disagreement coverage")
    if workload == "unknown":
        return Route(workload, primary, "fallback-second-parser",
                     "unknown workload never runs unchallenged")
    return Route(workload, primary, None, "native text takes the default path")


def check_second_parser_budget(budget: ResourceBudget) -> None:
    """Second-parser triggers are capped: escalation is bounded, not free."""
    try:
        budget.spend("second_parser_triggers", 1.0)
    except BudgetExhausted as exc:
        raise AdmissionError(
            "resource_limit_exceeded",
            f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
        ) from exc


def reconcile_units(
    primary_units: list[dict[str, Any]],
    secondary_units: list[dict[str, Any]] | None,
    *,
    parser_ids: tuple[str, str] = ("primary", "secondary"),
) -> Reconciliation:
    """Reconcile two parser outputs with explicit conflict/uncertain states."""
    by_id_primary = {u["unit_id"]: u for u in primary_units}
    if secondary_units is None:
        units = tuple(
            {**u, "parsers": [parser_ids[0]], "agreement": "unchallenged"}
            for u in primary_units
        )
        return Reconciliation("agree", units, (), ())
    by_id_secondary = {u["unit_id"]: u for u in secondary_units}
    merged: list[dict[str, Any]] = []
    conflicts: list[str] = []
    uncertain: list[str] = []
    for unit_id in sorted(set(by_id_primary) | set(by_id_secondary)):
        left = by_id_primary.get(unit_id)
        right = by_id_secondary.get(unit_id)
        if left is None or right is None:
            uncertain.append(unit_id)
            present = left if left is not None else right
            merged.append({**(present or {}), "parsers": [parser_ids[0] if left else parser_ids[1]],
                           "agreement": "single-sided-uncertain"})
        elif str(left.get("text", "")) == str(right.get("text", "")):
            merged.append({**left, "parsers": list(parser_ids), "agreement": "agree"})
        else:
            conflicts.append(unit_id)
            merged.append({
                "unit_id": unit_id,
                "kind": left.get("kind", "page"),
                "text": str(left.get("text", "")),
                "challenger_text": str(right.get("text", "")),
                "parsers": list(parser_ids),
                "agreement": "conflict",
            })
    verdict = "agree" if not conflicts and not uncertain else (
        "conflict" if conflicts else "uncertain")
    return Reconciliation(verdict, tuple(merged), tuple(conflicts), tuple(uncertain))


def to_source_ir(
    reconciliation: Reconciliation,
    *,
    source_id: str,
    tenant_id: str,
    workspace_id: str,
) -> list[dict[str, Any]]:
    """Emit Source IR unit shapes with dual-parser provenance; none dropped."""
    records = []
    for unit in reconciliation.units:
        records.append({
            "source_id": source_id,
            "source_unit_id": unit["unit_id"],
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "unit_kind": unit.get("kind", "page"),
            "state": "uncertain" if unit.get("agreement") != "agree" else "accounted",
            "provenance": {
                "parsers": unit.get("parsers", []),
                "agreement": unit.get("agreement", "unknown"),
            },
        })
    return records


@dataclass
class BenchmarkCase:
    case_id: str
    expected_units: int
    max_conflicts: int
    max_uncertain: int


@dataclass
class BenchmarkRun:
    case_id: str
    observed_units: int
    conflicts: int
    uncertain: int
    # No default: every scoring call must state the incumbent measurement,
    # otherwise a forgotten baseline silently reads as zero and any
    # full-coverage run "beats" nothing. Promotion requires a comparator.
    baseline_coverage: float


def score_run(case: BenchmarkCase, run: BenchmarkRun) -> BenchmarkScore:
    """Score one frozen benchmark case; challengers win only by measurement."""
    if case.case_id != run.case_id:
        raise AdmissionError("malformed_source", "benchmark case/run mismatch")
    coverage = run.observed_units / case.expected_units if case.expected_units else 0.0
    within_quality = run.conflicts <= case.max_conflicts and run.uncertain <= case.max_uncertain
    beats = coverage >= 1.0 and within_quality and coverage >= run.baseline_coverage
    return BenchmarkScore(
        case_id=case.case_id,
        coverage=round(coverage, 4),
        conflicts=run.conflicts,
        uncertain=run.uncertain,
        beats_baseline=beats,
    )
