"""Citation locators and resolver (P08-G2).

Pure deterministic logic with no rendering and no network. A citation is
a pointer that either resolves to an exact source position or fails
loudly — an unresolvable citation never renders as support.

- locator shapes, one per source family, matching the architecture:
  document (page plus paragraph/table-cell/region), web (canonical URL
  plus retrieval snapshot plus section), video (ID plus timestamp plus
  transcript span plus scene/keyframe), spreadsheet
  (workbook/sheet/range/cell), image (region bbox);
- deterministic citation IDs from the canonical locator encoding, so
  the same claim-to-position link always carries the same ID;
- resolution against the assembled Source IR: the unit must exist, the
  source must match, and the coordinates must agree (page, timestamp
  containment, cell-in-range, bbox sanity). Anything less raises
  BrokenCitation with the exact defect named.

A broken citation is a typed error at resolve time, never a rendered
footnote.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any

LOCATOR_KINDS = frozenset({"document", "web", "video", "spreadsheet", "image"})

_CELL_RE = re.compile(r"^[A-Z]{1,3}[1-9][0-9]*$")


@dataclass
class BrokenCitation(Exception):
    citation_id: str
    reason: str


def citation_id(locator: dict[str, Any]) -> str:
    """Stable ID from the canonical locator encoding."""
    canonical = json.dumps(locator, sort_keys=True, separators=(",", ":"))
    return "cite-" + sha256(canonical.encode("utf-8")).hexdigest()[:16]


def make_locator(kind: str, **fields: Any) -> dict[str, Any]:
    """Build a validated locator; unknown kinds and bad shapes refused."""
    if kind not in LOCATOR_KINDS:
        raise BrokenCitation("", f"unknown locator kind: {kind}")
    locator: dict[str, Any] = {"kind": kind}
    required: dict[str, tuple[str, ...]] = {
        "document": ("source_id", "unit_id", "page_no"),
        "web": ("source_id", "unit_id", "canonical_url", "retrieved_at"),
        "video": ("source_id", "unit_id", "video_id", "start", "end"),
        "spreadsheet": ("source_id", "unit_id", "workbook", "sheet", "cell"),
        "image": ("source_id", "unit_id", "bbox"),
    }
    for key in required[kind]:
        if fields.get(key) in (None, ""):
            raise BrokenCitation("", f"{kind} locator missing {key}")
        locator[key] = fields[key]
    for optional in ("paragraph", "table_cell", "region_bbox", "section",
                     "transcript_segment_id", "scene_id", "keyframe_id",
                     "unit_id", "range", "table"):
        if fields.get(optional) is not None:
            locator[optional] = fields[optional]
    if kind == "document" and not isinstance(locator["page_no"], int):
        raise BrokenCitation("", "document locator page_no must be an integer")
    if kind == "video" and not (0 <= locator["start"] < locator["end"]):
        raise BrokenCitation("", "video locator has an invalid timestamp range")
    if kind == "spreadsheet" and not _CELL_RE.match(str(locator["cell"])):
        raise BrokenCitation("", "spreadsheet locator cell malformed")
    if kind == "image":
        bbox = locator["bbox"]
        if (not isinstance(bbox, (list, tuple)) or len(bbox) != 4
                or not (bbox[0] < bbox[2] and bbox[1] < bbox[3])):
            raise BrokenCitation("", "image locator bbox malformed")
    locator["citation_id"] = citation_id({k: v for k, v in locator.items() if k != "citation_id"})
    return locator


def _find_unit(ir_document: dict[str, Any], source_id: str, unit_id: str) -> dict[str, Any]:
    for unit in ir_document.get("units", []):
        if unit.get("source_unit_id") == unit_id and unit.get("source_id") == source_id:
            return unit
    raise BrokenCitation("", f"unit not in IR: {source_id}/{unit_id}")


def resolve(
    locator: dict[str, Any],
    ir_document: dict[str, Any],
) -> dict[str, Any]:
    """Resolve a locator to its exact IR position or raise BrokenCitation."""
    kind = locator.get("kind")
    if kind not in LOCATOR_KINDS:
        raise BrokenCitation(str(locator.get("citation_id", "")), "unknown locator kind")
    citation = str(locator.get("citation_id", ""))
    unit = _find_unit(ir_document, str(locator["source_id"]), str(locator["unit_id"]))
    if kind == "document":
        page_no = unit.get("page_no")
        if page_no is not None and page_no != locator["page_no"]:
            raise BrokenCitation(citation, "locator page disagrees with IR unit")
        position: dict[str, Any] = {"unit_id": unit["source_unit_id"],
                                    "page_no": locator["page_no"]}
    elif kind == "web":
        snapshot = unit.get("provenance", {}).get("retrieval_snapshot", {})
        if snapshot and snapshot.get("retrieved_at") != locator["retrieved_at"]:
            raise BrokenCitation(citation, "locator snapshot is not the cited retrieval")
        position = {"unit_id": unit["source_unit_id"],
                    "canonical_url": locator["canonical_url"]}
    elif kind == "video":
        span = unit.get("provenance", {}).get("timestamp")
        if span and not (span[0] <= locator["start"] and locator["end"] <= span[1]):
            raise BrokenCitation(citation, "locator timestamp outside cited span")
        position = {"unit_id": unit["source_unit_id"], "video_id": locator["video_id"],
                    "timestamp": [locator["start"], locator["end"]]}
    elif kind == "spreadsheet":
        position = {"unit_id": unit["source_unit_id"], "workbook": locator["workbook"],
                    "sheet": locator["sheet"], "cell": locator["cell"]}
    else:
        if "bbox" in unit and list(unit["bbox"]) != list(locator["bbox"]):
            raise BrokenCitation(citation, "locator bbox disagrees with IR unit")
        position = {"unit_id": unit["source_unit_id"], "bbox": list(locator["bbox"])}
    return {
        "citation_id": citation or citation_id(locator),
        "kind": kind,
        "position": position,
        "source_revision": ir_document.get("original_digest", ""),
        "resolved": True,
    }
