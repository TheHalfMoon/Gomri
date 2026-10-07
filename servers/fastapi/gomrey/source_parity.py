"""Cross-source IR parity: file, web, video, connector into one model (P07 exit).

Pure deterministic logic composing the P05–P07 contracts. Each source
family enters through its own gateway proof and leaves as the same unit
record shape, so one assembly gate and one coverage gate govern them all:

- web pages: retrieval snapshots plus parsed sections become units with
  snapshot provenance (canonical URL, digest, retrieval timestamp);
- video: aligned transcript segments become timestamped units; scenes
  without transcript become uncertain units with reasons — gaps enter
  accounting, never vanish;
- connector changes: upserts become units with provider-revision
  provenance; tombstones become revocation receipts (P05-G4), linking
  deletion to projection invalidation;
- parity: the union assembles and reconciles through the same gates.
"""

from typing import Any

from gomrey.gateway import AdmissionError
from gomrey.ir_provenance import assemble_ir, verify_coverage
from gomrey.parser_boundary import RevocationReceipt, revoke_source


def web_page_to_units(
    *,
    snapshot: dict[str, Any],
    parser_id: str,
    sections: list[dict[str, Any]],
    source_id: str,
    tenant_id: str,
    workspace_id: str,
    unit_prefix: str = "web",
) -> list[dict[str, Any]]:
    """Snapshot plus parsed sections into IR units with retrieval provenance.

    unit_prefix namespaces multi-page crawls: two pages must not emit the
    same unit ids into one assembly (the gate refuses duplicates loudly).
    """
    if not sections:
        raise AdmissionError("normalization_failure", "web page yielded no sections")
    units = []
    for index, section in enumerate(sections):
        text = section.get("text", "")
        if not isinstance(text, str) or not text:
            raise AdmissionError("normalization_failure", "web section without text")
        units.append({
            "source_id": source_id,
            "source_unit_id": f"{unit_prefix}-{index}",
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "unit_kind": "section",
            "state": "accounted",
            "provenance": {
                "parsers": [parser_id],
                "agreement": "unchallenged",
                "retrieval_snapshot": {
                    "canonical_url": snapshot.get("canonical_url"),
                    "content_digest": snapshot.get("content_digest"),
                    "retrieved_at": snapshot.get("retrieved_at"),
                },
            },
        })
    return units


def media_aligned_to_units(
    *,
    alignment: dict[str, Any],
    source_id: str,
    tenant_id: str,
    workspace_id: str,
) -> list[dict[str, Any]]:
    """Aligned transcript into timestamped units; uncovered scenes uncertain."""
    units = []
    for entry in alignment.get("aligned", []):
        scenes = entry.get("scenes", [])
        units.append({
            "source_id": source_id,
            "source_unit_id": f"seg-{entry['segment_id']}",
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "unit_kind": "segment",
            "state": "accounted" if entry.get("visual_grounded") else "uncertain",
            "provenance": {
                "parsers": ["transcript-scene-worker"],
                "agreement": "agree" if entry.get("visual_grounded") else "single-sided-uncertain",
                "timestamp": entry.get("span"),
                "scenes": scenes,
            },
        })
    for scene_id in alignment.get("scenes_without_transcript", []):
        units.append({
            "source_id": source_id,
            "source_unit_id": f"scene-{scene_id}-uncovered",
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "unit_kind": "scene",
            "state": "uncertain",
            "provenance": {
                "parsers": ["transcript-scene-worker"],
                "agreement": "single-sided-uncertain",
                "reason": "scene-without-transcript",
            },
        })
    if not units:
        raise AdmissionError("normalization_failure", "media alignment yielded no units")
    return units


def sync_changes_to_units(
    *,
    upserts: list[dict[str, Any]],
    tombstones: list[str],
    source_id: str,
    tenant_id: str,
    workspace_id: str,
    provider: str,
) -> tuple[list[dict[str, Any]], list[RevocationReceipt]]:
    """Connector changes into revision-provenance units plus revocation receipts."""
    units = [
        {
            "source_id": source_id,
            "source_unit_id": f"item-{u['item_id']}",
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "unit_kind": "item",
            "state": "accounted",
            "provenance": {
                "parsers": ["connector-normalizer"],
                "agreement": "unchallenged",
                "provider": provider,
                "provider_revision": u["revision"],
            },
        }
        for u in upserts
    ]
    receipts = [revoke_source(source_id, [f"projection-for-{t}"]) for t in tombstones]
    return units, receipts


def parity_assemble(
    *,
    source_id: str,
    tenant_id: str,
    workspace_id: str,
    original_digest: str,
    unit_groups: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    """Assemble heterogeneous units through the single IR gate."""
    records = [record for group in unit_groups for record in group]
    document = assemble_ir(
        source_id=source_id,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        original_digest=original_digest,
        records=records,
    )
    declared = [r["source_unit_id"] for r in records]
    coverage = verify_coverage(declared, records)
    return {"document": document, "coverage": coverage}
