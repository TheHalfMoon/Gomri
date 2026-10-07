"""Tests for the P06-G3 OCR worker contracts and Arabic P0 suite."""

import pytest

from gomrey.gateway import AdmissionError
from gomrey.ocr_worker import (
    ARABIC_P0_CASES,
    OCRRegion,
    check_arabic_case,
    map_ocr_regions,
    quality_observations,
    script_profile,
)


def _region(region_id: str, text: str, **overrides) -> OCRRegion:
    base = {
        "region_id": region_id,
        "bbox": (10.0, 20.0, 200.0, 60.0),
        "text": text,
    }
    base.update(overrides)
    return OCRRegion(**base)


def test_script_profiles_arabic_english_mixed() -> None:
    arabic = script_profile("مرحبا بالعالم")
    assert arabic.arabic is True and arabic.latin is False
    assert arabic.direction == "rtl"
    english = script_profile("Hello world")
    assert english.latin is True and english.arabic is False
    assert english.direction == "ltr"
    mixed = script_profile("تقرير Report 2026")
    assert mixed.direction == "mixed"
    assert mixed.western_digits is True
    indic = script_profile("العدد ١٢٣")
    assert indic.arabic_indic_digits is True
    assert indic.western_digits is False


def test_region_mapping_preserves_visual_provenance() -> None:
    intermediate = map_ocr_regions(
        source_id="src-1", parser_id="ocr-visual-worker",
        input_digest="e" * 64, page_no=3,
        regions=[_region("r1", "نص عربي", confidence=0.93, rotation_degrees=90.0,
                         degraded=("rotation-corrected",))],
    )
    unit = intermediate.units[0]
    assert unit["unit_id"] == "p3-r1"
    assert unit["bbox"] == [10.0, 20.0, 200.0, 60.0]
    assert unit["direction"] == "rtl"
    assert unit["rotation_degrees"] == 90.0
    assert unit["degraded"] == ["rotation-corrected"]
    with pytest.raises(AdmissionError):
        map_ocr_regions(source_id="s", parser_id="p", input_digest="d",
                        page_no=1, regions=[])
    with pytest.raises(AdmissionError):
        map_ocr_regions(source_id="s", parser_id="p", input_digest="d",
                        page_no=1, regions=[_region("r", "x", bbox=(5.0, 5.0, 1.0, 9.0))])
    with pytest.raises(AdmissionError):
        map_ocr_regions(source_id="s", parser_id="p", input_digest="d",
                        page_no=1, regions=[_region("r", "x", confidence=1.5)])


def test_quality_observations_escalate_honestly() -> None:
    regions = [
        _region("good", "نص واضح", confidence=0.95),
        _region("faint", "نص باهت", confidence=0.3, degraded=("low-confidence",)),
    ]
    obs = quality_observations(regions)
    assert obs["low_confidence_regions"] == ["faint"]
    assert obs["needs_second_parser"] is True
    clean = quality_observations([_region("good", "نص واضح", confidence=0.95)])
    assert clean["needs_second_parser"] is False


def test_arabic_p0_suite_all_nine_cases() -> None:
    assert len(ARABIC_P0_CASES) == 9
    assert check_arabic_case("arabic-only", [_region("r", "مرحبا")])["passed"] is True
    assert check_arabic_case("arabic-only", [_region("r", "Hello")])["passed"] is False
    assert check_arabic_case("english-only", [_region("r", "Hello")])["passed"] is True
    assert check_arabic_case(
        "mixed-arabic-english",
        [_region("a", "مرحبا"), _region("b", "Hello")])["passed"] is True
    assert check_arabic_case(
        "rtl-tables", [_region("t", "الجدول Table 1")])["passed"] is True
    assert check_arabic_case(
        "numerals-both-systems",
        [_region("a", "العدد ١٢٣"), _region("b", "count 456")])["passed"] is True
    assert check_arabic_case(
        "rotated-scanned",
        [_region("r", "نص", rotation_degrees=90.0, degraded=("rotation-corrected",))],
    )["passed"] is True
    assert check_arabic_case(
        "poor-scans",
        [_region("r", "نص", confidence=0.2, degraded=("low-confidence",))],
    )["passed"] is True
    # A clean scan must NOT pass the poor-scan case: escalation is required.
    assert check_arabic_case(
        "poor-scans", [_region("r", "نص واضح", confidence=0.97)])["passed"] is False
    assert check_arabic_case(
        "decimals-units-dates",
        [_region("r", "السعر ١٢٫٥٠ جنيه 2026-10-07")])["passed"] is True
    # Bare digits without decimal/date shape do not satisfy the case.
    assert check_arabic_case(
        "decimals-units-dates", [_region("r", "عدد 456")])["passed"] is False
    assert check_arabic_case(
        "charts-formulas",
        [_region("r", "شكل", degraded=("visual-missing",))])["passed"] is True
    with pytest.raises(AdmissionError):
        check_arabic_case("klingon", [_region("r", "x")])
    # Empty input never vacuously passes any case.
    with pytest.raises(AdmissionError):
        check_arabic_case("arabic-only", [])
