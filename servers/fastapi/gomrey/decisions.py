"""Decision graph, traceable synthesis, and calibration routing (P09-G3).

Pure deterministic logic with no generation and no model calls.
Decisions are traceable records, not autonomous judgments: a decision
links a question to the claims, evidence, constraints, assumptions,
uncertainty, alternatives, and the selected conclusion — with conflicts
exposed downstream, never flattened into an answer string.

- graph: nodes are claims, evidence spans, sources, citations, and
  decisions; edges are supports/contradicts/cites/derives. Dangling
  references and orphan citations are malformed, not partial;
- synthesis consumes verification verdicts: only supported and
  partially_supported claims may enter the synthesis; contradicted,
  does_not_establish, unresolved, and blocked claims are excluded
  with explicit omissions. Generated prose stays downstream of this
  structured record;
- conflicts are first-class output: contradicting evidence, mixed
  stances, and open disagreements travel with the synthesis;
- calibration registry: providers earn workloads by measured
  profiles (benchmark identity, sample size, abstention behavior),
  never by assertion. Routing prefers a valid calibrated profile
  and falls back to deterministic-only with the reason named;
- disagreement policy: deterministic checks first, then an
  independently diverse challenger where supplied, else ABSTAIN /
  UNRESOLVED. Incompatible probabilities are never averaged.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field, replace
from hashlib import sha256
import json
import re
from typing import Any, Optional, Protocol, runtime_checkable

from gomrey.gateway import AdmissionError

NODE_KINDS = frozenset({"claim", "evidence", "source", "citation", "decision"})

EDGE_RELATIONS = frozenset({"supports", "contradicts", "cites", "derives", "context"})

DECISION_STATUSES = frozenset({"proposed", "accepted", "abstained", "blocked", "superseded"})

SYNTHESIS_ELIGIBLE = frozenset({"supported", "partially_supported"})

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _check_id(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not _ID_RE.match(value):
        raise AdmissionError("malformed_source", f"invalid {field_name}")
    return value


@dataclass
class GraphNode:
    node_id: str
    kind: str
    ref: str


@dataclass
class GraphEdge:
    from_id: str
    to_id: str
    relation: str
    note: str = ""


@dataclass
class SupportGraph:
    tenant_id: str
    workspace_id: str
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


def build_graph(
    *,
    tenant_id: str,
    workspace_id: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> SupportGraph:
    """Assemble a validated support graph; dangling refs refused."""
    _check_id(tenant_id, "tenant_id")
    _check_id(workspace_id, "workspace_id")
    seen: set[str] = set()
    graph_nodes: list[GraphNode] = []
    for node in nodes:
        _check_id(str(node.get("node_id", "")), "node_id")
        if node.get("kind") not in NODE_KINDS:
            raise AdmissionError("malformed_source", f"unknown node kind: {node.get('kind')}")
        if not str(node.get("ref", "")).strip():
            raise AdmissionError("malformed_source", "graph node without ref")
        if str(node["node_id"]) in seen:
            raise AdmissionError("normalization_failure", f"duplicate node: {node['node_id']}")
        seen.add(str(node["node_id"]))
        graph_nodes.append(GraphNode(node_id=str(node["node_id"]), kind=str(node["kind"]), ref=str(node["ref"])))
    graph_edges: list[GraphEdge] = []
    for edge in edges:
        if edge.get("relation") not in EDGE_RELATIONS:
            raise AdmissionError("malformed_source", f"unknown edge relation: {edge.get('relation')}")
        for endpoint in ("from_id", "to_id"):
            if str(edge.get(endpoint, "")) not in seen:
                raise AdmissionError(
                    "normalization_failure", f"edge references unknown node: {edge.get(endpoint)}")
        graph_edges.append(GraphEdge(
            from_id=str(edge["from_id"]), to_id=str(edge["to_id"]),
            relation=str(edge["relation"]), note=str(edge.get("note", ""))))
    citation_targets = {edge.to_id for edge in graph_edges if edge.relation == "cites"}
    evidence_ids = {node.node_id for node in graph_nodes if node.kind == "evidence"}
    orphaned = citation_targets - evidence_ids
    if orphaned:
        raise AdmissionError("normalization_failure", f"orphan citation: {sorted(orphaned)[0]}")
    return SupportGraph(tenant_id=tenant_id, workspace_id=workspace_id, nodes=graph_nodes, edges=graph_edges)


def graph_digest(graph: SupportGraph) -> str:
    """Reproducible digest for audit and regeneration checks."""
    canonical = json.dumps({
        "tenant_id": graph.tenant_id,
        "workspace_id": graph.workspace_id,
        "nodes": [{"node_id": n.node_id, "kind": n.kind, "ref": n.ref} for n in graph.nodes],
        "edges": [{"from_id": e.from_id, "to_id": e.to_id,
                   "relation": e.relation, "note": e.note} for e in graph.edges],
    }, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class Decision:
    decision_id: str
    question: str
    tenant_id: str
    workspace_id: str
    claim_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    uncertainty: str = "unknown"
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    conclusion: str = ""
    status: str = "proposed"
    version: int = 1


def make_decision(
    *,
    decision_id: str,
    question: str,
    tenant_id: str,
    workspace_id: str,
    claim_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    constraints: list[str] | None = None,
    assumptions: list[str] | None = None,
    uncertainty: str = "unknown",
    alternatives: list[dict[str, Any]] | None = None,
    conclusion: str = "",
    status: str = "proposed",
    version: int = 1,
) -> Decision:
    """Build a validated decision record; traceability fields required."""
    _check_id(decision_id, "decision_id")
    _check_id(tenant_id, "tenant_id")
    _check_id(workspace_id, "workspace_id")
    if not isinstance(question, str) or not question.strip():
        raise AdmissionError("malformed_source", "decision question is required")
    claims = [_check_id(str(value), "claim_ids") for value in (claim_ids or [])]
    evidence = [_check_id(str(value), "evidence_ids") for value in (evidence_ids or [])]
    if len(set(claims)) != len(claims):
        raise AdmissionError("normalization_failure", "duplicate claim_ids")
    if uncertainty not in ("low", "medium", "high", "unknown"):
        raise AdmissionError("malformed_source", f"unknown uncertainty: {uncertainty}")
    if status not in DECISION_STATUSES:
        raise AdmissionError("malformed_source", f"unknown decision status: {status}")
    if not isinstance(version, int) or version < 1:
        raise AdmissionError("malformed_source", "decision version must be positive")
    for alternative in alternatives or []:
        if not isinstance(alternative, dict) or not str(alternative.get("option", "")).strip():
            raise AdmissionError("malformed_source", "alternative without option")
    return Decision(
        decision_id=decision_id, question=question.strip(),
        tenant_id=tenant_id, workspace_id=workspace_id,
        claim_ids=claims, evidence_ids=evidence,
        constraints=list(constraints or []), assumptions=list(assumptions or []),
        uncertainty=uncertainty, alternatives=[dict(a) for a in (alternatives or [])],
        conclusion=conclusion, status=status, version=version,
    )


def synthesize(
    decision: Decision,
    verdicts: dict[str, dict[str, Any]],
    *,
    require_alternative_when_conflict: bool = True,
) -> dict[str, Any]:
    """Traceable synthesis over verified claims. Conflicts exposed, never hidden.

    Only supported/partially_supported claims enter the synthesis.
    Everything else is listed under omissions with its verdict.
    """
    included: list[str] = []
    omissions: list[dict[str, str]] = []
    conflicts: list[dict[str, Any]] = []
    for claim_id in decision.claim_ids:
        verdict = verdicts.get(claim_id)
        if verdict is None:
            omissions.append({"claim_id": claim_id, "verdict": "unresolved", "reason": "no-verdict-supplied"})
            continue
        state = str(verdict.get("verdict", "unresolved"))
        if state in SYNTHESIS_ELIGIBLE:
            included.append(claim_id)
            if state == "partially_supported":
                conflicts.append({"claim_id": claim_id, "kind": "partial-support",
                                  "reasons": list(verdict.get("reasons", []))})
        else:
            omissions.append({"claim_id": claim_id, "verdict": state,
                              "reason": ",".join(verdict.get("reasons", [])[:2]) or state})
            if state == "contradicted":
                conflicts.append({"claim_id": claim_id, "kind": "contradiction",
                                  "reasons": list(verdict.get("reasons", []))})
    if conflicts and require_alternative_when_conflict and not decision.alternatives:
        return {
            "decision_id": decision.decision_id,
            "question": decision.question,
            "status": "abstained",
            "included_claims": [],
            "omissions": omissions + [{"claim_id": c, "verdict": "withheld",
                                       "reason": "conflict-without-alternative"} for c in included],
            "conflicts": conflicts,
            "conclusion": "",
            "reasons": ["conflict-requires-alternative"],
        }
    status = "accepted" if included else "abstained"
    return {
        "decision_id": decision.decision_id,
        "question": decision.question,
        "status": status,
        "included_claims": included,
        "omissions": omissions,
        "conflicts": conflicts,
        "conclusion": decision.conclusion if included else "",
        "reasons": ["synthesis-complete"] if included else ["no-eligible-claims"],
    }


@dataclass
class CalibrationProfile:
    provider: str
    workload: str
    benchmark: str
    samples: int
    abstention_rate: float


def register_profile(
    registry: dict[str, CalibrationProfile],
    *,
    provider: str,
    workload: str,
    benchmark: str,
    samples: int,
    abstention_rate: float,
) -> dict[str, CalibrationProfile]:
    """Register a measured calibration profile; assertions refused."""
    if not provider.strip() or not workload.strip() or not benchmark.strip():
        raise AdmissionError("malformed_source", "calibration identity is required")
    if not isinstance(samples, int) or samples < 50:
        raise AdmissionError("malformed_source", "calibration needs at least 50 samples")
    if not 0.0 <= abstention_rate <= 1.0:
        raise AdmissionError("malformed_source", "abstention rate out of range")
    updated = dict(registry)
    updated[f"{provider}::{workload}"] = CalibrationProfile(
        provider=provider, workload=workload, benchmark=benchmark,
        samples=samples, abstention_rate=abstention_rate)
    return updated


def route_workload(
    registry: dict[str, CalibrationProfile],
    workload: str,
    candidates: list[str],
) -> dict[str, Any]:
    """Prefer a calibrated provider; else deterministic-only with reason."""
    for provider in candidates:
        profile = registry.get(f"{provider}::{workload}")
        if profile is not None:
            return {"provider": provider, "mode": "calibrated",
                    "benchmark": profile.benchmark, "reason": "valid-profile"}
    return {"provider": "deterministic", "mode": "deterministic-only",
            "benchmark": "", "reason": "no-valid-profile"}


def adjudicate(
    deterministic_verdict: str,
    challenger_verdict: Optional[str] = None,
    challenger_independent: bool = False,
) -> dict[str, Any]:
    """Disagreement policy: deterministic first, else independent challenger, else abstain."""
    if deterministic_verdict not in ("supported", "partially_supported", "contradicted",
                                     "does_not_establish", "unresolved", "blocked"):
        raise AdmissionError("malformed_source", f"unknown verdict: {deterministic_verdict}")
    if challenger_verdict is None:
        return {"verdict": deterministic_verdict, "mode": "deterministic-only", "abstained": False}
    if challenger_verdict == deterministic_verdict:
        return {"verdict": deterministic_verdict, "mode": "agreement", "abstained": False}
    if challenger_independent:
        return {"verdict": "unresolved", "mode": "independent-disagreement",
                "abstained": True, "reason": "challenger-divergence-needs-evidence"}
    return {"verdict": deterministic_verdict, "mode": "deterministic-wins",
            "abstained": False, "reason": "challenger-not-independent"}


@runtime_checkable
class DecisionStore(Protocol):
    """Durable truth for decision records behind tenant isolation."""

    def put(self, decision: Decision) -> None:
        """Insert or replace the canonical decision record."""
        ...

    def get(self, decision_id: str, tenant_id: str, workspace_id: str) -> Optional[Decision]:
        """Return the decision, or None when absent."""
        ...

    def delete(self, decision_id: str, tenant_id: str, workspace_id: str) -> bool:
        """Remove the decision. Returns True when a record was removed."""
        ...


class MemoryDecisionStore:
    """Deterministic dict-backed DecisionStore for tests and adapters."""

    def __init__(self) -> None:
        self._decisions: dict[tuple[str, str, str], Decision] = {}

    def put(self, decision: Decision) -> None:
        self._decisions[(decision.tenant_id, decision.workspace_id, decision.decision_id)] = replace(
            decision, claim_ids=list(decision.claim_ids),
            evidence_ids=list(decision.evidence_ids),
            constraints=list(decision.constraints),
            assumptions=list(decision.assumptions),
            alternatives=[dict(a) for a in decision.alternatives])

    def get(self, decision_id: str, tenant_id: str, workspace_id: str) -> Optional[Decision]:
        stored = self._decisions.get((tenant_id, workspace_id, decision_id))
        if stored is None:
            return None
        return replace(
            stored, claim_ids=list(stored.claim_ids),
            evidence_ids=list(stored.evidence_ids),
            constraints=list(stored.constraints),
            assumptions=list(stored.assumptions),
            alternatives=[dict(a) for a in stored.alternatives])

    def delete(self, decision_id: str, tenant_id: str, workspace_id: str) -> bool:
        return self._decisions.pop((tenant_id, workspace_id, decision_id), None) is not None
