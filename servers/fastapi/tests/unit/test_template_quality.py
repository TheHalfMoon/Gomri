"""Deterministic legibility checks for resolved presentation themes.

These tests cover ``templates.v2.quality`` — the WCAG AA contrast linter that
closes the gap left by ``materialize_theme``, which repairs only two of the
resolved theme's surface pairs.

The donor-derived fixture gives the suite a *realistic negative case*: the 18
style presets shipped by the authorised NextSlide skill look entirely
reasonable, yet violate the donor's own mandatory 4.5:1 text-contrast rule on
10 of 54 text-on-background pairs.
"""

import json
import pathlib

import pytest

from templates.v2.quality import (
    WCAG_AA_NON_TEXT_RATIO,
    WCAG_AA_NORMAL_TEXT_RATIO,
    evaluate_theme_legibility,
    legibility_report_for_theme_colors,
)
from templates.v2.theme import contrast_ratio

FIXTURE_PATH = (
    pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "donor_nextslide_presets.json"
)


def _load_donor_presets() -> list[dict]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["presets"]


def _theme(**overrides: str) -> dict:
    colors = {
        "primary": "#1d4ed8",
        "background": "#ffffff",
        "card": "#f8fafc",
        "stroke": "#64748b",
        "background_text": "#0f172a",
        "primary_text": "#ffffff",
        "graph_0": "#1d4ed8",
        "graph_1": "#0f766e",
        "graph_2": "#b45309",
        "graph_3": "#7e22ce",
        "graph_4": "#be123c",
        "graph_5": "#4d7c0f",
        "graph_6": "#0369a1",
        "graph_7": "#a21caf",
        "graph_8": "#c2410c",
        "graph_9": "#0f766e",
    }
    colors.update(overrides)
    return {"data": {"colors": colors}}


# --------------------------------------------------------------------------- #
# Known contrast arithmetic
# --------------------------------------------------------------------------- #


def test_known_contrast_ratios_match_the_wcag_reference_values():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0, abs=0.01)
    assert contrast_ratio("#ffffff", "#000000") == pytest.approx(21.0, abs=0.01)
    # #767676 is the canonical last-passing grey on white.
    assert contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)
    # #777777 is the canonical first-failing grey on white.
    assert contrast_ratio("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)
    assert contrast_ratio("#ffffff", "#ffffff") == pytest.approx(1.0, abs=0.001)


# --------------------------------------------------------------------------- #
# A well-formed theme
# --------------------------------------------------------------------------- #


def test_a_well_formed_theme_reports_no_violations():
    report = evaluate_theme_legibility(_theme())

    assert report.ok is True
    assert report.violations == ()
    assert report.errors == ()
    assert report.warnings == ()
    assert report.checked_pairs > 0
    assert "OK" in report.describe()


def test_report_is_serialisable():
    payload = evaluate_theme_legibility(_theme()).as_dict()

    assert payload["ok"] is True
    assert payload["violations"] == []
    assert isinstance(payload["checked_pairs"], int)


# --------------------------------------------------------------------------- #
# Failing themes
# --------------------------------------------------------------------------- #


def test_a_failing_text_pair_is_reported_as_an_error_with_both_hex_values():
    # #94a3b8 on #f8fafc is 2.45:1 — below the 4.5:1 text requirement for
    # body text drawn on a card surface.
    report = evaluate_theme_legibility(_theme(background_text="#94a3b8"))

    assert report.ok is False
    assert len(report.errors) == 1

    violation = report.errors[0]
    assert violation.foreground_role == "background_text"
    assert violation.background_role == "card"
    assert violation.foreground == "#94a3b8"
    assert violation.background == "#f8fafc"
    assert violation.ratio == pytest.approx(2.45, abs=0.02)
    assert violation.required_ratio == WCAG_AA_NORMAL_TEXT_RATIO
    assert violation.severity == "error"
    assert "background_text" in violation.describe()


def test_the_brand_colour_is_judged_as_a_graphical_object_not_as_text():
    """``primary`` is a brand fill, so WCAG 1.4.11 (3:1) applies, not 4.5:1.

    ``#2563EB`` on ``#F8FAFC`` is 4.4:1 — below the 4.5:1 text threshold but
    comfortably above the 3:1 graphical threshold. Flagging it as a text error
    would reject entirely standard design-system pairings.
    """
    report = evaluate_theme_legibility(_theme(primary="#2563EB", background="#f8fafc"))

    assert report.ok is True
    assert report.errors == ()
    assert report.warnings == ()


def test_a_brand_colour_below_the_graphical_threshold_is_a_warning():
    # #14b8a6 on #f0fdfa is 2.39:1 — below even the 3:1 graphical threshold.
    report = evaluate_theme_legibility(_theme(primary="#14b8a6", background="#f0fdfa"))

    assert report.ok is False
    assert report.errors == ()
    assert len(report.warnings) == 1

    violation = report.warnings[0]
    assert violation.foreground_role == "primary"
    assert violation.background_role == "background"
    assert violation.required_ratio == WCAG_AA_NON_TEXT_RATIO
    assert violation.severity == "warning"


def test_decorative_borders_are_not_checked():
    """WCAG 1.4.11 covers graphical objects required to understand content.

    A hairline separator is decorative, so a low-contrast ``stroke`` must not
    be reported.
    """
    report = evaluate_theme_legibility(_theme(stroke="#e2e8f0"))

    assert report.ok is True
    assert report.violations == ()


def test_chart_series_colours_are_checked_against_the_non_text_ratio():
    report = evaluate_theme_legibility(_theme(graph_0="#f1f5f9"))

    assert report.ok is False
    assert any(
        violation.foreground_role == "graph_0"
        and violation.required_ratio == WCAG_AA_NON_TEXT_RATIO
        for violation in report.violations
    )


def test_the_two_pairs_materialize_theme_already_guarantees_are_not_rechecked():
    # materialize_theme repairs background_text/background and
    # primary_text/primary to 4.5:1, so the linter must not re-report them.
    report = evaluate_theme_legibility(
        _theme(background_text="#ffffff", background="#000000")
    )

    assert all(
        not (
            violation.foreground_role == "background_text"
            and violation.background_role == "background"
        )
        for violation in report.violations
    )


# --------------------------------------------------------------------------- #
# Robustness
# --------------------------------------------------------------------------- #


def test_missing_roles_are_skipped_rather_than_crashing():
    report = legibility_report_for_theme_colors({"background": "#ffffff"})

    assert report.ok is True
    assert report.checked_pairs == 0
    assert report.skipped_pairs > 0


def test_malformed_colour_values_are_skipped_rather_than_crashing():
    report = legibility_report_for_theme_colors(
        {
            "primary": "not-a-colour",
            "background": "#ffffff",
            "card": "#f8fafc",
            "background_text": "#0f172a",
        }
    )

    assert report.ok is True
    assert report.skipped_pairs >= 1


def test_uppercase_hex_is_normalised():
    report = legibility_report_for_theme_colors(
        {"primary": "#14B8A6", "background": "#F0FDFA"}
    )

    assert report.violations
    assert report.violations[0].foreground == "#14b8a6"
    assert report.violations[0].background == "#f0fdfa"


def test_non_mapping_themes_yield_an_empty_report():
    for candidate in (None, "not-a-theme", 42, []):
        report = evaluate_theme_legibility(candidate)
        assert report.ok is True
        assert report.checked_pairs == 0


def test_a_bare_colour_mapping_is_accepted():
    report = evaluate_theme_legibility(
        {
            "colors": {
                "primary": "#14b8a6",
                "background": "#f0fdfa",
                "card": "#f8fafc",
            }
        }
    )

    assert report.ok is False
    assert report.warnings[0].foreground_role == "primary"


# --------------------------------------------------------------------------- #
# The donor-derived negative fixture
# --------------------------------------------------------------------------- #


def test_the_donor_fixture_contains_eighteen_presets():
    presets = _load_donor_presets()

    assert len(presets) == 18
    assert presets[0]["name"] == "Minimal Clean"
    assert presets[0]["tokens"]["--ns-bg"] == "#ffffff"


def test_the_donor_presets_violate_the_donors_own_contrast_rule():
    """The measured defect that motivates this linter, pinned as a regression.

    The donor declares a 4.5:1 minimum text contrast rule and then ships 10
    violating text-on-background pairs across its 18 presets: 7 on
    ``--ns-primary`` and 3 on ``--ns-text-muted``.
    """
    presets = _load_donor_presets()

    failures = []
    for preset in presets:
        tokens = preset["tokens"]
        background = tokens.get("--ns-bg")
        if background is None:
            continue
        for role in ("--ns-text", "--ns-text-muted", "--ns-primary"):
            value = tokens.get(role)
            if value is None:
                continue
            ratio = contrast_ratio(value, background)
            if ratio < WCAG_AA_NORMAL_TEXT_RATIO:
                failures.append((preset["name"], role, value, background, ratio))

    assert len(failures) == 10

    by_role = {}
    for _name, role, *_rest in failures:
        by_role[role] = by_role.get(role, 0) + 1

    assert by_role["--ns-primary"] == 7
    assert by_role["--ns-text-muted"] == 3
    assert by_role.get("--ns-text", 0) == 0


def test_the_gomrey_linter_catches_the_donor_presets_that_fail_the_graphical_rule():
    """Every donor preset maps onto a Gomrey theme; the linter must catch them.

    ``--ns-primary`` is the brand colour, which is Gomrey's ``primary`` role;
    ``--ns-bg`` is Gomrey's ``background`` role. Judged as a graphical object
    (3:1), 2 of the donor's 7 brand-colour failures fall below the threshold
    and must be reported as warnings.
    """
    presets = _load_donor_presets()

    caught = 0
    for preset in presets:
        tokens = preset["tokens"]
        background = tokens.get("--ns-bg")
        primary = tokens.get("--ns-primary")
        if background is None or primary is None:
            continue

        report = evaluate_theme_legibility(
            _theme(primary=primary, background=background)
        )
        offending = [
            violation
            for violation in report.warnings
            if violation.foreground_role == "primary"
            and violation.background_role == "background"
        ]
        if offending:
            caught += 1
            assert offending[0].ratio < WCAG_AA_NON_TEXT_RATIO

    assert caught == 2


# --------------------------------------------------------------------------- #
# Wiring: the report reaches the presentation theme payload
# --------------------------------------------------------------------------- #


def test_template_theme_payload_carries_the_legibility_report():
    from templates.v2.theme import template_theme_for_presentation

    payload = template_theme_for_presentation(
        template_id="tpl-1",
        template_name="Example",
        template_description=None,
        theme={
            "colors": {
                "primary": "#14b8a6",
                "background": "#f0fdfa",
                "card": "#f8fafc",
                "stroke": "#64748b",
                "background_text": "#0f172a",
                "primary_text": "#ffffff",
            }
        },
    )

    assert payload is not None
    assert payload["template_id"] == "tpl-1"
    assert payload["source"] == "template"

    legibility = payload["legibility"]
    assert legibility["ok"] is False
    assert any(
        violation["foreground_role"] == "primary"
        and violation["background_role"] == "background"
        for violation in legibility["violations"]
    )
    assert legibility["checked_pairs"] > 0
    assert all(
        "foreground" in violation and "ratio" in violation
        for violation in legibility["violations"]
    )


def test_template_theme_payload_stays_additive_for_consumers():
    from templates.v2.theme import template_theme_for_presentation

    payload = template_theme_for_presentation(
        template_id="tpl-2",
        template_name="Example",
        template_description=None,
        theme={"colors": {"primary": "#1d4ed8", "background": "#ffffff"}},
    )

    assert payload is not None
    # The pre-existing keys are untouched.
    for key in ("name", "description", "data", "source", "template_id"):
        assert key in payload
    assert payload["data"] == {"colors": {"primary": "#1d4ed8", "background": "#ffffff"}}
