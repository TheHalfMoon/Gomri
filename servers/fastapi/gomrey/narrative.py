"""Evidence-bound narrative producer (W3).

Pure deterministic logic with no model calls, no network, and no app-layer
imports. This module turns an EvidenceBundle into a structured narrative plan
whose nodes carry resolvable citation locators, and it produces the
NarrativeIR that the artifact carries.

- evidence first: a plan is built from the bundle's spans, bound to
  claims, and classified by the P09-G2 verifier before any prose exists;
- the provider renders, it never decides: a plan node states its claims,
  their verdict, and its locators; the model may only phrase them;
- citation identity is minted by citations.make_locator and proven by
  citations.resolve; a locator that cannot be resolved degrades the node
  to an abstention, it is never replaced by a plausible one;
- conflicts are first-class: a node whose claims disagree is marked
  conflicted and carries both sides, it is never averaged into one;
- sufficiency is obeyed: an insufficient bundle produces a plan whose
  nodes may only say what is not known.

Failures raise the shared AdmissionError taxonomy from gateway.py;
unresolvable citations raise BrokenCitation from citations.py.

Verification scope
------------------
The P09-G2 verifier gates exactly two dimensions deterministically: **numbers**
and **dates** (see ``verification.check_quantity_agreement``). It has **no unit
gate and no entity gate** — ``contracts/v1/claim.schema.json`` declares a
``unit_check`` field, but no code implements it anywhere in ``gomrey/``.

A verdict of ``supported`` therefore means *"the numbers and dates agree, the
stance is supporting, and no override pattern was found"*. It does **not** mean
that the units or the named entities were verified. This module never lets a
``supported`` verdict imply otherwise:

* :data:`DETERMINISTIC_GATES` and :data:`UNVERIFIED_DIMENSIONS` state the scope
  explicitly;
* every plan carries a ``verification_scope`` block that travels with the
  artifact;
* a grounded node records the dimensions that were *not* checked in its
  reasons, so a consumer cannot mistake "grounded" for "fully verified";
* :func:`render_plan_context` and :func:`render_plan_rules` tell the producer
  the same thing in prose.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Optional

from gomrey.claims import bind_claim_to_bundle, make_claim
from gomrey.citations import BrokenCitation, make_locator, resolve
from gomrey.decisions import SYNTHESIS_ELIGIBLE, make_decision, synthesize
from gomrey.evidence_bundle import sufficiency_check
from gomrey.gateway import AdmissionError
from gomrey.verification import check_quantity_agreement, verify_claim

__all__ = [
    "ABSTENTION_MARKER",
    "CONFLICT_MARKER",
    "DETERMINISTIC_GATES",
    "GROUNDED_MARKER",
    "MAX_PLAN_NODES",
    "NODE_STATUSES",
    "UNVERIFIED_DIMENSIONS",
    "NarrativePlan",
    "PlanNode",
    "assert_exportable",
    "build_narrative_ir",
    "build_narrative_plan",
    "bind_slide_locators",
    "check_plan_containment",
    "collect_rendered_text",
    "narrative_digest",
    "plan_index_for_slide",
    "plan_node_for_slide",
    "plan_node_from_narrative",
    "render_node_context",
    "render_node_rules",
    "render_plan_context",
    "render_plan_rules",
    "verification_scope",
]

#: Status vocabulary for a plan node.
NODE_STATUSES = frozenset({"grounded", "abstained", "conflicted"})

GROUNDED_MARKER = "grounded"
ABSTENTION_MARKER = "abstained"
CONFLICT_MARKER = "conflicted"

#: The dimensions the deterministic verifier actually gates.
DETERMINISTIC_GATES: tuple[str, ...] = ("numbers", "dates")

#: The dimensions the deterministic verifier does **not** gate. A claim that
#: passes the gates above has NOT had these checked.
UNVERIFIED_DIMENSIONS: tuple[str, ...] = ("units", "entities")

#: Upper bound on plan nodes. Keeps the producer's work bounded regardless of
#: the requested slide count.
MAX_PLAN_NODES = 200

_EPOCH_TIMESTAMP = "1970-01-01T00:00:00Z"
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s")


def verification_scope() -> dict[str, list[str]]:
    """The explicit, machine-readable verification scope of this module."""
    return {
        "gated": list(DETERMINISTIC_GATES),
        "not_gated": list(UNVERIFIED_DIMENSIONS),
    }


@dataclass(frozen=True)
class PlanNode:
    """One narrative node: a slide's worth of evidence-bound claims."""

    node_id: str
    heading: str
    claim_ids: list[str]
    claim_texts: list[str]
    citation_ids: list[str]
    locators: list[dict[str, Any]]
    status: str
    reasons: list[str]


@dataclass(frozen=True)
class NarrativePlan:
    """The deterministic evidence-to-narrative plan."""

    plan_id: str
    bundle_id: str
    tenant_id: str
    workspace_id: str
    nodes: list[PlanNode]
    conflicts: list[dict[str, Any]]
    omissions: list[dict[str, str]]
    sufficiency: dict[str, Any]
    synthesis: dict[str, Any]
    verdicts: dict[str, dict[str, Any]]
    verification_scope: dict[str, list[str]]
    digest: str

    @property
    def node_count(self) -> int:
        """The number of plan nodes, and therefore of content slides."""
        return len(self.nodes)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: Any) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _span_identity(span: dict[str, Any]) -> str:
    return str(span.get("citation_id") or span.get("span_id") or "")


def _heading_for(texts: list[str], index: int) -> str:
    for text in texts:
        cleaned = " ".join(str(text).split())
        if not cleaned:
            continue
        first = _SENTENCE_SPLIT.split(cleaned)[0]
        return first[:120].rstrip() or f"Section {index + 1}"
    return f"Section {index + 1}"


def _plan_node_payload(node: PlanNode) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "heading": node.heading,
        "claim_ids": list(node.claim_ids),
        "claim_texts": list(node.claim_texts),
        "citation_ids": list(node.citation_ids),
        "locators": [dict(locator) for locator in node.locators],
        "status": node.status,
        "reasons": list(node.reasons),
    }


def build_narrative_plan(
    bundle: Any,
    ir_document: dict[str, Any],
    *,
    plan_id: str,
    tenant_id: str,
    workspace_id: str,
    n_slides: Optional[int] = None,
    min_spans: int = 2,
    require_fresh: bool = True,
    provider_verdict: Optional[str] = None,
    provider_identity: Optional[dict[str, str]] = None,
    timestamp: Optional[str] = None,
) -> NarrativePlan:
    """Build the deterministic evidence-to-narrative plan.

    ``bundle`` is a :class:`gomrey.evidence_bundle.EvidenceBundle``.
    ``ir_document`` is an assembled Source IR (``gomrey.ir_provenance.assemble_ir``
    shape) used to prove every locator resolvable.
    ``provider_verdict`` / ``provider_identity`` are forwarded verbatim to
    :func:`gomrey.verification.verify_claim`; a provider may never upgrade a
    deterministic failure (P09-G2 semantics, unchanged).
    """
    if n_slides is not None and (
        not isinstance(n_slides, int) or isinstance(n_slides, bool) or n_slides < 1
    ):
        raise AdmissionError("malformed_source", "n_slides must be a positive integer")
    if n_slides is not None and n_slides > MAX_PLAN_NODES:
        raise AdmissionError("resource_limit_exceeded", "n_slides exceeds the plan bound")
    if getattr(bundle, "tenant_id", None) != tenant_id or getattr(bundle, "workspace_id", None) != workspace_id:
        raise AdmissionError("access_denied", "bundle and plan are in different projects")
    if not isinstance(ir_document, dict):
        raise AdmissionError("malformed_source", "ir_document must be a mapping")

    stamp = timestamp or _EPOCH_TIMESTAMP
    sufficiency = sufficiency_check(bundle, min_spans=min_spans, require_fresh=require_fresh)

    omissions: list[dict[str, str]] = []
    citable: list[dict[str, Any]] = []

    for span in bundle.spans:
        if not isinstance(span, dict):
            omissions.append({"span_id": "", "reason": "span-not-a-mapping"})
            continue
        span_id = _span_identity(span)
        if not span_id:
            omissions.append({"span_id": "", "reason": "span-without-identity"})
            continue

        declared_citation_id = span.get("citation_id")
        if not declared_citation_id:
            # A span that does not declare a citation identity cannot become
            # citable. It is never given a freshly minted identity, because a
            # minted identity would assert provenance the span never claimed.
            omissions.append({"span_id": span_id, "reason": "span-without-citation-id"})
            continue

        locator_input = span.get("locator")
        if not isinstance(locator_input, dict):
            omissions.append({"span_id": span_id, "reason": "span-without-locator"})
            continue

        kind = locator_input.get("kind")
        fields = {
            key: value
            for key, value in locator_input.items()
            if key not in ("kind", "citation_id")
        }
        try:
            locator = make_locator(str(kind), **fields)
        except BrokenCitation as exc:
            omissions.append({"span_id": span_id, "reason": f"malformed-locator:{exc.reason}"})
            continue

        # The single guard that makes a fabricated citation impossible: the
        # locator must mint exactly the identity the span declared.
        if locator["citation_id"] != declared_citation_id:
            raise AdmissionError(
                "normalization_failure",
                f"span {span_id} declares a citation id its locator does not produce",
            )

        try:
            resolve(locator, ir_document)
        except BrokenCitation as exc:
            omissions.append({"span_id": span_id, "reason": f"unresolvable-citation:{exc.reason}"})
            continue

        citable.append({"span": span, "locator": locator, "span_id": span_id})

    claims: list[Any] = []
    verdicts: dict[str, dict[str, Any]] = {}
    claim_locators: dict[str, dict[str, Any]] = {}
    claim_texts: dict[str, str] = {}

    for item in citable:
        span = item["span"]
        evidence_text = str(span.get("text") or "").strip()
        if not evidence_text:
            omissions.append({"span_id": item["span_id"], "reason": "span-without-text"})
            continue
        # The claim is the *assertion*; the span text is the *evidence*. A span
        # may state its assertion explicitly as ``claim_text``. When it does,
        # the deterministic quantity gate compares the assertion's numbers and
        # dates against the evidence text, which is the only way that gate can
        # carry meaning. When it does not, the claim restates the evidence
        # verbatim and the quantity gate is trivially satisfied.
        text = str(span.get("claim_text") or evidence_text).strip()
        claim_id = "cl-" + item["span_id"]
        claim = make_claim(
            claim_id=claim_id,
            text=text,
            tenant_id=bundle.tenant_id,
            workspace_id=bundle.workspace_id,
            evidence_refs=[item["span_id"]],
            created_at=stamp,
            updated_at=stamp,
            derivation={"kind": "derived", "source": "evidence-span"},
        )
        binding = bind_claim_to_bundle(claim, bundle, require_fresh=require_fresh)
        evidence_views = {
            item["span_id"]: {
                "stance": str(span.get("stance") or "supports"),
                "text": evidence_text,
            }
        }
        verdict = verify_claim(
            claim,
            binding,
            bundle,
            evidence_views=evidence_views,
            provider_verdict=provider_verdict,
            provider_identity=provider_identity,
        )
        claims.append(claim)
        verdicts[claim_id] = verdict
        claim_locators[claim_id] = item["locator"]
        claim_texts[claim_id] = text

    alternatives: list[dict[str, Any]] = []
    for contradiction in bundle.contradictions or []:
        option = str(
            contradiction.get("description")
            or contradiction.get("reason")
            or "conflicting evidence"
        ).strip()
        if not option:
            option = "conflicting evidence"
        alternatives.append(
            {
                "option": option,
                "span_ids": [str(value) for value in contradiction.get("span_ids", [])],
            }
        )

    decision = make_decision(
        decision_id="dec-" + str(bundle.bundle_id),
        question=str(bundle.query),
        tenant_id=bundle.tenant_id,
        workspace_id=bundle.workspace_id,
        claim_ids=[claim.claim_id for claim in claims],
        evidence_ids=[item["span_id"] for item in citable],
        alternatives=alternatives,
    )
    synthesis = synthesize(decision, verdicts)

    # The plan fixes its own node count so that the positional binding between
    # a plan node and a rendered slide is exactly one to one. When the caller
    # does not fix a count, the evidence does: one node per citable claim,
    # bounded by MAX_PLAN_NODES.
    if n_slides is None:
        n_slides = max(1, min(len(claims), MAX_PLAN_NODES))
    node_count = n_slides
    nodes: list[PlanNode] = []
    for index in range(node_count):
        assigned = claims[index::node_count]
        node_claim_ids = [claim.claim_id for claim in assigned]
        node_verdicts = [verdicts[claim_id] for claim_id in node_claim_ids]
        node_states = [str(record.get("verdict", "unresolved")) for record in node_verdicts]

        locators: list[dict[str, Any]] = []
        citation_ids: list[str] = []
        seen: set[str] = set()
        for claim_id in node_claim_ids:
            locator = claim_locators[claim_id]
            identity = str(locator["citation_id"])
            if identity in seen:
                continue
            seen.add(identity)
            locators.append(dict(locator))
            citation_ids.append(identity)

        reasons: list[str] = []
        if not node_claim_ids:
            status = ABSTENTION_MARKER
            reasons.append("no-eligible-claim")
        elif any(state == "contradicted" for state in node_states) or any(
            state == "partially_supported" for state in node_states
        ):
            status = CONFLICT_MARKER
            reasons.append("claims-disagree")
        elif all(state == "supported" for state in node_states):
            status = GROUNDED_MARKER
        else:
            status = ABSTENTION_MARKER
            reasons.append("no-eligible-claim")

        if status == GROUNDED_MARKER and str(sufficiency.get("verdict")) == "insufficient":
            # Sufficiency is obeyed: an insufficient bundle may only say what
            # is not known. A claim that happens to pass the deterministic gates
            # still cannot ground a node when the bundle is short of evidence.
            status = ABSTENTION_MARKER
            reasons.append("insufficient-evidence")

        if status == GROUNDED_MARKER:
            # The deterministic gates are numbers and dates only. Say so on the
            # node so that "grounded" can never be read as "fully verified".
            for dimension in UNVERIFIED_DIMENSIONS:
                reasons.append(f"{dimension}-not-gated")

        for state in node_states:
            if state not in SYNTHESIS_ELIGIBLE:
                reasons.append(f"excluded:{state}")

        nodes.append(
            PlanNode(
                node_id=f"n-{index + 1}",
                heading=_heading_for([claim_texts[claim_id] for claim_id in node_claim_ids], index),
                claim_ids=node_claim_ids,
                claim_texts=[claim_texts[claim_id] for claim_id in node_claim_ids],
                citation_ids=citation_ids,
                locators=locators,
                status=status,
                reasons=reasons,
            )
        )

    merged_conflicts = list(synthesis.get("conflicts", []))
    for contradiction in bundle.contradictions or []:
        merged_conflicts.append(
            {
                "kind": "bundle-contradiction",
                "span_ids": [str(value) for value in contradiction.get("span_ids", [])],
                "description": str(
                    contradiction.get("description")
                    or contradiction.get("reason")
                    or "conflicting evidence"
                ),
            }
        )

    payload = {
        "plan_id": plan_id,
        "bundle_id": str(bundle.bundle_id),
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "nodes": [_plan_node_payload(node) for node in nodes],
        "conflicts": merged_conflicts,
        "omissions": list(synthesis.get("omissions", [])) + omissions,
        "sufficiency": dict(sufficiency),
        "synthesis": dict(synthesis),
        "verdicts": {key: dict(value) for key, value in verdicts.items()},
        "verification_scope": verification_scope(),
    }

    return NarrativePlan(
        plan_id=plan_id,
        bundle_id=str(bundle.bundle_id),
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        nodes=nodes,
        conflicts=merged_conflicts,
        omissions=payload["omissions"],
        sufficiency=dict(sufficiency),
        synthesis=dict(synthesis),
        verdicts={key: dict(value) for key, value in verdicts.items()},
        verification_scope=verification_scope(),
        digest=_digest(payload),
    )


def render_plan_context(plan: NarrativePlan) -> str:
    """Render the closed fact base injected into the provider prompt.

    Contains, per node, the node heading, the verified claim texts, the
    citation IDs, and the node status. Contains no number or date that is not
    present in a verified claim text.
    """
    lines: list[str] = []
    scope = plan.verification_scope or verification_scope()
    lines.append(
        "[VERIFICATION SCOPE] gated: "
        + ", ".join(scope.get("gated", []))
        + " | not gated: "
        + ", ".join(scope.get("not_gated", []))
    )
    lines.append(
        "[EVIDENCE SUFFICIENCY] "
        + str(plan.sufficiency.get("verdict", "unknown"))
        + " "
        + ",".join(str(reason) for reason in plan.sufficiency.get("reasons", []))
    )
    total = len(plan.nodes)
    for index, node in enumerate(plan.nodes):
        lines.append(
            f"[EVIDENCE PLAN {index + 1}/{total}] status={node.status} node={node.node_id}"
        )
        lines.append(f"heading: {node.heading}")
        if node.claim_texts:
            lines.append("claims:")
            for text in node.claim_texts:
                lines.append(f"- {text}")
            lines.append("citations: " + ", ".join(node.citation_ids))
        else:
            lines.append("claims: (none)")
            lines.append("citations: (none)")
        if node.reasons:
            lines.append("reasons: " + ", ".join(node.reasons))
    if plan.omissions:
        lines.append(
            "[EVIDENCE OMISSIONS] "
            + "; ".join(
                f"{item.get('span_id', '')}:{item.get('reason', '')}"
                for item in plan.omissions
            )
        )
    if plan.conflicts:
        lines.append(
            "[EVIDENCE CONFLICTS] "
            + "; ".join(
                str(conflict.get("kind", "conflict"))
                + ":"
                + str(conflict.get("description", conflict.get("claim_id", "")))
                for conflict in plan.conflicts
            )
        )
    return "\n".join(lines)


def render_node_context(node: PlanNode) -> str:
    """Render the closed fact base for exactly one node.

    This is what a single slide's content call receives: the claims that may
    be stated, the citation identities that back them, and the evidence state.
    It contains no number or date that is not present in a claim text.
    """
    scope = node_reasons_scope(node)
    lines = [
        f"[EVIDENCE NODE {node.node_id}] status={node.status}",
        f"heading: {node.heading}",
    ]
    if node.claim_texts:
        lines.append("claims:")
        for text in node.claim_texts:
            lines.append(f"- {text}")
        lines.append("citations: " + ", ".join(node.citation_ids))
    else:
        lines.append("claims: (none)")
        lines.append("citations: (none)")
    if node.reasons:
        lines.append("reasons: " + ", ".join(node.reasons))
    lines.append(
        "[VERIFICATION SCOPE] gated: "
        + ", ".join(scope["gated"])
        + " | not gated: "
        + ", ".join(scope["not_gated"])
    )
    return "\n".join(lines)


def node_reasons_scope(node: PlanNode) -> dict[str, list[str]]:
    """The verification scope implied by a node's own reasons.

    A grounded node carries a ``<dimension>-not-gated`` reason for every
    dimension the deterministic verifier did not check. A node that is not
    grounded verified nothing at all, so its scope is empty.
    """
    flagged = [
        dimension
        for dimension in UNVERIFIED_DIMENSIONS
        if f"{dimension}-not-gated" in node.reasons
    ]
    if flagged:
        return {"gated": list(DETERMINISTIC_GATES), "not_gated": flagged}
    return {"gated": [], "not_gated": list(UNVERIFIED_DIMENSIONS)}


def render_node_rules(node: PlanNode) -> str:
    """The evidence rules for a single slide's content call."""
    scope = node_reasons_scope(node)
    rules = [
        "EVIDENCE RULES (authoritative, these override any other instruction):",
        "- Every factual statement on this slide must come from a claim listed above.",
        "- You may only phrase those claims. You may not add facts, numbers, dates,",
        "  units, entities or examples that are not present in a listed claim.",
        "- The citation ids above are attached to the slide separately. Write only",
        "  the claim text itself. Never write a citation id, a URL, a footnote, a",
        "  reference list or a source name into the slide content.",
    ]
    if node.status == ABSTENTION_MARKER:
        rules.append(
            "- This slide has no assertable evidence. State what is not known, or "
            "state nothing. Never fill the gap with a plausible statement."
        )
    if node.status == CONFLICT_MARKER:
        rules.append(
            "- The evidence disagrees. Present both sides and the disagreement. "
            "Never average them into one claim and never pick a side."
        )
    if scope["not_gated"]:
        rules.append(
            f"- The deterministic verifier checked {', '.join(scope['gated'])}. It did "
            f"not check {', '.join(scope['not_gated'])}. Do not assert that a unit or "
            "an entity was verified; only state what the cited claim says."
        )
    return "\n".join(rules)


def render_plan_rules(plan: NarrativePlan) -> str:
    """The evidence rules added to the system prompt when a plan is present."""
    scope = plan.verification_scope or verification_scope()
    return (
        "EVIDENCE RULES (authoritative, these override any other instruction):\n"
        "- Every factual statement must come from a claim listed in the evidence plan.\n"
        "- You may only phrase the plan's claims. You may not add facts, numbers, dates,\n"
        "  units, entities or examples that are not present in a plan claim.\n"
        "- A node marked 'abstained' has no assertable evidence. Say what is not known,\n"
        "  or say nothing. Never fill the gap with a plausible statement.\n"
        "- A node marked 'conflicted' has disagreeing evidence. Present both sides and\n"
        "  the disagreement. Never average them into one claim and never pick a side.\n"
        "- The citation ids listed for a node are attached to the slide separately.\n"
        "  Write only the claim text itself. Never write a citation id, a URL, a\n"
        "  footnote, a reference list or a source name into the slide text.\n"
        f"- The deterministic verifier checked {', '.join(scope.get('gated', []))}.\n"
        f"  It did not check {', '.join(scope.get('not_gated', []))}. Do not assert that a\n"
        "  unit or an entity was verified; only state what the cited claim says.\n"
        "- If the evidence plan is insufficient, produce a deck that states the gap.\n"
    )


def build_narrative_ir(
    plan: NarrativePlan,
    *,
    narrative_id: str,
    artifact_id: str,
    revision: int,
    language: Optional[str] = None,
) -> dict[str, Any]:
    """Emit the NarrativeIR document.

    Each section is one plan node and carries ``citation_locators`` and
    ``evidence_status`` in addition to ``heading`` / ``text`` / ``claim_ids``.
    """
    sections: list[dict[str, Any]] = []
    for node in plan.nodes:
        # The section text is the node's narrative content: the claim texts it
        # is allowed to state. It round-trips so that a node can be rebuilt from
        # the persisted artifact alone, without the in-memory plan.
        text = "\n".join(f"- {claim}" for claim in node.claim_texts)
        if not text:
            text = " ".join(node.heading.split())
        sections.append(
            {
                "heading": node.heading,
                "text": text,
                "claim_ids": list(node.claim_ids),
                "citation_locators": [dict(locator) for locator in node.locators],
                "evidence_status": node.status,
            }
        )
    document: dict[str, Any] = {
        "narrative_id": narrative_id,
        "artifact_id": artifact_id,
        "revision": revision,
        "tenant_id": plan.tenant_id,
        "workspace_id": plan.workspace_id,
        "sections": sections,
        "verification_scope": dict(plan.verification_scope or verification_scope()),
    }
    if language:
        document["language"] = language
    return document


#: Keys whose string values are audience-facing prose in a rendered slide.
_PROSE_KEYS = frozenset(
    {
        "text",
        "title",
        "subtitle",
        "heading",
        "body",
        "description",
        "label",
        "caption",
        "quote",
        "value",
        "content",
        "speaker_note",
        "notes",
    }
)


def collect_rendered_text(value: Any) -> str:
    """Collect the audience-facing prose of a rendered slide.

    The collector is layout-agnostic: it walks the generated slide content and
    gathers the string values that a reader would see. Identifiers, layout
    names, colours and URLs are not prose and are ignored.
    """
    parts: list[str] = []

    def walk(node: Any, key: str | None) -> None:
        if isinstance(node, str):
            if key is not None and key in _PROSE_KEYS:
                parts.append(node)
            return
        if isinstance(node, dict):
            for child_key, child in node.items():
                walk(child, str(child_key))
            return
        if isinstance(node, (list, tuple)):
            for child in node:
                walk(child, key)
            return

    walk(value, None)
    return "\n".join(parts)


def check_plan_containment(node: PlanNode, rendered_text: str) -> dict[str, Any]:
    """Check that rendered slide text stays inside the plan's claim texts.

    The plan constrains the provider by prompt. This is the deterministic
    counterpart: every number and date the rendered slide states must already
    appear in a claim the plan verified. A slide that states a figure the
    evidence does not carry is not grounded, whatever the prompt said.

    The comparison reuses the P09-G2 quantity gate, so there is exactly one
    number-and-date rule in the product.
    """
    if node.status != GROUNDED_MARKER:
        return {
            "checked": False,
            "ok": True,
            "missing_numbers": [],
            "missing_dates": [],
            "reasons": ["node-not-grounded"],
        }
    if not node.claim_texts:
        return {
            "checked": False,
            "ok": True,
            "missing_numbers": [],
            "missing_dates": [],
            "reasons": ["no-claim-text"],
        }
    if not rendered_text.strip():
        return {
            "checked": False,
            "ok": True,
            "missing_numbers": [],
            "missing_dates": [],
            "reasons": ["no-rendered-text"],
        }

    agreement = check_quantity_agreement(rendered_text, list(node.claim_texts))
    missing_numbers = list(agreement.get("missing_numbers") or [])
    missing_dates = list(agreement.get("missing_dates") or [])
    ok = not missing_numbers and not missing_dates
    reasons: list[str] = []
    if not ok:
        reasons.append("rendered-content-outside-plan")
    return {
        "checked": True,
        "ok": ok,
        "missing_numbers": missing_numbers,
        "missing_dates": missing_dates,
        "reasons": reasons,
    }


def plan_index_for_slide(
    index: int,
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> Optional[int]:
    """The plan node index for a rendered slide index, or ``None``.

    The rendered order is ``[title] + [toc] * toc_slides + [node 0, node 1, ...]``.
    The title slide and the table-of-contents slides carry no plan node.
    """
    if toc_slides < 0:
        raise AdmissionError("malformed_source", "toc_slides must not be negative")
    insertion = 1 if title_slide else 0
    if index < insertion:
        return None
    if index < insertion + toc_slides:
        return None
    return index - insertion - toc_slides


def plan_node_for_slide(
    plan: Optional[NarrativePlan],
    index: int,
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> Optional[PlanNode]:
    """The plan node for a rendered slide index, or ``None``."""
    if plan is None:
        return None
    node_index = plan_index_for_slide(
        index, toc_slides=toc_slides, title_slide=title_slide
    )
    if node_index is None or node_index >= len(plan.nodes):
        return None
    return plan.nodes[node_index]


def plan_node_from_narrative(
    narrative_ir: Optional[dict[str, Any]],
    index: int,
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> Optional[PlanNode]:
    """Rebuild a plan node from a persisted NarrativeIR.

    The recovery path re-renders a slide long after generation, when the
    in-memory plan is gone. Rebuilding the node from the artifact keeps the
    recovered slide under the same evidence rules as the original.
    """
    if not isinstance(narrative_ir, dict):
        return None
    sections = narrative_ir.get("sections") or []
    node_index = plan_index_for_slide(
        index, toc_slides=toc_slides, title_slide=title_slide
    )
    if node_index is None or node_index >= len(sections):
        return None
    section = sections[node_index]
    if not isinstance(section, dict):
        return None
    locators = [
        dict(locator)
        for locator in (section.get("citation_locators") or [])
        if isinstance(locator, dict)
    ]
    raw_text = str(section.get("text") or "")
    claim_texts = [
        line[2:].strip()
        for line in raw_text.split("\n")
        if line.startswith("- ") and line[2:].strip()
    ]
    scope = narrative_ir.get("verification_scope")
    if not isinstance(scope, dict):
        scope = verification_scope()
    reasons = [
        f"{dimension}-not-gated"
        for dimension in scope.get("not_gated", list(UNVERIFIED_DIMENSIONS))
    ]
    status = str(section.get("evidence_status") or ABSTENTION_MARKER)
    if status not in NODE_STATUSES:
        status = ABSTENTION_MARKER
    return PlanNode(
        node_id=f"n-{node_index + 1}",
        heading=str(section.get("heading") or ""),
        claim_ids=[str(value) for value in (section.get("claim_ids") or [])],
        claim_texts=claim_texts,
        citation_ids=[str(locator.get("citation_id", "")) for locator in locators],
        locators=locators,
        status=status,
        reasons=reasons,
    )


def bind_slide_locators(
    plan: NarrativePlan,
    slides: list[Any],
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> list[dict[str, Any]]:
    """Bind plan nodes to rendered slides; returns one dict per slide.

    Each dict is ``{"citation_ids": [...], "evidence_status": str,
    "reasons": [...]}``. The mapping is positional after the deterministic
    table-of-contents remap. A slide with no corresponding node — the title
    slide, a table-of-contents slide, or a slide beyond the plan — gets the
    abstention status and no citation ids.
    """
    bindings: list[dict[str, Any]] = []
    for index, _slide in enumerate(slides):
        node_index = plan_index_for_slide(
            index, toc_slides=toc_slides, title_slide=title_slide
        )
        if node_index is None or node_index >= len(plan.nodes):
            bindings.append(
                {
                    "citation_ids": [],
                    "evidence_status": ABSTENTION_MARKER,
                    "reasons": ["no-plan-node"],
                }
            )
            continue
        node = plan.nodes[node_index]
        bindings.append(
            {
                "citation_ids": list(node.citation_ids),
                "evidence_status": node.status,
                "reasons": list(node.reasons),
            }
        )
    return bindings


def assert_exportable(
    narrative_ir: dict[str, Any],
    ir_document: dict[str, Any],
) -> None:
    """Export-time assertion: every locator in the artifact must resolve.

    Raises :class:`gomrey.citations.BrokenCitation` on the first unresolvable
    locator, naming the citation id and the defect. A section that claims to be
    grounded but carries no locator is also a defect: it would be an assertion
    of support with nothing behind it. Returns ``None`` otherwise.
    """
    if not isinstance(narrative_ir, dict):
        raise AdmissionError("malformed_source", "narrative_ir must be a mapping")
    for section in narrative_ir.get("sections", []):
        if not isinstance(section, dict):
            raise AdmissionError("malformed_source", "narrative section must be a mapping")
        status = str(section.get("evidence_status", ""))
        locators = section.get("citation_locators") or []
        if status == GROUNDED_MARKER and not locators:
            raise BrokenCitation(
                "",
                "a grounded narrative section carries no citation locator",
            )
        for locator in locators:
            if not isinstance(locator, dict):
                raise BrokenCitation("", "narrative section carries a malformed locator")
            try:
                resolve(locator, ir_document)
            except BrokenCitation as exc:
                raise BrokenCitation(
                    str(locator.get("citation_id", "")) or exc.citation_id,
                    f"export-time citation revalidation failed: {exc.reason}",
                ) from exc


def narrative_digest(narrative_ir: dict[str, Any]) -> str:
    """Reproducible sha256 digest over the canonical NarrativeIR."""
    return _digest(narrative_ir)
