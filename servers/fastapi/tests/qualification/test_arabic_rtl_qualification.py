"""The Arabic / RTL qualification suite (W13).

This is the **Python half** of the qualification. It reads the one shared
contract fixture and asserts the model-level properties:

- the script profile of each case;
- the base direction each case resolves to;
- that the OCR worker's re-exported classifier is the shared one, so the OCR
  behaviour is unchanged;
- that the declared script ranges in the contract match the module's, so the
  TypeScript mirror can be checked against the same declaration.

The **markup** half of the qualification lives in
``servers/nextjs/tests/arabic-rtl-qualification.test.mjs``, which reads the
same fixture.

Evidence class
--------------
Every assertion in this suite is ``model``-level: it measures the
classification of the text. No assertion here claims anything about rendered
pixels — there is no headless browser in the test environment — and none of
them claims anything about the exported PPTX, whose fidelity belongs to the
export-fidelity wave.
"""

import json
import pathlib

import pytest

from gomrey import ocr_worker
from gomrey.text_direction import (
    SCRIPT_RANGES,
    ScriptProfile,
    resolve_base_direction,
    script_profile,
)

CONTRACT_PATH = pathlib.Path(__file__).resolve().parent / "arabic_rtl_contract.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _cases() -> list[dict]:
    return _contract()["cases"]


CASES = _cases()
CASE_IDS = [case["id"] for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_the_script_profile_matches_the_contract(case: dict) -> None:
    profile = script_profile(case["text"])
    assert profile.direction == case["expected_script_direction"]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_the_base_direction_matches_the_contract(case: dict) -> None:
    assert resolve_base_direction(case["text"]) == case["expected_base_direction"]


def test_the_declared_ranges_match_the_contract() -> None:
    """One declaration, so the TypeScript mirror is checked against it too."""
    assert SCRIPT_RANGES == _contract()["script_ranges"]


def test_the_ocr_worker_re_exports_the_shared_classifier() -> None:
    """The OCR behaviour is unchanged; only its home moved."""
    assert ocr_worker.script_profile is script_profile
    assert ocr_worker.ScriptProfile is ScriptProfile
    assert ocr_worker.ARABIC_RE is not None
    assert ocr_worker.LATIN_RE is not None
    assert ocr_worker.ARABIC_INDIC_RE is not None
    assert ocr_worker.WESTERN_DIGIT_RE is not None


def test_the_ocr_worker_still_judges_a_region_the_same_way() -> None:
    """A regression guard on the OCR side: presence-based direction is unchanged."""
    arabic_only = ocr_worker.script_profile("مرحبا بالعالم")
    assert arabic_only.direction == "rtl"
    assert arabic_only.arabic is True
    assert arabic_only.latin is False

    mixed = ocr_worker.script_profile("تقرير Report 2026")
    assert mixed.direction == "mixed"
    assert mixed.arabic is True
    assert mixed.latin is True

    english_only = ocr_worker.script_profile("Hello world")
    assert english_only.direction == "ltr"


def test_the_base_direction_is_resolved_from_the_first_strong_character() -> None:
    """Digits and punctuation do not decide."""
    assert resolve_base_direction("2026") == "ltr"
    assert resolve_base_direction("   ") == "ltr"
    assert resolve_base_direction("2026 مرحبا") == "rtl"
    assert resolve_base_direction("Report مرحبا") == "ltr"


def test_the_contract_declares_its_evidence_classes() -> None:
    """The suite must state what it does NOT measure."""
    classes = _contract()["evidence_classes"]
    assert "rendered" in classes
    for case in CASES:
        assert case["evidence_class"] in {"model", "markup", "model+markup"}
