"""Parity proof: file, web, video, and connector sources, one IR model."""

import pytest

from gomrey.gateway import AdmissionError
from gomrey.ir_provenance import assemble_ir
from gomrey.media_pipeline import (
    MediaTimeline,
    SceneSegment,
    TranscriptSegment,
    align_transcript_visual,
)
from gomrey.budgets import ResourceBudget
from gomrey.source_parity import (
    media_aligned_to_units,
    parity_assemble,
    sync_changes_to_units,
    web_page_to_units,
)
from gomrey.web_acquisition import page_snapshot


def test_four_families_one_model() -> None:
    tenant, workspace, source = "t-1", "w-1", "src-parity"
    digest = "p" * 64
    file_units = [{
        "source_id": source,
        "source_unit_id": "p1-s0",
        "tenant_id": tenant,
        "workspace_id": workspace,
        "unit_kind": "page",
        "state": "accounted",
        "provenance": {"parsers": ["docling-default"], "agreement": "agree"},
    }]
    snapshot = page_snapshot(
        canonical_url="https://93.184.216.34/a", content_digest="a" * 64,
        mime="text/html", response_bytes=512, retrieved_at="2026-10-07T00:00:00Z",
    )
    web_units = web_page_to_units(
        snapshot=snapshot, parser_id="crawl4ai-bounded",
        sections=[{"text": "Page body."}],
        source_id=source, tenant_id=tenant, workspace_id=workspace,
        unit_prefix="web-a",
    )
    second_snapshot = page_snapshot(
        canonical_url="https://93.184.216.34/b", content_digest="b" * 64,
        mime="text/html", response_bytes=256, retrieved_at="2026-10-07T00:00:00Z",
    )
    web_units += web_page_to_units(
        snapshot=second_snapshot, parser_id="crawl4ai-bounded",
        sections=[{"text": "Second page."}],
        source_id=source, tenant_id=tenant, workspace_id=workspace,
        unit_prefix="web-b",
    )
    timeline = MediaTimeline(
        video_id="vid-1", duration_seconds=120.0,
        transcript=[TranscriptSegment("t1", 10.0, 20.0, "Spoken line")],
        scenes=[SceneSegment("s1", 0.0, 30.0, keyframe_ids=("k1",)),
                SceneSegment("s2", 90.0, 110.0, keyframe_ids=("k2",))],
    )
    alignment = align_transcript_visual(
        timeline, ResourceBudget(limits={"media_segments": 10.0}))
    video_units = media_aligned_to_units(
        alignment=alignment, source_id=source,
        tenant_id=tenant, workspace_id=workspace,
    )
    # One grounded segment plus one uncertain uncovered scene.
    assert {u["state"] for u in video_units} == {"accounted", "uncertain"}
    connector_units, receipts = sync_changes_to_units(
        upserts=[{"item_id": "doc-9", "revision": "r-5"}],
        tombstones=["doc-4"],
        source_id=source, tenant_id=tenant, workspace_id=workspace,
        provider="drive",
    )
    assert len(receipts) == 1
    assert receipts[0].audit_preserved is True
    assert receipts[0].projections_invalidated == ("projection-for-doc-4",)
    result = parity_assemble(
        source_id=source, tenant_id=tenant, workspace_id=workspace,
        original_digest=digest,
        unit_groups=[file_units, web_units, video_units, connector_units],
    )
    assert result["document"]["unit_count"] == 6
    assert result["coverage"]["status"] == "partial"
    assert result["coverage"]["uncertain_units"] == ["scene-s2-uncovered"]
    assert result["coverage"]["silent_drops"] == 0
    # The tombstoned item leaves no unit record: deletion is a receipt.
    assert "item-doc-4" not in [u["source_unit_id"]
                                for u in result["document"]["units"]]


def test_parity_gate_refuses_mixed_tenants() -> None:
    foreign = {
        "source_id": "src-parity",
        "source_unit_id": "web-0",
        "tenant_id": "t-2",
        "workspace_id": "w-1",
        "unit_kind": "section",
        "state": "accounted",
        "provenance": {"parsers": ["x"], "agreement": "agree"},
    }
    with pytest.raises(AdmissionError) as exc:
        parity_assemble(
            source_id="src-parity", tenant_id="t-1", workspace_id="w-1",
            original_digest="p" * 64, unit_groups=[[foreign]],
        )
    assert exc.value.code == "unsafe_source"
