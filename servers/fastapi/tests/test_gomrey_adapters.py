"""Deterministic tests for Presenton-to-Gomrey adapters (P03-G2).

Rows are duck-typed doubles: adapters must never require SQLAlchemy,
an engine, or the editor. Outputs are validated with the Pydantic
contract records, proving the seam maps real state without migration.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from gomrey.adapters import (
    owner_to_scope,
    presentation_to_artifact,
    presentation_to_revision,
    slides_to_narrative,
)
from gomrey.contracts import (
    ArtifactRecord,
    ArtifactRevisionRecord,
)

WHEN = datetime(2026, 10, 7, tzinfo=timezone.utc)


def make_presentation(**overrides):
    values = {
        "id": uuid4(),
        "owner_id": uuid4(),
        "n_slides": 2,
        "title": "Board update",
        "created_at": WHEN,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_slide(index, **overrides):
    values = {
        "id": uuid4(),
        "index": index,
        "layout_group": "body",
        "layout": "title-body",
        "content": {"blocks": [index]},
        "speaker_note": f"Note {index}",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_owner_scope_is_explicit() -> None:
    owner = uuid4()
    tenant, workspace = owner_to_scope(owner)
    assert tenant == f"tenant:{owner}"
    assert workspace == f"tenant:{owner}:default"


def test_unowned_rows_map_to_explicit_unowned_scope() -> None:
    tenant, workspace = owner_to_scope(None)
    assert tenant == "tenant:unowned"
    assert workspace == "workspace:default"


def test_presentation_maps_to_valid_artifact() -> None:
    presentation = make_presentation()
    record = ArtifactRecord(**presentation_to_artifact(presentation))
    assert record.artifact_id == str(presentation.id)
    assert record.tenant_id == f"tenant:{presentation.owner_id}"
    assert record.artifact_type == "presentation"
    assert record.current_revision == 1


def test_untitled_presentation_gets_explicit_fallback() -> None:
    presentation = make_presentation(title=None)
    record = ArtifactRecord(**presentation_to_artifact(presentation))
    assert record.title == "Untitled presentation"


def test_revision_digest_is_deterministic_and_content_bound() -> None:
    presentation = make_presentation()
    slides = [make_slide(0), make_slide(1)]
    first = presentation_to_revision(presentation, slides)
    second = presentation_to_revision(presentation, slides)
    assert first["content_digest"] == second["content_digest"]
    changed = presentation_to_revision(presentation, [make_slide(0), make_slide(9)])
    assert changed["content_digest"] != first["content_digest"]
    record = ArtifactRevisionRecord(**first)
    assert record.revision == 1
    assert record.verification_state == "unverified"


def test_narrative_orders_slides_by_index() -> None:
    presentation = make_presentation()
    slides = [make_slide(2), make_slide(0), make_slide(1)]
    narrative = slides_to_narrative(presentation, slides)
    assert [section["heading"] for section in narrative["sections"]] == [
        "Slide 1",
        "Slide 2",
        "Slide 3",
    ]
    assert narrative["sections"][0]["text"] == "Note 0"
    assert narrative["tenant_id"] == f"tenant:{presentation.owner_id}"
