"""Deterministic claim verification with a provider seam (P09-G2).

Pure deterministic logic with no model calls. The verifier classifies the
claim-to-evidence relationship; providers may supply an opinion, never a
verdict. Hard policy wins over model confidence:

- verdicts are closed: supported / partially_supported / contradicted /
  does_not_establish / unresolved / blocked;
- unbindable claims (missing refs, cross-project, stale, open
  contradictions, override flags) never verify as supported — the
  binder's refusal is inherited, not re-judged;
- evidence views carry stance (supports/contradicts/context) plus text.
  Missing views for bound refs mean there is nothing to judge with:
  does_not_establish, not support by assumption;
- deterministic content checks run before any provider opinion:
  numbers and calendar dates named in the claim must appear in at
  least one supporting view; mismatches downgrade to
  does_not_establish with the exact defect named;
- the provider seam is explicit: provider_verdict carries identity
  (provider, model revision); a provider cannot upgrade a
  deterministically failed claim, suppress a contradiction, or clear
  an override flag. Overreach is recorded as provider-overruled;
- source/model/tool text is data: override tripwires in the claim or
  any evidence view force unresolved, never support;
- every verdict carries reasons, the deterministic checks applied,
  and a reproducible digest.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from hashlib import sha256
import json
import re
from typing import Any, Optional

from gomrey.claims import detect_policy_override_attempt
from gomrey.gateway import AdmissionError

VERDICTS = frozenset({
    "supported",
    "partially_supported",
    "contradicted",
    "does_not_establish",
    "unresolved",
    "blocked",
})

STANCES = frozenset({"supports", "contradicts", "context"})

_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\b(?:19|20)\d{2}\b)"
)


def _numbers(text: str) -> list[str]:
    return _NUMBER_RE.findall(text or "")


def _dates(text: str) -> list[str]:
    return _DATE_RE.findall(text or "")


def check_quantity_agreement(claim_text: str, supporting_texts: list[str]) -> dict[str, Any]:
    """Deterministic gate: claim numbers/dates must appear in support.

    Returns {ok, missing_numbers, missing_dates}. Empty claim
    quantities trivially agree; agreement requires presence, never
    inference.
    """
    if not isinstance(claim_text, str) or not claim_text.strip():
        raise AdmissionError("malformed_source", "claim text is required")
    pooled = "\n".join(supporting_texts)
    missing_numbers = [n for n in _numbers(claim_text) if n not in pooled]
    missing_dates = [d for d in _dates(claim_text) if d not in pooled]
    return {
        "ok": not missing_numbers and not missing_dates,
        "missing_numbers": missing_numbers,
        "missing_dates": missing_dates,
    }


def verify_claim(
    claim: Any,
    binding_report: dict[str, Any],
    bundle: Any,
    *,
    evidence_views: Optional[dict[str, dict[str, Any]]] = None,
    provider_verdict: Optional[str] = None,
    provider_identity: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Classify the claim-to-evidence relationship deterministically."""
    if binding_report.get("claim_id") != claim.claim_id:
        raise AdmissionError("malformed_source", "binding report is for another claim")
    if bundle.bundle_id != binding_report.get("bundle_id"):
        raise AdmissionError("malformed_source", "binding report is for another bundle")
    if provider_verdict is not None and provider_verdict not in VERDICTS:
        raise AdmissionError("malformed_source", f"unknown provider verdict: {provider_verdict}")
    if provider_verdict is not None:
        identity = provider_identity or {}
        if not identity.get("provider") or not identity.get("model_revision"):
            raise AdmissionError("malformed_source", "provider verdict without identity")

    reasons: list[str] = []
    checks: list[str] = ["binding-inherited", "stance-tally", "quantity-agreement", "override-tripwire"]

    if not binding_report.get("bindable_for_verification", False):
        for reason in binding_report.get("reasons", []):
            reasons.append(f"binding:{reason}")
        verdict = "contradicted" if "binding:contradictions-open" in reasons else "unresolved"
        if binding_report.get("override_flag"):
            verdict = "unresolved"
        return _verdict(
            claim=claim, bundle=bundle, verdict=verdict, reasons=reasons,
            checks=checks, provider_verdict=provider_verdict,
            provider_identity=provider_identity, overruled=False,
        )

    views = dict(evidence_views or {})
    bound = list(binding_report.get("bound_spans", []))
    absent = [ref for ref in bound if ref not in views]
    if absent:
        reasons.append(f"no-evidence-view:{absent[0]}")
        return _verdict(
            claim=claim, bundle=bundle, verdict="does_not_establish", reasons=reasons,
            checks=checks, provider_verdict=provider_verdict,
            provider_identity=provider_identity,
            overruled=provider_verdict in ("supported", "partially_supported"),
        )

    for ref in bound:
        view = views[ref]
        if not isinstance(view, dict) or view.get("stance") not in STANCES:
            raise AdmissionError("malformed_source", f"evidence view without stance: {ref}")
        if detect_policy_override_attempt(str(view.get("text", ""))):
            reasons.append(f"evidence-override-flagged:{ref}")
    if detect_policy_override_attempt(claim.text):
        reasons.append("policy-override-flagged")
    if any(reason.startswith("evidence-override-flagged") or reason == "policy-override-flagged"
           for reason in reasons):
        return _verdict(
            claim=claim, bundle=bundle, verdict="unresolved", reasons=reasons,
            checks=checks, provider_verdict=provider_verdict,
            provider_identity=provider_identity,
            overruled=provider_verdict in ("supported", "partially_supported", "contradicted"),
        )

    supporting = [ref for ref in bound if views[ref]["stance"] == "supports"]
    contradicting = [ref for ref in bound if views[ref]["stance"] == "contradicts"]
    if contradicting and not supporting:
        verdict = "contradicted"
        reasons.append("contradicting-evidence-only")
    elif contradicting and supporting:
        verdict = "partially_supported"
        reasons.append("conflicting-evidence")
    elif supporting:
        agreement = check_quantity_agreement(
            claim.text, [str(views[ref].get("text", "")) for ref in supporting])
        if not agreement["ok"]:
            verdict = "does_not_establish"
            for missing in agreement["missing_numbers"]:
                reasons.append(f"quantity-mismatch:{missing}")
            for missing in agreement["missing_dates"]:
                reasons.append(f"date-mismatch:{missing}")
        else:
            verdict = "supported"
            reasons.append("supporting-evidence-agrees")
    else:
        verdict = "does_not_establish"
        reasons.append("no-supporting-stance")

    overruled = False
    if provider_verdict is not None:
        if verdict in ("contradicted", "does_not_establish", "unresolved", "blocked"):
            if provider_verdict in ("supported", "partially_supported"):
                overruled = True
                reasons.append("provider-overruled-by-policy")
        if verdict == "partially_supported" and provider_verdict == "supported":
            overruled = True
            reasons.append("provider-overruled-by-policy")

    return _verdict(
        claim=claim, bundle=bundle, verdict=verdict, reasons=reasons,
        checks=checks, provider_verdict=provider_verdict,
        provider_identity=provider_identity, overruled=overruled,
    )


def _verdict(
    *,
    claim: Any,
    bundle: Any,
    verdict: str,
    reasons: list[str],
    checks: list[str],
    provider_verdict: Optional[str],
    provider_identity: Optional[dict[str, str]],
    overruled: bool,
) -> dict[str, Any]:
    record = {
        "claim_id": claim.claim_id,
        "bundle_id": bundle.bundle_id,
        "verdict": verdict,
        "reasons": list(reasons),
        "checks": list(checks),
        "provider_verdict": provider_verdict,
        "provider_identity": dict(provider_identity or {}),
        "provider_overruled": overruled,
    }
    digest = sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    record["digest"] = digest
    return record
