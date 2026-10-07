"""Source IR provenance completion and coverage gate (P06-G4).

Pure deterministic logic with no models and no network. This grain
finishes the P06 ingestion contract by proving two properties over the
outputs of G1–G3:

- provenance completeness: an assembled Source IR document carries an
  unbroken chain on every unit — source/tenant/workspace identity equal
  across admission, parsing, and routing records; content digests linked;
  parser identities and agreement states present; page/bbox coordinates
  where visual. Anything less is refused, not defaulted;
- coverage: the declared unit set reconciles against the emitted
  records through the P04 UnitLedger. Consistent with ledger semantics,
  `verified` means explicitly accounted-for (the reliability contract
  is 100% accounting, never an accuracy claim). Silent drops fail
  loudly; partial results carry exact unresolved coordinates.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from typing import Any

from gomrey.accounting import UnitLedger
from gomrey.gateway import AdmissionError


def _require_match(field_name: str, *values: str) -> str:
    first = values[0]
    if any(not isinstance(v, str) or v != first for v in values):
        raise AdmissionError("unsafe_source", f"cross-record {field_name} mismatch (source mixing)")
    if not first:
        raise AdmissionError("malformed_source", f"empty {field_name}")
    return first


def assemble_ir(
    *,
    source_id: str,
    tenant_id: str,
    workspace_id: str,
    original_digest: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the Source IR document, refusing incomplete provenance."""
    if not records:
        raise AdmissionError("normalization_failure", "IR assembly has no units")
    if len(original_digest) != 64:
        raise AdmissionError("malformed_source", "invalid original digest")
    seen: set[str] = set()
    for position, record in enumerate(records):
        _require_match("source_id", source_id, str(record.get("source_id", "")))
        _require_match("tenant_id", tenant_id, str(record.get("tenant_id", "")))
        _require_match("workspace_id", workspace_id, str(record.get("workspace_id", "")))
        unit_id = record.get("source_unit_id")
        if not isinstance(unit_id, str) or not unit_id or unit_id in seen:
            raise AdmissionError("normalization_failure", f"bad unit id at position {position}")
        seen.add(unit_id)
        provenance = record.get("provenance")
        if not isinstance(provenance, dict) or not provenance.get("parsers"):
            raise AdmissionError("normalization_failure", f"unit {unit_id} lacks parser provenance")
        if "agreement" not in provenance:
            raise AdmissionError("normalization_failure", f"unit {unit_id} lacks agreement state")
        if record.get("state") not in {
            "accounted", "verified", "uncertain", "failed", "skipped", "duplicate", "declared",
        }:
            raise AdmissionError("normalization_failure", f"unit {unit_id} has illegal state")
    return {
        "source_id": source_id,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "original_digest": original_digest,
        "unit_count": len(records),
        "units": [dict(r) for r in records],
    }


_LEDGER_MARK = {
    "verified": "verified",
    "accounted": "verified",
    "uncertain": "uncertain",
    "failed": "failed",
    "skipped": "skipped",
    "duplicate": "duplicate",
    "declared": "uncertain",
}


def verify_coverage(
    declared_unit_ids: list[str],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Reconcile declared units against emitted records via the P04 ledger.

    Silent drops raise loudly. Partial results return exact unresolved
    coordinates instead of a rounded-up success.
    """
    ledger = UnitLedger()
    try:
        ledger.declare(list(declared_unit_ids))
    except Exception as exc:
        raise AdmissionError("malformed_source", f"bad declaration: {type(exc).__name__}") from exc
    record_ids = [str(r.get("source_unit_id", "")) for r in records]
    if len(set(record_ids)) != len(record_ids):
        raise AdmissionError("normalization_failure", "duplicate unit records emitted")
    for record in records:
        unit_id = str(record.get("source_unit_id", ""))
        state = str(record.get("state", ""))
        mark = _LEDGER_MARK.get(state)
        if unit_id not in ledger._states or mark is None:
            raise AdmissionError("normalization_failure", f"unresolvable record: {unit_id or '(empty)'}")
        reason = str(record.get("skip_reason", ""))
        canonical = str(record.get("duplicate_of", ""))
        try:
            ledger.mark(unit_id, mark, reason=reason, canonical_id=canonical)
        except ValueError as exc:
            raise AdmissionError("normalization_failure", f"unmarkable record {unit_id}: {exc}") from exc
    counts = ledger.counts()
    if counts["silent_drops"] > 0:
        raise AdmissionError(
            "normalization_failure",
            f"{counts['silent_drops']} silent drops: {','.join(ledger.unaccounted()[:10])}",
        )
    return {
        "status": ledger.status(),
        "declared": counts["declared_total"],
        "accounted": counts["accounted_units"],
        "uncertain_units": sorted(u for u in ledger.declared if ledger._states[u] == "uncertain"),
        "failed_units": sorted(u for u in ledger.declared if ledger._states[u] == "failed"),
        "silent_drops": 0,
    }
