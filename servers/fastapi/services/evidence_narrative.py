"""App-layer wiring for the W3 evidence-bound narrative producer.

This module is the first production import edge from the application layer
into the pure ``gomrey/`` domain package. The dependency direction is
one-way: ``gomrey/`` never imports from ``api/``, ``utils/``, ``models/`` or
``services/``, so the domain layer stays free of app concerns.

What this module does, and nothing else:

- turn a caller's evidence bundle and source IR into a deterministic
  :class:`gomrey.narrative.NarrativePlan`;
- bind plan nodes to rendered slides, with the deterministic table-of-contents
  remap applied exactly once;
- build and persist the NarrativeIR that the artifact carries;
- revalidate every persisted citation before an artifact may be exported.

It never fabricates a citation, never repairs a broken one, and never
downgrades a deterministic verification failure.
"""

from __future__ import annotations

from typing import Any, Optional

from gomrey.adapters import owner_to_scope
from gomrey.evidence_bundle import build_bundle
from gomrey.narrative import (
    NarrativePlan,
    assert_exportable,
    bind_slide_locators,
    build_narrative_ir,
    build_narrative_plan,
)

__all__ = [
    "assert_artifact_exportable",
    "bind_plan_to_slides",
    "build_plan_from_request",
    "narrative_for_presentation",
]


def build_plan_from_request(
    *,
    evidence_bundle: Optional[Any],
    source_ir: Optional[dict[str, Any]],
    owner_id: Any,
    n_slides: Optional[int],
) -> Optional[NarrativePlan]:
    """Build the evidence plan, or return ``None`` when no evidence was given.

    A bundle without a source IR is refused: a locator that cannot be proven
    resolvable must never reach the artifact.
    """
    if evidence_bundle is None:
        return None
    if not source_ir:
        raise ValueError("source_ir is required when an evidence bundle is supplied")

    tenant_id, workspace_id = owner_to_scope(owner_id)

    payload = evidence_bundle
    if hasattr(evidence_bundle, "model_dump"):
        payload = evidence_bundle.model_dump()

    bundle = build_bundle(
        bundle_id=str(payload["bundle_id"]),
        query=str(payload["query"]),
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        source_revisions=list(payload.get("source_revisions") or []),
        spans=list(payload.get("spans") or []),
        retrieval_identities=list(payload.get("retrieval_identities") or []),
        contradictions=list(payload.get("contradictions") or []),
        omissions=list(payload.get("omissions") or []),
        dropped_without_reason=int(payload.get("dropped_without_reason") or 0),
    )

    return build_narrative_plan(
        bundle,
        source_ir,
        plan_id="plan-" + str(bundle.bundle_id),
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        n_slides=n_slides,
    )


def bind_plan_to_slides(
    plan: Optional[NarrativePlan],
    slides: list[Any],
    *,
    toc_slides: int = 0,
    title_slide: bool = True,
) -> list[dict[str, Any]]:
    """Bind plan nodes to rendered slides.

    With no plan, every slide is explicitly abstained rather than silently
    unbound, so a consumer can tell the difference between "no evidence was
    supplied" and "this slide was grounded".
    """
    if plan is None:
        return [
            {
                "citation_ids": [],
                "evidence_status": "abstained",
                "reasons": ["no-evidence-plan"],
            }
            for _slide in slides
        ]
    return bind_slide_locators(
        plan, slides, toc_slides=toc_slides, title_slide=title_slide
    )


def narrative_for_presentation(
    plan: NarrativePlan,
    *,
    artifact_id: str,
    revision: int,
    language: Optional[str] = None,
) -> dict[str, Any]:
    """Build the NarrativeIR document for a presentation."""
    return build_narrative_ir(
        plan,
        narrative_id=f"{artifact_id}:narrative:{revision}",
        artifact_id=str(artifact_id),
        revision=revision,
        language=language,
    )


def assert_artifact_exportable(presentation: Any) -> None:
    """Revalidate every persisted citation before the artifact may be exported.

    Raises :class:`gomrey.citations.BrokenCitation` on the first locator that
    no longer resolves. A presentation with no narrative is not checked: it
    carries no citation claim.
    """
    narrative = getattr(presentation, "narrative", None)
    source_ir = getattr(presentation, "source_ir", None)
    if not narrative or not source_ir:
        return
    assert_exportable(narrative, source_ir)
