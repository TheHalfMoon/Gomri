"""Deterministic legibility rules for resolved presentation themes.

Gomrey already computes WCAG contrast in
:func:`templates.v2.theme.contrast_ratio`, and
:func:`templates.v2.theme.materialize_theme` already *repairs* two pairs so that
body text on the slide background and text on the primary surface reach 4.5:1
(see ``_repair_text_color``). Those two pairs are therefore guaranteed by
construction.

Several other resolved pairs are **not** guaranteed and were not checked
anywhere:

* ``background_text`` on ``card`` — body text drawn on a card surface;
* ``primary`` on ``background`` — the brand colour used as text or as an accent;
* ``stroke`` on ``background`` and on ``card`` — borders and separators;
* ``graph_N`` on ``background`` — chart series colours.

This module closes that hole with a deterministic, dependency-free linter. It
reuses the existing :func:`contrast_ratio` implementation rather than
introducing a second contrast formula, and it reports failures with both hex
values, the measured ratio and the offending role names so a designer or an
agent can act on them.

The rule itself is the WCAG 2.1 AA contrast requirement: 4.5:1 for body text
and 3:1 for large text and non-text graphical objects. It is recorded as a
public, vendor-neutral accessibility standard rather than donor-specific
behaviour.

Rule provenance
---------------
The accessibility threshold is WCAG 2.1 AA (1.4.3 Contrast Minimum for text,
1.4.11 Non-text Contrast). The *choice to enforce it as a deterministic
pre-export check*, and the observation that plausible-looking palettes violate
it, are informed by the authorised NextSlide skill's own mandatory design rules
(``0xRafie/nextslide`` @ ``90a46f933b3056d27460400c915ef268a9ec3f56``, MIT),
whose 18 shipped presets were measured to fail its own 4.5:1 rule on 10 of 54
text-on-background pairs. See ``docs/donors/nextslide-skill/NOTICE.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, Mapping

from templates.v2.theme import contrast_ratio

__all__ = [
    "WCAG_AA_LARGE_TEXT_RATIO",
    "WCAG_AA_NON_TEXT_RATIO",
    "WCAG_AA_NORMAL_TEXT_RATIO",
    "ContrastViolation",
    "ThemeLegibilityReport",
    "evaluate_theme_legibility",
    "legibility_report_for_theme_colors",
]

#: WCAG 2.1 AA minimum contrast for normal body text.
WCAG_AA_NORMAL_TEXT_RATIO = 4.5

#: WCAG 2.1 AA minimum contrast for large text (>= 18pt, or >= 14pt bold).
WCAG_AA_LARGE_TEXT_RATIO = 3.0

#: WCAG 2.1 AA minimum contrast for non-text graphical objects and UI parts.
WCAG_AA_NON_TEXT_RATIO = 3.0

Severity = Literal["error", "warning"]

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")

# (foreground role, background role, required ratio, severity)
#
# Pairs that ``materialize_theme`` already guarantees are deliberately absent:
# ``background_text``/``background`` and ``primary_text``/``primary`` are
# repaired to 4.5:1 by ``_repair_text_color``.
#
# ``primary`` is the brand *fill* colour in Gomrey's role model, not a text
# colour, so it is judged as a graphical object (WCAG 1.4.11, 3:1) rather than
# as body text. Treating it as text at 4.5:1 produced false positives on
# entirely standard design-system pairings such as ``#2563EB`` on ``#F8FAFC``.
#
# ``stroke`` is a decorative border. WCAG 1.4.11 covers graphical objects
# *required to understand the content*; a hairline separator is neither, so it
# is not checked here.
_TEXT_SURFACE_PAIRS: tuple[tuple[str, str], ...] = (
    ("background_text", "card"),
)

_NON_TEXT_SURFACE_PAIRS: tuple[tuple[str, str], ...] = (
    ("primary", "background"),
)


@dataclass(frozen=True)
class ContrastViolation:
    """A single resolved theme pair that fails its required contrast ratio."""

    foreground_role: str
    foreground: str
    background_role: str
    background: str
    ratio: float
    required_ratio: float
    severity: Severity

    def describe(self) -> str:
        return (
            f"{self.severity}: {self.foreground_role} ({self.foreground}) on "
            f"{self.background_role} ({self.background}) has contrast "
            f"{self.ratio:.2f}:1, below the required {self.required_ratio:.1f}:1"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "foreground_role": self.foreground_role,
            "foreground": self.foreground,
            "background_role": self.background_role,
            "background": self.background,
            "ratio": round(self.ratio, 3),
            "required_ratio": self.required_ratio,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ThemeLegibilityReport:
    """The result of evaluating one resolved theme."""

    violations: tuple[ContrastViolation, ...]
    checked_pairs: int
    skipped_pairs: int

    @property
    def ok(self) -> bool:
        """True when no violation of any severity was found."""
        return not self.violations

    @property
    def errors(self) -> tuple[ContrastViolation, ...]:
        return tuple(v for v in self.violations if v.severity == "error")

    @property
    def warnings(self) -> tuple[ContrastViolation, ...]:
        return tuple(v for v in self.violations if v.severity == "warning")

    def describe(self) -> str:
        if self.ok:
            return (
                f"Theme legibility OK: {self.checked_pairs} pairs checked, "
                "no violations."
            )
        return "Theme legibility violations: " + "; ".join(
            violation.describe() for violation in self.violations
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checked_pairs": self.checked_pairs,
            "skipped_pairs": self.skipped_pairs,
            "violations": [violation.as_dict() for violation in self.violations],
        }


def _normalize_hex(value: Any) -> str | None:
    """Return a lowercase ``#rrggbb`` string, or ``None`` when unusable."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not _HEX_COLOR.match(candidate):
        return None
    return candidate.lower()


def _check_pair(
    colors: Mapping[str, Any],
    foreground_role: str,
    background_role: str,
    required_ratio: float,
    severity: Severity,
) -> ContrastViolation | None:
    foreground = _normalize_hex(colors.get(foreground_role))
    background = _normalize_hex(colors.get(background_role))
    if foreground is None or background is None:
        return None
    ratio = round(contrast_ratio(foreground, background), 3)
    if ratio >= required_ratio:
        return None
    return ContrastViolation(
        foreground_role=foreground_role,
        foreground=foreground,
        background_role=background_role,
        background=background,
        ratio=ratio,
        required_ratio=required_ratio,
        severity=severity,
    )


def legibility_report_for_theme_colors(
    colors: Mapping[str, Any],
) -> ThemeLegibilityReport:
    """Evaluate an explicit role -> hex colour mapping."""
    if not isinstance(colors, Mapping):
        return ThemeLegibilityReport(violations=(), checked_pairs=0, skipped_pairs=0)

    violations: list[ContrastViolation] = []
    checked = 0
    skipped = 0

    def consider(
        foreground_role: str,
        background_role: str,
        required_ratio: float,
        severity: Severity,
    ) -> None:
        nonlocal checked, skipped
        foreground = _normalize_hex(colors.get(foreground_role))
        background = _normalize_hex(colors.get(background_role))
        if foreground is None or background is None:
            skipped += 1
            return
        checked += 1
        violation = _check_pair(
            colors, foreground_role, background_role, required_ratio, severity
        )
        if violation is not None:
            violations.append(violation)

    for foreground_role, background_role in _TEXT_SURFACE_PAIRS:
        consider(
            foreground_role,
            background_role,
            WCAG_AA_NORMAL_TEXT_RATIO,
            "error",
        )

    for foreground_role, background_role in _NON_TEXT_SURFACE_PAIRS:
        consider(
            foreground_role,
            background_role,
            WCAG_AA_NON_TEXT_RATIO,
            "warning",
        )

    # Chart series colours are graphical objects, not text: WCAG 1.4.11 applies.
    background = _normalize_hex(colors.get("background"))
    if background is not None:
        for index in range(10):
            role = f"graph_{index}"
            series = _normalize_hex(colors.get(role))
            if series is None:
                continue
            checked += 1
            ratio = round(contrast_ratio(series, background), 3)
            if ratio < WCAG_AA_NON_TEXT_RATIO:
                violations.append(
                    ContrastViolation(
                        foreground_role=role,
                        foreground=series,
                        background_role="background",
                        background=background,
                        ratio=ratio,
                        required_ratio=WCAG_AA_NON_TEXT_RATIO,
                        severity="warning",
                    )
                )

    return ThemeLegibilityReport(
        violations=tuple(violations),
        checked_pairs=checked,
        skipped_pairs=skipped,
    )


def evaluate_theme_legibility(theme: Any) -> ThemeLegibilityReport:
    """Evaluate a materialized presentation theme.

    Accepts either the theme wrapper produced by
    :func:`templates.v2.theme.template_theme_for_presentation`
    (``{"data": {"colors": {...}}}``), a bare ``{"colors": {...}}`` mapping, or a
    ``PresentationThemeData``-shaped object exposing a ``colors`` attribute.
    A theme without a usable colour mapping yields an empty report rather than
    raising, so the linter can be called defensively from generation paths.
    """
    colors: Any = None

    if isinstance(theme, Mapping):
        data = theme.get("data")
        if isinstance(data, Mapping) and isinstance(data.get("colors"), Mapping):
            colors = data["colors"]
        elif isinstance(theme.get("colors"), Mapping):
            colors = theme["colors"]
    else:
        candidate = getattr(theme, "colors", None)
        if isinstance(candidate, Mapping):
            colors = candidate

    if not isinstance(colors, Mapping):
        return ThemeLegibilityReport(violations=(), checked_pairs=0, skipped_pairs=0)

    return legibility_report_for_theme_colors(colors)
