"""Read-only adapters: imported Presenton rows to Gomrey contract records.

These functions project existing presentation state into Gomrey-owned
contracts without writing to the database, migrating any table, or
touching the editor. Rows are duck-typed: only the documented attributes
are read, so adapters never import SQLAlchemy models or the engine.

Owner-scope rule: the imported base is single-tenant with an optional
owner_id. The owner UUID becomes both the tenant and the default
workspace scope (tenant str(owner), workspace str(owner) + ":default").
Rows without an owner map to the explicit unowned scope rather than
silently inheriting ambient access. Multi-tenant remapping is a later
migration grain, not a silent default here.
"""

import json
from hashlib import sha256
from typing import Any, Optional
from uuid import UUID

UNOWNED_TENANT = "tenant:unowned"
UNOWNED_WORKSPACE = "workspace:default"


def owner_to_scope(owner_id: Optional[UUID | str]) -> tuple[str, str]:
    """Map an imported owner_id to an explicit (tenant_id, workspace_id)."""
    if owner_id is None:
        return UNOWNED_TENANT, UNOWNED_WORKSPACE
    text = str(owner_id)
    return f"tenant:{text}", f"tenant:{text}:default"


def canonical_digest(payload: Any) -> str:
    """sha256 over canonical JSON (sorted keys, compact separators)."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(encoded.encode("utf-8")).hexdigest()


def presentation_to_artifact(presentation: Any) -> dict[str, Any]:
    """Project a presentation row to an Artifact contract dict."""
    tenant_id, workspace_id = owner_to_scope(getattr(presentation, "owner_id", None))
    return {
        "artifact_id": str(presentation.id),
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "artifact_type": "presentation",
        "title": getattr(presentation, "title", None) or "Untitled presentation",
        "current_revision": 1,
        "created_at": getattr(presentation, "created_at", None),
        "status": "draft",
    }


def presentation_to_revision(presentation: Any, slides: list[Any]) -> dict[str, Any]:
    """Project a presentation plus its slides to an ArtifactRevision dict."""
    tenant_id, workspace_id = owner_to_scope(getattr(presentation, "owner_id", None))
    snapshot = {
        "presentation_id": str(presentation.id),
        "n_slides": getattr(presentation, "n_slides", len(slides)),
        "slides": [
            {
                "id": str(slide.id),
                "index": getattr(slide, "index", position),
                "layout_group": getattr(slide, "layout_group", ""),
                "layout": getattr(slide, "layout", ""),
                "content": getattr(slide, "content", {}),
            }
            for position, slide in enumerate(slides)
        ],
    }
    return {
        "artifact_id": str(presentation.id),
        "revision": 1,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "content_digest": canonical_digest(snapshot),
        "verification_state": "unverified",
        "created_at": getattr(presentation, "created_at", None),
    }


def slides_to_narrative(presentation: Any, slides: list[Any]) -> dict[str, Any]:
    """Project slides to a structural NarrativeIR dict.

    Structural only: one section per slide in index order with the speaker
    note as text. No semantic extraction or claim mining happens here;
    evidence binding is a later ingestion grain.
    """
    tenant_id, workspace_id = owner_to_scope(getattr(presentation, "owner_id", None))
    ordered = sorted(slides, key=lambda slide: getattr(slide, "index", 0))
    sections = [
        {
            "heading": f"Slide {position + 1}",
            "text": getattr(slide, "speaker_note", None) or "",
            "claim_ids": [],
        }
        for position, slide in enumerate(ordered)
    ]
    return {
        "narrative_id": f"{presentation.id}:narrative:1",
        "artifact_id": str(presentation.id),
        "revision": 1,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "sections": sections,
    }
