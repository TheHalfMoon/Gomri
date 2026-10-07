"""OCR/visual worker contracts and the Arabic P0 suite (P06-G3).

Pure deterministic logic with no models, no weights, and no image bytes.
This grain defines what an OCR worker must produce and how the nine
canonical Arabic P0 cases are judged — the worker processes that fill
these contracts (PaddleOCR-class and later challengers) qualify through
them, never around them:

- script/direction analysis over Unicode ranges: Arabic block,
  Arabic-supplement/ presentation forms, Latin, Arabic-Indic vs Western
  digits. Classification is observed metadata, never a quality claim;
- region model: every OCR region carries its bounding box, rotation,
  confidence observation, script tags, and degraded flags into the unit
  record, so visual provenance survives into Source IR;
- Arabic P0 suite: the nine MASTER_PLAN cases as frozen expectations
  checked deterministically over region fixtures — Arabic-only,
  English-only, mixed, RTL tables, numerals, rotated/scanned, poor
  scans, decimals/units/dates, charts/formulas;
- degraded modes are explicit labels (rotation-corrected, low-confidence,
  visual-missing), never silent downgrades;
- no accuracy percentages are asserted here; coverage and explicit
  uncertainty remain the contract.

Failures raise the shared AdmissionError taxonomy from gateway.py.
"""

from dataclasses import dataclass, field
import re
from typing import Any

from gomrey.gateway import AdmissionError
from gomrey.parser_boundary import ParserIntermediate

PADDLE_ADOPTION = {
    "donor": "PaddlePaddle/PaddleOCR",
    "mode": "DEPEND / WORKER",
    "role": "scanned/multilingual/table/formula/chart OCR; Arabic/English qualification",
    "forbidden": "no weights vendored and no lockfile change in this grain",
}

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
ARABIC_INDIC_RE = re.compile(r"[\u0660-\u0669]")
WESTERN_DIGIT_RE = re.compile(r"[0-9]")

ARABIC_P0_CASES = (
    "arabic-only",
    "english-only",
    "mixed-arabic-english",
    "rtl-tables",
    "numerals-both-systems",
    "rotated-scanned",
    "poor-scans",
    "decimals-units-dates",
    "charts-formulas",
)


@dataclass
class OCRRegion:
    region_id: str
    bbox: tuple[float, float, float, float]
    text: str
    confidence: float = 1.0
    rotation_degrees: float = 0.0
    degraded: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScriptProfile:
    arabic: bool
    latin: bool
    arabic_indic_digits: bool
    western_digits: bool
    direction: str


def script_profile(text: str) -> ScriptProfile:
    """Observe script and numeral systems present in a region's text."""
    arabic = ARABIC_RE.search(text) is not None
    latin = LATIN_RE.search(text) is not None
    direction = "rtl" if arabic and not latin else ("mixed" if arabic and latin else "ltr")
    return ScriptProfile(
        arabic=arabic,
        latin=latin,
        arabic_indic_digits=ARABIC_INDIC_RE.search(text) is not None,
        western_digits=WESTERN_DIGIT_RE.search(text) is not None,
        direction=direction,
    )


def validate_region(region: OCRRegion) -> OCRRegion:
    """Reject malformed regions before they enter unit accounting."""
    if not region.region_id:
        raise AdmissionError("normalization_failure", "OCR region without id")
    x0, y0, x1, y1 = region.bbox
    if not (x0 < x1 and y0 < y1):
        raise AdmissionError("normalization_failure", "OCR region with inverted bbox")
    if not 0.0 <= region.confidence <= 1.0:
        raise AdmissionError("normalization_failure", "OCR confidence outside [0, 1]")
    if not -360.0 <= region.rotation_degrees <= 360.0:
        raise AdmissionError("normalization_failure", "OCR rotation out of range")
    return region


def map_ocr_regions(
    *,
    source_id: str,
    parser_id: str,
    input_digest: str,
    page_no: int,
    regions: list[OCRRegion],
) -> ParserIntermediate:
    """Map validated OCR regions to units with bbox/script provenance."""
    if not regions:
        raise AdmissionError("normalization_failure", "OCR output has no regions")
    units: list[dict[str, Any]] = []
    for region in regions:
        validate_region(region)
        profile = script_profile(region.text)
        units.append({
            "unit_id": f"p{page_no}-{region.region_id}",
            "kind": "region",
            "text": region.text,
            "page_no": page_no,
            "bbox": list(region.bbox),
            "scripts": {"arabic": profile.arabic, "latin": profile.latin},
            "direction": profile.direction,
            "confidence": region.confidence,
            "rotation_degrees": region.rotation_degrees,
            "degraded": list(region.degraded),
        })
    return ParserIntermediate(
        source_id=source_id,
        parser_id=parser_id,
        input_digest=input_digest,
        units=units,
    )


def quality_observations(regions: list[OCRRegion]) -> dict[str, Any]:
    """Report coverage risks as observations; never a quality certificate."""
    low = sorted(r.region_id for r in regions if r.confidence < 0.6)
    rotated = sorted(r.region_id for r in regions if abs(r.rotation_degrees) > 1.0)
    degraded = sorted({flag for r in regions for flag in r.degraded})
    return {
        "low_confidence_regions": low,
        "rotated_regions": rotated,
        "degraded_flags": degraded,
        "needs_second_parser": bool(low or degraded),
    }


def check_arabic_case(case_id: str, regions: list[OCRRegion]) -> dict[str, Any]:
    """Judge one frozen Arabic P0 case over region fixtures."""
    if case_id not in ARABIC_P0_CASES:
        raise AdmissionError("malformed_source", f"unknown Arabic P0 case: {case_id}")
    if not regions:
        # Empty input must never vacuously pass: all() over nothing is True.
        raise AdmissionError("malformed_source", "Arabic P0 case has no regions")
    for region in regions:
        validate_region(region)
    texts = [r.text for r in regions]
    profiles = [script_profile(t) for t in texts]
    reasons: list[str] = []
    if case_id == "arabic-only" and not all(p.arabic and not p.latin for p in profiles):
        reasons.append("non-arabic-text-present")
    if case_id == "english-only" and not all(p.latin and not p.arabic for p in profiles):
        reasons.append("non-english-text-present")
    if case_id == "mixed-arabic-english" and not (
        any(p.arabic for p in profiles) and any(p.latin for p in profiles)
    ):
        reasons.append("both-scripts-required")
    if case_id == "rtl-tables" and not any(p.direction in {"rtl", "mixed"} for p in profiles):
        reasons.append("rtl-content-required")
    if case_id == "numerals-both-systems" and not (
        any(p.arabic_indic_digits for p in profiles)
        and any(p.western_digits for p in profiles)
    ):
        reasons.append("both-numeral-systems-required")
    if case_id == "rotated-scanned" and not any(abs(r.rotation_degrees) > 1.0 for r in regions):
        reasons.append("rotation-signal-required")
    if case_id == "poor-scans":
        obs = quality_observations(regions)
        if not obs["needs_second_parser"]:
            reasons.append("poor-scan-must-escalate")
    if case_id == "decimals-units-dates" and not any(
        re.search(r"[\d\u0660-\u0669][.,\u066B\u066C][\d\u0660-\u0669]", t)
        or re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", t)
        for t in texts
    ):
        reasons.append("decimal-or-date-shape-required")
    if case_id == "charts-formulas":
        if not any(r.degraded for r in regions):
            reasons.append("visual-content-must-label-degraded")
        certain_visual = [
            r.region_id for r in regions
            if not r.degraded and r.confidence >= 0.9 and not r.text.strip()
        ]
        # Empty high-confidence "reads" of visual regions are certain
        # claims about nothing: reject the presentation, not the content.
        if certain_visual:
            reasons.append("certain-claim-over-visual-content")
    return {"case_id": case_id, "passed": not reasons, "reasons": reasons}
