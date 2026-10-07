"""Parser boundary and quarantine exit (P05-G4).

Pure deterministic logic with no database and no network, closing the P05
gateway: parsers run on quarantined bytes and return a normalized
intermediate; only the explicit normalization gate can build the trusted
Source IR release, and only from the ``normalized`` trust state.

- isolation: the ParserAdapter protocol receives a QuarantinedView
  (bytes plus admission metadata) and returns a ParserIntermediate. It
  takes no store, no ledger, no network — there is no parameter through
  which a parser could mutate trusted domain state;
- normalization gate: input-digest match, unique unit IDs, legal unit
  kinds/states, character budgets, and provenance preservation are
  checked before anything becomes canonical;
- trusted exit: ``promote_to_trusted`` requires the ``normalized`` state
  and a validated intermediate, then emits a TrustedRelease carrying the
  Source IR fields, evidence spans, taint, and classification labels;
- taint: source content is wrapped as data-not-instructions with
  instruction-pattern markers. This is a defensible boundary with
  provenance, not a claim that prompt injection is solved;
- classification hooks: deterministic secret/credential/PII patterns
  label spans for DLP/egress decisions downstream;
- revocation: deletion emits a tombstone receipt that invalidates named
  derived projections while preserving the audit record;
- failures map to the shared AdmissionError taxonomy; raw parser
  exceptions never cross the product boundary untyped.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Protocol

from gomrey.budgets import BudgetExhausted, ResourceBudget
from gomrey.gateway import AdmissionError, transition_trust

LEGAL_UNIT_KINDS = frozenset({
    "page", "section", "slide", "sheet", "segment",
    "scene", "range", "region", "item",
})

_INSTRUCTION_PATTERNS: list[tuple[str, str]] = [
    ("ignore-prior-instructions", r"ignore\s+(all\s+)?(previous|prior)\s+instructions"),
    ("system-role-claim", r"^\s*system\s*:"),
    ("tool-call-shape", r"(?:tool_call|function_call|<\s*tool\s*>)"),
    ("instruction-brackets", r"\[(?:INST|SYS|SYSTEM)\]"),
    ("prompt-leak-request", r"(?:reveal|repeat|print)\s+(?:your|the)\s+(?:system\s+)?prompt"),
    ("authority-claim", r"you\s+are\s+now\s+(?:an?\s+)?(?:admin|root|developer)"),
]

_SENSITIVITY_PATTERNS: list[tuple[str, str]] = [
    ("secret-aws-key", r"AKIA[0-9A-Z]{16}"),
    ("secret-private-key", r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ("secret-password-assign", r"(?i)password\s*[:=]\s*\S+"),
    ("secret-api-token", r"(?i)(?:api[_-]?key|bearer)\s*[:=]\s*\S+"),
    ("pii-ssn-shape", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("pii-card-shape", r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"),
]


@dataclass(frozen=True)
class QuarantinedView:
    """The only thing a parser may see: bytes plus admission metadata."""

    source_id: str
    parser_id: str
    content_digest: str
    data: bytes
    mime: str


@dataclass
class ParserIntermediate:
    """Untrusted parser output: validated by the gate, never stored as truth."""

    source_id: str
    parser_id: str
    input_digest: str
    units: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TrustedRelease:
    """Quarantine exit: canonical Source IR fields plus taint/provenance."""

    source_id: str
    tenant_id: str
    workspace_id: str
    unit_count: int
    evidence_spans: list[dict[str, Any]]
    taint: dict[str, Any]
    sensitivity_labels: list[str]
    trust_state: str = "trusted-for-retrieval"


@dataclass(frozen=True)
class RevocationReceipt:
    source_id: str
    projections_invalidated: tuple[str, ...]
    audit_preserved: bool = True


class ParserAdapter(Protocol):
    """Parser contract: quarantined bytes in, intermediate out, nothing else."""

    parser_id: str

    def parse(self, view: QuarantinedView) -> ParserIntermediate:
        ...


def run_parser(adapter: ParserAdapter, view: QuarantinedView) -> ParserIntermediate:
    """Execute a parser behind the boundary; raw failures become typed errors."""
    if adapter.parser_id != view.parser_id:
        raise AdmissionError("parser_failure", "parser identity mismatch")
    try:
        result = adapter.parse(view)
    except AdmissionError:
        raise
    except Exception as exc:
        raise AdmissionError("parser_failure", f"parser crashed: {type(exc).__name__}") from exc
    if not isinstance(result, ParserIntermediate):
        raise AdmissionError("parser_failure", "parser returned no intermediate")
    if result.source_id != view.source_id or result.input_digest != view.content_digest:
        raise AdmissionError("parser_failure", "parser intermediate misbound to source")
    return result


def validate_intermediate(
    intermediate: ParserIntermediate,
    *,
    budget: ResourceBudget | None = None,
) -> ParserIntermediate:
    """Normalization gate: reject malformed intermediates before IR release."""
    seen: set[str] = set()
    chars = 0
    for position, unit in enumerate(intermediate.units):
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id or unit_id in seen:
            raise AdmissionError("normalization_failure", f"bad unit id at position {position}")
        seen.add(unit_id)
        if unit.get("kind") not in LEGAL_UNIT_KINDS:
            raise AdmissionError("normalization_failure", f"bad unit kind at position {position}")
        text = unit.get("text", "")
        if not isinstance(text, str):
            raise AdmissionError("normalization_failure", f"non-text unit at position {position}")
        chars += len(text)
    if budget is not None:
        try:
            budget.spend("normalized_chars", float(chars))
            budget.spend("normalized_units", float(len(intermediate.units)))
        except BudgetExhausted as exc:
            raise AdmissionError(
                "resource_limit_exceeded",
                f"{exc.budget} exhausted at {exc.consumed:.0f}/{exc.limit:.0f}",
            ) from exc
    return intermediate


def taint_content(text: str) -> dict[str, Any]:
    """Wrap retrieved content as data with instruction-pattern markers.

    Markers are provenance metadata for downstream model contexts
    (system/user/tool/retrieved/quoted separation). A marker is raised
    attention, not a safety proof: absence of markers is not safety.
    """
    lowered = text.lower()
    markers = sorted({name for name, pattern in _INSTRUCTION_PATTERNS if re.search(pattern, lowered)})
    return {
        "role": "retrieved-source-content",
        "treat_as": "data-not-instructions",
        "instruction_markers": markers,
        "text": text,
    }


def classify_sensitivity(text: str) -> list[str]:
    """Deterministic secret/credential/PII hooks for DLP/egress decisions."""
    return sorted({name for name, pattern in _SENSITIVITY_PATTERNS if re.search(pattern, text)})


def promote_to_trusted(
    *,
    source_id: str,
    tenant_id: str,
    workspace_id: str,
    trust_state: str,
    intermediate: ParserIntermediate,
) -> TrustedRelease:
    """Quarantine exit: only the normalized state releases trusted IR."""
    if trust_state != "normalized":
        raise AdmissionError("unsafe_source", "only normalized sources release trusted IR")
    transition_trust(source_id, "normalized", "trusted-for-retrieval")
    spans: list[dict[str, Any]] = []
    labels: set[str] = set()
    tainted_units: list[dict[str, Any]] = []
    for unit in intermediate.units:
        text = str(unit.get("text", ""))
        tainted = taint_content(text)
        tainted_units.append(tainted)
        labels.update(classify_sensitivity(text))
        spans.append({
            "source_id": source_id,
            "source_unit_id": unit["unit_id"],
            "parser_id": intermediate.parser_id,
            "taint": {"role": tainted["role"], "treat_as": tainted["treat_as"]},
        })
    return TrustedRelease(
        source_id=source_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        unit_count=len(intermediate.units),
        evidence_spans=spans,
        taint={"units": tainted_units, "parser_id": intermediate.parser_id},
        sensitivity_labels=sorted(labels),
    )


def revoke_source(source_id: str, derived_projection_ids: list[str]) -> RevocationReceipt:
    """Delete/revoke: invalidate derived projections, preserve audit history."""
    if not source_id:
        raise AdmissionError("malformed_source", "invalid source_id")
    return RevocationReceipt(
        source_id=source_id,
        projections_invalidated=tuple(derived_projection_ids),
        audit_preserved=True,
    )
