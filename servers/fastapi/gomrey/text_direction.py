"""Script and text-direction classification (W13).

Pure deterministic logic with no rendering, no network and no app-layer
imports. This module is the **single source of truth** for the script ranges
and the direction rules, so that the Python side and the TypeScript side
cannot drift apart.

Two distinct concepts live here, and they are not the same thing:

``script_profile(text)``
    *Which scripts and numeral systems are present* in the text. The
    ``direction`` field of the profile is **presence-based**: it is ``rtl``
    when Arabic is present and Latin is not, ``mixed`` when both are present,
    and ``ltr`` otherwise. This is the rule the OCR worker uses to judge a
    scanned region, and it is unchanged by this module.

``resolve_base_direction(text)``
    *Which base direction the text's paragraphs have.* This is the
    **first-strong-character** rule that CSS ``dir="auto"`` implements: the
    first character with a strong bidi type decides. ``R`` (Hebrew, Arabic,
    Syriac, Thaana) gives ``rtl``; ``L`` (Latin, Greek, Cyrillic) gives
    ``ltr``; digits and punctuation are not strong and do not decide; text
    with no strong character is ``ltr``.

The first-strong rule is not an approximation of ``dir="auto"`` — it is the
same rule, so a caller that needs a *decision* (a schema default, a test
expectation, a routing gate) agrees with the browser that will do the
rendering.

The TypeScript mirror is
``servers/nextjs/components/slide-editor/text/text-direction.ts``. The
qualification suite asserts that the two agree.
"""

from dataclasses import dataclass
import re

__all__ = [
    "ARABIC_INDIC_RE",
    "ARABIC_RE",
    "LATIN_RE",
    "LTR_STRONG_RE",
    "RTL_STRONG_RE",
    "SCRIPT_RANGES",
    "WESTERN_DIGIT_RE",
    "ScriptProfile",
    "resolve_base_direction",
    "script_profile",
]

#: Arabic script, including the Arabic Presentation Forms blocks.
ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")

#: Latin letters.
LATIN_RE = re.compile(r"[A-Za-z]")

#: Arabic-Indic digits (٠-٩).
ARABIC_INDIC_RE = re.compile(r"[٠-٩]")

#: Western digits (0-9).
WESTERN_DIGIT_RE = re.compile(r"[0-9]")

#: Characters with a strong right-to-left bidi type.
#:
#: Hebrew, Arabic, Syriac and Thaana. This is deliberately wider than
#: :data:`ARABIC_RE`: the direction rule is about the bidi type, not about
#: one script.
RTL_STRONG_RE = re.compile(
    r"[֐-ࣿיִ-﷿ﹰ-ﻼ]"
)

#: Characters with a strong left-to-right bidi type.
#:
#: Latin, Latin-1 supplement letters, Latin Extended, Greek, Cyrillic and
#: Latin Extended Additional.
LTR_STRONG_RE = re.compile(
    r"[A-Za-zÀ-ʯͰ-֏Ѐ-ԯ԰-ᙿ"
    r"Ḁ-῿Ⰰ-퟿]"
)

#: The ranges, as data, so that the TypeScript mirror and the qualification
#: suite can be checked against one declaration instead of two copies.
SCRIPT_RANGES: dict[str, str] = {
    "arabic": r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]",
    "latin": r"[A-Za-z]",
    "arabic_indic_digits": r"[٠-٩]",
    "western_digits": r"[0-9]",
}


@dataclass(frozen=True)
class ScriptProfile:
    """Which scripts and numeral systems a text contains."""

    arabic: bool
    latin: bool
    arabic_indic_digits: bool
    western_digits: bool
    direction: str


def script_profile(text: str) -> ScriptProfile:
    """Observe script and numeral systems present in a region's text.

    The ``direction`` field is **presence-based** and is unchanged from the OCR
    worker's original rule: ``rtl`` when Arabic is present and Latin is not,
    ``mixed`` when both are present, ``ltr`` otherwise.
    """
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


def resolve_base_direction(text: str) -> str:
    """Resolve the base direction of ``text`` from its first strong character.

    Returns ``"rtl"`` or ``"ltr"``. This is the rule CSS ``dir="auto"``
    implements, so it agrees with the browser that will render the text.
    Digits and punctuation do not decide, and text with no strong character is
    ``ltr``.
    """
    for character in text:
        if RTL_STRONG_RE.match(character):
            return "rtl"
        if LTR_STRONG_RE.match(character):
            return "ltr"
    return "ltr"
