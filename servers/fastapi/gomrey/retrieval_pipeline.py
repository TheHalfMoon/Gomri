"""Layered retrieval pipeline contracts (P08-G1).

Pure deterministic logic with no index servers and no embeddings. The
pipeline is an ordering discipline over candidate records that future
index stages produce — and a set of guarantees that hold even when the
expensive stages are absent:

- ACL first: tenant/workspace/scope filtering precedes all ranking. No
  score ever promotes an unauthorized record into visibility; denied
  candidates are counted, never leaked;
- cheap signals first: exact identifier/location lookup, then lexical
  overlap computed directly, before any dense/visual/graph scores that
  arrive as inputs;
- fusion is explicit: weighted combination with recorded weights and
  per-candidate channel presence, so a missing channel reads as absent
  evidence, not zero quality;
- freshness is a filter: stale records are excluded by default and
  labeled when explicitly included (P07-exit obligation);
- diversity caps bound per-source dominance;
- rebuildable rule: with dense/visual/graph channels absent, the
  pipeline still retrieves through exact plus lexical — never nothing.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from typing import Any

from gomrey.gateway import AdmissionError

CHANNELS = ("exact", "lexical", "dense", "visual", "graph")


def acl_filter(
    candidates: list[dict[str, Any]],
    *,
    tenant_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """First stage: keep only in-scope records; count the denied."""
    kept: list[dict[str, Any]] = []
    denied = 0
    for candidate in candidates:
        if (candidate.get("tenant_id") == tenant_id
                and candidate.get("workspace_id") == workspace_id):
            kept.append(candidate)
        else:
            denied += 1
    return {"kept": kept, "denied": denied}


def lexical_overlap(query: str, text: str) -> float:
    """Deterministic term-overlap score in [0, 1]; the lexical channel."""
    query_terms = {t for t in query.lower().split() if len(t) > 2}
    if not query_terms:
        return 0.0
    text_terms = set(text.lower().split())
    return round(len(query_terms & text_terms) / len(query_terms), 4)


def exact_boost(
    candidates: list[dict[str, Any]],
    *,
    identifiers: list[str],
) -> list[dict[str, Any]]:
    """Identifier/location matches surface first, scores preserved."""
    wanted = set(identifiers)
    hits = [c for c in candidates if c.get("unit_id") in wanted]
    rest = [c for c in candidates if c.get("unit_id") not in wanted]
    for candidate in hits:
        scores = dict(candidate.get("scores", {}))
        scores["exact"] = 1.0
        candidate["scores"] = scores
    return hits + rest


def fuse(
    candidates: list[dict[str, Any]],
    *,
    weights: dict[str, float],
) -> list[dict[str, Any]]:
    """Weighted score combination with explicit channel presence."""
    unknown = set(weights) - set(CHANNELS)
    if unknown:
        raise AdmissionError("malformed_source", f"unknown fusion channels: {sorted(unknown)}")
    if any(w < 0 for w in weights.values()):
        raise AdmissionError("malformed_source", "negative fusion weight")
    total = sum(weights.values())
    if total <= 0:
        raise AdmissionError("malformed_source", "fusion weights sum to zero")
    fused = []
    for candidate in candidates:
        scores = candidate.get("scores", {})
        combined = sum(scores.get(ch, 0.0) * w for ch, w in weights.items()) / total
        present = sorted(ch for ch in weights if ch in scores)
        fused.append({**candidate, "fused_score": round(combined, 4),
                      "channels_present": present})
    fused.sort(key=lambda c: c["fused_score"], reverse=True)
    return fused


def apply_constraints(
    ranked: list[dict[str, Any]],
    *,
    max_per_source: int = 3,
    include_stale: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """Freshness filter, per-source diversity caps, and result limit."""
    if max_per_source <= 0 or limit <= 0:
        raise AdmissionError("malformed_source", "constraints must be positive")
    visible: list[dict[str, Any]] = []
    excluded_stale = 0
    per_source: dict[str, int] = {}
    for candidate in ranked:
        if not candidate.get("is_fresh", True) and not include_stale:
            excluded_stale += 1
            continue
        source_id = str(candidate.get("source_id", ""))
        if per_source.get(source_id, 0) >= max_per_source:
            continue
        per_source[source_id] = per_source.get(source_id, 0) + 1
        record = dict(candidate)
        if not candidate.get("is_fresh", True):
            record["stale_labeled"] = True
        visible.append(record)
        if len(visible) >= limit:
            break
    return {"results": visible, "excluded_stale": excluded_stale}


def retrieve(
    *,
    query: str,
    candidates: list[dict[str, Any]],
    tenant_id: str,
    workspace_id: str,
    identifiers: list[str] | None = None,
    weights: dict[str, float] | None = None,
    max_per_source: int = 3,
    include_stale: bool = False,
    limit: int = 10,
) -> dict[str, Any]:
    """One composed pass: ACL, exact, lexical fill, fusion, constraints."""
    if not query:
        raise AdmissionError("malformed_source", "empty retrieval query")
    scoped = acl_filter(candidates, tenant_id=tenant_id, workspace_id=workspace_id)
    ordered = exact_boost(scoped["kept"], identifiers=identifiers or [])
    for candidate in ordered:
        scores = dict(candidate.get("scores", {}))
        scores.setdefault("lexical", lexical_overlap(query, str(candidate.get("text", ""))))
        candidate["scores"] = scores
    fused = fuse(ordered, weights=weights or {"exact": 3.0, "lexical": 2.0, "dense": 1.0})
    final = apply_constraints(fused, max_per_source=max_per_source,
                              include_stale=include_stale, limit=limit)
    return {
        "results": final["results"],
        "denied_by_acl": scoped["denied"],
        "excluded_stale": final["excluded_stale"],
        "candidates_seen": len(candidates),
    }
