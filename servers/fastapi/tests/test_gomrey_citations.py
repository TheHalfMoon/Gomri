"""Tests for the P08-G2 citation locators and resolver."""

import pytest

from gomrey.citations import BrokenCitation, citation_id, make_locator, resolve


def _doc() -> dict:
    return {
        "source_id": "src-1",
        "original_digest": "d" * 64,
        "units": [
            {"source_id": "src-1", "source_unit_id": "p1-s0", "page_no": 1,
             "provenance": {"parsers": ["docling-default"], "agreement": "agree"}},
            {"source_id": "src-1", "source_unit_id": "web-0",
             "provenance": {"parsers": ["crawl4ai-bounded"], "agreement": "agree",
                            "retrieval_snapshot": {
                                "canonical_url": "https://93.184.216.34/a",
                                "retrieved_at": "2026-10-07T00:00:00Z"}}},
            {"source_id": "src-1", "source_unit_id": "seg-t1",
             "provenance": {"parsers": ["transcript-scene-worker"], "agreement": "agree",
                            "timestamp": [10.0, 20.0]}},
            {"source_id": "src-1", "source_unit_id": "item-c1",
             "provenance": {"parsers": ["connector-normalizer"], "agreement": "agree"}},
            {"source_id": "src-1", "source_unit_id": "r1",
             "bbox": [10.0, 20.0, 200.0, 60.0],
             "provenance": {"parsers": ["ocr-visual-worker"], "agreement": "agree"}},
        ],
    }


def test_all_five_families_resolve() -> None:
    doc = _doc()
    locators = [
        make_locator("document", source_id="src-1", unit_id="p1-s0", page_no=1),
        make_locator("web", source_id="src-1", unit_id="web-0",
                     canonical_url="https://93.184.216.34/a",
                     retrieved_at="2026-10-07T00:00:00Z"),
        make_locator("video", source_id="src-1", unit_id="seg-t1",
                     video_id="vid-1", start=12.0, end=18.0,
                     transcript_segment_id="t1"),
        make_locator("spreadsheet", source_id="src-1", unit_id="item-c1",
                     workbook="wb", sheet="Sheet1", cell="B4"),
        make_locator("image", source_id="src-1", unit_id="r1",
                     bbox=[10.0, 20.0, 200.0, 60.0]),
    ]
    ids = {loc["citation_id"] for loc in locators}
    assert len(ids) == 5
    for locator in locators:
        resolved = resolve(locator, doc)
        assert resolved["resolved"] is True
        assert resolved["source_revision"] == "d" * 64
    # Deterministic IDs: same locator, same ID.
    again = make_locator("document", source_id="src-1", unit_id="p1-s0", page_no=1)
    assert again["citation_id"] == locators[0]["citation_id"]
    assert citation_id({"kind": "document"}) != ""


def test_broken_citations_fail_loudly() -> None:
    doc = _doc()
    with pytest.raises(BrokenCitation):
        make_locator("hologram", source_id="s", unit_id="u")
    with pytest.raises(BrokenCitation):
        make_locator("document", source_id="src-1", unit_id="p1-s0")
    with pytest.raises(BrokenCitation):
        make_locator("spreadsheet", source_id="s", unit_id="u",
                     workbook="w", sheet="s", cell="nope")
    with pytest.raises(BrokenCitation):
        make_locator("video", source_id="s", unit_id="u",
                     video_id="v", start=9.0, end=9.0)
    with pytest.raises(BrokenCitation):
        resolve(make_locator("document", source_id="src-1", unit_id="ghost", page_no=1), doc)
    with pytest.raises(BrokenCitation):
        resolve(make_locator("document", source_id="src-1", unit_id="p1-s0", page_no=7), doc)
    with pytest.raises(BrokenCitation):
        resolve(make_locator("web", source_id="src-1", unit_id="web-0",
                             canonical_url="https://93.184.216.34/a",
                             retrieved_at="1999-01-01T00:00:00Z"), doc)
    with pytest.raises(BrokenCitation):
        resolve(make_locator("video", source_id="src-1", unit_id="seg-t1",
                             video_id="vid-1", start=0.0, end=5.0), doc)
    with pytest.raises(BrokenCitation):
        resolve({"kind": "hologram"}, doc)
